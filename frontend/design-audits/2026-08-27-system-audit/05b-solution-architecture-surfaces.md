> Diagnostic audit artifact. It records evidence and proposals; it does not replace the binding Markdown handoffs in `frontend/design-handoffs/` and does not authorize product-behavior changes.

# Surface solution architecture — LEAD-008 through LEAD-014

Status: solution architecture only. No application code, handoff, product behavior, API contract, fixture, or repository file was changed.

## Authority and implementation posture

- `BINDING` findings can be corrected only within the current handoffs and frozen product behavior. The proposals below identify a compliant implementation boundary; they do not authorize adjacent behavior changes.
- `PRINCIPLE` findings may be corrected when the proposal does not contradict a handoff or product rule.
- `DECISION` findings are options for an operator ruling. They must not be implemented, or silently resolved through CSS, before that ruling names the selected behavior/composition.
- Existing CSS is evidence, not authority. The Markdown files in `frontend/design-handoffs/` remain the sole visual authority.

## LEAD-008 — Activity flattens notification meaning and can retain stale unread styling

**Classification / severity:** `BINDING` / High.

### 1. Lead problem

Activity does not visually distinguish the actor from the action, and a successful mark-all-read request does not update the locally rendered read state. A row can therefore be semantically flat before the request and visibly false after it.

### 2. Technical explanation

- `VIS-006`: `notificationText()` in `frontend/src/pages/ActivityPage.jsx:9-20` serializes actor, verb, object, and punctuation into one string. The renderer at `ActivityPage.jsx:120-126` wraps that whole string in `<strong>`. The rules in `frontend/src/styles.css:194-199` can only change the weight of that single strong node, so the Activity handoff's actor-name `600` / verb-normal distinction is structurally impossible.
- The same row derives `.read` or `.unread` only from `notification.read_at` at `ActivityPage.jsx:123`. `markAllRead()` at `ActivityPage.jsx:62-69` clears only its request state on success; it never updates `state.results`. The server can accept the mutation while every mounted notification keeps its previous unread class.
- `VIS-007` and `SPC-008`: continuation failure is stored as the string-only `actionError` at `ActivityPage.jsx:72-86`, then rendered above the ledger at `:104`, while the originating Load more control remains below it at `:130-134`. This separates failure meaning from the operation that failed and shifts the ledger.
- `SPC-006`: Activity's Retry and classless Load more controls are not guaranteed the ruled 44px mobile recovery/pagination target because `frontend/src/styles.css:384-391` governs target size through a selector whitelist.
- `SPC-007`: direct-list styling in `frontend/src/styles.css:31-32` and `.activity-row` styling at `:194-203` both add row treatment. The result is a ledger item plus an inset component, including approximately 32px lateral inset per side rather than one continuous Activity ledger.
- Affected evidence states are R05 read/unread, every notification presenter type, sparse/dense lists, mark-read pending/success/failure, and pagination pending/failure at mobile and desktop widths.

### 3. Solution proposals, system first

1. **Create a semantic notification presenter, not a text formatter.** Replace `notificationText()` with a presenter that returns role-bearing data such as `{ actorLabel, actionLabel, objectLabel, destination }`. Render separate nodes inside a dedicated `NotificationSentence` primitive: actor identity receives the ruled weight; verb/object remain sentence UI. Keep current notification types, copy, punctuation, and destinations unchanged.
   - Likely boundary: a presentation module adjacent to `homeFeedPresentation.js`, plus `NotificationSentence` or equivalent in the Activity component layer.
   - The primitive should make read-state styling an explicit variant rather than deriving meaning from nested `<strong>` selectors.
2. **Model mark-all-read as an in-place bookkeeping mutation.** On successful POST, immutably set each mounted notification's local read marker to the accepted state, without refetching or remounting the ledger. On failure, retain the rows and expose the existing local recovery operation.
   - Likely boundary: Activity page state/reducer only. No API or notification contract change is needed.
3. **Adopt a phase-aware collection state for Activity.** Separate `initial`, `continuation`, and `readBookkeeping` state. Continuation pending/error belongs in a stable slot where Load more sits; prior rows stay mounted. Read-bookkeeping error remains a distinct local sentence + Retry because it retries a different operation.
   - Likely boundary: shared collection-state helper/primitive if introduced under LEAD-010; otherwise Activity-local reducer as the first migration.
4. **Render Activity through governed primitives.** Use one `Ledger`/`LedgerRow` treatment, one `PaginationRecovery` control, and one sentence primitive. Remove dependence on generic `main ol/ul > li` styling and the mobile selector whitelist as part of the LEAD-014 migration.

### 4. NO-GO constraints

- Do not change notification types, API payloads, automatic mark-all-read timing, row destinations, or navigation behavior without an operator ruling.
- Do not bold the whole sentence, use unread color as the actor hierarchy, or invent a new emphasis color. Names carry weight; verbs remain normal sentence UI.
- Do not refetch or clear the full Activity ledger after mark-all-read success.
- Do not move a continuation error to the page top, remove already loaded rows, or make Retry perform an initial reload.
- Do not fix target size or double padding by adding Activity to another selector whitelist or by stacking compensating negative margins.

