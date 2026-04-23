---
title: Pick client APIs by key cardinality and work done per request
impact: MEDIUM
tags: client, batch, operate, expression, performance
doc: https://aerospike.com/docs/develop/learn/
last_verified: 2026-04-23
---

## Pick client APIs by key cardinality and work done per request

**Rule**

**One key,** multiple bins or a record-shaped update: prefer **`operate`** (and [record lock / mixed R/W](binop-operate-record-lock-read-write.md) semantics) so the server does **one round-trip** and you avoid **get/put** races. **Many keys,** each known: prefer **[batch](batch-parallel-key-operations.md)** (reads, writes, or batch **`operate`** with **one entry per key**). **Server-side predicate, trim, or numeric/bin patch** on read or write: use **[filter/operation expressions](expr-compute-to-data.md)** so work stays **on the data nodes**. **Do not** string together serial **get**/**put** when a **single** `operate` or **single** expression chain can express the work.

**Why**

Round-trips and client-side re-reads dominate latency. Aerospike **compute-to-data** (expressions) and **atomic** multi-op **`operate`** are the idioms that match the storage model; naive patterns replicate RDBMS habits that multiply trips and contention.

**Prefer**

- **`operate`** for **one key**, **N bins**, or **CDT paths** in one call
- **Batch** with **coalesced keys** and **per-key** result handling
- **Expressions** for “read only if condition” or “write only if bin matches”
- Deeper reading: [binop-operate-record-lock-read-write.md](binop-operate-record-lock-read-write.md), [binop-operate-atomicity.md](binop-operate-atomicity.md), [batch-parallel-key-operations.md](batch-parallel-key-operations.md), [expr-compute-to-data.md](expr-compute-to-data.md)

**Avoid**

- **Parallel single-key** calls in a loop for **hundreds+** hot keys with **no** batching when the API is appropriate
- **read-modify-write in the app** for bins that the server can [operate or express](expr-compute-to-data.md) into one request

**See also**

- [cdt-server-side-ops.md](cdt-server-side-ops.md) (collection operations inside `operate`)
- [model-hot-keys.md](model-hot-keys.md) (when one key is still the bottleneck)
