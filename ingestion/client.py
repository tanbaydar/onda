"""RA transport adapter.

Public, non-authenticated headers empirically required by RA's Cloudflare edge
(verified 2026-07-30). No cookies, credentials, session tokens, CAPTCHA handling,
or challenge circumvention. The Referer is transport metadata only; event
geography comes solely from the seed and CITY_IDENTITY, never from headers. The
NYC Referer's suitability for other cities (e.g. Boston) is unverified and pending
a supervised probe.
"""

from __future__ import annotations

import json
import random
import socket
import time
from dataclasses import dataclass
from datetime import date, datetime, timezone as datetime_timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.utils import timezone


GRAPHQL_ENDPOINT = "https://ra.co/graphql"
MAX_ATTEMPTS = 3
BASE_BACKOFF_SECONDS = 1.0
MAX_BACKOFF_SECONDS = 8.0
REQUEST_TIMEOUT_SECONDS = 20
RETRYABLE_HTTP_STATUSES = frozenset({408, 429, 500, 502, 503, 504})

# This exact public, non-authenticated set passed the supervised RA edge probe.
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    ),
    "Origin": "https://ra.co",
    "Referer": "https://ra.co/events/us/newyork",
    "Accept-Language": "en-US,en;q=0.9",
}

_REQUEST_FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "recon"
    / "fixtures"
    / "ra_event_listings_request.json"
)


@dataclass(frozen=True)
class FetchResult:
    status_code: int | None
    body_text: str | None
    fetched_at: datetime
    error: str | None = None

    def __post_init__(self):
        if (self.status_code is None) != (self.error is not None):
            raise ValueError(
                "error must be populated if and only if status_code is None"
            )


class RaClient:
    def __init__(
        self,
        *,
        timeout_seconds: float = REQUEST_TIMEOUT_SECONDS,
        max_attempts: int = MAX_ATTEMPTS,
    ):
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least one")
        self.timeout_seconds = timeout_seconds
        self.max_attempts = max_attempts
        with _REQUEST_FIXTURE.open(encoding="utf-8") as fixture:
            captured = json.load(fixture)
        self.operation_name = captured["operationName"]
        self.query = captured["query"]
        self.base_variables = captured["variables"]

    def fetch_page(
        self,
        seed,
        window_start: date,
        window_end: date,
        page_number: int,
        page_size: int,
    ) -> FetchResult:
        payload = {
            "operationName": self.operation_name,
            "variables": {
                **self.base_variables,
                "filters": {
                    **self.base_variables["filters"],
                    "areas": {"eq": int(seed.area_ref)},
                    "listingDate": {
                        "gte": window_start.isoformat(),
                        "lte": window_end.isoformat(),
                    },
                },
                "page": page_number,
                "pageSize": page_size,
            },
            "query": self.query,
        }
        request_body = json.dumps(payload, separators=(",", ":")).encode("utf-8")

        last_transport_error = None
        for attempt in range(1, self.max_attempts + 1):
            request = Request(
                GRAPHQL_ENDPOINT,
                data=request_body,
                headers=HEADERS,
                method="POST",
            )
            try:
                with urlopen(request, timeout=self.timeout_seconds) as response:
                    status = response.status
                    body = response.read().decode("utf-8", errors="replace")
                    result = FetchResult(
                        status_code=status,
                        body_text=body,
                        fetched_at=timezone.now(),
                    )
                    if (
                        status in RETRYABLE_HTTP_STATUSES
                        and attempt < self.max_attempts
                    ):
                        self._sleep_before_retry(
                            attempt,
                            response.headers.get("Retry-After"),
                        )
                        continue
                    return result
            except HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                result = FetchResult(
                    status_code=exc.code,
                    body_text=body,
                    fetched_at=timezone.now(),
                )
                if (
                    exc.code in RETRYABLE_HTTP_STATUSES
                    and attempt < self.max_attempts
                ):
                    self._sleep_before_retry(
                        attempt,
                        exc.headers.get("Retry-After"),
                    )
                    continue
                return result
            except (TimeoutError, socket.timeout, URLError) as exc:
                last_transport_error = self._transport_error_text(exc, attempt)
                if attempt < self.max_attempts:
                    self._sleep_before_retry(attempt, None)
                    continue

        return FetchResult(
            status_code=None,
            body_text=None,
            fetched_at=timezone.now(),
            error=last_transport_error or "transport failure",
        )

    @staticmethod
    def _transport_error_text(exc: Exception, attempts: int) -> str:
        reason = exc.reason if isinstance(exc, URLError) else exc
        return f"{reason} after {attempts} attempt(s)"

    @staticmethod
    def _sleep_before_retry(attempt: int, retry_after: str | None):
        delay = RaClient._retry_after_seconds(retry_after)
        if delay is None:
            ceiling = min(
                MAX_BACKOFF_SECONDS,
                BASE_BACKOFF_SECONDS * (2 ** (attempt - 1)),
            )
            delay = random.uniform(0, ceiling)
        time.sleep(delay)

    @staticmethod
    def _retry_after_seconds(value: str | None) -> float | None:
        if not value:
            return None
        try:
            return max(0.0, float(value))
        except ValueError:
            try:
                retry_at = parsedate_to_datetime(value)
            except (TypeError, ValueError):
                return None
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=datetime_timezone.utc)
            return max(
                0.0,
                (
                    retry_at
                    - datetime.now(datetime_timezone.utc)
                ).total_seconds(),
            )
