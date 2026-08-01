import json
from datetime import UTC, datetime
from unittest.mock import patch

from django.test import Client, TestCase, override_settings

from catalog.models import Artist, City, Event, EventArtist, EventStatus, Venue
from users.models import (
    DiaryEntry,
    FavoriteArtist,
    FavoriteEvent,
    FavoriteVenue,
    Follow,
    FollowStatus,
    Notification,
    Review,
    ReviewLike,
    User,
    WillBeThere,
)


NOW = datetime(2026, 8, 20, 16, 0, tzinfo=UTC)
VERIFICATION_ERROR = {
    "errors": {
        "verification": ["Email verification is required for account actions."]
    }
}


class VerificationGateSweepTests(TestCase):
    """New social write routes must be added to the canonical cases below."""

    def setUp(self):
        city = City.objects.get(name="Boston")
        self.venue = Venue.objects.create(name="Gate Sweep Venue", city=city)
        self.other_venue = Venue.objects.create(
            name="Gate Sweep Other Venue", city=city
        )
        self.artist = Artist.objects.create(name="Gate Sweep Artist")
        self.other_artist = Artist.objects.create(name="Gate Sweep Other Artist")
        self.events = [
            self.make_event(f"Gate Sweep Past {index}", f"2026-07-{index:02d}")
            for index in range(1, 13)
        ]
        self.upcoming_events = [
            self.make_event(
                f"Gate Sweep Upcoming {index}",
                f"2026-08-{index:02d}",
            )
            for index in (21, 22)
        ]
        self.user = self.make_user("gate.sweep@example.com", "gate.sweep", True)
        self.public_targets = [
            self.make_user(
                f"gate.public.{index}@example.com", f"gate.public.{index}"
            )
            for index in range(1, 4)
        ]
        self.private_targets = [
            self.make_user(
                f"gate.private.{index}@example.com",
                f"gate.private.{index}",
                True,
            )
            for index in range(1, 3)
        ]
        self.incoming = [
            self.make_user(
                f"gate.incoming.{index}@example.com", f"gate.incoming.{index}"
            )
            for index in range(1, 3)
        ]
        self.client = Client()
        self.client.force_login(self.user)
        self._prepare_existing_state()

    def make_user(self, email, username, is_private=False):
        return User.objects.create_user(
            email=email,
            password="A-real-password-123!",
            username=username,
            display_name=username,
            is_private=is_private,
        )

    def make_event(self, title, event_date):
        event = Event.objects.create(
            title=title,
            event_date=event_date,
            start_time="20:00:00",
            venue=self.venue,
            status=EventStatus.ACTIVE,
        )
        EventArtist.objects.create(event=event, artist=self.artist, position=1)
        return event

    def _entry(self, event, rating="4.0"):
        return DiaryEntry.objects.create(
            user=self.user,
            event=event,
            rating=rating,
            rated_at=NOW,
        )

    def _prepare_existing_state(self):
        self._entry(self.events[1])
        self._entry(self.events[2])
        review_edit_entry = self._entry(self.events[3])
        Review.objects.create(
            entry=review_edit_entry,
            body="Existing review to edit",
            published_at=NOW,
        )
        review_delete_entry = self._entry(self.events[4])
        Review.objects.create(
            entry=review_delete_entry,
            body="Existing review to delete",
            published_at=NOW,
        )
        self._entry(self.events[5])
        self._entry(self.events[6])

        author = self.public_targets[0]
        like_entry = DiaryEntry.objects.create(
            user=author,
            event=self.events[7],
            rating="4.5",
            rated_at=NOW,
        )
        self.like_review = Review.objects.create(
            entry=like_entry,
            body="Review to like",
            published_at=NOW,
        )
        unlike_entry = DiaryEntry.objects.create(
            user=author,
            event=self.events[8],
            rating="4.0",
            rated_at=NOW,
        )
        self.unlike_review = Review.objects.create(
            entry=unlike_entry,
            body="Review to unlike",
            published_at=NOW,
        )
        ReviewLike.objects.create(user=self.user, review=self.unlike_review)

        Follow.objects.create(
            follower=self.user,
            followee=self.public_targets[1],
            status=FollowStatus.APPROVED,
            created_at=NOW,
            approved_at=NOW,
        )
        Follow.objects.create(
            follower=self.user,
            followee=self.private_targets[1],
            status=FollowStatus.PENDING,
            created_at=NOW,
            approved_at=None,
        )
        for requester in self.incoming:
            Follow.objects.create(
                follower=requester,
                followee=self.user,
                status=FollowStatus.PENDING,
                created_at=NOW,
                approved_at=None,
            )

        FavoriteEvent.objects.create(
            user=self.user, event=self.events[10], added_at=NOW
        )
        FavoriteArtist.objects.create(
            user=self.user, artist=self.other_artist, added_at=NOW
        )
        FavoriteVenue.objects.create(
            user=self.user, venue=self.other_venue, added_at=NOW
        )
        WillBeThere.objects.create(
            user=self.user, event=self.upcoming_events[1], created_at=NOW
        )
        self.notification = Notification.objects.create(
            recipient=self.user,
            actor=self.public_targets[0],
            type="follow",
            created_at=NOW,
        )
        Notification.objects.create(
            recipient=self.user,
            actor=self.public_targets[1],
            type="follow",
            created_at=NOW,
        )

    def canonical_social_write_cases(self):
        # This is the canonical verification-gate sweep. Every new social
        # mutation route must be represented here with its flag-off status.
        return (
            ("log Been", "put", f"/api/events/{self.events[0].id}/been/", {"rating": 4.0}, 201),
            ("edit rating", "put", f"/api/events/{self.events[1].id}/been/", {"rating": 4.5}, 200),
            ("remove rating", "delete", f"/api/events/{self.events[5].id}/been/rating/", None, 200),
            ("remove Been", "delete", f"/api/events/{self.events[6].id}/been/", None, 204),
            ("create review", "put", f"/api/events/{self.events[2].id}/been/review/", {"body": "New review"}, 201),
            ("edit review", "put", f"/api/events/{self.events[3].id}/been/review/", {"body": "Edited review"}, 200),
            ("delete review", "delete", f"/api/events/{self.events[4].id}/been/review/", None, 204),
            ("like review", "post", f"/api/reviews/{self.like_review.id}/like/", None, 201),
            ("unlike review", "delete", f"/api/reviews/{self.unlike_review.id}/like/", None, 204),
            ("follow", "post", f"/api/users/{self.public_targets[2].id}/follow/", None, 201),
            ("unfollow", "delete", f"/api/users/{self.public_targets[1].id}/follow/", None, 204),
            ("request follow", "post", f"/api/users/{self.private_targets[0].id}/follow/", None, 201),
            ("accept request", "post", f"/api/me/follow-requests/{self.incoming[0].id}/accept/", None, 200),
            ("decline request", "post", f"/api/me/follow-requests/{self.incoming[1].id}/decline/", None, 204),
            ("withdraw request", "delete", f"/api/users/{self.private_targets[1].id}/follow/", None, 204),
            ("mark notification read", "post", f"/api/me/notifications/{self.notification.id}/read/", None, 200),
            ("mark all notifications read", "post", "/api/me/notifications/read-all/", None, 200),
            ("favorite event", "put", f"/api/events/{self.events[9].id}/favorite/", None, 201),
            ("unfavorite event", "delete", f"/api/events/{self.events[10].id}/favorite/", None, 204),
            ("favorite artist", "put", f"/api/artists/{self.artist.id}/favorite/", None, 201),
            ("unfavorite artist", "delete", f"/api/artists/{self.other_artist.id}/favorite/", None, 204),
            ("favorite venue", "put", f"/api/venues/{self.venue.id}/favorite/", None, 201),
            ("unfavorite venue", "delete", f"/api/venues/{self.other_venue.id}/favorite/", None, 204),
            ("mark WBT", "put", f"/api/events/{self.upcoming_events[0].id}/will-be-there/", None, 201),
            ("unmark WBT", "delete", f"/api/events/{self.upcoming_events[1].id}/will-be-there/", None, 204),
            ("edit profile", "put", "/api/me/profile/", {"display_name": "Gate Sweep", "avatar": None, "bio": None, "home_city_id": None}, 200),
            ("change privacy", "put", "/api/me/privacy/", {"is_private": False}, 200),
        )

    def request(self, method, path, payload):
        with patch("users.services.timezone_now", return_value=NOW), patch(
            "users.views.timezone_now", return_value=NOW
        ):
            return getattr(self.client, method)(
                path,
                data=json.dumps(payload or {}),
                content_type="application/json",
            )

    @override_settings(EMAIL_VERIFICATION_ENFORCED=True)
    def test_flag_on_rejects_every_social_write_with_field_keyed_error(self):
        for name, method, path, payload, _off_status in self.canonical_social_write_cases():
            with self.subTest(action=name):
                response = self.request(method, path, payload)
                self.assertEqual(response.status_code, 403)
                self.assertEqual(response.json(), VERIFICATION_ERROR)

    @override_settings(EMAIL_VERIFICATION_ENFORCED=False)
    def test_flag_off_preserves_every_social_write_status(self):
        for name, method, path, payload, expected_status in self.canonical_social_write_cases():
            with self.subTest(action=name):
                response = self.request(method, path, payload)
                self.assertEqual(response.status_code, expected_status)
