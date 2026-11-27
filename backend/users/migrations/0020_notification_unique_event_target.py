from django.db import migrations, models
from django.db.models import Count, Min


TARGET = "event"
KEY = (f"{TARGET}_id", "actor_id", "type", "recipient_id")


def merge_duplicate_notifications(apps, schema_editor):
    """Leave one row for each value of the key, so that the key can go on.

    Before this migration, a Will Be There mark that a person removed and
    added again wrote a second notification for each follower. The oldest row
    of each group stays, because it is the row that the service keeps from now
    on. It becomes read if the recipient read one of the copies, so the merge
    shows nothing as new.
    """
    Notification = apps.get_model("users", "Notification")
    rows = Notification.objects.using(schema_editor.connection.alias)
    groups = (
        rows.filter(**{f"{TARGET}__isnull": False})
        .values(*KEY)
        .annotate(
            copies=Count("id"),
            oldest_id=Min("id"),
            first_read_at=Min("read_at"),
        )
        .filter(copies__gt=1)
    )
    for group in list(groups):
        copies = rows.filter(**{column: group[column] for column in KEY})
        if group["first_read_at"] is not None:
            copies.filter(pk=group["oldest_id"], read_at__isnull=True).update(
                read_at=group["first_read_at"]
            )
        copies.exclude(pk=group["oldest_id"]).delete()


class Migration(migrations.Migration):
    # One key in this migration, for the reason that 0019 gives.

    dependencies = [
        ("users", "0019_notification_unique_review_target"),
    ]

    operations = [
        # The reverse is empty: the rows that the merge deleted do not come back.
        migrations.RunPython(
            merge_duplicate_notifications,
            migrations.RunPython.noop,
        ),
        migrations.AddConstraint(
            model_name="notification",
            constraint=models.UniqueConstraint(
                fields=("event", "actor", "type", "recipient"),
                name="uq_notification_event_target",
            ),
        ),
    ]
