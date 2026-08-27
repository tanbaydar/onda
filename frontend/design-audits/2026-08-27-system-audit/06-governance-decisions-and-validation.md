> Diagnostic audit artifact. It records evidence and proposals; it does not replace the binding Markdown handoffs in `frontend/design-handoffs/` and does not authorize product-behavior changes.

# Cross-system design-governance architecture

Status: solution architecture only. This document does not change frontend code, backend behavior, product rules, handoffs, fixtures, or deployment state. `frontend/design-handoffs/*.md` remains the sole visual authority.

## Governing rule

Correct the root role/state/layout system before correcting pages. A page-level change is admissible only when it is a migration to a governed shared role, a handoff-specific composition, or an explicitly ruled exception. Existing CSS and the deployed bundle are evidence, never authority.

Classification remains:

- **BINDING:** implement the existing handoff/product rule; no new visual decision is needed.
- **PRINCIPLE:** correct the systemic mismatch only where it does not contradict a handoff.
- **DECISION:** do not implement until the operator selects one of the mutually exclusive options in the decision register.

## 1. Consolidated NO-GO registry

The registry is deliberately phrased as prohibitions. It tells future agents what they may not “solve” locally, and ties every prohibition to the diagnostic IDs and controlling authority.

| No-go | Prohibition | Diagnostic keys | Binding authority / boundary |
|---|---|---|---|
| **NG-01 — Authority and release parity** | Do not certify production from source inspection alone; do not patch already-correct current source to imitate an older deployed bundle; do not treat the production token/registration divergence as a new design choice. Reconcile the exact source SHA, build inputs, output hashes, and deployed asset manifest first. | LEAD-001; VIS-017 | `accessibility-handoff.md` readable quiet/focus/target rules; `auth-handoff.md` untouched-registration rule; current `design-tokens.css` |
| **NG-02 — No cosmetic-system expansion** | Do not add fonts, decorative colors, brand gradients, shadows, cards, glass, general radii, or new depth to answer these findings. The current source already uses the three authorized families, semantic palette, flat depth, and media grammar. Correct allocation, not inventory. | LEAD-002, LEAD-014; VIS-004, VIS-005, VIS-011, VIS-016 | `DESIGN_BRIEF.md` type/color allocation; `accessibility-handoff.md`; `profile-handoff.md`; token hairline rules |
| **NG-03 — No visual meaning from bare tags or location selectors** | Do not style all `h1`, `h3`, `ul`, `ol`, or `li` as one visual role; do not extend the mobile-action selector whitelist. Semantic markup and visual role must be separate, explicit contracts. | LEAD-002, LEAD-008, LEAD-014; VIS-004, VIS-005, VIS-006, VIS-010; SPC-006, SPC-007 | Search primary-object ruling; Profile/Edit form ruling; Activity sentence ruling in `design-tokens.css`/`DESIGN_CONTRACT.md`; `accessibility-handoff.md` target floor |
| **NG-04 — No endpoint-shaped async UI** | Do not let one generic `loading/error/retry` field represent initial load, continuation, mutation, session bootstrap, and logout. Do not let Retry invoke a different operation from the operation named by the error. | LEAD-003, LEAD-004, LEAD-008, LEAD-010; VIS-001, VIS-002, VIS-007, VIS-008; SPC-008 | `accessibility-handoff.md` local recovery and retained-content rule; `discover-handoff.md` continuation rule; `DESIGN_CONTRACT.md` state-slot rules |
| **NG-05 — No whole-surface replacement for local actions** | Do not unmount stable identity, ledgers, or successfully loaded rows for favorite, follow, rating, review, WBT, read-bookkeeping, pagination, or retry work. Pending/error belongs to the action or continuation slot that owns it. | LEAD-003, LEAD-004, LEAD-010; VIS-007, VIS-008; SPC-008 | `accessibility-handoff.md`; `profile-handoff.md` FollowControl recovery; `artist-handoff.md`, `discover-handoff.md`, and `venue-handoff.md` continuation retention |
| **NG-06 — No identity-free loading/failure fragments** | Do not reduce Event, Venue, Artist, Profile, Edit Profile, Discover, or not-found states to unrelated generic paragraphs that erase the page's stable signature. Preserve the ruled identity/ledger slot and expose a local state within it. | LEAD-004; VIS-004; SPC-008 | `artist-handoff.md` states; `event-handoff.md` composition; `profile-handoff.md`; accessibility recovery; generic not-found contract |
| **NG-07 — No new event-row fork by page** | Do not hand-tune Search, Discover, Venue, Artist, Profile, or feed event rows as unrelated components. Keep one semantic event-row presenter and governed amplitude/composition variants. Do not choose whether Discover's overlay is the standard or compact variant before DEC-09. | LEAD-005, LEAD-013; VIS-015; SPC-004 | `search-handoff.md` verbatim reuse and desktop spread; `discover-handoff.md`; `artist-handoff.md`; `venue-handoff.md`; EventListRow token grammar |
| **NG-08 — No unruled inert-control policy** | Do not silently hide, disable, preserve, or reorder Sort/Circle controls in unavailable states. Preserve current behavior until DEC-05 and DEC-07 are ruled; after ruling, encode availability as a shared collection/module state rather than per-page conditionals. | LEAD-006; VIS-012; SPC-009 (conditional-child analogue) | `polish-handoff.md` sort styling; Event composition; general empty-state principles |
| **NG-09 — No silent past-event reorder** | Do not claim that the general “reviews lead” thesis authorizes reordering the detailed Event handoff. Do not claim that current detail order silently overrides the thesis. Resolve DEC-04 first. | LEAD-007; LEAD-006 subset; VIS-012; SPC-003 | `DESIGN_BRIEF.md`/`DESIGN_CONTRACT.md` past-event thesis versus `event-handoff.md` detailed composition |
| **NG-10 — No flattened social sentence or stale state** | Do not serialize actor, verb, object, and read status into one styled string. Do not leave unread styling after mark-read success. Do not fix Activity padding independently of the global ledger-role leak or its continuation state. | LEAD-008; VIS-006, VIS-007; SPC-007, SPC-008 | Activity sentence/UI ruling in `design-tokens.css` and `DESIGN_CONTRACT.md`; `accessibility-handoff.md` local recovery |
| **NG-11 — No permission-policy invention** | Do not normalize redirect, inline gate, dead-page, or mixed public/private behavior across Home, Activity, Settings, Event, Verify, and legacy routes without DEC-06. A visual audit is not authority to change shipped access behavior. | LEAD-009; VIS-002, VIS-003 | Frozen-behavior rule; `auth-handoff.md` persistent chrome; Event guest composition; navigation contract |
| **NG-12 — No local responsive patch before the capacity contract** | Do not choose arbitrary new breakpoints/gutters, shrink protected typography, clip data, or add document overflow. Binding no-overflow defects must be fixed, but the shared 768/gutter/intermediate-tier strategy requires DEC-01; Search scopes and StarInput separately require DEC-02/DEC-03. | LEAD-011; SPC-001, SPC-002, SPC-005, SPC-010, SPC-013 | `stats-handoff.md`; `search-handoff.md`; `event-handoff.md`; `accessibility-handoff.md`; `DESIGN_CONTRACT.md` 320/768/no-overflow QA |
| **NG-13 — No dead columns for absent children** | Do not reserve artwork/action columns when their semantic child is absent. Missing and failed media must share the ruled fallback slot; conditional layouts must recompose from the actual child set. | LEAD-012; VIS-009; SPC-003, SPC-009 | `polish-handoff.md` fixed media fallback; `event-handoff.md` aligned content column; functional-whitespace principles |
| **NG-14 — No auth-register drift** | Do not restore auth-only chrome, summary-style validation, pre-choice privacy consequences, or collapsed primary-action spacing. Do not decide footer presence without DEC-08. | LEAD-001; VIS-003, VIS-010, VIS-017; SPC-011 | `auth-handoff.md` dated 2026-08-20/27 deltas and 32px primary separation; `accessibility-handoff.md` |
| **NG-15 — No target-size-by-memory** | Do not rely on agents remembering to add each new recovery, pagination, menu, tab, follow, row-removal, or dialog selector to a mobile list. Target class is a role, with 44px for named essential mobile actions and 24px for the remaining floor. | LEAD-014; SPC-006 | `accessibility-handoff.md` target-size section; profile/search/event action rulings |
| **NG-16 — No local vocabulary or glyph synonyms** | Do not introduce `Try again` beside governed `Retry`, punctuated button labels, or stemmed disclosure arrows beside the chevron grammar. Reuse one recovery vocabulary and one disclosure role. | VIS-013, VIS-014 | `accessibility-handoff.md` Retry grammar; `discover-handoff.md` chevron; `profile-handoff.md` dropdown affordance |
| **NG-17 — No profile-only geometry hacks** | Do not solve statistics, counts, empty judgment, favorites, or header grouping with value-specific font shrinking, clipping, or extra dividers. Preserve the ruled statistic roles, public 4-digit counts, judgment-only green, fused header/statistics band, and conditional action layout. | LEAD-012; VIS-011, VIS-016; SPC-001, SPC-009, SPC-013 | `profile-handoff.md`; `stats-handoff.md`; `accessibility-handoff.md`; token hairline rule |
| **NG-18 — No unowned shell feedback** | Do not duplicate session status in header and page, hide authored status through positional CSS, double-inset recovery, or route logout failure through bootstrap copy/Retry. Shell, page, collection, and action feedback each need one owner. | LEAD-010; VIS-001, VIS-002, VIS-003; SPC-012 | `accessibility-handoff.md` session/local recovery; `auth-handoff.md` persistent shell; common ledger alignment rules |

