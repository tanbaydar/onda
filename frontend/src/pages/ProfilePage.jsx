import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { fetchJson, fetchWithCsrf } from "../api.js";
import FollowControl from "../components/FollowControl.jsx";
import ProfileAvatar from "../components/ProfileAvatar.jsx";
import EventRowPresenter from "../components/EventRowPresenter.jsx";
import SortMenu from "../components/SortMenu.jsx";
import RatingHistogram from "../components/RatingHistogram.jsx";
import ImageSlot from "../components/ImageSlot.jsx";
import FavoriteControl from "../components/FavoriteControl.jsx";
import ArtistAvatar from "../components/ArtistAvatar.jsx";
import ProfileConnectionsDialog from "../components/ProfileConnectionsDialog.jsx";
import ConfirmDialog from "../components/ConfirmDialog.jsx";
import { formatEventDateTime } from "../formatEventDateTime.js";
import { artistPath, eventPath, venuePath } from "../entityRoutes.js";
import { PROFILE_EMPTY_STATES, profileTabPath } from "../profilePresentation.js";
import { profileNavigationVisible, profilePath } from "../profileRoutes.js";
import { profileRatingBuckets, profileRatingCount } from "../ratingHistogram.js";
import { eventIsPast } from "../eventTime.js";
import SystemStatePage from "../components/SystemStatePage.jsx";

function Pagination({ pagination, onPage }) {
  if (pagination.total_pages <= 1) return null;
  return <nav className="profile-pagination" aria-label="Profile content pagination"><button className="quiet-control pagination-action" type="button" disabled={pagination.previous_page === null} onClick={() => onPage(pagination.previous_page)}>Previous</button><span>Page {pagination.page} of {pagination.total_pages}</span><button className="quiet-control pagination-action" type="button" disabled={pagination.next_page === null} onClick={() => onPage(pagination.next_page)}>Next</button></nav>;
}

function BeenTab({ onReviewDeleted, owner, username }) {
  const [page, setPage] = useState(1);
  const [retry, setRetry] = useState(0);
  const [reviewToDelete, setReviewToDelete] = useState(null);
  const [deletingReviewId, setDeletingReviewId] = useState(null);
  const [actionError, setActionError] = useState(null);
  const [state, setState] = useState({ loading: true, error: null, data: null });
  useEffect(() => {
    const controller = new AbortController();
    setState((current) => ({ loading: true, error: null, data: page > 1 ? current.data : null }));
    fetchJson(`/api/users/${encodeURIComponent(username)}/been/?page=${page}&page_size=3`, { signal: controller.signal, cache: "no-store" }).then((data) => setState((current) => ({ loading: false, error: null, data: page === 1 ? data : { ...data, results: [...(current.data?.results ?? []), ...data.results] } }))).catch((error) => { if (error.name !== "AbortError") setState((current) => ({ loading: false, error, data: current.data })); });
    return () => controller.abort();
  }, [page, retry, username]);

  async function deleteReview(event) {
    setDeletingReviewId(event.id);
    setActionError(null);
    try {
      await fetchWithCsrf(`/api/events/${event.id}/been/review/`, { method: "DELETE" });
      setState((current) => current.data ? {
        ...current,
        data: {
          ...current.data,
          results: current.data.results.map((entry) => entry.event.id === event.id ? { ...entry, has_review: false } : entry),
        },
      } : current);
      onReviewDeleted();
    } catch (error) {
      if (error.status === 404) setRetry((value) => value + 1);
      else setActionError("The review could not be deleted.");
    } finally {
      setDeletingReviewId(null);
    }
  }

  return (
    <section className="profile-tab-panel" aria-label="Been">
      {state.loading && !state.data ? <p>Loading Been history…</p> : null}
      {state.error ? <><p>{state.data ? "More Been history could not be loaded." : "Been history could not be loaded."}</p><button className="recovery-action quiet-control" type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></> : null}
      {state.data?.results.length === 0 ? <p className="profile-tab-empty">{PROFILE_EMPTY_STATES.been}</p> : null}
      {actionError ? <p role="alert">{actionError}</p> : null}
      {state.data?.results.length ? <><ol className="profile-diary-list ledger-list">{state.data.results.map((entry) => <EventRowPresenter key={entry.id} variant="profile-diary" event={entry.event} rating={entry.rating} hasReview={entry.has_review} onDeleteReview={owner && entry.has_review ? () => setReviewToDelete(entry.event) : null} reviewPending={deletingReviewId === entry.event.id} />)}</ol>{state.data.pagination.next_page ? <button className="quiet-control profile-show-more" type="button" disabled={state.loading} onClick={() => setPage(state.data.pagination.next_page)}>{state.loading ? "Loading…" : "Show more"}</button> : null}</> : null}
      <ConfirmDialog open={reviewToDelete !== null} title="Delete your written review?" consequence="Its likes will be permanently deleted. Your rating and Been entry will remain." confirmLabel="Delete review" onCancel={() => setReviewToDelete(null)} onConfirm={() => { const event = reviewToDelete; setReviewToDelete(null); if (event) deleteReview(event); }} />
    </section>
  );
}

