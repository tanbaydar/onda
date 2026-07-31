import json
import math
from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.core.paginator import EmptyPage, Paginator
from django.db.models import Count, Exists, IntegerField, OuterRef, Prefetch, Value
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
from .models import DiaryEntry, RATING_VALUES, Review, ReviewLike
from .services import (
    EventNotStarted,
    NOT_STARTED_MESSAGE,
    ReviewLikeConflict,
    ReviewRequiresRating,
    delete_review,
    like_review,
    remove_entry,
    remove_rating,
    save_rating,
    save_review,
    serialize_diary_entry,
    serialize_review,
    unlike_review,
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


def _review_body(request):
    payload = _json_object(request)
    if payload is None or type(payload.get("body")) is not str:
        return None
    body = payload["body"].strip()
    return body if 1 <= len(body) <= 1000 else None


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
    result = remove_rating(user=request.user, event=event)
    if result is None:
        return JsonResponse({"error": "Been entry not found."}, status=404)
    entry, cascade = result
    return JsonResponse(
        {"entry": serialize_diary_entry(entry), "cascade": cascade}
    )


@require_http_methods(["PUT", "DELETE"])
def event_been_review(request, event_id):
    auth_error = _authentication_required(request)
    if auth_error is not None:
        return auth_error
    event = _visible_event(event_id)
    if request.method == "DELETE":
        if not delete_review(user=request.user, event=event):
            return JsonResponse({"error": "Review not found."}, status=404)
        return JsonResponse({}, status=204)

    body = _review_body(request)
    if body is None:
        return JsonResponse(
            {
                "errors": {
                    "body": [
                        "Review must contain 1 to 1,000 characters after trimming."
                    ]
                }
            },
            status=400,
        )
    try:
        review, created = save_review(
            user=request.user,
            event=event,
            body=body,
        )
    except ReviewRequiresRating:
        return JsonResponse(
            {"errors": {"rating": ["A rating is required to publish a review."]}},
            status=409,
        )
    if review is None:
        return JsonResponse({"error": "Been entry not found."}, status=404)
    return JsonResponse(
        {"review": serialize_review(review)},
        status=201 if created else 200,
    )


def _visible_review(viewer, review_id):
    return get_object_or_404(
        Review.objects.visible_to(viewer).select_related("entry__user"),
        pk=review_id,
    )


@require_http_methods(["POST", "DELETE"])
def review_like(request, review_id):
    auth_error = _authentication_required(request)
    if auth_error is not None:
        return auth_error
    review = _visible_review(request.user, review_id)
    if request.method == "DELETE":
        if not unlike_review(user=request.user, review=review):
            return JsonResponse({"error": "Review like not found."}, status=404)
        return JsonResponse({}, status=204)
    try:
        like_count = like_review(user=request.user, review=review)
    except ReviewLikeConflict as exc:
        return JsonResponse({"error": str(exc)}, status=409)
    return JsonResponse(
        {"like_count": like_count, "viewer_has_liked": True},
        status=201,
    )


@require_GET
def event_review_list(request, event_id):
    event = _visible_event(event_id)
    sort = request.GET.get("sort", "most_liked")
    if sort not in ("most_liked", "newest"):
        return JsonResponse(
            {"error": "sort must be most_liked or newest"},
            status=400,
        )
    try:
        page_number = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))
        if page_number < 1 or page_size < 1 or page_size > 50:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse(
            {"error": "page and page_size must be positive integers"},
            status=400,
        )

    reviews = (
        Review.objects.for_public_section()
        .filter(entry__event=event)
        .select_related("entry__user")
        .annotate(
            like_count=Count("likes"),
            author_follower_count=Value(0, output_field=IntegerField()),
        )
    )
    if request.user.is_authenticated:
        reviews = reviews.annotate(
            viewer_has_liked=Exists(
                ReviewLike.objects.filter(
                    user=request.user,
                    review_id=OuterRef("pk"),
                )
            )
        )
    order_by = (
        ("-like_count", "-author_follower_count", "-published_at", "-id")
        if sort == "most_liked"
        else ("-published_at", "-id")
    )
    paginator = Paginator(reviews.order_by(*order_by), page_size)
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        return JsonResponse({"error": "page out of range"}, status=404)
    return JsonResponse(
        {
            "results": [
                serialize_review(
                    review,
                    include_author=True,
                    viewer=request.user,
                )
                for review in page.object_list
            ],
            "pagination": {
                "page": page.number,
                "page_size": page_size,
                "total_results": paginator.count,
                "total_pages": paginator.num_pages,
                "next_page": page.next_page_number() if page.has_next() else None,
                "previous_page": (
                    page.previous_page_number() if page.has_previous() else None
                ),
            },
        }
    )


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
        .select_related("event__venue__city", "review")
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
        serialized = serialize_diary_entry(entry, include_review=False)
        serialized["has_review"] = getattr(entry, "review", None) is not None
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
