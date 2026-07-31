import json
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from django.apps import apps
from django.db import IntegrityError, connection, transaction
from django.db.models.deletion import RestrictedError
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext

from catalog.models import Artist, City, Event, EventArtist, EventStatus, Venue
from users.models import DiaryEntry, Follow, FollowStatus, User


EVENT_DAY = datetime(2026, 8, 20, 16, 0, tzinfo=UTC)
BEFORE_BOSTON_EXPIRY = datetime(2026, 8, 21, 3, 59, tzinfo=UTC)
AT_BOSTON_EXPIRY = datetime(2026, 8, 21, 4, 0, tzinfo=UTC)


class WillBeThereApiContractTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        boston = City.objects.get(name="Boston")
        cls.tokyo = City.objects.create(
            name="Tokyo Test",
            region_code="13",
            region_name="Tokyo",
            country_code="JP",
            timezone="Asia/Tokyo",
        )
        boston_venue = Venue.objects.create(name="WBT Boston Venue", city=boston)
        tokyo_venue = Venue.objects.create(name="WBT Tokyo Venue", city=cls.tokyo)
        artist = Artist.objects.create(name="WBT Artist")
        cls.event = cls.make_event("WBT Boston Event", boston_venue, artist)
        cls.other_event = cls.make_event("WBT Other Event", boston_venue, artist)
        cls.tokyo_event = cls.make_event("WBT Tokyo Event", tokyo_venue, artist)
        cls.hidden_event = cls.make_event(
            "WBT Hidden Event", boston_venue, artist, status=EventStatus.HIDDEN
        )
        cls.viewer = cls.user("wbt.viewer")
        cls.public_user = cls.user("wbt.public")
        cls.private_user = cls.user("wbt.private", is_private=True)
        cls.other = cls.user("wbt.other")

    @classmethod
    def make_event(cls, title, venue, artist, status=EventStatus.ACTIVE):
        event = Event.objects.create(
            title=title,
            event_date="2026-08-20",
            start_time="10:00:00",
            venue=venue,
            status=status,
        )
        EventArtist.objects.create(event=event, artist=artist, position=1)
        return event

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
        client = Client(enforce_csrf_checks=True)
        if user is not None:
            client.force_login(user)
        client.get("/api/auth/session/")
        return client

    def request(self, client, method, path, *, now=EVENT_DAY):
        token = client.cookies.get("csrftoken")
        headers = {"HTTP_X_CSRFTOKEN": token.value} if token else {}
        with (
            patch("users.views.timezone_now", return_value=now),
            patch("users.services.timezone_now", return_value=now),
        ):
            return getattr(client, method)(
                path,
                data=json.dumps({}),
                content_type="application/json",
                **headers,
            )

    def get(self, client, path, *, now=EVENT_DAY, data=None):
        with (
            patch("users.views.timezone_now", return_value=now),
            patch("users.services.timezone_now", return_value=now),
        ):
            return client.get(path, data or {})

    def mark(self, user, event=None, *, now=EVENT_DAY):
        return self.request(
            self.client_for(user),
            "put",
            f"/api/events/{(event or self.event).id}/will-be-there/",
            now=now,
        )

    def follow(self, follower, followee):
        return Follow.objects.create(
            follower=follower,
            followee=followee,
            status=FollowStatus.APPROVED,
            created_at=EVENT_DAY,
            approved_at=EVENT_DAY,
        )

    def test_mark_after_start_repeat_and_expiry_boundary(self):
        first = self.mark(self.viewer, now=EVENT_DAY)
        repeated = self.mark(self.viewer, now=BEFORE_BOSTON_EXPIRY)
        expired = self.mark(self.other, now=AT_BOSTON_EXPIRY)
        self.assertEqual(first.status_code, 201)
        self.assertEqual(repeated.status_code, 200)
        self.assertEqual(
            first.json()["will_be_there"]["created_at"],
            repeated.json()["will_be_there"]["created_at"],
        )
        self.assertEqual(expired.status_code, 409)
        self.assertIn("will_be_there", expired.json()["errors"])

    def test_event_detail_viewer_state_and_guest_omission(self):
        self.mark(self.viewer)
        marked = self.get(self.client_for(self.viewer), f"/api/events/{self.event.id}/")
        guest = self.get(self.client_for(), f"/api/events/{self.event.id}/")
        expired = self.get(
            self.client_for(self.viewer),
            f"/api/events/{self.event.id}/",
            now=AT_BOSTON_EXPIRY,
        )
        self.assertTrue(marked.json()["viewer_will_be_there"]["is_marked"])
        self.assertNotIn("viewer_will_be_there", guest.json())
        self.assertFalse(expired.json()["viewer_will_be_there"]["is_marked"])
        self.assertFalse(expired.json()["viewer_will_be_there"]["can_mark"])

    def test_tokyo_expiry_uses_venue_date_not_server_date(self):
        before_tokyo_midnight = datetime(2026, 8, 20, 14, 59, tzinfo=UTC)
        at_tokyo_midnight = datetime(2026, 8, 20, 15, 0, tzinfo=UTC)
        before = self.mark(
            self.public_user, self.tokyo_event, now=before_tokyo_midnight
        )
        expired = self.mark(
            self.other, self.tokyo_event, now=at_tokyo_midnight
        )
        self.assertEqual(before.status_code, 201)
        self.assertEqual(expired.status_code, 409)

    def test_public_and_circle_lists_apply_privacy_order_and_expiry(self):
        self.follow(self.viewer, self.private_user)
        self.mark(self.public_user, now=EVENT_DAY - timedelta(minutes=1))
        self.mark(self.private_user, now=EVENT_DAY)
        public = self.get(self.client_for(), f"/api/events/{self.event.id}/will-be-there/public/")
        circle = self.get(self.client_for(self.viewer), f"/api/events/{self.event.id}/will-be-there/circle/")
        expired_public = self.get(
            self.client_for(),
            f"/api/events/{self.event.id}/will-be-there/public/",
            now=AT_BOSTON_EXPIRY,
        )
        self.assertEqual([row["user"]["id"] for row in public.json()["results"]], [self.public_user.id])
        self.assertEqual(
            [row["user"]["id"] for row in circle.json()["results"]],
            [self.private_user.id],
        )
        self.assertEqual(expired_public.json()["results"], [])
        self.assertEqual(expired_public.json()["pagination"]["total_results"], 0)

    def test_circle_excludes_self_and_guest_requires_authentication(self):
        self.mark(self.viewer)
        own_circle = self.get(self.client_for(self.viewer), f"/api/events/{self.event.id}/will-be-there/circle/")
        guest_circle = self.get(self.client_for(), f"/api/events/{self.event.id}/will-be-there/circle/")
        self.assertEqual(own_circle.json()["results"], [])
        self.assertEqual(guest_circle.status_code, 401)

    def test_unmark_is_idempotent_and_removes_feed_item(self):
        self.follow(self.viewer, self.public_user)
        self.mark(self.public_user)
        before = self.get(self.client_for(self.viewer), "/api/me/home/").json()
        first = self.request(
            self.client_for(self.public_user),
            "delete",
            f"/api/events/{self.event.id}/will-be-there/",
        )
        second = self.request(
            self.client_for(self.public_user),
            "delete",
            f"/api/events/{self.event.id}/will-be-there/",
        )
        after = self.get(self.client_for(self.viewer), "/api/me/home/").json()
        self.assertEqual([item["type"] for item in before["results"]], ["will_be_there"])
        self.assertEqual(first.status_code, 204)
        self.assertEqual(second.status_code, 204)
        self.assertEqual(after["results"], [])

    def test_wbt_and_been_coexist_as_two_feed_items(self):
        self.follow(self.viewer, self.public_user)
        self.mark(self.public_user)
        DiaryEntry.objects.create(
            user=self.public_user,
            event=self.event,
            rating="4.5",
            rated_at=EVENT_DAY + timedelta(minutes=1),
        )
        results = self.get(self.client_for(self.viewer), "/api/me/home/").json()["results"]
        self.assertCountEqual([item["type"] for item in results], ["rated_been", "will_be_there"])

    def test_private_wbt_is_visible_to_follower_feed_only_until_unfollow(self):
        relationship = self.follow(self.viewer, self.private_user)
        self.mark(self.private_user)
        visible = self.get(self.client_for(self.viewer), "/api/me/home/").json()
        relationship.delete()
        gone = self.get(self.client_for(self.viewer), "/api/me/home/").json()
        self.assertEqual([item["type"] for item in visible["results"]], ["will_be_there"])
        self.assertEqual(gone["results"], [])

    def test_expired_feed_item_is_dormant_and_postponement_restores_it(self):
        self.follow(self.viewer, self.public_user)
        self.mark(self.public_user)
        expired = self.get(
            self.client_for(self.viewer), "/api/me/home/", now=AT_BOSTON_EXPIRY
        ).json()
        self.event.event_date = "2026-08-22"
        self.event.save(update_fields=("event_date",))
        restored = self.get(
            self.client_for(self.viewer), "/api/me/home/", now=AT_BOSTON_EXPIRY
        ).json()
        self.assertEqual(expired["results"], [])
        self.assertEqual(restored["results"][0]["type"], "will_be_there")

    def test_hidden_event_suppresses_without_deleting_and_resurrection_restores(self):
        self.follow(self.viewer, self.public_user)
        self.hidden_event.status = EventStatus.ACTIVE
        self.hidden_event.save(update_fields=("status",))
        self.mark(self.public_user, self.hidden_event)
        self.hidden_event.status = EventStatus.HIDDEN
        self.hidden_event.save(update_fields=("status",))
        hidden = self.get(self.client_for(), f"/api/events/{self.hidden_event.id}/will-be-there/public/")
        hidden_feed = self.get(self.client_for(self.viewer), "/api/me/home/").json()
        self.hidden_event.status = EventStatus.ACTIVE
        self.hidden_event.save(update_fields=("status",))
        restored = self.get(self.client_for(), f"/api/events/{self.hidden_event.id}/will-be-there/public/")
        restored_feed = self.get(self.client_for(self.viewer), "/api/me/home/").json()
        WillBeThere = apps.get_model("users", "WillBeThere")
        self.assertEqual(hidden.status_code, 404)
        self.assertEqual(hidden_feed["results"], [])
        self.assertTrue(WillBeThere.objects.filter(user=self.public_user, event=self.hidden_event).exists())
        self.assertEqual(restored.json()["results"][0]["user"]["id"], self.public_user.id)
        self.assertEqual(restored_feed["results"][0]["type"], "will_be_there")

    def test_home_query_count_is_constant_across_multiple_cities(self):
        self.follow(self.viewer, self.public_user)
        self.tokyo_event.event_date = "2026-08-21"
        self.tokyo_event.save(update_fields=("event_date",))
        self.mark(self.public_user, self.event)
        self.mark(self.public_user, self.tokyo_event)
        client = self.client_for(self.viewer)
        with (
            patch("users.views.timezone_now", return_value=EVENT_DAY),
            CaptureQueriesContext(connection) as queries,
        ):
            response = client.get("/api/me/home/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(queries), 4)
        self.assertEqual(sum("UNION ALL" in row["sql"] for row in queries), 1)
        self.assertEqual(len(response.json()["results"]), 2)

    def test_guest_writes_are_unauthorized_and_database_keys_enforce_contract(self):
        guest = self.request(
            self.client_for(), "put", f"/api/events/{self.event.id}/will-be-there/"
        )
        self.assertEqual(guest.status_code, 401)
        self.mark(self.viewer)
        WillBeThere = apps.get_model("users", "WillBeThere")
        with self.assertRaises(IntegrityError), transaction.atomic():
            WillBeThere.objects.create(user=self.viewer, event=self.event)

    def test_user_delete_cascades_and_event_delete_is_restricted(self):
        disposable = self.user("wbt.disposable")
        self.mark(disposable)
        disposable.delete()
        WillBeThere = apps.get_model("users", "WillBeThere")
        self.assertFalse(WillBeThere.objects.filter(event=self.event).exists())
        self.mark(self.public_user)
        with self.assertRaises(RestrictedError):
            self.event.delete()
