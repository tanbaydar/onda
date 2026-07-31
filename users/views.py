import json
import math
from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.core.paginator import EmptyPage, Paginator
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
    require_POST,
)

from catalog.models import EventArtist
from catalog.views import _event_queryset, _serialize_event
from .forms import LoginForm, RegistrationForm
from .models import DiaryEntry, RATING_VALUES
from .services import (
    EventNotStarted,
    NOT_STARTED_MESSAGE,
    remove_entry,
    remove_rating,
    save_rating,
    serialize_diary_entry,
)


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


def _authentication_required(request):
    if request.user.is_authenticated:
        return None
    return JsonResponse(
        {"errors": {"authentication": ["Authentication required."]}},
        status=401,
    )


def _rating_from_payload(request):
    payload = _json_object(request)
    if (
        payload is None
        or "rating" not in payload
        or type(payload["rating"]) not in (int, float)
        or not math.isfinite(payload["rating"])
    ):
        return None
    rating = Decimal(str(payload["rating"]))
    return rating if rating in RATING_VALUES else None


def _visible_event(event_id):
    return get_object_or_404(_event_queryset(), pk=event_id)


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


@require_http_methods(["PUT", "DELETE"])
def event_been(request, event_id):
    auth_error = _authentication_required(request)
    if auth_error is not None:
        return auth_error
    event = _visible_event(event_id)
    if request.method == "DELETE":
        if not remove_entry(user=request.user, event=event):
            return JsonResponse({"error": "Been entry not found."}, status=404)
        return JsonResponse({}, status=204)

    rating = _rating_from_payload(request)
    if rating is None:
        return JsonResponse(
            {
                "errors": {
                    "rating": [
                        "Rating must be a half-star value from 0.5 to 5.0."
                    ]
                }
            },
            status=400,
        )
    try:
        entry, created = save_rating(
            user=request.user,
            event=event,
            rating=rating,
        )
    except EventNotStarted:
        return JsonResponse(
            {"errors": {"event": [NOT_STARTED_MESSAGE]}},
            status=409,
        )
    return JsonResponse(
        {"entry": serialize_diary_entry(entry)},
        status=201 if created else 200,
    )


@require_http_methods(["DELETE"])
def event_been_rating(request, event_id):
    auth_error = _authentication_required(request)
    if auth_error is not None:
        return auth_error
    event = _visible_event(event_id)
    entry = remove_rating(user=request.user, event=event)
    if entry is None:
        return JsonResponse({"error": "Been entry not found."}, status=404)
    return JsonResponse({"entry": serialize_diary_entry(entry)})


@require_GET
def diary_list(request):
    auth_error = _authentication_required(request)
    if auth_error is not None:
        return auth_error
    try:
        page_number = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 20))
        if page_number < 1 or page_size < 1 or page_size > 100:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse(
            {"error": "page and page_size must be positive integers"},
            status=400,
        )

    lineup = EventArtist.objects.select_related("artist").order_by("position")
    entries = (
        DiaryEntry.objects.visible_to(request.user)
        .select_related("event__venue__city")
        .prefetch_related(
            Prefetch(
                "event__event_artists",
                queryset=lineup,
                to_attr="_ordered_event_artists",
            )
        )
        .order_by("-event__event_date", "-event_id")
    )
    paginator = Paginator(entries, page_size)
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        return JsonResponse({"error": "page out of range"}, status=404)

    results = []
    for entry in page.object_list:
        serialized = serialize_diary_entry(entry)
        serialized["event"] = _serialize_event(entry.event)
        results.append(serialized)
    return JsonResponse(
        {
            "results": results,
            "pagination": {
                "page": page.number,
                "page_size": page_size,
                "total_results": paginator.count,
                "total_pages": paginator.num_pages,
                "next_page": (
                    page.next_page_number() if page.has_next() else None
                ),
                "previous_page": (
                    page.previous_page_number()
                    if page.has_previous()
                    else None
                ),
            },
        }
    )
