# Onda UI/UX design contract and audit

- Status: consolidated reference and implementation audit
- Audit date: 2026-08-26
- Implementation baseline: `5ea03c6`
- Scope: the responsive React web application under `frontend/`

## 1. How to use this document

This document normalizes Onda's design information into one vocabulary for design, implementation, review, and QA. It records both the intended system and the current implementation status.

It does **not** replace the repository's design authority. Under `AGENTS.md`, the Markdown files in `frontend/design-handoffs/` remain the sole authority for visual rulings. If this document conflicts with a handoff, use the newest dated handoff that explicitly covers the surface. If no handoff decides the issue, mark it open and ask the operator; do not infer a new rule from existing CSS.

The supporting sources have these roles:

| Source | Role |
|---|---|
| `frontend/design-handoffs/*.md` | Sole authority for approved visual and interaction rulings |
| `frontend/DESIGN_BRIEF.md` | Product character, allocation principles, anti-goals, and frozen implementation constraints |
| `frontend/design-tokens.css` | Shared implementation vocabulary and locked foundation values |
| `frontend/src/*.css` | Shipped implementation evidence, not independent design authority |
| `frontend/src/pages/` and `frontend/src/components/` | Shipped structure, semantics, interaction, and state evidence |
| `frontend/design-fixtures/` | Sparse and dense data reality for design QA |

Within the handoffs, a later dated and more narrowly scoped delta supersedes an earlier clause only for the named scope. An unresolved `FLAG` is not a rule.

Requirement language in this document:

- **Required**: directly stated by an authoritative handoff.
- **Prohibited**: directly ruled out by an authoritative handoff.
- **Shipped choice**: implemented, but not necessarily ratified as a general rule.
- **Open**: explicitly unresolved or not covered by a handoff.
- **Audit risk**: a verified implementation or accessibility concern; resolving it may require an operator ruling.

## 2. Product and experience thesis

Onda is a social diary for dance-music events: an event diary and taste network, not a ticketing marketplace, promoter page, listings portal, or generic social dashboard.

The visual direction is an **editorial instrument on a pure white surface**. Premium quality comes from restraint, typography, information hierarchy, and rhythm. It must not come from darkness, gloss, card stacks, decorative effects, or urgency.

The system allocates one visual channel to one job:

| Channel | Job | Consequence |
|---|---|---|
| Display type | Identity | Use for event, artist, and venue names; selected profile headings; the wordmark; and major numerals. Never use it for long prose or routine controls. |
| Color | Judgment | Green belongs to ratings, likes, favorites after commitment, rating distributions, and the active WBT count/state. Routine navigation and controls remain ink or grey. |
| Imagery | Atmosphere and identity | Event fliers and human/artist portraits receive presence. Do not add decorative stock imagery or illustrations. |
| Space | Reviews and hierarchy | Reviews become prominent through placement, measure, and breathing room—not louder styling. |

Event hierarchy changes with time:

- **Past event:** reviews lead; ratings and likes carry judgment; the flier anchors identity.
- **Upcoming event:** flier, lineup, date, and venue lead; the active WBT count takes the judgment slot; review and rating controls do not appear.

Design qualities:

- Information-dense, spatially airy.
- Editorial, calm, and human.
- White, typographic, and flat.
- Mobile-heavy without sacrificing desktop composition.
- Content-led, with repeated data presented as ledgers rather than cards.

Anti-goals:

- Dark “premium tech,” glass, gradients, glow, and shadows.
- Rounded-card dashboards or equal-weight grids of everything.
- Ticketing urgency, countdowns, badges, FOMO, or promotional chrome.
- Sterile fintech emptiness.
- A generic SaaS information architecture.
- Decorative color that does not communicate judgment or error.

## 3. Foundations

### 3.1 Typography

All fonts are self-hosted WOFF2 assets under `frontend/fonts/` and use `font-display: swap`.

| Role | Family | Available styles | Use |
|---|---|---|---|
| Display | Rozha One | 400 | Event, artist, and venue names; approved profile headings; wordmark role; prominent numerals |
| Functional | General Sans | 400, 500, 600 | Navigation, controls, labels, metadata, user names outside profile headings, system messages |
| Prose | Gambetta | 400, 400 italic | Reviews and profile biography |