### 5. REQUIRES OPERATOR DECISION

No operator decision is required to correct the identified binding defects while preserving current copy, behavior, and destinations. An operator ruling would be required only to change when notifications become read, add per-row read controls, change notification copy, or introduce a new visual unread signifier beyond the current handoff.

### 6. Measurable acceptance/evidence criteria

- For every supported notification type, DOM evidence exposes separate actor and action nodes; computed actor weight is `600`, while verb/object sentence text is normal. Read state recedes according to the Activity ruling without flattening the roles.
- After a mocked successful `read-all` request, every mounted row immediately reports the local read variant without a new notifications GET and without changing row geometry.
- After a mocked mark-read failure, rows remain mounted and the local Retry invokes only `read-all`.
- After a page-two failure, existing row IDs and vertical positions remain stable; one local error sentence plus Retry occupies the former pagination slot.
- At 320px and 390px, Retry and Load more measure at least 44×44px; Activity has no document overflow and no double ledger inset.
- Keyboard focus remains visible on every row and recovery action; read/unread meaning is not conveyed by color alone.

### 7. Dependencies and sequencing

1. Define role-bearing typography, ledger, recovery, and collection-state primitives under LEAD-014/LEAD-010.
2. Introduce the structured presenter with fixture coverage for all notification types.
3. Move Activity to phase-aware state and local success updates.
4. Migrate row and recovery styling, then verify read, continuation, error, keyboard, mobile-target, and dense-list states.

---

## LEAD-009 — Equivalent permission boundaries use different page models

**Classification / severity:** `DECISION` / Medium.

### 1. Lead problem

Equivalent direct-access conditions do not share a predictable access-boundary policy. Guest Home redirects to Discover, Settings redirects to Login, Activity stays in place with non-actionable copy, Event preserves public content with a gated Circle module, and Verify Email can expose a generic destination state.

### 2. Technical explanation

- R04 Home applies the shipped `homeAccessRedirect()` and navigates a guest away from the requested personalized surface.
- R07 Settings uses an authentication redirect to Login; R16 legacy Been also resolves through session-dependent redirects.
- R05 Activity returns `<main><h1>Activity</h1><p>Sign in to view your activity.</p></main>` at `frontend/src/pages/ActivityPage.jsx:94-99`, preserving the route but providing no local Login action.
- R08 Event keeps its public identity and public social content while `frontend/src/components/YourCircle.jsx:62-68` renders an inline sign-in boundary for the personalized module.
- R13 Verify Email is mounted from `frontend/src/App.jsx:132` with `email={session.user?.email}`; direct entry can therefore render an auth step without a session-supplied destination.
- `VIS-002` shows that session-checking feedback in the global shell is emitted at `App.jsx:99` but hidden by `frontend/src/styles.css:115`, while root resolver status separately appears at `App.jsx:24-28`. This makes the transition into permission resolution less legible.
- `VIS-003` is a separate `DECISION` tension: the shell mounts a footer globally at `App.jsx:159-164`, but `frontend/src/styles.css:373` hides it for R11-R15. Current handoffs restore persistent navigation/account chrome but do not explicitly rule the footer.
- `SPC-002` and `SPC-012` affect how the shell and account-status recovery align, but they do not adjudicate the permission behavior. They must not be used as visual pretexts to change routing.

### 3. Solution proposals, system first

1. **Obtain an operator ruling for an access-boundary matrix before implementation.** The ruling should specify, for every personalized surface, whether direct guest access (a) preserves the destination and presents an auth action, (b) redirects to Login with an approved return destination, (c) redirects to a public default, or (d) preserves public content and gates only the private module.
2. **After the ruling, encode it as one route/access policy module.** Route components should consume named outcomes such as `redirect-login`, `redirect-public-default`, `inline-page-boundary`, or `inline-module-boundary`; they should not each invent prose and routing independently.
   - Likely boundary: route-policy/presentation module near `landing.js` and `primaryNavigation.js`, with a shared `AccessBoundary` surface primitive.
   - Preserve backend access control. This governs client presentation only after behavior is ruled.
3. **Give every preserved boundary a complete anatomy.** If the ruling keeps the viewer on the route, render functional heading, concise explanation, and an approved Login action. If it is module-local, retain accessible public content and place the boundary only in that module's slot.
4. **Resolve the auth-footer question independently.** Record whether R11-R15 retain or suppress the provenance footer, then encode that decision as explicit shell configuration rather than `:has(main.auth-page)`.
5. **Make session resolution visible through a governed shell-status slot.** This is a presentation correction under VIS-002 and does not itself alter any permission destination.

### 4. NO-GO constraints

