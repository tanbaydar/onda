# Music Events Social Diary — Product and Technical Specification

**Status:** Working specification v0.1  
**Working title:** Onda
**Product shorthand:** Letterboxd for music events  
**Initial stack:** React with JSX · Python/Django · Django REST Framework · MySQL 8  
**Database client:** DataGrip

---

## 1. Product definition

Onda is a consumer social diary for music events.

The central analogy is exact:

| Letterboxd | Onda |
|---|---|
| Film | Music event |
| Film page | Event page |
| Cast and crew | Artists and lineup |
| Cinema/location | Venue |
| Watching a film | Attending an event |
| Diary entry | Attendance log |
| Rating/review | Event rating/review |
| Watchlist | Interested events |
| Film list | Event list |

Examples of a valid event:

- Shakira at Madison Square Garden
- John Summit at Savaya Bali
- A concert, DJ set, club night, festival, day party, livestream, or other named music performance

The event is the one primary object users log, rate, review, discuss, and add to lists. An artist or venue helps identify and discover an event, but neither is the review target in MVP.

## 2. Product principles

1. **The user is a logger first.** The diary is the core product. Reviews and social activity grow around it.
2. **The event is the equivalent of a film.** Ratings always describe the event as a complete experience.
3. **This is consumer-only.** Venues, promoters, artists, and other businesses do not create accounts, claim pages, manage events, or receive operator scores.
4. **Catalog identity and account identity are separate.** A user account is a person using the app. An artist record is catalog data.
5. **No provider is assumed yet.** Event data acquisition will be designed later. The initial product supports staff-created catalog records and user requests for missing records.
6. **Canonical objects replace free text.** Logs, reviews, lists, and search point to database-backed events, artists, venues, and cities.
7. **Incomplete data is acceptable.** An event may have an incomplete lineup, missing image, unknown end time, or uncertain venue details.
8. **History can be corrected.** Staff can merge duplicates and correct past events without breaking diary entries.
9. **Genre is metadata, not a schema boundary.** The database must support Shakira, John Summit, and other kinds of music without hardcoded genre exclusions.

## 3. MVP scope

### Included

- Consumer registration, login, logout, password reset, and account deletion
- Public user profiles
- Canonical music event pages
- Artist, venue, city, and genre catalog records
- Event search and discovery
- Event diary/log
- Half-star event ratings from 0.5 to 5
- Optional written event reviews
- Interested/watchlist
- User-created event lists
- User-to-user follows
- Likes on written reviews
- One-level comments on written reviews
- Activity feed and notifications inbox
- Missing-event requests
- Content reporting and staff moderation
- Django staff catalog administration

### Explicitly excluded from MVP

- Business, venue, promoter, or artist accounts
- Page claiming and verification
- Business dashboards or event-management portals
- Ticket sales or ticketing integrations
- Promoter ownership
- Venue or promoter ratings
- Separate “vibe” and “set” scores
- Per-artist or per-set reviews inside an event
- Direct community creation or editing of canonical events
- Automatic event scraping or third-party ingestion
- Recommendation machine learning
- Private messaging

## 4. Catalog model

### Event

An event is one identifiable music occurrence at a specific time and, when applicable, place.

Examples:

- `Shakira — Las Mujeres Ya No Lloran World Tour` at Madison Square Garden on a specific date
- `John Summit` at Savaya Bali on a specific date
- A named festival spanning multiple days
- A published livestream with a scheduled start time

Two performances with the same artist and venue on different dates are different events. Two legitimate events may also occur at the same venue on the same date, so venue and date must never form a uniqueness constraint.

Event types:

- concert
- dj_set
- club_night
- festival
- day_party
- livestream
- other

Event lifecycle:

- `draft`: staff is still preparing the record
- `published`: visible and usable
- `cancelled`: visible, marked cancelled, cannot be newly logged as attended
- `archived`: hidden from normal discovery but retained for existing references
- `merged`: duplicate redirected to a surviving canonical event

