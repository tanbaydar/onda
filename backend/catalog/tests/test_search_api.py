from django.test import TestCase

from catalog.models import Artist, City, Event, EventArtist, EventStatus, Venue


class SearchApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        city = City.objects.get(name="Boston")
        cls.venue = Venue.objects.create(name="Marble Hall", city=city)
        cls.artist = Artist.objects.create(name="Mar")
        cls.prefix_artist = Artist.objects.create(name="Market Artist")
        cls.contains_artist = Artist.objects.create(name="The Marías")
        event = Event.objects.create(
            title="Afterhours",
            event_date="2026-08-20",
            venue=cls.venue,
            status=EventStatus.ACTIVE,
        )
        EventArtist.objects.create(event=event, artist=cls.artist, position=1)

    def test_accepts_single_character_and_returns_canonical_group_order(self):
        response = self.client.get("/api/search/", {"q": "a"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.json()["groups"]),
            ["events", "artists", "venues", "people"],
        )

    def test_orders_exact_before_prefix_before_contains(self):
        response = self.client.get(
            "/api/search/", {"q": "mar", "scope": "artists"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["name"] for item in response.json()["results"]],
            ["Mar", "Market Artist", "The Marías"],
        )

    def test_returns_an_empty_result_set(self):
        response = self.client.get(
            "/api/search/", {"q": "zzzz-no-match", "scope": "events"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"], [])
