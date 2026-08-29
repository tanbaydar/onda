from datetime import UTC, datetime, timedelta

from django.db import connection
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext

from catalog.models import Artist, City, Event, EventArtist, EventStatus, Venue
from users.models import (DiaryEntry, FavoriteArtist, FavoriteEvent, Follow,
                          FollowStatus, Review, ReviewLike, User, WillBeThere)


NOW = datetime(2026, 8, 20, 16, 0, tzinfo=UTC)


class HomeFeedContractTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        city = City.objects.get(name="Boston")
        venue = Venue.objects.create(name="Home Feed Venue", city=city)
        artist = Artist.objects.create(name="Home Feed Artist")
        cls.events = []
        for index in range(6):
            event = Event.objects.create(
                title=f"Home Feed Event {index}",
                event_date="2026-07-01",
                start_time="20:00:00",
                venue=venue,
                status=EventStatus.ACTIVE,
            )
            EventArtist.objects.create(event=event, artist=artist, position=1)
            cls.events.append(event)
        cls.hidden_event = Event.objects.create(
            title="Hidden Home Feed Event",
            event_date="2026-07-02",
            start_time="20:00:00",
            venue=venue,
            status=EventStatus.HIDDEN,
        )
        EventArtist.objects.create(event=cls.hidden_event, artist=artist, position=1)
        cls.viewer = cls.user("home.viewer")
        cls.actor = cls.user("home.actor")
        cls.actor.avatar = "https://images.example.test/home-actor.jpg"
        cls.actor.save(update_fields=("avatar",))
        cls.actor_two = cls.user("home.actor.two")
        cls.target = cls.user("home.target")
        cls.private_author = cls.user("home.private", is_private=True)

    @classmethod
    def user(cls, username, is_private=False):
        return User.objects.create_user(
            email=f"{username}@test.example",
            password="A-real-password-123!",
            username=username,
            display_name=username,
            is_private=is_private,
        )

    def client_for(self, user=None):
        client = Client()
        if user is not None:
            client.force_login(user)
        return client

    def approved(self, follower, followee, *, at=NOW, created_at=None):
        return Follow.objects.create(
            follower=follower,
            followee=followee,
            status=FollowStatus.APPROVED,
            created_at=created_at or at,
            approved_at=at,
        )

    def entry(self, user, event, *, at=NOW, rating="4.0"):
        return DiaryEntry.objects.create(
            user=user, event=event, rating=rating, rated_at=at
        )

    def test_seven_type_identical_timestamp_order_and_source_key_tiebreak_are_fixed(self):
        self.approved(self.viewer, self.actor, at=NOW - timedelta(days=1))
        self.entry(self.actor, self.events[0], at=NOW)
        self.events[0].cover_image_url = "https://images.example.test/home-event.jpg"
        self.events[0].save(update_fields=("cover_image_url",))
        review_entry = self.entry(self.actor, self.events[1], at=NOW - timedelta(days=2))
        Review.objects.create(
            entry=review_entry, body="Written review", published_at=NOW
        )
        author_entry = self.entry(self.target, self.events[2], at=NOW - timedelta(days=2))
        review = Review.objects.create(
            entry=author_entry, body="Visible liked review", published_at=NOW
        )
        like = ReviewLike.objects.create(user=self.actor, review=review)
        ReviewLike.objects.filter(pk=like.pk).update(created_at=NOW)
        self.events[3].event_date = "2099-01-01"
        self.events[3].save(update_fields=("event_date",))
        WillBeThere.objects.create(user=self.actor, event=self.events[3], created_at=NOW)
        FavoriteEvent.objects.create(user=self.actor, event=self.events[3], added_at=NOW)
        FavoriteEvent.objects.create(user=self.actor, event=self.events[4], added_at=NOW)
        FavoriteArtist.objects.create(user=self.actor, artist=Artist.objects.get(name="Home Feed Artist"), added_at=NOW)
        unrated = DiaryEntry.objects.create(user=self.actor, event=self.events[5])
        DiaryEntry.objects.filter(pk=unrated.pk).update(created_at=NOW)

        client = self.client_for(self.viewer)
        with CaptureQueriesContext(connection) as queries:
            response = client.get("/api/me/home/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["type"] for item in response.json()["results"][:8]],
            ["will_be_there", "review_like", "review", "rated_been", "favorite_event", "favorite_event", "favorite_artist", "been"],
        )
        favorite_event_ids = [
            item["target"]["event"]["id"]
            for item in response.json()["results"]
            if item["type"] == "favorite_event"
        ]
        self.assertEqual(
            favorite_event_ids,
            sorted((self.events[3].id, self.events[4].id), reverse=True),
        )
        results = response.json()["results"]
        self.assertTrue(all(item["actor"]["avatar"] == self.actor.avatar for item in results))
        rated = next(item for item in results if item["target"]["event"]["id"] == self.events[0].id)
        self.assertEqual(rated["target"]["event"]["cover_image_url"], self.events[0].cover_image_url)
        self.assertEqual(rated["target"]["event"]["venue"], {"name": "Home Feed Venue", "city": {"name": "Boston"}})
        written_review = next(item for item in results if item["target"]["event"]["id"] == self.events[1].id)
        self.assertEqual(written_review["type"], "review")
        self.assertEqual(written_review["activity_at"], NOW.isoformat().replace("+00:00", "Z"))
        self.assertEqual(written_review["context"]["rating"], 4.0)
        self.assertEqual(written_review["context"]["review"]["body"], "Written review")
        self.assertEqual(
            sum(item["target"].get("event", {}).get("id") == self.events[1].id for item in results),
            1,
        )
        been = next(item for item in results if item["type"] == "been")
        self.assertEqual(been["target"]["event"]["id"], self.events[5].id)
        self.assertIsNone(been["context"])
        liked_review = next(item for item in results if item["type"] == "review_like")
        self.assertEqual(
            liked_review["target"]["review"],
            {
                "id": review.id,
                "body": "Visible liked review",
                "rating": 4.0,
                "author": {
                    "id": self.target.id,
                    "username": self.target.username,
                    "display_name": self.target.display_name,
                },
            },
        )
        favorite_without_cover = next(item for item in results if item["type"] == "favorite_event")
        self.assertIsNone(favorite_without_cover["target"]["event"]["cover_image_url"])
        # Two fixed session/auth lookups, one bounded city-boundary lookup,
        # and exactly one five-branch feed UNION.
        self.assertEqual(len(queries), 4)
        self.assertEqual(
            sum("UNION ALL" in query["sql"] for query in queries.captured_queries),
            1,
        )

    def test_cursor_is_stable_when_new_activity_arrives(self):
        self.approved(self.viewer, self.actor)
        for index, event in enumerate(self.events[:3]):
            self.entry(self.actor, event, at=NOW - timedelta(minutes=index + 1))
        first = self.client_for(self.viewer).get("/api/me/home/", {"page_size": 2}).json()
        first_ids = [item["target"]["event"]["id"] for item in first["results"]]
        self.entry(self.actor, self.events[3], at=NOW + timedelta(minutes=1))
        second = self.client_for(self.viewer).get(
            "/api/me/home/", {"page_size": 2, "cursor": first["next_cursor"]}
        ).json()
        second_ids = [item["target"]["event"]["id"] for item in second["results"]]
        self.assertFalse(set(first_ids) & set(second_ids))
        self.assertEqual(second_ids, [self.events[2].id])

    def test_additive_identity_fields_preserve_null_fallbacks(self):
        self.approved(self.viewer, self.actor_two)
        self.entry(self.actor_two, self.events[0])
        item = self.client_for(self.viewer).get("/api/me/home/").json()["results"][0]
        self.assertIsNone(item["actor"]["avatar"])
        self.assertIsNone(item["target"]["event"]["cover_image_url"])
        self.assertEqual(item["target"]["event"]["venue"]["name"], "Home Feed Venue")
        self.assertEqual(item["target"]["event"]["venue"]["city"]["name"], "Boston")

    def test_private_actor_activity_disappears_immediately_on_unfollow(self):
        self.actor.is_private = True
        self.actor.save(update_fields=("is_private",))
        relationship = self.approved(self.viewer, self.actor)
        self.entry(self.actor, self.events[0])
        visible = self.client_for(self.viewer).get("/api/me/home/").json()
        relationship.delete()
        gone = self.client_for(self.viewer).get("/api/me/home/").json()
        self.assertEqual(len(visible["results"]), 1)
        self.assertEqual(gone["results"], [])

    def test_review_like_never_leaks_an_invisible_private_review(self):
        self.approved(self.viewer, self.actor)
        private_entry = self.entry(self.private_author, self.events[0])
        review = Review.objects.create(
            entry=private_entry, body="Private review", published_at=NOW
        )
        like = ReviewLike.objects.create(user=self.actor, review=review)
        ReviewLike.objects.filter(pk=like.pk).update(created_at=NOW)
        result = self.client_for(self.viewer).get("/api/me/home/").json()
        self.assertEqual(result["results"], [])

    def test_hidden_items_are_suppressed_and_resurrection_restores_them(self):
        self.approved(self.viewer, self.actor)
        self.entry(self.actor, self.hidden_event)
        hidden = self.client_for(self.viewer).get("/api/me/home/").json()
        self.hidden_event.status = EventStatus.ACTIVE
        self.hidden_event.save(update_fields=("status",))
        restored = self.client_for(self.viewer).get("/api/me/home/").json()
        self.assertEqual(hidden["results"], [])
        self.assertEqual(restored["results"][0]["target"]["event"]["id"], self.hidden_event.id)

    def test_rating_removal_relabels_as_been_and_rerating_repositions(self):
        self.approved(self.viewer, self.actor)
        old = self.entry(self.actor, self.events[0], at=NOW - timedelta(days=2))
        DiaryEntry.objects.filter(pk=old.pk).update(created_at=NOW - timedelta(days=3))
        self.entry(self.actor, self.events[1], at=NOW - timedelta(days=1))
        old.rating = None
        old.rated_at = None
        old.save(update_fields=("rating", "rated_at"))
        removed = self.client_for(self.viewer).get("/api/me/home/").json()
        old.rating = "5.0"
        old.rated_at = NOW + timedelta(days=1)
        old.save(update_fields=("rating", "rated_at"))
        rerated = self.client_for(self.viewer).get("/api/me/home/").json()
        self.assertEqual(
            [item["type"] for item in removed["results"]],
            ["rated_been", "been"],
        )
        self.assertEqual(rerated["results"][0]["target"]["event"]["id"], self.events[0].id)
        self.assertEqual(rerated["results"][0]["type"], "rated_been")

    def test_follow_activity_is_not_in_home(self):
        self.approved(self.viewer, self.actor)
        self.approved(self.viewer, self.actor_two)
        self.approved(self.actor, self.target, at=NOW)
        self.approved(self.actor_two, self.target, at=NOW)
        results = self.client_for(self.viewer).get("/api/me/home/").json()["results"]
        self.assertEqual(results, [])

    def test_guest_and_invalid_cursor_errors_are_field_keyed(self):
        self.assertEqual(self.client_for().get("/api/me/home/").status_code, 401)
        invalid = self.client_for(self.viewer).get("/api/me/home/", {"cursor": "bad"})
        oversized = self.client_for(self.viewer).get(
            "/api/me/home/", {"cursor": "a" * 513}
        )
        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(oversized.status_code, 400)
        self.assertIn("cursor", invalid.json()["errors"])
        self.assertIn("cursor", oversized.json()["errors"])
