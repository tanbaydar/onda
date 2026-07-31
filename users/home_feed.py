import base64
import json
import re

from django.db.models import (
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    F,
    IntegerField,
    Q,
    TimeField,
    Value,
)
from django.db.models.functions import Cast, Concat, LPad
from django.utils.dateparse import parse_datetime

from .models import DiaryEntry, Follow, FollowStatus, Review, ReviewLike


ACTIVITY_TYPES = ("rated_been", "review_like", "follow")
SOURCE_KEY_RE = re.compile(r"^\d{20}(?::\d{20})?$")


def _source_part(field):
    return LPad(Cast(field, CharField()), 20, Value("0"))


def _nulls():
    return {
        "event_id": Value(None, output_field=IntegerField()),
        "event_title": Value(None, output_field=CharField()),
        "event_date": Value(None, output_field=DateField()),
        "event_start_time": Value(None, output_field=TimeField()),
        "rating": Value(None, output_field=DecimalField(max_digits=2, decimal_places=1)),
        "review_id": Value(None, output_field=IntegerField()),
        "review_body": Value(None, output_field=CharField()),
        "review_author_id": Value(None, output_field=IntegerField()),
        "review_author_username": Value(None, output_field=CharField()),
        "review_author_display_name": Value(None, output_field=CharField()),
        "target_user_id": Value(None, output_field=IntegerField()),
        "target_username": Value(None, output_field=CharField()),
        "target_display_name": Value(None, output_field=CharField()),
    }


FEED_FIELDS = (
    "activity_type", "activity_at", "source_key",
    "actor_id", "actor_username", "actor_display_name",
    "event_id", "event_title", "event_date", "event_start_time",
    "rating", "review_id", "review_body", "review_author_id",
    "review_author_username", "review_author_display_name",
    "target_user_id", "target_username", "target_display_name",
)


def encode_cursor(row):
    value = [row["activity_at"].isoformat(), row["activity_type"], row["source_key"]]
    return base64.urlsafe_b64encode(json.dumps(value).encode()).decode().rstrip("=")


def decode_cursor(value):
    try:
        padded = value + "=" * (-len(value) % 4)
        decoded = json.loads(base64.urlsafe_b64decode(padded).decode())
        if not isinstance(decoded, list) or len(decoded) != 3:
            raise ValueError
        timestamp = parse_datetime(decoded[0])
        activity_type, source_key = decoded[1:]
        if (
            timestamp is None or timestamp.tzinfo is None
            or activity_type not in ACTIVITY_TYPES
            or not isinstance(source_key, str)
            or SOURCE_KEY_RE.fullmatch(source_key) is None
        ):
            raise ValueError
        return timestamp, activity_type, source_key
    except (ValueError, TypeError, UnicodeError, json.JSONDecodeError):
        return None


def _after_cursor(queryset, cursor):
    if cursor is None:
        return queryset
    timestamp, activity_type, source_key = cursor
    return queryset.filter(
        Q(activity_at__lt=timestamp)
        | Q(activity_at=timestamp, activity_type__lt=activity_type)
        | Q(
            activity_at=timestamp,
            activity_type=activity_type,
            source_key__lt=source_key,
        )
    )


