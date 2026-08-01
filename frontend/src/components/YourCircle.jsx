import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { fetchJson, fetchWithCsrf } from "../api.js";
import { profilePath } from "../profileRoutes.js";
import { pluralize } from "../lib/plural.js";
import ExpandableText from "./ExpandableText.jsx";


export default function YourCircle({
  eventId,
  user,
  version,
  onSocialChanged,
  onAuthenticationRequired,
}) {
  const [page, setPage] = useState(1);
  const [retry, setRetry] = useState(0);
  const [actionError, setActionError] = useState(null);
  const [loadingMore, setLoadingMore] = useState(false);
  const [state, setState] = useState({ loading: true, error: null, data: null });

  useEffect(() => {
    if (!user) {
      setState({ loading: false, error: null, data: null });
      return undefined;
    }
    const controller = new AbortController();
    const query = new URLSearchParams({ page: String(page), page_size: "10" });
    if (page === 1) setState({ loading: true, error: null, data: null });
    else setLoadingMore(true);
    fetchJson(`/api/events/${eventId}/circle/?${query}`, {
      cache: "no-store",
      signal: controller.signal,
    })
      .then((data) => { setState((current) => ({ loading: false, error: null, data: page === 1 || !current.data ? data : { ...data, results: [...current.data.results, ...data.results] } })); setLoadingMore(false); })
      .catch((error) => {
        if (error.name !== "AbortError") {
          setState({ loading: false, error, data: null });
        }
      })
      .finally(() => setLoadingMore(false));
    return () => controller.abort();
  }, [eventId, page, retry, user, version]);

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
              {pluralize(state.data.rating_summary.count, "Circle rating")}, including yours.
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
                    <h3><Link to={profilePath(entry.user.username)}>{entry.user.display_name}</Link></h3>
                    <p><Link to={profilePath(entry.user.username)}>@{entry.user.username}</Link></p>
                    <p className="stars">Rating: {pluralize(entry.rating.toFixed(1), "star")}</p>
                    {entry.review ? (
                      <>
                        <ExpandableText>{entry.review.body}</ExpandableText>
                        <p>{pluralize(entry.review.like_count, "like")}</p>
                        <button className="like-action" type="button" onClick={() => changeLike(entry.review)}>
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
          {state.data.pagination.next_page ? <button className="quiet-action" type="button" disabled={loadingMore} onClick={() => setPage(state.data.pagination.next_page)}>{loadingMore ? "Loading more Circle entries." : `Show ${state.data.pagination.total_results - state.data.results.length} more Circle entries`}</button> : null}
        </>
      ) : null}
    </section>
  );
}
