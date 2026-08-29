import { useEffect, useState } from "react";
import { Link, Navigate, useLocation } from "react-router-dom";

import { fetchJson } from "../api.js";
import EventRowPresenter from "../components/EventRowPresenter.jsx";
import ProfileAvatar from "../components/ProfileAvatar.jsx";
import { compactRelativeTime, feedItemPath, groupFeedItems, homeFeedVerb, HOME_EMPTY_COPY } from "../homeFeedPresentation.js";
import { homeAccessRedirect } from "../landing.js";


function FeedItem({ item }) {
  if (item.grouped) {
    const objects = item.grouped.map((entry) => entry.target.event?.title ?? entry.target.artist?.name);
    const visible = objects.slice(0, 3);
    const more = objects.length - visible.length;
    return <Link className="home-feed-item home-feed-grouped" to={feedItemPath(item)}><span className="home-feed-actor-line"><ProfileAvatar profile={item.actor} small /><strong className="home-feed-actor-name">{item.actor.display_name}</strong><span className="home-feed-verb">{homeFeedVerb(item)}</span><strong className="home-feed-object">{visible.join(", ")}</strong>{more ? <small className="home-feed-group-count">+{more} more</small> : null}<time dateTime={item.activity_at}>{compactRelativeTime(item.activity_at)}</time></span></Link>;
  }
  const event = item.target.event;
  const artist = item.target.artist;
  const objectName = event?.title ?? artist?.name;
  if (event) return <EventRowPresenter variant="feed-object" item={item} />;
  return (
    <Link className="home-feed-item" to={feedItemPath(item)}>
      <span className="home-feed-copy">
        <span className="home-feed-actor-line">
          <ProfileAvatar profile={item.actor} small />
          <strong className="home-feed-actor-name">{item.actor.display_name}</strong>
          <span className="home-feed-verb">{homeFeedVerb(item)}</span>
          {artist ? <strong className="home-feed-object">{objectName}</strong> : null}
          <time dateTime={item.activity_at}>{compactRelativeTime(item.activity_at)}</time>
        </span>
      </span>
    </Link>
  );
}


export default function HomePage({ session }) {
  const location = useLocation();
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({ loading: true, error: null, results: [], next: null });
  const [loadingMore, setLoadingMore] = useState(false);
  const [loadMoreError, setLoadMoreError] = useState(null);

  useEffect(() => {
    if (!session.user) return undefined;
    const controller = new AbortController();
    setState({ loading: true, error: null, results: [], next: null });
    setLoadMoreError(null);
    fetchJson("/api/me/home/", { signal: controller.signal, cache: "no-store" })
      .then((data) => setState({ loading: false, error: null, results: data.results, next: data.next_cursor }))
      .catch((error) => {
        if (error.name !== "AbortError") setState({ loading: false, error, results: [], next: null });
      });
    return () => controller.abort();
  }, [retry, session.user]);

  async function loadMore() {
    setLoadingMore(true);
    setLoadMoreError(null);
    try {
      const data = await fetchJson(`/api/me/home/?cursor=${encodeURIComponent(state.next)}`, { cache: "no-store" });
      setState((current) => ({ ...current, results: [...current.results, ...data.results], next: data.next_cursor }));
    } catch (error) {
      setLoadMoreError(error);
    } finally {
      setLoadingMore(false);
    }
  }

  if (session.loading) return <main><p>Checking session…</p></main>;
  const redirect = homeAccessRedirect(session.user);
  if (redirect) return <Navigate to={redirect} replace state={{ from: `${location.pathname}${location.search}` }} />;
  return (
    <main className="feed-page">
      {state.loading ? <p className="home-feed-status">Loading activity…</p> : null}
      {state.error ? (
        <div className="home-feed-status"><p>Home activity could not be loaded.</p><button className="quiet-control" type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></div>
      ) : null}
      {!state.loading && !state.error && state.results.length === 0 ? (
        <div className="home-feed-empty"><p>{HOME_EMPTY_COPY}</p><Link to="/discover">Discover events</Link></div>
      ) : null}
      {state.results.length > 0 ? <ol className="home-feed-list ledger-list">{groupFeedItems(state.results).map((item) => <li key={`${item.type}-${item.activity_at}-${item.actor.id}-${item.target.event?.id ?? item.target.artist?.id}`}><FeedItem item={item} /></li>)}</ol> : null}
      {loadMoreError ? <div className="continuation-feedback home-feed-status" role="alert"><p>More home activity could not be loaded.</p><button className="recovery-action" type="button" disabled={loadingMore} onClick={loadMore}>{loadingMore ? "Retrying…" : "Retry"}</button></div> : null}
      {state.next && !state.error && !loadMoreError ? <button className="pagination-action home-feed-load-more" type="button" disabled={loadingMore} onClick={loadMore}>{loadingMore ? "Loading more…" : "Load more"}</button> : null}
    </main>
  );
}
