import { useEffect, useRef, useState } from "react";
import { fetchJson } from "../api.js";
import { appendUniqueEvents } from "../eventListPresentation.js";
import EventRowPresenter from "./EventRowPresenter.jsx";

export default function EventList({
  heading,
  scopeName,
  scopeId,
  when,
  emptyMessage,
  pageSize = 20,
  showVenue = true,
  omittedArtistId = null,
  quietHeading = false,
  discover = false,
  ledger = null,
  onLedgerChange = null,
}) {
  const loadMoreRef = useRef(null);
  const [localPage, setLocalPage] = useState(1);
  const [localRetry, setLocalRetry] = useState(0);
  const [localState, setLocalState] = useState({
    loading: true,
    error: null,
    data: null,
  });
  const page = ledger?.page ?? localPage;
  const retry = ledger?.retry ?? localRetry;
  const state = ledger?.state ?? localState;
  const setPage = (nextPage) => ledger
    ? onLedgerChange((current) => ({ ...current, page: nextPage }))
    : setLocalPage(nextPage);
  const setRetry = (update) => ledger
    ? onLedgerChange((current) => ({ ...current, retry: update(current.retry) }))
    : setLocalRetry(update);
  const setState = (update) => ledger
    ? onLedgerChange((current) => ({ ...current, state: typeof update === "function" ? update(current.state) : update }))
    : setLocalState(update);

  useEffect(() => {
    const controller = new AbortController();
    const requestKey = `${when}:${scopeName}:${scopeId}:${page}:${pageSize}:${retry}`;
    if (ledger?.requestKey === requestKey && ledger.state.data && !ledger.state.error) return () => controller.abort();
    const query = new URLSearchParams({
      when,
      [scopeName]: String(scopeId),
      page: String(page),
      page_size: String(pageSize),
    });

    if (ledger) onLedgerChange((current) => ({ ...current, requestKey }));
    setState((current) => ({ loading: true, error: null, data: page > 1 ? current.data : null }));
    fetchJson(`/api/events/?${query}`, { signal: controller.signal })
      .then((data) => {
        setState((current) => ({ loading: false, error: null, data: discover && page > 1 && current.data ? { ...data, results: appendUniqueEvents(current.data.results, data.results) } : data }));
      })
      .catch((error) => {
        if (error.name !== "AbortError") {
          setState((current) => ({
            loading: false,
            error,
            data: page > 1 ? current.data : null,
          }));
        }
      });

    return () => controller.abort();
  }, [discover, page, pageSize, retry, scopeId, scopeName, when]);

  const nextPage = discover ? state.data?.pagination.next_page : null;
  useEffect(() => {
    const target = loadMoreRef.current;
    if (!target || !nextPage || state.loading || state.error) return undefined;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setPage(nextPage);
      },
      { rootMargin: "320px 0px" },
    );
    observer.observe(target);
    return () => observer.disconnect();
  }, [nextPage, state.error, state.loading]);

  const errorState = state.error ? (
    <div className="event-list-error" role="alert">
      <p>{state.data ? "More events could not be loaded." : "Events could not be loaded."}</p>
      <button className="recovery-action" type="button" onClick={() => setRetry((value) => value + 1)}>
        Retry
      </button>
    </div>
  ) : null;

  return (
    <section className={`event-list ${discover ? "discover-event-list" : "detail-event-list"}`} aria-busy={state.loading}>
      <h2 className={quietHeading ? "sr-only" : "section-heading"}>{heading}</h2>
      {state.loading && !state.data ? <p className="event-list-status" role="status">Loading events…</p> : null}
      {state.error && !state.data ? errorState : null}
      {state.data && state.data.results.length === 0 ? (
        <p>{emptyMessage}</p>
      ) : null}
      {state.data && state.data.results.length > 0 ? (
        <>
          <ul className="discover-event-ledger ledger-list">
            {state.data.results.map((event) => (
              <EventRowPresenter
                key={event.id}
                event={event}
                variant="standard-ledger"
                showVenue={showVenue}
                venueFirst={discover}
                omittedArtistId={omittedArtistId}
                compact={!discover}
              />
            ))}
          </ul>
          {state.error ? errorState : null}
          {discover ? (state.data.pagination.next_page ? <div className="discover-scroll-sentinel" ref={loadMoreRef} role="status" aria-live="polite">{state.loading ? "Loading more events…" : ""}</div> : null) : state.data.pagination.total_pages > 1 ? <nav className="ledger-pagination" aria-label={`${heading} pagination`}>
            <button
              className="quiet-control pagination-action"
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
              className="quiet-control pagination-action"
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
