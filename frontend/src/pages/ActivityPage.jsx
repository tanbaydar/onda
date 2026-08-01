import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { fetchJson, fetchWithCsrf } from "../api.js";
import { formatTimestamp } from "../lib/formatTimestamp.js";


function notificationText(notification) {
  if (notification.type === "review_like") {
    return `${notification.actor.display_name} liked your review.`;
  }
  if (notification.type === "follow") {
    return `${notification.actor.display_name} followed you.`;
  }
  if (notification.type === "follow_request") {
    return `${notification.actor.display_name} requested to follow you.`;
  }
  return `${notification.actor.display_name} accepted your follow request.`;
}


export default function ActivityPage({ session }) {
  const navigate = useNavigate();
  const [retry, setRetry] = useState(0);
  const [loadingMore, setLoadingMore] = useState(false);
  const [actionError, setActionError] = useState(null);
  const [state, setState] = useState({
    loading: true,
    error: null,
    results: [],
    nextCursor: null,
  });

  useEffect(() => {
    if (session.loading || !session.user) {
      setState({ loading: false, error: null, results: [], nextCursor: null });
      return undefined;
    }
    const controller = new AbortController();
    setState({ loading: true, error: null, results: [], nextCursor: null });
    Promise.all([
      fetchJson("/api/me/notifications/", { signal: controller.signal }),
      fetchWithCsrf("/api/me/notifications/read-all/", { method: "POST", signal: controller.signal }),
    ])
      .then(([data]) =>
        setState({
          loading: false,
          error: null,
          results: data.results,
          nextCursor: data.next_cursor,
        }),
      )
      .catch((error) => {
        if (error.name !== "AbortError") {
          setState({ loading: false, error, results: [], nextCursor: null });
        }
      });
    return () => controller.abort();
  }, [retry, session.loading, session.user]);

  async function loadMore() {
    setLoadingMore(true);
    setActionError(null);
    try {
      const query = new URLSearchParams({ cursor: state.nextCursor });
      const data = await fetchJson(`/api/me/notifications/?${query}`);
      setState((current) => ({
        ...current,
        results: [...current.results, ...data.results],
        nextCursor: data.next_cursor,
      }));
    } catch {
      setActionError("More activity could not be loaded.");
    } finally {
      setLoadingMore(false);
    }
  }

  function openNotification(notification) {
    navigate(notification.review ? `/events/${notification.review.event_id}` : `/u/${notification.actor.username}`);
  }

  if (session.loading) {
    return <main><p>Checking session.</p></main>;
  }
  if (!session.user) {
    return <main><h1>Activity</h1><p>Sign in to view your activity.</p></main>;
  }

  return (
    <main className="activity-page">
      <h1>Activity</h1>
      {actionError ? <p>{actionError}</p> : null}
      {state.loading ? <p>Loading activity.</p> : null}
      {state.error ? (
        <>
          <p>Activity could not be loaded.</p>
          <button type="button" onClick={() => setRetry((value) => value + 1)}>
            Retry
          </button>
        </>
      ) : null}
      {!state.loading && !state.error && state.results.length === 0 ? (
        <p>No activity yet.</p>
      ) : null}
      {state.results.length > 0 ? (
        <>
          <ol className="activity-list">
            {state.results.map((notification) => (
              <li key={notification.id}>
                <button className={`activity-row ${notification.read_at ? "read" : "unread"}`} type="button" onClick={() => openNotification(notification)}>
                  <p><strong>{notificationText(notification)}</strong></p>
                  <p>@{notification.actor.username} · <time dateTime={notification.created_at}>{formatTimestamp(notification.created_at)}</time></p>
                </button>
              </li>
            ))}
          </ol>
          {state.nextCursor ? (
            <button type="button" disabled={loadingMore} onClick={loadMore}>
              {loadingMore ? "Loading more." : "Load more"}
            </button>
          ) : null}
        </>
      ) : null}
    </main>
  );
}
