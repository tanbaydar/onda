import { useEffect, useState } from "react";
import { fetchJson, fetchWithCsrf } from "../api.js";
import { pluralize } from "../lib/plural.js";
import EventReviewRow from "./EventReviewRow.jsx";
import RatingStars from "./RatingStars.jsx";
import { Link } from "react-router-dom";


export default function YourCircle({
  eventId,
  user,
  version,
  onSocialChanged,
  onAuthenticationRequired,
  returnTo = null,
}) {
  const [page, setPage] = useState(1);
  const [retry, setRetry] = useState(0);
  const [actionError, setActionError] = useState(null);
  const [loadingMore, setLoadingMore] = useState(false);
  const [pendingLikes, setPendingLikes] = useState(() => new Set());
  const [state, setState] = useState({ loading: true, error: null, data: null });

  useEffect(() => {
    setPage(1);
  }, [eventId, version]);

  useEffect(() => {
    if (!user) {
      setState({ loading: false, error: null, data: null });
      return undefined;
    }
    const controller = new AbortController();
    const query = new URLSearchParams({ page: String(page), page_size: "10" });
    if (page === 1) setState((current) => current.data
      ? { ...current, loading: false, error: null }
      : { loading: true, error: null, data: null });
    else setLoadingMore(true);
    fetchJson(`/api/events/${eventId}/circle/?${query}`, {
      cache: "no-store",
      signal: controller.signal,
    })
      .then((data) => { setState((current) => ({ loading: false, error: null, data: page === 1 || !current.data ? data : { ...data, results: [...current.data.results.filter((existing) => !data.results.some((item) => item.id === existing.id)), ...data.results] } })); setLoadingMore(false); })
      .catch((error) => {
        if (error.name !== "AbortError") {
          setState((current) => ({ loading: false, error, data: current.data }));
        }
      })
      .finally(() => setLoadingMore(false));
    return () => controller.abort();
  }, [eventId, page, retry, user, version]);

  async function changeLike(review) {
    setActionError(null);
    setPendingLikes((current) => new Set(current).add(review.id));
    try {
      const adding = !review.viewer_has_liked;
      const response = await fetchWithCsrf(`/api/reviews/${review.id}/like/`, {
        method: adding ? "POST" : "DELETE",
      });
      const nextLikeCount = adding
        ? response?.like_count ?? review.like_count + 1
        : Math.max(0, review.like_count - 1);
      setState((current) => current.data ? {
        ...current,
        data: {
          ...current.data,
          results: current.data.results.map((entry) => entry.review?.id === review.id
            ? { ...entry, review: { ...entry.review, viewer_has_liked: adding, like_count: nextLikeCount } }
            : entry),
        },
      } : current);
      onSocialChanged();
    } catch (error) {
      if (error.status === 401 || error.status === 403) {
        setActionError("Sign in required.");
        onAuthenticationRequired();
      } else if (error.status === 404 || error.status === 409) {
        onSocialChanged();
      } else {
        setActionError("The review like could not be changed.");
      }
    } finally {
      setPendingLikes((current) => {
        const next = new Set(current);
        next.delete(review.id);
        return next;
      });
    }
  }

  if (!user) {
    return (
      <section className="authentication-boundary">
        <p><Link to="/login" state={returnTo ? { from: returnTo } : undefined}>Sign in</Link> to see ratings from Your Circle.</p>
      </section>
    );
  }

  return (
    <section className="event-circle" aria-busy={state.loading}>
      <h2 className="section-heading">Your Circle</h2>
      {actionError ? <p className="favorite-notice" role="alert">{actionError}</p> : null}
      {state.loading ? <p role="status" aria-live="polite">Loading Your Circle…</p> : null}
      {state.error ? (
        <div role="alert">
          <p>Your Circle could not be loaded.</p>
          <button className="recovery-action" type="button" onClick={() => setRetry((value) => value + 1)}>
            Retry
          </button>
        </div>
      ) : null}
      {state.data ? (
        <>
          {state.data.rating_summary.state === "available" ? (
            <div
              className="circle-rating-summary"
              aria-label={`${state.data.rating_summary.average.toFixed(1)} average from ${pluralize(state.data.rating_summary.count, "rating")} from Your Circle, including yours.`}
            >
              <div className="circle-rating-score" aria-hidden="true">
                <strong>{state.data.rating_summary.average.toFixed(1)}</strong>
                <span>Average</span>
              </div>
              <div className="circle-rating-context" aria-hidden="true">
                <RatingStars className="circle-rating-stars" value={state.data.rating_summary.average} />
                <p>{pluralize(state.data.rating_summary.count, "rating")}</p>
                <small>Including yours</small>
              </div>
            </div>
          ) : (
            <p>No ratings from Your Circle yet.</p>
          )}
          {state.data.results.length === 0 ? (
            <p>No followed users have rated this event.</p>
          ) : (
            <ol className="review-ledger ledger-list">
              {state.data.results.map((entry) => (
                <li key={entry.id}>
                  <EventReviewRow person={entry.user} rating={entry.rating} review={entry.review} ratedAt={entry.rated_at} onLike={entry.review ? () => changeLike(entry.review) : null} likePending={pendingLikes.has(entry.review?.id)} />
                </li>
              ))}
            </ol>
          )}
          {state.data.pagination.next_page ? <button className="pagination-action quiet-action" type="button" disabled={loadingMore} onClick={() => setPage(state.data.pagination.next_page)}>{loadingMore ? "Loading more Circle entries…" : `Show ${state.data.pagination.total_results - state.data.results.length} more Circle entries`}</button> : null}
        </>
      ) : null}
    </section>
  );
}
