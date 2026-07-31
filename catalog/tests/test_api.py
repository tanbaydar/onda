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


class UpcomingEventsApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.boston = City.objects.get(name="Boston")
        cls.new_york = City.objects.get(name="New York City")
        cls.boston_venue = Venue.objects.create(
            name="Frozen Boston Hall",
            city=cls.boston,
        )
        cls.new_york_venue = Venue.objects.create(
            name="Frozen New York Hall",
            city=cls.new_york,
        )
        cls.artist = Artist.objects.create(name="Frozen API Artist")

        cls.yesterday = cls.make_event(
            title="Yesterday",
            event_date="2026-08-13",
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
            artist=cls.artist,
            position=1,
        )
        return event

    def get_events(self, **params):
        query = {
            "city_id": self.boston.id,
            "when": "upcoming",
            **params,
        }
        with patch("django.utils.timezone.now", return_value=FIXED_NOW):
            return self.client.get("/api/events/", query)

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
