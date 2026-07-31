from django.db import migrations


TABLES = (
    ("FAVORITE_EVENT", "fk_favorite_event_user"),
    ("FAVORITE_ARTIST", "fk_favorite_artist_user"),
    ("FAVORITE_VENUE", "fk_favorite_venue_user"),
)


def _replace(schema_editor, *, cascade):
    quote = schema_editor.quote_name
    for table, replacement in TABLES:
        with schema_editor.connection.cursor() as cursor:
            constraints = schema_editor.connection.introspection.get_constraints(cursor, table)
        matches = [name for name, details in constraints.items() if details["columns"] == ["user_id"] and details["foreign_key"] and details["foreign_key"][0].lower() == "danced_user"]
        if len(matches) != 1:
            raise RuntimeError(f"Expected one {table}.user_id foreign key; found {matches!r}")
        suffix = " ON DELETE CASCADE" if cascade else ""
        schema_editor.execute(
            f"ALTER TABLE {quote(table)} DROP FOREIGN KEY {quote(matches[0])}, "
            f"ADD CONSTRAINT {quote(replacement)} FOREIGN KEY ({quote('user_id')}) "
            f"REFERENCES {quote('DANCED_USER')} ({quote('id')}){suffix}"
        )


def forwards(apps, schema_editor):
    _replace(schema_editor, cascade=True)


def backwards(apps, schema_editor):
    _replace(schema_editor, cascade=False)


class Migration(migrations.Migration):
    atomic = False
    dependencies = [("users", "0012_favoriteartist_favoriteevent_favoritevenue")]
    operations = [migrations.RunPython(forwards, backwards)]
