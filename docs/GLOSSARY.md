[Onda](../README.md) / [Documentation](README.md) / Glossary

# Glossary

> **For** all readers. **Use** this page to find the one meaning of a word in these pages.

Each thing has one name in these pages.
The column "In code" gives the name that the code uses for the same thing.

## Product words

| Word | Meaning | In code |
|---|---|---|
| Activity | One item in Home. It shows what a person did. Seven types are possible. | `activity_type` |
| Been | The diary. The list of events that a person went to. | `DIARY_ENTRY` |
| Been entry | One person's record of one event. It can have a rating and a review. | `DiaryEntry` |
| Circle | The people that you follow with an approved follow. | `for_circle` |
| Favorite | An event, an artist or a venue that a person shows on a profile. The app label is "Favourites". | `FAVORITE_EVENT`, `FAVORITE_ARTIST`, `FAVORITE_VENUE` |
| Follow | A link from one person to a second person. It is `pending` or `approved`. | `FOLLOW` |
| Followee | The person that a follower follows. | `followee_id` |
| Home | The page that shows the activity of your circle. | `home_feed` |
| Private profile | A profile that shows its diary only to its owner and to approved followers. | `is_private` |
| Rating | A value from 0.5 to 5.0 in steps of 0.5. | `rating` |
| Review | Text about an event. One Been entry can have one review. | `REVIEW` |
| Viewer | The person who sends the request. | `viewer`, `request.user` |
| Will Be There | A mark that tells your circle about a plan to go to an event. | `WILL_BE_THERE` |

## Data words

| Word | Meaning | In code |
|---|---|---|
| Source | The external site that publishes event listings. Today it is Resident Advisor. | `Source.RA` |
| Listing | One event as the source publishes it in one response. | "listing wrapper" |
| Seed | One city on the source that Onda tracks. | `TRACKED_SOURCE_PAGE` |
| Run | One execution of the sync command. | `SYNC_RUN` |
| Snapshot | All pages of one seed in one run. | `_SeedState` |
| Complete snapshot | A snapshot that passes all the completeness conditions. Onda can account for each page and each listing. | `_seed_completeness` |
| Evidence | The stored responses and the stored rejection records. | `RAW_INGEST`, `REJECTED_INGEST` |
| Rejection | A record of one listing that Onda did not admit, with the reason. | `REJECTED_INGEST` |
| Catalog | The trusted tables for cities, venues, artists, events and lineups. | `catalog` app |
| Onda ID | The primary key of a catalog row. All product tables use it. | `EVENT.id` |
| Source ID | The identifier that the source gives to a thing. | `source_id` |
| Identity map | A table that translates a source ID into an Onda ID. | `EVENT_IDENTITY` and three more |
| Miss | One complete snapshot that does not contain an event. | `misses` |
| Event status | `active`, `unverified` or `hidden`. A hidden event behaves as an unknown event. | `EVENT.status` |
| Alias | A second event row for the same real event. Reads use the first row. | `canonical_event_id` |

## System words

| Word | Meaning |
|---|---|
| Nightly path | The scheduled work that gets listings and updates the catalog. No person waits for it. |
| Request path | The work that answers one request from a person. It uses local data only. |
| View | The function that reads the HTTP request, validates it, and writes the HTTP response. |
| Service | The function that owns one change of state and its transaction. |
| Invariant | A rule about the data that must be true after each transaction. |
| Idempotent | You can do the operation two times, and the result is the same as one time. |
| Cursor | A value that marks a position in an ordered list. The client sends it back to get the next page. |
| Keyset pagination | Pages that start after a key, not after a count of rows. |
| Total order | An order that has no two equal rows. |
| Fan-out on read | The system builds a feed from the source rows when a person asks for it. |
| Fan-out on write | The system copies each action to each follower when the action occurs. |
| Row lock | A lock on one database row that makes a second transaction wait. |
| Advisory lock | A named lock in the database that code takes and releases. |
