# Onda full design-system compliance audit

> Diagnostic audit artifact dated 2026-08-27. This folder records evidence and proposals; it does not replace the binding Markdown handoffs in `frontend/design-handoffs/` and does not authorize product-behavior changes.

> Remediation status: DEC-00–DEC-09 were subsequently approved and implemented. Read [the completion record](07-remediation-completion.md) for the historical-plan reconciliation, final correction, test inventory, and release evidence. The findings below remain the original diagnostic baseline rather than a claim about current production.

## Bottom line

The professional-quality problem is structural, not a marketing, branding, or “make it prettier” problem.

Onda already has a deliberately narrow visual vocabulary in the current source: three role-specific typefaces, a controlled neutral palette, one judgment accent, a spacing scale, fixed content measures, and detailed page handoffs. The amateur feeling comes from places where the implementation stops obeying that vocabulary as a system:

- production is not serving the same ruled foundation as the audited source;
- visual roles are inferred from tags and selector whitelists instead of explicit primitives;
- functional headings inherit catalog-identity typography;
- local mutations, loading, continuation, and errors share replacement state and erase stable context;
- one breakpoint makes usable width shrink when the viewport grows;
- layouts keep columns for children that are not present;
- desktop event ledgers retain mobile anatomy and leave width without a scanning job;
- several genuine product/visual tensions have never received an operator ruling.

This is why isolated font, gray, padding, or whitespace edits would not solve the problem. The recurrence mechanism is in the ground rules and component/state architecture.

## Audit size and coverage

- **18 route/surface classes:** R00–R17.
- **Every routed screen:** global shell, landing resolver, Discover, Search, Home, Activity, profile Been/Reviews, Edit Profile, Event, Venue, Artist, Register, Login, Verify Email, both password-reset stages, legacy Been, and all not-found variants.
- **Interaction depth:** zero-touch pages through multi-step rating, review editing, confirmations, follow, favorite, Will Be There, menus, disclosures, filters, search, pagination, recovery, and auth flows.
- **State axes:** guest/authenticated, owner/other/private/pending/approved, loading/empty/sparse/dense/error/retry/continuation/mutation, media present/absent/broken, pagination, long/extreme content, and local permission boundaries.
- **Responsive axes:** 320, 390, 767, 768, 1280, wider desktop, plus zoom/text-enlargement implications.
- **14 lead problems:** semantic/design mismatches that describe user-visible system failures.
- **30 specialist root causes:** 17 visible-content findings and 13 spacing/composition findings.
- **Solution governance:** 18 consolidated no-go rules, 10 operator-decision gates, 8 root-first delivery phases, and an R00–R17 validation matrix.

The [complete route/state matrix](01-route-state-matrix.md) is the coverage contract. A route is not treated as reviewed merely because its default screenshot was inspected; its material child states are enumerated there.

## How to read this folder

1. [Route and state matrix](01-route-state-matrix.md) — every screen, access model, state, interaction, density, and viewport that belongs in the audit.
2. [Lead problems](02-lead-problems.md) — the 14 high-level semantic/design mismatches and their mapped root IDs.
3. [Visible-content root causes](03-visible-content-root-causes.md) — typography, labels, glyphs, color, media, content hierarchy, controls, feedback, and explicit rendered states.
4. [Spacing root causes](04-spacing-root-causes.md) — responsive geometry, rhythm, grids, containers, conditional whitespace, target sizing, and continuation slots.
5. [Foundations solution architecture](05a-solution-architecture-foundations.md) — LEAD-001–007 in the requested format: lead problem, technical explanation, solution proposals, no-go constraints, decisions, acceptance, and sequencing.
6. [Surface solution architecture](05b-solution-architecture-surfaces.md) — the same complete format for LEAD-008–014.
7. [Governance, decisions, and validation](06-governance-decisions-and-validation.md) — consolidated no-go registry, decision register, remediation phases, primitive boundaries, and regression matrix.
8. [Remediation completion](07-remediation-completion.md) — implementation reconciliation, frozen mechanical acceptance inventory, and source/production release evidence.

## What the three obvious symptoms actually mean

### “Too many fonts”

The source does not primarily fail because it loads three families. Those three are explicitly ruled for three different jobs: display identity, prose, and functional UI. The failure is that global `h1`/`h3` styling treats semantic tags as visual roles. Search, Activity, and failure headings can therefore receive the same display identity as an event or artist name. The system feels typographically inconsistent because role allocation leaks, not because the font count alone is excessive.