An event may have multiple artists. The lineup relationship stores billing order and a participation label such as headliner, support, guest, or performer. A back-to-back DJ appearance is represented by multiple artists attached to the same event; it does not create multiple user ratings.

### Artist

An artist is a canonical catalog identity such as a solo performer, DJ, band, group, or collaborative act.

Artists:

- do not have credentials;
- are not user roles;
- cannot claim or edit pages in MVP;
- may have aliases, genres, images, biography text, and links;
- appear on event lineups;
- are searchable and have read-only catalog pages.

### Venue

A venue is inert catalog metadata for a physical location. It is not a business account.

A venue may have a name, address, city, coordinates, timezone override, and an event history. Location fields may be incomplete. Online events do not require a venue.

### City and timezone

Cities are canonical reference rows. A venue belongs to a city when known.

An event stores an IANA timezone explicitly. It normally inherits the venue/city timezone when created, but the stored event timezone is the historical source of truth. Event times must not be interpreted using the viewer’s timezone.

## 5. Consumer behavior

### Accounts and profiles

A user has:

- unique immutable username for MVP;
- unique email;
- password;
- display name;
- avatar;
- biography;
- optional home city;
- joined date;
- account status;
- privacy setting for their diary and reviews.

Public profiles show:

- identity and biography;
- four favorite events;
- recent diary entries;
- reviews;
- lists;
- followers and following;
- derived statistics.

Initial profile statistics:

- Events attended
- Events rated
- Reviews written
- Artists seen
- Venues visited
- Lists created

Counts are derived from source data. Cached values may be added only if profiling proves necessary.

### Event diary

A user can log a published past or currently occurring event as attended.

Each user may have at most one diary entry per canonical event. An entry contains:

- event;
- user;
- attended date;
- optional rating;
- optional review body;
- visibility;
- timestamps;
- edited timestamp when applicable.

The event’s local start date is the default attended date. Staff corrections or event merges must preserve the user’s entry.

A rating or review automatically creates the diary entry if one does not exist. Removing a rating or review does not remove the attendance log unless the user explicitly removes the entry.

Rating rules:

- 0.5–5.0 in half-star increments;
- stored as an integer from 1–10 to avoid decimal ambiguity;
- optional;
- one current rating per user per event;
- editable;
- cancelled events cannot receive new attendance logs or ratings;
- the event aggregate uses one rating per user.

Written reviews:

- are optional;
- have a maximum length of 5,000 characters;
- can be edited;
- display an edited marker after publication changes;
- can receive likes, comments, and reports;
- can be removed independently while preserving the diary entry and rating.

Stars-only entries appear in rating aggregates and the user’s diary but do not create a comment thread or social review card.

### Interested/watchlist

Users can mark upcoming published events as interested. This is the equivalent of a Letterboxd watchlist.

- One interested record per user and event
- Automatically removed when the user logs the event
- Cancelled events remain visible in the list with their status
- Does not imply ticket ownership or attendance

### Lists

Users can create ordered or unranked lists of events.

A list has:

- title;
- optional description;
- public, followers-only, or private visibility;
- ranked/unranked mode;
- ordered event items;
- optional note per item.

An event can appear only once in a list. List positions are changed transactionally.

### Favorites

A user can select up to four favorite events. Favorites are ordered and appear prominently on the public profile.

### Following and activity

Users follow other users, not artists, venues, or businesses in MVP.

The home feed contains activity from followed users:

- new written reviews;
- event logs with ratings;
- published lists;
- list likes if implemented later.

The activity inbox contains:

- likes on the user’s review;
- comments on the user’s review;
- replies to the user’s comment;
- new followers.

Feed and inbox items are derived from their underlying records for MVP. A dedicated notification table records delivered/read state for inbox notifications.

### Likes and comments

MVP likes target written reviews only.

Comments:

- target one written review;
- allow one reply level;
- cannot be attached to stars-only diary entries;
- have a 2,000-character maximum;
- can be edited or soft-removed;
- can receive reports;
- cannot target a different review through their parent.

