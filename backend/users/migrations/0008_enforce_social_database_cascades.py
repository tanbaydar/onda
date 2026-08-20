from django.db import migrations


FOREIGN_KEYS = (
    ("FOLLOW", "follower_id", "ONDA_USER", "fk_follow_follower"),
    ("FOLLOW", "followee_id", "ONDA_USER", "fk_follow_followee"),
    ("NOTIFICATION", "recipient_id", "ONDA_USER", "fk_notification_recipient"),
    ("NOTIFICATION", "actor_id", "ONDA_USER", "fk_notification_actor"),
    ("NOTIFICATION", "review_id", "REVIEW", "fk_notification_review"),
)


def _replace_foreign_keys(schema_editor, *, cascade):
    connection = schema_editor.connection
    quote = schema_editor.quote_name
    for table, column, target_table, name in FOREIGN_KEYS:
        with connection.cursor() as cursor:
            constraints = connection.introspection.get_constraints(cursor, table)
        matches = [
            constraint_name
            for constraint_name, details in constraints.items()
            if details["columns"] == [column]
            and details["foreign_key"] is not None
            and details["foreign_key"][0].lower() == target_table.lower()
            and details["foreign_key"][1] == "id"
        ]
        if len(matches) != 1:
            raise RuntimeError(
                f"Expected exactly one FK {table}.{column} -> "
                f"{target_table}.id; found {matches!r}"
            )
        delete_clause = " ON DELETE CASCADE" if cascade else ""
        schema_editor.execute(
            f"ALTER TABLE {quote(table)} "
            f"DROP FOREIGN KEY {quote(matches[0])}, "
            f"ADD CONSTRAINT {quote(name)} "
            f"FOREIGN KEY ({quote(column)}) "
            f"REFERENCES {quote(target_table)} ({quote('id')})"
            f"{delete_clause}"
        )


def enforce_cascades(apps, schema_editor):
    _replace_foreign_keys(schema_editor, cascade=True)


def restore_restrictive_keys(apps, schema_editor):
    _replace_foreign_keys(schema_editor, cascade=False)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("users", "0007_follow_notification"),
    ]

    operations = [
        migrations.RunPython(enforce_cascades, restore_restrictive_keys),
    ]
