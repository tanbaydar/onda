> Diagnostic audit artifact. It records evidence and proposals; it does not replace the binding Markdown handoffs in `frontend/design-handoffs/` and does not authorize product-behavior changes.

# Visible-content root-cause audit

Status: complete diagnostic report
Scope authority: `01-route-state-matrix.md` (R00–R17)
Product authority: `frontend/design-handoffs/*.md`, then `frontend/DESIGN_BRIEF.md`, `frontend/DESIGN_CONTRACT.md`, and `frontend/design-tokens.css` in the precedence stated by `AGENTS.md` and `DESIGN_CONTRACT.md:9-26`
Principle reference: `refactoring-ui-for-agents/`, especially the operating system, hierarchy, typography, color, imagery, depth, finishing, and `QUICK_AUDIT.md` modules
Audit mode: diagnostic only; no application, behavior, authority, fixture, or repository file was changed.

## Classification

- **BINDING** — a direct mismatch with a current handoff or locked token/component rule.
- **PRINCIPLE** — a mismatch with the design-memory principles or consolidated contract where no current handoff decides otherwise.
- **DECISION** — the implementation and principles point in different directions, or current authority is silent/ambiguous; an operator ruling is required before changing it.

Severity describes the visible system damage, not implementation effort.

## Executive root-cause map

The present branch does **not** contain an uncontrolled number of font families, arbitrary colors, card effects, shadows, gradients, or radii. It uses the three ruled families and the locked semantic palette. The recurring failures are allocation failures:

1. Global element selectors assign identity typography and ledger spacing to unrelated system/state content.
2. Request state is modeled by endpoint instead of by user-visible phase, so initial, continuation, and mutation failures inherit the wrong copy, location, and recovery behavior.
3. A few surfaces fork a new local rendering grammar instead of reusing the ruled row/state grammar.
4. Availability is not always represented in styling conditions, so judgment color and controls remain present when the underlying judgment/content is absent.
5. The deployed public site is not fully aligned with the audited source in at least one binding registration state.

These are design-system/root-cause defects, not isolated requests to make individual pixels prettier.

---

## Findings

### VIS-001 — Logout reuses session-bootstrap state and therefore renders the wrong mutation semantics

- **Class / severity:** BINDING / High
- **Affected scope:** R00 account menu; signed-in mobile and desktop; logout pending and logout failure.
- **Lead problem:** The account menu has no visible logout-in-progress or logout-failure grammar. A failed logout is announced as `Account status could not be loaded.` in the global session line.
- **Root cause:** `App` stores bootstrap lookup failure and logout mutation failure in the same `session.error` field. `AccountMenu` receives only an untyped `onLogout` callback, with no pending/error state. The menu action therefore cannot change its label, disable duplicate commits, or own its local failure copy.
- **Evidence:**
  - `frontend/src/App.jsx:46-50` defines one session state with one `error` channel.
  - `frontend/src/App.jsx:67-78` writes logout failure into that channel.
  - `frontend/src/App.jsx:101-105` always translates that channel to `Account status could not be loaded.` plus `Retry`, whose action re-runs session lookup rather than logout.
  - `frontend/src/components/AccountMenu.jsx:31-38` renders a static `Log out` row with no pending/failure state.
- **Authority mismatch:** `accessibility-handoff.md:28-30` requires a local sentence plus Retry and retention for action failures; the account-status line is specifically the session-lookup recovery surface. The rendered copy describes a different operation from the one that failed.
- **Visible consequence:** The UI lies about the failure, leaves the original action semantically unresolved, and makes the offered Retry perform a different request.

### VIS-002 — The global shell renders a session-checking message and immediately hides it at every viewport

- **Class / severity:** PRINCIPLE / Medium
- **Affected scope:** R00 and R01; public-route shell while session lookup is pending; 390px and 1280px.
- **Lead problem:** Public pages can change from guest to signed-in chrome without any visible system feedback even though the application emits `Checking session…`.
- **Root cause:** A tag/position selector suppresses all qualifying direct header paragraphs instead of distinguishing obsolete header copy from the current async status.
- **Evidence:**
  - `frontend/src/App.jsx:99` renders `<p>Checking session…</p>` in the site header.
  - `frontend/src/styles.css:115` sets `body>div>header>p:not(:first-child){display:none}` with no viewport override.
  - `frontend/src/App.jsx:24-28` separately shows the status only on the root resolver; it does not cover session checking on already-addressed public routes.
