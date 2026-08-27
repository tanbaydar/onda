> Diagnostic audit artifact. It records evidence and proposals; it does not replace the binding Markdown handoffs in `frontend/design-handoffs/` and does not authorize product-behavior changes.

# Spacing and Root-Composition Audit

## Audit contract

- **Scope:** the complete R00–R17 route/state matrix in `01-route-state-matrix.md`, including 320, 390, 767, 768, 1280, wider-desktop, and 200%-zoom implications.
- **Authority order:** binding repository handoffs and design contract first; `refactoring-ui-for-agents` principles only where they do not conflict with a handoff; operator decisions are called out where the authorities themselves create a constraint collision.
- **Method:** read-only rendered inspection of representative public/authenticated states, plus source, tests, and fixtures for protected, destructive, empty, error, continuation, dense, and extreme-content states. No live data was mutated.
- **Output boundary:** diagnostic root causes only. This report deliberately does not prescribe final solutions.

## Prioritized root-cause index

| ID | Class | Severity | Root cause | Principal route classes |
|---|---|---:|---|---|
| SPC-001 | BINDING | Critical | Desktop profile statistics are wider than their layout band at the exact 768 breakpoint | R06 |
| SPC-002 | DECISION | High | The fixed 768/106px-gutter contract produces a non-monotonic content-width cliff | R00, R02–R10, R17 |
| SPC-003 | BINDING | High | Missing event artwork does not release the desktop community-section indent | R08 |
| SPC-004 | BINDING | High | Shared compact event ledgers never acquire the required desktop row spread | R03, R09, R10 |
| SPC-005 | DECISION | High | Search's five-scope row cannot satisfy all narrow-screen constraints simultaneously | R03 |
| SPC-006 | BINDING | High | Mobile recovery/pagination target sizing is implemented as a brittle selector whitelist | R03–R10, R17 |
| SPC-007 | BINDING | High | Global list-item ledger CSS leaks into unrelated activity and validation lists | R05, R07 |
| SPC-008 | BINDING | High | Continuation state is modeled as page replacement or an upstream error, not a stable local slot | R04–R10 |
| SPC-009 | PRINCIPLE | Medium | Non-owner favorites retain an absent owner's action column | R06 |
| SPC-010 | DECISION | Medium | The ruled star-input geometry cannot fit the 320px content ledger | R08 |
| SPC-011 | BINDING | Medium | Auth primary-action separation resolves to 24px instead of the specified 32px | R11–R15 |
| SPC-012 | PRINCIPLE | Medium | Session failure messaging is double-inset from the page ledger on desktop | R00 and all signed-in routes |
| SPC-013 | BINDING | High | Profile social counts are forced into a fixed single line that cannot contain required 4-digit fixtures | R06 |

## Findings

### SPC-001 — Desktop profile statistics overflow their layout band at 768px

- **Classification / severity:** BINDING / Critical.
- **Observed condition:** at exactly 768px, `/u/codex.design.audit` has `documentElement.clientWidth = 768` and `scrollWidth = 774`. `.profile-statistics` is `x=12, width=744, scrollWidth=762`; its final child ends at `x=774`. The overflow is present with ordinary live values before applying the required dense histogram and 4-digit-count fixtures.
- **Consequence:** the breakpoint creates document-level horizontal scrolling and clips the statistics strip at the first desktop width. Dense rating bins, longer values, and 200% zoom increase the failure. The page's primary ledger remains `x=106..662`, so the strip also abandons the page alignment system at the same transition.
- **Binding authority:** `frontend/design-handoffs/stats-handoff.md:19-30` requires the desktop statistics treatment and zero horizontal scroll on the mobile/narrow treatment; `frontend/DESIGN_CONTRACT.md:167,190,726` defines minimum-width, no-horizontal-scroll, and breakpoint QA obligations. The route matrix explicitly requires exact-768, dense-histogram, and horizontal-overflow review.
- **Evidence:** `frontend/src/styles.css:443-451` (`.profile-statistics` negative margins, max-content children, fixed inter-item spacing); live R06 owner profile, 768px.
- **Root cause:** the desktop strip combines `width:auto`, negative lateral margins, max-content statistics, and fixed 48px gaps inside a 744px available band. The desktop composition assumes materially more width than the breakpoint actually supplies.
- **Blast radius:** R06 owner/non-owner/public/private profiles; sparse and dense stats; 768-class tablets, narrow desktop windows, and zoomed desktop.

