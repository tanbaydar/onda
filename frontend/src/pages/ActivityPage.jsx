import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { fetchJson, fetchWithCsrf } from "../api.js";


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
    fetchJson("/api/me/notifications/", { signal: controller.signal })
      .then((data) =>
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

  async function markRead(notification, destination = null) {
    setActionError(null);
    try {
      const data = await fetchWithCsrf(
        `/api/me/notifications/${notification.id}/read/`,
        { method: "POST" },
      );
      setState((current) => ({
        ...current,
        results: current.results.map((item) =>
          item.id === notification.id
            ? { ...item, read_at: data.notification.read_at }
            : item,
        ),
      }));
      if (destination) {
        navigate(destination);
      }
    } catch {
      setActionError("The notification could not be marked as read.");
    }
  }

  async function markAllRead() {
    setActionError(null);
    try {
      const data = await fetchWithCsrf("/api/me/notifications/read-all/", {
        method: "POST",
      });
      setState((current) => ({
        ...current,
        results: current.results.map((item) => ({
          ...item,
          read_at: item.read_at ?? data.read_at,
        })),
      }));
    } catch {
      setActionError("Activity could not be marked as read.");
    }
  }

  if (session.loading) {
    return <main><p>Checking session.</p></main>;
  }
  if (!session.user) {
    return <main><h1>Activity</h1><p>Sign in to view your activity.</p></main>;
  }

  return (
    <main>
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
          <p><button type="button" onClick={markAllRead}>Mark all as read</button></p>
          <ol>
            {state.results.map((notification) => (
              <li key={notification.id}>
                <article>
                  <p>{notification.read_at ? "Read" : "Unread"}</p>
                  <p>{notificationText(notification)}</p>
                  <p>@{notification.actor.username}</p>
                  {notification.review ? (
                    <button
                      type="button"
                      onClick={() =>
                        markRead(notification, `/events/${notification.review.event_id}`)
                      }
                    >
                      Open event
                    </button>
                  ) : !notification.read_at ? (
                    <button type="button" onClick={() => markRead(notification)}>
                      Mark as read
                    </button>
                  ) : null}
                </article>
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
