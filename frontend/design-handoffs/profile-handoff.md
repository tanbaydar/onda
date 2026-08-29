# OWNER PROFILE PAGE + EDIT PROFILE SURFACE — incremental handoff (delta; markdown is sole authority)
Ruled 2026-08-02. Zero new tokens; statistics strip per stats-handoff v3 (placed, untouched). Preview frames rendered in-session for approval only — no HTML authority artifact.

## 1. Page composition (top → bottom, both widths)
Identity header → STATISTICS strip → tabs (Been | Reviews) → active tab's rows → favorites line → (owner settings live on the Edit surface, NOT this page).
Strip sits between header and tabs: statistics are header-band data; the tabs contract only the content below them.

## 2. Identity header (owner view)
- Avatar: 72px circle. Default = plain `--avatar` (#DEDEDE) circle — never placeholder words. (See §6 avatar flag for the initials proposal.)
- Display name: **display face** (Rozha One), 20px mobile / 24px desktop, ink. DATED OVERRIDE: supersedes the "user names never take display face" clause — on PROFILE HEADERS only; user names in rows, reviews, feeds, search stay functional 600.
- @handle: micro `--text-muted`. Home city, when set, appends to the same line as compact metadata: `@handle · Boston`. No "No home city." — silent absence.
- Followers / Following: locked header pattern (count fn 600 14 + micro caps label, gap 6/16), under the handle line.
- Bio: quiet prose — `--font-prose` 16/1.6 `--text-secondary`, max measure 640, under the F/F row (margin-top 12). Empty = silently absent, never "No bio."
- Owner affordance: quiet micro link "Edit profile" where the FollowControl sits on others' profiles (margin-top 12). Routes to the Edit surface (§5).

## 3. Tab register (first tabbed surface — the pattern)
- Row of text tabs, fn 14, gap 24: active = `--text` 600; resting = `--text-muted` 400. No link underline ever.
- The tab row sits on a full-width 1px `--border` hairline; the active tab carries a 2px `--action` indicator flush on that hairline (margin-bottom −1px). 48 above the row, 16 below to first row.
- Contract: exactly the content below the hairline swaps; nothing above re-renders.

## 4. Been rows (diary rows)
- EventListRow anatomy: 56×70 flier thumb slot left (empty slot holds x), then: event name row-title token **display face** → one meta line micro `--text-secondary`: `Fri 19 June, 10:00 pm · Big Night Live, Boston` → judgment element: small stars 14px `--judgment` (★★★★, halves as ½) + "Written review" marker micro `--text-muted` (gap 8) when a review exists. Never the text "2.0 stars".
- Desktop spread: [thumb | name + venue] left, [date ui/500; stars + marker] right column, per the ledger grammar. Rows 16px padding, `--border-muted` hairlines between. Whole row → event.
- Unrated attendance: stars slot shows "Unrated attendance" micro muted (existing rule).
- Reviews tab: same row grammar; review-bearing rows lead with the same anatomy (no new register).
- Empty tab: ONE quiet line, ui `--text-secondary` ("No events in Been yet." / "No reviews yet." ⚠ copy flag), no overline above it.

## 5. Edit Profile surface (own route: /settings/profile or clearly separated mode)
- Layout: auth-column register — 360px centered mobile and desktop; heading "Edit profile" fn 600 20; wordmark chrome unchanged.
- Fields (auth form register: caps micro 500 muted labels, 6 below label, 16 between fields; inputs 1px `--border-strong`, pad 12, fn 16):
  1. Display name — text input.
  2. Avatar — see flag (§6).
  3. Bio — textarea (min 3 lines); counter bottom-right under the field, micro `--text-muted`, live: `0 / 150`.
  4. Home city — the existing custom dropdown, styled to the input register (input box + ▾ affordance right, fn 16; menu = panel register: `--bg`, 1px `--border-strong`, options ui 14, hover/focus row = the same unruled focus treatment carried from search ⚠).
  5. Account privacy — radio pair, ui 14: ◉ Public ◯ Private, consequence sentence inline micro `--text-secondary` (existing ruled copy).
- Actions: "Save changes" full-width bordered-ink primary (1.5px `--action`, pad 12, fn 16/500 — NO fills) + "Cancel" quiet micro link centered below. Destructive nothing here.
- ⚠ copy flag: "Save changes", "Cancel", route name unruled.

## 6. FLAGS (unruled — decide, don't let integration default)
1. **Avatar mechanic (v1)** — recommendation: initials-avatar as the real default (1–2 initials, fn 500, `--text-secondary` on `--avatar` — zero new tokens) + "Avatar URL" as a plain advanced text field below it in the form; the URL field styled to the input register either way. Alternative: URL field as the primary avatar control, no initials. RULE ONE.
2. Empty-tab and Save/Cancel copy (§4, §5).
3. Focus/hover row treatment for the city dropdown menu — same open question as search's keyboard-focus row.
4. Follow-request row actions (Approve/Decline) are newly composed from existing registers (control-sm pair) — confirm or amend.

## Allocation audit (page-wide)
Judgment color: Been-row stars + the strip's judgment unit ONLY. Display face: name (header override), event names, strip numerals. Everything else functional/prose registers. No global resets; all styles scoped.

## Dated delta — 2026-08-27 copy, targets, and local recovery

- Empty-tab copy is ratified: `No events in Been yet.` and `No reviews yet.` Save/Cancel and `/settings/profile` are ratified as shipped.
- `Requested` is ratified for an outgoing pending follow request. Approve/Decline remains the ruled follow-request composition.
- Follow action failure is local to FollowControl, preserves the loaded profile, and offers Retry. It never replaces the profile with a page-level failure.
- Edit Profile initial-load failure keeps the route context and offers Retry in place.
- Follow and essential profile actions meet the cross-cutting mobile target ruling while retaining their quiet visual register.

## Dated operator override — 2026-08-27 follow-request ownership

- Follow requests do not appear in Edit Profile. Profile editing ends after Save/Cancel because social inbox work is not profile configuration.
- Pending follow requests appear at the top of Activity, before its notification ledger. A persistent summary row exposes the pending count and disclosure state; expanding it reveals requester identity plus Approve/Delete actions in the existing quiet control register.
- Instagram-style dual access is intentional: while a request remains pending, its matching notification row also exposes Approve/Delete. Resolving the request in either location removes the pending actions from the other location; historical notification copy remains after resolution.
- The request module loads and recovers independently. Failure to load or decide a request must not hide already-loaded Activity notifications, and an empty request collection renders no placeholder section.

## Dated operator override — 2026-08-27 Instagram spacing and Letterboxd diary rows

- Profile spacing follows the attached Instagram reference without importing Instagram styling or unrelated features. The profile surface is one centered 800px measure. The identity cluster uses a circular 80px avatar beside identity on mobile and the existing 160px identity size on desktop, with a 24–48px governed gap. Display name leads; follower/following counts share one inline row; handle and bio follow; the owner Edit profile or viewer Follow action spans the identity measure beneath the cluster.
- Statistics, tabs, active diary ledger, and Favorites share the same centered measure. The statistic label is `Avg. Rating`.
- Been and Reviews rows follow the attached Letterboxd placement using Onda tokens: 80×100 flyer at left; title plus event year at top; venue below; judgment plus `Been` date below that; written review prose and like count continue vertically when supplied. Rows use existing hairlines and functional/prose/display roles only.
- Past diary rows display the event date without its stored start time. Been may show the existing `Written review` marker because its shipped payload does not include review prose. Reviews renders the shipped body and like count; this ruling does not expand the API contract.

## Dated operator override — 2026-08-29 statistics vertical centering

- The Statistics block sits at an equal 48px interval between the profile header action and the tab register. Its section heading adds no second top margin. Statistics, tabs, and all content below them therefore move upward together while the identity header remains fixed.

## Dated operator override — 2026-08-29 Favourites-first profile tabs

- The profile tab register is `Favourites | Been | Reviews`, in that order. Favourites is the default active tab at `/u/:username`; Been lives at `/u/:username/been`, and Reviews remains at `/u/:username/reviews`.
- Favourites is tab content, not a persistent section below Been or Reviews. Exactly one of Favourites, Been, or Reviews renders beneath the shared tab hairline.
- The legacy `/been` entry point continues to open the signed-in user's Been tab rather than the new Favourites default.

## Dated operator override — 2026-08-29 image scale (corrected after live review)

- The identity avatar remains 120×120 mobile and 240×240 desktop. Been/Reviews flyers and rectangular Favorites artwork are 153×191.25; circular Favorites artist artwork is 153×153. This flyer correction supersedes the earlier 102×127.5 / 102×102 ruling because that live result remained visually too small.
- Below the width at which three 153px Favorites items fit, the governed three-column row constrains each image to its available column to prevent document overflow. Discover and Been/Reviews flyers retain the full corrected size at every width.
- Existing aspect ratios, centered Favorites composition, typography, copy, gaps, and all non-Profile surfaces remain unchanged.
