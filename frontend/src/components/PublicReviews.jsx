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
  const [state, setState] = useState({ loading: true, error: null, data: null });

  useEffect(() => {
    const controller = new AbortController();
    const query = new URLSearchParams({ sort, page: String(page) });
    setState({ loading: true, error: null, data: null });
    fetchJson(`/api/events/${eventId}/reviews/?${query}`, {
      cache: "no-store",
      signal: controller.signal,
    })
      .then((data) => setState({ loading: false, error: null, data }))
      .catch((error) => {
        if (error.name !== "AbortError") {
          setState({ loading: false, error, data: null });
        }
      });
    return () => controller.abort();
  }, [eventId, page, retry, sort, user?.id, version]);

  async function changeLike(review) {
    setActionError(null);
    try {
      await fetchWithCsrf(`/api/reviews/${review.id}/like/`, {
        method: review.viewer_has_liked ? "DELETE" : "POST",
      });
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
    }
  }

  return (
    <section className="event-public-reviews">
      <h2>Public</h2>
      <SortMenu value={sort} options={EVENT_REVIEW_SORTS} onChange={(value) => { setSort(value); setPage(1); }} />
      {actionError ? <p>{actionError}</p> : null}
      {state.loading ? <p>Loading public reviews.</p> : null}
      {state.error ? (
        <>
          <p>Public reviews could not be loaded.</p>
          <button type="button" onClick={() => setRetry((value) => value + 1)}>
            Retry
          </button>
        </>
      ) : null}
      {state.data && state.data.results.length === 0 ? (
        <p>No public reviews yet.</p>
      ) : null}
      {state.data && state.data.results.length > 0 ? (
        <>
          <ol>
            {state.data.results.map((review) => (
              <li key={review.id}>
                <EventReviewRow person={review.author} rating={review.rating} review={review} onLike={!user || review.author.id !== user.id ? () => changeLike(review) : null} />
              </li>
            ))}
          </ol>
          {state.data.pagination.total_pages > 1 ? <nav aria-label="Public reviews pagination">
            <button
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