Separate, FK-backed tables are preferred over polymorphic target columns.

### Search and discovery

Global search groups results in this order:

1. Events
2. Artists
3. Venues
4. People
5. Lists

Event search can match:

- event title;
- artist name or alias;
- venue;
- city;
- date;
- genre.

Initial discovery shelves:

- Popular events this week
- Recently reviewed by friends
- Upcoming in the browsing city
- Highest-rated recent events
- Popular community lists

Home city is persistent profile identity. Browsing city is a temporary discovery filter and never silently changes the home city.

Popularity is based on app activity, not ticket sales. Aggregate ratings must show rating count, and the UI should avoid ranking an event as “highest rated” until it reaches a configurable minimum number of ratings.

### Catalog requests

When an event is missing, a user submits a structured request rather than creating a public catalog row.

Requested fields:

- event name;
- event date;
- artist name(s);
- venue/city;
- evidence URL;
- optional note.

Staff can approve, deny, merge duplicates, or request correction. Approval creates or links a canonical event. The requesting user receives a notification.

## 6. Screen inventory

### Primary navigation

Mobile-first bottom navigation:

- Home
- Search
- Activity
- Profile

The current dark, restrained, artwork-led visual direction can remain. Event posters and performance photography replace business-page branding.

### Required screens

1. Sign up, login, password reset
2. Home feed
3. City/discovery view
4. Global search
5. Search results
6. Event detail
7. Log/rate/review composer
8. Review detail and comments
9. Artist detail
10. Venue detail
11. Public user profile
12. Full event diary
13. Lists index, detail, and editor
14. Interested events
15. Activity inbox
16. Settings and account deletion
17. Missing-event request form

### Event page

The event page is the product’s most important catalog screen. It contains:

- poster/image;
- title;
- type;
- local date and time;
- venue and city, or online label;
- lineup;
- genres/tags;
- event status;
- aggregate rating and rating distribution;
- the viewer’s log/rating/review state;
- actions: log, rate, review, interested, add to list, report correction;
- popular and recent written reviews;
- friends who logged it.

## 7. Relational data model v2

The previous ERD must not be implemented as-is. It mixes account identity with artist and business catalog identity. The revised schema separates these concepts.

### Core tables

#### `user`

- `id` bigint PK
- `username` varchar, unique
- `username_normalized` varchar, unique
- `email` varchar, unique
- `email_normalized` varchar, unique
- `password`
- `display_name`
- `avatar_url` nullable
- `bio` nullable
- `home_city_id` nullable FK
- `status` enum: active, suspended, deleted
- `diary_visibility` enum: public, followers, private
- `created_at`, `updated_at`

Use a custom Django user model from the first migration. Django staff/superuser flags provide administration; `admin` is not a public account type.

#### `city`

- `id` bigint PK
- `name`
- `region` nullable
- `country_code`
- `timezone`
- unique normalized location key

#### `venue`

- `id` bigint PK
- `name`
- `slug` unique
- `city_id` nullable FK
- `address` nullable
- `latitude`, `longitude` nullable
- `timezone` nullable
- `status` enum: active, archived, merged
- `merged_into_id` nullable self-FK
- timestamps

#### `artist`

- `id` bigint PK
- `name`
- `slug` unique
- `artist_type` enum: solo, dj, band, group, collaborative, other
- `bio` nullable
- `image_url` nullable
- `country_code` nullable
- `status` enum: active, archived, merged
- `merged_into_id` nullable self-FK
- timestamps

Artist names are not globally unique.

#### `artist_alias`

- `id` bigint PK
- `artist_id` FK
- `name`
- `normalized_name`
- unique (`artist_id`, `normalized_name`)

#### `genre`

- `id` bigint PK
- `name`
- `slug` unique

#### `artist_genre`

- `artist_id` FK
- `genre_id` FK
- unique (`artist_id`, `genre_id`)

#### `event`

