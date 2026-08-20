from email.utils import parseaddr

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


SMTP_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
POSTMARK_SMTP_HOST = "smtp.postmarkapp.com"
POSTMARK_STARTTLS_PORTS = {25, 587, 2525}


class Command(BaseCommand):
    help = "Validate the deployed Postmark SMTP configuration without sending email."

    def handle(self, *args, **options):
        errors = []

        if settings.EMAIL_BACKEND != SMTP_BACKEND:
            errors.append(f"DJANGO_EMAIL_BACKEND must be {SMTP_BACKEND}")
        if settings.EMAIL_HOST.lower() != POSTMARK_SMTP_HOST:
            errors.append(f"DJANGO_EMAIL_HOST must be {POSTMARK_SMTP_HOST}")
        if settings.EMAIL_PORT not in POSTMARK_STARTTLS_PORTS:
            errors.append("DJANGO_EMAIL_PORT must be 25, 587, or 2525 for Postmark STARTTLS")
        if not settings.EMAIL_USE_TLS:
            errors.append("DJANGO_EMAIL_USE_TLS must be true")
        if settings.EMAIL_USE_SSL:
            errors.append("DJANGO_EMAIL_USE_SSL must be false when STARTTLS is enabled")
        if not settings.EMAIL_HOST_USER:
            errors.append("DJANGO_EMAIL_HOST_USER must contain the Postmark SMTP credential")
        if not settings.EMAIL_HOST_PASSWORD:
            errors.append("DJANGO_EMAIL_HOST_PASSWORD must contain the Postmark SMTP credential")

        _, sender_address = parseaddr(settings.DEFAULT_FROM_EMAIL)
        sender_domain = sender_address.rpartition("@")[2].lower()
        if not sender_address or not sender_domain:
            errors.append("DJANGO_DEFAULT_FROM_EMAIL must contain a valid email address")
        elif sender_domain.endswith(
            (
                ".invalid",
                ".local",
                ".localhost",
                ".test",
                ".example",
                ".example.com",
                ".example.net",
                ".example.org",
            )
        ) or sender_domain in {
            "localhost",
            "example.com",
            "example.net",
            "example.org",
        }:
            errors.append("DJANGO_DEFAULT_FROM_EMAIL must use a verified sending domain")

        if errors:
            details = "\n".join(f"- {error}" for error in errors)
            raise CommandError(f"Postmark email configuration is not ready:\n{details}")

        self.stdout.write(
            self.style.SUCCESS(
                "Postmark email configuration is ready for a live delivery test."
            )
        )
