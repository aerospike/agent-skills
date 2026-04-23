---
title: Choose flat bins, nested CDTs, or multiple records for one logical entity
impact: HIGH
tags: modeling, bins, cdt, record-size, contention, denormalization
doc: https://aerospike.com/docs/database/learn/architecture/data-storage/data-model
also:
  - https://aerospike.com/docs/develop/data-types/collections
last_verified: 2026-04-23
---

## Choose flat bins, nested CDTs, or multiple records for one logical entity

**Rule**

**Flat bins:** prefer when fields are read or written **together** under one primary key, record size stays within bounds, and you do not need deep partial structure. **Nested CDTs (lists/maps):** use when a **sub-structure** is updated **in place** (server-side `operate` on a path), you need **ordering or map key semantics** from the type system, and growth is **bounded** per [cdt-bounded-collections.md](cdt-bounded-collections.md). **Multiple records (same or related keys):** use when different **slices** of a logical entity have different **read/write hotness**, **independent** primary-key access paths, or you must stay **under max record size** and avoid a single contended row—accept **fan-out reads** or **batch** to reassemble, and [denormalize](model-access-paths-denormalization.md) where a single PK read must win.

**Why**

Bins are cheap to address individually; CDTs add path operations and size but avoid shipping whole records for small nested changes. A single large record can become a **contention and hot-key** point; many small records can push work to **batch** and **index/query** design. [Record size and hardware efficiency](model-record-size-hardware-efficiency.md) and [hot keys](model-hot-keys.md) tie directly to this choice.

**Prefer**

- **One PK + flat bins** when the happy path is one get/put or one `operate` over known bin names
- **CDT `operate`** on a **nested path** when updates are **partial** and colocated with the same key
- **Extra records** keyed by a **natural access path** (for example `user:orders:<id>`) when paths split cleanly and you can **batch** or index only what queries need; pair with [query-sindex-by-access-path.md](query-sindex-by-access-path.md) for predicate-driven indexes

**Avoid**

- **Unbounded** list/map growth on a “document-shaped” record; see [cdt-bounded-collections.md](cdt-bounded-collections.md)
- **Giant** nested JSON-like blobs updated only via full-record **get**/**put** under **concurrent writers**; prefer [binop](binop-operate-record-lock-read-write.md) and [expressions](expr-compute-to-data.md) on the server
- **Multiple records** for “normalization” alone when every read still needs all of them—[denormalize](model-access-paths-denormalization.md) for the dominant path

**See also**

- [cdt-nested-collections.md](cdt-nested-collections.md) (context, ordering, path expressions)
- [model-record-size-hardware-efficiency.md](model-record-size-hardware-efficiency.md)
- [query-secondary-index-discipline.md](query-secondary-index-discipline.md) (if secondary lookups drive the split)
