from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, override_settings


POSTMARK_SETTINGS = {
    "EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend",
    "DEFAULT_FROM_EMAIL": "Onda <noreply@onda-platform.dev>",
    "EMAIL_HOST": "smtp.postmarkapp.com",
    "EMAIL_PORT": 587,
    "EMAIL_HOST_USER": "postmark-user",
    "EMAIL_HOST_PASSWORD": "postmark-password",
    "EMAIL_USE_TLS": True,
    "EMAIL_USE_SSL": False,
}


class CheckPostmarkEmailCommandTests(SimpleTestCase):
    @override_settings(**POSTMARK_SETTINGS)
    def test_accepts_ready_postmark_configuration_without_connecting(self):
        stdout = StringIO()

        call_command("check_postmark_email", stdout=stdout)

        self.assertIn("ready for a live delivery test", stdout.getvalue())

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend",
        DEFAULT_FROM_EMAIL="noreply@example.invalid",
        EMAIL_HOST="localhost",
        EMAIL_PORT=25,
        EMAIL_HOST_USER="",
        EMAIL_HOST_PASSWORD="",
        EMAIL_USE_TLS=False,
        EMAIL_USE_SSL=False,
    )
    def test_reports_all_unsafe_defaults_without_exposing_credentials(self):
        with self.assertRaises(CommandError) as caught:
            call_command("check_postmark_email")

        message = str(caught.exception)
        self.assertIn("DJANGO_EMAIL_BACKEND", message)
        self.assertIn("DJANGO_EMAIL_HOST", message)
        self.assertIn("DJANGO_EMAIL_HOST_USER", message)
        self.assertIn("DJANGO_EMAIL_HOST_PASSWORD", message)
        self.assertIn("verified sending domain", message)

    @override_settings(**{**POSTMARK_SETTINGS, "EMAIL_HOST_PASSWORD": "secret-value"})
    def test_success_output_does_not_expose_credentials(self):
        stdout = StringIO()

        call_command("check_postmark_email", stdout=stdout)

        self.assertNotIn("secret-value", stdout.getvalue())
