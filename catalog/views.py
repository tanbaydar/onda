from zoneinfo import ZoneInfo

from django.core.paginator import EmptyPage, Paginator
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from catalog.models import City, Event, EventArtist, EventStatus


DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


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


def event_list(request):
    if request.GET.get("when") != "upcoming":
        return JsonResponse(
            {"error": "when must be upcoming"},
            status=400,
        )

    try:
        city_id = _positive_integer(request, "city_id")
        page_number = _positive_integer(request, "page", default=1)
        page_size = _positive_integer(
            request,
            "page_size",
            default=DEFAULT_PAGE_SIZE,
            maximum=MAX_PAGE_SIZE,
        )
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    city = get_object_or_404(City, pk=city_id)
    local_today = timezone.now().astimezone(ZoneInfo(city.timezone)).date()
    lineup = EventArtist.objects.select_related("artist").order_by("position")
    events = (
        Event.objects.filter(
            venue__city=city,
            event_date__gte=local_today,
            status__in=(
                EventStatus.ACTIVE,
                EventStatus.UNVERIFIED,
            ),
        )
        .select_related("venue__city")
        .prefetch_related(
            Prefetch(
                "event_artists",
                queryset=lineup,
                to_attr="_ordered_event_artists",
            )
        )
        .order_by("event_date", "id")
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
