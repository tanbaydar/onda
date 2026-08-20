import json
import os
import subprocess
import sys
from pathlib import Path
from unittest import TestCase


BASE_DIR = Path(__file__).resolve().parents[2]


class EmailSettingsTests(TestCase):
    def test_smtp_environment_is_mapped_to_django_settings(self):
        env = os.environ.copy()
        env.update(
            {
                "DJANGO_SECRET_KEY": "email-settings-test-key",
                "DJANGO_EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend",
                "DJANGO_DEFAULT_FROM_EMAIL": "Onda <noreply@example.com>",
                "DJANGO_EMAIL_HOST": "smtp.example.com",
                "DJANGO_EMAIL_PORT": "587",
                "DJANGO_EMAIL_HOST_USER": "smtp-user",
                "DJANGO_EMAIL_HOST_PASSWORD": "smtp-password",
                "DJANGO_EMAIL_USE_TLS": "true",
                "DJANGO_EMAIL_USE_SSL": "false",
                "DJANGO_EMAIL_TIMEOUT": "15",
            }
        )
        script = """
import json
from config import settings
print(json.dumps({
    'backend': settings.EMAIL_BACKEND,
    'from_email': settings.DEFAULT_FROM_EMAIL,
    'host': settings.EMAIL_HOST,
    'port': settings.EMAIL_PORT,
    'user': settings.EMAIL_HOST_USER,
    'password': settings.EMAIL_HOST_PASSWORD,
    'tls': settings.EMAIL_USE_TLS,
    'ssl': settings.EMAIL_USE_SSL,
    'timeout': settings.EMAIL_TIMEOUT,
}))
"""

        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=BASE_DIR,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(
            json.loads(result.stdout),
            {
                "backend": "django.core.mail.backends.smtp.EmailBackend",
                "from_email": "Onda <noreply@example.com>",
                "host": "smtp.example.com",
                "port": 587,
                "user": "smtp-user",
                "password": "smtp-password",
                "tls": True,
                "ssl": False,
                "timeout": 15,
            },
        )
