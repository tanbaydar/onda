from django.db import migrations, models
from django.db.models import Count, Min


TARGET = "review"
KEY = (f"{TARGET}_id", "actor_id", "type", "recipient_id")


def merge_duplicate_notifications(apps, schema_editor):
    """Leave one row for each value of the key, so that the key can go on.

    Before this migration, a like that a person removed and added again wrote
    a second notification. The oldest row of each group stays, because it is
    the row that the service keeps from now on. It becomes read if the
    recipient read one of the copies, so the merge shows nothing as new.
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
    # One key in this migration, on purpose. MySQL commits each ALTER TABLE
    # by itself, so a migration with two keys can stop between them, and a
    # second run then fails on the key that is there. With one key, a run
    # that fails can start again: the merge finds nothing more to do.

    dependencies = [
        ("users", "0018_notification_will_be_there"),
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
                fields=("review", "actor", "type", "recipient"),
                name="uq_notification_review_target",
            ),
        ),
    ]
