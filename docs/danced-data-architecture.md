# Danced — Data Architecture (High Level)

**Scope:** The journey of event data: where it lives in the world → how we find it → how it becomes rows in the tables we want.
**Foundational assumption:** Danced's knowledge of events is exactly what Resident Advisor lists. No user-created events, no second source, no manual catalog entry. If it isn't on RA, it doesn't exist for us — by design.
**Design goal:** Consistency over completeness. Every row in our canonical tables is provably valid; missing events are an accepted consequence of source coverage, never a data-quality defect.

**Product/catalog boundary:** MVP catalog scope is Resident Advisor listings for the seeded launch cities. This is a coverage fact, not a product redefinition. Danced remains genre-agnostic at the application layer: diary, ratings, reviews, social behavior, profiles, and discovery contain no electronic-only rules and must work unchanged for any physical music event. The broader “all physical music events” ambition describes the product's design envelope, not v1 catalog completeness.

Canonical entities are source-neutral. Provider identifiers live in the concrete
`EVENT_IDENTITY`, `VENUE_IDENTITY`, and `ARTIST_IDENTITY` tables. Adding a provider
such as Ticketmaster requires no canonical schema change, but it does require an
entity-matching process whose output is new identity rows. The mapping structure makes
cross-source attachment possible; it does not make cross-source matching automatic.

---

## The shape of the system

Data flows one direction through four layers. Each layer has exactly one responsibility, one owner, and one guarantee it makes to the layer above it. No layer reaches around another.

```
┌─────────────────────────────────────────────────────┐
│  LAYER 0 — THE SOURCE (Resident Advisor)            │
│  The world's club-event listings, behind GraphQL     │
└──────────────────────┬──────────────────────────────┘
                       │  nightly fetch
┌──────────────────────▼──────────────────────────────┐
│  LAYER 1 — ACQUISITION                              │
│  Ask RA what's on; archive every answer verbatim     │
│  Guarantee: nothing RA ever told us is lost          │
└──────────────────────┬──────────────────────────────┘
                       │  validate + normalize
┌──────────────────────▼──────────────────────────────┐
│  LAYER 2 — ADMISSION                                │
│  Strict gate: valid events pass, rest quarantined    │
│  Guarantee: nothing malformed gets through           │
└──────────────────────┬──────────────────────────────┘
                       │  upsert
┌──────────────────────▼──────────────────────────────┐
│  LAYER 3 — CANONICAL CATALOG                        │
│  The tables we want: EVENT, VENUE, ARTIST            │
│  Guarantee: every row satisfies the product contract │
└──────────────────────┬──────────────────────────────┘
                       │  read-only
                 [ the Danced app ]
```

---

## Layer 0 — The source

Resident Advisor is the club scene's listings directory. Because RA is a *directory* rather than a ticket seller, it lists events regardless of who sells the tickets — which makes it the single source with the fewest coverage holes for our domain. Its website runs on a GraphQL endpoint with a typed schema: events, venues, artists, promoters, and genres are first-class objects, each with a stable ID.

Three properties of the source shape everything downstream:

- **Typed and ID'd.** We consume a declared schema, not guessed JSON. Stable IDs make deduplication trivial and updates unambiguous.
- **Unofficial.** There is no permission, contract, or stability guarantee. RA can change the schema or block us at any time. This risk is accepted and deliberately confined to Layer 1 — it can never reach the catalog or the app.
- **Living.** Events appear with incomplete data (lineup TBA), get edited, get rescheduled, and disappear. The pipeline is designed around data that changes under it, not around a static dump.

**What we ask for:** upcoming event listings for a small set of city areas (New York, Boston), fetched nightly. Seeds are RA area IDs — a handful of rows in a registry table. Growing coverage means inserting a row, never writing code.

Before launch, the same acquisition path targets the trailing 24 months for those seeded cities as a bounded historical backfill. It pages through date windows chronologically, with the same sequential requests, throttling, backoff, raw archiving, admission checks, quarantine behavior, and canonical upserts as the nightly job.

