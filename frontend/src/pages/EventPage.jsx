import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ApiError, fetchJson, fetchWithCsrf } from "../api.js";
import { formatEventDateTime } from "../formatEventDateTime.js";

const RATINGS = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5];


export default function EventPage({ user, onAuthenticationRequired }) {
  const { eventId } = useParams();
  const [retry, setRetry] = useState(0);
  const [rating, setRating] = useState("");
  const [saving, setSaving] = useState(false);
  const [actionError, setActionError] = useState(null);
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

  async function mutate(path, options) {
    setSaving(true);
    setActionError(null);
    try {
      await fetchWithCsrf(path, options);
      setRetry((value) => value + 1);
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
    if (!window.confirm("Remove your rating? The event will remain in Been.")) {
      return;
    }
    mutate(`/api/events/${eventId}/been/rating/`, { method: "DELETE" });
  }

  function removeEntry() {
    if (
      !window.confirm(
        "Remove this event from Been? This permanently deletes its rating.",
      )
    ) {
      return;
    }
    mutate(`/api/events/${eventId}/been/`, { method: "DELETE" });
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
          <Link to="/">Return to Discover</Link>
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
          <Link to={`/?city_id=${event.venue.city.id}`}>
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
        <section>
          <h2>Rating</h2>
          {event.rating_summary.state === "available" ? (
            <p>
              {event.rating_summary.average.toFixed(1)} average from{" "}
              {event.rating_summary.count} ratings.
            </p>
          ) : (
            <p>Not enough ratings</p>
          )}
        </section>
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
                        {value.toFixed(1)} stars
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
                  </>
                ) : null}
              </>
            )}
          </section>
        ) : null}
      </article>
    </main>
  );
}
