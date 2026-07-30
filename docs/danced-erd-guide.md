# Danced — ERD Construction Guide

**Goal:** One complete, reviewed ERD covering all three zones. This document ends at "ERD finished." No models, no migrations, no code before that gate.
**Inputs:** `PRODUCT_QA_SPEC.md`, `danced-data-architecture.md`, the assumptions register (A1 revised: no cancellation cascade; A2: approximately two months around launch), the recon fixtures.
**Method:** Draft zone-by-zone in build order → assemble → review the seams → annotate constraints → red-team → freeze.

---

## Step 0 — Tooling (15 min)

Use a **text-based** diagram format so the ERD lives in the repo and diffs like code. Either:

- **dbdiagram.io** (DBML) — fastest, renders relationships and constraints cleanly, exports SQL you can sanity-check against MySQL 8, or
- **Mermaid `erDiagram`** — renders in GitHub READMEs natively.

Pick one; don't use a drawing tool (draw.io, Figma). Hand-positioned boxes rot; text regenerates.

Conventions to fix before drawing anything:
- Table names `UPPER_SNAKE`, singular (`EVENT`, not `events`)
- Every table: surrogate `id` PK unless a composite PK is specified below
- Crow's foot cardinality on every edge
- Constraint annotations as notes on the table (DBML `Note:` / Mermaid comments)
- Three visually separated regions, labeled: **INGESTION**, **CANONICAL + IDENTITY**, **APP**

---

## Step 1 — Draft Zone 1: Ingestion (30 min)

Five tables. Mostly linear. Draw:

- **TRACKED_SOURCE_PAGE** — `id, source, area_ref, label, active, last_synced_at, last_success_at`
  *(seeds are RA city areas: NYC=8, Boston=530)*
- **RAW_INGEST** — `id, seed_id → TRACKED_SOURCE_PAGE, payload JSON, http_status, fetched_at, processing_status ENUM(pending, processed, quarantined, dropped)`
- **REJECTED_INGEST** — `id, raw_ingest_id → RAW_INGEST, entity_ref, reason ENUM(PARSE_FAILURE, OUT_OF_SCOPE, NO_ARTIST, EMPTY_TITLE, BAD_DATE), detail, first_seen_at, last_attempt_at, attempt_count, resolved_at NULL`
- **SYNC_RUN** — `id, run_type ENUM(nightly, backfill), started_at, finished_at, seeds_attempted, seeds_failed, events_upserted, events_quarantined, events_dropped`
- *(No cancellation-related structures anywhere — A1 revised is final.)*

**Self-check before moving on:**
- [ ] RAW_INGEST has no FK pointing *out* of the ingestion zone
- [ ] Every REJECTED_INGEST row is traceable to its raw payload
- [ ] Nothing in this zone references EVENT/VENUE/ARTIST — ingestion observes the source, the Transformer writes the catalog

---

## Step 2 — Draft Zone 2: Canonical + Identity (45 min)

Six tables. The identity constraints are the hard part — get them exactly right.

- **CITY** — `id, name, country_code, timezone` *(preloaded reference; timezone lives here)*
- **VENUE** — `id, name, city_id → CITY, parent_venue_id → VENUE NULL` *(no source columns — source-neutral)*
- **ARTIST** — `id, name, image_url NULL`
- **EVENT** — `id, title, event_date DATE, start_time TIME NULL, venue_id → VENUE, cover_image_url NULL, status ENUM(active, unverified, hidden), last_seen_at, misses INT`
- **EVENT_ARTIST** — `PK(event_id → EVENT, artist_id → ARTIST), position`
- **EXTERNAL_IDENTITY** — `id, entity_type ENUM(event, venue, artist), canonical_id, source, source_id`

**Constraint annotations (mandatory on the diagram):**
- EXTERNAL_IDENTITY: `UNIQUE(source, source_id, entity_type)` — one external record maps to one canonical row
- EXTERNAL_IDENTITY: `UNIQUE(entity_type, canonical_id, source)` — one canonical row has at most one identity per source
- EVENT: indexes `(event_date, status)` and `(venue_id, event_date)`
- EVENT: note "`start_time NULL` = source gave no time (no fake midnights); `misses`/`last_seen_at` = v1 absence tracking, migrates to EXTERNAL_IDENTITY at source #2"

**Self-check:**
- [ ] Zero `source`/`source_id` columns on EVENT, VENUE, ARTIST
- [ ] `canonical_id` is deliberately *not* a real FK (it points into three tables via `entity_type`) — annotate this as a known polymorphic trade-off, enforced in the Transformer
- [ ] Status enum has exactly three values; no `cancelled`
- [ ] Timezone reachable from EVENT via `venue → city` (loggability path, Q73–74)

---

## Step 3 — Draft Zone 3: App (90 min)

Twelve tables. The cascade chains are the hard part. Work through them in this order:

**Identity & social graph:**
- **USER** — `id, email UNIQUE, email_verified_at NULL, username UNIQUE, display_name, bio VARCHAR(150), avatar NULL, home_city_id → CITY NULL, is_private BOOL NOT NULL (no default — Q204 forced choice), status ENUM(active, deactivated, pending_deletion), deletion_due_at NULL`
- **USERNAME_HOLD** — `username UNIQUE, user_id → USER, held_until` *(30-day cooling, Q113–115; deactivation writes no hold, Q175)*
- **FOLLOW** — `PK(follower_id → USER, followee_id → USER), status ENUM(pending, approved), created_at` *(entire Q33–36 state machine)*

