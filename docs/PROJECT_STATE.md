# Danced — Project State and Conversation Handoff

> Last verified: 2026-08-02 (America/New_York)
>
> Repository: `/Users/ilkerbaydar/Desktop/danced_app`
>
> Branch: `main`
>
> Verified implementation state: Milestone 4 is effectively complete; the M5
> verification-enforcement prerequisites are code-complete behind the disabled flag.
>
> Verified Git state before this documentation commit: local `HEAD` and
> `origin/main` both at `f1d637055245202cb3763bb17b5f67f2ccea83d4`.
>
> Purpose: provide the single current, evidence-based handoff for ingestion,
> catalog, product, social architecture, local operations, and the next phase.

## Status of this document

This file is updated in place and is the sole current project-state document. Every
future session must read `docs/PROJECT_STATE.md`; do not create numbered successors.
The superseded Milestone 1 handoff remains only as historical evidence at
`docs/archive/PROJECT_STATE_MILESTONE_1_2026-07-30.md`.

This document summarizes implementation. It does not supersede the frozen DBML,
ERD review, product decisions, ingestion architecture, fixture contract, committed
tests, migrations, or `docs/NAVIGATION.md`. If a summary here conflicts with an
authoritative artifact, investigate the discrepancy rather than choosing whichever
text is convenient.

## Current status — 2026-08-01/02 session

### Headline status

**Milestone 4 is effectively complete.** Every product surface is designed and
implemented over the real semantic frontend: Discover, Search, Event, Profile,
Edit Profile, Home, Activity (timestamps), and all four auth surfaces. The
unstyled-semantic era is over. The M5 verification-enforcement slice is
code-complete and armed behind its flag.

### Decisions resolved this session

- **Search: KEEP — built and shipped.** The five-position navigation skeleton is complete; Search occupies position 3 for guests and authenticated users. The desktop header quick-search was built and then removed by ruling; the Search page and DiscoverSearch are the only search surfaces.
- **Deploy target: Render** (supersedes Railway). MySQL 8.x as a Render private service with persistent disk is the pending approach (unratified until deploy schedules). RENDER-DEPLOY-GATED order is fully drafted and shelved; blockers: operator's persona/bot-boundary ruling. Deploy inherits: server-level 301s via Django ownership of public entity paths (slug report note); backups; pinned MySQL + physical-constraint rerun; basic-auth gate; console email acceptable while verification stays dark.
- **Slug strategy resolved**: /e|/v|/a/{slug}-{id}, ID-last, derived slugs, no storage, SPA canonicalization now, true 301s at deploy.
- **Allocation rule color clause ratified permanent** (semantic green). See spec amendment block.
- **Punch-list closures**: pluralization sweep (zero-form grammar, product-wide), feed activity timestamps (relative, Home + Activity), event-page hierarchy (owner block + state gating, verified both directions), WBT-count prominence (color slot on upcoming events).

### Commit ledger (this session, chronological, all on origin/main)

| Commit | What |
|---|---|
| f9a1b39 | Favicon |
| 8c7e16b | Search integration (page, API, nav, scopes, recents, keyboard) |
| 1dce6d5 | Recents: commit-signal recording, prefix dedupe |
| a01deae | Search scope-switch fix (stale-payload crash) |
| fa9ac00 | Discover dropdown + quick-search panel conform |
| da750ec / d6f3b73 / b30cf49 / a670e9e / c135a58 | Handoffs tracked (search, histogram, event, stats, home, discover, auth) |
| 34e21d9 | Markdown-only handoff policy; AGENTS.md rule |
| d18c185 | Event page: StarInput, owner block, state gating; histogram integration |
| 0dd16cf | Histogram render gate removed (always renders) |
| fb23a31 / 879b1f3 | Navigation contract extraction; header quick-search removed |
| 50caa91 | F/F counts public on private-outsider profiles |
| 0d30a27 | Profile statistics surface (header F/F, five-item strip, FollowControl) |
| 97b789f | Profile Reviews conform (custom sort menu, favorites rows) |
| 2fb1f78 | Additive avatars: review authors + Circle (operator ruling) |
| 8967d40 | Event review rows conform; favorite-rejection recovery |
| 8e11385 | Event review sort → shared custom menu (last native select) |
| bd7576b | Account-menu flat panel; "more" truncation-gated |
| 6906e8a | Guest header: bordered Register + quiet Log in |
| a137fe4 | Account menu + logout flow |
| 7114de7 / e1c8bd9 | Home feed serializer amendment + implementation |
| c147d74 / 42cc60b / a1b294f | Verification-enforcement prerequisites (all three) |
| 88efdf1 | Canonical slug routes + centralized URL builder (+ event_title on notifications) |
| 404db4d | Discover redesign implementation |
| b9f92ff / da851a3 / c6e5f33 | Auth handoff amendment; username-or-email login; auth surfaces |
| 53fa4c5 / f2c0dfe | StarInput interaction and shared half-star geometry; operator live-verified |
| 3d2b68b / 70799b7 / 21567db | Imagery-polish handoff, backend amendments, and frontend integration |
| 2c73b00 | Repository formalization and clean full-history secrets audit |
| 00dd359 / 34ba1c0 | Frontend quality Fix A and honest source-assertion test labels |
| f1d6370 | Personal and archived HTML artifacts removed |
| pending | Tier B frontend refactor slice — audit report is the specification |
| pending | Browser-DOM test infrastructure slice — coverage map recorded by audit |
| pending | Design blessing for the A1 session-error slot placement |

