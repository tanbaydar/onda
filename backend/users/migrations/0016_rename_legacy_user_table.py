from django.db import migrations


LEGACY_TABLE = "DANCED_USER"
CURRENT_TABLE = "ONDA_USER"


def rename_legacy_table(apps, schema_editor):
    """Bridge existing deployments to the Onda table name.

    Fresh databases already create ONDA_USER from the current migration history.
    An existing pre-rename database still has DANCED_USER, so this migration
    renames that table without copying or dropping account data.
    """

    tables = set(schema_editor.connection.introspection.table_names())
    if CURRENT_TABLE in tables:
        return
    if LEGACY_TABLE not in tables:
        raise RuntimeError(
            f"Cannot rename account table: neither {LEGACY_TABLE} nor "
            f"{CURRENT_TABLE} exists."
        )

    quote = schema_editor.quote_name
    schema_editor.execute(
        f"RENAME TABLE {quote(LEGACY_TABLE)} TO {quote(CURRENT_TABLE)}"
    )


def restore_legacy_table(apps, schema_editor):
    tables = set(schema_editor.connection.introspection.table_names())
    if LEGACY_TABLE in tables:
        return
    if CURRENT_TABLE not in tables:
        raise RuntimeError(
            f"Cannot restore account table: neither {CURRENT_TABLE} nor "
            f"{LEGACY_TABLE} exists."
        )

    quote = schema_editor.quote_name
    schema_editor.execute(
        f"RENAME TABLE {quote(CURRENT_TABLE)} TO {quote(LEGACY_TABLE)}"
    )


class Migration(migrations.Migration):
    dependencies = [("users", "0015_enforce_account_code_user_cascade")]

    operations = [
        migrations.RunPython(rename_legacy_table, restore_legacy_table),
    ]
