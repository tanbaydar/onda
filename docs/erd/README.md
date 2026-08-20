# Generated ERD diagrams

These diagrams are generated from the authoritative `docs/onda.dbml` source.

- `onda-erd-ingestion.svg` / `.png` — full columns for the ingestion zone.
- `onda-erd-canonical-identity.svg` / `.png` — full columns for the canonical and identity zone, plus PK-only App boundary stubs.
- `onda-erd-app.svg` / `.png` — full columns for the app zone, plus PK-only canonical boundary stubs.
- `onda-erd-overview.svg` / `.png` — all relationships, with columns collapsed to PK/FK fields for full-diagram readability.

The Graphviz renderer uses orthogonal routing, zone clusters, dedicated edge gutters,
PK/FK column markers, and cardinality markers at both ends of every relationship.
Regenerate after changing the DBML:

```sh
docs/erd/regenerate.sh
```

`regenerate.sh` requires Python 3, Graphviz `dot`, and `rsvg-convert`. Generation fails
if SVG node/edge counts diverge from the selected DBML objects or if the three zone
edge totals, after removing duplicated boundary edges, do not equal the DBML total.
