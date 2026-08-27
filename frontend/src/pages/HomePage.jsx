import { useEffect, useState } from "react";
import { Link, Navigate, useLocation } from "react-router-dom";

import { fetchJson } from "../api.js";
import { formatEventDateTime } from "../formatEventDateTime.js";
import FeedReviewExcerpt from "../components/FeedReviewExcerpt.jsx";
import ProfileAvatar from "../components/ProfileAvatar.jsx";
import RatingStars from "../components/RatingStars.jsx";
import ImageSlot from "../components/ImageSlot.jsx";
import { compactRelativeTime, feedItemPath, groupFeedItems, HOME_EMPTY_COPY, HOME_FEED_VERBS } from "../homeFeedPresentation.js";
import { homeAccessRedirect } from "../landing.js";


function FeedItem({ item }) {
  if (item.grouped) {
    const objects = item.grouped.map((entry) => entry.target.event?.title ?? entry.target.artist?.name ?? entry.target.user?.display_name);
    const visible = objects.slice(0, 3);
    const more = objects.length - visible.length;
    return <Link className="home-feed-item home-feed-grouped" to={feedItemPath(item)}><span className="home-feed-actor-line"><ProfileAvatar profile={item.actor} small /><strong className="home-feed-actor-name">{item.actor.display_name}</strong><span className="home-feed-verb">{HOME_FEED_VERBS[item.type]}</span>{item.type === "follow" ? <span className="home-feed-follow-group">{visible.map((name, index) => <strong key={name}>{index ? (index === visible.length - 1 ? " and " : ", ") : ""}{name}</strong>)}{more ? ` and ${more} others` : null}</span> : null}<time dateTime={item.activity_at}>{compactRelativeTime(item.activity_at)}</time></span>{item.type !== "follow" ? <span className="home-feed-grouped-objects">{visible.map((name) => <strong key={name}>{name}</strong>)}{more ? <small>+{more} more</small> : null}</span> : null}</Link>;
  }
  const event = item.target.event;
  const artist = item.target.artist;
  const followed = item.target.user;
  const isRated = item.type === "rated_been";
  const objectName = event?.title ?? artist?.name ?? followed?.display_name;
  return (
    <Link className={`home-feed-item${event ? " home-feed-event" : ""}${isRated ? " home-feed-rich" : ""}`} to={feedItemPath(item)}>
      {event ? (
        <ImageSlot className="home-feed-flier" name={event.title} src={event.cover_image_url} />
      ) : null}
      <span className="home-feed-copy">
        <span className="home-feed-actor-line">
          <ProfileAvatar profile={item.actor} small />
          <strong className="home-feed-actor-name">{item.actor.display_name}</strong>
          <span className="home-feed-verb">{HOME_FEED_VERBS[item.type]}</span>
          {followed ? <strong className="home-feed-followed-name">{objectName}</strong> : null}
          <time dateTime={item.activity_at}>{compactRelativeTime(item.activity_at)}</time>
        </span>
        {event || artist ? <strong className="home-feed-object">{objectName}</strong> : null}
        {isRated ? <RatingStars className="home-feed-stars" value={item.context.rating} /> : null}
        {item.type === "will_be_there" ? (
          <span className="home-feed-meta">{formatEventDateTime(event.event_date, event.start_time)} · {event.venue.name}</span>
        ) : null}
        {isRated && item.context.review ? (
          <FeedReviewExcerpt>{item.context.review.body}</FeedReviewExcerpt>
        ) : null}
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
      {state.results.length > 0 ? <ol className="home-feed-list ledger-list">{groupFeedItems(state.results).map((item) => <li key={`${item.type}-${item.activity_at}-${item.actor.id}-${item.target.event?.id ?? item.target.user?.id ?? item.target.artist?.id}`}><FeedItem item={item} /></li>)}</ol> : null}
      {loadMoreError ? <div className="continuation-feedback home-feed-status" role="alert"><p>More home activity could not be loaded.</p><button className="recovery-action" type="button" disabled={loadingMore} onClick={loadMore}>{loadingMore ? "Retrying…" : "Retry"}</button></div> : null}
      {state.next && !state.error && !loadMoreError ? <button className="pagination-action home-feed-load-more" type="button" disabled={loadingMore} onClick={loadMore}>{loadingMore ? "Loading more…" : "Load more"}</button> : null}
    </main>
  );
}
