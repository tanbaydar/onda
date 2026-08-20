from django.urls import path

from .views import (
    login_view,
    logout_view,
    password_reset_confirm,
    password_reset_request,
    register,
    session_detail,
    verification_code_confirm,
    verification_code_request,
)


urlpatterns = [
    path("session/", session_detail, name="session"),
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path(
        "verification/request/",
        verification_code_request,
        name="verification-code-request",
    ),
    path(
        "verification/confirm/",
        verification_code_confirm,
        name="verification-code-confirm",
    ),
    path(
        "password-reset/request/",
        password_reset_request,
        name="password-reset-request",
    ),
    path(
        "password-reset/confirm/",
        password_reset_confirm,
        name="password-reset-confirm",
    ),
]
