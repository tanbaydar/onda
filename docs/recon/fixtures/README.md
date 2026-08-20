# Ingestion fixture corpus

These fixtures are test inputs for the RA listing boundary. Captured evidence and
synthetic edge cases are labeled separately; synthetic payloads imitate only fields
observed in the captured `GET_EVENT_LISTINGS` operation.

All fixtures run under seed `(ra, 8) → New York City` unless the fixture's block says
otherwise.

## Captured and sanitized

- `ra_event_listings_historical_response.sample.json` — representative subset of a
  historical Boston response. Its `totalResults` describes the original response, not
  the sanitized one-event subset, so it must not be used for exact-count tests.
- `ra_cancelled_event_detail.sample.json` — detail-query recon evidence only. It is not
  valid Transformer input.

## Synthetic listing payloads

| Scenario | Payload | Expected admission behavior |
|---|---|---|
| Complete representative page | `ra_listing_complete.synthetic.json` | 2 admitted |
| Date only | `ra_listing_date_only.synthetic.json` | admitted; `start_time = NULL` |
| TBA lineup | `ra_listing_tba_lineup.synthetic.json` | quarantined `NO_ARTIST` |
| Festival lineup | `ra_listing_festival.synthetic.json` | admitted; lineup order 1–3 |
| Sold out | `ra_listing_sold_out.synthetic.json` | admitted; ticket state is irrelevant |
| Cancellation text only | `ra_listing_cancelled_title.synthetic.json` | admitted `active`; title parsing triggers nothing |
| Structurally malformed event | `ra_listing_malformed_event.synthetic.json` | quarantined `PARSE_FAILURE` with known event ID |
| Missing event ID | `ra_listing_missing_event_id.synthetic.json` | quarantined `PARSE_FAILURE`; healthy sibling admitted |
| Whitespace-only title | `ra_listing_empty_title.synthetic.json` | quarantined `EMPTY_TITLE` |
| String-but-unparseable date | `ra_listing_bad_date.synthetic.json` | quarantined `BAD_DATE` |
| Duplicate event listings | `ra_listing_duplicate_event.synthetic.json` | 4 wrappers admitted; 2 unique events |
| Whole-payload failure | `ra_listing_malformed_payload.synthetic.txt` | payload status `failed`; no event outcomes |
| Pagination page 1 | `ra_listing_paginated_page_1.synthetic.json` | complete only together with page 2 |
| Pagination page 2 | `ra_listing_paginated_page_2.synthetic.json` | complete only together with page 1 |

The third column is a non-authoritative summary; the Expected outcomes blocks below
govern. On any disagreement, the block wins.

The pagination scenario is one test case represented by two files because one fixture
equals one HTTP response boundary. All synthetic IDs use the `syn-` prefix and can
never be confused with captured provider identifiers.
The synthetic corpus contains 14 files covering 13 scenarios; pagination is the one
scenario that spans two response-boundary files.

## `ra_listing_complete.synthetic.json`

Synthetic baseline listing containing two events that repeat the same provider venue.

### Expected outcomes

- processing_status: processed
- events admitted: 2
- events quarantined: 0 — []
- events dropped: 0
- observed source IDs: [`syn-event-complete-1`, `syn-event-complete-2`]
- VENUE rows created: 1 — [`Synthetic Hall`], each city = New York City
- ARTIST rows created: 2 — [`Synthetic Artist One`, `Synthetic Artist Two`]
- identity rows: 2 EVENT_IDENTITY, 1 VENUE_IDENTITY, 2 ARTIST_IDENTITY
- notable field assertions: both events reference the same canonical venue row;
  each event has one EVENT_ARTIST at position 1; `syn-event-complete-1` stores
  `event_date = 2026-08-14`, `start_time = 22:00`, and
  `cover_image_url = https://example.invalid/flyers/complete-1.jpg`;
  `syn-event-complete-2` stores `event_date = 2026-08-15`,
  `start_time = 23:30`, and `cover_image_url = NULL`. The Transformer derives
  `event_date` only from the date component of `event.date` and `start_time` only from
  the time component of `event.startTime`; midnight padding in `event.date` is not a
  midnight start. Explicit-null and absent flyer fields both produce NULL, rendered by
  the app as its default image.