Relevant findings: LEAD-002, LEAD-014, VIS-004, VIS-005, VIS-006, SPC-007.

### “Too many colours”

The current source palette is relatively disciplined. The material failures are state and deployment problems: production still serves weaker muted/border values and lacks current focus/target tokens; unavailable profile judgment is colored like a committed rating; error/recovery ownership varies by component; and accent meaning can be applied by container rather than actual value state. Changing isolated grays would hide the cause.

Relevant findings: LEAD-001, LEAD-010, VIS-011, VIS-017, SPC-006.

### “Unutilized whitespace”

Most 640/800px measures are intentional and should not be widened merely to fill a monitor. The defective whitespace is the portion with no compositional job:

- the 767→768 transition reduces usable content width and lets component geometry break;
- missing event artwork leaves a 192px community-column indent;
- non-owner favorite rows reserve an absent owner-action column;
- desktop Search/Venue/Artist event rows span 800px but keep all metadata stacked at the left as if they were mobile rows;
- session errors can be double-inset inside an already centered ledger.

Relevant findings: LEAD-011, LEAD-012, LEAD-013, SPC-001–005, SPC-009, SPC-012, SPC-013.

## Lead problem register

| ID | Severity / class | Lead problem | Solution detail |
|---|---|---|---|
| LEAD-001 | High · Binding | Live production is not running the current ruled foundation. | [Foundations](05a-solution-architecture-foundations.md#lead-001--the-live-site-is-not-running-the-current-ruled-design-foundation) |
| LEAD-002 | High · Binding | Tag-based typography leaks catalog identity into functional and failure states. | [Foundations](05a-solution-architecture-foundations.md#lead-002--typography-is-assigned-by-html-tag-so-display-identity-leaks-into-functional-and-failure-states) |
| LEAD-003 | High · Binding | Local actions trigger whole-surface refetches and erase context. | [Foundations](05a-solution-architecture-foundations.md#lead-003--local-actions-are-implemented-as-whole-surface-refetches-erasing-context-and-hierarchy) |
| LEAD-004 | High · Binding | Loading/error branches remove stable page identity and spatial signature. | [Foundations](05a-solution-architecture-foundations.md#lead-004--loading-and-error-branches-remove-the-pages-identity-instead-of-preserving-its-spatial-signature) |
| LEAD-005 | Medium · Binding | Repeated rows and feedback jobs have multiple visual grammars. | [Foundations](05a-solution-architecture-foundations.md#lead-005--repeated-eventresultfeedback-semantics-are-copied-into-parallel-components-so-one-meaning-has-multiple-visual-grammars) |
| LEAD-006 | Medium · Principle/Decision | Empty or unavailable states keep controls/modules that cannot do useful work. | [Foundations](05a-solution-architecture-foundations.md#lead-006--empty-and-unavailable-states-keep-controls-or-modules-that-cannot-perform-useful-work) |
| LEAD-007 | High · Decision | The past-event template does not fully express the promised hierarchy inversion. | [Foundations](05a-solution-architecture-foundations.md#lead-007--the-past-event-template-does-not-fully-express-the-products-promised-hierarchy-inversion) |
| LEAD-008 | High · Binding | Activity flattens actor/action meaning and can retain stale unread styling. | [Surfaces](05b-solution-architecture-surfaces.md#lead-008--activity-flattens-notification-meaning-and-can-retain-stale-unread-styling) |
| LEAD-009 | Medium · Decision | Equivalent permission boundaries use inconsistent page models. | [Surfaces](05b-solution-architecture-surfaces.md#lead-009--equivalent-permission-boundaries-use-different-page-models) |
| LEAD-010 | Medium · Principle/Binding | Feedback ownership is fragmented across global/page/section/action layers. | [Surfaces](05b-solution-architecture-surfaces.md#lead-010--feedback-ownership-is-fragmented-across-global-page-section-and-action-layers) |
| LEAD-011 | Critical/High · Decision + Binding failures | Desktop geometry activates before it can fit. | [Surfaces](05b-solution-architecture-surfaces.md#lead-011--desktop-geometry-activates-before-it-can-fit) |
| LEAD-012 | High · Binding/Principle | Conditional children leave implementation-shaped whitespace. | [Surfaces](05b-solution-architecture-surfaces.md#lead-012--conditional-children-leave-implementation-shaped-whitespace) |
| LEAD-013 | High · Binding | Desktop event ledgers spend width without assigning it a scanning role. | [Surfaces](05b-solution-architecture-surfaces.md#lead-013--desktop-event-ledgers-spend-width-without-a-scanning-role) |
| LEAD-014 | High · Binding/Principle | Visual roles are encoded through tags and selector inventories instead of primitives. | [Surfaces](05b-solution-architecture-surfaces.md#lead-014--visual-roles-are-encoded-through-tags-and-selector-inventories-instead-of-primitives) |

## Root-first delivery order

The solution architecture deliberately does not prescribe a page-by-page repaint. The governed order is:

1. **Baseline and release parity.** Record current source/build/production values and decide whether the live/source mismatch is a missing deployment or an intentional production hold. Do not mix deployment drift with new design work.
2. **Explicit visual-role foundation.** Replace tag/location/whitelist semantics with role-bearing primitives for headings, ledgers, actions, recovery, pagination, and feedback.
3. **Async state ownership.** Separate initial load, continuation, and mutation state so successful content and identity remain mounted; define which layer owns each message and Retry.
4. **Shared content families.** Consolidate repeated event/result rows and make conditional layouts depend on their actual child set.
5. **Responsive contract.** Obtain the required breakpoint/narrow-composition decisions, then make width behavior monotonic and prove no overflow at the mandated widths.
6. **Route migration.** Move Activity, Search, Profile, Event, Venue, Artist, Discover, Home, and Edit Profile onto the new roles without changing their product rules.
7. **Decision-dependent hierarchy.** Implement past-event, guest-boundary, empty-sort, footer, and overlay choices only after explicit rulings.
8. **Build/deploy parity and recurrence gates.** Validate the same built asset users receive and keep the full route/state matrix in regression coverage.

The detailed dependencies and exit criteria are in [the governance phases](06-governance-decisions-and-validation.md#3-dependency-aware-remediation-phases).

## Operator decisions required before affected implementation — historical

These are genuine gray spaces. The audit records options and consequences without silently choosing:

- DEC-00 — whether source/production divergence is corrected by deployment or represents an intentional hold;
- DEC-01 — the responsive capacity contract at and above 768px;
- DEC-02 — how five Search scopes fit at 320px while preserving target size;
- DEC-03 — how StarInput fits at 320px/high zoom;
- DEC-04 — the past-event reading order;
- DEC-05 — placement of unavailable guest-personalized modules relative to public content;
- DEC-06 — the direct-access permission model;
- DEC-07 — whether Sort appears before a successful non-empty collection exists;
- DEC-08 — footer presence on authentication routes;
- DEC-09 — whether the Discover overlay uses the shared event-row role or a separately ruled compact variant.

The mutually exclusive options are in the [operator decision register](06-governance-decisions-and-validation.md#2-operator-decision-register). All ten were later approved; the binding choices are in `frontend/design-handoffs/system-remediation-rulings-2026-08-27.md`.

## No-go summary

Until a later operator ruling changes an authority, implementation must not:

- change shipped backend behavior, API contracts, product rules, route destinations, or permission outcomes as a side effect of design work;
- treat this diagnostic folder as higher authority than `frontend/design-handoffs/*.md`;
- fix production drift by inventing new token values or bypassing the audited build artifact;
- solve role leakage with more page-local overrides while leaving tag/selector semantics intact;
- clear successful content for continuation or local mutation feedback;
- widen every page to fill the viewport or remove the ruled 640/800px measures;
- shrink essential targets below the mobile accessibility floor merely to make a row fit;
- remove ruled media fallbacks, identity anatomy, or recovery behavior to simplify geometry;
- choose a new breakpoint, past-event order, permission model, auth footer policy, or compact-row grammar without the explicit decision recorded for it;
- certify only default screenshots while omitting dense, empty, error, pagination, missing-media, keyboard, zoom, and exact-breakpoint states.

The complete 18-rule register is in [governance](06-governance-decisions-and-validation.md#1-consolidated-no-go-registry).

## Evidence boundary

Public production routes were inspected read-only at `https://ondaapp.io`. Protected, owner, mutation, confirmation, and populated social states were exercised against the local application with a disposable local-only audit account. Dense, private, continuation, and hostile-content states were verified through shipped source, tests, and the repository's real-response design fixtures rather than by mutating live data.

No application code, design handoff, backend behavior, API contract, or product rule was changed by this audit.
