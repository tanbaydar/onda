> Diagnostic audit artifact. It records evidence and proposals; it does not replace the binding Markdown handoffs in `frontend/design-handoffs/` and does not authorize product-behavior changes.

# Lead semantic and design-mismatch audit

Status: complete diagnostic consolidation. No application, behavior, design-authority, or repository files were changed.

## Audit intent

The user needs every reachable Onda surface and material state to communicate its real job with a stable, professionally governed hierarchy, while preserving shipped product behavior and the binding visual handoffs.

This audit reviews semantic/design mismatch: whether the order, prominence, page anatomy, and state composition tell the truth about the user's job. It does not use “prettier” as a criterion and does not propose a redesign.

## Evidence boundary

- Router, components, state branches, tests, fixtures, CSS, and binding design authority were inspected in the checked-out repository at `c125c4d` (public-beta remediation is commit `71f23f9`).
- Public production routes were inspected read-only at `https://ondaapp.io` at desktop and mobile sizes. No account was created, no authentication data was entered, and no live mutation was performed.
- Protected, owner, destructive, error, and extreme-data states are established from source, tests, and fixtures. They are not claimed as live production screenshots.
- Existing CSS is evidence, not authority. The Markdown handoffs remain the sole visual authority.

## Authority classes

- `BINDING`: contradicts a current handoff, product/navigation contract, frozen shipped rule, or product-wide system ruling.
- `PRINCIPLE`: contradicts the general design memory without contradicting a higher authority.
- `DECISION`: a genuine tension or missing ruling; correction would choose product direction and therefore must be decided by the operator.

## Exhaustive route/state graph

The detailed state matrix is `01-route-state-matrix.md`. The following table is its route-level index; every row is crossed with viewport, session, access, density, media, network, interaction, and preference axes.

| ID | Route/surface | Material destinations and substates |
|---|---|---|
| R00 | Global shell | guest/signed-in nav, account menu, session status/error, logout, footer, mobile/desktop chrome |
| R01 | `/` | session resolver, guest/Home/unverified destinations, legacy city preservation |
| R02 | `/discover` | city states/dropdown, inline search panel, Upcoming/Recent, independent ledgers, continuation |
| R03 | `/search` | recents, one-character silence, five scopes, grouped/single results, keyboard index, continuation |
| R04 | `/home` | auth redirect, all six activity types, grouping, empty/error/dense, pagination |
| R05 | `/activity` | guest boundary, read/unread notifications, mark-read bookkeeping, pagination |
| R06 | `/u/:username[/reviews]` | owner/public/private stub, relationship states, statistics, tabs/sort, diary/reviews/favorites |
| R07 | `/settings/profile` | auth gate, avatar, profile/privacy form, city dropdown, validation/save, follow requests |
| R08 | `/e/:key`, `/events/:key` | canonical/error, past/upcoming inversion, rating/WBT/favorite, Circle/Public, edit and confirmations |
| R09 | `/v/:key`, `/venues/:key` | identity/location/favorite plus two independent event ledgers |
| R10 | `/a/:key`, `/artists/:key` | portrait/favorite plus two independent event ledgers |
| R11 | `/register` | five-field form, unselected/Public/Private, validation/pending/redirect |
| R12 | `/login` | validation, non-enumerating failure, pending/redirect, recovery links |
| R13 | `/verify-email` | code entry, invalid/expired/resend, terminal completion |
| R14 | `/reset-password` | request/error/pending, non-enumerating confirmation, destination actions |
| R15 | `/reset-password/confirm` | direct email entry, code/resend, password/error, terminal completion |
| R16 | `/been` | session transient and guest/owner canonical redirects |
| R17 | `*` and entity/profile not-found | generic and resource-specific stable failures/recovery |

Cross-cutting coverage includes 320/390/767/768/1280/wide widths; 200% zoom; guest/verified/unverified/owner/other-public/private/pending/approved; empty/sparse/normal/dense and pagination; present/absent/broken media; initial/continuation/mutation states; rest/hover/focus/pressed/selected/disabled/pending/success/error; and reduced-motion/forced-color considerations.

## High-level lead problems

### LEAD-001 — The live site is not running the current ruled design foundation

