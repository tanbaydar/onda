from datetime import date
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock, call, patch
from urllib.error import HTTPError

from django.test import SimpleTestCase

from ingestion.client import RaClient
from ingestion.runner import RequestBudget


class Response:
    def __init__(self, *, status=200, body=b'{"data": {}}'):
        self.status = status
        self.body = body
        self.headers = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return self.body


class RaClientPacingTests(SimpleTestCase):
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
