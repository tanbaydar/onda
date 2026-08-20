import copy
import json
from datetime import UTC, date, datetime
from unittest.mock import patch

from catalog.models import (
    Artist,
    Event,
    EventIdentity,
    Venue,
)
from ingestion.client import FetchResult
from ingestion.models import RawIngest, SyncRunStatus, SyncRunType
from ingestion.runner import run_sync
from ingestion.tests.test_runner import FakeClient, FakeLock
from ingestion.tests.test_transformer import TransformerHarness
from ingestion.transformer import transform


FIXTURE = "ra_listing_duplicate_event.synthetic.json"
WINDOW_START = date(2026, 8, 24)
WINDOW_END = date(2026, 8, 27)
FIXED_NOW = datetime(2026, 8, 1, 12, 0, tzinfo=UTC)


class WrapperGrainCompletenessTests(TransformerHarness):
    def fetch_result(self, payload):
        return FetchResult(
            status_code=200,
            body_text=json.dumps(payload),
            fetched_at=FIXED_NOW,
        )

    def route_payload(self, client, payload):
        client.route(
            area_ref="8",
            window_start=WINDOW_START,
            window_end=WINDOW_END,
            page_number=1,
            result=self.fetch_result(payload),
        )

    def run_payload(self, payload):
        client = FakeClient()
        lock = FakeLock()
        self.route_payload(client, payload)
        run = run_sync(
            run_type=SyncRunType.NIGHTLY,
            client=client,
            lock=lock,
            window_start=WINDOW_START,
            window_end=WINDOW_END,
            page_size=4,
        )
        return run, client, lock

    def test_duplicate_wrappers_upsert_one_event_and_observe_one_id(self):
        raw = self.make_raw(FIXTURE)

        outcome = transform(raw)

        self.assertEqual(outcome.admitted_count, 4)
        self.assertEqual(outcome.quarantined_count, 0)
        self.assertEqual(outcome.dropped_count, 0)
        self.assertSetEqual(
            set(outcome.observed_source_ids),
            {
                "syn-event-duplicate",
                "syn-event-duplicate-sibling",
            },
        )
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(EventIdentity.objects.count(), 2)
        self.assertEqual(Venue.objects.count(), 1)
        self.assertEqual(Artist.objects.count(), 2)
        self.assertEqual(
            EventIdentity.objects.filter(
                source="ra",
                source_id="syn-event-duplicate",
            ).count(),
            1,
        )

    def test_wrapper_grain_completeness_accepts_duplicate_event_ids(self):
        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            run, client, lock = self.run_payload(self.fixture_json(FIXTURE))

        run.refresh_from_db()
        self.assertEqual(run.status, SyncRunStatus.COMPLETED)
        self.assertEqual(run.seeds_attempted, 1)
        self.assertEqual(run.seeds_failed, 0)
        self.assertIsNone(run.error_summary)
        self.assertEqual(run.events_upserted, 4)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(EventIdentity.objects.count(), 2)
        self.assertEqual(RawIngest.objects.filter(run=run).count(), 1)
        self.assertListEqual(lock.actions, ["acquire", "release"])

    def test_wrapper_coverage_failure_records_numeric_diagnostic(self):
        payload = copy.deepcopy(self.fixture_json(FIXTURE))
        payload["data"]["eventListings"]["data"].pop()

        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            run, client, lock = self.run_payload(payload)

        run.refresh_from_db()
        self.assertEqual(run.status, SyncRunStatus.COMPLETED)
        self.assertEqual(run.seeds_failed, 1)
        self.assertIsNotNone(run.error_summary)
        self.assertIn("wrapper coverage 3 != totalResults 4", run.error_summary)
        self.assertListEqual(lock.actions, ["acquire", "release"])

    def test_missing_event_id_remains_incomplete_with_numeric_diagnostic(self):
        payload = self.fixture_json(
            "ra_listing_missing_event_id.synthetic.json"
        )

        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            run, client, lock = self.run_payload(payload)

        run.refresh_from_db()
        self.assertEqual(run.status, SyncRunStatus.COMPLETED)
        self.assertEqual(run.seeds_failed, 1)
        self.assertIsNotNone(run.error_summary)
        self.assertIn(
            "1/2 listing wrappers missing event.id",
            run.error_summary,
        )
        self.assertListEqual(lock.actions, ["acquire", "release"])
