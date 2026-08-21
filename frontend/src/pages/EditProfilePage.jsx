import { useEffect, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { fetchJson, fetchWithCsrf } from "../api.js";
import CityDropdown from "../components/CityDropdown.jsx";
import ProfileAvatar from "../components/ProfileAvatar.jsx";
import { profileBioCount } from "../profilePresentation.js";
import { profilePath } from "../profileRoutes.js";

function Pagination({ pagination, onPage }) {
  return <nav aria-label="Follow request pagination"><button className="quiet-control" type="button" disabled={pagination.previous_page === null} onClick={() => onPage(pagination.previous_page)}>Previous</button><span>Page {pagination.page} of {pagination.total_pages}</span><button className="quiet-control" type="button" disabled={pagination.next_page === null} onClick={() => onPage(pagination.next_page)}>Next</button></nav>;
}

function FollowRequests() {
  const [page, setPage] = useState(1);
  const [retry, setRetry] = useState(0);
  const [pendingUserId, setPendingUserId] = useState(null);
  const [state, setState] = useState({ loading: true, error: null, data: null });
  useEffect(() => {
    const controller = new AbortController();
    setState((current) => current.data
      ? { ...current, loading: false, error: null }
      : { loading: true, error: null, data: null });
    fetchJson(`/api/me/follow-requests/?page=${page}`, { signal: controller.signal, cache: "no-store" }).then((data) => setState({ loading: false, error: null, data })).catch((error) => { if (error.name !== "AbortError") setState((current) => current.data ? { ...current, loading: false, error } : { loading: false, error, data: null }); });
    return () => controller.abort();
  }, [page, retry]);
  async function decide(userId, action) {
    setPendingUserId(userId);
    setState((current) => ({ ...current, error: null }));
    try {
      await fetchWithCsrf(`/api/me/follow-requests/${userId}/${action}/`, { method: "POST" });
      setState((current) => {
        if (!current.data) return current;
        const results = current.data.results.filter((request) => request.user.id !== userId);
        const totalResults = Math.max(0, current.data.pagination.total_results - 1);
        return {
          ...current,
          data: {
            ...current.data,
            results,
            pagination: {
              ...current.data.pagination,
              total_results: totalResults,
              total_pages: Math.max(1, Math.ceil(totalResults / current.data.pagination.page_size)),
            },
          },
        };
      });
      if (state.data?.results.length === 1 && page > 1) setPage(page - 1);
    } catch { setState((current) => ({ ...current, error: new Error("request") })); }
    finally { setPendingUserId(null); }
  }
  return (
    <section className="edit-follow-requests">
      <h2>Follow requests</h2>
      {state.loading ? <p>Loading follow requests.</p> : null}
      {state.error ? <><p>Follow requests could not be changed or loaded.</p><button className="quiet-control" type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></> : null}
      {state.data?.pagination.total_results === 0 ? <p className="edit-profile-empty">No pending follow requests.</p> : null}
      {state.data?.results.length ? <><ul>{state.data.results.map((request) => <li key={request.user.id}><ProfileAvatar profile={request.user} small /><Link to={profilePath(request.user.username)}>{request.user.display_name}</Link><span className="follow-request-actions"><button className="quiet-control" type="button" disabled={pendingUserId !== null} aria-busy={pendingUserId === request.user.id} onClick={() => decide(request.user.id, "accept")}>Approve</button><button className="quiet-control" type="button" disabled={pendingUserId !== null} aria-busy={pendingUserId === request.user.id} onClick={() => decide(request.user.id, "decline")}>Decline</button></span></li>)}</ul><Pagination pagination={state.data.pagination} onPage={setPage} /></> : null}
    </section>
  );
}

export default function EditProfilePage({ session }) {
  const navigate = useNavigate();
  const [cities, setCities] = useState([]);
  const [state, setState] = useState({ loading: true, error: null, data: null });
  const [form, setForm] = useState(null);
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState(null);
  const [saving, setSaving] = useState(false);
  const [avatarState, setAvatarState] = useState({ uploading: false, error: null });

  useEffect(() => {
    if (!session.user) return undefined;
    const controller = new AbortController();
    Promise.all([
      fetchJson(`/api/users/${encodeURIComponent(session.user.username)}/`, { signal: controller.signal, cache: "no-store" }),
      fetchJson("/api/cities/", { signal: controller.signal }),
    ]).then(([data, cityData]) => {
      setState({ loading: false, error: null, data });
      setCities(cityData.results);
      setForm({ display_name: data.profile.display_name, avatar: data.profile.avatar ?? "", bio: data.profile.bio ?? "", home_city_id: data.profile.home_city?.id ?? "", is_private: data.account.is_private });
    }).catch((error) => { if (error.name !== "AbortError") setState({ loading: false, error, data: null }); });
    return () => controller.abort();
  }, [session.user]);

  async function submit(event) {
    event.preventDefault();
    setErrors({});
    setMessage(null);
    setSaving(true);
    try {
      await fetchWithCsrf("/api/me/profile/", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ display_name: form.display_name, bio: form.bio, home_city_id: form.home_city_id === "" ? null : Number(form.home_city_id) }) });
      if (form.is_private !== state.data.account.is_private) await fetchWithCsrf("/api/me/privacy/", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ is_private: form.is_private }) });
      navigate(profilePath(session.user.username));
    } catch (error) {
      if (error.status === 400) setErrors(error.data?.errors ?? { request: ["Profile could not be saved."] });
      else setMessage(error.status === 401 || error.status === 403 ? "Sign in required before changing your profile." : "Something went wrong. Try again.");
    } finally {
      setSaving(false);
    }
  }

  function fieldErrors(name) { return errors[name]?.map((error) => <li key={error}>{error}</li>); }
  async function uploadAvatar(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    setAvatarState({ uploading: true, error: null });
    const body = new FormData(); body.append("avatar", file);
    try { const data = await fetchWithCsrf("/api/me/profile/avatar/", { method: "POST", body }); setForm((current) => ({ ...current, avatar: data.profile.avatar ?? "" })); setAvatarState({ uploading: false, error: null }); }
    catch (error) { setAvatarState({ uploading: false, error: error.data?.errors?.avatar?.[0] ?? "Photo could not be uploaded." }); }
    event.target.value = "";
  }
  async function removeAvatar() {
    setAvatarState({ uploading: true, error: null });
    try { await fetchWithCsrf("/api/me/profile/avatar/", { method: "DELETE" }); setForm((current) => ({ ...current, avatar: "" })); setAvatarState({ uploading: false, error: null }); }
    catch { setAvatarState({ uploading: false, error: "Photo could not be removed." }); }
  }
  if (session.loading) return <main className="edit-profile-page"><p>Checking session.</p></main>;
  if (!session.user) return <Navigate to="/login" replace />;
  if (state.loading || !form) return <main className="edit-profile-page"><p>Loading profile settings.</p></main>;
  if (state.error) return <main className="edit-profile-page"><h1>Edit profile</h1><p>Profile settings could not be loaded.</p></main>;
  const selectedCity = cities.find((city) => String(city.id) === String(form.home_city_id)) ?? null;
  const preview = { display_name: form.display_name || state.data.profile.display_name, avatar: form.avatar || null };
  const privacyCopy = form.is_private ? "Existing approved followers keep access, and future follows require approval." : "Your profile and attributed content become public, and every pending request is accepted immediately.";
  return (
    <main className="edit-profile-page">
      <h1>Edit profile</h1>
      {message ? <p role="alert">{message}</p> : null}
      {errors.request ? <ul role="alert">{fieldErrors("request")}</ul> : null}
      <form onSubmit={submit}>
        <div className="edit-avatar-upload"><ProfileAvatar profile={preview} /><div><label className={`avatar-upload-control${avatarState.uploading ? " is-uploading" : ""}`}>{avatarState.uploading ? "Uploading…" : "Upload photo"}<input type="file" accept="image/jpeg,image/png,image/webp" disabled={avatarState.uploading} onChange={uploadAvatar} /></label>{form.avatar ? <button className="avatar-remove" type="button" disabled={avatarState.uploading} onClick={removeAvatar}>Remove</button> : null}{avatarState.error ? <p className="avatar-upload-error" role="alert">{avatarState.error}</p> : null}</div></div>
        <div className="edit-profile-field"><label htmlFor="profile-display-name">Display name</label><input id="profile-display-name" value={form.display_name} maxLength="50" onChange={(event) => setForm({ ...form, display_name: event.target.value })} />{errors.display_name ? <ul role="alert">{fieldErrors("display_name")}</ul> : null}</div>
        <div className="edit-profile-field edit-profile-bio"><label htmlFor="profile-bio">Bio</label><textarea id="profile-bio" rows="3" value={form.bio} maxLength="150" onChange={(event) => setForm({ ...form, bio: event.target.value })} /><output htmlFor="profile-bio">{profileBioCount(form.bio)}</output>{errors.bio ? <ul role="alert">{fieldErrors("bio")}</ul> : null}</div>
        <div className="edit-profile-field"><CityDropdown cities={cities} selectedCity={selectedCity} nullOptionLabel="No home city" label="Home city" getOptionLabel={(city) => `${city.name}, ${city.region_code}`} onSelect={(cityId) => setForm({ ...form, home_city_id: cityId === null ? "" : String(cityId) })} />{errors.home_city_id ? <ul role="alert">{fieldErrors("home_city_id")}</ul> : null}</div>
        <fieldset className="privacy-field"><legend>Account privacy</legend><label><input type="radio" name="profile-privacy" checked={!form.is_private} onChange={() => setForm({ ...form, is_private: false })} /> Public</label><label><input type="radio" name="profile-privacy" checked={form.is_private} onChange={() => setForm({ ...form, is_private: true })} /> Private</label><p>{privacyCopy}</p></fieldset>
        <button className="edit-profile-save" type="submit" disabled={saving}>{saving ? "Saving…" : "Save changes"}</button>
        <Link className="edit-profile-cancel" to={profilePath(session.user.username)}>Cancel</Link>
      </form>
      <FollowRequests />
    </main>
  );
}
