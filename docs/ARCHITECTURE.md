[Onda](../README.md) / [Documentation](README.md) / How Onda works

# How Onda works

> **For** engineers who want to understand the system. **Read time** 9 minutes.

This page follows one rating, from the tap of one person to the feed of a friend.
Each step names the principle that it uses.
The [decisions page](DECISIONS.md) gives the options that I did not select, and the cost of each decision.

## In brief

- Onda is one Django application and one MySQL database. The database has three layers, and the keys point one way.
- A write is one transaction. A row lock makes each "read, then write" sequence safe. The schema holds the invariants.
- The catalog comes from a source that Onda does not control. Onda stores each response first. A missing listing does not delete data.
- Home is a query, not a table. One `UNION ALL` reads the rows as they are now, in a total order.
- A request does not call the source. If the source stops, people continue to read and to write.

## The system in one figure

![Two paths share one database. The nightly path gets listings from the source and writes valid events to the catalog. The request path serves people from local data.](assets/figures/system-map.svg)

| Module | What it owns | Where it writes |
|---|---|---|
| `ingestion` | The nightly path: fetch, evidence, admission, reconciliation | Evidence and catalog |
| `catalog` | Reads of cities, venues, artists and events. Search | No table |
| `users` | Accounts, privacy, follows, diary, reviews, plans, favorites, notifications, Home | Social data |
| `frontend` | The React app | No table. It calls the API |

The modules are Python packages in one process. They are not network services.
Two rules keep the layers apart:

- Only `ingestion` writes to the catalog.
- A product table stores Onda IDs only. A source ID stops at an identity map.

## Step 1. The request is a contract

Maya goes to a show. The next morning she gives it four and a half stars.

```http
PUT /api/events/847/been/
Content-Type: application/json
X-CSRFToken: <value of the csrftoken cookie>

{"rating": 4.5}
```

The route names a thing: the Been entry of this person for event 847.
`PUT` sets the state of that thing, so the request is idempotent.
The first request creates the entry and returns `201`.
The same request again returns `200` and changes no row.
Thus a client can retry after a timeout, and no second entry is possible.

The status code tells the client engineer what to change.

| Status | Meaning | What to change |
|---|---|---|
| `400` | The shape is incorrect. `4.3` is not a half step. `"4.5"` is text, not a number. | The client code |
| `401` | The request has no session. | The person logs in |
| `404` | The event is unknown or hidden. The two cases look the same. | Nothing |
| `409` | The request is valid, but the state does not accept it. The event did not start. | Nothing. Time must go by |

![A request goes through four guards: the edge, the view, the service and the schema. Each guard stops one class of fault.](assets/figures/write-path.svg)

The [API reference](API.md) gives the contract of each route.

## Step 2. The write is one transaction

This is the service function, in a short form. The source is [`backend/users/services.py`](../backend/users/services.py).

```python
@transaction.atomic
def save_rating(*, user, event, rating):
    require_account_action(user)
    User.objects.select_for_update().get(pk=user.pk)           # row lock on the user
    entry = DiaryEntry.objects.visible_to(user).filter(user=user, event=event).first()
    now = timezone_now()
    if entry is None:
        if not event_is_loggable(event):                        # time at the venue
            raise EventNotStarted                               # the view returns 409
        return DiaryEntry.objects.create(user=user, event=event, rating=rating, rated_at=now), True
    entry.rating = rating                                       # same row, new value
    ...
    return entry, False
```

**The problem.** The function reads, and then it writes.
MySQL runs these transactions at the `READ COMMITTED` isolation level, the default of Django.
At that level, two requests at the same time can read "no entry", and then the two try to insert.

**The two guards.**

1. **A row lock.** `select_for_update` locks the row of the user. A second request from the same person waits until the first transaction commits. Different people do not wait for each other.
2. **A unique key.** `UNIQUE (user_id, event_id)` is the last guard. If code does not take the lock, the database refuses the second row.

The same lock protects a rule that no constraint can express.
"A person has a maximum of three favorite events" is a count of many rows.
The service locks the user row, counts, and then inserts.

| Invariant | Guard in the service | Guard in the schema |
|---|---|---|
| One Been entry for each person and event | Row lock, then lookup | Unique key `(user_id, event_id)` |
| A rating is a half step from 0.5 to 5.0 | The view validates a decimal value | Check constraint |
| `rating` and `rated_at` are set together | Service | Check constraint |
| A review has a rating | `save_review` refuses. `remove_rating` deletes the review in the same transaction | None. The rule uses two tables |
| A maximum of three favorites of each type | Row lock, then count | None. The rule uses many rows |
| No follow to yourself, no second follow | Service | Check constraint, composite primary key |
| One notification for each recipient, actor, type and target | Lookup, then insert | Two unique keys |
| An event with history stays | None | Foreign key with `RESTRICT` |

> [!NOTE]
> A rule that one row can prove goes into the schema.
> A rule that uses more than one row goes into one service function, in a transaction, behind a lock.

The [database reference](DATABASE.md) lists all constraints.

## Step 3. Where event 847 came from