- Do not normalize redirects, add `return_to`, change auth destinations, alter verification eligibility, or expose private data without an explicit operator ruling naming those behavior changes.
- Do not infer a universal “redirect everything to Login” or “always preserve context” policy from generic design principles.
- Do not treat Event's public-plus-gated-module model as authority for fully private pages, or vice versa.
- Do not use CSS to hide a route state that remains reachable in the router.
- Do not merge the footer decision with access-policy remediation; they are separate rulings.

### 5. REQUIRES OPERATOR DECISION

The operator must decide:

1. The guest direct-access outcome for R04 Home, R05 Activity, R07 Settings, and R16 Been.
2. Whether a redirect to Login preserves and later restores the requested destination.
3. Whether R13 direct Verify Email without a known eligible address is a valid page state, a redirect, or an inline boundary.
4. Whether authentication routes R11-R15 show the global provenance footer.
5. Whether the current R08 public-content-plus-gated-Circle composition remains the exception or becomes a reusable policy for mixed-access pages.

### 6. Measurable acceptance/evidence criteria

- A checked-in, operator-approved matrix covers R04, R05, R07, R08, R13, and R16 for session checking, guest, verified, unverified, and session-failure states.
- Route tests assert the exact ruled outcome and destination for each matrix cell; no route owns an unapproved one-off redirect.
- Every preserved page boundary contains a usable auth action with visible focus and a 44px mobile target; every module boundary leaves public content mounted.
- Session lookup failure still permits public browsing and offers only the session lookup Retry required by the accessibility handoff.
- Footer behavior on R11-R15 is explicit in shell configuration and covered by visual tests, not inferred from descendant markup.

### 7. Dependencies and sequencing

1. Operator rules the access matrix and footer policy.
2. Architect the shared policy module and boundary primitive without changing backend enforcement.
3. Migrate routes one policy class at a time, adding redirect/context tests.
4. Apply LEAD-010 shell feedback and LEAD-014 primitive work so preserved boundaries use stable feedback, typography, and targets.

---

## LEAD-010 — Feedback ownership is fragmented across global, page, section, and action layers

**Classification / severity:** `PRINCIPLE` cross-cutting, with local `BINDING` recovery violations / Medium.

### 1. Lead problem

The interface has no stable answer to which layer owns loading, failure, and Retry. The same operation phase can produce duplicate shell/page status, page-level alerts, destructive full reloads, displaced continuation errors, or local ad-hoc copy.

### 2. Technical explanation

- `VIS-001`: `frontend/src/App.jsx:46-78` stores session bootstrap and logout mutation failure in the same `session.error`. `App.jsx:101-105` always renders `Account status could not be loaded.` and makes Retry rerun session lookup, even when Logout failed. `AccountMenu.jsx:31-38` receives no mutation pending/error state.
- `VIS-002`: root session status is duplicated between `LandingPage` (`App.jsx:24-28`) and the header (`App.jsx:99`), while `frontend/src/styles.css:115` hides the header instance on all viewports.
- `VIS-007` / `SPC-008`: Home writes continuation failure into initial `state.error` at `HomePage.jsx:70-79`; its Retry at `:89-96` increments the full-load dependency and clears successful results. Activity renders a page-top continuation string without Retry.
- `VIS-008` / `SPC-008`: `YourCircle.jsx:27-39` correctly appends success but sets `data:null` on any failure. Shared detail `EventList`, PublicReviews, WillBeThereAttendees, Profile ledgers, and follow requests repeat the initial/continuation state collapse identified in SPC-008.
- `VIS-014`: Discover inline search uses `Search failed.` + `Try again.` at `DiscoverSearch.jsx:52-57`, while Search uses the ruled `Retry` vocabulary at `SearchPage.jsx:105-110`.
- `SPC-006`: recovery/pagination control dimensions depend on membership in `frontend/src/styles.css:384-391`, so equivalent feedback actions have different mobile targets.
- `SPC-012`: `.session-error-slot` at `frontend/src/styles.css:108-118,395-415` is both max-width centered and padded with page gutters, creating an unexplained second left edge on desktop.
- Scope is R00-R10, especially session bootstrap/logout, R01 resolver, R04/R05 continuation, and R08 nested social modules.

### 3. Solution proposals, system first

1. **Define one feedback-state model by user-visible phase and operation identity.** Minimum phases: `initial`, `continuation`, `mutation`, and `bookkeeping`; minimum fields: operation key, pending, error, retry function, retained-content policy, and owning slot. Endpoint identity alone is insufficient.
   - Likely boundary: a small collection/action state abstraction plus render primitives, not a global toast system.
