import copy
import json
from datetime import date
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from catalog.models import City, CityIdentity, EventIdentity
from ingestion.models import (
    RawIngest,
    RawProcessingStatus,
    RejectedIngest,
    RejectionReason,
    SyncRun,
    SyncRunStatus,
    SyncRunType,
    TrackedSourcePage,
)
from ingestion.transformer import transform


FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "recon"
    / "fixtures"
    / "ra_listing_complete.synthetic.json"
)


class TicketingIngestionTests(TestCase):
    def setUp(self):
        city, _ = City.objects.get_or_create(
            country_code="US",
            region_code="NY",
            name="New York City",
            defaults={
                "region_name": "New York",
                "timezone": "America/New_York",
            },
        )
        CityIdentity.objects.update_or_create(
            source="ra",
            source_id="8",
            defaults={"city": city},
        )
        self.seed, _ = TrackedSourcePage.objects.get_or_create(
            source="ra",
            area_ref="8",
            defaults={"label": "New York City"},
        )

    def make_raw(self, payload):
        run = SyncRun.objects.create(
            run_type=SyncRunType.NIGHTLY,
            status=SyncRunStatus.RUNNING,
            started_at=timezone.now(),
        )
        return RawIngest.objects.create(
            seed=self.seed,
            run=run,
            window_start=date(2026, 8, 1),
            window_end=date(2026, 8, 31),
            page_number=1,
            page_size=100,
            response_body=json.dumps(payload),
            http_status=200,
            fetched_at=timezone.now(),
            processing_status=RawProcessingStatus.PENDING,
        )

    def ticketing_payload(self):
        payload = json.loads(FIXTURE.read_text())
        events = payload["data"]["eventListings"]["data"]
        events[0]["event"]["isTicketed"] = True
        events[1]["event"]["isTicketed"] = False
        absent = copy.deepcopy(events[1])
        absent["id"] = "syn-listing-ticket-unknown"
        absent["event"]["id"] = "syn-event-ticket-unknown"
        absent["event"]["title"] = "Synthetic Ticket Status Unknown"
        absent["event"].pop("isTicketed", None)
        events.append(absent)
        payload["data"]["eventListings"]["totalResults"] = 3
        return payload

    def test_transformer_persists_true_false_and_absent_ticket_status(self):
        transform(self.make_raw(self.ticketing_payload()))

        statuses = {
            identity.source_id: identity.event.is_ticketed
            for identity in EventIdentity.objects.select_related("event").filter(
                source_id__in={
                    "syn-event-complete-1",
                    "syn-event-complete-2",
                    "syn-event-ticket-unknown",
                }
            )
        }
        self.assertEqual(
            statuses,
            {
                "syn-event-complete-1": True,
                "syn-event-complete-2": False,
                "syn-event-ticket-unknown": None,
            },
        )

    def test_backfill_updates_from_latest_archive_and_reports_counts(self):
        baseline = self.ticketing_payload()
        for listing in baseline["data"]["eventListings"]["data"]:
            listing["event"].pop("isTicketed", None)
        transform(self.make_raw(baseline))

        archived = self.ticketing_payload()
        archived_events = archived["data"]["eventListings"]["data"]
        archived_events[1]["event"].pop("isTicketed", None)
        unmatched = copy.deepcopy(archived_events[0])
        unmatched["id"] = "syn-listing-ticket-unmatched"
        unmatched["event"]["id"] = "syn-event-ticket-unmatched"
        unmatched["event"]["isTicketed"] = False
        archived_events.append(unmatched)
        archived_raw = self.make_raw(archived)

        output = StringIO()
        call_command("backfill_is_ticketed", stdout=output)

        self.assertEqual(
            output.getvalue().strip(),
            "updated=1 unknown=2 unmatched=1",
        )
        mapped = EventIdentity.objects.select_related("event").get(
            source="ra",
            source_id="syn-event-complete-1",
        )
        self.assertTrue(mapped.event.is_ticketed)

        second_output = StringIO()
        call_command("backfill_is_ticketed", stdout=second_output)
        self.assertEqual(
            second_output.getvalue().strip(),
            "updated=0 unknown=2 unmatched=1",
        )

        RejectedIngest.objects.create(
            raw_ingest=archived_raw,
            entity_index=99,
            entity_ref="syn-event-ticket-unmatched",
            reason=RejectionReason.NO_ARTIST,
            rejected_at=timezone.now(),
        )
        no_trace_payload = self.ticketing_payload()
        no_trace_event = no_trace_payload["data"]["eventListings"]["data"][0]
        no_trace_event["event"]["id"] = "syn-event-ticket-no-trace"
        no_trace_payload["data"]["eventListings"]["data"] = [no_trace_event]
        self.make_raw(no_trace_payload)

        diagnostic_output = StringIO()
        call_command(
            "backfill_is_ticketed",
            show_unmatched=True,
            stdout=diagnostic_output,
        )
        self.assertEqual(
            diagnostic_output.getvalue().strip().splitlines(),
            [
                "updated=0 unknown=2 unmatched=2",
                "unmatched_bucket_counts quarantine=1 hidden=0 no_trace=1",
                "unmatched syn-event-ticket-unmatched quarantine",
                "unmatched syn-event-ticket-no-trace no_trace",
            ],
        )