### SPC-002 — The 768px breakpoint creates a content-width cliff

- **Classification / severity:** DECISION / High.
- **Observed condition:** the global ledger is approximately 719px wide at 767px (`24px` side gutters) but only 556px wide at 768px (`106px` side gutters). On Discover at 768px, the content ledger is `x=106..662`, while the city/search control group is `x=216.35..708.35`, bleeding 46px into the right gutter. The DOM does not scroll there only because the overflow remains inside the viewport.
- **Consequence:** adding one viewport pixel removes roughly 163px of usable content. Pages become visually less stable as they grow, controls detach from headings/ledgers, and the desktop geometry starts before its fixed-width compositions have room.
- **Authority tension:** `frontend/design-tokens.css:22-24` and `frontend/DESIGN_CONTRACT.md:187-188,300` bind grouping and the 800px desktop ledger; `frontend/src/styles.css:395-415` and the handoffs bind the 768 transition and 106px desktop gutters. `refactoring-ui-for-agents/03-layout-and-spacing` requires responsive behavior to be monotonic and fixed/fluid choices to be intentional. These constraints cannot all hold at 768 without an operator ruling on breakpoint, gutter, or intermediate composition.
- **Evidence:** `frontend/src/styles.css:28,385-415`; `frontend/src/discover.css:25-30`; live R02 Discover at 768px; comparative source geometry at 767px.
- **Root cause:** a single hard breakpoint changes both the gutter system and several component compositions, with no intermediate-width contract.
- **Blast radius:** the R00 shell and nearly every content route R02–R10/R17; strongest where rows, controls, statistics, or secondary columns activate at the same breakpoint.

### SPC-003 — Missing event art leaves a permanent unrelated indent

- **Classification / severity:** BINDING / High.
- **Observed condition:** on `/e/gravagerz-2284` at 1280px, the missing-art event identity, title, metadata, lineup, and owner controls use the full content ledger `x=240..1040` (800px). The first community section begins at `x=432` and is 608px wide, leaving a 192px empty column even though no artwork occupies or explains it.
- **Consequence:** the page's semantic hierarchy splits into two left edges, and high-value review/community content is compressed while functional whitespace becomes dead whitespace. The discontinuity is most conspicuous precisely in the missing-art state the matrix requires.
- **Binding authority:** `frontend/design-handoffs/event-handoff.md:32` requires reviews/community to align to the desktop content column; `frontend/DESIGN_CONTRACT.md:400,686` requires event sections to align and community sections not to introduce unrelated edges.
- **Evidence:** `frontend/src/styles.css:421-430` (`.event-community-section` always receives `max-width:608px; margin-left:192px` at desktop); live R08 upcoming event with missing artwork, 1280px.
- **Root cause:** the secondary-column offset is keyed only to viewport width, not to whether the artwork column actually exists.
- **Blast radius:** R08 missing-art events at desktop and wider desktop; the misalignment persists through reviews, attendee/community modules, and their local states.

### SPC-004 — Compact event ledgers do not spread on desktop

- **Classification / severity:** BINDING / High.
- **Observed condition:** on `/a/gravagerz-3494` at 1280px, each event row spans `x=240..1040` (800px), but uses only a 56px thumbnail plus a single copy column beginning at `x=308`; date and venue remain stacked beneath the title. The full right portion of the ledger has no compositional role.
- **Consequence:** desktop venue, artist, and event-search results look like enlarged mobile rows. Scan-critical date/location metadata does not form a consistent right-hand column, and the wide ledger reads as unutilized whitespace rather than calm structure.
- **Binding authority:** `frontend/design-tokens.css:120` requires desktop `EventListRow` to spread across the available row; `frontend/design-handoffs/search-handoff.md:18` explicitly requires desktop event-result spread; `frontend/design-handoffs/artist-handoff.md:14-21` and `frontend/design-handoffs/venue-handoff.md:15` bind the compact shared ledger and responsive composition.
- **Evidence:** `frontend/src/components/EventList.jsx:84-104`; `frontend/src/discover.css:1-31` (compact row composition has no desktop spread rule); live R10 artist detail, 1280px. The same component is used by R09 and event results in R03.
- **Root cause:** one mobile-first two-column row is reused at all widths without a desktop metadata region or desktop grid-template change.
- **Blast radius:** R03 event search results, R09 venue events, R10 artist events; sparse, dense, paginated, and long-metadata states.

