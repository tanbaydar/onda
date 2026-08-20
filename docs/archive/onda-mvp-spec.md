# Dance Music Events Platform — Master Spec (v1.2, frozen)

**One line:** Letterboxd for the dancefloor. A B2B2C review marketplace for dance music events where users build a diary of every party they attend, rate artist sets and the venue vibe separately, and follow friends, clubs, promoters, and artists.

**Stack:** Java Spring Boot modular monolith · MySQL (chosen over Postgres, partial-index tradeoff accepted) · React. Redis explicitly deferred until profiling proves need. Three client surfaces (consumer app, business/artist portal, admin panel), one backend.

**Scope:** House music only — afro, deep, melodic house included; no techno, no mainstage EDM. "Dance music events," never "nightlife" — day parties, rooftops, pop-ups, happy hours are first-class.

---

## 1. Product identity — the rulings that shape everything

- **The core user is a LOGGER, not a reader.** They build a complete diary to flex their event history ("onda 23 times"). Reviews are optional decoration on the log, not the point.
- **The diary unit is a "dance."** You don't log nights — you log dances. Stats say "Onda," not "Attended."
- **Performers are "artists,"** never DJs — enum value, page copy, every flow.
- **The reviewable unit is the artist SET within an event** — not the event, not the venue. The event is the "film"; sets are what you rate.
- **Two rating types, always visually distinct:**
  - **Set review** — judges the artists. Per set, half-stars 1–5, optional text ≤ 2,000 chars.
  - **"The vibe"** (experience rating) — judges the operators. Once per event, same scale, flows to both co-hosts (club + promoter).
- **Everything is an object.** No free-text inputs anywhere — every artist, club, promoter, city, and event is a row born through admin approval or the ingestion pipeline. Never typed into existence by a user.
- **B2B model:** clubs and promoters self-register and get verified; they create their own events. No scraping (the earlier scraping approach is dead).
- **Empty catalog at launch is accepted.** B2B-first reality; we do not engineer around cold start.
- **Tone:** cool and insider-y, for people who see dancing as identity. Warm and alive, never corporate, never neon club clichés. Quiet stats; flyer artwork does the visual heavy lifting.

---

## 2. Roles — one USER table, five types

| Type | How born | Credentials | Page |
|---|---|---|---|
| admin | Seeded by hand in DB, no signup flow | yes | no |
| consumer | Self-signup | yes | profile |
| club | Verification (create/claim) or ingestion | claimed only | yes |
| promoter | Verification (create/claim) or ingestion | claimed only | yes |
| artist | Admin/pipeline only | claimed only | yes |

- **One global username namespace** — a single UNIQUE column across all types. Powers @mentions and `/@handle` URLs. Immutable in MVP.
- **Unclaimed page** = a USER row with NULL email/password. Claiming = verification approved → credentials set.
- One email = one account. A club manager who also parties uses two emails (accepted).

---

## 3. Consumer features — the five frozen screens

Mobile-first (~380px), four-tab bottom nav: **Home / Search / Activity / Profile.**

### Profile (owner view — public profiles undesigned, backlogged)
- Identity block: avatar (null → generic) · @username · city · joined date. Read-only; the **gear icon is the only door to settings**.
- Stat row — four derived counts, computed on read, hidden until first logged dance, count exactly what the log shows (never disagree), only grow, dead numbers in MVP:
  - **Onda** — distinct events with any log (set rating, vibe rating, stars-only all count)
  - **Sets rated** — count of set reviews, written or stars-only
  - **Venues** — distinct clubs across logged dances
  - **Artists seen** — distinct artists across rated sets (b2b counts each)