- **Principle mismatch:** `DESIGN_CONTRACT.md:377-385` requires loading states to preserve their intended slot and hierarchy; `QUICK_AUDIT.md:86-92` requires real loading states to be visually checked.
- **Visible consequence:** The shell contains two contradictory truths: a loading state in markup and silence in presentation. That makes account-chrome changes look incidental rather than controlled.

### VIS-003 — Footer presence on authentication routes is an unresolved authority tension

- **Class / severity:** DECISION / Medium
- **Affected scope:** R11–R15, both widths.
- **Lead problem:** Authentication pages are the only route family where the globally rendered provenance footer disappears.
- **Root cause:** The global shell always mounts the footer, while one `:has(main.auth-page)` selector makes route content decide whether that shell landmark exists visually.
- **Evidence:**
  - `frontend/src/App.jsx:159-164` renders the footer outside `Routes`.
  - `frontend/src/styles.css:373` hides it whenever an auth page is present.
  - `DESIGN_CONTRACT.md:410-416` describes a footer as part of native page anatomy.
  - `auth-handoff.md:47-49` explicitly withdraws the auth-only exception for navigation and account controls, but does not explicitly rule the footer in or out.
- **Why this requires a ruling:** The implementation suggests deliberate route suppression; current sole-authority handoffs are explicit about persistent product chrome but silent about this footer. Treating either choice as already authorized would invent authority.
- **Visible consequence:** Auth routes feel like a separate mini-site even though the newer handoff explicitly moves them back into the persistent product shell.

### VIS-004 — One global H1 rule makes system failures look like catalog identity, and Profile forks an incomplete not-found state

- **Class / severity:** PRINCIPLE / High
- **Affected scope:** R17 generic, event, venue, artist, and profile not-found variants; both widths.
- **Lead problem:** Not-found titles use the same expressive display face and 30/36px identity scale as event/artist/venue identity. The Profile variant additionally omits the route back to Discover.
- **Root cause:** `h1` is treated as a visual role instead of a semantic element requiring a scoped role. Separately, each entity owns bespoke not-found markup; Profile's fork has drifted from the common anatomy.
- **Evidence:**
  - `frontend/src/styles.css:10-13` applies display-face identity styling to every `h1` and `h3`.
  - Generic: `frontend/src/App.jsx:31-39`; event: `EventPage.jsx:173-181`; venue: `VenuePage.jsx:55-63`; artist: `ArtistPage.jsx:55-63`.
  - `frontend/src/pages/ProfilePage.jsx:134-136` renders `Profile not found` plus explanation but no `Return to Discover` action.
  - `DESIGN_CONTRACT.md:406` calls for a functional H1, concise explanation, and one route to Discover.
- **Principle mismatch:** Display type is allocated to identity, not routine system prose (`DESIGN_BRIEF.md:12-22`; `DESIGN_CONTRACT.md:42-49`). The global selector collapses those roles.
- **Visible consequence:** A recoverable/system state receives catalog-level drama, while the one outlier variant is also less useful.

### VIS-005 — The Search heading visually outranks the object explicitly ruled as primary

- **Class / severity:** BINDING / High
- **Affected scope:** R03 empty, one-character, loading, success, empty-results, error, and continuation states; 390px and 1280px.
- **Lead problem:** `Search` is a 30/36px display identity above an 18px functional search field, so the page's label becomes more visually important than the user's search instrument.
- **Root cause:** The same global H1 identity selector described in VIS-004 is allowed to determine the hierarchy of a task surface. The local Search styles reduce only the H1 margin and do not assign it a functional role.
- **Evidence:**
  - `frontend/src/pages/SearchPage.jsx:97-103` places the H1 before the search object.
  - `frontend/src/styles.css:10-11,58-65` gives the H1 display-title amplitude while the field uses the ruled 18px register.
  - Read-only live inspection at `/search`, 390×844 and 1280×900, confirmed the display title is the first dominant object.