Every diagnostic ID is represented above. The no-go registry does not turn `DECISION` items into implementation authority; it freezes them against silent resolution.

## 2. Operator DECISION register

No option is selected here. Options within each decision are mutually exclusive at the named contract level. Choosing an option must produce or amend a Markdown handoff before implementation.

### DEC-00 — Reconcile audited source and deployed production

**Keys:** LEAD-001, VIS-017.
**Question:** Which artifact becomes the remediation baseline?

- **Option A — Promote the audited source baseline.** Build and deploy the audited commit, then verify production asset hashes and the Register untouched state. Consequence: current-source fixes/tokens become live together; release risk includes every change between production and that commit.
- **Option B — Recover and audit the exact live source.** Identify the commit/build inputs that produced `index-BUdU25RU.css`, run the audit against that tree, then remediate there. Consequence: lowest ambiguity about current users' code, but duplicates analysis and delays current-branch work.
- **Option C — Isolated production-parity release.** Cherry-pick only already-ruled token/Register parity into the live release line, then later promote the broader audited source. Consequence: fastest narrow correction, but creates a temporary second release lineage that must be reconciled and reverified.

### DEC-01 — Responsive capacity contract at and above 768px

**Keys:** LEAD-011; SPC-001, SPC-002, SPC-013.
**Question:** How should desktop semantics, 106px gutters, and component desktop layouts activate?