- **Severity:** High
- **Class:** `BINDING`
- **Observed condition:** Production computes `--text-muted:#8A8A8A` and `--border-strong:#C4C4C4`; `--focus-width`, `--target-min`, and `--target-mobile` are absent from the loaded production bundle (`index-BUdU25RU.css`). The repository authority at `frontend/design-tokens.css:58-71` requires `#6E6E6E`, `#949494`, a 2px focus width, a 24px target floor, and a 44px essential-mobile target. Live untouched Register also shows the Public consequence while neither privacy option is selected, although current source correctly omits it.
- **Semantic consequence:** The live system presents supporting text and functional boundaries as visually optional even when they carry navigation, labels, or control identity. Any code-only audit of current HEAD would falsely certify a design users do not receive.
- **Scope:** R00–R17 in production; especially small muted text, inputs, menus, navigation, recovery, and focus states.
- **Authority:** `frontend/design-handoffs/accessibility-handoff.md`; current `frontend/design-tokens.css`.
- **Root-cause links:** `VIS-017` (deployment-specific state drift); `SPC-006` (current source still encodes mobile targets through an incomplete selector inventory, so the deployed omission compounds a live system weakness).

### LEAD-002 — Typography is assigned by HTML tag, so display identity leaks into functional and failure states

- **Severity:** High
- **Class:** `BINDING`
- **Observed condition:** `frontend/src/styles.css:10-13` assigns the display face to every `h1`/`h3`. As a result Search, Activity, generic Not Found, Profile Not Found, and entity Not Found headings receive the same identity channel reserved for event/artist/venue names, approved profile headings, the wordmark, and major numerals. Production Search visibly renders a 36px Rozha `Search` heading immediately above the ruled primary search object.
- **Semantic consequence:** A route label or system failure is presented as catalog identity. On Search, the heading competes with the field even though the handoff names the field as the page's primary object. This makes font usage feel arbitrary despite there being only three deliberate families.
- **Scope:** R03, R05, R17; also any future functional route that adds a plain H1.
- **Authority:** `frontend/DESIGN_BRIEF.md` allocation rule; `frontend/DESIGN_CONTRACT.md` §§2, 3.1; Search surface contract; Refactoring UI hierarchy/type-role rules.
- **Root-cause links:** `VIS-004`, `VIS-005`; `SPC-007` (the same tag-level role leak affects structural spacing through global list selectors).

### LEAD-003 — Local actions are implemented as whole-surface refetches, erasing context and hierarchy

- **Severity:** High
- **Class:** `BINDING`
- **Observed condition:** Event rating/review/WBT/favorite mutations end in `setRetry`, and the Event effect immediately sets `{loading:true,event:null}` (`EventPage.jsx:42-73,75-163`), replacing the entire page with `Loading event…`. Venue/Artist favorite changes do the same (`VenuePage.jsx:22-46,88`; `ArtistPage.jsx:22-46,84`). Profile follow changes trigger a full profile reload (`ProfilePage.jsx:108-136`). Owner favorite removal replaces the Favorites ledger with its loading state (`ProfilePage.jsx:83-99`).
- **Semantic consequence:** A small reversible judgment or relationship action temporarily destroys the identity and social context it modifies. The UI communicates navigation or page replacement when the user performed an in-place state change, producing conspicuous jumps and a prototype-like interaction model.
- **Scope:** R06, R08, R09, R10; related nested pagination/retry states.
- **Authority:** `frontend/DESIGN_CONTRACT.md` §5.14 (avoid layout jumps); accessibility handoff recovery rule; fixed FollowControl/favorite/state grammar; Refactoring UI state-specific hierarchy.
- **Root-cause links:** `VIS-007`, `VIS-008`; `SPC-008`.

### LEAD-004 — Loading and error branches remove the page's identity instead of preserving its spatial signature

- **Severity:** High
- **Class:** `BINDING`
- **Observed condition:** Event, Venue, Artist, Profile, and Edit Profile initial loading/failure branches return generic paragraphs or a reduced fragment before their identity anatomy exists (`EventPage.jsx:166-192`; `VenuePage.jsx:48-74`; `ArtistPage.jsx:48-74`; `ProfilePage.jsx:134-136`; `EditProfilePage.jsx:107-110`). Discover has no city/page identity until its first request resolves. Multiple nested fetches then introduce separate headings and loading lines after the shell appears.
- **Semantic consequence:** The page changes shape and reading start between waiting, failure, and success. Users cannot tell which stable object is loading, and sparse/error states read like unstyled implementation fallbacks rather than states of the same product surface.
- **Scope:** R02, R06–R10, R17; secondarily R00/R01 duplicate session transients.
- **Authority:** `frontend/DESIGN_CONTRACT.md` §§5.14 and 11; artist/accessibility handoffs; Refactoring UI review/state and empty-state rules.
- **Root-cause links:** `VIS-002`, `VIS-004`, `VIS-007`, `VIS-008`; `SPC-008`, `SPC-012`.

