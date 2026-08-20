from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase


class SyncCommandAlarmTests(SimpleTestCase):
    def test_zero_upsert_run_logs_and_exits_nonzero(self):
        run = SimpleNamespace(
            id=42,
            status="completed",
            seeds_attempted=2,
            seeds_failed=0,
            events_upserted=0,
            events_quarantined=0,
        )
        stderr = StringIO()

        with (
            patch(
                "ingestion.management.commands.sync_ra.run_sync",
                return_value=run,
            ),
            self.assertLogs(
                "ingestion.management.commands.sync_ra",
                level="ERROR",
            ) as logs,
            self.assertRaises(CommandError) as raised,
        ):
            call_command("sync_ra", stderr=stderr)

        self.assertEqual(raised.exception.returncode, 1)
        self.assertIn("zero events upserted", stderr.getvalue())
        self.assertTrue(
            any("zero events upserted" in message for message in logs.output)
        )
