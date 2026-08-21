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
MAX_ARCHIVED_BYTES_PER_RUN = 100 * 1024 * 1024


class SyncAlreadyRunning(Exception):
    pass


class RequestBudgetExhausted(Exception):
    pass


class ResponseBudgetExhausted(Exception):
    pass


class RequestBudget:
    def __init__(self, *, limit):
        if limit < 1:
            raise ValueError("request budget limit must be at least one")
        self.limit = limit
        self.used = 0

    @property
    def remaining(self):
        return self.limit - self.used

    def consume(self):
        if self.used >= self.limit:
            raise RequestBudgetExhausted(
                f"request ceiling {self.limit} exhausted after "
                f"{self.used} attempts"
            )
        self.used += 1


class ResponseBudget:
    def __init__(self, *, limit):
        if limit < 1:
            raise ValueError("response budget limit must be at least one")
        self.limit = limit
        self.used = 0

    def consume(self, body_text):
        size = len(body_text.encode("utf-8")) if body_text is not None else 0
        if self.used + size > self.limit:
            raise ResponseBudgetExhausted(
                f"archived response ceiling {self.limit} bytes exhausted after "
                f"{self.used} bytes"
            )
        self.used += size


class MySqlAdvisoryLock:
    def __init__(self, name="onda_sync_ra"):
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
    wrapper_count: int = 0
    missing_event_id_count: int = 0
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
    missing_event_id_count = 0
    for wrapper in events:
        event = wrapper.get("event") if isinstance(wrapper, dict) else None
        source_id = event.get("id") if isinstance(event, dict) else None
        if not isinstance(source_id, str) or not source_id:
            missing_event_id_count += 1
    return total, len(events), missing_event_id_count


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
    response_budget,
    client_counts_attempts,
):
    page_number = 1
    while True:
        try:
            if not client_counts_attempts:
                request_budget.consume()
            result = client.fetch_page(
                state.seed,
                window_start,
                window_end,
                page_number,
                page_size,
            )
        except RequestBudgetExhausted as exc:
            state.fetch_valid = False
            state.errors.append(str(exc))
            return
        try:
            response_budget.consume(result.body_text)
        except ResponseBudgetExhausted as exc:
            state.fetch_valid = False
            state.errors.append(str(exc))
            return
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
            (
                total_results,
                wrapper_count,
                missing_event_id_count,
            ) = _envelope_metadata(result.body_text)
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

        state.wrapper_count += wrapper_count
        state.missing_event_id_count += missing_event_id_count

        if page_number >= state.expected_pages:
            return
        page_number += 1


def _seed_completeness(state):
    if not state.fetch_valid:
        return False, list(state.errors)
    if state.expected_pages is None or state.total_results is None:
        return False, ["pagination totals unavailable"]
    if len(state.raws) != state.expected_pages:
        return False, [
            f"page coverage {len(state.raws)} != "
            f"expectedPages {state.expected_pages}"
        ]
    statuses = dict(
        RawIngest.objects.filter(
            pk__in=[raw.pk for raw in state.raws]
        ).values_list("pk", "processing_status")
    )
    page_errors = []
    for raw in state.raws:
        if raw.http_status != 200:
            page_errors.append(
                f"page {raw.page_number} http {raw.http_status}"
            )
        status = statuses.get(raw.pk)
        if status != RawProcessingStatus.PROCESSED:
            page_errors.append(
                f"page {raw.page_number} processing_status {status}"
            )
    if page_errors:
        return False, page_errors
    if state.wrapper_count != state.total_results:
        return False, [
            f"wrapper coverage {state.wrapper_count} != "
            f"totalResults {state.total_results}"
        ]
    if state.missing_event_id_count:
        return False, [
            f"{state.missing_event_id_count}/{state.wrapper_count} "
            "listing wrappers missing event.id"
        ]
    return True, []


def run_sync(
    run_type=SyncRunType.NIGHTLY,
    client=None,
    lock=None,
    window_start=None,
    window_end=None,
    page_size=None,
):
    client = client or RaClient()
    request_budget = RequestBudget(limit=MAX_REQUESTS_PER_RUN)
    response_budget = ResponseBudget(limit=MAX_ARCHIVED_BYTES_PER_RUN)
    attach_request_budget = getattr(client, "attach_request_budget", None)
    client_counts_attempts = attach_request_budget is not None
    if client_counts_attempts:
        attach_request_budget(request_budget.consume)
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
                response_budget=response_budget,
                client_counts_attempts=client_counts_attempts,
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
            complete, completeness_errors = _seed_completeness(state)
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
                errors.extend(completeness_errors)

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
