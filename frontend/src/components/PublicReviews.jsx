import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { fetchJson, fetchWithCsrf } from "../api.js";
import { profilePath } from "../profileRoutes.js";


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
    <section>
      <h2>Public reviews</h2>
      <p>
        <label htmlFor="review-sort">Sort reviews</label>{" "}
        <select
          id="review-sort"
          value={sort}
          onChange={(event) => {
            setSort(event.target.value);
            setPage(1);
          }}
        >
          <option value="most_liked">Most liked</option>
          <option value="newest">Newest</option>
        </select>
      </p>
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
                <article>
                  <h3><Link to={profilePath(review.author.username)}>{review.author.display_name}</Link></h3>
                  <p><Link to={profilePath(review.author.username)}>@{review.author.username}</Link></p>
                  <p>Rating: {review.rating.toFixed(1)} stars</p>
                  <p>{review.body}</p>
                  <p>
                    Published {new Date(review.published_at).toLocaleString()}
                  </p>
                  <p>{review.like_count} likes</p>
                  {!user || review.author.id !== user.id ? (
                    <button type="button" onClick={() => changeLike(review)}>
                      {review.viewer_has_liked ? "Unlike" : "Like"}
                    </button>
                  ) : null}
                </article>
              </li>
            ))}
          </ol>
          <nav aria-label="Public reviews pagination">
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
          </nav>
        </>
      ) : null}
    </section>
  );
}
