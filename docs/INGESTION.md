[Onda](../README.md) / [Documentation](README.md) / Ingestion

# Ingestion: trust at a network boundary

> **For** engineers who want the full design of the nightly path. **Read time** 8 minutes.

Onda builds its catalog from event listings on a website that it does not control.
This page shows how a listing becomes a catalog event, and when Onda refuses to change the catalog.

## In brief

- The request path does not use the source. Only a scheduled command does.
- Onda stores each response before it parses the response.
- Each listing is one transaction. A bad listing gives a rejection record and no other change.
- A source ID maps to an Onda ID. Thus a replay does not make duplicates.
- An absent event is a miss only in a complete snapshot. Three misses hide a future event. Nothing deletes it.

## Why the source gets this care

Letterboxd, a film diary, gets its film data from one database, [TMDB](https://letterboxd.com/about/film-data/).
Live music has no equivalent: no one source is complete and has authority.
Resident Advisor was the best source that I found for the first version.
Its listings have five properties that make a direct connection to the product unsafe:

- An event can change or disappear.
- A request for one page can fail, and the other pages can be successful.
- The IDs belong to the source.
- A listing can be successful as a response and incomplete as an event.
- The interface is a web interface. It is not a contract with Onda.

## One run

![The client fetches a page and Onda stores the response before it parses it. Each listing goes through its own transaction. After the last page, Onda counts misses only if the snapshot is complete.](assets/figures/ingestion-pipeline.svg)

1. A host schedule starts the command `manage.py sync_ra` each night.
2. The runner takes the advisory lock `onda_sync_ra`. If a different run has the lock, the command stops with exit code 2 and writes nothing.
3. For each seed, the client fetches the listings of the next 30 days. It gets 20 listings for each page, one page at a time.
4. The runner stores each result in `RAW_INGEST` with the status `pending`.
5. The transformer processes each `pending` row. This includes rows from an earlier run that stopped.
6. For each seed, the runner tests the completeness conditions. If they pass in a nightly run, the reconciler counts the misses.
7. The runner writes the counters to `SYNC_RUN` and releases the lock.

The command stops with exit code 1 if a seed failed or if the run admitted no listing.
Thus the schedule log shows a bad run without a read of the database.

## Rule 1. Store first

A row in `RAW_INGEST` has the seed, the run, the date window, the page number, the body, the HTTP status and the fetch time.

- A transport failure is evidence too. Its row has no status code and no body.
- A body that is not JSON stays as it arrived. The row gets the status `failed`. The column type is text, not JSON, for this reason.
- The foreign keys to the seed and to the run use `RESTRICT`. A delete of a parent row cannot remove evidence.

The transformer reads only stored rows. Thus the same code path does the first pass and each replay.

## Rule 2. One listing, one transaction

For each listing on a page, the transformer does these steps:

1. It records the source ID as "seen", before admission.
2. It validates the title, the date, the venue, the artists and the IDs.
3. It opens a transaction.
4. It finds or creates the venue, the artists, the event, the identity rows and the ordered lineup.
5. It commits all rows. If a step fails, it rolls back all rows.
6. After a rollback, it writes one rejection record with the reason.

| Reason | Meaning |
|---|---|
| `NO_ARTIST` | The lineup has no artist with an ID |
| `EMPTY_TITLE` | The title has no visible character |
| `BAD_DATE` | Onda cannot read the date |
| `PARSE_FAILURE` | A field is absent or has an incorrect type |

Onda admits an event only if its lineup has one artist or more.
It does not repair a listing: it does not invent an artist, and it does not correct a date.
Thus a rejection is not always an error at the source.

The unique key `(raw_ingest_id, entity_index)` makes the rejection record idempotent. A replay does not write a second record.

## Rule 3. Translate the identity

| Identity map | Unique keys |
|---|---|
| `CITY_IDENTITY`, `VENUE_IDENTITY`, `ARTIST_IDENTITY`, `EVENT_IDENTITY` | `(source, source_id)` and `(entity, source)` |

- The transformer finds the row by `(source, source_id)`. If the row is there, it updates the catalog row. If not, it creates the two rows.
- A name is an attribute, not a key. A venue with a new name stays the same venue.
- The lineup changes only if the ordered list of artists is different.
- The source sometimes gives two IDs to one real event. If title, venue, date, start time and lineup all agree, the later row becomes an alias. Reads show the first row only, and Onda deletes no row.

A second source can add a second identity row for the same event.
The schema is ready for that. The match of two sources is separate work, and it is not built.

## Rule 4. When is a snapshot complete?

The last page is not proof. A snapshot of one seed is complete only if all five conditions are true:

- The number of stored pages is equal to the number of expected pages.
- Each page has the HTTP status 200.
- Each page has the status `processed`.
- The number of listings is equal to the total that the source reports, and the total is the same on each page.
- Each listing has a source ID for its event.

The count uses listings, not events, because the source can give two listings for one event.

> [!IMPORTANT]
> An incomplete snapshot can add data. It cannot subtract data.

Onda admits a good event on page 1 when page 2 fails.
But an event that is absent from an incomplete snapshot does not get a miss.

## Rule 5. A miss is a suspicion

![An event is active when the source shows it. One miss makes it unverified. Three misses make it hidden. One later sight makes it active again.](assets/figures/event-lifecycle.svg)

- The reconciler looks only at future events of one source, in one city, in the date window of the run.
- An event that the run saw gets `misses = 0`. An event that the run did not see gets one more miss.
- The status comes from all identity rows of the event and of its aliases. If one source sees the event, it stays `active`.
- A backfill run and a replay run do not count misses.
- A past event keeps its last status. Thus the history of a past night does not change.
- The source has no field for a cancellation. Onda does not read a title to find one.

## The limits of the client

| Guard | Value |
|---|---|
| Timeout for one attempt | 20 seconds |
| Attempts for one page | A maximum of 3 |
| Faults that cause a retry | A timeout, a connection error, or status 408, 429, 500, 502, 503, 504 |
| Delay before a retry | `Retry-After`, or a random time up to 1 second, then up to 2 seconds |
| Delay between pages | 1.5 seconds |
| Attempts for one run | A maximum of 1,000 |
| Size of one response | A maximum of 2 MiB |
| Stored bodies for one run | A maximum of 100 MiB |
| Endpoint | One HTTPS URL. A redirect must keep the same origin |

[Decision 7](DECISIONS.md#7-bound-each-fault-at-the-network-boundary) gives the reason for each limit.

## What each failure keeps and blocks

| Failure | Onda keeps | Onda blocks |
|---|---|---|
| A second run starts | The first run and the catalog | The second run. No run record |
| A transport failure or an HTTP error | The fetch result and the error text | Completeness, and thus the miss count |
| A response over the size limit | The earlier evidence and the error text | That body, and completeness |
| A page that is not JSON | The exact body | All listings on that page |
| One listing that is not valid | The other listings, and a rejection record | All writes for that listing |
| A listing with no event ID | The rejection record | Completeness for the seed |
| A crash of the run | Committed listings and stored responses | Nothing more. The run gets the status `crashed` |
| The source stays down | The catalog and all user data | New events and updates |

## How to add a second source

This procedure is the planned path. No second source is in the code today.

1. Get permission from the owner of the source.
2. Add the source to the `Source` list in `backend/config/sources.py`.
3. Write a client with the limits in the table above.
4. Record synthetic fixtures for a complete page, a bad page and a page with errors.
5. Map each response field to `EventDTO`.
6. Add the seeds, and add one `CITY_IDENTITY` row for each city.
7. Make the decision how an event of the new source matches an event that is in the catalog.
8. Write the completeness conditions for the new source.
9. Run a backfill, and compare its result with the catalog before the nightly schedule starts.

The React app, the social tables and the API do not change, because they use Onda IDs only.

## Evidence

- 53 tests in [`backend/ingestion/tests/`](../backend/ingestion/tests/) run against MySQL in CI.
- 14 synthetic fixtures give complete, bad, double, multi-page and incomplete responses.
- A backfill run on 2026-08-20 had 2 of 2 seeds complete. It admitted 1,919 listings and rejected 1,128.
- The live catalog had 360 upcoming events on 2026-11-27. Thus the nightly path operates.

## The source and permission

- The client calls one public listing endpoint of Resident Advisor, with the same public headers as its web page.
- The client uses no account, no cookie and no bypass of a challenge. It sends one request each 1.5 seconds.
- Onda has no connection with Resident Advisor.
- Before a wider release or commercial use, I will contact Resident Advisor about the use of its data.

## Code map

| Subject | File |
|---|---|
| Command and exit codes | [`backend/ingestion/management/commands/sync_ra.py`](../backend/ingestion/management/commands/sync_ra.py) |
| Run, budgets, completeness | [`backend/ingestion/runner.py`](../backend/ingestion/runner.py) |
| HTTP limits and delays | [`backend/ingestion/client.py`](../backend/ingestion/client.py) |
| Validation and admission | [`backend/ingestion/transformer.py`](../backend/ingestion/transformer.py) |
| Miss count and status | [`backend/ingestion/reconciler.py`](../backend/ingestion/reconciler.py) |
| Evidence tables | [`backend/ingestion/models.py`](../backend/ingestion/models.py) |
| Catalog and identity maps | [`backend/catalog/models.py`](../backend/catalog/models.py) |
