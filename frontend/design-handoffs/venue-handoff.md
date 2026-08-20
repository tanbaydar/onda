# VENUE PAGE — identity and location delta

Ruled 2026-08-20 by the current operator. This delta uses the existing design tokens and detail-ledger grammar.

## Identity

- The venue name leads the page in the display face. Do not add a descriptive eyebrow or card treatment.
- Location is one quiet, self-identifying line in this format: `City, Region · Country` (for example, `Boston, Massachusetts · United States`). Omit unavailable or duplicate parts gracefully.
- The full location line links to that city's Discover view. It has no field labels and no default underline; hover may reveal the underline.
- Never expose timezone on the venue page. It is operational data, not useful venue identity content.
- The favorite heart sits directly beneath the location within the identity block. Do not create a separate FAVORITE section.

## Event collections

- Upcoming and Past follow the compact shared event-ledger anatomy.
- Keep section separation through whitespace. Do not wrap the identity or event collections in cards.
- Pagination chrome is absent when a collection has one page.