**Diary core:**
- **DIARY_ENTRY** — `id, user_id → USER, event_id → EVENT, rating DECIMAL(2,1) NULL, rated_at NULL, created_at` — `UNIQUE(user_id, event_id)`, `CHECK(rating BETWEEN 0.5 AND 5.0 AND MOD(rating*10,5)=0)`; note "`rating NULL` = unrated Been (Q186)"
- **REVIEW** — `id, entry_id → DIARY_ENTRY UNIQUE, body VARCHAR(1000), published_at, edited_at NULL` — 1:1 with entry (Q22); `published_at` immutable (Q69)
- **REVIEW_LIKE** — `PK(user_id → USER, review_id → REVIEW), created_at`
- **WILL_BE_THERE** — `PK(user_id → USER, event_id → EVENT), created_at` — note "expiry computed from event_date + venue city timezone (Q94); no stored expiry"

**Profile & periphery:**
- **FAVORITE_EVENT** — `PK(user_id, event_id), added_at` *(cap 3, app-enforced; order = added_at ASC, Q133)*
- **FAVORITE_ARTIST** — `PK(user_id, artist_id), added_at` *(cap 3)*
- **FAVORITE_VENUE** — `PK(user_id, venue_id), added_at` *(uncapped, never public, Q84)*
- **NOTIFICATION** — `id, recipient_id → USER, type ENUM(review_like, follow, follow_request, request_accepted), actor_id → USER, review_id → REVIEW NULL, created_at, read_at NULL`
- **REPORT** — `id, reporter_id → USER, target_type ENUM(review, profile), target_review_id → REVIEW NULL, target_user_id → USER NULL, body VARCHAR(1000), created_at` — generated column `target_key`, `UNIQUE(reporter_id, target_key)` (Q172; MySQL NULL-in-unique workaround)
- **RECENT_SEARCH** — `id, user_id → USER, query, searched_at` *(cap 10 trimmed app-side)*

**Cascade annotations (mandatory — draw the delete behavior on the edges):**
- USER delete → cascades to everything it owns (Q174 permanent deletion)
- DIARY_ENTRY delete → REVIEW → REVIEW_LIKE (Q45, Q71)
- REVIEW delete alone → REVIEW_LIKE cascade; entry and rating survive (Q70–71)
- EVENT is **never deleted** by any path (A1 revised) — hidden only; annotate this on EVENT

**Self-check:**
- [ ] Every FK leaving the app zone lands on a canonical `id` (EVENT, VENUE, ARTIST, CITY) — nothing else
- [ ] No app table references EXTERNAL_IDENTITY, RAW_INGEST, or any ingestion table
- [ ] No FEED table exists (feed is derived — Q97/Q178/Q189 disappearance rules come free)
- [ ] No denormalized counters anywhere
- [ ] All four notification types present; nothing for declines (Q107)

---

## Step 4 — Assemble (30 min)

Merge the three drafts into one diagram with the three labeled regions. Layout rule: ingestion left, canonical center, app right — data flows left to right, reads flow right to left. The center column is the firewall, and it should *look* like one.

---

## Step 5 — Seam review (60 min — the step that justifies the whole exercise)

Walk every edge that crosses a region boundary. There should be exactly these, and no others:

**Ingestion ↔ Canonical:**
- (none as FKs — the Transformer connects them in code; EXTERNAL_IDENTITY + REJECTED_INGEST are the only durable traces of that relationship)

**App → Canonical (all one-directional, all landing on `id`):**
- DIARY_ENTRY → EVENT
- WILL_BE_THERE → EVENT
- FAVORITE_EVENT → EVENT; FAVORITE_ARTIST → ARTIST; FAVORITE_VENUE → VENUE
- USER → CITY (home city)

Any other cross-region edge is a design violation. If you feel the need to draw one, stop and bring the question back — that is the contradiction this process exists to catch.

**Then trace these five spec scenarios across the assembled diagram, edge by edge:**
1. User rates an event → entry insert → where does the feed item come from? (derived — confirm no table needed)
2. User removes rating, keeps Been (Q187) → `rating=NULL` + REVIEW delete + like cascade — confirm the chain
3. Event vanishes from RA for 3 nights → EVENT.status=hidden — confirm no app-table row is touched
4. User deactivates (Q174–175) → status flip only; username freed with no USERNAME_HOLD row — confirm
5. Private account approves a follower (Q33) → FOLLOW.status pending→approved — confirm one row covers it

---

## Step 6 — Red-team checklist (30 min)

Final pass. Every box checked or explicitly waived with a written reason:

- [ ] Both EXTERNAL_IDENTITY uniques present and annotated
- [ ] `UNIQUE(user_id, event_id)` on DIARY_ENTRY
- [ ] Rating CHECK constraint (half-star steps) annotated
- [ ] `is_private` has no default
- [ ] Username uniqueness noted as case-insensitive (MySQL `ai_ci` collation)
- [ ] All ENUMs enumerated in full on the diagram — no "status: enum" hand-waving
- [ ] Every NULL-able column's NULL has a stated meaning (start_time, rating, resolved_at, read_at, edited_at…) — a NULL without semantics is a smell
- [ ] EVENT deletion impossibility annotated
- [ ] No table exists that no spec question requires (hunt for speculative tables)
- [ ] No spec question requires a table that doesn't exist (spot-check Q32, Q94, Q113, Q159-as-amended, Q172, Q186)

---

## Definition of done

The ERD is **finished** when:

1. All ~23 tables drawn in three labeled regions, every edge carrying cardinality
2. All constraint and cascade annotations from Steps 2–3 present
3. Seam review passed: only the sanctioned cross-region edges exist
4. All five trace scenarios walk cleanly
5. Red-team checklist fully checked or waived in writing
6. The source file (`.dbml` or `.mmd`) is committed to the repo alongside the two spec documents

Then — and only then — the next conversation is Django models, transcribed zone by zone from this diagram.

**Stop here. Nothing below this line exists yet.**