### LEAD-005 — Repeated event/result/feedback semantics are copied into parallel components, so one meaning has multiple visual grammars

- **Severity:** Medium
- **Class:** `BINDING`
- **Observed condition:** The same compact event-result job is split between `DiscoverEventRow`, `CompactEventResultRow`, `ProfileDiaryRow`, and page-local feed/favorites anatomy. In particular, Discover's overlay uses `CompactEventResultRow` with a body-size title (`styles.css:77-85`) while the global Search event result uses the ruled row-title register through `DiscoverEventRow` (`discover.css:12-23`). Pagination, loading, error, and Retry anatomy is separately restated in EventList, Profile tabs, PublicReviews, attendee lists, Activity, Edit Profile, and pages.
- **Semantic consequence:** Moving between lists changes title amplitude, padding, control shape, and recovery language even though object meaning and row job are unchanged. The system appears tuned per screen rather than governed by reusable roles.
- **Scope:** R02–R10, especially Discover overlay vs Search, profile ledgers, and entity ledgers.
- **Authority:** `frontend/DESIGN_CONTRACT.md` §§4.2, 5.5, 5.14; Search handoff reuse clause; Refactoring UI systems-before-local-fixes rule.
- **Root-cause links:** `VIS-015`; `SPC-004`, `SPC-006`, `SPC-007`.

### LEAD-006 — Empty and unavailable states keep controls or modules that cannot perform useful work

- **Severity:** Medium
- **Class:** `PRINCIPLE` with one `DECISION` subset
- **Observed condition:** PublicReviews renders Sort before loading/error/empty is known (`PublicReviews.jsx:61-77`); Profile Reviews renders Sort whenever the route is selected, including loading/error/empty (`ProfilePage.jsx:153-154`). Guest Event states place an unavailable Your Circle sign-in module before accessible Public reviews/attendees (`YourCircle.jsx:62-68`; `WillBeThereAttendees.jsx:40-47`; `EventPage.jsx:254-280`).
- **Semantic consequence:** Dead sort chrome implies a collection exists when it does not. On guest Event pages, an unavailable personalized module consumes an earlier hierarchy position than public content the viewer can use, so permission status competes with the actual job.
- **Scope:** R06 and R08; sparse/empty/guest states.
- **Authority:** Refactoring UI empty-state rule to hide/simplify inert controls. Reordering/removing the guest Circle module conflicts with the current detailed event composition and is therefore `DECISION`, not an authorized correction.
- **Root-cause links:** `VIS-012`; `SPC-009` (the same state-insensitive anatomy reserves space for a control that is not mounted).

### LEAD-007 — The past-event template does not fully express the product's promised hierarchy inversion

- **Severity:** High
- **Class:** `DECISION`
- **Observed condition:** Past and upcoming Event identities share title → artwork/meta → Lineup → judgment → owner composition. On a live past Event, the 365px identity block presents title, full metadata, Lineup, and insufficient-rating status before Your Circle and Public. For guests, the unavailable Circle block comes before Public reviews. The general thesis says reviews lead on past events, while the detailed Event handoff fixes several portions of the current order.
- **Semantic consequence:** A past event still reads primarily as a listing/lineup page; diary evidence and community judgment are downstream. The visual distinction between past and upcoming is mostly the substituted data module, not a changed reading path.
- **Scope:** R08 past, especially guest, insufficient-rating, no-review, and dense-review states at desktop and mobile.
- **Authority tension:** `frontend/DESIGN_BRIEF.md` and `DESIGN_CONTRACT.md` §2 vs the more specific current Event handoff/composition. This cannot be changed without an operator ruling.
- **Root-cause links:** `VIS-012`; `SPC-003`. The reports establish availability/control and content-column causes; the ordering tension itself remains the lead-level operator decision.

### LEAD-008 — Activity renders notification semantics as a flat bold string and can display stale unread meaning after success

