from collections import defaultdict

import django.db.models.deletion
from django.db import migrations, models


def _normalized_title(value):
    return " ".join(value.split()).casefold()


def mark_semantic_event_aliases(apps, schema_editor):
    Event = apps.get_model("catalog", "Event")
    EventArtist = apps.get_model("catalog", "EventArtist")
    DiaryEntry = apps.get_model("users", "DiaryEntry")
    FavoriteEvent = apps.get_model("users", "FavoriteEvent")
    WillBeThere = apps.get_model("users", "WillBeThere")

    groups = defaultdict(list)
    for event in Event.objects.order_by("id").iterator():
        lineup = tuple(
            EventArtist.objects.filter(event_id=event.id)
            .order_by("position")
            .values_list("artist_id", flat=True)
        )
        key = (
            _normalized_title(event.title),
            event.event_date,
            event.start_time,
            event.venue_id,
            lineup,
        )
        groups[key].append(event)

    for events in groups.values():
        if len(events) < 2:
            continue
        event_ids = [event.id for event in events]
        has_user_data = (
            DiaryEntry.objects.filter(event_id__in=event_ids).exists()
            or FavoriteEvent.objects.filter(event_id__in=event_ids).exists()
            or WillBeThere.objects.filter(event_id__in=event_ids).exists()
        )
        if has_user_data:
            continue
        canonical = events[0]
        Event.objects.filter(id__in=event_ids[1:]).update(
            canonical_event_id=canonical.id
        )


def unmark_semantic_event_aliases(apps, schema_editor):
    Event = apps.get_model("catalog", "Event")
    Event.objects.exclude(canonical_event_id=None).update(canonical_event_id=None)


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0005_seed_city_identities_and_enforce_cascade"),
        ("users", "0016_rename_legacy_user_table"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="canonical_event",
            field=models.ForeignKey(
                blank=True,
                db_column="canonical_event_id",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="source_aliases",
                to="catalog.event",
            ),
        ),
        migrations.RunPython(
            mark_semantic_event_aliases,
            unmark_semantic_event_aliases,
        ),
    ]
