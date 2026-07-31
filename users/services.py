from datetime import datetime, time
from zoneinfo import ZoneInfo

from django.db import transaction
from django.db.models import Avg, Count
from django.utils.timezone import now as timezone_now

from .models import DiaryEntry, User


NOT_STARTED_MESSAGE = (
    "This event can be added to Been once its scheduled start arrives."
)


class EventNotStarted(Exception):
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


def serialize_diary_entry(entry):
    return {
        "id": entry.id,
        "rating": float(entry.rating) if entry.rating is not None else None,
        "rated_at": (
            entry.rated_at.isoformat().replace("+00:00", "Z")
            if entry.rated_at is not None
            else None
        ),
        "created_at": entry.created_at.isoformat().replace("+00:00", "Z"),
    }


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
    if entry.rating is not None:
        entry.rating = None
        entry.rated_at = None
        entry.save(update_fields=("rating", "rated_at"))
    return entry


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
