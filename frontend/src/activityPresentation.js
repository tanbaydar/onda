import { eventPath } from "./entityRoutes.js";
import { profilePath } from "./profileRoutes.js";


export function activityNotificationVerb(notification) {
  if (notification.type === "review_like") return "liked your review.";
  if (notification.type === "follow") return "followed you.";
  if (notification.type === "follow_request") return "requested to follow you.";
  return "accepted your follow request.";
}

export function followRequestKey({ user, actor, created_at: createdAt }) {
  return `${(user ?? actor).id}:${createdAt}`;
}

export function activityNotificationPath(notification) {
  return notification.review
    ? eventPath({ id: notification.review.event_id, title: notification.review.event_title })
    : profilePath(notification.actor.username);
}
