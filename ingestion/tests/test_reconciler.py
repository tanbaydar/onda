import copy
from datetime import UTC, date, datetime
from unittest.mock import patch

from catalog.models import Event, EventArtist, EventIdentity
from ingestion.models import SyncRunType
from ingestion.reconciler import reconcile
from ingestion.transformer import transform
from ingestion.tests.test_transformer import TransformerHarness


FIXED_NOW = datetime(2026, 8, 1, 12, 0, tzinfo=UTC)
BASELINE_FIXTURE = "ra_listing_complete.synthetic.json"
EVENT_1 = "syn-event-complete-1"
EVENT_2 = "syn-event-complete-2"
BASELINE_WINDOW_START = date(2026, 8, 14)
BASELINE_WINDOW_END = date(2026, 8, 15)


class ReconcilerContractTests(TransformerHarness):
    def transform_baseline(self, *, payload=None):
        raw = self.make_raw(BASELINE_FIXTURE, payload=payload)
        transform(raw)
        return raw

    def identity(self, source_id):
        return EventIdentity.objects.select_related("event").get(
            source="ra",
            source_id=source_id,
        )

    def make_reconcile_run(self, run_type=SyncRunType.NIGHTLY):
        run = self.make_run()
        if run.run_type != run_type:
            run.run_type = run_type
            run.save(update_fields=["run_type"])
        return run

    def reconcile_nightly(
        self,
        observed_source_ids,
        *,
        fetch_complete=True,
        window_start=BASELINE_WINDOW_START,
        window_end=BASELINE_WINDOW_END,
    ):
        run = self.make_reconcile_run()
        reconcile(
            self.seed,
            run,
            observed_source_ids,
            fetch_complete,
            window_start,
            window_end,
        )
        return run

    def identity_state(self):
        field_names = [
            field.attname
            for field in EventIdentity._meta.concrete_fields
        ]
        return sorted(EventIdentity.objects.values_list(*field_names))

    def assert_identity_lifecycle(self, source_id, *, misses, status):
        identity = self.identity(source_id)
        self.assertEqual(identity.misses, misses)
        self.assertEqual(identity.event.status, status)
        return identity

    def test_absence_ladder(self):
        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            self.transform_baseline()
            event_2 = self.identity(EVENT_2)
            event_2_pk = event_2.event_id
            event_2_identity_pk = event_2.pk
            event_2_lineup_pks = set(
                EventArtist.objects.filter(event_id=event_2_pk).values_list(
                    "pk",
                    flat=True,
                )
            )
            self.assert_identity_lifecycle(EVENT_1, misses=0, status="active")
            self.assert_identity_lifecycle(EVENT_2, misses=0, status="active")

            self.reconcile_nightly({EVENT_1})

            self.assert_identity_lifecycle(EVENT_1, misses=0, status="active")
            self.assert_identity_lifecycle(
                EVENT_2,
                misses=1,
                status="unverified",
            )

            self.reconcile_nightly({EVENT_1})

            self.assert_identity_lifecycle(EVENT_1, misses=0, status="active")
            self.assert_identity_lifecycle(
                EVENT_2,
                misses=2,
                status="unverified",
            )

            self.reconcile_nightly({EVENT_1})

            self.assert_identity_lifecycle(EVENT_1, misses=0, status="active")
            final_identity = self.assert_identity_lifecycle(
                EVENT_2,
                misses=3,
                status="hidden",
            )
            self.assertEqual(Event.objects.count(), 2)
            self.assertEqual(EventIdentity.objects.count(), 2)
            self.assertEqual(EventArtist.objects.count(), 2)
            self.assertEqual(final_identity.pk, event_2_identity_pk)
            self.assertEqual(final_identity.event_id, event_2_pk)
            self.assertSetEqual(
                set(
                    EventArtist.objects.filter(
                        event_id=event_2_pk
                    ).values_list("pk", flat=True)
                ),
                event_2_lineup_pks,
            )

    def test_presence_resets(self):
        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            self.transform_baseline()
            self.reconcile_nightly({EVENT_1})
            self.reconcile_nightly({EVENT_1})
            self.assert_identity_lifecycle(
                EVENT_2,
                misses=2,
                status="unverified",
            )

            self.reconcile_nightly({EVENT_1, EVENT_2})

            self.assert_identity_lifecycle(EVENT_2, misses=0, status="active")

    def test_resurrection_from_hidden(self):
        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            self.transform_baseline()
            self.reconcile_nightly({EVENT_1})
            self.reconcile_nightly({EVENT_1})
            self.reconcile_nightly({EVENT_1})
            self.assert_identity_lifecycle(
                EVENT_2,
                misses=3,
                status="hidden",
            )

            self.reconcile_nightly({EVENT_1, EVENT_2})

            self.assert_identity_lifecycle(EVENT_2, misses=0, status="active")

    def test_quarantined_but_listed_resets(self):
        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            self.transform_baseline()
            self.reconcile_nightly({EVENT_1})
            self.reconcile_nightly({EVENT_1})
            self.assert_identity_lifecycle(
                EVENT_2,
                misses=2,
                status="unverified",
            )

            self.reconcile_nightly({EVENT_1, EVENT_2})

            self.assert_identity_lifecycle(EVENT_2, misses=0, status="active")

    def test_incomplete_fetch_changes_nothing(self):
        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            self.transform_baseline()
            self.reconcile_nightly({EVENT_1})
            self.assert_identity_lifecycle(
                EVENT_2,
                misses=1,
                status="unverified",
            )
            identity_state_before = self.identity_state()
            event_statuses_before = sorted(
                Event.objects.values_list("pk", "status")
            )

            self.reconcile_nightly(set(), fetch_complete=False)

            self.assertListEqual(self.identity_state(), identity_state_before)
            self.assertListEqual(
                sorted(Event.objects.values_list("pk", "status")),
                event_statuses_before,
            )
            self.assert_identity_lifecycle(
                EVENT_2,
                misses=1,
                status="unverified",
            )

    def test_past_events_untouched(self):
        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            payload = copy.deepcopy(self.fixture_json(BASELINE_FIXTURE))
            first = payload["data"]["eventListings"]["data"][0]["event"]
            second = payload["data"]["eventListings"]["data"][1]["event"]
            first["date"] = "2026-07-30T00:00:00.000"
            first["startTime"] = "2026-07-30T22:00:00.000"
            second["date"] = "2026-07-31T00:00:00.000"
            second["startTime"] = "2026-07-31T23:30:00.000"
            self.transform_baseline(payload=payload)

            self.reconcile_nightly(
                set(),
                window_start=date(2026, 7, 30),
                window_end=date(2026, 7, 31),
            )

            self.assert_identity_lifecycle(EVENT_1, misses=0, status="active")
            self.assert_identity_lifecycle(EVENT_2, misses=0, status="active")

    def test_backfill_and_replay_never_reconcile(self):
        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            self.transform_baseline()
            for run_type in (SyncRunType.BACKFILL, SyncRunType.REPLAY):
                with self.subTest(run_type=run_type):
                    identity_state_before = self.identity_state()
                    event_statuses_before = sorted(
                        Event.objects.values_list("pk", "status")
                    )
                    run = self.make_reconcile_run(run_type=run_type)

                    reconcile(
                        self.seed,
                        run,
                        set(),
                        True,
                        BASELINE_WINDOW_START,
                        BASELINE_WINDOW_END,
                    )

                    self.assertListEqual(
                        self.identity_state(),
                        identity_state_before,
                    )
                    self.assertListEqual(
                        sorted(Event.objects.values_list("pk", "status")),
                        event_statuses_before,
                    )

    def test_scope_is_per_seed_window(self):
        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            self.transform_baseline()
            identity_state_before = self.identity_state()
            event_statuses_before = sorted(
                Event.objects.values_list("pk", "status")
            )

            self.reconcile_nightly(
                set(),
                window_start=date(2026, 8, 20),
                window_end=date(2026, 8, 21),
            )

            self.assertListEqual(self.identity_state(), identity_state_before)
            self.assertListEqual(
                sorted(Event.objects.values_list("pk", "status")),
                event_statuses_before,
            )
            self.assert_identity_lifecycle(EVENT_1, misses=0, status="active")
            self.assert_identity_lifecycle(EVENT_2, misses=0, status="active")
