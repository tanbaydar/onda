from django.core.management.base import BaseCommand
from django.db.models import Count, Q

from catalog.models import City
from ingestion.artwork import backfill_event_artwork


class Command(BaseCommand):
    help = "Backfill event artwork from retained raw RA listing payloads."

    def handle(self, *args, **options):
        result = backfill_event_artwork()
        self.stdout.write(
            f"Artwork backfill: {result['observed']} observed, "
            f"{result['matched']} matched, {result['changed']} changed."
        )
        cities = City.objects.annotate(
            total=Count("venues__events"),
            covered=Count(
                "venues__events",
                filter=Q(venues__events__cover_image_url__isnull=False),
            ),
        ).order_by("name")
        for city in cities:
            percentage = 100 * city.covered / city.total if city.total else 0
            self.stdout.write(
                f"{city.name}: {city.covered}/{city.total} "
                f"({percentage:.1f}%)"
            )
