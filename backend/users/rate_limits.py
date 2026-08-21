import ipaddress
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.signing import salted_hmac
from django.db import transaction
from django.utils.timezone import now as timezone_now

from .models import RequestThrottle


class RateLimitExceeded(Exception):
    def __init__(self, retry_after):
        self.retry_after = retry_after
        super().__init__("Too many requests.")


def client_address(request):
    value = request.META.get("REMOTE_ADDR", "")
    if settings.ONDA_TRUST_X_REAL_IP:
        value = request.META.get("HTTP_X_REAL_IP", value)
    try:
        return ipaddress.ip_address(value).compressed
    except ValueError:
        return "unknown"


def _key_hash(scope, key):
    return salted_hmac(
        "onda.request-throttle",
        f"{scope}:{key}",
        algorithm="sha256",
    ).hexdigest()


@transaction.atomic
def consume_rate_limit(*, scope, key, limit, window_seconds):
    if limit < 1 or window_seconds < 1:
        raise ValueError("rate-limit values must be positive")

    now = timezone_now()
    record, created = RequestThrottle.objects.select_for_update().get_or_create(
        scope=scope,
        key_hash=_key_hash(scope, key),
        defaults={"window_started_at": now, "count": 1},
    )
    if not created:
        window_end = record.window_started_at + timedelta(seconds=window_seconds)
        if now >= window_end:
            record.window_started_at = now
            record.count = 1
            record.save(update_fields=("window_started_at", "count", "updated_at"))
        elif record.count >= limit:
            retry_after = max(1, int((window_end - now).total_seconds()) + 1)
            raise RateLimitExceeded(retry_after)
        else:
            record.count += 1
            record.save(update_fields=("count", "updated_at"))

    # Keep the table bounded without adding a separate always-on worker.
    if secrets.randbelow(100) == 0:
        RequestThrottle.objects.filter(
            updated_at__lt=now - timedelta(days=2)
        ).delete()
