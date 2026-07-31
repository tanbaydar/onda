# Danced — Project State and Conversation Handoff

> Last verified: 2026-07-30 (America/New_York)
>
> Repository: `/Users/ilkerbaydar/Desktop/danced_app`
>
> Git branch and HEAD: `main` at `0cb3600`
>
> Purpose: give a new Codex conversation enough reliable context to continue this
> project without reopening settled architecture or guessing about local runtime
> state.

## Read this first

Danced is a resume project: a Letterboxd-style social diary for live music and
dance-music events. The finished product is intended to let users discover events,
mark attendance intentions, log and rate attended events, write reviews, follow
other users, and browse social activity.

The project is currently between two milestones:

- **Milestone 1 is complete:** the ingestion and canonical catalog pipeline exists,
  is tested, has ingested real Resident Advisor data, and is scheduled locally.
- **Milestone 2 has not started:** there is not yet a catalog API, usable website,
  React application, authentication flow, diary UI, or social layer.

Do not mistake the large product schema in `docs/danced.dbml` for fully implemented
Django models. Only the ingestion and catalog zones have been transcribed into
Django. The 15 user-facing/application tables remain design only.

The most important workflow rule is:

> Do not silently redesign settled behavior while implementing it. The DBML,
> architecture document, fixture expectations, and committed tests are contracts.
> If implementation exposes a genuine contradiction, raise it explicitly and
> perform a documented freeze-break with focused contract coverage.

## Immediate state summary

### What works

- Django 6 application scaffold.
- MySQL-backed ingestion and catalog models with migrations.
- RA GraphQL client built from captured request evidence.
- Raw response archival.
- Event-level transformation and quarantine.
- Source-neutral canonical catalog with concrete identity tables.
- Idempotent replay and upsert behavior.
- Absence reconciliation and event resurrection.
- Seed completeness checks at the correct listing-wrapper grain.
- Sequential pagination, fixed politeness delay, bounded retry behavior, and a
  per-run request ceiling.
- MySQL advisory lock preventing overlapping syncs.
- Management command for nightly and bounded backfill runs.
- Two live cities: New York City and Boston.
- Real catalog populated from RA.
- Local macOS `launchd` job scheduled daily at 4:00 PM.
- Homebrew MySQL registered as a user background service.
- 44 ingestion tests passing.

### What does not exist yet

- Public catalog endpoints or REST/GraphQL API.
- Frontend/React shell.
- Production deployment.
- Cloud database or cloud scheduler.
- User-facing account models.
- Diary entries, ratings, reviews, likes, follows, favorites, reports,
  notifications, or recent search implementation.
- External monitoring service.
- Reliable scheduling while the laptop is asleep, logged out, or powered off.

### The best next product step

Start Milestone 2 with a **read-only catalog API and a browsable frontend shell**:

1. Define the smallest read-only event-list endpoints required by Discover,
   city browsing, venue pages, and artist pages.
2. Add API tests against the existing catalog.
3. Implement Django views/serialization without changing ingestion semantics.
4. Create the frontend shell and display real NYC/Boston upcoming events.
5. Only then begin the user/account and social application zone.

This order produces a clickable resume project early. Do not begin by migrating all
15 social tables simply because they exist in the DBML.

## Sources of truth and their authority

Use these documents in this order:

1. `docs/PRODUCT_QA_SPEC.md`
   - Detailed product behavior decisions and numbered questions.
2. `docs/danced.dbml`
   - Frozen full product database blueprint: 28 tables total after
     `CITY_IDENTITY` was added.
3. `docs/ERD_REVIEW.md`
   - Architecture review record, rulings, intentional ORM deltas, and
     freeze-break changelog.
4. `docs/danced-data-architecture.md`
   - Runtime ingestion contract, lifecycle behavior, and design assumptions.
5. `docs/recon/fixtures/README.md`
   - Frozen Transformer fixture contract and cross-cutting ingestion rules.
6. `docs/RA_SOURCE_RECON.md`
   - Captured RA behavior and source reconnaissance.
7. `docs/OPERATIONS.md`
   - Nightly command, alarm behavior, and scheduler guidance.
8. `docs/danced-erd-guide.md`
   - Design/review method and rationale. It is a decision record, not scripture;
     later reviewed artifacts win if prose conflicts.
9. `docs/archive/`
   - Historical and superseded material. Never treat it as current truth.

