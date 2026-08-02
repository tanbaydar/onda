import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { fetchJson, fetchWithCsrf } from "../api.js";
import FollowControl from "../components/FollowControl.jsx";
import ProfileAvatar from "../components/ProfileAvatar.jsx";
import ProfileDiaryRow from "../components/ProfileDiaryRow.jsx";
import ProfileSortMenu from "../components/ProfileSortMenu.jsx";
import RatingHistogram from "../components/RatingHistogram.jsx";
import ImageSlot from "../components/ImageSlot.jsx";
import FavoriteControl from "../components/FavoriteControl.jsx";
import { formatEventDateTime } from "../formatEventDateTime.js";
import { artistPath, eventPath, venuePath } from "../entityRoutes.js";
import { PROFILE_EMPTY_STATES, profileTabPath } from "../profilePresentation.js";
import { profileNavigationVisible, profilePath } from "../profileRoutes.js";
import { profileRatingBuckets } from "../ratingHistogram.js";

function Pagination({ pagination, onPage }) {
  return <nav className="profile-pagination" aria-label="Profile content pagination"><button className="quiet-control" type="button" disabled={pagination.previous_page === null} onClick={() => onPage(pagination.previous_page)}>Previous</button><span>Page {pagination.page} of {pagination.total_pages}</span><button className="quiet-control" type="button" disabled={pagination.next_page === null} onClick={() => onPage(pagination.next_page)}>Next</button></nav>;
}

function BeenTab({ username }) {
  const [page, setPage] = useState(1);
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({ loading: true, error: null, data: null });
  useEffect(() => {
    const controller = new AbortController();
    setState({ loading: true, error: null, data: null });
    fetchJson(`/api/users/${encodeURIComponent(username)}/been/?page=${page}`, { signal: controller.signal, cache: "no-store" }).then((data) => setState({ loading: false, error: null, data })).catch((error) => { if (error.name !== "AbortError") setState({ loading: false, error, data: null }); });
    return () => controller.abort();
  }, [page, retry, username]);
  return (
    <section className="profile-tab-panel" aria-label="Been">
      {state.loading ? <p>Loading Been history.</p> : null}
      {state.error ? <><p>Been history could not be loaded.</p><button className="quiet-control" type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></> : null}
      {state.data?.results.length === 0 ? <p className="profile-tab-empty">{PROFILE_EMPTY_STATES.been}</p> : null}
      {state.data?.results.length ? <><ol className="profile-diary-list">{state.data.results.map((entry) => <ProfileDiaryRow key={entry.id} event={entry.event} rating={entry.rating} hasReview={entry.has_review} />)}</ol><Pagination pagination={state.data.pagination} onPage={setPage} /></> : null}
    </section>
  );
}

function ReviewsTab({ username, sort }) {
  const [page, setPage] = useState(1);
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({ loading: true, error: null, data: null });
  useEffect(() => {
    const controller = new AbortController();
    const query = new URLSearchParams({ sort, page: String(page) });
    setState({ loading: true, error: null, data: null });
    fetchJson(`/api/users/${encodeURIComponent(username)}/reviews/?${query}`, { signal: controller.signal, cache: "no-store" }).then((data) => setState({ loading: false, error: null, data })).catch((error) => { if (error.name !== "AbortError") setState({ loading: false, error, data: null }); });
    return () => controller.abort();
  }, [page, retry, sort, username]);
  return (
    <section className="profile-tab-panel" aria-label="Reviews">
      {state.loading ? <p>Loading reviews.</p> : null}
      {state.error ? <><p>Reviews could not be loaded.</p><button className="quiet-control" type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></> : null}
      {state.data?.results.length === 0 ? <p className="profile-tab-empty">{PROFILE_EMPTY_STATES.reviews}</p> : null}
      {state.data?.results.length ? <><ol className="profile-diary-list">{state.data.results.map((review) => <ProfileDiaryRow key={review.id} event={review.event} rating={review.rating} hasReview />)}</ol><Pagination pagination={state.data.pagination} onPage={setPage} /></> : null}
    </section>
  );
}

