> Diagnostic audit artifact. It records evidence and proposals; it does not replace the binding Markdown handoffs in `frontend/design-handoffs/` and does not authorize product-behavior changes.

# Onda exhaustive route and state matrix

This matrix is the shared scope for the semantic lead, visible-content root-cause auditor, and spacing/root-composition auditor. It is a coverage contract, not a claim that every state can be reached safely in production. Read-only production evidence may be used for public states; authenticated, error, destructive, and extreme-data states must be established from the shipped code, tests, and fixtures without mutating live data.

## Authority

Visual authority order for this audit:

1. `AGENTS.md`, explicit operator rulings, and frozen shipped product behavior.
2. `frontend/design-handoffs/*.md` (sole visual authority; later/narrower dated deltas win).
3. Binding product/navigation contracts and `frontend/DESIGN_BRIEF.md`.
4. `frontend/design-tokens.css` and `frontend/DESIGN_CONTRACT.md` as implementation vocabulary/consolidated index.
5. `refactoring-ui-for-agents/` general principles.
6. Existing CSS is evidence, not authority.

Classify every finding as one of:

- `BINDING`: violates a current product rule or handoff.
- `PRINCIPLE`: violates the agent design memory without conflicting with product authority.
- `DECISION`: a tension/ambiguity where a correction would choose product direction; do not resolve it.

## Cross-cutting axes to apply to every applicable route

- Viewports: 320px, 390px, 767px, 768px, 1280px, and a wider desktop; also 200% zoom/text enlargement.
- Session shell: session checking; guest; signed-in verified; signed-in unverified where exposed; session lookup failure with guest navigation + persistent Retry; account menu closed/open/focused; logout pending/failure/success.
- Identity/access: owner; other public user; other private user with no approval; pending follow; approved follow; profile follows viewer.
- Data: empty, sparse, normal, dense; one page, multiple pages, exhausted; 4-digit counts; long names/titles/locations/reviews; missing optional values.
- Media: present, absent, broken; hostile crop/aspect; event 4:5 fallback; user initials; artist silhouette.
- Network: initial loading, success, initial failure + Retry, continuation failure retaining prior content, mutation pending/success/error/conflict/auth-expiry.
- Interaction: rest, hover, visible keyboard focus, pressed, selected/current, disabled, pending, success, inline error, Escape/outside dismissal; reduced motion/forced colors where applicable.
- Global page anatomy: persistent header/nav/account controls, main, session-error slot, footer; mobile fixed top-account bar and bottom nav; desktop top header; no horizontal scrolling or chrome overlap.

## Reachable route/surface graph

### R00 — global shell on every route (0 touches)

- Guest primary navigation: Discover, Search; Register and Log in account controls.
- Signed-in primary navigation: Home, Discover, Search, Activity, Profile; `@handle` account trigger.
- Account menu (1 touch): Edit profile and Log out; open/selected/focus/outside-click/Escape/logout-error states.
- Session checking indicator; session lookup failure with persistent Retry while public content remains usable.
- Footer with Resident Advisor source link.
- Desktop and mobile chrome/reservation states.

### R01 — landing resolver `/` (0 touches)

- Session checking transient.
- Guest redirect to `/discover`; signed-in verified redirect to `/home`; unverified destination per shipped landing rules.
- Legacy `/?city_id={id}` city-preserving redirect to `/discover?city_id={id}`.
- Session error still permits public browsing through global shell.

### R02 — Discover `/discover?city_id={id}` (0–1 touches)

- Cities: initial loading; load error + Retry; no cities; invalid/missing city id normalized to first city; selected city.
- Header band: city H1, City dropdown closed/open, selected option, long option labels, keyboard traversal/Escape/outside close.
- Inline city search: empty, one-character silence, debounce/loading, results, fewer-than-three tail action, no results, failure/Try again, Clear, Escape/outside close, keyboard-focused rows, navigate to global Search.
- Tabs: Upcoming and Recent, rest/focus/selected; switching retains independent ledger state.
- Each ledger: initial loading, error + Retry, empty, sparse, dense, present/missing/broken fliers, long titles/venues/lineups, automatic continuation loading, continuation failure retaining rows, exhausted.
- Recent rows: below/at rating threshold and judgment-star presence.
- Destinations: event detail from whole row; venue/artist/search through later surfaces.