## `ra_listing_date_only.synthetic.json`

Synthetic date-only event. Synthetic serialization: explicit-null `startTime` is
assumed; live RA may use absent fields, which the cross-cutting null-equivalence rule
covers.

### Expected outcomes

- processing_status: processed
- events admitted: 1
- events quarantined: 0 — []
- events dropped: 0
- observed source IDs: [`syn-event-date-only`]
- VENUE rows created: 1 — [`Synthetic Date Hall`], each city = New York City
- ARTIST rows created: 1 — [`Synthetic Date Artist`]
- identity rows: 1 EVENT_IDENTITY, 1 VENUE_IDENTITY, 1 ARTIST_IDENTITY
- notable field assertions: one EVENT_ARTIST at position 1;
  `event_date = 2026-08-16`, `start_time = NULL`, and `cover_image_url = NULL`.
  `start_time IS NULL` is the fixture's central assertion under Q72–73. The midnight
  padding in `event.date` is ignored and does not contradict the explicit-null
  `event.startTime`.

## `ra_listing_tba_lineup.synthetic.json`

Synthetic event with a present-but-empty artist collection.

### Expected outcomes

- processing_status: processed
- events admitted: 0
- events quarantined: 1 — [`syn-event-tba` → `NO_ARTIST`]
- events dropped: 0
- observed source IDs: [`syn-event-tba`]
- VENUE rows created: 0 — []
- ARTIST rows created: 0 — []
- identity rows: 0 EVENT_IDENTITY, 0 VENUE_IDENTITY, 0 ARTIST_IDENTITY
- notable field assertions: the quarantined event ID remains observed and must prevent
  false absence misses; one REJECTED_INGEST row is written with
  `entity_ref = syn-event-tba`, `reason = NO_ARTIST`, and a link to this payload.
  The valid title/date/time do not change the pass-4 failure. The empty artist array
  exercises collection equivalence.

## `ra_listing_festival.synthetic.json`

Synthetic multi-artist festival. Per A6, a festival is an ordinary event; the only
festival-specific shape exercised here is a larger artist collection.

### Expected outcomes

- processing_status: processed
- events admitted: 1
- events quarantined: 0 — []
- events dropped: 0
- observed source IDs: [`syn-event-festival`]
- VENUE rows created: 1 — [`Synthetic Festival Grounds`], each city = New York City
- ARTIST rows created: 3 — [`Synthetic Opener`, `Synthetic Middle`,
  `Synthetic Headliner`]
- identity rows: 1 EVENT_IDENTITY, 1 VENUE_IDENTITY, 3 ARTIST_IDENTITY
- notable field assertions: exactly 3 EVENT_ARTIST rows map source array indices
  0, 1, 2 to positions 1, 2, 3 respectively:
  `Synthetic Opener → 1`, `Synthetic Middle → 2`, `Synthetic Headliner → 3`.
  The source supplies array order only and no position field; position is array order
  plus one. Presentation order is stored without reordering by importance—the
  adversarially named `Synthetic Headliner` remains third. The event stores
  `event_date = 2026-08-18`, `start_time = 14:00`, and
  `cover_image_url = https://example.invalid/flyers/festival.jpg`. No end-date or
  multi-day behavior is asserted because none exists in the contract.

## `ra_listing_sold_out.synthetic.json`

Synthetic event carrying ticket inventory fields and an explicit sold-out tag.

### Expected outcomes

- processing_status: processed
- events admitted: 1
- events quarantined: 0 — []
- events dropped: 0
- observed source IDs: [`syn-event-sold-out`]
- VENUE rows created: 1 — [`Synthetic Sold Out Hall`], each city = New York City
- ARTIST rows created: 1 — [`Synthetic Sold Out Artist`]
- identity rows: 1 EVENT_IDENTITY, 1 VENUE_IDENTITY, 1 ARTIST_IDENTITY
- notable field assertions: one EVENT_ARTIST at position 1; the event stores
  `event_date = 2026-08-19`, `start_time = 21:00`, `cover_image_url = NULL`, and
  `status = active`. The entire `tickets` and `ticketing` subtree—including
  `ticketing.tags[].type = SOLD_OUT`—is unread by the Transformer. It is not read and
  mapped to active. Onda models attendance and memory, not ticket inventory, and the
  frozen schema has no sold-out state.

