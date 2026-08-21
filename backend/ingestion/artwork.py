import json

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import transaction

from catalog.models import Event, EventIdentity
from ingestion.models import RawIngest


_validate_https_url = URLValidator(schemes=("https",))


def _safe_image_url(value):
    if not isinstance(value, str) or len(value) > 2048:
        return None
    try:
        _validate_https_url(value)
    except ValidationError:
        return None
    return value


def event_cover_image_url(event):
    flyer_front = _safe_image_url(event.get("flyerFront"))
    if flyer_front is not None:
        return flyer_front

    images = event.get("images") or []
    if not isinstance(images, list):
        return None
    for image in images:
        if not isinstance(image, dict) or image.get("type") != "FLYERFRONT":
            continue
        filename = _safe_image_url(image.get("filename"))
        if filename is not None:
            return filename
    return None


@transaction.atomic
def backfill_event_artwork():
    latest = {}
    raw_rows = (
        RawIngest.objects.filter(http_status=200)
        .exclude(response_body__isnull=True)
        .select_related("seed")
        .order_by("fetched_at", "id")
    )
    for raw in raw_rows.iterator():
        try:
            payload = json.loads(raw.response_body)
            listings = payload["data"]["eventListings"]["data"]
        except (json.JSONDecodeError, KeyError, TypeError):
            continue
        if not isinstance(listings, list):
            continue
        for listing in listings:
            event = listing.get("event") if isinstance(listing, dict) else None
            source_id = event.get("id") if isinstance(event, dict) else None
            if isinstance(source_id, str) and source_id:
                latest[(raw.seed.source, source_id)] = event_cover_image_url(event)

    identities = EventIdentity.objects.select_related("event").filter(
        source_id__in=[source_id for _, source_id in latest]
    )
    changed = []
    matched = 0
    for identity in identities:
        key = (identity.source, identity.source_id)
        if key not in latest:
            continue
        matched += 1
        cover_image_url = latest[key]
        if identity.event.cover_image_url != cover_image_url:
            identity.event.cover_image_url = cover_image_url
            changed.append(identity.event)
    Event.objects.bulk_update(changed, ("cover_image_url",))
    return {"observed": len(latest), "matched": matched, "changed": len(changed)}
