import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { ApiError, fetchWithCsrf } from "../api.js";
import { retainRegistrationValues } from "../authPresentation.js";
import { postAuthDestination } from "../landing.js";

const EMPTY = { username: "", email: "", password: "", display_name: "", privacy: "" };

export default function RegisterPage({ onAuthenticated }) {
  const navigate = useNavigate();
  const [form, setForm] = useState(EMPTY);
  const [submitting, setSubmitting] = useState(false);
  const [errors, setErrors] = useState({});

  function change(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
    setErrors((current) => ({ ...current, [name === "privacy" ? "is_private" : name]: undefined }));
  }
  function fieldError(field) {
    const messages = errors[field] ?? [];
    if (field === "username" && messages.some((message) => message.toLowerCase().includes("taken"))) return "That username is taken.";
    if (field === "password" && messages.length) return "At least 8 characters.";
    return messages.join(" ");
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const localErrors = {};
    if (!form.username.trim()) localErrors.username = ["Enter a username."];
    else if (form.username.trim().length < 3) localErrors.username = ["Use at least 3 characters."];
    if (!form.email.trim()) localErrors.email = ["Enter your email."];
    else if (event.currentTarget.elements.email.validity.typeMismatch) localErrors.email = ["Enter a valid email address."];
    if (form.password.length < 8) localErrors.password = ["At least 8 characters."];
    if (!form.display_name.trim()) localErrors.display_name = ["Enter a display name."];
    if (!form.privacy) localErrors.is_private = ["Choose Public or Private."];
    if (Object.keys(localErrors).length) {
      setErrors(localErrors);
      return;
    }
    setSubmitting(true);
    setErrors({});
    try {
      const data = await fetchWithCsrf("/api/auth/register/", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username: form.username.trim(), email: form.email.trim(), password: form.password, display_name: form.display_name.trim(), is_private: form.privacy === "private" }) });
      onAuthenticated(data.user);
      navigate(postAuthDestination(data.user));
    } catch (error) {
      setForm(retainRegistrationValues(form));
      setErrors(error instanceof ApiError && error.data?.errors ? error.data.errors : { request: ["Registration could not be completed."] });
    } finally { setSubmitting(false); }
  }

  function renderInput(name, label, props = {}) {
    const message = fieldError(name);
    return <div className="auth-field"><label htmlFor={`register-${name}`}>{label}</label><input id={`register-${name}`} name={name} value={form[name]} onChange={change} aria-invalid={message ? "true" : undefined} aria-describedby={message ? `register-${name}-error` : undefined} {...props} />{message ? <p id={`register-${name}-error`} className="auth-error" role="alert">{message}</p> : null}</div>;
  }

  const privacyCopy = form.privacy === "private"
    ? "Existing approved followers keep access, and future follows require approval."
    : form.privacy === "public"
      ? "Your profile and attributed content become public, and every pending request is accepted immediately."
      : null;
  const privacyError = fieldError("is_private");
  const privacyDescription = [privacyCopy ? "register-privacy-description" : null, privacyError ? "register-privacy-error" : null].filter(Boolean).join(" ") || undefined;
  return (
    <main className="auth-page">
      <h1 className="functional-title">Register</h1>
      <form onSubmit={handleSubmit} noValidate>
        {renderInput("username", "Username", { autoComplete: "username", minLength: 3, maxLength: 30, required: true })}
        {renderInput("email", "Email", { type: "email", autoComplete: "email", required: true })}
        {renderInput("password", "Password", { type: "password", autoComplete: "new-password", minLength: 8, required: true })}
        {renderInput("display_name", "Display name", { autoComplete: "name", maxLength: 50, required: true })}
        <fieldset className="auth-privacy" aria-invalid={privacyError ? "true" : undefined} aria-describedby={privacyDescription}>
          <legend>Account privacy</legend>
          <div><label><input name="privacy" type="radio" value="public" checked={form.privacy === "public"} onChange={change} required /> Public</label><label><input name="privacy" type="radio" value="private" checked={form.privacy === "private"} onChange={change} required /> Private</label></div>
          {privacyCopy ? <p id="register-privacy-description">{privacyCopy}</p> : null}
          {privacyError ? <p id="register-privacy-error" className="auth-error" role="alert">{privacyError}</p> : null}
        </fieldset>
        {fieldError("request") ? <p className="auth-error" role="alert">{fieldError("request")}</p> : null}
        <button className="auth-primary" type="submit" disabled={submitting}>{submitting ? "Registering…" : "Register"}</button>
      </form>
      <div className="auth-links"><p>Already have an account? <Link to="/login">Log in</Link></p></div>
    </main>
  );
}