## `ra_listing_cancelled_title.synthetic.json`

Synthetic event whose title contains cancellation prose. Its marker styling
deliberately differs from the captured evidence (`[CANCELLED]` bracketed): no styling
is recognized, so the difference is immaterial by design. Promoters write
cancellation into titles in arbitrary formats, and Onda preserves all of them
verbatim.

### Expected outcomes

- processing_status: processed
- events admitted: 1
- events quarantined: 0 — []
- events dropped: 0
- observed source IDs: [`syn-event-cancelled-title`]
- VENUE rows created: 1 — [`Synthetic Cancellation Hall`], each city = New York City
- ARTIST rows created: 1 — [`Synthetic Cancellation Artist`]
- identity rows: 1 EVENT_IDENTITY, 1 VENUE_IDENTITY, 1 ARTIST_IDENTITY
- notable field assertions: one EVENT_ARTIST at position 1; the event stores
  `event_date = 2026-08-20`, `start_time = 22:00`, `cover_image_url = NULL`,
  `status = active`, and the title verbatim as `CANCELLED: Synthetic Night`.
  Under A1-revised, the Transformer performs no title pattern-matching: it does not
  detect or strip cancellation markers, nor infer status from title prose in any
  punctuation style. The cancellation text remains only as faithfully preserved
  cosmetic title content. The venue's `live = true` field is outside the closed
  event-field set and carries no assertion.

## `ra_listing_malformed_event.synthetic.json`

Synthetic parseable listing envelope containing one structurally malformed event and
one healthy sibling. The malformed event deliberately has multiple defects so the
fixture exercises rejection-reason precedence rather than a single-field special
case.

### Expected outcomes

- processing_status: processed
- events admitted: 1
- events quarantined: 1 — [`syn-event-malformed` → `PARSE_FAILURE`]
- events dropped: 0
- observed source IDs: [`syn-event-malformed`, `syn-event-malformed-sibling`]
- VENUE rows created: 1 — [`Synthetic Healthy Hall`], each city = New York City
- ARTIST rows created: 1 — [`Synthetic Healthy Artist`]
- identity rows: 1 EVENT_IDENTITY, 1 VENUE_IDENTITY, 1 ARTIST_IDENTITY
- notable field assertions: one REJECTED_INGEST row is written with
  `entity_ref = syn-event-malformed`, `reason = PARSE_FAILURE`, and a link to this
  payload. The malformed event's object-valued `date` and absent `venue` prevent its
  DTO from being built in pass 1; later defects are not evaluated. Its otherwise
  ID-bearing artist creates no canonical row because quarantine rolls back the event's
  entire canonical transaction. The healthy sibling is isolated from that failure and
  stores `event_date = 2026-08-21`, `start_time = 23:00`,
  `cover_image_url = NULL`, and one EVENT_ARTIST at position 1. The payload remains
  processed because its envelope parsed and both contained events received outcomes.

## `ra_listing_missing_event_id.synthetic.json`

Synthetic parseable listing envelope containing one event without an `id` key and one
fully healthy sibling.

### Expected outcomes

- processing_status: processed
- events admitted: 1
- events quarantined: 1 — [`entity_index = 0` → `PARSE_FAILURE`,
  `entity_ref = NULL`]
- events dropped: 0
- observed source IDs: [`syn-event-missing-id-sibling`]
- VENUE rows created: 1 — [`Synthetic Missing ID Healthy Hall`], each city =
  New York City
- ARTIST rows created: 1 — [`Synthetic Missing ID Healthy Artist`]
- identity rows: 1 EVENT_IDENTITY, 1 VENUE_IDENTITY, 1 ARTIST_IDENTITY
- notable field assertions: one REJECTED_INGEST row is written with
  `entity_index = 0`, `entity_ref = NULL`, `reason = PARSE_FAILURE`, and a link to this
  payload. The healthy sibling remains isolated and writes its canonical and identity
  rows. Because one listing wrapper has no usable nested `event.id`, the second
  content condition for SeedFetchOutcome completeness fails and reconciliation is
  skipped for this seed in this run. The sibling's canonical writes still land:
  incomplete fetches can add, never subtract. The arithmetic reconciles:
  1 admitted + 1 quarantined = 2 payload events ≥ 1 observed source ID.

