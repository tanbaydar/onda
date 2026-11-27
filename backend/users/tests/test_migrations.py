from datetime import UTC, datetime, timedelta
from importlib import import_module

from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

from catalog.models import City, Event, EventStatus, Venue
from users.models import DiaryEntry, Notification, Review, User


rename_migration = import_module(
    "users.migrations.0016_rename_legacy_user_table"
)
NOW = datetime(2026, 8, 20, 16, 0, tzinfo=UTC)


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


class NotificationUniqueKeyMigrationTests(TransactionTestCase):
    before = [("users", "0018_notification_will_be_there")]
    after = [("users", "0020_notification_unique_event_target")]
    keys = {"uq_notification_review_target", "uq_notification_event_target"}

    def migrate(self, targets):
        executor = MigrationExecutor(connection)
        executor.migrate(targets)

    def migrate_to_latest(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())

    def unique_keys(self):
        with connection.cursor() as cursor:
            constraints = connection.introspection.get_constraints(
                cursor, "NOTIFICATION"
            )
        return {
            name: details["columns"]
            for name, details in constraints.items()
            if details["unique"] and not details["primary_key"]
        }

    def setUp(self):
        self.addCleanup(self.migrate_to_latest)
        self.migrate(self.before)
        city = City.objects.create(
            name="Merge City",
            region_code="MA",
            region_name="Massachusetts",
            country_code="US",
            timezone="America/New_York",
        )
        venue = Venue.objects.create(name="Merge Venue", city=city)
        self.event = Event.objects.create(
            title="Merge Event",
            event_date="2026-07-01",
            venue=venue,
            status=EventStatus.ACTIVE,
        )
        self.author, self.maya, self.sam = (
            User.objects.create_user(
                email=f"{name}@merge.test",
                password="A-real-password-123!",
                username=f"merge.{name}",
                display_name=name,
                is_private=False,
            )
            for name in ("author", "maya", "sam")
        )
        entry = DiaryEntry.objects.create(
            user=self.author, event=self.event, rating="4.0", rated_at=NOW
        )
        self.review = Review.objects.create(
            entry=entry, body="Merge target", published_at=NOW
        )

    def notify(self, recipient, actor, minutes, *, read_after=None, **target):
        created_at = NOW + timedelta(minutes=minutes)
        return Notification.objects.create(
            recipient=recipient,
            actor=actor,
            created_at=created_at,
            read_at=(
                created_at + timedelta(minutes=read_after)
                if read_after is not None
                else None
            ),
            **target,
        ).id

    def test_migration_merges_copies_keeps_the_read_state_and_adds_the_keys(self):
        like = {"type": "review_like", "review": self.review}
        plan = {"type": "will_be_there", "event": self.event}
        follow = {"type": "follow"}
        # The recipient read the first copy. Two later copies are not read.
        read_first = self.notify(self.author, self.maya, 0, read_after=1, **like)
        self.notify(self.author, self.maya, 10, **like)
        self.notify(self.author, self.maya, 20, **like)
        # The recipient read only the second copy.
        read_later = self.notify(self.sam, self.maya, 0, **plan)
        self.notify(self.sam, self.maya, 10, read_after=5, **plan)
        # The recipient read no copy.
        not_read = self.notify(self.author, self.maya, 0, **plan)
        self.notify(self.author, self.maya, 10, **plan)
        # These rows are not copies: a second actor, and a type with no target.
        single = self.notify(self.author, self.sam, 0, **like)
        follows = [self.notify(self.author, self.sam, 0, **follow) for _ in range(2)]
        self.assertEqual(self.unique_keys(), {})

        self.migrate(self.after)

        self.assertEqual(
            dict(Notification.objects.values_list("id", "read_at")),
            {
                read_first: NOW + timedelta(minutes=1),
                read_later: NOW + timedelta(minutes=15),
                not_read: None,
                single: None,
                follows[0]: None,
                follows[1]: None,
            },
        )
        self.assertEqual(
            self.unique_keys(),
            {
                "uq_notification_review_target": [
                    "review_id", "actor_id", "type", "recipient_id",
                ],
                "uq_notification_event_target": [
                    "event_id", "actor_id", "type", "recipient_id",
                ],
            },
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.notify(self.author, self.maya, 30, **like)
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.notify(self.author, self.maya, 30, **plan)

    def test_migration_reverses_and_keeps_each_foreign_key(self):
        self.migrate(self.after)
        with connection.cursor() as cursor:
            before_reverse = connection.introspection.get_relations(
                cursor, "NOTIFICATION"
            )

        self.migrate(self.before)

        with connection.cursor() as cursor:
            after_reverse = connection.introspection.get_relations(
                cursor, "NOTIFICATION"
            )
        self.assertEqual(self.unique_keys(), {})
        self.assertEqual(after_reverse, before_reverse)
        self.assertEqual(
            set(after_reverse), {"recipient_id", "actor_id", "review_id", "event_id"}
        )
        # With no key, a copy is possible again. The next forward run merges it.
        for minutes in (0, 10):
            self.notify(
                self.author, self.maya, minutes, type="will_be_there", event=self.event
            )
        self.migrate(self.after)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(set(self.unique_keys()), self.keys)