function ReviewsTab({ username }) {
  const [page, setPage] = useState(1);
  const [sort, setSort] = useState("newest");
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({ loading: true, error: null, data: null });
  useEffect(() => {
    const controller = new AbortController();
    const query = new URLSearchParams({ sort, page: String(page) });
    setState((current) => ({ loading: true, error: null, data: current.data }));
    fetchJson(`/api/users/${encodeURIComponent(username)}/reviews/?${query}`, { signal: controller.signal, cache: "no-store" }).then((data) => setState({ loading: false, error: null, data })).catch((error) => { if (error.name !== "AbortError") setState((current) => ({ loading: false, error, data: current.data })); });
    return () => controller.abort();
  }, [page, retry, sort, username]);
  return (
    <section className="profile-tab-panel" aria-label="Reviews">
      {state.data?.results.length ? <div className="profile-review-sort"><SortMenu value={sort} onChange={(value) => { setSort(value); setPage(1); }} /></div> : null}
      {state.loading ? <p>Loading reviews…</p> : null}
      {state.error ? <><p>Reviews could not be loaded.</p><button className="recovery-action quiet-control" type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></> : null}
      {state.data?.results.length === 0 ? <p className="profile-tab-empty">{PROFILE_EMPTY_STATES.reviews}</p> : null}
      {state.data?.results.length ? <><ol className="profile-diary-list ledger-list">{state.data.results.map((review) => <EventRowPresenter key={review.id} variant="profile-diary" event={review.event} rating={review.rating} hasReview reviewBody={review.body} likeCount={review.like_count} />)}</ol><Pagination pagination={state.data.pagination} onPage={setPage} /></> : null}
    </section>
  );
}

function ProfileStatistics({ username, version = 0 }) {
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({ loading: true, error: null, data: null });
  useEffect(() => {
    const controller = new AbortController();
    setState((current) => current.data ? { ...current, loading: false, error: null } : { loading: true, error: null, data: null });
    fetchJson(`/api/users/${encodeURIComponent(username)}/stats/`, { signal: controller.signal, cache: "no-store" }).then((data) => setState({ loading: false, error: null, data })).catch((error) => { if (error.name !== "AbortError") setState((current) => current.data ? { ...current, loading: false, error } : { loading: false, error, data: null }); });
    return () => controller.abort();
  }, [retry, username, version]);
  if (state.loading && !state.data) return <section className="profile-statistics"><h2 className="section-heading">Statistics</h2><p>Loading statistics…</p></section>;
  if (state.error && !state.data) return <section className="profile-statistics"><h2 className="section-heading">Statistics</h2><p>Statistics could not be loaded.</p><button className="recovery-action quiet-control" type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></section>;
  const statistics = state.data.statistics;
  const distribution = state.data.rating_distribution;
  const ratingBuckets = profileRatingBuckets(distribution);
  const ratingCount = profileRatingCount(distribution);
  return <section className="profile-statistics"><h2 className="section-heading">Statistics</h2>{state.error ? <div className="action-feedback" role="alert"><p>Statistics could not be refreshed.</p><button className="recovery-action quiet-control" type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></div> : null}<div className="profile-statistics-strip"><div className="profile-stat stat-lead"><span className="stat-value">{statistics.events_in_been}</span><span className="stat-label">Events in Been</span></div><div className="profile-stat stat-venues"><span className="stat-value">{statistics.venues_visited}</span><span className="stat-label">Venues visited</span></div><div className="profile-stat stat-cities"><span className="stat-value">{statistics.cities_visited}</span><span className="stat-label">Cities visited</span></div><div className="profile-stat stat-reviews"><span className="stat-value">{statistics.written_reviews}</span><span className="stat-label">Written reviews</span></div><div className={`profile-stat stat-average${statistics.average_rating_given.state === "available" ? " is-available" : ""}`}><span className="stat-value">{statistics.average_rating_given.state === "available" ? statistics.average_rating_given.value.toFixed(1) : "—"}</span><span className="stat-label">Avg. Rating</span></div><div className={`profile-histogram-group${ratingCount === 0 ? " is-empty" : ""}`}><RatingHistogram className="profile-stat-histogram" buckets={ratingBuckets} staticLabel={ratingCount === 0 ? "Rating distribution: no ratings given yet." : null} /></div></div></section>;
}