- **Authority mismatch:** `search-handoff.md:11-18` explicitly states `Bar = the page's primary object` and assigns it the primary-control register.
- **Visible consequence:** The page reads as a branded title page followed by a control, not as an immediate search instrument.

### VIS-006 — Activity serializes actor and verb into one bold string, destroying the ruled sentence hierarchy

- **Class / severity:** BINDING / High
- **Affected scope:** R05 populated sparse/dense activity; read and unread rows; both widths.
- **Lead problem:** Every word in `Ada liked your review.` or `Ada followed you.` receives the actor emphasis. Read state then changes the weight of the entire sentence, not just the actor name.
- **Root cause:** `notificationText()` returns one interpolated string. Rendering wraps that entire string in `<strong>`, so CSS has no node representing the actor role separately from the verb and object.
- **Evidence:**
  - `frontend/src/pages/ActivityPage.jsx:9-20` flattens actor, action, and punctuation into one string.
  - `frontend/src/pages/ActivityPage.jsx:120-126` wraps that string wholly in `<strong>`.
  - `frontend/src/styles.css:194-199` applies unread 600/read 500 to every `strong` in the row.
- **Authority mismatch:** `frontend/design-tokens.css:136-138` rules `sentence ui with names 600 ink`; read state recedes text and names to muted/500. `DESIGN_CONTRACT.md:403` repeats the actor-name distinction.
- **Visible consequence:** Activity loses the fast scan pattern common to professional social feeds: who acted is not separated from what happened.

### VIS-007 — Home and Activity model continuation failures as page errors, so recovery is displaced or destructive

- **Class / severity:** BINDING / High
- **Affected scope:** R04 and R05 continuation failure after populated data; both widths.
- **Lead problem:** Activity shows `More activity could not be loaded.` above the entire ledger with no Retry. Home shows a page-level error above the retained ledger; pressing its Retry clears and reloads the complete feed instead of retrying continuation.
- **Root cause:** Neither page has a complete, phase-specific continuation state. Activity has a string-only `actionError`; Home writes continuation failure into the same `state.error` used for initial failure and connects its Retry to the initial-load `retry` dependency.
- **Evidence:**
  - Activity: `frontend/src/pages/ActivityPage.jsx:72-88,104` records a bare continuation error and renders no recovery action; the originating control remains at `130-134` below the ledger.
  - Home: `frontend/src/pages/HomePage.jsx:54-68` defines a full-load retry; `70-79` writes load-more failure into the shared error; `89-96` renders the error before rows and hides continuation; the Retry increments the full-load dependency.
- **Authority mismatch:** `accessibility-handoff.md:27-30` requires one local sentence plus Retry and retained successful content for continuation failure. `DESIGN_CONTRACT.md:614-616` names Home and Activity explicitly.
- **Visible consequence:** Failures are detached from the control and content boundary where they occurred. Home's offered recovery temporarily destroys the very successful content the design says to preserve.

### VIS-008 — Your Circle clears successful rows when continuation fails

- **Class / severity:** BINDING / High
- **Affected scope:** R08 past event, signed-in Circle with more than one page, continuation failure; both widths.
- **Lead problem:** A page-two failure replaces the rating summary and all already-loaded Circle reviews with a generic section error.
- **Root cause:** The success branch appends to existing `state.data`, but the catch branch is not page-aware and always writes `data:null`.
- **Evidence:**
  - `frontend/src/components/YourCircle.jsx:27-33` correctly distinguishes first load from continuation and appends results.
  - `frontend/src/components/YourCircle.jsx:34-39` clears `data` on every non-abort failure.
  - `frontend/src/components/YourCircle.jsx:71-107` can render either the error or successful Circle payload only because that payload has been erased.
- **Authority mismatch:** `accessibility-handoff.md:28` requires successful content to remain mounted after continuation failure; `DESIGN_CONTRACT.md:379-385` repeats the rule.
- **Visible consequence:** A network failure rewrites the user's understanding from “these Circle entries loaded” to “Your Circle could not be loaded,” which is factually and visually false.