## `ra_listing_empty_title.synthetic.json`

Synthetic single-event payload with a structurally valid but whitespace-only title.

### Expected outcomes

- processing_status: processed
- events admitted: 0
- events quarantined: 1 — [`syn-event-empty-title` → `EMPTY_TITLE`]
- events dropped: 0
- observed source IDs: [`syn-event-empty-title`]
- VENUE rows created: 0 — []
- ARTIST rows created: 0 — []
- identity rows: 0 EVENT_IDENTITY, 0 VENUE_IDENTITY, 0 ARTIST_IDENTITY
- notable field assertions: one REJECTED_INGEST row is written with
  `entity_ref = syn-event-empty-title`, `reason = EMPTY_TITLE`, and a link to this
  payload. The whitespace-only string reaches pass 5 and is empty after full
  whitespace trimming. Quarantine rollback leaves zero canonical writes despite the
  otherwise valid venue and artist.

## `ra_listing_bad_date.synthetic.json`

Synthetic single-event payload whose date has the expected string type but an
unparseable value.

### Expected outcomes

- processing_status: processed
- events admitted: 0
- events quarantined: 1 — [`syn-event-bad-date` → `BAD_DATE`]
- events dropped: 0
- observed source IDs: [`syn-event-bad-date`]
- VENUE rows created: 0 — []
- ARTIST rows created: 0 — []
- identity rows: 0 EVENT_IDENTITY, 0 VENUE_IDENTITY, 0 ARTIST_IDENTITY
- notable field assertions: one REJECTED_INGEST row is written with
  `entity_ref = syn-event-bad-date`, `reason = BAD_DATE`, and a link to this payload.
  The string-valued `date = not-a-date` passes structural parsing but fails value
  validation in pass 5. Quarantine rollback leaves zero canonical writes despite the
  otherwise valid title, venue, and artist.

## `ra_listing_duplicate_event.synthetic.json`

Synthetic listing payload modeled on the duplicate-wrapper behavior observed during
the first supervised live run. Four listing wrappers are present; three carry the
same nested `event.id`, while `totalResults` counts all four wrappers.

### Expected outcomes

- processing_status: processed
- events admitted: 4
- events quarantined: 0 — []
- events dropped: 0
- observed source IDs: [`syn-event-duplicate`, `syn-event-duplicate-sibling`]
- VENUE rows created: 1 — [`Synthetic Duplicate Hall`], each city = New York City
- ARTIST rows created: 2 — [`Synthetic Repeated Artist`, `Synthetic Unique Artist`]
- identity rows: 2 EVENT_IDENTITY, 1 VENUE_IDENTITY, 2 ARTIST_IDENTITY
- notable field assertions: all four observations complete canonical upserts, but
  the three wrappers carrying `syn-event-duplicate` resolve through one
  EVENT_IDENTITY to exactly one canonical EVENT row. Final canonical state contains
  exactly 2 EVENT rows. `observed_source_ids` is the unique event-grain set of two
  IDs. SeedFetchOutcome is complete because wrapper coverage is
  `4 = totalResults 4`, every wrapper carries a usable nested `event.id`, and duplicate
  event IDs are expected and harmless.

## `ra_listing_malformed_payload.synthetic.txt`

Synthetic HTTP-200 response body containing a Cloudflare-style HTML challenge rather
than JSON. This fixture exercises the payload grain, not the event grain.

### Expected outcomes

- processing_status: failed
- events admitted: 0
- events quarantined: 0 — []
- events dropped: 0
- observed source IDs: []
- VENUE rows created: 0 — []
- ARTIST rows created: 0 — []
- identity rows: 0 EVENT_IDENTITY, 0 VENUE_IDENTITY, 0 ARTIST_IDENTITY
- notable field assertions: zero REJECTED_INGEST rows are written. Whole-payload
  failure lives only on RAW_INGEST's processing status because no entity reference can
  be extracted. The harness archives the `.txt` body verbatim in the LONGTEXT
  `response_body` before transformation, preserving failure evidence regardless of
  format. The Transformer's only verdict is `failed`; it performs no event-level
  interpretation. Despite HTTP status 200, the unparseable listing envelope violates
  SeedFetchOutcome completeness. The seed is incomplete for this run, reconciliation
  is skipped for it, and no event accrues an absence miss from this fetch. Nothing
  observed is distinct from nothing listed: garbage input produces silence, never
  evidence of absence.

