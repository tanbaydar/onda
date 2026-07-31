import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ApiError, fetchJson } from "../api.js";
import { formatEventDateTime } from "../formatEventDateTime.js";

export default function EventPage() {
  const { eventId } = useParams();
  const [retry, setRetry] = useState(0);
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
  }, [eventId, retry]);

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
      </article>
    </main>
  );
}