- "Recent" = 3 dance cards (vibe stars + top set + "see all ratings" — hidden when only one rating) · "See all dances" → full log, newest first, month headers. Stars-only dances appear in your own log (public-listing silence rule doesn't apply to your own diary).

### Settings
- Full screen. Edit avatar/city, email, password, logout, delete.
- **Locked username row** (immutable).
- Delete = personalized count of your content + type-your-username gate.

### Activity — two tabs
- **You** (default): comments on your things, replies, likes received.
- **Following**: written reviews + comments by followed people only. Followed pages' events route to Home, not here.

### Home — two tabs
- **For you** (default): quick-log prompt (tappable stars log the vibe in place) · followed pages' upcoming events · friends' latest reviews.
- **[City]**: flyer wall of the week · like-ranked popular reviews (likes over trailing 7 days, per city). Tab label doubles as city switcher with browsing breadcrumb.
- **Two-city semantics:** home city = identity (USER.city_id, set in settings); browsing city = session-level lens, defaults to home, switching never touches identity. Client-side only, no schema.

### Search
- One bar, live-as-you-type, **global scope** (city shown per row), name-matching only.
- Groups: Events → Artists → Clubs and promoters → People. Empty groups don't render. Pre-search = recent searches only.

### Social layer
- **Like** — reviews, vibe ratings, comments. One per user per target.
- **Follow** — any user can follow any user (people and pages). Routing differs: a person's reviews/comments → Activity Following; a page's events → Home For-you shelf.
- **Comment** — YouTube-style one-level threading, any role can comment. Only *written* reviews/ratings are commentable; stars-only is silent arithmetic. Pages and events have no comment box (no forum).

---

## 4. Business / artist features

- **Verification** — one queue, one table, four request types: create_business, claim_business, create_artist, claim_artist. Evidence link + admin decision, resubmittable.
- **Event creation** — verified pages only. Club picks the date; we store it, no interpretation (midnight problem is theirs). Co-hosts (club + promoter) co-edit; unclaimed co-host = no rights until claimed.
- **The vibe flows to both co-hosts** — co-hosting an event means co-owning it, no special cases.
- Self-reviews permitted (owner via consumer identity); one review per user per set is the only wall; report button is the recourse.

## 5. Admin features

- Verification queue (approve/deny with reason).
- Report queue — polymorphic, anything flaggable → keep/remove with reason.
- Structured request inbox with **demand-signal counters** (replaces any automated watchlist) — users request artists/venues/cities; counts tell admins what's wanted.
- Admin overrides: duplicate event on a date, editing frozen events, trust-list removals.
- All lists (whitelists, trust states) are **private** — never published to users.

---

## 6. Event lifecycle rules

- **UNIQUE (club_id, event_date)** — one event per club per date, admin_override only exception.
- `start_time` required (doors time). **Reviews open at event_date + start_time in the club's city timezone** — live reviewing during the event.
- Frozen after event_date — admin-only edits after.
- Never deleted; **cancel is the only exit**; cancelling past events is admin-only; cancelled blocks reviewing.
- One event = one date. Festivals/multi-day out of MVP (also excluded from the trust algorithm by the same rule).
- Back-to-back sets = one ARTIST_SET with multiple artists attached; the set's rating flows to every artist on it.
- Experience rating allowed without any set log — rate either, both, or neither.

## 7. Deletion & lifecycle

- **Consumer deletes** → hard-wipe everything: reviews, ratings, comments, likes, follows, reports.
- **Page account deletes** → page reverts to unclaimed (owner NULL); the club still exists in reality.
- Review/rating: editable forever; `edited` flag once changed after a comment exists.

## 8. Derived, never stored as truth (all computed on read)

- Set score → artist score · vibe ratings → club/promoter scores · event score = avg of its set reviews.
- Profile stat row (four counts) · popular-this-week (likes, trailing 7 days, per city).

---

## 9. The catalog — what appears in the app

**Inclusion OR-gate** (admin-controlled, all lists private):
- venue in a core city AND consistently tickets on credible platforms, **OR**
- promoter in the global whitelist, **OR**
- artist in the global headliner whitelist.
- Users can push via the structured request inbox (demand counters). Dead pages with zero reviews are explicitly accepted.
- **List membership ≠ existing in the app.** The moment an event ingests, every artist on its lineup gets a page — untrusted or not. Profiles are born from events; powers are born from trust.

**Data source:** Resident Advisor GraphQL API (stable artist and venue IDs) — v1 is RA-only, collapsing the dedupe/alias problem to near-zero.

## 10. The trust machine (internal editorial plumbing — invisible to users)

Prestige accumulates through **counters, not matrix computation** — events arrive one at a time forever. Seed a small set of axioms (hand-typed by founders once), then propagate trust through co-signed credits as the pipeline processes events chronologically.

**The constitution:**
1. **Multi-day event → skip.** (Festivals excluded in one rule.)
2. **No anchor on the event → skip.** Anchor = anchor artist, anchor venue, or anchor promoter.
3. **Ingested →** untrusted venue **+1**; untrusted artist **+credit** (stamped with venue) if an anchor artist is on the bill. Max one credit event per event each.
4. **Promotion to Anchor — permanent, append-only** (removal is admin-only; inactivity never demotes):
   - Artist: ~15 credits (flat) / ~30 points (weighted) within 12 months, across **≥ 5 distinct venues**.
   - Venue: ~10 credited events / 6 months.
   - Promoter: ~8 events / 2+ cities.

**One trust state only: Anchor.** The Voucher tier was cut (cascade risk — vouchers minting vouchers with no gate — plus the equal-credit flaw). The country/travel gate was removed (biased against strong local and US-market artists); venue diversity does the work instead.

**Leading candidate — stature-weighted co-signs (PageRank instinct, no recursion):**
- Weight is read from the scene, never computed from trust itself. An anchor's stature = distinct venues that booked them in the trailing 12 months (a GROUP BY, refreshed weekly).
- Buckets: ≥ ~15 venues = major, pays **+3** · ~8–14 = established, **+2** · < 8 = fringe, **+1**.
- A bill pays the **strongest** anchor's stature — max, not sum (sum resurrects the stacked-bill exploit).
- Venue-diversity gate stays an unweighted count of rooms.
- **Status: pending calibration** — the credit function is pluggable; run the 5-year replay twice, flat vs weighted, against the same answer key.

**Bootstrap = the live product:** identical pipeline code. The 5-year historical harvest replays chronologically once before launch, producing the grown trusted sets AND the full backfill catalog simultaneously; the same loop then continues nightly.

---

## 11. Schema — 12 entities (see ERD)

Constraints crow's foot can't express (become unique indexes + application rules):
- UNIQUE: EVENT (club_id, event_date) unless admin_override · REVIEW (user_id, set_id) · EXPERIENCE_RATING (user_id, event_id) · SET_ARTIST (set_id, artist_id) · LIKE (user_id, target) · USER (username), USER (email).
- XOR: COMMENT targets exactly one of review/experience_rating · LIKE targets exactly one of review/rating/comment.
- One-level nesting: a comment's parent must itself have no parent.
- Commentability: only where target's body is non-null (application-level).
- Role guards: club_id → type=club, promoter_id → type=promoter, artist_id → type=artist (application-level).
- EVENT creation requires verified pages (club side can be unclaimed if promoter-created). Artist rows created by admin/pipeline only.

| Entity | Purpose |
|---|---|
| USER | Every actor — admin, consumer, club, promoter, artist. Unclaimed pages have NULL credentials |
| CITY | Preloaded reference: country, name, timezone. No free-typing |
| EVENT | The party. Owned by club, optional promoter co-host |
| ARTIST_SET | Weak on EVENT. order_num required, start_time optional |
| SET_ARTIST | Weak join. B2b = multiple rows; rating flows to all |
| REVIEW | Set-level, judges the artists |
| EXPERIENCE_RATING | Event-level "the vibe," judges the operators, flows to both co-hosts |
| COMMENT | One conversation mechanism, one-level threads, all roles |
| VERIFICATION_REQUEST | create/claim × business/artist, one admin queue |
| REPORT | Polymorphic (target_type + target_id), one admin queue |
| LIKE | XOR target: review / vibe rating / comment |
| FOLLOW | Composite PK self-join; routing differs by followed type |

---

## 12. Patch-1 backlog (explicitly deferred, not forgotten)

- Sockpuppet defenses · notifications · comment tombstoning · minimum-n score display · event draft states.
- Public profile view (others' profiles) + follower counts + follow-button placement + privacy toggle.
- Stat drill-downs · year jump on the full log · "see all ratings" tap behavior (lean: inline expand) · highlights shelf.
- Discovery screen design (data model is discovery-ready; only the screen is deferred).
- Ticket link on events (comes back as one nullable column if businesses ask).

## 13. Open items before coding starts

- Calibrate flat vs stature-weighted credits via the historical replay.
- Working title ("Onda" used in design briefs) — name was not final at this milestone.
