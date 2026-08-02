import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ApiError, fetchJson } from "../api.js";
import EventList from "../components/EventList.jsx";
import FavoriteControl from "../components/FavoriteControl.jsx";
import { artistPath } from "../entityRoutes.js";
import useCanonicalEntityRoute from "../useCanonicalEntityRoute.js";

export default function ArtistPage({ user, sessionReady }) {
  const { artistKey } = useParams();
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({
    loading: true,
    error: null,
    artist: null,
    notFound: false,
  });
  const artistId = useCanonicalEntityRoute(artistKey, state.artist, artistPath);

  useEffect(() => {
    const controller = new AbortController();
    setState({ loading: true, error: null, artist: null, notFound: false });
    if (!sessionReady) return () => controller.abort();
    if (artistId === null) {
      setState({ loading: false, error: null, artist: null, notFound: true });
      return () => controller.abort();
    }
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
  }, [artistId, retry, sessionReady, user?.id]);

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
          <Link to="/discover">Return to Discover</Link>
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
    <main className="detail-page">
      <article className="identity">
        <h1>{artist.name}</h1>
        {artist.image_url ? (
          <img src={artist.image_url} alt={artist.name} loading="eager" />
        ) : null}
      </article>
      {user ? <FavoriteControl path={`/api/artists/${artist.id}/favorite/`} state={artist.viewer_favorite} onChanged={() => setRetry((value) => value + 1)} /> : null}
      <EventList
        heading="Upcoming"
        scopeName="artist_id"
        scopeId={artist.id}
        when="upcoming"
        emptyMessage="No upcoming events."
        omittedArtistId={artist.id}
      />
      <EventList
        heading="Past"
        scopeName="artist_id"
        scopeId={artist.id}
        when="past"
        emptyMessage="No past events."
        omittedArtistId={artist.id}
      />
    </main>
  );
}
