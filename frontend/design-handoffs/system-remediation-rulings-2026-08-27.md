# SYSTEM REMEDIATION — operator rulings

Ruled 2026-08-27 by the current operator. Scope: the cross-system frontend remediation identified in `frontend/design-audits/2026-08-27-system-audit/`. This Markdown handoff is implementation authority and supersedes earlier handoffs only where a decision below expressly conflicts. It does not authorize backend, API, data, or ingestion changes.

## Approved decision register

- **DEC-00 — Promote the audited source baseline.** The audited source is the release baseline. Build, verify, deploy, and then prove source/live asset parity.
- **DEC-01 — Keep desktop chrome at 768px; use fluid content capacity.** The desktop shell activates at 768px. Page gutters become fluid and shared components activate width-demanding layouts from their available container capacity. Usable content width must remain monotonic.
- **DEC-02 — Search scopes use an intentional horizontal rail when constrained.** Preserve all five labels, gaps, and mobile targets. Show a visible continuation cue at narrow capacity and scroll a keyboard-focused scope fully into view.
- **DEC-03 — StarInput's selected value stacks below the stars when constrained.** Preserve the five-star geometry, half-step behavior, numeral, and 44px whole-star targets.
- **DEC-04 — Past events become judgment-led.** After a minimal title/art/date/venue/city identity summary, community judgment and reviews precede lineup and secondary listing detail.
- **DEC-05 — Public content precedes unavailable Circle content for guests.** The unavailable Circle module becomes one compact sign-in boundary after the usable Public collection.
- **DEC-06 — Protected whole pages redirect to Login with a return destination.** Mixed public detail pages remain visible and use local authentication boundaries. A successful login returns to the originally addressed protected route.
- **DEC-07 — Sort exists only for successful, non-empty collections.** It is absent during initial loading, initial failure, and successful empty states.
- **DEC-08 — Suppress the provenance footer on authentication routes.** The header remains persistent per the auth handoff; the footer exception applies to Register, Login, Verify Email, and both password-reset routes.
- **DEC-09 — Discover overlay uses a governed compact variant of the same EventRow presenter.** The compact variant may reduce amplitude and metadata density inside the panel, but it must share semantic slots, focus behavior, fallback media, and navigation with the standard presenter.

## System implementation contract

1. Visual meaning is selected explicitly. Identity titles, functional titles, section headings, ledgers, field-error lists, recovery actions, pagination actions, state slots, and social sentence parts may not derive their product role from a bare heading/list tag or a location-based selector.
2. Initial load, continuation, mutation, session bootstrap, and logout have separate state owners. A local action or continuation failure retains already successful identity and collection content and retries that named operation.
3. One EventRow presenter family owns event-result semantics. Search, Artist, Venue, Discover, the Discover overlay, Profile diary rows, and event-bearing Home feed objects consume governed variants rather than page-local row forks. The governed variant names are `standard-ledger`, `compact-overlay`, `profile-diary`, and `feed-object`.
4. Conditional layouts allocate only mounted semantic slots. A non-owner Favorites row has no action column. A fixed media slot keeps its ruled fallback; a deliberately collapsible identity slot may collapse only where the applicable handoff says so.
5. The Activity sentence renders actor, verb, object, time, and read status as separate roles. Successful mark-read bookkeeping reconciles local read styling immediately.
6. Green remains judgment-only. No new fonts, colors, shadows, cards, gradients, radii, or decorative depth are authorized.
7. Every recoverable error uses the `Retry` vocabulary, a local owner, and the essential mobile target role. Disclosure controls use the shared chevron grammar.
8. Generic and resource-specific not-found surfaces use a functional system-state title, a concise explanation, and a Return to Discover action.

## Dated delta — 2026-08-27 completion ruling

- Per the operator's instruction to finish every concrete outcome in the approved migration plan, the four EventRow variants above are one implementation family. Profile and Home retain their existing compositions and behavior; consolidation changes ownership only.
- A named system action role has precedence over component-local compact-button declarations. `recovery-action`, `pagination-action`, `menu-action`, `tab-action`, and the other governed target roles cannot be reduced below the universal target floor or the 44px mobile target by a page selector.
- The frozen acceptance inventory is `frontend/src/remediationAcceptance.js`. It covers route classes R00–R17, the six viewport capacities, and the ruled density, media, network, interaction, and text-enlargement state families.

## Release acceptance

- No document-level horizontal overflow at 320, 390, 767, 768, or 1280px on the governed routes; Search's named local scope rail is the only approved local horizontal overflow.
- Increasing the viewport through 767→768 does not reduce usable page content width.
- Successful rows/identity remain mounted during continuation and local-mutation pending/error states.
- Mobile recovery, pagination, tab, menu, follow, row-removal, and dialog targets are at least 44×44px. All keyboard-operable controls retain the ruled visible 2px focus treatment.
- Search, Event, Profile, Activity, auth, entity, empty, not-found, and dense fixtures pass source-built tests before deployment. Production root tokens and asset hashes match the verified source build after deployment.

## Dated operator override — 2026-08-27 event and Activity corrections

- DEC-04 remains judgment-led, but no longer moves lineup out of event identity. On past and upcoming events, lineup follows the identity metadata and precedes rating/community/review content.
- Owner review mutations live under the single `Edit ▾` disclosure: Edit review, Remove review when present, and Remove from Been. Remove rating is not an event-page menu item.
- Follow requests are an independently loaded disclosure module at the top of Activity and are absent from Edit Profile. Dated operator correction: a matching request notification also carries Approve/Delete while the request is pending, intentionally duplicating Instagram's two access points; resolving either instance removes the action controls from both while preserving the historical notification.
- Past event start times remain stored but are not rendered. Discover metadata is venue-first. Event detail always reserves the governed flyer/placeholder slot. Profile identity spacing follows the attached Instagram reference, while Been/Reviews placement follows the attached Letterboxd reference and retains Onda's existing tokens and product data.

## Dated operator override — 2026-08-29 collection flyers and owner controls

- This override supersedes the earlier 56×70 and 80×100 row-flyer sizes for the three named collections. Events, Profile Been, and Favorites all use one 68×85 flyer slot: the exact average of 80×100 and 56×70. Detail-page identity flyers, Search, and Home retain their existing sizes.
- The supplied `/assets/favorite-heart.svg` and `/assets/been-hand.svg` are repository assets and are the required artwork for the adjacent Favorite and Been controls on a rated past event.
- `Remove from Been` is owned only by the Been control beside Favorite. The owner review disclosure contains exactly `Edit review` and `Delete review`.
