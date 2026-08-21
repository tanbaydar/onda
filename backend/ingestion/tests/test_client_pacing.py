from datetime import date
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock, call, patch
from urllib.error import HTTPError, URLError
from urllib.request import Request

from django.test import SimpleTestCase

from ingestion.client import (
    GRAPHQL_ENDPOINT,
    RaClient,
    _SameOriginHttpsRedirectHandler,
    urlopen,
)
from ingestion.runner import RequestBudget, ResponseBudget, ResponseBudgetExhausted


class Response:
    def __init__(self, *, status=200, body=b'{"data": {}}'):
        self.status = status
        self.body = body
        self.headers = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self, size=-1):
        return self.body if size < 0 else self.body[:size]


class RaClientPacingTests(SimpleTestCase):
    def test_transport_rejects_unconfigured_urls_and_cross_origin_redirects(self):
        with self.assertRaises(URLError):
            urlopen(Request("http://169.254.169.254/latest/meta-data/"), timeout=1)

        handler = _SameOriginHttpsRedirectHandler()
        with self.assertRaises(HTTPError) as raised:
            handler.redirect_request(
                Request(GRAPHQL_ENDPOINT, data=b"{}", method="POST"),
                BytesIO(b"redirect"),
                302,
                "Found",
                {},
                "http://169.254.169.254/latest/meta-data/",
            )
        self.assertEqual(raised.exception.code, 502)

    def test_transport_rejects_an_oversized_response_without_retrying(self):
        client = RaClient(max_attempts=3, inter_request_delay_seconds=0, delay=Mock())
        response = Response(body=b"x" * 65)

        with (
            patch("ingestion.client.MAX_RESPONSE_BYTES", 64),
            patch("ingestion.client.urlopen", return_value=response) as opener,
        ):
            result = client.fetch_page(
                SimpleNamespace(area_ref="8"),
                date(2026, 7, 31),
                date(2026, 8, 7),
                1,
                20,
            )

        self.assertIsNone(result.status_code)
        self.assertIn("exceeds 64 bytes", result.error)
        opener.assert_called_once()

    def test_inter_page_delay_runs_n_minus_one_times(self):
        delay = Mock()
        client = RaClient(
            inter_request_delay_seconds=0,
            delay=delay,
        )
        seed = SimpleNamespace(area_ref="8")

        with patch(
            "ingestion.client.urlopen",
            side_effect=[Response(), Response(), Response()],
        ):
            for page_number in (1, 2, 3):
                client.fetch_page(
                    seed,
                    date(2026, 7, 31),
                    date(2026, 8, 7),
                    page_number,
                    20,
                )

        self.assertListEqual(delay.call_args_list, [call(0), call(0)])

    def test_retry_attempts_consume_shared_request_budget(self):
        budget = RequestBudget(limit=10)
        client = RaClient(
            max_attempts=3,
            inter_request_delay_seconds=0,
            delay=Mock(),
            before_attempt=budget.consume,
        )
        retryable = lambda: HTTPError(
            "https://ra.co/graphql",
            500,
            "synthetic retryable response",
            {},
            BytesIO(b"retry"),
        )

        with patch(
            "ingestion.client.urlopen",
            side_effect=[retryable(), retryable(), Response()],
        ):
            result = client.fetch_page(
                SimpleNamespace(area_ref="8"),
                date(2026, 7, 31),
                date(2026, 8, 7),
                1,
                20,
            )

        self.assertEqual(result.status_code, 200)
        self.assertEqual(budget.used, 3)
        self.assertEqual(budget.remaining, 7)

    def test_archived_response_budget_counts_encoded_bytes(self):
        budget = ResponseBudget(limit=4)
        budget.consume("é")
        budget.consume("ab")

        self.assertEqual(budget.used, 4)
        with self.assertRaises(ResponseBudgetExhausted):
            budget.consume("x")
