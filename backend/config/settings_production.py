"""Production settings for the Docker Compose deployment."""

import os

from .settings import *  # noqa: F403


DEBUG = False

ONDA_DOMAIN = os.environ["ONDA_DOMAIN"]
ALLOWED_HOSTS = [ONDA_DOMAIN, "localhost", "127.0.0.1"]
CSRF_TRUSTED_ORIGINS = [f"https://{ONDA_DOMAIN}"]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31_536_000
# These policies must remain explicit deployment choices: includeSubDomains
# affects every hostname below ONDA_DOMAIN, and preload is intentionally
# difficult to reverse once the domain is submitted to browser preload lists.
SECURE_HSTS_INCLUDE_SUBDOMAINS = (
    os.environ.get("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", "false").lower() == "true"
)
SECURE_HSTS_PRELOAD = (
    os.environ.get("DJANGO_SECURE_HSTS_PRELOAD", "false").lower() == "true"
)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