### VIS-009 — Missing artwork removes the fixed upcoming-event identity slot instead of rendering its ruled fallback

- **Class / severity:** BINDING / High
- **Affected scope:** R08 upcoming event with absent artwork; missing, broken, and extreme media were reviewed; mobile and desktop.
- **Lead problem:** When `cover_image_url` is absent on an upcoming event, the entire 80×100/160×200 fixed artwork column disappears and metadata reflows to a text-only composition. Failed URLs do get `ImageSlot` fallback, so absent and failed media visibly disagree.
- **Root cause:** The event page condition treats all upcoming imagery as though it were the excluded full-bleed hero, despite the shipped page using the ruled fixed identity composition.
- **Evidence:**
  - `frontend/src/pages/EventPage.jsx:195-204` mounts `ImageSlot` only when artwork exists or the event is past.
  - `frontend/src/styles.css:310-316` proves the current composition is a fixed flier grid and contains a special text-only reflow branch.
  - Live read-only inspection of `/e/synapse-version-mind-717` at 390×844 and 1280×900 confirmed complete slot collapse for an upcoming event with no artwork.
- **Authority mismatch:** `polish-handoff.md:4-9` applies the initial fallback to event-page identity fliers at 80×100/160×200; only a full-bleed upcoming hero is excluded. `DESIGN_CONTRACT.md:210-211` explicitly notes the current shipped page uses the fixed composition rather than that hero.
- **Visible consequence:** The layout and identity amplitude change based on the transport shape of missing media, not on the intended event hierarchy.

### VIS-010 — Edit Profile field errors inherit ledger-row padding and borders from tag-wide list rules

- **Class / severity:** BINDING / High
- **Affected scope:** R07 request and field validation errors, including multiple messages; both widths.
- **Lead problem:** An inline validation message becomes a 16px-padded list item; multiple messages receive repeating-row hairlines. This visually promotes field feedback into a ledger/summary block.
- **Root cause:** Error content is rendered as `<ul><li>` with no error-list component class, while `main ul/li` globally means a repeating content ledger.
- **Evidence:**
  - `frontend/src/pages/EditProfilePage.jsx:92,117-124` renders request and field errors as role-alert unordered lists.
  - `frontend/src/styles.css:30-32` removes list markers, gives every main list item 16px vertical padding, and adds borders between siblings.
  - The dedicated ruled field-error register exists at `frontend/src/styles.css:349-355`, but applies only to `.auth-error`, not Edit Profile lists.
- **Authority mismatch:** `auth-handoff.md:13-17` rules one 12px danger line 6px below the field and prohibits summary blocks; `profile-handoff.md:28-37` explicitly inherits the auth-column/form register for Edit Profile. `frontend/design-tokens.css:145-148` limits danger surfaces to error/Retry treatment.
- **Visible consequence:** Error density and boundaries jump dramatically exactly when the form is under stress, making validation look like unrelated list content.

### VIS-011 — The unavailable profile average is colored as committed judgment

- **Class / severity:** BINDING / Medium
- **Affected scope:** R06 profile statistics with zero/insufficient rating history; public, private, and owner profiles where statistics render; both widths.
- **Lead problem:** The em dash meaning “no average is available” is green, the same color allocated to actual judgment data.
- **Root cause:** Color is attached to the containing statistic role rather than conditioned on the value's availability state.
- **Evidence:**
  - `frontend/src/pages/ProfilePage.jsx:76-80` renders either a numeric average or `—` in the same `.stat-value`.
  - `frontend/src/styles.css:156-159` colors every value in `.profile-judgment-unit` with `--judgment`.
- **Authority mismatch:** `accessibility-handoff.md:7-10` and `DESIGN_BRIEF.md:23-26` reserve green for actual judgment. Absence is not judgment.
- **Visible consequence:** Color asserts meaning that the data explicitly withholds, weakening the reliability of the only accent channel.

### VIS-012 — Sort controls remain visible before it is known whether sortable content exists