### Source reconnaissance gate

Before explicit cancellation handling is implemented:

- Find a visibly cancelled event on Resident Advisor.
- Capture the listing and event-detail GraphQL responses for it.
- Identify whether cancellation is represented by a typed status, boolean, enum, or another explicit field.
- Verify that the signal is stable across at least the listing and detail shapes used by acquisition.
- Record fixtures for active and cancelled events.

Before historical backfill is enabled:

- Confirm that the RA listing query accepts past date ranges for a seeded city.
- Capture and archive at least one historical listing response.
- Confirm pagination behavior across bounded historical date windows.
- Confirm that historical records contain the fields required by the admission contract.

Until this reconnaissance confirms an explicit source signal, the cancellation wipe branch is designed but unbuilt. Disappearance-to-hide is the only live removal path. If no trustworthy explicit cancellation signal exists, cancellation handling reverts to absence handling: hide after the miss threshold and preserve all user content.

If historical-query reconnaissance fails, the backfill is not approximated through scraping or user-path fetches. V1 falls back explicitly to launch-forward catalog coverage.

---

## Layer 1 — Acquisition (find the data, lose nothing)

One nightly job. For each active city seed, it sends RA's own listing query — the same request the RA website makes — pages through results politely (sequential, delayed, backoff on errors), and writes every response **verbatim** into an append-only archive table:

**`RAW_INGEST`** — the payload exactly as received, which seed produced it, when, and the HTTP status.

This layer performs no event-domain transformation. The RA client knows only request
construction and the transport/pagination envelope (`totalResults`, page coverage, and
GraphQL errors); the Transformer alone knows event-domain shape and canonical mappings.
Every response body is archived verbatim regardless of transient envelope metadata.
That separation of *fetching* from *understanding* is what makes the system survivable:

- **RA changes their schema →** we fix one module downstream and replay the archive. Zero data loss, ever.
- **A fetch fails →** the failure is recorded as data (status code, no payload) and the seed is flagged for this run. A failed fetch must never be mistaken for "the events are gone" — this distinction feeds Layer 2's lifecycle logic.
- **We were wrong about a mapping →** replay the archive through the corrected logic. The archive is the system's undo button.

The fetcher is the *only* replaceable part by design: if RA tightens anti-bot measures, a rented third-party actor can be swapped in behind the same interface, and Layers 2–3 never know.

### Acquisition execution contract

- Requests are sequential and share a hard per-run request ceiling. Retries consume the
  same ceiling.
- Bounded exponential backoff with jitter applies only to network errors, HTTP 408,
  HTTP 429 (honoring `Retry-After`), and HTTP 500/502/503/504. Ordinary 4xx responses
  are not retried.
- Expected transport exceptions become archived result values. Configuration errors,
  programming defects, and database failures escape to the runner and crash the run.
- A typed seed outcome is complete only when every expected page has a successful HTTP
  response, a usable listing envelope with no invalidating GraphQL errors, internally
  consistent page coverage, and a corresponding archived response.
- `last_synced_at` is written by the runner after a seed attempt finishes.
  `last_success_at` advances only after the entire seed outcome is complete; no
  individual page can claim seed success.
- One MySQL advisory lock permits exactly one active runner. Cron and manual invocations
  use the same lock and entry point; a second invocation exits without starting a run.

### Bootstrap and live ingestion are one path

Historical bootstrap is not a separate importer. It is the nightly pipeline pointed at bounded past date windows:

1. Seeded cities only.
2. Trailing 24 months only.
3. Windows processed chronologically.
4. Every response archived through `RAW_INGEST`.
5. Every event admitted, quarantined, and upserted through the same code used in live ingestion.
6. Safe to restart or replay because all canonical writes are idempotent.

The backfill may fail partway and resume or restart without cleanup. There is no second validation contract and no historical-only repair logic.

### No acquisition in the user request path

On-demand RA fetching from search, event pages, or any other user action is permanently rejected, not deferred.

