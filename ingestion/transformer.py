import json
from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Any

from django.db import transaction
from django.utils import timezone

from catalog.models import (
    Artist,
    ArtistIdentity,
    CityIdentity,
    Event,
    EventArtist,
    EventIdentity,
    Venue,
    VenueIdentity,
)
from config.sources import Source
from ingestion.models import (
    RawIngest,
    RawProcessingStatus,
    RejectedIngest,
    RejectionReason,
)


@dataclass(frozen=True)
class TransformOutcome:
    admitted_count: int
    quarantined_count: int
    dropped_count: int
    observed_source_ids: frozenset[str]


@dataclass(frozen=True)
class ArtistDTO:
    source_id: str
    name: str


@dataclass(frozen=True)
class EventDTO:
    source_id: str
    title: str
    date_text: str
    start_time_text: str | None
    cover_image_url: str | None
    venue_source_id: str
    venue_name: str
    artists: tuple[ArtistDTO, ...]


class EventRejection(Exception):
    def __init__(self, reason: str, detail: str | None = None):
        super().__init__(reason)
        self.reason = reason
        self.detail = detail


def _empty_outcome() -> TransformOutcome:
    return TransformOutcome(
        admitted_count=0,
        quarantined_count=0,
        dropped_count=0,
        observed_source_ids=frozenset(),
    )


def _listing_events(response_body: str | None) -> list[Any]:
    if response_body is None:
        raise ValueError("response body is absent")
    payload = json.loads(response_body)
    if not isinstance(payload, dict):
        raise ValueError("payload root is not an object")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise ValueError("data envelope is absent or invalid")
    event_listings = data.get("eventListings")
    if not isinstance(event_listings, dict):
        raise ValueError("eventListings envelope is absent or invalid")
    listings = event_listings.get("data")
    if not isinstance(listings, list):
        raise ValueError("eventListings.data is absent or invalid")
    return listings


def _event_ref(listing: Any) -> str | None:
    if not isinstance(listing, dict):
        return None
    event = listing.get("event")
    if not isinstance(event, dict):
        return None
    source_id = event.get("id")
    if not isinstance(source_id, str) or not source_id:
        return None
    return source_id


def _parse_event(listing: Any) -> EventDTO:
    if not isinstance(listing, dict):
        raise EventRejection(
            RejectionReason.PARSE_FAILURE,
            "listing wrapper is not an object",
        )
    event = listing.get("event")
    if not isinstance(event, dict):
        raise EventRejection(
            RejectionReason.PARSE_FAILURE,
            "event is absent or is not an object",
        )

    source_id = event.get("id")
    if not isinstance(source_id, str) or not source_id:
        raise EventRejection(
            RejectionReason.PARSE_FAILURE,
            "event.id is absent or invalid",
        )

    title = event.get("title")
    if not isinstance(title, str):
        raise EventRejection(
            RejectionReason.PARSE_FAILURE,
            "event.title is absent or is not a string",
        )

    date_text = event.get("date")
    if not isinstance(date_text, str):
        raise EventRejection(
            RejectionReason.PARSE_FAILURE,
            "event.date is absent or is not a string",
        )

    start_time_text = event.get("startTime")
    if start_time_text is not None and not isinstance(start_time_text, str):
        raise EventRejection(
            RejectionReason.PARSE_FAILURE,
            "event.startTime is not a string or null",
        )

    cover_image_url = event.get("flyerFront")
    if cover_image_url is not None and not isinstance(cover_image_url, str):
        raise EventRejection(
            RejectionReason.PARSE_FAILURE,
            "event.flyerFront is not a string or null",
        )

    venue = event.get("venue")
    if not isinstance(venue, dict):
        raise EventRejection(
            RejectionReason.PARSE_FAILURE,
            "event.venue is absent or is not an object",
        )
    venue_source_id = venue.get("id")
    venue_name = venue.get("name")
    if not isinstance(venue_source_id, str) or not venue_source_id:
        raise EventRejection(
            RejectionReason.PARSE_FAILURE,
            "event.venue.id is absent or invalid",
        )
    if not isinstance(venue_name, str):
        raise EventRejection(
            RejectionReason.PARSE_FAILURE,
            "event.venue.name is absent or is not a string",
        )

    raw_artists = event.get("artists")
    if raw_artists is None:
        raw_artists = []
    if not isinstance(raw_artists, list):
        raise EventRejection(
            RejectionReason.PARSE_FAILURE,
            "event.artists is not a collection or null",
        )

    artists = []
    for raw_artist in raw_artists:
        if not isinstance(raw_artist, dict):
            continue
        artist_source_id = raw_artist.get("id")
        if not isinstance(artist_source_id, str) or not artist_source_id:
            continue
        artist_name = raw_artist.get("name")
        if not isinstance(artist_name, str):
            raise EventRejection(
                RejectionReason.PARSE_FAILURE,
                "an ID-bearing artist has no string name",
            )
        artists.append(
            ArtistDTO(
                source_id=artist_source_id,
                name=artist_name,
            )
        )

    return EventDTO(
        source_id=source_id,
        title=title,
        date_text=date_text,
        start_time_text=start_time_text,
        cover_image_url=cover_image_url,
        venue_source_id=venue_source_id,
        venue_name=venue_name,
        artists=tuple(artists),
    )