When tests and prose appear to disagree, do not casually choose one. Read the
review changelog and Git history, identify which artifact is stale, and surface the
collision.

## Technology and local environment

### Stack

- Python 3.14 local virtual environment at `.venv/`
- Django `6.0.7`
- MySQL server `9.6.0` installed with Homebrew
- `mysqlclient==2.2.8`
- `python-dotenv==1.1.1`
- No Celery, Redis, Kafka, task queue, or external scheduler dependency
- No frontend framework installed yet

### Django settings

`config/settings.py`:

- `TIME_ZONE = "UTC"`
- `USE_TZ = True`
- UTC-aware datetime storage is mandatory.
- Venue-local calculations must use `CITY.timezone` at service boundaries.
- Never introduce naive datetimes.
- Default database:
  - engine: MySQL
  - name: `danced`
  - user: `root`
  - host: `127.0.0.1`
  - port: `3306`
- Environment overrides:
  - `DANCED_DB_NAME`
  - `DANCED_DB_USER`
  - `DANCED_DB_PASSWORD`
  - `DANCED_DB_HOST`
  - `DANCED_DB_PORT`
- `DJANGO_SECRET_KEY` is required from the environment/ignored `.env`.
- `.env` and `.venv/` are ignored and must never be committed.

### Database-service commands

MySQL is registered with Homebrew:

```sh
brew services list | grep mysql
brew services restart mysql
mysqladmin ping -uroot
```

Expected health response:

```text
mysqld is alive
```

Homebrew reporting `started` is not sufficient proof by itself. Verify an actual
connection with `mysqladmin ping` or a Django database query.

In the managed Codex sandbox, access to `127.0.0.1` or `/tmp/mysql.sock` may be
blocked even while MySQL is healthy. Database-backed verification may require an
approved unsandboxed command. This is a tool-environment restriction, not
necessarily a MySQL failure.

## Git and working-tree state

### Current committed HEAD

```text
0cb3600 docs: scope backfill to ~2 months around launch (A2), Boston Referer resolved
```

Recent important commits:

```text
cf7a86e feat: paced RA client (1.5s inter-page delay) + retry budget accounting
e282400 fix: completeness is wrapper-grain, missing-id guard preserved (live-contact freeze-break)
8d99d9d fix: RaClient sends RA-edge-required public headers (clears 403)
8249417 feat: RA client, runner, sync_ra command — full ingestion suite green (37/37)
8984ebb feat: reconciler — green against absence contract
4beccbb feat: transformer — green against contract and idempotency suites
5beb7f5 test: add runner suite (red); pin acquisition execution contract; close cancellation gate in prose
4f5eecd test: add reconciler suite (red)
81c7dd8 test: add idempotency suite (red)
2f19cb3 test: add transformer contract suite (red)
343162d docs: freeze ingestion expectations contract (13 fixtures + audit script)
5093f0c fix: freeze-break 2 — positional rejection identity (entity_index)
```

### Important: current uncommitted changes

At the time this handoff was written:

```text
 M .gitignore
 M ingestion/management/commands/sync_ra.py
?? docs/OPERATIONS.md
?? ingestion/tests/test_sync_command_alarm.py
```

These changes implement and document operator alarms:

- alarm if a run crashes;
- alarm if any seed fails;
- alarm if a completed run admits zero event observations;
- log at ERROR;
- write a clear stderr message;
- exit nonzero so scheduler stderr captures the failure;
- ignore `logs/`.

They are verified by the 44-test suite but are **not committed**. Do not discard or
overwrite them. Before large new work, review and commit them together:

```sh
git add .gitignore \
  ingestion/management/commands/sync_ra.py \
  ingestion/tests/test_sync_command_alarm.py \
  docs/OPERATIONS.md
git commit -m "ops: alarm on unhealthy nightly syncs and document scheduling"
```

The installed LaunchAgent executes the current working tree, so its behavior already
includes these uncommitted command changes. Git history and machine runtime are
therefore temporarily out of sync.

## Implemented database zones

The frozen DBML contains 28 product tables:

- ingestion: 4
- catalog and identities: 9
- application/social: 15

Only the first 13 are implemented in Django today.

### Ingestion tables

#### `TRACKED_SOURCE_PAGE`

- One row per provider area.
- Unique `(source, area_ref)`.
- Active NYC and Boston seeds exist.
- `last_synced_at` means an attempt finished.
- `last_success_at` means the entire seed coverage passed completeness.

