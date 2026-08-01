from django.db import migrations


def _replace_user_foreign_key(schema_editor, *, cascade):
    quote = schema_editor.quote_name
    with schema_editor.connection.cursor() as cursor:
        constraints = schema_editor.connection.introspection.get_constraints(
            cursor, "ACCOUNT_CODE"
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
            "Expected exactly one FK ACCOUNT_CODE.user_id -> "
            f"DANCED_USER.id; found {matches!r}"
        )
    delete_clause = " ON DELETE CASCADE" if cascade else ""
    schema_editor.execute(
        f"ALTER TABLE {quote('ACCOUNT_CODE')} "
        f"DROP FOREIGN KEY {quote(matches[0])}, "
        f"ADD CONSTRAINT {quote('fk_account_code_user')} "
        f"FOREIGN KEY ({quote('user_id')}) "
        f"REFERENCES {quote('DANCED_USER')} ({quote('id')})"
        f"{delete_clause}"
    )


def enforce_cascade(apps, schema_editor):
    _replace_user_foreign_key(schema_editor, cascade=True)


def restore_restrictive_key(apps, schema_editor):
    _replace_user_foreign_key(schema_editor, cascade=False)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [("users", "0014_accountcode")]

    operations = [
        migrations.RunPython(enforce_cascade, restore_restrictive_key),
    ]
