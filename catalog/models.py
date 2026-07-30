from django.db import models

from config.sources import Source


class EventStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    UNVERIFIED = "unverified", "Unverified"
    HIDDEN = "hidden", "Hidden"


class City(models.Model):
    name = models.CharField(max_length=120)
    region_code = models.CharField(max_length=20, null=True, blank=True)
    region_name = models.CharField(max_length=120, null=True, blank=True)
    country_code = models.CharField(max_length=2)
    timezone = models.CharField(max_length=64)

    class Meta:
        db_table = "CITY"
        constraints = [
            models.UniqueConstraint(
                fields=("country_code", "region_code", "name"),
                name="uq_city_country_region_name",
            ),
        ]


class Venue(models.Model):
    name = models.CharField(max_length=255)
    city = models.ForeignKey(
        City,
        db_column="city_id",
        on_delete=models.RESTRICT,
        related_name="venues",
    )

    class Meta:
        db_table = "VENUE"


class Artist(models.Model):
    name = models.CharField(max_length=255)
    image_url = models.URLField(max_length=2048, null=True, blank=True)

    class Meta:
        db_table = "ARTIST"


class Event(models.Model):
    title = models.CharField(max_length=500)
    event_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    venue = models.ForeignKey(
        Venue,
        db_column="venue_id",
        db_index=False,
        on_delete=models.RESTRICT,
        related_name="events",
    )
    cover_image_url = models.URLField(max_length=2048, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=EventStatus,
        default=EventStatus.ACTIVE,
    )

    class Meta:
        db_table = "EVENT"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=EventStatus.values),
                name="ck_event_status",
            ),
        ]
        indexes = [
            models.Index(
                fields=("status", "event_date"),
                name="ix_event_status_date",
            ),
            models.Index(
                fields=("venue", "event_date"),
                name="ix_event_venue_date",
            ),
        ]


class EventArtist(models.Model):
    event = models.ForeignKey(
        Event,
        db_column="event_id",
        db_index=False,
        on_delete=models.CASCADE,
        related_name="event_artists",
    )
    artist = models.ForeignKey(
        Artist,
        db_column="artist_id",
        on_delete=models.RESTRICT,
        related_name="event_artists",
    )
    position = models.IntegerField()

    class Meta:
        db_table = "EVENT_ARTIST"
        constraints = [
            models.UniqueConstraint(
                fields=("event", "artist"),
                name="uq_event_artist_pair",
            ),
            models.UniqueConstraint(
                fields=("event", "position"),
                name="uq_event_artist_position",
            ),
        ]


class EventIdentity(models.Model):
    event = models.ForeignKey(
        Event,
        db_column="event_id",
        db_index=False,
        on_delete=models.CASCADE,
        related_name="external_identities",
    )
    source = models.CharField(max_length=50, choices=Source)
    source_id = models.CharField(max_length=255)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    misses = models.IntegerField(default=0)

    class Meta:
        db_table = "EVENT_IDENTITY"
        constraints = [
            models.UniqueConstraint(
                fields=("source", "source_id"),
                name="uq_event_identity_external",
            ),
            models.UniqueConstraint(
                fields=("event", "source"),
                name="uq_event_identity_canonical_source",
            ),
        ]


class VenueIdentity(models.Model):
    venue = models.ForeignKey(
        Venue,
        db_column="venue_id",
        db_index=False,
        on_delete=models.CASCADE,
        related_name="external_identities",
    )
    source = models.CharField(max_length=50, choices=Source)
    source_id = models.CharField(max_length=255)

    class Meta:
        db_table = "VENUE_IDENTITY"
        constraints = [
            models.UniqueConstraint(
                fields=("source", "source_id"),
                name="uq_venue_identity_external",
            ),
            models.UniqueConstraint(
                fields=("venue", "source"),
                name="uq_venue_identity_canonical_source",
            ),
        ]


class ArtistIdentity(models.Model):
    artist = models.ForeignKey(
        Artist,
        db_column="artist_id",
        db_index=False,
        on_delete=models.CASCADE,
        related_name="external_identities",
    )
    source = models.CharField(max_length=50, choices=Source)
    source_id = models.CharField(max_length=255)

    class Meta:
        db_table = "ARTIST_IDENTITY"
        constraints = [
            models.UniqueConstraint(
                fields=("source", "source_id"),
                name="uq_artist_identity_external",
            ),
            models.UniqueConstraint(
                fields=("artist", "source"),
                name="uq_artist_identity_canonical_source",
            ),
        ]
