import { useEffect, useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";

import { fetchJson, fetchWithCsrf } from "../api.js";
import CityDropdown from "../components/CityDropdown.jsx";
import ProfileAvatar from "../components/ProfileAvatar.jsx";
import { profileBioCount } from "../profilePresentation.js";
import { profilePath } from "../profileRoutes.js";

const PROFILE_FIELD_ERROR_IDS = {
  avatar: "profile-avatar-errors",
  display_name: "profile-display-name-errors",
  bio: "profile-bio-errors",
  home_city_id: "profile-home-city-errors",
  is_private: "profile-privacy-errors",
};

export default function EditProfilePage({ session, onProfileUpdated = () => {} }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [cities, setCities] = useState([]);
  const [loadRetry, setLoadRetry] = useState(0);
  const [state, setState] = useState({ loading: true, error: null, data: null });
  const [form, setForm] = useState(null);
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState(null);
  const [saving, setSaving] = useState(false);
  const [avatarState, setAvatarState] = useState({ uploading: false, error: null });

  useEffect(() => {
    if (!session.user) return undefined;
    const controller = new AbortController();
    setState({ loading: true, error: null, data: null });
    setForm(null);
    Promise.all([
      fetchJson(`/api/users/${encodeURIComponent(session.user.username)}/`, { signal: controller.signal, cache: "no-store" }),
      fetchJson("/api/cities/", { signal: controller.signal }),
    ]).then(([data, cityData]) => {
      setState({ loading: false, error: null, data });
      setCities(cityData.results);
      setForm({ display_name: data.profile.display_name, avatar: data.profile.avatar ?? "", bio: data.profile.bio ?? "", home_city_id: data.profile.home_city?.id ?? "", is_private: data.account.is_private });
    }).catch((error) => { if (error.name !== "AbortError") setState({ loading: false, error, data: null }); });
    return () => controller.abort();
  }, [loadRetry, session.user]);

  async function submit(event) {
    event.preventDefault();
    setErrors({});
    setMessage(null);
    setSaving(true);
    try {
      const data = await fetchWithCsrf("/api/me/profile/", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ display_name: form.display_name, bio: form.bio, home_city_id: form.home_city_id === "" ? null : Number(form.home_city_id) }) });
      if (form.is_private !== state.data.account.is_private) await fetchWithCsrf("/api/me/privacy/", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ is_private: form.is_private }) });
      onProfileUpdated(data.profile);
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
    try { const data = await fetchWithCsrf("/api/me/profile/avatar/", { method: "POST", body }); setForm((current) => ({ ...current, avatar: data.profile.avatar ?? "" })); onProfileUpdated(data.profile); setAvatarState({ uploading: false, error: null }); }
    catch (error) { setAvatarState({ uploading: false, error: error.data?.errors?.avatar?.[0] ?? "Photo could not be uploaded." }); }
    event.target.value = "";
  }
  async function removeAvatar() {
    setAvatarState({ uploading: true, error: null });
    try { const data = await fetchWithCsrf("/api/me/profile/avatar/", { method: "DELETE" }); setForm((current) => ({ ...current, avatar: "" })); onProfileUpdated(data.profile); setAvatarState({ uploading: false, error: null }); }
    catch { setAvatarState({ uploading: false, error: "Photo could not be removed." }); }
  }
  if (session.loading) return <main className="edit-profile-page"><p>Checking session…</p></main>;
  if (!session.user) return <Navigate to="/login" replace state={{ from: `${location.pathname}${location.search}` }} />;
  if (state.error) return <main className="edit-profile-page"><h1 className="functional-title">Edit profile</h1><div role="alert"><p>Profile settings could not be loaded.</p><button className="recovery-action quiet-control" type="button" onClick={() => setLoadRetry((value) => value + 1)}>Retry</button></div></main>;
  if (state.loading || !form) return <main className="edit-profile-page" aria-busy="true"><h1 className="functional-title">Edit profile</h1><p>Loading profile settings…</p></main>;
  const selectedCity = cities.find((city) => String(city.id) === String(form.home_city_id)) ?? null;
  const preview = { display_name: form.display_name || state.data.profile.display_name, avatar: form.avatar || null };
  const privacyCopy = form.is_private ? "Existing approved followers keep access, and future follows require approval." : "Your profile and attributed content become public, and every pending request is accepted immediately.";
  return (
    <main className="edit-profile-page">
      <h1 className="functional-title">Edit profile</h1>
      {message ? <p role="alert">{message}</p> : null}
      {errors.request ? <ul className="field-error-list" role="alert">{fieldErrors("request")}</ul> : null}
      <form onSubmit={submit}>
        <div className="edit-avatar-upload"><ProfileAvatar profile={preview} /><div><label className={`avatar-upload-control${avatarState.uploading ? " is-uploading" : ""}`}>{avatarState.uploading ? "Uploading…" : "Upload photo"}<input type="file" accept="image/jpeg,image/png,image/webp" disabled={avatarState.uploading} aria-invalid={Boolean(avatarState.error)} aria-describedby={avatarState.error ? PROFILE_FIELD_ERROR_IDS.avatar : undefined} onChange={uploadAvatar} /></label>{form.avatar ? <button className="avatar-remove" type="button" disabled={avatarState.uploading} onClick={removeAvatar}>Remove</button> : null}{avatarState.error ? <p id={PROFILE_FIELD_ERROR_IDS.avatar} className="avatar-upload-error" role="alert">{avatarState.error}</p> : null}</div></div>
        <div className="edit-profile-field"><label htmlFor="profile-display-name">Display name</label><input id="profile-display-name" value={form.display_name} maxLength="50" aria-invalid={Boolean(errors.display_name)} aria-describedby={errors.display_name ? PROFILE_FIELD_ERROR_IDS.display_name : undefined} onChange={(event) => setForm({ ...form, display_name: event.target.value })} />{errors.display_name ? <ul className="field-error-list" id={PROFILE_FIELD_ERROR_IDS.display_name} role="alert">{fieldErrors("display_name")}</ul> : null}</div>
        <div className="edit-profile-field edit-profile-bio"><label htmlFor="profile-bio">Bio</label><textarea id="profile-bio" rows="3" value={form.bio} maxLength="150" aria-invalid={Boolean(errors.bio)} aria-describedby={errors.bio ? `profile-bio-count ${PROFILE_FIELD_ERROR_IDS.bio}` : "profile-bio-count"} onChange={(event) => setForm({ ...form, bio: event.target.value })} /><output id="profile-bio-count" htmlFor="profile-bio">{profileBioCount(form.bio)}</output>{errors.bio ? <ul className="field-error-list" id={PROFILE_FIELD_ERROR_IDS.bio} role="alert">{fieldErrors("bio")}</ul> : null}</div>
        <div className="edit-profile-field"><CityDropdown cities={cities} selectedCity={selectedCity} nullOptionLabel="No home city" label="Home city" getOptionLabel={(city) => `${city.name}, ${city.region_code}`} invalid={Boolean(errors.home_city_id)} describedBy={errors.home_city_id ? PROFILE_FIELD_ERROR_IDS.home_city_id : undefined} onSelect={(cityId) => setForm({ ...form, home_city_id: cityId === null ? "" : String(cityId) })} />{errors.home_city_id ? <ul className="field-error-list" id={PROFILE_FIELD_ERROR_IDS.home_city_id} role="alert">{fieldErrors("home_city_id")}</ul> : null}</div>
        <fieldset className="privacy-field" aria-invalid={Boolean(errors.is_private)} aria-describedby={errors.is_private ? `profile-privacy-copy ${PROFILE_FIELD_ERROR_IDS.is_private}` : "profile-privacy-copy"}><legend>Account privacy</legend><label><input type="radio" name="profile-privacy" checked={!form.is_private} onChange={() => setForm({ ...form, is_private: false })} /> Public</label><label><input type="radio" name="profile-privacy" checked={form.is_private} onChange={() => setForm({ ...form, is_private: true })} /> Private</label><p id="profile-privacy-copy">{privacyCopy}</p>{errors.is_private ? <ul className="field-error-list" id={PROFILE_FIELD_ERROR_IDS.is_private} role="alert">{fieldErrors("is_private")}</ul> : null}</fieldset>
        <button className="edit-profile-save" type="submit" disabled={saving}>{saving ? "Saving…" : "Save changes"}</button>
        <Link className="edit-profile-cancel" to={profilePath(session.user.username)}>Cancel</Link>
      </form>
    </main>
  );
}
