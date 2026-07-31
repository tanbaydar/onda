import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { fetchJson, fetchWithCsrf } from "../api.js";
import { formatEventDateTime } from "../formatEventDateTime.js";
import { profileNavigationVisible, profilePath } from "../profileRoutes.js";


function Pagination({ pagination, onPage }) {
  return (
    <nav aria-label="Profile content pagination">
      <button type="button" disabled={pagination.previous_page === null} onClick={() => onPage(pagination.previous_page)}>Previous</button>
      <span> Page {pagination.page} of {pagination.total_pages} </span>
      <button type="button" disabled={pagination.next_page === null} onClick={() => onPage(pagination.next_page)}>Next</button>
    </nav>
  );
}


function EventFacts({ event }) {
  return (
    <>
      <h3><Link to={`/events/${event.id}`}>{event.title}</Link></h3>
      <p><time dateTime={event.start_time ? `${event.event_date}T${event.start_time}` : event.event_date}>{formatEventDateTime(event.event_date, event.start_time)}</time></p>
      <p><Link to={`/venues/${event.venue.id}`}>{event.venue.name}</Link>, {event.venue.city.name}</p>
    </>
  );
}


function BeenTab({ username, access }) {
  const [page, setPage] = useState(1);
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({ loading: true, error: null, data: null });

  useEffect(() => {
    if (access === "stub") {
      setState({ loading: false, error: null, data: null });
      return undefined;
    }
    const controller = new AbortController();
    setState({ loading: true, error: null, data: null });
    fetchJson(`/api/users/${encodeURIComponent(username)}/been/?page=${page}`, { signal: controller.signal, cache: "no-store" })
      .then((data) => setState({ loading: false, error: null, data }))
      .catch((error) => {
        if (error.name !== "AbortError") setState({ loading: false, error, data: null });
      });
    return () => controller.abort();
  }, [access, page, retry, username]);

  if (access === "stub") return <p>This account&apos;s Been history is private.</p>;
  return (
    <section>
      <h2>Been</h2>
      {state.loading ? <p>Loading Been history.</p> : null}
      {state.error ? <><p>Been history could not be loaded.</p><button type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></> : null}
      {state.data?.results.length === 0 ? <p>No Been entries yet.</p> : null}
      {state.data?.results.length ? (
        <>
          <ol>{state.data.results.map((entry) => <li key={entry.id}><article><EventFacts event={entry.event} /><p>{entry.rating === null ? "Unrated attendance" : `${entry.rating.toFixed(1)} stars`}</p>{entry.has_review ? <p>Written review</p> : null}</article></li>)}</ol>
          <Pagination pagination={state.data.pagination} onPage={setPage} />
        </>
      ) : null}
    </section>
  );
}


function ReviewsTab({ username, access, sessionUser }) {
  const [sort, setSort] = useState("newest");
  const [page, setPage] = useState(1);
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({ loading: true, error: null, data: null });
  const [actionError, setActionError] = useState(null);

  useEffect(() => {
    if (access === "stub") {
      setState({ loading: false, error: null, data: null });
      return undefined;
    }
    const controller = new AbortController();
    const query = new URLSearchParams({ sort, page: String(page) });
    setState({ loading: true, error: null, data: null });
    fetchJson(`/api/users/${encodeURIComponent(username)}/reviews/?${query}`, { signal: controller.signal, cache: "no-store" })
      .then((data) => setState({ loading: false, error: null, data }))
      .catch((error) => {
        if (error.name !== "AbortError") setState({ loading: false, error, data: null });
      });
    return () => controller.abort();
  }, [access, page, retry, sort, username]);

  async function changeLike(review) {
    setActionError(null);
    try {
      await fetchWithCsrf(`/api/reviews/${review.id}/like/`, { method: review.viewer_has_liked ? "DELETE" : "POST" });
      setRetry((value) => value + 1);
    } catch (error) {
      if (error.status === 401 || error.status === 403) setActionError("Sign in required.");
      else if (error.status === 404 || error.status === 409) setRetry((value) => value + 1);
      else setActionError("The review like could not be changed.");
    }
  }

  if (access === "stub") return <p>This account&apos;s reviews are private.</p>;
  return (
    <section>
      <h2>Reviews</h2>
      <p><label htmlFor="profile-review-sort">Sort reviews</label>{" "}<select id="profile-review-sort" value={sort} onChange={(event) => { setSort(event.target.value); setPage(1); }}><option value="newest">Newest</option><option value="most_liked">Most liked</option><option value="oldest">Oldest</option><option value="longest">Longest entry</option></select></p>
      {actionError ? <p>{actionError}</p> : null}
      {state.loading ? <p>Loading reviews.</p> : null}
      {state.error ? <><p>Reviews could not be loaded.</p><button type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></> : null}
      {state.data?.results.length === 0 ? <p>No written reviews yet.</p> : null}
      {state.data?.results.length ? (
        <>
          <ol>{state.data.results.map((review) => <li key={review.id}><article><EventFacts event={review.event} /><p>{review.rating.toFixed(1)} stars</p><p>{review.body}</p><p><time dateTime={review.published_at}>Published {new Date(review.published_at).toLocaleString()}</time></p><p>{review.like_count} likes</p>{!sessionUser || sessionUser.username !== username ? <button type="button" onClick={() => changeLike(review)}>{review.viewer_has_liked ? "Unlike" : "Like"}</button> : null}</article></li>)}</ol>
          <Pagination pagination={state.data.pagination} onPage={setPage} />
        </>
      ) : null}
    </section>
  );
}


