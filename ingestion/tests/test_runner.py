from datetime import UTC, date, datetime
from unittest.mock import patch

from catalog.models import (
    Artist,
    City,
    CityIdentity,
    Event,
    EventIdentity,
    Venue,
)
from ingestion.client import FetchResult
from ingestion.models import (
    RawIngest,
    RawProcessingStatus,
    RejectedIngest,
    SyncRun,
    SyncRunStatus,
    SyncRunType,
    TrackedSourcePage,
)
from ingestion.runner import SyncAlreadyRunning, run_sync
from ingestion.transformer import transform
from ingestion.tests.test_transformer import TransformerHarness


FIXED_NOW = datetime(2026, 8, 1, 12, 0, tzinfo=UTC)
PAGINATION_START = date(2026, 8, 22)
PAGINATION_END = date(2026, 8, 23)
BASELINE_START = date(2026, 8, 14)
BASELINE_END = date(2026, 8, 15)


class FakeClient:
    def __init__(self):
        self.routes = {}
        self.requests = []

    def route(
        self,
        *,
        area_ref,
        window_start,
        window_end,
        page_number,
        result,
    ):
        self.routes[
            (area_ref, window_start, window_end, page_number)
        ] = result

    def fetch_page(
        self,
        seed,
        window_start,
        window_end,
        page_number,
        page_size,
    ):
        request = (
            seed.area_ref,
            window_start,
            window_end,
            page_number,
            page_size,
        )
        self.requests.append(request)
        result = self.routes[
            (seed.area_ref, window_start, window_end, page_number)
        ]
        if isinstance(result, BaseException):
            raise result
        return result


class FakeLock:
    def __init__(self, *, acquired=True):
        self.acquired = acquired
        self.actions = []

    def acquire(self):
        self.actions.append("acquire")
        return self.acquired

    def release(self):
        self.actions.append("release")


class UnexpectedClientBug(RuntimeError):
    pass


