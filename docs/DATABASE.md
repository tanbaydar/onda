# Shipped database: crow's-foot reference

This document describes the **implemented Onda product schema** as of August 20, 2026. It is derived from the current Django models and migrations: 24 project-owned tables across ingestion, canonical identity, and application data.

It deliberately excludes Django framework tables and generated framework junctions for admin, permissions, groups, content types, migrations, and sessions. Those tables exist in the deployed database but do not express Onda's domain model.

## Read the notation

| Mark | Meaning |
|---|---|
| `||` | exactly one |
| `o|` | zero or one |
| `o{` | zero or many |
| `PK` | primary key |
| `FK` | foreign key |
| `UK` | unique key |

The diagrams show physical relationship cardinality. A stricter service invariant is called out in prose when the database alone cannot express it—for example, ingestion admits an event with at least one artist, but a foreign key cannot force every `EVENT` row to have an `EVENT_ARTIST` child at every instant.

## Three data zones

```mermaid
flowchart LR
    subgraph IZ[Ingestion evidence — 4 tables]
        Seeds[Tracked source pages]
        Runs[Run telemetry]
        Raw[Raw responses]
        Rejected[Quarantined observations]
    end

    subgraph CZ[Canonical + identity — 9 tables]
        Canon[City / venue / artist / event / lineup]
        Identity[Four provider identity maps]
    end

    subgraph AZ[Application — 11 tables]
        Accounts[Accounts + follows]
        Diary[Diary + reviews + likes]
        Social[Plans + favorites + notifications]
    end

    IZ -->|Transformer only| CZ
    CZ -->|canonical foreign keys| AZ
```

There is intentionally no foreign key from application tables back to ingestion evidence. Provider-shaped data ends at the Transformer and identity mappings.

## 1. Ingestion evidence

```mermaid
erDiagram
    TRACKED_SOURCE_PAGE ||--o{ RAW_INGEST : "is requested by"
    SYNC_RUN ||--o{ RAW_INGEST : "archives"
    RAW_INGEST ||--o{ REJECTED_INGEST : "can quarantine"

    TRACKED_SOURCE_PAGE {
        bigint id PK
        varchar source
        varchar area_ref
        varchar label
        boolean active
        datetime last_synced_at
        datetime last_success_at
    }

    SYNC_RUN {
        bigint id PK
        varchar run_type
        varchar status
        datetime started_at
        datetime finished_at
        int seeds_attempted
        int seeds_failed
        int events_upserted
        int events_quarantined
        int events_dropped
        text error_summary
    }

    RAW_INGEST {
        bigint id PK
        bigint seed_id FK
        bigint run_id FK
        date window_start
        date window_end
        int page_number
        int page_size
        text response_body
        smallint http_status
        datetime fetched_at
        varchar processing_status
    }

    REJECTED_INGEST {
        bigint id PK
        bigint raw_ingest_id FK
        int entity_index
        varchar entity_ref
        varchar reason
        text detail
        datetime rejected_at
    }
```

Key constraints:

- `TRACKED_SOURCE_PAGE(source, area_ref)` is unique.
- `SYNC_RUN.run_type` is one of `nightly`, `backfill`, `replay`; status is `running`, `completed`, or `crashed`.
- `RAW_INGEST.processing_status` is `pending`, `processed`, or `failed`.
- `REJECTED_INGEST(raw_ingest_id, entity_index)` is unique, so replay cannot duplicate the same occurrence.
- Raw-to-seed, raw-to-run, and rejected-to-raw deletion behavior is restrictive. Evidence cannot disappear through an ordinary parent cascade.

`RAW_INGEST` has operational indexes on `run_id` and `(seed_id, fetched_at)`. The raw response is text rather than a native JSON column so a malformed or non-JSON body can still be preserved exactly.

## 2. Canonical catalog and provider identities

```mermaid
erDiagram
    CITY ||--o{ VENUE : "contains"
    VENUE ||--o{ EVENT : "hosts"
    EVENT ||--o{ EVENT_ARTIST : "has lineup slots"
    ARTIST ||--o{ EVENT_ARTIST : "fills"

    CITY ||--o{ CITY_IDENTITY : "maps from sources"
    VENUE ||--o{ VENUE_IDENTITY : "maps from sources"
    ARTIST ||--o{ ARTIST_IDENTITY : "maps from sources"
    EVENT ||--o{ EVENT_IDENTITY : "maps from sources"

    CITY {
        bigint id PK
        varchar name
        varchar region_code
        varchar region_name
        char country_code
        varchar timezone
    }

    VENUE {
        bigint id PK
        varchar name
        bigint city_id FK
    }

    ARTIST {
        bigint id PK
        varchar name
        varchar image_url
    }

    EVENT {
        bigint id PK
        varchar title
        date event_date
        time start_time
        bigint venue_id FK
        varchar cover_image_url
        varchar status
        bigint canonical_event_id FK
    }

    EVENT_ARTIST {
        bigint id PK
        bigint event_id FK
        bigint artist_id FK
        int position
    }

    CITY_IDENTITY {
        bigint id PK
        bigint city_id FK
        varchar source
        varchar source_id
    }

    VENUE_IDENTITY {
        bigint id PK
        bigint venue_id FK
        varchar source
        varchar source_id
    }

    ARTIST_IDENTITY {
        bigint id PK
        bigint artist_id FK
        varchar source
        varchar source_id
    }

    EVENT_IDENTITY {
        bigint id PK
        bigint event_id FK
        varchar source
        varchar source_id
        datetime last_seen_at
        int misses
    }
```

