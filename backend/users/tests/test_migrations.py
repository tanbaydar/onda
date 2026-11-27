from importlib import import_module

from django.db import connection
from django.test import TransactionTestCase


rename_migration = import_module(
    "users.migrations.0016_rename_legacy_user_table"
)


class OndaUserTableMigrationTests(TransactionTestCase):
    def test_table_rename_migration_is_non_atomic_for_mysql(self):
        self.assertFalse(rename_migration.Migration.atomic)

    def table_names(self):
        return set(connection.introspection.table_names())

    def rename_table(self, source, target):
        quote = connection.ops.quote_name
        with connection.schema_editor() as schema_editor:
            schema_editor.execute(
                f"RENAME TABLE {quote(source)} TO {quote(target)}"
            )

    def ensure_current_table_name(self):
        tables = self.table_names()
        if rename_migration.LEGACY_TABLE in tables:
            self.rename_table(
                rename_migration.LEGACY_TABLE,
                rename_migration.CURRENT_TABLE,
            )

    def test_forward_and_reverse_rename_preserve_the_user_table(self):
        self.addCleanup(self.ensure_current_table_name)
        self.rename_table(
            rename_migration.CURRENT_TABLE,
            rename_migration.LEGACY_TABLE,
        )

        with connection.schema_editor() as schema_editor:
            rename_migration.rename_legacy_table(None, schema_editor)

        self.assertIn(rename_migration.CURRENT_TABLE, self.table_names())
        self.assertNotIn(rename_migration.LEGACY_TABLE, self.table_names())

        with connection.schema_editor() as schema_editor:
            rename_migration.restore_legacy_table(None, schema_editor)

        self.assertIn(rename_migration.LEGACY_TABLE, self.table_names())
        self.assertNotIn(rename_migration.CURRENT_TABLE, self.table_names())
