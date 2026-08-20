import json
from datetime import UTC, datetime
from unittest.mock import patch

from django.apps import apps
from django.db import IntegrityError, transaction
from django.test import Client, TestCase

from catalog.models import Artist, City, Event, EventArtist, EventStatus, Venue
from users.models import DiaryEntry, User


NOW = datetime(2026, 8, 14, 16, 0, tzinfo=UTC)


class ReviewApiContractTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        city = City.objects.get(name="Boston")
        venue = Venue.objects.create(name="Review Test Venue", city=city)
        artist = Artist.objects.create(name="Review Test Artist")
        cls.event = Event.objects.create(
            title="Review Test Event",
            event_date="2026-07-01",
            start_time="20:00:00",
            venue=venue,
            status=EventStatus.ACTIVE,
        )
        cls.hidden_event = Event.objects.create(
            title="Hidden Review Test Event",
            event_date="2026-07-02",
            start_time="20:00:00",
            venue=venue,
            status=EventStatus.HIDDEN,
        )
        EventArtist.objects.create(event=cls.event, artist=artist, position=1)
        EventArtist.objects.create(
            event=cls.hidden_event,
            artist=artist,
            position=1,
        )
        cls.public_owner = cls.make_user("public@example.com", "public.owner")
        cls.private_owner = cls.make_user(
            "private@example.com",
            "private.owner",
            is_private=True,
        )
        cls.liker = cls.make_user("liker@example.com", "liker")
        cls.other = cls.make_user("other-review@example.com", "review.other")

    @classmethod
    def make_user(cls, email, username, is_private=False):
        return User.objects.create_user(
            email=email,
            password="A-real-password-123!",
            username=username,
            display_name=username,
            is_private=is_private,
        )

    def make_entry(self, user, event=None, rating="4.0"):
        return DiaryEntry.objects.create(
            user=user,
            event=event or self.event,
            rating=rating,
            rated_at=NOW if rating is not None else None,
        )

    def auth_client(self, user):
        client = Client(enforce_csrf_checks=True)
        client.force_login(user)
        client.get("/api/auth/session/")
        return client

    def request(self, client, method, path, payload=None, *, now=NOW):
        token = client.cookies.get("csrftoken")
        headers = {}
        if token is not None:
            headers["HTTP_X_CSRFTOKEN"] = token.value
        with patch("users.services.timezone_now", return_value=now):
            return getattr(client, method)(
                path,
                data=json.dumps(payload or {}),
                content_type="application/json",
                **headers,
            )

    def put_review(self, user, body, event=None, *, now=NOW):
        event = event or self.event
        return self.request(
            self.auth_client(user),
            "put",
            f"/api/events/{event.id}/been/review/",
            {"body": body},
            now=now,
        )

    def public_reviews(self, event=None, **params):
        event = event or self.event
        return self.client.get(
            f"/api/events/{event.id}/reviews/",
            params or {},
        )

    def test_review_requires_an_existing_rated_entry(self):
        missing = self.put_review(self.public_owner, "Missing")
        self.make_entry(self.private_owner, rating=None)
        unrated = self.put_review(self.private_owner, "Unrated")

        self.assertEqual(missing.status_code, 404)
        self.assertEqual(unrated.status_code, 409)
        self.assertIn("rating", unrated.json()["errors"])

    def test_body_is_trimmed_then_validated_at_one_and_one_thousand(self):
        self.make_entry(self.public_owner)
        blank = self.put_review(self.public_owner, " \t\n ")
        too_long = self.put_review(self.public_owner, "x" * 1001)
        boundary = self.put_review(self.public_owner, f"  {'x' * 1000}\n")
        Review = apps.get_model("users", "Review")

        self.assertEqual(blank.status_code, 400)
        self.assertEqual(too_long.status_code, 400)
        self.assertEqual(boundary.status_code, 201)
        self.assertEqual(len(Review.objects.get().body), 1000)

    def test_edit_preserves_original_publication_and_rating(self):
        entry = self.make_entry(self.public_owner, rating="3.5")
        created = self.put_review(self.public_owner, "First")
        edited = self.put_review(
            self.public_owner,
            "Edited body",
            now=datetime(2026, 8, 15, 16, 0, tzinfo=UTC),
        )
        entry.refresh_from_db()

        self.assertEqual(created.status_code, 201)
        self.assertEqual(edited.status_code, 200)
        self.assertEqual(
            created.json()["review"]["published_at"],
            edited.json()["review"]["published_at"],
        )
        self.assertEqual(entry.rating, 3.5)

    def test_review_only_delete_spares_rating_and_cascades_likes(self):
        entry = self.make_entry(self.public_owner)
        created = self.put_review(self.public_owner, "Delete me").json()["review"]
        self.request(
            self.auth_client(self.liker),
            "post",
            f"/api/reviews/{created['id']}/like/",
        )
        deleted = self.request(
            self.auth_client(self.public_owner),
            "delete",
            f"/api/events/{self.event.id}/been/review/",
        )
        ReviewLike = apps.get_model("users", "ReviewLike")
        entry.refresh_from_db()

        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(entry.rating, 4)
        self.assertFalse(ReviewLike.objects.exists())

    def test_rating_removal_reports_and_performs_review_cascade(self):
        self.make_entry(self.public_owner)
        review = self.put_review(self.public_owner, "Cascade").json()["review"]
        self.request(
            self.auth_client(self.liker),
            "post",
            f"/api/reviews/{review['id']}/like/",
        )
        removed = self.request(
            self.auth_client(self.public_owner),
            "delete",
            f"/api/events/{self.event.id}/been/rating/",
        )

        self.assertEqual(removed.status_code, 200)
        self.assertEqual(
            removed.json()["cascade"],
            {"review_deleted": True, "review_likes_deleted": 1},
        )
        self.assertIsNone(removed.json()["entry"]["review"])

    def test_database_allows_only_one_review_per_entry(self):
        entry = self.make_entry(self.public_owner)
        Review = apps.get_model("users", "Review")
        Review.objects.create(entry=entry, body="One", published_at=NOW)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Review.objects.create(entry=entry, body="Two", published_at=NOW)

    def test_self_like_and_duplicate_like_rejected_and_unlike_supported(self):
        self.make_entry(self.public_owner)
        review = self.put_review(self.public_owner, "Liked").json()["review"]
        self_like = self.request(
            self.auth_client(self.public_owner),
            "post",
            f"/api/reviews/{review['id']}/like/",
        )
        liker_client = self.auth_client(self.liker)
        liked = self.request(liker_client, "post", f"/api/reviews/{review['id']}/like/")
        duplicate = self.request(liker_client, "post", f"/api/reviews/{review['id']}/like/")
        unliked = self.request(liker_client, "delete", f"/api/reviews/{review['id']}/like/")

        self.assertEqual(self_like.status_code, 409)
        self.assertEqual(liked.status_code, 201)
        self.assertEqual(duplicate.status_code, 409)
        self.assertEqual(unliked.status_code, 204)
        self.assertEqual(unliked.content, b"")

    def test_public_review_visible_to_guest_and_private_review_owner_only(self):
        self.make_entry(self.public_owner)
        self.put_review(self.public_owner, "Public body")
        self.make_entry(self.private_owner)
        private_review = self.put_review(self.private_owner, "Private body")

        guest_public = self.public_reviews().json()["results"]
        owner_detail = self.auth_client(self.private_owner).get(
            f"/api/events/{self.event.id}/"
        ).json()
        owner_public = self.auth_client(self.private_owner).get(
            f"/api/events/{self.event.id}/reviews/"
        ).json()["results"]
        other_detail = self.auth_client(self.other).get(
            f"/api/events/{self.event.id}/"
        ).json()
        Review = apps.get_model("users", "Review")

        self.assertEqual([review["body"] for review in guest_public], ["Public body"])
        self.assertEqual(
            owner_detail["viewer_entry"]["review"]["id"],
            private_review.json()["review"]["id"],
        )
        self.assertNotIn("Private body", [review["body"] for review in owner_public])
        self.assertIsNone(other_detail["viewer_entry"])
        self.assertNotIn(
            "Private body",
            list(
                Review.objects.visible_to(self.other).values_list("body", flat=True)
            ),
        )
        self.assertNotIn(
            "Private body",
            list(Review.objects.visible_to(None).values_list("body", flat=True)),
        )

    def test_hidden_review_suppressed_from_visibility_and_public_then_resurrects(self):
        entry = self.make_entry(self.public_owner, event=self.hidden_event)
        Review = apps.get_model("users", "Review")
        review = Review.objects.create(entry=entry, body="Hidden body", published_at=NOW)

        self.assertFalse(Review.objects.visible_to(self.public_owner).exists())
        self.assertFalse(Review.objects.for_public_section().exists())
        self.assertEqual(self.public_reviews(self.hidden_event).status_code, 404)

        self.hidden_event.status = EventStatus.ACTIVE
        self.hidden_event.save(update_fields=("status",))
        self.assertEqual(Review.objects.visible_to(self.public_owner).get(), review)
        self.assertEqual(Review.objects.for_public_section().get(), review)

    def test_most_liked_orders_by_likes_then_publication_and_newest_is_alternate(self):
        Review = apps.get_model("users", "Review")
        first_entry = self.make_entry(self.public_owner)
        second_entry = self.make_entry(self.other)
        first = Review.objects.create(entry=first_entry, body="Older popular", published_at=NOW)
        second = Review.objects.create(
            entry=second_entry,
            body="Newer tied",
            published_at=datetime(2026, 8, 15, 16, tzinfo=UTC),
        )
        ReviewLike = apps.get_model("users", "ReviewLike")
        ReviewLike.objects.create(user=self.liker, review=first)
        ReviewLike.objects.create(user=self.liker, review=second)

        tied = self.public_reviews().json()["results"]
        ReviewLike.objects.create(user=self.private_owner, review=first)
        popular = self.public_reviews().json()["results"]
        newest = self.public_reviews(sort="newest").json()["results"]

        self.assertEqual([item["id"] for item in tied], [second.id, first.id])
        self.assertEqual([item["id"] for item in popular], [first.id, second.id])
        self.assertEqual([item["id"] for item in newest], [second.id, first.id])

    def test_private_liker_counts_without_identity_exposure(self):
        self.make_entry(self.public_owner)
        review = self.put_review(self.public_owner, "Anonymous liker").json()["review"]
        self.request(
            self.auth_client(self.private_owner),
            "post",
            f"/api/reviews/{review['id']}/like/",
        )
        payload = self.public_reviews().json()["results"][0]

        self.assertEqual(payload["like_count"], 1)
        self.assertNotIn("likers", payload)
        self.assertNotIn("viewer_has_liked", payload)

    def test_public_review_author_avatar_is_additive_and_nullable(self):
        Review = apps.get_model("users", "Review")
        self.public_owner.avatar = "https://images.example.test/reviewer.jpg"
        self.public_owner.save(update_fields=("avatar",))
        Review.objects.create(entry=self.make_entry(self.public_owner), body="Attributed review", published_at=NOW)
        attributed = self.public_reviews().json()["results"][0]

        Review.objects.create(entry=self.make_entry(self.other), body="Null avatar review", published_at=NOW)
        results = self.public_reviews().json()["results"]
        null_attributed = next(item for item in results if item["author"]["id"] == self.other.id)

        self.assertEqual(attributed["author"]["avatar"], self.public_owner.avatar)
        self.assertIsNone(null_attributed["author"]["avatar"])
        self.assertNotIn("viewer_has_liked", attributed)
        self.assertNotIn("likers", attributed)

    def test_guest_like_requires_authentication_and_diary_reports_review_presence(self):
        self.make_entry(self.public_owner)
        review = self.put_review(self.public_owner, "Diary marker").json()["review"]
        guest = Client(enforce_csrf_checks=True)
        guest.get("/api/auth/session/")
        denied = self.request(guest, "post", f"/api/reviews/{review['id']}/like/")
        diary = self.auth_client(self.public_owner).get("/api/me/been/").json()

        self.assertEqual(denied.status_code, 401)
        self.assertTrue(diary["results"][0]["has_review"])
