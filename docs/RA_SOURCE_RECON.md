# Resident Advisor Source Reconnaissance

**Status:** Listing acquisition confirmed; historical backfill enabled; explicit cancellation cascade disabled.
**Recon date:** 2026-07-30
**Seeded markets:** New York City and Boston

## Purpose

This document records only observed source behavior. It does not promote assumptions into ingestion contracts.

## Recon conclusion

Resident Advisor's public browser client uses:

- Endpoint: `POST https://ra.co/graphql`
- Request content type: `application/json`
- Full GraphQL query documents rather than persisted hashes (`usePersistedQueries` was disabled in the observed client)
- No account, cookie, authorization token, or API key for the public listing operation

The exact `GET_EVENT_LISTINGS` operation has been captured in `docs/recon/fixtures/ra_event_listings_request.json` and replayed directly outside the browser with HTTP 200.

**A2 historical backfill gate passes.** Boston returned records at the trailing 24-month boundary, including 2024-07-30 and 2024-08-01. Page 1 and page 2 returned distinct stable listing and event IDs while reporting the same `totalResults`. Bounded historical backfill may be implemented.

**A1 explicit-cancellation gate fails for now.** The cancelled detail fixture examined (`Event:1644565`) contains no explicit cancellation boolean, enum, or status in the fields requested by RA's own detail client. It reports `live: true`; cancellation exists only in the title and prose. Title parsing is not trustworthy enough to authorize destructive behavior. The Q159 wipe branch remains unbuilt. Cancellation follows absence-to-hide and preserves user content unless a future recon discovers a typed source signal.

**A8 per-event scope gate is unavailable.** No reliable per-event music/type field is
confirmed in the listing payload. V1 admission scope therefore equals membership in an
active tracked RA area. `OUT_OF_SCOPE` remains a reserved rejection reason and is unused
until recon identifies a trustworthy source field. The product remains genre-agnostic;
this is an acquisition-coverage rule, not application behavior.

**City resolution is seed-grain.** The captured listing operation requests only
`venue { id name contentUrl live }`; its response contains no venue area. The observed
detail fixture likewise supplies no usable venue-area object. The runner must therefore
resolve `(source, area_ref)` through `CITY_IDENTITY` before fetching. An unmapped seed
is a configuration failure, not an `UNMAPPED_AREA` rejection; no new rejection enum
value is introduced.

## Confirmed observations

### Historical listing URLs and GraphQL ranges work

Resident Advisor exposes date-addressable city listing pages. Indexed, recently crawled examples include:

- Boston historical/date listing: `https://ra.co/events/us/boston?startDate=2026-06-05`
- New York City historical/date listing: `https://ra.co/events/us/newyorkcity?startDate=2026-06-13`

The captured GraphQL operation accepts `listingDate.gte` and `listingDate.lte`. Direct tests confirmed:

- Boston area ID: `530`
- New York City area ID: `8`
- `2024-07-30` returned two results
- `2024-08-01` through `2024-08-07` returned 20 results
- Historical records included stable IDs, dates, start times, venues, and artist arrays
- New York City returned 150 results for 2024-08-01 through 2024-08-03, confirming the same historical path for the second seed

The backfill should still use small chronological windows and polite throttling rather than requesting all 24 months at once.

### Pagination is page-number based

`GET_EVENT_LISTINGS` accepts `page` and `pageSize` integers and returns `totalResults`.

For Boston, 2026-07-01 through 2026-07-07:

- page 1, size 2 returned event IDs `2477212`, `2480603`;
- page 2, size 2 returned event IDs `2479226`, `2480631`;
- both reported `totalResults: 15`.

Termination rule: stop after the page whose accumulated result count reaches `totalResults`, or immediately on an unexpectedly empty page. Archive every response independently.

### Cancelled events remain visible

Observed public examples:

- `https://ra.co/events/1644565` — title begins `[CANCELLED]`
- `https://ra.co/events/1820529` — title begins `[CANCELLED]`
- Boston's 2026-07-24 listing included `[CANCELLED] Nocturnal District presents: Rooftop Sessions 02`

Cancellation is visibly expressed in rendered data. For cancelled event `1644565`, RA's own event-detail cache included:

- `title: "[CANCELLED] SCANNDALE at Provocateur"`
- `live: true`
- cancellation prose in `content`
- no explicit cancellation status among the detail fields requested by the public client

A title prefix alone is not sufficiently trustworthy to authorize Danced's destructive future-event cascade.

### Direct access behavior

On 2026-07-30, a plain GET to an RA HTML route returned HTTP 403 from Cloudflare. The correct New York City route is `/events/us/newyorkcity`.

The public listing GraphQL POST itself returned HTTP 200 when called directly with ordinary `accept`, `content-type`, `origin`, and `referer` headers. No browser cookies or credentials were sent. The acquisition adapter should call the GraphQL endpoint directly and treat any future 403 as a named source-fetch failure; it must not add CAPTCHA solving or other access-control bypass behavior.

## Decisions still gated

- Exact event-detail query document, if detail enrichment is required beyond listing fields
- Maximum practical date-window size
- Throttling and error behavior

Until these are confirmed:

- explicit-cancellation deletion is not implementation-ready;
- disappearance-to-hide remains the only designed live removal path;
- no fetch is permitted in a user-facing request path.

Historical backfill is implementation-ready for both seeded cities.

## Browser capture procedure used

Recon used a disposable signed-out Chrome profile with remote debugging enabled. The profile did not touch the user's normal Chrome history or cookies.

1. Open Chrome DevTools, select **Network**, enable **Preserve log**, and clear the log.
2. Select the **Fetch/XHR** filter.
3. Visit `https://ra.co/events/us/boston`.
4. Change the displayed date once and load enough results to trigger the next page.
5. Open one ordinary event detail page.
6. Open a visibly cancelled event detail page, such as `https://ra.co/events/1644565`.
7. In Network, search for `graphql`. If that finds nothing, inspect Fetch/XHR requests whose response contains an event title.
8. Export **Save all as HAR with content**.
9. Place any future HAR at `recon/private/ra-browser.har`. This path remains uncommitted because a HAR may contain cookies or other credentials.

The HAR will be used locally to derive sanitized fixtures containing only:

- endpoint path and method;
- operation/query identity;
- non-secret headers required by the public client;
- variables;
- representative response JSON for active, cancelled, historical, and paginated listings.

No cookies, authorization tokens, IP data, analytics identifiers, or unrelated browser traffic belong in committed fixtures.

## Completion criteria

Listing recon is complete when the repository contains sanitized, replayable evidence for:

1. one upcoming listing page;
2. one second listing page proving pagination;
3. one historical listing page;
4. a written field map from source payloads to the admission contract;
5. an explicit conclusion on whether cancellation cascade and 24-month backfill are enabled.

Those conditions are now met for Boston and New York City listings. Detail-query enrichment remains a small follow-up task only if the canonical admission contract needs fields absent from the listing operation.