class RunnerContractTests(TransformerHarness):
    def success_result(self, fixture_name):
        return FetchResult(
            status_code=200,
            body_text=self.fixture_bytes(fixture_name).decode("utf-8"),
            fetched_at=FIXED_NOW,
            error=None,
        )

    def transport_failure(self, message):
        return FetchResult(
            status_code=None,
            body_text=None,
            fetched_at=FIXED_NOW,
            error=message,
        )

    def route_pagination(self, client, *, page_2_result=None):
        client.route(
            area_ref="8",
            window_start=PAGINATION_START,
            window_end=PAGINATION_END,
            page_number=1,
            result=self.success_result(
                "ra_listing_paginated_page_1.synthetic.json"
            ),
        )
        client.route(
            area_ref="8",
            window_start=PAGINATION_START,
            window_end=PAGINATION_END,
            page_number=2,
            result=page_2_result
            or self.success_result(
                "ra_listing_paginated_page_2.synthetic.json"
            ),
        )

    def run_pagination(self, client, lock):
        return run_sync(
            run_type=SyncRunType.NIGHTLY,
            client=client,
            lock=lock,
            window_start=PAGINATION_START,
            window_end=PAGINATION_END,
            page_size=2,
        )

    def test_happy_path_two_pages(self):
        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            client = FakeClient()
            lock = FakeLock()
            self.route_pagination(client)

            run = self.run_pagination(client, lock)

            raws = list(RawIngest.objects.order_by("page_number"))
            self.assertEqual(len(raws), 2)
            self.assertEqual(
                raws[0].response_body,
                self.fixture_bytes(
                    "ra_listing_paginated_page_1.synthetic.json"
                ).decode("utf-8"),
            )
            self.assertEqual(
                raws[1].response_body,
                self.fixture_bytes(
                    "ra_listing_paginated_page_2.synthetic.json"
                ).decode("utf-8"),
            )
            self.assertListEqual(
                [raw.processing_status for raw in raws],
                [
                    RawProcessingStatus.PROCESSED,
                    RawProcessingStatus.PROCESSED,
                ],
            )
            self.assertEqual(Event.objects.count(), 3)
            self.assertEqual(Venue.objects.count(), 1)
            self.assertEqual(Artist.objects.count(), 3)
            self.assertEqual(EventIdentity.objects.count(), 3)
            run.refresh_from_db()
            self.assertEqual(run.status, SyncRunStatus.COMPLETED)
            self.assertEqual(run.seeds_attempted, 1)
            self.assertEqual(run.seeds_failed, 0)
            self.assertEqual(run.events_upserted, 3)
            self.assertEqual(run.events_quarantined, 0)
            self.assertEqual(run.events_dropped, 0)
            self.assertListEqual(
                client.requests,
                [
                    ("8", PAGINATION_START, PAGINATION_END, 1, 2),
                    ("8", PAGINATION_START, PAGINATION_END, 2, 2),
                ],
            )
            self.assertListEqual(lock.actions, ["acquire", "release"])

    def test_transport_failure_seed(self):
        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            client = FakeClient()
            lock = FakeLock()
            failure_message = "timeout after 3 retries"
            self.route_pagination(
                client,
                page_2_result=self.transport_failure(failure_message),
            )

            run = self.run_pagination(client, lock)

            raws = list(RawIngest.objects.order_by("page_number"))
            self.assertEqual(len(raws), 2)
            self.assertEqual(
                raws[0].processing_status,
                RawProcessingStatus.PROCESSED,
            )
            self.assertEqual(raws[0].http_status, 200)
            self.assertEqual(
                raws[0].response_body,
                self.fixture_bytes(
                    "ra_listing_paginated_page_1.synthetic.json"
                ).decode("utf-8"),
            )
            self.assertIsNone(raws[1].http_status)
            self.assertIsNone(raws[1].response_body)
            self.assertEqual(Event.objects.count(), 2)
            self.assertEqual(EventIdentity.objects.count(), 2)
            self.assertSetEqual(
                set(EventIdentity.objects.values_list("misses", flat=True)),
                {0},
            )
            run.refresh_from_db()
            self.assertEqual(run.status, SyncRunStatus.COMPLETED)
            self.assertEqual(run.seeds_attempted, 1)
            self.assertEqual(run.seeds_failed, 1)
            self.assertIn(failure_message, run.error_summary)
            self.assertListEqual(lock.actions, ["acquire", "release"])

    def test_failed_payload_blocks_reconciliation(self):
        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            client = FakeClient()
            lock = FakeLock()
            self.route_pagination(
                client,
                page_2_result=self.success_result(
                    "ra_listing_malformed_payload.synthetic.txt"
                ),
            )

            run = self.run_pagination(client, lock)

            raws = list(RawIngest.objects.order_by("page_number"))
            self.assertEqual(len(raws), 2)
            self.assertEqual(
                raws[0].processing_status,
                RawProcessingStatus.PROCESSED,
            )
            self.assertEqual(raws[1].http_status, 200)
            self.assertEqual(
                raws[1].response_body,
                self.fixture_bytes(
                    "ra_listing_malformed_payload.synthetic.txt"
                ).decode("utf-8"),
            )
            self.assertEqual(
                raws[1].processing_status,
                RawProcessingStatus.FAILED,
            )
            self.assertEqual(Event.objects.count(), 2)
            self.assertEqual(EventIdentity.objects.count(), 2)
            self.assertSetEqual(
                set(EventIdentity.objects.values_list("misses", flat=True)),
                {0},
            )
            run.refresh_from_db()
            self.assertEqual(run.status, SyncRunStatus.COMPLETED)
            self.assertEqual(run.seeds_failed, 1)
            self.assertListEqual(lock.actions, ["acquire", "release"])

    def test_unmapped_seed_refused_before_fetch(self):
        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            unmapped = TrackedSourcePage.objects.create(
                source="ra",
                area_ref="syn-unmapped-area",
                label="Synthetic Unmapped Area",
            )
            client = FakeClient()
            lock = FakeLock()
            client.route(
                area_ref="8",
                window_start=BASELINE_START,
                window_end=BASELINE_END,
                page_number=1,
                result=self.success_result(
                    "ra_listing_complete.synthetic.json"
                ),
            )

            run = run_sync(
                run_type=SyncRunType.NIGHTLY,
                client=client,
                lock=lock,
                window_start=BASELINE_START,
                window_end=BASELINE_END,
                page_size=2,
            )

            self.assertFalse(
                any(request[0] == unmapped.area_ref for request in client.requests)
            )
            self.assertEqual(
                RawIngest.objects.filter(seed=unmapped).count(),
                0,
            )
            self.assertEqual(
                RawIngest.objects.filter(seed=self.seed).count(),
                1,
            )
            self.assertEqual(
                RawIngest.objects.get(seed=self.seed).processing_status,
                RawProcessingStatus.PROCESSED,
            )
            run.refresh_from_db()
            self.assertEqual(run.status, SyncRunStatus.COMPLETED)
            self.assertEqual(run.seeds_attempted, 2)
            self.assertEqual(run.seeds_failed, 1)
            self.assertIsNotNone(run.error_summary)
            self.assertIn(unmapped.area_ref, run.error_summary)
            self.assertListEqual(lock.actions, ["acquire", "release"])

    def test_advisory_lock_refuses_second_run(self):
        client = FakeClient()
        lock = FakeLock(acquired=False)
        runs_before = SyncRun.objects.count()

        with self.assertRaises(SyncAlreadyRunning):
            run_sync(
                run_type=SyncRunType.NIGHTLY,
                client=client,
                lock=lock,
                window_start=BASELINE_START,
                window_end=BASELINE_END,
                page_size=2,
            )

        self.assertEqual(SyncRun.objects.count(), runs_before)
        self.assertListEqual(client.requests, [])
        self.assertListEqual(lock.actions, ["acquire"])

    def test_recovery_sweep_transforms_but_never_reconciles(self):
        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            prior_catalog_raw = self.make_raw(
                "ra_listing_sold_out.synthetic.json"
            )
            transform(prior_catalog_raw)
            sold_out_identity = EventIdentity.objects.get(
                source="ra",
                source_id="syn-event-sold-out",
            )
            self.assertEqual(sold_out_identity.misses, 0)

            crashed_run = self.make_run()
            crashed_run.status = SyncRunStatus.CRASHED
            crashed_run.save(update_fields=["status"])
            leftover = self.make_raw(
                "ra_listing_tba_lineup.synthetic.json",
                run=crashed_run,
            )
            sold_out_leftover = self.make_raw(
                "ra_listing_sold_out.synthetic.json",
                run=crashed_run,
            )
            self.assertEqual(
                leftover.processing_status,
                RawProcessingStatus.PENDING,
            )

            client = FakeClient()
            lock = FakeLock()
            client.route(
                area_ref="8",
                window_start=BASELINE_START,
                window_end=date(2026, 8, 19),
                page_number=1,
                result=self.success_result(
                    "ra_listing_complete.synthetic.json"
                ),
            )

            run_sync(
                run_type=SyncRunType.NIGHTLY,
                client=client,
                lock=lock,
                window_start=BASELINE_START,
                window_end=date(2026, 8, 19),
                page_size=2,
            )

            leftover.refresh_from_db()
            self.assertEqual(
                leftover.processing_status,
                RawProcessingStatus.PROCESSED,
            )
            sold_out_leftover.refresh_from_db()
            self.assertEqual(
                sold_out_leftover.processing_status,
                RawProcessingStatus.PROCESSED,
            )
            self.assertTrue(
                RejectedIngest.objects.filter(
                    raw_ingest=leftover,
                    entity_ref="syn-event-tba",
                ).exists()
            )
            sold_out_identity.refresh_from_db()
            self.assertEqual(sold_out_identity.misses, 1)
            self.assertEqual(sold_out_identity.event.status, "unverified")
            self.assertSetEqual(
                set(
                    EventIdentity.objects.filter(
                        source_id__in={
                            "syn-event-complete-1",
                            "syn-event-complete-2",
                        }
                    ).values_list("misses", flat=True)
                ),
                {0},
            )
            self.assertListEqual(lock.actions, ["acquire", "release"])

    def test_crash_marks_run(self):
        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            client = FakeClient()
            lock = FakeLock()
            self.route_pagination(
                client,
                page_2_result=UnexpectedClientBug(
                    "synthetic client programming defect"
                ),
            )

            with self.assertRaisesRegex(
                UnexpectedClientBug,
                "synthetic client programming defect",
            ):
                self.run_pagination(client, lock)

            run = SyncRun.objects.get()
            self.assertEqual(run.status, SyncRunStatus.CRASHED)
            self.assertIsNotNone(run.error_summary)
            self.assertIn(
                "synthetic client programming defect",
                run.error_summary,
            )
            self.assertEqual(RawIngest.objects.count(), 1)
            archived = RawIngest.objects.get()
            self.assertEqual(archived.http_status, 200)
            self.assertEqual(
                archived.response_body,
                self.fixture_bytes(
                    "ra_listing_paginated_page_1.synthetic.json"
                ).decode("utf-8"),
            )
            self.assertListEqual(lock.actions, ["acquire", "release"])

    def test_telemetry_definition(self):
        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            prior_raw = self.make_raw("ra_listing_complete.synthetic.json")
            transform(prior_raw)
            boston = City.objects.get(
                country_code="US",
                region_code="MA",
                name="Boston",
            )
            CityIdentity.objects.update_or_create(
                source="ra",
                source_id="530",
                defaults={"city": boston},
            )
            TrackedSourcePage.objects.create(
                source="ra",
                area_ref="530",
                label="Boston",
            )
            client = FakeClient()
            lock = FakeLock()
            client.route(
                area_ref="8",
                window_start=date(2026, 8, 14),
                window_end=date(2026, 8, 17),
                page_number=1,
                result=self.success_result(
                    "ra_listing_complete.synthetic.json"
                ),
            )
            client.route(
                area_ref="530",
                window_start=date(2026, 8, 14),
                window_end=date(2026, 8, 17),
                page_number=1,
                result=self.success_result(
                    "ra_listing_tba_lineup.synthetic.json"
                ),
            )

            run = run_sync(
                run_type=SyncRunType.NIGHTLY,
                client=client,
                lock=lock,
                window_start=date(2026, 8, 14),
                window_end=date(2026, 8, 17),
                page_size=100,
            )

            run.refresh_from_db()
            self.assertEqual(run.status, SyncRunStatus.COMPLETED)
            self.assertEqual(run.seeds_attempted, 2)
            self.assertEqual(run.seeds_failed, 0)
            self.assertEqual(run.events_upserted, 2)
            self.assertEqual(run.events_quarantined, 1)
            self.assertEqual(run.events_dropped, 0)
            self.assertEqual(
                RejectedIngest.objects.filter(
                    raw_ingest__run=run
                ).count(),
                1,
            )
            self.assertListEqual(lock.actions, ["acquire", "release"])
