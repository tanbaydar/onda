# DELTA — Discover redesign
Date: 2026-08-02 · Scope: full Discover page, both widths, guest + signed-in. Replaces all pre-system markup. Authority: this file.

## Header band (kills BROWSE CITY overline + "Discover" H1)
- City name IS the page title: display face, 30px desktop / 24px mobile, ink.
- Control pair, visually matched (1px `--border-strong`, padding 9×12, fn 14, radius 0):
  - City dropdown (existing custom component restyles to this register), value ink, chevron `--text-muted`. 220px desktop.
  - DiscoverSearch field (built), placeholder "Search events in {city}", `--text-muted`. 260px desktop.
- Desktop: title left, control pair right, baseline-aligned, gap 12 within pair. Mobile: title, then pair stacked full-width, 8px gap, 16px below title.

## Tabs
Upcoming/Recent in the ruled tab register: active ink 600 + 2px ink indicator overlapping the hairline; resting `--text-muted`; gap 24; no underlines. Future Q154 sections mount below the tab block; the band never changes.

## Event rows (Discover variant of EventListRow)
- Flier 80×100 (existing 4:5 size; NOT 56×70 — Discover is a primary imagery surface). `--image-slot` placeholder when absent (designed collapse, no icon).
- Event name: display face 20px desktop / 18px mobile, line-height 1.25, max 2 lines (`-webkit-line-clamp:2`), never underlined.
- Meta line: fn 14 desktop / 12 mobile — date compact per product grammar ("Thu 6 Aug, 10:00 pm") weight 500 `--text-secondary` · venue name 400. No "Venue:" label. Venue TBA renders muted.
- Lineup line: micro 12 `--text-muted`, listing order, 2–3 names then "+N" ("System Failure, Echotheism +1"). One line, no links inside the row. No "Artists:" label.
- Whole row navigates; hover bg none (hairline register); separators `--border-muted`; padding 16 vertical, gap 16.
- Desktop measure: centered 800 ledger (per Home centering ruling).
- Pagination: existing "Load more" grammar.

## Dated delta — 2026-08-20 discover continuation
- The visible "Load more" control is withdrawn. Reaching the end of the loaded ledger requests the next page automatically through an observed sentinel, preserving the current Upcoming/Recent ledger and scroll position.
- Continuation loading uses one quiet micro status line in the existing ledger slot. A failed continuation keeps every loaded row in place and offers Retry; it never clears the ledger.

## States
- Guest = signed-in composition, only the header chrome differs (auth cluster per auth-header-handoff.md; mobile guest has no tab bar).
- Judgment color: nowhere on Discover (no judgment data renders here).

## Flags
- FLAG: "Recent" tab content anatomy unruled (same row minus lineup? with avg rating?) — rendered structure assumes identical rows; ratings would introduce judgment color and need a ruling.
- FLAG: dropdown open-state styling inherits the DiscoverSearch dropdown register — assumed, not re-ruled.