def _parse_iso_datetime(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    return datetime.fromisoformat(normalized)


def _event_date(value: str) -> date:
    try:
        return _parse_iso_datetime(value).date()
    except ValueError as exc:
        raise EventRejection(
            RejectionReason.BAD_DATE,
            "event.date is not parseable",
        ) from exc


def _event_start_time(value: str | None) -> time | None:
    if value is None:
        return None
    try:
        parsed = _parse_iso_datetime(value).time()
    except ValueError as exc:
        raise EventRejection(
            RejectionReason.PARSE_FAILURE,
            "event.startTime is not parseable",
        ) from exc
    return parsed.replace(tzinfo=None)


def _resolve_venue(*, dto: EventDTO, source: str, city) -> Venue:
    try:
        identity = VenueIdentity.objects.select_related("venue").get(
            source=source,
            source_id=dto.venue_source_id,
        )
    except VenueIdentity.DoesNotExist:
        venue = Venue.objects.create(name=dto.venue_name, city=city)
        VenueIdentity.objects.create(
            venue=venue,
            source=source,
            source_id=dto.venue_source_id,
        )
        return venue

    venue = identity.venue
    changed_fields = []
    if venue.name != dto.venue_name:
        venue.name = dto.venue_name
        changed_fields.append("name")
    if venue.city_id != city.id:
        venue.city = city
        changed_fields.append("city")
    if changed_fields:
        venue.save(update_fields=changed_fields)
    return venue


def _resolve_artist(*, dto: ArtistDTO, source: str) -> Artist:
    try:
        identity = ArtistIdentity.objects.select_related("artist").get(
            source=source,
            source_id=dto.source_id,
        )
    except ArtistIdentity.DoesNotExist:
        artist = Artist.objects.create(name=dto.name)
        ArtistIdentity.objects.create(
            artist=artist,
            source=source,
            source_id=dto.source_id,
        )
        return artist

    artist = identity.artist
    if artist.name != dto.name:
        artist.name = dto.name
        artist.save(update_fields=["name"])
    return artist


def _upsert_event(
    *,
    dto: EventDTO,
    source: str,
    venue: Venue,
    artists: list[Artist],
    observed_at: datetime,
) -> Event:
    parsed_date = _event_date(dto.date_text)
    parsed_start_time = _event_start_time(dto.start_time_text)

    try:
        identity = EventIdentity.objects.select_related("event").get(
            source=source,
            source_id=dto.source_id,
        )
    except EventIdentity.DoesNotExist:
        event = Event.objects.create(
            title=dto.title,
            event_date=parsed_date,
            start_time=parsed_start_time,
            venue=venue,
            cover_image_url=dto.cover_image_url,
            status="active",
        )
        identity = EventIdentity.objects.create(
            event=event,
            source=source,
            source_id=dto.source_id,
            last_seen_at=observed_at,
            misses=0,
        )
    else:
        event = identity.event
        event.title = dto.title
        event.event_date = parsed_date
        event.start_time = parsed_start_time
        event.venue = venue
        event.cover_image_url = dto.cover_image_url
        event.status = "active"
        event.save(
            update_fields=[
                "title",
                "event_date",
                "start_time",
                "venue",
                "cover_image_url",
                "status",
            ]
        )
        identity.last_seen_at = observed_at
        identity.misses = 0
        identity.save(update_fields=["last_seen_at", "misses"])

    desired_lineup = [
        (artist.id, position)
        for position, artist in enumerate(artists, start=1)
    ]
    existing_lineup = list(
        EventArtist.objects.filter(event=event)
        .order_by("position")
        .values_list("artist_id", "position")
    )
    if existing_lineup != desired_lineup:
        EventArtist.objects.filter(event=event).delete()
        EventArtist.objects.bulk_create(
            [
                EventArtist(
                    event=event,
                    artist_id=artist_id,
                    position=position,
                )
                for artist_id, position in desired_lineup
            ]
        )
    return event


def _admit_event(*, dto: EventDTO, source: str, city) -> None:
    with transaction.atomic():
        venue = _resolve_venue(dto=dto, source=source, city=city)

        if not dto.artists:
            raise EventRejection(RejectionReason.NO_ARTIST)

        if not dto.title.strip():
            raise EventRejection(RejectionReason.EMPTY_TITLE)

        parsed_artists = [
            _resolve_artist(dto=artist_dto, source=source)
            for artist_dto in dto.artists
        ]
        _upsert_event(
            dto=dto,
            source=source,
            venue=venue,
            artists=parsed_artists,
            observed_at=timezone.now(),
        )


def _record_rejection(
    *,
    raw_ingest: RawIngest,
    entity_index: int,
    entity_ref: str | None,
    rejection: EventRejection,
) -> None:
    with transaction.atomic():
        RejectedIngest.objects.get_or_create(
            raw_ingest=raw_ingest,
            entity_index=entity_index,
            defaults={
                "entity_ref": entity_ref,
                "reason": rejection.reason,
                "detail": rejection.detail,
                "rejected_at": timezone.now(),
            },
        )


def transform(raw_ingest_row: RawIngest) -> TransformOutcome:
    source = raw_ingest_row.seed.source
    if source != Source.RA:
        raise ValueError(f"Unsupported source registry value: {source!r}")

    city_identity = CityIdentity.objects.select_related("city").get(
        source=source,
        source_id=raw_ingest_row.seed.area_ref,
    )

    try:
        listings = _listing_events(raw_ingest_row.response_body)
    except (json.JSONDecodeError, TypeError, ValueError):
        raw_ingest_row.processing_status = RawProcessingStatus.FAILED
        raw_ingest_row.save(update_fields=["processing_status"])
        return _empty_outcome()

    admitted_count = 0
    quarantined_count = 0
    observed_source_ids = set()

    for entity_index, listing in enumerate(listings):
        entity_ref = _event_ref(listing)
        if entity_ref is not None:
            observed_source_ids.add(entity_ref)

        try:
            dto = _parse_event(listing)
            _admit_event(
                dto=dto,
                source=source,
                city=city_identity.city,
            )
        except EventRejection as rejection:
            _record_rejection(
                raw_ingest=raw_ingest_row,
                entity_index=entity_index,
                entity_ref=entity_ref,
                rejection=rejection,
            )
            quarantined_count += 1
        else:
            admitted_count += 1

    raw_ingest_row.processing_status = RawProcessingStatus.PROCESSED
    raw_ingest_row.save(update_fields=["processing_status"])
    return TransformOutcome(
        admitted_count=admitted_count,
        quarantined_count=quarantined_count,
        dropped_count=0,
        observed_source_ids=frozenset(observed_source_ids),
    )