Display type is rationed. A person name uses General Sans 600 in feeds, reviews, people rows, activity, and search. The profile identity heading is the explicit exception and uses Rozha One.

#### Type scale

| Token or scoped register | Mobile | Desktop | Typical role |
|---|---:|---:|---|
| Auth/axis micro | 11px | 11px | Auth labels, histogram axis/tooltips, social-count labels |
| `--text-micro` | 12px | 12px | Timestamps, overlines, quiet metadata, counts |
| `--text-ui` | 14px | 14px | Navigation, labels, buttons, metadata, lineup support |
| `--text-body` | 16px | 16px | Body and review prose |
| `--text-body-lg` | 18px | 18px | Primary search input and large functional text |
| `--text-row-title` | 18px | 20px | Event and catalog names in ledgers |
| `--text-title-past` | 20px | 24px | Compact titles and profile identity name |
| `--text-numeral-sm` | 20px | 24px | Inline selected rating |
| `--text-numeral-md` | 24px | 30px | Profile statistics |
| `--text-title` | 30px | 36px | Detail-page identities |
| `--text-numeral-lg` | 48px | 60px | Event average, WBT count, lead profile statistic |
| Discover city title | 24px | 30px | Scoped Discover page identity |
| Star input glyph | 32px | 32px | Five-star rating composer |

Type behavior:

- Display titles and numerals: line-height 1.0–1.2; display text at 30px or above uses `-0.01em` tracking.
- Functional UI and microcopy: line-height about 1.4.
- Review and biography prose: 16px, line-height 1.6, maximum measure 640px.
- Section overlines: General Sans 12/500, uppercase, `0.05em` tracking.
- Do not write numeric rating prose such as “4.0 stars” where the star grammar is available.

### 3.2 Color

No colors outside the semantic palette are permitted without a new ruling.

| Token | Value | Contrast on white | Role |
|---|---|---:|---|
| `--bg` | `#FFFFFF` | — | Primary surface |
| `--bg-subtle` | `#F1F1F1` | — | Quiet wash; currently used for menus and the reserved unverified banner |
| `--text` | `#1B1B1B` | 17.22:1 | Primary ink; use instead of black |
| `--text-secondary` | `#4F4F4F` | 8.19:1 | Secondary copy and quiet controls |
| `--text-muted` | `#8A8A8A` | 3.45:1 | Recessive chrome and metadata |
| `--border-strong` | `#C4C4C4` | 1.74:1 | Inputs and quiet control boundaries |
| `--border` | `#E6E6E6` | 1.25:1 | Standard hairlines |
| `--border-muted` | `#F1F1F1` | 1.13:1 | Repeating-row separators |
| `--image-slot` | `#ECECEC` | — | Event/catalog image fallback |
| `--avatar` | `#DEDEDE` | — | Person-avatar fallback |
| `--action` | `#1B1B1B` | 17.22:1 | Primary outlines, active indicators, destructive fill |
| `--judgment` | `#1D6D48` | 6.30:1 | Ratings, likes, committed favorites, WBT, histogram |
| `--judgment-muted` | `#82CEAB` | 1.85:1 | Reserved and currently unused |
| `--danger` | `#753129` | 9.43:1 | Error borders |
| `--danger-text` | `#57241E` | 12.53:1 | Error and retry text |
| `--backdrop` | `rgba(27,27,27,.4)` | — | Modal backdrop only |

Color semantics:

- Green means a person judged, liked, favorited, rated, or marked something. It is not a generic success, link, navigation, or hover color.
- Before a favorite is committed, its heart and label are grey; the committed heart alone becomes green.
- Success confirmations stay quiet ink/grey, not green.
- Danger wine is limited to validation, error, and retry states. Destructive buttons use ink fill, not danger fill.
- Timestamps are always grey and never judgment green.
- `--judgment-muted` is reserved; do not introduce it casually.

### 3.3 Spacing and rhythm

Legal shared spacing steps are 2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, and 128px through `--sp-*` tokens.

The grouping law is: **space around a group is greater than space within it**.

Canonical rhythm:

- Row internals: 4–8px.
- Between repeating ledger rows: 12–16px plus one hairline.
- Section heading: at least twice as much space above as below; normally 32/12 mobile and 48/12 desktop.
- Sections: at least 32px apart on mobile and 48px on desktop.
- Form label to input: 6px.
- Field to field: 16px, except auth surfaces whose ruled field blocks currently use 24px.
- Feed items: 16px vertical; rich rated entries use 24px.

Component geometry may use ruled non-spacing values such as 11, 20, 26, 30, 34, 40, 44, 56, 70, 72, 80, 100, 104, 120, 150, 160, 200, 220, 260, 320, 360, 480, 640, 768, 800, and 1012px. These are dimensions, not additions to the spacing scale.

### 3.4 Measures and responsive geometry

| Token/register | Value | Purpose |
|---|---:|---|
| Minimum viewport | 320px | Smallest supported layout |
| Desktop breakpoint | 768px | Single responsive breakpoint |
| Mobile gutter | 24px | Main page inset |
| Desktop gutter | 106px | Main page inset |
| Main shell maximum | 1012px | Current implementation shell |
| Ledger measure | 800px | Events, feed, activity, search groups |
| Prose measure | 640px | Reviews and biographies; never exceed the ruled 680px ceiling |
| Auth column | 360px | Auth and edit-profile forms |
| Header / mobile tab bar | 64px | Persistent chrome reservation |
| Compact flier | 56×70px | Shared ledger row, 4:5 |
| Mobile identity flier | 80×100px | Event identity and Discover row, 4:5 |
| Desktop identity flier | 160×200px | Detail identity, 4:5 |
| Person avatar | 72px / 26px | Identity / row |
| Artist portrait | 160px desktop; 112px current mobile identity; 56px row | Circular portrait grammar |

Responsive rules:

- Mobile reserves a fixed 64px top bar and 64px bottom navigation bar.
- Desktop uses one fixed 64px top header and no bottom bar.
- Mobile event identity is title-led, then an 80×100 flier/meta pair; lineup, judgment data, and owner controls return to full measure below.
- Desktop event identity is a 160×200 flier beside one continuous content column. Community sections keep the same content-column edge.
- Home and Discover use a centered 800px desktop ledger. Detail pages preserve their identity alignment rather than centering each section independently.
- Forms remain one 360px column at both widths.
- Do not add horizontal scrolling to profile statistics or standard content ledgers.

### 3.5 Shape, borders, and depth

- Global radius is 0.
- Person and artist portraits are the only circular shape exception.
- Separation uses whitespace and 1px hairlines.
- Primary controls use a 1.5px ink outline.
- Quiet controls and fields use a 1px strong-grey outline.
- Repeating siblings may use hairlines; unrelated sections use whitespace only.
- No cards, shadows, gradients, glass, glow, or general elevation.
- Popup panels remain flat: white background, strong hairline outline, no shadow.
- The confirm-dialog backdrop is the only dimensional overlay treatment.

### 3.6 Imagery and fallback grammar

- Event artwork is always 4:5 and center-cropped.
- Fixed 4:5 slots preserve their footprint when artwork is missing or fails. They show `--image-slot` and the first rendered title character in Rozha One, colored `--border-strong`, at 36% of slot width with a slight upward optical nudge.
- The fixed-slot initial applies to Discover, feed, Been, favorites, search results, and event identity fliers.
- The upcoming full-bleed hero exclusion remains in the handoff, although the current shipped page uses the fixed identity composition rather than a full-bleed hero.
- Person avatars use a circular image or 1–2 functional-font initials on `--avatar`.
- Artist identity, Search, and Favorites use a circular center-cropped portrait. Missing/failed portraits use the same neutral head-and-shoulders silhouette.
- Circles mean people or portrait identity; event and venue slots stay rectangular.
- Images must have meaningful alternative text when informative. Purely tonal fallbacks may be hidden when adjacent text already names the object.

## 4. Information architecture and hierarchy

### 4.1 Persistent chrome

The Onda wordmark and primary navigation persist on every route, including authentication routes.

Desktop:

- Wordmark left.
- Navigation right, General Sans 14; active item ink/600, inactive grey.
- Account menu or guest Register/Log in cluster remains in the same header.
- One bottom hairline; no left rail.