2. **Create scoped primitives with fixed anatomy.** Suggested roles are `InitialState`, `ContinuationState`, `ActionFeedback`, and `ShellStatus`. Each implements the ruled ellipsis, one local sentence + `Retry`, appropriate `aria-live`/`role`, and 44px mobile recovery target. A shared primitive may accept copy, but copy remains operation-specific.
3. **Separate session bootstrap from account mutations.** `session.lookup` owns the persistent shell line and lookup Retry. `logout` owns menu-local pending/error and logout Retry. A logout failure must keep the signed-in shell and menu context; it must not mutate the session lookup channel.
4. **Use retained-data collection state.** Initial failure may occupy the collection's initial slot; continuation pending/error must preserve current items and replace only pagination chrome. Mutation/bookkeeping failure must preserve the affected object and keep Retry beside the initiating action.
5. **Standardize the recovery vocabulary.** Use `Retry` for the action; stable errors end with a period; progress labels use an ellipsis. Migrate Discover inline search and every local fork.
6. **Align the shell status to the global ledger.** The shell-status container should own either width or gutters, not both. Implement through the shared container primitive established under LEAD-011/014.
7. **Migrate by operation family, not route cosmetics.** Recommended first families: session lookup/logout; cursor collection continuation; relationship/social mutations; nested Event community collections.

### 4. NO-GO constraints

- Do not use a global banner/toast for every failure. The accessibility ruling requires local recovery and forbids stacks of banners/cards.
- Do not clear successful content for continuation, relationship-action, or read-bookkeeping failure.
- Do not let one Retry invoke a different operation than the failed operation.
- Do not merge unrelated error channels into one boolean/string, and do not standardize copy so aggressively that it stops naming the failed task.
- Do not add selectors to the mobile target whitelist as the system fix.
- Do not alter API behavior, retry policy, auth-expiry behavior, or shipped mutation semantics under a presentation refactor.

### 5. REQUIRES OPERATOR DECISION

No operator ruling is needed for the binding recovery corrections, operation-specific ownership, stable slots, or vocabulary already named by the handoffs. A ruling is required before introducing new global notification behavior, automatic retries, optimistic business-state commits not already implied by accepted responses, or changing the destination after auth expiry.

### 6. Measurable acceptance/evidence criteria

- An operation/slot inventory covers session lookup, logout, initial loads, every cursor continuation, favorite/follow/like/WBT/rating mutations, and mark-read bookkeeping across R00-R10.
- For each forced continuation failure, previously rendered item IDs stay mounted and in the same order; the message + Retry occupies the pagination slot; Retry repeats only the failed cursor request.
- Forced logout failure leaves session/user chrome intact and renders logout-specific local feedback; session lookup Retry is absent unless lookup itself failed.
- No screen simultaneously emits duplicate `Checking session…` messages; a single visible shell/resolver status has a stable slot.
- All progress copy ends in an ellipsis; all recovery controls read `Retry`; all recoveries meet 44×44px at 320/390.
- The desktop account-status line aligns to the same ledger edge as page content and creates no nested gutter.

### 7. Dependencies and sequencing

1. Establish LEAD-014 feedback/action primitives and LEAD-011 container ownership.
2. Separate App session lookup and logout state first because they affect every route.
3. Introduce phase-aware collection state and migrate Home/Activity as reference implementations.
4. Migrate Event/Profile/Venue/Artist nested ledgers and mutations.
5. Run a fault-injection matrix for initial, continuation, mutation, bookkeeping, auth-expiry, and Retry states at mobile/desktop.

---

## LEAD-011 — Desktop geometry activates before it can fit

**Classification / severity:** `DECISION` for the shared responsive tier; `BINDING` for ruled fit/no-overflow failures / Critical on Profile, High system-wide.

### 1. Lead problem

At 768px the system abruptly reduces usable content width and activates layouts that need more room. Exact supported widths and extreme fixtures then produce bleed, clipped controls, dead gutters, or document-level horizontal scrolling.

### 2. Technical explanation

- `SPC-002`: `frontend/src/styles.css:385-415` changes global gutters at 768px. The content measure falls from about 719px at 767 to about 556px at 768. Discover's control pair (`frontend/src/discover.css:25-30`) then crosses the ledger edge. This is a non-monotonic container contract with no intermediate tier.
- `SPC-001`: `.profile-statistics` at `frontend/src/styles.css:443-451` combines negative lateral margins, max-content children, and fixed 48px gaps. At 768px it measures a 762px scroll width inside a 744px band and causes document width 774px before dense fixtures.
- `SPC-013`: `.profile-social-counts` at `frontend/src/styles.css:234-240` is forced onto one line inside an approximately 184px identity column at 320px. Even `0 FOLLOWERS 0 FOLLOWING` overflows that column; the ruled `1204`/`1048` private fixture is necessarily worse.
- `SPC-005`: Search's five single-line scopes need 316px inside a 272px content width at 320px. The fifth scope is initially out of view, while the handoffs simultaneously require side-by-side scopes, 24px gaps, 44px targets, and narrow no-overflow.
- `SPC-010`: Event StarInput's fixed stars, hit geometry, adjacent numeral, and nowrap row produce 280px of content in a 272px ledger at 320px. The event handoff binds both star geometry and adjacent selected value.
- Scope includes R00 and R02-R10/R17 at exact 320, 767, 768, 1280, wide desktop, 200% zoom, long/localized content, dense statistics, and four-digit counts.