- **Class / severity:** DECISION / Medium
- **Affected scope:** R06 Reviews loading/error/empty and R08 Public reviews loading/error/empty; both widths.
- **Lead problem:** A `Most liked`/`Newest` trigger is present while reviews are loading, failed, or empty. It becomes visual chrome with no useful result set to reorder.
- **Root cause:** Sort control mounting is based only on being in the Reviews/Public surface, not on successful non-empty data availability.
- **Evidence:**
  - `frontend/src/components/PublicReviews.jsx:61-77` mounts `SortMenu` before every state branch.
  - `frontend/src/pages/ProfilePage.jsx:153-154` mounts the profile sort from route-tab selection outside the Reviews data component, so it cannot know loading/error/empty state.
  - Live read-only inspection of a past event with no public reviews at 390×844 and 1280×900 showed the sort trigger directly above `No public reviews yet.`
- **Why this requires a ruling:** `QUICK_AUDIT.md:86-92` says controls that cannot work in empty states should be hidden or meaningfully disabled, but `polish-handoff.md:35-37` blesses the sort menu “as shipped” without distinguishing its data states. The static component styling is clearly authorized; state-dependent visibility is not clearly decided.
- **Visible consequence:** Empty and error states look unfinished because a control advertises a comparison operation with nothing to compare.

### VIS-013 — The city selector uses stemmed arrows where the ruled control calls for a muted chevron

- **Class / severity:** BINDING / Low
- **Affected scope:** R02 city closed/open/keyboard states and R07 Home-city selector reuse; both widths.
- **Lead problem:** The control shows `↓`/`↑`, visually stronger directional arrows, rather than the quiet disclosure chevron used by the ruled input grammar.
- **Root cause:** The disclosure mark is an unscoped text shortcut in component markup, not a designed glyph role.
- **Evidence:** `frontend/src/components/CityDropdown.jsx:66-73` renders literal up/down arrows. `discover-handoff.md:4-9` specifies a `--text-muted` chevron, and `profile-handoff.md:28-35` specifies the same dropdown with a `▾` affordance.
- **Visible consequence:** A high-frequency control carries a different icon vocabulary from the menu/disclosure grammar, a small but repeated sign of local implementation rather than system reuse.

### VIS-014 — Discover search uses a separate error vocabulary from the product recovery grammar

- **Class / severity:** BINDING / Medium
- **Affected scope:** R02 inline-search failure; both widths.
- **Lead problem:** The panel renders `Search failed.` followed by a button labelled `Try again.`. Elsewhere the ruled control word is `Retry`, and the button itself carries sentence punctuation.
- **Root cause:** The inline search owns local ad-hoc copy instead of the cross-cutting recovery vocabulary already used by the full Search page.
- **Evidence:** `frontend/src/components/DiscoverSearch.jsx:52-57`; compare the full Search page at `frontend/src/pages/SearchPage.jsx:105-110`.
- **Authority mismatch:** `accessibility-handoff.md:27-30` requires one stable local sentence plus `Retry`; `DESIGN_CONTRACT.md:610-616` calls out Retry versus Try again as vocabulary to standardize.
- **Visible consequence:** Identical search failures change tone and control grammar based only on entry point.

### VIS-015 — The Discover dropdown forks a compact event-result typography instead of clearly reusing the ruled row role

- **Class / severity:** DECISION / Medium
- **Affected scope:** R02 inline-search populated results, sparse/dense/long-title/missing-art states; both widths.
- **Lead problem:** Inline event-result titles render at body 16px, while standard event/search row titles use the 18/20px row-title token. The row is also a button-only compact variant rather than the full row component used on the Search page.
- **Root cause:** `compact=true` selects a separate `CompactEventResultRow` and a separate CSS rule, duplicating event-result anatomy rather than amplitude-scaling the integrated row.
- **Evidence:**
  - `frontend/src/components/SearchResults.jsx:37-49,52-66` forks compact event results.
  - `frontend/src/styles.css:79-85` sets compact result titles to `--text-body`; standard result names use `--text-row-title` at `89-92`.
  - `search-handoff.md:17-21` requires result rows to reuse integrated components verbatim; its Discover-dropdown section at `28-29` specifies the panel but does not explicitly state whether that verbatim anatomy or a compact amplitude applies inside it.