function ProfileEditor({ profile, onSaved }) {
  const [cities, setCities] = useState([]);
  const [form, setForm] = useState({ display_name: profile.display_name, avatar: profile.avatar ?? "", bio: profile.bio ?? "", home_city_id: profile.home_city?.id ?? "" });
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState(null);

  useEffect(() => {
    fetchJson("/api/cities/").then((data) => setCities(data.results)).catch(() => setMessage("Cities could not be loaded."));
  }, []);

  async function submit(event) {
    event.preventDefault();
    setErrors({});
    setMessage(null);
    try {
      const data = await fetchWithCsrf("/api/me/profile/", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...form, avatar: form.avatar || null, bio: form.bio, home_city_id: form.home_city_id === "" ? null : Number(form.home_city_id) }) });
      onSaved(data.profile);
      setMessage("Profile saved.");
    } catch (error) {
      if (error.status === 400) setErrors(error.data?.errors ?? { request: ["Profile could not be saved."] });
      else if (error.status === 401 || error.status === 403) setMessage("Sign in required before changing your profile.");
      else setMessage("Something went wrong. Try again.");
    }
  }

  function fieldErrors(name) { return errors[name]?.map((error) => <li key={error}>{error}</li>); }
  return (
    <section>
      <h2>Edit profile</h2>
      {message ? <p>{message}</p> : null}
      {errors.request ? <ul>{fieldErrors("request")}</ul> : null}
      <form onSubmit={submit}>
        <p><label htmlFor="profile-display-name">Display name</label><br /><input id="profile-display-name" value={form.display_name} maxLength="50" onChange={(event) => setForm({ ...form, display_name: event.target.value })} /></p>{errors.display_name ? <ul>{fieldErrors("display_name")}</ul> : null}
        <p><label htmlFor="profile-avatar">Avatar URL</label><br /><input id="profile-avatar" type="url" value={form.avatar} maxLength="2048" onChange={(event) => setForm({ ...form, avatar: event.target.value })} /></p>{errors.avatar ? <ul>{fieldErrors("avatar")}</ul> : null}
        <p><label htmlFor="profile-bio">Bio</label><br /><textarea id="profile-bio" value={form.bio} maxLength="150" onChange={(event) => setForm({ ...form, bio: event.target.value })} /></p><p>{form.bio.length}/150 characters</p>{errors.bio ? <ul>{fieldErrors("bio")}</ul> : null}
        <p><label htmlFor="profile-city">Home city</label><br /><select id="profile-city" value={form.home_city_id} onChange={(event) => setForm({ ...form, home_city_id: event.target.value })}><option value="">No home city</option>{cities.map((city) => <option key={city.id} value={city.id}>{city.name}, {city.region_code}</option>)}</select></p>{errors.home_city_id ? <ul>{fieldErrors("home_city_id")}</ul> : null}
        <button type="submit">Save profile</button>
      </form>
    </section>
  );
}


