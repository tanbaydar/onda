import { Link } from "react-router-dom";

import { compactLineup } from "../discoverPresentation.js";
import { eventPath } from "../entityRoutes.js";
import { formatCompactEventDateTime } from "../formatEventDateTime.js";
import { recentRatingVisible } from "../polishPresentation.js";
import ImageSlot from "./ImageSlot.jsx";
import RatingStars from "./RatingStars.jsx";

export default function DiscoverEventRow({ event, omittedArtistId = null, showVenue = true, onFocus, compact = false }) {
  const lineup = compactLineup(event.artists, omittedArtistId);
  const venueName = event.venue?.name?.trim();
  const venueIsTba = !venueName || venueName.toUpperCase() === "TBA";
  const dateTime = event.start_time ? `${event.event_date}T${event.start_time}` : event.event_date;

  return (
    <li>
      <Link className={`discover-event-row${compact ? " discover-event-row-compact" : ""}`} to={eventPath(event)} onFocus={onFocus}>
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
