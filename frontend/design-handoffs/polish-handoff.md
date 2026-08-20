# DELTA — seven-item polish handoff
Date: 2026-08-02 · Markdown is sole authority · frames: spec/polish-preview.html · zero new tokens, scoped styles.

## 1. Empty-flier placeholder — product-wide (DATED OVERRIDE)
Overrides "flier-absent = slot stays EMPTY / designed collapse" (design-tokens.css ROWS note) for all FIXED 4:5 slots.
- Treatment: slot keeps `--image-slot` fill; centered on it, the event's (or item's) FIRST INITIAL in the display face, color `--border-strong` — a tonal mark, two greys apart from the bg, never ink. Uppercase as the title renders it; numeral/symbol initials render verbatim.
- One rule, all sizes: initial size = 36% of slot width → 20px @ 56×70 · 29px @ 80×100 · 57px @ 160×200. Line-height 1, optically centered (nudge -2% Y). Not a border, not a pattern, no icon glyph.
- Applies: Discover rows, feed slots, Been rows, favorites, search results, event-page identity fliers (80×100 / 160×200).
- Does NOT apply: the upcoming event page's full-bleed hero — a poster-scale initial would dominate the page; hero-absent keeps the designed collapse (identity reflows to type). FLAG for veto if you want the mark there too.

## 2. Favorites rows — full row anatomy (3 types, one list)
- All three types share the 56×70 slot + name + meta grammar; hairlines `--border-muted`, padding 12 vertical, whole row navigates.
- Events: flier thumb (or §1 placeholder) · name display row-title · meta micro `--text-secondary` "date · venue".
- Artists: 56×70 slot with the §1 initial mark (artists have no artwork by contract — the mark IS their thumb, same treatment, no avatar circle: circles mean people-accounts, artists are catalog identity) · name display row-title · no meta line (an artist row is name-only; nothing invented).
- Venues: same slot + initial mark · name display row-title · meta micro `--text-secondary`: city.
- Section stays under the existing FAVORITES overline grammar; 3-per-type cap renders as one continuous list grouped by type order events → artists → venues, no sub-headers (the anatomy self-identifies via meta).
- Empty favorites: silent absence (existing ruling holds).

## 3. Avatar upload — replaces the Avatar URL field (Edit surface)
- Anatomy: current avatar 72px circle left — photo (center-cropped in the circle mask) or initials fallback (fn 600, 24px, `--text-secondary` on `--avatar`) — + control column right, gap 16, top-aligned.
- Controls: "Upload photo" quiet control (1px `--border-strong`, pad 8×16, fn 14/500, `--text-secondary`). When a photo exists, "Remove" joins as a quiet text affordance below (fn 12, `--text-secondary`, underline) — NOT danger, NOT a dialog: removal is recoverable by re-upload, and reversible actions never summon ConfirmDialog (standing rule). No remove-confirm state exists.
- States: empty = initials + Upload photo only · uploading = control text swaps to "Uploading…" `--text-muted`, control disabled, avatar unchanged until success · uploaded = new photo + Remove appears · error = one line in the ruled error register (micro 12 `--danger-text`) under the control, slot unchanged.
- FLAG (engineering boundary): design specs center-crop display in the circle mask only; whether a client-side cropper ships is an engineering ruling. If a cropper is added later it needs its own design pass — nothing here assumes it.

## 4. Event-page metadata alignment (kills "Venue:" / "City:" labels + ARTISTS overline)
- Meta = the locked self-identifying stacks, no labels ever: past = date ui/500 → venue `--text-secondary` → city `--text-muted` (three-step recession); upcoming = venue-led 16px stack. Production's labeled prose is replaced by these verbatim.
- Lineup: KEEPING a quiet header, argued — the event page is the one surface holding the FULL ordered lineup; after the meta stack, a bare artist-name column starting with a display-face headliner can misread as more title material. One section heading in the existing register (caps micro 500 `--text-muted`), copy **"Lineup"** (not ARTISTS — FLAG: copy ratification).
- Lineup rows: headliner first — display face 20px, ink; supporting artists in listing order, fn 14 `--text-secondary`, one per row, padding 8 vertical, NO hairlines (a lineup is one group — whitespace rhythm only), full-width tap targets, whole row → artist page. No inline underlines; hover = text to ink.