### R03 — Search `/search[?q=&scope=]` (1 touch)

- Empty query with Recent searches absent/empty/populated; apply one recent, remove one, Clear all.
- One-character silent state.
- Typed 2+ query: Clear control; All/Events/Artists/Venues/People selected states; debounce/loading; initial failure + Retry; no results.
- All scope grouped results: each group absent/present, cap at five, View all count and scope transition.
- Single scopes: sparse/dense rows, next cursor, Load more pending, continuation failure retaining rows, exhausted.
- Result variants: event flier fallback; artist portrait/silhouette; venue context; person avatar/initials and handle; hostile/long text.
- Keyboard result index via Up/Down, focused row, Enter navigation, Escape reset.
- Query/scope deep links and stale request cancellation.

### R04 — Home `/home` (1 touch signed-in; guest redirect)

- Session checking; session error; guest redirect to Discover; verified signed-in feed.
- Feed loading; initial failure + Retry; empty + Discover-events action; sparse/dense chronology.
- Every activity type: rated Been with/without review; Will Be There; review like; favorited event; favorited artist; follow.
- Legal grouped one-line types: 1–3 objects and overflow; long actor/object names; actor truncation while verb survives.
- Flier present/absent/broken; relative time extremes; review clamp + Read more navigation.
- Load more rest/pending; continuation failure retaining rows; exhausted.

### R05 — Activity `/activity` (1 touch signed-in)

- Session checking; guest sign-in message; authenticated loading; initial failure + Retry; empty.
- Read and unread rows; each notification type supported by presenter; long actor/event strings; relative time.
- Whole-row destination to event or actor profile.
- Mark-all-read pending/success/failure while content remains; Retry marking-as-read.
- Pagination/load-more rest/pending/failure retaining rows/exhausted.

### R06 — Profile Been `/u/:username` and Reviews `/u/:username/reviews` (1–multi touch)

- Initial loading; not found; initial failure + Retry.
- Owner, other public, other private stub, pending request, approved/following/follows-you relationships.
- Header: image/initial avatar; long display name/handle/home city; optional/long bio; 0/1/4-digit follower/following counts; owner Edit profile vs fixed-width Follow states (Follow/Unfollow/Request/Requested/pending/error + local Retry).
- Statistics: independent loading/error + Retry; zero/sparse/dense counts; rating unavailable; histogram hidden below five vs static histogram shown at/above five.
- Tabs stable above swapped content; Been/Reviews focus/current states.
- Been tab: independent loading/error + Retry; empty; rated/unrated; written-review marker; sparse/dense; pagination first/middle/last.
- Reviews tab: independent loading/error + Retry; empty/data; Sort menu closed/open, four selections, keyboard/outside dismissal; pagination.
- Favorites: independent loading/error + Retry; silent empty; event/artist/venue rows; owner heart remove pending/error/reload; non-owner no remove; missing/broken media.
- Private stub with public identity/social counts and no private modules.

### R07 — Edit profile `/settings/profile` (1–2 touches, owner only)

- Session checking; guest redirect to Login; initial load; load error + Retry; loaded form.
- Avatar: initials/photo, Upload target, native picker entry, uploading, upload error, Remove pending/success/error.
- Display name empty/long/server error; bio empty/max/over/error with live counter; City dropdown none/selected/open/keyboard/error; Public/Private selection and consequence copy; field/request/global errors.
- Save pristine/changed/pending/success navigation/error; Cancel.
- Follow requests module independently loading/error + Retry/empty/data; requester rows; Approve/Decline pending/success/error; pagination.

### R08 — Event detail canonical `/e/:slug-id`; legacy `/events/:key` (1–5 touches)

