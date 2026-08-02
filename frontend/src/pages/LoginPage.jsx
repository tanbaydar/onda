import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { fetchWithCsrf } from "../api.js";
import { postAuthDestination } from "../landing.js";
import { INVALID_LOGIN_MESSAGE } from "../authPresentation.js";

export default function LoginPage({ onAuthenticated }) {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setSubmitting(true);
    setError(null);
    try {
      const data = await fetchWithCsrf("/api/auth/login/", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email: form.get("identifier"), password: form.get("password") }) });
      onAuthenticated(data.user);
      navigate(postAuthDestination(data.user));
    } catch (requestError) {
      setError(requestError.data?.errors?.credentials?.[0] ?? INVALID_LOGIN_MESSAGE);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="auth-page">
      <h1>Log in</h1>
      <form onSubmit={handleSubmit} noValidate>
        <div className="auth-field">
          <label htmlFor="login-identifier">Username or email</label>
          <input id="login-identifier" name="identifier" autoComplete="username" required />
        </div>
        <div className="auth-field">
          <label htmlFor="login-password">Password</label>
          <input id="login-password" name="password" type="password" autoComplete="current-password" required aria-invalid={error ? "true" : undefined} aria-describedby={error ? "login-error" : undefined} />
          {error ? <p id="login-error" className="auth-error" role="alert">That username or email and password don&apos;t match. Try again or <Link to="/reset-password">reset your password</Link>.</p> : null}
        </div>
        <button className="auth-primary" type="submit" disabled={submitting}>{submitting ? "Logging in…" : "Log in"}</button>
      </form>
      <div className="auth-links">
        <p>Forgot your password? <Link to="/reset-password">Reset it</Link></p>
        <p>New here? <Link to="/register">Register</Link></p>
      </div>
    </main>
  );
}
