import json
from datetime import UTC, datetime

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings

from catalog.models import City


class AuthApiContractTests(TestCase):
    valid_registration = {
        "email": "listener@example.com",
        "password": "A-real-password-123!",
        "username": "listener.one",
        "display_name": "Listener One",
        "is_private": False,
    }

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self._refresh_csrf()

    def _refresh_csrf(self):
        response = self.client.get("/api/auth/session/")
        self.csrf_token = self.client.cookies.get("csrftoken")
        return response

    def _post(self, path, payload):
        headers = {}
        csrf_token = self.client.cookies.get("csrftoken")
        if csrf_token is not None:
            headers["HTTP_X_CSRFTOKEN"] = csrf_token.value
        return self.client.post(
            path,
            data=json.dumps(payload),
            content_type="application/json",
            **headers,
        )

    def _register(self, **overrides):
        payload = {**self.valid_registration, **overrides}
        return self._post("/api/auth/register/", payload)

    def assert_field_error(self, response, field, message=None):
        self.assertEqual(response.status_code, 400)
        self.assertIn(field, response.json()["errors"])
        if message is not None:
            self.assertIn(message, response.json()["errors"][field])

    def test_session_bootstrap_sets_csrf_cookie_and_reports_guest(self):
        response = self._refresh_csrf()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"authenticated": False, "user": None},
        )
        self.assertIsNotNone(self.client.cookies.get("csrftoken"))

    def test_registration_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)

        response = client.post(
            "/api/auth/register/",
            data=json.dumps(self.valid_registration),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_registration_signs_in_and_returns_self_only_user_shape(self):
        response = self._register(
            email="Listener@Example.com",
            username="Listener.One",
            display_name="  Listener One  ",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "user": {
                    "id": response.json()["user"]["id"],
                    "email": "listener@example.com",
                    "username": "listener.one",
                    "display_name": "Listener One",
                    "avatar": None,
                    "is_private": False,
                }
            },
        )
        user = get_user_model().objects.get()
        self.assertEqual(user.username, "listener.one")
        self.assertEqual(user.display_name, "Listener One")
        self.assertIsNone(user.email_verified_at)
        self.assertTrue(self.client.session.get("_auth_user_id"))

    def test_username_rejects_fewer_than_three_characters(self):
        self.assert_field_error(self._register(username="ab"), "username")

    def test_username_rejects_more_than_thirty_characters(self):
        self.assert_field_error(self._register(username="a" * 31), "username")

    def test_username_rejects_characters_outside_allowed_set(self):
        self.assert_field_error(self._register(username="bad-name"), "username")

    def test_username_must_begin_with_letter_or_number(self):
        self.assert_field_error(self._register(username="_listener"), "username")

    def test_username_must_end_with_letter_or_number(self):
        self.assert_field_error(self._register(username="listener_"), "username")

    def test_username_rejects_consecutive_periods(self):
        self.assert_field_error(self._register(username="listener..one"), "username")

    def test_username_accepts_letters_numbers_underscores_and_periods(self):
        response = self._register(username="listener_1.test")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["user"]["username"], "listener_1.test")

    def test_username_uniqueness_is_case_insensitive(self):
        self.assertEqual(self._register(username="Listener.One").status_code, 201)
        self.client = Client(enforce_csrf_checks=True)
        self._refresh_csrf()

        response = self._register(
            email="other@example.com",
            username="LISTENER.ONE",
        )

        self.assert_field_error(response, "username", "This username is already taken.")

    def test_display_name_is_trimmed_and_accepts_fifty_characters(self):
        response = self._register(display_name=f"  {'x' * 50}  ")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["user"]["display_name"], "x" * 50)

    def test_display_name_rejects_empty_after_trimming(self):
        self.assert_field_error(self._register(display_name=" \t\n "), "display_name")

    def test_display_name_rejects_more_than_fifty_characters_after_trimming(self):
        self.assert_field_error(
            self._register(display_name=f"  {'x' * 51}  "),
            "display_name",
        )

    def test_duplicate_email_is_rejected_case_insensitively(self):
        self.assertEqual(self._register(email="Listener@Example.com").status_code, 201)
        self.client = Client(enforce_csrf_checks=True)
        self._refresh_csrf()

        response = self._register(
            email="LISTENER@example.COM",
            username="someone.else",
        )

        self.assert_field_error(
            response,
            "email",
            "An account with this email already exists.",
        )

    def test_privacy_choice_is_required_and_strictly_boolean(self):
        for value in ("missing", None, "false", 0):
            with self.subTest(value=value):
                payload = dict(self.valid_registration)
                if value == "missing":
                    payload.pop("is_private")
                else:
                    payload["is_private"] = value
                self.assert_field_error(
                    self._post("/api/auth/register/", payload),
                    "is_private",
                )

    def test_registration_requires_each_identity_field(self):
        for field in ("email", "password", "username", "display_name"):
            with self.subTest(field=field):
                payload = dict(self.valid_registration)
                payload.pop(field)
                self.assert_field_error(
                    self._post("/api/auth/register/", payload),
                    field,
                )

    def test_registration_preserves_required_display_name_and_privacy_contract(self):
        for field in ("display_name", "is_private"):
            with self.subTest(field=field):
                payload = dict(self.valid_registration)
                payload.pop(field)
                response = self._post("/api/auth/register/", payload)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(list(response.json()["errors"]), [field])

    def test_login_rejects_wrong_password_without_email_enumeration(self):
        self.assertEqual(self._register().status_code, 201)
        self._post("/api/auth/logout/", {})

        response = self._post(
            "/api/auth/login/",
            {"email": "listener@example.com", "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(),
            {"errors": {"credentials": ["That username or email and password don't match. Try again or reset your password."]}},
        )

    def test_login_accepts_username_case_insensitively_without_changing_email_login(self):
        self.assertEqual(self._register().status_code, 201)
        self._post("/api/auth/logout/", {})
        username_login = self._post(
            "/api/auth/login/",
            {"email": "LISTENER.ONE", "password": self.valid_registration["password"]},
        )
        self.assertEqual(username_login.status_code, 200)
        self.assertEqual(username_login.json()["user"]["email"], "listener@example.com")
        self._post("/api/auth/logout/", {})
        email_login = self._post(
            "/api/auth/login/",
            {"email": "LISTENER@EXAMPLE.COM", "password": self.valid_registration["password"]},
        )
        self.assertEqual(email_login.status_code, 200)

    def test_unknown_username_and_wrong_password_have_byte_identical_failures(self):
        self.assertEqual(self._register().status_code, 201)
        self._post("/api/auth/logout/", {})
        unknown = self._post(
            "/api/auth/login/",
            {"email": "unknown.listener", "password": "wrong-password"},
        )
        wrong_password = self._post(
            "/api/auth/login/",
            {"email": "listener.one", "password": "wrong-password"},
        )
        self.assertEqual(unknown.status_code, 401)
        self.assertEqual(wrong_password.status_code, 401)
        self.assertEqual(unknown.content, wrong_password.content)

    def test_login_persists_session_across_requests(self):
        self.assertEqual(self._register().status_code, 201)
        self._post("/api/auth/logout/", {})

        response = self._post(
            "/api/auth/login/",
            {
                "email": "LISTENER@EXAMPLE.COM",
                "password": self.valid_registration["password"],
            },
        )
        session_response = self.client.get("/api/auth/session/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(session_response.json()["authenticated"])
        self.assertEqual(
            session_response.json()["user"]["email"],
            "listener@example.com",
        )

    @override_settings(EMAIL_VERIFICATION_ENFORCED=False)
    def test_flag_off_self_payload_is_byte_identical_to_the_existing_contract(self):
        registered = self._register()
        expected_user = {
            "id": registered.json()["user"]["id"],
            "email": "listener@example.com",
            "username": "listener.one",
            "display_name": "Listener One",
            "avatar": None,
            "is_private": False,
        }
        self.assertEqual(registered.content, json.dumps({"user": expected_user}).encode())
        session = self.client.get("/api/auth/session/")
        self.assertEqual(
            session.content,
            json.dumps({"authenticated": True, "user": expected_user}).encode(),
        )

    @override_settings(EMAIL_VERIFICATION_ENFORCED=True)
    def test_flag_on_self_payload_exposes_verification_state_only_to_self(self):
        registered = self._register()
        self.assertIs(registered.json()["user"]["email_verified"], False)
        self.assertIs(
            self.client.get("/api/auth/session/").json()["user"]["email_verified"],
            False,
        )
        user = get_user_model().objects.get()
        user.email_verified_at = datetime(2026, 8, 20, 16, tzinfo=UTC)
        user.save(update_fields=("email_verified_at",))
        self.assertIs(
            self.client.get("/api/auth/session/").json()["user"]["email_verified"],
            True,
        )
        public_profile = self.client.get(f"/api/users/{user.username}/").json()
        self.assertNotIn("email_verified", public_profile["profile"])

    def test_logout_invalidates_session_and_is_idempotent(self):
        self.assertEqual(self._register().status_code, 201)

        first = self._post("/api/auth/logout/", {})
        session_response = self.client.get("/api/auth/session/")
        self.csrf_token = self.client.cookies.get("csrftoken")
        second = self._post("/api/auth/logout/", {})

        self.assertEqual(first.status_code, 204)
        self.assertFalse(session_response.json()["authenticated"])
        self.assertEqual(second.status_code, 204)

    def test_catalog_endpoints_remain_available_to_guests(self):
        city = City.objects.create(
            name="Test City",
            region_code="TC",
            region_name="Test Region",
            country_code="US",
            timezone="America/New_York",
        )
        guest = Client(enforce_csrf_checks=True)

        cities_response = guest.get("/api/cities/")
        events_response = guest.get(
            f"/api/events/?when=upcoming&city_id={city.id}"
        )

        self.assertEqual(cities_response.status_code, 200)
        self.assertEqual(events_response.status_code, 200)
