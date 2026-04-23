---
title: Model for primary-key access paths and denormalize deliberately
impact: HIGH
tags: modeling, denormalization, key-design
doc: https://aerospike.com/docs/develop/learn
also:
  - https://aerospike.com/docs/database/learn/architecture/data-storage/data-model
last_verified: 2026-04-21
---

## Model for primary-key access paths and denormalize deliberately

**Rule**

Design schemas around **how data is read and written**: namespace, set, and user key should make the common path a single primary-key operation. There are no server-side joins—duplicate or embed via bins and CDTs when that matches query needs.

**Why**

Relational normalization without access-pattern alignment forces multi-round-trip patterns in application code. Hot keys and uneven partition distribution are modeling problems, not fixed by indexes alone.

**Prefer**

- Access-pattern-first key design
- CDTs for embedded aggregates when reads are colocated by key

**Avoid**

- Join-shaped APIs in application code mirroring SQL without redesign

**See also**

- [model-namespace-set-boundaries.md](model-namespace-set-boundaries.md)
- [model-bin-cdt-multiple-records.md](model-bin-cdt-multiple-records.md)
- [model-record-size-hardware-efficiency.md](model-record-size-hardware-efficiency.md)
- [query-secondary-index-discipline.md](query-secondary-index-discipline.md)
- [cdt-server-side-ops.md](cdt-server-side-ops.md)
