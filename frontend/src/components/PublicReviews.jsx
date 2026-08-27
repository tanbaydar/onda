import { useEffect, useState } from "react";
import { fetchJson, fetchWithCsrf } from "../api.js";
import EventReviewRow from "./EventReviewRow.jsx";
import SortMenu from "./SortMenu.jsx";

const EVENT_REVIEW_SORTS = [
  { value: "most_liked", label: "Most liked" },
  { value: "newest", label: "Newest" },
];


export default function PublicReviews({
  eventId,
  user,
  version,
  onSocialChanged,
  onAuthenticationRequired,
}) {
  const [sort, setSort] = useState("most_liked");
  const [page, setPage] = useState(1);
  const [retry, setRetry] = useState(0);
  const [actionError, setActionError] = useState(null);
  const [pendingLikes, setPendingLikes] = useState(() => new Set());
  const [state, setState] = useState({ loading: true, error: null, data: null });

  useEffect(() => {
    const controller = new AbortController();
    const query = new URLSearchParams({ sort, page: String(page) });
    setState((current) => current.data
      ? { ...current, loading: false, error: null }
      : { loading: true, error: null, data: null });
    fetchJson(`/api/events/${eventId}/reviews/?${query}`, {
      cache: "no-store",
      signal: controller.signal,
    })
      .then((data) => setState({ loading: false, error: null, data }))
      .catch((error) => {
        if (error.name !== "AbortError") {
          setState((current) => ({ loading: false, error, data: current.data }));
        }
      });
    return () => controller.abort();
  }, [eventId, page, retry, sort, user?.id, version]);

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
          results: current.data.results.map((item) => item.id === review.id
            ? { ...item, viewer_has_liked: adding, like_count: nextLikeCount }
            : item),
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

  return (
    <section className="event-public-reviews" aria-busy={state.loading}>
      <h2 className="section-heading">Public</h2>
      {state.data?.results.length ? <SortMenu value={sort} options={EVENT_REVIEW_SORTS} onChange={(value) => { setSort(value); setPage(1); }} /> : null}
      {actionError ? <p className="favorite-notice" role="alert">{actionError}</p> : null}
      {state.loading ? <p role="status" aria-live="polite">Loading public reviews…</p> : null}
      {state.error ? (
        <div role="alert">
          <p>Public reviews could not be loaded.</p>
          <button className="recovery-action" type="button" onClick={() => setRetry((value) => value + 1)}>
            Retry
          </button>
        </div>
      ) : null}
      {state.data && state.data.results.length === 0 ? (
        <p>No public reviews yet.</p>
      ) : null}
      {state.data && state.data.results.length > 0 ? (
        <>
          <ol className="review-ledger ledger-list">
            {state.data.results.map((review) => (
              <li key={review.id}>
                <EventReviewRow person={review.author} rating={review.rating} review={review} onLike={!user || review.author.id !== user.id ? () => changeLike(review) : null} likePending={pendingLikes.has(review.id)} />
              </li>
            ))}
          </ol>
          {state.data.pagination.total_pages > 1 ? <nav aria-label="Public reviews pagination">
            <button
              className="pagination-action"
              type="button"
              disabled={state.data.pagination.previous_page === null}
              onClick={() => setPage(state.data.pagination.previous_page)}
            >
              Previous
            </button>
            <span>
              {" "}
              Page {state.data.pagination.page} of{" "}
              {state.data.pagination.total_pages}{" "}
            </span>
            <button
              className="pagination-action"
              type="button"
              disabled={state.data.pagination.next_page === null}
              onClick={() => setPage(state.data.pagination.next_page)}
            >
              Next
            </button>
          </nav> : null}
        </>
      ) : null}
    </section>
  );
}
