import json
import io
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from django.db import IntegrityError, connection, transaction
from django.db.models.deletion import RestrictedError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from PIL import Image

from catalog.models import Artist, City, Event, EventArtist, EventStatus, Venue
from users.models import DiaryEntry, Follow, FollowStatus, Review, ReviewLike, User


NOW = datetime(2026, 8, 20, 16, 0, tzinfo=UTC)


class ProfileApiContractTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.boston = City.objects.get(name="Boston")
        cls.new_york = City.objects.get(name="New York City")
        cls.venue = Venue.objects.create(name="Profile Test Venue", city=cls.boston)
        cls.artist = Artist.objects.create(name="Profile Test Artist")
        cls.events = []
        for offset, title in enumerate(("Old Profile Event", "Middle Profile Event", "New Profile Event"), start=1):
            event = Event.objects.create(
                title=title,
                event_date=f"2026-07-0{offset}",
                start_time="20:00:00",
                venue=cls.venue,
                status=EventStatus.ACTIVE,
            )
            EventArtist.objects.create(event=event, artist=cls.artist, position=1)
            cls.events.append(event)
        cls.hidden_event = Event.objects.create(
            title="Hidden Profile Event",
            event_date="2026-07-04",
            start_time="20:00:00",
            venue=cls.venue,
            status=EventStatus.HIDDEN,
        )
        EventArtist.objects.create(event=cls.hidden_event, artist=cls.artist, position=1)
        cls.public_user = cls.make_user("public@profile.test", "profile.public")
        cls.private_user = cls.make_user(
            "private@profile.test", "profile.private", is_private=True
        )
        cls.viewer = cls.make_user("viewer@profile.test", "profile.viewer")
        cls.follower = cls.make_user("follower@profile.test", "profile.follower")

    @classmethod
    def make_user(cls, email, username, *, is_private=False):
        return User.objects.create_user(
            email=email,
            password="A-real-password-123!",
            username=username,
            display_name=username,
            is_private=is_private,
        )

    def auth_client(self, user):
        client = Client(enforce_csrf_checks=True)
        client.force_login(user)
        client.get("/api/auth/session/")
        return client

    def put_json(self, client, path, payload):
        token = client.cookies.get("csrftoken")
        return client.put(
            path,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token.value,
        )

    def entry(self, user, event, *, rating="4.0", rated_at=NOW):
        return DiaryEntry.objects.create(
            user=user,
            event=event,
            rating=rating,
            rated_at=rated_at if rating is not None else None,
        )

    def review(self, user, event, body, *, published_at=NOW, rating="4.0"):
        return Review.objects.create(
            entry=self.entry(user, event, rating=rating),
            body=body,
            published_at=published_at,
        )

    def approve(self, follower, followee):
        return Follow.objects.create(
            follower=follower,
            followee=followee,
            status=FollowStatus.APPROVED,
            created_at=NOW,
            approved_at=NOW,
        )

    def test_profile_resolution_is_case_insensitive_and_unknown_is_not_found(self):
        response = self.client.get("/api/users/PROFILE.PUBLIC/")
        missing = self.client.get("/api/users/no.such.user/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["profile"]["username"], "profile.public")
        self.assertEqual(missing.status_code, 404)

    def test_private_stub_has_only_identity_and_no_restricted_or_email_fields(self):
        self.private_user.avatar = None
        self.private_user.bio = "Private bio"
        self.private_user.home_city = self.boston
        self.private_user.save(update_fields=("avatar", "bio", "home_city"))
        self.entry(self.private_user, self.events[0])
        self.approve(self.follower, self.private_user)
        self.approve(self.private_user, self.public_user)

        response = self.client.get(f"/api/users/{self.private_user.username}/")
        statistics = self.client.get(
            f"/api/users/{self.private_user.username}/stats/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()), {"profile", "access"})
        self.assertEqual(response.json()["access"], "stub")
        self.assertEqual(
            set(response.json()["profile"]),
            {
                "id",
                "username",
                "display_name",
                "avatar",
                "bio",
                "home_city",
                "follower_count",
                "following_count",
            },
        )
        self.assertEqual(response.json()["profile"]["follower_count"], 1)
        self.assertEqual(response.json()["profile"]["following_count"], 1)
        self.assertEqual(statistics.status_code, 403)
        self.assertNotIn("followers", response.json())
        self.assertNotIn("following", response.json())
        serialized = json.dumps(response.json())
        for forbidden in ("email", "is_private", "statistics", "diary"):
            self.assertNotIn(forbidden, serialized)

    def test_public_approved_follower_and_owner_access_are_named(self):
        self.approve(self.follower, self.private_user)

        public = self.client.get(f"/api/users/{self.public_user.username}/")
        follower = self.auth_client(self.follower).get(
            f"/api/users/{self.private_user.username}/"
        )
        owner = self.auth_client(self.private_user).get(
            f"/api/users/{self.private_user.username}/"
        )

        self.assertEqual(public.json()["access"], "full")
        self.assertEqual(follower.json()["access"], "full")
        self.assertEqual(owner.json()["access"], "owner")
        self.assertEqual(owner.json()["account"], {"is_private": True})
        self.assertNotIn("account", public.json())
        self.assertNotIn("relationship", owner.json())
        self.assertEqual(follower.json()["profile"]["follower_count"], 1)
        self.assertEqual(owner.json()["profile"]["follower_count"], 1)

    def test_followers_and_following_return_only_approved_public_identities(self):
        self.approve(self.follower, self.public_user)
        self.approve(self.viewer, self.public_user)
        self.approve(self.public_user, self.private_user)
        Follow.objects.create(
            follower=self.viewer,
            followee=self.private_user,
            status=FollowStatus.PENDING,
            created_at=NOW,
            approved_at=None,
        )

        first_page = self.client.get(
            f"/api/users/{self.public_user.username}/followers/",
            {"page": 1, "page_size": 1},
        )
        second_page = self.client.get(
            f"/api/users/{self.public_user.username}/followers/",
            {"page": 2, "page_size": 1},
        )
        following = self.client.get(
            f"/api/users/{self.public_user.username}/following/"
        )
        private_followers = self.client.get(
            f"/api/users/{self.private_user.username}/followers/"
        )

        self.assertEqual((first_page.status_code, second_page.status_code), (200, 200))
        self.assertEqual(first_page.json()["pagination"]["total_results"], 2)
        follower_usernames = {
            first_page.json()["results"][0]["username"],
            second_page.json()["results"][0]["username"],
        }
        self.assertEqual(
            follower_usernames,
            {self.follower.username, self.viewer.username},
        )
        self.assertEqual(
            [user["username"] for user in following.json()["results"]],
            [self.private_user.username],
        )
        self.assertEqual(
            [user["username"] for user in private_followers.json()["results"]],
            [self.public_user.username],
        )
        serialized = json.dumps(
            first_page.json()["results"] + following.json()["results"]
        )
        for forbidden in ("email", "bio", "home_city", "is_private"):
            self.assertNotIn(forbidden, serialized)

    def test_connection_lists_validate_pagination_and_unknown_profiles(self):
        invalid = self.client.get(
            f"/api/users/{self.public_user.username}/followers/", {"page": 0}
        )
        out_of_range = self.client.get(
            f"/api/users/{self.public_user.username}/following/", {"page": 2}
        )
        missing = self.client.get("/api/users/no.such.user/followers/")

        self.assertEqual((invalid.status_code, out_of_range.status_code, missing.status_code), (400, 404, 404))

    def test_relationship_capabilities_cover_follow_request_withdraw_and_follows_you(self):
        inverse = self.approve(self.public_user, self.viewer)
        none = self.auth_client(self.viewer).get(
            f"/api/users/{self.public_user.username}/"
        ).json()["relationship"]
        Follow.objects.create(
            follower=self.viewer,
            followee=self.private_user,
            status=FollowStatus.PENDING,
            created_at=NOW,
            approved_at=None,
        )
        pending = self.auth_client(self.viewer).get(
            f"/api/users/{self.private_user.username}/"
        ).json()["relationship"]

        self.assertEqual(
            none,
            {
                "outgoing_status": None,
                "follows_you": True,
                "can_follow": True,
                "can_unfollow": False,
                "follow_action": "follow",
            },
        )
        self.assertEqual(pending["outgoing_status"], "pending")
        self.assertFalse(pending["can_follow"])
        self.assertTrue(pending["can_unfollow"])
        self.assertIsNone(pending["follow_action"])
        self.assertTrue(Follow.objects.filter(pk=inverse.pk).exists())

    def test_private_content_is_403_not_empty_while_authorized_empty_is_200(self):
        blocked_been = self.client.get(
            f"/api/users/{self.private_user.username}/been/"
        )
        blocked_reviews = self.client.get(
            f"/api/users/{self.private_user.username}/reviews/"
        )
        self.approve(self.follower, self.private_user)
        allowed = self.auth_client(self.follower).get(
            f"/api/users/{self.private_user.username}/been/"
        )

        self.assertEqual(blocked_been.status_code, 403)
        self.assertEqual(blocked_reviews.status_code, 403)
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(allowed.json()["results"], [])

    def test_approved_follower_sees_private_been_and_review_through_sanctioned_boundaries(self):
        entry = self.entry(self.private_user, self.events[0])
        review = Review.objects.create(
            entry=entry,
            body="Follower-visible review",
            published_at=NOW,
        )
        self.approve(self.follower, self.private_user)
        client = self.auth_client(self.follower)

        been = client.get(f"/api/users/{self.private_user.username}/been/")
        reviews = client.get(f"/api/users/{self.private_user.username}/reviews/")

        self.assertEqual([item["id"] for item in been.json()["results"]], [entry.id])
        self.assertEqual([item["id"] for item in reviews.json()["results"]], [review.id])

    def test_most_liked_tie_uses_publication_then_id_tiebreak(self):
        older = self.review(
            self.public_user,
            self.events[0],
            "Older tie",
            published_at=NOW - timedelta(days=1),
        )
        first = self.review(self.public_user, self.events[1], "First", published_at=NOW)
        second = self.review(self.public_user, self.events[2], "Second", published_at=NOW)

        response = self.client.get(
            f"/api/users/{self.public_user.username}/reviews/",
            {"sort": "most_liked"},
        )

        self.assertEqual(
            [item["id"] for item in response.json()["results"]],
            [second.id, first.id, older.id],
        )

    def test_public_been_orders_by_event_history_includes_unrated_and_suppresses_hidden(self):
        old = self.entry(self.public_user, self.events[0])
        newest = self.entry(self.public_user, self.events[2], rating=None)
        hidden = self.entry(self.public_user, self.hidden_event)

        response = self.client.get(f"/api/users/{self.public_user.username}/been/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["id"] for row in response.json()["results"]], [newest.id, old.id])
        self.assertIsNone(response.json()["results"][0]["rating"])
        self.assertNotIn("created_at", response.json()["results"][0])
        self.assertNotIn("rated_at", response.json()["results"][0])
        self.hidden_event.status = EventStatus.ACTIVE
        self.hidden_event.save(update_fields=("status",))
        resurrected = self.client.get(f"/api/users/{self.public_user.username}/been/")
        self.assertEqual(resurrected.json()["results"][0]["id"], hidden.id)

    def test_reviews_support_all_four_stable_sorts(self):
        older = self.review(
            self.public_user,
            self.events[0],
            "equal",
            published_at=NOW - timedelta(days=2),
        )
        newer = self.review(
            self.public_user,
            self.events[1],
            "equal",
            published_at=NOW - timedelta(days=1),
        )
        longest = self.review(
            self.public_user,
            self.events[2],
            "the longest body",
            published_at=NOW,
        )
        ReviewLike.objects.create(user=self.viewer, review=older)
        ReviewLike.objects.create(user=self.follower, review=older)
        ReviewLike.objects.create(user=self.viewer, review=newer)

        def ids(sort):
            response = self.client.get(
                f"/api/users/{self.public_user.username}/reviews/", {"sort": sort}
            )
            self.assertEqual(response.status_code, 200)
            return [row["id"] for row in response.json()["results"]]

        self.assertEqual(ids("newest"), [longest.id, newer.id, older.id])
        self.assertEqual(ids("oldest"), [older.id, newer.id, longest.id])
        self.assertEqual(ids("most_liked"), [older.id, newer.id, longest.id])
        self.assertEqual(ids("longest"), [longest.id, newer.id, older.id])

    def test_longest_equal_length_uses_publication_then_id_tiebreak(self):
        first = self.review(self.public_user, self.events[0], "same", published_at=NOW)
        second = self.review(self.public_user, self.events[1], "size", published_at=NOW)

        response = self.client.get(
            f"/api/users/{self.public_user.username}/reviews/", {"sort": "longest"}
        )

        self.assertEqual(
            [row["id"] for row in response.json()["results"]],
            [second.id, first.id],
        )

    def test_profile_edit_validates_and_preserves_nonempty_bio_verbatim(self):
        client = self.auth_client(self.public_user)
        self.public_user.avatar = "https://legacy.example.test/avatar.png"
        self.public_user.save(update_fields=("avatar",))
        payload = {
            "display_name": "  Updated Name  ",
            "bio": "  visible bio\n",
            "home_city_id": self.new_york.id,
        }
        response = self.put_json(client, "/api/me/profile/", payload)
        self.public_user.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.public_user.display_name, "Updated Name")
        self.assertEqual(self.public_user.avatar, "https://legacy.example.test/avatar.png")
        self.assertEqual(self.public_user.bio, "  visible bio\n")
        self.assertEqual(self.public_user.home_city, self.new_york)

    def test_profile_edit_normalizes_semantically_empty_fields_and_validates_boundaries(self):
        client = self.auth_client(self.public_user)
        valid = {
            "display_name": "x" * 50,
            "bio": " \t\n ",
            "home_city_id": None,
        }
        cleared = self.put_json(client, "/api/me/profile/", valid)
        too_long_bio = self.put_json(client, "/api/me/profile/", {**valid, "bio": "x" * 151})
        bad_name = self.put_json(client, "/api/me/profile/", {**valid, "display_name": "  "})
        bad_city = self.put_json(client, "/api/me/profile/", {**valid, "home_city_id": 999999})
        bad_avatar = self.put_json(
            client,
            "/api/me/profile/",
            {**valid, "avatar": "https://example.test/not-accepted.jpg"},
        )
        self.public_user.refresh_from_db()

        self.assertEqual(cleared.status_code, 200)
        self.assertIsNone(self.public_user.avatar)
        self.assertIsNone(self.public_user.bio)
        for response, field in (
            (too_long_bio, "bio"),
            (bad_name, "display_name"),
            (bad_city, "home_city_id"),
            (bad_avatar, "avatar"),
        ):
            self.assertEqual(response.status_code, 400)
            self.assertIn(field, response.json()["errors"])

    def test_avatar_upload_validates_crops_and_removes(self):
        client = self.auth_client(self.public_user)
        token = client.cookies["csrftoken"].value
        image = Image.new("RGB", (900, 600), "red")
        source = io.BytesIO()
        image.save(source, "PNG")
        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            uploaded = client.post(
                "/api/me/profile/avatar/",
                {"avatar": SimpleUploadedFile("photo.png", source.getvalue(), content_type="image/png")},
                HTTP_X_CSRFTOKEN=token,
            )
            self.assertEqual(uploaded.status_code, 200)
            self.public_user.refresh_from_db()
            stored_path = self.public_user.avatar.split("/media/", 1)[1]
            with Image.open(f"{media_root}/{stored_path}") as stored:
                self.assertEqual((stored.format, stored.size), ("JPEG", (512, 512)))
            removed = client.delete("/api/me/profile/avatar/", HTTP_X_CSRFTOKEN=token)
            self.assertEqual(removed.status_code, 200)
            self.public_user.refresh_from_db()
            self.assertIsNone(self.public_user.avatar)

    def test_avatar_upload_rejects_invalid_type_and_oversize(self):
        client = self.auth_client(self.public_user)
        token = client.cookies["csrftoken"].value
        invalid = client.post("/api/me/profile/avatar/", {"avatar": SimpleUploadedFile("bad.gif", b"GIF89a", content_type="image/gif")}, HTTP_X_CSRFTOKEN=token)
        oversize = client.post("/api/me/profile/avatar/", {"avatar": SimpleUploadedFile("large.png", b"x" * (2 * 1024 * 1024 + 1), content_type="image/png")}, HTTP_X_CSRFTOKEN=token)
        wide_image = Image.new("RGB", (4097, 1), "red")
        wide_source = io.BytesIO()
        wide_image.save(wide_source, "PNG")
        oversized_dimensions = client.post(
            "/api/me/profile/avatar/",
            {
                "avatar": SimpleUploadedFile(
                    "wide.png",
                    wide_source.getvalue(),
                    content_type="image/png",
                )
            },
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(
            (invalid.status_code, oversize.status_code, oversized_dimensions.status_code),
            (400, 400, 400),
        )
        self.assertIn("avatar", invalid.json()["errors"])
        self.assertIn("avatar", oversize.json()["errors"])
        self.assertIn("avatar", oversized_dimensions.json()["errors"])

    def test_avatar_upload_handles_decompression_bomb_rejection(self):
        client = self.auth_client(self.public_user)
        token = client.cookies["csrftoken"].value
        upload = SimpleUploadedFile("bomb.png", b"not-decoded", content_type="image/png")

        with patch(
            "users.views.Image.open",
            side_effect=Image.DecompressionBombError("unsafe pixel count"),
        ):
            response = client.post(
                "/api/me/profile/avatar/",
                {"avatar": upload},
                HTTP_X_CSRFTOKEN=token,
            )

        self.assertEqual(response.status_code, 400)
        self.assertIn("avatar", response.json()["errors"])

    def test_avatar_removal_never_deletes_another_users_file(self):
        client = self.auth_client(self.public_user)
        token = client.cookies["csrftoken"].value
        victim_name = f"avatars/{self.private_user.id}/{'a' * 32}.jpg"
        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            victim_path = Path(media_root) / victim_name
            victim_path.parent.mkdir(parents=True)
            victim_path.write_bytes(b"victim-avatar")
            self.public_user.avatar = f"https://testserver/media/{victim_name}"
            self.public_user.save(update_fields=("avatar",))

            removed = client.delete(
                "/api/me/profile/avatar/",
                HTTP_X_CSRFTOKEN=token,
            )

            self.assertEqual(removed.status_code, 200)
            self.assertTrue(victim_path.exists())

    def test_home_city_delete_is_restricted_at_orm_and_database_layers(self):
        city = City.objects.create(
            name="Profile Restrict City",
            region_code="PR",
            region_name="Profile Restrict",
            country_code="US",
            timezone="America/New_York",
        )
        user = self.make_user("restrict@profile.test", "profile.restrict")
        user.home_city = city
        user.save(update_fields=("home_city",))

        with self.assertRaises(RestrictedError):
            city.delete()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute('DELETE FROM CITY WHERE id = %s', [city.id])
        user.refresh_from_db()
        self.assertEqual(user.home_city_id, city.id)
