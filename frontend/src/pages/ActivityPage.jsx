import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { fetchJson, fetchWithCsrf } from "../api.js";
import { compactRelativeTime } from "../homeFeedPresentation.js";
import { eventPath } from "../entityRoutes.js";


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
  const [markReadState, setMarkReadState] = useState({ loading: false, error: null });
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
    setMarkReadState({ loading: false, error: null });
    fetchJson("/api/me/notifications/", { signal: controller.signal })
      .then((data) => {
        setState({
          loading: false,
          error: null,
          results: data.results,
          nextCursor: data.next_cursor,
        });
        markAllRead(controller.signal);
      })
      .catch((error) => {
        if (error.name !== "AbortError") {
          setState({ loading: false, error, results: [], nextCursor: null });
        }
      });
    return () => controller.abort();
  }, [retry, session.loading, session.user]);

  async function markAllRead(signal) {
    setMarkReadState({ loading: true, error: null });
    try {
      await fetchWithCsrf("/api/me/notifications/read-all/", { method: "POST", ...(signal ? { signal } : {}) });
      if (!signal?.aborted) setMarkReadState({ loading: false, error: null });
    } catch (error) {
      if (error.name !== "AbortError") setMarkReadState({ loading: false, error });
    }
  }

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
    navigate(notification.review ? eventPath({ id: notification.review.event_id, title: notification.review.event_title }) : `/u/${notification.actor.username}`);
  }

  if (session.loading) {
    return <main><p>Checking session…</p></main>;
  }
  if (!session.user) {
    return <main><h1>Activity</h1><p>Sign in to view your activity.</p></main>;
  }

  return (
    <main className="activity-page" aria-busy={state.loading}>
      <h1>Activity</h1>
      {actionError ? <p role="alert">{actionError}</p> : null}
      {markReadState.error ? <div className="activity-action-error" role="alert"><p>Activity is visible, but it could not be marked as read.</p><button type="button" disabled={markReadState.loading} onClick={() => markAllRead()}>{markReadState.loading ? "Retrying…" : "Retry marking as read"}</button></div> : null}
      {state.loading ? <p role="status" aria-live="polite">Loading activity…</p> : null}
      {state.error ? (
        <div role="alert">
          <p>Activity could not be loaded.</p>
          <button type="button" onClick={() => setRetry((value) => value + 1)}>
            Retry
          </button>
        </div>
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
                  <p>@{notification.actor.username} · <time dateTime={notification.created_at}>{compactRelativeTime(notification.created_at)}</time></p>
                </button>
              </li>
            ))}
          </ol>
          {state.nextCursor ? (
            <button type="button" disabled={loadingMore} onClick={loadMore}>
              {loadingMore ? "Loading more…" : "Load more"}
            </button>
          ) : null}
        </>
      ) : null}
    </main>
  );
}