Composite uniqueness that cannot be expressed field-by-field in the compact diagram:

- `CITY(country_code, region_code, name)`;
- `EVENT_ARTIST(event_id, artist_id)` and `EVENT_ARTIST(event_id, position)`;
- every identity table: `(source, source_id)` and `(canonical_id, source)`.

Canonical records never store an RA ID. A provider ID is unique only inside its `(entity type, source)` namespace and resolves through the matching identity table. This supports stable Onda IDs when provider display attributes change and creates a place for another source identity if a future integration deliberately maps it to the same real entity.

`EVENT.status` is constrained to `active`, `unverified`, or `hidden`. `EVENT_IDENTITY.misses` and `last_seen_at` retain the source testimony used to derive that status. Catalog indexes support `(status, event_date)` and `(venue_id, event_date)` reads.

A provider can occasionally publish separate source IDs for the same show. When title, venue, local date/time, and ordered lineup all agree, the later `EVENT` row retains its own identity evidence but points to the earliest row through `canonical_event_id`. Catalog reads expose only the canonical row, old alias URLs resolve to it, and lifecycle reconciliation considers evidence from the whole alias group. The migration only marks groups that have no user-owned Been, Will Be There, or favorite data; it never deletes source or event rows.

Deletion intent differs by relationship:

- deleting a canonical city, venue, artist, or event is restricted while downstream canonical/product references exist;
- deleting an event cascades through its lineup and provider identity rows only after those restrictions have been resolved;
- deleting an artist is restricted by lineup use;
- canonical deletion is not the normal response to source absence—lifecycle status is.

## 3. Application and social data

### Accounts, follows, and publishing

```mermaid
erDiagram
    CITY o|--o{ ONDA_USER : "is optional home city for"
    ONDA_USER ||--o{ ACCOUNT_CODE : "owns"
    ONDA_USER ||--o{ FOLLOW : "acts as follower"
    ONDA_USER ||--o{ FOLLOW : "acts as followee"

    ONDA_USER ||--o{ DIARY_ENTRY : "logs"
    EVENT ||--o{ DIARY_ENTRY : "is logged in"
    DIARY_ENTRY ||--o| REVIEW : "may publish"
    ONDA_USER ||--o{ REVIEW_LIKE : "creates"
    REVIEW ||--o{ REVIEW_LIKE : "receives"

    CITY {
        bigint id PK
    }

    EVENT {
        bigint id PK
    }

    ONDA_USER {
        bigint id PK
        varchar email UK
        varchar username UK
        varchar display_name
        varchar bio
        varchar avatar
        bigint home_city_id FK
        boolean is_private
        varchar status
        datetime email_verified_at
        datetime deletion_due_at
        datetime created_at
    }

    ACCOUNT_CODE {
        bigint id PK
        bigint user_id FK
        varchar purpose
        varchar code_hash
        datetime sent_at
        datetime expires_at
        smallint failed_attempts
        datetime consumed_at
    }

    FOLLOW {
        bigint follower_id PK, FK
        bigint followee_id PK, FK
        varchar status
        datetime created_at
        datetime approved_at
    }

    DIARY_ENTRY {
        bigint id PK
        bigint user_id FK
        bigint event_id FK
        decimal rating
        datetime rated_at
        datetime created_at
    }

    REVIEW {
        bigint id PK
        bigint entry_id FK, UK
        varchar body
        datetime published_at
    }

    REVIEW_LIKE {
        bigint user_id PK, FK
        bigint review_id PK, FK
        datetime created_at
    }
```

### Plans and favorites

```mermaid
erDiagram
    ONDA_USER ||--o{ WILL_BE_THERE : "plans"
    EVENT ||--o{ WILL_BE_THERE : "is planned"

    ONDA_USER ||--o{ FAVORITE_EVENT : "chooses"
    EVENT ||--o{ FAVORITE_EVENT : "is selected"
    ONDA_USER ||--o{ FAVORITE_ARTIST : "chooses"
    ARTIST ||--o{ FAVORITE_ARTIST : "is selected"
    ONDA_USER ||--o{ FAVORITE_VENUE : "chooses"
    VENUE ||--o{ FAVORITE_VENUE : "is selected"

    ONDA_USER {
        bigint id PK
    }

    EVENT {
        bigint id PK
    }

    ARTIST {
        bigint id PK
    }

    VENUE {
        bigint id PK
    }

    WILL_BE_THERE {
        bigint user_id PK, FK
        bigint event_id PK, FK
        datetime created_at
    }

    FAVORITE_EVENT {
        bigint user_id PK, FK
        bigint event_id PK, FK
        datetime added_at
    }

    FAVORITE_ARTIST {
        bigint user_id PK, FK
        bigint artist_id PK, FK
        datetime added_at
    }

    FAVORITE_VENUE {
        bigint user_id PK, FK
        bigint venue_id PK, FK
        datetime added_at
    }
```

