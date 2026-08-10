"""Production settings for the Docker Compose deployment."""

import os

from .settings import *  # noqa: F403


DEBUG = False

DANCED_DOMAIN = os.environ["DANCED_DOMAIN"]
ALLOWED_HOSTS = [DANCED_DOMAIN, "localhost", "127.0.0.1"]
CSRF_TRUSTED_ORIGINS = [f"https://{DANCED_DOMAIN}"]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31_536_000
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