#### `SYNC_RUN`

- Execution telemetry, not canonical state.
- Types: `nightly`, `backfill`, `replay`.
- Statuses: `running`, `completed`, `crashed`.
- Completion-time snapshots:
  - seeds attempted/failed;
  - admitted event observations;
  - quarantine occurrences;
  - drops;
  - error summary.
- `events_upserted` is historical naming. Its pinned meaning is admitted
  observations that completed canonical upsert, including inserted, changed, and
  unchanged observations.

#### `RAW_INGEST`

- One HTTP request/response per row.
- `response_body` is LONGTEXT through Django `TextField`, not JSON.
- Stores malformed HTML, plaintext errors, truncated data, and JSON verbatim.
- `NULL` body means no body was received.
- Statuses: `pending`, `processed`, `failed`.
- Payload-level parse failures set `failed` and create no per-event rejection rows.
- Request metadata includes seed, run, date window, page, and page size.

#### `REJECTED_INGEST`

- Immutable per-observation rejection occurrence.
- Key is positional:
  - `entity_index` is the zero-based listing-array position;
  - `entity_ref` is nested `event.id` when usable, otherwise `NULL`;
  - listing-wrapper IDs are never substituted.
- Unique `(raw_ingest_id, entity_index)` makes replay idempotent.
- Reasons:
  - `PARSE_FAILURE`
  - `NO_ARTIST`
  - `EMPTY_TITLE`
  - `BAD_DATE`
  - `OUT_OF_SCOPE` exists but is unreachable in v1 because no reliable scope field
    is present.
- All failures except `OUT_OF_SCOPE` are quarantine-class and retry naturally.

### Canonical catalog tables

#### `CITY`

- Curated reference data.
- Currently NYC and Boston.
- Stores IANA timezone.
- Unique `(country_code, region_code, name)`.
- v1 data is US-only, while the schema remains international-tolerant.

#### `VENUE`

- Canonical source-neutral venue.
- Fields are deliberately minimal: name and city.
- No parent venue or room-grouping model.
- Venue granularity equals RA source granularity in v1.

#### `ARTIST`

- Canonical source-neutral artist.
- Names are intentionally non-unique.
- External identity, not display name, provides provider uniqueness.

#### `EVENT`

- Canonical source-neutral event.
- Fields:
  - title
  - event date
  - nullable start time
  - venue
  - nullable cover image
  - status
- Statuses:
  - `active`
  - `unverified`
  - `hidden`
- No canonical `source` or `source_id` columns.
- No cancelled or sold-out status.
- Events are never deleted by the pipeline.

#### `EVENT_ARTIST`

- Ordered lineup join.
- `position` is RA presentation order plus one.
- No semantic headliner meaning.
- Unique event/artist pair and unique event/position.
- Lineup updates delete and reinsert join rows atomically to avoid position
  collisions.

### Identity firewall

Four concrete tables map provider identities to canonical rows:

- `CITY_IDENTITY`
- `VENUE_IDENTITY`
- `ARTIST_IDENTITY`
- `EVENT_IDENTITY`

Each table has:

- unique `(source, source_id)`;
- unique `(canonical_id, source)`;
- a real foreign key to the correct canonical type.

This split intentionally rejects a polymorphic `canonical_id` whose referential
integrity could only be enforced in application code.

The mapping tables make provider attachment possible without a schema change. They
do not solve entity matching across providers. Adding another provider requires a
matching process whose output is identity rows.

`EVENT_IDENTITY` also holds provider-grain observation state:

- `last_seen_at`
- `misses`

Observation state does not belong on canonical `EVENT`.

## Application/social schema: designed but not implemented

The DBML contains these 15 future tables:

- `DANCED_USER`
- `USERNAME_HOLD`
- `EMAIL_VERIFICATION_REQUEST`
- `EMAIL_CHANGE_REQUEST`
- `FOLLOW`
- `DIARY_ENTRY`
- `REVIEW`
- `REVIEW_LIKE`
- `WILL_BE_THERE`
- `FAVORITE_EVENT`
- `FAVORITE_ARTIST`
- `FAVORITE_VENUE`
- `NOTIFICATION`
- `REPORT`
- `RECENT_SEARCH`

Important: do not migrate all 15 preemptively. Build them when the corresponding
product layer begins. The original implementation plan is separate migrations by
zone/layer so the catalog remains demoable even before social features exist.

