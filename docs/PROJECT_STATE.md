# Danced — Project State and Conversation Handoff

> Last verified: 2026-07-31 (America/New_York)
>
> Repository: `/Users/ilkerbaydar/Desktop/danced_app`
>
> Branch: `main`
>
> Verified implementation state: Phase C Slice 4A complete through frontend,
> including the post-slice social-state synchronization fix.
>
> Remote state: `origin/main` is at `819da58`; the working tree was clean when Slice
> 4B began.
>
> Purpose: provide a self-contained, evidence-based handoff for the current
> ingestion, catalog, identity, Been, rating, and review implementation.

## Status of this document

This file is updated in place and is the sole current project-state document. Every
future orientation must read `docs/PROJECT_STATE.md`; do not create numbered
successors. The superseded Milestone 1 handoff is retained only as historical evidence
at `docs/archive/PROJECT_STATE_MILESTONE_1_2026-07-30.md`.

This file does not supersede the frozen product and architecture contracts. It
summarizes their current implementation. When this file conflicts with an
authoritative contract, investigate rather than silently choosing whichever text is
more convenient.

## Read this first

Danced is a Letterboxd-style social diary for live music. It is intended to let
people discover events, record events they attended, rate them, write reviews,
follow other users, and eventually browse social activity around live music.

The project now has three working vertical foundations:

1. A conservative, replayable Resident Advisor ingestion pipeline.
2. A public read-only catalog API and unstyled React browsing shell.
3. Session-based identity and user content: Been entries, ratings, written reviews,
   and public review likes.

This is no longer merely a data-pipeline project. A founder can:

- browse real New York City and Boston catalog data;
- navigate event, venue, and artist pages;
- register and choose a public/private account;
- log in and out;
- see whether an event is currently loggable;
- add a past event to Been with a mandatory rating;
- edit or remove that rating;
- remove the Been entry;
- view their own diary;
- see global rating availability and averages on event pages;
- write, edit, and delete a review attached to a rated Been entry;
- browse public reviews and like or unlike another user's review.

On 2026-07-31, the founder completed the first real product click-through:

- registered the persistent account `tan`;
- confirmed a future event is not loggable;
- confirmed an event happening tonight remains unavailable before its scheduled
  venue-local start;
- navigated through a venue's Past section;
- rated `Martin Garrix Afterparty` 2.0 stars;
- confirmed the entry renders on `/been`.

That account and diary entry are intentional real development data and must not be
deleted as test cleanup.

## Workflow rule

The central implementation rule remains:

> Do not silently redesign settled behavior while implementing it.

Treat the DBML, ERD review, product questions, architecture contract, frozen fixture
README, committed migrations, and committed tests as contracts. If implementation
reveals a contradiction:

1. stop the affected design branch;
2. identify the exact conflicting rulings;
3. report the correctness hole;
4. propose the smallest evidence-based resolution;
5. wait for product approval when the specification does not answer the question;
6. record any approved freeze-break or amendment;
7. cover it with focused tests.

Do not reopen settled ingestion behavior without concrete contradictory evidence.
Do not make product decisions merely because a framework default is convenient.

## Current milestone position

### Milestone 1 — ingestion and catalog foundation

Complete for the current local prototype:

- source reconnaissance and captured request fixtures;
- append-only raw request evidence;
- per-observation admission/quarantine;
- source-neutral canonical catalog;
- source identity firewall;
- replay-safe upserts;
- completeness-gated absence reconciliation;
- resurrection;
- bounded, paced acquisition;
- local nightly scheduling and alarms;
- live NYC and Boston data.

### Milestone 2 / Phase A — read-only catalog API

Complete:

- cities endpoint;
- scoped upcoming and past event lists;
- venue, artist, and event detail;
- visibility rules;
- per-event venue-local date boundaries;
- deterministic pagination;
- contract tests.

### Phase B — guest frontend shell

Complete and deliberately unstyled:

- Vite + React in plain JavaScript;
- Discover city browsing;
- event detail;
- venue detail with independent Upcoming and Past sections;
- artist detail with independent Upcoming and Past sections;
- semantic loading, error, retry, empty, and not-found states;
- Resident Advisor footer attribution;
- shared venue-local datetime formatting;
- contextual suppression of redundant list metadata.

### Phase C slice 1 — identity

Complete with an explicit temporary verification deferral:

- custom Django user;
- registration;
- mandatory public/private choice;
- email/password login;
- logout;
- current-session bootstrap;
- CSRF-protected same-origin session authentication;
- signed-in navigation.

### Phase C slice 2 — Been and ratings

Complete:

- one diary entry per user/event;
- mandatory rating on first creation;
- nullable rating after creation;
- start-time logging gate;
- rating edit;
- rating removal while retaining attendance;
- entry deletion;
- owner-only diary;
- anonymous global aggregates;
- hidden-event suppression and resurrection;
- first real founder entry.

### Phase C slice 2.5 — recent-event navigation

Complete:

- Discover includes city-scoped Recent events below Upcoming;
- the section reuses the existing past-event endpoint and shared event list;
- Upcoming and Recent paginate independently;
- the list is explicitly an interim recency stand-in, not popularity ranking.

### Phase C slice 3 — written reviews and likes

Complete:

- one review per rated Been entry;
- post-trim 1–1,000-character body contract;
- immutable original publication time and silent edits;
- review-only deletion preserving rating and attendance;
- rating/entry deletion cascades through review likes;
- public-account reviews visible to guests;
- private-account reviews visible only to their owner until follows widen access;
- stored review likes with no liker-identity surface;
- Public review ordering by likes, follower count, publication time, and stable ID;
- Public review ordering uses real approved-follower counts;
- standing public browser-test account `review.public.test`, documented in Operations.