### SPC-005 — Search's scope row has an unresolved narrow-screen constraint collision

- **Classification / severity:** DECISION / High.
- **Observed condition:** at 320px, `.search-scopes` has `clientWidth=272` and `scrollWidth=316`. Five 44px targets with the ruled 24px separation run from `x=24` to `x=340`; the People scope is outside the viewport. The row scrolls horizontally, but the rendered state provides no persistent affordance that another scope exists.
- **Consequence:** a primary result type is visually absent at first render, keyboard/focus movement can occur into a clipped region, and the route fails the matrix's no-horizontal-overflow expectation even though the overflow is locally contained.
- **Authority tension:** `frontend/design-handoffs/search-handoff.md:11-15` binds the single-line scope row and its hierarchy; `frontend/design-handoffs/accessibility-handoff.md:21` and `frontend/DESIGN_CONTRACT.md:167,190,586-588` bind narrow-screen fit and 44px mobile actions; `frontend/src/styles.css:63` implements the 24px gap and horizontal scroll. At 272px content width, those simultaneous constraints are geometrically incompatible, so the narrow recomposition requires an operator ruling.
- **Evidence:** `frontend/src/styles.css:60-66,385-391`; live R03 Search, 320px.
- **Root cause:** the scope model has no declared narrow-width compression or alternate composition; overflow is being used as an implicit fallback.
- **Blast radius:** R03 at 320px, long localized labels, text scaling, and 200% zoom.

### SPC-006 — Recovery and pagination sizing depends on a selector whitelist

- **Classification / severity:** BINDING / High.
- **Observed condition:** the baseline button minimum height is 34px. The mobile rule raises only an enumerated set of selectors to 44px. Classless pagination buttons and generic `.quiet-control` recovery actions fall through to 34px, including Activity recovery/load-more, profile submodule recovery, edit-profile follow-request pagination, event attendee/review pagination, and not-found recovery. New local recovery states inherit the defect unless manually added to the list.
- **Consequence:** the same action role has two target sizes depending on DOM location and class naming. Error and pagination states—where precision and accessibility matter most—become less usable than the successful state.
- **Binding authority:** `frontend/design-handoffs/accessibility-handoff.md:21` requires 44×44 mobile pagination/recovery actions; `frontend/DESIGN_CONTRACT.md:167,586-588` repeats the mobile-width and target rule.
- **Evidence:** `frontend/src/styles.css:15,384-391`; `frontend/src/pages/ActivityPage.jsx:107-112,130-134`; `frontend/src/pages/EditProfilePage.jsx:18-20,107-110`; `frontend/src/components/PublicReviews.jsx:67-73,87-107`; `frontend/src/components/WillBeThereAttendees.jsx:53-59,76-94`; `frontend/src/App.jsx:36-41`. Search's `.search-load-more` and Home's generic Retry likewise are not members of the mobile selector set.
- **Root cause:** action-role semantics are encoded as an incomplete CSS selector inventory rather than as a shared pagination/recovery primitive or role-bearing class.
- **Blast radius:** R03–R10 and R17; initial, empty, continuation-error, and multi-page states at 320/390/767 and zoomed layouts.

### SPC-007 — Global list CSS leaks into unrelated list semantics

