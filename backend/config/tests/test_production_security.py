import json
import os
import subprocess
import sys
from pathlib import Path
from unittest import TestCase


BASE_DIR = Path(__file__).resolve().parents[2]


class ProductionSecuritySettingsTests(TestCase):
    def test_production_defaults_fail_closed(self):
        env = os.environ.copy()
        env.update(
            {
                "DJANGO_SECRET_KEY": "production-security-test-key",
                "ONDA_DOMAIN": "onda.example.test",
                "ONDA_DB_NAME": "onda",
                "ONDA_DB_USER": "onda_app",
                "ONDA_DB_PASSWORD": "a-secure-test-password",
                "ONDA_DB_HOST": "db",
                "DJANGO_EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend",
                "DJANGO_DEFAULT_FROM_EMAIL": "noreply@onda.example.test",
                "DJANGO_EMAIL_HOST": "smtp.example.test",
                "DJANGO_EMAIL_HOST_USER": "smtp-user",
                "DJANGO_EMAIL_HOST_PASSWORD": "smtp-password",
                "DJANGO_EMAIL_USE_TLS": "true",
                "DJANGO_EMAIL_USE_SSL": "false",
            }
        )
        env.pop("EMAIL_VERIFICATION_ENFORCED", None)
        script = """
import json
from config import settings_production as settings
print(json.dumps({
    'allowed_hosts': settings.ALLOWED_HOSTS,
    'admin_enabled': settings.ADMIN_ENABLED,
    'email_verification_enforced': settings.EMAIL_VERIFICATION_ENFORCED,
    'referrer_policy': settings.SECURE_REFERRER_POLICY,
    'trust_x_real_ip': settings.ONDA_TRUST_X_REAL_IP,
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
                "allowed_hosts": ["onda.example.test"],
                "admin_enabled": False,
                "email_verification_enforced": True,
                "referrer_policy": "no-referrer",
                "trust_x_real_ip": True,
            },
        )

    def test_production_rejects_log_exposing_email_backend(self):
        env = os.environ.copy()
        env.update(
            {
                "DJANGO_SECRET_KEY": "production-security-test-key",
                "ONDA_DOMAIN": "onda.example.test",
                "ONDA_DB_NAME": "onda",
                "ONDA_DB_USER": "onda_app",
                "ONDA_DB_PASSWORD": "a-secure-test-password",
                "ONDA_DB_HOST": "db",
                "EMAIL_VERIFICATION_ENFORCED": "false",
                "DJANGO_EMAIL_BACKEND": "django.core.mail.backends.console.EmailBackend",
            }
        )

        result = subprocess.run(
            [sys.executable, "-c", "from config import settings_production"],
            cwd=BASE_DIR,
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("account recovery requires a real email backend", result.stderr)

    def test_production_rejects_wildcard_host_and_ambiguous_boolean(self):
        base_env = os.environ.copy()
        base_env.update(
            {
                "DJANGO_SECRET_KEY": "production-security-test-key",
                "ONDA_DB_NAME": "onda",
                "ONDA_DB_USER": "onda_app",
                "ONDA_DB_PASSWORD": "a-secure-test-password",
                "ONDA_DB_HOST": "db",
                "EMAIL_VERIFICATION_ENFORCED": "false",
            }
        )

        wildcard = subprocess.run(
            [sys.executable, "-c", "from config import settings_production"],
            cwd=BASE_DIR,
            env={**base_env, "ONDA_DOMAIN": "*"},
            capture_output=True,
            text=True,
        )
        ambiguous = subprocess.run(
            [sys.executable, "-c", "from config import settings_production"],
            cwd=BASE_DIR,
            env={
                **base_env,
                "ONDA_DOMAIN": "onda.example.test",
                "EMAIL_VERIFICATION_ENFORCED": "tru",
            },
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(wildcard.returncode, 0)
        self.assertIn("without a scheme, port, or wildcard", wildcard.stderr)
        self.assertNotEqual(ambiguous.returncode, 0)
        self.assertIn("must be exactly true or false", ambiguous.stderr)

    def test_production_rejects_root_or_weak_database_credentials(self):
        base_env = os.environ.copy()
        base_env.update(
            {
                "DJANGO_SECRET_KEY": "production-security-test-key",
                "ONDA_DOMAIN": "onda.example.test",
                "ONDA_DB_NAME": "onda",
                "ONDA_DB_HOST": "db",
                "EMAIL_VERIFICATION_ENFORCED": "false",
            }
        )

        root_user = subprocess.run(
            [sys.executable, "-c", "from config import settings_production"],
            cwd=BASE_DIR,
            env={
                **base_env,
                "ONDA_DB_USER": "root",
                "ONDA_DB_PASSWORD": "a-secure-test-password",
            },
            capture_output=True,
            text=True,
        )
        weak_password = subprocess.run(
            [sys.executable, "-c", "from config import settings_production"],
            cwd=BASE_DIR,
            env={
                **base_env,
                "ONDA_DB_USER": "onda_app",
                "ONDA_DB_PASSWORD": "short",
            },
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(root_user.returncode, 0)
        self.assertIn("dedicated application account", root_user.stderr)
        self.assertNotEqual(weak_password.returncode, 0)
        self.assertIn("at least 16 characters", weak_password.stderr)

    def test_production_rejects_a_display_name_wrapped_local_sender(self):
        env = os.environ.copy()
        env.update(
            {
                "DJANGO_SECRET_KEY": "production-security-test-key",
                "ONDA_DOMAIN": "onda.example.test",
                "ONDA_DB_NAME": "onda",
                "ONDA_DB_USER": "onda_app",
                "ONDA_DB_PASSWORD": "a-secure-test-password",
                "ONDA_DB_HOST": "db",
                "DJANGO_EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend",
                "DJANGO_DEFAULT_FROM_EMAIL": "Onda <noreply@onda.local>",
                "DJANGO_EMAIL_HOST": "smtp.example.test",
                "DJANGO_EMAIL_HOST_USER": "smtp-user",
                "DJANGO_EMAIL_HOST_PASSWORD": "smtp-password",
                "DJANGO_EMAIL_USE_TLS": "true",
                "DJANGO_EMAIL_USE_SSL": "false",
            }
        )

        result = subprocess.run(
            [sys.executable, "-c", "from config import settings_production"],
            cwd=BASE_DIR,
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DJANGO_DEFAULT_FROM_EMAIL (public)", result.stderr)
