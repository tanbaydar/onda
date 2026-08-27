# HOME FEED — incremental handoff (delta; markdown is sole authority)
Ruled 2026-08-02 · APPROVED as rendered + two dispatch amendments (§1 actor-line truncation, §5 desktop centering). Zero new tokens; scoped styles. Covers all six activity types (spec Q153) with ONE anatomy.

## 1. Item anatomy (one grammar, amplitude varies — never six layouts)
Every item = [flier slot]? + [actor line] + [object line]? + [payload]? — timestamp always on the actor line.
- **Actor line**: avatar 26 circle + name fn **600** ink + action phrase ui 14 `--text-secondary` + relative timestamp right-aligned (see §4). TRUNCATION RULING: the NAME truncates (ellipsis, flex min-width:0); the VERB always survives — verb span is flex-none, nowrap, never truncation-eligible. A feed item may lose the name's tail, never its meaning. Object may complete the sentence for follows ("followed **Review Public Test**" — person names fn 600; the followed name may truncate, the verb may not).
- **Object line** (event/artist items): the object name in **display face**, row-title token — the item's identity per the skeleton rule.
- **Flier slot**: event items (rated_been, WBT, favorited event, review like) carry the event flier at **56×70** left of object line + payload (EventListRow slot); flier-null = empty slot holds x (ruled). Non-event items (follows, favorited artists) have NO slot — text at page x; the two starting edges deliberately separate event activity from social activity.
- **Payload** by type:
  · rated_been: stars 14px `--judgment` (halves) directly under the object line; review excerpt when present — quiet prose 16/1.6 `--text-secondary`?  no: `--text` prose at measure ≤640, clamped 4 lines, ending with a quiet micro "more" affordance (DATED OVERRIDE of "feed clamp stays navigational-only") routing to the event page. Whole item remains a tap target → event.
  · will_be_there: event meta line micro `--text-secondary` (date · venue) under the object line. No judgment color (the mark is the actor's state, count lives on the event page).
  · review like: action phrase "liked a review of"; object line + slot; no excerpt.
  · favorited event / artist: actor line + object line (+ slot for events). Nothing else — one-liner presence.
  · follow: actor line only.

## 2. Judgment allocation
Stars 14 `--judgment` on rated items; like counts keep their existing grammar where rendered. NOTHING else in the feed takes green. Never rating-as-text ("4.0 stars" is dead).

## 3. Page header — RULED: the feed simply begins
No "Home" page title, no overline. Wordmark/tab chrome carries orientation; first item starts at the content top (24 mobile / 32 desktop above the first actor line).

## 4. Timestamps — PRODUCT-WIDE RULING (closes the standing backlog item)
Relative compact form: `18h`, `2d`, `3w` (existing "18h" ruling extended). Register: micro 12 `--text-muted`. Placement: right-aligned on the actor line, flex space-between — identical at both widths and on every item type; Activity adopts the same treatment. Absolute dates stay on reviews/diary entries only (existing rule). Timestamps never take accent (register 13, closed).

## 5. Rhythm & pagination
- Items separated by 1px `--border-muted` hairlines (ledger idiom — repeating siblings), padding 16 vertical; rated_been items (the large scale) take 24.
- Desktop: single ledger at 800, **CENTERED in the content width** (dated override, Home only — the landing surface has no identity block to anchor a left edge; detail pages keep the shared left edge). Excerpt measure ≤640; timestamp stays on the actor line.
- Cursor "Load more": existing micro-link grammar at the ledger end; absent when exhausted.

## 6. Empty feed
One quiet line ui `--text-secondary`: "No activity from people you follow yet." + ONE affordance: "Discover events" as a bordered-ink control (control-md: 1.5px `--action`, 8×16, fn 14/500), margin-top 16. Nothing else — no dead page, no illustration.

## FLAGS (unruled)
1. review_like items have no fixture — rendered from a flagged stand-in; confirm the serializer shape (actor, review author, event) before wiring.
2. "more" affordance copy ("more" vs "Read more") — rendered lowercase "more"; veto if you want parity with the event page's "Read more".
3. Grouping ("Kim and 2 others followed…") stays legal per the locked spec but is undesigned — flag for a later pass; current anatomy renders one actor per item.

## Dated delta — 2026-08-27 review continuation copy

- The truncated feed marker is `Read more`, not lowercase `more`. It remains inside the whole event-target row.
- Expanded event-page review copy is `Show less`; collapsed copy is `Read more`. The control meets the essential mobile target rule without gaining button chrome.
