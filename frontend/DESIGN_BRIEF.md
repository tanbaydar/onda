# DESIGN_BRIEF.md — Onda, Milestone 4

## What Onda is
A social diary for dance-music events. Log nights, rate them, review
them, follow people. Letterboxd for the dancefloor — an event diary,
not ticketing, not a promoter site, not a listings guide.

## Direction (decided 2026-08-01, from 12-round taste session)
Editorial instrument on a pure white surface. Premium through
restraint and type, never through darkness or gloss.

## The allocation rule (core principle)
We present almost nothing but information; the failure mode is choice
overload. Every visual channel therefore has exactly one job:

- **Display type carries identity, not prose.** Loud, characterful
  display type is reserved for the skeleton: event names, artist
  names, venues, and big numerals. These are short and few. Review
  prose sets QUIET — comfortable reading size, generous measure,
  minimal chrome. Reviews are the loudest objects on the page by
  PLACEMENT and SPACE, never by font styling. Text volume is
  already loudness.
- **Color carries judgment.** Star ratings and likes are the ONLY
  colored interface elements. One accent color (two max). If it's
  colored, someone judged something. Nav, metadata, buttons: ink on
  white.
- **Imagery carries atmosphere.** Fliers and profile pictures are
  the only images. Give them real presence — no thumbnail apology.
  They are the only saturated objects on the page.
- **Space carries reviews.** Their prominence is positional: first
  in past-event hierarchy, uncrowded width, room to breathe.

Four channels, four jobs. Nothing else competes.

## Hierarchy inverts by event state
- **Past event:** reviews speak, ratings/likes glow, flier anchors.
- **Upcoming event:** flier, lineup, date/venue speak; the active
  WBT count takes the color slot — it is the only judgment signal
  an upcoming event has. No review chrome on events that cannot
  have reviews yet.

## Surface & type
- Pure cool white. Warmth enters only through fliers and avatars.
- Muted grayscale chrome; generous spacing.
- Dense in information, airy in layout: rich content, each element
  owns its space.
- Display type: loud and alive, but rationed — titles and numerals
  only. The louder the display face, the fewer places it may
  appear. Prose and functional type: quiet, legible, unremarkable.

## References (Mobbin taste session)
- Letterboxd — Film detail: page structure, diary mechanics
- Dice — event pages: typographic energy (in the skeleton only)
- Cosmos — channel/feed: white surface, spacing
- SSENSE — product pages: restraint, content-as-star

## Anti-goals
- Dark "premium tech" cliché: glass cards, gradients, glow
- Sterile fintech emptiness — white but bloodless
- Ticketing-site urgency: countdowns, badges, FOMO chrome
- Choice overload: equal-weight grids of everything
- Generic SaaS dashboard anatomy

## Frozen constraints
- Plain JavaScript/JSX. No TypeScript, no component library, no CSS
  framework unless a deliberate design-time decision reverses this.
- Responsive web app (mobile-heavy usage, desktop must hold).
- Design integrates over existing semantic markup — no speculative
  wrappers.
- Fixtures in frontend/design-fixtures/ are the data reality; check
  sparse AND dense variants. docs/recon/fixtures/ is ingestion
  input, not design data.

## Punch-list obligations (design must resolve)
- Event-page section order reflects event state (above).
- WBT count: prominent on upcoming, de-emphasized on past.
- Timestamp presentation: choose relative vs absolute once,
  globally (formatter is centralized in src/lib/formatTimestamp.js).

## Auth screens (design now, most ship in M5)
Eight states: register · login · check-your-inbox · verify success /
expired / already-used · reset request · reset form. Register asks
email, username, password — nothing else. Compose register/login so
a "Continue with Google" button could slot in later without
redesign. Tone: calm door-of-the-venue; no exclamation marks, no
bureaucratic error voice.