### Phase C slice 4A — follows, notifications, Activity, and Your Circle

Complete and pushed:

- FOLLOW and NOTIFICATION models, constraints, and physical cascades;
- public follows and private requests with accept/decline/withdraw/unfollow;
- serialized privacy transitions with pending-request bulk acceptance;
- stored historical review-like/follow/request/acceptance notifications;
- cursor-paginated Activity with read and mark-all-read actions;
- public/private attributed visibility widening through sanctioned boundaries;
- separately owned Circle-list and Circle-average query methods;
- event-page Your Circle list and one-rating-threshold average;
- real approved-follower counts in Q195 Public review ordering;
- temporary follow controls on public-review bylines;
- Q205 privacy API without speculative Settings UI;
- real two-connection concurrency coverage for privacy transition versus follow.

### Not implemented

The following remain design-only or deferred:

- email verification delivery and gating;
- password reset;
- email change verification;
- public user profiles;
- favorites;
- onboarding flow;
- rating-distribution display;
- Will Be There;
- feeds;
- reports and moderation UI;
- account settings and privacy switching UI;
- deletion/deactivation workflow;
- search;
- Home, Profile, and Settings product destinations;
- styling and responsive visual design;
- production deployment;
- cloud database/scheduler;
- frontend automated test harness.

Do not migrate all remaining DBML application tables preemptively. Each slice should
introduce only the tables it consumes.

## Sources of truth and authority

Read current artifacts in this order:

1. `docs/PRODUCT_QA_SPEC.md`
   - 210 product decisions plus appended amendments.
2. `docs/danced.dbml`
   - Frozen full database blueprint.
3. `docs/ERD_REVIEW.md`
   - Reviewed deltas, freeze-breaks, and physical-database notes.
4. `docs/danced-data-architecture.md`
   - Ingestion boundaries and invariants.
5. `docs/recon/fixtures/README.md`
   - Frozen fixture contract and Transformer rules.
6. Committed tests
   - Executable contracts for implemented behavior.
7. Committed migrations
   - Immutable history of the physical schema.
8. `docs/RA_SOURCE_RECON.md`
   - Source evidence and captured request behavior.
9. `docs/OPERATIONS.md`
   - Current local operations and browser-equivalent CSRF verification guidance.
10. `docs/NAVIGATION.md`
   - Binding destination order, landing rules, and interim absorbers.
11. This file
    - Current implementation and runtime handoff.
12. `docs/archive/`
    - Superseded history only.

If tests and prose appear to disagree, inspect Git history and the amendment record.
Do not automatically assume either side is correct.

## Technology and repository shape

### Backend

- Python 3.14 local runtime
- Django 6.0.7
- MySQL through `mysqlclient` 2.2.8
- `python-dotenv` 1.1.1
- Plain Django JSON views
- Django session authentication
- Django CSRF middleware
- No Django REST Framework
- No GraphQL server
- No Celery or worker queue

### Frontend

- Vite 8.2
- React 19.2
- React DOM 19.2
- React Router DOM 6.30
- Plain JavaScript and JSX
- Plain `fetch`
- No TypeScript
- No state-management library
- No component library
- No CSS files, inline styles, `className`, or CSS framework

### Django apps

- `catalog`
  - canonical event catalog;
  - public read APIs.
- `ingestion`
  - acquisition, archival, transformation, quarantine, reconciliation, runner,
    and command.
- `users`
  - custom user, authentication, diary/rating services, and APIs.
- `config`
  - settings, source enum, URL wiring.

### Important frontend files

- `frontend/src/App.jsx`
  - routes, session bootstrap, global navigation, logout, footer.
- `frontend/src/api.js`
  - small JSON/CSRF fetch helper.
- `frontend/src/components/EventList.jsx`
  - shared scoped event-list and pagination UI.
- `frontend/src/formatEventDateTime.js`
  - timezone-neutral display formatting for already-local catalog values.
- `frontend/src/pages/DiscoverPage.jsx`
- `frontend/src/pages/EventPage.jsx`
- `frontend/src/pages/VenuePage.jsx`
- `frontend/src/pages/ArtistPage.jsx`
- `frontend/src/pages/RegisterPage.jsx`
- `frontend/src/pages/LoginPage.jsx`
- `frontend/src/pages/BeenPage.jsx`
- `frontend/src/pages/ActivityPage.jsx`
- `frontend/src/components/PublicReviews.jsx`
- `frontend/src/components/YourCircle.jsx`

## Git state and important commits

The verified current local checkpoint contains:

```text
feat: add follow graph, notifications, and Your Circle API (local)
docs: consolidate project state into one canonical handoff (local)
docs: record follow approval lifecycle and interim surfaces (local)
20eb0ba feat: add review publishing and public review interactions (pushed)
d3b05c3 feat: add written reviews, privacy boundaries, and review likes (pushed)
aab5b6b feat: add city-scoped recent events to Discover (pushed)
fb47ba7 docs: freeze five-destination navigation contract (pushed)
```

Recent vertical-slice history:

```text
c841c80 fix: trust documented Vite origins in local development
47f09a0 fix: render registration failures by error class
b150fc8 feat: add zero-style Been diary and rating controls
e5986ac feat: add Been diary, ratings, and private aggregation boundary
6d529ec feat: add zero-style registration and login frontend
9f2360f feat: add custom user and session auth API
989676e feat: refine guest catalog content before styling
059b24e feat: add unstyled guest catalog frontend
391613f feat: add canonical cities API
0a4e40b feat: add past catalog filters and entity detail endpoints
6d45262 feat: read-only upcoming-events API
cdf95dd ops: add nightly health alarms and project handoff
```