Maya did not create event 847. A nightly run did.
The source is a website that Onda does not control.
Its listings change, disappear, and arrive with errors.
Four rules keep the catalog safe:

1. **Store first.** Onda stores each response before it parses the response. The stored responses are a log, and a later run can replay them.
2. **One listing, one transaction.** The venue, the artists, the event, the lineup and the IDs commit together. A listing that is not valid rolls back alone.
3. **Translate the identity.** An identity map changes the source ID into an Onda ID. A second pass on the same listing updates the same rows. Thus a replay is idempotent.
4. **Absence is evidence only in a complete snapshot.** If one page fails, Onda adds data and subtracts nothing. Three complete snapshots without a future event make that event hidden. Nothing deletes it.

The result for Maya: her plans and her favorites stay if the source drops a listing.
They show again if the listing comes back.
A past event does not change its status, so a rating is not at risk.

The [ingestion page](INGESTION.md) gives the full design, the limits and the failure table.

## Step 4. How Leo sees the rating

Leo follows Maya. He opens Home.
Onda has no feed table. `GET /api/me/home/` runs one query.

![Five branches read the rows of the followees. Each branch applies the same four filters. One UNION ALL joins them, sorts by time, type and key, and returns 21 rows.](assets/figures/home-feed.svg)

- **Each branch is an index lookup.** The keys of the five tables start with `user_id`. Thus "all rows of this followee" is a range in an index.
- **The filters run before the union.** A filter after the page limit can make a short page. It can also show that a private row is there.
- **The order is total.** Two activities can have the same time. The order `(time, type, key)` has no equal rows.
- **The cursor is the last key of the page.** New activity cannot move a page that Leo has.

Home reads the diary rows directly. Thus Leo sees the rating on his next request, and no worker copies it.
If Maya deletes the rating, or Leo stops the follow, the next request shows the change.

The [Home feed page](HOME_FEED.md) gives the query plan, the measured cost and the limit of this design.

## Step 5. Time belongs to the venue

An event has a local date and an optional local start time. Its city has an IANA time zone.
Onda changes "now" into the time of the venue before each decision.

| Decision | Rule in venue time |
|---|---|
| The event is upcoming | `event_date >= today` |
| The event is past | `event_date < today` |
| A person can add the event to Been | The time is at or after the start time. With no start time, the start of the day applies |
| A Will Be There mark is active | `today <= event_date` |

A live example: at 03:14 UTC on 2026-11-27 the public API listed events of 2026-11-26 as upcoming.
That was correct. The time in New York was 22:14 on 2026-11-26.
The time zone of the server and the time zone of the viewer have no effect.

## Step 6. One host runs it

![One host runs Caddy, Django and MySQL in containers. Host schedules start the nightly sync, the daily backup and a health probe. GitHub Actions deploys the commit that passed all checks.](assets/figures/deployment.svg)

- Caddy is the only container with public ports. MySQL is on an internal network with no published port.
- Each service container has a read-only file system and a user that is not root. It has no Linux capability that it does not use.
- A deploy uses the exact commit that passed 5 checks. The script makes a backup before the migration, and it does a health check after.

The [operations page](../infrastructure/README.md) gives the procedures.

## What continues when a part fails

| Failure | Effect on people | Recovery |
|---|---|---|
| The source is down, or its format changes | None. The catalog gets no new events | The next run that is successful |
| The sync stops in the middle of a run | None. Committed listings stay | The next run replays each response with the status `pending` |
| A second sync starts | None. It stops immediately | An advisory lock refuses the second run |
| One listing has an error | None. The other listings on the page continue | A rejection record keeps the reason |
| A container stops | The site is down for a short time | Docker starts the container again |
| A deploy is bad | The health check fails, and the deploy job fails | A revert commit goes through the same checks |
| The host fails | The site is down. Writes after the last backup can be lost | A person restores the last backup on a new host |

## Limits

- **One host.** The host is a single point of failure. The backup is daily.
- **One source.** If the source stops, the catalog does not get new events.
- **The Home query reads all visible rows of the followees.** Its cost increases with their activity. See [Home feed](HOME_FEED.md#the-cost-and-the-limit).
- **Search is a substring match.** It reads all rows of a table. The live catalog had 4,990 events on 2026-11-27.
- **Some error bodies are not JSON.** An unknown ID and a missing CSRF token get the HTML page of Django.

## Code map

| Subject | File |
|---|---|
| Routes | [`backend/config/urls.py`](../backend/config/urls.py), [`backend/users/been_urls.py`](../backend/users/been_urls.py) |
| Views of the product | [`backend/users/views.py`](../backend/users/views.py) |
| Service functions and transactions | [`backend/users/services.py`](../backend/users/services.py) |
| Models, constraints and visibility querysets | [`backend/users/models.py`](../backend/users/models.py), [`backend/catalog/models.py`](../backend/catalog/models.py) |
| The Home query | [`backend/users/home_feed.py`](../backend/users/home_feed.py) |
| The nightly path | [`backend/ingestion/`](../backend/ingestion/) |
| The fetch wrapper of the React app | [`frontend/src/api.js`](../frontend/src/api.js) |
