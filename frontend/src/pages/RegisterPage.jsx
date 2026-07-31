import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { fetchWithCsrf } from "../api.js";


export default function RegisterPage({ onAuthenticated }) {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [errors, setErrors] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setSubmitting(true);
    setErrors(null);
    try {
      const data = await fetchWithCsrf("/api/auth/register/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: form.get("email"),
          password: form.get("password"),
          username: form.get("username"),
          display_name: form.get("display_name"),
          is_private: form.get("privacy") === "private",
        }),
      });
      onAuthenticated(data.user);
      navigate("/");
    } catch (error) {
      setErrors(
        error.data?.errors ?? {
          request: ["Registration could not be completed."],
        },
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main>
      <h1>Register</h1>
      {errors ? (
        <section aria-label="Registration errors">
          <h2>Registration could not be completed</h2>
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
          <label htmlFor="register-email">Email</label>{" "}
          <input
            id="register-email"
            name="email"
            type="email"
            autoComplete="email"
            required
          />
        </p>
        <p>
          <label htmlFor="register-username">Username</label>{" "}
          <input
            id="register-username"
            name="username"
            minLength="3"
            maxLength="30"
            pattern="[A-Za-z0-9](?!.*\.\.)[A-Za-z0-9_.]*[A-Za-z0-9]"
            required
          />
        </p>
        <p>
          <label htmlFor="register-display-name">Display name</label>{" "}
          <input
            id="register-display-name"
            name="display_name"
            maxLength="50"
            required
          />
        </p>
        <p>
          <label htmlFor="register-password">Password</label>{" "}
          <input
            id="register-password"
            name="password"
            type="password"
            autoComplete="new-password"
            required
          />
        </p>
        <fieldset>
          <legend>Account privacy</legend>
          <label>
            <input
              name="privacy"
              type="radio"
              value="public"
              required
            />{" "}
            Public
          </label>
          <label>
            <input
              name="privacy"
              type="radio"
              value="private"
              required
            />{" "}
            Private
          </label>
        </fieldset>
        <p>
          <button type="submit" disabled={submitting}>
            {submitting ? "Creating account." : "Create account"}
          </button>
        </p>
      </form>
    </main>
  );
}