- **Option A — Move the desktop tier as a unit.** Mobile/narrow composition continues until the viewport can support the 800px ledger plus desktop gutters; desktop chrome, gutters, and component layouts switch together. Consequence: simplest capacity rule, but changes the handoff's current 768 activation.
- **Option B — Keep 768 as desktop chrome, add a tablet content tier.** Header/chrome changes at 768; gutters and width-demanding component compositions remain narrow or use a defined tablet composition until capacity exists. Consequence: preserves the semantic 768 shell boundary, but creates a third governed tier for every shared primitive.
- **Option C — Keep 768 and make gutters/container capacity-fluid.** Desktop semantics start at 768 while gutters interpolate and components activate their desktop sublayout by container capacity. Consequence: most monotonic use of width, but replaces the fixed 106px-gutter assumption with a fluid/container contract.

Binding overflows in SPC-001/SPC-013 must be removed under any option; the decision is the shared means, not whether overflow is allowed.

### DEC-02 — Search's five scopes at 320px

**Keys:** SPC-005; LEAD-011.
**Question:** Which existing constraint yields when five named 44px targets and 24px gaps do not fit one 272px line?

- **Option A — Intentional horizontal rail.** Keep one line and target/gap values; add an explicit continuation affordance, deterministic focus scrolling, and a local-scroll acceptance rule. Consequence: preserves all labels and targets but formally permits local horizontal scrolling.
- **Option B — Two-line scope group.** Keep all labels and targets visible by wrapping into a ruled two-row composition. Consequence: no hidden scope and no rail, but supersedes the single-line handoff and changes vertical rhythm.
- **Option C — Collapsed scope selector.** Replace the five inline scopes at narrow widths with one 44px disclosure that exposes all options. Consequence: fits cleanly but adds a touch and changes the current immediate-comparison model.

### DEC-03 — StarInput at 320px and high zoom

**Keys:** SPC-010; LEAD-011.
**Question:** How should the handoff's fixed star geometry, adjacent value, ledger gutter, and 44px targets fit together?

