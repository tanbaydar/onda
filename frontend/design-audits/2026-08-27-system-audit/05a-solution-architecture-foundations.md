> Diagnostic audit artifact. It records evidence and proposals; it does not replace the binding Markdown handoffs in `frontend/design-handoffs/` and does not authorize product-behavior changes.

# Onda design audit — foundations solution architecture (LEAD-001–LEAD-007)

Status: diagnostic solution architecture only. No application code, backend behavior, API contract, handoff, product rule, fixture, or repository file was changed.

## Authority and classification guardrail

This document is downstream of:

1. `AGENTS.md` and explicit operator rulings;
2. `frontend/design-handoffs/*.md` as the sole visual authority;
3. the frozen product/navigation contract;
4. `frontend/DESIGN_BRIEF.md`, `frontend/DESIGN_CONTRACT.md`, and `frontend/design-tokens.css` as the consolidated vocabulary;
5. the general `refactoring-ui-for-agents/` principles only where they do not conflict with a higher authority.

`BINDING` findings may be corrected to the already-ruled outcome without a new design choice. `PRINCIPLE` findings permit a system-level correction only where no handoff conflicts. `DECISION` findings remain alternatives; this report does not silently select one.

## Shared foundation proposed by this cluster

The seven problems should not become seven page-specific patches. They converge on four foundations:

1. **Role-bearing visual primitives.** Typography, list/ledger anatomy, controls, and state treatment are selected by explicit component/class roles rather than `h1`, `h3`, `main ul > li`, DOM position, or selector whitelists.
2. **Phase-aware async state.** Initial load, continuation, mutation, and reconciliation are distinct phases. A later request cannot erase earlier successful identity or collection data.
3. **Stable page signatures.** Each route owns a stable identity/content slot across loading, error, empty, sparse, and success states. Local failures remain at the boundary of the action or continuation that failed.
4. **Ruled variants, not copies.** Repeated event rows, collection states, recovery actions, and pagination share primitives. Variants exist only for an authority-backed semantic difference such as Discover's 80×100 ledger versus the standard 56×70 ledger.

The recommended implementation order across all seven findings is: first encode roles and state phases; second migrate global shell and shared primitives; third migrate route surfaces; fourth resolve the operator decisions; fifth perform the production-release parity gate. This keeps work system-first and prevents deployment of another partly governed visual layer.

---

## LEAD-001 — The live site is not running the current ruled design foundation

**Class / severity:** `BINDING` / High
**Principal routes/states:** production R00–R17; strongest in small muted copy, input/menu boundaries, keyboard focus, authentication, recovery, pagination, and essential mobile actions.

### 1. Lead problem

The public site and the audited source do not share one design-foundation version. Production serves older quiet-text and boundary values and omits the ruled focus/target tokens. It also renders an obsolete untouched Register state. Even current source still assigns mobile target size through a manually maintained selector inventory, so deployment drift amplifies a structural weakness rather than being only a one-off release error.

### 2. Technical explanation and exact root evidence

| Root | Technical cause | Exact evidence and affected state |
|---|---|---|
| `VIS-017` (`BINDING`) | The deployed Register bundle is older/different from current source. The live form exposes the Public privacy consequence before a privacy choice; current source does not. | Live R11 untouched Register at 390×844 showed neither radio selected while Public-only copy was visible. Current `frontend/src/pages/RegisterPage.jsx:59-65,74-78` computes `privacyCopy = null` until selection. `frontend/design-handoffs/auth-handoff.md:51-59` prohibits consequence copy before choice. |
| Lead production token evidence (`BINDING`) | Production computes `--text-muted:#8A8A8A` and `--border-strong:#C4C4C4`; the production CSS bundle lacks `--focus-width`, `--target-min`, and `--target-mobile`. | R00–R17 live production, especially navigation, labels, menus, quiet actions, and recovery. Current `frontend/design-tokens.css:58-71` rules `#6E6E6E`, `#949494`, 2px focus, 24px pointer floor, and 44px essential-mobile targets. `frontend/design-handoffs/accessibility-handoff.md:5-23` makes this product-wide and binding. |
| `SPC-006` (`BINDING`) | Even current source expresses target semantics as a selector whitelist. The baseline `button` remains 34px; only enumerated selectors receive 24/44px. Equivalent controls fall through when their class or DOM location differs. | `frontend/src/styles.css:15` sets 34px; `:384-390` lists specific selectors. Classless or generic recovery/pagination controls in `ActivityPage.jsx:107-112,130-134`, `PublicReviews.jsx:67-73,87-107`, `WillBeThereAttendees.jsx:53-59,76-94`, `EditProfilePage.jsx:18-20,107-110`, and `App.jsx:36-41` can remain 34px on R03–R10/R17 mobile states. |

The shared cause is missing **foundation-version enforcement**: design authority exists in source, but neither component semantics nor the release gate prove that the built artifact consumes it.

### 3. Solution proposals, system-first

1. **Create a foundation conformance manifest in the frontend build boundary.** Treat the ruled token set and version as a build contract: exact semantic token names and values, required font files, and required foundation stylesheet inclusion. A small build/test assertion should fail if a production build omits or overrides `--focus-width`, `--target-min`, `--target-mobile`, `--text-muted`, or `--border-strong`.
   - Likely boundary: `frontend/design-tokens.css`, Vite entry/import path, `frontend/visual-tests/ui-contract.spec.js`, and deployment/build configuration.
   - This is not permission to redesign tokens; it is a parity check against already-ruled values.

2. **Replace target-size whitelisting with explicit action-role primitives.** Introduce role-bearing classes/components such as `EssentialMobileAction`, `RecoveryAction`, `PaginationAction`, `MenuAction`, and `CompactPointerAction`. Apply the 44px target through the semantic role; use invisible padding to retain the editorial register as explicitly allowed by the accessibility handoff.
   - Likely boundary: shared button/link primitives or small role classes in `styles.css`; all pagination/recovery/menu/tab consumers R00/R02–R10/R17.
   - Keep the 24px floor separately for non-essential pointer targets.

3. **Add artifact-level production smoke checks.** Run the built app, not the source dev server, at 390×844 and 1280×900. Assert computed token values, representative focus outlines, mobile target rectangles, and untouched Register privacy state. Store evidence by build commit/hash.
   - Likely boundary: visual/contract test suite and release workflow; no product code behavior change.