- **Severity:** High
- **Class:** `BINDING`
- **Observed condition:** `notificationText()` returns one flat sentence and the renderer wraps the entire result in `<strong>` (`ActivityPage.jsx:9-20,123-125`). The Activity ruling requires names to carry 600 while verbs remain normal sentence UI. After `markAllRead` succeeds, local notification objects are not updated; rows keep their original unread classes until another full fetch (`ActivityPage.jsx:42-69,123`).
- **Semantic consequence:** Actor identity, action, and object have the same emphasis, so scanning cannot answer “who did what.” The screen may continue to visually assert “unread” after the server accepted the opposite state.
- **Scope:** R05 read/unread, all notification types, mark-read success/failure.
- **Authority:** `frontend/design-tokens.css` Activity note; `frontend/DESIGN_CONTRACT.md` Activity surface contract; Refactoring UI hierarchy rule.
- **Root-cause links:** `VIS-006`, `VIS-007`; `SPC-006`, `SPC-007`, `SPC-008`.

### LEAD-009 — Permission boundaries use inconsistent page models for equivalent direct-access cases

- **Severity:** Medium
- **Class:** `DECISION`
- **Observed condition:** Guest Home redirects to Discover, guest Settings redirects to Login, guest Activity remains on Activity with a sentence but no local Login action, guest Event keeps public content plus sign-in-gated Circle, and Verify Email can render with a generic destination when no eligible session supplies an address.
- **Semantic consequence:** The same “viewer cannot use this personalized surface” condition may look like navigation, a dead page, an inline module, or an apparently usable auth step. Users cannot build a stable expectation for whether access boundaries preserve context or lead to authentication.
- **Scope:** R04, R05, R07, R08, R13, R16.
- **Authority tension:** Current shipped behavior is frozen and the navigation contract does not normalize every direct-access state. A unified policy is a product decision, not a visual-only repair.
- **Root-cause links:** `VIS-002`, `VIS-003`; no independent spacing finding adjudicates the permission-policy difference. `SPC-002` and `SPC-012` are inherited shell constraints, not causes of this product-rule tension.

### LEAD-010 — Feedback ownership is fragmented between global, page, section, and action layers

- **Severity:** Medium
- **Class:** `PRINCIPLE` plus local `BINDING` violations
- **Observed condition:** Root session checking appears both in the header and Landing main (`App.jsx:24-29,101`); session failure owns a global alert while some routes also render their own account-dependent failure. Continuation and mutation errors sometimes use local Retry and retain content, sometimes become a plain alert with no Retry (Activity load more), and sometimes convert Retry into a full initial reload (Home continuation). Nested Event sections separately own overlapping social-action error text.
- **Semantic consequence:** Users see duplicate status, recovery actions with different scope, and no consistent visual answer to “what failed?” or “what will Retry replace?” This makes feedback feel appended by implementation layer rather than designed around the user's current task.
- **Scope:** R00–R10, especially R01, R04, R05, R08.
- **Authority:** accessibility handoff local recovery rule; `DESIGN_CONTRACT.md` §5.14; Refactoring UI state-specific hierarchy/review rules.
- **Root-cause links:** `VIS-001`, `VIS-002`, `VIS-007`, `VIS-008`, `VIS-014`; `SPC-006`, `SPC-008`, `SPC-012`.

### LEAD-011 — The responsive contract activates desktop geometry before the geometry can fit

- **Severity:** Critical at Profile; High system-wide
- **Class:** `DECISION` at the shared breakpoint, with `BINDING` failures in components whose handoffs already require fit
- **Observed condition:** At 767px the main content is about 719px wide; at 768px, one additional viewport pixel activates 106px side gutters and reduces usable content to about 556px. Discover controls then cross the ledger edge. Profile statistics produce document-level horizontal overflow at ordinary values, and the ruled four-digit social-count fixture cannot fit the 320px identity row. Search's five 44px scopes and Event's fixed StarInput also have no ruled narrow recomposition that can satisfy all current dimensions simultaneously.
- **Semantic consequence:** The interface becomes less stable as the viewport grows, and exact supported widths expose clipped, hidden, or gutter-breaking content. This is a missing responsive system tier, not a collection of isolated component widths.
- **Scope:** R00, R02–R10, R17; strongest at R03, R06, and R08; exact 320/767/768 and 200% zoom.
- **Authority:** `frontend/DESIGN_CONTRACT.md` width/no-overflow/QA rules; profile/statistics, Search, Event, and accessibility handoffs; responsive monotonicity principles. Choosing a new breakpoint/gutter/intermediate composition requires an operator ruling, while already-specified no-overflow violations remain binding defects.
- **Root-cause links:** no independent visible-content root cause; `SPC-001`, `SPC-002`, `SPC-005`, `SPC-010`, `SPC-013`.

