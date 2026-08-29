import { useEffect, useState } from "react";
import { Link, Navigate, useLocation } from "react-router-dom";

import { fetchJson, fetchWithCsrf } from "../api.js";
import ActivityFollowRequests from "../components/ActivityFollowRequests.jsx";
import ProfileAvatar from "../components/ProfileAvatar.jsx";
import { activityNotificationPath, activityNotificationVerb, followRequestKey } from "../activityPresentation.js";
import { compactRelativeTime } from "../homeFeedPresentation.js";


export default function ActivityPage({ session }) {
  const location = useLocation();
  const [retry, setRetry] = useState(0);
  const [loadingMore, setLoadingMore] = useState(false);
  const [actionError, setActionError] = useState(null);
  const [markReadState, setMarkReadState] = useState({ loading: false, error: null });
  const [pendingRequestKeys, setPendingRequestKeys] = useState(() => new Set());
  const [requestActions, setRequestActions] = useState({});
  const [requestRefresh, setRequestRefresh] = useState(0);
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

  useEffect(() => {
    if (session.loading || !session.user) {
      setPendingRequestKeys(new Set());
      return undefined;
    }
    const controller = new AbortController();
    fetchJson("/api/me/follow-requests/?page_size=100", { signal: controller.signal, cache: "no-store" })
      .then((data) => setPendingRequestKeys(new Set(data.results.map(followRequestKey))))
      .catch((error) => {
        if (error.name !== "AbortError") setPendingRequestKeys(new Set());
      });
    return () => controller.abort();
  }, [requestRefresh, session.loading, session.user]);

  async function markAllRead(signal) {
    setMarkReadState({ loading: true, error: null });
    try {
      await fetchWithCsrf("/api/me/notifications/read-all/", { method: "POST", ...(signal ? { signal } : {}) });
      if (!signal?.aborted) {
        const readAt = new Date().toISOString();
        setState((current) => ({ ...current, results: current.results.map((notification) => ({ ...notification, read_at: notification.read_at ?? readAt })) }));
        setMarkReadState({ loading: false, error: null });
      }
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

  function removePendingRequest(request) {
    setPendingRequestKeys((current) => {
      const next = new Set(current);
      next.delete(followRequestKey(request));
      return next;
    });
  }

  async function decideRequest(notification, action) {
    setRequestActions((current) => ({
      ...current,
      [notification.id]: { pending: true, action, result: null, error: null },
    }));
    try {
      await fetchWithCsrf(`/api/me/follow-requests/${notification.actor.id}/${action}/`, { method: "POST" });
      removePendingRequest(notification);
      setRequestActions((current) => ({
        ...current,
        [notification.id]: {
          pending: false,
          result: action === "accept" ? "Approved" : "Deleted",
          error: null,
        },
      }));
      setRequestRefresh((current) => current + 1);
    } catch (error) {
      if (error.status === 404) {
        removePendingRequest(notification);
        setRequestActions((current) => ({
          ...current,
          [notification.id]: { pending: false, result: "No longer pending", error: null },
        }));
        setRequestRefresh((current) => current + 1);
        return;
      }
      setRequestActions((current) => ({
        ...current,
        [notification.id]: { pending: false, result: null, error: "Request could not be updated. Try again." },
      }));
    }
  }

  if (session.loading) {
    return <main><p>Checking session…</p></main>;
  }
  if (!session.user) {
    return <Navigate to="/login" replace state={{ from: `${location.pathname}${location.search}` }} />;
  }

  return (
    <main className="activity-page" aria-busy={state.loading}>
      <h1 className="functional-title">Activity</h1>
      <ActivityFollowRequests refreshToken={requestRefresh} onDecided={removePendingRequest} />
      {actionError ? <div className="continuation-feedback" role="alert"><p>{actionError}</p><button className="recovery-action" type="button" disabled={loadingMore} onClick={loadMore}>{loadingMore ? "Retrying…" : "Retry"}</button></div> : null}
      {markReadState.error ? <div className="activity-action-error" role="alert"><p>Activity is visible, but it could not be marked as read.</p><button className="recovery-action" type="button" disabled={markReadState.loading} onClick={() => markAllRead()}>{markReadState.loading ? "Retrying…" : "Retry marking as read"}</button></div> : null}
      {state.loading ? <p role="status" aria-live="polite">Loading activity…</p> : null}
      {state.error ? (
        <div role="alert">
          <p>Activity could not be loaded.</p>
          <button className="recovery-action" type="button" onClick={() => setRetry((value) => value + 1)}>
            Retry
          </button>
        </div>
      ) : null}
      {!state.loading && !state.error && state.results.length === 0 ? (
        <p>No activity yet.</p>
      ) : null}
      {state.results.length > 0 ? (
        <>
          <ol className="activity-list ledger-list">
            {state.results.map((notification) => {
              const requestAction = requestActions[notification.id];
              const actionable = notification.type === "follow_request" && pendingRequestKeys.has(followRequestKey(notification));
              return (
                <li className="activity-item" key={notification.id}>
                  <Link className={`activity-row ${notification.read_at ? "read" : "unread"}`} to={activityNotificationPath(notification)}>
                    <ProfileAvatar profile={notification.actor} small className="activity-avatar" />
                    <span className="activity-row-copy">
                      <span className="activity-message"><strong className="activity-actor">{notification.actor.display_name}</strong> <span className="activity-verb">{activityNotificationVerb(notification)}</span>{notification.event ? <> <span className="activity-object">{notification.event.title}</span>.</> : null}</span>
                      <span className="activity-meta">@{notification.actor.username} · <time dateTime={notification.created_at}>{compactRelativeTime(notification.created_at)}</time></span>
                    </span>
                  </Link>
                  {actionable ? (
                    <span className="activity-request-actions" aria-label={`Follow request from ${notification.actor.display_name}`}>
                      <button className="activity-request-approve mobile-target" type="button" disabled={requestAction?.pending} aria-busy={requestAction?.pending && requestAction.action === "accept"} onClick={() => decideRequest(notification, "accept")}>Approve</button>
                      <button className="activity-request-delete mobile-target" type="button" disabled={requestAction?.pending} aria-busy={requestAction?.pending && requestAction.action === "decline"} onClick={() => decideRequest(notification, "decline")}>Delete</button>
                    </span>
                  ) : requestAction?.result ? <span className="activity-request-result" role="status">{requestAction.result}</span> : null}
                  {requestAction?.error ? <p className="activity-request-error" role="alert">Request could not be updated. Try again.</p> : null}
                </li>
              );
            })}
          </ol>
          {state.nextCursor ? (
            <button className="pagination-action" type="button" disabled={loadingMore} onClick={loadMore}>
              {loadingMore ? "Loading more…" : "Load more"}
            </button>
          ) : null}
        </>
      ) : null}
    </main>
  );
}
