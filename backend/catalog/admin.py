from django.contrib import admin

from .models import (
    Artist,
    ArtistIdentity,
    City,
    CityIdentity,
    Event,
    EventArtist,
    EventIdentity,
    Venue,
    VenueIdentity,
)


admin.site.register(
    (
        City,
        Venue,
        Artist,
        Event,
        EventArtist,
        EventIdentity,
        VenueIdentity,
        ArtistIdentity,
        CityIdentity,
    )
)