- **Option A — Stack the selected value below the stars at constrained widths.** Consequence: preserves star and target geometry, but supersedes “beside the stars” at narrow capacity.
- **Option B — Widen the owner-control band beyond the normal ledger.** Consequence: preserves adjacency and star geometry, but introduces a deliberate local alignment exception.
- **Option C — Authorize a constrained-width star/gap variant.** Keep the value beside the run while reducing visible star/gap geometry; retain 44px hit regions through invisible/overlapping target padding. Consequence: preserves ledger alignment and adjacency, but changes the ruled 32px/6px visual rhythm and needs careful hit-target testing.

### DEC-04 — Past-event reading order

**Keys:** LEAD-007; LEAD-006 subset; SPC-003.
**Question:** Which authority controls the semantic hierarchy of past events?

- **Option A — Detailed Event composition wins.** Keep identity/meta/lineup/owner composition before community; amend the product thesis so it no longer says reviews lead. Consequence: lowest UI change, but past and upcoming remain structurally similar.
- **Option B — Reviews/community lead after a minimal identity summary.** Move Circle/Public judgment ahead of lineup and secondary listing detail. Consequence: fulfills the thesis and differentiates past events strongly, but requires a new detailed Event handoff and migration of guest/owner states.
- **Option C — Judgment-first within the identity column.** Keep the title/art/meta opening, then place rating/community signal before lineup and owner actions while leaving full reviews below. Consequence: creates a moderate hierarchy inversion without fully moving collections, but adds a new past-only composition tier.

### DEC-05 — Guest placement of unavailable personalized modules

**Keys:** LEAD-006, LEAD-007; VIS-012.
**Question:** Where does the unavailable `Your Circle` state sit relative to usable public content?

- **Option A — Preserve Circle before Public.** The current order becomes explicit authority. Consequence: stable cross-session section order, but an unavailable module continues to precede useful public evidence.
- **Option B — Place Public before Circle for guests only.** Consequence: guest task utility improves, but section order changes by session state.
- **Option C — Keep the Circle slot but reduce it to one inline authentication boundary attached after Public.** Consequence: least dead vertical space, but changes both module anatomy and position.

### DEC-06 — Direct-access permission model

**Keys:** LEAD-009; LEAD-006 guest subset; VIS-002.
**Question:** What is the product-wide rule for a guest/unverified viewer addressing a personalized route?

- **Option A — Redirect protected whole pages to Login with return destination.** Mixed public detail pages retain local gates. Consequence: predictable route protection and authentication path, but loses immediate context unless return navigation is reliable.
- **Option B — Preserve every addressed route with an inline authentication boundary.** Consequence: maximum context retention and consistent anatomy, but exposes shells of routes whose useful content may be entirely protected.
- **Option C — Ratify the current route-specific policy.** Document Home, Activity, Settings, Verify, Event, and legacy behavior separately. Consequence: no shipped behavior change, but agents must carry a more complex permission matrix indefinitely.

### DEC-07 — Sort controls without a successful non-empty collection

**Keys:** LEAD-006; VIS-012.
**Question:** What should the sort role do during loading, error, and empty states?

- **Option A — Mount only for successful non-empty data.** Consequence: removes inert chrome and simplifies empty/error hierarchy; the trigger appears after data resolves.
- **Option B — Preserve the slot but render a disabled trigger.** Consequence: stable geometry and discoverable feature, but retains a non-operable control that needs disabled semantics/copy.
- **Option C — Keep the active control in every state.** Consequence: no component change and sorting remains preselectable, but the handoff must explicitly accept inert-looking chrome when no data exists.

### DEC-08 — Footer on authentication routes

**Keys:** VIS-003; LEAD-009 shell boundary.
**Question:** Is the provenance footer part of persistent product chrome on auth pages?

- **Option A — Footer on every route.** Consequence: one shell anatomy and provenance everywhere; auth pages gain an additional landmark below the focused form.
- **Option B — Footer suppressed on R11–R15.** Consequence: preserves the current focused auth composition, but formalizes one exception to global chrome.

### DEC-09 — Discover overlay event-result role

**Keys:** LEAD-005, LEAD-013; VIS-015; SPC-004.
**Question:** Is the Discover overlay the standard event result at smaller amplitude, or a separate compact role?

- **Option A — Reuse the standard EventListRow presenter and role verbatim.** Consequence: maximum consistency and one row contract, but the overlay must accommodate standard title/meta amplitude.
- **Option B — Ratify a compact overlay variant within the same presenter family.** Consequence: better density inside the panel, but the handoff must define its title scale, metadata, media, keyboard, and responsive boundaries so it cannot drift into a second component system.

