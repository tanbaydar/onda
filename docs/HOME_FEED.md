[Onda](../README.md) / [Documentation](README.md) / Home feed

# The Home feed: a query, not a table

> **For** engineers who want the full design of Home. **Read time** 7 minutes.

Home shows what the followees of a person did, newest first.
Onda keeps no copy of that list. Each request builds one page from the source rows.

## In brief

- Home has no table. One `UNION ALL` of five branches builds each page.
- Privacy and event status are filters in each branch. They run before the union and before the limit.
- The order `(time, type, key)` is total. The cursor is the last key of the page.
- One request uses 4 SQL statements. A test fixes that number.
- The limit of the design: the first page reads all visible rows of the followees.

## What Home shows

| Type | Source table | Time of the activity | Key |
|---|---|---|---|
| `will_be_there` | `WILL_BE_THERE` | `created_at` | user and event |
| `review_like` | `REVIEW_LIKE` | `created_at` | user and review |
| `been` | `DIARY_ENTRY` with no rating | `created_at` | entry |
| `rated_been` | `DIARY_ENTRY` with a rating | `rated_at` | entry |
| `review` | `DIARY_ENTRY` with a review | `published_at` | entry |
| `favorite_event` | `FAVORITE_EVENT` | `added_at` | user and event |
| `favorite_artist` | `FAVORITE_ARTIST` | `added_at` | user and artist |

One Been entry gives one item. The type of the item follows the state of the entry.
A review does not add a second item for the same night.
A follow and a favorite venue are not in Home.

## The query

![Five branches read the rows of the followees. Each branch applies the same four filters. One UNION ALL joins them, sorts by time, type and key, and returns 21 rows.](assets/figures/home-feed.svg)

```sql
SELECT … FROM DIARY_ENTRY     WHERE user_id IN (followees) AND visible AND after_cursor
UNION ALL
SELECT … FROM REVIEW_LIKE     WHERE user_id IN (followees) AND review_visible AND after_cursor
UNION ALL
SELECT … FROM WILL_BE_THERE   WHERE user_id IN (followees) AND visible AND event_not_past AND after_cursor
UNION ALL
SELECT … FROM FAVORITE_EVENT  WHERE user_id IN (followees) AND visible AND after_cursor
UNION ALL
SELECT … FROM FAVORITE_ARTIST WHERE user_id IN (followees) AND after_cursor
ORDER BY activity_at DESC, activity_type DESC, source_key DESC
LIMIT 21;
```

Each branch returns the same 26 columns. A column that a branch does not use is `NULL`.
The source is [`backend/users/home_feed.py`](../backend/users/home_feed.py).

### Why the filters are in the branches

A filter after `LIMIT` has three faults:

- **A short page.** The database returns 21 rows, the filter removes 6, and the person gets 14.
- **A leak.** A short page tells the viewer that a hidden row is there.
- **A cursor that jumps.** The last key of the page can be a row that the viewer cannot see.

One case shows the care that this takes.
A followee can like the review of a private person that the viewer does not follow.
The like branch thus accepts a like only if the viewer can see the review.

### Why the order has three parts

Two activities can have the same time. An order by time alone then has equal rows.
A row on the page boundary can then show two times, or not at all.

- `activity_type` divides rows of different types.
- `source_key` divides rows of the same type. It is the ID of the row as text, and each ID has a fixed width of 20 digits.

A fixed width makes the text order equal to the number order: `…0042` is before `…0847`.

### The cursor

The cursor is the key of the last row on the page, as base64 text.
The next request sends it back, and each branch adds this filter:

```sql
    activity_at < :time
OR (activity_at = :time AND activity_type < :type)
OR (activity_at = :time AND activity_type = :type AND source_key < :key)
```

![Two new rows arrive between the request for page 1 and the request for page 2. With an offset, page 2 shows two rows again. With a keyset cursor, page 2 starts after the last key.](assets/figures/keyset.svg)

The server does not trust the cursor. It validates the length, the three parts, the time zone, the type and the key format.
A bad cursor gets `400`.
The query asks for 21 rows and returns 20. Row 21 is proof that a next page is there.

## What "a query, not a table" gives

| Event | Effect on the next request |
|---|---|
| Maya removes a rating and keeps the Been entry | The same item changes its type to `been` |
| Leo stops the follow | All items of Maya are gone |
| An event becomes `hidden` | Its items are gone. They come back if the event comes back |
| A followee likes a review that Leo cannot see | No item |
| New activity arrives while Leo reads | Page 2 does not repeat a row of page 1 |

No job repairs copies, because there are no copies.
Each row of this table has a test in [`test_home_api.py`](../backend/users/tests/test_home_api.py).

## How MySQL runs it

`EXPLAIN ANALYZE` on the benchmark database (MySQL 8.0.46) shows this plan:

1. Each branch starts at the primary key of `FOLLOW` and finds the 50 followees of the viewer.
2. For each followee, the branch does one index lookup on its source table.
3. `Union all materialize` puts 7,920 rows into a temporary table.
4. A sort with `limit input to 21 rows` keeps the top 21.

No branch does a table scan of a source table.
The reason is the order of the columns in the keys.
`WILL_BE_THERE`, `REVIEW_LIKE` and the favorite tables have a primary key that starts with `user_id`.
`DIARY_ENTRY` has the unique key `(user_id, event_id)`.
Thus one key gives the rule "no duplicate" and also the read path "all rows of this person".

## The cost and the limit

| | 2026-08-17 | 2026-11-27 |
|---|---|---|
| Query | Six branches (an earlier version) | Five branches (the version in this repository) |
| Machine | Apple M4 Pro, MySQL 9.6 | Cloud machine, 4 virtual CPUs at 2.1 GHz, MySQL 8.0.46 |
| p95 of page 1 | 45.9 ms | 87.6 ms |
| p95 of page 50 | 31.6 ms | 77.6 ms |
| Record | [`results.yaml`](../benchmarks/home-feed/results.yaml) | [`results-2026-11-27.yaml`](../benchmarks/home-feed/results-2026-11-27.yaml) |

**Method.**

- The script seeds 100,000 rows for 500 people. The viewer follows 50 of them.
- It sends 220 requests for each page, and it discards the first 20.
- The requests go one at a time through the Django test client, with the production settings. Thus the numbers do not include the network or Gunicorn.
- The 2026-11-27 column is the median of three runs.

**What the numbers show.** Page 50 is not slower than page 1. The cursor does not make a deep page more expensive.

**What the numbers do not show.** They are not a capacity test. No request ran at the same time as a second request.

**The limit.** For the first page, the database reads and sorts all visible rows of the followees.
That was 7,920 rows in the benchmark. The cost increases with the number of followees and with their activity.
[Decision 10](DECISIONS.md#10-build-home-when-a-person-reads-it) gives the condition that will make me change the design.

## Notifications are different

A notification is a stored row for each recipient, because each recipient has a separate read state.
A new Will Be There mark thus writes one row for each approved follower, in the same transaction.
The list of notifications uses a keyset cursor on `(created_at, id)`.

## Code and tests

| Subject | File |
|---|---|
| The query and the cursor | [`backend/users/home_feed.py`](../backend/users/home_feed.py) |
| The view | `home_feed` in [`backend/users/views.py`](../backend/users/views.py) |
| Order, statement count, privacy, hidden events | [`backend/users/tests/test_home_api.py`](../backend/users/tests/test_home_api.py) |
| The benchmark | [`benchmarks/home-feed/`](../benchmarks/home-feed/) |
| A read-only command that prints the Home of one person | `python manage.py show_home_feed <username>` |
