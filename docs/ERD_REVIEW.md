# Danced ERD — Assembly Review

**Artifact reviewed:** `docs/danced.dbml`
**Target:** MySQL 8.0.16+
**Result:** Frozen. DBML parses successfully and generates MySQL SQL. The schema
decisions pass the seam, scenario, and red-team reviews. One historical documentation
count mismatch is recorded below.

## Manifest

### Ingestion — 4 tables

1. `TRACKED_SOURCE_PAGE`
2. `SYNC_RUN`
3. `RAW_INGEST`
4. `REJECTED_INGEST`

The construction guide says “five tables” but lists only these four. No fifth ingestion table was adjudicated or required. A speculative table was not added to satisfy the incorrect count.

### Canonical + identity — 9 tables

1. `CITY`
2. `VENUE`
3. `ARTIST`
4. `EVENT`
5. `EVENT_ARTIST`
6. `EVENT_IDENTITY`
7. `VENUE_IDENTITY`
8. `ARTIST_IDENTITY`
9. `CITY_IDENTITY`

### App — 15 tables

1. `DANCED_USER`
2. `USERNAME_HOLD`
3. `EMAIL_VERIFICATION_REQUEST`
4. `EMAIL_CHANGE_REQUEST`
5. `FOLLOW`
6. `DIARY_ENTRY`
7. `REVIEW`
8. `REVIEW_LIKE`
9. `WILL_BE_THERE`
10. `FAVORITE_EVENT`
11. `FAVORITE_ARTIST`
12. `FAVORITE_VENUE`
13. `NOTIFICATION`
14. `REPORT`
15. `RECENT_SEARCH`

The app count is higher than the guide because the review correctly added two separate, spec-required email request lifecycles.

**Total: 28 tables.**

## Seam review

### Ingestion → canonical

No foreign keys cross this boundary. The Transformer is the only bridge.

- `RAW_INGEST` references only ingestion tables.
- `REJECTED_INGEST` references only `RAW_INGEST`.
- No ingestion table references `EVENT`, `VENUE`, `ARTIST`, or an identity table.

**Result:** Pass.

### App → canonical

Only the approved read-side references exist:

- `DANCED_USER → CITY`
- `DIARY_ENTRY → EVENT`
- `WILL_BE_THERE → EVENT`
- `FAVORITE_EVENT → EVENT`
- `FAVORITE_ARTIST → ARTIST`
- `FAVORITE_VENUE → VENUE`

No app table references an ingestion or identity table.

**Result:** Pass.

## Required scenario traces

### 1. User rates an event

`DIARY_ENTRY` is created with non-NULL `rating` and `rated_at`. The feed derives the item from the entry; its timestamp is `rated_at`. No feed table exists.

**Result:** Pass.

### 2. User removes a rating but keeps Been

The service clears `rating` and `rated_at`, deletes `REVIEW` when present, and the database cascades from `REVIEW` to `REVIEW_LIKE` and review-linked `NOTIFICATION`. `DIARY_ENTRY` remains as unrated Been history. The derived feed item disappears because `rated_at` is NULL.

**Result:** Pass.

### 3. Event vanishes from RA for three complete successful fetches

The relevant `EVENT_IDENTITY.misses` increments. With one identity, the canonical aggregation changes `EVENT.status` from `active` to `unverified` after one miss and to `hidden` after three. No app row is deleted. A later observed presence resets misses and allows the event and suppressed user state to resurface.

**Result:** Pass.

### 4. User deactivates

One transaction copies `username` to `recovery_username`, clears `username`, and changes status to `deactivated`. The biconditional constraint requires the namespace release. No `USERNAME_HOLD` is created. Content remains stored but hidden.

**Result:** Pass.

### 5. Private account approves a follower

The existing `FOLLOW` row changes from `pending` to `approved`. A `request_accepted` notification is inserted. The original `FOLLOW.created_at` remains request time by design.

**Result:** Pass.

## Red-team checklist

