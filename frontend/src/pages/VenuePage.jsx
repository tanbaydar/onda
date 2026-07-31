import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ApiError, fetchJson } from "../api.js";
import EventList from "../components/EventList.jsx";

export default function VenuePage() {
  const { venueId } = useParams();
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({
    loading: true,
    error: null,
    venue: null,
    notFound: false,
  });

  useEffect(() => {
    const controller = new AbortController();
    setState({ loading: true, error: null, venue: null, notFound: false });
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
  }, [retry, venueId]);

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
    <main>
      <article>
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
      <EventList
        heading="Upcoming"
        scopeName="venue_id"
        scopeId={venue.id}
        when="upcoming"
        emptyMessage="No upcoming events."
        showVenue={false}
        showCity={false}
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