Mobile:

- Fixed top bar contains the wordmark and account actions.
- Fixed bottom bar contains public/product navigation.
- Signed-in order is Home, Discover, Search, Activity, Profile.
- Guest navigation keeps Discover and Search, with account actions in the top bar.
- Content reserves both bars directly; selector-dependent accidental spacing is prohibited.

### 4.2 Page hierarchy

- One visible H1 identifies a standard page, except Home, whose feed begins without a page title.
- Display identity precedes metadata; metadata recedes from ink to secondary to muted.
- Section overlines label major groups only. Do not narrate individual owner controls with headings.
- Repeated content uses one list anatomy and amplitude changes, not a new layout for each activity type.
- Whole-row navigation is preferred for event, activity, result, and favorite ledgers.
- Avoid labels where content is self-identifying: no “Venue:”, “City:”, or “Artists:” prose on event identity.

### 4.3 Content semantics

- Relative compact timestamps (`18h`, `2d`, `3w`) belong to Home and Activity.
- Absolute dates belong to reviews, diary entries, event identity, and event metadata.
- Event identity dates retain the 16px stack register; the global micro timestamp style must not shrink them.
- Past event metadata is date-led: date ink/500 → venue secondary → city muted.
- Upcoming event metadata is venue-led at 16px: venue ink/500 → date secondary → city muted.
- Venue identity location is `City, Region · Country`, gracefully omitting unavailable or duplicate parts. It links to Discover and never exposes timezone.
- Counts use correct zero, singular, and plural forms. Avoid “0 active marks,” “1 likes,” and similar mechanical copy.
- Empty optional identity fields such as bio or home city disappear silently rather than producing “No …” filler.

## 5. Reusable component contracts

### 5.1 Section heading

General Sans 12/500, uppercase, `0.05em` tracking, muted. Use 32–48px above and 12px below. Hairlines separate repeating siblings, not sections.

### 5.2 Controls

| Size | Padding | Text | Use |
|---|---|---|---|
| Small | 4×8px | 12px | Cancel, compact pagination, quiet row action |
| Medium | 8×16px | 14px | WBT, Follow, standard control |
| Large | 12×24px | 16px | Large/auth primary register |

- Primary actions: white surface, 1.5px ink outline, medium weight.
- Quiet actions: secondary or muted text, minimal outline or underlined text as ruled.
- Destructive irreversible action: ink fill with white text, inside ConfirmDialog.
- Reversible actions do not require confirmation.
- Disabled states remain recognizable without becoming the only explanation of why an action is unavailable.

### 5.3 Forms

- Labels: uppercase micro, 500, `0.05em`, muted, 6px before the field.
- Inputs: full width, 1px strong border, 12px padding, 16px functional text, white background.
- Focus: darken/thicken inward without adding a second decorative rectangle.
- Errors attach to the relevant field with a danger border and 12px danger text 6px below.
- Do not use toast-only or summary-only validation when a field is identifiable.
- Preserve entered values after validation failures.
- Textareas resize vertically and begin at a practical multi-line height.
- Code entry uses one paste-native six-character field, numeric input mode, centered 24px text, and `0.5em` tracking.

### 5.4 Tabs

- General Sans 14, 24px gap.
- Active: ink/600 plus a 2px ink indicator flush with the base hairline.
- Resting: muted/400.
- No link underline.
- Only content below the tab hairline swaps; identity and controls above remain stable.

### 5.5 Ledgers and rows

- Standard event row: 56×70 flier slot plus display title and metadata.
- Discover row: 80×100 flier, two-line title clamp, compact date/venue, one-line lineup.
- Mobile standard row stacks title → date → venue → lineup/judgment.
- Desktop standard row spreads identity left and date/venue or judgment right within 800px.
- Rows use 12–16px vertical padding and muted hairlines between siblings.
- Missing art keeps the ruled slot and initial fallback.
- One-page collections render no pagination chrome.

### 5.6 People identity

- Identity avatar: 72px circle.
- Row avatar: 26px circle.
- Row name: General Sans 600, 14px.
- Handle/relationship: 12px muted.
- People names do not use the display face outside the explicit profile-header exception.