function ProfileFavoriteGroup({ group, owner, onRemove, onReconcile }) {
  if (!group.items.length) return null;
  const headingId = `profile-favorite-${group.key}`;
  return (
    <section className="profile-favorite-group" aria-labelledby={headingId}>
      <h3 className="section-heading" id={headingId}>{group.label}</h3>
      <ul className="profile-favorite-list">
        {group.items.map((item) => (
          <li className={`profile-favorite-item${owner ? " is-owner has-action" : ""}`} key={item.key}>
            <Link className="profile-favorite-link" to={item.to}>
              {item.artist ? <ArtistAvatar artist={item.artist} small className="profile-favorite-thumb" /> : <ImageSlot className="profile-favorite-thumb" name={item.name} src={item.image} />}
              <span className="profile-favorite-copy"><strong>{item.name}</strong>{item.meta ? <small>{item.meta}</small> : null}</span>
            </Link>
            {owner ? <FavoriteControl row path={item.favoritePath} state={{ is_favorite: true }} onChanged={(nextFavorite) => nextFavorite?.is_favorite === false ? onRemove(item) : onReconcile()} /> : null}
          </li>
        ))}
      </ul>
    </section>
  );
}

function ProfileFavorites({ username, owner }) {
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({ loading: true, error: null, favorites: null });
  useEffect(() => {
    const controller = new AbortController();
    fetchJson(`/api/users/${encodeURIComponent(username)}/favorites/`, { signal: controller.signal, cache: "no-store" }).then((favorites) => setState({ loading: false, error: null, favorites })).catch((error) => { if (error.name !== "AbortError") setState((current) => current.favorites ? { ...current, loading: false, error } : { loading: false, error, favorites: null }); });
    return () => controller.abort();
  }, [owner, retry, username]);
  if (state.loading && !state.favorites) return <section className="profile-favorites"><h2 className="section-heading">Favorites</h2><p>Loading favorites…</p></section>;
  if (state.error && !state.favorites) return <section className="profile-favorites"><h2 className="section-heading">Favorites</h2><p>Favorites could not be loaded.</p><button className="recovery-action quiet-control" type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></section>;
  const groups = [
    { key: "events", label: "Events", items: state.favorites.events.map(({ event }) => ({ key: `event-${event.id}`, collection: "events", id: event.id, to: eventPath(event), name: event.title, meta: `${formatEventDateTime(event.event_date, eventIsPast(event) ? null : event.start_time)} · ${event.venue.name}`, image: event.cover_image_url, favoritePath: `/api/events/${event.id}/favorite/` })) },
    { key: "artists", label: "Artists", items: state.favorites.artists.map(({ artist }) => ({ key: `artist-${artist.id}`, collection: "artists", id: artist.id, to: artistPath(artist), name: artist.name, artist, favoritePath: `/api/artists/${artist.id}/favorite/` })) },
    { key: "venues", label: "Venues", items: state.favorites.venues.map(({ venue }) => ({ key: `venue-${venue.id}`, collection: "venues", id: venue.id, to: venuePath(venue), name: venue.name, meta: venue.city.name, favoritePath: `/api/venues/${venue.id}/favorite/` })) },
  ];
  const hasFavorites = groups.some((group) => group.items.length > 0);
  function removeFavorite(item) {
    const entityKey = item.collection.slice(0, -1);
    setState((current) => current.favorites ? {
      ...current,
      favorites: {
        ...current.favorites,
        [item.collection]: current.favorites[item.collection].filter((favorite) => favorite[entityKey].id !== item.id),
      },
    } : current);
  }
  return <section className="profile-favorites"><h2 className="section-heading">Favorites</h2>{state.error ? <div className="action-feedback" role="alert"><p>Favorites could not be refreshed.</p><button className="recovery-action quiet-control" type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></div> : null}{hasFavorites ? <div className="profile-favorite-groups">{groups.map((group) => <ProfileFavoriteGroup key={group.key} group={group} owner={owner} onRemove={removeFavorite} onReconcile={() => setRetry((value) => value + 1)} />)}</div> : <div className="profile-favorites-empty"><p>No favorites yet.</p>{owner ? <Link to="/discover">Discover events</Link> : null}</div>}</section>;
}

