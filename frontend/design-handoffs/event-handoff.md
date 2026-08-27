# EVENT PAGE — incremental handoff (delta; base system already integrated)
Ruled 2026-08-01. Zero new tokens — all values from frontend/design-tokens.css. Visual truth: spec/event-owner-block.html.

## 1. REPLACE the native rating <select> with StarInput (register 18 closed)
- Ten-step control: 5 star glyphs, 32px, gap 6 (whole-star hit ≥44px with padding).
- Input: tap/click left half of a star = .5, right half = full; drag scrubs continuously; keyboard ←/→ steps 0.5 (range 0.5–5.0); Enter commits. A11y: role="slider", aria-valuemin 0.5, aria-valuemax 5, aria-valuenow, step announced as 0.5.
- Rendering: unselected = outline glyph ☆ `--text-muted`; selected = filled ★ `--judgment`; half = judgment fill clipped at 50% over a muted outline. Never a native form control.
- Chosen value renders beside the stars: numeral-sm token, `--font-display`, `--judgment` (e.g. 3.5). Absent until a value exists.
- Selecting a value creates the Been entry (composer state b). Rated viewers do NOT see the input here — their entry lives in the review column marked "Yours" with the single "Edit ▾" affordance (locked).

## 2. COLLAPSE the five caps sections into ONE owner block
Kill the per-item overlines (WBT ATTENDANCE / FAVORITE / RATING AVERAGE / WILL BE THERE / YOUR BEEN ENTRY as section headers). The page keeps ONLY the locked headers (YOUR CIRCLE, PUBLIC, ARTISTS). Owner actions group into one hairline-topped block (1px `--border`, padding-top 16, no header — headers never narrate):
- PAST event, unrated viewer: [StarInput empty] + [Add favorite quiet micro link]. Sits between the rating block and Your Circle (the composer position).
- PAST event, rated viewer: block reduces to [Add favorite] (+ one quiet ink WBT record line when the viewer had marked WBT — dormant record, no expiry narration).
- UPCOMING event: [Mark Will Be There control] + [Add favorite] in the block; WBT COUNT stays the color slot (numeral `--judgment`); zero review/rating chrome anywhere (locked).
- Rating average block (numeral + histogram + count line) is PAGE data, not an owner action — it stays where the locked design puts it (identity column on desktop v1.5, after header on mobile), never under an overline.

## 3. Buttons to the designed control register
- Primary/toggle ("Mark Will Be There"): 1.5px `--action` border, padding 8×16, fn 14/500, radius 0. Marked state: border+text `--judgment` (favorites grammar).
- Quiet actions ("Add favorite", "Edit ▾"): micro links, `--text-muted`→`--text` hover, underline hairline. No browser-default buttons anywhere.

## 4. Plural grammar (apply everywhere counts render)
- 0 → "No active marks yet." / "No ratings from Your Circle yet." (zero-form sentence, never "0 active marks")
- 1 → "1 active mark" · "1 like" · "1 rating"
- n → "N active marks" · "N likes" · "N ratings"

## Flags
- Dormant WBT record line copy on past events ("Will Be There · marked") is unrendered in fixtures (viewer never marked) — confirm copy at integration, keep it one quiet ink line.

## Dated delta — 2026-08-20 responsive identity alignment
- Mobile event identity is title-led, followed by an 80×100 artwork/meta pair; lineup, rating/WBT state, and owner actions return to the full content measure below it. The fixed top chrome must never cover the title.
- Desktop identity uses the existing 160×200 artwork and one continuous content column for title, venue/date/city, lineup, rating/WBT state, and owner actions. Community/review sections align to that content column so the page does not jump between unrelated left edges.
- Event meta inherits the 16px stack register, including the semantic `time` element; the global micro timestamp rule must not shrink event identity dates.
- Attendee collections use the shared people-row identity grammar (26px avatar, functional name, muted handle). Pagination chrome is absent when a detail collection has only one page.

## Dated delta — 2026-08-27 lineup empty state and trust hold

- `Lineup` is ratified as the quiet section-heading copy.
- The dormant past-event record copy is ratified as `Will Be There · marked`, rendered as one quiet line only when the viewer previously marked the event.
- When no artists are listed, the section remains present and renders one quiet line: `No lineup has been listed.` It must not render a bare heading followed by an empty list.
- No unverified-event banner or status treatment is authorized by this frontend ruling. Exposing the ingestion lifecycle through the API and UI remains held pending a separate operator ruling that explicitly names that backend contract change.

## Dated override — 2026-08-27 information hierarchy

This operator-approved override supersedes the earlier three-step event metadata styling, display-scale WBT numeral, unconditional green WBT control, and micro-uppercase Lineup treatment wherever they conflict.

- Event identity retains one dominant display title. Venue, city, date, time, and lineup names share one existing information recipe: General Sans UI size, regular weight, and secondary ink.
- Venue and city form one self-identifying line separated by a middle dot. Date and time form the other compact line. Upcoming identity remains location-led; past identity remains date-led.
- `Lineup` uses the existing UI size in semibold primary ink and sentence case. It is separated from artist information by the shared 8px step; artists remain a semantic ordered list with 6px internal rhythm.
- Upcoming attendance is one compact group after Lineup: the active-mark sentence and owner action share a row when capacity permits and wrap as a unit when constrained. The display-font numeral is removed.
- An unmarked `Will Be There` action uses the standard ink action boundary. Judgment green appears on the action only after commitment; the active-mark count may remain judgment green because it represents committed social activity.
