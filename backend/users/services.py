from datetime import datetime, time
from zoneinfo import ZoneInfo

from django.db import IntegrityError, transaction
from django.db.models import Avg, Count
from django.utils.timezone import now as timezone_now

from .auth_services import require_account_action, require_account_action_for_user_id
from .models import (
    DiaryEntry,
    Follow,
    FollowStatus,
    Notification,
    NotificationType,
    RATING_VALUES,
    Review,
    ReviewLike,
    User,
    UserStatus,
    WillBeThere,
)


NOT_STARTED_MESSAGE = (
    "This event can be added to Been once its scheduled start arrives."
)


class EventNotStarted(Exception):
    pass


class ReviewRequiresRating(Exception):
    pass


class ReviewLikeConflict(Exception):
    pass


class FollowConflict(Exception):
    pass


class WillBeThereExpired(Exception):
    pass


class FavoriteLimitReached(Exception):
    pass


@transaction.atomic
def save_favorite(*, user_id, model, target_field, target_id, limit=None):
    require_account_action_for_user_id(user_id)
    User.objects.select_for_update().get(pk=user_id)
    lookup = {"user_id": user_id, f"{target_field}_id": target_id}
    existing = model.objects.filter(**lookup).first()
    if existing is not None:
        return existing, False
    if limit is not None and model.objects.filter(user_id=user_id).count() >= limit:
        raise FavoriteLimitReached
    return model.objects.create(**lookup, added_at=timezone_now()), True


@transaction.atomic
def remove_favorite(*, user_id, model, target_field, target_id):
    require_account_action_for_user_id(user_id)
    User.objects.select_for_update().get(pk=user_id)
    model.objects.filter(
        user_id=user_id,
        **{f"{target_field}_id": target_id},
    ).delete()


def serialize_public_user(user):
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "avatar": user.avatar,
    }


def serialize_follow(follow, *, user):
    return {
        "user": serialize_public_user(user),
        "status": follow.status,
        "created_at": follow.created_at.isoformat().replace("+00:00", "Z"),
        "approved_at": (
            follow.approved_at.isoformat().replace("+00:00", "Z")
            if follow.approved_at is not None
            else None
        ),
    }


@transaction.atomic
def follow_user(*, follower_id, followee_id):
    require_account_action_for_user_id(follower_id)
    followee = (
        User.objects.select_for_update()
        .filter(pk=followee_id, status=UserStatus.ACTIVE, username__isnull=False)
        .first()
    )
    if followee is None:
        return None
    if follower_id == followee_id:
        raise FollowConflict("A user cannot follow themselves.")
    if Follow.objects.filter(follower_id=follower_id, followee=followee).exists():
        raise FollowConflict("A follow or follow request already exists.")
    now = timezone_now()
    status = FollowStatus.PENDING if followee.is_private else FollowStatus.APPROVED
    follow = Follow.objects.create(
        follower_id=follower_id,
        followee=followee,
        status=status,
        created_at=now,
        approved_at=now if status == FollowStatus.APPROVED else None,
    )
    Notification.objects.create(
        recipient=followee,
        actor_id=follower_id,
        type=(
            NotificationType.FOLLOW_REQUEST
            if status == FollowStatus.PENDING
            else NotificationType.FOLLOW
        ),
        created_at=now,
    )
    return follow


@transaction.atomic
def unfollow_user(*, follower_id, followee_id):
    require_account_action_for_user_id(follower_id)
    User.objects.select_for_update().filter(pk=followee_id).first()
    deleted, _ = Follow.objects.filter(
        follower_id=follower_id,
        followee_id=followee_id,
    ).delete()
    return deleted > 0


@transaction.atomic
def accept_follow_request(*, followee_id, follower_id):
    require_account_action_for_user_id(followee_id)
    User.objects.select_for_update().get(pk=followee_id)
    follow = (
        Follow.objects.select_for_update()
        .select_related("follower")
        .filter(
            follower_id=follower_id,
            followee_id=followee_id,
            status=FollowStatus.PENDING,
        )
        .first()
    )
    if follow is None:
        return None
    now = timezone_now()
    follow.status = FollowStatus.APPROVED
    follow.approved_at = now
    follow.save(update_fields=("status", "approved_at"))
    Notification.objects.create(
        recipient_id=follower_id,
        actor_id=followee_id,
        type=NotificationType.REQUEST_ACCEPTED,
        created_at=now,
    )
    return follow


@transaction.atomic
def decline_follow_request(*, followee_id, follower_id):
    require_account_action_for_user_id(followee_id)
    User.objects.select_for_update().get(pk=followee_id)
    deleted, _ = Follow.objects.filter(
        follower_id=follower_id,
        followee_id=followee_id,
        status=FollowStatus.PENDING,
    ).delete()
    return deleted > 0


