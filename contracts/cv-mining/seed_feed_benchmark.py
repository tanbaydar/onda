#!/usr/bin/env python3
"""Seed and benchmark the shipped home feed against a dedicated MySQL database.

Run with DJANGO_SETTINGS_MODULE=config.settings_production and a DANCED_DB_NAME
containing ``benchmark``. The safety checks intentionally reject the normal
``danced`` database and any database that already contains application data.
"""

from __future__ import annotations

import argparse
import math
import os
import platform
import subprocess
import sys
import time
from datetime import UTC, date, datetime, time as datetime_time, timedelta
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_production")

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from django.db import connection, transaction  # noqa: E402
from django.test import Client  # noqa: E402

from catalog.models import Artist, City, Event, EventStatus, Venue  # noqa: E402
from users.models import (  # noqa: E402
    DiaryEntry,
    FavoriteArtist,
    FavoriteEvent,
    Follow,
    FollowStatus,
    Review,
    ReviewLike,
    User,
    WillBeThere,
)


PASSWORD = "feed-benchmark-only-password"
VIEWER_EMAIL = "cv-feed-viewer@benchmark.invalid"
BATCH_SIZE = 2_000
TARGETS = {
    "follow": 20_000,
    "rated_been": 20_000,
    "will_be_there": 15_000,
    "favorite_event": 20_000,
    "favorite_artist": 15_000,
    "review_like": 10_000,
}


def guard_database() -> None:
    name = settings.DATABASES["default"]["NAME"]
    if "benchmark" not in name.lower() or name.lower() == "danced":
        raise SystemExit(
            f"Refusing database {name!r}; DANCED_DB_NAME must name a dedicated "
            "database containing 'benchmark'."
        )
    if settings.DEBUG:
        raise SystemExit("Refusing to benchmark with DEBUG enabled.")


def chunks(items, size=BATCH_SIZE):
    for start in range(0, len(items), size):
        yield items[start : start + size]


def bulk(model, rows) -> None:
    for batch in chunks(rows):
        model.objects.bulk_create(batch, batch_size=BATCH_SIZE)


def pair_stream(size: int, *, offset: int = 1):
    """Yield deterministic non-self user-index pairs without repetition."""
    emitted = 0
    distance = offset
    while emitted < size:
        for left in range(500):
            right = (left + distance) % 500
            if left != right:
                yield left, right
                emitted += 1
                if emitted == size:
                    return
        distance += 1


