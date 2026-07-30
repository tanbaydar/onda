from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import timedelta

from django.db import connection
from django.utils import timezone

from catalog.models import CityIdentity
from ingestion.client import RaClient
from ingestion.models import (
    RawIngest,
    RawProcessingStatus,
    RejectedIngest,
    SyncRun,
    SyncRunStatus,
    SyncRunType,
    TrackedSourcePage,
)
from ingestion.reconciler import reconcile
from ingestion.transformer import transform


DEFAULT_PAGE_SIZE = 20
DEFAULT_NIGHTLY_DAYS = 30
MAX_REQUESTS_PER_RUN = 1_000


class SyncAlreadyRunning(Exception):
    pass


class MySqlAdvisoryLock:
    def __init__(self, name="danced_sync_ra"):
        self.name = name

    def acquire(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT GET_LOCK(%s, 0)", [self.name])
            row = cursor.fetchone()
        return bool(row and row[0] == 1)

    def release(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT RELEASE_LOCK(%s)", [self.name])


@dataclass
class _SeedState:
    seed: TrackedSourcePage
    raws: list[RawIngest] = field(default_factory=list)
    expected_pages: int | None = None
    total_results: int | None = None
    fetch_valid: bool = True
    errors: list[str] = field(default_factory=list)
    observed_source_ids: set[str] = field(default_factory=set)


def _append_error(errors, message):
    if message:
        errors.append(str(message))


def _envelope_metadata(body):
    payload = json.loads(body)
    if not isinstance(payload, dict):
        raise ValueError("payload root is not an object")
    if payload.get("errors"):
        raise ValueError("GraphQL response contains errors")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise ValueError("data envelope is absent or invalid")
    listings = data.get("eventListings")
    if not isinstance(listings, dict):
        raise ValueError("eventListings envelope is absent or invalid")
    events = listings.get("data")
    total = listings.get("totalResults")
    if not isinstance(events, list):
        raise ValueError("eventListings.data is absent or invalid")
    if not isinstance(total, int) or isinstance(total, bool) or total < 0:
        raise ValueError("eventListings.totalResults is invalid")
    return total


def _archive_result(
    *,
    seed,
    run,
    window_start,
    window_end,
    page_number,
    page_size,
    result,
):
    return RawIngest.objects.create(
        seed=seed,
        run=run,
        window_start=window_start,
        window_end=window_end,
        page_number=page_number,
        page_size=page_size,
        response_body=result.body_text,
        http_status=result.status_code,
        fetched_at=result.fetched_at,
        processing_status=RawProcessingStatus.PENDING,
    )


def _fetch_seed(
    *,
    state,
    run,
    client,
    window_start,
    window_end,
    page_size,
    request_budget,
):
    page_number = 1
    while True:
        if request_budget[0] >= MAX_REQUESTS_PER_RUN:
            state.fetch_valid = False
            state.errors.append("hard per-run request ceiling reached")
            return
        request_budget[0] += 1

        result = client.fetch_page(
            state.seed,
            window_start,
            window_end,
            page_number,
            page_size,
        )
        raw = _archive_result(
            seed=state.seed,
            run=run,
            window_start=window_start,
            window_end=window_end,
            page_number=page_number,
            page_size=page_size,
            result=result,
        )
        state.raws.append(raw)

        if result.status_code is None:
            state.fetch_valid = False
            _append_error(state.errors, result.error)
            return
        if result.status_code != 200:
            state.fetch_valid = False
            state.errors.append(
                f"HTTP {result.status_code} for seed {state.seed.area_ref} "
                f"page {page_number}"
            )
            return
        try:
            total_results = _envelope_metadata(result.body_text)
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            state.fetch_valid = False
            state.errors.append(
                f"unusable listing envelope for seed "
                f"{state.seed.area_ref} page {page_number}: {exc}"
            )
            return

        if state.total_results is None:
            state.total_results = total_results
            state.expected_pages = max(1, math.ceil(total_results / page_size))
        elif total_results != state.total_results:
            state.fetch_valid = False
            state.errors.append(
                f"inconsistent totalResults for seed {state.seed.area_ref}"
            )
            return

        if page_number >= state.expected_pages:
            return
        page_number += 1


def _seed_is_complete(state):
    if not state.fetch_valid:
        return False
    if state.expected_pages is None or state.total_results is None:
        return False
    if len(state.raws) != state.expected_pages:
        return False
    statuses = dict(
        RawIngest.objects.filter(
            pk__in=[raw.pk for raw in state.raws]
        ).values_list("pk", "processing_status")
    )
    if any(
        raw.http_status != 200
        or statuses.get(raw.pk) != RawProcessingStatus.PROCESSED
        for raw in state.raws
    ):
        return False
    return len(state.observed_source_ids) == state.total_results


def run_sync(
    run_type=SyncRunType.NIGHTLY,
    client=None,
    lock=None,
    window_start=None,
    window_end=None,
    page_size=None,
):
    client = client or RaClient()
    lock = lock or MySqlAdvisoryLock()
    if not lock.acquire():
        raise SyncAlreadyRunning("an RA synchronization is already running")

    run = None
    try:
        now = timezone.now()
        if window_start is None:
            window_start = now.date()
        if window_end is None:
            window_end = window_start + timedelta(days=DEFAULT_NIGHTLY_DAYS)
        page_size = page_size or DEFAULT_PAGE_SIZE
        if page_size < 1:
            raise ValueError("page_size must be at least one")

        run = SyncRun.objects.create(
            run_type=run_type,
            status=SyncRunStatus.RUNNING,
            started_at=now,
        )
        states = {}
        errors = []
        request_budget = [0]

        seeds = list(
            TrackedSourcePage.objects.filter(active=True).order_by("pk")
        )
        run.seeds_attempted = len(seeds)

        for seed in seeds:
            try:
                CityIdentity.objects.get(
                    source=seed.source,
                    source_id=seed.area_ref,
                )
            except CityIdentity.DoesNotExist:
                run.seeds_failed += 1
                errors.append(
                    f"seed {seed.source}:{seed.area_ref} has no city mapping"
                )
                seed.last_synced_at = timezone.now()
                seed.save(update_fields=["last_synced_at"])
                continue

            state = _SeedState(seed=seed)
            states[seed.pk] = state
            _fetch_seed(
                state=state,
                run=run,
                client=client,
                window_start=window_start,
                window_end=window_end,
                page_size=page_size,
                request_budget=request_budget,
            )

        rejection_count_before = RejectedIngest.objects.count()
        current_raw_ids = {
            raw.pk for state in states.values() for raw in state.raws
        }
        raw_to_state = {
            raw.pk: state
            for state in states.values()
            for raw in state.raws
        }
        for raw in RawIngest.objects.filter(
            processing_status=RawProcessingStatus.PENDING
        ).order_by("pk"):
            outcome = transform(raw)
            run.events_upserted += outcome.admitted_count
            run.events_dropped += outcome.dropped_count
            if raw.pk in current_raw_ids:
                raw_to_state[raw.pk].observed_source_ids.update(
                    outcome.observed_source_ids
                )

        run.events_quarantined = (
            RejectedIngest.objects.count() - rejection_count_before
        )

        for state in states.values():
            state.seed.last_synced_at = timezone.now()
            complete = _seed_is_complete(state)
            if complete:
                state.seed.last_success_at = timezone.now()
                state.seed.save(
                    update_fields=["last_synced_at", "last_success_at"]
                )
                if run_type not in (
                    SyncRunType.BACKFILL,
                    SyncRunType.REPLAY,
                ):
                    reconcile(
                        state.seed,
                        run,
                        state.observed_source_ids,
                        True,
                        window_start,
                        window_end,
                    )
            else:
                run.seeds_failed += 1
                state.seed.save(update_fields=["last_synced_at"])
                errors.extend(state.errors)

        run.status = SyncRunStatus.COMPLETED
        run.finished_at = timezone.now()
        run.error_summary = "\n".join(errors) or None
        run.save(
            update_fields=[
                "status",
                "finished_at",
                "seeds_attempted",
                "seeds_failed",
                "events_upserted",
                "events_quarantined",
                "events_dropped",
                "error_summary",
            ]
        )
        return run
    except Exception as exc:
        if run is not None:
            run.status = SyncRunStatus.CRASHED
            run.finished_at = timezone.now()
            run.error_summary = str(exc)
            run.save(
                update_fields=["status", "finished_at", "error_summary"]
            )
        raise
    finally:
        lock.release()
