[Onda](../README.md) / [Documentation](README.md) / Database reference

# Database reference

> **For** engineers who read or write the data. **Use** this page as a lookup table.

Onda uses one MySQL 8.4 database with InnoDB tables.
Onda owns 25 tables. Django adds its own tables for sessions and migrations, and this page does not list them.
The facts on this page come from the models, and from `information_schema` after all migrations.

## In brief

- The tables are in three layers: evidence (4), catalog (9) and social data (12).
- Keys point one way, from social data to the catalog. No key points from social data to evidence.
- A rule that one row can prove is a constraint. This page lists all of them.
- Read through the shared querysets. They contain the privacy filter and the status filter.
- Write through the service functions. They contain the transaction and the lock.

## Contents

- [The three layers](#the-three-layers)
- [How to read safely](#how-to-read-safely) and [how to write safely](#how-to-write-safely)
- Tables: [evidence](#layer-1-evidence), [catalog](#layer-2-catalog), [social data](#layer-3-social-data)
- [Rules that the database cannot express](#rules-that-the-database-cannot-express)
- [Delete rules](#delete-rules), [indexes](#indexes-and-the-read-paths-that-they-serve), [stored and derived data](#stored-and-derived-data)

## The three layers

![The evidence layer has 4 tables, the catalog layer has 9 and the social layer has 12. Only the transformer writes from evidence to the catalog. Social tables refer to catalog rows. A source ID stops at the identity map.](assets/figures/data-layers.svg)

In the figures on this page, a short cross line is the "one" end of a relation. Three lines are the "many" end.

| Layer | Contents | Who writes |
|---|---|---|
| Evidence | Each response of the source, and each rejection | `ingestion` |
| Catalog | Cities, venues, artists, events, lineups, and the identity maps | `ingestion` |
| Social data | Accounts, follows, diary, reviews, likes, plans, favorites, notifications | `users` |

The isolation level is `READ COMMITTED`, the default of Django for MySQL.

## How to read safely

A query on a raw model can return a hidden event, an alias or a private row.
Use these entry points.

| You want | Use |
|---|---|
| Events that people can see | `_event_queryset()` in `catalog/views.py`. It removes hidden events and aliases |
| One event from an ID in a URL | `_canonical_event(event_id)`. It follows an alias, and it gives `404` for a hidden event |
| The Been entries that a viewer can see | `DiaryEntry.objects.visible_to(viewer)` |
| The ratings for a public average | `DiaryEntry.objects.for_aggregation()`. It includes private profiles, with no name |
| The ratings of the circle of a viewer | `DiaryEntry.objects.for_circle(viewer)` |
| The reviews that a viewer can see | `Review.objects.visible_to(viewer)` |
| The reviews for the public section of an event | `Review.objects.for_public_section()` |
| The plans that are active now | `WillBeThere.objects.active_at(now)`, `.visible_to(viewer, now)` |
| The profiles that show their content to a viewer | `User.objects.profile_content_visible_to(viewer)` |
| The viewer for a privacy decision | `effective_visibility_viewer(request.user)` |

## How to write safely

Change state only through these functions in `users/services.py`.
Each function is one transaction.

| Change | Function | Row that it locks | Conflict that it raises |
|---|---|---|---|
| Add or change a rating | `save_rating` | The user | `EventNotStarted` |
| Remove a rating | `remove_rating` | The Been entry | None. It also deletes the review |
| Remove a Been entry | `remove_entry` | The Been entry | None |
| Add or change a review | `save_review` | The Been entry | `ReviewRequiresRating` |
| Delete a review | `delete_review` | The review | None |
| Like a review | `like_review` | The review | `ReviewLikeConflict` |
| Add a plan | `save_will_be_there` | None. The primary key is the guard | `WillBeThereExpired` |
| Add a favorite | `save_favorite` | The user | `FavoriteLimitReached` |
| Follow a person | `follow_user` | The followee | `FollowConflict` |
| Answer a follow request | `accept_follow_request`, `decline_follow_request` | The user | None |
| Change privacy | `change_privacy` | The user | None |
| Count an attempt for a rate limit | `consume_rate_limit` in `users/rate_limits.py` | The counter row | `RateLimitExceeded` |

`like_review` and `save_will_be_there` also write the notifications, in the same transaction.
Each function writes a notification only for a recipient who has none from that actor for that review or event.
Thus a like or a plan that a person removes and adds again writes no second notification.
No key in the schema enforces this rule. The service is the only guard.

## Layer 1. Evidence

![One seed has many stored responses. One run has many stored responses. One stored response has many rejection records.](assets/figures/er-evidence.svg)

| Table | One row is | Columns | Keys and checks |
|---|---|---|---|
| `TRACKED_SOURCE_PAGE` | One city on the source (a seed) | `id`, `source`, `area_ref`, `label`, `active`, `last_synced_at`, `last_success_at` | Unique `(source, area_ref)` |
| `SYNC_RUN` | One run of the sync command | `id`, `run_type`, `status`, `started_at`, `finished_at`, `seeds_attempted`, `seeds_failed`, `events_upserted`, `events_quarantined`, `events_dropped`, `error_summary` | Check: `run_type` is `nightly`, `backfill` or `replay`. Check: `status` is `running`, `completed` or `crashed` |
| `RAW_INGEST` | One stored response for one page | `id`, `seed_id`, `run_id`, `window_start`, `window_end`, `page_number`, `page_size`, `response_body`, `http_status`, `fetched_at`, `processing_status` | Check: `processing_status` is `pending`, `processed` or `failed` |
| `REJECTED_INGEST` | One listing that Onda did not admit | `id`, `raw_ingest_id`, `entity_index`, `entity_ref`, `reason`, `detail`, `rejected_at` | Unique `(raw_ingest_id, entity_index)`. Check on `reason` |

- `response_body` is text, not JSON. Thus a body that is not JSON stays as it arrived.
- `events_upserted` counts admitted listings. It is not a count of new events, because a listing can update a row.

## Layer 2. Catalog

![A city has many venues, a venue has many events, and an event has many lineup rows. An artist has many lineup rows. Each of the four entities has many identity rows.](assets/figures/er-catalog.svg)

| Table | One row is | Columns | Keys and checks |
|---|---|---|---|
| `CITY` | One city | `id`, `name`, `region_code`, `region_name`, `country_code`, `timezone` | Unique `(country_code, region_code, name)` |
| `VENUE` | One venue | `id`, `name`, `city_id` | |
| `ARTIST` | One artist | `id`, `name`, `image_url` | |
| `EVENT` | One event | `id`, `title`, `event_date`, `start_time`, `venue_id`, `cover_image_url`, `status`, `canonical_event_id` | Check: `status` is `active`, `unverified` or `hidden` |
| `EVENT_ARTIST` | One artist in one lineup | `id`, `event_id`, `artist_id`, `position` | Unique `(event_id, artist_id)`. Unique `(event_id, position)` |
| `EVENT_IDENTITY` | One source ID of one event | `id`, `event_id`, `source`, `source_id`, `last_seen_at`, `misses` | Unique `(source, source_id)`. Unique `(event_id, source)` |
| `VENUE_IDENTITY`, `ARTIST_IDENTITY`, `CITY_IDENTITY` | One source ID of one entity | `id`, the entity ID, `source`, `source_id` | The same two unique keys |

- `event_date` and `start_time` are local values at the venue. `CITY.timezone` is an IANA name, for example `America/New_York`.
- `canonical_event_id` is `NULL` for a normal row. An alias row points to the first row of the same real event.
- A catalog table has no source ID column. Only the identity maps have one.
- The foreign key cannot make sure that an event has an artist. The transformer does: it admits an event only with one artist or more.

## Layer 3. Social data

![One user has many follows, Been entries, plans, favorites, notifications and codes. One Been entry has zero or one review. One review has many likes. Been entries, plans and favorites refer to catalog rows.](assets/figures/er-social.svg)

| Table | One row is | Columns | Keys and checks |
|---|---|---|---|
| `ONDA_USER` | One account | `id`, `email`, `email_verified_at`, `username`, `recovery_username`, `display_name`, `bio`, `avatar`, `home_city_id`, `is_private`, `status`, `deletion_due_at`, `created_at`, and the account columns of Django | Unique `email`. Unique `username`. Check: an `active` account has a username. Check: only a `pending_deletion` account has `deletion_due_at` |
| `ACCOUNT_CODE` | One code for one purpose | `id`, `user_id`, `purpose`, `code_hash`, `sent_at`, `expires_at`, `failed_attempts`, `consumed_at` | Unique `(user_id, purpose)`. Check: `failed_attempts <= 5`. Check: `expires_at > sent_at` |
| `REQUEST_THROTTLE` | One counter of a rate limit | `id`, `scope`, `key_hash`, `window_started_at`, `count`, `updated_at` | Unique `(scope, key_hash)`. Check: `count >= 1` |
| `FOLLOW` | One follow | `follower_id`, `followee_id`, `status`, `created_at`, `approved_at` | Primary key `(follower_id, followee_id)`. Check: not to yourself. Check: `approved` has `approved_at`, and `pending` does not |
| `DIARY_ENTRY` | One Been entry | `id`, `user_id`, `event_id`, `rating`, `rated_at`, `created_at` | Unique `(user_id, event_id)`. Check: `rating` is `NULL` or a half step from 0.5 to 5.0. Check: `rating` and `rated_at` are set together |
| `REVIEW` | One review | `id`, `entry_id`, `body`, `published_at` | Unique `entry_id`. Check: `body` has a visible character |
| `REVIEW_LIKE` | One like | `user_id`, `review_id`, `created_at` | Primary key `(user_id, review_id)` |
| `WILL_BE_THERE` | One plan | `user_id`, `event_id`, `created_at` | Primary key `(user_id, event_id)` |
| `FAVORITE_EVENT`, `FAVORITE_ARTIST`, `FAVORITE_VENUE` | One favorite | `user_id`, the target ID, `added_at` | Primary key `(user_id, target ID)` |
| `NOTIFICATION` | One notification for one recipient | `id`, `recipient_id`, `actor_id`, `type`, `review_id`, `event_id`, `created_at`, `read_at` | Check: the actor is not the recipient. Check: `review_like` has a review, `will_be_there` has an event, and the other types have none |

- A composite primary key makes a second row for the same pair impossible.
- `DIARY_ENTRY` has a surrogate `id`, because `REVIEW.entry_id` refers to one row.
- `REQUEST_THROTTLE` has no foreign key to a user. `key_hash` is an HMAC of the address or of the account name.
- `WILL_BE_THERE` has no column for an end time. The read derives "active" from the date of the event at the venue.

## Rules that the database cannot express

These rules use more than one row. One service function enforces each rule, in a transaction.

| Rule | Function |
|---|---|
| A new Been entry is possible only after the start of the event at the venue | `save_rating` |
| A review has a rating. The removal of a rating deletes the review | `save_review`, `remove_rating` |
| A person has a maximum of 3 favorites of each type | `save_favorite` |
| A plan is possible only until the end of the day of the event at the venue | `save_will_be_there` |
| A follow to a private profile starts as `pending` | `follow_user` |
| A change from private to public approves all open requests | `change_privacy` |
| A person cannot like their own review | `like_review` |

## Delete rules

MySQL shows `RESTRICT` as `NO ACTION`. In InnoDB the two do the same: the delete fails immediately.

| If you delete | These rows go too (`CASCADE`) | The delete fails while these rows are there (`RESTRICT`) |
|---|---|---|
| A user | Codes, follows, Been entries, likes, plans, favorites, notifications | |
| A Been entry | Its review | |
| A review | Its likes and its notifications | |
| An event | Its lineup rows and its identity rows | Been entries, plans, favorites, notifications, alias rows |
| An artist | Its identity rows | Lineup rows, favorites |
| A venue | Its identity rows | Events, favorites |
| A city | Its identity rows | Venues, the home city of a user |
| A seed or a run | | Stored responses |
| A stored response | | Rejection records |

Django applies `on_delete=CASCADE` in Python and leaves the key in MySQL with no action.
The migrations add the `CASCADE` action to the keys in the left column, and tests delete rows with direct SQL to prove it.
One key is different: `NOTIFICATION.event_id` cascades in Django only.

No application code deletes an event. The answer to a missing event is a status, not a delete.

## Indexes and the read paths that they serve

| Index | Read path |
|---|---|
| `EVENT (status, event_date)` | Upcoming and past lists of visible events |
| `EVENT (venue_id, event_date)` | The events of one venue |
| `FOLLOW` primary key `(follower_id, followee_id)` | The followees of a viewer. Each branch of Home starts here |
| `FOLLOW (followee_id, status)` | Follower counts, open requests, the privacy filter |
| `DIARY_ENTRY (user_id, event_id)` | The Been entries of one person. The Home branch |
| Primary keys that start with `user_id` | The plans, the likes and the favorites of one person. The Home branches |
| `NOTIFICATION (recipient_id, created_at)` | The list of notifications in keyset order |
| `NOTIFICATION (recipient_id, read_at)` | The unread count, and "read all" |
| `RAW_INGEST (run_id)`, `(seed_id, fetched_at)` | The rows of one run. The history of one seed |
| `REQUEST_THROTTLE (updated_at)` | The removal of old counters |

## Stored and derived data

| Subject | Stored | Derived on each read |
|---|---|---|
| Event status | `EVENT.status` and the miss counter | If a query shows the event |
| A plan | The pair and its time | If the plan is active |
| A follow | The pair, the status and the times | If a viewer can see the content |
| The rating of an event | Each rating | The count, the average and the distribution |
| Home | The source rows only | The feed and its cursor |
| Notifications | One row for each recipient | Nothing. Each row has its own read state |
| Recent searches | Nothing on the server. The browser keeps them | |

A value that Onda can derive is not stored. Thus no copy can be old.

## How to do a check of the schema

1. Make sure that the models and the migrations agree.

   ```bash
   python backend/manage.py makemigrations --check --dry-run
   ```

2. Run the tests. They use a MySQL database.

   ```bash
   python backend/manage.py test
   ```

3. Read the delete action of each foreign key.

   ```sql
   SELECT TABLE_NAME, REFERENCED_TABLE_NAME, DELETE_RULE
   FROM information_schema.REFERENTIAL_CONSTRAINTS
   WHERE CONSTRAINT_SCHEMA = DATABASE();
   ```

## Source files

| Layer | Models | Migrations |
|---|---|---|
| Evidence | [`backend/ingestion/models.py`](../backend/ingestion/models.py) | [`backend/ingestion/migrations/`](../backend/ingestion/migrations/) |
| Catalog | [`backend/catalog/models.py`](../backend/catalog/models.py) | [`backend/catalog/migrations/`](../backend/catalog/migrations/) |
| Social data | [`backend/users/models.py`](../backend/users/models.py) | [`backend/users/migrations/`](../backend/users/migrations/) |
