import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { fetchWithCsrf } from "../api.js";
import { AUTHENTICATED_LANDING } from "../landing.js";


export default function LoginPage({ onAuthenticated }) {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [errors, setErrors] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setSubmitting(true);
    setErrors(null);
    try {
      const data = await fetchWithCsrf("/api/auth/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: form.get("email"),
          password: form.get("password"),
        }),
      });
      onAuthenticated(data.user);
      navigate(AUTHENTICATED_LANDING);
    } catch (error) {
      setErrors(
        error.data?.errors ?? {
          request: ["Login could not be completed."],
        },
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="auth-page">
      <h1>Log in</h1>
      {errors ? (
        <section aria-label="Login errors">
          <h2>Login could not be completed</h2>
          <ul>
            {Object.entries(errors).flatMap(([field, messages]) =>
              messages.map((message) => (
                <li key={`${field}-${message}`}>{message}</li>
              )),
            )}
          </ul>
        </section>
      ) : null}
      <form onSubmit={handleSubmit}>
        <p>
          <label htmlFor="login-email">Email</label>{" "}
          <input
            id="login-email"
            name="email"
            type="email"
            autoComplete="email"
            required
          />
        </p>
        <p>
          <label htmlFor="login-password">Password</label>{" "}
          <input
            id="login-password"
            name="password"
            type="password"
            autoComplete="current-password"
            required
          />
        </p>
        <p>
          <button type="submit" disabled={submitting}>
            {submitting ? "Logging in." : "Log in"}
          </button>
        </p>
      </form>
      <p><Link to="/reset-password">Forgot password?</Link></p>
    </main>
  );
}
