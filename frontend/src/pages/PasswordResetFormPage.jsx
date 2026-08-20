import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { ApiError, fetchWithCsrf } from "../api.js";
import { CODE_EXPIRY_NOTICE, codeError } from "../authPresentation.js";
import { clearPasswordResetEmail, readPasswordResetEmail, savePasswordResetEmail } from "../passwordResetSession.js";

export default function PasswordResetFormPage() {
  const location = useLocation();
  const [email, setEmail] = useState(() => location.state?.email || readPasswordResetEmail());
  const [emailEntry, setEmailEntry] = useState("");
  const [step, setStep] = useState("code");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [resendStatus, setResendStatus] = useState("");

  async function requestCode(resetEmail) {
    await fetchWithCsrf("/api/auth/password-reset/request/", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email: resetEmail }) });
  }

  async function enterEmail(event) {
    event.preventDefault(); setSubmitting(true); setError(null); setResendStatus("");
    try {
      const resetEmail = emailEntry.trim().toLowerCase();
      if (!resetEmail) { setError("Enter your email."); return; }
      await requestCode(resetEmail);
      savePasswordResetEmail(resetEmail);
      setEmail(resetEmail); setEmailEntry("");
      setResendStatus("If an account exists, a code is on its way.");
    } catch (requestError) {
      setError(requestError instanceof ApiError && requestError.data?.errors?.email ? requestError.data.errors.email.join(" ") : "The reset request could not be submitted. Try again.");
    } finally { setSubmitting(false); }
  }

  async function resendCode() {
    setSubmitting(true); setError(null); setResendStatus("");
    try {
      await requestCode(email);
      setResendStatus("If an account exists, a code is on its way.");
    } catch {
      setError("The reset request could not be submitted. Try again.");
    } finally { setSubmitting(false); }
  }

  function acceptCode(event) { event.preventDefault(); setError(null); if (/^\d{6}$/.test(code)) setStep("password"); else setError("That code isn't right. Check the email or resend."); }
  async function reset(event) {
    event.preventDefault();
    if (password.length < 8) { setError("At least 8 characters."); return; }
    if (password !== confirmation) { setError("Passwords must match."); return; }
    setSubmitting(true); setError(null);
    try {
      await fetchWithCsrf("/api/auth/password-reset/confirm/", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, code, password }) });
      clearPasswordResetEmail();
      setStep("complete");
    } catch (requestError) {
      const errors = requestError instanceof ApiError ? requestError.data?.errors ?? {} : {};
      if (errors.code) { if (errors.code.join(" ").toLowerCase().includes("expired")) await fetchWithCsrf("/api/auth/password-reset/request/", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email }) }).catch(() => {}); setStep("code"); setError(codeError(errors.code)); }
      else setError(errors.password ? "At least 8 characters." : "The password could not be reset. Try again.");
    } finally { setSubmitting(false); }
  }

  if (!email) return <main className="auth-page"><h1>Enter your email</h1><form onSubmit={enterEmail} noValidate><div className="auth-field"><label htmlFor="reset-email-entry">Email</label><input id="reset-email-entry" type="email" autoComplete="email" value={emailEntry} onChange={(event) => setEmailEntry(event.target.value)} required aria-invalid={error ? "true" : undefined} />{error ? <p className="auth-error" role="alert">{error}</p> : null}</div><button className="auth-primary" type="submit" disabled={submitting}>Send code</button></form><div className="auth-links"><p>Remembered it? <Link to="/login">Log in</Link></p></div></main>;
  if (step === "complete") return <main className="auth-page"><h1>Password changed</h1><p className="auth-intro">Your password has been reset.</p><div className="auth-links"><p><Link to="/login">Log in</Link></p></div></main>;
  if (step === "code") return <main className="auth-page auth-code-page"><h1>Enter your code</h1><p className="auth-expiry">{CODE_EXPIRY_NOTICE}</p><form onSubmit={acceptCode} noValidate><div className="auth-field"><label htmlFor="reset-code">Reset code</label><input className="auth-code-input" id="reset-code" inputMode="numeric" autoComplete="one-time-code" maxLength="6" value={code} onChange={(event) => setCode(event.target.value.replace(/\D/g, ""))} aria-invalid={error ? "true" : undefined} />{error ? <p className="auth-error" role="alert">{error}</p> : null}</div><button className="auth-primary" type="submit">Continue</button></form><div className="auth-links"><button className="auth-link-button" type="button" onClick={resendCode} disabled={submitting}>Resend code</button>{resendStatus ? <p role="status">{resendStatus}</p> : null}<Link to="/reset-password" onClick={() => clearPasswordResetEmail()}>Use a different email</Link></div></main>;
  return <main className="auth-page"><h1>Set a new password</h1><form onSubmit={reset} noValidate><div className="auth-field"><label htmlFor="reset-password">New password</label><input id="reset-password" type="password" autoComplete="new-password" value={password} onChange={(event) => setPassword(event.target.value)} aria-invalid={error ? "true" : undefined} />{error ? <p className="auth-error" role="alert">{error}</p> : null}</div><div className="auth-field"><label htmlFor="reset-confirm-password">Confirm new password</label><input id="reset-confirm-password" type="password" autoComplete="new-password" value={confirmation} onChange={(event) => setConfirmation(event.target.value)} /></div><button className="auth-primary" type="submit" disabled={submitting}>Set password</button></form></main>;
}
