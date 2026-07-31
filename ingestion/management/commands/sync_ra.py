import logging
from datetime import date

from django.core.management.base import BaseCommand, CommandError

from ingestion.models import SyncRunStatus, SyncRunType
from ingestion.runner import SyncAlreadyRunning, run_sync


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Fetch, archive, transform, and reconcile RA event listings."

    def add_arguments(self, parser):
        parser.add_argument(
            "--backfill",
            action="store_true",
            help="Run the shared pipeline as a historical backfill.",
        )
        parser.add_argument("--window-start", type=date.fromisoformat)
        parser.add_argument("--window-end", type=date.fromisoformat)
        parser.add_argument("--page-size", type=int)

    def handle(self, *args, **options):
        try:
            run = run_sync(
                run_type=(
                    SyncRunType.BACKFILL
                    if options["backfill"]
                    else SyncRunType.NIGHTLY
                ),
                window_start=options["window_start"],
                window_end=options["window_end"],
                page_size=options["page_size"],
            )
        except SyncAlreadyRunning as exc:
            self.stderr.write(str(exc))
            raise CommandError(str(exc), returncode=2) from exc
        except Exception as exc:
            message = f"sync crashed: {exc}"
            logger.exception(message)
            self.stderr.write(message)
            raise

        alarm_reasons = []
        if run.status == SyncRunStatus.CRASHED:
            alarm_reasons.append("run status is crashed")
        if run.seeds_failed:
            alarm_reasons.append(
                f"{run.seeds_failed}/{run.seeds_attempted} seeds failed"
            )
        if run.events_upserted == 0:
            alarm_reasons.append("zero events upserted")
        if alarm_reasons:
            message = (
                f"sync {run.id} operator alarm: "
                + "; ".join(alarm_reasons)
            )
            logger.error(message)
            self.stderr.write(message)
            raise CommandError(message, returncode=1)

        self.stdout.write(
            self.style.SUCCESS(
                f"sync {run.id} {run.status}: "
                f"{run.events_upserted} admitted, "
                f"{run.events_quarantined} quarantined, "
                f"{run.seeds_failed}/{run.seeds_attempted} seeds failed"
            )
        )