- The application never imports RA-shaped code or identifiers.
- User-facing latency and availability never depend on RA.
- Rate limits or blocking can freeze catalog growth but cannot break search or diary reads.
- A catalog miss remains a catalog miss until an asynchronous ingestion run supplies the event.

---

## Layer 2 — Admission (the gate between their data and our tables)

The Transformer reads unprocessed archive rows and processes each event **individually** — one bad event never poisons its siblings — inside its own database transaction, so canonical writes are all-or-nothing. It is the only code in the entire system that knows RA's shape.

Every event faces a fixed sequence of checks derived directly from the product spec:

1. **Parse** the typed payload; structurally broken → quarantine.
2. **Scope**: v1 scope is membership in a tracked RA area. No reliable per-event type
   field is confirmed in the listing payload, so `OUT_OF_SCOPE` remains a reserved,
   currently unused reason. A future reliable field may activate explicit scope drops.
3. **Resolve entities**: for each RA venue and artist, look up its concrete identity
   table by `(source, source_id)`. A hit resolves the canonical row. A miss creates the
   canonical row and mapping in the same transaction. Within v1, one RA identity
   therefore resolves forever to one canonical row. An event with no resolvable artist
   → quarantine.
4. **Validate the event**: non-empty title, parseable venue-local date (time optional and honestly nullable — no fake midnights), image URL or an explicit null that the app renders as a default. Any hard failure → quarantine. The rule is **strict: reject, never repair.** No synthesized titles, no guessed timezones. Every repair heuristic is a lie told to our own catalog.
5. **Upsert through the identity seam**: look up `EVENT_IDENTITY`. On hit,
   field-level update the mapped canonical event. On miss, create the canonical event
   and mapping in the same transaction. Fully idempotent: the same payload processed a
   thousand times produces identical state.

The Transformer sweeps all `RAW_INGEST.processing_status = pending` rows, including
leftovers from crashed runs. Each event receives its own transaction. The payload moves
to `processed` only after every event has an outcome, outside the event transactions;
an unusable envelope becomes `failed`, and a crash leaves it `pending`. Recovered
payloads may update canonical state and current execution telemetry, but only observations
from the current run's complete seed outcome may drive that run's reconciliation.

`events_upserted` means event observations that passed admission and completed a
canonical upsert during this execution, whether the row was inserted, changed, or
already identical. The frozen column name remains; this definition preserves the
zero-admission alarm.

**Quarantine is a state, not a verdict.** Rejected events land in `REJECTED_INGEST` with a machine-readable reason (`NO_ARTIST`, `BAD_DATE`, …). Because the same city pages are re-fetched nightly, every quarantined event retries automatically — the club night whose lineup gets announced two weeks out admits *itself* the night RA publishes it. The quarantine table doubles as the data-quality dashboard: "why is the catalog thin" is a GROUP BY, not an investigation.

**Lifecycle handling** (data that changes under us):

- Event edited on RA → silent in-place update; user states attached to the event follow automatically.
- Explicit RA cancellation signal on a future-dated event → mark hidden and apply the Q159 cascade. Delete **Will Be There** states and their feed items, plus any edge-case Been entries, ratings, reviews, and likes. Because normal logging opens only at the event start, future cancellations should rarely have diary content.
- Explicit RA cancellation signal on a past-dated event → mark hidden, preserve all user-created content, and emit a warning for later review. Historical diary integrity outranks destructive cancellation when these rules collide.
- Future event vanishes from listings → marked `unverified` after one miss, `hidden` after three consecutive misses. Hidden events leave browsing but **user content is never deleted by the pipeline** — absence alone can only hide, never destroy.
- A miss counter advances only after a successful, complete fetch for the event's seed omits the event.
- Fetch failure, incomplete pagination, or an unusable source response → no miss and no lifecycle state change.
- Past events are never touched by absence logic. History is permanent, which is exactly what a diary product requires.

The Transformer returns the observed event source-ID set for each payload. The runner
unions those sets across the current seed's complete page coverage and passes that set
plus the covered window to the reconciler. Listed-but-quarantined IDs still count as
observed: an existing mapped identity resets `misses` even while its latest observation
is degraded. Backfill and replay runs never execute absence reconciliation.

