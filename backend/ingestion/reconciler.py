from zoneinfo import ZoneInfo

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from catalog.models import CityIdentity, Event, EventIdentity
from ingestion.models import SyncRunType


def _local_today(timezone_name: str):
    return timezone.now().astimezone(ZoneInfo(timezone_name)).date()


def _derived_status(identities):
    misses = [identity.misses for identity in identities]
    if all(value >= 3 for value in misses):
        return "hidden"
    if all(value >= 1 for value in misses):
        return "unverified"
    return "active"


def reconcile(
    seed,
    run,
    observed_source_ids,
    fetch_complete,
    window_start,
    window_end,
):
    if not fetch_complete:
        return
    if run.run_type in (SyncRunType.BACKFILL, SyncRunType.REPLAY):
        return

    observed_source_ids = set(observed_source_ids)

    with transaction.atomic():
        city_identity = CityIdentity.objects.select_related("city").get(
            source=seed.source,
            source_id=seed.area_ref,
        )
        city = city_identity.city
        local_today = _local_today(city.timezone)

        identities = list(
            EventIdentity.objects.select_for_update()
            .select_related("event", "event__canonical_event")
            .filter(
                source=seed.source,
                event__venue__city=city,
                event__event_date__gt=local_today,
                event__event_date__gte=window_start,
                event__event_date__lte=window_end,
            )
        )

        affected_event_ids = set()
        for identity in identities:
            new_misses = (
                0
                if identity.source_id in observed_source_ids
                else identity.misses + 1
            )
            if identity.misses != new_misses:
                identity.misses = new_misses
                identity.save(update_fields=["misses"])
            affected_event_ids.add(
                identity.event.canonical_event_id or identity.event_id
            )

        for event_id in affected_event_ids:
            all_identities = list(
                EventIdentity.objects.select_for_update().filter(
                    Q(event_id=event_id) | Q(event__canonical_event_id=event_id)
                )
            )
            status = _derived_status(all_identities)
            related_events = Event.objects.select_for_update().filter(
                Q(pk=event_id) | Q(canonical_event_id=event_id)
            )
            related_events.exclude(status=status).update(status=status)
