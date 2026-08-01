import json
import threading
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from django.apps import apps
from django.db import IntegrityError, close_old_connections, transaction
from django.test import Client, TestCase, TransactionTestCase

from catalog.models import Artist, City, Event, EventArtist, EventStatus, Venue
from users.models import DiaryEntry, Review, User


NOW = datetime(2026, 8, 20, 16, 0, tzinfo=UTC)


class SocialApiContractTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        city = City.objects.get(name="Boston")
        venue = Venue.objects.create(name="Social Test Venue", city=city)
        artist = Artist.objects.create(name="Social Test Artist")
        cls.event = Event.objects.create(
            title="Social Test Event",
            event_date="2026-07-01",
            start_time="20:00:00",
            venue=venue,
            status=EventStatus.ACTIVE,
        )
        cls.other_event = Event.objects.create(
            title="Unrelated Social Test Event",
            event_date="2026-07-02",
            start_time="20:00:00",
            venue=venue,
            status=EventStatus.ACTIVE,
        )
        cls.hidden_event = Event.objects.create(
            title="Hidden Social Test Event",
            event_date="2026-07-03",
            start_time="20:00:00",
            venue=venue,
            status=EventStatus.HIDDEN,
        )
        for event in (cls.event, cls.other_event, cls.hidden_event):
            EventArtist.objects.create(event=event, artist=artist, position=1)
        cls.viewer = cls.make_user("viewer@social.test", "social.viewer")
        cls.public_user = cls.make_user("public@social.test", "social.public")
        cls.private_user = cls.make_user(
            "private@social.test", "social.private", is_private=True
        )
        cls.other = cls.make_user("other@social.test", "social.other")
        cls.popular = cls.make_user("popular@social.test", "social.popular")

    @classmethod
    def make_user(cls, email, username, is_private=False):
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

    def request(self, client, method, path, payload=None):
        token = client.cookies.get("csrftoken")
        headers = {"HTTP_X_CSRFTOKEN": token.value} if token else {}
        with patch("users.services.timezone_now", return_value=NOW):
            return getattr(client, method)(
                path,
                data=json.dumps(payload or {}),
                content_type="application/json",
                **headers,
            )

    def follow(self, follower, followee):
        return self.request(
            self.auth_client(follower),
            "post",
            f"/api/users/{followee.id}/follow/",
        )

    def entry(self, user, *, event=None, rating="4.0", rated_at=NOW):
        return DiaryEntry.objects.create(
            user=user,
            event=event or self.event,
            rating=rating,
            rated_at=rated_at,
        )

    def review(self, user, body, *, event=None, published_at=NOW):
        return Review.objects.create(
            entry=self.entry(user, event=event),
            body=body,
            published_at=published_at,
        )

    def test_public_and_private_follow_lifecycle_and_conflicts(self):
        public = self.follow(self.viewer, self.public_user)
        private = self.follow(self.viewer, self.private_user)
        duplicate = self.follow(self.viewer, self.private_user)
        self_follow = self.follow(self.viewer, self.viewer)
        unknown = self.request(
            self.auth_client(self.viewer), "post", "/api/users/999999/follow/"
        )
        Notification = apps.get_model("users", "Notification")

        self.assertEqual(public.status_code, 201)
        self.assertEqual(public.json()["follow"]["status"], "approved")
        self.assertEqual(
            public.json()["follow"]["created_at"],
            public.json()["follow"]["approved_at"],
        )
        self.assertEqual(private.status_code, 201)
        self.assertEqual(private.json()["follow"]["status"], "pending")
        self.assertIsNone(private.json()["follow"]["approved_at"])
        self.assertEqual(duplicate.status_code, 409)
        self.assertEqual(self_follow.status_code, 409)
        self.assertEqual(unknown.status_code, 404)
        self.assertCountEqual(
            Notification.objects.values_list("type", flat=True),
            ["follow", "follow_request"],
        )

    def test_accept_preserves_request_time_and_decline_is_silent(self):
        first = self.follow(self.viewer, self.private_user).json()["follow"]
        accepted = self.request(
            self.auth_client(self.private_user),
            "post",
            f"/api/me/follow-requests/{self.viewer.id}/accept/",
        )
        self.follow(self.other, self.private_user)
        Notification = apps.get_model("users", "Notification")
        before_decline = Notification.objects.count()
        declined = self.request(
            self.auth_client(self.private_user),
            "post",
            f"/api/me/follow-requests/{self.other.id}/decline/",
        )

        self.assertEqual(accepted.status_code, 200)
        self.assertEqual(accepted.json()["follow"]["created_at"], first["created_at"])
        self.assertIsNotNone(accepted.json()["follow"]["approved_at"])
        self.assertEqual(declined.status_code, 204)
        self.assertEqual(Notification.objects.count(), before_decline)
        self.assertEqual(
            Notification.objects.filter(
                recipient=self.viewer,
                type="request_accepted",
            ).count(),
            1,
        )

    def test_pending_list_is_owner_scoped_and_wrong_target_actions_are_404(self):
        self.follow(self.viewer, self.private_user)
        owner = self.auth_client(self.private_user).get("/api/me/follow-requests/")
        other = self.auth_client(self.other).get("/api/me/follow-requests/")
        wrong = self.request(
            self.auth_client(self.other),
            "post",
            f"/api/me/follow-requests/{self.viewer.id}/accept/",
        )

        self.assertEqual(owner.status_code, 200)
        self.assertEqual(owner.json()["results"][0]["user"]["id"], self.viewer.id)
        self.assertEqual(other.json()["results"], [])
        self.assertEqual(wrong.status_code, 404)

    def test_privacy_bulk_accepts_at_one_timestamp_and_same_value_is_noop(self):
        self.follow(self.viewer, self.private_user)
        self.follow(self.other, self.private_user)
        changed = self.request(
            self.auth_client(self.private_user),
            "put",
            "/api/me/privacy/",
            {"is_private": False},
        )
        Follow = apps.get_model("users", "Follow")
        rows = list(Follow.objects.filter(followee=self.private_user))
        no_op = self.request(
            self.auth_client(self.private_user),
            "put",
            "/api/me/privacy/",
            {"is_private": False},
        )

        self.assertEqual(changed.status_code, 200)
        self.assertEqual(changed.json()["privacy"]["pending_requests_approved"], 2)
        self.assertEqual({row.status for row in rows}, {"approved"})
        self.assertEqual(len({row.approved_at for row in rows}), 1)
        self.assertEqual(no_op.json()["privacy"]["pending_requests_approved"], 0)

    def test_follow_database_biconditional_and_self_checks(self):
        Follow = apps.get_model("users", "Follow")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Follow.objects.create(
                follower=self.viewer,
                followee=self.public_user,
                status="pending",
                created_at=NOW,
                approved_at=NOW,
            )
        with self.assertRaises(IntegrityError), transaction.atomic():
            Follow.objects.create(
                follower=self.viewer,
                followee=self.public_user,
                status="approved",
                created_at=NOW,
                approved_at=None,
            )
        with self.assertRaises(IntegrityError), transaction.atomic():
            Follow.objects.create(
                follower=self.viewer,
                followee=self.viewer,
                status="approved",
                created_at=NOW,
                approved_at=NOW,
            )

    def test_visibility_boundary_widens_without_unscoped_endpoint_leak(self):
        public_entry = self.entry(self.public_user)
        private_entry = self.entry(self.private_user)
        self.follow(self.viewer, self.private_user)
        self.request(
            self.auth_client(self.private_user),
            "post",
            f"/api/me/follow-requests/{self.viewer.id}/accept/",
        )

        self.assertIn(public_entry, DiaryEntry.objects.visible_to(None))
        self.assertIn(private_entry, DiaryEntry.objects.visible_to(self.viewer))
        self.assertNotIn(private_entry, DiaryEntry.objects.visible_to(self.other))
        self.assertIsNone(
            self.auth_client(self.viewer).get(
                f"/api/events/{self.other_event.id}/"
            ).json()["viewer_entry"]
        )
        diary_ids = {
            item["id"]
            for item in self.auth_client(self.viewer)
            .get("/api/me/been/")
            .json()["results"]
        }
        self.assertNotIn(public_entry.id, diary_ids)

    def test_private_review_widens_to_follower_but_public_section_stays_public(self):
        private_review = self.review(self.private_user, "Follower only")
        self.follow(self.viewer, self.private_user)
        self.request(
            self.auth_client(self.private_user),
            "post",
            f"/api/me/follow-requests/{self.viewer.id}/accept/",
        )

        self.assertIn(private_review, Review.objects.visible_to(self.viewer))
        self.assertNotIn(private_review, Review.objects.visible_to(self.other))
        self.assertNotIn(private_review, Review.objects.for_public_section())
        public_bodies = [
            item["body"]
            for item in self.client.get(
                f"/api/events/{self.event.id}/reviews/"
            ).json()["results"]
        ]
        self.assertNotIn("Follower only", public_bodies)

    def test_public_review_follow_capabilities_are_auth_only(self):
        review = self.review(self.public_user, "Follow this author")
        guest = self.client.get(f"/api/events/{self.event.id}/reviews/").json()[
            "results"
        ][0]
        signed_in = self.auth_client(self.viewer).get(
            f"/api/events/{self.event.id}/reviews/"
        ).json()["results"][0]
        self.follow(self.viewer, self.public_user)
        following = self.auth_client(self.viewer).get(
            f"/api/events/{self.event.id}/reviews/"
        ).json()["results"][0]

        self.assertEqual(guest["id"], review.id)
        for field in ("viewer_follows", "can_follow", "can_unfollow"):
            self.assertNotIn(field, guest)
        self.assertFalse(signed_in["viewer_follows"])
        self.assertTrue(signed_in["can_follow"])
        self.assertTrue(following["viewer_follows"])
        self.assertTrue(following["can_unfollow"])

    def test_circle_list_excludes_self_summary_includes_self_and_rating_only(self):
        self.entry(self.viewer, rating="5.0")
        followed = self.entry(self.private_user, rating="3.0")
        self.follow(self.viewer, self.private_user)
        self.request(
            self.auth_client(self.private_user),
            "post",
            f"/api/me/follow-requests/{self.viewer.id}/accept/",
        )
        payload = self.auth_client(self.viewer).get(
            f"/api/events/{self.event.id}/circle/"
        ).json()

        self.assertEqual(payload["rating_summary"]["count"], 2)
        self.assertEqual(payload["rating_summary"]["average"], 4.0)
        self.assertEqual([item["id"] for item in payload["results"]], [followed.id])
        self.assertIsNone(payload["results"][0]["review"])

    def test_circle_orders_by_rating_time_not_review_publication(self):
        older = self.entry(
            self.public_user,
            rated_at=NOW - timedelta(days=2),
        )
        Review.objects.create(
            entry=older,
            body="Published later",
            published_at=NOW + timedelta(days=1),
        )
        newer = self.entry(self.other, rated_at=NOW - timedelta(days=1))
        self.follow(self.viewer, self.public_user)
        self.follow(self.viewer, self.other)
        results = self.auth_client(self.viewer).get(
            f"/api/events/{self.event.id}/circle/"
        ).json()["results"]

        self.assertEqual([item["id"] for item in results], [newer.id, older.id])

    def test_hidden_event_suppresses_circle_and_resurrection_restores_it(self):
        entry = self.entry(self.public_user, event=self.hidden_event)
        self.follow(self.viewer, self.public_user)
        hidden = self.auth_client(self.viewer).get(
            f"/api/events/{self.hidden_event.id}/circle/"
        )
        self.hidden_event.status = EventStatus.ACTIVE
        self.hidden_event.save(update_fields=("status",))
        restored = self.auth_client(self.viewer).get(
            f"/api/events/{self.hidden_event.id}/circle/"
        )

        self.assertEqual(hidden.status_code, 404)
        self.assertEqual(restored.json()["results"][0]["id"], entry.id)

    def test_unfollow_removes_circle_access_but_retracts_no_notification(self):
        self.entry(self.public_user)
        self.follow(self.viewer, self.public_user)
        Notification = apps.get_model("users", "Notification")
        before = Notification.objects.count()
        removed = self.request(
            self.auth_client(self.viewer),
            "delete",
            f"/api/users/{self.public_user.id}/follow/",
        )
        circle = self.auth_client(self.viewer).get(
            f"/api/events/{self.event.id}/circle/"
        ).json()

        self.assertEqual(removed.status_code, 204)
        self.assertEqual(removed.content, b"")
        self.assertEqual(circle["results"], [])
        self.assertEqual(Notification.objects.count(), before)

    def test_review_like_creates_exactly_one_historical_notification(self):
        review = self.review(self.public_user, "Notify me")
        client = self.auth_client(self.viewer)
        first = self.request(client, "post", f"/api/reviews/{review.id}/like/")
        duplicate = self.request(client, "post", f"/api/reviews/{review.id}/like/")
        unliked = self.request(client, "delete", f"/api/reviews/{review.id}/like/")
        Notification = apps.get_model("users", "Notification")

        self.assertEqual(first.status_code, 201)
        self.assertEqual(duplicate.status_code, 409)
        self.assertEqual(unliked.status_code, 204)
        self.assertEqual(
            Notification.objects.filter(type="review_like", review=review).count(),
            1,
        )

    def test_review_deletion_cascades_like_notification(self):
        review = self.review(self.public_user, "Delete notification")
        self.request(
            self.auth_client(self.viewer), "post", f"/api/reviews/{review.id}/like/"
        )
        Notification = apps.get_model("users", "Notification")
        review.delete()
        self.assertFalse(Notification.objects.exists())

    def test_notifications_order_mark_read_and_mark_all_preserve_history(self):
        self.follow(self.viewer, self.public_user)
        self.follow(self.other, self.public_user)
        client = self.auth_client(self.public_user)
        listed = client.get("/api/me/notifications/", {"page_size": 1})
        results = listed.json()["results"]
        next_page = client.get(
            "/api/me/notifications/",
            {"page_size": 1, "cursor": listed.json()["next_cursor"]},
        ).json()
        first_id = results[0]["id"]
        first = self.request(client, "post", f"/api/me/notifications/{first_id}/read/")
        again = self.request(client, "post", f"/api/me/notifications/{first_id}/read/")
        all_read = self.request(client, "post", "/api/me/notifications/read-all/")

        self.assertEqual(
            [item["id"] for item in results],
            sorted([item["id"] for item in results], reverse=True),
        )
        self.assertNotEqual(results[0]["id"], next_page["results"][0]["id"])
        self.assertEqual(
            first.json()["notification"]["read_at"],
            again.json()["notification"]["read_at"],
        )
        self.assertEqual(all_read.json()["updated_count"], 1)

    def test_notification_database_biconditionals_reject_invalid_rows(self):
        Notification = apps.get_model("users", "Notification")
        review = self.review(self.public_user, "Constraint target")
        for values in (
            {
                "recipient": self.viewer,
                "actor": self.viewer,
                "type": "follow",
                "review": None,
            },
            {
                "recipient": self.public_user,
                "actor": self.viewer,
                "type": "review_like",
                "review": None,
            },
            {
                "recipient": self.public_user,
                "actor": self.viewer,
                "type": "follow",
                "review": review,
            },
        ):
            with self.subTest(values=values), self.assertRaises(IntegrityError), transaction.atomic():
                Notification.objects.create(created_at=NOW, **values)

    def test_real_follower_count_orders_public_review_tie(self):
        first = self.review(self.public_user, "Less followed")
        second = self.review(
            self.popular,
            "More followed",
            published_at=NOW - timedelta(days=1),
        )
        self.follow(self.viewer, self.popular)
        payload = self.client.get(f"/api/events/{self.event.id}/reviews/").json()
        self.assertEqual([item["id"] for item in payload["results"]], [second.id, first.id])

    def test_guest_writes_are_401_and_circle_requires_authentication(self):
        guest = Client(enforce_csrf_checks=True)
        guest.get("/api/auth/session/")
        for method, path in (
            ("post", f"/api/users/{self.public_user.id}/follow/"),
            ("delete", f"/api/users/{self.public_user.id}/follow/"),
            ("put", "/api/me/privacy/"),
            ("post", "/api/me/notifications/read-all/"),
        ):
            with self.subTest(path=path):
                self.assertEqual(self.request(guest, method, path).status_code, 401)
        self.assertEqual(
            guest.get(f"/api/events/{self.event.id}/circle/").status_code,
            401,
        )


class FollowPrivacyConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def test_concurrent_public_transition_and_follow_leave_no_pending_ghost(self):
        target = User.objects.create_user(
            email="race-target@social.test",
            password="A-real-password-123!",
            username="race.target",
            display_name="Race Target",
            is_private=True,
        )
        follower = User.objects.create_user(
            email="race-follower@social.test",
            password="A-real-password-123!",
            username="race.follower",
            display_name="Race Follower",
            is_private=False,
        )
        barrier = threading.Barrier(2)
        errors = []

        def run_follow():
            close_old_connections()
            try:
                from users.services import follow_user

                barrier.wait()
                follow_user(follower_id=follower.id, followee_id=target.id)
            except Exception as exc:  # recorded and asserted in the main thread
                errors.append(exc)
            finally:
                close_old_connections()

        def run_transition():
            close_old_connections()
            try:
                from users.services import change_privacy

                barrier.wait()
                change_privacy(user_id=target.id, is_private=False)
            except Exception as exc:  # recorded and asserted in the main thread
                errors.append(exc)
            finally:
                close_old_connections()

        threads = [threading.Thread(target=run_follow), threading.Thread(target=run_transition)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)

        Follow = apps.get_model("users", "Follow")
        target.refresh_from_db()
        follow = Follow.objects.get(follower=follower, followee=target)
        self.assertEqual(errors, [])
        self.assertFalse(target.is_private)
        self.assertEqual(follow.status, "approved")
        self.assertIsNotNone(follow.approved_at)
