"""Production settings for the Docker Compose deployment."""

import os
import re
from email.utils import parseaddr

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.validators import validate_email

from .settings import *  # noqa: F403


DEBUG = False

ONDA_DOMAIN = os.environ["ONDA_DOMAIN"]
domain_label = r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
if (
    ONDA_DOMAIN != ONDA_DOMAIN.strip().lower()
    or len(ONDA_DOMAIN) > 253
    or re.fullmatch(rf"(?:{domain_label}\.)+{domain_label}", ONDA_DOMAIN) is None
):
    raise ImproperlyConfigured(
        "ONDA_DOMAIN must be one lowercase DNS name without a scheme, port, or wildcard."
    )
ALLOWED_HOSTS = [ONDA_DOMAIN]
CSRF_TRUSTED_ORIGINS = [f"https://{ONDA_DOMAIN}"]


def _strict_boolean(name, default):
    value = os.environ.get(name, default).lower()
    if value not in {"true", "false"}:
        raise ImproperlyConfigured(f"{name} must be exactly true or false.")
    return value == "true"


# Production fails closed when the environment omits this flag. An operator may
# still disable it deliberately for a private, non-user-facing deployment.
EMAIL_VERIFICATION_ENFORCED = _strict_boolean("EMAIL_VERIFICATION_ENFORCED", "true")
EMAIL_USE_TLS = _strict_boolean("DJANGO_EMAIL_USE_TLS", "false")
EMAIL_USE_SSL = _strict_boolean("DJANGO_EMAIL_USE_SSL", "false")
ADMIN_ENABLED = False

database = DATABASES["default"]  # noqa: F405
missing_database_settings = [
    name
    for name, value in (
        ("ONDA_DB_NAME", database["NAME"]),
        ("ONDA_DB_USER", database["USER"]),
        ("ONDA_DB_PASSWORD", database["PASSWORD"]),
        ("ONDA_DB_HOST", database["HOST"]),
    )
    if not str(value).strip()
]
if missing_database_settings:
    raise ImproperlyConfigured(
        "Production database configuration is incomplete: "
        + ", ".join(missing_database_settings)
    )
if str(database["USER"]).lower() == "root":
    raise ImproperlyConfigured(
        "ONDA_DB_USER must be a dedicated application account, not root."
    )
if len(str(database["PASSWORD"])) < 16:
    raise ImproperlyConfigured(
        "ONDA_DB_PASSWORD must contain at least 16 characters."
    )

unsafe_email_backends = {
    "django.core.mail.backends.console.EmailBackend",
    "django.core.mail.backends.dummy.EmailBackend",
    "django.core.mail.backends.locmem.EmailBackend",
}
if EMAIL_BACKEND in unsafe_email_backends:  # noqa: F405
    raise ImproperlyConfigured(
        "Production account recovery requires a real email backend; "
        "console, dummy, and in-memory delivery are not allowed."
    )
if EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend":  # noqa: F405
    missing_email_settings = [
        name
        for name, value in (
            ("DJANGO_EMAIL_HOST", EMAIL_HOST),  # noqa: F405
            ("DJANGO_EMAIL_HOST_USER", EMAIL_HOST_USER),  # noqa: F405
            ("DJANGO_EMAIL_HOST_PASSWORD", EMAIL_HOST_PASSWORD),  # noqa: F405
            ("DJANGO_DEFAULT_FROM_EMAIL", DEFAULT_FROM_EMAIL),  # noqa: F405
        )
        if not value
    ]
    if EMAIL_HOST in {"localhost", "127.0.0.1", "::1"}:  # noqa: F405
        missing_email_settings.append("DJANGO_EMAIL_HOST (non-local)")
    _, sender_address = parseaddr(str(DEFAULT_FROM_EMAIL))  # noqa: F405
    try:
        validate_email(sender_address)
    except ValidationError:
        missing_email_settings.append("DJANGO_DEFAULT_FROM_EMAIL (valid address)")
    sender_domain = sender_address.rpartition("@")[2].lower()
    if sender_domain == "localhost" or sender_domain.endswith(".local"):
        missing_email_settings.append("DJANGO_DEFAULT_FROM_EMAIL (public)")
    if EMAIL_USE_TLS == EMAIL_USE_SSL:  # noqa: F405
        missing_email_settings.append("exactly one of TLS or SSL")
    if missing_email_settings:
        raise ImproperlyConfigured(
            "Secure production SMTP is incomplete: "
            + ", ".join(missing_email_settings)
        )

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31_536_000
# These policies must remain explicit deployment choices: includeSubDomains
# affects every hostname below ONDA_DOMAIN, and preload is intentionally
# difficult to reverse once the domain is submitted to browser preload lists.
SECURE_HSTS_INCLUDE_SUBDOMAINS = _strict_boolean(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", "false"
)
SECURE_HSTS_PRELOAD = _strict_boolean("DJANGO_SECURE_HSTS_PRELOAD", "false")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "no-referrer"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

# Only the directly connected Caddy container may supply this value. Caddy
# overwrites the header before forwarding, so clients cannot spoof their key for
# application-level authentication throttles.
ONDA_TRUST_X_REAL_IP = True
