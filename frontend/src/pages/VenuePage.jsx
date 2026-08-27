import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ApiError, fetchJson } from "../api.js";
import EventList from "../components/EventList.jsx";
import FavoriteControl from "../components/FavoriteControl.jsx";
import { venuePath } from "../entityRoutes.js";
import useCanonicalEntityRoute from "../useCanonicalEntityRoute.js";
import { formatVenueLocation } from "../venuePresentation.js";
import SystemStatePage from "../components/SystemStatePage.jsx";

export default function VenuePage({ user, sessionReady }) {
  const { venueKey } = useParams();
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({
    loading: true,
    error: null,
    venue: null,
    notFound: false,
  });
  const venueId = useCanonicalEntityRoute(venueKey, state.venue, venuePath);

  useEffect(() => {
    const controller = new AbortController();
    setState((current) => current.venue?.id === venueId
      ? { ...current, loading: false, error: null, notFound: false }
      : { loading: true, error: null, venue: null, notFound: false });
    if (!sessionReady) return () => controller.abort();
    if (venueId === null) {
      setState({ loading: false, error: null, venue: null, notFound: true });
      return () => controller.abort();
    }
    fetchJson(`/api/venues/${venueId}/`, { signal: controller.signal })
      .then((venue) => {
        setState({ loading: false, error: null, venue, notFound: false });
      })
      .catch((error) => {
        if (error.name === "AbortError") {
          return;
        }
        setState((current) => current.venue?.id === venueId && error.status !== 404
          ? { ...current, loading: false, error, notFound: false }
          : {
              loading: false,
              error: error.status === 404 ? null : error,
              venue: null,
              notFound: error instanceof ApiError && error.status === 404,
            });
      });
    return () => controller.abort();
  }, [retry, sessionReady, user?.id, venueId]);

  function changeFavorite(nextFavorite) {
    if (!nextFavorite) {
      setRetry((value) => value + 1);
      return;
    }
    setState((current) => current.venue ? {
      ...current,
      venue: { ...current.venue, viewer_favorite: nextFavorite },
    } : current);
  }

  if (state.loading && !state.venue) {
    return (
      <SystemStatePage title="Venue" actionTo={null} busy><p>Loading venue…</p></SystemStatePage>
    );
  }
  if (state.notFound) {
    return (
      <SystemStatePage title="Venue not found">
        <p>The venue does not exist.</p>
      </SystemStatePage>
    );
  }
  if (state.error && !state.venue) {
    return (
      <SystemStatePage title="Venue" actionTo={null}>
        <p>The venue could not be loaded.</p>
        <button className="recovery-action" type="button" onClick={() => setRetry((value) => value + 1)}>
          Retry
        </button>
      </SystemStatePage>
    );
  }

  const venue = state.venue;
  const location = formatVenueLocation(venue.city);
  return (
    <main className="detail-page venue-page">
      {state.error ? <div className="action-feedback" role="alert"><p>Venue status could not be refreshed.</p><button className="recovery-action" type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></div> : null}
      <article className="venue-identity">
        <h1 className="identity-title">{venue.name}</h1>
        {location ? (
          <p className="venue-location">
            <Link to={`/discover?city_id=${venue.city.id}`}>{location}</Link>
          </p>
        ) : null}
        {user ? <FavoriteControl compact path={`/api/venues/${venue.id}/favorite/`} state={venue.viewer_favorite} onChanged={changeFavorite} /> : null}
      </article>
      <EventList
        heading="Upcoming"
        scopeName="venue_id"
        scopeId={venue.id}
        when="upcoming"
        emptyMessage="No upcoming events."
        showVenue={false}
      />
      <EventList
        heading="Past"
        scopeName="venue_id"
        scopeId={venue.id}
        when="past"
        emptyMessage="No past events."
        showVenue={false}
        showCity={false}
      />
    </main>
  );
}
