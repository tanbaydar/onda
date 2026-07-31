import { useEffect, useState } from "react";

import { fetchJson, fetchWithCsrf } from "../api.js";


export default function YourCircle({ eventId, user, onAuthenticationRequired }) {
  const [page, setPage] = useState(1);
  const [retry, setRetry] = useState(0);
  const [actionError, setActionError] = useState(null);
  const [state, setState] = useState({ loading: true, error: null, data: null });

  useEffect(() => {
    if (!user) {
      setState({ loading: false, error: null, data: null });
      return undefined;
    }
    const controller = new AbortController();
    const query = new URLSearchParams({ page: String(page), page_size: "10" });
    setState({ loading: true, error: null, data: null });
    fetchJson(`/api/events/${eventId}/circle/?${query}`, {
      signal: controller.signal,
    })
      .then((data) => setState({ loading: false, error: null, data }))
      .catch((error) => {
        if (error.name !== "AbortError") {
          setState({ loading: false, error, data: null });
        }
      });
    return () => controller.abort();
  }, [eventId, page, retry, user]);

  async function changeLike(review) {
    setActionError(null);
    try {
      await fetchWithCsrf(`/api/reviews/${review.id}/like/`, {
        method: review.viewer_has_liked ? "DELETE" : "POST",
      });
      setRetry((value) => value + 1);
    } catch (error) {
      if (error.status === 401 || error.status === 403) {
        setActionError("Sign in required.");
        onAuthenticationRequired();
      } else {
        setActionError("The review like could not be changed.");
      }
    }
  }

  if (!user) {
    return (
      <section>
        <h2>Your Circle</h2>
        <p>Sign in to see friends&apos; ratings.</p>
      </section>
    );
  }

  return (
    <section>
      <h2>Your Circle</h2>
      {actionError ? <p>{actionError}</p> : null}
      {state.loading ? <p>Loading Your Circle.</p> : null}
      {state.error ? (
        <>
          <p>Your Circle could not be loaded.</p>
          <button type="button" onClick={() => setRetry((value) => value + 1)}>
            Retry
          </button>
        </>
      ) : null}
      {state.data ? (
        <>
          {state.data.rating_summary.state === "available" ? (
            <p>
              {state.data.rating_summary.average.toFixed(1)} average from{" "}
              {state.data.rating_summary.count} Circle ratings, including yours.
            </p>
          ) : (
            <p>No ratings from Your Circle yet.</p>
          )}
          {state.data.results.length === 0 ? (
            <p>No followed users have rated this event.</p>
          ) : (
            <ol>
              {state.data.results.map((entry) => (
                <li key={entry.id}>
                  <article>
                    <h3>{entry.user.display_name}</h3>
                    <p>@{entry.user.username}</p>
                    <p>Rating: {entry.rating.toFixed(1)} stars</p>
                    {entry.review ? (
                      <>
                        <p>{entry.review.body}</p>
                        <p>{entry.review.like_count} likes</p>
                        <button type="button" onClick={() => changeLike(entry.review)}>
                          {entry.review.viewer_has_liked ? "Unlike" : "Like"}
                        </button>
                      </>
                    ) : (
                      <p>No written review.</p>
                    )}
                  </article>
                </li>
              ))}
            </ol>
          )}
          <nav aria-label="Your Circle pagination">
            <button
              type="button"
              disabled={state.data.pagination.previous_page === null}
              onClick={() => setPage(state.data.pagination.previous_page)}
            >
              Previous
            </button>
            <span>
              {" "}Page {state.data.pagination.page} of{" "}
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
