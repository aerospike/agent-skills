# Reference — `aerospike-data-modeling`

Design-time data modeling. For implementation-time work against an existing
model, see the `aerospike-development` skill.

## Rule files

| File | Topic | Impact |
|------|-------|--------|
| [model-design-time-workflow.md](references/model-design-time-workflow.md) | The clarify → group → design → review loop and its stop points | HIGH |
| [model-failure-modes-checklist.md](references/model-failure-modes-checklist.md) | Seven detection tests to run against a drafted model | HIGH |
| [ex-guide-escalation.md](references/ex-guide-escalation.md) | Fetching the data modeling guide; routing by task | HIGH |
| [model-deliverables-schema-guide-summary.md](references/model-deliverables-schema-guide-summary.md) | Schema guide and derived schema summary | MEDIUM |

## Primary source

- **`aerospike/data-modeling-guide`** (internal) — the full design-time process: checklist, decision packs, sizing worksheets, workload archetypes, and the CDT/expression reference material that modeling decisions depend on. Start at its `AGENTS.md`.

## Aerospike documentation

- [Data modeling](https://aerospike.com/docs/develop/data-modeling/) — record sizing, key design, collections, relationships, indexes, conventions
- [Collection data types](https://aerospike.com/docs/develop/data-types/collections/) — List and Map operations, ordering, context
- [Expressions](https://aerospike.com/docs/develop/expressions/) — filter and operation expressions, path expressions
- [Transactions](https://aerospike.com/docs/database/learn/transactions) — multi-record transactions and their constraints
- [Client matrix](https://aerospike.com/docs/develop/client-matrix) — client/server feature compatibility
- [Configuration reference](https://aerospike.com/docs/database/reference/config) — namespace parameters and current defaults
- [System limits](https://aerospike.com/docs/database/reference/limitations) — bin name length, bins per record, record size

## Out of scope

Cluster deployment, hardware sizing, network topology, XDR setup, backup and
restore, and general administration. Route those to Aerospike Operations
documentation.