- `id` bigint PK
- `title`
- `slug` unique
- `event_type`
- `starts_at` datetime nullable
- `ends_at` datetime nullable
- `local_start_date` date
- `timezone`
- `venue_id` nullable FK
- `online_url` nullable
- `image_url` nullable
- `description` nullable
- `status`: draft, published, cancelled, archived, merged
- `merged_into_id` nullable self-FK
- `created_by_staff_id` nullable FK to user
- timestamps

Rules:

- physical events require a venue before publication;
- online events may omit venue and use `online_url`;
- `ends_at` must not precede `starts_at`;
- no venue/date uniqueness constraint;
- merged events cannot receive new writes;
- all reads of a merged event redirect to the survivor.

#### `event_artist`

- `id` bigint PK
- `event_id` FK
- `artist_id` FK
- `billing_order` integer nullable
- `participation_type`: headliner, support, guest, performer, host, other
- unique (`event_id`, `artist_id`, `participation_type`)

#### `event_genre`

- `event_id` FK
- `genre_id` FK
- unique (`event_id`, `genre_id`)

#### `diary_entry`

- `id` bigint PK
- `user_id` FK
- `event_id` FK
- `attended_on` date
- `rating_half_steps` tinyint nullable
- `review_body` text nullable
- `visibility`: public, followers, private
- `review_published_at` nullable
- `review_edited_at` nullable
- timestamps
- unique (`user_id`, `event_id`)

Database check: `rating_half_steps BETWEEN 1 AND 10`.

#### `interested_event`

- `user_id` FK
- `event_id` FK
- `created_at`
- unique (`user_id`, `event_id`)

#### `user_follow`

- `follower_id` FK
- `followed_id` FK
- `created_at`
- unique (`follower_id`, `followed_id`)
- check follower is not followed user

#### `review_like`

- `user_id` FK
- `diary_entry_id` FK
- `created_at`
- unique (`user_id`, `diary_entry_id`)

Application rule: the diary entry must contain a published review body.

#### `comment`

- `id` bigint PK
- `diary_entry_id` FK
- `author_id` FK
- `parent_id` nullable self-FK
- `body`
- `status`: visible, removed, hidden
- `edited_at` nullable
- timestamps

Application rules enforce one-level nesting and require parent and child to reference the same diary entry.

#### `event_list`

- `id` bigint PK
- `user_id` FK
- `title`
- `description` nullable
- `visibility`
- `is_ranked` boolean
- timestamps

#### `event_list_item`

- `id` bigint PK
- `list_id` FK
- `event_id` FK
- `position` integer
- `note` nullable
- `added_at`
- unique (`list_id`, `event_id`)
- unique (`list_id`, `position`)

#### `favorite_event`

- `user_id` FK
- `event_id` FK
- `position` tinyint
- unique (`user_id`, `event_id`)
- unique (`user_id`, `position`)
- check position between 1 and 4

#### `catalog_request`

- `id` bigint PK
- `requester_id` FK
- structured requested fields
- `evidence_url`
- `status`: pending, approved, denied, duplicate
- `resolved_event_id` nullable FK
- `reviewed_by_id` nullable FK
- `admin_reason` nullable
- timestamps

#### `notification`

- `id` bigint PK
- `recipient_id` FK
- `actor_id` nullable FK
- `notification_type`
- FK-backed nullable references for the supported MVP objects
- `read_at` nullable
- `created_at`

#### `report`

Use separate nullable FK targets with an exact-one-target check for the small MVP target set:

- `reporter_id` FK
- `reported_user_id` nullable FK
- `diary_entry_id` nullable FK
- `comment_id` nullable FK
- `reason_code`
- `details` nullable
- `status`: open, kept, removed
- `resolved_by_id` nullable FK
- `admin_reason` nullable
- timestamps

Do not use Django `GenericForeignKey` for integrity-sensitive social records.

### Important indexes