4. **Release the current governed foundation as one atomic artifact.** Do not cherry-pick only the Register correction or token values. Release token definitions, role primitive migration, and tests together so the public site cannot remain a hybrid of old and new foundation rules.

### 4. NO-GO constraints

- Do not choose new gray, border, focus, or target values. The 2026-08-27 accessibility handoff has already ruled them.
- Do not solve target compliance by visually inflating every control; invisible padding is the ruled mechanism for quiet text/glyph actions.
- Do not turn green into focus, generic action, success, navigation, or branding color.
- Do not alter registration privacy semantics, default selection, backend validation, or API behavior; only the already-ruled conditional consequence presentation may be aligned.
- Do not certify the source tree while ignoring the production bundle. Acceptance must run on the deployed/built artifact.

### 5. REQUIRES OPERATOR DECISION

- **None for the required visual outcome.** Token values, focus grammar, target floors, and the pristine Register state are already binding.
- An operator/engineering release decision is required only for rollout timing and whether the conformance gate blocks deployment or initially reports. That operational choice must not weaken the final pass criteria.

### 6. Measurable acceptance/evidence criteria

- On the production artifact, computed values equal: `--text-muted:#6E6E6E`, `--border-strong:#949494`, `--focus-width:2px`, `--target-min:24px`, `--target-mobile:44px`.
- Every keyboard-operable representative from R00–R17 shows a visible 2px action focus; bordered fields keep a single inset rectangle.
- At 320/390px, every pagination/recovery action in R03–R10/R17 has a measured target at least 44×44px; other pointer targets meet the 24×24px rule or a documented spacing/equivalent exception.
- Pristine `/register` at both widths shows no privacy consequence until Public or Private is selected; selecting each choice shows only its own ruled consequence.
- The artifact test fails when any required token import is removed, any ruled value drifts, or a representative essential action falls back to 34px.
- Evidence records the exact build commit and deployed asset hash so current-source and live parity are auditable.

### 7. Dependencies and sequencing

1. Implement the explicit action-role primitive before migrating selectors.
2. Migrate all current whitelist members and uncovered controls, then remove the whitelist.
3. Add build-artifact tests and Register untouched-state checks.
4. Produce one release candidate and verify at mobile/desktop.
5. Deploy only after source/build/deployment hash parity is proven.

---

## LEAD-002 — Typography is assigned by HTML tag, so display identity leaks into functional and failure states

**Class / severity:** `BINDING` / High
**Principal routes/states:** R03 Search; R05 Activity; R17 generic/entity/profile not found; R07 validation and any future functional surface using ordinary `h1`/`h3`/lists.

### 1. Lead problem

Semantic HTML tags currently double as visual roles. Every `h1`/`h3` receives catalog identity typography, while every direct main list item receives ledger spacing. Functional route labels, system failures, activity rows, and field errors therefore inherit the wrong meaning by default. The issue is not “too many fonts”; it is that the three ruled families are not allocated by semantic role.

### 2. Technical explanation and exact root evidence

| Root | Technical cause | Exact evidence and affected state |
|---|---|---|
| `VIS-004` (`PRINCIPLE`, with a binding not-found anatomy requirement) | The global heading selector treats every H1 as catalog identity; not-found variants are copied, and Profile's copy omits the common recovery route. | `frontend/src/styles.css:10-13` applies display face to all `h1,h3`. Generic `App.jsx:31-39`, Event `EventPage.jsx:173-181`, Venue `VenuePage.jsx:55-63`, and Artist `ArtistPage.jsx:55-63` render bespoke not-found fragments. Profile `ProfilePage.jsx:134-136` has no Return to Discover action. `DESIGN_CONTRACT.md:406` requires a functional H1, explanation, and one route to Discover. R17, both widths. |
| `VIS-005` (`BINDING`) | Search inherits the same display H1. A scoped rule changes only margin, so the route label dominates the actual primary search object. | `SearchPage.jsx:97-103` places H1 before the search field; `styles.css:10-11,58-65` renders the H1 at 30/36px display while the primary field is 18px. Live R03 at 390×844 and 1280×900 confirmed the title is dominant. `search-handoff.md:11-18` rules the bar as the primary object. |
| `SPC-007` (`BINDING`) | Global `main ol/ul > li` rules assign ledger padding/hairlines to all list semantics. Feature CSS then adds another component layer. | `styles.css:30-32` gives every direct main list item 16px vertical padding and sibling hairlines. Activity adds `.activity-row{padding:16px 0}` at `:194-203`, yielding doubled row inset in R05 populated states. Edit Profile error lists at `EditProfilePage.jsx:92,118,121-124` inherit ledger boxes instead of the 6px field-local error relation required on R07. |

The root is a missing **visual-role API**. Markup may remain semantic—one H1, lists for collections, lists for errors where appropriate—but CSS must not infer identity, ledger, or error role from tag name and location.

### 3. Solution proposals, system-first

1. **Define explicit typography roles.** Provide stable roles for `identity-title`, `profile-identity-title`, `functional-page-title`, `row-identity-title`, `section-label`, `functional-copy`, and `review-prose`. Apply font family, scale, weight, tracking, and measure only through those roles.
   - Likely boundary: a role layer in `styles.css`/`design-tokens.css` consumers and small shared heading components/classes.
   - Preserve H1 semantics independently of its visual role.

2. **Remove global display assignment from `h1,h3`.** Default headings should be functional; identity surfaces opt into display. Migrate event, venue, artist, ruled profile identity, Discover city, and row identity to explicit identity classes. Search, Activity, Not Found, Edit Profile, and future system pages opt into functional headings.
   - This turns “identity is rare” into the safe default rather than relying on agents to remember exclusions.

3. **Create one shared NotFoundState.** Inputs: resource label, explanation, and optional privacy/visibility wording. Output: functional H1, concise text, and exactly one Return to Discover action in the normal page ledger.
   - Likely boundary: `App.jsx`, `EventPage.jsx`, `VenuePage.jsx`, `ArtistPage.jsx`, `ProfilePage.jsx`, plus a shared component.
   - Preserve event hidden/not-public wording; do not flatten materially different explanations.

