import { Link } from "react-router-dom";

import { eventPath } from "../entityRoutes.js";
import RatingStars from "./RatingStars.jsx";
import ImageSlot from "./ImageSlot.jsx";

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
        <ImageSlot className="profile-diary-thumb" name={event.title} src={event.cover_image_url} referrerPolicy="no-referrer" />
        <strong className="profile-diary-title">{event.title}</strong>
        <span className="profile-diary-meta"><time dateTime={event.start_time ? `${event.event_date}T${event.start_time}` : event.event_date}>{diaryDate(event)}</time><span className="profile-diary-separator"> · </span><span className="profile-diary-venue">{event.venue.name}, {event.venue.city.name}</span></span>
        <span className="profile-diary-judgment">
          {rating === null ? <span className="profile-unrated">Unrated attendance</span> : <RatingStars className="profile-row-stars" value={rating} />}
          {hasReview ? <small>Written review</small> : null}
        </span>
      </Link>
    </li>
  );
}
