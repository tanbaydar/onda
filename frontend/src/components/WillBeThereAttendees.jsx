import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { fetchJson } from "../api.js";
import { profilePath } from "../profileRoutes.js";
import ProfileAvatar from "./ProfileAvatar.jsx";


export default function WillBeThereAttendees({ eventId, scope, user, version, activeCount = null }) {
  const [page, setPage] = useState(1);
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({ loading: true, error: null, data: null });
  const isCircle = scope === "circle";

  useEffect(() => {
    setPage(1);
  }, [eventId, version]);

  useEffect(() => {
    if (isCircle && !user) {
      setState({ loading: false, error: null, data: null });
      return undefined;
    }
    const controller = new AbortController();
    const query = new URLSearchParams({ page: String(page), page_size: "20" });
    setState((current) => current.data
      ? { ...current, loading: false, error: null }
      : { loading: true, error: null, data: null });
    fetchJson(`/api/events/${eventId}/will-be-there/${scope}/?${query}`, {
      cache: "no-store",
      signal: controller.signal,
    })
      .then((data) => setState({ loading: false, error: null, data }))
      .catch((error) => {
        if (error.name !== "AbortError") {
          setState((current) => current.data
            ? { ...current, loading: false, error }
            : { loading: false, error, data: null });
        }
      });
    return () => controller.abort();
  }, [eventId, isCircle, page, retry, scope, user, version]);

  const heading = isCircle ? "Your Circle" : "Public";
  if (isCircle && !user) {
    return (
      <section>
        <h2>{heading}</h2>
        <p>Sign in to see which people in your Circle will be there.</p>
      </section>
    );
  }
  return (
    <section>
      <h2>{heading}</h2>
      {state.loading ? <p>Loading attendees…</p> : null}
      {state.error ? (
        <>
          <p>Attendees could not be loaded.</p>
          <button type="button" onClick={() => setRetry((value) => value + 1)}>
            Retry
          </button>
        </>
      ) : null}
      {state.data && state.data.results.length === 0 ? (
        <p>{isCircle ? "No one in your Circle has marked Will Be There." : activeCount === 0 ? "No active marks yet." : "No public marks are visible."}</p>
      ) : null}
      {state.data && state.data.results.length > 0 ? (
        <>
          <ol className="event-attendee-list">
            {state.data.results.map((attendee) => (
              <li key={attendee.user.id}>
                <Link className="event-attendee-row" to={profilePath(attendee.user.username)}>
                  <ProfileAvatar profile={attendee.user} small />
                  <span><strong>{attendee.user.display_name}</strong><small>@{attendee.user.username}</small></span>
                </Link>
              </li>
            ))}
          </ol>
          {state.data.pagination.total_pages > 1 ? <nav aria-label={`${heading} pagination`}>
            <button
              type="button"
              disabled={state.data.pagination.previous_page === null}
              onClick={() => setPage(state.data.pagination.previous_page)}
            >
              Previous
            </button>
            <span>
              {" "}Page {state.data.pagination.page} of {state.data.pagination.total_pages}{" "}
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