### Backend contract amendments

The initial four additive amendments this session share one pattern (see spec block
for detail):
Home-feed presentation fields (7114de7); review/Circle avatars (2fb1f78);
event_title on review-like notifications (88efdf1); username-or-email login
(da851a3). All carry operator-ruling provenance in their commit messages; all
assert existing behavior unchanged by test; flag-off auth behavior proven
byte-identical. The later imagery/favorites boundary amendments are recorded in the
second-wave spec addendum and commit ledger.

### Verification-enforcement slice

Code-complete on main. Unverified sessions get guest-equivalent reads at the
sanctioned boundaries; session payloads expose self-only verification state
(flag-on only; never on public payloads); flag-on auth routes to /verify-email.
EMAIL_VERIFICATION_ENFORCED remains False. Remaining work is deployment-only:
flag flip, email provider + sending domain, landing-flow swap. Provider
shortlist when it matters: Resend or Postmark.

### Design handoffs (authoritative set, markdown-only)

frontend/design-handoffs/: search-handoff.md (dated deltas: recents rules,
quick-search removal) · histogram-handoff.md (superseded ≥5 gate noted) ·
event-handoff.md · stats-handoff.md (v3) · profile-handoff.md ·
home-handoff.md · discover-handoff.md · auth-handoff.md (dated delta:
five-field registration, username-or-email). All spec/*.html citations inside
handoffs are historical dead references per the markdown-only policy.

### Consolidated backlog (updated)

#### Design (small batch for next Claude Design pass)
- Bless the minimal **session-error slot placement** below the header band. Its
  behavior and error register are shipped; only placement awaits design review.

#### Product decisions (operator)
- **Persona/bot boundary** for demo seed data: safe tier (profiles, follows, Been, favorites, WBT — no fabricated opinions) vs. labeled demo reviews vs. founder-written reviews. Blocks the gated deploy. Note: mass-seeded engagement is adjacent to the parked sockpuppet-defense risk; keep seed data out of anything trust- or popularity-consuming.
- **Minimum-n score display**: reopened — the histogram's interim ≥5 gate partially answered it and was removed.
- **Guest Follow → login/register** affordance: parks with the Q203 onboarding decision.

#### Engineering
- **Tier B frontend refactor slice**: the frontend quality-audit report is its
  specification; no opportunistic adjacent cleanup.
- **Browser-DOM test infrastructure**: frontend tests are source/CSS assertions plus live-browser QA; a rendered-component framework is a deliberate future slice (flagged honestly by the agent four times; barred as scope creep so far). Pairs naturally with the parked React Router v7 upgrade (dependency-touching).
- **Sockpuppet defenses**: unchanged, parked until popularity/trust consumers exist.

#### Milestone 5 / deployment (updated)
- RENDER-DEPLOY-GATED: drafted, shelved, fire-on-command. Blockers: persona ruling only (prereqs and slugs landed this session).
- Email provider + sending domain: deployment-motion decision.
- RA contact: triggered by public availability; a basic-auth-gated private demo does not trigger it (operator's legal read to confirm before first external access).
- Scheduler migration (LaunchAgent → Render cron), pinned MySQL + physical-constraint rerun, backups: all specified inside the shelved deploy order.

### Conduct contract additions (AGENTS.md)

- Design handoffs: markdown sole authority; no spec HTML in repo; visual disputes escalate to the operator. (Committed, 34e21d9.)
- Every order gets a report, even "already shipped in X". (Recorded in this update.)
- Approved orders push by default; hold only when ordered or when unrelated work would publish — then ask. (Recorded in this update.)

### Session narrative (one paragraph, for the resume-project record)

This session closed Milestone 4. Design moved from module-level handoffs to
full-page composition across every surface, held together by a small set of
ratified patterns (allocation rule as settled law, tab register, panel
register, row anatomies, verb-survival, contextual titles). The workflow's
best moments were contract stops: the agent halted on the feed serializer's
missing presentation fields, the SPA's inability to emit real 301s, and two
auth-handoff/contract conflicts — each resolved by explicit operator ruling
with additive, test-asserted amendments rather than silent drift. The
verification slice went from deferred debt to armed; slugs made URLs
canonical; the product is one persona ruling and one deploy order away from a
gated demo.

## Read this first

Danced is a Letterboxd-style social diary for live music. It now has three complete
working foundations:

1. A conservative, replayable Resident Advisor ingestion pipeline over live New
   York City and Boston catalog data.
2. A public catalog API and fully integrated React product surface under the locked
   Milestone 4 design system.
3. A session-authenticated social layer: identity, privacy, Been, ratings, reviews,
   likes, follows, requests, notifications, Circle, Home, Will Be There, profiles,
   favorites, and profile statistics.

The product is no longer merely a scraper or event list. A user can browse the real
catalog; register and choose privacy; record and rate attendance; publish and like
reviews; follow public users or request private users; inspect Activity and Home;
mark Will Be There; edit a profile; select favorites; and inspect privacy-safe
profile history, statistics, and rating distribution.

Two standing local accounts are intentional data:

- `tan`: the founder's private account and real diary data;
- `review.public.test`: a public test account for the review/social browser pipeline.

Verification must never modify the founder's account or diary. Use disposable named
accounts and delete them with cascade verification, or use the standing public test
account only where its documented purpose applies. Never expose either account's
email in handoff prose or other-user serialization.

## Workflow rule

The central implementation rule remains:

> Do not silently redesign settled behavior while implementing it.

Treat the DBML, ERD review, product questions, architecture contract, frozen fixture
README, navigation contract, committed migrations, and tests as contracts. When
implementation reveals a contradiction:

1. stop the affected design branch;
2. identify the exact conflicting rulings;
3. report the correctness hole;
4. propose the smallest evidence-based resolution;
5. wait for approval when the specification does not answer;
6. record an approved freeze-break or interpretation;
7. prove it with focused tests and, where false positives are plausible, mutation
   evidence.

Do not reopen settled ingestion design without concrete contradictory evidence. Do
not make product decisions merely because a framework default is convenient.

## Current milestone position

### Milestone 1 — ingestion and catalog foundation

Complete and pushed:

- captured source evidence and replayable fixtures;
- append-only raw request archive;
- per-observation admission and quarantine;
- source-neutral canonical catalog and identity firewall;
- replay-safe upserts and stable lineup ordering;
- completeness-gated absence reconciliation and resurrection;
- bounded, paced acquisition with run lock, telemetry, and alarms;
- local daily scheduling;
- live NYC and Boston data.

### Milestone 2 — catalog API and guest shell

Complete and pushed:

- canonical cities endpoint;
- city-, venue-, and artist-scoped upcoming and past events;
- venue-local date classification and deterministic pagination;
- event, venue, and artist details;
- Vite + React guest shell in plain JSX;
- Discover with Upcoming and Recent sections;
- event, venue, and artist pages;
- loading, error/retry, empty, and not-found states;
- source attribution footer and timezone-neutral display formatting;
- no styling, placeholder imagery, speculative endpoints, or source-title parsing.

### Milestone 3 — social layer

**Complete, verified, and pushed.** Every planned slice shipped:

1. **Identity:** custom user, required privacy choice, registration, login, logout,
   current-session bootstrap, session authentication, and CSRF.
2. **Been and ratings:** venue-local logging gate, mandatory creation rating,
   editable/removable rating, preserved unrated attendance, deletion, diary, and
   anonymous global averages.
3. **Recent events (2.5):** independently paginated city-scoped Recent section on
   Discover as the explicit interim recency stand-in for future popularity.
4. **Reviews and likes:** review lifecycle coupled to rated attendance, immutable
   publication position, public/private visibility, likes, cascades, and Public
   review ordering.
5. **Follows, notifications, Activity, and Circle (4A):** public follows, private
   requests, transactional privacy transitions, stored notifications, Activity,
   widened visibility, Circle list/average, and real follower-count ordering.
6. **Home and landing transition (4B):** query-time database-union feed, cursor
   pagination, `/home`, `/discover`, authentication-aware `/`, and legacy city-link
   preservation.
7. **Will Be There:** venue-local calendar expiry, logical retention for
   postponement recovery, Public/Circle attendees, active anonymous count, controls,
   and Home activity.
8. **Profile core and absorption (6A):** `/u/{username}`, Been and Reviews tabs,
   private stub/full/owner access, identity/privacy editing, relationship controls,
   request queue, and absorption of every interim navigation surface.
9. **Favorites, statistics, and final feed sources (6B):** capped event/artist
   favorites, private venue favorites, profile statistics and normalized given-
   rating distribution, anonymous WBT count, and the fifth/sixth Home branches.

Post-close corrections are also pushed:

- `294d456` prevents private-profile stubs and direct protected-tab routes from
  advertising inaccessible Been/Reviews chrome;
- `0e577d5` preserves field-keyed favorite-cap 409 errors beside the favorite
  control instead of refetching the message out of existence.

Milestone 3 closes with the backend, frontend, migrations, fixtures, browser
security flow, concurrency contracts, and physical foreign-key behavior verified.

### Milestone 4 — Design

**Effectively complete.** The locked design system is integrated across Discover,
Search, Event, Profile, Edit Profile, Home, Activity timestamps, and all four auth
surfaces. The unstyled-semantic era is over. Remaining frontend work is the explicit
audit backlog, not unfinished M4 surface integration.

### Milestone 5 — Deployment

Planned after design. The verification-enforcement prerequisites are already
code-complete and armed behind `EMAIL_VERIFICATION_ENFORCED=False`; deployment must
still configure delivery, flip the flag, and replace the immediate-use landing flow.

- enable the already-built-dark mandatory email-verification gate only during the
  ruled deployment motion;
- activate the already-built password-reset screens and choose production email
  delivery; both flows share the six-digit-code foundation;
- choose and integrate an email provider;
- deploy to Render, with a deliberately pinned supported MySQL 8.x private service
  and persistent disk as the pending approach;
- migrate the local LaunchAgent schedule to hosted scheduling;
- establish backups, monitoring, environment/secrets handling, and recovery drills;
- complete the deployment security checklist: secure session and CSRF cookies,
  correct reverse-proxy HTTPS recognition or end-to-end TLS, HTTPS redirect/HSTS
  as appropriate, deployment hosts, and a clean `manage.py check --deploy`;
- deploy behind link access plus basic authentication for the gated posture;
- contact Resident Advisor by email at or before public availability;
- complete legal/source-terms review before broad access.

## Sources of truth and authority

Read current artifacts in this order:

1. `docs/PRODUCT_QA_SPEC.md` — 210 decisions plus appended amendments.
2. `docs/danced.dbml` — frozen full database blueprint.
3. `docs/ERD_REVIEW.md` — reviewed ORM/physical deltas and freeze-breaks.
4. `docs/danced-data-architecture.md` — ingestion ownership and invariants.
5. `docs/recon/fixtures/README.md` — frozen fixture and Transformer contract.
6. Committed tests — executable contracts for implemented behavior.
7. Committed migrations — immutable physical-schema history.
8. `docs/NAVIGATION.md` — binding destinations, landing, and absorptions.
9. `docs/RA_SOURCE_RECON.md` — source evidence and request behavior.
10. `docs/OPERATIONS.md` — local operations and browser-equivalent verification.
11. This file — current implementation and runtime handoff.
12. `docs/archive/` — superseded history only.

## Technology and repository shape

### Backend

- Python 3.14 local runtime
- Django 6.0.7
- MySQL via `mysqlclient` 2.2.8
- `python-dotenv` 1.1.1
- plain Django JSON views
- Django sessions and CSRF middleware
- no DRF, GraphQL, JWT, Celery, Redis, or worker queue

### Frontend

- Vite 8.2
- React and React DOM 19.2
- React Router DOM 6.30
- plain JavaScript and JSX
- plain `fetch`
- no TypeScript
- no global state-management library
- no component library
- scoped plain CSS and `className`; no CSS framework

### Django apps

- `catalog`: canonical event catalog and public reads;
- `ingestion`: acquisition, archival, transformation, quarantine, reconciliation,
  runner, and command;
- `users`: identity, authentication, social models/services, privacy boundaries,
  and APIs;
- `config`: settings, source enum, and URL wiring.

## Git state and closing commits

The verified pre-documentation state was clean with local and remote at:

```text
0e577d5 fix: preserve favorite limit errors beside controls
44080d6 feat: expose favorites and Milestone 3 profile summaries
d51b51c feat: add favorites, profile statistics, and final Home feed sources
294d456 fix: hide protected Profile tabs from private stubs
1e2e04c feat: add zero-style Profile core and absorb interim surfaces
51ca719 feat: add privacy-safe Profile core APIs and repair home-city restriction
0b780ca feat: add zero-style Will Be There controls and attendee sections
6231cd0 feat: add venue-local Will Be There state and Home activity
b59a240 feat: add Home and execute authenticated landing transition
cd1d95a feat: assemble cursor-paginated Home activity in one database union
```

This documentation commit advances both local and `origin/main`; its final hash is
reported in the completion message rather than predicted inside the file.

## Implemented database and migration state

All migrations listed here are applied to the real local database.

| App | Applied migrations |
|---|---:|
| `admin` | 3 |
| `auth` | 12 |
| `catalog` | 5 |
| `contenttypes` | 2 |
| `ingestion` | 3 |
| `sessions` | 1 |
| `users` | 13 |
| **Total** | **39** |

Current application migration tips:

```text
catalog.0005_seed_city_identities_and_enforce_cascade
ingestion.0003_remove_rejectedingest_uq_rejection_payload_entity_and_more
users.0013_enforce_favorite_user_cascades
```

The user-zone tables implemented through Milestone 3 are:

- `DANCED_USER`
- `DIARY_ENTRY`
- `REVIEW`
- `REVIEW_LIKE`
- `FOLLOW`
- `NOTIFICATION`
- `WILL_BE_THERE`
- `FAVORITE_EVENT`
- `FAVORITE_ARTIST`
- `FAVORITE_VENUE`

Important physical rules are enforced in MySQL, not merely simulated by ORM
collection behavior. User deletion cascades through owned diary, review-like,
follow, notification, WBT, and favorite rows as frozen. Canonical event/artist/
venue deletion remains restrictive where user history or preferences reference it.
The custom-user migration surgery preserved catalog and raw-ingestion evidence; its
durable pre-surgery dump remains outside the repository at:

```text
/Users/ilkerbaydar/danced-backups/danced_pre_users_20260731.sql
```

Do not migrate unused DBML tables speculatively. A slice introduces only tables it
consumes.

## Architecture facts to defend

### Catalog and lifecycle

- Event lifecycle values are `active`, `unverified`, and `hidden`.
- Public visibility includes active and unverified; hidden is suppressed.
- Hidden rows and user relationships are retained so resurrection restores them.
- No public payload exposes internal lifecycle vocabulary.
- Source titles do not produce cancellation or lineup inference.
- Venue records named TBA are ordinary source truth.
- Event dates and start times are venue-local values; frontend formatting never
  converts them through the browser timezone.

### Sanctioned visibility boundaries

Attributed and aggregate reads must use the named owned boundaries rather than
inline privacy filters:

- `User.objects.profile_content_visible_to(viewer)` — profile stub/full/owner
  authorization basis;
- `DiaryEntry.objects.visible_to(viewer)` — attributed diary/profile visibility;
- `DiaryEntry.objects.for_aggregation()` — anonymous global ratings;
- `DiaryEntry.objects.for_circle(viewer)` — followed users only, self excluded;
- `DiaryEntry.objects.for_circle_average(viewer)` — followed ratings plus self;
- `Review.objects.visible_to(viewer)` — attributed review visibility;
- `Review.objects.for_public_section()` — public-account event-page reviews only;
- `WillBeThere.objects.active_at(at)` — venue-local active-state boundary;
- `WillBeThere.objects.visible_to(viewer, at)` — attributed attendee visibility;
- `WillBeThere.objects.for_public_section(at)` — public attendees;
- `WillBeThere.objects.for_circle(viewer, at)` — followed attendees, self excluded.

Profile favorite and statistics endpoints first pass through the user-level profile
content boundary. Favorite venues are private by construction: the only list route
is `/api/me/favorite-venues/`, with no other-user identity parameter. Anonymous WBT
counts use active rows independently of privacy-filtered attendee-list totals.

### Home feed

Home is query-time assembly, not a stored feed and not fan-out. Its six source
querysets are combined with `UNION ALL` in the database before pagination:

1. `will_be_there`
2. `review_like`
3. `rated_been`
4. `follow`
5. `favorite_event`
6. `favorite_artist`

The frozen descending cursor key is:

```text
(activity_at, activity_type, source_key)
```

At identical timestamps, lexical type ordering and fixed-width source keys provide
deterministic technical ties. Cursor predicates are distributed into every branch
before the union. Visibility is enforced inside each branch. Hidden events suppress
event-backed activity; unfollow, rating removal, WBT removal/expiry, and unfavorite
make source activity disappear automatically.

The authenticated Home endpoint executes four bounded queries on a mixed six-type
page: fixed session/auth work, one bounded city-timezone lookup, and one six-branch
feed query. The contract asserts one `UNION ALL`; adding feed types must not inflate
the count or merge per-source results in Python.

### Navigation

`docs/NAVIGATION.md` owns five destination positions in order:

1. Home — implemented at `/home`, signed-in only.
2. Discover — implemented at `/discover`, guest and signed-in.
3. Search — implemented at `/search` for guests and signed-in users.
4. Activity — implemented at `/activity`, signed-in only.
5. Profile — implemented at `/u/{username}`; guests receive Register/Login account
   access at this position.

The interim register has no live items. Every former organ/control was absorbed:
`/been` is a compatibility redirect to the owner's Profile, review-author bylines
link to Profile, follow controls live on Profile, pending requests live on the
owner's Profile, and account/logout controls attach to the Profile position.

Guest `/` resolves to Discover; authenticated `/` resolves to Home. Legacy
`/?city_id={id}` redirects preserve the city at `/discover?city_id={id}`.

### Frontend error classification

Non-2xx behavior must never disappear silently:

- field-keyed 400 validation renders beside its field;
- request-level validation renders once at the owning form/control;
- authentication, CSRF, server, and network failures remain distinct and honest;
- a 409 that is a true business rejection renders the server's field-keyed message;
- a 404/409 that represents state drift deliberately refetches every affected
  projection.

The favorite-cap correction at `0e577d5` is the business-rejection precedent. A
fourth favorite returns 409 and its `errors.favorite` message stays beside the
unchanged control; it must not be grouped with review-like/WBT state-drift 409s,
whose correct response is reconciliation.

## Product surface at Milestone 3 close

### Catalog and Discover

- `/discover` has city selection, Upcoming, and Recent sections with independent
  pagination.
- Event, venue, and artist detail routes use real catalog data.
- Hidden events return 404; active/unverified remain visible.
- Shared event lists suppress contextually redundant city, venue, or artist data.

### Identity and Profile

- Registration requires email, password, lowercase-valid username, display name,
  and an explicit Public/Private choice.
- Login uses email/password; logout invalidates the session.
- `/u/{username}` resolves case-insensitively and defaults to Been.
- `/u/{username}/reviews` owns the Reviews tab and its four sorts.
- Private unauthorized viewers receive only the Q37 identity stub; protected fields
  and tab chrome are absent, not rendered as zero.
- Owners can edit display name, URL avatar, verbatim-or-null bio, canonical home
  city, and privacy.
- Profiles own follow/request/withdraw/unfollow and pending-request decisions.
- Visible profiles include favorite events/artists, statistics, and normalized
  given-rating distribution; favorite venues are owner-only.

### Been, reviews, and ratings

- First Been creation requires a half-star rating from 0.5 through 5.0.
- Logging opens at event start in the venue timezone, or local midnight when time is
  absent; existing entries may be edited afterward.
- Rating removal preserves unrated attendance and removes dependent review content.
- Diary/profile history orders by event date, so retroactive entries appear at their
  historical position.
- Reviews require a rated entry, store 1–1,000 post-trim characters, retain original
  publication order through edits, and cascade likes on deletion.
- Global rating aggregates include private contributions anonymously and appear at
  three ratings; Circle averages appear at one and include self.

### Social activity

- Public follows approve immediately; private accounts receive pending requests.
- Public-to-private preserves approved followers; private-to-public transactionally
  approves pending rows at one true timestamp.
- Activity stores historical notifications for review likes, follows, requests, and
  acceptances; unlike/unfollow do not rewrite history.
- Circle lists include approved followees and exclude self; Circle averages include
  self by explicit separate boundary.
- Home is strictly newest-first query-time activity from followed users.

### Will Be There and favorites

- WBT is active through the event's venue-local calendar date and expires at local
  midnight the following day.
- Rows remain logically dormant so postponement can restore intent; expiry never
  converts WBT to Been.
- Public/Circle attendee lists are privacy-filtered; the active headline count is
  anonymous-inclusive.
- Event and artist favorites are capped at three under a user-row lock; repeated PUT
  preserves `added_at`; removal is idempotent.
- Venue favorites are uncapped, owner-only, feedless, and notification-free.
- Profile favorite order is earliest-added first. Favorite events need not be Been.

## Current verified counts

Measured from the committed repository on 2026-07-31:

- backend Django suite: **182 tests**, all green on a fresh test database;
- frontend Node suite: **8 tests**, all green;
- frozen fixture audit: **13 JSON fixtures**, clean;
- applied migrations: **39 total** across the seven apps listed above;
- `makemigrations --check --dry-run`: no model drift at the Milestone 3 close;
- frontend production build: passing, 38 modules transformed at the latest build;
- `git diff --check`: clean at the verified code checkpoint.

The frontend suite is a deliberately small pure-logic harness, not a full React DOM
component suite. Browser-equivalent CDP click-throughs cover high-risk integrated
flows, including session/CSRF, social projection synchronization, WBT, Profile
privacy chrome, and favorite-cap feedback.

## Ingestion runtime and operational state

### Runtime ownership

- `ingestion/client.py` owns bounded transport and retry behavior.
- Every fetch outcome is archived before domain admission.
- `ingestion/transformer.py` owns RA listing shape and quarantines one observation
  without leaving a partial canonical graph.
- Wrapper grain proves completeness; unique event-ID grain owns identity and
  reconciliation.
- Incomplete fetches may add but cannot prove absence.
- Only complete nightly windows reconcile; backfill/replay never reconcile.
- Listed-but-quarantined IDs still count as observed for absence.
- Reconciliation derives active/unverified/hidden across all provider identities,
  resurrects reappearing events, and never deletes user history.

### Daily scheduler

Local LaunchAgent:

```text
label: com.tan.danced.sync
schedule: daily at 16:00 local time
program: /Users/ilkerbaydar/Desktop/danced_app/.venv/bin/python
working directory: /Users/ilkerbaydar/Desktop/danced_app
stdout: logs/sync.log
stderr: logs/sync.err.log
```

Latest verified scheduled run:

```text
run ID: 9
status: completed
started: 2026-07-31 16:00:02 EDT
finished: 2026-07-31 16:01:32 EDT
seeds attempted/failed: 2 / 0
events admitted/upserted: 498
events quarantined: 318
events dropped: 0
error summary: none
scheduler exit code: 0
stderr: empty
```

The approximately 38–39% quarantine rate is the established `NO_ARTIST` baseline:
RA commonly lists events before publishing an ID-bearing structured lineup. Recent
runs produced 303–318 quarantines alongside 486–498 admitted events. Investigate
when the percentage changes materially, a different structural rejection reason
begins contributing, admitted events unexpectedly reach zero, a seed fails, or
wrapper completeness fails. Do not alarm merely because quarantines are nonzero.

### MySQL sandbox lesson

A sandboxed Django/MySQL error 2003 with local TCP errno `1` is not evidence that
mysqld stopped. The sandbox can deny `127.0.0.1:3306` while MySQL remains healthy.
Before restarting anything, inspect the process/service and logs or rerun the
read-only check with appropriate local permission. Earlier “MySQL stopped” reports
were corrected after this distinction was proven.

### Local operational limitations

The LaunchAgent depends on the laptop, user session, network, MySQL, repository, and
virtualenv remaining available at fixed paths. This is acceptable only for local
development. There is no hosted uptime monitor or automated backup schedule. The
pre-user-surgery dump is valuable historical safety evidence, not an ongoing backup
system.

## Consolidated backlog and triggers

The current backlog is recorded in the 2026-08-01/02 status section above. The M4
pre-design punch list—event hierarchy, relative feed timestamps, pluralization, and
WBT-count prominence—is closed.

### Product surfaces and decisions

- **Owner-only WBT list on own Profile:** schedule after M4. It requires an explicit
  product amendment because Profile tabs are contractually enumerated; do not add a
  silent third tab.
- **Favorite-venue notifications:** deferred during Slice 6B preflight. Trigger: a
  future notification/discovery product decision; do not infer one from storage.
- **Expired WBT retention policy:** dormant rows are currently retained for
  postponement recovery. Any purge needs a product ruling; no trigger is set.

### Milestone 5 / deployment

- **Verification activation:** enforcement prerequisites are complete behind
  `EMAIL_VERIFICATION_ENFORCED=False`. Deployment still owns email delivery, the flag
  flip, and the landing-flow change.
- **Password reset:** the non-enumerating six-digit-code API and unstyled screens are
  built dark. Production activation needs only the deployment email backend; the
  product amendment is recorded in `PRODUCT_QA_SPEC.md`.
- **Render MySQL:** provision the ruled Render private-service approach, pin a
  supported MySQL 8.x version, and rerun physical constraints.
- **Scheduler migration:** replace the local LaunchAgent with hosted scheduling.
- **Email provider:** choose alongside verification/reset delivery.
- **Canonical-route ownership:** slug-first, ID-last URLs are shipped in the SPA;
  deployment must give Django ownership so legacy/stale routes emit true HTTP 301s.
- **Gated posture:** link access plus basic authentication before broader exposure.
- **RA contact:** email Resident Advisor at or before public availability.
- **Seed script and smoke crawl:** post-deployment, by founder decision; include
  canonical seed/reference data and a bounded route crawl.
- **Deployment transport security:** explicitly configure secure session/CSRF
  cookies, reverse-proxy HTTPS recognition or end-to-end TLS, HTTPS redirect/HSTS
  where appropriate, deployment hosts, and run `manage.py check --deploy`.
- **Security-review accepted risks:** login/registration/reset and social-mutation
  throttling, reset timing equalization, audit logging, lockout policy, CSP, and
  remote-avatar policy may remain behind the gated link+basic-auth posture. Their
  trigger is removal of that gate or broader public access; password-reset timing
  and delivery throttling are also revisited with the production email provider.

The focused security-boundary review is recorded in
`docs/SECURITY_BOUNDARY_REVIEW.md`. Its first finding is resolved: public event
rating distributions now require the same three-rated-entry anonymity threshold as
the global average. Below three they return `not_enough_ratings`; exactly three
renders. Profile distributions were deliberately left unchanged because strangers
receive 403 for private profiles, public profiles intentionally expose attributed
ratings, and approved followers can already see the corresponding private diary.

### Parked engineering risks

- **Unexpectedly empty ingestion pages:** implement immediate termination in
  `_fetch_seed` when a page is unexpectedly empty. Correctness is already protected
  by completeness gating; this is request-budget hygiene. Trigger: next
  ingestion-touching slice.
- **Sockpuppet defenses:** parked until popularity/trust consumers or real-user abuse
  make manipulation consequential.
- **React Router v7:** upgrade when dependency-touching work next occurs, not as an
  isolated churn slice.

## Known limitations and explicit deferrals

### Email verification

Q125–126 require verification before account actions. The approved freeze-break
remains the default because `EMAIL_VERIFICATION_ENFORCED` is false. The complete
dark-built path includes the 15-minute/six-digit lifecycle, service-owned capability
gate, guest-equivalent reads for unverified sessions, self-only session verification
state, and flag-on routing through `/verify-email`. Deployment owns only the email
provider, flag flip, and landing-flow change.

### Onboarding

Q203 remains deferred. The real dependencies—favorites and suggested users—must be
integrated deliberately after design rather than added as empty stubs. Current login
and registration correctly land on Home.

### Search

Search is kept, built, and shipped at navigation position 3. `/search` and the
city-scoped `DiscoverSearch` are the only search surfaces; desktop header
quick-search is intentionally removed.

### Styling

The Milestone 4 design system is integrated over the semantic frontend. Future
visual changes remain governed by the Markdown handoffs and operator rulings.

### Deployment and source dependency

RA is an unofficial source dependency. Archive/replay limits data-loss risk but does
not guarantee access or authorization. Complete legal/source-terms review, the RA
contact, backups, monitoring, and version-pinned infrastructure before public use.

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
19. Private ratings and WBT can contribute anonymously without attribution.
20. Attributed user data passes through a sanctioned named boundary.
21. Aggregates use explicitly separate aggregate paths.
22. Privacy-filtered list totals never substitute for anonymous aggregate counts.
23. Unsafe browser verification includes Origin.
24. Production does not inherit development CSRF exceptions.
25. Feed sources join the database union; they are never merged after pagination.
26. Business-rule rejection messages remain visible; state drift reconciles.
27. No speculative schema or services without a consuming slice.
28. Founder data is never verification cleanup.

## Commands for the next session

### Orient

```sh
pwd
cat docs/PROJECT_STATE.md
git status --short
git rev-parse HEAD
git rev-parse origin/main
git log -10 --oneline --decorate
```

### Verify repository contracts

```sh
.venv/bin/python manage.py check
.venv/bin/python manage.py test --noinput
.venv/bin/python docs/recon/fixtures/audit_expectations.py
.venv/bin/python manage.py makemigrations --check --dry-run
npm test --prefix frontend
npm run build --prefix frontend
git diff --check
```

### Start the local product

Terminal 1:

```sh
.venv/bin/python manage.py runserver
```

Terminal 2:

```sh
cd frontend
npm run dev
```

Open `http://127.0.0.1:5173`.

### Inspect the scheduler

```sh
launchctl print gui/$(id -u)/com.tan.danced.sync
tail -100 logs/sync.log
tail -100 logs/sync.err.log
```

### Inspect the latest run

```sh
.venv/bin/python manage.py shell -c "
from ingestion.models import SyncRun
r = SyncRun.objects.latest('id')
print(r.id, r.run_type, r.status, r.started_at, r.finished_at,
      r.seeds_attempted, r.seeds_failed, r.events_upserted,
      r.events_quarantined, r.events_dropped, r.error_summary)
"
```

If that command returns MySQL error 2003 under a restricted sandbox, verify MySQL
process/service state before treating it as downtime or restarting it.

## Next product work

Execute only the consolidated backlog in the 2026-08-01/02 status section. The next
major motion is the gated Render deployment after the operator resolves the persona
boundary; owner WBT Profile history still requires an explicit product amendment.

## Resume-project narrative

Danced's strongest claim is not feature count. It is the way boundaries preserve
truth under unreliable external data and privacy-sensitive social reads.

The ingestion side archives exact evidence, separates wrapper completeness from
identity, quarantines without partial writes, permits incomplete data to add but not
subtract, derives absence conservatively, resurrects safely, and never deletes user
history.

The product side consumes those guarantees: hidden events disappear coherently
without erasing diary/favorite/WBT intent; venue-local time owns event boundaries;
private contributions aggregate anonymously; attributed content passes through named
visibility boundaries; feed deletion rules emerge from source rows rather than
fan-out cleanup; and cursor pagination is stable across heterogeneous live activity.

The workflow's best engineering moments were correctness holes surfaced rather than
hidden: wrapper totals were not unique events; a database reset would have destroyed
the evidence needed to rebuild; ORM cascades did not guarantee physical MySQL rules;
a global mocked clock expired sessions; missing Origin made a false CSRF check pass;
private Profile chrome leaked inaccessible affordances; and a business-rule 409 was
refetched out of visibility. Each correction narrowed ownership and made the contract
more truthful.

Milestone 4 is effectively complete. The next major question is gated deployment,
not another social feature slice.
