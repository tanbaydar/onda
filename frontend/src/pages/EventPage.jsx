import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ApiError, fetchJson, fetchWithCsrf } from "../api.js";
import PublicReviews from "../components/PublicReviews.jsx";
import YourCircle from "../components/YourCircle.jsx";
import WillBeThereAttendees from "../components/WillBeThereAttendees.jsx";
import { formatEventDateTime } from "../formatEventDateTime.js";
import FavoriteControl from "../components/FavoriteControl.jsx";
import { pluralize } from "../lib/plural.js";
import ConfirmDialog from "../components/ConfirmDialog.jsx";
import RatingHistogram from "../components/RatingHistogram.jsx";
import StarInput from "../components/StarInput.jsx";
import ImageSlot from "../components/ImageSlot.jsx";
import { eventIsPast } from "../eventTime.js";
import { artistPath, eventPath, venuePath } from "../entityRoutes.js";
import EventReviewRow from "../components/EventReviewRow.jsx";
import useCanonicalEntityRoute from "../useCanonicalEntityRoute.js";
import "../eventReviews.css";


export default function EventPage({ user, sessionReady, onAuthenticationRequired }) {
  const { eventKey } = useParams();
  const [retry, setRetry] = useState(0);
  const [rating, setRating] = useState("");
  const [reviewBody, setReviewBody] = useState("");
  const [socialVersion, setSocialVersion] = useState(0);
  const [willBeThereVersion, setWillBeThereVersion] = useState(0);
  const [saving, setSaving] = useState(false);
  const [actionError, setActionError] = useState(null);
  const [willBeThereError, setWillBeThereError] = useState(null);
  const [confirmation, setConfirmation] = useState(null);
  const [editingEntry, setEditingEntry] = useState(false);
  const [state, setState] = useState({
    loading: true,
    error: null,
    event: null,
    notFound: false,
  });
  const eventId = useCanonicalEntityRoute(eventKey, state.event, eventPath);

  useEffect(() => {
    const controller = new AbortController();
    setState((current) => current.event?.id === eventId
      ? { ...current, loading: false, error: null, notFound: false }
      : { loading: true, error: null, event: null, notFound: false });
    if (!sessionReady) return () => controller.abort();
    if (eventId === null) {
      setState({ loading: false, error: null, event: null, notFound: true });
      return () => controller.abort();
    }
    fetchJson(`/api/events/${eventId}/`, { signal: controller.signal })
      .then((event) => {
        setState({ loading: false, error: null, event, notFound: false });
        setRating(
          event.viewer_entry?.rating === null ||
            event.viewer_entry?.rating === undefined
            ? ""
            : String(event.viewer_entry.rating),
        );
        setReviewBody(event.viewer_entry?.review?.body ?? "");
      })
      .catch((error) => {
        if (error.name === "AbortError") {
          return;
        }
        setState((current) => current.event?.id === eventId && error.status !== 404
          ? { ...current, loading: false, error: null, notFound: false }
          : {
              loading: false,
              error: error.status === 404 ? null : error,
              event: null,
              notFound: error instanceof ApiError && error.status === 404,
            });
      });
    return () => controller.abort();
  }, [eventId, retry, sessionReady, user?.id]);

  function changeFavorite(nextFavorite) {
    if (!nextFavorite) {
      setRetry((value) => value + 1);
      return;
    }
    setState((current) => current.event ? {
      ...current,
      event: { ...current.event, viewer_favorite: nextFavorite },
    } : current);
  }

  async function mutate(path, options, { reviewsChanged = false } = {}) {
    setSaving(true);
    setActionError(null);
    try {
      await fetchWithCsrf(path, options);
      setRetry((value) => value + 1);
      if (reviewsChanged) {
        setSocialVersion((value) => value + 1);
      }
    } catch (error) {
      if (error.status === 401 || error.status === 403) {
        setActionError("Sign in required.");
        onAuthenticationRequired();
      } else {
        const messages = error.data?.errors
          ? Object.values(error.data.errors).flat()
          : ["The Been entry could not be changed."];
        setActionError(messages.join(" "));
      }
    } finally {
      setSaving(false);
    }
  }

  function saveRating(nextRating = rating) {
    mutate(`/api/events/${eventId}/been/`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rating: Number(nextRating) }),
    });
  }

  function removeRating() {
    const warning = state.event.viewer_entry?.review
      ? "Remove your rating? The event will remain in Been, but your written review and all of its likes will be permanently deleted."
      : "Remove your rating? The event will remain in Been.";
    setConfirmation({ title: "Remove your rating?", consequence: warning.replace("Remove your rating? ", ""), label: "Remove rating", action: () => mutate(`/api/events/${eventId}/been/rating/`, { method: "DELETE" }, { reviewsChanged: true }) });
  }

  function removeEntry() {
    setConfirmation({ title: "Remove this event from Been?", consequence: state.event.viewer_entry?.review ? "This permanently deletes the entry, rating, written review, and all review likes." : "This permanently deletes its rating.", label: "Remove from Been", action: () => mutate(`/api/events/${eventId}/been/`, { method: "DELETE" }) });
  }

  function saveReview(event) {
    event.preventDefault();
    const trimmedLength = reviewBody.trim().length;
    if (trimmedLength < 1 || trimmedLength > 1000) {
      setActionError(
        "Written review must be between 1 and 1,000 characters after trimming.",
      );
      return;
    }
    mutate(
      `/api/events/${eventId}/been/review/`,
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ body: reviewBody }),
      },
      { reviewsChanged: true },
    );
  }

  function deleteReview() {
    setConfirmation({ title: "Delete your written review?", consequence: "Its likes will be permanently deleted. Your rating and Been entry will remain.", label: "Delete review", action: () => mutate(`/api/events/${eventId}/been/review/`, { method: "DELETE" }, { reviewsChanged: true }) });
  }

  async function changeWillBeThere() {
    setSaving(true);
    setWillBeThereError(null);
    try {
      const marking = !state.event.viewer_will_be_there.is_marked;
      await fetchWithCsrf(`/api/events/${eventId}/will-be-there/`, {
        method: marking ? "PUT" : "DELETE",
      });
      setState((current) => current.event ? {
        ...current,
        event: {
          ...current.event,
          viewer_will_be_there: {
            ...current.event.viewer_will_be_there,
            is_marked: marking,
            was_marked: marking,
          },
          will_be_there_summary: {
            ...current.event.will_be_there_summary,
            active_count: Math.max(0, current.event.will_be_there_summary.active_count + (marking ? 1 : -1)),
          },
        },
      } : current);
      setWillBeThereVersion((value) => value + 1);
    } catch (error) {
      if (error.status === 401 || error.status === 403) {
        setWillBeThereError("Sign in required.");
        onAuthenticationRequired();
      } else if (error.status === 404 || error.status === 409) {
        setRetry((value) => value + 1);
        setWillBeThereVersion((value) => value + 1);
      } else {
        setWillBeThereError("Will Be There could not be changed.");
      }
    } finally {
      setSaving(false);
    }
  }

  if (state.loading) {
    return (
      <main>
        <p>Loading event.</p>
      </main>
    );
  }
  if (state.notFound) {
    return (
      <main>
        <h1>Event not found</h1>
        <p>The event does not exist or is no longer publicly visible.</p>
        <p>
          <Link to="/discover">Return to Discover</Link>
        </p>
      </main>
    );
  }
  if (state.error) {
    return (
      <main>
        <p>The event could not be loaded.</p>
        <button type="button" onClick={() => setRetry((value) => value + 1)}>
          Retry
        </button>
      </main>
    );
  }

  const event = state.event;
  const isPast = eventIsPast(event);
  const hasIdentityArtwork = Boolean(event.cover_image_url || isPast);
  const wbtCount = event.will_be_there_summary.active_count;
  const viewerHasRating = event.viewer_entry?.rating !== null && event.viewer_entry?.rating !== undefined;
  const trimmedReviewLength = reviewBody.trim().length;
  return (
    <main className={hasIdentityArtwork ? "event-page" : "event-page event-page-no-artwork"}>
      <article className={`identity event-identity ${isPast ? "event-identity-past" : "event-identity-upcoming"}`}>
        <h1>{event.title}</h1>
        {hasIdentityArtwork ? <ImageSlot name={event.title} src={event.cover_image_url} alt={event.title} loading="eager" referrerPolicy="no-referrer" /> : null}
        <div className={`event-meta-stack ${isPast ? "event-meta-past" : "event-meta-upcoming"}`}>
        {!isPast ? <p><Link to={venuePath(event.venue)}>{event.venue.name}</Link></p> : null}
        <p>
          <time
            dateTime={
              event.start_time
                ? `${event.event_date}T${event.start_time}`
                : event.event_date
            }
          >
            {formatEventDateTime(event.event_date, event.start_time)}
          </time>
        </p>
        {isPast ? <p><Link to={venuePath(event.venue)}>{event.venue.name}</Link></p> : null}
        <p><Link to={`/discover?city_id=${event.venue.city.id}`}>{event.venue.city.name}</Link></p>
        </div>
        <section className="event-lineup">
          <h2>Lineup</h2>
          <ol>
            {event.artists.map((artist) => (
              <li key={artist.id}>
                <Link to={artistPath(artist)}>{artist.name}</Link>
              </li>
            ))}
          </ol>
        </section>
        {!isPast && wbtCount > 0 ? <div className="wbt-count"><span>{wbtCount}</span><p>{pluralize(wbtCount, "active mark")}</p></div> : null}
        {isPast ? <div className="event-rating-block">
          {event.rating_summary.state === "available" ? (
            <><p className="rating-value">{event.rating_summary.average.toFixed(1)}</p><RatingHistogram buckets={event.rating_distribution.buckets} /><p>{`Average from ${pluralize(event.rating_summary.count, "rating")}.`}</p></>
          ) : (
            <p>Not enough ratings for an average yet.</p>
          )}
        </div> : null}
        {user ? <div className="event-owner-block">
            {isPast && !viewerHasRating ? <StarInput value={rating} disabled={saving} onChange={(value) => setRating(String(value))} onCommit={saveRating} /> : null}
            {!isPast ? <>
            {willBeThereError ? <p>{willBeThereError}</p> : null}
            {event.viewer_will_be_there.can_mark ? (
              <button className={event.viewer_will_be_there.is_marked ? "wbt-marked" : ""} type="button" disabled={saving} onClick={changeWillBeThere}>
                {event.viewer_will_be_there.is_marked
                  ? "Remove Will Be There"
                  : "Mark Will Be There"}
              </button>
            ) : null}</> : null}
            <FavoriteControl compact path={`/api/events/${event.id}/favorite/`} state={event.viewer_favorite} onChanged={changeFavorite} />
            {isPast && event.viewer_will_be_there.was_marked ? <p className="dormant-wbt">Will Be There · marked</p> : null}
            {actionError ? <p role="alert">{actionError}</p> : null}
        </div> : null}
      </article>
      {!isPast ? <><WillBeThereAttendees
        eventId={event.id}
        scope="circle"
        user={user}
        version={willBeThereVersion}
      />
      <WillBeThereAttendees
        eventId={event.id}
        scope="public"
        user={user}
        version={willBeThereVersion}
        activeCount={wbtCount}
      /></> : null}
      {isPast ? <YourCircle
        eventId={event.id}
        user={user}
        version={socialVersion}
        onSocialChanged={() => setSocialVersion((value) => value + 1)}
        onAuthenticationRequired={onAuthenticationRequired}
      /> : null}
      {user && isPast && viewerHasRating ? <section className="owner-entry"><EventReviewRow person={user} rating={event.viewer_entry.rating} review={event.viewer_entry.review} ratedAt={event.viewer_entry.rated_at} yours onEdit={() => setEditingEntry((value) => !value)}>{editingEntry ? <div className="owner-entry-editor"><StarInput value={rating} disabled={saving} onChange={(value) => setRating(String(value))} onCommit={saveRating} /><form onSubmit={saveReview}><label htmlFor="review-body">Written review</label><textarea id="review-body" value={reviewBody} required rows={8} onChange={(changeEvent) => setReviewBody(changeEvent.target.value)} /><p>{trimmedReviewLength} of 1,000 stored characters</p><button type="submit" disabled={saving || trimmedReviewLength < 1 || trimmedReviewLength > 1000}>{event.viewer_entry.review ? "Save review changes" : "Publish review"}</button>{event.viewer_entry.review ? <button className="quiet-action" type="button" disabled={saving} onClick={deleteReview}>Delete review</button> : null}</form><button className="quiet-action" type="button" disabled={saving} onClick={removeRating}>Remove rating</button><button className="quiet-action" type="button" disabled={saving} onClick={removeEntry}>Remove from Been</button></div> : null}</EventReviewRow></section> : null}
      {isPast ? <PublicReviews
        eventId={event.id}
        user={user}
        version={socialVersion}
        onSocialChanged={() => setSocialVersion((value) => value + 1)}
        onAuthenticationRequired={onAuthenticationRequired}
      /> : null}
      <ConfirmDialog open={Boolean(confirmation)} title={confirmation?.title ?? ""} consequence={confirmation?.consequence ?? ""} confirmLabel={confirmation?.label ?? "Confirm"} onCancel={() => setConfirmation(null)} onConfirm={() => { const action = confirmation?.action; setConfirmation(null); action?.(); }} />
    </main>
  );
}