4. **Define collection/list roles.** Create explicit `LedgerList`/`LedgerRow`, `PlainGroupList`, and `FieldErrorList` roles. Remove `main ol/ul > li` visual semantics. Activity owns one ledger padding layer; Edit Profile errors own the auth-field error register.
   - Likely boundary: `styles.css:30-32`, Activity styles, Edit Profile validation markup/classes, and repeated collection components.

5. **Add static and rendered role checks.** A lint/contract test should reject unscoped `font-family:var(--font-display)` on functional surfaces and direct-location list selectors that assign borders/padding. Rendered checks should assert Search's field is the dominant first task object and not-found headings compute to the functional family.

### 4. NO-GO constraints

- Do not remove Rozha One, Gambetta, or General Sans; the three families are authorized. Correct allocation, not font-count reduction, is the goal.
- Do not reduce all display type to functional sans. Event/artist/venue identities, the wordmark, major numerals, row identities, and the explicit profile-header exception retain display roles.
- Do not change semantic heading levels merely to obtain a visual style; every standard page still has one H1 unless a handoff removes it (Home).
- Do not create per-route negative overrides such as `.search-page h1{font-family:...}` while keeping the global leak. The default must become safe.
- Do not turn not-found states into decorative illustrations, cards, or branded error moments.
- Do not convert error lists into ledger blocks or remove field ownership/`aria-describedby` relationships.

### 5. REQUIRES OPERATOR DECISION

- **None for Search, Activity, not-found role, and Edit Profile error/list corrections.** Their authority is explicit.
- If a future surface is proposed as an additional profile-style identity exception, that is a new visual allocation and requires a handoff; it must not be inferred from its `h1` tag.

### 6. Measurable acceptance/evidence criteria

- R03 Search, R05 Activity, and every R17 not-found H1 compute to the functional family/role; the primary Search field remains 18px and is visually dominant.
- Event, venue, artist, row identities, major numerals, and the ruled profile header still compute to the display role.
- Profile not found contains a functional H1, concise explanation, and one Return to Discover action, matching all sibling not-found states.
- Activity rows receive exactly one 16px vertical padding layer; list wrappers add no second layer.
- Edit Profile field errors use 12px danger text 6px below the owning field, with no ledger border or 16px item box.
- Repository CSS contains no tag-wide `h1,h3` identity assignment and no direct-location `main ol/ul > li` spacing/border assignment.
- QA covers long identity names, long functional headings, font-loading fallback, non-Latin text, 320/390/1280, and 200% zoom.

### 7. Dependencies and sequencing

1. Define typography/list role inventory and map every current consumer.
2. Migrate identity surfaces first so removal of global styles cannot regress them.
3. Migrate functional headings and shared NotFoundState.
4. Migrate ledger/plain/error lists; remove global selectors only after coverage.
5. Add static/rendered role tests.

---

## LEAD-003 — Local actions are implemented as whole-surface refetches, erasing context and hierarchy

**Class / severity:** `BINDING` / High
**Principal routes/states:** R06 profile follow/favorite; R08 rating/review/WBT/favorite/like; R09 venue favorite; R10 artist favorite; related continuation states R04–R10.

### 1. Lead problem

An in-place social judgment or relationship change is visually represented as navigation/page replacement. Successful identity and collection data are stored in the same replaceable object as initial-load state. Mutations and later-page requests therefore trigger `loading:true,data:null` or a whole-page retry, which destroys the user's position and the object being changed.

### 2. Technical explanation and exact root evidence

| Root | Technical cause | Exact evidence and affected state |
|---|---|---|
| Lead mutation evidence (`BINDING`) | Event mutation success increments the same retry dependency used by the initial entity effect, which immediately nulls the event. Venue/Artist favorite callbacks and Profile follow use the same pattern. | `EventPage.jsx:42-73` sets `{loading:true,event:null}` on retry; `:75-163` calls `setRetry` after rating/review/WBT changes; `:249` favorite also triggers retry. `VenuePage.jsx:22-46,88`, `ArtistPage.jsx:22-46,84`, and `ProfilePage.jsx:108-136` likewise refetch the whole identity. R06/R08/R09/R10 mutation success and conflict reconciliation. |
| `VIS-007` (`BINDING`) | Continuation failure is stored as page-level error. Activity has no local Retry; Home Retry invokes initial-load logic and clears retained feed. | `ActivityPage.jsx:72-88,104,130-134`; `HomePage.jsx:54-79,89-96`. R04/R05 populated page-two failure at both widths. |
| `VIS-008` (`BINDING`) | Your Circle distinguishes append success but not append failure; its catch writes `data:null`. | `YourCircle.jsx:27-39` appends on success and clears on failure; `:71-107` can then show either successful content or an error, never both. R08 signed-in past event, Circle page-two failure. |
| `SPC-008` (`BINDING`) | Initial and continuation phases share one state object across Home, Activity, shared EventList, Circle, attendees, PublicReviews, and profile tabs. A later request clears data or inserts the failure above the ledger. | `HomePage.jsx:61-79,89-96`; `ActivityPage.jsx:72-86,104-134`; `EventList.jsx:52-63,115-138`; `YourCircle.jsx:27-39,75-107`; `WillBeThereAttendees.jsx:24-36,53-94`; `PublicReviews.jsx:25-38,67-107`; `ProfilePage.jsx:28-60`. R04–R10 loading/page-two/failure. |

The system root is the absence of a **phase-separated request model**. `retry` is doing three incompatible jobs: initial recovery, post-mutation reconciliation, and continuation recovery.

### 3. Solution proposals, system-first

1. **Adopt a phase-aware state shape for every data owner.** Keep immutable/retained successful data separate from `initial`, `continuation`, `mutation`, and `reconcile` state. Each phase owns its pending/error/retry action. A continuation or mutation may update data after success but cannot set previously successful data to null.
   - Likely boundary: shared hook/reducer in `frontend/src/` plus Event, Profile, Home, Activity, EventList, Circle, attendee, and PublicReviews consumers.

