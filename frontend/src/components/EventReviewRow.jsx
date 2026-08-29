import { Link } from "react-router-dom";

import { formatTimestamp } from "../lib/formatTimestamp.js";
import { pluralize } from "../lib/plural.js";
import { profilePath } from "../profileRoutes.js";
import ProfileAvatar from "./ProfileAvatar.jsx";
import RatingStars from "./RatingStars.jsx";
import ReviewExcerpt from "./ReviewExcerpt.jsx";

function ReviewLikeIcon({ liked }) {
  return (
    <svg className="event-review-like-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 21.35 10.55 20.03C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35Z" fill={liked ? "currentColor" : "none"} />
    </svg>
  );
}

export default function EventReviewRow({ person, rating, review = null, ratedAt = null, onLike = null, likePending = false, yours = false, ownerActions = null, children = null }) {
  const timestamp = review?.published_at ?? ratedAt;
  const profile = profilePath(person.username);
  const usernameLink = <Link className="event-review-name" to={profile}>{person.username}</Link>;
  return (
    <article className="event-review-row">
      <Link className="event-review-avatar" to={profile} aria-label={`${person.display_name}'s profile`}>
        <ProfileAvatar profile={person} small />
      </Link>
      <div className="event-review-copy">
        {review?.body ? <ReviewExcerpt prefix={usernameLink}>{review.body}</ReviewExcerpt> : <p className="event-review-no-body">{usernameLink} <span>No written review.</span></p>}
        <RatingStars className="event-review-stars" value={rating} />
        <div className="event-review-meta">
          {timestamp ? <time dateTime={timestamp}>{formatTimestamp(timestamp)}</time> : null}
          {review?.like_count > 0 ? <span className="event-review-like-count">{pluralize(review.like_count, "like")}</span> : null}
          {yours ? <span className="event-review-yours">Yours</span> : null}
          {ownerActions}
        </div>
      </div>
      {review && onLike ? (
        <button
          className={`like-action event-review-like-button${review.viewer_has_liked ? " is-liked" : ""}`}
          type="button"
          disabled={likePending}
          aria-busy={likePending}
          aria-label={review.viewer_has_liked ? "Unlike review" : "Like review"}
          aria-pressed={review.viewer_has_liked}
          onClick={onLike}
        >
          <ReviewLikeIcon liked={review.viewer_has_liked} />
        </button>
      ) : null}
      {children ? <div className="event-review-children">{children}</div> : null}
    </article>
  );
}