The state-consolidation commit that updates this section is intentionally separate
from the amendments commit.

## Implemented database

All listed migrations were applied to the real local database at the last
verification.

### Catalog zone

#### `CITY`

Fields:

- canonical ID;
- name;
- region code and name;
- country code;
- IANA timezone.

Uniqueness is country + region + name.

Current cities:

| ID | City | Region | Country | Timezone |
|---:|---|---|---|---|
| 2 | Boston | MA | US | America/New_York |
| 1 | New York City | NY | US | America/New_York |

#### `VENUE`

- name;
- required canonical city;
- restrictive city deletion.

A venue always implies exactly one city. This supports suppressing both venue and
city lines inside a venue-scoped event list.

#### `ARTIST`

- name;
- optional image URL.

#### `EVENT`

- title;
- venue-local `event_date`;
- optional venue-local `start_time`;
- required venue;
- optional cover image;
- derived lifecycle status.

Actual lifecycle values:

- `active`
- `unverified`
- `hidden`

Public visibility is `ACTIVE` plus `UNVERIFIED`. `HIDDEN` is excluded. There is no
`status="cancelled"` or `status="active"`-only public rule. Public responses do not
expose lifecycle vocabulary.

#### `EVENT_ARTIST`

- event;
- artist;
- stable lineup position;
- unique event/artist;
- unique event/position.

The pipeline never infers lineup members from event titles. A source title can name
an artist absent from the structured lineup; the structured source relationship wins.

#### Identity tables

Concrete identity tables isolate provider IDs:

- `CITY_IDENTITY`
- `VENUE_IDENTITY`
- `ARTIST_IDENTITY`
- `EVENT_IDENTITY`

Canonical tables remain source-neutral. Current source enum value is `ra`.

`EVENT_IDENTITY` additionally owns:

- `last_seen_at`;
- absence `misses`.

Canonical event status is derived across all identities rather than treated as
independent source truth.

### Ingestion zone

#### `TRACKED_SOURCE_PAGE`

Defines the bounded acquisition seeds:

- source;
- provider area reference;
- human label;
- active flag;
- last sync and success times.

Current active seeds:

- RA area `8`: New York City
- RA area `530`: Boston

#### `SYNC_RUN`

Tracks:

- nightly, backfill, or replay run type;
- running, completed, or crashed status;
- start/end time;
- attempted/failed seeds;
- admitted/upserted observations;
- quarantines;
- drops;
- diagnostic summary.

#### `RAW_INGEST`

Archives every page-level acquisition result:

- seed and run;
- requested window;
- page number and size;
- exact response body text;
- HTTP status;
- fetched time;
- pending/processed/failed processing status.

Response text is preserved even when it is not valid JSON.

#### `REJECTED_INGEST`

Stores one rejected observation:

- raw page;
- zero-based listing position;
- nullable provider event reference;
- rejection reason;
- diagnostic detail;
- rejection time.

Replay uniqueness is raw page + listing position. Provider event ID is nullable
because a structural failure may occur before a usable nested ID exists.

### User zone

#### `DANCED_USER`

Custom user extends `AbstractUser`.

Product fields implemented from the DBML:

- unique lowercase email;
- nullable email-verification timestamp;
- lifecycle-nullable lowercase username;
- recovery username;
- display name;
- optional bio;
- optional avatar URL;
- optional home city;
- required `is_private`;
- account status;
- optional deletion due time;
- creation time.

Framework administrative columns inherited from `AbstractUser` are documented ORM
deltas. Product code must not invent product semantics for them.

Username lifecycle nullability is not registration optionality. Registration always
requires a username. Null is reserved for later deactivation/deletion semantics.

Current user status values:

- `active`
- `deactivated`
- `pending_deletion`

Database checks link username nullability and deletion date to lifecycle status.

#### `DIARY_ENTRY`

Implemented fields:

- user;
- event;
- nullable rating;
- nullable `rated_at`;
- `created_at`.

Constraints:

- one entry per user/event;
- rating and `rated_at` are null together or non-null together;
- rating is null or a half-star value from 0.5 through 5.0.

Physical deletion rules:

- user deletion cascades diary entries;
- event deletion is restrictive.

#### `REVIEW`

- one-to-one with `DIARY_ENTRY`;
- trimmed non-empty body, maximum 1,000 stored characters;
- immutable `published_at` and deliberately no edit timestamp;
- database and ORM cascade from entry deletion;
- owner/public visibility passes through `Review.visible_to(viewer)`;
- Public event sections use the separate `for_public_section()` boundary.

#### `REVIEW_LIKE`

- composite primary key `(user_id, review_id)`;
- one like per user/review;
- self-like rejected transactionally;
- physical database cascades from both user and review;
- counts include private likers but never expose liker identity.

#### `FOLLOW`

- composite primary key `(follower_id, followee_id)`;
- status `pending|approved`;
- immutable initiation `created_at`;
- nullable `approved_at`, with `status = approved` iff non-null;
- self-follow database check;
- public follows approve immediately; private follows remain pending;
- follow creation and privacy transition serialize on the target user row.

#### `NOTIFICATION`

- stored historical action records, not derived feed projections;
- types: review like, follow, follow request, request accepted;
- nullable `review_id` exactly for review-like notifications;
- nullable `read_at` defines unread state;
- actor cannot equal recipient;
- unlike and unfollow do not retract history; review deletion cascades linked likes.