2. **Use server-confirmed local mutation commits.** Disable only the originating action while pending. On success, patch the returned/known local fields where deterministic, then perform an optional background reconcile that retains the existing page. On 404/409, reconcile in place. On failure, retain all content and render one local sentence plus Retry beside the action.
   - This avoids claiming success before the server while also avoiding page replacement.
   - For Event, update `viewer_entry`, WBT summary/viewer state, favorite state, or social version independently rather than refetching the complete identity.

3. **Give each mutation an ownership boundary.** Rating/review errors stay in owner entry; WBT errors stay with WBT; favorite cap/commit errors stay with FavoriteControl; follow errors stay in FollowControl; review-like errors stay on the review collection/action. Do not share one generic `actionError` when retries perform different operations.

4. **Standardize continuation slots.** Keep loaded rows mounted; replace the pagination/load-more control slot with `Loading…`, local error + Retry, or exhausted state. Retry repeats only the failed cursor/page request. The list's top position and identity remain fixed.

5. **Preserve scroll/focus.** After server success or failure, focus remains with the initiating control or local recovery. Background reconciliation must not remount the page root, reset the active tab, collapse the editor, or move the user's scroll position.

### 4. NO-GO constraints

- Do not change rating creation, review deletion consequences, WBT, favorite caps, follow privacy/approval, like ownership, or conflict behavior; these are frozen product/backend rules.
- Do not claim optimistic success without an exact rollback path. The recommended baseline is server-confirmed local commit with retained context.
- Do not use a whole-page spinner, skeleton, navigation, or `data:null` reset for an in-place action or continuation request.
- Do not replace a specific mutation failure with a generic account/session error.
- Do not merge unrelated social-version requests into one page-wide busy state; one action must not disable unrelated controls.
- Do not add toast/banner stacks; the handoff requires one local sentence plus Retry.

### 5. REQUIRES OPERATOR DECISION

- **None if implementation keeps server-confirmed semantics and existing copy/behavior.** Retention and local recovery are already binding.
- Choosing optimistic visible success before the server responds would be a new interaction policy; avoid it unless separately ruled. It is not necessary to satisfy this finding.

### 6. Measurable acceptance/evidence criteria

- With Event, Profile, Venue, or Artist mutation requests artificially delayed, the identity H1, media, metadata, community sections, active tab, and loaded rows stay mounted and at the same coordinates.
- The originating control exposes pending/disabled state; unrelated actions remain available unless the backend rule genuinely couples them.
- On simulated mutation failure, successful content remains; one operation-accurate local error and Retry appear; Retry repeats that mutation/reconciliation only.
- On Home/Activity/Profile/EventList/Circle/PublicReviews page-two failure, every previously loaded row remains in the DOM and the error occupies the pagination/continuation slot.
- Retry uses the failed cursor/page and does not reissue the initial request or reset scroll.
- 404/409 reconciliation retains page identity and updates only the stale action/collection state.
- Focus and scroll position survive pending, error, retry, and success in keyboard and touch tests.

### 7. Dependencies and sequencing

1. Define the phase-aware reducer/hook and local RecoveryAction (ties to LEAD-001/005).
2. Migrate shared collection primitives first: EventList, PublicReviews, Circle, attendees.
3. Migrate Event mutations, then FavoriteControl and FollowControl consumers.
4. Migrate Home/Activity/Profile pagination.
5. Add deferred-response and forced-failure browser tests before removing retry-key reload paths.

---

## LEAD-004 — Loading and error branches remove the page's identity instead of preserving its spatial signature

**Class / severity:** `BINDING` / High
**Principal routes/states:** R02 Discover; R06 Profile; R07 Edit Profile; R08 Event; R09 Venue; R10 Artist; R17 resource failures; R00/R01 shell/session transients.

### 1. Lead problem

Initial loading and failure often return a different, reduced page rather than a state of the same surface. The stable identity, section edges, and reading start do not exist until data succeeds. Nested sections then appear independently, while continuation errors may move above retained content. Global session feedback is simultaneously hidden during checking and double-inset during failure.

### 2. Technical explanation and exact root evidence

| Root | Technical cause | Exact evidence and affected state |
|---|---|---|
| `VIS-002` (`PRINCIPLE`) | Session status is mounted but a position selector hides it on public routes. Root resolver separately duplicates the message. | `App.jsx:99` renders `Checking session…`; `styles.css:115` hides `body>div>header>p:not(:first-child)` at all widths. `App.jsx:24-28` shows it only in R01 root resolver. R00/R01 public-route session pending. |
| `VIS-004` (`PRINCIPLE` plus binding anatomy) | Entity not-found fragments fork and use identity typography; Profile omits recovery. | `styles.css:10-13`; `App.jsx:31-39`; `EventPage.jsx:173-181`; `VenuePage.jsx:55-63`; `ArtistPage.jsx:55-63`; `ProfilePage.jsx:134-136`. R17 at mobile/desktop. |
| `VIS-007` (`BINDING`) | Home/Activity continuation failure is rendered as upstream page feedback rather than local continuation state; Home Retry is destructive. | `HomePage.jsx:54-79,89-96`; `ActivityPage.jsx:72-88,104,130-134`. R04/R05 after loaded data. |
| `VIS-008` (`BINDING`) | Circle continuation failure erases the section's successful signature. | `YourCircle.jsx:27-39,71-107`. R08 Circle page-two failure. |
| `SPC-008` (`BINDING`) | Initial and later request states share replacement state across R04–R10. | `EventList.jsx:52-63,115-138`, `PublicReviews.jsx:25-38,67-107`, `WillBeThereAttendees.jsx:24-36,53-94`, and `ProfilePage.jsx:28-60`, in addition to Home/Activity/Circle above. |
| `SPC-012` (`PRINCIPLE`) | Session failure owns a centered 800px container and then repeats page-level gutters internally. | `.session-error-slot` at `styles.css:117` and desktop padding at `:411`; the normal desktop ledger begins at x=240 on 1280px while status begins around x=346. R00 signed-in session failure and protected routes. |
| Lead identity evidence (`BINDING`) | Entity/page components return generic paragraphs before mounting their success anatomy. | `EventPage.jsx:166-192`; `VenuePage.jsx:48-74`; `ArtistPage.jsx:48-74`; `ProfilePage.jsx:134-136`; `EditProfilePage.jsx:107-110`. Discover withholds city/page identity until initial city/request resolution. R02/R06–R10 initial load/failure. |

