import copy
from datetime import UTC, datetime
from unittest.mock import patch

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
from ingestion.models import RawIngest, RejectedIngest
from ingestion.transformer import transform
from ingestion.tests.test_transformer import TransformerHarness


FIXED_NOW = datetime(2026, 8, 1, 12, 0, tzinfo=UTC)
SNAPSHOT_MODELS = (
    City,
    CityIdentity,
    Venue,
    VenueIdentity,
    Artist,
    ArtistIdentity,
    Event,
    EventArtist,
    EventIdentity,
    RawIngest,
    RejectedIngest,
)
ALL_FIXTURES = (
    "ra_listing_complete.synthetic.json",
    "ra_listing_date_only.synthetic.json",
    "ra_listing_tba_lineup.synthetic.json",
    "ra_listing_festival.synthetic.json",
    "ra_listing_sold_out.synthetic.json",
    "ra_listing_cancelled_title.synthetic.json",
    "ra_listing_malformed_event.synthetic.json",
    "ra_listing_missing_event_id.synthetic.json",
    "ra_listing_empty_title.synthetic.json",
    "ra_listing_bad_date.synthetic.json",
    "ra_listing_malformed_payload.synthetic.txt",
    "ra_listing_paginated_page_1.synthetic.json",
    "ra_listing_paginated_page_2.synthetic.json",
)


class TransformerIdempotencyTests(TransformerHarness):
    def snapshot(self):
        state = {}
        for model in SNAPSHOT_MODELS:
            field_names = [
                field.attname
                for field in model._meta.concrete_fields
            ]
            state[model] = sorted(
                model._default_manager.values_list(*field_names)
            )
        return state

    def test_double_transform_all_fixtures(self):
        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            for fixture_name in ALL_FIXTURES:
                with self.subTest(fixture=fixture_name):
                    raw = self.make_raw(fixture_name)
                    transform(raw)
                    snapshot_before = self.snapshot()

                    transform(raw)
                    snapshot_after = self.snapshot()

                    self.assertEqual(snapshot_before, snapshot_after)

    def test_double_transform_after_pagination(self):
        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            run = self.make_run()
            page_1 = self.make_raw(
                "ra_listing_paginated_page_1.synthetic.json",
                run=run,
            )
            page_2 = self.make_raw(
                "ra_listing_paginated_page_2.synthetic.json",
                run=run,
            )
            transform(page_1)
            transform(page_2)
            snapshot_before = self.snapshot()

            transform(page_1)
            transform(page_2)
            snapshot_after = self.snapshot()

            self.assertEqual(snapshot_before, snapshot_after)

    def test_lineup_reorder(self):
        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            original_raw = self.make_raw("ra_listing_festival.synthetic.json")
            transform(original_raw)
            event_identity = EventIdentity.objects.get(
                source="ra",
                source_id="syn-event-festival",
            )
            event_pk = event_identity.event_id
            event_identity_pk = event_identity.pk
            artist_pks_before = dict(
                ArtistIdentity.objects.values_list("source_id", "artist_id")
            )

            reversed_payload = copy.deepcopy(
                self.fixture_json("ra_listing_festival.synthetic.json")
            )
            artists = reversed_payload["data"]["eventListings"]["data"][0][
                "event"
            ]["artists"]
            artists.reverse()
            reversed_raw = self.make_raw(
                "ra_listing_festival.synthetic.json",
                payload=reversed_payload,
            )

            transform(reversed_raw)

            event_identity.refresh_from_db()
            self.assertEqual(event_identity.pk, event_identity_pk)
            self.assertEqual(event_identity.event_id, event_pk)
            self.assertEqual(Event.objects.count(), 1)
            self.assertEqual(EventArtist.objects.count(), 3)
            self.assertListEqual(
                list(
                    EventArtist.objects.order_by("position").values_list(
                        "artist__name",
                        "position",
                    )
                ),
                [
                    ("Synthetic Headliner", 1),
                    ("Synthetic Middle", 2),
                    ("Synthetic Opener", 3),
                ],
            )
            self.assertEqual(Artist.objects.count(), 3)
            self.assertDictEqual(
                dict(
                    ArtistIdentity.objects.values_list(
                        "source_id",
                        "artist_id",
                    )
                ),
                artist_pks_before,
            )

    def test_lineup_reorder_is_idempotent(self):
        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            original_raw = self.make_raw("ra_listing_festival.synthetic.json")
            transform(original_raw)
            reversed_payload = copy.deepcopy(
                self.fixture_json("ra_listing_festival.synthetic.json")
            )
            artists = reversed_payload["data"]["eventListings"]["data"][0][
                "event"
            ]["artists"]
            artists.reverse()
            reversed_raw = self.make_raw(
                "ra_listing_festival.synthetic.json",
                payload=reversed_payload,
            )
            transform(reversed_raw)
            snapshot_before = self.snapshot()

            transform(reversed_raw)
            snapshot_after = self.snapshot()

            self.assertEqual(snapshot_before, snapshot_after)
