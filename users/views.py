import json
import math
import base64
from decimal import Decimal

from django.contrib.auth import authenticate, login, logout, password_validation
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, Paginator
from django.core.validators import URLValidator
from django.db import transaction
from django.db.models import Avg, Count, Exists, OuterRef, Prefetch, Q
from django.db.models.functions import Length
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
    require_POST,
)
from django.utils.dateparse import parse_datetime

from catalog.models import Artist, City, EventArtist, Venue
from catalog.views import _event_queryset, _serialize_artist, _serialize_event, _serialize_venue
from .forms import LoginForm, RegistrationForm
from .home_feed import decode_cursor as decode_home_cursor
from .home_feed import encode_cursor as encode_home_cursor
from .home_feed import home_feed_rows, serialize_feed_row
from .auth_services import (
    CodeAttemptLimit,
    CodeCooldown,
    CodeExpired,
    CodeInvalid,
    VERIFICATION_REQUIRED_MESSAGE,
    account_actions_allowed,
    effective_visibility_viewer,
    issue_account_code,
    request_password_reset,
    reset_password,
    verify_email,
)
from .models import (
    AccountCodePurpose,
    DiaryEntry,
    Follow,
    FollowStatus,
    Notification,
    RATING_VALUES,
    Review,
    ReviewLike,
    User,
    UserStatus,
    WillBeThere,
    FavoriteArtist,
    FavoriteEvent,
    FavoriteVenue,
)
from .services import (
    EventNotStarted,
    NOT_STARTED_MESSAGE,
    ReviewLikeConflict,
    ReviewRequiresRating,
    FollowConflict,
    WillBeThereExpired,
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
    remove_will_be_there,
    rating_distribution_payload,
    save_will_be_there,
    serialize_will_be_there,
    FavoriteLimitReached,
    save_favorite,
    remove_favorite,
)


def _user_payload(user):
    # This serializer is for the authenticated user's own session only. Email
    # must never be copied into future other-user/profile serializers.
    payload = {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "display_name": user.display_name,
        "is_private": user.is_private,
    }
    if settings.EMAIL_VERIFICATION_ENFORCED:
        payload["email_verified"] = user.email_verified_at is not None
    return payload


def _profile_identity(user):
    city = user.home_city
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "avatar": user.avatar,
        "bio": user.bio,
        "follower_count": Follow.objects.filter(
            followee=user,
            status=FollowStatus.APPROVED,
        ).count(),
        "following_count": Follow.objects.filter(
            follower=user,
            status=FollowStatus.APPROVED,
        ).count(),
        "home_city": (
            {
                "id": city.id,
                "name": city.name,
                "region_code": city.region_code,
                "country_code": city.country_code,
                "timezone": city.timezone,
            }
            if city is not None
            else None
        ),
    }


def _profile_user(username):
    return get_object_or_404(
        User.objects.select_related("home_city"),
        username__iexact=username,
        status=UserStatus.ACTIVE,
        username__isnull=False,
    )


def _profile_access(viewer, profile):
    viewer = effective_visibility_viewer(viewer)
    if viewer.is_authenticated and viewer.pk == profile.pk:
        return "owner"
    if User.objects.profile_content_visible_to(viewer).filter(pk=profile.pk).exists():
        return "full"
    return "stub"


def _private_content_response():
    return JsonResponse(
        {"errors": {"profile": ["This profile's content is private."]}},
        status=403,
    )