The system root is that a route's successful component tree is used as the only source of its layout signature. State branches live above that tree instead of inside ruled slots.

### 3. Solution proposals, system-first

1. **Create a stable `PageFrame` contract per surface family.** The frame owns main width, identity start, known functional H1/section labels, and content slots. Loading/error/not-found/empty/success render inside those slots instead of returning a different `<main>`.
   - Catalog detail frame: reserved identity area and section edges for Event/Venue/Artist.
   - Profile frame: profile route context, header/statistics/tab slots where legally knowable.
   - Form frame: Edit Profile heading/auth-column remains while its data slot loads/fails.
   - Ledger frame: Discover city/header and ledger slot, with state inside the ledger.

2. **Use quiet structural placeholders, not a new visual effect.** Preserve successful dimensions/edges with existing background/hairline/space rules and concise `Loading…` status in the owning slot. Avoid shimmer, animated skeletons, generic centered spinners, or placeholder cards. Where identity text is unknown, reserve its established block without inventing content.

3. **Create shared `InitialState`, `ContinuationState`, `EmptyState`, `LocalErrorState`, and `NotFoundState` renderers.** They enforce stable copy punctuation, `role=status`/`role=alert`, local Retry, target roles, and non-destructive continuation behavior while remaining visually quiet.

4. **Give shell status one deliberate slot.** Session checking should be visibly represented once, not mounted-and-hidden or duplicated. Session failure should align with the 800px ledger without applying a second gutter; public content and guest navigation stay usable.

5. **Keep identity and nested section data independently stable.** Once an entity identity succeeds, later statistics/reviews/attendee failures cannot collapse it. Each nested module retains its heading and ruled content slot while its own state changes.

### 4. NO-GO constraints

- Do not invent cards, elevated panels, gradients, shimmer, decorative illustrations, or a dashboard skeleton system.
- Do not block public browsing during session lookup failure; guest navigation and public routes must remain usable.
- Do not duplicate the same session status in header and main.
- Do not show guessed entity names, images, ratings, or private information during loading.
- Do not allow a continuation/mutation state to reuse the full initial frame or erase successful identity/content.
- Do not remove the one functional H1 from standard pages; use role-correct styling.
- Do not add unverified-event UI; the Event handoff explicitly holds it pending a backend ruling.

### 5. REQUIRES OPERATOR DECISION

- **No decision is required to preserve the successful layout signature and use quiet local status; that is binding.**
- Any proposal for animated shimmer, branded loading art, new placeholder color, or new structural wrapper beyond existing successful geometry would be a new visual system and requires a handoff. The recommended solution avoids these choices.
- The auth-footer tension (`VIS-003`) is outside LEAD-004's linked roots and remains unmodified.

### 6. Measurable acceptance/evidence criteria

- At 390×844 and 1280×900, initial loading, error, retry, and success screenshots for R02/R06–R10 share the same main start, identity left edge, content-column edge, and section-slot order.
- A successful entity identity never unmounts during nested loading, continuation, mutation, or retry.
- Session checking is exposed exactly once with polite status semantics; it is not hidden by DOM position.
- Session failure aligns to the normal desktop ledger and contains one local sentence + Retry without double 106px inset.
- All R17 variants share functional H1, explanation, and Return to Discover while preserving resource-specific wording.
- No layout shift caused by state replacement exceeds the dimensions of the local state slot; test assertions can compare bounding boxes before/during/after delayed requests.
- Copy follows `Loading…` for work and sentence periods for stable/error states.

### 7. Dependencies and sequencing

1. Establish typography and state primitives from LEAD-002/003.
2. Correct shell status ownership/alignment.
3. Migrate shared NotFoundState and catalog detail frames.
4. Migrate Profile/Edit Profile/Discover frames.
5. Migrate nested collection slots and add bounding-box regression tests.

---

## LEAD-005 — Repeated event/result/feedback semantics are copied into parallel components, so one meaning has multiple visual grammars

**Class / severity:** `BINDING` / Medium
**Principal routes/states:** R02 Discover overlay/list; R03 Search; R04–R08 feeds/profile/community; R09 Venue; R10 Artist; R17 recovery.

### 1. Lead problem

Repeated jobs—event-result rows, collection state, recovery, pagination—are implemented as parallel local components or raw markup. The same object therefore changes typography, thumbnail/title amplitude, desktop distribution, target size, and recovery vocabulary by entry point. Some differences are valid ruled variants; others are accidental forks.

### 2. Technical explanation and exact root evidence

| Root | Technical cause | Exact evidence and affected state |
|---|---|---|
| `VIS-015` (`DECISION`) | Discover inline search selects `CompactEventResultRow`, a separate button/anatomy with body-size display title, while standard Search uses the integrated event row register. | `SearchResults.jsx:37-49,52-66` forks compact results; `styles.css:79-85` sets title to `--text-body`; standard result name uses `--text-row-title` at `:89-92`. R02 overlay sparse/dense/long/missing-media. Search handoff requires integrated components verbatim for Search results but is ambiguous about overlay amplitude. |
| `SPC-004` (`BINDING`) | Shared compact `EventList` never gains its ruled desktop metadata region. | `EventList.jsx:84-104`; `discover.css:1-31` has no standard-row desktop grid change. Live R10 artist at 1280px showed an 800px row using only 56px thumbnail plus one stacked copy column; date/venue stay left and the right region has no job. Same component affects R03/R09/R10. |
| `SPC-006` (`BINDING`) | Recovery/pagination is restated with raw buttons and an incomplete target selector whitelist. | `styles.css:15,384-390`; examples in Activity, Edit Profile, PublicReviews, attendees, Search, Home, and Not Found. R03–R10/R17 mobile failure and pagination states. |
| `SPC-007` (`BINDING`) | Generic list markup inherits ledger styling even when the semantic role is Activity or validation. | `styles.css:30-32`; Activity `.activity-row` `:194-203`; Edit Profile error lists `EditProfilePage.jsx:92,118,121-124`. R05/R07. |
| Lead component-fork evidence (`BINDING`) | One compact event-result job is spread across `DiscoverEventRow`, `CompactEventResultRow`, `ProfileDiaryRow`, EventList, Home feed, and Favorites; feedback/pagination is restated again in every module. | `discover.css:12-23` (Discover 80×100 row); `styles.css:77-92` (Search variants); `styles.css:430-441` (Profile desktop diary); `EventList.jsx`; `ProfilePage.jsx:19-60`; `PublicReviews.jsx:61-107`; `YourCircle.jsx:71-107`. R02–R10. |