- `event(status, local_start_date)`
- `event(venue_id, local_start_date)`
- `event_artist(artist_id, event_id)`
- `diary_entry(user_id, attended_on)`
- `diary_entry(event_id, review_published_at)`
- `diary_entry(event_id, rating_half_steps)`
- `user_follow(followed_id, follower_id)`
- `comment(diary_entry_id, created_at)`
- `notification(recipient_id, read_at, created_at)`
- normalized artist aliases, venue names, event titles, and usernames

MySQL collation behavior must not be treated as a substitute for explicit normalized search/uniqueness fields.

### Deletion behavior

- User-owned social data: cascade or anonymize according to the final privacy policy.
- Catalog objects referenced by diary entries: protect from hard deletion.
- Duplicate artists, venues, and events: merge and redirect; never hard-delete referenced rows.
- Moderated reviews/comments: soft-remove to preserve discussion and audit history.
- Account deletion: revoke credentials immediately, then perform a transactionally safe erasure/anonymization job.

## 8. Backend architecture

Use a Django modular monolith with Django REST Framework.

Suggested Django apps:

```text
accounts      authentication, profiles, privacy
catalog       cities, venues, artists, genres, events, search
diary         logs, ratings, reviews, interested events, favorites
lists         event lists and ordering
social        follows, likes, comments, activity
moderation    reports and moderation actions
notifications inbox notifications
catalog_ops   missing-event requests, merges, future imports
```

Architecture rules:

- Business rules live in service functions, not views or serializers.
- Multi-row actions use `transaction.atomic()`.
- API serializers validate shape; services validate domain rules.
- QuerySets/selectors centralize feed and aggregate queries.
- Models use database constraints wherever MySQL can enforce the rule.
- Staff uses Django Admin first; a custom admin frontend is deferred.
- Background work may begin with Django management commands. Add Celery/Redis only when asynchronous workload justifies it.
- Store all system timestamps timezone-aware in UTC.
- Return event date/time plus IANA timezone to the frontend for correct local display.

### Initial API surface

```text
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/me
PATCH  /api/me

GET    /api/events
GET    /api/events/{slug}
PUT    /api/events/{id}/diary-entry
DELETE /api/events/{id}/diary-entry
PUT    /api/events/{id}/interested
DELETE /api/events/{id}/interested

GET    /api/artists/{slug}
GET    /api/venues/{slug}
GET    /api/search?q=

GET    /api/users/{username}
PUT    /api/users/{username}/follow
DELETE /api/users/{username}/follow

POST   /api/reviews/{diary_entry_id}/likes
DELETE /api/reviews/{diary_entry_id}/likes
GET    /api/reviews/{diary_entry_id}/comments
POST   /api/reviews/{diary_entry_id}/comments

GET    /api/lists
POST   /api/lists
GET    /api/lists/{id}
PATCH  /api/lists/{id}

GET    /api/feed
GET    /api/notifications
POST   /api/catalog-requests
POST   /api/reports
```

Use same-origin secure session cookies and CSRF protection for the web client unless a future native client creates a clear need for token authentication.

## 9. Frontend architecture

Use React written in JSX. Vite is the recommended build tool.

Suggested structure:

```text
frontend/src/
  api/
  app/
  components/
  features/
    accounts/
    activity/
    backend/catalog/
    diary/
    lists/
    social/
  pages/
  routes/
  styles/
```

Frontend rules:

- Keep server state behind one API client and query layer.
- Keep rating values as integer half-steps internally.
- URLs use durable slugs or IDs, never display names.
- Loading, empty, error, cancelled, archived, and merged states are designed states.
- Accessibility is required for star controls, dialogs, images, and keyboard navigation.
- The mobile layout is primary; desktop expands the layout rather than becoming a separate application.

## 10. MySQL and DataGrip

MySQL 8 is the application database. Django migrations are the only source of truth for schema changes.

DataGrip is a development and administration client. It may be used to:

- inspect schemas and query plans;
- review data;
- test read-only queries;
- troubleshoot migrations.

Schema changes made manually in DataGrip must not replace Django migrations.

Recommended development configuration:

- MySQL 8.x
- `utf8mb4`
- strict SQL mode
- timezone tables loaded
- separate development and test databases
- credentials supplied through environment variables

## 11. Data acquisition boundary

The data provider is deliberately unresolved.

MVP catalog population:

1. Staff creates events in Django Admin.
2. Users submit structured missing-event requests.
3. Staff resolves duplicates and publishes canonical records.
4. Seed fixtures provide enough events for development and testing.

Future ingestion must enter through a source-neutral import service:

```text
provider adapter
    -> normalized candidate
    -> match existing catalog
    -> create/update/flag conflict
    -> preserve source provenance
```

No provider-specific identifier belongs in the primary key of a core table. When ingestion is selected, add provider and entity-specific external-reference tables with unique `(provider, external_id)` constraints.

The provider decision must not block building accounts, catalog administration, diary behavior, reviews, lists, or social features.

## 12. Security and moderation

- Django password hashing and authentication primitives
- Secure, HttpOnly, SameSite cookies
- CSRF protection on mutating requests
- Rate limits on authentication, comments, likes, follows, requests, and reports
- Server-side visibility checks for every diary/list/feed query
- Sanitized plain text for reviews, comments, bios, and list notes
- File-type and size validation if direct image uploads are added
- Staff audit records for merges, removals, and catalog corrections
- No public exposure of private email, moderation reason, or provider raw payload

## 13. Delivery phases

### Phase 0 — foundation

- Django project and custom user model
- MySQL configuration and migrations
- React/JSX application shell
- Authentication and API conventions
- Seed city, venue, artist, and event fixtures

### Phase 1 — catalog and diary

- Staff catalog administration
- Event, artist, and venue pages
- Search
- Event logging
- Ratings and reviews
- Public profiles and diary

### Phase 2 — social identity

- Follows
- Feed
- Review likes
- Comments and replies
- Notifications
- Favorites

### Phase 3 — curation and discovery

- Interested events
- Lists
- City discovery
- Popularity shelves
- Catalog requests
- Moderation and duplicate merges

### Phase 4 — data acquisition

- Evaluate providers and legal/technical constraints
- Select ingestion strategy
- Build provider adapter and matching workflow
- Import in batches with auditability and rollback

## 14. Acceptance criteria for the first usable release

A release is usable when:

1. A consumer can create an account and public profile.
2. Staff can create Shakira at Madison Square Garden and John Summit at Savaya Bali as separate canonical events.
3. Each event has a venue, local date/time, timezone, type, image, and artist lineup.
4. A consumer can find either event by event, artist, venue, or city search.
5. A consumer can log, rate, and optionally review an event.
6. The log appears in the consumer’s chronological diary.
7. The rating contributes once to the event aggregate.
8. Another consumer can follow the reviewer, see the review in their feed, like it, and comment on it.
9. A consumer can mark an upcoming event as interested and add it to an event list.
10. Staff can merge a duplicate event without losing logs, ratings, reviews, likes, or comments.
11. No business, artist, venue, or promoter account is required anywhere in the flow.
12. All schema changes are reproducible through Django migrations.

## 15. Product decisions fixed by this specification

- Music event is the primary loggable and reviewable object.
- A rating describes the whole event experience.
- Artists and venues are catalog entities, not accounts.
- The public application has consumer accounts only.
- Staff permissions are not modeled as a public user type.
- There is one event rating scale, not separate set and vibe scores.
- Lists, interested events, and favorite events are core Letterboxd-style concepts.
- Data acquisition is deferred behind a future adapter boundary.
- JSX, Django, and MySQL form the initial runtime stack; DataGrip is a database client.

## 16. Open decisions that do not block foundation work

- Final product name and vocabulary for “log” versus “attended”
- Whether livestream viewing counts exactly like physical attendance
- Whether multi-day festivals are one event or one event per day
- Minimum rating count before ranked discovery
- Default diary visibility
- Whether past events can be requested and logged immediately after staff approval
- Image storage provider
- Production hosting and deployment platform
- Event data source and ingestion method