### 5.7 Stars and rating input

- Data stars use functional glyphs, green, 2px tracking; feed-large may use 3px.
- The composer contains five 32px glyphs in five 44px hit areas with 6px gaps.
- Unselected: outline star in muted grey. Selected: filled green. Half: green fill clipped over grey outline.
- Pointer/touch chooses half or whole by star half; drag scrubs; keyboard arrows step by 0.5; Enter commits.
- Slider semantics expose min 0.5, max 5, current value, and 0.5 step.
- The chosen display numeral appears only after selection.

### 5.8 Rating summary and histogram

- Event average: large green display numeral, ten uniform green vertical bars, then “average from N ratings.”
- Fewer than three event ratings: withhold the numeral/chart and use “Not enough ratings for an average yet.”
- Histogram order is ½★ to 5★, left to right.
- All bars share one color. Zero buckets use a baseline stub, never disappear.
- Permanent labels are only `½` and `5`; tooltip copy is `N · X★`.
- Profile histogram appears only at five or more ratings.
- Profile placement is a 104×30px sparkline companion to the average; event placement may use the 160×100px module.

### 5.9 Favorite control

- Use text glyphs `♡` and `♥`, not bespoke icon art.
- Detail scale: word plus 16px heart, 6px gap.
- Row scale: filled 14px heart in a 44px target, no word.
- Unfavorited: outline grey heart + “Favorite” in secondary text.
- Favorited: green filled heart + “Favorited” in secondary text.
- Hover before commit darkens to ink, not green.
- Removal is immediate and reversible; no dialog.
- A rejected three-per-type action keeps the heart outline and shows persistent inline danger copy.
- The shipped 120ms fill pulse is an unresolved optional motion choice, not a system-wide motion grammar.

### 5.10 Follow control

Follow, Unfollow, Request to follow, and Requested use one fixed 150px-minimum, 32px-high box with 8×16px padding, General Sans 14/500, secondary text, and a strong-grey border. State changes must not shift layout.

### 5.11 Review

- Header: 26–34px person avatar, functional name, muted handle/context, stars.
- Body: Gambetta 16/1.6 at no more than 640px.
- Feed excerpts clamp to four lines and offer quiet lowercase “more” in the shipped choice.
- Event/profile excerpts clamp around 8–10 lines and expand in place.
- Metadata is 12px muted; likes and Like/Unlike use judgment green.
- Own review shows “Yours” and one “Edit ▾” affordance; it does not show a like control.
- Reviews gain importance from placement and space, not display type or decorative containers.

### 5.12 Menus, dropdowns, and search panels

- White flat panel, 1px strong outline, no radius, no shadow.
- Options are 14px with 8×12px padding.
- Selected option is 600.
- The account and sort menus are approved as shipped.
- City-dropdown and result-row focus treatment remains only partially ruled; see audit risks.

### 5.13 Confirm dialog

- Native dialog with dim backdrop.
- White box, strong hairline, 24px padding, maximum current width 480px.
- Title: functional 16/600; consequence: 14px secondary.
- Cancel is quiet; destructive confirmation is ink-filled with white text.
- Use only for irreversible consequences.

### 5.14 System states

- Loading, error, retry, empty, missing image, and sparse/dense data must preserve the intended content slot and hierarchy.
- Loading uses a quiet status line and `aria-live` where the update is asynchronous.
- Errors use visible copy and in-place Retry when recovery is possible.
- Empty states are one quiet sentence, with at most one useful next action. No illustration is required.
- Continuation failure keeps already loaded rows in place.
- Pagination or continuation chrome disappears when exhausted.
- Avoid layout jumps when thresholds change, states toggle, or content loads.

## 6. Surface contracts

