import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { fetchJson } from "../api.js";
import { formatEventDateTime } from "../formatEventDateTime.js";

export function EventItem({
  event,
  showVenue = true,
  showCity = true,
  omittedArtistId = null,
}) {
  const visibleArtists = event.artists.filter(
    (artist) => String(artist.id) !== String(omittedArtistId),
  );

  return (
    <li>
      <article className="event-row">
        <h3>
          <Link to={`/events/${event.id}`}>{event.title}</Link>
        </h3>
        {event.cover_image_url ? (
          <img src={event.cover_image_url} alt={event.title} referrerPolicy="no-referrer" />
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
        {showVenue || showCity ? (
          <p>
            {showVenue ? (
              <>
                Venue:{" "}
                <Link to={`/venues/${event.venue.id}`}>{event.venue.name}</Link>
              </>
            ) : null}
            {showVenue && showCity ? " in " : null}
            {showCity ? (
              <Link to={`/discover?city_id=${event.venue.city.id}`}>
                {event.venue.city.name}
              </Link>
            ) : null}
          </p>
        ) : null}
        {visibleArtists.length > 0 ? (
          <p>
            Artists:{" "}
            {visibleArtists.map((artist, index) => (
              <span key={artist.id}>
                {index > 0 ? ", " : null}
                <Link to={`/artists/${artist.id}`}>{artist.name}</Link>
              </span>
            ))}
          </p>
        ) : null}
      </article>
    </li>
  );
}

export default function EventList({
  heading,
  scopeName,
  scopeId,
  when,
  emptyMessage,
  pageSize = 20,
  showVenue = true,
  showCity = true,
  omittedArtistId = null,
  hidden = false,
  quietHeading = false,
}) {
  const [page, setPage] = useState(1);
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({
    loading: true,
    error: null,
    data: null,
  });

  useEffect(() => {
    const controller = new AbortController();
    const query = new URLSearchParams({
      when,
      [scopeName]: String(scopeId),
      page: String(page),
      page_size: String(pageSize),
    });

    setState({ loading: true, error: null, data: null });
    fetchJson(`/api/events/?${query}`, { signal: controller.signal })
      .then((data) => {
        setState({ loading: false, error: null, data });
      })
      .catch((error) => {
        if (error.name !== "AbortError") {
          setState({ loading: false, error, data: null });
        }
      });

    return () => controller.abort();
  }, [page, pageSize, retry, scopeId, scopeName, when]);

  return (
    <section className="event-list" hidden={hidden}>
      <h2 className={quietHeading ? "sr-only" : undefined}>{heading}</h2>
      {state.loading ? <p>Loading events.</p> : null}
      {state.error ? (
        <>
          <p>Events could not be loaded.</p>
          <button type="button" onClick={() => setRetry((value) => value + 1)}>
            Retry
          </button>
        </>
      ) : null}
      {state.data && state.data.results.length === 0 ? (
        <p>{emptyMessage}</p>
      ) : null}
      {state.data && state.data.results.length > 0 ? (
        <>
          <ul className="ledger">
            {state.data.results.map((event) => (
              <EventItem
                key={event.id}
                event={event}
                showVenue={showVenue}
                showCity={showCity}
                omittedArtistId={omittedArtistId}
              />
            ))}
          </ul>
          <nav className="ledger-pagination" aria-label={`${heading} pagination`}>
            <button
              className="quiet-control"
              type="button"
              disabled={state.data.pagination.previous_page === null}
              onClick={() => setPage(state.data.pagination.previous_page)}
            >
              Previous
            </button>
            <span>
              {" "}
              Page {state.data.pagination.page} of{" "}
              {state.data.pagination.total_pages}{" "}
            </span>
            <button
              className="quiet-control"
              type="button"
              disabled={state.data.pagination.next_page === null}
              onClick={() => setPage(state.data.pagination.next_page)}
            >
              Next
            </button>
          </nav>
        </>
      ) : null}
    </section>
  );
}