## Pagination scenario

Files: `ra_listing_paginated_page_1.synthetic.json` and
`ra_listing_paginated_page_2.synthetic.json`.

Harness metadata is declared here, not derived from filenames or payload contents.
Both pages run under the default seed in one run with
`window_start = 2026-08-22`, `window_end = 2026-08-23`, and `page_size = 2`.
Page 1 has `page_number = 1`; page 2 has `page_number = 2`. Both responses report
`totalResults = 3`, so the expected page count is
`ceil(totalResults / page_size) = ceil(3 / 2) = 2`. The construction is internally
consistent by design: page 1 is full with two events, page 2 contains the one-event
remainder, and `totalResults` agrees across both pages. That agreement is part of the
SeedFetchOutcome completeness check.

### Page 1 expected outcomes

- processing_status: processed
- events admitted: 2
- events quarantined: 0 — []
- events dropped: 0
- observed source IDs: [`syn-event-page-1-a`, `syn-event-page-1-b`]
- VENUE rows created: 1 — [`Synthetic Paging Hall`], each city = New York City
- ARTIST rows created: 2 — [`Synthetic Page Artist A`, `Synthetic Page Artist B`]
- identity rows: 2 EVENT_IDENTITY, 1 VENUE_IDENTITY, 2 ARTIST_IDENTITY
- notable field assertions: each event has one EVENT_ARTIST at position 1. The
  Transformer handles this page as an ordinary payload and has no pagination
  responsibility. The payload arithmetic reconciles: 2 admitted + 0 quarantined =
  2 event objects = 2 observed source IDs.

### Page 2 expected outcomes

- processing_status: processed
- events admitted: 1
- events quarantined: 0 — []
- events dropped: 0
- observed source IDs: [`syn-event-page-2-a`]
- VENUE rows created: 0 — []; venue resolution hits the VENUE_IDENTITY created from
  page 1 and reuses the existing `Synthetic Paging Hall` canonical row
- ARTIST rows created: 1 — [`Synthetic Page Artist C`]
- identity rows: 1 EVENT_IDENTITY, 0 VENUE_IDENTITY, 1 ARTIST_IDENTITY
- notable field assertions: the event has one EVENT_ARTIST at position 1. This page
  proves identity-backed canonical reuse across payloads, not merely within one
  payload. The Transformer handles it as an ordinary payload and has no pagination
  responsibility. The payload arithmetic reconciles: 1 admitted + 0 quarantined =
  1 event object = 1 observed source ID.

### Combined seed-level expectations

- Final canonical state: exactly 3 EVENT rows, 1 VENUE row, and 3 ARTIST rows.
- Final identity state: exactly 3 EVENT_IDENTITY rows, 1 VENUE_IDENTITY row, and
  3 ARTIST_IDENTITY rows.
- Seed-level observed source-ID union:
  [`syn-event-page-1-a`, `syn-event-page-1-b`, `syn-event-page-2-a`].
  Its cardinality is 3 at event grain. This fixture happens to contain no duplicate
  event IDs, but observed-ID cardinality is not a completeness predicate.
- SeedFetchOutcome is complete: both expected pages were fetched, both were processed,
  both reported the same total, all 3 listing wrappers carry usable nested event IDs,
  and wrapper coverage matches `totalResults = 3`.
  This seed's current-run observations are therefore eligible to feed reconciliation.
- Negative twin: if page 2 instead fails at transport or receives a `failed`
  processing verdict, the union is partial, SeedFetchOutcome is incomplete, and
  reconciliation is skipped for the seed. Page 1's two admitted events still write
  canonically: canonical writes do not wait for completeness; only absence proof does.
  Incomplete fetches can still add, never subtract.

## Cross-cutting expectations

- Double-transform idempotency: transforming the same payload twice produces
  byte-identical database state across every canonical table, every identity table,
  and every REJECTED_INGEST row. The assertion standard is a full-state comparison,
  not row counts. Rejection writes achieve this through insert-or-ignore against
  `uq_rejection_payload_index`. This is invariant #2 as executable truth and applies
  to every fixture, including the failed-payload fixture: re-transforming it yields
  `failed` again and still produces zero writes.
