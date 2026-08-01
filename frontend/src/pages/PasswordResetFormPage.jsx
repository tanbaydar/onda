import { useState } from "react";
import { useLocation } from "react-router-dom";

import { ApiError, fetchWithCsrf } from "../api.js";


export default function PasswordResetFormPage() {
  const location = useLocation();
  const [submitting, setSubmitting] = useState(false);
  const [errors, setErrors] = useState([]);
  const [complete, setComplete] = useState(false);

  async function submit(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setSubmitting(true);
    setErrors([]);
    try {
      await fetchWithCsrf("/api/auth/password-reset/confirm/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: form.get("email"),
          code: form.get("code"),
          password: form.get("password"),
        }),
      });
      setComplete(true);
    } catch (error) {
      setErrors(
        error instanceof ApiError && error.data?.errors
          ? Object.values(error.data.errors).flat()
          : ["The password could not be reset. Try again."],
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main>
      <h1>Enter your reset code</h1>
      <p>Reset codes expire after 15 minutes.</p>
      {complete ? <p role="status">Your password has been reset. You can log in with the new password.</p> : null}
      {errors.length ? <ul role="alert">{errors.map((error) => <li key={error}>{error}</li>)}</ul> : null}
      {!complete ? (
        <form onSubmit={submit}>
          <p><label htmlFor="reset-confirm-email">Email</label>{" "}<input id="reset-confirm-email" name="email" type="email" autoComplete="email" defaultValue={location.state?.email ?? ""} required /></p>
          <p><label htmlFor="reset-code">Reset code</label>{" "}<input id="reset-code" name="code" inputMode="numeric" autoComplete="one-time-code" pattern="[0-9]{6}" maxLength="6" required /></p>
          <p><label htmlFor="reset-new-password">New password</label>{" "}<input id="reset-new-password" name="password" type="password" autoComplete="new-password" required /></p>
          <p><button type="submit" disabled={submitting}>{submitting ? "Resetting password." : "Reset password"}</button></p>
        </form>
      ) : null}
    </main>
  );
}
