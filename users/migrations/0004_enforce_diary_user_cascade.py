from django.db import migrations


def _replace_user_foreign_key(schema_editor, *, cascade):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        constraints = connection.introspection.get_constraints(
            cursor,
            "DIARY_ENTRY",
        )
    matches = [
        name
        for name, details in constraints.items()
        if details["columns"] == ["user_id"]
        and details["foreign_key"] is not None
        and details["foreign_key"][0].lower() == "danced_user"
        and details["foreign_key"][1] == "id"
    ]
    if len(matches) != 1:
        raise RuntimeError(
            "Expected exactly one FK DIARY_ENTRY.user_id -> DANCED_USER.id; "
            f"found {matches!r}"
        )
    quote = schema_editor.quote_name
    name = "fk_diary_entry_user" if cascade else "fk_diary_entry_user_restrict"
    delete_clause = " ON DELETE CASCADE" if cascade else ""
    schema_editor.execute(
        f"ALTER TABLE {quote('DIARY_ENTRY')} "
        f"DROP FOREIGN KEY {quote(matches[0])}, "
        f"ADD CONSTRAINT {quote(name)} "
        f"FOREIGN KEY ({quote('user_id')}) "
        f"REFERENCES {quote('DANCED_USER')} ({quote('id')})"
        f"{delete_clause}"
    )


def enforce_user_cascade(apps, schema_editor):
    _replace_user_foreign_key(schema_editor, cascade=True)


def restore_user_restrict(apps, schema_editor):
    _replace_user_foreign_key(schema_editor, cascade=False)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("users", "0003_diaryentry"),
    ]

    operations = [
        migrations.RunPython(
            enforce_user_cascade,
            restore_user_restrict,
        ),
    ]