@transaction.atomic
def change_privacy(*, user_id, is_private):
    require_account_action_for_user_id(user_id)
    user = User.objects.select_for_update().get(pk=user_id)
    if user.is_private == is_private:
        return user, 0
    now = timezone_now()
    accepted = []
    if user.is_private and not is_private:
        accepted = list(
            Follow.objects.select_for_update().filter(
                followee=user,
                status=FollowStatus.PENDING,
            )
        )
        if accepted:
            Follow.objects.filter(
                followee=user,
                status=FollowStatus.PENDING,
            ).update(status=FollowStatus.APPROVED, approved_at=now)
            Notification.objects.bulk_create(
                [
                    Notification(
                        recipient_id=follow.follower_id,
                        actor=user,
                        type=NotificationType.REQUEST_ACCEPTED,
                        created_at=now,
                    )
                    for follow in accepted
                ]
            )
    user.is_private = is_private
    user.save(update_fields=("is_private",))
    return user, len(accepted)


def event_is_loggable(event):
    local_now = timezone_now().astimezone(
        ZoneInfo(event.venue.city.timezone)
    )
    local_wall_now = local_now.replace(tzinfo=None)
    scheduled_wall_time = datetime.combine(
        event.event_date,
        event.start_time or time.min,
    )
    return local_wall_now >= scheduled_wall_time


def will_be_there_is_active(event, *, at=None):
    at = at or timezone_now()
    local_today = at.astimezone(ZoneInfo(event.venue.city.timezone)).date()
    return local_today <= event.event_date


@transaction.atomic
def save_will_be_there(*, user, event):
    require_account_action(user)
    now = timezone_now()
    if not will_be_there_is_active(event, at=now):
        raise WillBeThereExpired
    entry, created = WillBeThere.objects.get_or_create(
        user=user,
        event=event,
        defaults={"created_at": now},
    )
    if created:
        follower_ids = Follow.objects.filter(
            followee=user,
            status=FollowStatus.APPROVED,
        ).values_list("follower_id", flat=True)
        Notification.objects.bulk_create(
            [
                Notification(
                    recipient_id=follower_id,
                    actor=user,
                    type=NotificationType.WILL_BE_THERE,
                    event=event,
                    created_at=now,
                )
                for follower_id in follower_ids
            ]
        )
    return entry, created


def remove_will_be_there(*, user, event):
    require_account_action(user)
    WillBeThere.objects.filter(user=user, event=event).delete()


def serialize_will_be_there(entry):
    return {
        "event_id": entry.event_id,
        "created_at": entry.created_at.isoformat().replace("+00:00", "Z"),
    }


def viewer_will_be_there_state(*, user, event):
    active = will_be_there_is_active(event)
    has_record = WillBeThere.objects.filter(user=user, event=event).exists()
    marked = active and has_record
    return {
        "is_marked": marked,
        "was_marked": has_record,
        "can_mark": active,
        "unavailable_reason": (
            None
            if active
            else "Will Be There expired at the end of the event's local date."
        ),
    }


def serialize_review(review, *, include_author=False, viewer=None):
    like_count = getattr(review, "like_count", None)
    if like_count is None:
        like_count = review.likes.count()
    payload = {
        "id": review.id,
        "body": review.body,
        "published_at": review.published_at.isoformat().replace("+00:00", "Z"),
        "like_count": like_count,
    }
    if include_author:
        payload["rating"] = float(review.entry.rating)
        payload["author"] = serialize_public_user(review.entry.user)
        if viewer is not None and viewer.is_authenticated:
            payload["viewer_has_liked"] = getattr(
                review,
                "viewer_has_liked",
                ReviewLike.objects.filter(user=viewer, review=review).exists(),
            )
            is_self = review.entry.user_id == viewer.id
            viewer_follows = False if is_self else getattr(
                review,
                "viewer_follows",
                Follow.objects.filter(
                    follower=viewer,
                    followee_id=review.entry.user_id,
                    status=FollowStatus.APPROVED,
                ).exists(),
            )
            has_follow_row = False if is_self else getattr(
                review,
                "viewer_has_follow_row",
                Follow.objects.filter(
                    follower=viewer,
                    followee_id=review.entry.user_id,
                ).exists(),
            )
            payload["viewer_follows"] = viewer_follows
            payload["can_follow"] = not is_self and not has_follow_row
            payload["can_unfollow"] = viewer_follows
    return payload


def serialize_diary_entry(entry, *, include_review=True):
    payload = {
        "id": entry.id,
        "rating": float(entry.rating) if entry.rating is not None else None,
        "rated_at": (
            entry.rated_at.isoformat().replace("+00:00", "Z")
            if entry.rated_at is not None
            else None
        ),
        "created_at": entry.created_at.isoformat().replace("+00:00", "Z"),
    }
    if include_review:
        review = getattr(entry, "review", None)
        payload["review"] = (
            serialize_review(review) if review is not None else None
        )
    return payload


