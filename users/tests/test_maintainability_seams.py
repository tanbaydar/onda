import json
from datetime import UTC, datetime

from django.test import Client, TestCase, override_settings

from catalog.models import Artist, City, Event, EventArtist, EventStatus, Venue
from users.models import DiaryEntry, Follow, FollowStatus, Review, User


NOW = datetime(2026, 8, 20, 16, 0, tzinfo=UTC)


class BrowserEquivalentCsrfContractTests(TestCase):
    registration = {
        "email": "trusted-origin@example.com",
        "password": "A-real-password-123!",
        "username": "trusted.origin",
        "display_name": "Trusted Origin",
        "is_private": False,
    }

    def register_from(self, origin, payload):
        client = Client(enforce_csrf_checks=True)
        bootstrap = client.get("/api/auth/session/")
        token = client.cookies["csrftoken"].value
        response = client.post(
            "/api/auth/register/",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
            HTTP_ORIGIN=origin,
        )
        return bootstrap, response

    @override_settings(
        CSRF_TRUSTED_ORIGINS=[
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ]
    )
    def test_browser_origin_is_accepted_only_when_trusted(self):
        bootstrap, trusted = self.register_from(
            "http://127.0.0.1:5173", self.registration
        )
        _untrusted_bootstrap, untrusted = self.register_from(
            "http://untrusted.example",
            {
                **self.registration,
                "email": "untrusted-origin@example.com",
                "username": "untrusted.origin",
            },
        )

        self.assertEqual(bootstrap.status_code, 200)
        self.assertEqual(trusted.status_code, 201)
        self.assertEqual(untrusted.status_code, 403)


class CircleQueryCountContractTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        city = City.objects.get(name="Boston")
        venue = Venue.objects.create(name="Circle Query Venue", city=city)
        artist = Artist.objects.create(name="Circle Query Artist")
        cls.event = Event.objects.create(
            title="Circle Query Event",
            event_date="2026-07-01",
            start_time="20:00:00",
            venue=venue,
            status=EventStatus.ACTIVE,
        )
        EventArtist.objects.create(event=cls.event, artist=artist, position=1)
        cls.viewer = cls.make_user("circle.viewer@example.com", "circle.viewer")
        cls.followees = [
            cls.make_user(
                f"circle.followee.{index}@example.com", f"circle.followee.{index}"
            )
            for index in range(1, 4)
        ]
        for index, followee in enumerate(cls.followees):
            entry = DiaryEntry.objects.create(
                user=followee,
                event=cls.event,
                rating=str(4 - index / 2),
                rated_at=NOW,
            )
            if index < 2:
                Review.objects.create(
                    entry=entry,
                    body=f"Reviewed Circle entry {index}",
                    published_at=NOW,
                )
            Follow.objects.create(
                follower=cls.viewer,
                followee=followee,
                status=FollowStatus.APPROVED,
                created_at=NOW,
                approved_at=NOW,
            )

    @classmethod
    def make_user(cls, email, username):
        return User.objects.create_user(
            email=email,
            password="A-real-password-123!",
            username=username,
            display_name=username,
            is_private=False,
        )

    def test_circle_mixed_page_query_count_is_pinned_as_a_refactor_ceiling(self):
        client = Client()
        client.force_login(self.viewer)

        # Eleven includes seven fixed queries plus two queries for each of the
        # two reviewed rows. It is a ceiling to reduce, never to increase.
        with self.assertNumQueries(11):
            response = client.get(f"/api/events/{self.event.id}/circle/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 3)
