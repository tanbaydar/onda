import { Link } from "react-router-dom";

import { compactLineup } from "../discoverPresentation.js";
import { eventPath } from "../entityRoutes.js";
import { eventIsPast } from "../eventTime.js";
import { formatCompactEventDateTime, formatEventDateTime } from "../formatEventDateTime.js";
import { compactRelativeTime, feedItemPath, homeFeedVerb } from "../homeFeedPresentation.js";
import { pluralize } from "../lib/plural.js";
import { recentRatingVisible } from "../polishPresentation.js";
import FeedReviewExcerpt from "./FeedReviewExcerpt.jsx";
import ImageSlot from "./ImageSlot.jsx";
import ProfileAvatar from "./ProfileAvatar.jsx";
import RatingStars from "./RatingStars.jsx";

function diaryDate(event) {
  const date = new Date(`${event.event_date}T00:00:00`);
  return new Intl.DateTimeFormat("en-US", { day: "numeric", month: "short", year: "numeric" }).format(date);
}

function hasHappened(event) {
  return Boolean(event.venue?.city?.timezone) && eventIsPast(event);
}

function LedgerEventRow({ event, omittedArtistId = null, showVenue = true, venueFirst = false, onFocus, compact = false, variant }) {
  const lineup = compactLineup(event.artists, omittedArtistId);
  const venueName = event.venue?.name?.trim();
  const venueIsTba = !venueName || venueName.toUpperCase() === "TBA";
  const past = hasHappened(event);
  const visibleStartTime = past ? null : event.start_time;
  const dateTime = visibleStartTime ? `${event.event_date}T${visibleStartTime}` : event.event_date;
  const overlay = variant === "compact-overlay";
  const venue = showVenue ? <span className={venueIsTba ? "discover-venue-tba" : ""}>{venueIsTba ? "venue TBA" : venueName}</span> : null;
  const date = <time dateTime={dateTime}>{formatCompactEventDateTime(event.event_date, visibleStartTime)}</time>;

  return (
    <li>
      <Link className={`discover-event-row${compact ? " discover-event-row-compact" : ""}${overlay ? " discover-event-row-overlay" : ""}`} to={eventPath(event)} onFocus={onFocus}>
        <ImageSlot className={`discover-event-flier${compact ? " discover-event-flier-compact" : ""}`} name={event.title} src={event.cover_image_url} referrerPolicy="no-referrer" />
        <span className="discover-event-copy">
          <strong className="discover-event-title">{event.title}</strong>
          <span className="discover-event-meta">
            {venueFirst && venue ? <>{venue}<span aria-hidden="true"> · </span>{date}</> : <>{date}{venue ? <><span aria-hidden="true"> · </span>{venue}</> : null}</>}
            {recentRatingVisible(event.rating_summary) ? <><span aria-hidden="true"> · </span><RatingStars className="discover-recent-stars" value={event.rating_summary.average} /></> : null}
          </span>
          {lineup ? <span className="discover-event-lineup">{lineup}</span> : null}
        </span>
      </Link>
    </li>
  );
}

function ProfileDiaryEventRow({ event, rating, hasReview = false, reviewBody = null, likeCount = null, onDeleteReview = null, reviewPending = false }) {
  const eventYear = event.event_date.slice(0, 4);
  return (
    <li className={onDeleteReview ? "profile-diary-item has-review-action" : "profile-diary-item"}>
      <Link className="profile-diary-row" to={eventPath(event)}>
        <ImageSlot className="profile-diary-thumb" name={event.title} src={event.cover_image_url} referrerPolicy="no-referrer" />
        <span className="profile-diary-copy">
          <span className="profile-diary-title-line"><strong className="profile-diary-title">{event.title}</strong><span className="profile-diary-year">{eventYear}</span></span>
          <span className="profile-diary-venue">{event.venue.name}, {event.venue.city.name}</span>
          <span className="profile-diary-judgment">
            {rating === null ? <span className="profile-unrated">Unrated attendance</span> : <RatingStars className="profile-row-stars" value={rating} />}
            <span className="profile-diary-attended">Been <time dateTime={event.event_date}>{diaryDate(event)}</time></span>
            {hasReview && !reviewBody ? <small>Written review</small> : null}
          </span>
          {reviewBody ? <span className="profile-diary-review">{reviewBody}</span> : null}
          {reviewBody && likeCount !== null ? <span className="profile-diary-likes"><span aria-hidden="true">♥</span>{likeCount === 0 ? "No likes yet" : pluralize(likeCount, "like")}</span> : null}
        </span>
      </Link>
      {onDeleteReview ? <button className="profile-diary-delete" type="button" disabled={reviewPending} onClick={onDeleteReview}>Delete review</button> : null}
    </li>
  );
}

function FeedEventRow({ item }) {
  const event = item.target.event;
  const isRated = item.type === "rated_been";
  const isRich = isRated;
  const visibleStartTime = hasHappened(event) ? null : event.start_time;
  return (
    <Link className={`home-feed-item home-feed-event${isRich ? " home-feed-rich" : ""}`} to={feedItemPath(item)}>
      <ImageSlot className="home-feed-flier" name={event.title} src={event.cover_image_url} />
      <span className="home-feed-copy">
        <span className="home-feed-actor-line">
          <ProfileAvatar profile={item.actor} small />
          <strong className="home-feed-actor-name">{item.actor.display_name}</strong>
          <span className="home-feed-verb">{homeFeedVerb(item)}</span>
          <strong className="home-feed-object">{event.title}</strong>
          <time dateTime={item.activity_at}>{compactRelativeTime(item.activity_at)}</time>
        </span>
        {isRated ? <RatingStars className="home-feed-stars" value={item.context.rating} /> : null}
        {item.type === "will_be_there" ? <span className="home-feed-meta">{formatEventDateTime(event.event_date, visibleStartTime)} · {event.venue.name}</span> : null}
        {isRich && item.context.review ? <FeedReviewExcerpt>{item.context.review.body}</FeedReviewExcerpt> : null}
      </span>
    </Link>
  );
}

export default function EventRowPresenter({ variant = "standard-ledger", ...props }) {
  if (variant === "profile-diary") return <ProfileDiaryEventRow {...props} />;
  if (variant === "feed-object") return <FeedEventRow {...props} />;
  return <LedgerEventRow {...props} variant={variant} />;
}
