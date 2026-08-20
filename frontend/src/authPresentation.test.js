import assert from "node:assert/strict";
import test from "node:test";

import { CODE_EXPIRY_NOTICE, INVALID_LOGIN_MESSAGE, codeError, resetConfirmation, retainRegistrationValues } from "./authPresentation.js";
import { readFileSync } from "node:fs";

test("auth error and reset confirmation copy are exact", () => {
  assert.equal(INVALID_LOGIN_MESSAGE, "That username or email and password don't match. Try again or reset your password.");
  assert.equal(resetConfirmation("person@example.com"), "If an account exists for person@example.com, a six-digit code is on its way. Check your inbox.");
  assert.equal(CODE_EXPIRY_NOTICE, "Codes expire after 15 minutes.");
});

test("code errors use the designed invalid and expired registers", () => {
  assert.equal(codeError(["The code is invalid."]), "That code isn't right. Check the email or resend.");
  assert.equal(codeError(["The code has expired."]), "That code has expired. We've sent a new one.");
});

test("registration errors retain entered field values", () => {
  const values = { username: "taken", email: "person@example.com", display_name: "Person", password: "password", privacy: "private" };
  assert.deepEqual(retainRegistrationValues(values), values);
  assert.notEqual(retainRegistrationValues(values), values);
});

test("auth CSS and page sources contain the danger register and one code field per step", () => {
  const css = readFileSync(new URL("./styles.css", import.meta.url), "utf8");
  const verify = readFileSync(new URL("./pages/VerifyEmailPage.jsx", import.meta.url), "utf8");
  const reset = readFileSync(new URL("./pages/PasswordResetFormPage.jsx", import.meta.url), "utf8");
  assert.match(css, /\.auth-error\{[^}]*var\(--danger-text\)/);
  assert.match(css, /input\[aria-invalid="true"\]\{border-color:var\(--danger\)/);
  assert.equal((verify.match(/auth-code-input/g) ?? []).length, 1);
  assert.equal((reset.match(/auth-code-input/g) ?? []).length, 1);
});

test("password reset request opens the code form without an intermediate action", () => {
  const request = readFileSync(new URL("./pages/PasswordResetRequestPage.jsx", import.meta.url), "utf8");
  assert.match(request, /await fetchWithCsrf[\s\S]*navigate\("\/reset-password\/confirm", \{ state: \{ email \} \}\)/);
  assert.doesNotMatch(request, />Enter code</);
  assert.doesNotMatch(request, /setAccepted/);
});