- [x] Provider mappings use four concrete tables with real canonical FKs.
- [x] Both required unique constraints exist on every identity table.
- [x] Source fields exist only on seeds and identity mappings, never canonical entities.
- [x] `UNIQUE(user_id, event_id)` exists on `DIARY_ENTRY`.
- [x] Rating range, half-star increments, and rating/timestamp biconditional are annotated.
- [x] `is_private` is required and has no default.
- [x] Username uniqueness and holds are documented as case-insensitive.
- [x] Username/lifecycle biconditional is annotated.
- [x] All enum values are enumerated.
- [x] Every nullable column has a stated meaning, directly or through a table-level type-target invariant.
- [x] Canonical event deletion is forbidden and app references use `RESTRICT`.
- [x] No feed table or denormalized app counters exist.
- [x] `SYNC_RUN` counters are explicitly waived from the no-counter rule as immutable execution telemetry.
- [x] Review and notification cascades satisfy all reviewed deletion paths.
- [x] Favorite row-count caps are named service transaction invariants.
- [x] Self-like and initial-rating requirements are named cross-row/service invariants.
- [x] The source archive stores arbitrary response text rather than validated JSON.
- [x] Replay idempotency is enforced for rejection occurrences.
- [x] Event-level `PARSE_FAILURE` is distinct from payload-level parse failure.
- [x] `OUT_OF_SCOPE` alone is dropped; all quality failures quarantine and retry.
- [x] Deletion deadline and pending-deletion status form an enforced biconditional.
- [x] `RAW_INGEST` is explicitly append-only and never deleted in v1.
- [x] DBML was parsed by the official CLI and successfully generated MySQL SQL.

## Accepted implementation deltas

- Django will extend `AbstractUser`, so implementation migrations will contain framework administration and permission columns not shown in the product ERD.
- Those framework fields have no product semantics and product code must not depend on them.
- DBML notes describe CHECK constraints and service invariants; Django migrations must transcribe enforceable checks explicitly rather than assuming notes generate DDL.
- Django requires an `on_delete` policy for every foreign key. The ingestion-zone
  references omitted delete behavior in DBML because their parents and append-only raw
  evidence are never deleted in v1; the Django transcription uses `RESTRICT` so a
  mistaken seed, run, or raw-payload deletion fails loudly instead of cascading through
  evidence.
- Django has no native MySQL `ENUM` model field. Closed DBML enums are transcribed as
  `VARCHAR` plus named database `CHECK` constraints, with matching `TextChoices` for
  Python-facing validation. The storage spelling differs, but MySQL still rejects every
  value outside the frozen enum set; this is a documented ORM representation delta, not
  a weakening of the invariant.
- Django's composite-primary-key support remains unsuitable for `EVENT_ARTIST`'s
  relationship model. The implementation adds a surrogate `id` and enforces the two
  candidate keys as `uq_event_artist_pair` and `uq_event_artist_position`. Relationship
  identity and lineup-position uniqueness are unchanged.
- `uq_city_country_region_name` retains MySQL's deliberate multiple-NULL behavior:
  rows with `region_code IS NULL` are not mutually constrained. V1 US seed rows always
  carry a region code; any future no-region country must use the frozen sentinel
  convention rather than relying on NULL uniqueness.
- Django's `on_delete=models.CASCADE` is ORM collector behavior and does not emit
  MySQL `ON DELETE CASCADE`. Catalog migrations `0003` and `0005` explicitly replace
  the five DBML-cascade foreign keys at the database layer; without them, raw SQL
  deletion would contradict the frozen ERD even though ORM deletion appeared correct.

## Post-freeze amendment: city identity

The Transformer requires a deterministic city for every canonical venue. Captured RA
listing and detail payloads expose no venue-area reference; the request seed's area is
the only observed geographic identity. The frozen schema initially had no enforceable
relationship between `(TRACKED_SOURCE_PAGE.source, area_ref)` and `CITY`, leaving
label matching or a code dictionary as the only implementations. Both would encode an
unstored convention and contradict coverage-as-data.

`CITY_IDENTITY` was therefore added as a narrow, approved freeze break. It follows the
same concrete identity pattern and two uniques as its three siblings. The runner resolves
the seed through `(source, area_ref)` before making requests. A missing mapping is a
configuration defect that fails that seed loudly; it is not event-level quarantine.
No ingestion-to-canonical foreign key was introduced, so the firewall remains intact.

## Finding requiring documentation correction

The old expected count of 5 ingestion + 8 canonical + 13 app tables is incorrect. After
the approved city-identity freeze break, the adjudicated model contains
4 + 9 + 15 = 28 tables. This is not a schema violation:

- the guide itself names only four ingestion tables;
- the two app additions are the independently required registration-verification and email-change workflows;
- the canonical addition is the required seed-area-to-city identity seam;
- no table should be added or removed merely to match a stale count.