The root is not that every event row must look identical. It is that **variation is encoded by component duplication rather than a governed row/state model**, so agents cannot tell which differences are authoritative.

### 3. Solution proposals, system-first

1. **Define a governed EventRow family with named, authority-backed variants.**
   - `standard-ledger`: 56×70, whole-row target, mobile stacked metadata, desktop identity left + date/venue/judgment right within 800px.
   - `discover-ledger`: 80×100 and Discover-specific lineup/recent judgment rules.
   - `diary-ledger`: standard identity plus Been/review judgment marker and desktop right column.
   - `overlay-result`: pending operator decision below; it must reuse one of the above or become an explicitly ruled variant.
   - A variant defines slots/omissions, not arbitrary local font/padding knobs.

2. **Implement the standard desktop row spread once.** Use an explicit desktop grid with thumbnail, flexible identity, and right metadata/judgment column. Venue/Artist omission rules only remove content; they do not collapse the right-column alignment needed for scanning.

3. **Create shared collection-state primitives.** `CollectionFrame`, `CollectionStatus`, `RecoveryAction`, and `PaginationSlot` own loading/error/empty/continuation vocabulary, retention, target size, and state-slot geometry. Pages supply domain copy and data, not new markup anatomy.

4. **Create explicit list roles.** `LedgerList`, `LedgerRow`, `PlainList`, and `FieldErrorList` prevent the tag/location leak and allow semantic HTML without visual ambiguity.

5. **Centralize role-level evidence.** Story/fixture/visual cases should render each row variant with present/absent/broken media, long title/location, sparse/dense/paginated data, 320/390/1280, and focus. A cross-route test should assert that the same variant has the same computed role tokens everywhere.

### 4. NO-GO constraints

- Do not force genuinely different ruled semantics into one undifferentiated component: Discover's 80×100 ledger is not the standard 56×70 row.
- Do not permit page props that are merely arbitrary pixel values, font sizes, or padding overrides; variants must correspond to named product roles.
- Do not create cards, shadows, rounded containers, or desktop whitespace fillers.
- Do not change whole-row navigation, media fallback grammar, omissions, pagination behavior, or search thresholds.
- Do not reduce the 800px desktop ledger to hide unused width; the standard row must assign that width a scanning job.
- Do not keep raw recovery buttons outside the shared action-role target contract.

### 5. REQUIRES OPERATOR DECISION

- **`VIS-015`: choose the Discover overlay event-result role.**
  - **Option A — reuse `standard-ledger` verbatim (strongest system consistency):** 56×70, row-title amplitude, standard semantics inside the overlay. This most directly follows the integrated-row reuse principle.
  - **Option B — ratify a distinct `overlay-result` variant (strongest compact-overlay fit):** keep 56×70 but explicitly rule smaller title/padding/metadata, document where it may appear, and add its own fixture/acceptance cases.
  - Until ruled, do not silently normalize the live component to either option.
- No decision is needed for the standard desktop row spread, mobile target roles, or list-role leak; those outcomes are already binding.

### 6. Measurable acceptance/evidence criteria

- At 1280px, R03 event results and R09/R10 event ledgers use the full 800px row with identity on the left and aligned date/venue or judgment on the right.
- At mobile widths, each ruled variant retains its exact 56×70 or 80×100 media geometry and expected stacked hierarchy without horizontal scroll.
- The same named EventRow variant has identical computed title, metadata, padding, hairline, fallback, and focus styles across all consumers.
- Every recovery/pagination action is generated by the shared role and measures 44×44px on mobile.
- Continuation failure preserves prior rows and occupies the shared pagination slot.
- CSS has no tag/location-based list border/padding rule; route code has no page-local clone of the shared state anatomy without a documented exception.
- The selected overlay option is written into a handoff before implementation and covered at sparse/dense/long-title/missing-art states.

### 7. Dependencies and sequencing

1. Inventory repeated roles and lock the variant API.
2. Resolve the overlay decision or leave that consumer untouched while migrating unambiguous variants.
3. Implement standard EventRow desktop spread and collection-state/action primitives.
4. Migrate Search, Venue, Artist, Profile, feedback, and pagination consumers.
5. Remove copied selectors/markup only after parity tests pass.

---

## LEAD-006 — Empty and unavailable states keep controls or modules that cannot perform useful work

**Class / severity:** `PRINCIPLE`, with explicit `DECISION` subsets / Medium
**Principal routes/states:** R06 Reviews loading/error/empty and non-owner Favorites; R08 guest Circle and Public loading/error/empty.

### 1. Lead problem

Conditional data/permission state changes the semantic child set, but the surrounding layout and control anatomy remain invariant. Sort controls appear before sortable content exists; a guest-only unavailability module can outrank accessible public content; non-owner favorite rows reserve an owner-only action column.

### 2. Technical explanation and exact root evidence

| Root | Technical cause | Exact evidence and affected state |
|---|---|---|
| `VIS-012` (`DECISION`) | Sort ownership is based on being on a Reviews/Public surface, not on successful non-empty data. | `PublicReviews.jsx:61-77` mounts `SortMenu` before loading/error/empty branches. `ProfilePage.jsx:153-154` mounts Sort from route tab selection outside ReviewsTab, so it cannot know data availability. Live R08 past event with no public reviews at 390×844/1280×900 showed sort directly above `No public reviews yet.` `polish-handoff.md:35-37` blesses the Sort menu as shipped but does not rule per-state visibility. |
| Lead guest-module evidence (`DECISION`) | The Event composition mounts unavailable personalized Circle before accessible Public content for guests. | `YourCircle.jsx:62-68` renders H2 + sign-in sentence; `EventPage.jsx:266-280` places Circle before owner entry/Public. R08 guest past event, especially no-review and dense-Public states. The general hierarchy principle favors usable public evidence, but the detailed Event composition is authoritative enough to require a ruling. |
| `SPC-009` (`PRINCIPLE`) | Favorites row grid is invariant even when JSX omits the owner-only heart. | `ProfilePage.jsx:83-100` mounts `FavoriteControl` only for owner. `.profile-favorite-list > li` (reported at `styles.css:270-278`) remains `56px 210px 44px` at 390px, reserving the 44px action column plus gap for non-owners. R06 other-public profile, long names/text scaling. |