@transaction.atomic
def seed() -> dict[str, int]:
    populated = {
        "users": User.objects.count(),
        "events": Event.objects.count(),
        "artists": Artist.objects.count(),
        "activities": sum(
            model.objects.count()
            for model in (Follow, DiaryEntry, WillBeThere, FavoriteEvent, FavoriteArtist, ReviewLike)
        ),
    }
    # Shipped migrations seed the supported-city reference rows. They are not
    # benchmark application data and are deliberately retained.
    if any(populated.values()):
        raise SystemExit(f"Dedicated benchmark database is not empty: {populated}")

    base = datetime(2026, 8, 17, 12, 0, tzinfo=UTC)
    viewer = User.objects.create_user(
        email=VIEWER_EMAIL,
        password=PASSWORD,
        username="cv.feed.viewer",
        display_name="CV Feed Viewer",
        is_private=False,
    )
    actors = [
        User(
            email=f"cv-feed-{index:04d}@benchmark.invalid",
            username=f"cv.feed.{index:04d}",
            display_name=f"Feed Actor {index:04d}",
            is_private=(index % 10 == 0),
            password="!",
        )
        for index in range(500)
    ]
    bulk(User, actors)
    actors = list(User.objects.filter(email__endswith="@benchmark.invalid").exclude(pk=viewer.pk).order_by("pk"))

    city = City.objects.create(
        name="Benchmark City", region_code="BM", country_code="US", timezone="UTC"
    )
    venue = Venue.objects.create(name="Benchmark Venue", city=city)
    artists = [Artist(name=f"Benchmark Artist {index:04d}") for index in range(300)]
    bulk(Artist, artists)
    artists = list(Artist.objects.order_by("pk"))
    events = [
        Event(
            title=f"Benchmark Event {index:04d}",
            event_date=date(2027, 1, 1) + timedelta(days=index % 365),
            start_time=datetime_time(20, 0),
            venue=venue,
            status=EventStatus.ACTIVE,
        )
        for index in range(500)
    ]
    bulk(Event, events)
    events = list(Event.objects.order_by("pk"))

    follows = []
    # These 50 relationships define the viewer's realistically selective feed.
    for index, actor in enumerate(actors[:50]):
        stamp = base - timedelta(seconds=index)
        follows.append(Follow(follower=viewer, followee=actor, status=FollowStatus.APPROVED, created_at=stamp, approved_at=stamp))
    for left, right in pair_stream(TARGETS["follow"] - len(follows)):
        stamp = base - timedelta(seconds=len(follows))
        follows.append(Follow(follower=actors[left], followee=actors[right], status=FollowStatus.APPROVED, created_at=stamp, approved_at=stamp))
    bulk(Follow, follows)

    entries = []
    for index in range(TARGETS["rated_been"]):
        entries.append(
            DiaryEntry(
                user=actors[index % len(actors)],
                event=events[(index // len(actors)) % len(events)],
                rating="4.0",
                rated_at=base - timedelta(minutes=index),
            )
        )
    bulk(DiaryEntry, entries)
    entries = list(DiaryEntry.objects.order_by("pk"))
    reviews = [
        Review(entry=entry, body=f"Benchmark review {index}", published_at=entry.rated_at)
        for index, entry in enumerate(entries)
    ]
    bulk(Review, reviews)
    reviews = list(Review.objects.order_by("pk"))

    bulk(
        WillBeThere,
        [
            WillBeThere(
                user=actors[index % 500],
                event=events[(index // 500) % 500],
                created_at=base - timedelta(seconds=index * 2 + 1),
            )
            for index in range(TARGETS["will_be_there"])
        ],
    )
    bulk(
        FavoriteEvent,
        [
            FavoriteEvent(
                user=actors[index % 500],
                event=events[(index // 500) % 500],
                added_at=base - timedelta(seconds=index * 2 + 2),
            )
            for index in range(TARGETS["favorite_event"])
        ],
    )
    bulk(
        FavoriteArtist,
        [
            FavoriteArtist(
                user=actors[index % 500],
                artist=artists[(index // 500) % 300],
                added_at=base - timedelta(seconds=index * 2 + 3),
            )
            for index in range(TARGETS["favorite_artist"])
        ],
    )
    bulk(
        ReviewLike,
        [
            ReviewLike(
                user=actors[index % 500],
                review=reviews[(index * 7) % len(reviews)],
            )
            for index in range(TARGETS["review_like"])
        ],
    )
    return exact_counts()


def exact_counts() -> dict[str, int]:
    counts = {
        "users": User.objects.count(),
        "viewer_follows": Follow.objects.filter(follower__email=VIEWER_EMAIL).count(),
        "cities": City.objects.count(),
        "venues": Venue.objects.count(),
        "events": Event.objects.count(),
        "artists": Artist.objects.count(),
        "reviews": Review.objects.count(),
        "follow": Follow.objects.count(),
        "rated_been": DiaryEntry.objects.filter(rating__isnull=False).count(),
        "will_be_there": WillBeThere.objects.count(),
        "favorite_event": FavoriteEvent.objects.count(),
        "favorite_artist": FavoriteArtist.objects.count(),
        "review_like": ReviewLike.objects.count(),
    }
    counts["total_activity_rows"] = sum(counts[name] for name in TARGETS)
    return counts


def get(client: Client, cursor=None):
    params = {"page_size": 20}
    if cursor:
        params["cursor"] = cursor
    response = client.get("/api/me/home/", params, secure=True, HTTP_HOST="localhost")
    if response.status_code != 200:
        raise RuntimeError(f"Feed returned HTTP {response.status_code}: {response.content[:500]!r}")
    return response


def percentile95_ms(samples: list[float]) -> float:
    return sorted(samples)[math.ceil(0.95 * len(samples)) - 1] * 1_000


def measure(client: Client, cursor, requests=220, discard=20):
    samples = []
    for index in range(requests):
        started = time.perf_counter()
        response = get(client, cursor)
        elapsed = time.perf_counter() - started
        if index >= discard:
            samples.append(elapsed)
    return round(percentile95_ms(samples), 3), len(samples), len(response.json()["results"])


def benchmark() -> dict:
    client = Client()
    if not client.login(email=VIEWER_EMAIL, password=PASSWORD):
        raise RuntimeError("Session authentication failed")

    cursors = {1: None}
    cursor = None
    max_depth = 0
    for page in range(1, 51):
        cursors[page] = cursor
        payload = get(client, cursor).json()
        if not payload["results"]:
            break
        max_depth = page
        cursor = payload["next_cursor"]
        if not cursor:
            break
    depth = 50 if max_depth >= 50 else max_depth
    page1, page1_n, page1_items = measure(client, cursors[1])
    deep, deep_n, deep_items = measure(client, cursors[depth])
    with connection.cursor() as cursor_db:
        cursor_db.execute("SELECT VERSION()")
        mysql_version = cursor_db.fetchone()[0]
    try:
        hardware = subprocess.check_output(
            ["sysctl", "-n", "machdep.cpu.brand_string", "hw.memsize"], text=True
        ).strip().splitlines()
        cpu, memory_bytes = hardware[0], int(hardware[1])
    except (OSError, subprocess.SubprocessError, ValueError, IndexError):
        cpu, memory_bytes = platform.processor() or platform.machine(), None
    return {
        "page_1_p95_ms": page1,
        "page_1_measured_requests": page1_n,
        "page_1_items": page1_items,
        "deep_page": depth,
        "deep_page_p95_ms": deep,
        "deep_page_measured_requests": deep_n,
        "deep_page_items": deep_items,
        "max_depth_confirmed": max_depth,
        "mysql_version": mysql_version,
        "cpu": cpu,
        "memory_bytes": memory_bytes,
        "os": platform.platform(),
        "python": platform.python_version(),
        "django": django.get_version(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("seed", "counts", "benchmark"))
    args = parser.parse_args()
    guard_database()
    result = seed() if args.action == "seed" else exact_counts() if args.action == "counts" else benchmark()
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
