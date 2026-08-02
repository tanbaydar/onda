import { useEffect, useState } from "react";
import { fetchJson } from "../api.js";
import DiscoverEventRow from "./DiscoverEventRow.jsx";

export default function EventList({
  heading,
  scopeName,
  scopeId,
  when,
  emptyMessage,
  pageSize = 20,
  showVenue = true,
  omittedArtistId = null,
  hidden = false,
  quietHeading = false,
  discover = false,
}) {
  const [page, setPage] = useState(1);
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({
    loading: true,
    error: null,
    data: null,
  });

  useEffect(() => {
    const controller = new AbortController();
    const query = new URLSearchParams({
      when,
      [scopeName]: String(scopeId),
      page: String(page),
      page_size: String(pageSize),
    });

    setState((current) => ({ loading: true, error: null, data: discover && page > 1 ? current.data : null }));
    fetchJson(`/api/events/?${query}`, { signal: controller.signal })
      .then((data) => {
        setState((current) => ({ loading: false, error: null, data: discover && page > 1 && current.data ? { ...data, results: [...current.data.results, ...data.results] } : data }));
      })
      .catch((error) => {
        if (error.name !== "AbortError") {
          setState({ loading: false, error, data: null });
        }
      });

    return () => controller.abort();
  }, [discover, page, pageSize, retry, scopeId, scopeName, when]);

  return (
    <section className="event-list" hidden={hidden}>
      <h2 className={quietHeading ? "sr-only" : undefined}>{heading}</h2>
      {state.loading ? <p>Loading events.</p> : null}
      {state.error ? (
        <>
          <p>Events could not be loaded.</p>
          <button type="button" onClick={() => setRetry((value) => value + 1)}>
            Retry
          </button>
        </>
      ) : null}
      {state.data && state.data.results.length === 0 ? (
        <p>{emptyMessage}</p>
      ) : null}
      {state.data && state.data.results.length > 0 ? (
        <>
          <ul className="discover-event-ledger">
            {state.data.results.map((event) => (
              <DiscoverEventRow
                key={event.id}
                event={event}
                showVenue={showVenue}
                omittedArtistId={omittedArtistId}
              />
            ))}
          </ul>
          {discover ? (state.data.pagination.next_page ? <button className="discover-load-more" type="button" disabled={state.loading} onClick={() => setPage(state.data.pagination.next_page)}>{state.loading ? "Loading…" : "Load more"}</button> : null) : <nav className="ledger-pagination" aria-label={`${heading} pagination`}>
            <button
              className="quiet-control"
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
              className="quiet-control"
              type="button"
              disabled={state.data.pagination.next_page === null}
              onClick={() => setPage(state.data.pagination.next_page)}
            >
              Next
            </button>
          </nav>}
        </>
      ) : null}
    </section>
  );
}