- Legacy numeric/alternate key canonical replacement; invalid key; loading; not found/hidden; initial failure + Retry.
- Upcoming and past identity; guest and signed-in viewer; long title/venue/city; flier present/absent/broken; lineup empty/single/dense/long.
- Upcoming: WBT 0/1/many; viewer can/cannot mark; unmarked/marked/pending/error/auth-expiry; Circle/Public attendees independently loading/error/empty/sparse/dense/paginated; guest sign-in boundary.
- Past rating summary: insufficient vs available; 0/ten-bucket extremes; static chart; View distribution closed/open.
- Past social: Your Circle and Public independently loading/error/empty/sparse/dense/paginated; review sort closed/open/options; guest boundary; review excerpt collapsed/expanded; Like/Unlike rest/pending/error/auth-expiry; own review has no like.
- Signed-in owner block: unrated StarInput empty/hover/half/full/keyboard/commit/error; favorited/unfavorited/pending/cap-rejected; dormant WBT record.
- Rated viewer: own row collapsed; Edit expanded; rating update; review empty/valid/max/invalid; Publish/Save pending/error; Delete review confirmation; Remove rating confirmation (with/without review); Remove Been confirmation; dialog Cancel/confirm/Escape/focus.
- Guest sees no disabled/solicitation favorite/owner controls.

### R09 — Venue canonical `/v/:slug-id`; legacy `/venues/:key` (2+ touches)

- Canonical replacement; invalid key; loading; not found; error + Retry.
- Identity with long name and location variants/missing parts; location-to-Discover link; guest vs signed-in Favorite states/error/cap.
- Upcoming and Past ledgers independently loading/error/empty/sparse/dense/paginated/continuation error; venue omitted from rows; missing/broken fliers; one-page chrome absent.

### R10 — Artist canonical `/a/:slug-id`; legacy `/artists/:key` (2+ touches)

- Canonical replacement; invalid key; loading; not found; error + Retry.
- Portrait present/absent/broken; long name; guest vs signed-in Favorite states/error/cap.
- Upcoming and Past ledgers independently loading/error/empty/sparse/dense/paginated/continuation error; current artist omitted from lineup; missing/broken fliers; one-page chrome absent.

### R11 — Register `/register` (1 touch guest, contextual from Login)

- Pristine five-field form; privacy unchosen/Public/Private and selected consequence only.
- Local empty/type/length errors; username taken/server field errors/request error; values retained.
- Submit rest/pending/success redirect; long labels/content/autofill/password-manager states.

### R12 — Login `/login` (1 touch guest, contextual from auth)

- Pristine; empty identifier/password errors; non-enumerating invalid credentials attached to Password; server failure.
- Submit rest/pending/success redirect; autofill/password-manager.
- Links to reset and register.

### R13 — Verify email `/verify-email` (post-registration/stateful)

- Missing/generic email vs known destination.
- Code empty/partial/exact; local invalid; server invalid; expired with new code requested; request failure.
- Submit pending; Resend rest/pending/sent/error.
- Terminal success with form removed and primary Continue.

### R14 — Reset request `/reset-password` (1–2 touches)

- Form pristine; invalid/empty/server error; sending pending.
- Non-enumerating same-route confirmation with repeated destination; Enter code; Use different email; remembered/Login path.

### R15 — Reset confirmation `/reset-password/confirm` (2–5 touches/direct entry)

- Direct entry without stored email: email form pristine/error/pending/success.
- Code step: empty/partial/exact; invalid/expired; resend pending/success/error; different-email escape.
- New-password step: empty/short/mismatch/server errors; pending.
- Terminal Password changed + primary Log in.

### R16 — Legacy Been `/been` (contextual legacy URL)

- Session checking; guest redirect to Login; signed-in redirect to own canonical profile.

### R17 — global not found `*` and entity/profile not-found variants

- Generic Page not found with concise explanation + Return to Discover.
- Event hidden/not found; venue not found; artist not found; profile not found.
- Compare page anatomy, action hierarchy, persistent shell, and footer across all variants.

## Evidence requirements for both root-cause audits

For each finding, assign an ID and include:

1. observed condition;
2. user/comprehension consequence;
3. authority/principle and `BINDING`/`PRINCIPLE`/`DECISION` class;
4. exact route, state, viewport;
5. evidence: file + line/component/selector and live observation when available;
6. root cause (shared system, primitive, page-local composition, content rule, or state omission);
7. affected sibling surfaces/blast radius;
8. severity: Critical/High/Medium/Low by user impact and authority, not conspicuousness.

Do not propose a redesign or change behavior. Report diagnostic root causes only.