| Surface | Required composition and distinguishing behavior |
|---|---|
| Landing `/` | Session resolver only. Redirect to the correct destination; transient copy is functional, not a branded landing campaign. |
| Discover `/discover` | City is the H1. Matched city/search controls. Upcoming/Recent tabs. Centered 800px ledger with 80×100 fliers. Recent alone may show average stars at the ≥3-rating gate. Infinite continuation via sentinel; loaded rows survive failure. |
| Search `/search` | Primary 640px/18px search field, then All/Events/Artists/Venues/People scopes. Search begins at two trimmed characters after ~250ms. All groups cap at five with View all; single scope paginates. Search chrome never uses judgment green. |
| Home `/home` | No H1 or overline. Feed begins 24px mobile / 32px desktop from content top. One centered 800px ledger. Rich rated entries, row-scale event actions, and quiet grouped one-liners share one anatomy. |
| Register `/register` | 360px auth column. Username, email, password, display name, privacy. One primary Register action and quiet Log in path. |
| Login `/login` | Username-or-email and password. One primary Log in action. Non-enumerating credential error. Quiet reset and registration paths. |
| Verify `/verify-email` | “Check your email,” destination copy, expiry notice, single six-digit field, Verify, Resend code, quiet sent confirmation. |
| Reset request `/reset-password` | Email only, Send code, non-enumerating post-submit confirmation, Enter code, Use a different email. |
| Reset form `/reset-password/confirm` | Code step followed by new/confirm password step; same auth and code-entry registers. |
| Event detail | Identity hierarchy changes by past/upcoming state. Mobile and desktop alignment follow the event delta. Full Lineup group. Rating/WBT page data precedes one unlabelled owner block. Your Circle/Public/attendee sections share the aligned content column. |
| Profile Been/Reviews | Fused identity header, followers/following, bio, fixed follow/edit affordance, Statistics, tab hairline, active ledger, Favorites. Private stub keeps public identity counts but withholds private modules. |
| Edit profile | 360px column. Avatar upload, display name, bio counter, home city, privacy, save/cancel, and follow requests. Avatar removal is immediate and recoverable. |
| Activity `/activity` | H1 plus one 800px ledger. Whole rows route. Unread names 600; read state recedes to muted/500. Relative timestamp. No action chrome within rows. |
| Venue detail | Display name, linked natural-language location, favorite directly beneath, then Upcoming and Past compact event ledgers. No cards, labels, or timezone. |
| Artist detail | Circular portrait/fallback, display name, favorite, then Upcoming/Past compact ledgers. Portrait treatment is ruled; the broader artist-page composition has no dedicated handoff and should not be generalized without one. |
| Not found | Functional H1, concise explanation, one route back to Discover. No decorative error illustration. |

## 7. Interaction, semantics, and accessibility

### 7.1 Semantic structure

- Use native landmarks: one site header, primary `nav`, one `main`, and a footer.
- Use one H1 for page identity unless a handoff explicitly removes it, as on Home.
- Use `section` only when it has an accessible heading or label.
- Use ordered/unordered lists for repeated feed, event, review, result, attendee, and activity collections.
- Use links for navigation and buttons for state changes.
- Preserve machine-readable `time[datetime]` values.
- Use `aria-current` for the active route and explicit selected/pressed state for tabs, scopes, and options.
- Status updates use `role="status"`/`aria-live="polite"`; errors use `role="alert"`.
- Images and avatar fallbacks identify their subject accessibly without duplicating adjacent text unnecessarily.

### 7.2 Keyboard and touch

- Search: Up/Down traverses result rows, Enter opens, Escape clears/closes.
- Listbox menus: Arrow keys, Home/End, selection, and Escape return focus to the trigger.
- Star input: Left/Right steps 0.5; Enter commits; pointer and drag behavior have keyboard equivalents.
- Dialog focus stays within the native dialog lifecycle and returns appropriately after close.
- Interactive elements must expose a visible keyboard focus state.
- The established 44px hit areas for hearts and rating stars are the preferred mobile target. Existing smaller controls must at minimum retain adequate separation and a visible state.

### 7.3 Contrast audit baseline

For QA, evaluate normal text against 4.5:1 and meaningful component/focus boundaries against 3:1. This review target does not itself authorize changing an approved token; token changes require an operator ruling because they affect every surface.

### 7.4 Content voice

- Calm, direct, and specific: “door of the venue,” not bureaucratic software.
- No exclamation marks on auth surfaces.
- No marketing urgency, scarcity, countdown, or engagement bait.
- Error copy says what failed and, when safe, how to recover.
- Authentication failures avoid account enumeration.
- Empty copy is brief and factual; it does not blame the user.
- Loading voice should be standardized to one punctuation and ellipsis convention.