function ProfileStatistics({ username }) {
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({ loading: true, error: null, data: null });
  useEffect(() => {
    const controller = new AbortController();
    setState({ loading: true, error: null, data: null });
    fetchJson(`/api/users/${encodeURIComponent(username)}/stats/`, { signal: controller.signal, cache: "no-store" }).then((data) => setState({ loading: false, error: null, data })).catch((error) => { if (error.name !== "AbortError") setState({ loading: false, error, data: null }); });
    return () => controller.abort();
  }, [retry, username]);
  if (state.loading) return <section className="profile-statistics"><h2>Statistics</h2><p>Loading statistics.</p></section>;
  if (state.error) return <section className="profile-statistics"><h2>Statistics</h2><p>Statistics could not be loaded.</p><button className="quiet-control" type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></section>;
  const statistics = state.data.statistics;
  const ratingBuckets = profileRatingBuckets(state.data.rating_distribution);
  return <section className="profile-statistics"><h2>Statistics</h2><div className="profile-statistics-strip"><div className="profile-stat stat-lead"><span className="stat-value">{statistics.events_in_been}</span><span className="stat-label">Events in Been</span></div><div className="profile-stat stat-reviews"><span className="stat-value">{statistics.written_reviews}</span><span className="stat-label">Written reviews</span></div><div className="profile-stat stat-venues"><span className="stat-value">{statistics.venues_visited}</span><span className="stat-label">Venues visited</span></div><div className="profile-stat stat-cities"><span className="stat-value">{statistics.cities_visited}</span><span className="stat-label">Cities visited</span></div><div className="profile-judgment-unit"><div className="profile-stat"><span className="stat-value">{statistics.average_rating_given.state === "available" ? statistics.average_rating_given.value.toFixed(1) : "—"}</span><span className="stat-label">Average rating given</span></div><RatingHistogram className="profile-stat-histogram" buckets={ratingBuckets} /></div></div></section>;
}

function ProfileFavorites({ username, owner }) {
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({ loading: true, error: null, favorites: null });
  useEffect(() => {
    const controller = new AbortController();
    fetchJson(`/api/users/${encodeURIComponent(username)}/favorites/`, { signal: controller.signal, cache: "no-store" }).then((favorites) => setState({ loading: false, error: null, favorites })).catch((error) => { if (error.name !== "AbortError") setState({ loading: false, error, favorites: null }); });
    return () => controller.abort();
  }, [owner, retry, username]);
  if (state.loading) return <section className="profile-favorites"><h2>Favorites</h2><p>Loading favorites.</p></section>;
  if (state.error) return <section className="profile-favorites"><h2>Favorites</h2><p>Favorites could not be loaded.</p><button className="quiet-control" type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></section>;
  const items = [
    ...state.favorites.events.map(({ event }) => ({ key: `event-${event.id}`, to: eventPath(event), name: event.title, meta: `${formatEventDateTime(event.event_date, event.start_time)} · ${event.venue.name}`, image: event.cover_image_url, favoritePath: `/api/events/${event.id}/favorite/` })),
    ...state.favorites.artists.map(({ artist }) => ({ key: `artist-${artist.id}`, to: artistPath(artist), name: artist.name, favoritePath: `/api/artists/${artist.id}/favorite/` })),
    ...state.favorites.venues.map(({ venue }) => ({ key: `venue-${venue.id}`, to: venuePath(venue), name: venue.name, meta: venue.city.name, favoritePath: `/api/venues/${venue.id}/favorite/` })),
  ];
  return <section className="profile-favorites"><h2>Favorites</h2>{items.length ? <ul className="profile-favorite-list">{items.map((item) => <li key={item.key}><ImageSlot className="profile-favorite-thumb" name={item.name} src={item.image} /><Link to={item.to}><strong>{item.name}</strong>{item.meta ? <small>{item.meta}</small> : null}</Link>{owner ? <FavoriteControl row path={item.favoritePath} state={{ is_favorite: true }} onChanged={() => setRetry((value) => value + 1)} /> : null}</li>)}</ul> : null}</section>;
}