- Changed-event upsert-in-place: re-transforming a payload in which a previously
  admitted event has a changed start time, flyer, or title updates the same canonical
  EVENT row in place, preserving both its primary key and its EVENT_IDENTITY. It never
  creates a second event or deletes and recreates the event itself. Lineup replacement
  is the already-recorded mechanism-level exception: its join rows are deleted and
  reinserted while the canonical event identity remains stable.
- Unmapped-seed refusal is a runner-level contract exercised in test file #4. A seed
  whose `(source, area_ref)` has no CITY_IDENTITY mapping is a configuration defect
  refused before any fetch. The runner records the defect in `error_summary`, performs
  zero requests for that seed, archives nothing, and allows no event to accrue an
  absence miss from it. It is never represented as per-event quarantine.
- Provider event identity: `entity_ref`, observed source IDs, and
  EVENT_IDENTITY.source_id use the nested `event.id`, never the listing wrapper's
  `id`. `entity_ref = event.id` when present and is NULL when the event carries no ID;
  `entity_index` always locates the observation within its payload. A listing wrapper
  represents RA's act of listing and is not the stable event identity.
- Seed completeness has two content conditions: archived listing-wrapper coverage
  equals wrapper-grain `totalResults`, and every wrapper carries a usable nested
  `event.id`. Duplicate event IDs are expected and harmless. Reconciliation receives
  the unique event-grain observed-ID set, never wrapper IDs or wrapper cardinality.
- Arithmetic: admitted + quarantined = listing-wrapper count ≥ unique observed-ID
  count. Equality holds exactly when every wrapper carries an `event.id` and no
  event ID is repeated across wrappers.
- Envelope traversal versus domain fields: `data`, `eventListings`, `totalResults`,
  the listing-wrapper `data[]`, and nested `event` are navigation keys read only to
  reach event objects and paginate completely. The wrapper's `id` and `listingDate`
  are unread and cannot influence identity, admission, status, or canonical values.
- Rejection-reason precedence is pass order: an event's reason is the first pass it
  fails, and later defects in the same event are never evaluated or reported.
  Type-shape belongs to pass-1 parsing; value-validity belongs to pass-5 validation.
  Therefore a non-string date is `PARSE_FAILURE`, while a string-valued but
  unparseable date is `BAD_DATE`.
- Optional-field null equivalence: for `startTime`, flyer, and every future optional
  source field, an explicitly null field and an absent field both produce the canonical
  column's NULL. The Transformer must not distinguish them. The date-only fixture
  exercises the explicit-null arm; absent-field handling must use the same code path.
- Collection equivalence: an absent collection field, explicit null, and an empty array
  all mean no entries and must use the same code path.
- Quarantine rollback: a quarantined event produces zero canonical writes from its
  event transaction. Only its idempotent REJECTED_INGEST occurrence persists, written
  after canonical rollback. Canonical entities shared with an admitted sibling may
  still exist because the sibling earned them; quarantine never deletes those rows.
- Quarantine retry: when a later observation of the same event fills the admission gap,
  that later successful event transaction creates its VENUE, ARTIST, EVENT_ARTIST, and
  identity rows. No partial canonical graph is retained merely to prepare for retry.
- Lineup replacement: a changed lineup on re-observation atomically deletes and
  reinserts that event's EVENT_ARTIST rows in the new source-array order. The
  idempotency suite must include a reorder of the same event and assert the same join-row
  count, updated positions, and no intermediate unique-constraint violation.
- Closed event-field set: the Transformer reads exactly `id`, `title`, `date`,
  `startTime`, `venue.id`, `venue.name`, `artists[].id`, `artists[].name`, and
  `flyerFront`. Every other event key—including `tickets`, `ticketing`, `contentUrl`,
  `live`, and keys RA adds later—is unread. Unknown fields must neither break parsing
  nor influence admission, status, or any canonical value.
- Rejection coverage: every rejection reason reachable in v1 has an exercising
  fixture. `OUT_OF_SCOPE` alone is unexercised because A8 makes it unreachable in v1.