### 3. Solution proposals, system first

1. **Obtain an operator ruling for the responsive tier model.** The ruling must choose where desktop gutters/compositions begin and whether an intermediate tier exists. Viable system directions are:
   - delay desktop gutters/compositions until the ruled 800px ledger plus gutters actually fits;
   - introduce an intermediate fluid-gutter tier while retaining 768 as a named breakpoint;
   - keep 768 but explicitly keep selected components in their narrow composition until their own container has sufficient inline size.
   These are mutually meaningful product/layout choices; do not select one silently.
2. **Centralize container geometry.** After ruling, implement one `PageLedger`/container primitive with monotonic usable width and explicit tokens for narrow, intermediate, and wide gutters. Components should respond to available container width, not duplicate viewport assumptions.
3. **Resolve component collisions within their authority:**
   - Profile statistics: preserve the ruled narrow three-row composition until the full five-item desktop strip fits; remove negative-margin/max-content overflow mechanisms. Exact transition depends on the responsive ruling.
   - Profile social counts: introduce an authority-compliant narrow reflow/wrap for the two count-label pairs while keeping them inside identity and before FollowControl. Do not abbreviate or hide counts.
   - Search scopes: operator selects a ruled narrow composition—e.g. a compressed but still accessible single row, an explicitly disclosed horizontal scroller, or another stated composition. Current implicit clipping is not acceptable.
   - StarInput: operator selects whether the chosen numeral wraps/moves, star geometry adapts, or the content gutter/composition changes at 320. Preserve ten-step semantics and 44px hit targets.
4. **Add a reusable fit harness.** Render every governed primitive at 320/390/767/768/1280/wide, 200% zoom, long labels, four-digit values, and dense fixtures; assert both document and component scroll widths.

### 4. NO-GO constraints

- Do not lower essential mobile targets below 44px, hide Search scopes, abbreviate ruled count labels, remove the selected rating numeral, or alter rating steps to force fit.
- Do not mask document overflow with `overflow-x:hidden`; it conceals inaccessible content and does not solve geometry.
- Do not make component-specific breakpoint exceptions before the shared tier is ruled, unless a current handoff already explicitly supplies that component's valid composition.
- Do not replace 4-digit or dense fixtures with easier values.
- Do not use negative margins or transform offsets to keep an element visually inside while its scroll geometry still exceeds the ledger.

### 5. REQUIRES OPERATOR DECISION

The operator must decide:

1. The global breakpoint/gutter/intermediate-tier policy that resolves the 767→768 content-width cliff.
2. Search scope behavior when five 44px targets plus ruled gaps cannot fit at 320px.
3. StarInput's narrow placement/geometry compromise while preserving value, ten-step semantics, and target size.
4. Whether component transitions are viewport-based or container-based where the handoffs do not already decide.

The no-horizontal-overflow fixes for Profile statistics and four-digit social counts are binding; their implementation should follow, not pre-empt, the shared tier ruling.

### 6. Measurable acceptance/evidence criteria

- Usable ledger width is monotonic from 320 through wide desktop; increasing viewport width by 1px never removes content width without an explicitly documented component transition.
- `documentElement.scrollWidth === clientWidth` on R00, R02-R10, and R17 at 320/390/767/768/1280 and 200% zoom, including dense/long/missing-media states.
- Profile statistics satisfy the ruled mobile rows and desktop five-item order with dense histogram data; no child exceeds its container.
- `1204 FOLLOWERS` and `1048 FOLLOWING` remain fully legible on private/public profiles at 320/390 with no overlap into avatar, FollowControl, or gutter.
- All five Search scopes are discoverable, focusable, and visible according to the operator-selected pattern; focus is never clipped.
- StarInput exposes five stars, half-step keyboard/click behavior, adjacent/ruled value placement, and 44px whole-star targets without ledger overflow.

### 7. Dependencies and sequencing

1. Operator rules the shared tier, Search scopes, and StarInput narrow composition.
2. Implement and test the container primitive before page-level adjustments.
3. Fix Profile statistics/counts and then Search/Event collisions against that container.
4. Revalidate all inherited surfaces and exact-width/zoom fixtures before migrating unrelated spacing.

---

## LEAD-012 — Conditional children leave implementation-shaped whitespace

**Classification / severity:** missing Event artwork `BINDING` / High; non-owner Favorites `PRINCIPLE` / Medium.

### 1. Lead problem

Layouts reserve geometry based on an assumed child set instead of the children actually rendered. Missing Event artwork removes the ruled identity slot while community content keeps its artwork offset; non-owner Favorites omit the owner action but keep its column.

### 2. Technical explanation

