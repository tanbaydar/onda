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
  if (item.target.event) return `/events/${item.target.event.id}`;
  if (item.target.artist) return `/artists/${item.target.artist.id}`;
  return `/u/${item.target.user.username}`;
}