Django's generated MySQL foreign key did not physically emit the DBML-required user
cascade. The solution was deliberately split:

- `users.0003` creates `DIARY_ENTRY`;
- `users.0004` replaces the user foreign key with physical `ON DELETE CASCADE`.

Accepting an ORM-only cascade was rejected because the frozen contract requires the
database itself to preserve the rule.

## Migration history

### Catalog

```text
0001_initial
0002_seed_v1_cities
0003_enforce_database_cascades
0004_cityidentity
0005_seed_city_identities_and_enforce_cascade
```

### Ingestion

```text
0001_initial
0002_rawingest_ck_raw_processing_status_and_more
0003_remove_rejectedingest_uq_rejection_payload_entity_and_more
```

### Users

```text
0001_initial
0002_remove_legacy_auth_user_metadata
0003_diaryentry
0004_enforce_diary_user_cascade
0005_review_reviewlike_review_ck_review_body_nonblank
0006_enforce_review_database_cascades
0007_follow_notification
0008_enforce_social_database_cascades
```

### Custom-user migration surgery

The local database had already applied Django admin/auth migrations before the
custom user model existed. The legacy `auth_user` and its join tables were empty, but
changing `AUTH_USER_MODEL` after migration required remediation.

The rejected fallback was resetting the entire database. That would have destroyed
the raw archive that supposedly made the catalog rebuildable, invalidating its own
safety rationale.

The adopted sequence was:

1. create and verify a full `mysqldump`;
2. retain it outside the repository at
   `/Users/ilkerbaydar/danced-backups/danced_pre_users_20260731.sql`;
3. unapply admin migrations;
4. remove only the three verified-empty legacy user tables;
5. install `users.0001` as the swappable user root;
6. remove stale `auth.user` content-type metadata idempotently;
7. reapply admin;
8. validate the graph on the real database and through the full test runner's fresh
   database.

Catalog, ingestion, and raw evidence were preserved.

## Live database snapshot

Snapshot taken 2026-07-31 after the founder click-through:

| Entity | Count |
|---|---:|
| Cities | 2 |
| Venues | 355 |
| Artists | 3,132 |
| Events | 2,119 |
| Event identities | 2,119 |
| Users | 1 |
| Diary entries | 1 |
| Sync runs | 4 |
| Raw ingest pages | 301 |
| Rejected observations | 2,255 |
| Tracked seeds | 2 |

Event statuses at the snapshot:

| Status | Count |
|---|---:|
| active | 2,119 |
| unverified | 0 |
| hidden | 0 |

Persistent founder data:

- user ID 2;
- username `tan`;
- display name `Tan`;
- private account;
- active;
- email verification still null under the approved temporary deferral.

Persistent diary data:

- entry ID 1;
- event ID 2174;
- event `Martin Garrix Afterparty`;
- historical event date 2026-06-19;
- rating 2.0;
- rated and created 2026-07-31.

Do not expose the founder's email in handoff documents or other-user serializers.

## Ingestion runtime

### Acquisition client

`ingestion/client.py` owns transport only.

- Endpoint: RA GraphQL.
- Request shape comes from captured evidence.
- Fixed public browser-style headers:
  - Content-Type
  - Accept
  - Chrome User-Agent
  - Origin
  - NYC Referer
  - Accept-Language
- No cookies, account, session, CAPTCHA solving, or challenge machinery.
- Pages are sequential.
- Inter-page delay is 1.5 seconds after the first page.
- Maximum three attempts per page.
- Retryable failures:
  - connection/timeout;
  - 408;
  - 429, honoring `Retry-After`;
  - 500, 502, 503, 504.
- Shared run ceiling: 1,000 request attempts.

The Chrome User-Agent is browser impersonation. Its use is bounded by captured
evidence and public unauthenticated access; do not euphemize it as honest client
identification.

If RA begins requiring genuine interactive challenge completion, stop. Do not begin
an anti-bot escalation loop.

### Raw archival

Every fetch attempt outcome is archived before domain admission. Transport failure,
HTTP error, malformed JSON, and valid responses all remain inspectable evidence.

### Transformer

`ingestion/transformer.py` processes one raw page and owns RA event shape.

Admission precedence:

1. structural parsing and usable nested `event.id`;
2. scope check;
3. seed-driven city and venue resolution;
4. at least one ID-bearing artist;
5. non-empty title and parseable date;
6. canonical upsert.

Canonical work occurs inside a per-event transaction. A rejected observation leaves
no partial venue, artist, event, lineup, or identity graph. The rejection is written
after rollback.

The closed event-field set is:

- provider event ID;
- title;
- date;
- start time;
- venue ID/name;
- artist IDs/names;
- flyer/image.

Ticket state, wrapper IDs, prose tags, and unknown fields do not steer admission or
lifecycle.

Cancellation text is not parsed. Captured RA evidence did not provide a reliable
structured cancellation signal, so titles are preserved verbatim and absence
reconciliation owns visibility.

City comes from:

```text
raw seed
  -> (source, area_ref)
  -> CITY_IDENTITY
  -> CITY
```

Do not infer city from venue names, event titles, Referer, or fields absent from the
captured listing request.

### Completeness

RA `totalResults` counts listing wrappers, not unique events.

Completeness requires:

1. archived wrapper count equals `totalResults`;
2. every wrapper has a usable nested event ID.

Use:

- wrapper grain for completeness;
- unique event-ID grain for reconciliation and canonical identity.

Do not compare unique event count to `totalResults`.