- **Classification / severity:** BINDING / High.
- **Observed condition:** every direct `main > ul/ol > li` receives a border and 16px padding. Activity then adds another 16px inside `.activity-row`, producing 32px of lateral inset per side before row content. Edit-profile field-error `<ul>` elements receive ledger borders and 16px item boxes instead of staying attached to the field at the intended 6px separation.
- **Consequence:** Activity density is artificially low and repetitive; validation feedback reads like a separate content card/list rather than part of the failed field. Both symptoms come from the same semantic mismatch, not isolated padding values.
- **Binding authority:** `frontend/design-tokens.css:22-24` requires spacing to express grouping and fields/sections to use the correct semantic unit; `frontend/DESIGN_CONTRACT.md:403` defines Activity as one continuous ledger; `frontend/design-handoffs/profile-handoff.md:28-37` binds Edit Profile to the auth-column/form register, whose field-local error anatomy is ruled by `frontend/design-handoffs/auth-handoff.md:13-17`.
- **Evidence:** `frontend/src/styles.css:31-32,194-203`; `frontend/src/pages/ActivityPage.jsx:120-134`; `frontend/src/pages/EditProfilePage.jsx:92,118,121-124`. Live R05 was empty, so row geometry was verified from the exact rendered component/CSS path; edit error states were verified from source/fixtures as permitted by the matrix.
- **Root cause:** element-location selectors (`main ol/ul > li`) assign visual semantics to all lists, then feature CSS adds a second component layer without neutralizing the inherited ledger treatment.
- **Blast radius:** R05 non-empty/sparse/dense Activity and R07 request/global/field-error states; future direct lists under `main` are exposed to the same leak.

### SPC-008 — Continuation failures do not preserve a stable local slot

- **Classification / severity:** BINDING / High.
- **Observed condition:** multiple data modules clear successful content when a subsequent page starts or fails, or render the continuation error above the retained ledger rather than in the control's slot:
  - Home's catch writes a page-level error and Retry restarts the initial effect, clearing results.
  - Activity retains rows but renders `actionError` before the list, moving the ledger and separating the message from Load more.
  - the shared detail `EventList` sets `data:null` on page changes/failures.
  - `YourCircle`, `WillBeThereAttendees`, and `PublicReviews` replace prior successful data during pagination/failure.
  - profile Been/Reviews page changes replace their successful page rather than reserving the pagination region.
- **Consequence:** content jumps or disappears during ordinary pagination; error messages change the top-level page anatomy; recovery cannot be understood as local to the failed continuation. The same conceptual state has inconsistent height and placement across routes.
- **Binding authority:** `frontend/design-tokens.css:156` requires loading/error to use the same slot; `frontend/design-handoffs/accessibility-handoff.md:28`, `frontend/design-handoffs/discover-handoff.md:25`, and `frontend/DESIGN_CONTRACT.md:384,392,616` require successful content to remain mounted and continuation recovery to stay local. Discover implements the required separation and demonstrates that the rule is intentional rather than aspirational.
- **Evidence:** `frontend/src/pages/HomePage.jsx:61-79,89-96`; `frontend/src/pages/ActivityPage.jsx:72-86,104-134`; `frontend/src/components/EventList.jsx:52-63,115-138`; `frontend/src/components/YourCircle.jsx:27-39,75-107`; `frontend/src/components/WillBeThereAttendees.jsx:24-36,53-94`; `frontend/src/components/PublicReviews.jsx:25-38,67-107`; `frontend/src/pages/ProfilePage.jsx:28-60`.
- **Root cause:** initial-load state and continuation state share one data/error object in most modules. Rendering therefore has no stable, component-local continuation slot independent of successful content.
- **Blast radius:** R04 Home, R05 Activity, R06 Profile, R07 follow requests, R08 event community/reviews, R09 Venue, and R10 Artist; loading, page-two, exhausted, and continuation-failure states.

### SPC-009 — Non-owner favorites reserve an absent action column

- **Classification / severity:** PRINCIPLE / Medium.
- **Observed condition:** on `/u/tan` at 390px, each `.profile-favorite-list > li` uses `grid-template-columns: 56px 210px 44px`. Because the viewer is not the owner, JSX omits `FavoriteControl`; the 44px third column plus its preceding 16px gap remain empty. The useful title/link region ends around `x=306` while the row continues to `x=366`.
- **Consequence:** 60px of every narrow favorite row is non-functional whitespace, forcing earlier truncation of the content the row exists to communicate.
- **Principle authority:** `refactoring-ui-for-agents/03-layout-and-spacing` requires whitespace to perform a grouping/hierarchy job and warns against fixed dead zones; no handoff requires reserving an owner-only control for non-owners.
- **Evidence:** `frontend/src/styles.css:270-278`; `frontend/src/pages/ProfilePage.jsx:89-105`; live R06 non-owner profile, 390px.
- **Root cause:** the grid template is invariant while the semantic child set is conditional.
- **Blast radius:** R06 non-owner profiles at all widths, strongest at 320/390, with long venue/artist/event names and text scaling.

