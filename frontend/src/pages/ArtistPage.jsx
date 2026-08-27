import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ApiError, fetchJson } from "../api.js";
import EventList from "../components/EventList.jsx";
import FavoriteControl from "../components/FavoriteControl.jsx";
import ArtistAvatar from "../components/ArtistAvatar.jsx";
import { artistPath } from "../entityRoutes.js";
import useCanonicalEntityRoute from "../useCanonicalEntityRoute.js";
import SystemStatePage from "../components/SystemStatePage.jsx";

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
    setState((current) => current.artist?.id === artistId
      ? { ...current, loading: false, error: null, notFound: false }
      : { loading: true, error: null, artist: null, notFound: false });
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
        setState((current) => current.artist?.id === artistId && error.status !== 404
          ? { ...current, loading: false, error, notFound: false }
          : {
              loading: false,
              error: error.status === 404 ? null : error,
              artist: null,
              notFound: error instanceof ApiError && error.status === 404,
            });
      });
    return () => controller.abort();
  }, [artistId, retry, sessionReady, user?.id]);

  function changeFavorite(nextFavorite) {
    if (!nextFavorite) {
      setRetry((value) => value + 1);
      return;
    }
    setState((current) => current.artist ? {
      ...current,
      artist: { ...current.artist, viewer_favorite: nextFavorite },
    } : current);
  }

  if (state.loading && !state.artist) {
    return (
      <SystemStatePage title="Artist" actionTo={null} busy><p>Loading artist…</p></SystemStatePage>
    );
  }
  if (state.notFound) {
    return (
      <SystemStatePage title="Artist not found">
        <p>The artist does not exist.</p>
      </SystemStatePage>
    );
  }
  if (state.error && !state.artist) {
    return (
      <SystemStatePage title="Artist" actionTo={null}>
        <p>The artist could not be loaded.</p>
        <button className="recovery-action" type="button" onClick={() => setRetry((value) => value + 1)}>
          Retry
        </button>
      </SystemStatePage>
    );
  }

  const artist = state.artist;
  return (
    <main className="detail-page artist-page">
      {state.error ? <div className="action-feedback" role="alert"><p>Artist status could not be refreshed.</p><button className="recovery-action" type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></div> : null}
      <article className="catalog-identity artist-identity">
        <ArtistAvatar artist={artist} loading="eager" />
        <div className="catalog-identity-copy">
          <h1 className="identity-title">{artist.name}</h1>
          {user ? <FavoriteControl compact path={`/api/artists/${artist.id}/favorite/`} state={artist.viewer_favorite} onChanged={changeFavorite} /> : null}
        </div>
      </article>
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
