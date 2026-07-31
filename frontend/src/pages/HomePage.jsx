import { useEffect, useState } from "react";
import { Link, Navigate } from "react-router-dom";

import { fetchJson } from "../api.js";
import { formatEventDateTime } from "../formatEventDateTime.js";
import { homeAccessRedirect } from "../landing.js";


function FeedItem({ item }) {
  if (item.type === "follow") {
    return (
      <article>
        <h2>{item.actor.display_name} followed {item.target.user.display_name}</h2>
        <p>@{item.actor.username} followed @{item.target.user.username}.</p>
        <time dateTime={item.activity_at}>{new Date(item.activity_at).toLocaleString()}</time>
      </article>
    );
  }
  const event = item.target.event;
  if (item.type === "will_be_there") {
    return (
      <article>
        <h2>
          {item.actor.display_name} will be at{" "}
          <Link to={`/events/${event.id}`}>{event.title}</Link>
        </h2>
        <p>{formatEventDateTime(event.event_date, event.start_time)}</p>
        <time dateTime={item.activity_at}>{new Date(item.activity_at).toLocaleString()}</time>
      </article>
    );
  }
  if (item.type === "review_like") {
    return (
      <article>
        <h2>
          {item.actor.display_name} liked {item.target.review.author.display_name}&apos;s
          review of <Link to={`/events/${event.id}`}>{event.title}</Link>
        </h2>
        <blockquote>{item.target.review.body}</blockquote>
        <time dateTime={item.activity_at}>{new Date(item.activity_at).toLocaleString()}</time>
      </article>
    );
  }
  return (
    <article>
      <h2>
        {item.actor.display_name} rated{" "}
        <Link to={`/events/${event.id}`}>{event.title}</Link>
      </h2>
      <p>{item.context.rating.toFixed(1)} stars</p>
      <p>{formatEventDateTime(event.event_date, event.start_time)}</p>
      {item.context.review ? <blockquote>{item.context.review.body}</blockquote> : null}
      <time dateTime={item.activity_at}>{new Date(item.activity_at).toLocaleString()}</time>
    </article>
  );
}


export default function HomePage({ session }) {
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({ loading: true, error: null, results: [], next: null });
  const [loadingMore, setLoadingMore] = useState(false);

  useEffect(() => {
    if (!session.user) return undefined;
    const controller = new AbortController();
    setState({ loading: true, error: null, results: [], next: null });
    fetchJson("/api/me/home/", { signal: controller.signal, cache: "no-store" })
      .then((data) => setState({ loading: false, error: null, results: data.results, next: data.next_cursor }))
      .catch((error) => {
        if (error.name !== "AbortError") setState({ loading: false, error, results: [], next: null });
      });
    return () => controller.abort();
  }, [retry, session.user]);

  async function loadMore() {
    setLoadingMore(true);
    try {
      const data = await fetchJson(`/api/me/home/?cursor=${encodeURIComponent(state.next)}`, { cache: "no-store" });
      setState((current) => ({ ...current, results: [...current.results, ...data.results], next: data.next_cursor }));
    } catch (error) {
      setState((current) => ({ ...current, error }));
    } finally {
      setLoadingMore(false);
    }
  }

  if (session.loading) return <main><h1>Home</h1><p>Checking session.</p></main>;
  if (session.error) return <main><h1>Home</h1><p>Home could not be loaded.</p></main>;
  const redirect = homeAccessRedirect(session.user);
  if (redirect) return <Navigate to={redirect} replace />;
  return (
    <main>
      <h1>Home</h1>
      {state.loading ? <p>Loading activity.</p> : null}
      {state.error ? (
        <><p>Home activity could not be loaded.</p><button type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></>
      ) : null}
      {!state.loading && !state.error && state.results.length === 0 ? (
        <p>No activity from people you follow yet. <Link to="/discover">Discover events</Link>.</p>
      ) : null}
      {state.results.length > 0 ? <ol>{state.results.map((item) => <li key={`${item.type}-${item.activity_at}-${item.actor.id}-${item.target.event?.id ?? item.target.user?.id}`}><FeedItem item={item} /></li>)}</ol> : null}
      {state.next && !state.error ? <button type="button" disabled={loadingMore} onClick={loadMore}>{loadingMore ? "Loading more." : "Load more"}</button> : null}
    </main>
  );
}