Refer to the DBML and ERD review for settled details such as username release,
verification request lifecycles, rating/timestamp biconditionals, cascade behavior,
notification types, report uniqueness, and service-only invariants.

## Ingestion runtime architecture

### Module map

#### `ingestion/client.py`

- `FetchResult`: frozen four-field dataclass:
  - `status_code`
  - `body_text`
  - `fetched_at`
  - `error`
- Invariant: `error` is populated iff no HTTP response occurred.
- `RaClient.fetch_page(...)` is the only transport operation.
- Request operation/query/variables originate from captured recon fixtures, not a
  hand-reconstructed GraphQL query.
- Endpoint: `POST https://ra.co/graphql`.
- No domain transformation.
- Envelope and pagination navigation are allowed; event-domain interpretation is
  Transformer-only.

#### `ingestion/transformer.py`

- Processes one `RAW_INGEST` row.
- Produces:
  - admitted count;
  - quarantined count;
  - dropped count;
  - unique observed provider event IDs.
- Owns RA event shape.
- Uses per-event transactions.
- Canonical writes roll back entirely when the event is quarantined.
- Writes the rejection after rollback in its own small transaction.
- Sets payload to `processed` only after every listing observation receives an
  outcome.
- Unusable whole payload becomes `failed`.
- Unexpected mid-payload crash leaves `pending` for later recovery sweep.

#### `ingestion/reconciler.py`

- Receives completeness verdict from runner.
- No client/network knowledge.
- No-op for:
  - incomplete fetch;
  - backfill;
  - replay.
- Judges only future events inside the covered seed window.
- Present ID resets misses.
- Absent ID increments misses.
- Derives canonical status across every identity:
  - all identities misses >= 3 → hidden;
  - otherwise all identities misses >= 1 → unverified;
  - otherwise active.
- Any provider still vouching for an event keeps it active.
- A reappearing event resurrects from hidden automatically.
- Never deletes canonical or user content.

#### `ingestion/runner.py`

- Acquires MySQL advisory lock `danced_sync_ra`.
- Creates and completes/crashes `SYNC_RUN`.
- Resolves a seed through `CITY_IDENTITY` before fetching.
- Sequentially fetches pages.
- Archives every result, including transport failures.
- Sweeps all pending raw rows, including leftovers from prior crashed runs.
- Excludes recovered stale observations from current-run reconciliation evidence.
- Evaluates per-seed completeness.
- Reconciles complete nightly runs only.
- Maintains telemetry.
- Releases lock exactly once on success and crash.

#### `ingestion/management/commands/sync_ra.py`

- Thin operator shell.
- Bare command performs nightly sync.
- `--backfill` sets run type; it does not invent a window.
- Optional:
  - `--window-start`
  - `--window-end`
  - `--page-size`
- Lock refusal exits with code 2.
- Current uncommitted changes make unhealthy completed runs exit with code 1.

### Admission pass order and rejection precedence

The first failing pass determines the rejection:

1. Structural parse and usable nested `event.id`.
2. Scope pass (currently inactive/unreachable).
3. Seed-grain city and venue resolution.
4. At least one ID-bearing artist.
5. Non-empty trimmed title and parseable date.
6. Canonical admission/upsert.

Structural type-shape failures are `PARSE_FAILURE`. A string of invalid date text is
`BAD_DATE`; a non-string date shape fails structurally first.

### Closed event-field set

Transformer domain logic reads only:

- event ID
- title
- date
- start time
- venue ID and name
- artist IDs and names
- flyer/image

Envelope keys are navigational. Ticket inventory, ticketing tags, wrapper IDs,
`live`, content URL, and unknown future keys do not steer admission, status, or
canonical values.

This is why:

- sold-out events admit as active;
- cancellation prose is preserved in the title but does not create a cancellation
  status;
- unknown fields do not break or steer ingestion.

### Cancellation policy

Captured RA evidence returned `live: true` for a cancelled event and expressed
cancellation only in title prose. Therefore:

- the pipeline performs no cancellation-title pattern matching;
- title text is preserved verbatim;
- no cancellation cascade exists;
- missing events move through absence statuses;
- the pipeline never deletes user-created history;
- any future cancellation feature must prove a structured signal and temporal
  safety before a destructive branch is even designed.

### City resolution

City resolution is seed-grain:

```text
raw.seed
  -> (source, area_ref)
  -> CITY_IDENTITY
  -> CITY
```

