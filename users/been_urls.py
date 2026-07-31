from django.urls import path

from .views import (
    diary_list,
    event_been,
    event_been_rating,
    event_been_review,
    event_review_list,
    review_like,
)


urlpatterns = [
    path("me/been/", diary_list, name="diary-list"),
    path("events/<int:event_id>/been/", event_been, name="event-been"),
    path(
        "events/<int:event_id>/been/rating/",
        event_been_rating,
        name="event-been-rating",
    ),
    path(
        "events/<int:event_id>/been/review/",
        event_been_review,
        name="event-been-review",
    ),
    path(
        "events/<int:event_id>/reviews/",
        event_review_list,
        name="event-review-list",
    ),
    path(
        "reviews/<int:review_id>/like/",
        review_like,
        name="review-like",
    ),
]