export default function ProfilePage({ session, tab = "been" }) {
  const { username } = useParams();
  const [retry, setRetry] = useState(0);
  const [followPending, setFollowPending] = useState(false);
  const [followError, setFollowError] = useState(null);
  const [connections, setConnections] = useState(null);
  const [profileVersion, setProfileVersion] = useState(0);
  const [state, setState] = useState({ loading: true, error: null, data: null });
  useEffect(() => {
    const controller = new AbortController();
    setState((current) => current.data?.profile.username === username
      ? { ...current, loading: false, error: null }
      : { loading: true, error: null, data: null });
    if (session.loading) return () => controller.abort();
    fetchJson(`/api/users/${encodeURIComponent(username)}/`, { signal: controller.signal, cache: "no-store" }).then((data) => { setState({ loading: false, error: null, data }); setFollowPending(false); setFollowError(null); }).catch((error) => {
      if (error.name === "AbortError") return;
      setFollowPending(false);
      setState((current) => current.data?.profile.username === username && error.status !== 404
        ? { ...current, loading: false, error }
        : { loading: false, error, data: null });
      if (retry > 0 && error.status !== 404) setFollowError("The latest follow state could not be confirmed.");
    });
    return () => controller.abort();
  }, [retry, session.loading, session.user?.id, username]);

  async function changeFollow() {
    if (followPending) return;
    const relationship = state.data.relationship;
    setFollowPending(true);
    setFollowError(null);
    try {
      await fetchWithCsrf(`/api/users/${state.data.profile.id}/follow/`, { method: relationship.can_follow ? "POST" : "DELETE" });
      setRetry((value) => value + 1);
    } catch (error) {
      if (error.status === 404 || error.status === 409) setRetry((value) => value + 1);
      else { setFollowPending(false); setFollowError("The follow could not be changed."); }
    }
  }

  function retryFollow() {
    if (followError === "The latest follow state could not be confirmed.") {
      setFollowError(null);
      setRetry((value) => value + 1);
      return;
    }
    changeFollow();
  }

  if (state.loading && !state.data) return <SystemStatePage title="Profile" actionTo={null} busy><p>Loading profile…</p></SystemStatePage>;
  if (state.error?.status === 404) return <SystemStatePage title="Profile not found"><p>This profile does not exist.</p></SystemStatePage>;
  if (state.error && !state.data) return <SystemStatePage title="Profile" actionTo={null}><p>Profile could not be loaded.</p><button className="recovery-action" type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></SystemStatePage>;
  const data = state.data;
  const profile = data.profile;
  const owner = data.access === "owner";
  return (
    <main className="profile-page">
      {state.error ? <div className="action-feedback" role="alert"><p>Profile status could not be refreshed.</p><button className="recovery-action" type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></div> : null}
      <header className="profile-header">
        <ProfileAvatar profile={profile} />
        <div className="profile-identity-copy">
          <div className="profile-title-row"><h1 className="identity-title">{profile.display_name}</h1></div>
          <div className="profile-social-counts"><button className="mobile-target" type="button" aria-haspopup="dialog" onClick={() => setConnections("followers")}><strong>{profile.follower_count}</strong><small>Followers</small></button><button className="mobile-target" type="button" aria-haspopup="dialog" onClick={() => setConnections("following")}><strong>{profile.following_count}</strong><small>Following</small></button></div>
          <p className="profile-handle-line">@{profile.username}{profile.home_city ? ` · ${profile.home_city.name}` : ""}{data.relationship?.follows_you ? " · Follows you" : ""}{data.relationship?.outgoing_status === "approved" ? " · Following" : ""}</p>
          {profile.bio ? <p className="profile-bio">{profile.bio}</p> : null}
        </div>
        <div className="profile-header-action">{owner ? <Link className="profile-edit-link mobile-target" to="/settings/profile">Edit profile</Link> : <><FollowControl relationship={data.relationship} pending={followPending} onChange={changeFollow} />{followError ? <div className="profile-follow-error" role="alert"><p>{followError}</p><button className="recovery-action quiet-control" type="button" disabled={followPending} onClick={retryFollow}>{followPending ? "Retrying…" : "Retry"}</button></div> : null}</>}</div>
      </header>
      {data.access !== "stub" ? <ProfileStatistics username={profile.username} version={profileVersion} /> : null}
      {profileNavigationVisible(data.access) ? <nav className="profile-tabs" aria-label="Profile sections"><Link className={`tab-action${tab === "been" ? " active" : ""}`} aria-current={tab === "been" ? "page" : undefined} to={profileTabPath(profile.username, "been")}>Been</Link><Link className={`tab-action${tab === "reviews" ? " active" : ""}`} aria-current={tab === "reviews" ? "page" : undefined} to={profileTabPath(profile.username, "reviews")}>Reviews</Link></nav> : null}
      {data.access === "stub" ? <p className="profile-private-stub">This account is private. Follow and receive approval to see its activity.</p> : tab === "reviews" ? <ReviewsTab username={profile.username} /> : <BeenTab username={profile.username} owner={owner} onReviewDeleted={() => setProfileVersion((value) => value + 1)} />}
      {data.access !== "stub" ? <ProfileFavorites username={profile.username} owner={owner} /> : null}
      <ProfileConnectionsDialog open={connections !== null} initialKind={connections ?? "followers"} profile={profile} counts={{ followers: profile.follower_count, following: profile.following_count }} onClose={() => setConnections(null)} />
    </main>
  );
}