### SPC-010 — Star input cannot fit its ruled 320px ledger

- **Classification / severity:** DECISION / Medium.
- **Observed condition:** in the past-event editor at 320px, `.star-input-wrap` is `x=24, width=272, scrollWidth=280`; the five-star control occupies about 244px and the numeric output begins at `x=280`, ending at `x=304`, 8px beyond the content ledger's right edge. The wrapper is `nowrap`, so selecting/editing introduces an edge bleed and a local composition shift.
- **Consequence:** the interactive state is less aligned than the read state and has no remaining width for larger numerals, localization, or 200% zoom.
- **Authority tension:** the event handoff binds the five-star geometry and requires the value beside the stars, while the global narrow ledger binds 24px gutters and usable width. Those exact dimensions do not fit together at 320px; placement or geometry requires operator judgment.
- **Evidence:** `frontend/src/styles.css:175-184`; event-editor JSX in `frontend/src/pages/EventPage.jsx`; live R08 `/e/elysium-corruption-2280`, Edit state, 320px.
- **Root cause:** the input uses fixed hit-area/icon geometry plus a fixed adjacent output inside a non-wrapping row, with no narrow-state composition.
- **Blast radius:** R08 authenticated past-event create/edit states at 320px, high zoom, and larger text.

### SPC-011 — Auth primary action is only 24px from the final field

- **Classification / severity:** BINDING / Medium.
- **Observed condition:** live Login at 390px measures 24px from the final field block to the primary action. The same shared auth CSS is used by Register, Verify, Reset request, and Reset confirm.
- **Consequence:** the primary commitment is grouped like another field instead of receiving the stronger section break specified by the handoff. The form hierarchy is weakened consistently across all auth states.
- **Binding authority:** `frontend/design-handoffs/auth-handoff.md:10` requires the primary button 32px above; its chrome-reservation requirements are otherwise met.
- **Evidence:** `frontend/src/styles.css:345-356` (`.auth-field { margin-bottom:24px }`; `.auth-primary { margin-top:8px }`); live R12 Login, 390px. Margin collapsing resolves the intended additive values to the larger 24px margin, not 32px.
- **Root cause:** adjacent vertical margins are being used as if they add; CSS margin collapse selects one of them.
- **Blast radius:** R11–R15, including validation, pending, expired, mismatch, success, and prefilled-link states.

### SPC-012 — Session failure content is double-inset from the desktop ledger

- **Classification / severity:** PRINCIPLE / Medium.
- **Observed condition:** `.session-error-slot` is centered at max-width 800px and then receives the same 106px horizontal padding used by the page shell. At 1280px, the page ledger begins at `x=240`, while the session message begins around `x=346`, creating a second unexplained left edge and reducing the message measure to roughly 588px.
- **Consequence:** the highest-level signed-in recovery state does not align with the header or content ledger and spends scarce error-state space on nested gutters rather than message/action grouping.
- **Principle authority:** `frontend/design-tokens.css:22-24` requires shared grouping/alignment; `refactoring-ui-for-agents/03-layout-and-spacing` requires nested containers not to create arbitrary dead zones. No design handoff requires a second inner gutter for this slot.
- **Evidence:** `frontend/src/styles.css:108-118,395-415`; R00 session-loading/failure source path in `frontend/src/App.jsx:64-99`.
- **Root cause:** a component that already owns an 800px centered container also applies page-level gutters internally.
- **Blast radius:** R00 signed-in session failure and every protected route gated through it, especially 768/1280 and zoomed desktop.

### SPC-013 — Required 4-digit social counts cannot fit the fixed profile identity row