## 3. Dependency-aware remediation phases

### Phase 0 — Baseline, authority, and release gate

1. Record audited source SHA, dependency lock hash, build command, generated CSS/JS hashes, and production asset hashes.
2. Resolve DEC-00. Do not mix live-bundle defects with current-source defects in tickets or acceptance evidence.
3. Obtain operator rulings for DEC-01–DEC-09. Rulings update handoffs; they are not buried in implementation comments.
4. Freeze a route/state fixture manifest for R00–R17, including dense/extreme and failure cases.

**Exit:** every item has one authority class, one source/deploy baseline, and no unresolved decision hidden inside an implementation task.

### Phase 1 — Role foundation (source change, no page redesign)

1. Replace bare-tag/location styling with explicit typography, list, field-error, action-target, and feedback roles.
2. Centralize semantic tokens and prevent feature CSS from redefining system roles.
3. Establish container-capacity names after DEC-01; do not yet tune page-specific values.
4. Add static checks for forbidden broad selectors, unowned color literals, and recovery/pagination controls without a target role.

**Roots closed:** LEAD-002, LEAD-014; VIS-004/005/006/010/011/013/014/016; SPC-006/007/011/012 in their system portions.

### Phase 2 — Async state and feedback ownership (source change)

1. Separate initial, continuation, mutation, and session state channels.
2. Define stable initial-state, continuation-slot, and action-feedback roles with operation-specific Retry ownership.
3. Preserve successful content during continuation and local mutation failures.
4. Keep identity signatures mounted through loading/error/not-found where the handoff requires them.

**Roots closed:** LEAD-003/004/008/010; VIS-001/002/007/008; SPC-008; Activity stale-read semantics.

### Phase 3 — Shared content and conditional-composition families (source change)

1. Migrate event results to one presenter family; apply DEC-09 to its overlay variant and the existing desktop-spread handoffs.
2. Make media/action columns conditional by semantic child set while retaining required fallback slots.
3. Migrate profile statistics/count/favorites and Activity sentence roles to governed primitives.
4. Apply the ruled not-found and local recovery anatomy through shared roles, not copied fragments.

**Roots closed:** LEAD-005/012/013; VIS-009/015; SPC-003/004/009; remaining Profile/Activity roots.

### Phase 4 — Responsive system and constrained compositions (source change after decisions)

1. Implement DEC-01 once at the ledger/container layer.
2. Implement DEC-02 and DEC-03 as explicit narrow variants, not overflow patches.
3. Verify binding profile overflow/count fixtures and every component at exact 767/768.
4. Verify 200% zoom and long/localized copy before route polish.

**Roots closed:** LEAD-011; SPC-001/002/005/010/013.

### Phase 5 — Route migrations and decision-dependent hierarchy (source change)

Migrate R00–R17 to the shared roles. Apply DEC-04–DEC-08 only from amended handoffs. Route work may supply handoff-specific composition, but may not introduce a new font/color/action/state/ledger system.

**Exit:** every route/state matrix row passes without per-page exceptions that duplicate a shared role.

### Phase 6 — Build, deploy, and parity verification (deployment change)

1. Build reproducibly from the selected source baseline.
2. Run the complete validation matrix against the built artifact before release.
3. Deploy; verify the exact live asset hashes, computed root tokens, untouched Register state, route-state screenshots, and focus/target measurements.
4. Mark a finding closed only after production evidence matches the source evidence. “Fixed on branch” and “fixed for users” are separate statuses.

### Phase 7 — Recurrence prevention

1. Require new frontend work to cite the role and handoff it uses.
2. Reject new page-local CSS that restates a shared role without an explicit operator exception.
3. Add every new route/state to the matrix and to source-built and deployed smoke suites.
4. Keep decision rulings in Markdown handoffs; keep audit reports diagnostic and non-authoritative.

## 4. Shared primitive and role boundaries

These are ownership boundaries, not prescriptions for new visual values. Their concrete rendering comes only from the applicable handoff/tokens.