- **Why this requires a ruling:** The system principle favors one repeated row grammar, but the dropdown's constrained overlay may justify a smaller amplitude. The handoff does not explicitly adjudicate that collision.
- **Visible consequence:** The same event search result changes title scale and component grammar when accessed one touch earlier from Discover.

### VIS-016 — The profile identity header introduces a section boundary that the hairline system reserves for repeated siblings

- **Class / severity:** BINDING / Medium
- **Affected scope:** R06 owner, public, approved-private, and private-stub profiles; both widths.
- **Lead problem:** A full-width bottom hairline boxes off identity from Statistics even though the handoff defines both as one fused header band. The tab boundary below is therefore no longer the sole content-switching divider.
- **Root cause:** The profile header is styled as a panel with its own bottom border, rather than letting spacing express the identity/statistics grouping.
- **Evidence:**
  - `frontend/src/styles.css:234` adds `border-bottom` to `.profile-header`.
  - `profile-handoff.md:4-6` defines identity followed by Statistics as header-band data and says the tabs contract only content below them.
  - `frontend/design-tokens.css:86-88` states hairlines are only between repeating siblings and sections use whitespace.
- **Visible consequence:** The profile reads as a stack of bounded modules rather than a fused identity/statistics composition, one of the exact patterns that makes a flat editorial product look assembled from local blocks.

### VIS-017 — The live Register screen violates the no-consequence-before-choice rule even though the audited source is correct

- **Class / severity:** BINDING / High, deployment-specific
- **Affected scope:** R11 untouched registration state on the public live site; observed at 390×844. Current source branch does not reproduce it.
- **Lead problem:** With neither Public nor Private selected, live `/register` displays the Public consequence sentence.
- **Root cause:** This is a source/deployment divergence, not a current-branch component defect. The deployed bundle is older or otherwise different from the audited source for this state.
- **Evidence:**
  - Read-only live inspection of `https://ondaapp.io/register` at 390×844 showed no selected radio and the Public-only consequence copy simultaneously.
  - Current source `frontend/src/pages/RegisterPage.jsx:59-65,74-78` correctly computes `privacyCopy = null` before either choice and conditionally omits the paragraph.
- **Authority mismatch:** `auth-handoff.md:51-59` explicitly prohibits Public-only or Private-only consequence text before a privacy choice exists.
- **Visible consequence:** The untouched form appears to preselect a consequence semantically without reflecting a selected control, undermining trust at the highest-friction entry surface.

---

## Coverage ledger

Every route/state class from the shared matrix was reviewed against visible copy, typography, color, imagery/fallbacks, glyphs, borders/depth/shapes, controls, and rendered states. “No additional finding” means no independent visible-content root cause beyond the cross-cutting IDs listed; it does not claim spacing-agent clearance.