- **Classification / severity:** BINDING / High.
- **Observed condition:** at 320px the profile header allocates 184px to identity copy after a 72px avatar and 16px gap. `.profile-social-counts` is forced to one non-wrapping line. Even the live owner values `0 FOLLOWERS 0 FOLLOWING` measure about 186px (`scrollWidth`) in that 184px column. The required private-profile fixture uses `1204` followers and `1048` following, adding substantial width and forcing the line into the right gutter/document edge.
- **Consequence:** the extreme state required by the matrix creates clipping/overlap or document horizontal overflow before any localization or 200% zoom. It also makes privacy-state geometry differ from ordinary public states.
- **Binding authority:** the route matrix explicitly requires private profiles with 4-digit counts and zero horizontal scroll; `frontend/design-handoffs/stats-handoff.md:14-17,36-43` binds the identity/count content and the four-digit QA state; `frontend/DESIGN_CONTRACT.md:167,190,726` disallows narrow horizontal overflow.
- **Evidence:** `frontend/src/styles.css:234-240`; `frontend/src/pages/ProfilePage.jsx:144-162`; `frontend/design-fixtures/profile-other-private.json` (`follower_count:1204`, `following_count:1048`); live R06 owner profile measurement at 320px establishes the baseline overflow before the fixture expansion.
- **Root cause:** fixed avatar/copy columns and `white-space:nowrap` assume short counts, while the test contract explicitly requires 4-digit values.
- **Blast radius:** R06 private/public owner/non-owner headers at 320/390, localized labels, large counts, and text scaling.

## Coverage ledger

The ledger records every route class from the shared matrix. “No independent root” means the route was reviewed and either inherits a cross-route finding or did not reveal a separate spacing/composition cause.

| Route | Reviewed states and viewport axes | Result |
|---|---|---|
| R00 Global shell | signed out/in, session loading/failure, mobile/desktop/zoom source paths | SPC-002, SPC-012 |
| R01 Landing | signed-out render, signed-in redirect, 320/390/768/1280 composition | No independent root; shell/breakpoint inheritance only |
| R02 Discover | city query, loading/success/empty/continuation/error/exhausted; 320 and exact 768 rendered, wider/source checked | SPC-002; Discover's local continuation slot itself complies |
| R03 Search | blank/query, all scopes, empty/error/load more/long labels; 320 and desktop/source checked | SPC-004, SPC-005, SPC-006 |
| R04 Home | signed-out redirect, sparse/dense/empty/initial and continuation failure; narrow/desktop source checked | SPC-006, SPC-008 |
| R05 Activity | empty live state plus non-empty/dense/initial/continuation source states; narrow/desktop checked | SPC-006, SPC-007, SPC-008 |
| R06 Profile | owner/non-owner/private/not-found, 4-digit counts, dense stats, favorites and paginated modules; 320/390/exact 768/desktop | SPC-001, SPC-006, SPC-008, SPC-009, SPC-013 |
| R07 Edit profile | initial/success/validation/global error, follow requests empty/loading/paginated/error; narrow/desktop source checked | SPC-006, SPC-007, SPC-008 |
| R08 Event detail | upcoming/past, missing art, owner/editor, reviews/attendees/community, pagination/errors; 320 and 1280 rendered | SPC-002, SPC-003, SPC-006, SPC-008, SPC-010 |
| R09 Venue | identity, missing art, empty/sparse/dense/paginated/error event ledger; narrow/desktop checked | SPC-002, SPC-004, SPC-006, SPC-008 |
| R10 Artist | identity, missing art, empty/sparse/dense/paginated/error event ledger; 1280 rendered, narrow/source checked | SPC-002, SPC-004, SPC-006, SPC-008 |
| R11 Register | default/validation/submitting/success and long copy; 390 rendered/shared source checked | SPC-011 |
| R12 Login | default/error/submitting and redirects; 390 rendered/shared source checked | SPC-011 |
| R13 Verify email | pending/success/invalid/expired/retry; shared auth narrow/desktop source checked | SPC-011 |
| R14 Reset request | default/validation/submitting/success; shared auth narrow/desktop source checked | SPC-011 |
| R15 Reset confirm | valid/invalid/expired/mismatch/submitting/success; shared auth narrow/desktop source checked | SPC-011 |
| R16 Legacy Been | redirect and query preservation path | No independent root; no persistent screen is rendered |
| R17 Not found | missing route/entity recovery, narrow/desktop shell checked | SPC-002, SPC-006 |

## Diagnostic conclusion

The layout does not suffer from a collection of unrelated “too much whitespace” values. Most visible spacing defects trace to five systemic causes: a breakpoint that activates before its desktop geometry fits; component layouts that do not react to conditional children/content; role semantics expressed through global elements or selector whitelists; initial and continuation states sharing one replacement model; and fixed-width/no-wrap assumptions that contradict required extreme-content fixtures. Those roots explain the amateur-looking inconsistency more accurately than isolated pixel adjustments.