## 5. Discover Recent rows — RULED (closes discover-handoff flag 1)
- Same anatomy as Upcoming (flier 80×100, display name, meta, lineup) PLUS: when the event has an average (≥3 ratings), a compact judgment element ends the meta line — avg stars 12px `--judgment`, halves ("★★★" for 3.0). No numeral, no count on the row (they live on the event page).
- not_enough (<3 ratings): meta line unchanged, no judgment element, no placeholder text — silence is the designed state.
- DATED OVERRIDE (scoped): "judgment color nowhere on Discover" narrows to "nowhere except Recent-row avg stars" — it is judgment data, the allocation rule is what's being obeyed.

## 6. Menu blessings
- Account menu: BLESSED as shipped (flat panel, two rows, wash focus).
- Sort menu: BLESSED as shipped (flat panel, four options, wash focus).

## 7. Grouped feed activity (closes home-handoff flag 3)
- Grouping is legal ONLY for the one-liner types (favorited event / favorited artist / follow), same actor + same verb within a feed window; rated_been and WBT never group.
- Anatomy stays §1-of-home: ONE actor line (avatar 26 + name 600 + verb pluralized, ui `--text-secondary` + timestamp of the latest action right-aligned), then:
  - favorited events/artists: objects STACKED, one per line, display face row-title mobile 18 (the object line register, unchanged), max 3, then "+N more" micro `--text-muted` as the last line. No fliers on grouped items — the stack is the payload; a flier column would re-inflate a deliberately quiet type.
  - follows: objects run INLINE in the sentence ("followed **A**, **B** and **C**" — person names fn 600, no display face), max 3 names then "and N others". Follows have no object line; the sentence is the item.
- Whole grouped item routes to the actor's profile (no single object to own the tap).

## 8. ADDENDUM 2026-08-02 — favorite control (heart grammar)
Replaces the "Add favorite" quiet micro link everywhere favoriting exists (event/artist/venue pages; row-scale remove in the favorites list).
- Glyph, not icon art: ♡ (outline) / ♥ (filled) in the fn face — same idiom as the star runs. No SVG.
- RECOMMENDED: word + heart at detail-page scale (a control needs affordance the first time; stars never needed it because they're data), heart-only at row scale. Both rendered; veto to go word-less.
- States (detail scale: glyph 16px, word fn 14, gap 6):
  · unfavorited: ♡ `--text-muted` + "Favorite" `--text-secondary`. No green anywhere pre-commit.
  · hover (pointer only): glyph + word darken to ink. Quiet pre-commit response, never a green preview.
  · favorited: ♥ `--judgment` + word "Favorited" `--text-secondary` — green lives on the glyph only (the committed judgment mark), the word stays chrome.
  · favorited-hover: glyph unchanged, word swaps to "Remove" `--text-secondary` (FLAG: copy). Click un-favorites instantly — reversible, no ConfirmDialog.
  · fill moment: instant state swap is the spec. OPTIONAL (flagged — the system has no motion grammar): one 120ms ease-out scale 1→1.15→1 on the glyph at commit; nothing on un-favorite.
  · cap-rejected (3 per type, shipped behavior): the act is refused — heart STAYS outline; persistent message in the ruled error register (micro 12 `--danger-text`) beside the control (right at desktop, wrapping below at 390), control remains usable for other types' pages. Copy as shipped: "Favorites are limited to 3 per type." (FLAG: ratify).
- Row scale (favorites list remove affordance): heart-only 14px, filled `--judgment`, right-aligned in the row, hit target padded to 44px; hover → outline ink; click removes the row (un-favorite, reversible).
- Placement: event owner block — the heart takes the exact position of the killed "Add favorite" link (under the flier at both widths); artist/venue pages — same relationship to the identity block.

## FLAGS (summary)
1. §1 hero exclusion — veto if the initial mark should reach the full-bleed hero.
2. §4 "Lineup" header copy — ratify or rename.
3. §3 client-side crop — engineering ruling; design covers display-crop only.
4. §8 favorited-hover word "Remove" + cap-rejection copy — ratify.
5. §8 optional 120ms fill micro-transition — accept or hold to instant-swap (no motion grammar exists yet).
6. §8 word-vs-wordless at detail scale — recommendation is word + heart; veto for heart-only.

## Dated delta — 2026-08-20 artist portrait fallback
- Artist identity imagery is now portrait grammar: a circular, center-cropped photo when present and a neutral circular head-and-shoulders silhouette when absent or failed, matching the familiar social-profile fallback idiom.
- The same fallback appears at identity scale on Artist pages and row scale in Search and Favorites. This scoped ruling supersedes the earlier “artists are never circles” clause for portrait surfaces only; event fliers and venue/event list slots remain rectangular.
