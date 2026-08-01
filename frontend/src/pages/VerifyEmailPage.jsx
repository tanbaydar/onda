import { useState } from "react";

import { ApiError, fetchWithCsrf } from "../api.js";


function errorMessages(error, fallback) {
  if (error instanceof ApiError && error.data?.errors) {
    return Object.values(error.data.errors).flat();
  }
  return [fallback];
}


export default function VerifyEmailPage() {
  const [code, setCode] = useState("");
  const [message, setMessage] = useState(null);
  const [errors, setErrors] = useState([]);
  const [submitting, setSubmitting] = useState(false);

  async function requestCode() {
    setSubmitting(true);
    setMessage(null);
    setErrors([]);
    try {
      const data = await fetchWithCsrf("/api/auth/verification/request/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      setMessage(
        data.already_verified
          ? "Your email is already verified."
          : "A verification code was sent to your email.",
      );
    } catch (error) {
      setErrors(errorMessages(error, "The verification code could not be sent."));
    } finally {
      setSubmitting(false);
    }
  }

  async function verify(event) {
    event.preventDefault();
    setSubmitting(true);
    setMessage(null);
    setErrors([]);
    try {
      await fetchWithCsrf("/api/auth/verification/confirm/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code }),
      });
      setMessage("Your email is verified.");
    } catch (error) {
      setErrors(errorMessages(error, "The verification code could not be checked."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main>
      <h1>Verify your email</h1>
      <p>Enter the 6-digit code sent to your email. Codes expire after 15 minutes.</p>
      {message ? <p role="status">{message}</p> : null}
      {errors.length ? <ul role="alert">{errors.map((error) => <li key={error}>{error}</li>)}</ul> : null}
      <form onSubmit={verify}>
        <p>
          <label htmlFor="verification-code">Verification code</label>{" "}
          <input
            id="verification-code"
            name="code"
            inputMode="numeric"
            autoComplete="one-time-code"
            pattern="[0-9]{6}"
            maxLength="6"
            value={code}
            onChange={(event) => setCode(event.target.value)}
            required
          />
        </p>
        <p><button type="submit" disabled={submitting}>{submitting ? "Checking code." : "Verify email"}</button></p>
      </form>
      <p><button type="button" onClick={requestCode} disabled={submitting}>Send or resend code</button></p>
    </main>
  );
}
