from zoneinfo import ZoneInfo

from django.core.paginator import EmptyPage, Paginator
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from catalog.models import (
    Artist,
    City,
    Event,
    EventArtist,
    EventStatus,
    Venue,
)


DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
SCOPE_MODELS = {
    "city_id": City,
    "venue_id": Venue,
    "artist_id": Artist,
}
VISIBLE_EVENT_STATUSES = (
    EventStatus.ACTIVE,
    EventStatus.UNVERIFIED,
)


def _positive_integer(request, name, *, default=None, maximum=None):
    value = request.GET.get(name)
    if value is None:
        if default is not None:
            return default
        raise ValueError(f"{name} is required")
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a positive integer") from exc
    if parsed < 1:
        raise ValueError(f"{name} must be a positive integer")
    if maximum is not None and parsed > maximum:
        raise ValueError(f"{name} cannot exceed {maximum}")
    return parsed


def _serialize_event(event):
    return {
        "id": event.id,
        "title": event.title,
        "event_date": event.event_date.isoformat(),
        "start_time": (
            event.start_time.isoformat()
            if event.start_time is not None
            else None
        ),
        "cover_image_url": event.cover_image_url,
        "venue": {
            "id": event.venue.id,
            "name": event.venue.name,
            "city": {
                "id": event.venue.city.id,
                "name": event.venue.city.name,
                "timezone": event.venue.city.timezone,
            },
        },
        "artists": [
            {
                "id": event_artist.artist.id,
                "name": event_artist.artist.name,
                "position": event_artist.position,
            }
            for event_artist in event._ordered_event_artists
        ],
    }


def _serialize_venue(venue):
    return {
        "id": venue.id,
        "name": venue.name,
        "city": {
            "id": venue.city.id,
            "name": venue.city.name,
            "region_code": venue.city.region_code,
            "region_name": venue.city.region_name,
            "country_code": venue.city.country_code,
            "timezone": venue.city.timezone,
        },
    }


def _serialize_artist(artist):
    return {
        "id": artist.id,
        "name": artist.name,
        "image_url": artist.image_url,
    }


def _serialize_city_list_item(city):
    return {
        "id": city.id,
        "name": city.name,
        "region_code": city.region_code,
        "country_code": city.country_code,
        "timezone": city.timezone,
    }


def _event_queryset():
    lineup = EventArtist.objects.select_related("artist").order_by("position")
    return (
        Event.objects.filter(status__in=VISIBLE_EVENT_STATUSES)
        .select_related("venue__city")
        .prefetch_related(
            Prefetch(
                "event_artists",
                queryset=lineup,
                to_attr="_ordered_event_artists",
            )
        )
    )


def _scope_filter(scope_name, scope):
    if scope_name == "city_id":
        return Q(venue__city=scope)
    if scope_name == "venue_id":
        return Q(venue=scope)
    return Q(event_artists__artist=scope)


def _scope_cities(scope_name, scope):
    if scope_name == "city_id":
        return [scope]
    if scope_name == "venue_id":
        return [scope.city]
    return list(
        City.objects.filter(
            venues__events__event_artists__artist=scope
        ).distinct()
    )


def _date_filter(cities, when):
    date_filter = Q(pk__in=[])
    lookup = "event_date__gte" if when == "upcoming" else "event_date__lt"
    now = timezone.now()
    for city in cities:
        local_today = now.astimezone(ZoneInfo(city.timezone)).date()
        date_filter |= Q(
            **{
                "venue__city_id": city.id,
                lookup: local_today,
            }
        )
    return date_filter


