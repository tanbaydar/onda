import { Link } from "react-router-dom";

import { formatTimestamp } from "../lib/formatTimestamp.js";
import { pluralize } from "../lib/plural.js";
import { profilePath } from "../profileRoutes.js";
import ProfileAvatar from "./ProfileAvatar.jsx";
import RatingStars from "./RatingStars.jsx";
import ReviewExcerpt from "./ReviewExcerpt.jsx";

export default function EventReviewRow({ person, rating, review = null, ratedAt = null, onLike = null, likePending = false, yours = false, onEdit = null, children = null }) {
  const timestamp = review?.published_at ?? ratedAt;
  return (
    <article className="event-review-row">
      <div className="event-review-person">
        <ProfileAvatar profile={person} small />
        <Link className="event-review-name" to={profilePath(person.username)}>{person.display_name}</Link>
        <Link className="event-review-handle" to={profilePath(person.username)}>@{person.username}</Link>
        {yours ? <span className="event-review-yours">Yours</span> : null}
        {onEdit ? <button className="quiet-action event-review-edit" type="button" onClick={onEdit}>Edit ▾</button> : null}
      </div>
      <RatingStars className="event-review-stars" value={rating} />
      {review?.body ? <ReviewExcerpt>{review.body}</ReviewExcerpt> : <p className="event-review-no-body">No written review.</p>}
      <div className="event-review-meta">
        {timestamp ? <time dateTime={timestamp}>{formatTimestamp(timestamp)}</time> : null}
        {review ? <><span className="event-review-like-count">{pluralize(review.like_count, "like")}</span>{onLike ? <button className="like-action" type="button" disabled={likePending} aria-busy={likePending} onClick={onLike}>{review.viewer_has_liked ? "Unlike" : "Like"}</button> : null}</> : null}
      </div>
      {children}
    </article>
  );
}
