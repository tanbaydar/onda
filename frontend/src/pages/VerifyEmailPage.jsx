import { useState } from "react";
import { ApiError, fetchWithCsrf } from "../api.js";
import { CODE_EXPIRY_NOTICE, codeError } from "../authPresentation.js";

export default function VerifyEmailPage({ email }) {
  const [code, setCode] = useState("");
  const [notice, setNotice] = useState(null);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [complete, setComplete] = useState(false);

  const codeIsComplete = /^\d{6}$/.test(code);

  async function requestCode() {
    setSubmitting(true); setNotice(null); setError(null);
    try {
      await fetchWithCsrf("/api/auth/verification/request/", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({}) });
      setNotice("Code sent.");
    } catch (requestError) { setError("The code could not be sent. Try again."); }
    finally { setSubmitting(false); }
  }

  async function verify(event) {
    event.preventDefault();
    if (!codeIsComplete) {
      setError("Enter a 6-digit code.");
      return;
    }

    setSubmitting(true); setNotice(null); setError(null);
    try {
      await fetchWithCsrf("/api/auth/verification/confirm/", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ code }) });
      setCode("");
      setComplete(true);
    } catch (requestError) {
      const messages = requestError instanceof ApiError ? Object.values(requestError.data?.errors ?? {}).flat() : [];
      if (messages.join(" ").toLowerCase().includes("expired")) await requestCode();
      setError(codeError(messages));
    } finally { setSubmitting(false); }
  }

  if (complete) {
    return <main className="auth-page">
      <h1 className="functional-title">Email verified</h1>
      <p className="auth-intro" role="status">Your email is verified.</p>
      <button className="auth-primary" type="button" onClick={() => globalThis.location.assign("/")}>Continue</button>
    </main>;
  }

  return <main className="auth-page auth-code-page">
    <h1 className="functional-title">Check your email</h1>
    <p className="auth-intro">We sent a six-digit code to {email ?? "your email"}.</p>
    <p className="auth-expiry">{CODE_EXPIRY_NOTICE}</p>
    <form onSubmit={verify} noValidate>
      <div className="auth-field"><label htmlFor="verification-code">Verification code</label><input className="auth-code-input" id="verification-code" inputMode="numeric" autoComplete="one-time-code" pattern="[0-9]{6}" maxLength="6" value={code} onChange={(event) => { setCode(event.target.value.replace(/\D/g, "")); setError(null); }} required aria-invalid={error ? "true" : undefined} aria-describedby={error ? "verification-code-error" : undefined} />{error ? <p id="verification-code-error" className="auth-error" role="alert">{error}</p> : null}</div>
      <button className="auth-primary" type="submit" disabled={submitting || !codeIsComplete}>{submitting ? "Verifying…" : "Verify"}</button>
    </form>
    <div className="auth-links"><button className="auth-link-button" type="button" onClick={requestCode} disabled={submitting}>Resend code</button>{notice ? <p role="status">{notice}</p> : null}</div>
  </main>;
}
