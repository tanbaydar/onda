import json

from django.core.management.base import BaseCommand

from catalog.models import Event, EventIdentity
from config.sources import Source
from ingestion.models import RawIngest


class Command(BaseCommand):
    help = "Backfill Event.is_ticketed from archived RA listing responses."

    def handle(self, *args, **options):
        latest = {}
        raw_rows = (
            RawIngest.objects.filter(seed__source=Source.RA, http_status=200)
            .exclude(response_body__isnull=True)
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
                if not isinstance(source_id, str) or not source_id:
                    continue
                value = event.get("isTicketed")
                latest[source_id] = value if isinstance(value, bool) else None

        identities = {
            identity.source_id: identity
            for identity in EventIdentity.objects.select_related("event").filter(
                source=Source.RA,
                source_id__in=latest,
            )
        }
        changed = []
        unknown = 0
        unmatched = 0
        for source_id, value in latest.items():
            if value is None:
                unknown += 1
                continue
            identity = identities.get(source_id)
            if identity is None:
                unmatched += 1
                continue
            if identity.event.is_ticketed != value:
                identity.event.is_ticketed = value
                changed.append(identity.event)

        Event.objects.bulk_update(changed, ("is_ticketed",), batch_size=500)
        self.stdout.write(
            f"updated={len(changed)} unknown={unknown} unmatched={unmatched}"
        )