### Reconciliation

`ingestion/reconciler.py`:

- runs only for complete nightly seed windows;
- never reconciles backfill or replay;
- only considers future events in the covered window;
- resets misses for observed IDs, including listed-but-quarantined observations;
- increments misses for absent IDs;
- derives event status across all provider identities;
- resurrects when an event reappears;
- never deletes canonical events or user history.

Absence ladder:

- zero misses across identities: active;
- at least one miss across all identities: unverified;
- at least three misses across all identities: hidden.

Incomplete fetches may add admitted knowledge but cannot supply absence evidence.

### Runner

`ingestion/runner.py`:

- acquires MySQL advisory lock `danced_sync_ra`;
- refuses overlapping runs;
- resolves each seed through `CITY_IDENTITY` before fetch;
- archives each page;
- transforms current and previously pending raw rows;
- excludes recovered stale rows from tonight's completeness evidence;
- records run telemetry;
- releases the lock on success and failure;
- marks crashed runs.

### Command and alarm

Bare nightly command:

```sh
.venv/bin/python manage.py sync_ra
```

Default nightly window:

- current UTC date;
- 30 days forward;
- page size 20;
- all active seeds.

The command exits nonzero and logs clearly when:

- the run crashes;
- any seed fails;
- admitted/upserted observations equal zero.

It does not alarm merely because quarantines are nonzero.

## Latest ingestion evidence

Latest verified run:

```text
run ID: 8
type: nightly
status: completed
started: 2026-07-31 04:26:18 UTC
finished: 2026-07-31 04:27:35 UTC
seeds attempted: 2
seeds failed: 0
events upserted: 486
events quarantined: 303
events dropped: 0
error summary: none
```

Runs 7 and 8 both produced 486 admitted/upserted and 303 quarantined observations.
Run 6 produced 509 and 309. The approximately 38% quarantine rate is currently a
stable baseline, not a run-8 spike. In runs 5–8, quarantines were `NO_ARTIST`: RA
commonly lists an event before publishing an ID-bearing lineup. These observations
self-retry on later syncs.

Investigate if:

- the percentage materially changes;
- structural `PARSE_FAILURE`, `BAD_DATE`, or another rejection begins contributing;
- admitted events unexpectedly reach zero;
- a seed fails;
- wrapper completeness fails.

## Catalog API

All catalog reads remain public.

### `GET /api/cities/`

Returns canonical cities ordered by name:

- `id`
- `name`
- `region_code`
- `country_code`
- `timezone`

### `GET /api/events/`

Required:

- `when=upcoming|past`
- exactly one of:
  - `city_id`
  - `venue_id`
  - `artist_id`

Optional:

- `page`, default 1;
- `page_size`, default 20, maximum 100.

Errors:

- zero or multiple scope filters: 400;
- invalid `when`: 400;
- invalid pagination/scope number: 400;
- unknown scope resource: 404;
- page beyond the last page: 404.

Upcoming:

- event date greater than or equal to venue-local today;
- ordered `event_date ASC, id ASC`.

Past:

- event date less than venue-local today;
- ordered `event_date DESC, id DESC`.

Artist scope may cross cities and timezones. Each event is classified using its own
venue city's local date. Filtering occurs in the database so counts and page
boundaries remain truthful.

List event payload:

- event ID;
- title;
- local date;
- nullable local start time;
- nullable cover image;
- nested venue;
- short nested city with timezone;
- ordered artist lineup.

Internal lifecycle status is intentionally not returned.

### `GET /api/venues/{id}/`

Returns:

- venue ID/name;
- full city object:
  - ID/name;
  - region code/name;
  - country;
  - timezone.

It does not embed events. Upcoming and Past sections use the shared event endpoint.
A venue remains retrievable with zero visible events.

### `GET /api/artists/{id}/`

Returns:

- artist ID/name;
- nullable image URL.

It does not embed events. An artist remains retrievable with zero visible events.

### `GET /api/events/{id}/`

Hidden events return 404.

Returns the common event shape plus:

- `rating_summary`;
- `been.loggable`;
- `been.unavailable_reason`;
- authenticated-only `viewer_entry`.

Guests do not receive a `viewer_entry` key. A signed-in user with no entry receives
`viewer_entry: null`.

Rating summary below threshold:

```json
{
  "state": "not_enough_ratings",
  "count": 2
}
```

At three current ratings:

```json
{
  "state": "available",
  "count": 3,
  "average": 4.166666666666667
}
```

The API returns the arithmetic value. Display rounds to one decimal.

## Authentication API

All mutations use Django session authentication and CSRF. There are no JWT or token
endpoints.

### `GET /api/auth/session/`

- bootstraps the CSRF cookie;
- reports guest or authenticated session;
- returns the authenticated user's own email.

Email is self-only account data. Never copy this serializer into public profiles,
reviews, or feeds.

### `POST /api/auth/register/`

Requires:

- email;
- password;
- username;
- display name;
- strict JSON boolean `is_private`.

Successful registration currently creates an active account and signs it in
immediately.

Username:

- 3–30 characters;
- letters, numbers, underscores, periods;
- begins and ends with letter/number;
- no consecutive periods;
- stored and displayed lowercase;
- case-insensitive uniqueness.

Display name:

- trimmed;
- 1–50 visible characters.

Email uniqueness is case-insensitive.

### `POST /api/auth/login/`

- accepts email + password;
- uses one generic invalid-credentials response to avoid email enumeration;
- establishes a session.

### `POST /api/auth/logout/`

- invalidates the session;
- idempotent;
- returns 204.