def event_list(request):
    when = request.GET.get("when")
    if when not in ("upcoming", "past"):
        return JsonResponse(
            {"error": "when must be upcoming or past"},
            status=400,
        )

    supplied_scopes = [
        name for name in SCOPE_MODELS if name in request.GET
    ]
    if len(supplied_scopes) != 1:
        return JsonResponse(
            {
                "error": (
                    "exactly one of city_id, venue_id, or artist_id "
                    "is required"
                )
            },
            status=400,
        )

    scope_name = supplied_scopes[0]
    try:
        scope_id = _positive_integer(request, scope_name)
        page_number = _positive_integer(request, "page", default=1)
        page_size = _positive_integer(
            request,
            "page_size",
            default=DEFAULT_PAGE_SIZE,
            maximum=MAX_PAGE_SIZE,
        )
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    scope_queryset = SCOPE_MODELS[scope_name].objects
    if scope_name == "venue_id":
        scope_queryset = scope_queryset.select_related("city")
    scope = get_object_or_404(scope_queryset, pk=scope_id)
    order_by = (
        ("event_date", "id")
        if when == "upcoming"
        else ("-event_date", "-id")
    )
    events = (
        _event_queryset()
        .filter(
            _scope_filter(scope_name, scope),
            _date_filter(_scope_cities(scope_name, scope), when),
        )
        .order_by(*order_by)
    )
    paginator = Paginator(events, page_size)
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        return JsonResponse({"error": "page out of range"}, status=404)

    return JsonResponse(
        {
            "results": [_serialize_event(event) for event in page.object_list],
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


def city_list(request):
    cities = City.objects.order_by("name")
    return JsonResponse(
        {
            "results": [
                _serialize_city_list_item(city)
                for city in cities
            ]
        }
    )


def venue_detail(request, venue_id):
    venue = get_object_or_404(
        Venue.objects.select_related("city"),
        pk=venue_id,
    )
    payload = _serialize_venue(venue)
    from users.auth_services import effective_visibility_viewer
    viewer = effective_visibility_viewer(request.user)
    if viewer.is_authenticated:
        from users.models import FavoriteVenue
        favorite = FavoriteVenue.objects.filter(user=viewer, venue=venue).first()
        payload["viewer_favorite"] = {"is_favorite": favorite is not None, "added_at": favorite.added_at.isoformat().replace("+00:00", "Z") if favorite else None}
    return JsonResponse(payload)


def artist_detail(request, artist_id):
    artist = get_object_or_404(Artist, pk=artist_id)
    payload = _serialize_artist(artist)
    from users.auth_services import effective_visibility_viewer
    viewer = effective_visibility_viewer(request.user)
    if viewer.is_authenticated:
        from users.models import FavoriteArtist
        favorite = FavoriteArtist.objects.filter(user=viewer, artist=artist).first()
        payload["viewer_favorite"] = {"is_favorite": favorite is not None, "added_at": favorite.added_at.isoformat().replace("+00:00", "Z") if favorite else None}
    return JsonResponse(payload)


def event_detail(request, event_id):
    event = get_object_or_404(_event_queryset(), pk=event_id)
    from users.models import DiaryEntry, FavoriteEvent, WillBeThere
    from users.services import (
        NOT_STARTED_MESSAGE,
        event_is_loggable,
        event_rating_summary,
        rating_distribution_payload,
        serialize_diary_entry,
        viewer_will_be_there_state,
    )
    from users.auth_services import effective_visibility_viewer

    payload = _serialize_event(event)
    loggable = event_is_loggable(event)
    payload["rating_summary"] = event_rating_summary(event)
    payload["rating_distribution"] = rating_distribution_payload(
        DiaryEntry.objects.for_aggregation().filter(event=event),
        minimum_count=3,
    )
    payload["been"] = {
        "loggable": loggable,
        "unavailable_reason": None if loggable else NOT_STARTED_MESSAGE,
    }
    payload["will_be_there_summary"] = {
        "active_count": WillBeThere.objects.active_at(timezone.now()).filter(event=event).count()
    }
    viewer = effective_visibility_viewer(request.user)
    if viewer.is_authenticated:
        entry = (
            DiaryEntry.objects.visible_to(viewer)
            .select_related("review")
            .filter(user=viewer, event=event)
            .first()
        )
        payload["viewer_entry"] = (
            serialize_diary_entry(entry) if entry is not None else None
        )
        payload["viewer_will_be_there"] = viewer_will_be_there_state(
            user=viewer,
            event=event,
        )
        favorite = FavoriteEvent.objects.filter(user=viewer, event=event).first()
        payload["viewer_favorite"] = {"is_favorite": favorite is not None, "added_at": favorite.added_at.isoformat().replace("+00:00", "Z") if favorite else None}
    return JsonResponse(payload)
