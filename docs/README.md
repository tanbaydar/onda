# Onda engineering documentation

This directory has two layers:

1. A short review path that explains the shipped system.
2. Evidence and design records that preserve the detailed reasoning behind it.

## Start here

| Document | Scope |
|---|---|
| [Product guide](PRODUCT_GUIDE.md) | User-visible purpose, features, flows, and current demo boundaries |
| [Event ingestion](INGESTION.md) | Source acquisition, raw evidence, validation, idempotency, quarantine, and reconciliation |
| [Application data](APPLICATION_DATA.md) | Canonical reads, social writes, privacy, lifecycle behavior, feed assembly, and time semantics |
| [API](API.md) | First-party JSON API, sessions, CSRF, route inventory, errors, and pagination |
| [Database](DATABASE.md) | Crow's-foot diagrams of the 24 shipped product tables and their invariants |

The root [README](../README.md) is the one-page entry point.

## Evidence and implementation records

These documents go deeper than the public narrative. They are useful when reviewing a specific invariant or locating its enforcing code and tests.

| Document | Role |
|---|---|
| [DATA_FLOW.md](DATA_FLOW.md) | Evidence-linked trace from provider response through the product API |
| [onda-data-architecture.md](onda-data-architecture.md) | Original high-level ingestion architecture |
| [PRODUCT_QA_SPEC.md](PRODUCT_QA_SPEC.md) | Frozen shipped product behavior |
| [OPERATIONS.md](OPERATIONS.md) | Sync, failure, recovery, backup, and operational procedures |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Fresh AWS deployment and routine release procedure |
| [RA_SOURCE_RECON.md](RA_SOURCE_RECON.md) | Captured observations about the v1 source contract |
| [recon/fixtures](recon/fixtures) | Sanitized request/response fixtures used by ingestion contract tests |
| [ERD_REVIEW.md](ERD_REVIEW.md) | Review record for the original database blueprint and implementation deltas |
| [erd](erd) | Reproducible Graphviz exports of that blueprint |

## Design records and history

`onda.dbml` and its generated files are the frozen design blueprint used to reason about the database. They include planned tables that are not shipped. [DATABASE.md](DATABASE.md) is the implementation-level source for the current 24-table product schema.

`PROJECT_STATE.md`, discovery notes, maintainability/security reviews, and `archive/` preserve dated project history. They are not claims about the current production deployment unless a current document explicitly references them.

The only pre-Onda implementation name retained outside the root README is in the
forward database migration that must identify and rename an existing legacy user
table. Current code, schema state, configuration, and generated artifacts use Onda.
