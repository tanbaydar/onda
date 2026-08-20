# Onda Security-Boundary Review

Audited read-only at commit `2692918` ahead of Milestone 5 deployment.

## Executive result

The ownership checks and sanctioned-queryset consumers are generally sound. No direct numeric-ID ownership bypass was found in the implemented mutations.

Three issues should block the M5 flag flip or deployment:

1. The public event rating distribution can reveal a lone private user's exact rating.
2. “Unverified means guest capabilities” is not consistently enforced on read boundaries, and the frontend cannot route an unverified session through verification.
3. Production session/CSRF transport settings and reverse-proxy HTTPS recognition are not configured.

## Findings

### 1. A lone private rating is exposed through the public event distribution

- **Location:** `backend/catalog/views.py:291–294`, `backend/users/services.py:343–375`, `backend/users/models.py:279–283`
- **Concern:** `GET /api/events/{id}/` uses `DiaryEntry.objects.for_aggregation()` for the public ten-bucket distribution, and the distribution becomes available with one rating. If that rating belongs to a private user, its exact half-star value is identifiable from the sole nonzero bucket.
- **Severity:** High
- **Gated posture:** Medium. Basic-auth access narrows the audience, but every admitted visitor can infer the private rating.
- **Public posture:** High. Any anonymous visitor can retrieve it.
- **Concrete request:** `GET /api/events/123/` on an event with one private 2.0 rating returns `rating_summary.state = "not_enough_ratings"` but a distribution whose 2.0 bucket has `relative_value: 1.0`.
- **Remedy:** Apply an anonymity threshold to the event distribution—most consistently the existing three-rated-entry threshold—and return an explicit not-enough-ratings state below it.

At one contributor, “anonymous contribution” is individually recoverable.

### 2. The verification flag does not produce guest-equivalent read visibility

- **Location:** `backend/users/models.py:49–63`, `backend/users/models.py:245–256`, `backend/users/models.py:335–350`, `backend/users/models.py:419–430`; consumers at `backend/users/views.py:884–1122`
- **Concern:** Visibility boundaries treat every authenticated session as an authenticated viewer without considering `email_verified_at`. After the flag flips, an unverified approved follower can still retrieve a private profile's Been, Reviews, favorites, statistics, and rating distribution.
- **Severity:** High
- **Gated posture:** Medium. Exploitation requires a site-level basic-auth credential, an unverified account, and a previously approved relationship.
- **Public posture:** High. This contradicts the frozen “unverified = guest capabilities plus own session” rule.
- **Concrete requests:** With an unverified session that already follows private `tan`, the following use the normal authenticated/follower boundary rather than a guest-equivalent viewer:
  - `GET /api/users/tan/been/`
  - `GET /api/users/tan/reviews/`
  - `GET /api/users/tan/favorites/`
  - `GET /api/users/tan/stats/`
- **Remedy:** Define one effective visibility viewer for read boundaries. When enforcement is on and the session is unverified, explicitly permitted owner-only session data may remain accessible, but follower/public-content checks must receive guest-equivalent visibility.

Some personalized reads use `_authentication_required()` and reject unverified users while profile-content endpoints do not, making the flag behavior internally inconsistent.

### 3. Flag-on navigation strands newly registered unverified users

- **Location:** `backend/users/views.py:175–186`, `backend/users/views.py:295–318`, `frontend/src/App.jsx:50–145`, `frontend/src/pages/RegisterPage.jsx:21–34`, `frontend/src/pages/LoginPage.jsx:19–29`
- **Concern:** Registration signs the user in and routes directly to `/home`, but the session payload does not expose verification state and `/api/me/home/` returns a verification 403. There is no automatic redirect or visible navigation to `/verify-email`.
- **Severity:** High
- **Gated posture:** High operational impact. Every newly registered user hits a broken first-run flow after enforcement is enabled.
- **Public posture:** High operational impact at larger volume.
- **Concrete flow:** `POST /api/auth/register/` → `201`; frontend navigates to `/home`; `GET /api/me/home/` → `403 {"errors":{"verification":[...]}}`; the user must know the unadvertised `/verify-email` route.
- **Remedy:** Before flag flip, expose self-only verification state in the session response and route unverified registration/login sessions to verification. Verification success must refresh session state and resume the intended destination.

The backend verification endpoints work, but the flag is not operationally ready.

### 4. Verification enforcement is split between service and view boundaries

