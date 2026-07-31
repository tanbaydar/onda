import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { ApiError, fetchWithCsrf } from "../api.js";
import { AUTHENTICATED_LANDING } from "../landing.js";


export default function RegisterPage({ onAuthenticated }) {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});
  const [formError, setFormError] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setSubmitting(true);
    setFieldErrors({});
    setFormError(null);
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
      navigate(AUTHENTICATED_LANDING);
    } catch (error) {
      if (
        error instanceof ApiError &&
        error.status === 400 &&
        error.data?.errors
      ) {
        const { request, __all__: nonField, ...fields } = error.data.errors;
        setFieldErrors(fields);
        setFormError([...(request ?? []), ...(nonField ?? [])].join(" ") || null);
      } else if (error instanceof ApiError && error.status === 403) {
        setFormError(
          "Your registration could not be submitted securely. Refresh the page and try again.",
        );
      } else if (error instanceof ApiError) {
        setFormError(
          "Something went wrong while creating your account. Try again.",
        );
      } else {
        setFormError(
          "Could not reach the server. Check your connection and try again.",
        );
      }
    } finally {
      setSubmitting(false);
    }
  }

  function renderFieldErrors(field) {
    const messages = fieldErrors[field] ?? [];
    return messages.length > 0 ? (
      <ul id={`register-${field}-errors`}>
        {messages.map((message) => (
          <li key={message}>{message}</li>
        ))}
      </ul>
    ) : null;
  }

  return (
    <main>
      <h1>Register</h1>
      {formError ? <p role="alert">{formError}</p> : null}
      <form onSubmit={handleSubmit}>
        <p>
          <label htmlFor="register-email">Email</label>{" "}
          <input
            id="register-email"
            name="email"
            type="email"
            autoComplete="email"
            required
            aria-invalid={fieldErrors.email ? "true" : undefined}
            aria-describedby={
              fieldErrors.email ? "register-email-errors" : undefined
            }
          />
        </p>
        {renderFieldErrors("email")}
        <p>
          <label htmlFor="register-username">Username</label>{" "}
          <input
            id="register-username"
            name="username"
            minLength="3"
            maxLength="30"
            pattern="[A-Za-z0-9](?!.*\.\.)[A-Za-z0-9_.]*[A-Za-z0-9]"
            required
            aria-invalid={fieldErrors.username ? "true" : undefined}
            aria-describedby={
              fieldErrors.username ? "register-username-errors" : undefined
            }
          />
        </p>
        {renderFieldErrors("username")}
        <p>
          <label htmlFor="register-display-name">Display name</label>{" "}
          <input
            id="register-display-name"
            name="display_name"
            maxLength="50"
            required
            aria-invalid={fieldErrors.display_name ? "true" : undefined}
            aria-describedby={
              fieldErrors.display_name
                ? "register-display_name-errors"
                : undefined
            }
          />
        </p>
        {renderFieldErrors("display_name")}
        <p>
          <label htmlFor="register-password">Password</label>{" "}
          <input
            id="register-password"
            name="password"
            type="password"
            autoComplete="new-password"
            required
            aria-invalid={fieldErrors.password ? "true" : undefined}
            aria-describedby={
              fieldErrors.password ? "register-password-errors" : undefined
            }
          />
        </p>
        {renderFieldErrors("password")}
        <fieldset
          aria-invalid={fieldErrors.is_private ? "true" : undefined}
          aria-describedby={
            fieldErrors.is_private ? "register-is_private-errors" : undefined
          }
        >
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
          {renderFieldErrors("is_private")}
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
