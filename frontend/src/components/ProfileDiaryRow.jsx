import { Link } from "react-router-dom";

import { ratingStars } from "../profilePresentation.js";
import { eventPath } from "../entityRoutes.js";

function diaryDate(event) {
  const date = new Date(`${event.event_date}T${event.start_time ?? "00:00:00"}`);
  const datePart = new Intl.DateTimeFormat("en-US", { weekday: "short", day: "numeric", month: "long" }).format(date);
  if (!event.start_time) return datePart;
  const timePart = new Intl.DateTimeFormat("en-US", { hour: "numeric", minute: "2-digit" }).format(date).toLowerCase();
  return `${datePart}, ${timePart}`;
}

export default function ProfileDiaryRow({ event, rating, hasReview = false }) {
  return (
    <li>
      <Link className="profile-diary-row" to={eventPath(event)}>
        <span className="profile-diary-thumb">{event.cover_image_url ? <img src={event.cover_image_url} alt="" referrerPolicy="no-referrer" /> : null}</span>
        <strong className="profile-diary-title">{event.title}</strong>
        <span className="profile-diary-meta"><time dateTime={event.start_time ? `${event.event_date}T${event.start_time}` : event.event_date}>{diaryDate(event)}</time><span className="profile-diary-separator"> · </span><span className="profile-diary-venue">{event.venue.name}, {event.venue.city.name}</span></span>
        <span className="profile-diary-judgment">
          <span className={rating === null ? "profile-unrated" : "profile-row-stars"}>{ratingStars(rating)}</span>
          {hasReview ? <small>Written review</small> : null}
        </span>
      </Link>
    </li>
  );
}
