---
title: Design secondary indexes for query paths—not for every column
impact: HIGH
tags: query, secondary-index, cardinality
doc: https://aerospike.com/docs/develop/learn/queries/
also:
  - https://aerospike.com/docs/database/learn/architecture/data-storage/secondary-index
last_verified: 2026-04-21
---

## Design secondary indexes for query paths—not for every column

**Rule**

Use secondary indexes for predicates that match a **planned query path** at sensible cardinality. Do not index high-cardinality values (for example unique UUIDs per row) as a substitute for a primary key redesign. Prefer primary-key access when the key is known.

**Why**

Indexes have memory and write-amplification cost. Wrong index choices yield large candidate sets and slow queries. Aerospike’s fastest path remains direct primary-key access.

**Prefer**

- Modeling that answers “how do I look this up?” with PK when possible
- Indexes on fields that partition the key space usefully for queries

**Avoid**

- “Index everything” patterns carried over from relational databases

**See also**

- [policy-send-key.md](policy-send-key.md) (when query results must return stored user keys)
- [model-access-paths-denormalization.md](model-access-paths-denormalization.md)
- [single-record-operations.md](single-record-operations.md)