The shared root is the absence of **state-aware composition ownership**. A parent with knowledge of data availability/access must own both controls and the layout variant; conditional children cannot be omitted while their space and hierarchy stay permanent.

### 3. Solution proposals, system-first

1. **Move control ownership into the data-bearing collection frame.** ReviewsTab/PublicReviews should decide sort visibility/disabled presentation from `initial | error | empty | data` state. This enables one ruled state policy instead of rendering sort unconditionally at the route shell.

2. **Add explicit composition states, not CSS guessing.** Examples: `hasSortableResults`, `viewerCanPersonalize`, and `hasRowAction`. Components choose a named layout variant; CSS must not infer behavior from `:empty`, child order, or fixed columns.

3. **Release absent action columns.** Non-owner Favorite rows use a two-column `media + content` layout; owner rows use `media + content + 44px action`. The content column should consume the released width without changing media, hairline, or whole-row navigation.

4. **After operator ruling, encode guest Event hierarchy as a template rule.** If Circle remains before Public, reduce it to the ruled quiet access boundary without dead controls. If Public leads, move the entire Circle module as one slot; do not reorder individual internal pieces ad hoc.

### 4. NO-GO constraints

- Do not make an inert Sort control look active; no sort request should run without a successful non-empty collection.
- Do not add disabled favorite/follow/rating controls to guest Event; the handoff says guest sees no disabled/solicitation owner controls.
- Do not hide accessible Public reviews/attendees behind authentication.
- Do not add a placeholder heart/action column for visual symmetry on non-owner profiles.
- Do not alter private-profile access, guest permissions, review visibility, or backend sorting behavior.
- Do not silently reorder Your Circle/Public against the detailed Event handoff.

### 5. REQUIRES OPERATOR DECISION

- **Sort in loading/error/empty states (`VIS-012`):**
  - Option A: hide Sort until successful non-empty data exists (lowest dead chrome; design-principle preference).
  - Option B: keep it disabled in a stable reserved slot with an explicit disabled grammar (stronger geometric stability, but requires ruling a disabled state).
  - Option C: retain as shipped in all states and explicitly accept inert chrome. This resolves authority but does not address the principle finding.
- **Guest past-event Circle position:**
  - Option A: Public first for guests, then quiet Circle sign-in boundary.
  - Option B: retain Circle first but compress it to one quiet access line within the established slot.
  - Option C: omit the guest Circle module and surface authentication only where a personalized action is attempted. This changes visible composition most and needs explicit approval.
- **No operator decision is required to release the absent non-owner Favorites action column** because no handoff requires preserving it; this is a principle-level conditional layout correction.

### 6. Measurable acceptance/evidence criteria

- For R06/R08 Reviews/Public initial, loading, error, empty, and data states, Sort matches the operator-selected policy and cannot invoke a meaningless request.
- Empty/error text retains its ruled collection slot; changing sort availability does not create a page-wide jump.
- Guest R08 follows one documented Circle/Public order at mobile and desktop; accessible Public content remains reachable without authentication.
- At 320/390px, non-owner Favorite rows contain no empty 44px grid track; content expands by the released action width and long names truncate later than owner rows.
- Owner rows retain the 44px heart target and unchanged whole-row navigation semantics.
- Tests cover guest/signed-in, empty/dense Public, loading/error, owner/non-owner, long title, and 200% zoom.

### 7. Dependencies and sequencing

1. Implement state-aware collection/frame and conditional row-variant APIs without changing disputed presentation.
2. Correct non-owner Favorites composition.
3. Obtain operator rulings for sort and guest Circle order.
4. Encode selected states in the Event/Profile handoff before changing disputed UI.
5. Add fixture-driven cross-state tests.

---

## LEAD-007 — The past-event template does not fully express the product's promised hierarchy inversion

**Class / severity:** `DECISION` / High
**Principal routes/states:** R08 past event, especially guest, insufficient-rating, no-review, sparse/dense-review, mobile/desktop; related missing-art alignment state.

### 1. Lead problem

The product thesis says past events lead toward reviews/ratings while upcoming events lead toward flier/lineup/date/venue/WBT. The current past template still uses title → artwork/meta → Lineup → rating/owner → Circle → owner review → Public. On the live desktop past event, roughly a 365px identity block, full metadata, Lineup, and insufficient-rating message precede community evidence. The detailed Event handoff fixes several parts of this order, so changing it cannot be treated as a generic hierarchy correction.

### 2. Technical explanation and exact root evidence

| Root | Technical cause | Exact evidence and affected state |
|---|---|---|
| Lead order evidence (`DECISION`) | Upcoming/past share one JSX tree and identity grid; `isPast` swaps modules but does not establish two explicit reading templates. | `EventPage.jsx:195-280`: title/art/meta (`:200-219`), Lineup (`:220-229`), rating/WBT (`:230-237`), owner block (`:238-252`), then Circle/attendees (`:254-272`), owner review (`:273`), and Public (`:274-280`). `DESIGN_BRIEF.md:30-40` and `DESIGN_CONTRACT.md:53-54,668-674` promise inversion; `event-handoff.md:13-16,30-34` fixes owner block and responsive identity composition. |
| `VIS-012` (`DECISION`) | Public Sort remains before data availability, adding chrome ahead of an empty/failed review collection. Guest Circle unavailable module also precedes Public. | `PublicReviews.jsx:61-77`; `YourCircle.jsx:62-68`; `EventPage.jsx:266-280`. Live past/no-Public state at both widths. `polish-handoff.md` blesses the menu but not state visibility. |
| `SPC-003` (`BINDING`) | Event community alignment is keyed only to desktop viewport, not to actual ruled art-slot composition. In the observed missing-art state the identity uses the full ledger but community remains indented 192px. | Desktop selector `.event-page>section` at `styles.css:430` always uses `max-width:608px; margin-left:192px`; missing-art identity collapses through `styles.css:428-429`. Live R08 missing-art at 1280px showed identity x=240..1040 and community x=432..1040. `event-handoff.md:32` requires one continuous content-column edge. |

