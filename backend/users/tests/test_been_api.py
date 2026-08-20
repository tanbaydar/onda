import json
from datetime import UTC, datetime
from unittest.mock import patch

from django.apps import apps
from django.db import IntegrityError, transaction
from django.test import Client, TestCase

from catalog.models import Artist, City, Event, EventArtist, EventStatus, Venue
from users.models import User


BOUNDARY_NOW = datetime(2026, 8, 14, 16, 0, tzinfo=UTC)


class BeenApiContractTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.get(name="Boston")
        cls.venue = Venue.objects.create(name="Been Test Venue", city=cls.city)
        cls.artist = Artist.objects.create(name="Been Test Artist")
        cls.started = cls.make_event(
            "Started",
            "2026-08-14",
            "12:00:00",
        )
        cls.just_future = cls.make_event(
            "Just Future",
            "2026-08-14",
            "12:01:00",
        )
        cls.date_only_today = cls.make_event("Date Only Today", "2026-08-14")
        cls.date_only_tomorrow = cls.make_event("Date Only Tomorrow", "2026-08-15")
        cls.old = cls.make_event("Old", "2026-07-01", "20:00:00")
        cls.newer = cls.make_event("Newer", "2026-08-01", "20:00:00")
        cls.hidden = cls.make_event(
            "Hidden",
            "2026-07-15",
            "20:00:00",
            status=EventStatus.HIDDEN,
        )
        cls.ambiguous = cls.make_event(
            "Fall Back",
            "2026-11-01",
            "01:30:00",
        )
        cls.nonexistent = cls.make_event(
            "Spring Forward",
            "2026-03-08",
            "02:30:00",
        )
        cls.owner = cls.make_user(
            "owner@example.com",
            "owner",
            is_private=True,
        )
        cls.other = cls.make_user("other@example.com", "other")
        cls.third = cls.make_user("third@example.com", "third")

    @classmethod
    def make_event(cls, title, event_date, start_time=None, status=EventStatus.ACTIVE):
        event = Event.objects.create(
            title=title,
            event_date=event_date,
            start_time=start_time,
            venue=cls.venue,
            status=status,
        )
        EventArtist.objects.create(event=event, artist=cls.artist, position=1)
        return event

    @classmethod
    def make_user(cls, email, username, is_private=False):
        return User.objects.create_user(
            email=email,
            password="A-real-password-123!",
            username=username,
            display_name=username.title(),
            is_private=is_private,
        )

    def auth_client(self, user):
        client = Client(enforce_csrf_checks=True)
        client.force_login(user)
        client.get("/api/auth/session/")
        return client

    def guest_client(self, *, bootstrap=True):
        client = Client(enforce_csrf_checks=True)
        if bootstrap:
            client.get("/api/auth/session/")
        return client

    def request(self, client, method, path, payload=None, *, now=BOUNDARY_NOW):
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

    def put_rating(self, client, event, rating=4.0, *, now=BOUNDARY_NOW):
        return self.request(
            client,
            "put",
            f"/api/events/{event.id}/been/",
            {"rating": rating},
            now=now,
        )

    def test_rating_rejects_every_out_of_contract_value(self):
        client = self.auth_client(self.owner)
        for value in (0, -0.5, 5.5, 3.7, "4.5", True):
            with self.subTest(value=value):
                response = self.put_rating(client, self.started, value)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(
                    list(response.json()["errors"]),
                    ["rating"],
                )

    def test_creation_requires_rating_but_rating_removal_succeeds(self):
        client = self.auth_client(self.owner)
        missing = self.request(
            client,
            "put",
            f"/api/events/{self.started.id}/been/",
            {},
        )
        created = self.put_rating(client, self.started, 4.5)
        removed = self.request(
            client,
            "delete",
            f"/api/events/{self.started.id}/been/rating/",
        )

        self.assertEqual(missing.status_code, 400)
        self.assertIn("rating", missing.json()["errors"])
        self.assertEqual(created.status_code, 201)
        self.assertEqual(removed.status_code, 200)
        self.assertIsNone(removed.json()["entry"]["rating"])
        self.assertIsNone(removed.json()["entry"]["rated_at"])

    def test_one_entry_per_user_event_and_edit_preserves_rated_at(self):
        client = self.auth_client(self.owner)
        created = self.put_rating(client, self.started, 3.0)
        edited = self.put_rating(
            client,
            self.started,
            4.5,
            now=datetime(2026, 8, 15, 16, 0, tzinfo=UTC),
        )
        DiaryEntry = apps.get_model("users", "DiaryEntry")

        self.assertEqual(created.status_code, 201)
        self.assertEqual(edited.status_code, 200)
        self.assertEqual(DiaryEntry.objects.count(), 1)
        self.assertEqual(
            edited.json()["entry"]["rated_at"],
            created.json()["entry"]["rated_at"],
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            DiaryEntry.objects.create(
                user=self.owner,
                event=self.started,
                rating="4.0",
                rated_at=BOUNDARY_NOW,
            )

    def test_start_time_gate_rejects_before_and_accepts_at_boundary(self):
        client = self.auth_client(self.owner)
        before = self.put_rating(
            client,
            self.started,
            now=datetime(2026, 8, 14, 15, 59, 59, tzinfo=UTC),
        )
        at_boundary = self.put_rating(client, self.started, now=BOUNDARY_NOW)
        future = self.put_rating(client, self.just_future, now=BOUNDARY_NOW)

        self.assertEqual(before.status_code, 409)
        self.assertEqual(at_boundary.status_code, 201)
        self.assertEqual(future.status_code, 409)
        self.assertIn("scheduled start", future.json()["errors"]["event"][0])

    def test_null_start_time_opens_at_venue_local_midnight(self):
        client = self.auth_client(self.owner)
        before_midnight = datetime(2026, 8, 14, 3, 59, 59, tzinfo=UTC)
        midnight = datetime(2026, 8, 14, 4, 0, tzinfo=UTC)

        before = self.put_rating(
            client,
            self.date_only_today,
            now=before_midnight,
        )
        at_boundary = self.put_rating(
            client,
            self.date_only_today,
            now=midnight,
        )
        tomorrow = self.put_rating(client, self.date_only_tomorrow, now=BOUNDARY_NOW)

        self.assertEqual(before.status_code, 409)
        self.assertEqual(at_boundary.status_code, 201)
        self.assertEqual(tomorrow.status_code, 409)

    def test_dst_wall_clock_rules_use_first_fall_occurrence_and_spring_jump(self):
        client = self.auth_client(self.owner)
        before_fall = self.put_rating(
            client,
            self.ambiguous,
            now=datetime(2026, 11, 1, 5, 29, 59, tzinfo=UTC),
        )
        first_fall_occurrence = self.put_rating(
            client,
            self.ambiguous,
            now=datetime(2026, 11, 1, 5, 30, tzinfo=UTC),
        )
        before_spring_jump = self.put_rating(
            client,
            self.nonexistent,
            now=datetime(2026, 3, 8, 6, 59, 59, tzinfo=UTC),
        )
        after_spring_jump = self.put_rating(
            client,
            self.nonexistent,
            now=datetime(2026, 3, 8, 7, 0, tzinfo=UTC),
        )

        self.assertEqual(before_fall.status_code, 409)
        self.assertEqual(first_fall_occurrence.status_code, 201)
        self.assertEqual(before_spring_jump.status_code, 409)
        self.assertEqual(after_spring_jump.status_code, 201)

    def test_remove_then_rerate_sets_a_new_rated_at(self):
        client = self.auth_client(self.owner)
        created = self.put_rating(client, self.started, 3.0)
        self.request(
            client,
            "delete",
            f"/api/events/{self.started.id}/been/rating/",
        )
        rerated = self.put_rating(
            client,
            self.started,
            4.0,
            now=datetime(2026, 8, 15, 16, 0, tzinfo=UTC),
        )

        self.assertEqual(rerated.status_code, 200)
        self.assertNotEqual(
            rerated.json()["entry"]["rated_at"],
            created.json()["entry"]["rated_at"],
        )

    def test_aggregate_threshold_is_explicit_at_two_and_available_at_three(self):
        self.put_rating(self.auth_client(self.owner), self.started, 3.0)
        self.put_rating(self.auth_client(self.other), self.started, 4.0)

        at_two = self.client.get(f"/api/events/{self.started.id}/")
        self.put_rating(self.auth_client(self.third), self.started, 5.0)
        at_three = self.client.get(f"/api/events/{self.started.id}/")

        self.assertEqual(
            at_two.json()["rating_summary"],
            {"state": "not_enough_ratings", "count": 2},
        )
        self.assertEqual(
            at_three.json()["rating_summary"],
            {"state": "available", "count": 3, "average": 4.0},
        )

    def test_unrated_entries_are_excluded_and_edit_changes_average(self):
        owner_client = self.auth_client(self.owner)
        self.put_rating(owner_client, self.started, 1.0)
        self.put_rating(self.auth_client(self.other), self.started, 3.0)
        self.put_rating(self.auth_client(self.third), self.started, 5.0)
        self.request(
            owner_client,
            "delete",
            f"/api/events/{self.started.id}/been/rating/",
        )

        after_removal = self.client.get(f"/api/events/{self.started.id}/")
        self.put_rating(owner_client, self.started, 4.0)
        after_rerate = self.client.get(f"/api/events/{self.started.id}/")
        self.put_rating(owner_client, self.started, 2.0)
        after_edit = self.client.get(f"/api/events/{self.started.id}/")

        self.assertEqual(
            after_removal.json()["rating_summary"],
            {"state": "not_enough_ratings", "count": 2},
        )
        self.assertEqual(after_rerate.json()["rating_summary"]["average"], 4.0)
        self.assertAlmostEqual(
            after_edit.json()["rating_summary"]["average"],
            10 / 3,
            places=5,
        )

    def test_entry_deletion_removes_contribution_and_allows_fresh_readd(self):
        client = self.auth_client(self.owner)
        created = self.put_rating(client, self.started, 4.0)
        self.put_rating(self.auth_client(self.other), self.started, 4.0)
        self.put_rating(self.auth_client(self.third), self.started, 4.0)

        deleted = self.request(
            client,
            "delete",
            f"/api/events/{self.started.id}/been/",
        )
        summary = self.client.get(f"/api/events/{self.started.id}/")
        readded = self.put_rating(
            client,
            self.started,
            5.0,
            now=datetime(2026, 8, 15, 16, 0, tzinfo=UTC),
        )
        repeated_delete = self.request(
            self.auth_client(self.make_user("fourth@example.com", "fourth")),
            "delete",
            f"/api/events/{self.started.id}/been/",
        )

        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(summary.json()["rating_summary"]["count"], 2)
        self.assertEqual(readded.status_code, 201)
        self.assertNotEqual(
            readded.json()["entry"]["created_at"],
            created.json()["entry"]["created_at"],
        )
        self.assertEqual(repeated_delete.status_code, 404)

    def test_guest_write_statuses_respect_csrf_before_auth(self):
        bootstrapped = self.guest_client()
        writes = (
            ("put", f"/api/events/{self.started.id}/been/", {"rating": 4.0}),
            ("delete", f"/api/events/{self.started.id}/been/rating/", None),
            ("delete", f"/api/events/{self.started.id}/been/", None),
        )
        for method, path, payload in writes:
            with self.subTest(method=method, path=path):
                response = self.request(bootstrapped, method, path, payload)
                self.assertEqual(response.status_code, 401)

        unbootstrapped = self.guest_client(bootstrap=False)
        response = self.request(
            unbootstrapped,
            "put",
            f"/api/events/{self.started.id}/been/",
            {"rating": 4.0},
        )
        self.assertEqual(response.status_code, 403)

    def test_guest_cannot_list_a_diary(self):
        response = self.guest_client().get("/api/me/been/")

        self.assertEqual(response.status_code, 401)

    def test_owner_only_diary_and_private_rating_stays_anonymous(self):
        self.put_rating(self.auth_client(self.owner), self.started, 4.5)
        owner_diary = self.auth_client(self.owner).get("/api/me/been/")
        other_diary = self.auth_client(self.other).get("/api/me/been/")
        DiaryEntry = apps.get_model("users", "DiaryEntry")

        self.assertEqual(
            [item["event"]["id"] for item in owner_diary.json()["results"]],
            [self.started.id],
        )
        self.assertEqual(other_diary.json()["results"], [])
        self.assertEqual(
            list(DiaryEntry.objects.visible_to(self.other)),
            [],
        )
        self.assertEqual(
            DiaryEntry.objects.for_aggregation().get().user,
            self.owner,
        )

    def test_retroactive_entry_appears_at_historical_position(self):
        client = self.auth_client(self.owner)
        self.put_rating(client, self.newer, 4.0)
        self.put_rating(
            client,
            self.old,
            5.0,
            now=datetime(2026, 8, 20, 16, 0, tzinfo=UTC),
        )

        response = client.get("/api/me/been/")

        self.assertEqual(
            [item["event"]["id"] for item in response.json()["results"]],
            [self.newer.id, self.old.id],
        )

    def test_hidden_entries_are_suppressed_from_both_paths_then_resurrect(self):
        DiaryEntry = apps.get_model("users", "DiaryEntry")
        entry = DiaryEntry.objects.create(
            user=self.owner,
            event=self.hidden,
            rating="4.0",
            rated_at=BOUNDARY_NOW,
        )

        self.assertFalse(DiaryEntry.objects.visible_to(self.owner).exists())
        self.assertFalse(DiaryEntry.objects.for_aggregation().exists())

        self.hidden.status = EventStatus.ACTIVE
        self.hidden.save(update_fields=("status",))

        self.assertEqual(DiaryEntry.objects.visible_to(self.owner).get(), entry)
        self.assertEqual(DiaryEntry.objects.for_aggregation().get(), entry)

    def test_database_rejects_rating_timestamp_mismatches_and_invalid_values(self):
        DiaryEntry = apps.get_model("users", "DiaryEntry")
        invalid_rows = (
            {"rating": "4.0", "rated_at": None},
            {"rating": None, "rated_at": BOUNDARY_NOW},
            {"rating": "3.7", "rated_at": BOUNDARY_NOW},
        )
        for index, values in enumerate(invalid_rows):
            with self.subTest(values=values), self.assertRaises(IntegrityError):
                with transaction.atomic():
                    DiaryEntry.objects.create(
                        user=self.owner,
                        event=(self.old, self.newer, self.started)[index],
                        **values,
                    )

    def test_event_detail_reports_creation_loggability_at_boundary(self):
        before = datetime(2026, 8, 14, 15, 59, 59, tzinfo=UTC)
        with patch("users.services.timezone_now", return_value=before):
            before_response = self.client.get(f"/api/events/{self.started.id}/")
        with patch("users.services.timezone_now", return_value=BOUNDARY_NOW):
            at_response = self.client.get(f"/api/events/{self.started.id}/")

        self.assertEqual(
            before_response.json()["been"],
            {
                "loggable": False,
                "unavailable_reason": (
                    "This event can be added to Been once its scheduled start arrives."
                ),
            },
        )
        self.assertEqual(
            at_response.json()["been"],
            {"loggable": True, "unavailable_reason": None},
        )

    def test_event_detail_includes_viewer_entry_only_for_signed_in_viewer(self):
        client = self.auth_client(self.owner)
        self.put_rating(client, self.started, 4.0)

        owner_detail = client.get(f"/api/events/{self.started.id}/")
        no_entry_detail = self.auth_client(self.other).get(
            f"/api/events/{self.started.id}/"
        )
        guest_detail = self.client.get(f"/api/events/{self.started.id}/")

        self.assertEqual(owner_detail.json()["viewer_entry"]["rating"], 4.0)
        self.assertIsNone(no_entry_detail.json()["viewer_entry"])
        self.assertNotIn("viewer_entry", guest_detail.json())
