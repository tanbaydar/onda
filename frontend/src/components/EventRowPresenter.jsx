import { Link } from "react-router-dom";

import { compactLineup } from "../discoverPresentation.js";
import { eventPath } from "../entityRoutes.js";
import { formatCompactEventDateTime, formatEventDateTime } from "../formatEventDateTime.js";
import { compactRelativeTime, feedItemPath, HOME_FEED_VERBS } from "../homeFeedPresentation.js";
import { recentRatingVisible } from "../polishPresentation.js";
import FeedReviewExcerpt from "./FeedReviewExcerpt.jsx";
import ImageSlot from "./ImageSlot.jsx";
import ProfileAvatar from "./ProfileAvatar.jsx";
import RatingStars from "./RatingStars.jsx";

function diaryDate(event) {
  const date = new Date(`${event.event_date}T${event.start_time ?? "00:00:00"}`);
  const datePart = new Intl.DateTimeFormat("en-US", { weekday: "short", day: "numeric", month: "long" }).format(date);
  if (!event.start_time) return datePart;
  const timePart = new Intl.DateTimeFormat("en-US", { hour: "numeric", minute: "2-digit" }).format(date).toLowerCase();
  return `${datePart}, ${timePart}`;
}

function LedgerEventRow({ event, omittedArtistId = null, showVenue = true, onFocus, compact = false, variant }) {
  const lineup = compactLineup(event.artists, omittedArtistId);
  const venueName = event.venue?.name?.trim();
  const venueIsTba = !venueName || venueName.toUpperCase() === "TBA";
  const dateTime = event.start_time ? `${event.event_date}T${event.start_time}` : event.event_date;
  const overlay = variant === "compact-overlay";

  return (
    <li>
      <Link className={`discover-event-row${compact ? " discover-event-row-compact" : ""}${overlay ? " discover-event-row-overlay" : ""}`} to={eventPath(event)} onFocus={onFocus}>
        <ImageSlot className={`discover-event-flier${compact ? " discover-event-flier-compact" : ""}`} name={event.title} src={event.cover_image_url} referrerPolicy="no-referrer" />
        <span className="discover-event-copy">
          <strong className="discover-event-title">{event.title}</strong>
          <span className="discover-event-meta">
            <time dateTime={dateTime}>{formatCompactEventDateTime(event.event_date, event.start_time)}</time>
            {showVenue ? <><span aria-hidden="true"> · </span><span className={venueIsTba ? "discover-venue-tba" : ""}>{venueIsTba ? "venue TBA" : venueName}</span></> : null}
            {recentRatingVisible(event.rating_summary) ? <><span aria-hidden="true"> · </span><RatingStars className="discover-recent-stars" value={event.rating_summary.average} /></> : null}
          </span>
          {lineup ? <span className="discover-event-lineup">{lineup}</span> : null}
        </span>
      </Link>
    </li>
  );
}

function ProfileDiaryEventRow({ event, rating, hasReview = false, onDeleteReview = null, reviewPending = false }) {
  return (
    <li className={onDeleteReview ? "profile-diary-item has-review-action" : "profile-diary-item"}>
      <Link className="profile-diary-row" to={eventPath(event)}>
        <ImageSlot className="profile-diary-thumb" name={event.title} src={event.cover_image_url} referrerPolicy="no-referrer" />
        <strong className="profile-diary-title">{event.title}</strong>
        <span className="profile-diary-meta"><time dateTime={event.start_time ? `${event.event_date}T${event.start_time}` : event.event_date}>{diaryDate(event)}</time><span className="profile-diary-separator"> · </span><span className="profile-diary-venue">{event.venue.name}, {event.venue.city.name}</span></span>
        <span className="profile-diary-judgment">
          {rating === null ? <span className="profile-unrated">Unrated attendance</span> : <RatingStars className="profile-row-stars" value={rating} />}
          {hasReview && !onDeleteReview ? <small>Written review</small> : null}
        </span>
      </Link>
      {onDeleteReview ? <button className="profile-diary-delete" type="button" disabled={reviewPending} onClick={onDeleteReview}>Delete review</button> : null}
    </li>
  );
}

function FeedEventRow({ item }) {
  const event = item.target.event;
  const isRated = item.type === "rated_been";
  return (
    <Link className={`home-feed-item home-feed-event${isRated ? " home-feed-rich" : ""}`} to={feedItemPath(item)}>
      <ImageSlot className="home-feed-flier" name={event.title} src={event.cover_image_url} />
      <span className="home-feed-copy">
        <span className="home-feed-actor-line">
          <ProfileAvatar profile={item.actor} small />
          <strong className="home-feed-actor-name">{item.actor.display_name}</strong>
          <span className="home-feed-verb">{HOME_FEED_VERBS[item.type]}</span>
          <time dateTime={item.activity_at}>{compactRelativeTime(item.activity_at)}</time>
        </span>
        <strong className="home-feed-object">{event.title}</strong>
        {isRated ? <RatingStars className="home-feed-stars" value={item.context.rating} /> : null}
        {item.type === "will_be_there" ? <span className="home-feed-meta">{formatEventDateTime(event.event_date, event.start_time)} · {event.venue.name}</span> : null}
        {isRated && item.context.review ? <FeedReviewExcerpt>{item.context.review.body}</FeedReviewExcerpt> : null}
      </span>
    </Link>
  );
}

export default function EventRowPresenter({ variant = "standard-ledger", ...props }) {
  if (variant === "profile-diary") return <ProfileDiaryEventRow {...props} />;
  if (variant === "feed-object") return <FeedEventRow {...props} />;
  return <LedgerEventRow {...props} variant={variant} />;
}