`VIS-012` and `SPC-003` are not the cause of the entire inversion conflict. They expose the same architectural weakness: the Event page is one static DOM sequence with conditional fragments and viewport selectors, rather than explicit state/presence templates whose order and alignment can be reviewed as a unit.

### 3. Solution proposals, system-first

1. **Represent Event composition as two explicit templates.** Define named slots—identity, lineup, judgment summary, owner action, Circle, owner entry, Public—and map them separately for `past` and `upcoming`. Shared components remain shared, but their ordering and emphasis are visible in one configuration rather than implicit conditionals throughout JSX.

2. **Keep alignment coupled to the actual identity template.** Under the already-ruled fixed event-flier treatment, absent/broken art should render `ImageSlot` and preserve the 160×200/80×100 slot. If a future state legitimately has no art slot, community alignment must follow that template's real content edge rather than a viewport-only 192px indent.

3. **Resolve the past-order authority conflict with an explicit operator ruling.** Three coherent directions are available:
   - **Option A — diary-first past template (closest to product thesis):** title/compact identity, judgment summary/owner entry, Circle/Public reviews, then full Lineup/supporting catalog detail. Reviews gain prominence by early placement and measure, not decoration.
   - **Option B — constrained inversion inside the current detailed Event handoff:** retain fixed identity/Lineup order, but move Circle/Public immediately after the identity block and place lower-priority owner/detail material after community where the handoff permits. This needs exact slot-by-slot adjudication because owner block placement is locked.
   - **Option C — ratify the current detailed order as authoritative:** keep present sequence and amend the general thesis/contract so “past inversion” means substituted rating/review modules rather than reviews-first reading order. This resolves the documentation conflict but intentionally accepts the current semantic consequence.

4. **Resolve guest and empty-review states with the LEAD-006 decisions.** The chosen past template must explicitly state guest Circle/Public order and Sort behavior for loading/error/empty; otherwise sparse states will continue to contradict the intended hierarchy.

5. **Validate hierarchy by task-time evidence, not only coordinates.** For each template, record the first dominant identity object, first judgment object, first usable social evidence, and distance/touches to owner entry/Public. This makes “reviews lead” operational rather than subjective.

### 4. NO-GO constraints

- Do not change the Event order until an operator ruling reconciles the general thesis and the detailed Event handoff.
- Do not use one static event template for past and upcoming.
- Do not introduce review/rating chrome on upcoming events; WBT remains the upcoming judgment slot.
- Do not make reviews loud with display type, cards, colored panels, oversized quotes, gradients, or decoration. Their prominence comes from placement, width, and breathing room.
- Do not move or split the owner block in a way that violates its locked past/upcoming contents, confirmation behavior, or relationship to rating state without explicit ruling.
- Do not alter backend event-state, rating gates, review visibility, WBT, like, or ownership rules.
- Do not collapse a fixed 4:5 missing-art slot; the current polish handoff already rules the initial fallback for event identity fliers.

### 5. REQUIRES OPERATOR DECISION

- **Choose A, B, or C for the past-event hierarchy and write the exact slot order into `event-handoff.md`.** This is the core unresolved decision.
- **Choose guest Circle/Public order** and **Sort behavior in loading/error/empty** from LEAD-006; these materially affect whether the selected hierarchy remains true in the most common sparse/guest states.
- If Option A or B moves Lineup or owner entry relative to reviews, the ruling must explicitly name those moves because the current detailed handoff fixes Lineup and owner-block placement.
- No decision is needed for the missing fixed-art fallback or continuous community alignment; those are already binding.

### 6. Measurable acceptance/evidence criteria

- The handoff contains an explicit ordered slot list for both past and upcoming Event templates, including guest, owner-rated, owner-unrated, insufficient-rating, empty-Public, and dense-Public states.
- Rendered R08 DOM/visual order matches that list at 320/390/1280 and 200% zoom.
- In the operator-selected past model, the first usable social/judgment evidence appears at the ruled hierarchy position without card/display/color amplification.
- Upcoming remains flier/lineup/date/venue/WBT-led and contains zero review/rating controls.
- Missing and broken event art use the fixed 4:5 fallback; desktop identity and every community section share the ruled continuous content-column edge with no unexplained 192px dead indent.
- Guest Public content remains usable; unavailable Circle and inert Sort follow the operator-selected policies.
- State transitions—loading, insufficient rating, empty Circle/Public, dense reviews, owner editor—do not reorder slots unexpectedly or erase identity.

### 7. Dependencies and sequencing

1. Obtain the past-template, guest-order, and Sort-state rulings before disputed UI work.
2. Record the ruling in the sole-authority Event handoff with exact slot order/state matrix.
3. Implement the explicit template configuration and fixed media/alignment foundation.
4. Reuse phase-aware collection and state primitives from LEAD-003–006.
5. Verify all R08 states with sparse/dense fixtures and browser evidence at every required viewport.

---

## Cluster sequencing and release gates

| Phase | Work | Blocks |
|---|---|---|
| 1. Role foundation | Typography roles, list roles, action roles, shared state vocabulary | Required before removing global selectors/whitelists |
| 2. State foundation | Phase-aware data model, retained identity/data, local recovery slots | Required before mutation/pagination migrations |
| 3. Shared primitives | EventRow variants, CollectionFrame, NotFoundState, PageFrame | Required before page-by-page cleanup |
| 4. Unambiguous binding migrations | Token/target parity, Search hierarchy, desktop row spread, stable states, local mutation recovery | Can proceed without new design ruling |
| 5. Operator rulings | Discover overlay variant; empty-state Sort; guest Circle/Public; past-event slot order | Must precede disputed presentation changes |
| 6. Production parity | Built-artifact tests, source/build/deployed hash parity, 390/1280 plus 320/768/zoom evidence | Must pass before considering the foundation live |

## Diagnostic boundary

This report proposes implementation architecture and acceptance evidence; it does not authorize changes. In particular, the `DECISION` items under LEAD-005, LEAD-006, and LEAD-007 must be resolved by the operator and recorded in the relevant Markdown handoff before implementation. All proposed corrections must preserve shipped backend behavior and API contracts.