### LEAD-012 — Conditional content does not recompose its layout, creating unowned whitespace and false hierarchy

- **Severity:** High
- **Class:** `BINDING` for missing event artwork; `PRINCIPLE` for non-owner Favorites
- **Observed condition:** An upcoming event with absent artwork drops the ruled fixed identity slot, but its desktop community sections still keep the 192px artwork-column indent. A non-owner Favorites row omits the owner-only heart while its grid permanently reserves the 44px action column plus gap.
- **Semantic consequence:** Whitespace does not identify a group, preserve a measure, or create hierarchy; it marks where a conditional child would have been. Useful public content is compressed or truncated to protect an empty column, making the page visibly implementation-shaped.
- **Scope:** R06 non-owner Favorites; R08 upcoming missing-art state at mobile and desktop; long names and zoom amplify both.
- **Authority:** fixed media fallback and Event alignment rulings; Refactoring UI functional-whitespace and conditional-composition principles.
- **Root-cause links:** `VIS-009`; `SPC-003`, `SPC-009`.

### LEAD-013 — Desktop ledgers spend width without assigning it a scanning job

- **Severity:** High
- **Class:** `BINDING`
- **Observed condition:** Shared compact Event rows on Search, Venue, and Artist span the ruled 800px desktop ledger but retain the mobile thumbnail-plus-stacked-copy anatomy. Date and venue do not form the required right-hand metadata column, so much of the row remains visually unused.
- **Semantic consequence:** The whitespace is not calm or luxurious because it does not separate or align information; it simply enlarges a mobile row. Repeated data becomes slower to compare, and the desktop surface reads as unfinished.
- **Scope:** R03 Event results, R09 Venue ledgers, R10 Artist ledgers; sparse/dense/paginated/long-metadata states.
- **Authority:** Search handoff's verbatim EventListRow and desktop-spread ruling; Artist/Venue shared-ledger rules; design-token row grammar.
- **Root-cause links:** `VIS-015` (the related component fork in Discover search); `SPC-004`.

### LEAD-014 — Component roles are encoded through tag selectors and selector inventories instead of governed primitives

- **Severity:** High
- **Class:** `BINDING` plus cross-cutting `PRINCIPLE`
- **Observed condition:** Global `h1/h3` rules assign identity typography; global `main ul/ol > li` rules assign ledger padding and hairlines; a long whitelist decides which mobile actions reach 44px. Activity therefore double-pads rows, Edit Profile turns field errors into ledger items, functional headings inherit catalog identity, and multiple recovery/pagination actions remain 34px.
- **Semantic consequence:** Correctness depends on incidental markup and remembering to append every new component to a selector list. New screens inherit wrong visual meaning by default, which is the structural condition that makes later agent work drift.
- **Scope:** R03–R10, R17 directly; future routes and new states share the blast radius.
- **Authority:** product-wide type allocation, Activity/Edit Profile anatomy, mobile target ruling, and systems-before-local-fixes design principles.
- **Root-cause links:** `VIS-004`, `VIS-005`, `VIS-010`; `SPC-006`, `SPC-007`.

## Coverage ledger

| Route class | Semantic lead reviewed | Visible-content root report | Spacing root report |
|---|---:|---:|---:|
| R00 | yes | yes | yes |
| R01 | yes | yes | yes |
| R02 | yes | yes | yes |
| R03 | yes | yes | yes |
| R04 | yes | yes | yes |
| R05 | yes | yes | yes |
| R06 | yes | yes | yes |
| R07 | yes | yes | yes |
| R08 | yes | yes | yes |
| R09 | yes | yes | yes |
| R10 | yes | yes | yes |
| R11 | yes | yes | yes |
| R12 | yes | yes | yes |
| R13 | yes | yes | yes |
| R14 | yes | yes | yes |
| R15 | yes | yes | yes |
| R16 | yes | yes | yes |
| R17 | yes | yes | yes |

## Root-report index

- Rendered elements, copy, typography, color, imagery, controls, and visible state grammar: `03-visible-content-root-causes.md` (`VIS-001`–`VIS-017`).
- Whitespace, grouping, rhythm, measure, density, containers, alignment, responsive composition, and state-slot geometry: `04-spacing-root-causes.md` (`SPC-001`–`SPC-013`).

This lead report remains diagnostic. It deliberately does not select solutions for `DECISION` items or authorize behavior changes.
