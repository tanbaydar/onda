import json

from django.core.management.base import BaseCommand, CommandError

from catalog.models import Event, EventIdentity
from config.sources import Source
from ingestion.models import RawIngest, RejectedIngest


class Command(BaseCommand):
    help = "Backfill Event.is_ticketed from archived RA listing responses."

    def add_arguments(self, parser):
        parser.add_argument(
            "--show-unmatched",
            action="store_true",
            help="Classify and print unmatched RA event IDs.",
        )

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
        unmatched_source_ids = set()
        for source_id, value in latest.items():
            if value is None:
                unknown += 1
                continue
            identity = identities.get(source_id)
            if identity is None:
                unmatched += 1
                unmatched_source_ids.add(source_id)
                continue
            if identity.event.is_ticketed != value:
                identity.event.is_ticketed = value
                changed.append(identity.event)

        Event.objects.bulk_update(changed, ("is_ticketed",), batch_size=500)
        self.stdout.write(
            f"updated={len(changed)} unknown={unknown} unmatched={unmatched}"
        )
        if options["show_unmatched"]:
            self._print_unmatched(unmatched_source_ids)

    def _print_unmatched(self, source_ids):
        quarantined_ids = set(
            RejectedIngest.objects.filter(entity_ref__in=source_ids)
            .exclude(entity_ref__isnull=True)
            .values_list("entity_ref", flat=True)
        )
        traced = {
            identity.source_id: identity
            for identity in EventIdentity.objects.select_related("event").filter(
                source=Source.RA,
                source_id__in=source_ids,
            )
        }
        live_ids = sorted(
            source_id
            for source_id, identity in traced.items()
            if identity.event.status != "hidden"
        )
        if live_ids:
            raise CommandError(
                "unmatched RA IDs map to live catalog events: "
                + ", ".join(live_ids)
            )

        buckets = {"quarantine": [], "hidden": [], "no_trace": []}
        for source_id in sorted(source_ids):
            if source_id in quarantined_ids:
                bucket = "quarantine"
            elif source_id in traced:
                bucket = "hidden"
            else:
                bucket = "no_trace"
            buckets[bucket].append(source_id)

        self.stdout.write(
            "unmatched_bucket_counts "
            + " ".join(
                f"{bucket}={len(source_ids)}"
                for bucket, source_ids in buckets.items()
            )
        )
        for bucket, bucket_source_ids in buckets.items():
            for source_id in bucket_source_ids:
                self.stdout.write(f"unmatched {source_id} {bucket}")