| ID | Surface/state class reviewed | Viewports/evidence | Root findings |
|---|---|---|---|
| R00 | Global shell: guest/signed-in chrome, account menu open/closed, session checking/failure, logout pending/failure, footer | Source/CSS; live shell at 390×844 and 1280×900 | VIS-001, VIS-002, VIS-003 |
| R01 | Landing/session resolver redirects and transient checking state | Source/CSS; route-state logic | VIS-002 |
| R02 | Discover: city loading/error/empty/open/keyboard, Upcoming/Recent, inline search idle/loading/results/empty/error, sparse/dense/long/missing media | Source/CSS/fixtures guidance; live at 390×844 and 1280×900 | VIS-013, VIS-014, VIS-015; VIS-009's media-allocation root applies to shared fixed slots but Discover's `ImageSlot` path itself conforms |
| R03 | Search: empty-query Recent, 1 char, scopes, loading, grouped/single results, empty, initial/continuation error, keyboard, hostile text/media | Source/CSS; live empty and populated results at 390×844 and 1280×900 | VIS-005; standard Search continuation retention and fallback paths otherwise conform |
| R04 | Home: session gates, loading, empty, sparse/dense/grouped feed, initial/continuation error, long review/media fallback | Source/CSS/fixture variants | VIS-007 |
| R05 | Activity: guest/loading/empty/populated read/unread, initial/continuation/read-bookkeeping failure, dense content | Source/CSS/fixture variants | VIS-006, VIS-007 |
| R06 | Profile Been/Reviews: owner/public/private/stub, statistics zero/available/error, tabs loading/empty/error/dense, follow/favorites states | Source/CSS/fixture variants | VIS-011, VIS-012, VIS-016; VIS-004 covers profile not-found |
| R07 | Edit Profile: session/load/error, all fields, upload/remove/errors, privacy, save/server errors, follow requests sparse/dense | Source/CSS/fixture variants | VIS-010, VIS-013 |
| R08 | Event: upcoming/past, owner/guest, rating/WBT/favorite, Circle/Public/attendees, pagination/continuation, empty/error, absent/broken/extreme media | Source/CSS/fixtures; live upcoming missing-art and past empty-Public at 390×844 and 1280×900 | VIS-008, VIS-009, VIS-012; VIS-004 covers event not-found |
| R09 | Venue: loading/error/not-found, identity/location/favorite, Upcoming/Past ledgers, sparse/dense/missing media | Source/CSS/fixture variants | VIS-004 covers not-found; no additional visible-content root cause found |
| R10 | Artist: loading/error/not-found, portrait present/absent/failed, favorite, Upcoming/Past ledgers | Source/CSS/fixture variants | VIS-004 covers not-found; circular portrait/silhouette grammar conforms |
| R11 | Register: untouched, local invalid, server field/request error, submitting, long values, privacy choices | Source/CSS; live untouched state at 390×844 | VIS-003, VIS-017 |
| R12 | Login: untouched, local invalid, credential/server error, submitting | Source/CSS | VIS-003; field-owned error register conforms |
| R13 | Verify email: entry, invalid/expired, resend pending/error/success, verification success/continuation | Source/CSS | VIS-003; terminal-state and primary-action grammar conform |
| R14 | Reset request: untouched/invalid/submitting/error/success and alternate-email path | Source/CSS | VIS-003; non-enumerating completion grammar conforms |
| R15 | Reset confirm/form: missing email/code, code/new-password steps, invalid/mismatch, pending/error/success | Source/CSS | VIS-003; no additional visible-content root cause found |
| R16 | Legacy/route-resolution and session-checking transients | Source route/redirect logic and global shell CSS | VIS-002 |
| R17 | Generic and entity not-found variants, unknown/malformed keys, explanatory copy/action | Source across App/Event/Venue/Artist/Profile | VIS-004 |

## System-level controls that held

These checks are recorded to prevent the later solution phase from “fixing” compliant foundations:

- **Font count:** exactly three authorized families are loaded: Rozha One (identity), General Sans (functional), Gambetta (prose), in `frontend/design-tokens.css:11-16,35-39`. The defect is role leakage (VIS-004/005), not raw family count.
- **Palette:** inspected styles use the locked semantic palette. Green remains concentrated in rating/like/favorite/WBT roles except the availability leak in VIS-011; no separate decorative brand palette was found.
- **Depth/shape:** no card system, decorative shadows, gradients, glass, or general rounded rectangles were found. Panels are flat; circles are restricted to portrait/avatar grammar. VIS-016 is a boundary-allocation problem, not a request for added depth.
- **Media fallbacks:** shared `ImageSlot`, person initials, and artist silhouette paths cover missing/failed media consistently across ledgers. VIS-009 is the one high-level mount-condition exception.
- **Contrast/focus:** current readable quiet tokens and product-wide 2px focus grammar are present and reinforced by `frontend/visual-tests/ui-contract.spec.js:139-186`. No independent visible-content contrast root cause was found in the reviewed states.

## Diagnostic boundary

No solution is proposed here. In particular, DECISION findings VIS-003, VIS-012, and VIS-015 must not be silently resolved from implementation preference or generic design advice; they need operator authority because the current handoffs do not conclusively decide the named collision.
