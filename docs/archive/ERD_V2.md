# Music Events Social Diary — ERD v2

This diagram accompanies `MUSIC_EVENTS_PLATFORM_SPEC.md`.

The central relationship is:

```text
USER -> DIARY_ENTRY -> EVENT <- EVENT_ARTIST -> ARTIST
                                  |
                                VENUE -> CITY
```

`USER` is an authenticated consumer. `ARTIST` and `VENUE` are catalog records, not accounts or businesses in the application.

```mermaid
erDiagram
    USER {
        bigint id PK
        varchar username UK
        varchar username_normalized UK
        varchar email UK
        varchar email_normalized UK
        varchar display_name
        bigint home_city_id FK
        varchar status
        varchar diary_visibility
        datetime created_at
        datetime updated_at
    }

    CITY {
        bigint id PK
        varchar name
        varchar region
        char country_code
        varchar timezone
        varchar normalized_key UK
    }

    VENUE {
        bigint id PK
        varchar name
        varchar slug UK
        bigint city_id FK
        varchar address
        varchar timezone
        varchar status
        bigint merged_into_id FK
    }

    ARTIST {
        bigint id PK
        varchar name
        varchar slug UK
        varchar artist_type
        text bio
        varchar image_url
        varchar status
        bigint merged_into_id FK
    }

    ARTIST_ALIAS {
        bigint id PK
        bigint artist_id FK
        varchar name
        varchar normalized_name
    }

    GENRE {
        bigint id PK
        varchar name
        varchar slug UK
    }

    ARTIST_GENRE {
        bigint artist_id FK
        bigint genre_id FK
    }

    EVENT {
        bigint id PK
        varchar title
        varchar slug UK
        varchar event_type
        datetime starts_at
        datetime ends_at
        date local_start_date
        varchar timezone
        bigint venue_id FK
        varchar online_url
        varchar image_url
        varchar status
        bigint merged_into_id FK
    }

    EVENT_ARTIST {
        bigint id PK
        bigint event_id FK
        bigint artist_id FK
        int billing_order
        varchar participation_type
    }

    EVENT_GENRE {
        bigint event_id FK
        bigint genre_id FK
    }

    DIARY_ENTRY {
        bigint id PK
        bigint user_id FK
        bigint event_id FK
        date attended_on
        tinyint rating_half_steps
        text review_body
        varchar visibility
        datetime review_published_at
        datetime review_edited_at
    }

    INTERESTED_EVENT {
        bigint user_id FK
        bigint event_id FK
        datetime created_at
    }

    USER_FOLLOW {
        bigint follower_id FK
        bigint followed_id FK
        datetime created_at
    }

    REVIEW_LIKE {
        bigint user_id FK
        bigint diary_entry_id FK
        datetime created_at
    }

    COMMENT {
        bigint id PK
        bigint diary_entry_id FK
        bigint author_id FK
        bigint parent_id FK
        text body
        varchar status
        datetime edited_at
    }

    EVENT_LIST {
        bigint id PK
        bigint user_id FK
        varchar title
        text description
        varchar visibility
        boolean is_ranked
    }

    EVENT_LIST_ITEM {
        bigint id PK
        bigint list_id FK
        bigint event_id FK
        int position
        text note
    }

    FAVORITE_EVENT {
        bigint user_id FK
        bigint event_id FK
        tinyint position
    }

    CATALOG_REQUEST {
        bigint id PK
        bigint requester_id FK
        varchar status
        bigint resolved_event_id FK
        bigint reviewed_by_id FK
    }

    NOTIFICATION {
        bigint id PK
        bigint recipient_id FK
        bigint actor_id FK
        varchar notification_type
        datetime read_at
        datetime created_at
    }

    REPORT {
        bigint id PK
        bigint reporter_id FK
        bigint reported_user_id FK
        bigint diary_entry_id FK
        bigint comment_id FK
        varchar reason_code
        varchar status
        bigint resolved_by_id FK
    }

    CITY o|--o{ USER : "home city"
    CITY o|--o{ VENUE : contains
    VENUE o|--o{ EVENT : hosts

    ARTIST ||--o{ ARTIST_ALIAS : has
    ARTIST ||--o{ ARTIST_GENRE : tagged
    GENRE ||--o{ ARTIST_GENRE : classifies

    EVENT ||--o{ EVENT_ARTIST : has
    ARTIST ||--o{ EVENT_ARTIST : performs
    EVENT ||--o{ EVENT_GENRE : tagged
    GENRE ||--o{ EVENT_GENRE : classifies

    USER ||--o{ DIARY_ENTRY : logs
    EVENT ||--o{ DIARY_ENTRY : receives
    USER ||--o{ INTERESTED_EVENT : saves
    EVENT ||--o{ INTERESTED_EVENT : saved_as_interested

    USER ||--o{ USER_FOLLOW : follower
    USER ||--o{ USER_FOLLOW : followed

    USER ||--o{ REVIEW_LIKE : gives
    DIARY_ENTRY ||--o{ REVIEW_LIKE : receives
    DIARY_ENTRY ||--o{ COMMENT : discusses
    USER ||--o{ COMMENT : writes
    COMMENT o|--o{ COMMENT : replies

    USER ||--o{ EVENT_LIST : creates
    EVENT_LIST ||--o{ EVENT_LIST_ITEM : contains
    EVENT ||--o{ EVENT_LIST_ITEM : listed
    USER ||--o{ FAVORITE_EVENT : selects
    EVENT ||--o{ FAVORITE_EVENT : favorited

    USER ||--o{ CATALOG_REQUEST : requests
    EVENT o|--o{ CATALOG_REQUEST : resolves_to
    USER ||--o{ NOTIFICATION : receives
    USER o|--o{ NOTIFICATION : acts
    USER ||--o{ REPORT : submits
```

## Required uniqueness constraints

- `USER(username_normalized)`
- `USER(email_normalized)`
- `ARTIST_ALIAS(artist_id, normalized_name)`
- `ARTIST_GENRE(artist_id, genre_id)`
- `EVENT_ARTIST(event_id, artist_id, participation_type)`
- `EVENT_GENRE(event_id, genre_id)`
- `DIARY_ENTRY(user_id, event_id)`
- `INTERESTED_EVENT(user_id, event_id)`
- `USER_FOLLOW(follower_id, followed_id)`
- `REVIEW_LIKE(user_id, diary_entry_id)`
- `EVENT_LIST_ITEM(list_id, event_id)`
- `EVENT_LIST_ITEM(list_id, position)`
- `FAVORITE_EVENT(user_id, event_id)`
- `FAVORITE_EVENT(user_id, position)`

## Required checks and service rules

- `DIARY_ENTRY.rating_half_steps` is null or between 1 and 10.
- A user cannot follow themselves.
- A review like requires a non-empty published review body.
- A comment requires a non-empty published review body.
- A reply and its parent must point to the same diary entry.
- A reply cannot itself have a reply.
- Favorite position is between 1 and 4.
- Exactly one report target is set.
- An event end time cannot precede its start time.
- A merged catalog record redirects to one active surviving record.
- A physical published event requires a venue; an online event does not.
- Venue and date are deliberately not unique.

Cross-row and cross-table rules belong in transactional Django services because MySQL checks cannot enforce all of them safely.