def event_rating_summary(event):
    aggregate = (
        DiaryEntry.objects.for_aggregation()
        .filter(event=event)
        .aggregate(count=Count("id"), average=Avg("rating"))
    )
    if aggregate["count"] < 1:
        return {
            "state": "not_enough_ratings",
            "count": aggregate["count"],
        }
    return {
        "state": "available",
        "count": aggregate["count"],
        "average": float(aggregate["average"]),
    }


def rating_distribution_payload(entries, *, minimum_count=0):
    rated = entries.filter(rating__isnull=False)
    distribution = {float(value): 0 for value in RATING_VALUES}
    for row in rated.values("rating").annotate(count=Count("id")):
        distribution[float(row["rating"])] = row["count"]
    if sum(distribution.values()) < minimum_count:
        return {"state": "not_enough_ratings"}
    maximum = max(distribution.values(), default=0)
    if maximum == 0:
        return {"state": "empty"}
    return {
        "state": "available",
        "buckets": [
            {"rating": rating, "count": count, "relative_value": count / maximum}
            for rating, count in distribution.items()
        ],
    }


@transaction.atomic
def save_rating(*, user, event, rating):
    require_account_action(user)
    User.objects.select_for_update().get(pk=user.pk)
    entry = (
        DiaryEntry.objects.visible_to(user)
        .filter(user=user, event=event)
        .first()
    )
    now = timezone_now()
    if entry is None:
        if not event_is_loggable(event):
            raise EventNotStarted
        return (
            DiaryEntry.objects.create(
                user=user,
                event=event,
                rating=rating,
                rated_at=now,
            ),
            True,
        )

    entry.rating = rating
    update_fields = ["rating"]
    if entry.rated_at is None:
        entry.rated_at = now
        update_fields.append("rated_at")
    entry.save(update_fields=update_fields)
    return entry, False


@transaction.atomic
def remove_rating(*, user, event):
    require_account_action(user)
    entry = (
        DiaryEntry.objects.visible_to(user)
        .select_for_update()
        .filter(user=user, event=event)
        .first()
    )
    if entry is None:
        return None
    review = getattr(entry, "review", None)
    cascade = {
        "review_deleted": review is not None,
        "review_likes_deleted": review.likes.count() if review is not None else 0,
    }
    if review is not None:
        review.delete()
        entry._state.fields_cache.pop("review", None)
    if entry.rating is not None:
        entry.rating = None
        entry.rated_at = None
        entry.save(update_fields=("rating", "rated_at"))
    return entry, cascade


@transaction.atomic
def remove_entry(*, user, event):
    require_account_action(user)
    entry = (
        DiaryEntry.objects.visible_to(user)
        .select_for_update()
        .filter(user=user, event=event)
        .first()
    )
    if entry is None:
        return False
    entry.delete()
    return True


@transaction.atomic
def save_review(*, user, event, body):
    require_account_action(user)
    entry = (
        DiaryEntry.objects.visible_to(user)
        .select_for_update()
        .filter(user=user, event=event)
        .first()
    )
    if entry is None:
        return None, False
    if entry.rating is None:
        raise ReviewRequiresRating
    review = Review.objects.filter(entry=entry).first()
    if review is None:
        return (
            Review.objects.create(
                entry=entry,
                body=body,
                published_at=timezone_now(),
            ),
            True,
        )
    review.body = body
    review.save(update_fields=("body",))
    return review, False


@transaction.atomic
def delete_review(*, user, event):
    require_account_action(user)
    review = (
        Review.objects.visible_to(user)
        .select_for_update()
        .filter(entry__user=user, entry__event=event)
        .first()
    )
    if review is None:
        return False
    review.delete()
    return True


@transaction.atomic
def like_review(*, user, review):
    require_account_action(user)
    review = Review.objects.select_for_update().get(pk=review.pk)
    if review.entry.user_id == user.id:
        raise ReviewLikeConflict("A user cannot like their own review.")
    try:
        ReviewLike.objects.create(user=user, review=review)
    except IntegrityError as exc:
        raise ReviewLikeConflict("Review is already liked.") from exc
    Notification.objects.create(
        recipient=review.entry.user,
        actor=user,
        type=NotificationType.REVIEW_LIKE,
        review=review,
        created_at=timezone_now(),
    )
    return review.likes.count()


@transaction.atomic
def unlike_review(*, user, review):
    require_account_action(user)
    deleted, _ = ReviewLike.objects.filter(user=user, review=review).delete()
    return deleted > 0