### Email-verification freeze-break

Q125–126 require verification before account actions. It is deliberately deferred,
not cancelled.

Current temporary behavior:

- account created active;
- registration signs in immediately;
- `email_verified_at` exists but gates nothing.

Before public deployment, a repayment slice must:

- deliver verification;
- stop immediate usable sign-in after registration;
- direct the user to check email;
- gate account actions until verification.

## Been and rating API

All writes require authenticated session + CSRF.

### `PUT /api/events/{id}/been/`

Upsert with:

```json
{"rating": 4.5}
```

- creation: 201;
- edit or re-rate: 200;
- invalid rating: field-keyed 400;
- event not started on creation: 409;
- guest with valid CSRF: 401;
- missing/malformed CSRF can be rejected by middleware as 403;
- hidden/unknown event: 404.

Creation requires a rating. Existing entries may become unrated.

### `DELETE /api/events/{id}/been/rating/`

- removes rating and `rated_at`;
- retains attendance;
- idempotent while the entry exists;
- 404 when no entry exists.

### `DELETE /api/events/{id}/been/`

- permanently deletes entry and rating;
- returns 204;
- repeated deletion returns 404;
- the event may be re-added later as a fresh entry.

### `GET /api/me/been/`

- authenticated owner only;
- paginated;
- ordered `event_date DESC, event_id DESC`;
- retroactive old entries appear at their historical position, not at the top.

## Logging-time boundary

An event becomes loggable at:

```text
event_date + start_time in the venue city's timezone
```

If start time is null, the boundary is 00:00 venue-local.

The gate applies only to first creation. An existing entry's rating may be edited
later without rechecking the creation boundary.

DST ruling:

- ambiguous fall-back wall time opens at the first occurrence;
- nonexistent spring-forward wall time opens immediately after the clock jump.

The service owns a patchable clock dependency. Do not globally patch
`django.utils.timezone.now` in tests: doing so previously moved Django's session
clock forward and silently expired authenticated test sessions.

This service-owned seam should be reused for future time-gated product behavior,
including Will Be There expiry.

## Diary privacy architecture

There are two explicit read boundaries.

### `visible_to(viewer)`

The only sanctioned attributed-entry path.

Current behavior:

- owner sees their own entries;
- guests see none;
- other users see none because profiles/circles do not exist yet;
- hidden-event entries are suppressed;
- resurrection restores them.

### `for_aggregation()`

The anonymous aggregate path:

- includes public and private users;
- excludes unrated entries;
- excludes hidden-event entries;
- resurrection restores their contribution.

No view should reproduce these filters inline.

Private ratings contributing to an average must never imply attributed visibility.

## Frontend behavior

### Global structure

- semantic HTML only;
- browser-default presentation;
- header and primary navigation;
- route content;
- footer on every route;
- footer attribution links to `https://ra.co`;
- no per-event RA/source URL.

### Discover `/`

- city list comes from `/api/cities/`;
- city selection lives in `?city_id=`;
- invalid, missing, or unknown city ID falls back to the first city;
- city switch does not persist to account state;
- upcoming list is independently paginated;
- event items suppress redundant city.

### Event `/events/{id}`

- event facts, venue, city, artists;
- cover image only when present;
- no placeholder imagery;
- rating availability or one-decimal global average;
- signed-in Been form;
- not-yet-started explanation;
- confirmation for rating removal;
- confirmation for entry removal;
- 404 page rather than crash.
- owner review create/edit/delete controls when the Been entry remains rated;
- Public reviews with Most liked/Newest ordering, independent pagination, and likes;
- guests may read public reviews and receive an account-required message on like.

### Venue `/venues/{id}`

- full venue/city detail;
- separately fetched/paginated Upcoming and Past sections;
- both venue and city suppressed inside scoped list items.

### Artist `/artists/{id}`

- artist fields;
- separately fetched/paginated Upcoming and Past;
- current artist omitted from each event's artist line;
- other billed artists retained;
- venue and city retained.

### Been `/been`

- guest sign-in prompt;
- authenticated owner diary;
- loading, error/retry, and empty states;
- pagination;
- rated and unrated entries;
- shared formatted dates.
- review-presence indicator.

### Activity `/activity`

- signed-in destination only;
- stored notifications ordered newest-first with cursor-based load-more;
- unread/read text, per-item mark-read, and mark-all-read;
- review-like activity opens the existing event page after marking read;
- follow/request/acceptance items remain plain text until Profile exists;
- no accept/decline controls yet because private-user discovery is deferred.

### Event-page social sections

- guests see the Q199 sign-in prompt instead of making a Circle request;
- signed-in viewers fetch independently paginated Your Circle data;
- Circle list excludes self and contains followed rating-only and reviewed entries;
- Circle average includes the viewer's own current rating and appears at one rating;
- Public review bylines expose follow/unfollow only to signed-in non-self viewers;
- author names remain plain text until `/u/{username}` exists.
- Circle and Public are sibling projections of the same review/follow state. A
  successful mutation invalidates and refetches both projections; a 404/409 mutation
  conflict is treated as state drift and also refetches both without a dead-end error.
- These live social refetches bypass the browser cache. DELETE endpoints return a
  genuinely bodyless HTTP 204 so the Vite proxy and browser can complete the request.

### Date formatting

Display form:

```text
Friday, August 14, 2026 at 10:00 PM
```

Null time:

```text
Friday, August 14, 2026
```

The API's date/time values are already venue-local. The helper parses date parts
directly and uses UTC calendar math only to derive weekday. It never sends the raw
date through browser-local timezone conversion.

