import copy
import json
from datetime import date, time
from pathlib import Path

from django.test import TestCase
from django.utils import timezone

from catalog.models import (
    Artist,
    ArtistIdentity,
    City,
    CityIdentity,
    Event,
    EventArtist,
    EventIdentity,
    Venue,
    VenueIdentity,
)
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


FIXTURE_DIR = (
    Path(__file__).resolve().parents[2] / "docs" / "recon" / "fixtures"
)
DEFAULT_WINDOW_START = date(2026, 8, 1)
DEFAULT_WINDOW_END = date(2026, 8, 31)


class TransformerHarness(TestCase):
    def setUp(self):
        self.city, _ = City.objects.get_or_create(
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
            defaults={"city": self.city},
        )
        self.seed, _ = TrackedSourcePage.objects.get_or_create(
            source="ra",
            area_ref="8",
            defaults={"label": "New York City"},
        )

    def make_run(self):
        return SyncRun.objects.create(
            run_type=SyncRunType.NIGHTLY,
            status=SyncRunStatus.RUNNING,
            started_at=timezone.now(),
        )

    def fixture_bytes(self, fixture_name):
        return (FIXTURE_DIR / fixture_name).read_bytes()

    def fixture_json(self, fixture_name):
        return json.loads(self.fixture_bytes(fixture_name))

    def make_raw(self, fixture_name, *, payload=None, run=None):
        run = run or self.make_run()
        if payload is None:
            body_bytes = self.fixture_bytes(fixture_name)
            response_body = body_bytes.decode("utf-8")
        else:
            response_body = json.dumps(payload)
            body_bytes = response_body.encode("utf-8")

        pagination = fixture_name.startswith("ra_listing_paginated_page_")
        if pagination:
            window_start = date(2026, 8, 22)
            window_end = date(2026, 8, 23)
            page_size = 2
            page_number = 1 if "_page_1." in fixture_name else 2
        else:
            window_start = DEFAULT_WINDOW_START
            window_end = DEFAULT_WINDOW_END
            page_size = 100
            page_number = 1

        raw = RawIngest.objects.create(
            seed=self.seed,
            run=run,
            window_start=window_start,
            window_end=window_end,
            page_number=page_number,
            page_size=page_size,
            response_body=response_body,
            http_status=200,
            fetched_at=timezone.now(),
            processing_status=RawProcessingStatus.PENDING,
        )
        self.assertEqual(raw.response_body.encode("utf-8"), body_bytes)
        return raw

    def assert_outcome(
        self,
        outcome,
        *,
        admitted,
        quarantined,
        dropped,
        observed,
    ):
        self.assertEqual(outcome.admitted_count, admitted)
        self.assertEqual(outcome.quarantined_count, quarantined)
        self.assertEqual(outcome.dropped_count, dropped)
        self.assertSetEqual(set(outcome.observed_source_ids), set(observed))

    def assert_raw_status(self, raw, expected):
        raw.refresh_from_db()
        self.assertEqual(raw.processing_status, expected)

    def assert_graph_counts(
        self,
        *,
        events,
        venues,
        artists,
        event_artists,
        event_identities,
        venue_identities,
        artist_identities,
        rejections,
    ):
        self.assertEqual(Event.objects.count(), events)
        self.assertEqual(Venue.objects.count(), venues)
        self.assertEqual(Artist.objects.count(), artists)
        self.assertEqual(EventArtist.objects.count(), event_artists)
        self.assertEqual(EventIdentity.objects.count(), event_identities)
        self.assertEqual(VenueIdentity.objects.count(), venue_identities)
        self.assertEqual(ArtistIdentity.objects.count(), artist_identities)
        self.assertEqual(RejectedIngest.objects.count(), rejections)

    def assert_identity_values(
        self,
        *,
        events=(),
        venues=(),
        artists=(),
    ):
        self.assertSetEqual(
            set(EventIdentity.objects.values_list("source", "source_id")),
            {("ra", source_id) for source_id in events},
        )
        self.assertSetEqual(
            set(VenueIdentity.objects.values_list("source", "source_id")),
            {("ra", source_id) for source_id in venues},
        )
        self.assertSetEqual(
            set(ArtistIdentity.objects.values_list("source", "source_id")),
            {("ra", source_id) for source_id in artists},
        )

    def event_for_source_id(self, source_id):
        return EventIdentity.objects.select_related("event").get(
            source="ra",
            source_id=source_id,
        ).event

    def assert_rejection(self, raw, *, entity_index, entity_ref, reason):
        rejection = RejectedIngest.objects.get(raw_ingest=raw)
        self.assertEqual(rejection.entity_index, entity_index)
        self.assertEqual(rejection.entity_ref, entity_ref)
        self.assertEqual(rejection.reason, reason)
        self.assertEqual(rejection.raw_ingest_id, raw.id)
        self.assertIsNotNone(rejection.rejected_at)


