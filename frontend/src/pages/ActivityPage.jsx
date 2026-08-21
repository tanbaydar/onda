import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { fetchJson, fetchWithCsrf } from "../api.js";
import ProfileAvatar from "../components/ProfileAvatar.jsx";
import { activityNotificationPath, activityNotificationVerb, followRequestKey } from "../activityPresentation.js";
import { compactRelativeTime } from "../homeFeedPresentation.js";


export default function ActivityPage({ session }) {
  const [retry, setRetry] = useState(0);
  const [loadingMore, setLoadingMore] = useState(false);
  const [actionError, setActionError] = useState(null);
  const [pendingRequestKeys, setPendingRequestKeys] = useState(() => new Set());
  const [requestActions, setRequestActions] = useState({});
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
      fetchJson("/api/me/follow-requests/?page_size=100", { signal: controller.signal, cache: "no-store" }),
      fetchWithCsrf("/api/me/notifications/read-all/", { method: "POST", signal: controller.signal }),
    ])
      .then(([data, requests]) => {
        setPendingRequestKeys(new Set(requests.results.map(followRequestKey)));
        setRequestActions({});
        setState({
          loading: false,
          error: null,
          results: data.results,
          nextCursor: data.next_cursor,
        });
      })
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

  async function decideRequest(notification, action) {
    setActionError(null);
    setRequestActions((current) => ({
      ...current,
      [notification.id]: { pending: true, action, result: null, error: null },
    }));
    try {
      await fetchWithCsrf(`/api/me/follow-requests/${notification.actor.id}/${action}/`, { method: "POST" });
      setPendingRequestKeys((current) => {
        const next = new Set(current);
        next.delete(followRequestKey(notification));
        return next;
      });
      setRequestActions((current) => ({
        ...current,
        [notification.id]: {
          pending: false,
          result: action === "accept" ? "Approved" : "Deleted",
          error: null,
        },
      }));
    } catch (error) {
      if (error.status === 404) {
        setPendingRequestKeys((current) => {
          const next = new Set(current);
          next.delete(followRequestKey(notification));
          return next;
        });
        setRequestActions((current) => ({
          ...current,
          [notification.id]: { pending: false, result: "No longer pending", error: null },
        }));
        return;
      }
      setRequestActions((current) => ({
        ...current,
        [notification.id]: { pending: false, result: null, error: "Request could not be updated. Try again." },
      }));
    }
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
            {state.results.map((notification) => {
              const requestAction = requestActions[notification.id];
              const actionable = notification.type === "follow_request" && pendingRequestKeys.has(followRequestKey(notification));
              return (
                <li className="activity-item" key={notification.id}>
                  <Link className={`activity-row ${notification.read_at ? "read" : "unread"}`} to={activityNotificationPath(notification)}>
                    <ProfileAvatar profile={notification.actor} small className="activity-avatar" />
                    <span className="activity-row-copy">
                      <span className="activity-message"><strong>{notification.actor.display_name}</strong> {activityNotificationVerb(notification)}</span>
                      <span className="activity-meta">@{notification.actor.username} · <time dateTime={notification.created_at}>{compactRelativeTime(notification.created_at)}</time></span>
                    </span>
                  </Link>
                  {actionable ? (
                    <span className="activity-request-actions" aria-label={`Follow request from ${notification.actor.display_name}`}>
                      <button className="activity-request-approve" type="button" disabled={requestAction?.pending} aria-busy={requestAction?.pending && requestAction.action === "accept"} onClick={() => decideRequest(notification, "accept")}>Approve</button>
                      <button className="activity-request-delete" type="button" disabled={requestAction?.pending} aria-busy={requestAction?.pending && requestAction.action === "decline"} onClick={() => decideRequest(notification, "decline")}>Delete</button>
                    </span>
                  ) : requestAction?.result ? <span className="activity-request-result" role="status">{requestAction.result}</span> : null}
                  {requestAction?.error ? <p className="activity-request-error" role="alert">{requestAction.error}</p> : null}
                </li>
              );
            })}
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
