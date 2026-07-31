# Design fixtures

These files are real Danced catalog and social API response shapes captured for design work. They are deliberately raw responses: the JSON is only pretty-printed, not cleaned up or reshaped.

The original files are sparse variants that preserve ordinary empty and low-density states. Files ending in `-dense.json` are stress variants with larger rating, review, like, attendee, feed, notification, and relationship populations. Multi-fetch dense surfaces are endpoint-keyed bundles; every value inside the bundle is the untouched response from the endpoint named by its key. Design work must check **both sparse and dense variants** so empty-state clarity is not traded for dense-state usability, or vice versa.

The files in `docs/recon/fixtures/` are Resident Advisor ingestion **input**. They must not be used as a design data source.

Captured from the local development database on 2026-07-31 as `review.public.test`, using Django's test client. Disposable supporting accounts created through the normal registration API were removed after capture; no founder data was used or changed.
