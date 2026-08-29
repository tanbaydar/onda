from datetime import UTC, datetime

from django.test import Client, TestCase

from catalog.models import City, Event, EventStatus, Venue
from users.models import DiaryEntry, User


NOW = datetime(2026, 8, 1, 12, 0, tzinfo=UTC)


class EventRatingDistributionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(
            name="Distribution City",
            region_code="MA",
            country_code="US",
            timezone="America/New_York",
        )
        cls.venue = Venue.objects.create(name="Distribution Venue", city=cls.city)
        cls.event = Event.objects.create(
            title="Distribution Event",
            event_date="2026-07-01",
            venue=cls.venue,
            status=EventStatus.ACTIVE,
        )

    @classmethod
    def user(cls, suffix, *, private=False):
        return User.objects.create_user(
            email=f"distribution.{suffix}@test.example",
            password="A-real-password-123!",
            username=f"distribution.{suffix}",
            display_name=f"Distribution {suffix}",
            is_private=private,
        )

    def detail_distribution(self):
        response = Client().get(f"/api/events/{self.event.id}/")
        self.assertEqual(response.status_code, 200)
        return response.json()["rating_distribution"]

    def rate(self, suffix, rating, *, private=False):
        return DiaryEntry.objects.create(
            user=self.user(suffix, private=private),
            event=self.event,
            rating=rating,
            rated_at=NOW,
        )

    def test_empty_event_has_explicit_not_enough_distribution(self):
        self.assertEqual(
            self.detail_distribution(),
            {"state": "not_enough_ratings"},
        )

    def test_single_private_rating_is_available_anonymously(self):
        self.rate("single-private", "1.0", private=True)

        distribution = self.detail_distribution()

        self.assertEqual(distribution["state"], "available")
        self.assertEqual(
            sum(bucket["count"] for bucket in distribution["buckets"]),
            1,
        )

    def test_two_ratings_are_available(self):
        self.rate("two-a", "1.0")
        self.rate("two-private", "4.0", private=True)

        distribution = self.detail_distribution()

        self.assertEqual(distribution["state"], "available")
        self.assertEqual(
            sum(bucket["count"] for bucket in distribution["buckets"]),
            2,
        )

    def test_three_mixed_public_private_ratings_render(self):
        self.rate("thr-a", "1.0")
        self.rate("thr-private", "4.0", private=True)
        self.rate("thr-b", "5.0")

        distribution = self.detail_distribution()

        self.assertEqual(distribution["state"], "available")
        self.assertEqual(len(distribution["buckets"]), 10)
        self.assertEqual(sum(bucket["count"] for bucket in distribution["buckets"]), 3)
        self.assertEqual(
            [bucket["rating"] for bucket in distribution["buckets"]],
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
        )
        self.assertEqual(
            next(
                bucket["relative_value"]
                for bucket in distribution["buckets"]
                if bucket["rating"] == 4.0
            ),
            1.0,
        )

    def test_half_star_values_land_in_exact_normalized_buckets(self):
        self.rate("half-a", "0.5")
        self.rate("half-b", "0.5")
        self.rate("one", "1.0")
        self.rate("five", "5.0")

        buckets = {
            bucket["rating"]: bucket["relative_value"]
            for bucket in self.detail_distribution()["buckets"]
        }

        self.assertEqual(buckets[0.5], 1.0)
        self.assertEqual(buckets[1.0], 0.5)
        self.assertEqual(buckets[5.0], 0.5)
        self.assertEqual(buckets[1.5], 0.0)

    def test_private_rating_contributes_above_threshold_while_unrated_entry_does_not(self):
        self.rate("private", "4.0", private=True)
        self.rate("public-a", "3.0")
        self.rate("public-b", "5.0")
        DiaryEntry.objects.create(
            user=self.user("unrated"),
            event=self.event,
        )

        distribution = self.detail_distribution()

        self.assertEqual(
            next(
                bucket["relative_value"]
                for bucket in distribution["buckets"]
                if bucket["rating"] == 4.0
            ),
            1.0,
        )
        self.assertEqual(
            sum(bucket["relative_value"] for bucket in distribution["buckets"]),
            3.0,
        )

    def test_event_and_profile_distributions_have_identical_available_shape(self):
        owner = self.user("parity")
        for index in range(3):
            event = self.event
            if index:
                event = Event.objects.create(
                    title=f"Parity Event {index}",
                    event_date="2026-07-01",
                    venue=self.venue,
                    status=EventStatus.ACTIVE,
                )
            DiaryEntry.objects.create(
                user=owner,
                event=event,
                rating="3.5",
                rated_at=NOW,
            )
        self.rate("parity-other-a", "3.5")
        self.rate("parity-other-b", "3.5")

        event_distribution = self.detail_distribution()
        profile_distribution = Client().get(
            f"/api/users/{owner.username}/stats/"
        ).json()["rating_distribution"]

        self.assertEqual(event_distribution, profile_distribution)
