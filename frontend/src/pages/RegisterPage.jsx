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

  function change(event) { setForm((current) => ({ ...current, [event.target.name]: event.target.value })); }
  function fieldError(field) {
    const messages = errors[field] ?? [];
    if (field === "username" && messages.some((message) => message.toLowerCase().includes("taken"))) return "That username is taken.";
    if (field === "password" && messages.length) return "At least 8 characters.";
    return messages.join(" ");
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (!form.privacy) { setErrors({ is_private: ["Choose Public or Private."] }); return; }
    setSubmitting(true);
    setErrors({});
    try {
      const data = await fetchWithCsrf("/api/auth/register/", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username: form.username, email: form.email, password: form.password, display_name: form.display_name, is_private: form.privacy === "private" }) });
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

  const privacyCopy = form.privacy === "private" ? "Existing approved followers keep access, and future follows require approval." : "Your profile and attributed content become public, and every pending request is accepted immediately.";
  return (
    <main className="auth-page">
      <h1>Register</h1>
      <form onSubmit={handleSubmit} noValidate>
        {renderInput("username", "Username", { autoComplete: "username", minLength: 3, maxLength: 30, required: true })}
        {renderInput("email", "Email", { type: "email", autoComplete: "email", required: true })}
        {renderInput("password", "Password", { type: "password", autoComplete: "new-password", minLength: 8, required: true })}
        {renderInput("display_name", "Display name", { autoComplete: "name", maxLength: 50, required: true })}
        <fieldset className="auth-privacy" aria-invalid={fieldError("is_private") ? "true" : undefined}>
          <legend>Account privacy</legend>
          <div><label><input name="privacy" type="radio" value="public" checked={form.privacy === "public"} onChange={change} required /> Public</label><label><input name="privacy" type="radio" value="private" checked={form.privacy === "private"} onChange={change} required /> Private</label></div>
          <p>{privacyCopy}</p>
          {fieldError("is_private") ? <p className="auth-error" role="alert">{fieldError("is_private")}</p> : null}
        </fieldset>
        {fieldError("request") ? <p className="auth-error" role="alert">{fieldError("request")}</p> : null}
        <button className="auth-primary" type="submit" disabled={submitting}>{submitting ? "Registering…" : "Register"}</button>
      </form>
      <div className="auth-links"><p>Already have an account? <Link to="/login">Log in</Link></p></div>
    </main>
  );
}