function PrivacyControl({ account, onChanged }) {
  const [error, setError] = useState(null);
  async function changePrivacy() {
    const next = !account.is_private;
    const warning = next ? "Switch to Private? Existing approved followers keep access, and future follows require approval." : "Switch to Public? Your profile and attributed content become public, and every pending request is accepted immediately.";
    if (!window.confirm(warning)) return;
    setError(null);
    try {
      const data = await fetchWithCsrf("/api/me/privacy/", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ is_private: next }) });
      onChanged(data.privacy);
    } catch (requestError) {
      setError(requestError.status === 401 || requestError.status === 403 ? "Sign in required before changing privacy." : "Privacy could not be changed.");
    }
  }
  return <section><h2>Account privacy</h2><p>Your account is {account.is_private ? "Private" : "Public"}.</p><button type="button" onClick={changePrivacy}>Switch to {account.is_private ? "Public" : "Private"}</button>{error ? <p>{error}</p> : null}</section>;
}


function FollowRequests({ version }) {
  const [page, setPage] = useState(1);
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({ loading: true, error: null, data: null });
  useEffect(() => {
    const controller = new AbortController();
    setState({ loading: true, error: null, data: null });
    fetchJson(`/api/me/follow-requests/?page=${page}`, { signal: controller.signal, cache: "no-store" }).then((data) => setState({ loading: false, error: null, data })).catch((error) => { if (error.name !== "AbortError") setState({ loading: false, error, data: null }); });
    return () => controller.abort();
  }, [page, retry, version]);
  async function decide(userId, action) {
    try { await fetchWithCsrf(`/api/me/follow-requests/${userId}/${action}/`, { method: "POST" }); setRetry((value) => value + 1); }
    catch { setState((current) => ({ ...current, error: new Error("request") })); }
  }
  return <section><h2>Follow requests</h2>{state.loading ? <p>Loading follow requests.</p> : null}{state.error ? <><p>Follow requests could not be changed or loaded.</p><button type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></> : null}{state.data?.results.length === 0 ? <p>No pending follow requests.</p> : null}{state.data?.results.length ? <><ul>{state.data.results.map((request) => <li key={request.user.id}><Link to={profilePath(request.user.username)}>{request.user.display_name} (@{request.user.username})</Link>{" "}<button type="button" onClick={() => decide(request.user.id, "accept")}>Accept</button>{" "}<button type="button" onClick={() => decide(request.user.id, "decline")}>Decline</button></li>)}</ul><Pagination pagination={state.data.pagination} onPage={setPage} /></> : null}</section>;
}


