# DELTA — Authentication surfaces (Log in · Register · Email verification · Password reset)
Date: 2026-08-02 · Scope: all four auth surfaces, both widths. Authority: this file. Preview: spec/auth-preview.html.

## Shared auth-column register (Edit Profile lineage — restated, unchanged)
- 360px column, centered; desktop top pad 72; mobile pad 48 top / 24 sides.
- Chrome: guest header desktop (wordmark + auth cluster per auth-header-handoff.md); mobile = centered wordmark only, hairline below. No nav, no tab bar, no marketing copy.
- Screen title: fn 20/600 ink (display face is the wordmark's only appearance).
- Labels: micro caps 11/500 ls .05em `--text-muted`, 24 above / 6 below.
- Inputs: full-width, 1px `--border-strong`, pad 12, fn 16 ink; placeholder `--text-muted`. Focus: border ink.
- Primary: full-width bordered-ink button (1.5px, pad 12, fn 14/500), 32 above. One per screen. No fills.
- Quiet links: 12px, question in `--text-muted`, link 500 `--text-secondary`, 24 below button, stacked 8.

## Error register (ruled danger pair, applied)
Input border → `--danger`; message 12px `--danger-text`, 6 below the field. Errors attach to fields; never toast, never summary block.
- Log in invalid credentials: one message on the password field, deliberately non-specific: "That username and password don't match. Try again or reset your password."
- Register username taken: inline on blur/submit: "That username is taken." Field keeps its value.
- Password rule: "At least 8 characters." renders only on failure — no persistent helper line.

## Log in
Identifier ("Username or email") + password · primary "Log in" · quiet links: "Forgot your password? Reset it" / "New here? Register".

## Register
Built field set only: username, email, password. Primary "Register" · "Already have an account? Log in".

## Email verification (post-registration landing under M5)
- Title "Check your email" + sub 14 `--text-secondary`: "We sent a six-digit code to {email}."
- Code input: ONE 6-char field — fn 24, letter-spacing .5em, centered, same border register. Numeric inputmode, paste-friendly.
- Primary "Verify" · quiet "Resend code" · sent-confirmation: "Code sent." 12px `--text-secondary` below the resend link (quiet ink — success is never green in chrome).
- Expired: "That code has expired. We've sent a new one." Invalid: "That code isn't right. Check the email or resend."

## Password reset (3 steps, one register)
1. Request: email field, primary "Send code", "Remembered it? Log in". Post-submit swaps form for confirmation — NON-ENUMERATING copy verbatim: "If an account exists for {email}, a six-digit code is on its way. Check your inbox." + primary "Enter code" + quiet "Use a different email". Same copy whether or not the account exists.
2. Code: same code-input register as verification.
3. New password: new + confirm, primary "Set password".

## Flags
- FLAG (code input): single 6-char field chosen over six cells — one border, paste-native, fits the hairline register; six-cell is more glanceable but adds 6 bordered boxes of chrome. Reverse with one word.
- FLAG (copy): all error/confirmation strings above are proposed copy — ratify or amend; the non-enumerating string especially is product-security copy.
- FLAG: unverified-banner slot styling on signed-in screens (Phase 2 slot) still unruled — not an auth screen, not designed here.

## Dated delta — 2026-08-02 registration and login contract
- **Login:** the identifier field accepts username or email; failures use one non-enumerating message for unknown identifiers and wrong passwords.
- **Registration:** the three-field mock is superseded. Preserve all five shipped fields: username, email, password, display name, and Public/Private selection. Privacy uses the Edit-surface radio-pair grammar and existing consequence copy.
- **Password reset:** remains email-only.
- **Code entry:** verification and reset display the quiet notice “Codes expire after 15 minutes.”