Why: the captured listing query does not request venue-area data. Do not infer city
from venue name, event text, Referer, or a theoretical RA schema field absent from
the captured request.

Venue-grain resolution remains a priced future change requiring:

1. amended GraphQL query;
2. new recon capture;
3. fixtures;
4. contract change;
5. Transformer update.

### Completeness: keep the grains separate

RA `totalResults` counts listing wrappers, not unique events. A single event may
appear in several wrappers.

Completeness requires exactly:

1. archived listing-wrapper count equals `totalResults`;
2. every wrapper contains a usable nested `event.id`.

Do not compare unique observed event IDs to `totalResults`.

At the same time:

- wrapper count is used for completeness;
- unique `event.id` set is used for reconciliation;
- identity upserts deduplicate canonical events.

This separation came from live first-contact evidence:

```text
274 wrappers
274 totalResults
265 unique event IDs
```

The former implementation incorrectly marked this incomplete. Freeze-break
`e282400` corrected it and added a duplicate-listing contract fixture.

### Incomplete adds, never subtracts

This is a core safety invariant:

- successfully transformed pages may add/update canonical data even if a later page
  makes the seed incomplete;
- an incomplete seed never supplies absence evidence;
- reconciliation is skipped;
- therefore partial or broken fetches can add known observations but cannot hide
  events merely because coverage was partial.

### Recovery sweep rule

Every run transforms all pending raw rows, including leftovers from crashed runs.
This safely recovers canonical updates because transformation is idempotent.

However, recovered observations were fetched in an earlier run and cannot vouch for
what RA says tonight. Their observed IDs never enter the current run’s reconciliation
set.

## RA transport posture

The client sends a fixed public, non-authenticated header set empirically required by
RA’s Cloudflare edge:

- Content-Type
- Accept
- Chrome User-Agent
- Origin
- NYC Referer
- Accept-Language

Be precise about the ethical/technical claim: the Chrome User-Agent is browser
impersonation. The justification is evidence and bounded scope, not “honest client
identification.”

The explicit boundary is:

- allowed/current:
  - public request headers;
  - fixed politeness pacing;
  - bounded retry;
  - no authentication;
- prohibited:
  - cookies;
  - credentials;
  - session tokens;
  - CAPTCHA solving;
  - interactive challenge circumvention;
  - escalating anti-bot evasion.

If RA begins requiring genuine interactive challenge completion, stop. The planned
fallback is a legitimate third-party/rented acquisition actor, not an evasion arms
race.

The NYC Referer was tested against the real captured Boston area-530 request and
returned HTTP 200. RA did not correlate the Referer with requested geography. It is
transport metadata only; city resolution remains seed-driven.

### Pacing and retry

- Pages are fetched sequentially.
- Fixed inter-page delay: 1.5 seconds before every page except the first.
- Retryable:
  - connection errors/timeouts;
  - HTTP 408;
  - HTTP 429, honoring `Retry-After`;
  - HTTP 500, 502, 503, 504.
- Ordinary 4xx responses are not retried.
- Retry uses bounded exponential backoff with jitter.
- Maximum client attempts per page: 3.
- All attempts, including retries, count against the shared run ceiling.
- Maximum request attempts per run: 1,000.
- No concurrency, adaptive rate limiter, token bucket, Celery, or worker queue.

## Fixture and test contract

### Fixture corpus

Location:

```text
docs/recon/fixtures/
```

Important files:

- captured GraphQL requests;
- sanitized live evidence;
- synthetic scenario payloads;
- malformed plaintext payload;
- `README.md` with exact expected outcomes;
- `audit_expectations.py` reproducible mechanical auditor.

The fixture README is read-only contract input during implementation. Do not let
production code and tests jointly invent new expectations.

Run the audit:

```sh
.venv/bin/python docs/recon/fixtures/audit_expectations.py
```

Latest verified result:

```text
AUDIT CLEAN: 13 JSON fixtures; counts, observed IDs, scenario IDs,
and rejection coverage agree
```

### Ingestion tests

Test modules:

- `test_transformer.py`
- `test_idempotency.py`
- `test_reconciler.py`
- `test_runner.py`
- `test_completeness_grain.py`
- `test_client_pacing.py`
- `test_sync_command_alarm.py` (currently uncommitted)

Latest verified full result:

```text
Found 44 test(s).
Ran 44 tests in 0.484s
OK
```

Standard regression commands:

```sh
.venv/bin/python manage.py test ingestion
.venv/bin/python docs/recon/fixtures/audit_expectations.py
git diff --check
```

### What the tests prove

- fixture-specific canonical and rejection outcomes;
- positional missing-ID rejection;
- complete payload vs whole-payload failure grain;
- full-state idempotency;
- canonical upsert in place;
- quarantine retry;
- null/absent optional-field equivalence;
- collection null/absent/empty equivalence;
- atomic lineup reorder;
- absence ladder and resurrection;
- incomplete/backfill/replay reconciliation refusal;
- past/out-of-window protection;
- client injection and request sequencing;
- advisory-lock refusal and release;
- recovery-sweep observation exclusion;
- crash telemetry;
- wrapper-grain completeness;
- missing-event-ID incompleteness;
- fixed inter-page pacing without sleeping in tests;
- retry-attempt budget accounting;
- operator zero-upsert alarm.

## Live database state

Last verified against local MySQL on 2026-07-30:

### Reference data

```text
CITY
1  New York City, NY, US  America/New_York
2  Boston, MA, US         America/New_York

CITY_IDENTITY
ra:8   -> New York City
ra:530 -> Boston

TRACKED_SOURCE_PAGE
1  ra:8    New York City  active
2  ra:530  Boston         active
```

Both seeds have successful sync timestamps.

### Catalog totals

```text
Events:             2,119
Venues:               355
Artists:            3,132
Event identities:   2,119
Venue identities:     355
Artist identities:  3,132
Raw responses:        261
Rejections:         1,952
Sync runs retained:     3
```

Events by city:

```text
New York City: 1,960
Boston:          159
```

Events by status:

```text
active: 2,119
unverified: 0
hidden: 0
```

High `NO_ARTIST` quarantine volume is expected for listings without an announced,
ID-bearing lineup. Quarantine rollback creates no orphan canonical venue/artist
rows for the rejected event. Nightly re-fetch allows these events to self-admit once
RA publishes a lineup.

### Latest runs

```text
Run 7  nightly   completed  486 admitted  303 quarantined  0/2 seeds failed
Run 6  nightly   completed  509 admitted  309 quarantined  0/2 seeds failed
Run 5  backfill  completed 2210 admitted 1340 quarantined  0/2 seeds failed
```

All three have `error_summary = NULL`.

Remember: admitted count is observation telemetry, not “new canonical Event rows.”
Unchanged re-observations count as admitted after successful upsert.

### Backfill decision

The original 24-month ambition was deliberately reduced:

1. trailing 24 months;
2. then 2026 year-to-date;
3. finally approximately two months around launch, recent plus upcoming.

Reason: this is a resume demonstration with no real users requiring deep history.
A populated current/upcoming catalog demonstrates the same pipeline. Deeper history
remains the same backfill code path with a different runtime window.

The completed supervised backfill used:

```sh
.venv/bin/python manage.py sync_ra --backfill \
  --window-start 2026-06-01 \
  --window-end 2026-09-30 \
  --page-size 20
```

Do not run another large backfill casually. Approve the window, expected request
volume, and supervision plan first.

## Nightly operations

### Bare command

```sh
.venv/bin/python manage.py sync_ra
```

Defaults:

- run type: nightly;
- window start: current UTC date;
- window end: start plus 30 days;
- page size: 20;
- all active seeds;
- sequential paced requests.

Explicit windows override the planner:

```sh
.venv/bin/python manage.py sync_ra \
  --window-start YYYY-MM-DD \
  --window-end YYYY-MM-DD \
  --page-size 20
```

### Local LaunchAgent

Installed user plist:

```text
/Users/ilkerbaydar/Library/LaunchAgents/com.tan.danced.sync.plist
```

Label:

```text
com.tan.danced.sync
```

Verified schedule:

```text
Daily at 16:00 (4:00 PM local time)
```

Actual program:

```text
/Users/ilkerbaydar/Desktop/danced_app/.venv/bin/python
```

Arguments:

```text
/Users/ilkerbaydar/Desktop/danced_app/manage.py
sync_ra
```

Working directory:

```text
/Users/ilkerbaydar/Desktop/danced_app
```

Logs:

```text
/Users/ilkerbaydar/Desktop/danced_app/logs/sync.log
/Users/ilkerbaydar/Desktop/danced_app/logs/sync.err.log
```

Verify registration:

