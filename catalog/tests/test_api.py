from datetime import UTC, datetime
from unittest.mock import patch

from django.test import TestCase

from catalog.models import (
    Artist,
    City,
    Event,
    EventArtist,
    EventStatus,
    Venue,
)


FIXED_NOW = datetime(2026, 8, 14, 16, 0, tzinfo=UTC)
CROSS_TIMEZONE_NOW = datetime(2026, 8, 14, 2, 0, tzinfo=UTC)


class CatalogApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.boston = City.objects.get(name="Boston")
        cls.new_york = City.objects.get(name="New York City")
        cls.tokyo = City.objects.create(
            name="Tokyo",
            region_code="13",
            region_name="Tokyo",
            country_code="JP",
            timezone="Asia/Tokyo",
        )
        cls.boston_venue = Venue.objects.create(
            name="Frozen Boston Hall",
            city=cls.boston,
        )
        cls.new_york_venue = Venue.objects.create(
            name="Frozen New York Hall",
            city=cls.new_york,
        )
        cls.tokyo_venue = Venue.objects.create(
            name="Frozen Tokyo Hall",
            city=cls.tokyo,
        )
        cls.empty_venue = Venue.objects.create(
            name="Frozen Empty Venue",
            city=cls.boston,
        )
        cls.artist = Artist.objects.create(
            name="Frozen API Artist",
            image_url="https://example.invalid/artist.jpg",
        )
        cls.empty_artist = Artist.objects.create(name="Frozen Empty Artist")
        cls.cross_timezone_artist = Artist.objects.create(
            name="Frozen International Artist"
        )

        cls.yesterday = cls.make_event(
            title="Yesterday",
            event_date="2026-08-13",
        )
        cls.older_first = cls.make_event(
            title="Older First",
            event_date="2026-08-12",
        )
        cls.older_second = cls.make_event(
            title="Older Second",
            event_date="2026-08-12",
        )
        cls.today_first = cls.make_event(
            title="Today First",
            event_date="2026-08-14",
            start_time="23:30:00",
            cover_image_url="https://example.invalid/today-first.jpg",
        )
        cls.today_second = cls.make_event(
            title="Today Second",
            event_date="2026-08-14",
            status=EventStatus.UNVERIFIED,
        )
        cls.tomorrow = cls.make_event(
            title="Tomorrow",
            event_date="2026-08-15",
        )
        cls.hidden = cls.make_event(
            title="Cancelled by evidence",
            event_date="2026-08-16",
            status=EventStatus.HIDDEN,
        )
        cls.later = cls.make_event(
            title="Later",
            event_date="2026-08-17",
        )
        cls.other_city = cls.make_event(
            title="New York Event",
            event_date="2026-08-14",
            venue=cls.new_york_venue,
        )
        cls.cross_timezone_boston = cls.make_event(
            title="Boston Local Today",
            event_date="2026-08-13",
            artist=cls.cross_timezone_artist,
        )
        cls.cross_timezone_tokyo = cls.make_event(
            title="Tokyo Local Yesterday",
            event_date="2026-08-13",
            venue=cls.tokyo_venue,
            artist=cls.cross_timezone_artist,
        )

    @classmethod
    def make_event(
        cls,
        *,
        title,
        event_date,
        venue=None,
        start_time=None,
        cover_image_url=None,
        status=EventStatus.ACTIVE,
        artist=None,
    ):
        event = Event.objects.create(
            title=title,
            event_date=event_date,
            start_time=start_time,
            venue=venue or cls.boston_venue,
            cover_image_url=cover_image_url,
            status=status,
        )
        EventArtist.objects.create(
            event=event,
            artist=artist or cls.artist,
            position=1,
        )
        return event

    def request_events(self, query, *, now=FIXED_NOW):
        with patch("django.utils.timezone.now", return_value=now):
            return self.client.get("/api/events/", query)

    def get_events(self, **params):
        return self.request_events(
            {
                "city_id": self.boston.id,
                "when": "upcoming",
                **params,
            }
        )

    def test_cities_are_canonical_fields_ordered_by_name(self):
        response = self.client.get("/api/cities/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "results": [
                    {
                        "id": self.boston.id,
                        "name": "Boston",
                        "region_code": "MA",
                        "country_code": "US",
                        "timezone": "America/New_York",
                    },
                    {
                        "id": self.new_york.id,
                        "name": "New York City",
                        "region_code": "NY",
                        "country_code": "US",
                        "timezone": "America/New_York",
                    },
                    {
                        "id": self.tokyo.id,
                        "name": "Tokyo",
                        "region_code": "13",
                        "country_code": "JP",
                        "timezone": "Asia/Tokyo",
                    },
                ]
            },
        )

    def test_filters_by_city_and_public_lifecycle_visibility(self):
        response = self.get_events(page_size=100)

        self.assertEqual(response.status_code, 200)
        ids = [event["id"] for event in response.json()["results"]]
        self.assertIn(self.today_first.id, ids)
        self.assertIn(self.today_second.id, ids)
        self.assertNotIn(self.hidden.id, ids)
        self.assertNotIn(self.other_city.id, ids)

    def test_today_is_upcoming_until_venue_local_midnight(self):
        response = self.get_events(page_size=100)

        self.assertEqual(response.status_code, 200)
        ids = [event["id"] for event in response.json()["results"]]
        self.assertIn(self.today_first.id, ids)
        self.assertNotIn(self.yesterday.id, ids)

    def test_orders_by_event_date_then_canonical_id(self):
        response = self.get_events(page_size=100)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [event["id"] for event in response.json()["results"]],
            [
                self.today_first.id,
                self.today_second.id,
                self.tomorrow.id,
                self.later.id,
            ],
        )

    def test_response_contract_does_not_expose_lifecycle_status(self):
        response = self.get_events(page_size=1)

        self.assertEqual(response.status_code, 200)
        event = response.json()["results"][0]
        self.assertEqual(
            event,
            {
                "id": self.today_first.id,
                "title": "Today First",
                "event_date": "2026-08-14",
                "start_time": "23:30:00",
                "cover_image_url": (
                    "https://example.invalid/today-first.jpg"
                ),
                "venue": {
                    "id": self.boston_venue.id,
                    "name": "Frozen Boston Hall",
                    "city": {
                        "id": self.boston.id,
                        "name": "Boston",
                        "timezone": "America/New_York",
                    },
                },
                "artists": [
                    {
                        "id": self.artist.id,
                        "name": "Frozen API Artist",
                        "position": 1,
                    }
                ],
            },
        )
        self.assertNotIn("status", event)

    def test_paginates_full_and_partial_pages_without_overlap(self):
        first = self.get_events(page=1, page_size=3)
        second = self.get_events(page=2, page_size=3)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(
            [event["id"] for event in first.json()["results"]],
            [self.today_first.id, self.today_second.id, self.tomorrow.id],
        )
        self.assertEqual(
            [event["id"] for event in second.json()["results"]],
            [self.later.id],
        )
        self.assertEqual(
            first.json()["pagination"],
            {
                "page": 1,
                "page_size": 3,
                "total_results": 4,
                "total_pages": 2,
                "next_page": 2,
                "previous_page": None,
            },
        )
        self.assertEqual(
            second.json()["pagination"],
            {
                "page": 2,
                "page_size": 3,
                "total_results": 4,
                "total_pages": 2,
                "next_page": None,
                "previous_page": 1,
            },
        )

    def test_page_beyond_last_page_is_not_found(self):
        response = self.get_events(page=3, page_size=3)

        self.assertEqual(response.status_code, 404)

    def test_when_is_required_and_rejects_unknown_values(self):
        missing = self.request_events({"city_id": self.boston.id})
        unknown = self.request_events(
            {"city_id": self.boston.id, "when": "later"}
        )

        self.assertEqual(missing.status_code, 400)
        self.assertEqual(unknown.status_code, 400)

    def test_requires_exactly_one_scope_filter(self):
        no_scope = self.request_events({"when": "upcoming"})
        multiple_scopes = self.request_events(
            {
                "when": "upcoming",
                "city_id": self.boston.id,
                "venue_id": self.boston_venue.id,
            }
        )

        self.assertEqual(no_scope.status_code, 400)
        self.assertEqual(multiple_scopes.status_code, 400)

    def test_unknown_scope_ids_are_not_found(self):
        for filter_name in ("city_id", "venue_id", "artist_id"):
            with self.subTest(filter_name=filter_name):
                response = self.request_events(
                    {"when": "upcoming", filter_name: 999_999}
                )
                self.assertEqual(response.status_code, 404)

    def test_past_excludes_today_and_orders_date_then_id_descending(self):
        response = self.request_events(
            {
                "city_id": self.boston.id,
                "when": "past",
                "page_size": 100,
            }
        )

        self.assertEqual(response.status_code, 200)
        ids = [event["id"] for event in response.json()["results"]]
        self.assertEqual(
            ids,
            [
                self.cross_timezone_boston.id,
                self.yesterday.id,
                self.older_second.id,
                self.older_first.id,
            ],
        )
        self.assertNotIn(self.today_first.id, ids)

    def test_venue_scope_reuses_upcoming_and_past_boundaries(self):
        upcoming = self.request_events(
            {
                "venue_id": self.boston_venue.id,
                "when": "upcoming",
                "page_size": 100,
            }
        )
        past = self.request_events(
            {
                "venue_id": self.boston_venue.id,
                "when": "past",
                "page_size": 100,
            }
        )

        self.assertEqual(upcoming.status_code, 200)
        self.assertEqual(past.status_code, 200)
        upcoming_ids = {
            event["id"] for event in upcoming.json()["results"]
        }
        past_ids = {event["id"] for event in past.json()["results"]}
        self.assertIn(self.today_first.id, upcoming_ids)
        self.assertNotIn(self.today_first.id, past_ids)

    def test_artist_scope_classifies_each_event_in_its_venue_timezone(self):
        upcoming = self.request_events(
            {
                "artist_id": self.cross_timezone_artist.id,
                "when": "upcoming",
                "page_size": 100,
            },
            now=CROSS_TIMEZONE_NOW,
        )
        past = self.request_events(
            {
                "artist_id": self.cross_timezone_artist.id,
                "when": "past",
                "page_size": 100,
            },
            now=CROSS_TIMEZONE_NOW,
        )

        self.assertEqual(upcoming.status_code, 200)
        self.assertEqual(past.status_code, 200)
        self.assertEqual(
            [event["id"] for event in upcoming.json()["results"]],
            [self.cross_timezone_boston.id],
        )
        self.assertEqual(
            [event["id"] for event in past.json()["results"]],
            [self.cross_timezone_tokyo.id],
        )

    def test_venue_detail_returns_full_city_and_no_embedded_events(self):
        response = self.client.get(f"/api/venues/{self.boston_venue.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "id": self.boston_venue.id,
                "name": "Frozen Boston Hall",
                "city": {
                    "id": self.boston.id,
                    "name": "Boston",
                    "region_code": "MA",
                    "region_name": "Massachusetts",
                    "country_code": "US",
                    "timezone": "America/New_York",
                },
            },
        )
        self.assertNotIn("events", response.json())

    def test_artist_detail_returns_model_fields_and_no_embedded_events(self):
        response = self.client.get(f"/api/artists/{self.artist.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "id": self.artist.id,
                "name": "Frozen API Artist",
                "image_url": "https://example.invalid/artist.jpg",
            },
        )
        self.assertNotIn("events", response.json())

    def test_event_detail_reuses_public_event_shape(self):
        detail = self.client.get(f"/api/events/{self.today_first.id}/")
        listing = self.get_events(page_size=1)

        self.assertEqual(detail.status_code, 200)
        detail_payload = detail.json()
        rating_summary = detail_payload.pop("rating_summary")
        been = detail_payload.pop("been")
        will_be_there_summary = detail_payload.pop("will_be_there_summary")
        self.assertEqual(detail_payload, listing.json()["results"][0])
        self.assertEqual(
            rating_summary,
            {"state": "not_enough_ratings", "count": 0},
        )
        self.assertIn("loggable", been)
        self.assertIn("unavailable_reason", been)
        self.assertEqual(will_be_there_summary, {"active_count": 0})
        self.assertNotIn("status", detail_payload)

    def test_hidden_event_detail_is_not_found(self):
        response = self.client.get(f"/api/events/{self.hidden.id}/")

        self.assertEqual(response.status_code, 404)

    def test_entity_details_survive_zero_visible_events(self):
        venue = self.client.get(f"/api/venues/{self.empty_venue.id}/")
        artist = self.client.get(f"/api/artists/{self.empty_artist.id}/")

        self.assertEqual(venue.status_code, 200)
        self.assertEqual(artist.status_code, 200)

    def test_unknown_detail_ids_are_not_found(self):
        for path in (
            "/api/venues/999999/",
            "/api/artists/999999/",
            "/api/events/999999/",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 404)
