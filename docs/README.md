# Documentation

These pages explain the shipped product and the engineering decisions behind it. The root [README](../README.md) is the one-page entry point.

| Document | Scope |
|---|---|
| [Product guide](PRODUCT_GUIDE.md) | User-visible purpose, features, flows, and current demo boundaries |
| [Event ingestion](INGESTION.md) | Source acquisition, raw evidence, validation, idempotency, quarantine, and reconciliation |
| [Application data](APPLICATION_DATA.md) | Canonical reads, social writes, privacy, lifecycle behavior, feed assembly, and time semantics |
| [API](API.md) | First-party JSON API, sessions, CSRF, route inventory, errors, and pagination |
| [Database](DATABASE.md) | Crow's-foot diagrams of the 25 shipped product tables and their invariants |

Implementation paths and enforcing tests are linked directly from each page so the documentation can be checked against the code without navigating internal project records.