def home_feed_rows(viewer, *, cursor=None, limit=21):
    followees = Follow.objects.filter(
        follower=viewer,
        status=FollowStatus.APPROVED,
    ).values("followee_id")

    been_nulls = _nulls()
    for key in ("event_id", "event_title", "event_date", "event_start_time", "rating", "review_id", "review_body"):
        been_nulls.pop(key)
    been = DiaryEntry.objects.visible_to(viewer).filter(
        user_id__in=followees,
        rating__isnull=False,
        rated_at__isnull=False,
    ).annotate(
        activity_type=Value("rated_been", output_field=CharField()),
        activity_at=F("rated_at"),
        source_key=_source_part(F("id")),
        actor_id=F("user_id"),
        actor_username=F("user__username"),
        actor_display_name=F("user__display_name"),
        event_title=F("event__title"),
        event_date=F("event__event_date"),
        event_start_time=F("event__start_time"),
        review_id=F("review__id"),
        review_body=F("review__body"),
        **been_nulls,
    ).values(*FEED_FIELDS)

    follow_nulls = _nulls()
    for key in ("target_user_id", "target_username", "target_display_name"):
        follow_nulls.pop(key)
    follows = Follow.objects.filter(
        follower_id__in=followees,
        status=FollowStatus.APPROVED,
        approved_at__isnull=False,
    ).annotate(
        activity_type=Value("follow", output_field=CharField()),
        activity_at=F("approved_at"),
        source_key=Concat(
            _source_part(F("follower_id")), Value(":"), _source_part(F("followee_id"))
        ),
        actor_id=F("follower_id"),
        actor_username=F("follower__username"),
        actor_display_name=F("follower__display_name"),
        target_user_id=F("followee_id"),
        target_username=F("followee__username"),
        target_display_name=F("followee__display_name"),
        **follow_nulls,
    ).values(*FEED_FIELDS)

    visible_reviews = Review.objects.visible_to(viewer).values("id")
    like_nulls = _nulls()
    for key in (
        "event_id", "event_title", "event_date", "event_start_time",
        "review_id", "review_body", "review_author_id",
        "review_author_username", "review_author_display_name",
    ):
        like_nulls.pop(key)
    likes = ReviewLike.objects.filter(
        user_id__in=followees,
        review_id__in=visible_reviews,
    ).annotate(
        activity_type=Value("review_like", output_field=CharField()),
        activity_at=F("created_at"),
        source_key=Concat(
            _source_part(F("user_id")), Value(":"), _source_part(F("review_id"))
        ),
        actor_id=F("user_id"),
        actor_username=F("user__username"),
        actor_display_name=F("user__display_name"),
        event_id=F("review__entry__event_id"),
        event_title=F("review__entry__event__title"),
        event_date=F("review__entry__event__event_date"),
        event_start_time=F("review__entry__event__start_time"),
        review_body=F("review__body"),
        review_author_id=F("review__entry__user_id"),
        review_author_username=F("review__entry__user__username"),
        review_author_display_name=F("review__entry__user__display_name"),
        **like_nulls,
    ).values(*FEED_FIELDS)

    combined = _after_cursor(been, cursor).union(
        _after_cursor(likes, cursor),
        _after_cursor(follows, cursor),
        all=True,
    ).order_by("-activity_at", "-activity_type", "-source_key")
    return list(combined[:limit])


def serialize_feed_row(row):
    item = {
        "type": row["activity_type"],
        "activity_at": row["activity_at"].isoformat().replace("+00:00", "Z"),
        "actor": {
            "id": row["actor_id"],
            "username": row["actor_username"],
            "display_name": row["actor_display_name"],
        },
        "target": {},
        "context": None,
    }
    if row["activity_type"] == "follow":
        item["target"]["user"] = {
            "id": row["target_user_id"],
            "username": row["target_username"],
            "display_name": row["target_display_name"],
        }
        return item
    event = {
        "id": row["event_id"],
        "title": row["event_title"],
        "event_date": row["event_date"].isoformat(),
        "start_time": row["event_start_time"].isoformat() if row["event_start_time"] else None,
    }
    item["target"]["event"] = event
    if row["activity_type"] == "rated_been":
        item["context"] = {
            "rating": float(row["rating"]),
            "review": (
                {"id": row["review_id"], "body": row["review_body"]}
                if row["review_id"] is not None else None
            ),
        }
    else:
        item["target"]["review"] = {
            "id": row["review_id"],
            "body": row["review_body"],
            "author": {
                "id": row["review_author_id"],
                "username": row["review_author_username"],
                "display_name": row["review_author_display_name"],
            },
        }
    return item