class TransformerFixtureContractTests(TransformerHarness):
    def test_complete_representative_page(self):
        raw = self.make_raw("ra_listing_complete.synthetic.json")

        outcome = transform(raw)

        self.assert_outcome(
            outcome,
            admitted=2,
            quarantined=0,
            dropped=0,
            observed={"syn-event-complete-1", "syn-event-complete-2"},
        )
        self.assert_raw_status(raw, RawProcessingStatus.PROCESSED)
        self.assert_graph_counts(
            events=2,
            venues=1,
            artists=2,
            event_artists=2,
            event_identities=2,
            venue_identities=1,
            artist_identities=2,
            rejections=0,
        )
        self.assert_identity_values(
            events={"syn-event-complete-1", "syn-event-complete-2"},
            venues={"syn-venue-complete"},
            artists={"syn-artist-complete-1", "syn-artist-complete-2"},
        )
        venue = Venue.objects.get(name="Synthetic Hall")
        self.assertEqual(venue.city, self.city)
        first = self.event_for_source_id("syn-event-complete-1")
        second = self.event_for_source_id("syn-event-complete-2")
        self.assertEqual(first.event_date, date(2026, 8, 14))
        self.assertEqual(first.start_time, time(22, 0))
        self.assertEqual(
            first.cover_image_url,
            "https://example.invalid/flyers/complete-1.jpg",
        )
        self.assertEqual(second.event_date, date(2026, 8, 15))
        self.assertEqual(second.start_time, time(23, 30))
        self.assertIsNone(second.cover_image_url)
        self.assertEqual(first.venue_id, second.venue_id)
        self.assertSetEqual(
            set(
                EventArtist.objects.values_list(
                    "event__external_identities__source_id",
                    "position",
                )
            ),
            {
                ("syn-event-complete-1", 1),
                ("syn-event-complete-2", 1),
            },
        )

    def test_date_only(self):
        raw = self.make_raw("ra_listing_date_only.synthetic.json")

        outcome = transform(raw)

        self.assert_outcome(
            outcome,
            admitted=1,
            quarantined=0,
            dropped=0,
            observed={"syn-event-date-only"},
        )
        self.assert_raw_status(raw, RawProcessingStatus.PROCESSED)
        self.assert_graph_counts(
            events=1,
            venues=1,
            artists=1,
            event_artists=1,
            event_identities=1,
            venue_identities=1,
            artist_identities=1,
            rejections=0,
        )
        self.assert_identity_values(
            events={"syn-event-date-only"},
            venues={"syn-venue-date-only"},
            artists={"syn-artist-date-only"},
        )
        event = self.event_for_source_id("syn-event-date-only")
        self.assertEqual(event.event_date, date(2026, 8, 16))
        self.assertIsNone(event.start_time)
        self.assertIsNone(event.cover_image_url)
        self.assertEqual(event.venue.name, "Synthetic Date Hall")
        self.assertEqual(event.venue.city, self.city)
        self.assertEqual(event.event_artists.get().position, 1)

    def test_tba_lineup(self):
        raw = self.make_raw("ra_listing_tba_lineup.synthetic.json")

        outcome = transform(raw)

        self.assert_outcome(
            outcome,
            admitted=0,
            quarantined=1,
            dropped=0,
            observed={"syn-event-tba"},
        )
        self.assert_raw_status(raw, RawProcessingStatus.PROCESSED)
        self.assert_graph_counts(
            events=0,
            venues=0,
            artists=0,
            event_artists=0,
            event_identities=0,
            venue_identities=0,
            artist_identities=0,
            rejections=1,
        )
        self.assert_identity_values()
        self.assert_rejection(
            raw,
            entity_index=0,
            entity_ref="syn-event-tba",
            reason=RejectionReason.NO_ARTIST,
        )

    def test_festival_lineup(self):
        raw = self.make_raw("ra_listing_festival.synthetic.json")

        outcome = transform(raw)

        self.assert_outcome(
            outcome,
            admitted=1,
            quarantined=0,
            dropped=0,
            observed={"syn-event-festival"},
        )
        self.assert_raw_status(raw, RawProcessingStatus.PROCESSED)
        self.assert_graph_counts(
            events=1,
            venues=1,
            artists=3,
            event_artists=3,
            event_identities=1,
            venue_identities=1,
            artist_identities=3,
            rejections=0,
        )
        self.assert_identity_values(
            events={"syn-event-festival"},
            venues={"syn-venue-festival"},
            artists={
                "syn-artist-festival-1",
                "syn-artist-festival-2",
                "syn-artist-festival-3",
            },
        )
        event = self.event_for_source_id("syn-event-festival")
        self.assertEqual(event.event_date, date(2026, 8, 18))
        self.assertEqual(event.start_time, time(14, 0))
        self.assertEqual(
            event.cover_image_url,
            "https://example.invalid/flyers/festival.jpg",
        )
        self.assertEqual(event.venue.name, "Synthetic Festival Grounds")
        self.assertEqual(event.venue.city, self.city)
        self.assertListEqual(
            list(
                EventArtist.objects.order_by("position").values_list(
                    "artist__name",
                    "position",
                )
            ),
            [
                ("Synthetic Opener", 1),
                ("Synthetic Middle", 2),
                ("Synthetic Headliner", 3),
            ],
        )

    def test_sold_out(self):
        raw = self.make_raw("ra_listing_sold_out.synthetic.json")

        outcome = transform(raw)

        self.assert_outcome(
            outcome,
            admitted=1,
            quarantined=0,
            dropped=0,
            observed={"syn-event-sold-out"},
        )
        self.assert_raw_status(raw, RawProcessingStatus.PROCESSED)
        self.assert_graph_counts(
            events=1,
            venues=1,
            artists=1,
            event_artists=1,
            event_identities=1,
            venue_identities=1,
            artist_identities=1,
            rejections=0,
        )
        self.assert_identity_values(
            events={"syn-event-sold-out"},
            venues={"syn-venue-sold-out"},
            artists={"syn-artist-sold-out"},
        )
        event = self.event_for_source_id("syn-event-sold-out")
        self.assertEqual(event.event_date, date(2026, 8, 19))
        self.assertEqual(event.start_time, time(21, 0))
        self.assertIsNone(event.cover_image_url)
        self.assertEqual(event.status, "active")
        self.assertEqual(event.venue.name, "Synthetic Sold Out Hall")
        self.assertEqual(event.venue.city, self.city)
        self.assertEqual(event.event_artists.get().position, 1)

    def test_cancellation_text_only(self):
        raw = self.make_raw("ra_listing_cancelled_title.synthetic.json")

        outcome = transform(raw)

        self.assert_outcome(
            outcome,
            admitted=1,
            quarantined=0,
            dropped=0,
            observed={"syn-event-cancelled-title"},
        )
        self.assert_raw_status(raw, RawProcessingStatus.PROCESSED)
        self.assert_graph_counts(
            events=1,
            venues=1,
            artists=1,
            event_artists=1,
            event_identities=1,
            venue_identities=1,
            artist_identities=1,
            rejections=0,
        )
        self.assert_identity_values(
            events={"syn-event-cancelled-title"},
            venues={"syn-venue-cancelled-title"},
            artists={"syn-artist-cancelled-title"},
        )
        event = self.event_for_source_id("syn-event-cancelled-title")
        self.assertEqual(event.title, "CANCELLED: Synthetic Night")
        self.assertEqual(event.event_date, date(2026, 8, 20))
        self.assertEqual(event.start_time, time(22, 0))
        self.assertIsNone(event.cover_image_url)
        self.assertEqual(event.status, "active")
        self.assertEqual(event.venue.name, "Synthetic Cancellation Hall")
        self.assertEqual(event.venue.city, self.city)
        self.assertEqual(event.event_artists.get().position, 1)

    def test_structurally_malformed_event(self):
        raw = self.make_raw("ra_listing_malformed_event.synthetic.json")

        outcome = transform(raw)

        self.assert_outcome(
            outcome,
            admitted=1,
            quarantined=1,
            dropped=0,
            observed={"syn-event-malformed", "syn-event-malformed-sibling"},
        )
        self.assert_raw_status(raw, RawProcessingStatus.PROCESSED)
        self.assert_graph_counts(
            events=1,
            venues=1,
            artists=1,
            event_artists=1,
            event_identities=1,
            venue_identities=1,
            artist_identities=1,
            rejections=1,
        )
        self.assert_identity_values(
            events={"syn-event-malformed-sibling"},
            venues={"syn-venue-malformed-sibling"},
            artists={"syn-artist-malformed-sibling"},
        )
        self.assert_rejection(
            raw,
            entity_index=0,
            entity_ref="syn-event-malformed",
            reason=RejectionReason.PARSE_FAILURE,
        )
        event = self.event_for_source_id("syn-event-malformed-sibling")
        self.assertEqual(event.event_date, date(2026, 8, 21))
        self.assertEqual(event.start_time, time(23, 0))
        self.assertIsNone(event.cover_image_url)
        self.assertEqual(event.venue.name, "Synthetic Healthy Hall")
        self.assertEqual(event.venue.city, self.city)
        self.assertEqual(event.event_artists.get().position, 1)

    def test_missing_event_id(self):
        raw = self.make_raw("ra_listing_missing_event_id.synthetic.json")

        outcome = transform(raw)

        self.assert_outcome(
            outcome,
            admitted=1,
            quarantined=1,
            dropped=0,
            observed={"syn-event-missing-id-sibling"},
        )
        self.assert_raw_status(raw, RawProcessingStatus.PROCESSED)
        self.assert_graph_counts(
            events=1,
            venues=1,
            artists=1,
            event_artists=1,
            event_identities=1,
            venue_identities=1,
            artist_identities=1,
            rejections=1,
        )
        self.assert_identity_values(
            events={"syn-event-missing-id-sibling"},
            venues={"syn-venue-missing-id-sibling"},
            artists={"syn-artist-missing-id-sibling"},
        )
        self.assert_rejection(
            raw,
            entity_index=0,
            entity_ref=None,
            reason=RejectionReason.PARSE_FAILURE,
        )
        event = self.event_for_source_id("syn-event-missing-id-sibling")
        self.assertEqual(event.venue.name, "Synthetic Missing ID Healthy Hall")
        self.assertEqual(event.venue.city, self.city)

    def test_whitespace_only_title(self):
        raw = self.make_raw("ra_listing_empty_title.synthetic.json")

        outcome = transform(raw)

        self.assert_outcome(
            outcome,
            admitted=0,
            quarantined=1,
            dropped=0,
            observed={"syn-event-empty-title"},
        )
        self.assert_raw_status(raw, RawProcessingStatus.PROCESSED)
        self.assert_graph_counts(
            events=0,
            venues=0,
            artists=0,
            event_artists=0,
            event_identities=0,
            venue_identities=0,
            artist_identities=0,
            rejections=1,
        )
        self.assert_identity_values()
        self.assert_rejection(
            raw,
            entity_index=0,
            entity_ref="syn-event-empty-title",
            reason=RejectionReason.EMPTY_TITLE,
        )

    def test_string_but_unparseable_date(self):
        raw = self.make_raw("ra_listing_bad_date.synthetic.json")

        outcome = transform(raw)

        self.assert_outcome(
            outcome,
            admitted=0,
            quarantined=1,
            dropped=0,
            observed={"syn-event-bad-date"},
        )
        self.assert_raw_status(raw, RawProcessingStatus.PROCESSED)
        self.assert_graph_counts(
            events=0,
            venues=0,
            artists=0,
            event_artists=0,
            event_identities=0,
            venue_identities=0,
            artist_identities=0,
            rejections=1,
        )
        self.assert_identity_values()
        self.assert_rejection(
            raw,
            entity_index=0,
            entity_ref="syn-event-bad-date",
            reason=RejectionReason.BAD_DATE,
        )

    def test_whole_payload_failure(self):
        raw = self.make_raw("ra_listing_malformed_payload.synthetic.txt")
        archived_body = raw.response_body

        outcome = transform(raw)

        self.assert_outcome(
            outcome,
            admitted=0,
            quarantined=0,
            dropped=0,
            observed=set(),
        )
        self.assert_raw_status(raw, RawProcessingStatus.FAILED)
        self.assertEqual(raw.response_body, archived_body)
        self.assertEqual(
            raw.response_body.encode("utf-8"),
            self.fixture_bytes("ra_listing_malformed_payload.synthetic.txt"),
        )
        self.assert_graph_counts(
            events=0,
            venues=0,
            artists=0,
            event_artists=0,
            event_identities=0,
            venue_identities=0,
            artist_identities=0,
            rejections=0,
        )
        self.assert_identity_values()

    def test_paginated_page_1(self):
        raw = self.make_raw("ra_listing_paginated_page_1.synthetic.json")

        outcome = transform(raw)

        self.assertEqual(raw.window_start, date(2026, 8, 22))
        self.assertEqual(raw.window_end, date(2026, 8, 23))
        self.assertEqual(raw.page_size, 2)
        self.assertEqual(raw.page_number, 1)
        self.assert_outcome(
            outcome,
            admitted=2,
            quarantined=0,
            dropped=0,
            observed={"syn-event-page-1-a", "syn-event-page-1-b"},
        )
        self.assert_raw_status(raw, RawProcessingStatus.PROCESSED)
        self.assert_graph_counts(
            events=2,
            venues=1,
            artists=2,
            event_artists=2,
            event_identities=2,
            venue_identities=1,
            artist_identities=2,
            rejections=0,
        )
        self.assert_identity_values(
            events={"syn-event-page-1-a", "syn-event-page-1-b"},
            venues={"syn-venue-pages"},
            artists={"syn-artist-page-1-a", "syn-artist-page-1-b"},
        )
        venue = Venue.objects.get(name="Synthetic Paging Hall")
        self.assertEqual(venue.city, self.city)
        self.assertSetEqual(
            set(EventArtist.objects.values_list("position", flat=True)),
            {1},
        )

    def test_paginated_page_2(self):
        run = self.make_run()
        page_1 = self.make_raw(
            "ra_listing_paginated_page_1.synthetic.json",
            run=run,
        )
        transform(page_1)
        venue_pk = VenueIdentity.objects.get(
            source="ra",
            source_id="syn-venue-pages",
        ).venue_id
        venues_before = Venue.objects.count()
        page_2 = self.make_raw(
            "ra_listing_paginated_page_2.synthetic.json",
            run=run,
        )

        outcome = transform(page_2)

        self.assertEqual(page_2.window_start, date(2026, 8, 22))
        self.assertEqual(page_2.window_end, date(2026, 8, 23))
        self.assertEqual(page_2.page_size, 2)
        self.assertEqual(page_2.page_number, 2)
        self.assert_outcome(
            outcome,
            admitted=1,
            quarantined=0,
            dropped=0,
            observed={"syn-event-page-2-a"},
        )
        self.assert_raw_status(page_2, RawProcessingStatus.PROCESSED)
        self.assertEqual(Venue.objects.count() - venues_before, 0)
        self.assertEqual(
            VenueIdentity.objects.get(
                source="ra",
                source_id="syn-venue-pages",
            ).venue_id,
            venue_pk,
        )
        self.assert_graph_counts(
            events=3,
            venues=1,
            artists=3,
            event_artists=3,
            event_identities=3,
            venue_identities=1,
            artist_identities=3,
            rejections=0,
        )
        self.assert_identity_values(
            events={
                "syn-event-page-1-a",
                "syn-event-page-1-b",
                "syn-event-page-2-a",
            },
            venues={"syn-venue-pages"},
            artists={
                "syn-artist-page-1-a",
                "syn-artist-page-1-b",
                "syn-artist-page-2-a",
            },
        )
        self.assertEqual(
            Venue.objects.get(pk=venue_pk).name,
            "Synthetic Paging Hall",
        )
        self.assertEqual(Venue.objects.get(pk=venue_pk).city, self.city)
        self.assertSetEqual(
            set(EventArtist.objects.values_list("position", flat=True)),
            {1},
        )
        # SeedFetchOutcome completeness is intentionally not asserted in file #1.


