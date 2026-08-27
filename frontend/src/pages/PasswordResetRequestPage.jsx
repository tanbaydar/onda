import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ApiError, fetchWithCsrf } from "../api.js";
import { resetConfirmation } from "../authPresentation.js";
import { clearPasswordResetEmail, savePasswordResetEmail } from "../passwordResetSession.js";

export default function PasswordResetRequestPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [acceptedEmail, setAcceptedEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  async function submit(event) {
    event.preventDefault();
    const resetEmail = email.trim().toLowerCase();
    if (!resetEmail) {
      setError("Enter your email.");
      return;
    }

    setSubmitting(true); setError(null);
    try {
      await fetchWithCsrf("/api/auth/password-reset/request/", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email: resetEmail }) });
      savePasswordResetEmail(resetEmail);
      setAcceptedEmail(resetEmail);
    } catch (requestError) {
      setError(requestError instanceof ApiError && requestError.data?.errors?.email ? requestError.data.errors.email.join(" ") : "The reset request could not be submitted. Try again.");
    } finally { setSubmitting(false); }
  }

  if (acceptedEmail) {
    return <main className="auth-page">
      <h1>Check your email</h1>
      <p className="auth-intro" role="status">{resetConfirmation(acceptedEmail)}</p>
      <button className="auth-primary" type="button" onClick={() => navigate("/reset-password/confirm", { state: { email: acceptedEmail } })}>Enter code</button>
      <div className="auth-links"><button className="auth-link-button" type="button" onClick={() => { clearPasswordResetEmail(); setAcceptedEmail(""); setEmail(""); }}>Use a different email</button></div>
    </main>;
  }

  return <main className="auth-page"><h1>Reset your password</h1><form onSubmit={submit} noValidate><div className="auth-field"><label htmlFor="reset-email">Email</label><input id="reset-email" name="email" type="email" autoComplete="email" value={email} onChange={(event) => { setEmail(event.target.value); setError(null); }} required aria-invalid={error ? "true" : undefined} aria-describedby={error ? "reset-email-error" : undefined} />{error ? <p id="reset-email-error" className="auth-error" role="alert">{error}</p> : null}</div><button className="auth-primary" type="submit" disabled={submitting}>{submitting ? "Sending…" : "Send code"}</button></form><div className="auth-links"><p>Remembered it? <Link to="/login">Log in</Link></p></div></main>;
}
