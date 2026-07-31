from datetime import UTC, datetime, timedelta
import threading

from django.db import close_old_connections
from django.test import Client, TestCase, TransactionTestCase

from catalog.models import Artist, City, Event, EventStatus, Venue
from users import models


NOW = datetime(2026, 8, 20, 16, 0, tzinfo=UTC)


class FavoritesContractTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city, _ = City.objects.get_or_create(name="Boston", region_code="MA", country_code="US", defaults={"timezone": "America/New_York"})
        cls.venue = Venue.objects.create(name="Favorite Venue", city=cls.city)
        cls.artist = Artist.objects.create(name="Favorite Artist")
        cls.events = [
            Event.objects.create(
                title=f"Favorite Event {index}", event_date="2026-08-01",
                venue=cls.venue, status=EventStatus.ACTIVE,
            )
            for index in range(5)
        ]
        cls.owner = cls.user("favorite.owner")
        cls.viewer = cls.user("favorite.viewer")

    @classmethod
    def user(cls, username, private=False):
        return models.User.objects.create_user(
            email=f"{username}@test.example", password="A-real-password-123!",
            username=username, display_name=username, is_private=private,
        )

    def client_for(self, user=None):
        client = Client()
        if user:
            client.force_login(user)
        return client

    def test_event_favorite_cap_idempotency_and_removal(self):
        client = self.client_for(self.owner)
        first = client.put(f"/api/events/{self.events[0].id}/favorite/")
        repeated = client.put(f"/api/events/{self.events[0].id}/favorite/")
        self.assertEqual((first.status_code, repeated.status_code), (201, 200))
        self.assertEqual(first.json()["favorite"]["added_at"], repeated.json()["favorite"]["added_at"])
        for event in self.events[1:3]:
            self.assertEqual(client.put(f"/api/events/{event.id}/favorite/").status_code, 201)
        fourth = client.put(f"/api/events/{self.events[3].id}/favorite/")
        self.assertEqual(fourth.status_code, 409)
        self.assertIn("favorite", fourth.json()["errors"])
        self.assertEqual(client.delete(f"/api/events/{self.events[0].id}/favorite/").status_code, 204)
        self.assertEqual(client.delete(f"/api/events/{self.events[0].id}/favorite/").status_code, 204)

    def test_profile_favorites_are_earliest_added_first_and_need_no_been(self):
        FavoriteEvent = getattr(models, "FavoriteEvent")
        late = FavoriteEvent.objects.create(user=self.owner, event=self.events[1], added_at=NOW)
        FavoriteEvent.objects.create(user=self.owner, event=self.events[0], added_at=NOW - timedelta(days=1))
        response = self.client_for().get(f"/api/users/{self.owner.username}/favorites/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["event"]["id"] for row in response.json()["events"]], [self.events[0].id, late.event_id])
        self.assertFalse(models.DiaryEntry.objects.filter(user=self.owner).exists())

    def test_private_profile_favorites_and_stats_are_absent_not_zero(self):
        self.owner.is_private = True
        self.owner.save(update_fields=("is_private",))
        favorite = self.client_for(self.viewer).get(f"/api/users/{self.owner.username}/favorites/")
        stats = self.client_for(self.viewer).get(f"/api/users/{self.owner.username}/stats/")
        self.assertEqual((favorite.status_code, stats.status_code), (403, 403))
        self.assertNotIn("statistics", stats.json())

    def test_favorite_venues_have_only_an_owner_endpoint_and_ascending_order(self):
        FavoriteVenue = getattr(models, "FavoriteVenue")
        other = Venue.objects.create(name="Other Favorite Venue", city=self.city)
        FavoriteVenue.objects.create(user=self.owner, venue=other, added_at=NOW)
        FavoriteVenue.objects.create(user=self.owner, venue=self.venue, added_at=NOW - timedelta(days=1))
        own = self.client_for(self.owner).get("/api/me/favorite-venues/")
        self.assertEqual([row["venue"]["id"] for row in own.json()["results"]], [self.venue.id, other.id])
        self.assertEqual(self.client_for(self.viewer).get("/api/me/favorite-venues/").json()["results"], [])
        self.assertEqual(self.client_for().get(f"/api/users/{self.owner.username}/favorite-venues/").status_code, 404)

    def test_stats_include_unrated_been_but_distribution_does_not(self):
        models.DiaryEntry.objects.create(user=self.owner, event=self.events[0])
        models.DiaryEntry.objects.create(user=self.owner, event=self.events[1], rating="4.0", rated_at=NOW)
        payload = self.client_for().get(f"/api/users/{self.owner.username}/stats/").json()
        self.assertEqual(payload["statistics"]["events_in_been"], 2)
        self.assertEqual(payload["statistics"]["average_rating_given"]["value"], 4.0)
        buckets = payload["rating_distribution"]["buckets"]
        self.assertEqual(len(buckets), 10)
        self.assertEqual(next(row for row in buckets if row["rating"] == 4.0)["relative_value"], 1.0)

    def test_hidden_event_suppresses_favorite_and_stats_then_resurrects(self):
        FavoriteEvent = getattr(models, "FavoriteEvent")
        FavoriteEvent.objects.create(user=self.owner, event=self.events[0], added_at=NOW)
        models.DiaryEntry.objects.create(user=self.owner, event=self.events[0], rating="3.0", rated_at=NOW)
        self.events[0].status = EventStatus.HIDDEN
        self.events[0].save(update_fields=("status",))
        hidden = self.client_for().get(f"/api/users/{self.owner.username}/favorites/").json()
        hidden_stats = self.client_for().get(f"/api/users/{self.owner.username}/stats/").json()
        self.events[0].status = EventStatus.ACTIVE
        self.events[0].save(update_fields=("status",))
        restored = self.client_for().get(f"/api/users/{self.owner.username}/favorites/").json()
        self.assertEqual(hidden["events"], [])
        self.assertEqual(hidden_stats["statistics"]["events_in_been"], 0)
        self.assertEqual(len(restored["events"]), 1)

    def test_event_detail_wbt_count_is_anonymous_inclusive_and_active_only(self):
        WillBeThere = models.WillBeThere
        public = self.user("wbt.count.public")
        private = self.user("wbt.count.private", private=True)
        event = Event.objects.create(title="Count Event", event_date="2099-01-01", venue=self.venue, status=EventStatus.ACTIVE)
        WillBeThere.objects.create(user=public, event=event, created_at=NOW)
        WillBeThere.objects.create(user=private, event=event, created_at=NOW)
        payload = self.client_for().get(f"/api/events/{event.id}/").json()
        self.assertEqual(payload["will_be_there_summary"], {"active_count": 2})

    def test_guest_writes_are_rejected(self):
        self.assertEqual(self.client_for().put(f"/api/events/{self.events[0].id}/favorite/").status_code, 401)


class FavoriteCapConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def test_two_concurrent_third_event_favorites_cannot_breach_cap(self):
        city, _ = City.objects.get_or_create(name="Boston", region_code="MA", country_code="US", defaults={"timezone": "America/New_York"})
        venue = Venue.objects.create(name="Favorite Race Venue", city=city)
        user = models.User.objects.create_user(email="favorite.race@test.example", password="A-real-password-123!", username="favorite.race", display_name="Favorite Race", is_private=False)
        events = [Event.objects.create(title=f"Race Favorite {index}", event_date="2026-08-01", venue=venue, status=EventStatus.ACTIVE) for index in range(4)]
        models.FavoriteEvent.objects.create(user=user, event=events[0], added_at=NOW)
        models.FavoriteEvent.objects.create(user=user, event=events[1], added_at=NOW)
        barrier = threading.Barrier(2)
        outcomes = []

        def add(event_id):
            close_old_connections()
            try:
                from users.services import FavoriteLimitReached, save_favorite
                barrier.wait()
                try:
                    save_favorite(user_id=user.id, model=models.FavoriteEvent, target_field="event", target_id=event_id, limit=3)
                    outcomes.append("created")
                except FavoriteLimitReached:
                    outcomes.append("limited")
            finally:
                close_old_connections()

        threads = [threading.Thread(target=add, args=(events[2].id,)), threading.Thread(target=add, args=(events[3].id,))]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        self.assertEqual(sorted(outcomes), ["created", "limited"])
        self.assertEqual(models.FavoriteEvent.objects.filter(user=user).count(), 3)

    def test_two_concurrent_third_artist_favorites_cannot_breach_cap(self):
        user = models.User.objects.create_user(email="artist.favorite.race@test.example", password="A-real-password-123!", username="artist.favorite.race", display_name="Artist Favorite Race", is_private=False)
        artists = [Artist.objects.create(name=f"Race Favorite Artist {index}") for index in range(4)]
        models.FavoriteArtist.objects.create(user=user, artist=artists[0], added_at=NOW)
        models.FavoriteArtist.objects.create(user=user, artist=artists[1], added_at=NOW)
        barrier = threading.Barrier(2)
        outcomes = []

        def add(artist_id):
            close_old_connections()
            try:
                from users.services import FavoriteLimitReached, save_favorite
                barrier.wait()
                try:
                    save_favorite(user_id=user.id, model=models.FavoriteArtist, target_field="artist", target_id=artist_id, limit=3)
                    outcomes.append("created")
                except FavoriteLimitReached:
                    outcomes.append("limited")
            finally:
                close_old_connections()

        threads = [threading.Thread(target=add, args=(artists[2].id,)), threading.Thread(target=add, args=(artists[3].id,))]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        self.assertEqual(sorted(outcomes), ["created", "limited"])
        self.assertEqual(models.FavoriteArtist.objects.filter(user=user).count(), 3)
