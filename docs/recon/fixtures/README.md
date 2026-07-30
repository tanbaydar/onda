# Ingestion fixture corpus

These fixtures are test inputs for the RA listing boundary. Captured evidence and
synthetic edge cases are labeled separately; synthetic payloads imitate only fields
observed in the captured `GET_EVENT_LISTINGS` operation.

## Captured and sanitized

- `ra_event_listings_historical_response.sample.json` — representative subset of a
  historical Boston response. Its `totalResults` describes the original response, not
  the sanitized one-event subset, so it must not be used for exact-count tests.
- `ra_cancelled_event_detail.sample.json` — detail-query recon evidence only. It is not
  valid Transformer input.

## Synthetic listing payloads

| Scenario | Payload | Expected admission behavior |
|---|---|---|
| Complete representative page | `ra_listing_complete.synthetic.json` | 2 admitted |
| Date only | `ra_listing_date_only.synthetic.json` | admitted; `start_time = NULL` |
| TBA lineup | `ra_listing_tba_lineup.synthetic.json` | quarantined `NO_ARTIST` |
| Festival lineup | `ra_listing_festival.synthetic.json` | admitted; lineup order 1–3 |
| Sold out | `ra_listing_sold_out.synthetic.json` | admitted; ticket state is irrelevant |
| Cancellation text only | `ra_listing_cancelled_title.synthetic.json` | admitted `active`; title parsing triggers nothing |
| Structurally malformed event | `ra_listing_malformed_event.synthetic.json` | quarantined `PARSE_FAILURE` with known event ID |
| Whole-payload failure | `ra_listing_malformed_payload.synthetic.txt` | payload status `failed`; no event outcomes |
| Pagination page 1 | `ra_listing_paginated_page_1.synthetic.json` | complete only together with page 2 |
| Pagination page 2 | `ra_listing_paginated_page_2.synthetic.json` | complete only together with page 1 |

The pagination scenario is one test case represented by two files because one fixture
equals one HTTP response boundary. All synthetic IDs use the `syn-` prefix and can
never be confused with captured provider identifiers.
