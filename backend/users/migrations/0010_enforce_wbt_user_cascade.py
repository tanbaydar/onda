from django.db import migrations


def _replace_user_foreign_key(schema_editor, *, cascade):
    connection = schema_editor.connection
    quote = schema_editor.quote_name
    with connection.cursor() as cursor:
        constraints = connection.introspection.get_constraints(
            cursor, "WILL_BE_THERE"
        )
    matches = [
        name
        for name, details in constraints.items()
        if details["columns"] == ["user_id"]
        and details["foreign_key"] is not None
        and details["foreign_key"][0].lower() == "onda_user"
        and details["foreign_key"][1] == "id"
    ]
    if len(matches) != 1:
        raise RuntimeError(
            "Expected exactly one FK WILL_BE_THERE.user_id -> "
            f"ONDA_USER.id; found {matches!r}"
        )
    delete_clause = " ON DELETE CASCADE" if cascade else ""
    schema_editor.execute(
        f"ALTER TABLE {quote('WILL_BE_THERE')} "
        f"DROP FOREIGN KEY {quote(matches[0])}, "
        f"ADD CONSTRAINT {quote('fk_wbt_user')} "
        f"FOREIGN KEY ({quote('user_id')}) "
        f"REFERENCES {quote('ONDA_USER')} ({quote('id')})"
        f"{delete_clause}"
    )


def enforce_cascade(apps, schema_editor):
    _replace_user_foreign_key(schema_editor, cascade=True)


def restore_restrictive_key(apps, schema_editor):
    _replace_user_foreign_key(schema_editor, cascade=False)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [("users", "0009_willbethere")]

    operations = [
        migrations.RunPython(enforce_cascade, restore_restrictive_key),
    ]
