from django.urls import path

from .views import (
    accept_request,
    decline_request,
    diary_list,
    event_been,
    event_been_rating,
    event_been_review,
    event_review_list,
    event_circle,
    follow_resource,
    home_feed,
    notification_list,
    notification_read,
    notifications_read_all,
    pending_follow_requests,
    privacy_detail,
    review_like,
    will_be_there_resource,
    public_will_be_there,
    circle_will_be_there,
)


urlpatterns = [
    path("me/home/", home_feed, name="home-feed"),
    path("me/been/", diary_list, name="diary-list"),
    path("me/privacy/", privacy_detail, name="privacy-detail"),
    path(
        "me/follow-requests/",
        pending_follow_requests,
        name="pending-follow-request-list",
    ),
    path(
        "me/follow-requests/<int:follower_id>/accept/",
        accept_request,
        name="follow-request-accept",
    ),
    path(
        "me/follow-requests/<int:follower_id>/decline/",
        decline_request,
        name="follow-request-decline",
    ),
    path("me/notifications/", notification_list, name="notification-list"),
    path(
        "me/notifications/read-all/",
        notifications_read_all,
        name="notifications-read-all",
    ),
    path(
        "me/notifications/<int:notification_id>/read/",
        notification_read,
        name="notification-read",
    ),
    path(
        "users/<int:user_id>/follow/",
        follow_resource,
        name="follow-resource",
    ),
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
        "events/<int:event_id>/circle/",
        event_circle,
        name="event-circle",
    ),
    path(
        "reviews/<int:review_id>/like/",
        review_like,
        name="review-like",
    ),
    path(
        "events/<int:event_id>/will-be-there/",
        will_be_there_resource,
        name="will-be-there-resource",
    ),
    path(
        "events/<int:event_id>/will-be-there/public/",
        public_will_be_there,
        name="will-be-there-public",
    ),
    path(
        "events/<int:event_id>/will-be-there/circle/",
        circle_will_be_there,
        name="will-be-there-circle",
    ),
]