- `VIS-009`: `frontend/src/pages/EventPage.jsx:195-204` mounts `ImageSlot` only when artwork exists or the event is past. `frontend/src/styles.css:310-316` then activates a text-only grid branch. An absent upcoming URL collapses the 80×100/160×200 identity slot, whereas a broken URL renders the fallback. The same semantic missing-media state has two compositions.
- `SPC-003`: `.event-community-section` at `frontend/src/styles.css:421-430` always applies `max-width:608px; margin-left:192px` on desktop. On a missing-art event, identity content uses the full 800px ledger while community content starts 192px later, leaving an unexplained empty column.
- `SPC-009`: `.profile-favorite-list > li` at `frontend/src/styles.css:270-278` always declares `56px minmax(0,1fr) 44px`. `frontend/src/pages/ProfilePage.jsx:89-105` omits `FavoriteControl` for a non-owner, but the 44px track and 16px gap remain. At 390px this consumes about 60px and accelerates title truncation.
- Affected states are R08 upcoming absent/broken artwork on mobile/desktop and R06 owner/non-owner Favorites with long names and text scaling.

### 3. Solution proposals, system first

1. **Make conditional composition explicit in layout APIs.** Governed row/identity primitives should receive semantic variants such as `mediaState` and `hasTrailingAction`, or derive them from actual slots. CSS grid tracks must be created only for mounted semantic slots.
2. **Correct Event missing-media identity at the source.** For every upcoming event, mount the ruled fixed `ImageSlot`; when URL is absent or broken, render the approved initial fallback in that same 80×100/160×200 slot. This removes the unauthorized text-only branch and gives desktop community alignment a real identity column.
   - Likely boundary: Event identity JSX plus the fixed-flier `ImageSlot` primitive; remove/retire the missing-image grid exception only after state coverage proves equivalence.
3. **Tie Event community alignment to the governed identity composition.** Use an event-layout grid or shared content-column variable rather than a hard-coded `margin-left:192px`. The identity and every community/review state should resolve to the same ruled content column.
4. **Make Favorite rows slot-aware.** Owner rows use `media / content / action`; non-owner rows use `media / content`. Prefer a primitive or explicit modifier (`has-action`) rather than `:empty` or positional hacks.
5. **Test absent, broken, and present slots as equivalent geometry contracts.** Media transport state may change fallback content, not page anatomy.

### 4. NO-GO constraints

- Do not remove the fixed Event artwork slot for absent URLs, invent a full-bleed hero, or introduce a new fallback beyond the ruled `ImageSlot` initial treatment.
- Do not keep a 192px community indent when no governed identity column explains it.
- Do not reserve the Favorite action column on non-owner rows, and do not show disabled/placeholder heart controls to fill the gap.
- Do not change favorite permissions, ownership checks, truncation rules, or event data contracts.
- Do not solve either defect with arbitrary padding reductions; slot structure is the root.

### 5. REQUIRES OPERATOR DECISION

No operator decision is needed for the binding Event fallback/alignment correction or the principle-level removal of an absent non-owner action track, provided all current media, ownership, and behavior rules remain unchanged. A ruling would be required to replace the fixed Event identity composition, change fallback art, or expose owner actions to non-owners.

### 6. Measurable acceptance/evidence criteria

- Present, absent, and broken upcoming artwork produce identical Event identity grid geometry at 320/390/1280; only the media content changes.
- At desktop, title/meta/lineup/owner block and Circle/Public sections share the ruled continuous content-column left edge; no unexplained 192px dead zone remains.
- Owner Favorites retain a 44px action target; non-owner Favorites have no third grid track or reserved gap and gain the released width for content.
- Long Favorite names at 320/390 truncate only after consuming all non-action content width; no document overflow occurs at 200% zoom.

### 7. Dependencies and sequencing

1. Define slot-aware identity/row composition primitives under LEAD-014.
2. Correct Event fallback mounting, then align community sections through one event-layout contract.
3. Migrate Favorite rows to conditional tracks.
4. Verify present/absent/broken media and owner/non-owner matrices before broader row reuse.

---

## LEAD-013 — Desktop event ledgers spend width without a scanning role

**Classification / severity:** `BINDING` / High. The Discover-overlay component fork linked by `VIS-015` remains a separate `DECISION` tension.

### 1. Lead problem

Event results in Search, Venue, and Artist use an 800px desktop ledger but preserve the narrow thumbnail-plus-stacked-copy anatomy. Date and venue do not form the ruled right metadata column, so the extra width is neither used for grouping nor scanning.

### 2. Technical explanation

- `SPC-004`: `frontend/src/components/EventList.jsx:84-104` renders the shared compact result; `frontend/src/discover.css:1-31` defines a two-column thumbnail/copy grid at every width and changes only metadata font size at desktop. On a live Artist route at 1280, the row spans x=240..1040 but nearly all content remains at the left.
- The same component supplies R03 event search results, R09 Venue ledgers, and R10 Artist ledgers, so this is one shared component defect rather than three page spacing defects.
- The Search handoff requires `EventListRow` verbatim with 56×70 media, mobile stack, and desktop spread/right metadata column. Artist and Venue handoffs inherit the shared ledger grammar.
- `VIS-015`: Discover inline search deliberately takes `compact=true` and `frontend/src/components/SearchResults.jsx:37-66` forks `CompactEventResultRow`; `frontend/src/styles.css:79-92` gives it body-size rather than row-title type. The overlay handoff does not explicitly decide whether constrained results use the full verbatim row amplitude. That fork is `DECISION`; it cannot be silently merged while correcting the binding desktop ledger.