| Role boundary | Owns | Must not own |
|---|---|---|
| **TypeRole** | Identity title, functional page title, section heading, row title, actor name, metadata, prose, micro/status, judgment numeral | HTML tag choice, arbitrary page overrides, new families |
| **PageLedger / CapacityTier** | Centering, max measure, narrow/desktop gutters, capacity names, chrome reservation, no-overflow contract | Page-specific content order, identity typography, data semantics |
| **IdentityBand** | Stable title/media/meta/action slots for Event/Venue/Artist/Profile; loading/failure signature | Collection pagination, unrelated feedback, generic card treatment |
| **RepeatingLedger / LedgerRow** | Sibling hairlines, row padding, row focus/navigation, empty/initial/continuation slots | Validation lists, prose lists, Activity actor grammar, page-level spacing |
| **EventRowPresenter** | Shared event data roles, media fallback, title/meta/lineup/judgment regions, context omission rules | Independent page forks; Discover compact amplitude before DEC-09 |
| **CollectionState** | `idle/loading/success-empty/success-data/initial-error/continuing/continuation-error/exhausted`; successful-data retention | Mutation state, page/session errors, data-fetch implementation details |
| **ActionState** | Rest/pending/success/error for one named operation; duplicate-submit prevention; local Retry | Clearing page/collection identity, reusing a generic unrelated error |
| **SessionStatus** | Bootstrap status, guest fallback, persistent lookup Retry, logout as a separately named action | Page-specific data failure, hiding state through positional CSS |
| **FeedbackSlot** | One sentence, correct operation name, local Retry, stable placement and danger semantics | Toast/card proliferation, page replacement, operation-ambiguous copy |
| **ActionTargetRole** | Essential-mobile 44px class and universal 24px floor independent of visible glyph/text size | Selector whitelists or one-off component padding memory |
| **Disclosure / Menu / Tab / Scope** | Trigger-option relationship, selected/current/focus/open/dismiss semantics and ruled glyph vocabulary | Page-specific arrow characters, judgment color, unruled narrow recomposition |
| **Field / FieldError** | Label-control-description-error association, local error geometry, alert/`aria-describedby` semantics | Ledger row borders/padding, summary blocks, unrelated route errors |
| **MediaSlot** | Stable aspect/size, present/absent/failed equivalence, event flier/avatar/artist fallback family | Conditional disappearance where a fixed fallback is ruled; invented card chrome |
| **ConditionalComposition** | Layout based on actual semantic children (art/action present or absent) | Empty reserved columns, value-specific width hacks |
| **ActivitySentence** | Separate actor, verb, object, time, read/unread roles and navigation destination | One pre-styled interpolated string, display type, stale local read state |
| **StatisticsGroup** | Named statistic roles, available/unavailable judgment state, count formats, histogram relationship | Green on absent values, font shrinking, clipping, new separators |
| **SystemStatePage** | Functional title, concise explanation, route recovery, persistent shell | Catalog identity type by default, entity-specific markup forks |

## 5. Complete validation matrix

### Axis definitions

- **V-ALL:** 320, 390, 767, exact 768, 1280, wider desktop; 200% zoom/text enlargement at a desktop size; portrait/landscape where fixed chrome changes available height.
- **D0/D1/D2/D3:** empty / sparse / normal / dense-extreme. D3 includes 4-digit counts, long names/titles/locations/reviews, maximum histogram buckets, multi-page results, and localization-length pressure.
- **M0/M1/M2:** media present / absent / failed-hostile crop.
- **N0/N1/N2/N3/N4/N5:** initial loading / success / initial failure+Retry / continuation pending-failure-retry with content retained / mutation pending-success-error-conflict-auth-expiry / session lookup or logout failure.
- **I0/I1/I2/I3/I4:** rest-hover-focus-pressed / selected-current-disabled / open-Escape-outside-dismiss / keyboard traversal-commit / reduced motion and forced colors.

Every row below is run at V-ALL. “Applicable” axes are not optional omissions: they mean every state in the cell is crossed with all meaningful widths and interaction modes.

