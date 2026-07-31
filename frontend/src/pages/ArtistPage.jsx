import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ApiError, fetchJson } from "../api.js";
import EventList from "../components/EventList.jsx";

export default function ArtistPage() {
  const { artistId } = useParams();
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({
    loading: true,
    error: null,
    artist: null,
    notFound: false,
  });

  useEffect(() => {
    const controller = new AbortController();
    setState({ loading: true, error: null, artist: null, notFound: false });
    fetchJson(`/api/artists/${artistId}/`, { signal: controller.signal })
      .then((artist) => {
        setState({ loading: false, error: null, artist, notFound: false });
      })
      .catch((error) => {
        if (error.name === "AbortError") {
          return;
        }
        setState({
          loading: false,
          error: error.status === 404 ? null : error,
          artist: null,
          notFound: error instanceof ApiError && error.status === 404,
        });
      });
    return () => controller.abort();
  }, [artistId, retry]);

  if (state.loading) {
    return (
      <main>
        <p>Loading artist.</p>
      </main>
    );
  }
  if (state.notFound) {
    return (
      <main>
        <h1>Artist not found</h1>
        <p>The artist does not exist.</p>
        <p>
          <Link to="/">Return to Discover</Link>
        </p>
      </main>
    );
  }
  if (state.error) {
    return (
      <main>
        <p>The artist could not be loaded.</p>
        <button type="button" onClick={() => setRetry((value) => value + 1)}>
          Retry
        </button>
      </main>
    );
  }

  const artist = state.artist;
  return (
    <main>
      <article>
        <h1>{artist.name}</h1>
        {artist.image_url ? (
          <img src={artist.image_url} alt={artist.name} />
        ) : null}
      </article>
      <EventList
        heading="Upcoming"
        scopeName="artist_id"
        scopeId={artist.id}
        when="upcoming"
        emptyMessage="No upcoming events."
      />
      <EventList
        heading="Past"
        scopeName="artist_id"
        scopeId={artist.id}
        when="past"
        emptyMessage="No past events."
      />
    </main>
  );
}