### Notifications

```mermaid
erDiagram
    ONDA_USER ||--o{ NOTIFICATION : "receives"
    ONDA_USER ||--o{ NOTIFICATION : "acts in"
    REVIEW o|--o{ NOTIFICATION : "optionally concerns"

    ONDA_USER {
        bigint id PK
    }

    REVIEW {
        bigint id PK
    }

    NOTIFICATION {
        bigint id PK
        bigint recipient_id FK
        bigint actor_id FK
        varchar type
        bigint review_id FK
        datetime created_at
        datetime read_at
    }
```

`ONDA_USER` is the custom Django user table. It also contains framework account
fields such as the password hash and staff/activity flags, omitted above so the
domain relationships remain readable.

### Composite identities and caps

The following relationships use composite primary keys, which makes “the same relationship twice” physically impossible:

- `FOLLOW(follower_id, followee_id)`;
- `REVIEW_LIKE(user_id, review_id)`;
- `WILL_BE_THERE(user_id, event_id)`;
- each of the three favorite tables `(user_id, target_id)`.

`DIARY_ENTRY` uses a surrogate primary key but makes `(user_id, event_id)` unique because `REVIEW.entry_id` needs a stable one-to-one parent. Favorite counts—at most three events, artists, and venues per user—are cross-row rules enforced transactionally in the service layer rather than by a simple row check.

### Checks that encode product laws

Representative database checks include:

- an active user must have a username; deactivated/pending-deletion users must not;
- only a pending-deletion user has `deletion_due_at`;
- account-code expiry is after send time and failed attempts are at most five;
- a user cannot follow themself;
- pending follows have no approval time and approved follows do;
- diary `rating` and `rated_at` are null or populated together;
- rating is null or a valid half-star value from 0.5 through 5.0;
- review body cannot be whitespace-only;
- notification actor and recipient differ;
- only `review_like` notifications have a review reference.

Some domain laws require transactions rather than row-local checks: an event must have started before the first Been entry, a review needs a rating, Will Be There expires by venue-local date, favorite lists have caps, and viewer privacy depends on an approved follow relationship.

### Cascades and restrictions

User-owned data uses physical MySQL cascades:

```mermaid
flowchart LR
    User[ONDA_USER deleted] --> Owned[Codes, follows, diary, likes,<br/>plans, favorites, notifications deleted]
    Diary[DIARY_ENTRY deleted] --> Review[REVIEW deleted]
    Review --> Likes[REVIEW_LIKE deleted]
    Review --> ReviewNotif[Review-linked notifications deleted]

    Event[EVENT referenced] -->|RESTRICT| DiaryKeep[DIARY_ENTRY]
    Event -->|RESTRICT| PlanKeep[WILL_BE_THERE]
    Event -->|RESTRICT| FavKeep[FAVORITE_EVENT]
```

Django ORM cascade declarations do not automatically mean MySQL emitted the same physical `ON DELETE` action. The migration history explicitly rebuilds and tests those foreign keys, so the ownership policy survives direct database enforcement as well as ORM deletion.

## Indexes aligned with read paths

The schema uses targeted indexes rather than indexing every foreign key twice:

| Index | Read path |
|---|---|
| `EVENT(status, event_date)` | visible upcoming/past catalog |
| `EVENT(venue_id, event_date)` | venue event lists |
| `RAW_INGEST(run_id)` | run recovery and diagnostics |
| `RAW_INGEST(seed_id, fetched_at)` | source-page history |
| `FOLLOW(followee_id, status)` | follower counts, requests, privacy checks |
| `NOTIFICATION(recipient_id, created_at)` | notification timeline |
| `NOTIFICATION(recipient_id, read_at)` | unread counts and bulk read |

Composite primary/unique keys also provide useful access paths for relationship existence checks. Query-count and cursor behavior for the most complex read—the six-branch Home feed—are covered separately in [APPLICATION_DATA.md](APPLICATION_DATA.md#home-is-a-projection-not-a-ledger).

## Source of truth

The diagrams above cover the 24 Onda-owned tables that are currently shipped. Django framework tables are present in the physical database but omitted because they do not define Onda's domain model. Unshipped design ideas are not included.

| Schema area | Models | Migration history |
|---|---|---|
| Ingestion evidence | `backend/ingestion/models.py` | `backend/ingestion/migrations/` |
| Canonical and identity | `backend/catalog/models.py` | `backend/catalog/migrations/` |
| Accounts and social | `backend/users/models.py` | `backend/users/migrations/` |

Run `.venv/bin/python backend/manage.py makemigrations --check --dry-run` to detect model/migration drift and `.venv/bin/python backend/manage.py test` to exercise schema and behavioral constraints against MySQL.