class TransformerCrossCuttingContractTests(TransformerHarness):
    def test_changed_event_upsert_in_place(self):
        first_raw = self.make_raw("ra_listing_complete.synthetic.json")
        first_outcome = transform(first_raw)
        event = self.event_for_source_id("syn-event-complete-1")
        event_pk = event.pk
        identity_pk = EventIdentity.objects.get(
            source="ra",
            source_id="syn-event-complete-1",
        ).pk
        modified = copy.deepcopy(
            self.fixture_json("ra_listing_complete.synthetic.json")
        )
        changed_event = modified["data"]["eventListings"]["data"][0]["event"]
        changed_event["startTime"] = "2026-08-14T23:45:00.000"
        changed_event["title"] = "Synthetic Friday Night Updated"
        changed_event["flyerFront"] = (
            "https://example.invalid/flyers/complete-1-updated.jpg"
        )
        second_raw = self.make_raw(
            "ra_listing_complete.synthetic.json",
            payload=modified,
        )

        second_outcome = transform(second_raw)

        self.assert_outcome(
            first_outcome,
            admitted=2,
            quarantined=0,
            dropped=0,
            observed={"syn-event-complete-1", "syn-event-complete-2"},
        )
        self.assert_outcome(
            second_outcome,
            admitted=2,
            quarantined=0,
            dropped=0,
            observed={"syn-event-complete-1", "syn-event-complete-2"},
        )
        self.assertEqual(Event.objects.count(), 2)
        updated = self.event_for_source_id("syn-event-complete-1")
        self.assertEqual(updated.pk, event_pk)
        self.assertEqual(
            EventIdentity.objects.get(
                source="ra",
                source_id="syn-event-complete-1",
            ).pk,
            identity_pk,
        )
        self.assertEqual(updated.start_time, time(23, 45))
        self.assertEqual(updated.title, "Synthetic Friday Night Updated")
        self.assertEqual(
            updated.cover_image_url,
            "https://example.invalid/flyers/complete-1-updated.jpg",
        )

    def test_quarantine_retry(self):
        first_raw = self.make_raw("ra_listing_tba_lineup.synthetic.json")
        first_outcome = transform(first_raw)
        modified = copy.deepcopy(
            self.fixture_json("ra_listing_tba_lineup.synthetic.json")
        )
        modified["data"]["eventListings"]["data"][0]["event"]["artists"] = [
            {
                "id": "syn-artist-tba-announced",
                "name": "Synthetic Announced Artist",
            }
        ]
        retry_raw = self.make_raw(
            "ra_listing_tba_lineup.synthetic.json",
            payload=modified,
        )

        retry_outcome = transform(retry_raw)

        self.assert_outcome(
            first_outcome,
            admitted=0,
            quarantined=1,
            dropped=0,
            observed={"syn-event-tba"},
        )
        self.assert_outcome(
            retry_outcome,
            admitted=1,
            quarantined=0,
            dropped=0,
            observed={"syn-event-tba"},
        )
        self.assert_graph_counts(
            events=1,
            venues=1,
            artists=1,
            event_artists=1,
            event_identities=1,
            venue_identities=1,
            artist_identities=1,
            rejections=1,
        )
        self.assert_identity_values(
            events={"syn-event-tba"},
            venues={"syn-venue-tba"},
            artists={"syn-artist-tba-announced"},
        )
        self.assert_rejection(
            first_raw,
            entity_index=0,
            entity_ref="syn-event-tba",
            reason=RejectionReason.NO_ARTIST,
        )
        self.assertEqual(
            self.event_for_source_id("syn-event-tba").venue.city,
            self.city,
        )

    def test_optional_field_null_equivalence(self):
        explicit_raw = self.make_raw("ra_listing_date_only.synthetic.json")
        explicit_outcome = transform(explicit_raw)
        explicit_event = self.event_for_source_id("syn-event-date-only")
        event_pk = explicit_event.pk
        explicit_state = (
            explicit_event.event_date,
            explicit_event.start_time,
            explicit_event.cover_image_url,
            explicit_event.venue_id,
        )
        absent = copy.deepcopy(
            self.fixture_json("ra_listing_date_only.synthetic.json")
        )
        del absent["data"]["eventListings"]["data"][0]["event"]["startTime"]
        absent_raw = self.make_raw(
            "ra_listing_date_only.synthetic.json",
            payload=absent,
        )

        absent_outcome = transform(absent_raw)

        self.assert_outcome(
            explicit_outcome,
            admitted=1,
            quarantined=0,
            dropped=0,
            observed={"syn-event-date-only"},
        )
        self.assert_outcome(
            absent_outcome,
            admitted=1,
            quarantined=0,
            dropped=0,
            observed={"syn-event-date-only"},
        )
        absent_event = self.event_for_source_id("syn-event-date-only")
        self.assertEqual(absent_event.pk, event_pk)
        self.assertTupleEqual(
            (
                absent_event.event_date,
                absent_event.start_time,
                absent_event.cover_image_url,
                absent_event.venue_id,
            ),
            explicit_state,
        )
        self.assertIsNone(absent_event.start_time)
        self.assertEqual(Event.objects.count(), 1)

    def test_collection_equivalence(self):
        empty_raw = self.make_raw("ra_listing_tba_lineup.synthetic.json")
        empty_outcome = transform(empty_raw)

        absent = copy.deepcopy(
            self.fixture_json("ra_listing_tba_lineup.synthetic.json")
        )
        del absent["data"]["eventListings"]["data"][0]["event"]["artists"]
        absent_raw = self.make_raw(
            "ra_listing_tba_lineup.synthetic.json",
            payload=absent,
        )
        absent_outcome = transform(absent_raw)

        explicit_null = copy.deepcopy(
            self.fixture_json("ra_listing_tba_lineup.synthetic.json")
        )
        explicit_null["data"]["eventListings"]["data"][0]["event"]["artists"] = None
        null_raw = self.make_raw(
            "ra_listing_tba_lineup.synthetic.json",
            payload=explicit_null,
        )
        null_outcome = transform(null_raw)

        for outcome in (empty_outcome, absent_outcome, null_outcome):
            self.assert_outcome(
                outcome,
                admitted=0,
                quarantined=1,
                dropped=0,
                observed={"syn-event-tba"},
            )
        self.assert_graph_counts(
            events=0,
            venues=0,
            artists=0,
            event_artists=0,
            event_identities=0,
            venue_identities=0,
            artist_identities=0,
            rejections=3,
        )
        self.assertSetEqual(
            set(
                RejectedIngest.objects.values_list(
                    "raw_ingest_id",
                    "entity_index",
                    "entity_ref",
                    "reason",
                )
            ),
            {
                (empty_raw.id, 0, "syn-event-tba", RejectionReason.NO_ARTIST),
                (absent_raw.id, 0, "syn-event-tba", RejectionReason.NO_ARTIST),
                (null_raw.id, 0, "syn-event-tba", RejectionReason.NO_ARTIST),
            },
        )
