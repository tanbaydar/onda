import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { fetchJson } from "../api.js";
import { formatEventDateTime } from "../formatEventDateTime.js";
import { pluralize } from "../lib/plural.js";


export default function BeenPage({ session }) {
  const [page, setPage] = useState(1);
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({
    loading: false,
    error: null,
    data: null,
  });

  useEffect(() => {
    if (!session.user) {
      setState({ loading: false, error: null, data: null });
      return undefined;
    }
    const controller = new AbortController();
    setState({ loading: true, error: null, data: null });
    fetchJson(`/api/me/been/?page=${page}`, { signal: controller.signal })
      .then((data) => setState({ loading: false, error: null, data }))
      .catch((error) => {
        if (error.name !== "AbortError") {
          setState({ loading: false, error, data: null });
        }
      });
    return () => controller.abort();
  }, [page, retry, session.user]);

  if (session.loading) {
    return (
      <main>
        <p>Checking session.</p>
      </main>
    );
  }
  if (!session.user) {
    return (
      <main>
        <h1>Been</h1>
        <p>
          <Link to="/login">Sign in</Link> to see your diary.
        </p>
      </main>
    );
  }

  return (
    <main>
      <h1>Been</h1>
      {state.loading ? <p>Loading your diary.</p> : null}
      {state.error ? (
        <>
          <p>Your diary could not be loaded.</p>
          <button type="button" onClick={() => setRetry((value) => value + 1)}>
            Retry
          </button>
        </>
      ) : null}
      {state.data && state.data.results.length === 0 ? (
        <p>You have not added any events to Been.</p>
      ) : null}
      {state.data && state.data.results.length > 0 ? (
        <>
          <ol>
            {state.data.results.map((entry) => (
              <li key={entry.id}>
                <article>
                  <h2>
                    <Link to={`/events/${entry.event.id}`}>
                      {entry.event.title}
                    </Link>
                  </h2>
                  <p>
                    <time
                      dateTime={
                        entry.event.start_time
                          ? `${entry.event.event_date}T${entry.event.start_time}`
                          : entry.event.event_date
                      }
                    >
                      {formatEventDateTime(
                        entry.event.event_date,
                        entry.event.start_time,
                      )}
                    </time>
                  </p>
                  <p>
                    {entry.rating === null
                      ? "Unrated"
                      : `Your rating: ${pluralize(entry.rating.toFixed(1), "star")}`}
                  </p>
                  {entry.has_review ? <p>Written review</p> : null}
                </article>
              </li>
            ))}
          </ol>
          <nav aria-label="Been pagination">
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
    </main>
  );
}
