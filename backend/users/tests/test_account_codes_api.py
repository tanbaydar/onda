import json
import re
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core import mail
from django.db import DatabaseError, connection
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from users.auth_services import AccountActionVerificationRequired, verify_email
from users.models import AccountCode, AccountCodePurpose
from users.services import follow_user


PASSWORD = "A-real-password-123!"


class AccountCodeApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="codes@example.com",
            password=PASSWORD,
            username="code.user",
            display_name="Code User",
            is_private=False,
        )
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.user)
        self.client.get("/api/auth/session/")

    def post(self, path, payload=None, *, client=None):
        client = client or self.client
        token = client.cookies["csrftoken"].value
        return client.post(
            path,
            data=json.dumps(payload or {}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )

    def sent_code(self):
        match = re.search(r"\b(\d{6})\b", mail.outbox[-1].body)
        self.assertIsNotNone(match)
        return match.group(1)

    def test_verification_request_sends_six_digit_code_and_stores_only_hash(self):
        response = self.post("/api/auth/verification/request/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"sent": True, "cooldown_seconds": 60})
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Your Onda App verification code")
        self.assertIn("Your Onda App email verification code is", mail.outbox[0].body)
        code = self.sent_code()
        record = AccountCode.objects.get(
            user=self.user, purpose=AccountCodePurpose.EMAIL_VERIFICATION
        )
        self.assertNotEqual(record.code_hash, code)
        self.assertEqual(len(record.code_hash), 64)

    def test_physical_user_delete_cascades_account_codes(self):
        self.post("/api/auth/verification/request/")
        user_id = self.user.id

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM ONDA_USER WHERE id = %s", (user_id,))

        self.assertFalse(AccountCode.objects.filter(user_id=user_id).exists())

    def test_verification_code_expires_after_fifteen_minutes(self):
        start = timezone.now()
        with patch("users.auth_services.timezone_now", return_value=start):
            self.post("/api/auth/verification/request/")
            code = self.sent_code()
        with patch(
            "users.auth_services.timezone_now",
            return_value=start + timedelta(minutes=15),
        ):
            response = self.post(
                "/api/auth/verification/confirm/", {"code": code}
            )

        self.assertEqual(response.status_code, 400)
        self.assertIn("expired", response.json()["errors"]["code"][0].lower())

    def test_five_failed_attempts_lock_the_code(self):
        self.post("/api/auth/verification/request/")
        correct_code = self.sent_code()
        incorrect_code = "000000" if correct_code != "000000" else "000001"

        for attempt in range(5):
            response = self.post(
                "/api/auth/verification/confirm/", {"code": incorrect_code}
            )
            self.assertEqual(response.status_code, 400, attempt)
        response = self.post(
            "/api/auth/verification/confirm/", {"code": correct_code}
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("too many", response.json()["errors"]["code"][0].lower())

    def test_resend_has_sixty_second_cooldown_then_rotates_code(self):
        start = timezone.now()
        with patch("users.auth_services.timezone_now", return_value=start):
            self.assertEqual(
                self.post("/api/auth/verification/request/").status_code, 200
            )
            first_code = self.sent_code()
        with patch(
            "users.auth_services.timezone_now",
            return_value=start + timedelta(seconds=59),
        ):
            cooldown = self.post("/api/auth/verification/request/")
        with patch(
            "users.auth_services.timezone_now",
            return_value=start + timedelta(seconds=60),
        ):
            resent = self.post("/api/auth/verification/request/")
            second_code = self.sent_code()
            old_code = self.post(
                "/api/auth/verification/confirm/", {"code": first_code}
            )

        self.assertEqual(cooldown.status_code, 429)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(resent.status_code, 200)
        self.assertNotEqual(first_code, second_code)
        self.assertEqual(old_code.status_code, 400)

    def test_valid_code_verifies_user_and_cannot_be_reused(self):
        self.post("/api/auth/verification/request/")
        code = self.sent_code()

        response = self.post("/api/auth/verification/confirm/", {"code": code})
        reused = self.post("/api/auth/verification/confirm/", {"code": code})

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"verified": True})
        self.assertIsNotNone(self.user.email_verified_at)
        self.assertEqual(reused.status_code, 400)

    def test_verification_flag_failure_rolls_back_code_consumption(self):
        self.post("/api/auth/verification/request/")
        code = self.sent_code()

        with patch("users.models.User.save", side_effect=DatabaseError("forced")):
            with self.assertRaises(DatabaseError):
                verify_email(user=self.user, code=code)

        record = AccountCode.objects.get(
            user=self.user,
            purpose=AccountCodePurpose.EMAIL_VERIFICATION,
        )
        self.user.refresh_from_db()
        self.assertIsNone(record.consumed_at)
        self.assertIsNone(self.user.email_verified_at)

    def test_verification_endpoints_require_the_users_own_session(self):
        guest = Client(enforce_csrf_checks=True)
        guest.get("/api/auth/session/")

        response = self.post(
            "/api/auth/verification/request/", client=guest
        )

        self.assertEqual(response.status_code, 401)


class VerificationGateTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="gate@example.com",
            password=PASSWORD,
            username="gate.user",
            display_name="Gate User",
            is_private=False,
        )
        self.target = get_user_model().objects.create_user(
            email="target@example.com",
            password=PASSWORD,
            username="gate.target",
            display_name="Gate Target",
            is_private=False,
        )
        self.client = Client()
        self.client.force_login(self.user)

    @override_settings(EMAIL_VERIFICATION_ENFORCED=False)
    def test_flag_off_preserves_unverified_account_action_behavior(self):
        response = self.client.post(f"/api/users/{self.target.id}/follow/")

        self.assertEqual(response.status_code, 201)

    @override_settings(EMAIL_VERIFICATION_ENFORCED=True)
    def test_flag_on_rejects_unverified_account_action(self):
        response = self.client.post(f"/api/users/{self.target.id}/follow/")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json(),
            {
                "errors": {
                    "verification": [
                        "Email verification is required for account actions."
                    ]
                }
            },
        )

    @override_settings(EMAIL_VERIFICATION_ENFORCED=True)
    def test_flag_on_registration_still_signs_in_before_gating_actions(self):
        client = Client(enforce_csrf_checks=True)
        client.get("/api/auth/session/")
        token = client.cookies["csrftoken"].value
        response = client.post(
            "/api/auth/register/",
            data=json.dumps(
                {
                    "email": "new.unverified@example.com",
                    "password": PASSWORD,
                    "username": "new.unverified",
                    "display_name": "New Unverified",
                    "is_private": False,
                }
            ),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )
        action = client.post(f"/api/users/{self.target.id}/follow/")

        self.assertEqual(response.status_code, 201)
        self.assertTrue(client.session.get("_auth_user_id"))
        self.assertEqual(action.status_code, 403)

    @override_settings(EMAIL_VERIFICATION_ENFORCED=True)
    def test_service_boundary_rejects_unverified_action_outside_a_view(self):
        with self.assertRaises(AccountActionVerificationRequired):
            follow_user(follower_id=self.user.id, followee_id=self.target.id)

    @override_settings(EMAIL_VERIFICATION_ENFORCED=True)
    def test_verified_account_keeps_full_capabilities(self):
        self.user.email_verified_at = timezone.now()
        self.user.save(update_fields=("email_verified_at",))

        response = self.client.post(f"/api/users/{self.target.id}/follow/")

        self.assertEqual(response.status_code, 201)


class PasswordResetApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="reset@example.com",
            password=PASSWORD,
            username="reset.user",
            display_name="Reset User",
            is_private=False,
        )

    def post(self, client, path, payload):
        client.get("/api/auth/session/")
        token = client.cookies["csrftoken"].value
        return client.post(
            path,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )

    def sent_code(self):
        return re.search(r"\b(\d{6})\b", mail.outbox[-1].body).group(1)

    def test_reset_request_does_not_enumerate_accounts(self):
        existing_client = Client(enforce_csrf_checks=True)
        missing_client = Client(enforce_csrf_checks=True)

        existing = self.post(
            existing_client,
            "/api/auth/password-reset/request/",
            {"email": "RESET@example.com"},
        )
        missing = self.post(
            missing_client,
            "/api/auth/password-reset/request/",
            {"email": "missing@example.com"},
        )

        self.assertEqual(existing.status_code, 200)
        self.assertEqual(missing.status_code, 200)
        self.assertEqual(existing.json(), {"accepted": True})
        self.assertEqual(missing.json(), existing.json())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Your Onda App password reset code")
        self.assertIn("Your Onda App password reset code is", mail.outbox[0].body)

    def test_reset_code_expiry_attempt_limit_and_cooldown_match_verification(self):
        client = Client(enforce_csrf_checks=True)
        start = timezone.now()
        with patch("users.auth_services.timezone_now", return_value=start):
            self.post(
                client,
                "/api/auth/password-reset/request/",
                {"email": self.user.email},
            )
            code = self.sent_code()
            second = self.post(
                client,
                "/api/auth/password-reset/request/",
                {"email": self.user.email},
            )
        self.assertEqual(second.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

        with patch(
            "users.auth_services.timezone_now",
            return_value=start + timedelta(minutes=16),
        ):
            expired = self.post(
                client,
                "/api/auth/password-reset/confirm/",
                {"email": self.user.email, "code": code, "password": "New-real-password-456!"},
            )
        self.assertEqual(expired.status_code, 400)

    def test_successful_reset_changes_password_and_invalidates_all_sessions(self):
        first = Client()
        second = Client()
        first.force_login(self.user)
        second.force_login(self.user)
        session_keys = {first.session.session_key, second.session.session_key}
        reset_client = Client(enforce_csrf_checks=True)
        self.post(
            reset_client,
            "/api/auth/password-reset/request/",
            {"email": self.user.email},
        )
        code = self.sent_code()

        response = self.post(
            reset_client,
            "/api/auth/password-reset/confirm/",
            {
                "email": self.user.email,
                "code": code,
                "password": "New-real-password-456!",
            },
        )

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"reset": True})
        self.assertTrue(self.user.check_password("New-real-password-456!"))
        self.assertFalse(Session.objects.filter(session_key__in=session_keys).exists())

    def test_invalid_reset_code_uses_field_keyed_error(self):
        client = Client(enforce_csrf_checks=True)

        response = self.post(
            client,
            "/api/auth/password-reset/confirm/",
            {
                "email": self.user.email,
                "code": "123456",
                "password": "New-real-password-456!",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("code", response.json()["errors"])

    def test_reset_confirmation_does_not_reveal_account_existence(self):
        existing_client = Client(enforce_csrf_checks=True)
        missing_client = Client(enforce_csrf_checks=True)
        payload = {
            "code": "123456",
            "password": "New-real-password-456!",
        }

        existing = self.post(
            existing_client,
            "/api/auth/password-reset/confirm/",
            {**payload, "email": self.user.email},
        )
        missing = self.post(
            missing_client,
            "/api/auth/password-reset/confirm/",
            {**payload, "email": "missing@example.com"},
        )

        self.assertEqual(existing.status_code, 400)
        self.assertEqual(missing.status_code, 400)
        self.assertEqual(existing.json(), missing.json())

    def test_reset_code_locks_after_five_wrong_attempts(self):
        client = Client(enforce_csrf_checks=True)
        self.post(
            client,
            "/api/auth/password-reset/request/",
            {"email": self.user.email},
        )
        correct_code = self.sent_code()
        incorrect_code = "000000" if correct_code != "000000" else "000001"
        payload = {
            "email": self.user.email,
            "password": "New-real-password-456!",
        }
        for _attempt in range(5):
            response = self.post(
                client,
                "/api/auth/password-reset/confirm/",
                {**payload, "code": incorrect_code},
            )
            self.assertEqual(response.status_code, 400)

        locked = self.post(
            client,
            "/api/auth/password-reset/confirm/",
            {**payload, "code": correct_code},
        )

        self.assertEqual(locked.status_code, 400)
        self.assertIn("too many", locked.json()["errors"]["code"][0].lower())
