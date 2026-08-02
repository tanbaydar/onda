import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ApiError, fetchWithCsrf } from "../api.js";
import { resetConfirmation } from "../authPresentation.js";

export default function PasswordResetRequestPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [accepted, setAccepted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  async function submit(event) {
    event.preventDefault(); setSubmitting(true); setError(null);
    try {
      await fetchWithCsrf("/api/auth/password-reset/request/", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email }) });
      setAccepted(true);
    } catch (requestError) {
      setError(requestError instanceof ApiError && requestError.data?.errors?.email ? requestError.data.errors.email.join(" ") : "The reset request could not be submitted. Try again.");
    } finally { setSubmitting(false); }
  }

  if (accepted) return <main className="auth-page"><h1>Check your email</h1><p className="auth-intro">{resetConfirmation(email)}</p><button className="auth-primary auth-standalone-primary" type="button" onClick={() => navigate("/reset-password/confirm", { state: { email } })}>Enter code</button><div className="auth-links"><button className="auth-link-button" type="button" onClick={() => setAccepted(false)}>Use a different email</button></div></main>;
  return <main className="auth-page"><h1>Reset your password</h1><form onSubmit={submit} noValidate><div className="auth-field"><label htmlFor="reset-email">Email</label><input id="reset-email" type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} required aria-invalid={error ? "true" : undefined} />{error ? <p className="auth-error" role="alert">{error}</p> : null}</div><button className="auth-primary" type="submit" disabled={submitting}>Send code</button></form><div className="auth-links"><p>Remembered it? <Link to="/login">Log in</Link></p></div></main>;
}
