from django.db import IntegrityError, connection, transaction
from django.test import TestCase

from .models import (
    Artist,
    ArtistIdentity,
    City,
    CityIdentity,
    Event,
    EventArtist,
    EventIdentity,
    EventStatus,
    Venue,
    VenueIdentity,
)


class CatalogSchemaTests(TestCase):
    def test_v1_cities_are_seeded_with_iana_timezones(self):
        self.assertCountEqual(
            City.objects.values_list(
                "name",
                "region_code",
                "country_code",
                "timezone",
            ),
            [
                ("New York City", "NY", "US", "America/New_York"),
                ("Boston", "MA", "US", "America/New_York"),
            ],
        )

    def test_v1_city_identities_resolve_ra_seed_areas(self):
        self.assertEqual(
            CityIdentity.objects.get(source="ra", source_id="8").city.name,
            "New York City",
        )
        self.assertEqual(
            CityIdentity.objects.get(source="ra", source_id="530").city.name,
            "Boston",
        )

    def test_event_status_is_enforced_by_the_database(self):
        city = City.objects.get(name="Boston")
        venue = Venue.objects.create(name="Schema Test Venue", city=city)
        event = Event.objects.create(
            title="Schema Test Event",
            event_date="2026-08-01",
            venue=venue,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            Event.objects.filter(pk=event.pk).update(status="not-a-status")

    def test_database_cascades_remove_canonical_shadow_rows(self):
        city = City.objects.get(name="New York City")
        venue = Venue.objects.create(name="Cascade Test Venue", city=city)
        artist = Artist.objects.create(name="Cascade Test Artist")
        event = Event.objects.create(
            title="Cascade Test Event",
            event_date="2026-08-01",
            venue=venue,
            status=EventStatus.ACTIVE,
        )
        EventArtist.objects.create(event=event, artist=artist, position=1)
        EventIdentity.objects.create(event=event, source="ra", source_id="event-1")
        VenueIdentity.objects.create(venue=venue, source="ra", source_id="venue-1")
        ArtistIdentity.objects.create(
            artist=artist,
            source="ra",
            source_id="artist-1",
        )

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM EVENT WHERE id = %s", [event.pk])
            cursor.execute("DELETE FROM VENUE WHERE id = %s", [venue.pk])
            cursor.execute("DELETE FROM ARTIST WHERE id = %s", [artist.pk])

        self.assertFalse(EventArtist.objects.exists())
        self.assertFalse(EventIdentity.objects.exists())
        self.assertFalse(VenueIdentity.objects.exists())
        self.assertFalse(ArtistIdentity.objects.exists())

    def test_database_cascade_removes_city_identity(self):
        city = City.objects.create(
            name="Cascade Test City",
            region_code="TC",
            region_name="Test",
            country_code="US",
            timezone="America/New_York",
        )
        CityIdentity.objects.create(
            city=city,
            source="ra",
            source_id="cascade-test-area",
        )

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM CITY WHERE id = %s", [city.pk])

        self.assertFalse(
            CityIdentity.objects.filter(source_id="cascade-test-area").exists()
        )