### 3. Solution proposals, system first

1. **Establish one canonical `EventListRow` semantic anatomy.** Slots should be media, primary identity/title, secondary contextual line, and temporal/location metadata. Markup remains stable; responsive CSS assigns mobile stacking and desktop metadata regions.
2. **Implement the ruled desktop spread in the shared row.** At sufficient container width, use a three-region grid: fixed 56×70 media, flexible identity, and a right-aligned/minmax metadata column. Align comparable date/location values across siblings; preserve whole-row navigation and hairlines.
   - Likely boundary: `EventList.jsx`/row component plus `discover.css`, consumed unchanged by Search, Venue, and Artist.
3. **Keep page context omissions explicit.** Venue rows may omit redundant venue identity and Artist rows may omit the current artist as already ruled, but those omissions should feed the same slots rather than fork markup.
4. **Treat Discover overlay as an explicit unresolved variant.** Until ruled, do not replace it as part of the binding desktop-spread change. Prepare either (a) canonical anatomy with a governed compact amplitude variant, or (b) literal canonical row reuse, but implement only after operator selection.
5. **Add dense-ledger comparison tests.** Sparse screenshots hide the scan failure; validate repeated long titles/dates/locations and pagination at mobile and desktop.

### 4. NO-GO constraints

- Do not create separate Search, Venue, and Artist row components or page-local padding fixes.
- Do not place date/location arbitrarily at the far edge without a stable metadata column and alignment rule.
- Do not introduce cards, shadows, gradients, or decorative whitespace to fill the ledger.
- Do not change whole-row navigation, media size, entity omissions, event order, or pagination behavior.
- Do not silently decide that Discover overlay must use either full or compact amplitude; `VIS-015` remains `DECISION`.

### 5. REQUIRES OPERATOR DECISION

No decision is needed to implement desktop spread for the canonical row on R03/R09/R10; the handoffs bind it. The operator must decide whether R02 Discover inline-search results reuse the canonical row verbatim or use an explicitly governed compact-amplitude variant inside the constrained panel.

### 6. Measurable acceptance/evidence criteria

- The same row component and role-bearing classes render R03 event results and R09/R10 ledgers.
- At 1280/wide desktop, each row visibly uses media, flexible identity, and a consistent right metadata region across a dense ledger; dates/locations align across siblings.
- At 320/390, the row retains the ruled narrow composition, 56×70 fallback slot, full-width navigation target, and no horizontal overflow.
- Long title/venue/date fixtures do not overlap; truncation occurs in declared flexible slots; pagination/error slots remain stable.
- Discover overlay visual regression remains unchanged until its operator ruling, or changes only under a recorded ruling.

### 7. Dependencies and sequencing

1. Define the canonical row primitive and container-responsive threshold after LEAD-011's tier ruling.
2. Migrate/verify Search, Venue, and Artist together because they share the binding anatomy.
3. Obtain the Discover overlay amplitude ruling.
4. Consolidate or explicitly variant the overlay and remove obsolete duplicate markup only after that ruling.

---

## LEAD-014 — Visual roles are encoded through tags and selector inventories instead of primitives

**Classification / severity:** local `BINDING` violations plus cross-cutting `PRINCIPLE` / High.

### 1. Lead problem

Visual meaning is inferred from incidental HTML (`h1`, `h3`, direct `ul/li`) or membership in long CSS selector lists. Correctness depends on every future agent remembering exceptions, so new screens inherit wrong type, spacing, boundaries, and targets by default.

### 2. Technical explanation

- `VIS-004`: `frontend/src/styles.css:10-13` assigns the display face to every H1/H3. Generic/entity/profile not-found states therefore receive catalog identity amplitude; `ProfilePage.jsx:134-136` also forks incomplete not-found anatomy.
- `VIS-005`: the same selector makes Search's H1 at `SearchPage.jsx:97-103` outrank the search field, contradicting the handoff's primary-object ruling.
- `VIS-010` / `SPC-007`: global `main ul/ol > li` styling at `frontend/src/styles.css:30-32` turns Edit Profile error lists (`EditProfilePage.jsx:92,117-124`) into bordered/padded ledgers and combines with Activity's own row padding (`styles.css:194-203`).
- `SPC-006`: mobile target correctness comes from the whitelist at `frontend/src/styles.css:384-391`; classless recovery/pagination actions on R03-R10/R17 remain at the 34px baseline. Any new route is noncompliant until manually appended.
- `VIS-006` demonstrates the same structural failure within content: one `<strong>` tag is asked to represent actor identity, sentence action, and read state.
- Direct blast radius is R03-R10/R17 and every future route/component using those elements.

