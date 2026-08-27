# System remediation completion record

Date: 2026-08-27. Scope: the controlled design-system migration proposed after the R00–R17 audit and authorized by the operator through DEC-00–DEC-09. This file is evidence, not design authority; the Markdown files under `frontend/design-handoffs/` remain the sole visual authority.

## Outcome

The migration is implemented as a system correction rather than a page-by-page restyling. No new framework, palette, font, shadow, radius, card, gradient, or decorative layer was introduced. Backend behavior, API contracts, ingestion, and data rules were not changed.

## Historical plan reconciliation

| Proposed outcome | Status | Shipped evidence |
|---|---|---|
| 1. Decide DEC-00 through DEC-09 before dependent work | Complete | `frontend/design-handoffs/system-remediation-rulings-2026-08-27.md` records all ten operator rulings before the implementation baseline. |
| 2. Introduce explicit system primitives | Complete by ownership, not by an empty wrapper tree | Explicit title, ledger, field-error, action-target, feedback, system-state, conditional-composition, statistics, activity, and EventRow roles live in the existing component/CSS boundary. The suggested `frontend/src/ui/` names were illustrative; the plan explicitly prohibited a generic abstraction library. |
| 3. Replace selector-driven design semantics | Complete | Governed classes own identity/functional/section type, ledger rows, field errors, state slots, and target sizes. `systemRemediation.test.js` rejects the former broad selectors and ensures target roles outrank component-local compact rules. |
| 4. Separate asynchronous state by operation | Complete | Initial collection, continuation, mutation, session bootstrap, and logout feedback have distinct owners. Source tests prove retained successful content, local retry, stale-response handling, and operation-specific copy. |
| 5. Consolidate repeated content families | Complete | `EventRowPresenter.jsx` owns `standard-ledger`, `compact-overlay`, `profile-diary`, and `feed-object`; Activity sentence parts, Profile judgment availability, system not-found anatomy, image fallback, recovery, and pagination use governed shared roles. |
| 6. Implement responsive behavior by capacity | Complete | Fluid page gutter tokens, container queries, the exact 767→768 monotonic-capacity check, the narrow Search rail, narrow StarInput composition, conditional columns, and wide-desktop coverage are committed. |
| 7. Migrate in dependency order | Complete as one atomic delivery | The eight-PR list was a sequencing recommendation, not a product requirement. Authority, roles, state ownership, shared content, responsive capacity, route migrations, and production parity were delivered together so users never received a half-migrated foundation. |
| 8. Make acceptance mechanical | Complete | `remediationAcceptance.js` freezes R00–R17, 320/390/767/768/1280/1440 capacities, density/media/network/interaction families, and 200% text enlargement. Node and Playwright tests enforce the system contracts. |

## Final correction prompted by live review

The event title retains the approved Rozha One display role. Its date, venue, and lineup now share one existing information recipe: General Sans `--text-ui` (14px), weight 400, `--text-secondary`. The previous 500-weight date and 12px muted lineup treatment were removed. No new type style or token was created.

The expanded browser matrix also found that `.event-list-error button { min-height: 0 }` could outrank the semantic `recovery-action` role. The target-role selectors now carry system-level precedence, so page selectors cannot shrink Retry or other governed actions below 24px generally or 44px on mobile.

## Frozen acceptance inventory

- Route/surface inventory: R00–R17 in `frontend/src/remediationAcceptance.js`.
- Viewports: 320, 390, 767, 768, 1280, and 1440px.
- State families: empty, sparse, normal, dense/extreme; present, absent, and failed media; initial loading/error; continuation and mutation failure; hover and keyboard focus; selected, disabled, open, and dismiss; 200% text enlargement.
- Mechanical browser exemplars: public shell, Search, auth, event rows, failed media, dense text, initial/continuation recovery, target geometry, focus, local rail, and breakpoint monotonicity.
- Mechanical source coverage: authenticated and destructive flows, local mutations, Profile/Event/Activity/Edit Profile state continuity, auth completion, not-found anatomy, row-family ownership, judgment availability, and responsive role recurrence.

## Release evidence

The implementation commit, dependency lock hash, build command, generated asset hashes, CI result, deployment result, and exact live asset parity are recorded below.

- Implementation commit: `78dc1d2cdfd8f220379e08f84d31404044400fce`
- Dependency lock: `frontend/package-lock.json` SHA-256 `e6b76cdd5472eab7482b283c2506bf84d7109b9596af903ced912796bffd76a7`
- Build command: `cd frontend && npm run build`
- Generated source assets:
  - `dist/index.html`: SHA-256 `d2b9cf0849c24db3afbef4e095d2c8def796ac51a95f2a119f303ef59e052f63`
  - `dist/assets/index-cl5s7p3a.css`: SHA-256 `1e8b383a3d46395366c92432b1fff9d47ff53a54b4efec349c600dcf88b642cf`
  - `dist/assets/index-DrcFxRPc.js`: SHA-256 `833eabc57dcc1dc9a4bb85a29493c6b3f6ad134f1c1c73a848a9238046758c10`
- Source validation: 139/139 Node tests passed; production build passed; Playwright ran 84 project cases across six widths with 48 applicable passes, 36 expected not-applicable skips, and zero failures.
- CI: pending push
- Production deployment: pending merge and deployment
- Live asset parity: pending deployment
