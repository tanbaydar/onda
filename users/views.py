import json
import math
import base64
from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.core.paginator import EmptyPage, Paginator
from django.db import transaction
from django.db.models import Avg, Count, Exists, OuterRef, Prefetch, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
    require_POST,
)
from django.utils.dateparse import parse_datetime

from catalog.models import EventArtist
from catalog.views import _event_queryset, _serialize_event
from .forms import LoginForm, RegistrationForm
from .home_feed import decode_cursor as decode_home_cursor
from .home_feed import encode_cursor as encode_home_cursor
from .home_feed import home_feed_rows, serialize_feed_row
from .models import (
    DiaryEntry,
    Follow,
    FollowStatus,
    Notification,
    RATING_VALUES,
    Review,
    ReviewLike,
)
from .services import (
    EventNotStarted,
    NOT_STARTED_MESSAGE,
    ReviewLikeConflict,
    ReviewRequiresRating,
    FollowConflict,
    accept_follow_request,
    change_privacy,
    decline_follow_request,
    delete_review,
    like_review,
    remove_entry,
    remove_rating,
    save_rating,
    save_review,
    serialize_follow,
    serialize_public_user,
    timezone_now,
    serialize_diary_entry,
    serialize_review,
    unlike_review,
    unfollow_user,
    follow_user,
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


def _pagination(request, *, default=20, maximum=100):
    try:
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", default))
        if page < 1 or page_size < 1 or page_size > maximum:
            raise ValueError
    except (TypeError, ValueError):
        return None
    return page, page_size


def _notification_payload(notification):
    return {
        "id": notification.id,
        "type": notification.type,
        "actor": serialize_public_user(notification.actor),
        "review": (
            {
                "id": notification.review_id,
                "event_id": notification.review.entry.event_id,
            }
            if notification.review_id is not None
            else None
        ),
        "created_at": notification.created_at.isoformat().replace("+00:00", "Z"),
        "read_at": (
            notification.read_at.isoformat().replace("+00:00", "Z")
            if notification.read_at is not None
            else None
        ),
    }


def _cursor_encode(notification):
    raw = f"{notification.created_at.isoformat()}|{notification.id}"
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


def _cursor_decode(value):
    try:
        padded = value + "=" * (-len(value) % 4)
        timestamp, identifier = base64.urlsafe_b64decode(padded).decode().rsplit("|", 1)
        parsed = parse_datetime(timestamp)
        identifier = int(identifier)
        if parsed is None or identifier < 1:
            raise ValueError
        return parsed, identifier
    except (ValueError, TypeError, UnicodeError):
        return None


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
    return HttpResponse(status=204)


@require_http_methods(["PUT", "DELETE"])
def event_been(request, event_id):
    auth_error = _authentication_required(request)
    if auth_error is not None:
        return auth_error
    event = _visible_event(event_id)
    if request.method == "DELETE":
        if not remove_entry(user=request.user, event=event):
            return JsonResponse({"error": "Been entry not found."}, status=404)
        return HttpResponse(status=204)

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
        return HttpResponse(status=204)

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
        return HttpResponse(status=204)
    try:
        like_count = like_review(user=request.user, review=review)
    except ReviewLikeConflict as exc:
        return JsonResponse({"error": str(exc)}, status=409)
    return JsonResponse(
        {"like_count": like_count, "viewer_has_liked": True},
        status=201,
    )


@require_http_methods(["POST", "DELETE"])
def follow_resource(request, user_id):
    auth_error = _authentication_required(request)
    if auth_error is not None:
        return auth_error
    if request.method == "DELETE":
        if not unfollow_user(follower_id=request.user.id, followee_id=user_id):
            return JsonResponse({"error": "Follow not found."}, status=404)
        return HttpResponse(status=204)
    try:
        follow = follow_user(follower_id=request.user.id, followee_id=user_id)
    except FollowConflict as exc:
        return JsonResponse({"error": str(exc)}, status=409)
    if follow is None:
        return JsonResponse({"error": "User not found."}, status=404)
    return JsonResponse(
        {"follow": serialize_follow(follow, user=follow.followee)},
        status=201,
    )


@require_GET
def pending_follow_requests(request):
    auth_error = _authentication_required(request)
    if auth_error is not None:
        return auth_error
    pagination = _pagination(request)
    if pagination is None:
        return JsonResponse(
            {"error": "page and page_size must be positive integers"}, status=400
        )
    page_number, page_size = pagination
    requests = (
        Follow.objects.filter(
            followee=request.user,
            status=FollowStatus.PENDING,
        )
        .select_related("follower")
        .order_by("-created_at", "-follower_id")
    )
    paginator = Paginator(requests, page_size)
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        return JsonResponse({"error": "page out of range"}, status=404)
    return JsonResponse(
        {
            "results": [
                serialize_follow(follow, user=follow.follower)
                for follow in page.object_list
            ],
            "pagination": {
                "page": page.number,
                "page_size": page_size,
                "total_results": paginator.count,
                "total_pages": paginator.num_pages,
                "next_page": page.next_page_number() if page.has_next() else None,
                "previous_page": page.previous_page_number() if page.has_previous() else None,
            },
        }
    )


@require_POST
def accept_request(request, follower_id):
    auth_error = _authentication_required(request)
    if auth_error is not None:
        return auth_error
    follow = accept_follow_request(
        followee_id=request.user.id,
        follower_id=follower_id,
    )
    if follow is None:
        return JsonResponse({"error": "Follow request not found."}, status=404)
    return JsonResponse(
        {"follow": serialize_follow(follow, user=follow.follower)}
    )


@require_POST
def decline_request(request, follower_id):
    auth_error = _authentication_required(request)
    if auth_error is not None:
        return auth_error
    if not decline_follow_request(
        followee_id=request.user.id,
        follower_id=follower_id,
    ):
        return JsonResponse({"error": "Follow request not found."}, status=404)
    return HttpResponse(status=204)


@require_http_methods(["PUT"])
def privacy_detail(request):
    auth_error = _authentication_required(request)
    if auth_error is not None:
        return auth_error
    payload = _json_object(request)
    if payload is None or type(payload.get("is_private")) is not bool:
        return JsonResponse(
            {"errors": {"is_private": ["Choose Public or Private."]}},
            status=400,
        )
    user, accepted = change_privacy(
        user_id=request.user.id,
        is_private=payload["is_private"],
    )
    return JsonResponse(
        {
            "privacy": {
                "is_private": user.is_private,
                "pending_requests_approved": accepted,
            }
        }
    )


@require_GET
def notification_list(request):
    auth_error = _authentication_required(request)
    if auth_error is not None:
        return auth_error
    try:
        page_size = int(request.GET.get("page_size", 20))
        if page_size < 1 or page_size > 100:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({"error": "page_size must be a positive integer"}, status=400)
    notifications = Notification.objects.filter(recipient=request.user)
    cursor = request.GET.get("cursor")
    if cursor:
        decoded = _cursor_decode(cursor)
        if decoded is None:
            return JsonResponse({"error": "cursor is invalid"}, status=400)
        created_at, identifier = decoded
        notifications = notifications.filter(
            Q(created_at__lt=created_at)
            | Q(created_at=created_at, id__lt=identifier)
        )
    rows = list(
        notifications.select_related("actor", "review__entry")
        .order_by("-created_at", "-id")[: page_size + 1]
    )
    has_more = len(rows) > page_size
    rows = rows[:page_size]
    return JsonResponse(
        {
            "results": [_notification_payload(item) for item in rows],
            "next_cursor": _cursor_encode(rows[-1]) if has_more and rows else None,
        }
    )


@require_GET
def home_feed(request):
    auth_error = _authentication_required(request)
    if auth_error is not None:
        return auth_error
    try:
        page_size = int(request.GET.get("page_size", 20))
        if page_size < 1 or page_size > 100:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse(
            {"errors": {"page_size": ["Must be an integer from 1 to 100."]}},
            status=400,
        )
    cursor = None
    if "cursor" in request.GET:
        cursor = decode_home_cursor(request.GET["cursor"])
        if cursor is None:
            return JsonResponse(
                {"errors": {"cursor": ["Cursor is invalid."]}}, status=400
            )
    rows = home_feed_rows(request.user, cursor=cursor, limit=page_size + 1)
    has_more = len(rows) > page_size
    rows = rows[:page_size]
    return JsonResponse(
        {
            "results": [serialize_feed_row(row) for row in rows],
            "next_cursor": encode_home_cursor(rows[-1]) if has_more and rows else None,
        }
    )
@require_POST
@transaction.atomic
def notification_read(request, notification_id):
    auth_error = _authentication_required(request)
    if auth_error is not None:
        return auth_error
    notification = (
        Notification.objects.select_for_update()
        .filter(pk=notification_id, recipient=request.user)
        .first()
    )
    if notification is None:
        return JsonResponse({"error": "Notification not found."}, status=404)
    if notification.read_at is None:
        notification.read_at = timezone_now()
        notification.save(update_fields=("read_at",))
    return JsonResponse(
        {
            "notification": {
                "id": notification.id,
                "read_at": notification.read_at.isoformat().replace("+00:00", "Z"),
            }
        }
    )


@require_POST
def notifications_read_all(request):
    auth_error = _authentication_required(request)
    if auth_error is not None:
        return auth_error
    now = timezone_now()
    updated = Notification.objects.filter(
        recipient=request.user,
        read_at__isnull=True,
    ).update(read_at=now)
    return JsonResponse(
        {
            "updated_count": updated,
            "read_at": now.isoformat().replace("+00:00", "Z"),
        }
    )


@require_GET
def event_circle(request, event_id):
    auth_error = _authentication_required(request)
    if auth_error is not None:
        return auth_error
    event = _visible_event(event_id)
    pagination = _pagination(request, default=10, maximum=50)
    if pagination is None:
        return JsonResponse(
            {"error": "page and page_size must be positive integers"}, status=400
        )
    page_number, page_size = pagination
    entries = (
        DiaryEntry.objects.for_circle(request.user)
        .filter(event=event)
        .select_related("user", "review")
        .order_by("-rated_at", "-id")
    )
    paginator = Paginator(entries, page_size)
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        return JsonResponse({"error": "page out of range"}, status=404)
    aggregate = (
        DiaryEntry.objects.for_circle_average(request.user)
        .filter(event=event)
        .aggregate(count=Count("id"), average=Avg("rating"))
    )
    summary = {"state": "not_enough_ratings", "count": 0}
    if aggregate["count"]:
        summary = {
            "state": "available",
            "count": aggregate["count"],
            "average": float(aggregate["average"]),
        }
    results = []
    for entry in page.object_list:
        review = getattr(entry, "review", None)
        serialized_review = None
        if review is not None:
            serialized_review = serialize_review(review)
            serialized_review["viewer_has_liked"] = ReviewLike.objects.filter(
                user=request.user,
                review=review,
            ).exists()
        results.append(
            {
                "id": entry.id,
                "user": serialize_public_user(entry.user),
                "rating": float(entry.rating),
                "rated_at": entry.rated_at.isoformat().replace("+00:00", "Z"),
                "review": serialized_review,
            }
        )
    return JsonResponse(
        {
            "rating_summary": summary,
            "results": results,
            "pagination": {
                "page": page.number,
                "page_size": page_size,
                "total_results": paginator.count,
                "total_pages": paginator.num_pages,
                "next_page": page.next_page_number() if page.has_next() else None,
                "previous_page": page.previous_page_number() if page.has_previous() else None,
            },
        }
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
            like_count=Count("likes__user_id", distinct=True),
            author_follower_count=Count(
                "entry__user__follower_relationships__follower_id",
                filter=Q(
                    entry__user__follower_relationships__status=FollowStatus.APPROVED
                ),
                distinct=True,
            ),
        )
    )
    if request.user.is_authenticated:
        reviews = reviews.annotate(
            viewer_has_liked=Exists(
                ReviewLike.objects.filter(
                    user=request.user,
                    review_id=OuterRef("pk"),
                )
            ),
            viewer_follows=Exists(
                Follow.objects.filter(
                    follower=request.user,
                    followee_id=OuterRef("entry__user_id"),
                    status=FollowStatus.APPROVED,
                )
            ),
            viewer_has_follow_row=Exists(
                Follow.objects.filter(
                    follower=request.user,
                    followee_id=OuterRef("entry__user_id"),
                )
            ),
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
        .filter(user=request.user)
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