### Registration errors

The frontend distinguishes:

- field-keyed 400 validation beside the matching field;
- request-level 400 once above the form;
- 403 secure-submission failure;
- other HTTP/server failure;
- network failure.

The previous template duplicated a generic message as both heading and bullet. That
block was removed. Invalid controls use `aria-invalid` and `aria-describedby`.

## Local CSRF and Vite

Development uses:

```text
frontend origin -> Vite :5173 -> /api proxy -> Django :8000
```

Under `DEBUG` only, Django trusts exactly:

```text
http://127.0.0.1:5173
http://localhost:5173
```

There are no wildcards, `csrf_exempt`, disabled origin checks, or production trust
entries. A deployed same-origin frontend must not need this development exception.

### Critical testing lesson

Browser-equivalent verification of POST/PUT/DELETE must include an `Origin` header.

An earlier scripted check sent the cookie and matching `X-CSRFToken` but omitted
`Origin`. It passed while every real browser registration failed with:

```text
Origin checking failed - http://127.0.0.1:5173 does not match any trusted origins.
```

After the narrow setting fix, the verified chain was:

1. Origin-bearing session GET: 200 and CSRF cookie.
2. Origin-bearing registration POST: 201.
3. Session and CSRF cookies rotated on login.
4. Named throwaway account deleted and absence confirmed.
5. Founder browser registration subsequently succeeded.

Never call an unsafe-method check end-to-end if it omits browser security headers.

## Test contract

Current backend suite:

```text
138 tests
```

Major groups:

- ingestion transport pacing and retry budget;
- wrapper-grain completeness;
- transformation fixtures;
- idempotency and lineup reorder;
- reconciliation ladder and resurrection;
- runner crash/lock/recovery/telemetry;
- operator alarm;
- catalog database constraints;
- city/event/detail API;
- per-event timezone classification;
- identity registration/login/logout/session;
- username/display/email/privacy validation;
- Been lifecycle, timing, privacy, aggregates, and database checks.
- review lifecycle, privacy, ordering, likes, cascades, and hidden-event resurrection.
- follow lifecycle, privacy-transition concurrency, notifications, Circle asymmetry,
  follower-count ordering, and widened-boundary surface scoping.

Important test-first lessons retained:

- A 404 test can falsely pass while a route is missing. Mutation-check the
  production branch when expected missing-route behavior matches the assertion.
- A behavior already implemented can make a newly written test green. Mutate the
  relevant branch to prove the test detects the intended contract.
- Expectation edits during green are high-risk and must be reported explicitly.
- Global clock patches can alter unrelated framework behavior.
- Browser verification must include Origin.

Mutation checks already performed for Been:

- remove hidden filtering from aggregation: hidden/resurrection test fails;
- sort by entry creation: retroactive-history test fails;
- expose average at two ratings: threshold test fails.

There is still no frontend unit/component test harness. The registration
error-classification regression is the evidence-based first candidate when such a
harness is introduced.

## Verification baseline

At the last implementation verification:

- full Django suite: 138 green;
- Django system checks: clean;
- test runner built and destroyed a fresh database successfully;
- fixture audit: clean across 13 JSON fixtures;
- frontend production build: passed, 31 transformed modules;
- `makemigrations --check --dry-run`: no changes;
- `git diff --check`: clean;
- real MySQL diary constraints inspected;
- migrations applied;
- founder click-through complete.

## Nightly operations

Local LaunchAgent:

```text
/Users/ilkerbaydar/Library/LaunchAgents/com.tan.danced.sync.plist
```

Label:

```text
com.tan.danced.sync
```

Schedule:

```text
daily at 16:00 local time
```

Program:

```text
/Users/ilkerbaydar/Desktop/danced_app/.venv/bin/python
```

Working directory:

```text
/Users/ilkerbaydar/Desktop/danced_app
```

Logs:

```text
logs/sync.log
logs/sync.err.log
```

The job depends on:

- laptop powered on;
- user environment available;
- MySQL running;
- network available;
- repository and virtualenv remaining at fixed paths.

This is acceptable for a local prototype, not production availability.

## Known limitations and risks

### Email verification

Deferred despite the frozen requirement. This must be repaid before public
deployment or broader account actions.

### Frontend is intentionally unstyled

The semantic structure is deliberate. Styling was postponed because Phase C changes
navigation and page content. Do not add speculative wrappers merely for future CSS.

### No frontend automated tests

The production build catches syntax/bundle failures, not interaction regressions.
Registration error classification is the first justified test target.

### Privacy architecture is widened but has no Profile consumer yet

`DiaryEntry.visible_to` and `Review.visible_to` now express owner, public-account,
and approved-follower visibility. Public, aggregate, Circle-list, and Circle-average
rules remain separate sanctioned methods. Owner endpoints add explicit owner scope;
the widened boundary must never be mistaken for ownership again.

### Rating threshold but no distribution

Event detail exposes average and count only after three current ratings. The product
spec's distribution UI is not implemented.

### Private Follow/Profile reachability

Private users remain undiscoverable through the frontend because Search and Profile
do not exist. The private request state machine is API-complete while the temporary
public-review byline exposes only public follow/unfollow controls.

### Local scheduling and monitoring

There is no hosted uptime monitor, pager, or push alarm. A failure can sit in
`logs/sync.err.log`.

### Backups

A pre-custom-user-surgery snapshot exists outside the repository, but there is no
automated backup schedule. Raw evidence, user history, and reviews will require
durable backups.

### RA access

RA is an unofficial source dependency. Query shape and edge behavior may change.
Archive/replay reduces data-loss risk but cannot guarantee access or authorization.
Perform legal/terms review before public launch.

