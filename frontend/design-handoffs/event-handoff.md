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