function ProfileFavoritesAndStats({ username, owner }) {
  const [retry, setRetry] = useState(0);
  const [state, setState] = useState({ loading: true, error: null, favorites: null, stats: null, venues: null });
  useEffect(() => {
    const controller = new AbortController();
    setState({ loading: true, error: null, favorites: null, stats: null, venues: null });
    Promise.all([
      fetchJson(`/api/users/${encodeURIComponent(username)}/favorites/`, { signal: controller.signal, cache: "no-store" }),
      fetchJson(`/api/users/${encodeURIComponent(username)}/stats/`, { signal: controller.signal, cache: "no-store" }),
      owner ? fetchJson("/api/me/favorite-venues/", { signal: controller.signal, cache: "no-store" }) : Promise.resolve(null),
    ]).then(([favorites, stats, venues]) => setState({ loading: false, error: null, favorites, stats, venues })).catch((error) => { if (error.name !== "AbortError") setState({ loading: false, error, favorites: null, stats: null, venues: null }); });
    return () => controller.abort();
  }, [owner, retry, username]);
  if (state.loading) return <section><h2>Favorites and statistics</h2><p>Loading favorites and statistics.</p></section>;
  if (state.error) return <section><h2>Favorites and statistics</h2><p>Favorites and statistics could not be loaded.</p><button type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></section>;
  const statistics = state.stats.statistics;
  return <>
    <section><h2>Favorite events</h2>{state.favorites.events.length ? <ol>{state.favorites.events.map(({ event }) => <li key={event.id}><Link to={`/events/${event.id}`}>{event.title}</Link></li>)}</ol> : <p>No favorite events.</p>}</section>
    <section><h2>Favorite artists</h2>{state.favorites.artists.length ? <ol>{state.favorites.artists.map(({ artist }) => <li key={artist.id}><Link to={`/artists/${artist.id}`}>{artist.name}</Link></li>)}</ol> : <p>No favorite artists.</p>}</section>
    {owner ? <section><h2>Favorite venues</h2>{state.venues.results.length ? <ol>{state.venues.results.map(({ venue }) => <li key={venue.id}><Link to={`/venues/${venue.id}`}>{venue.name}</Link></li>)}</ol> : <p>No favorite venues.</p>}</section> : null}
    <section><h2>Statistics</h2><dl><dt>Events in Been</dt><dd>{statistics.events_in_been}</dd><dt>Written reviews</dt><dd>{statistics.written_reviews}</dd><dt>Venues visited</dt><dd>{statistics.venues_visited}</dd><dt>Cities visited</dt><dd>{statistics.cities_visited}</dd><dt>Average rating given</dt><dd>{statistics.average_rating_given.state === "available" ? statistics.average_rating_given.value.toFixed(1) : "No ratings"}</dd><dt>Followers</dt><dd>{statistics.followers}</dd><dt>Following</dt><dd>{statistics.following}</dd></dl></section>
    <section><h2>Rating distribution</h2>{state.stats.rating_distribution.state === "empty" ? <p>No ratings.</p> : <ol>{state.stats.rating_distribution.buckets.map((bucket) => <li key={bucket.rating}><span>{bucket.rating.toFixed(1)} stars </span><meter min="0" max="1" value={bucket.relative_value}>{bucket.relative_value}</meter></li>)}</ol>}</section>
  </>;
}


export default function ProfilePage({ session, tab = "been" }) {
  const { username } = useParams();
  const [retry, setRetry] = useState(0);
  const [requestVersion, setRequestVersion] = useState(0);
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
  return (
    <main>
      <header><h1>{profile.display_name}</h1><p>@{profile.username}</p>{profile.avatar ? <img src={profile.avatar} alt={`${profile.display_name}'s avatar`} /> : <p>Default avatar</p>}{profile.bio ? <p>{profile.bio}</p> : <p>No bio.</p>}{profile.home_city ? <p>Home city: {profile.home_city.name}, {profile.home_city.region_code}</p> : <p>No home city.</p>}</header>
      {data.relationship ? <section><h2>Relationship</h2>{data.relationship.follows_you ? <p>Follows you.</p> : null}{data.relationship.outgoing_status === "pending" ? <p>Request pending.</p> : null}{data.relationship.outgoing_status === "approved" ? <p>Following.</p> : null}{data.relationship.can_follow ? <button type="button" onClick={changeFollow}>{data.relationship.follow_action === "request" ? "Request to follow" : "Follow"}</button> : null}{data.relationship.can_unfollow ? <button type="button" onClick={changeFollow}>{data.relationship.outgoing_status === "pending" ? "Withdraw request" : "Unfollow"}</button> : null}</section> : null}
      {profileNavigationVisible(data.access) ? <nav aria-label="Profile sections"><ul><li><Link to={profilePath(profile.username)}>Been</Link></li><li><Link to={`${profilePath(profile.username)}/reviews`}>Reviews</Link></li></ul></nav> : null}
      {data.access === "stub" ? <p>This account is private. Follow and receive approval to see its activity.</p> : tab === "reviews" ? <ReviewsTab username={profile.username} access={data.access} sessionUser={session.user} /> : <BeenTab username={profile.username} access={data.access} />}
      {data.access !== "stub" ? <ProfileFavoritesAndStats username={profile.username} owner={data.access === "owner"} /> : null}
      {data.access === "owner" ? <><ProfileEditor profile={profile} onSaved={(saved) => setState((current) => ({ ...current, data: { ...current.data, profile: saved } }))} /><PrivacyControl account={data.account} onChanged={(privacy) => { setState((current) => ({ ...current, data: { ...current.data, account: { is_private: privacy.is_private } } })); setRequestVersion((value) => value + 1); }} /><FollowRequests version={requestVersion} /></> : null}
    </main>
  );
}
