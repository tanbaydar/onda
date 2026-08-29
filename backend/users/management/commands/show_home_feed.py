from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from users.home_feed import home_feed_rows
from users.models import Follow, FollowStatus, User


class Command(BaseCommand):
    help = (
        "Print the Home feed exactly as the API would return it for one viewer. "
        "Read-only: this command never writes."
    )

    def add_arguments(self, parser):
        parser.add_argument("viewer", help="username whose Home feed is inspected")
        parser.add_argument("--limit", type=int, default=20)

    def handle(self, *args, **options):
        try:
            viewer = User.objects.get(username=options["viewer"])
        except User.DoesNotExist:
            raise CommandError(f"no user with username {options['viewer']!r}")

        followees = sorted(
            Follow.objects.filter(
                follower=viewer, status=FollowStatus.APPROVED
            ).values_list("followee__username", flat=True)
        )
        self.stdout.write(f"viewer  : {viewer.username}")
        self.stdout.write(
            f"follows : {', '.join(followees) if followees else '(nobody — Home will be empty)'}"
        )
        self.stdout.write("")

        rows = home_feed_rows(viewer, at=timezone.now(), limit=options["limit"])
        if not rows:
            self.stdout.write("Home is empty for this viewer.")
            return

        for position, row in enumerate(rows, start=1):
            if row["activity_type"] == "favorite_artist":
                target = f"artist: {row['artist_name']}"
            else:
                target = f"event: {row['event_title']}"
            self.stdout.write(
                f"{position:>2}. {row['activity_at'].isoformat()}  "
                f"{row['activity_type']:<14} {row['actor_username']:<20} {target}"
            )