```sh
launchctl list | grep com.tan.danced.sync
launchctl print gui/$(id -u)/com.tan.danced.sync
```

Trigger manually:

```sh
launchctl kickstart -k gui/$(id -u)/com.tan.danced.sync
```

Read logs:

```sh
tail -100 logs/sync.log
tail -100 logs/sync.err.log
```

### Laptop dependency

The local schedule works only when:

- the Mac is powered on;
- the user is logged in;
- the machine is awake or able to execute the launchd catch-up;
- internet is available;
- MySQL is running;
- the repository and virtual environment remain at their absolute paths.

VS Code and Terminal do not need to be open.

This is acceptable for the current resume-project stage but is not production-grade
availability. The eventual industry-standard move is:

- deploy Django to an always-on platform;
- move MySQL to a persistent hosted database;
- run the scheduler on that platform;
- preserve logs, alerts, backups, and one-run-at-a-time semantics;
- then disable the local LaunchAgent to prevent duplicate syncs.

Do not deploy only the scheduler while leaving the database laptop-local. Scheduler,
application, and persistent database should share a coherent deployment boundary.

## Operator alarms

The current working tree alarms when:

- run crashes;
- any seed fails;
- admitted observations equal zero.

Alarm behavior:

- logs at ERROR;
- writes clear stderr;
- exits nonzero;
- launchd captures stderr in:

```text
/Users/ilkerbaydar/Desktop/danced_app/logs/sync.err.log
```

There is no email provider, pager, Slack webhook, or hosted monitoring service.
Therefore the operator must inspect the error log. The system does not currently
push a notification to Tan.

An empty stderr log plus a new success line in `sync.log` is the local indication
of a healthy scheduled run.

## Notable live-world findings and freeze-breaks

### Cloudflare 403

Initial live contact returned HTTP 403 with the minimal header set. A controlled curl
probe proved that a six-header public browser-style set returned 200. The client was
updated, regression-tested, and first contact then succeeded.

Do not add cookies or challenge machinery if this regresses.

### Listing wrappers are not events

Live RA returned duplicate listing wrappers for the same stable event. Completeness
must remain wrapper-grain while canonical identity and observed reconciliation remain
event-grain.

### Missing provider event IDs

An event observation can structurally fail before producing an `event.id`.
`REJECTED_INGEST` therefore uses always-known payload position as its replay key and
allows nullable `entity_ref`.

### NYC Referer with Boston

The exact production header set, including NYC Referer, returned 200 for the real
captured Boston area-530 request. No per-seed Referer is needed unless new evidence
changes this.

## Safety and invariants worth defending

1. **Raw evidence is lossless.**
   Store exact response text even when it is not JSON.
2. **Replay is idempotent.**
   Reprocessing raw history yields identical durable state.
3. **Canonical tables are source-neutral.**
   Provider identity belongs in concrete identity tables.
4. **Incomplete fetches cannot prove absence.**
   Partial data may add, never subtract.
5. **Quarantine is per observation and self-healing.**
   A future corrected listing can admit normally.
6. **Quarantine writes no partial canonical graph.**
   Per-event canonical work rolls back as a unit.
7. **Observed does not mean admitted.**
   A listed-but-quarantined event ID still resets absence misses.
8. **Recovered observations are stale for completeness.**
   Recovery sweep updates canonical state but does not vouch for tonight.
9. **Backfill and replay never reconcile absence.**
10. **The pipeline never deletes user-created history.**
11. **Event status is derived across provider identities.**
    Any source still vouching keeps the event alive.
12. **All timezone work is aware and boundary-owned.**
13. **No source-display-name matching for identity.**
14. **No title-text cancellation heuristic.**
15. **No speculative schema or services without a consuming requirement.**

## Known limitations and risks

### Quarantine baseline

Recent nightly/backfill runs consistently quarantine approximately 38% of listed
observations. Runs 5–8 were 37.7%, 37.8%, 38.4%, and 38.4%; every quarantine in
those runs was `NO_ARTIST`, not a structural or payload-shape failure. RA commonly
lists events before publishing an ID-bearing lineup. These observations retry
naturally and can self-admit on a later sync; investigate if the rate materially
changes or other rejection reasons begin contributing.

### Scheduling reliability

Local launchd depends on the laptop. If that is unacceptable, deploy the whole
application/database/scheduler boundary. Do not pretend local launchd is highly
available.

### MySQL version

