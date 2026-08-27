import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { fetchWithCsrf } from "../api.js";
import { postAuthDestination } from "../landing.js";
import { INVALID_LOGIN_MESSAGE } from "../authPresentation.js";

export default function LoginPage({ onAuthenticated }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [errors, setErrors] = useState({});

  function changeIdentifier(event) {
    setIdentifier(event.target.value);
    setErrors((current) => ({ ...current, identifier: undefined }));
  }

  function changePassword(event) {
    setPassword(event.target.value);
    setErrors((current) => ({ ...current, password: undefined }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const localErrors = {};
    if (!identifier.trim()) localErrors.identifier = "Enter your username or email.";
    if (!password) localErrors.password = "Enter your password.";
    if (Object.keys(localErrors).length) {
      setErrors(localErrors);
      return;
    }

    setSubmitting(true);
    setErrors({});
    try {
      const data = await fetchWithCsrf("/api/auth/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: identifier.trim(), password }),
      });
      onAuthenticated(data.user);
      const requestedDestination = typeof location.state?.from === "string" && location.state.from.startsWith("/") && !location.state.from.startsWith("//") ? location.state.from : null;
      navigate(requestedDestination ?? postAuthDestination(data.user), { replace: true });
    } catch (requestError) {
      const serverErrors = requestError.data?.errors ?? {};
      setErrors({
        identifier: serverErrors.email?.[0],
        password: serverErrors.password?.[0] ?? serverErrors.credentials?.[0] ?? INVALID_LOGIN_MESSAGE,
      });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="auth-page">
      <h1 className="functional-title">Log in</h1>
      <form onSubmit={handleSubmit} noValidate>
        <div className="auth-field">
          <label htmlFor="login-identifier">Username or email</label>
          <input id="login-identifier" name="identifier" autoComplete="username" value={identifier} onChange={changeIdentifier} required aria-invalid={errors.identifier ? "true" : undefined} aria-describedby={errors.identifier ? "login-identifier-error" : undefined} />
          {errors.identifier ? <p id="login-identifier-error" className="auth-error" role="alert">{errors.identifier}</p> : null}
        </div>
        <div className="auth-field">
          <label htmlFor="login-password">Password</label>
          <input id="login-password" name="password" type="password" autoComplete="current-password" value={password} onChange={changePassword} required aria-invalid={errors.password ? "true" : undefined} aria-describedby={errors.password ? "login-password-error" : undefined} />
          {errors.password ? <p id="login-password-error" className="auth-error" role="alert">{errors.password}</p> : null}
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