def _pagination_payload(page, page_size, total):
    return {
        "page": page.number,
        "page_size": page_size,
        "total_results": total,
        "total_pages": page.paginator.num_pages,
        "next_page": page.next_page_number() if page.has_next() else None,
        "previous_page": page.previous_page_number() if page.has_previous() else None,
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
    if not request.user.is_authenticated:
        return JsonResponse(
            {"errors": {"authentication": ["Authentication required."]}},
            status=401,
        )
    if not account_actions_allowed(request.user):
        return JsonResponse(
            {"errors": {"verification": [VERIFICATION_REQUIRED_MESSAGE]}},
            status=403,
        )
    return None


def _session_required(request):
    if request.user.is_authenticated:
        return None
    return JsonResponse(
        {"errors": {"authentication": ["Authentication required."]}},
        status=401,
    )


def _code_from_payload(request):
    payload = _json_object(request)
    if payload is None or not isinstance(payload.get("code"), str):
        return None
    code = payload["code"]
    return code if len(code) == 6 and code.isascii() and code.isdigit() else None


def _code_error(exc):
    return JsonResponse(
        {"errors": {"code": [str(exc)]}},
        status=400,
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


@require_POST
def verification_code_request(request):
    auth_error = _session_required(request)
    if auth_error is not None:
        return auth_error
    if request.user.email_verified_at is not None:
        return JsonResponse({"sent": False, "already_verified": True})
    try:
        issue_account_code(
            user=request.user,
            purpose=AccountCodePurpose.EMAIL_VERIFICATION,
        )
    except CodeCooldown as exc:
        return JsonResponse(
            {
                "errors": {
                    "code": [
                        f"Wait {exc.retry_after} seconds before requesting another code."
                    ]
                },
                "retry_after": exc.retry_after,
            },
            status=429,
        )
    return JsonResponse({"sent": True, "cooldown_seconds": 60})


@require_POST
def verification_code_confirm(request):
    auth_error = _session_required(request)
    if auth_error is not None:
        return auth_error
    code = _code_from_payload(request)
    if code is None:
        return JsonResponse(
            {"errors": {"code": ["Enter a 6-digit code."]}},
            status=400,
        )
    try:
        verified_at = verify_email(user=request.user, code=code)
    except (CodeAttemptLimit, CodeExpired, CodeInvalid) as exc:
        return _code_error(exc)
    request.user.email_verified_at = verified_at
    return JsonResponse({"verified": True})


@require_POST
def password_reset_request(request):
    payload = _json_object(request)
    if payload is None or not isinstance(payload.get("email"), str):
        return JsonResponse(
            {"errors": {"email": ["Enter a valid email address."]}},
            status=400,
        )
    request_password_reset(email=payload["email"].strip().lower())
    return JsonResponse({"accepted": True})


@require_POST
def password_reset_confirm(request):
    payload = _json_object(request)
    if payload is None:
        return JsonResponse(
            {"errors": {"request": ["Request body must be a JSON object."]}},
            status=400,
        )
    email = payload.get("email")
    password = payload.get("password")
    code = payload.get("code")
    errors = {}
    if not isinstance(email, str) or not email.strip():
        errors["email"] = ["Enter a valid email address."]
    if not isinstance(code, str) or len(code) != 6 or not code.isascii() or not code.isdigit():
        errors["code"] = ["Enter a 6-digit code."]
    if not isinstance(password, str):
        errors["password"] = ["Enter a new password."]
    if errors:
        return JsonResponse({"errors": errors}, status=400)
    try:
        # Validate without account attributes before lookup so an invalid reset
        # submission cannot use user-specific errors for account enumeration.
        password_validation.validate_password(password)
    except ValidationError as exc:
        return JsonResponse(
            {"errors": {"password": list(exc.messages)}},
            status=400,
        )
    user = User.objects.filter(email__iexact=email.strip()).first()
    if user is None:
        return JsonResponse(
            {"errors": {"code": ["The code is invalid."]}},
            status=400,
        )
    try:
        reset_password(user=user, code=code, password=password)
    except ValidationError as exc:
        return JsonResponse(
            {"errors": {"password": list(exc.messages)}},
            status=400,
        )
    except (CodeAttemptLimit, CodeExpired, CodeInvalid) as exc:
        return _code_error(exc)
    return JsonResponse({"reset": True})


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


@require_http_methods(["PUT", "DELETE"])
def will_be_there_resource(request, event_id):
    auth_error = _authentication_required(request)
    if auth_error is not None:
        return auth_error
    event = _visible_event(event_id)
    if request.method == "DELETE":
        remove_will_be_there(user=request.user, event=event)
        return HttpResponse(status=204)
    try:
        entry, created = save_will_be_there(user=request.user, event=event)
    except WillBeThereExpired:
        return JsonResponse(
            {
                "errors": {
                    "will_be_there": [
                        "This event's Will Be There window has expired."
                    ]
                }
            },
            status=409,
        )
    return JsonResponse(
        {"will_be_there": serialize_will_be_there(entry)},
        status=201 if created else 200,
    )


def _attendee_page(request, entries):
    pagination = _pagination(request)
    if pagination is None:
        return JsonResponse(
            {"error": "page and page_size must be positive integers"}, status=400
        )
    page_number, page_size = pagination
    paginator = Paginator(
        entries.select_related("user").order_by("-created_at", "-user_id"),
        page_size,
    )
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        return JsonResponse({"error": "page out of range"}, status=404)
    return JsonResponse(
        {
            "results": [
                {
                    "user": serialize_public_user(entry.user),
                    "created_at": entry.created_at.isoformat().replace("+00:00", "Z"),
                }
                for entry in page.object_list
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
def public_will_be_there(request, event_id):
    event = _visible_event(event_id)
    entries = WillBeThere.objects.for_public_section(timezone_now()).filter(event=event)
    return _attendee_page(request, entries)


@require_GET
def circle_will_be_there(request, event_id):
    auth_error = _authentication_required(request)
    if auth_error is not None:
        return auth_error
    event = _visible_event(event_id)
    entries = WillBeThere.objects.for_circle(request.user, timezone_now()).filter(
        event=event
    )
    return _attendee_page(request, entries)


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
def profile_detail(request, username):
    profile = _profile_user(username)
    viewer = effective_visibility_viewer(request.user)
    access = _profile_access(viewer, profile)
    payload = {"profile": _profile_identity(profile), "access": access}
    if access == "owner":
        payload["account"] = {"is_private": profile.is_private}
    elif viewer.is_authenticated:
        outgoing = Follow.objects.filter(
            follower=viewer,
            followee=profile,
        ).first()
        payload["relationship"] = {
            "outgoing_status": outgoing.status if outgoing is not None else None,
            "follows_you": Follow.objects.filter(
                follower=profile,
                followee=viewer,
                status=FollowStatus.APPROVED,
            ).exists(),
            "can_follow": outgoing is None,
            "can_unfollow": outgoing is not None,
            "follow_action": (
                ("request" if profile.is_private else "follow")
                if outgoing is None
                else None
            ),
        }
    return JsonResponse(payload)


@require_http_methods(["PUT"])
def profile_edit(request):
    auth_error = _authentication_required(request)
    if auth_error is not None:
        return auth_error
    payload = _json_object(request)
    if payload is None:
        return JsonResponse(
            {"errors": {"request": ["Request body must be a JSON object."]}},
            status=400,
        )
    errors = {}
    required = ("display_name", "avatar", "bio", "home_city_id")
    for field in required:
        if field not in payload:
            errors[field] = ["This field is required."]

    display_name = payload.get("display_name")
    if "display_name" in payload:
        if type(display_name) is not str or not 1 <= len(display_name.strip()) <= 50:
            errors["display_name"] = [
                "Display name must contain 1 to 50 characters after trimming."
            ]
        else:
            display_name = display_name.strip()

    avatar = payload.get("avatar")
    if "avatar" in payload:
        if avatar is not None and type(avatar) is not str:
            errors["avatar"] = ["Avatar must be an HTTP or HTTPS URL, or null."]
        elif type(avatar) is str:
            avatar = avatar.strip() or None
            if avatar is not None:
                try:
                    URLValidator(schemes=("http", "https"))(avatar)
                except ValidationError:
                    errors["avatar"] = ["Avatar must be an HTTP or HTTPS URL, or null."]
                if len(avatar) > 2048:
                    errors["avatar"] = ["Avatar URL cannot exceed 2,048 characters."]

    bio = payload.get("bio")
    if "bio" in payload:
        if bio is not None and type(bio) is not str:
            errors["bio"] = ["Bio must be text or null."]
        elif type(bio) is str:
            if len(bio) > 150:
                errors["bio"] = ["Bio cannot exceed 150 characters."]
            elif not bio.strip():
                bio = None

    home_city = None
    home_city_id = payload.get("home_city_id")
    if "home_city_id" in payload:
        if home_city_id is not None and (
            type(home_city_id) is not int or home_city_id < 1
        ):
            errors["home_city_id"] = ["Choose a canonical city or null."]
        elif home_city_id is not None:
            home_city = City.objects.filter(pk=home_city_id).first()
            if home_city is None:
                errors["home_city_id"] = ["Choose a canonical city or null."]

    if errors:
        return JsonResponse({"errors": errors}, status=400)
    request.user.display_name = display_name
    request.user.avatar = avatar
    request.user.bio = bio
    request.user.home_city = home_city
    request.user.save(update_fields=("display_name", "avatar", "bio", "home_city"))
    return JsonResponse({"profile": _profile_identity(request.user)})


def _profile_content_target(request, username):
    profile = _profile_user(username)
    viewer = effective_visibility_viewer(request.user)
    if not User.objects.profile_content_visible_to(viewer).filter(pk=profile.pk).exists():
        return profile, _private_content_response()
    return profile, None


@require_GET
def profile_been(request, username):
    profile, denied = _profile_content_target(request, username)
    if denied is not None:
        return denied
    pagination = _pagination(request, default=20, maximum=100)
    if pagination is None:
        return JsonResponse(
            {"error": "page and page_size must be positive integers"}, status=400
        )
    page_number, page_size = pagination
    lineup = EventArtist.objects.select_related("artist").order_by("position")
    viewer = effective_visibility_viewer(request.user)
    entries = (
        DiaryEntry.objects.visible_to(viewer)
        .filter(user=profile)
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
    results = [
        {
            "id": entry.id,
            "rating": float(entry.rating) if entry.rating is not None else None,
            "has_review": getattr(entry, "review", None) is not None,
            "event": _serialize_event(entry.event),
        }
        for entry in page.object_list
    ]
    return JsonResponse(
        {
            "results": results,
            "pagination": _pagination_payload(page, page_size, paginator.count),
        }
    )


@require_GET
def profile_reviews(request, username):
    profile, denied = _profile_content_target(request, username)
    if denied is not None:
        return denied
    sort = request.GET.get("sort", "newest")
    if sort not in ("newest", "most_liked", "oldest", "longest"):
        return JsonResponse(
            {"errors": {"sort": ["Sort must be newest, most_liked, oldest, or longest."]}},
            status=400,
        )
    pagination = _pagination(request, default=20, maximum=100)
    if pagination is None:
        return JsonResponse(
            {"error": "page and page_size must be positive integers"}, status=400
        )
    page_number, page_size = pagination
    lineup = EventArtist.objects.select_related("artist").order_by("position")
    viewer = effective_visibility_viewer(request.user)
    reviews = (
        Review.objects.visible_to(viewer)
        .filter(entry__user=profile)
        .select_related("entry__event__venue__city")
        .prefetch_related(
            Prefetch(
                "entry__event__event_artists",
                queryset=lineup,
                to_attr="_ordered_event_artists",
            )
        )
        .annotate(
            like_count=Count("likes__user_id", distinct=True),
            author_follower_count=Count(
                "entry__user__follower_relationships__follower_id",
                filter=Q(
                    entry__user__follower_relationships__status=FollowStatus.APPROVED
                ),
                distinct=True,
            ),
            body_length=Length("body"),
        )
    )
    if viewer.is_authenticated:
        reviews = reviews.annotate(
            viewer_has_liked=Exists(
                ReviewLike.objects.filter(user=viewer, review_id=OuterRef("pk"))
            )
        )
    ordering = {
        "newest": ("-published_at", "-id"),
        "oldest": ("published_at", "id"),
        "most_liked": (
            "-like_count",
            "-author_follower_count",
            "-published_at",
            "-id",
        ),
        "longest": ("-body_length", "-published_at", "-id"),
    }[sort]
    paginator = Paginator(reviews.order_by(*ordering), page_size)
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        return JsonResponse({"error": "page out of range"}, status=404)
    results = []
    for review in page.object_list:
        item = {
            "id": review.id,
            "event": _serialize_event(review.entry.event),
            "rating": float(review.entry.rating),
            "body": review.body,
            "published_at": review.published_at.isoformat().replace("+00:00", "Z"),
            "like_count": review.like_count,
        }
        if viewer.is_authenticated:
            item["viewer_has_liked"] = review.viewer_has_liked
        results.append(item)
    return JsonResponse(
        {
            "results": results,
            "pagination": _pagination_payload(page, page_size, paginator.count),
        }
    )


def _favorite_resource(request, *, target, model, target_field, limit):
    auth_error = _authentication_required(request)
    if auth_error is not None:
        return auth_error
    if request.method == "PUT":
        try:
            favorite, created = save_favorite(
                user_id=request.user.id, model=model, target_field=target_field,
                target_id=target.id, limit=limit,
            )
        except FavoriteLimitReached:
            return JsonResponse(
                {"errors": {"favorite": [f"You may favorite at most {limit} items of this type."]}},
                status=409,
            )
        return JsonResponse(
            {"favorite": {"is_favorite": True, "added_at": favorite.added_at.isoformat().replace("+00:00", "Z")}},
            status=201 if created else 200,
        )
    remove_favorite(
        user_id=request.user.id, model=model, target_field=target_field,
        target_id=target.id,
    )
    return HttpResponse(status=204)


@require_http_methods(["PUT", "DELETE"])
def event_favorite(request, event_id):
    return _favorite_resource(request, target=_visible_event(event_id), model=FavoriteEvent, target_field="event", limit=3)


@require_http_methods(["PUT", "DELETE"])
def artist_favorite(request, artist_id):
    return _favorite_resource(request, target=get_object_or_404(Artist, pk=artist_id), model=FavoriteArtist, target_field="artist", limit=3)


@require_http_methods(["PUT", "DELETE"])
def venue_favorite(request, venue_id):
    return _favorite_resource(request, target=get_object_or_404(Venue, pk=venue_id), model=FavoriteVenue, target_field="venue", limit=None)


@require_GET
def profile_favorites(request, username):
    profile, denied = _profile_content_target(request, username)
    if denied is not None:
        return denied
    lineup = EventArtist.objects.select_related("artist").order_by("position")
    events = FavoriteEvent.objects.filter(
        user=profile, event__status__in=("active", "unverified")
    ).select_related("event__venue__city").prefetch_related(
        Prefetch("event__event_artists", queryset=lineup, to_attr="_ordered_event_artists")
    ).order_by("added_at", "event_id")
    artists = FavoriteArtist.objects.filter(user=profile).select_related("artist").order_by("added_at", "artist_id")
    return JsonResponse({
        "events": [{"event": _serialize_event(row.event), "added_at": row.added_at.isoformat().replace("+00:00", "Z")} for row in events],
        "artists": [{"artist": _serialize_artist(row.artist), "added_at": row.added_at.isoformat().replace("+00:00", "Z")} for row in artists],
    })


@require_GET
def favorite_venues(request):
    auth_error = _authentication_required(request)
    if auth_error is not None:
        return auth_error
    pagination = _pagination(request, default=20, maximum=100)
    if pagination is None:
        return JsonResponse({"errors": {"page": ["Invalid pagination."]}}, status=400)
    page_number, page_size = pagination
    rows = FavoriteVenue.objects.filter(user=request.user).select_related("venue__city").order_by("added_at", "venue_id")
    paginator = Paginator(rows, page_size)
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        return JsonResponse({"error": "page out of range"}, status=404)
    return JsonResponse({
        "results": [{"venue": _serialize_venue(row.venue), "added_at": row.added_at.isoformat().replace("+00:00", "Z")} for row in page.object_list],
        "pagination": _pagination_payload(page, page_size, paginator.count),
    })


@require_GET
def profile_stats(request, username):
    profile, denied = _profile_content_target(request, username)
    if denied is not None:
        return denied
    viewer = effective_visibility_viewer(request.user)
    entries = DiaryEntry.objects.visible_to(viewer).filter(user=profile)
    rated = entries.filter(rating__isnull=False)
    average = rated.aggregate(value=Avg("rating"))["value"]
    rating_payload = rating_distribution_payload(entries)
    return JsonResponse({
        "statistics": {
            "events_in_been": entries.count(),
            "written_reviews": Review.objects.visible_to(viewer).filter(entry__user=profile).count(),
            "venues_visited": entries.values("event__venue_id").distinct().count(),
            "cities_visited": entries.values("event__venue__city_id").distinct().count(),
            "average_rating_given": ({"state": "empty"} if average is None else {"state": "available", "value": float(average)}),
            "followers": Follow.objects.filter(followee=profile, status=FollowStatus.APPROVED).count(),
            "following": Follow.objects.filter(follower=profile, status=FollowStatus.APPROVED).count(),
        },
        "rating_distribution": rating_payload,
    })


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
    rows = home_feed_rows(
        request.user,
        at=timezone_now(),
        cursor=cursor,
        limit=page_size + 1,
    )
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
        .annotate(
            review_like_count=Count("review__likes"),
            viewer_has_liked=Exists(
                ReviewLike.objects.filter(
                    user=request.user,
                    review_id=OuterRef("review__pk"),
                )
            ),
        )
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
            review.like_count = entry.review_like_count
            serialized_review = serialize_review(review)
            serialized_review["viewer_has_liked"] = entry.viewer_has_liked
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
    viewer = effective_visibility_viewer(request.user)
    if viewer.is_authenticated:
        reviews = reviews.annotate(
            viewer_has_liked=Exists(
                ReviewLike.objects.filter(
                    user=viewer,
                    review_id=OuterRef("pk"),
                )
            ),
            viewer_follows=Exists(
                Follow.objects.filter(
                    follower=viewer,
                    followee_id=OuterRef("entry__user_id"),
                    status=FollowStatus.APPROVED,
                )
            ),
            viewer_has_follow_row=Exists(
                Follow.objects.filter(
                    follower=viewer,
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
                    viewer=viewer,
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
