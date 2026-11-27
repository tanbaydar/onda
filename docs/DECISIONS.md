[Onda](../README.md) / [Documentation](README.md) / Decisions

# Design decisions

> **For** engineers who want the reasons. **Read time** 12 minutes, or 1 minute for the table.

Each record gives the problem, the options, the decision, the reasons, the cost, and the condition that changes the decision.
The records for data correctness come first. The record for tools comes last, on purpose.

## In brief

| # | Decision | Principle |
|---|---|---|
| [1](#1-one-application-and-one-database) | One application and one database | An invariant must be in one transaction boundary |
| [2](#2-store-each-response-before-interpretation) | Store each response before interpretation | A durable log comes first |
| [3](#3-one-transaction-for-each-listing) | One transaction for each listing | Atomicity sets the size of a failure |
| [4](#4-source-ids-stop-at-an-identity-map) | Source IDs stop at an identity map | Stable identity makes replay idempotent |
| [5](#5-a-miss-counts-only-in-a-complete-snapshot) | A miss counts only in a complete snapshot | Negative inference uses complete data only |
| [6](#6-hide-an-event-do-not-delete-it) | Hide an event, do not delete it | A state that you can reverse is safer than a delete |
| [7](#7-bound-each-fault-at-the-network-boundary) | Bound each fault at the network boundary | Timeout, limited retry, budget, mutual exclusion |
| [8](#8-each-invariant-at-the-lowest-layer-that-can-enforce-it) | Each invariant at the lowest layer that can enforce it | The schema is the guard that all writers share |
| [9](#9-a-row-lock-for-each-read-then-write-sequence) | A row lock for each read-then-write sequence | Isolation |
| [10](#10-build-home-when-a-person-reads-it) | Build Home when a person reads it | Derive, do not copy |
| [11](#11-a-keyset-cursor-on-a-total-order) | A keyset cursor on a total order | Pages stay stable while rows arrive |
| [12](#12-idempotent-methods-and-one-meaning-for-each-status-code) | Idempotent methods and one meaning for each status code | A retry is a normal event |
| [13](#13-a-session-cookie-and-a-csrf-token) | A session cookie and a CSRF token | The mechanism follows the threat model |
| [14](#14-time-belongs-to-the-venue) | Time belongs to the venue | A civil time is not an instant |
| [15](#15-one-host-with-the-safety-steps-of-a-larger-system) | One host, with the safety steps of a larger system | Operations in proportion to the load |
| [16](#16-tools-that-i-know) | Tools that I know | Put the risk in the problem, not in the tools |

## Data from a source that I do not control

### 1. One application and one database

**Problem.** Product rules use more than one table.
A review must have a rating. A change of privacy must approve the open requests in the same step.
A diary row must refer to an event that is there.

**Options.**

- Three services with three databases. Each service scales alone. But a rule that uses two services then makes a distributed transaction or a saga necessary, and each call can time out.
- One process and one database, with module boundaries in the code.

**Decision.** One process and one database. The dependencies go one way: `ingestion` writes the catalog, and `users` reads it by Onda ID.

**Why.** One ACID transaction covers each rule. A foreign key connects each diary row to its event. No measured load makes separate scale necessary.

**Cost.** One failure domain. One slow query can make all requests slow.

**Change it when** the nightly path and the requests compete for the database, or a second team owns a module.
The catalog can move first, because only one module writes it.

### 2. Store each response before interpretation

**Problem.** A parser can have a defect. The source can send a new shape. The process can stop between the fetch and the write.

**Options.**

- Parse in memory and store only the result. The input is then gone, and nobody can repeat the conclusion.
- Store the response first. Then process the stored copy.

**Decision.** The runner stores each final fetch result with the status `pending`. It also stores a transport failure.
Each run processes all rows that have the status `pending`.

**Why.** The table is a write-ahead log for the catalog.
After a crash, the next run continues from the stored responses.
After a correction of the parser, a replay gives the corrected result.
The table also divides "what arrived" from "what Onda concluded".

**Cost.** Storage. Two limits bound it: 2 MiB for each response and 100 MiB for each run. The client refuses a larger response, and Onda does not store it.

**Change it when** the evidence is the largest part of the database. Then old response bodies can move to object storage.

### 3. One transaction for each listing

**Problem.** One page has 20 listings. One of them has no artist, or a date that Onda cannot read.

**Options.**

- One transaction for the page. One bad listing then rolls back 19 good listings.
- No transaction. A failure in the middle then leaves an event with no lineup.
- One transaction for each listing.

**Decision.** One transaction for each listing. The venue, the artists, the event, the lineup and the identity rows commit together.
On a rejection the transaction rolls back. Then a second small transaction writes the rejection record.

**Why.** Atomicity sets the size of a failure to one listing. The catalog cannot contain a part of an event.
Onda does not repair data. It does not invent an artist, and it does not correct a date.

**Cost.** Approximately 20 commits for each page, not one. The nightly path has the time.

**Change it when** the run time of the nightly path becomes important. Then savepoints in one page transaction give the same isolation with fewer commits.

### 4. Source IDs stop at an identity map

**Problem.** The source owns its IDs. A name is not an identity: two artists can have the same name, and a venue can change its name.
A second source will have different IDs for the same event.

**Options.**

- Use the source ID as the key in product tables. This is the shortest path, and it connects all user data to one source.
- Use a natural key, for example name and date. Such a key is not stable.
- Give each entity an Onda ID, and translate source IDs in separate tables.

**Decision.** Four identity maps, for cities, venues, artists and events. Each has a unique key on `(source, source_id)`.

**Why.** A replay is idempotent, because the same source ID finds the same row.
A new name is an update of one column. A product table does not change when the source changes.
A second source can map to the same event.

**Cost.** One more lookup for each entity in the nightly path.
The schema does not match two sources automatically. That match is separate work, and it is not built.

### 5. A miss counts only in a complete snapshot

**Problem.** A response does not contain an event. That fact has three possible causes.
The source removed the event, or a page failed, or the pages moved during the fetch.

**Options.**

- Delete an event when a run does not see it. This is easy, and it destroys data on a network error.
- Count a miss on each run.
- Count a miss only when Onda can prove that the snapshot is complete.

**Decision.** A snapshot is complete only if [five conditions](INGESTION.md#rule-4-when-is-a-snapshot-complete) are true. Only a nightly run counts misses.
An incomplete run can add events. It cannot subtract.

**Why.** An error on my side must not look like a change at the source.
The rule is not symmetric, on purpose. A false "present" costs one old row for a short time.
A false "absent" removes a real event from the view of all people.

**Cost.** A canceled event stays visible for a maximum of three nights.

**Change it when** the source gives a field for cancellation. A positive signal is better than an inference.

### 6. Hide an event, do not delete it

**Problem.** Onda concludes that a future event disappeared. People have plans and favorites on that event. The conclusion can be incorrect.

**Options.**

- Delete the event and all rows that refer to it. Nobody can reverse this.
- Keep the event, and give it a status.

**Decision.** `EVENT.status` is `active`, `unverified` or `hidden`. A hidden event answers as an unknown event.
A foreign key with `RESTRICT` stops a delete of an event that has user data. One later sight of the event makes it `active` again.

**Why.** If the conclusion is incorrect, the next run corrects it, and no data is lost.
The mechanism is a failure detector with a threshold: one miss gives a suspect, three misses give a conclusion.

**Cost.** Each read path must filter by status. Two shared querysets contain the filter, and tests do a check of each path.

### 7. Bound each fault at the network boundary

**Problem.** The fetch crosses a network to a server that I do not control.

**Decision.** Each fault has a limit.

| Fault | Limit |
|---|---|
| A slow server | 20 seconds for each attempt |
| A temporary error | A maximum of 3 attempts, and only for status 408, 429, 500, 502, 503 and 504 |
| Retries at the same moment | The delay from `Retry-After` if the server sends it. If not, exponential backoff with full jitter |
| Too many requests | 1.5 seconds between pages, and a budget of 1,000 attempts for each run |
| A very large body | 2 MiB for each response |
| A redirect to a different host | The client accepts one HTTPS origin only |
| Two runs at the same time | A MySQL advisory lock that does not wait. MySQL releases it if the connection stops |

**Why.** Each limit changes a fault with no bound into a fault with a known maximum cost.

**Cost.** A long failure of the source gives no new data. I accept that, because the request path does not use the source.

## Data that people write

### 8. Each invariant at the lowest layer that can enforce it

**Problem.** A rule in a view is lost when a second code path writes the same table.

**Decision.**

- A rule that one row can prove is a constraint: a check, a unique key, a composite primary key or a foreign key.
- A rule that uses more than one row is in one service function.
- A view validates the shape of the request and no more.

**Why.** The database is the one component that all writers share.

**A detail that is easy to miss.** Django applies `on_delete=CASCADE` in Python. The foreign key in MySQL then has no delete action.
Migrations in this repository add `ON DELETE CASCADE` to the rows that a user owns, and tests delete rows with direct SQL to prove it.
Thus a delete outside Django obeys the same rule.

**Cost.** A change of a constraint is a migration. The message of a constraint error is not friendly, so the service does its check first and gives a clear `409`.

### 9. A row lock for each read-then-write sequence

**Problem.** "Read the entry, then insert" is a race at the `READ COMMITTED` level. Two requests can read "no entry".

**Options.**

- Use the `SERIALIZABLE` level for all transactions. It is correct, but each transaction can then fail and must run again.
- Use a unique key and a retry. This is sufficient for "one row". It cannot express "a maximum of three rows".
- Lock one parent row.

**Decision.** `SELECT … FOR UPDATE` on the row of the user is a mutex for one person. The unique keys stay as the last guard.
A like is the exception: its primary key is sufficient. The service inserts, and a second like becomes `409`.

**Why.** The lock is narrow. The rule and its lock are in one function.

**Cost.** The writes of one person go in sequence. A follow locks the row of the followee, so many follows to one popular person wait in a line.

**Change it when** lock waits on one row show in the measurements.

### 10. Build Home when a person reads it

**Problem.** Home shows what the followees of a person did, newest first.

**Options.**

- **Fan-out on write.** Copy each action into a feed row for each follower. A read is then one index range. But each write costs one row for each follower. An unfollow, a delete, a change of privacy and a hidden event then all make a repair of copies necessary.
- **Fan-out on read.** Keep no copies. Build the page from the source rows on each request.

**Decision.** Fan-out on read. One `UNION ALL` of five branches reads the rows as they are now.

**Why.** A copy can be old. A source row cannot.
A delete, an unfollow and a change of privacy apply on the next request, with no repair work.
No queue and no worker are necessary.

**Cost.** The read is heavier. For the first page the query reads all visible rows of the followees.
With 50 followees and 7,920 visible rows, the p95 is 88 ms on a cloud machine with 4 virtual CPUs.
[Home feed](HOME_FEED.md) has the plan and the method.

**One exception.** A notification is a stored row for each recipient, because each recipient has a separate read state.

**Change it when** Home is the slowest request in production. Then I will measure a limit in each branch against a stored feed for viewers with many followees.

### 11. A keyset cursor on a total order

**Problem.** New rows arrive at the top while a person reads the feed.
With `OFFSET`, each new row moves all rows down, so the next page repeats rows.
`OFFSET n` also reads `n` rows and discards them.

**Decision.** The cursor is the last key of the page: `(time, type, key)`.
The next page is "all rows below that key".
The client gets the cursor as text and must not read it. The server validates each part and returns `400` for a bad cursor.

**Why a total order.** Two activities can have the same time. If the order has equal rows, a row on the page boundary can show two times or not at all.
The type and a key with a fixed width make each row different.

**Where page numbers stay.** Catalog lists use page numbers. Their order is `(date, ID)`, the data changes one time each night, and people go directly to a page.

**Cost.** No "go to page 7", and no total count.

## The contract with the client

### 12. Idempotent methods and one meaning for each status code

**Problem.** A mobile network drops responses. A client that does not know if a write arrived sends it again.

**Decision.**

- A write that sets state is `PUT`. The first request returns `201`, and the same request again returns `200`.
- A `DELETE` does not make a second change. A plan and a favorite return `204` each time.
- A like is `POST`. A second like returns `409` and adds no row.
- Each status code has one meaning in all routes.

| Status | The one meaning |
|---|---|
| `400` | The shape of the request is incorrect. The client code must change |
| `401` | No session |
| `403` | The viewer is known and is not permitted |
| `404` | Unknown, hidden or not visible. The three cases look the same |
| `409` | The request is valid, and the state does not accept it |
| `429` | Too many attempts. Wait |

**Why.** A `400` is a defect that an engineer corrects. A `409` is a message that the app can show to a person.
A `404` for a hidden event gives no sign that the row is there.

**Cost.** Two JSON shapes for errors are in use, and some `404` bodies are HTML. The [API reference](API.md#errors) lists them.

**Change it when** a second client arrives. Then one error shape and a version in the path become necessary.

### 13. A session cookie and a CSRF token

**Problem.** The only client is the React app on the same origin.

**Options.**

- A token in browser storage. Script can read it, so one script injection defect gives the token away. To end a token early, the server must keep a list.
- A session cookie that script cannot read.

**Decision.** A session cookie with `HttpOnly`, `Secure` and `SameSite=Lax`, for 7 days.
Each request that changes state must also send the CSRF token in a header.

**Why.** The browser keeps the secret away from script. The server can end a session: a password reset deletes all sessions of the account.

**Cost.** A cookie makes CSRF protection necessary. This design does not serve third-party clients.

### 14. Time belongs to the venue

**Problem.** "Is the event today?" has three different answers: in Boston, on a server in UTC, and in the browser of a person on a trip.

**Decision.** An event stores a local date and an optional local start time. A city stores an IANA time zone.
Each rule changes "now" into venue time first.

**Why.** An event is a civil time at a place. All viewers get the same answer.

**Cost.** A query for many cities has one date condition for each city. Today there are two cities.

## Operations and tools

### 15. One host, with the safety steps of a larger system

**Problem.** The load is small. The data of real people is not small.

**Decision.** One EC2 host with Docker Compose. The safety steps stay:

- The deploy job uses the exact commit that passed all checks, and it accepts a fast-forward only.
- The script makes a backup and tests it before each migration. A health check must pass after.
- Deploys run one at a time. Nothing cancels a deploy in the middle.
- Images and CI actions use fixed digests.
- A monthly job restores a backup into an empty database and does a check of each table.

**Why.** The cost and the effort stay in proportion to the load. A backup is proof only after a restore.

**Cost.** One host is a single point of failure. A restore is manual. The writes after the last backup can be lost.

**Change it when** one hour of downtime has a real cost. Then a managed database with point-in-time recovery is the first step.

### 16. Tools that I know

I selected tools that I knew well. Thus the risk was in the problem and not in the tools.

| Tool | Reason |
|---|---|
| Python and Django | Python is my strongest language. Django has the ORM, the migrations, the sessions and the CSRF protection that a relational application uses |
| Plain JSON views | One client and 46 routes. Plain views keep each status code explicit, with one less dependency |
| MySQL | I knew its locks and its constraints best |
| React and Vite | I knew React. One JSON contract divides the app from the server, so each side has its tests |
| Docker Compose and Caddy | Cost and effort in proportion to the load. Caddy gets and renews the TLS certificates |
| A host schedule | One nightly job does not make a queue and a worker necessary |

**Cost.** Two parts are specific to MySQL: the advisory lock, and the migrations that set the delete actions.
A move to PostgreSQL changes these two parts.
