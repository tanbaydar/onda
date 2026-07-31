from datetime import datetime, time
from zoneinfo import ZoneInfo

from django.db import IntegrityError, transaction
from django.db.models import Avg, Count
from django.utils.timezone import now as timezone_now

from .models import DiaryEntry, Review, ReviewLike, User


NOT_STARTED_MESSAGE = (
    "This event can be added to Been once its scheduled start arrives."
)


class EventNotStarted(Exception):
    pass


class ReviewRequiresRating(Exception):
    pass


class ReviewLikeConflict(Exception):
    pass


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
        payload["author"] = {
            "id": review.entry.user.id,
            "username": review.entry.user.username,
            "display_name": review.entry.user.display_name,
        }
        if viewer is not None and viewer.is_authenticated:
            payload["viewer_has_liked"] = getattr(
                review,
                "viewer_has_liked",
                ReviewLike.objects.filter(user=viewer, review=review).exists(),
            )
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
    if aggregate["count"] < 3:
        return {
            "state": "not_enough_ratings",
            "count": aggregate["count"],
        }
    return {
        "state": "available",
        "count": aggregate["count"],
        "average": float(aggregate["average"]),
    }


@transaction.atomic
def save_rating(*, user, event, rating):
    User.objects.select_for_update().get(pk=user.pk)
    entry = (
        DiaryEntry.objects.visible_to(user)
        .filter(event=event)
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
    entry = (
        DiaryEntry.objects.visible_to(user)
        .select_for_update()
        .filter(event=event)
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
    entry = (
        DiaryEntry.objects.visible_to(user)
        .select_for_update()
        .filter(event=event)
        .first()
    )
    if entry is None:
        return False
    entry.delete()
    return True


@transaction.atomic
def save_review(*, user, event, body):
    entry = (
        DiaryEntry.objects.visible_to(user)
        .select_for_update()
        .filter(event=event)
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
    review = Review.objects.select_for_update().get(pk=review.pk)
    if review.entry.user_id == user.id:
        raise ReviewLikeConflict("A user cannot like their own review.")
    try:
        ReviewLike.objects.create(user=user, review=review)
    except IntegrityError as exc:
        raise ReviewLikeConflict("Review is already liked.") from exc
    return review.likes.count()


@transaction.atomic
def unlike_review(*, user, review):
    deleted, _ = ReviewLike.objects.filter(user=user, review=review).delete()
    return deleted > 0