## 8. Current implementation audit

### 8.1 Conforming or explicitly shipped

- The three self-hosted font families and all declared weights are present and loaded.
- Production CSS uses the semantic color variables; there are no component-level hex-color additions.
- The interface is white, square, flat, and hairline-led, with no card/elevation system.
- Persistent guest/signed-in chrome, mobile bar reservation, and desktop header are implemented.
- Discover uses the ruled city-led header, tabs, 80×100 rows, rating gate for Recent, and sentinel continuation.
- Search and Discover share the two-character threshold and 250ms debounce.
- Event identity alignment, semantic event time, people rows, and single-page pagination suppression are implemented.
- Fixed-slot initial fallbacks and failed-image fallbacks are shared.
- Artist portrait fallback is shared across detail, Search, and Favorites.
- Profile histogram is suppressed below five ratings.
- Empty Favorites is silent.
- Account and Sort menus use the approved flat-panel treatment.
- Auth, search, feed, profile, event, venue, and activity surfaces expose core landmark/list/status semantics.
- Destructive dialog action uses the ruled ink fill; avatar upload and primary search have explicit focus treatment.

### 8.2 Audit risks requiring a ruling or scoped follow-up

| ID | Risk | Evidence and impact | Status |
|---|---|---|---|
| A11Y-01 | Muted text contrast | `--text-muted` is 3.45:1 on white but is used for 11–14px navigation, labels, timestamps, handles, and read-state content. This misses the 4.5:1 normal-text audit target. | Open; changing the token would alter an approved visual register. |
| A11Y-02 | Control-boundary contrast | `--border-strong` is 1.74:1 on white but carries inputs, quiet controls, menus, and dialog boundaries. Meaningful boundaries may miss the 3:1 non-text audit target. | Open; requires a system-level color ruling. |
| A11Y-03 | Uneven keyboard focus | Search results/scopes and avatar upload have strong focus. City, Sort, Account, guest auth, histogram bars, and some auth fields remove native outlines and rely on low-contrast color/wash changes. | Partially ruled; city/search row treatment remains flagged. |
| A11Y-04 | Small targets | Hearts and rating stars use 44px targets, but mobile nav links, quiet links, menu triggers, pagination controls, and Follow use smaller boxes. | Open as a cross-product touch-target policy. |
| A11Y-05 | Motion preference | The optional 120ms favorite pulse is shipped without a `prefers-reduced-motion` override, and no broader motion grammar exists. | Open; either ratify instant state only or add a reduced-motion contract. |
| SYS-01 | Token discipline | Shared foundations are tokenized, but several ruled/scoped sizes remain literal in component CSS, including 11px labels, 20/24/30px scoped titles, and specific geometry. | Acceptable when scoped by a handoff; avoid new literals and consolidate when a token is genuinely reusable. |
| SYS-02 | Search empty-state ambiguity | The handoff says the page renders nothing below two characters, while the shipped page shows Recent searches only when the query is empty. | Conflict to rule: retain Recent searches as an approved exception or remove them. |
| SYS-03 | Loading language | Copy alternates among periods and ellipses: “Loading activity.”, “Loading…”, and “Loading more events…”. | Open content-system normalization. |
| SYS-04 | Visual regression evidence | Fixtures exist, but no committed route screenshots or automated visual baselines were found. Dense wrapping, browser focus, cropping, menus, and 320/390px states therefore require manual verification. | Open QA infrastructure. |
| SYS-05 | Unverified banner | A CSS slot exists, but its styling remains explicitly unruled and the event UI does not currently present a verified/unverified visual state. | Open; do not ship a visual distinction without an operator/product ruling. |
| SYS-06 | Artist-page authority gap | The portrait rule is explicit, but no dedicated artist handoff defines its full identity hierarchy or event collection details. | Current implementation is evidence only, not a reusable authority. |

### 8.3 Unresolved handoff flags

The following remain open after applying dated overrides:

- Event dormant WBT record copy.
- Auth error and confirmation copy ratification, including the non-enumerating reset message.
- Auth single-field code-entry choice, although it is shipped.
- Unverified-banner styling.
- Search/city dropdown keyboard-focus row treatment.
- Profile empty-tab and Save/Cancel copy.
- Follow-request Approve/Decline composition.
- Follow-control “Requested” copy and unverified private-count fixture coverage.
- Event lineup heading copy “Lineup.”
- Client-side avatar cropper boundary; current design covers display crop only.
- Favorite detail word-versus-heart-only choice, “Remove” hover copy, cap-rejection copy, and optional fill animation.
- Full-bleed upcoming-event hero fallback exclusion, if that hero composition returns.
- Home review-like fixture/serializer coverage and lowercase “more” copy.
- Histogram 1px zero stub in the compact profile placement.

Older flags resolved by later handoffs must not be reopened accidentally: Discover Recent rating anatomy, grouped one-line feed activity, avatar upload replacing Avatar URL, Discover automatic continuation, artist portrait fallback, persistent auth chrome, and responsive event identity alignment.

## 9. QA matrix

Every affected surface should be reviewed at minimum in these conditions:

| Dimension | Required cases |
|---|---|
| Width | 320px, 390px, 767px, 768px, and a wide desktop viewport |
| Density | Empty, sparse, normal, and dense fixture |
| Text | Long title, long display name, long venue/city, long review, 4-digit counts |
| Images | Present, absent, broken, portrait crop, and flier crop |
| Session | Guest, signed in, unverified where applicable, owner, other public, other private |
| Network | Initial loading, success, empty, initial failure, retry, continuation failure |
| Event | Upcoming, past, rated, unrated, not-enough-ratings, WBT zero/one/many |
| Interaction | Rest, hover, keyboard focus, pressed, disabled, pending, success, error |
| Input | Keyboard-only, touch, paste into code field, browser autofill, password manager |
| Preferences | 200% zoom, text enlargement, reduced motion, high contrast/forced colors where supported |

Visual checks should verify:

- Fixed chrome never covers headings or final content.
- No horizontal scroll appears at supported widths.
- Display titles wrap without colliding with metadata or controls.
- Actor names truncate before action verbs; the verb remains legible.
- Fliers remain 4:5 and portraits remain centered circles.
- Hairlines are visible without reading as card outlines.
- Green appears only where judgment is present.
- Empty/loading/error transitions preserve alignment and loaded content.
- Focus is visible in every interactive state.
- Review measure stays readable and does not expand to the full desktop shell.

## 10. Definition of done for future UI work

A UI change is design-complete only when:

1. The applicable handoff is identified, including later dated deltas.
2. No unresolved flag is silently converted into a design decision.
3. Existing tokens and component grammars are reused before adding values or variants.
4. Display type, color, imagery, and space retain their single assigned jobs.
5. Mobile and desktop hierarchy are both specified at the 768px breakpoint.
6. Empty, loading, error, retry, missing-image, sparse, dense, and pagination states are addressed.
7. Semantic HTML, keyboard operation, focus, announcements, contrast, and target size are reviewed.
8. Copy follows Onda's calm, non-promotional voice and correct plural grammar.
9. Relevant frontend tests pass and the production build succeeds.
10. Visual QA covers representative mobile and desktop fixtures.
11. Any adjacent issue is reported, not repaired outside the named scope.
12. The new or amended handoff remains the authority; this consolidated document is updated only as an index and audit record.

## 11. Standard format for new component records

Use this structure when adding a component or surface to the design system:

```md
### Component name

- Authority: handoff file, date, and section
- Purpose: one sentence
- Anatomy: ordered parts
- Content hierarchy: primary → secondary → tertiary
- Typography: family / size / weight / line-height
- Color roles: semantic tokens only
- Geometry: width, height, ratio, measure, and alignment
- Spacing: internal and external tokens
- States: default, hover, focus, active, selected, disabled, pending, success, error, empty
- Interaction: pointer, touch, keyboard, and dismissal behavior
- Semantics: native element, accessible name, relationships, and announcements
- Responsive behavior: below and above 768px
- Data extremes: missing, sparse, dense, long, and failed media
- Prohibitions: patterns this component must not introduce
- Open flags: operator decisions still required
- Verification: fixture, test, and viewport coverage
```
