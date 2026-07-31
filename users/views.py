import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .forms import LoginForm, RegistrationForm


def _user_payload(user):
    # This serializer is for the authenticated user's own session only. Email
    # must never be copied into future other-user/profile serializers.
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "display_name": user.display_name,
        "is_private": user.is_private,
    }


def _json_object(request):
    try:
        value = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _form_errors(form):
    return {
        field: [error["message"] for error in errors]
        for field, errors in form.errors.get_json_data().items()
    }


@require_GET
@ensure_csrf_cookie
def session_detail(request):
    if not request.user.is_authenticated:
        return JsonResponse({"authenticated": False, "user": None})
    return JsonResponse(
        {"authenticated": True, "user": _user_payload(request.user)}
    )


@require_POST
def register(request):
    payload = _json_object(request)
    if payload is None:
        return JsonResponse(
            {"errors": {"request": ["Request body must be a JSON object."]}},
            status=400,
        )
    if "is_private" not in payload or type(payload["is_private"]) is not bool:
        return JsonResponse(
            {"errors": {"is_private": ["Choose Public or Private."]}},
            status=400,
        )
    form = RegistrationForm(payload)
    if not form.is_valid():
        return JsonResponse({"errors": _form_errors(form)}, status=400)
    user = form.save()
    login(request, user)
    return JsonResponse({"user": _user_payload(user)}, status=201)


@require_POST
def login_view(request):
    payload = _json_object(request)
    if payload is None:
        return JsonResponse(
            {"errors": {"request": ["Request body must be a JSON object."]}},
            status=400,
        )
    form = LoginForm(payload)
    if not form.is_valid():
        return JsonResponse({"errors": _form_errors(form)}, status=400)
    user = authenticate(
        request,
        email=form.cleaned_data["email"],
        password=form.cleaned_data["password"],
    )
    if user is None:
        return JsonResponse(
            {"errors": {"credentials": ["Invalid email or password."]}},
            status=401,
        )
    login(request, user)
    return JsonResponse({"user": _user_payload(user)})


@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({}, status=204)