Local Homebrew currently runs MySQL 9.6.0, while the architectural floor was MySQL
8.0.16+ for enforced CHECK constraints. Current behavior passes tests, but a cloud
deployment should deliberately pin a supported MySQL 8.x release rather than
casually inheriting “latest.”

### RA is unofficial

RA access is not an official public product API contract. Query shape and edge
behavior can change. The archive/replay design limits data-loss risk but cannot make
provider access guaranteed or legally authorized.

Before global/public launch, perform legal and terms review. Current use is a
private resume-project prototype.

### Monitoring

Alarm output exists, but there is no push notification or external uptime monitor.
On a laptop, failures may sit unnoticed in a file.

### Backups

There is no documented automated `mysqldump` backup schedule yet. The catalog is
rebuildable from provider data only while access remains available; raw history and
review artifacts still deserve backups.

### User-facing architecture delta

The DBML is a product blueprint. Django `AbstractUser` will add framework admin
columns when the user zone is implemented. That known delta should be logged, and
product code must not invent semantics for those administrative fields.

### Product not yet clickable

The pipeline is impressive but not recruiter-facing by itself. The highest-value
next work is a browsable catalog UI over real data.

## Commands a future conversation will need

### Orient safely

```sh
pwd
git status --short
git log -5 --oneline --decorate
.venv/bin/python manage.py showmigrations
```

### Verify code and contracts

```sh
.venv/bin/python manage.py check
.venv/bin/python manage.py test ingestion
.venv/bin/python docs/recon/fixtures/audit_expectations.py
git diff --check
```

### Inspect latest run

```sh
.venv/bin/python manage.py shell -c "
from ingestion.models import SyncRun
r = SyncRun.objects.latest('id')
print(
    r.id,
    r.status,
    r.run_type,
    r.seeds_attempted,
    r.seeds_failed,
    r.events_upserted,
    r.events_quarantined,
    r.error_summary,
)
"
```

### Inspect catalog counts

```sh
.venv/bin/python manage.py shell -c "
from catalog.models import Event, Venue, Artist
from django.db.models import Count
print('events', Event.objects.count())
print('venues', Venue.objects.count())
print('artists', Artist.objects.count())
print(list(
    Event.objects.values('venue__city__name')
    .annotate(n=Count('id'))
    .order_by('-n')
))
"
```

### Run one supervised nightly sync

```sh
.venv/bin/python manage.py sync_ra
```

### Check local scheduler

```sh
launchctl print gui/$(id -u)/com.tan.danced.sync
tail -100 logs/sync.log
tail -100 logs/sync.err.log
```

## Recommended next-session procedure

A new conversation should begin with:

1. Read this file completely.
2. Run `git status --short`.
3. Read the specific authoritative artifact relevant to the requested layer.
4. Do not assume the uncommitted alarm changes were committed; verify.
5. If continuing Milestone 2, inspect current URLs/views before designing the API.
6. Ask product questions when endpoint/UI choices are not settled.
7. Argue against proposals that violate the invariants above or add speculative
   machinery.
8. Preserve unrelated user changes in the working tree.

Suggested opening prompt:

```text
Read docs/PROJECT_STATE.md completely, then verify git status and the relevant
files before acting. Treat the frozen DBML, ERD review, architecture contract,
fixture README, and committed tests as authoritative. Do not reopen settled
ingestion design without concrete contradictory evidence. I encourage you to argue
back when you find a correctness hole. Ask before making product decisions that
the specs do not answer.

My next goal is: <insert goal>.
```

## Short project narrative for interviews

Danced’s data pipeline ingests unofficial live-event listings into a source-neutral
catalog while preserving raw evidence and isolating provider identity. The design
uses append-only request archives, replay-safe transformation, per-event
transactions, quarantine rather than destructive drops, concrete identity tables
with real foreign keys, and completeness-gated absence reconciliation.

The strongest real-world story is that supervised first contact exposed two
production assumptions:

1. Cloudflare rejected the minimal transport header set.
2. RA’s `totalResults` counted listing wrappers, not unique event IDs.

In both cases the system failed conservatively, archived the evidence, avoided
destructive reconciliation, and enabled a focused evidence-driven correction with
contract tests. The resulting pipeline populated 2,119 canonical events across NYC
and Boston and now maintains a 30-day forward window nightly.

That is the project’s core engineering claim: not merely that it fetches events, but
that it treats external data as fallible testimony and makes unsafe state
transitions difficult.
