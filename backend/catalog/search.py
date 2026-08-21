from django.contrib.auth import get_user_model
from django.db.models import Case, Count, IntegerField, Q, Value, When
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from catalog.models import Artist, Venue
from catalog.views import _event_queryset, _serialize_event
from users.models import FollowStatus, UserStatus


SCOPES = ("all", "events", "artists", "venues", "people")
GROUP_LIMIT = 5
PAGE_SIZE = 20
MAX_QUERY_LENGTH = 100
MAX_OFFSET = 10_000


def _rank(field, query):
    return Case(
        When(**{f"{field}__iexact": query}, then=Value(0)),
        When(**{f"{field}__istartswith": query}, then=Value(1)),
        default=Value(2),
        output_field=IntegerField(),
    )


def _events(query, city_id=None):
    queryset = _event_queryset().filter(title__icontains=query)
    if city_id is not None:
        queryset = queryset.filter(venue__city_id=city_id)
    return queryset.annotate(
        _match_rank=_rank("title", query),
        _popularity=Count("diary_entries__user_id", distinct=True)
        + Count("will_be_there_entries__user_id", distinct=True),
    ).order_by("_match_rank", "-_popularity", "title", "id")


def _artists(query):
    return Artist.objects.filter(name__icontains=query).annotate(
        _match_rank=_rank("name", query),
        _popularity=Count("favorited_by__user_id", distinct=True)
        + Count("event_artists__event__diary_entries__user_id", distinct=True),
    ).order_by("_match_rank", "-_popularity", "name", "id")


def _venues(query):
    return Venue.objects.filter(name__icontains=query).select_related("city").annotate(
        _match_rank=_rank("name", query),
        _popularity=Count("favorited_by__user_id", distinct=True)
        + Count("events__diary_entries__user_id", distinct=True),
    ).order_by("_match_rank", "-_popularity", "name", "id")


def _people(query):
    User = get_user_model()
    return User.objects.filter(
        Q(username__icontains=query) | Q(display_name__icontains=query),
        status=UserStatus.ACTIVE,
        username__isnull=False,
    ).annotate(
        _username_rank=_rank("username", query),
        _display_rank=_rank("display_name", query),
        _popularity=Count(
            "follower_relationships__follower_id",
            filter=Q(follower_relationships__status=FollowStatus.APPROVED),
            distinct=True,
        ),
    ).annotate(
        _match_rank=Case(
            When(_username_rank__lt=2, then="_username_rank"),
            default="_display_rank",
            output_field=IntegerField(),
        )
    ).order_by("_match_rank", "-_popularity", "display_name", "id")


def _serialize_artist(artist):
    return {"id": artist.id, "name": artist.name}


def _serialize_venue(venue):
    return {
        "id": venue.id,
        "name": venue.name,
        "city": {"id": venue.city.id, "name": venue.city.name},
    }


def _serialize_person(user):
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "avatar": user.avatar,
    }


GROUPS = {
    "events": (_events, _serialize_event),
    "artists": (_artists, _serialize_artist),
    "venues": (_venues, _serialize_venue),
    "people": (_people, _serialize_person),
}


def _page(queryset, serializer, *, offset, limit):
    total = queryset.count()
    rows = list(queryset[offset : offset + limit])
    next_offset = offset + len(rows)
    return {
        "results": [serializer(row) for row in rows],
        "total": total,
        "next_cursor": str(next_offset) if next_offset < total else None,
    }


@require_GET
def search(request):
    query = request.GET.get("q", "").strip()
    scope = request.GET.get("scope", "all")
    if len(query) < 1:
        return JsonResponse({"errors": {"q": ["Enter at least one character."]}}, status=400)
    if len(query) > MAX_QUERY_LENGTH:
        return JsonResponse(
            {"errors": {"q": [f"Enter at most {MAX_QUERY_LENGTH} characters."]}},
            status=400,
        )
    if scope not in SCOPES:
        return JsonResponse({"errors": {"scope": ["Invalid search scope."]}}, status=400)
    try:
        offset = int(request.GET.get("cursor", "0"))
        city_id = int(request.GET["city_id"]) if "city_id" in request.GET else None
    except (TypeError, ValueError):
        return JsonResponse({"errors": {"cursor": ["Invalid search cursor."]}}, status=400)
    if offset < 0 or offset > MAX_OFFSET:
        return JsonResponse({"errors": {"cursor": ["Invalid search cursor."]}}, status=400)

    if scope == "all":
        groups = {}
        for name, (builder, serializer) in GROUPS.items():
            queryset = builder(query, city_id) if name == "events" else builder(query)
            groups[name] = _page(queryset, serializer, offset=0, limit=GROUP_LIMIT)
        return JsonResponse({"query": query, "groups": groups})

    builder, serializer = GROUPS[scope]
    queryset = builder(query, city_id) if scope == "events" else builder(query)
    return JsonResponse(
        {"query": query, "scope": scope, **_page(queryset, serializer, offset=offset, limit=PAGE_SIZE)}
    )
