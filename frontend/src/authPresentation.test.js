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

test("password reset request stays on the request screen until the explicit code action", () => {
  const request = readFileSync(new URL("./pages/PasswordResetRequestPage.jsx", import.meta.url), "utf8");
  assert.match(request, /await fetchWithCsrf[\s\S]*savePasswordResetEmail\(resetEmail\);[\s\S]*setAcceptedEmail\(resetEmail\)/);
  assert.match(request, /resetConfirmation\(acceptedEmail\)/);
  assert.match(request, />Enter code<\/button>/);
  assert.match(request, /onClick=\{\(\) => navigate\("\/reset-password\/confirm", \{ state: \{ email: acceptedEmail \} \}\)\}/);
});

test("password reset confirmation preserves context, validates locally, and cleans up", () => {
  const reset = readFileSync(new URL("./pages/PasswordResetFormPage.jsx", import.meta.url), "utf8");
  assert.match(reset, /location\.state\?\.email \|\| readPasswordResetEmail\(\)/);
  assert.match(reset, /if \(!resetEmail\)[\s\S]*Enter your email\./);
  assert.match(reset, /if \(!email\)[\s\S]*onSubmit=\{enterEmail\}/);
  assert.match(reset, /onClick=\{resendCode\}[\s\S]*>Resend code</);
  assert.match(reset, /We sent a six-digit code to \{email\}\./);
  assert.match(reset, /if \(!codeIsComplete\)[\s\S]*Enter a 6-digit code\./);
  assert.match(reset, /password\.length < 8[\s\S]*At least 8 characters\./);
  assert.match(reset, /password !== confirmation[\s\S]*Passwords must match\./);
  assert.match(reset, /serverErrors\.password\.join\(" "\)/);
  assert.match(reset, /await fetchWithCsrf\("\/api\/auth\/password-reset\/confirm\/[\s\S]*clearPasswordResetEmail\(\)/);
});

test("auth submissions have local completion gates and field-owned errors", () => {
  const login = readFileSync(new URL("./pages/LoginPage.jsx", import.meta.url), "utf8");
  const verify = readFileSync(new URL("./pages/VerifyEmailPage.jsx", import.meta.url), "utf8");
  const reset = readFileSync(new URL("./pages/PasswordResetFormPage.jsx", import.meta.url), "utf8");

  assert.match(login, /if \(!identifier\.trim\(\)\)[\s\S]*if \(!password\)[\s\S]*Object\.keys\(localErrors\)\.length/);
  assert.match(login, /aria-describedby=\{errors\.identifier \? "login-identifier-error"/);
  assert.match(login, /aria-describedby=\{errors\.password \? "login-password-error"/);
  assert.match(verify, /const codeIsComplete = \/\^\\d\{6\}\$\//);
  assert.match(verify, /disabled=\{submitting \|\| !codeIsComplete\}/);
  assert.match(verify, /aria-describedby=\{error \? "verification-code-error"/);
  assert.match(reset, /disabled=\{submitting \|\| !codeIsComplete\}/);
  assert.match(reset, /aria-describedby=\{errors\.confirmation \? "reset-confirm-password-error"/);
});

test("verification success replaces the form with a terminal completion state", () => {
  const verify = readFileSync(new URL("./pages/VerifyEmailPage.jsx", import.meta.url), "utf8");
  assert.match(verify, /setCode\(""\);[\s\S]*setComplete\(true\)/);
  assert.match(verify, /if \(complete\)[\s\S]*<h1 className="functional-title">Email verified<\/h1>[\s\S]*>Continue<\/button>/);
  assert.match(verify, /globalThis\.location\.assign\("\/"\)/);
});

test("registration privacy consequence appears only for the selected choice", () => {
  const register = readFileSync(new URL("./pages/RegisterPage.jsx", import.meta.url), "utf8");
  assert.match(register, /form\.privacy === "private"[\s\S]*form\.privacy === "public"[\s\S]*: null/);
  assert.match(register, /\{privacyCopy \? <p id="register-privacy-description">\{privacyCopy\}<\/p> : null\}/);
  assert.match(register, /aria-describedby=\{privacyDescription\}/);
  assert.match(register, /id="register-privacy-error"/);
  assert.match(register, /if \(!form\.username\.trim\(\)\)[\s\S]*if \(!form\.email\.trim\(\)\)[\s\S]*form\.password\.length < 8[\s\S]*if \(!form\.display_name\.trim\(\)\)/);
});
