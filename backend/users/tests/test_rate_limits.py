import json

from django.test import Client, TestCase, override_settings

from users.models import RequestThrottle, User


TEST_LIMITS = {
    "register": {"limit": 2, "window_seconds": 300},
    "login": {"limit": 2, "window_seconds": 300},
    "login_account": {"limit": 20, "window_seconds": 300},
    "verification_request_account": {"limit": 2, "window_seconds": 300},
    "password_reset_request": {"limit": 2, "window_seconds": 300},
    "password_reset_request_account": {"limit": 2, "window_seconds": 300},
    "password_reset_confirm": {"limit": 2, "window_seconds": 300},
    "password_reset_confirm_account": {"limit": 2, "window_seconds": 300},
    "avatar_upload_account": {"limit": 2, "window_seconds": 300},
}


@override_settings(ONDA_AUTH_RATE_LIMITS=TEST_LIMITS)
class AuthenticationRateLimitTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="rate-limit@example.test",
            password="A-real-password-123!",
            username="rate.limit",
            display_name="Rate Limit",
            is_private=False,
        )
        self.client = Client(enforce_csrf_checks=True, REMOTE_ADDR="203.0.113.8")
        self.client.get("/api/auth/session/")

    def post_login(self, password):
        return self.client.post(
            "/api/auth/login/",
            data=json.dumps({"email": self.user.email, "password": password}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=self.client.cookies["csrftoken"].value,
        )

    def test_login_attempts_are_limited_with_retry_metadata(self):
        self.assertEqual(self.post_login("wrong-password").status_code, 401)
        self.assertEqual(self.post_login("wrong-password").status_code, 401)

        limited = self.post_login("A-real-password-123!")

        self.assertEqual(limited.status_code, 429)
        self.assertGreater(int(limited["Retry-After"]), 0)
        self.assertEqual(limited["Cache-Control"], "no-store")

    def test_client_address_is_hashed_before_storage(self):
        self.post_login("wrong-password")

        record = RequestThrottle.objects.get(scope="login")
        self.assertEqual(len(record.key_hash), 64)
        self.assertNotIn("203.0.113.8", record.key_hash)

    def test_login_is_also_limited_by_normalized_account_identifier(self):
        with override_settings(
            ONDA_AUTH_RATE_LIMITS={
                **TEST_LIMITS,
                "login": {"limit": 20, "window_seconds": 300},
                "login_account": {"limit": 2, "window_seconds": 300},
            }
        ):
            first = Client(enforce_csrf_checks=True, REMOTE_ADDR="203.0.113.9")
            second = Client(enforce_csrf_checks=True, REMOTE_ADDR="203.0.113.10")
            third = Client(enforce_csrf_checks=True, REMOTE_ADDR="203.0.113.11")
            for client in (first, second, third):
                client.get("/api/auth/session/")

            def attempt(client, identifier):
                return client.post(
                    "/api/auth/login/",
                    data=json.dumps(
                        {"email": identifier, "password": "wrong-password"}
                    ),
                    content_type="application/json",
                    HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
                )

            self.assertEqual(attempt(first, "RATE-LIMIT@example.test").status_code, 401)
            self.assertEqual(attempt(second, "rate-limit@example.test").status_code, 401)
            self.assertEqual(attempt(third, "rate-limit@example.test").status_code, 429)
