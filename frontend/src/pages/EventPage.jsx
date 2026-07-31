import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ApiError, fetchJson, fetchWithCsrf } from "../api.js";
import PublicReviews from "../components/PublicReviews.jsx";
import YourCircle from "../components/YourCircle.jsx";
import WillBeThereAttendees from "../components/WillBeThereAttendees.jsx";
import { formatEventDateTime } from "../formatEventDateTime.js";
import FavoriteControl from "../components/FavoriteControl.jsx";
import { pluralize } from "../lib/plural.js";

const RATINGS = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5];


export default function EventPage({ user, onAuthenticationRequired }) {
  const { eventId } = useParams();
  const [retry, setRetry] = useState(0);
  const [rating, setRating] = useState("");
  const [reviewBody, setReviewBody] = useState("");
  const [socialVersion, setSocialVersion] = useState(0);
  const [willBeThereVersion, setWillBeThereVersion] = useState(0);
  const [saving, setSaving] = useState(false);
  const [actionError, setActionError] = useState(null);
  const [willBeThereError, setWillBeThereError] = useState(null);
  const [state, setState] = useState({
    loading: true,
    error: null,
    event: null,
    notFound: false,
  });

  useEffect(() => {
    const controller = new AbortController();
    setState({ loading: true, error: null, event: null, notFound: false });
    fetchJson(`/api/events/${eventId}/`, { signal: controller.signal })
      .then((event) => {
        setState({ loading: false, error: null, event, notFound: false });
        setRating(
          event.viewer_entry?.rating === null ||
            event.viewer_entry?.rating === undefined
            ? ""
            : String(event.viewer_entry.rating),
        );
        setReviewBody(event.viewer_entry?.review?.body ?? "");
      })
      .catch((error) => {
        if (error.name === "AbortError") {
          return;
        }
        setState({
          loading: false,
          error: error.status === 404 ? null : error,
          event: null,
          notFound: error instanceof ApiError && error.status === 404,
        });
      });
    return () => controller.abort();
  }, [eventId, retry, user?.id]);

  async function mutate(path, options, { reviewsChanged = false } = {}) {
    setSaving(true);
    setActionError(null);
    try {
      await fetchWithCsrf(path, options);
      setRetry((value) => value + 1);
      if (reviewsChanged) {
        setSocialVersion((value) => value + 1);
      }
    } catch (error) {
      if (error.status === 401 || error.status === 403) {
        setActionError("Sign in required.");
        onAuthenticationRequired();
      } else {
        const messages = error.data?.errors
          ? Object.values(error.data.errors).flat()
          : ["The Been entry could not be changed."];
        setActionError(messages.join(" "));
      }
    } finally {
      setSaving(false);
    }
  }

  function saveRating(event) {
    event.preventDefault();
    mutate(`/api/events/${eventId}/been/`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rating: Number(rating) }),
    });
  }

  function removeRating() {
    const warning = state.event.viewer_entry?.review
      ? "Remove your rating? The event will remain in Been, but your written review and all of its likes will be permanently deleted."
      : "Remove your rating? The event will remain in Been.";
    if (!window.confirm(warning)) {
      return;
    }
    mutate(
      `/api/events/${eventId}/been/rating/`,
      { method: "DELETE" },
      { reviewsChanged: true },
    );
  }

  function removeEntry() {
    if (
      !window.confirm(
        state.event.viewer_entry?.review
          ? "Remove this event from Been? This permanently deletes the entry, rating, written review, and all review likes."
          : "Remove this event from Been? This permanently deletes its rating.",
      )
    ) {
      return;
    }
    mutate(`/api/events/${eventId}/been/`, { method: "DELETE" });
  }

  function saveReview(event) {
    event.preventDefault();
    const trimmedLength = reviewBody.trim().length;
    if (trimmedLength < 1 || trimmedLength > 1000) {
      setActionError(
        "Written review must be between 1 and 1,000 characters after trimming.",
      );
      return;
    }
    mutate(
      `/api/events/${eventId}/been/review/`,
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ body: reviewBody }),
      },
      { reviewsChanged: true },
    );
  }

  function deleteReview() {
    if (
      !window.confirm(
        "Delete your written review? Its likes will be permanently deleted. Your rating and Been entry will remain.",
      )
    ) {
      return;
    }
    mutate(
      `/api/events/${eventId}/been/review/`,
      { method: "DELETE" },
      { reviewsChanged: true },
    );
  }

  async function changeWillBeThere() {
    setSaving(true);
    setWillBeThereError(null);
    try {
      await fetchWithCsrf(`/api/events/${eventId}/will-be-there/`, {
        method: state.event.viewer_will_be_there.is_marked ? "DELETE" : "PUT",
      });
      setRetry((value) => value + 1);
      setWillBeThereVersion((value) => value + 1);
    } catch (error) {
      if (error.status === 401 || error.status === 403) {
        setWillBeThereError("Sign in required.");
        onAuthenticationRequired();
      } else if (error.status === 404 || error.status === 409) {
        setRetry((value) => value + 1);
        setWillBeThereVersion((value) => value + 1);
      } else {
        setWillBeThereError("Will Be There could not be changed.");
      }
    } finally {
      setSaving(false);
    }
  }

  if (state.loading) {
    return (
      <main>
        <p>Loading event.</p>
      </main>
    );
  }
  if (state.notFound) {
    return (
      <main>
        <h1>Event not found</h1>
        <p>The event does not exist or is no longer publicly visible.</p>
        <p>
          <Link to="/discover">Return to Discover</Link>
        </p>
      </main>
    );
  }
  if (state.error) {
    return (
      <main>
        <p>The event could not be loaded.</p>
        <button type="button" onClick={() => setRetry((value) => value + 1)}>
          Retry
        </button>
      </main>
    );
  }

  const event = state.event;
  const trimmedReviewLength = reviewBody.trim().length;
  return (
    <main>
      <article>
        <h1>{event.title}</h1>
        {event.cover_image_url ? (
          <img src={event.cover_image_url} alt={event.title} />
        ) : null}
        <p>
          <time
            dateTime={
              event.start_time
                ? `${event.event_date}T${event.start_time}`
                : event.event_date
            }
          >
            {formatEventDateTime(event.event_date, event.start_time)}
          </time>
        </p>
        <p>
          Venue: <Link to={`/venues/${event.venue.id}`}>{event.venue.name}</Link>
        </p>
        <p>
          City:{" "}
          <Link to={`/discover?city_id=${event.venue.city.id}`}>
            {event.venue.city.name}
          </Link>
        </p>
        <section>
          <h2>Artists</h2>
          <ol>
            {event.artists.map((artist) => (
              <li key={artist.id}>
                <Link to={`/artists/${artist.id}`}>{artist.name}</Link>
              </li>
            ))}
          </ol>
        </section>
        <section><h2>Will Be There attendance</h2><p>{pluralize(event.will_be_there_summary.active_count, "active mark")}.</p></section>
        {user ? <FavoriteControl path={`/api/events/${event.id}/favorite/`} state={event.viewer_favorite} onChanged={() => setRetry((value) => value + 1)} /> : null}
        <section>
          <h2>Rating</h2>
          {event.rating_summary.state === "available" ? (
            <p>
              {event.rating_summary.average.toFixed(1)} average from{" "}
              {pluralize(event.rating_summary.count, "rating")}.
            </p>
          ) : (
            <p>Not enough ratings</p>
          )}
        </section>
        {user ? (
          <section>
            <h2>Will Be There</h2>
            {willBeThereError ? <p>{willBeThereError}</p> : null}
            {event.viewer_will_be_there.can_mark ? (
              <button type="button" disabled={saving} onClick={changeWillBeThere}>
                {event.viewer_will_be_there.is_marked
                  ? "Remove Will Be There"
                  : "Mark Will Be There"}
              </button>
            ) : (
              <p>{event.viewer_will_be_there.unavailable_reason}</p>
            )}
          </section>
        ) : null}
        {user ? (
          <section>
            <h2>Your Been entry</h2>
            {actionError ? <p>{actionError}</p> : null}
            {!event.viewer_entry && !event.been.loggable ? (
              <p>{event.been.unavailable_reason}</p>
            ) : (
              <>
                <form onSubmit={saveRating}>
                  <label htmlFor="rating">Rating</label>{" "}
                  <select
                    id="rating"
                    value={rating}
                    onChange={(changeEvent) => setRating(changeEvent.target.value)}
                    required
                  >
                    <option value="">Choose a rating</option>
                    {RATINGS.map((value) => (
                      <option key={value} value={value}>
                        {pluralize(value.toFixed(1), "star")}
                      </option>
                    ))}
                  </select>{" "}
                  <button type="submit" disabled={saving}>
                    {event.viewer_entry ? "Save rating" : "Add to Been"}
                  </button>
                </form>
                {event.viewer_entry ? (
                  <>
                    {event.viewer_entry.rating !== null ? (
                      <p>
                        <button
                          type="button"
                          disabled={saving}
                          onClick={removeRating}
                        >
                          Remove rating
                        </button>
                      </p>
                    ) : null}
                    <p>
                      <button
                        type="button"
                        disabled={saving}
                        onClick={removeEntry}
                      >
                        Remove from Been
                      </button>
                    </p>
                    {event.viewer_entry.rating !== null ? (
                      <form onSubmit={saveReview}>
                        <p>
                          <label htmlFor="review-body">Written review</label>
                        </p>
                        <textarea
                          id="review-body"
                          value={reviewBody}
                          required
                          rows={8}
                          onChange={(changeEvent) =>
                            setReviewBody(changeEvent.target.value)
                          }
                        />
                        <p>
                          {trimmedReviewLength} of 1,000 stored characters
                        </p>
                        <button
                          type="submit"
                          disabled={
                            saving ||
                            trimmedReviewLength < 1 ||
                            trimmedReviewLength > 1000
                          }
                        >
                          {event.viewer_entry.review
                            ? "Save review changes"
                            : "Publish review"}
                        </button>
                        {event.viewer_entry.review ? (
                          <>
                            {" "}
                            <button
                              type="button"
                              disabled={saving}
                              onClick={deleteReview}
                            >
                              Delete review
                            </button>
                          </>
                        ) : null}
                      </form>
                    ) : null}
                  </>
                ) : null}
              </>
            )}
          </section>
        ) : null}
      </article>
      <WillBeThereAttendees
        eventId={event.id}
        scope="circle"
        user={user}
        version={willBeThereVersion}
      />
      <WillBeThereAttendees
        eventId={event.id}
        scope="public"
        user={user}
        version={willBeThereVersion}
      />
      <YourCircle
        eventId={event.id}
        user={user}
        version={socialVersion}
        onSocialChanged={() => setSocialVersion((value) => value + 1)}
        onAuthenticationRequired={onAuthenticationRequired}
      />
      <PublicReviews
        eventId={event.id}
        user={user}
        version={socialVersion}
        onSocialChanged={() => setSocialVersion((value) => value + 1)}
        onAuthenticationRequired={onAuthenticationRequired}
      />
    </main>
  );
}
