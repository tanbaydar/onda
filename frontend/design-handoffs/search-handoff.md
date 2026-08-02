# SEARCH — incremental handoff (delta only; base system already integrated)
Approved as rendered 2026-08-01. Consumes ONLY existing tokens from frontend/design-tokens.css — zero new tokens, zero changes to integrated components. Visual truth: spec/search-wireframes.html · semantics: spec/SEARCH.md.

2026-08-01 operator delta: Search nav text routes directly to `/search` on every width. The desktop header quick-search auxiliary surface is withdrawn; Search page and Discover inline search are the only search surfaces. This supersedes the desktop-header clauses below.

## CHANGED (the only touches to existing chrome)
- Mobile tab bar: 4 → 5 tabs, Search at position 3: Home · Discover · Search · Activity · Profile. Same register (fn 12, muted / active ink 600).
- Desktop header nav: gains Search at position 3. Resting = quiet text like siblings; activating swaps it in place to an inline input (~320px, 1px `--border-strong`, pad 8 12, fn 14).
- Discover page: gains one quiet inline field beneath the city header (same input register, width 320 desktop / full mobile). NOTHING else on Discover moves.

## ADDED — Search page (new route, both widths)
- Bar = the page's primary object: 1.5px `--action` border, padding 16, fn 18 (primary-control register). Full-width mobile / 640px desktop. Page renders nothing below 2 chars.
- Scope row under the bar (margin-top 16): All · Events · Artists · Venues · People — side-by-side text, ui 14, gap 24, resting `--text-muted`, ACTIVE = ink + 600 (bold is the whole selection grammar; no underline, no dropdown). All = default.
- Live search ≥2 chars, ~250ms debounce. Loading: "Searching…" micro `--text-muted`. Empty: No results for "q". — ui `--text-secondary`.
- All scope → grouped list: EVENTS / ARTISTS / VENUES / PEOPLE as caps overlines (fn 12/500/+0.05em `--text-muted`, 32 above 12 below), max 5 rows per group, then micro link "View all (N)" when N>5 → sets that scope bold in place.
- Single scope → one list, no headers, standard cursor "Load more".
- Result row anatomies REUSE integrated components verbatim:
  · Event = EventListRow (56×70 thumb slot, empty slot holds x; mobile stack / desktop spread with right meta column)
  · Artist / Venue = display-face name (row-title token) + one micro muted context line (artist: "Artist"; venue: its city)
  · People = avatar 26 + fn 600 name + @handle micro muted
  · Whole row navigates; rows separated by `--border-muted` hairlines, padding 12.
- Keyboard: ↑/↓ across rows (headers skipped), Enter opens, Esc closes/clears.
- Search is chrome: zero `--judgment` color anywhere in search UI.

## ADDED — desktop header quick search (auxiliary)
Dropdown panel below the header input: width 480, `--bg`, 1px `--border-strong` outline, NO shadow (flat register). Same grouped content, same caps. Enter and "View all (N)" route to the Search page with the query.

## ADDED — Discover dropdown
Events only, scoped to the selected city. Panel overlays the city ledger (same panel register). Thin results (<3): tail row "Search all cities →" (micro link, `--border-muted` top hairline) routes to the Search page carrying the query.

## FLAGS for integration (unruled — do not invent)
1. Keyboard-focus row treatment: wireframes show a `--bg-subtle` wash; alternative is a 2px ink inset. Needs an operator ruling — pick neither silently.
2. Search corpus fixture: none exists in frontend/design-fixtures/ — add one before wiring live search; wireframe result rows beyond fixtures are flagged stand-ins.
