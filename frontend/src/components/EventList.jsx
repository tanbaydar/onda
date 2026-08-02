import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { fetchJson } from "../api.js";
import { formatEventDateTime } from "../formatEventDateTime.js";
import { formatCompactEventDateTime } from "../formatEventDateTime.js";
import { compactLineup } from "../discoverPresentation.js";
import { artistPath, eventPath, venuePath } from "../entityRoutes.js";

export function EventItem({
  event,
  showVenue = true,
  showCity = true,
  omittedArtistId = null,
  discover = false,
}) {
  const visibleArtists = event.artists.filter(
    (artist) => String(artist.id) !== String(omittedArtistId),
  );

  if (discover) {
    const lineup = compactLineup(event.artists, omittedArtistId);
    const venueName = event.venue?.name?.trim();
    const venueIsTba = !venueName || venueName.toUpperCase() === "TBA";
    return (
      <li>
        <Link className="discover-event-row" to={eventPath(event)}>
          <span className="discover-event-flier" aria-hidden="true">
            {event.cover_image_url ? <img src={event.cover_image_url} alt="" referrerPolicy="no-referrer" /> : null}
          </span>
          <span className="discover-event-copy">
            <strong className="discover-event-title">{event.title}</strong>
            <span className="discover-event-meta"><time dateTime={event.start_time ? `${event.event_date}T${event.start_time}` : event.event_date}>{formatCompactEventDateTime(event.event_date, event.start_time)}</time><span aria-hidden="true"> · </span><span className={venueIsTba ? "discover-venue-tba" : ""}>{venueIsTba ? "venue TBA" : venueName}</span></span>
            {lineup ? <span className="discover-event-lineup">{lineup}</span> : null}
          </span>
        </Link>
      </li>
    );
  }

  return (
    <li>
      <article className="event-row">
        <h3>
          <Link to={eventPath(event)}>{event.title}</Link>
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
                <Link to={venuePath(event.venue)}>{event.venue.name}</Link>
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
                <Link to={artistPath(artist)}>{artist.name}</Link>
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
  discover = false,
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

    setState((current) => ({ loading: true, error: null, data: discover && page > 1 ? current.data : null }));
    fetchJson(`/api/events/?${query}`, { signal: controller.signal })
      .then((data) => {
        setState((current) => ({ loading: false, error: null, data: discover && page > 1 && current.data ? { ...data, results: [...current.data.results, ...data.results] } : data }));
      })
      .catch((error) => {
        if (error.name !== "AbortError") {
          setState({ loading: false, error, data: null });
        }
      });

    return () => controller.abort();
  }, [discover, page, pageSize, retry, scopeId, scopeName, when]);

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
          <ul className={discover ? "discover-event-ledger" : "ledger"}>
            {state.data.results.map((event) => (
              <EventItem
                key={event.id}
                event={event}
                showVenue={showVenue}
                showCity={showCity}
                omittedArtistId={omittedArtistId}
                discover={discover}
              />
            ))}
          </ul>
          {discover ? (state.data.pagination.next_page ? <button className="discover-load-more" type="button" disabled={state.loading} onClick={() => setPage(state.data.pagination.next_page)}>{state.loading ? "Loading…" : "Load more"}</button> : null) : <nav className="ledger-pagination" aria-label={`${heading} pagination`}>
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
          </nav>}
        </>
      ) : null}
    </section>
  );
}
