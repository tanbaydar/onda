from django.urls import path

from .views import diary_list, event_been, event_been_rating


urlpatterns = [
    path("me/been/", diary_list, name="diary-list"),
    path("events/<int:event_id>/been/", event_been, name="event-been"),
    path(
        "events/<int:event_id>/been/rating/",
        event_been_rating,
        name="event-been-rating",
    ),
]