**Absence register note:** absence is a per-source observation, not a canonical fact.
`last_seen_at` and `misses` therefore live on `EVENT_IDENTITY`. The reconciler derives
canonical `EVENT.status` across all identities: any source still vouching for an event
keeps it active.

---

## Layer 3 — The canonical catalog (the tables we want)

The destination. Owned by the pipeline for writes, read-only for everything else.

- **`EVENT`** — source-neutral title, date, nullable start time, venue reference, image URL, and derived lifecycle status.
- **`VENUE`** — source-neutral name and city reference. Timezone lives on the city reference table and drives when an event becomes loggable.
- **`ARTIST`** — source-neutral artist identity and name.
- **`EVENT_ARTIST`** — the lineup, order preserved.
- **`EVENT_IDENTITY`, `VENUE_IDENTITY`, `ARTIST_IDENTITY`** — concrete provider
  mappings with real canonical foreign keys. Each table enforces
  `UNIQUE(source, source_id)` and `UNIQUE(canonical_id, source)`.
- **`EVENT_IDENTITY` observations** — `last_seen_at` and consecutive `misses` live at
  the source-testimony grain where they are true.

Two structural rules carry the whole consistency story:

- **Provider identity is separate from canonical identity.** V1 creates exactly one RA mapping for every imported canonical entity. Adding a provider requires no schema change; it requires a matching process that either attaches a new identity to an existing canonical row or creates a new canonical row and identity together.
- **Mapping does not equal matching.** Determining that two provider records describe
  the same real-world event, venue, or artist is an entity-resolution problem. It is
  explicitly future work, and its durable output is rows in the type-appropriate
  identity table.
- **The firewall rule:** nothing above this layer imports anything RA-shaped. The app references internal IDs only. If RA vanished tomorrow, Danced keeps running on the catalog as-of-yesterday; only new events stop arriving.

The guarantee this layer gives the application: *every row here passed the admission contract.* The entire app — diary, ratings, reviews, feeds, discovery — is therefore written with zero defensive validation. Consistency is enforced once, at one gate, instead of hoped-for everywhere.

---

## The invariants (what makes this architecture valid)

1. **The archive is truth about what RA said. The catalog is truth about what passed our contract. Quarantine is the diff, with reasons.** All downstream state is rebuildable from the first onto the last two.
2. **Idempotent everywhere.** Replay is always safe; nothing stochastic ever writes to canonical tables.
3. **One adapter boundary knows the source.** The client knows RA transport and
   pagination; the Transformer knows RA event-domain fields. No catalog consumer or app
   code knows either shape.
4. **Destruction requires explicit signals and temporal safety.** Missing data hides; it never deletes what users created. Even an explicit cancellation signal cannot delete past-event diary history.
5. **Every failure has a name.** No silent data loss anywhere in the flow.
6. **Canonical identity is source-neutral.** Provider records attach through concrete
   identity tables. Adding a provider is schema-stable but work-required: entity
   matching must produce valid mappings.

---

## Accepted consequences of the foundational assumption

- Catalog coverage = RA's coverage of our cities. Gaps are accessibility facts, not bugs.
- The de facto v1 catalog is a club-culture catalog for the seeded launch cities, initially New York and Boston. This is the launch wedge, not a permanent genre boundary.
- Mainstream concerts outside RA coverage may not exist in v1 even though the product model supports them.
- Target v1 history is the trailing 24 months in seeded cities plus forward coverage, contingent on reconnaissance confirming past-date listing queries.
- If historical queries are unsupported, catalog history begins at first sync and retroactive logging is limited to the accumulated canonical catalog.
- If RA blocks us, the catalog freezes (gracefully) until the fetcher is swapped.
- RA's occasional errors (wrong date, misassigned venue) become our errors until RA corrects them and the next sync propagates the fix.

Each is accepted with eyes open, because the alternative to a single well-handled dependency is many badly-handled ones.