### MySQL version

Local Homebrew MySQL is newer than the originally documented 8.0.16+ floor. A hosted
deployment should deliberately pin a supported MySQL 8.x release and rerun physical
constraint verification.

### Local dev-server hygiene

Duplicate Vite servers previously occupied 5173 and 5174 simultaneously. Before
diagnosing proxy behavior, inspect listeners and run one frontend server.

## Invariants to defend

1. Raw source evidence is preserved.
2. Replay is idempotent.
3. Canonical data is source-neutral.
4. Provider identity lives in identity tables.
5. Incomplete fetches may add but cannot prove absence.
6. Quarantine is per observation and leaves no partial graph.
7. Listed-but-quarantined IDs still count as observed for absence.
8. Recovery rows are stale for current completeness.
9. Backfill and replay never reconcile.
10. Ingestion never deletes user history.
11. Lifecycle is derived across provider identities.
12. Hidden events are suppressed, not destructive.
13. Active and unverified events remain public.
14. Every timezone boundary has an explicit owner.
15. Source local dates/times are not browser-timezone converted.
16. No title-text cancellation or lineup inference.
17. No venue-name heuristics for TBA.
18. No source display-name matching for identity.
19. Private ratings can contribute anonymously without attribution.
20. Attributed user data passes through `visible_to`.
21. Aggregates pass through `for_aggregation`.
22. Unsafe browser verification includes Origin.
23. Production must not inherit development CSRF exceptions.
24. No speculative schema or services without a consuming slice.

## Commands for the next session

### Orient

```sh
pwd
git status --short
git log -8 --oneline --decorate
```

### Read authority

```sh
cat docs/PROJECT_STATE.md
cat docs/PRODUCT_QA_SPEC.md
cat docs/ERD_REVIEW.md
```

Read the relevant DBML and fixture/architecture section before changing that layer.

### Verify backend and fixtures

```sh
.venv/bin/python manage.py check
.venv/bin/python manage.py test
.venv/bin/python docs/recon/fixtures/audit_expectations.py
.venv/bin/python manage.py makemigrations --check --dry-run
git diff --check
```

### Verify frontend

```sh
npm run build --prefix frontend
```

### Start local product

Terminal 1:

```sh
.venv/bin/python manage.py runserver
```

Terminal 2:

```sh
cd frontend
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

### Inspect listeners

```sh
lsof -nP -iTCP:8000 -sTCP:LISTEN
lsof -nP -iTCP:5173 -sTCP:LISTEN
lsof -nP -iTCP:5174 -sTCP:LISTEN
```

### Inspect live counts without exposing email

```sh
.venv/bin/python manage.py shell -c "
from catalog.models import City, Venue, Artist, Event
from users.models import User, DiaryEntry
print({
    'cities': City.objects.count(),
    'venues': Venue.objects.count(),
    'artists': Artist.objects.count(),
    'events': Event.objects.count(),
    'users': User.objects.count(),
    'diary_entries': DiaryEntry.objects.count(),
})
"
```

### Inspect latest ingestion run

```sh
.venv/bin/python manage.py shell -c "
from ingestion.models import SyncRun
r = SyncRun.objects.latest('id')
print(
    r.id,
    r.run_type,
    r.status,
    r.seeds_attempted,
    r.seeds_failed,
    r.events_upserted,
    r.events_quarantined,
    r.events_dropped,
    r.error_summary,
)
"
```

### Scheduler

```sh
launchctl print gui/$(id -u)/com.tan.danced.sync
tail -100 logs/sync.log
tail -100 logs/sync.err.log
```

## Next product work

Phase C Slice 4A is implemented locally and awaits review/push. Slice 4B is next:
query-time Home feed, `/discover` migration, `/` landing resolver, login/registration
landing flip, and `/?city_id=` compatibility. The named 4B test obligation is to
prove delayed acceptance orders by `approved_at` and same-time bulk approvals use the
heterogeneous technical tiebreak.

Before deployment:

- repay email verification;
- choose email delivery;
- establish hosted app/database/scheduler boundary;
- add backups and monitoring;
- remove reliance on DEBUG-only Vite CSRF trust;
- perform legal and source-terms review;
- pin and verify the production database version.

## Resume-project narrative

Danced now demonstrates more than a catalog scraper.

The ingestion side treats external data as fallible testimony:

- it archives exact evidence;
- separates wrapper completeness from event identity;
- quarantines bad observations without partial writes;
- permits incomplete data to add but never subtract;
- derives absence conservatively;
- resurrects safely;
- never deletes user history.

The product side now consumes those guarantees:

- hidden events disappear coherently from catalog, diary, and aggregates without
  deleting user records;
- venue-local time governs both browsing boundaries and logging eligibility;
- private ratings contribute anonymously through a separate aggregate boundary;
- retroactive history sorts by the event's historical position;
- session/CSRF behavior is exercised through a real React flow.

The strongest engineering stories are the correctness holes that were surfaced and
resolved rather than hidden:

- Cloudflare rejected the minimal acquisition headers.
- RA wrapper count did not equal unique event count.
- provider event identity could be absent at rejection time.
- resetting the database would have destroyed the raw evidence needed to rebuild it.
- Django's MySQL schema editor did not emit the required physical diary cascade.
- a global mocked clock expired authenticated test sessions.
- an omitted browser Origin made a false CSRF verification pass.

Each correction narrowed the system toward evidence and explicit ownership rather
than adding broad machinery. That discipline is the project’s central technical
claim.
