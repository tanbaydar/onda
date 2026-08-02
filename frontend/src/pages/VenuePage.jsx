import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ApiError, fetchJson } from "../api.js";
import EventList from "../components/EventList.jsx";
import FavoriteControl from "../components/FavoriteControl.jsx";
import { venuePath } from "../entityRoutes.js";
import useCanonicalEntityRoute from "../useCanonicalEntityRoute.js";

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
    setState({ loading: true, error: null, venue: null, notFound: false });
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
        setState({
          loading: false,
          error: error.status === 404 ? null : error,
          venue: null,
          notFound: error instanceof ApiError && error.status === 404,
        });
      });
    return () => controller.abort();
  }, [retry, sessionReady, user?.id, venueId]);

  if (state.loading) {
    return (
      <main>
        <p>Loading venue.</p>
      </main>
    );
  }
  if (state.notFound) {
    return (
      <main>
        <h1>Venue not found</h1>
        <p>The venue does not exist.</p>
        <p>
          <Link to="/discover">Return to Discover</Link>
        </p>
      </main>
    );
  }
  if (state.error) {
    return (
      <main>
        <p>The venue could not be loaded.</p>
        <button type="button" onClick={() => setRetry((value) => value + 1)}>
          Retry
        </button>
      </main>
    );
  }

  const venue = state.venue;
  return (
    <main className="detail-page">
      <article className="identity">
        <h1>{venue.name}</h1>
        <p>
          City:{" "}
          <Link to={`/discover?city_id=${venue.city.id}`}>{venue.city.name}</Link>
        </p>
        <dl>
          <dt>Region</dt>
          <dd>{venue.city.region_name ?? venue.city.region_code ?? "Not provided"}</dd>
          <dt>Country</dt>
          <dd>{venue.city.country_code}</dd>
          <dt>Timezone</dt>
          <dd>{venue.city.timezone}</dd>
        </dl>
      </article>
      {user ? <FavoriteControl path={`/api/venues/${venue.id}/favorite/`} state={venue.viewer_favorite} onChanged={() => setRetry((value) => value + 1)} /> : null}
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
