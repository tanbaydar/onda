import { artistPath, eventPath } from "./entityRoutes.js";

export const HOME_EMPTY_COPY = "No activity from people you follow yet.";

export const HOME_FEED_VERBS = {
  rated_been: "rated",
  will_be_there: "will be at",
  follow: "followed",
  review_like: "liked a review of",
  favorite_event: "favorited",
  favorite_artist: "favorited",
};

export function compactRelativeTime(value, now = new Date()) {
  const elapsed = Math.max(0, now.getTime() - new Date(value).getTime());
  const minutes = Math.floor(elapsed / 60000);
  if (minutes < 60) return `${Math.max(1, minutes)}m`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d`;
  return `${Math.floor(days / 7)}w`;
}

export function feedItemPath(item) {
  if (item.grouped) return `/u/${item.actor.username}`;
  if (item.target.event) return eventPath(item.target.event);
  if (item.target.artist) return artistPath(item.target.artist);
  return `/u/${item.target.user.username}`;
}

const GROUPABLE = new Set(["favorite_event", "favorite_artist", "follow"]);
export function groupFeedItems(items) {
  const grouped = [];
  for (const item of items) {
    const previous = grouped.at(-1);
    if (GROUPABLE.has(item.type) && previous?.type === item.type && previous.actor.id === item.actor.id) {
      previous.grouped.push(item);
    } else grouped.push(GROUPABLE.has(item.type) ? { ...item, grouped: [item] } : item);
  }
  return grouped;
}