| Route | Required data/access/media states | Required network/state transitions | Required interactions and assertions |
|---|---|---|---|
| **R00 Global shell** | guest, verified, unverified; D0 shell; long handle; M0/M1 avatar | N0, N1, N5 session; logout N4 | I0–I4 nav/account/menu/logout; one feedback owner; focus not clipped; mobile 44px; no chrome overlap; footer per DEC-08 |
| **R01 `/` resolver** | guest/verified/unverified; legacy city query | N0, N1, N5; each redirect destination | Keyboard-accessible shell during transient; no duplicate status; query preservation; no persistent blank frame |
| **R02 Discover** | city missing/invalid/long; D0–D3 each tab/search; M0–M2 | N0–N3 for cities, each ledger, inline search independently | I0–I4 city menu/search/results/tabs/sentinel/Retry; rows retained; no cross-ledger reset; exact-768 alignment |
| **R03 Search** | blank/recent/1-char/2+; all/grouped/single scopes; D0–D3; M0–M2 | N0–N3 with cancellation/stale response | I0–I4 field/Clear/scopes/results/Load more; DEC-02 composition; event desktop spread; no judgment green |
| **R04 Home** | guest redirect; D0–D3 all six feed types; long actor/object/review; M0–M2 | N0–N3; retained feed on continuation failure | I0–I4 row/read-more/pagination/Retry; actor truncates before verb; operation-local recovery |
| **R05 Activity** | guest; D0–D3 all notification types; read/unread; long strings | N0–N4 initial/continuation/mark-read | I0–I4 whole rows, mark-read, Load more, Retry; actor-only emphasis; success clears unread styling; no double padding |
| **R06 Profile** | owner/public/private/pending/approved/follows-you/not-found; D0–D3 Been/Reviews/Favorites/stats; 4-digit counts; M0–M2 | N0–N4 independently for profile/stats/tabs/favorites/follow | I0–I4 Follow/Edit/tabs/sort/pagination/remove; DEC-07 sort state; fixed Follow dimensions; no overflow at 320/768; unavailable average not green |
| **R07 Settings/Profile** | guest; loaded fields empty/max/invalid; privacy states; D0–D3 requests; M0–M2 avatar | N0–N4 for load/save/upload/remove/request actions | I0–I4 fields/dropdown/radios/upload/Save/Cancel/request actions; errors remain field-local; 32px primary separation; no ledger leakage |
| **R08 Event** | invalid/not-found; upcoming/past; guest/owner; D0–D3 lineup/distribution/Circle/Public/attendees; M0–M2; WBT/rated/review variants | N0–N4 independently for detail, collections, rating/review/WBT/favorite/like/delete | I0–I4 StarInput, favorite, WBT, sort, expand, pagination, dialogs; DEC-03/04/05/07; missing art retains fallback; local actions preserve identity |
| **R09 Venue** | invalid/not-found; long/missing location; D0–D3 upcoming/past; M0–M2 | N0–N4 detail/favorite/two ledgers | I0–I4 location/favorite/rows/pagination/Retry; shared event-row spread; independent ledgers; no one-page pagination |
| **R10 Artist** | invalid/not-found; long name; D0–D3 upcoming/past; M0–M2 portrait | N0–N4 detail/favorite/two ledgers | I0–I4 favorite/rows/pagination/Retry; silhouette without shift; shared event-row spread; omitted current artist rule |
| **R11 Register** | pristine; every local/server error; long/autofill; privacy none/public/private | N1/N2/N4 submit | I0–I4 fields/radios/links/submit; no consequence before choice; field error ownership; production parity check |
| **R12 Login** | pristine; empty/invalid/non-enumerating failure; autofill | N1/N2/N4 submit | I0–I4 fields/links/submit; password-owned failure; target/focus; 32px primary separation |
| **R13 Verify** | generic/known email; partial/exact/invalid/expired code; terminal success | N1/N2/N4 verify/resend | I0–I4 code/Verify/Resend/Continue; terminal form removed; ellipsis/copy exact; footer per DEC-08 |
| **R14 Reset request** | pristine/invalid; non-enumerating confirmation; long destination | N1/N2/N4 request | I0–I4 form/Enter code/different email/login; exact security copy; confirmation replaces form |
| **R15 Reset confirm** | direct email/code/password steps; invalid/expired/mismatch; terminal success | N1/N2/N4 send/resend/set password | I0–I4 each field/action/escape path; terminal sole primary action; field errors; stable auth column |
| **R16 Legacy Been** | guest/signed-in; query/path variants | N0/N1/N5 session and redirect | Shell remains usable; destination is Login or canonical own profile per ruled behavior; no intermediate persistent screen |
| **R17 Not-found family** | generic/event/venue/artist/profile; malformed/missing keys; M0–M2 where identity slot applies | N0/N1/N2 distinction between not-found and recoverable failure | I0–I4 Return/Retry; functional title role; concise explanation; persistent shell; all variants share governed anatomy |

### Cross-matrix acceptance gates