export default function ProfilePage({ session, tab = "been" }) {
  const { username } = useParams();
  const [retry, setRetry] = useState(0);
  const [reviewSort, setReviewSort] = useState("newest");
  const [state, setState] = useState({ loading: true, error: null, data: null });
  useEffect(() => {
    const controller = new AbortController();
    setState({ loading: true, error: null, data: null });
    fetchJson(`/api/users/${encodeURIComponent(username)}/`, { signal: controller.signal, cache: "no-store" }).then((data) => setState({ loading: false, error: null, data })).catch((error) => { if (error.name !== "AbortError") setState({ loading: false, error, data: null }); });
    return () => controller.abort();
  }, [retry, session.user?.id, username]);

  async function changeFollow() {
    const relationship = state.data.relationship;
    try {
      await fetchWithCsrf(`/api/users/${state.data.profile.id}/follow/`, { method: relationship.can_follow ? "POST" : "DELETE" });
      setRetry((value) => value + 1);
    } catch (error) {
      if (error.status === 404 || error.status === 409) setRetry((value) => value + 1);
      else setState((current) => ({ ...current, error }));
    }
  }

  if (state.loading) return <main><p>Loading profile.</p></main>;
  if (state.error?.status === 404) return <main><h1>Profile not found</h1><p>This profile does not exist.</p></main>;
  if (state.error) return <main><p>Profile could not be loaded.</p><button type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></main>;
  const data = state.data;
  const profile = data.profile;
  const owner = data.access === "owner";
  return (
    <main className="profile-page">
      <header className="profile-header">
        <ProfileAvatar profile={profile} />
        <div className="profile-identity-copy">
          <h1>{profile.display_name}</h1>
          <p className="profile-handle-line">@{profile.username}{profile.home_city ? ` · ${profile.home_city.name}` : ""}{data.relationship?.follows_you ? " · Follows you" : ""}{data.relationship?.outgoing_status === "approved" ? " · Following" : ""}</p>
          <div className="profile-social-counts"><span><strong>{profile.follower_count}</strong><small>Followers</small></span><span><strong>{profile.following_count}</strong><small>Following</small></span></div>
          {owner ? <Link className="profile-edit-link" to="/settings/profile">Edit profile</Link> : <FollowControl relationship={data.relationship} onChange={changeFollow} />}
          {profile.bio ? <p className="profile-bio">{profile.bio}</p> : null}
        </div>
      </header>
      {data.access !== "stub" ? <ProfileStatistics username={profile.username} /> : null}
      {profileNavigationVisible(data.access) ? <nav className="profile-tabs" aria-label="Profile sections"><Link className={tab === "been" ? "active" : ""} aria-current={tab === "been" ? "page" : undefined} to={profileTabPath(profile.username, "been")}>Been</Link><Link className={tab === "reviews" ? "active" : ""} aria-current={tab === "reviews" ? "page" : undefined} to={profileTabPath(profile.username, "reviews")}>Reviews</Link>{tab === "reviews" ? <ProfileSortMenu value={reviewSort} onChange={setReviewSort} /> : null}</nav> : null}
      {data.access === "stub" ? <p className="profile-private-stub">This account is private. Follow and receive approval to see its activity.</p> : tab === "reviews" ? <ReviewsTab key={reviewSort} username={profile.username} sort={reviewSort} /> : <BeenTab username={profile.username} />}
      {data.access !== "stub" ? <ProfileFavorites username={profile.username} owner={owner} /> : null}
    </main>
  );
}