- **Location:** `backend/users/auth_services.py:45–61`, `backend/users/views.py:175–186`; direct mutations at `backend/users/views.py:812–881`, `backend/users/views.py:1196–1237`
- **Concern:** Most social services call `require_account_action`, but profile editing and notification read-state mutations occur directly in views and rely only on `_authentication_required()`. The “one service boundary” claim is therefore not literally true.
- **Severity:** Medium
- **Gated posture:** Low. Current HTTP routes are protected and the 27-mutation sweep pins them.
- **Public posture:** Medium. A future alternate caller or endpoint could reuse mutation logic without the gate.
- **Concrete requests currently protected:** `PUT /api/me/profile/`, `POST /api/me/notifications/{id}/read/`, and `POST /api/me/notifications/read-all/`.
- **Remedy:** Before adding alternate callers, put these mutations behind gated service functions. Retain the endpoint sweep as defense in depth.

No current HTTP bypass was found; this is boundary fragility.

### 5. Secure production cookie and HTTPS proxy settings are absent

- **Location:** `backend/config/settings.py:20–42`, `backend/config/settings.py:83–91`
- **Concern:** No deployment settings enable `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, HSTS/SSL redirect, or reverse-proxy HTTPS recognition. Django's secure-cookie defaults are false.
- **Severity:** High
- **Gated posture:** High if deployed without correct TLS proxy configuration. Basic authentication does not protect session cookies from transport mistakes.
- **Public posture:** High.
- **Concrete effect:** A session cookie is not marked `Secure`; if HTTP is reachable, the browser may transmit it without TLS. Behind TLS termination, missing `SECURE_PROXY_SSL_HEADER` can also make Django perceive an HTTPS browser request as HTTP and reject same-origin CSRF checks.
- **Remedy:** Add explicit deployment-only settings for secure session/CSRF cookies, trusted proxy HTTPS handling or end-to-end TLS, HTTPS redirect/HSTS as appropriate, deployment hosts, and a `manage.py check --deploy` deployment check.

Positive findings:

- Session cookies retain Django's default `HttpOnly` protection.
- SameSite defaults support the same-origin architecture.
- Development trusted origins are restricted to explicit localhost Vite origins under `DEBUG`.
- No wildcard trusted origins or CSRF exemptions exist.

### 6. Password-reset responses are shape-safe but timing-enumerable

- **Location:** `backend/users/auth_services.py:165–174`, `backend/users/views.py:397–453`
- **Concern:** Missing and existing accounts receive equivalent JSON, but their execution paths differ materially. Existing-account requests lock/write and send email while missing accounts return immediately; confirmation for existing accounts performs code lookup and HMAC comparison while missing accounts return after only the user lookup.
- **Severity:** Medium
- **Gated posture:** Low-to-medium. Basic auth limits probing, but an admitted user can still measure it.
- **Public posture:** Medium-to-high without request throttling.
- **Concrete requests:** Repeatedly compare latency for `POST /api/auth/password-reset/request/` or `POST /api/auth/password-reset/confirm/` using known and random emails. Response bodies match, but the paths are distinguishable.
- **Remedy:** Queue or otherwise equalize request-side email work and perform comparable dummy code-hash work on missing-account confirmation paths. Add timing-tolerance tests at the service boundary.

Password validation correctly happens before account lookup, preventing user-specific validator messages from becoming a response-shape oracle.

### 7. Registration explicitly enumerates registered email addresses

- **Location:** `backend/users/forms.py:15–19`, `backend/users/views.py:295–318`
- **Concern:** Registration returns “An account with this email already exists,” revealing account existence.
- **Severity:** Medium
- **Gated posture:** Low because only basic-auth-admitted visitors can query it.
- **Public posture:** Medium.
- **Concrete request:** `POST /api/auth/register/` with a target email returns a distinct duplicate-email 400.
- **Remedy:** Before public availability, decide deliberately whether this UX disclosure is accepted; otherwise use a generic registration/account-recovery response.

Login itself does not enumerate: unknown email and wrong password return the same credentials error.

### 8. User-controlled avatar URLs create a client-side tracking surface

- **Location:** `backend/users/views.py:838–850`, `backend/users/models.py:82`, `frontend/src/pages/ProfilePage.jsx:261`
- **Concern:** A user can set any syntactically valid HTTP/HTTPS avatar URL, and each visitor's browser loads it directly, exposing visitor IP, user agent, timing, and referrer behavior to the avatar host.
- **Severity:** Medium
- **Gated posture:** Low. Exposure is limited to admitted visitors.
- **Public posture:** Medium, especially on public profiles.
- **Concrete request:** `PUT /api/me/profile/` with `avatar: "https://tracker.example/pixel?id=..."`, followed by another visitor opening `/u/{username}`.
- **Remedy:** For public deployment, use a controlled image proxy/upload pipeline or tightly governed host policy. At minimum, require HTTPS and define a referrer policy.

`javascript:` and `data:` URLs are rejected by `URLValidator(schemes=("http", "https"))`. There is no server-side fetch, so this is not backend SSRF.

### 9. Account-code rate limits are per account with no caller/IP throttle

- **Location:** `backend/users/auth_services.py:15–17`, `backend/users/auth_services.py:84–174`
- **Concern:** Codes have a five-attempt limit and 60-second per-user/purpose resend cooldown, but no IP or caller-wide throttle. Resending replaces the code and resets failed attempts.
- **Severity:** Medium
- **Gated posture:** Low.
- **Public posture:** Medium. It permits sustained email traffic and approximately five guesses per account per minute.
- **Concrete request:** Password-reset requests for one known email are accepted every 60 seconds; distributing requests across many emails has no application-level ceiling.
- **Remedy:** Add deployment-edge and application rate limits keyed by IP plus normalized account identifier while preserving non-enumerating responses.

The implemented code lifecycle itself is sound:

- Six cryptographically generated digits.
- Only a salted HMAC is stored.
- User and purpose are included in the HMAC.
- One record exists per user/purpose.
- Expiry and attempt counters are locked transactionally.
- Failed-attempt increments survive rejection.
- Successful consumption and verification/password update are atomic.
- Verification and reset purposes cannot consume one another's codes.

### 10. Custom account lifecycle status is not an authentication control

- **Location:** `backend/users/models.py:49–55`, `backend/users/models.py:65–123`
- **Concern:** `User.status` can be `deactivated` or `pending_deletion`, but authentication still depends on inherited `is_active`. Changing only the custom status does not invalidate a session or necessarily prevent login.
- **Severity:** Medium
- **Gated posture:** Low because no user-facing deactivation flow currently exists.
- **Public posture:** Medium once Q174–176 lifecycle operations ship.
- **Concrete scenario:** Set `status="deactivated"` while `is_active=True`; Django's standard authentication backend can still authenticate the account.
- **Remedy:** Before implementing deactivation/deletion, define and test the coupling among `status`, `is_active`, and session invalidation.

## Verified privacy boundaries

### Profiles

- `GET /api/users/{username}/` returns only Q37 identity fields: ID, username, display name, avatar, bio, and home city.
- A private response has `access: "stub"` and does not embed diary entries, reviews, favorites, statistics, counts, or rating distributions.
- An authenticated viewer may receive their own relationship capabilities, not the private user's content.
- Direct `/been/`, `/reviews/`, `/favorites/`, and `/stats/` requests pass through `_profile_content_target()` and return 403 to unauthorized viewers.
- Email is absent from other-user serialization.

The earlier frontend tab-chrome leak is not mirrored in the API.

### Diary entries and reviews

- Profile Been uses `visible_to(viewer).filter(user=profile)`.
- Profile Reviews uses `visible_to(viewer).filter(entry__user=profile)`.
- Profile stats restrict visible diary/review querysets to the selected profile.
- Current-user diary uses `visible_to(request.user).filter(user=request.user)`.
- Event detail's viewer entry uses `visible_to(request.user).filter(user=request.user, event=event)`.
- Home rated activity uses `visible_to(viewer)` and then approved followees.
- Home review-like activity first restricts liked reviews through `Review.visible_to(viewer)`.
- Public event reviews use `for_public_section()` and exclude private accounts even when the viewer follows them.
- Circle uses approved followees only and excludes self from its list; its aggregate includes self by the settled contract.

No endpoint returns a private user's individual rating to an unauthorized ordinary viewer, apart from the single-contributor distribution inference described above.

### Will Be There

- Public attendees use `for_public_section()` and expose public accounts only.
- Circle attendees use approved followees and exclude self.
- Home WBT activity uses `visible_to(viewer)` and is also followee-scoped.
- Expired and hidden-event marks are removed from every read surface.
- The active count includes all privacy states anonymously by deliberate product ruling.

### Feed and notifications

- Every Home branch starts from approved followees.
- Rated Been and WBT branches also pass sanctioned visibility boundaries.
- Review-like activity appears only when the liked review is visible to the viewer.
- Favorite-event activity suppresses hidden events.
- Follow activity identifies private targets only with the Q37-safe ID/username/display-name shape.
- Notifications are always filtered by `recipient=request.user`.
- Notification payloads expose actor public identity and, for review likes, review ID and event ID—not private review text.
- Historical follow notifications surviving unfollow do not restore content access.

## Verified object-level authorization

No implemented IDOR was found.

| Surface | Server-side ownership or permission enforcement |
|---|---|
| Edit/delete rating or Been entry | Service filters `DiaryEntry` by both `user=request.user` and event. |
| Create/edit/delete review | Service resolves the current user's entry; delete filters `entry__user=user`. |
| Like review | Review ID must pass `Review.visible_to(request.user)`. |
| Unlike review | Deletes only `ReviewLike(user=request.user, review=review)`. |
| Favorites | Target ID is public catalog data; favorite create/delete is scoped to `request.user.id`. |
| Follow/unfollow/withdraw | Follow row is scoped by `follower_id=request.user.id`. |
| Accept/decline request | Follow row is scoped by `followee_id=request.user.id` and pending status. |
| Notification mark-read | Fetch uses both notification ID and `recipient=request.user`. |
| Mark-all-read | Updates only `recipient=request.user`. |
| Profile edit/privacy change | Operates only on `request.user.id`; no target-user ID is accepted. |
| WBT mark/unmark | Create/delete is scoped by current user and event. |
| Owner diary/favorite-venue reads | Query is scoped directly to `request.user`. |

Guessing a valid numeric ID either operates on the caller's own state or produces 404.

## Verified session and CSRF behavior

- `CsrfViewMiddleware` is active globally.
- No `csrf_exempt` use was found.
- Unsafe POST/PUT/DELETE methods therefore pass CSRF middleware.
- Browser-equivalent trusted and untrusted Origin behavior is contract-tested.
- Development trusted origins are explicit localhost Vite origins under `DEBUG`.
- Django `login()` is used for registration and login, rotating session keys against fixation.
- The frontend rereads the CSRF cookie for every unsafe request after Django token rotation.
- `logout()` flushes the session and is tested as invalidating and idempotent.
- Password reset deletes every active database session belonging to the user after changing the password.
- Password reset does not create a replacement authenticated session.

## Input and stored-content handling

- **Username:** Server-side 3–30 characters, lowercase storage, ASCII letters/numbers/underscore/period, bounded endpoints, and no consecutive periods.
- **Display name:** Server-side 1–50 characters after trimming on registration and profile edit.
- **Bio:** Exact stored length limited to 150; whitespace-only becomes null; mixed visible content remains verbatim.
- **Review:** Surrounding whitespace trimmed; stored length 1–1,000; database nonblank constraint.
- **Rating:** Exact half-star enumeration from 0.5 through 5.0.
- **Avatar:** HTTP/HTTPS only, at most 2,048 characters.
- **JSON:** Views reject non-object payloads where an object is required.

No `dangerouslySetInnerHTML`, raw `innerHTML`, or equivalent insertion was found. React renders usernames, display names, bios, reviews, titles, and entity names as escaped text. Stored `<script>` content displays as text rather than executing.

## Accepted-risk absence inventory

Ranked by public-posture severity:

1. **No login throttling or lockout — High public / Medium gated.** Add edge and application rate limiting before public access; prefer progressive throttling over permanent lockout.
2. **No registration throttling — High public / Low-to-medium gated.** Rate-limit by IP/device and add abuse monitoring before removing basic auth.
3. **No password-reset IP/global throttling — Medium-high public / Low gated.** Combine account cooldown with IP and global email-send limits in M5 deployment.
4. **No like/follow/favorite/WBT mutation throttling — Medium public / Low gated.** Add per-user burst limits before these actions influence popularity, trust, or significant notification volume.
5. **No security audit logging — Medium public / Low gated.** Record login failures, password resets, verification changes, privacy transitions, and administrative account-state changes before broader access.
6. **No application-level account lockout — Medium public / Low gated.** Accept through the gated season if login throttling exists at the deployment edge; revisit before public access.
7. **No CSP — Low-to-medium public / Low gated.** React escaping currently limits stored-XSS exposure, but define a deployment CSP after M4 finalizes image/font/style origins.

## Must fix before M5 flag flip

1. Suppress event rating distributions below an anonymity threshold.
2. Make verification state part of session/navigation and enforce guest-equivalent read visibility consistently for unverified sessions.
3. Add and verify production HTTPS/proxy/cookie security settings.

## Can ride as accepted risk through the gated season

Provided link + basic auth remains in front of the application:

- Login and registration throttling, with an explicit requirement before public opening.
- Password-reset timing enumeration and global/IP throttling, but not beyond the gated season.
- Mutation burst limits for likes, follows, favorites, and WBT.
- Security audit logging.
- Application-level lockout.
- CSP.
- Remote-avatar tracking exposure.
- Future coupling of custom account status to Django `is_active`, until account deactivation ships.

The private-rating distribution and verification-boundary issues should not be accepted merely because deployment is gated; both violate settled privacy and authentication semantics.