### 3. Solution proposals, system first

1. **Define a small role taxonomy and primitives.** At minimum:
   - typography: `IdentityTitle`, `FunctionalPageTitle`, `SectionHeading`, `RowTitle`, `SentenceActor`, `Body`, `Micro`, `ErrorText`;
   - collections: `Ledger`, `LedgerRow`, `FieldErrorList`, `InlineList`;
   - actions: `PrimaryAction`, `QuietAction`, `RecoveryAction`, `PaginationAction`, `MenuAction`, `DialogAction`;
   - layout/state: `PageLedger`, `StateSlot`, `ContinuationSlot`.
   Primitives may be semantic HTML internally, but visual roles are selected explicitly.
2. **Narrow global CSS to true resets and inherited defaults.** Remove visual identity from global H1/H3 and ledger anatomy from direct-list selectors after all consumers migrate. Element selectors must not decide product role.
3. **Make target floors intrinsic to action roles.** Recovery and pagination primitives own 44px mobile and 24px general floors. Remove the selector whitelist once coverage confirms no orphan action.
4. **Migrate by role family.** First typography (Search/system failures), then list semantics (Activity/Edit Profile), then recovery/pagination (R03-R10/R17). Avoid a route-by-route exception campaign.
5. **Consolidate state/not-found anatomy.** Use one functional system-state primitive for generic/entity/profile not found, accepting resource-specific copy while preserving the required explanation + Return to Discover action.
6. **Add enforcement.** Static checks should reject new unscoped global heading/list visual selectors and classless recovery/pagination actions. Component tests should verify role classes, computed type family/size/weight, target dimensions, and no inherited ledger border in field errors.
7. **Document agent routing.** Add the primitive/role map to the design memory or frontend design-system index only in a separately authorized documentation order, so future agents select roles before writing markup.

### 4. NO-GO constraints

- Do not “fix” symptoms with page-specific overrides, `!important`, negative margins, or additions to selector inventories.
- Do not replace semantic HTML with generic divs; semantics and visual roles should both be correct.
- Do not make every heading functional or every list a ledger. Identity titles remain expressive only where the handoffs assign identity.
- Do not create a large abstraction framework unrelated to the identified roles, introduce new tokens, or change colors/type families under this migration.
- Do not alter route copy, navigation, API behavior, or product rules while extracting presentation primitives.
- Do not edit design handoffs to match existing CSS; implementation must follow authority.

### 5. REQUIRES OPERATOR DECISION

No decision is required for the identified binding corrections: Search must keep the field primary; system failures use functional type; Activity and Edit Profile must not inherit generic list treatment; mobile recovery/pagination actions must reach 44px. Operator input is required only when a surface's role is genuinely unruled (for example Discover overlay amplitude in VIS-015), or before adding/changing design tokens or product copy.

### 6. Measurable acceptance/evidence criteria

- No product-role styling remains on global `h1`, `h3`, `main ul/ol > li`, or equivalent descendant/location selectors; global rules are limited to reset/inheritance semantics.
- Search/system headings and identity headings use explicit, testable roles with the correct family/amplitude; the Search field is the first dominant object.
- Edit Profile field errors sit 6px below their field in the ruled 12px danger register with no ledger border/padding; Activity rows receive exactly one ledger treatment.
- Every recovery and pagination control on R03-R10/R17 measures at least 44×44px on 320/390 without relying on a selector whitelist.
- Adding a fixture-only new recovery action through the governed primitive passes target/focus tests without CSS changes; a classless/unruled action fails static or component checks.
- Generic, event, venue, artist, and profile not-found states share functional anatomy and all include the ruled Discover recovery route.

### 7. Dependencies and sequencing

1. Inventory current semantic roles and map each existing selector consumer before deletion.
2. Introduce primitives and characterization tests with no visual change where current output is already compliant.
3. Migrate typography, collection/list, then action/state roles; fix binding mismatches during their family migration.
4. Remove global role selectors and mobile whitelist only after the final consumer moves.
5. Run exhaustive route/state visual, keyboard, target-size, overflow, and regression checks; separately authorize any design-memory documentation update.

## Recommended cross-problem delivery order

1. **Operator rulings:** LEAD-009 access matrix/footer; LEAD-011 responsive tier/Search scopes/StarInput; LEAD-013 Discover overlay amplitude.
2. **Foundations:** LEAD-014 role primitives plus LEAD-011 PageLedger/container contract.
3. **State architecture:** LEAD-010 phase/operation feedback model.
4. **High-trust surface repair:** LEAD-008 Activity semantics/read state.
5. **Conditional composition:** LEAD-012 Event/Favorites slots.
6. **Shared content rows:** LEAD-013 canonical EventListRow desktop spread.
7. **Evidence gate:** exhaustive route/state/viewport/fault-injection matrix before any visual handoff is declared complete.
