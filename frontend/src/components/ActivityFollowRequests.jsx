import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { fetchJson, fetchWithCsrf } from "../api.js";
import { pluralize } from "../lib/plural.js";
import { profilePath } from "../profileRoutes.js";
import ProfileAvatar from "./ProfileAvatar.jsx";

function FollowRequestPagination({ pagination, onPage }) {
  if (pagination.total_pages <= 1) return null;
  return (
    <nav className="activity-follow-request-pagination" aria-label="Follow request pagination">
      <button className="pagination-action quiet-action" type="button" disabled={pagination.previous_page === null} onClick={() => onPage(pagination.previous_page)}>Previous</button>
      <span>Page {pagination.page} of {pagination.total_pages}</span>
      <button className="pagination-action quiet-action" type="button" disabled={pagination.next_page === null} onClick={() => onPage(pagination.next_page)}>Next</button>
    </nav>
  );
}

export default function ActivityFollowRequests({ refreshToken = 0, onDecided = () => {} }) {
  const [page, setPage] = useState(1);
  const [retry, setRetry] = useState(0);
  const [expanded, setExpanded] = useState(false);
  const [pendingUserId, setPendingUserId] = useState(null);
  const [requestErrorUserId, setRequestErrorUserId] = useState(null);
  const [state, setState] = useState({ loading: true, error: null, data: null });

  useEffect(() => {
    const controller = new AbortController();
    setState((current) => current.data
      ? { ...current, loading: true, error: null }
      : { loading: true, error: null, data: null });
    fetchJson(`/api/me/follow-requests/?page=${page}`, { signal: controller.signal, cache: "no-store" })
      .then((data) => setState({ loading: false, error: null, data }))
      .catch((error) => {
        if (error.name !== "AbortError") {
          setState((current) => current.data
            ? { ...current, loading: false, error }
            : { loading: false, error, data: null });
        }
      });
    return () => controller.abort();
  }, [page, refreshToken, retry]);

  async function decide(request, action) {
    const userId = request.user.id;
    setPendingUserId(userId);
    setRequestErrorUserId(null);
    try {
      await fetchWithCsrf(`/api/me/follow-requests/${userId}/${action}/`, { method: "POST" });
      const moveToPreviousPage = state.data?.results.length === 1 && page > 1;
      setState((current) => {
        if (!current.data) return current;
        const results = current.data.results.filter((request) => request.user.id !== userId);
        const totalResults = Math.max(0, current.data.pagination.total_results - 1);
        return {
          ...current,
          data: {
            ...current.data,
            results,
            pagination: {
              ...current.data.pagination,
              total_results: totalResults,
              total_pages: Math.max(1, Math.ceil(totalResults / current.data.pagination.page_size)),
            },
          },
        };
      });
      onDecided(request, action);
      if (moveToPreviousPage) setPage((current) => current - 1);
    } catch (error) {
      if (error.status === 404) {
        onDecided(request, action);
        setRetry((value) => value + 1);
      } else {
        setRequestErrorUserId(userId);
      }
    } finally {
      setPendingUserId(null);
    }
  }

  if (state.loading && !state.data) {
    return <p className="activity-follow-requests-status" role="status" aria-live="polite">Loading follow requests…</p>;
  }
  if (state.error && !state.data) {
    return <div className="activity-follow-requests-status" role="alert"><p>Follow requests could not be loaded.</p><button className="recovery-action quiet-action" type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></div>;
  }
  if (!state.data || state.data.pagination.total_results === 0) return null;

  const requestCount = state.data.pagination.total_results;
  const previewProfiles = state.data.results.slice(0, 2);
  return (
    <section className="activity-follow-requests" aria-busy={state.loading}>
      <button
        className="activity-follow-requests-trigger mobile-target"
        type="button"
        aria-expanded={expanded}
        aria-controls="activity-follow-request-list"
        onClick={() => setExpanded((current) => !current)}
      >
        <span className="activity-follow-request-avatars" aria-hidden="true">
          {previewProfiles.map((request) => <ProfileAvatar key={request.user.id} profile={request.user} small />)}
        </span>
        <span className="activity-follow-request-summary">
          <strong>Follow requests</strong>
          <span>{pluralize(requestCount, "pending request")}</span>
        </span>
        <span className="activity-follow-request-chevron" aria-hidden="true">{expanded ? "▴" : "▾"}</span>
      </button>
      {expanded ? (
        <div id="activity-follow-request-list">
          {state.error ? <div className="activity-follow-requests-error" role="alert"><p>Follow requests could not be refreshed.</p><button className="recovery-action quiet-action" type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></div> : null}
          <ul className="activity-follow-request-list ledger-list">
            {state.data.results.map((request) => (
              <li key={request.user.id}>
                <Link className="activity-follow-request-person" to={profilePath(request.user.username)}>
                  <ProfileAvatar profile={request.user} small />
                  <span><strong>{request.user.display_name}</strong><small>@{request.user.username}</small></span>
                </Link>
                <span className="activity-follow-request-actions">
                  <button className="activity-request-approve mobile-target" type="button" disabled={pendingUserId !== null} aria-busy={pendingUserId === request.user.id} onClick={() => decide(request, "accept")}>Approve</button>
                  <button className="activity-request-delete mobile-target" type="button" disabled={pendingUserId !== null} aria-busy={pendingUserId === request.user.id} onClick={() => decide(request, "decline")}>Delete</button>
                </span>
                {requestErrorUserId === request.user.id ? <p className="activity-follow-request-row-error" role="alert">Request could not be updated. Try again.</p> : null}
              </li>
            ))}
          </ul>
          <FollowRequestPagination pagination={state.data.pagination} onPage={setPage} />
        </div>
      ) : null}
    </section>
  );
}
