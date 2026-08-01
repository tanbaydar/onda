import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { ApiError, fetchWithCsrf } from "../api.js";


export default function PasswordResetRequestPage() {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  async function submit(event) {
    event.preventDefault();
    const email = new FormData(event.currentTarget).get("email");
    setSubmitting(true);
    setError(null);
    try {
      await fetchWithCsrf("/api/auth/password-reset/request/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      navigate("/reset-password/confirm", { state: { email } });
    } catch (requestError) {
      setError(
        requestError instanceof ApiError && requestError.data?.errors?.email
          ? requestError.data.errors.email.join(" ")
          : "The reset request could not be submitted. Try again.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main>
      <h1>Reset your password</h1>
      <p>If an account exists for the email, a 6-digit reset code will be sent.</p>
      {error ? <p role="alert">{error}</p> : null}
      <form onSubmit={submit}>
        <p><label htmlFor="reset-email">Email</label>{" "}<input id="reset-email" name="email" type="email" autoComplete="email" required /></p>
        <p><button type="submit" disabled={submitting}>{submitting ? "Requesting code." : "Request reset code"}</button></p>
      </form>
    </main>
  );
}
