# PROFILE STATISTICS v3 — incremental handoff (delta; supersedes v2)
Correction pass 2026-08-01 — structure from v2 approved and unchanged (header F/F · five-item strip · baselines · widths · mobile rows). Two corrections:

## A. Histogram → data register IN THIS PLACEMENT (supersedes 160×100 here; standalone module spec in histogram-handoff.md is otherwise untouched)
- Sparkline-weight companion to the judgment numeral — never a co-equal figure.
- Bar area 30px tall × 104px wide; tallest bar tops out level with the adjacent "3.4"; axis row (½/5) sits on the strip's shared label baseline.
- SAME fixed size at both widths — never scales with its container.
- Internals unchanged: ten flex bars gap 2, uniform `--judgment`, hover/tap count tooltips. Zero-count stub: **1px** at this height (2px overwhelmed the reduced scale — render call, flagged).

## B. FollowControl — one fixed box, all states
- Follow / Unfollow / Request to follow / Requested: identical box — padding 8×16, fn 14/500, height 32px, min-width 150px (fitted to "Request to follow"), text centered, 1px `--border-strong`, `--text-secondary`.
- Zero dimension change or layout shift on state toggle. Proven in render: Unfollow (public profile) + Request to follow (private stub).

## 1. MOVE Followers / Following into the header (both widths, EVERY profile incl. private)
- Placement: inside the identity block, directly under the @handle/relationship line (margin-top 8), before the FollowControl.
- Register (quiet, identity-anchored): count fn 600 14px `--text` + label 11px caps +0.05em `--text-muted`, baseline-aligned pair, gap 6; two pairs, gap 16.
- Public visibility always — they render on the private stub too (between handle and Request to follow). They never appear in the statistics strip again.

## 2. STATISTICS strip → five items (module follows account privacy)
- Order: EVENTS IN BEEN (lead) · WRITTEN REVIEWS · VENUES VISITED · CITIES VISITED · judgment unit (AVERAGE RATING GIVEN `--judgment` + locked histogram attached, gap 12, axis on the label baseline).
- Reclaimed width spent on presence: secondaries scale 30 → **36px** (existing type-scale value) and gap 24 → **48** (--sp-48). Lead stays 60. Desktop sum ≈ 810px < 988 — zero scroll, zero clipping, still air to spare.
- Shared label baseline unchanged: flex row `align-items:flex-end`, numeral above / micro-caps label below (margin-top 4), labels nowrap.
- Section header STATISTICS keeps the caps overline.

## 3. Mobile 390 re-solve
- Header: F/F pairs as above.
- Strip rows (visible without scrolling, zero horizontal scroll):
  Row 1: Events in Been (48, lead) + Written reviews (24), gap 24
  Row 2 (mt 24): judgment unit — avg (24, `--judgment`; label wraps, max 2 lines, max-width 72px — the one nowrap exception) + histogram 160
  Row 3 (mt 24): Venues visited + Cities visited (24), gap 24
- Lead stat AND judgment unit both above the fold.

## Flags
- Zero-stub at 1px in the strip placement = render call within the ruling's latitude — veto if 2px preferred.
- "Requested" state copy/behavior unrendered (no fixture) — same fixed box, confirm copy at integration.
- Private-stub F/F counts: no private-profile follower fixture — counts are stand-ins; confirm the serializer exposes counts on private profiles (the ruling implies it must).
- 4-digit counts QA carries over (secondary at 36px: "1,204" ≈ 90px — still fits; verify at integration).

## Dated delta — 2026-08-27 compact placement ratification

- The 1px zero-count stub is ratified for the 104×30 profile sparkline placement. The standalone/event histogram retains its 2px stub.
- `Requested` is ratified for pending outbound follow requests, within the same fixed FollowControl box.
- Private stubs expose Followers and Following counts. The private design fixture now carries four-digit values so visibility, wrapping, and serializer expectations are covered in integration QA.