1. **Geometry:** `document.scrollWidth <= document.clientWidth` at every V-ALL case unless an operator ruling explicitly authorizes a named local rail; content width must not decrease discontinuously as viewport width increases within one tier.
2. **Focus/targets:** visible 2px action focus on every keyboard target; no clipping by fixed chrome/overflow; named essential mobile actions measure at least 44×44 and all others satisfy the 24px floor/equivalent-control rule.
3. **Type/color/depth:** computed styles map to explicit roles; display type never leaks through bare headings; green appears only for available committed judgment; no unruled font/color/depth additions.
4. **State ownership:** initial, continuation, mutation, and session failures have distinct operation names, slots, and Retry functions. N3/N4 never removes successful stable content.
5. **Conditional composition:** M1 and conditional-control absence do not leave dead columns; absent and failed media use the same ruled fallback geometry.
6. **Density:** D3 never shrinks the semantic type role, clips required text/counts, collides with controls, or creates document overflow.
7. **Shell:** header/nav/account/footer decisions remain consistent across route transitions; mobile content reserves fixed chrome; public routes remain usable under N5 session failure.
8. **Parity:** source-built and deployed runs use the same fixture expectations, root token values, asset hashes, and untouched Register assertion. A passing source run cannot close a production defect.

## 6. Conflicts and duplicate proposals the problem architects must avoid

| Coordination rule | Overlapping diagnostics | Conflict to prevent |
|---|---|---|
| **C-01 — One role-system proposal** | LEAD-002/014; VIS-004/005/006/010; SPC-006/007 | Do not propose separate Search H1, Activity padding, Edit error, and mobile-target CSS patches. They are migrations from tag/location/whitelist styling to explicit roles. |
| **C-02 — One async-state proposal** | LEAD-003/004/010; VIS-001/002/007/008; SPC-008/012 | Do not create page-specific loading/error components with incompatible state schemas. Define ownership and phase once; pages supply operation copy/content. |
| **C-03 — One event-row family** | LEAD-005/013; VIS-015; SPC-004 | Do not let one architect standardize Search/Venue/Artist while another formalizes an unrelated Discover component. DEC-09 decides the variant boundary. |
| **C-04 — Responsive decision before local geometry** | LEAD-011; SPC-001/002/005/010/013 | Do not propose a breakpoint change in one report and component shrink/wrap assumptions in another. DEC-01 is upstream; DEC-02/03 are named exceptions after it. |
| **C-05 — Past-event order is not a spacing fix** | LEAD-006/007; VIS-012; SPC-003 | Do not use removal of whitespace, Sort, or a missing-art indent to smuggle in a past-event/community reorder. DEC-04/05/07 are separate rulings. |
| **C-06 — Permission behavior is not shell styling** | LEAD-009; VIS-002/003 | Do not treat redirect-vs-inline behavior or auth footer presence as consequences of a CSS shell primitive. DEC-06 and DEC-08 are product/visual decisions. |
| **C-07 — Deploy drift is not a source defect** | LEAD-001; VIS-017 | Do not submit a current-branch Register/token patch unless the exact audited source fails. Submit release-parity work under DEC-00 with separate source/live evidence. |
| **C-08 — Conditional composition has two governed cases** | LEAD-012; VIS-009; SPC-003/009 | Missing event art must retain its fixed fallback; non-owner action absence must release its column. Do not generalize “always preserve the slot” or “always collapse the slot” across both. |
| **C-09 — Profile corrections share one band** | VIS-011/016; SPC-001/009/013 | Do not independently add separators, shrink counts, recolor absence, or widen favorite rows. Preserve profile/statistics roles, solve capacity and conditional children together. |
| **C-10 — Activity needs semantic, state, and spacing migration together** | LEAD-008; VIS-006/007; SPC-007/008 | Do not close Activity after changing font weight alone; actor nodes, read-state reconciliation, row role, target size, and continuation slot must pass together. |
| **C-11 — No inventory inflation** | all findings; source controls that held | Do not propose new colors/fonts/cards/shadows/radii as a common “professionalism” layer. Such work is outside the findings and contradicts the current ruled foundation. |
| **C-12 — Decisions stay unresolved in architect proposals** | every DEC key | Problem architects may describe consequences and implementation dependencies, but must not label an option preferred, recommended, or implied by generic principles when handoffs conflict. |

## Closure rule

A lead problem closes only when its root diagnostic IDs pass the full applicable matrix on both the selected source artifact and the deployed artifact. A screenshot of one happy page, a unit test of one component, or a token diff alone cannot close a cross-system finding.
