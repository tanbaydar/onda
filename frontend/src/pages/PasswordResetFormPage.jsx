import { useState } from "react";
import { Link, useLocation } from "react-router-dom";

import { ApiError, fetchWithCsrf } from "../api.js";
import { CODE_EXPIRY_NOTICE, codeError, resetConfirmation } from "../authPresentation.js";
import { clearPasswordResetEmail, readPasswordResetEmail, savePasswordResetEmail } from "../passwordResetSession.js";

export default function PasswordResetFormPage() {
  const location = useLocation();
  const [email, setEmail] = useState(() => location.state?.email || readPasswordResetEmail());
  const [emailEntry, setEmailEntry] = useState("");
  const [step, setStep] = useState("code");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [resendStatus, setResendStatus] = useState("");

  const codeIsComplete = /^\d{6}$/.test(code);

  async function requestCode(resetEmail) {
    await fetchWithCsrf("/api/auth/password-reset/request/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: resetEmail }),
    });
  }

  async function enterEmail(event) {
    event.preventDefault();
    const resetEmail = emailEntry.trim().toLowerCase();
    if (!resetEmail) {
      setErrors({ email: "Enter your email." });
      return;
    }

    setSubmitting(true);
    setErrors({});
    setResendStatus("");
    try {
      await requestCode(resetEmail);
      savePasswordResetEmail(resetEmail);
      setEmail(resetEmail);
      setEmailEntry("");
      setResendStatus(resetConfirmation(resetEmail));
    } catch (requestError) {
      setErrors({
        email: requestError instanceof ApiError && requestError.data?.errors?.email
          ? requestError.data.errors.email.join(" ")
          : "The reset request could not be submitted. Try again.",
      });
    } finally {
      setSubmitting(false);
    }
  }

  async function resendCode() {
    setSubmitting(true);
    setErrors({});
    setResendStatus("");
    try {
      await requestCode(email);
      setResendStatus(resetConfirmation(email));
    } catch {
      setErrors({ code: "The reset request could not be submitted. Try again." });
    } finally {
      setSubmitting(false);
    }
  }

  function acceptCode(event) {
    event.preventDefault();
    if (!codeIsComplete) {
      setErrors({ code: "Enter a 6-digit code." });
      return;
    }
    setErrors({});
    setStep("password");
  }

  async function reset(event) {
    event.preventDefault();
    const localErrors = {};
    if (password.length < 8) localErrors.password = "At least 8 characters.";
    if (!confirmation) localErrors.confirmation = "Confirm your new password.";
    else if (password !== confirmation) localErrors.confirmation = "Passwords must match.";
    if (Object.keys(localErrors).length) {
      setErrors(localErrors);
      return;
    }

    setSubmitting(true);
    setErrors({});
    try {
      await fetchWithCsrf("/api/auth/password-reset/confirm/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, code, password }),
      });
      clearPasswordResetEmail();
      setCode("");
      setPassword("");
      setConfirmation("");
      setStep("complete");
    } catch (requestError) {
      const serverErrors = requestError instanceof ApiError ? requestError.data?.errors ?? {} : {};
      if (serverErrors.code) {
        if (serverErrors.code.join(" ").toLowerCase().includes("expired")) {
          await requestCode(email).catch(() => {});
        }
        setStep("code");
        setErrors({ code: codeError(serverErrors.code) });
      } else if (serverErrors.password) {
        setErrors({ password: serverErrors.password.join(" ") });
      } else {
        setErrors({ password: "The password could not be reset. Try again." });
      }
    } finally {
      setSubmitting(false);
    }
  }

  if (!email) {
    return <main className="auth-page">
      <h1 className="functional-title">Enter your email</h1>
      <form onSubmit={enterEmail} noValidate>
        <div className="auth-field">
          <label htmlFor="reset-email-entry">Email</label>
          <input id="reset-email-entry" type="email" autoComplete="email" value={emailEntry} onChange={(event) => { setEmailEntry(event.target.value); setErrors({}); }} required aria-invalid={errors.email ? "true" : undefined} aria-describedby={errors.email ? "reset-email-entry-error" : undefined} />
          {errors.email ? <p id="reset-email-entry-error" className="auth-error" role="alert">{errors.email}</p> : null}
        </div>
        <button className="auth-primary" type="submit" disabled={submitting}>{submitting ? "Sending…" : "Send code"}</button>
      </form>
      <div className="auth-links"><p>Remembered it? <Link to="/login">Log in</Link></p></div>
    </main>;
  }

  if (step === "complete") {
    return <main className="auth-page">
      <h1 className="functional-title">Password changed</h1>
      <p className="auth-intro" role="status">Your password has been reset.</p>
      <Link className="auth-primary auth-standalone-primary" to="/login">Log in</Link>
    </main>;
  }

  if (step === "code") {
    return <main className="auth-page auth-code-page">
      <h1 className="functional-title">Enter your code</h1>
      <p className="auth-intro">We sent a six-digit code to {email}.</p>
      <p className="auth-expiry">{CODE_EXPIRY_NOTICE}</p>
      <form onSubmit={acceptCode} noValidate>
        <div className="auth-field">
          <label htmlFor="reset-code">Reset code</label>
          <input className="auth-code-input" id="reset-code" inputMode="numeric" autoComplete="one-time-code" pattern="[0-9]{6}" maxLength="6" value={code} onChange={(event) => { setCode(event.target.value.replace(/\D/g, "")); setErrors({}); }} required aria-invalid={errors.code ? "true" : undefined} aria-describedby={errors.code ? "reset-code-error" : undefined} />
          {errors.code ? <p id="reset-code-error" className="auth-error" role="alert">{errors.code}</p> : null}
        </div>
        <button className="auth-primary" type="submit" disabled={submitting || !codeIsComplete}>Continue</button>
      </form>
      <div className="auth-links">
        <button className="auth-link-button" type="button" onClick={resendCode} disabled={submitting}>Resend code</button>
        {resendStatus ? <p role="status">{resendStatus}</p> : null}
        <Link to="/reset-password" onClick={() => clearPasswordResetEmail()}>Use a different email</Link>
      </div>
    </main>;
  }

  return <main className="auth-page">
    <h1 className="functional-title">Set a new password</h1>
    <form onSubmit={reset} noValidate>
      <div className="auth-field">
        <label htmlFor="reset-password">New password</label>
        <input id="reset-password" type="password" autoComplete="new-password" value={password} onChange={(event) => { setPassword(event.target.value); setErrors((current) => ({ ...current, password: undefined, confirmation: undefined })); }} minLength="8" required aria-invalid={errors.password ? "true" : undefined} aria-describedby={errors.password ? "reset-password-error" : undefined} />
        {errors.password ? <p id="reset-password-error" className="auth-error" role="alert">{errors.password}</p> : null}
      </div>
      <div className="auth-field">
        <label htmlFor="reset-confirm-password">Confirm new password</label>
        <input id="reset-confirm-password" type="password" autoComplete="new-password" value={confirmation} onChange={(event) => { setConfirmation(event.target.value); setErrors((current) => ({ ...current, confirmation: undefined })); }} required aria-invalid={errors.confirmation ? "true" : undefined} aria-describedby={errors.confirmation ? "reset-confirm-password-error" : undefined} />
        {errors.confirmation ? <p id="reset-confirm-password-error" className="auth-error" role="alert">{errors.confirmation}</p> : null}
      </div>
      <button className="auth-primary" type="submit" disabled={submitting}>{submitting ? "Setting password…" : "Set password"}</button>
    </form>
  </main>;
}
