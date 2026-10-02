---
title: Pick client APIs by key cardinality and work done per request
impact: MEDIUM
tags: client, batch, operate, expression, performance
doc: https://aerospike.com/docs/develop/learn/
also:
  - https://aerospike.com/docs/develop/learn/operations-and-expressions/
last_verified: 2026-10-01
---

## Pick client APIs by key cardinality and work done per request

**Rule**

**One key,** multiple bins or a record-shaped update: prefer **`operate`** (and [record lock / mixed R/W](aerospike-development-operate-record-lock-read-write.md) semantics) so the server does **one round-trip** and you avoid **get/put** races. **Many keys,** each known: prefer **[batch](aerospike-development-batch-parallel-key-operations.md)** (reads, writes, or batch **`operate`** with **one entry per key**). **Server-side predicate, or a patch derived from other bins** on read or write: use **[filter/operation expressions](aerospike-development-expr-compute-to-data.md)** so work stays **on the data nodes**; a change to one bin in place (trim, append, increment) is an operation inside the same **`operate`**. **Do not** string together serial **get**/**put** when a **single** `operate` or **single** expression chain can express the work. An **operation** acts in place on one named bin and changes what is stored; an **expression** evaluates to a typed value and changes nothing by itself. Use an operation to change a bin in place, and an expression to filter records, to return a computed value you do not want stored, or to store a value derived from more than one bin; one command often carries both.

**Why**

Round-trips and client-side re-reads dominate latency. Aerospike **compute-to-data** (expressions) and **atomic** multi-op **`operate`** are the idioms that match the storage model; naive patterns replicate RDBMS habits that multiply trips and contention.

The terms overlap. An operation is a data type's own operation API (list, map, string, blob, HLL and plain bin operations), and it goes into `operate` as it is. An expression composes, so one expression's result feeds another and one expression can read several bins. To run inside `operate` it is wrapped as a read expression, which returns the value under a name that exists only in the response and leaves the record unchanged, or as a write expression, which stores the value in a bin; the docs call those wrapped forms operation expressions. A modify expression such as an uppercase or an append is therefore not a write: it yields the transformed value, and the stored bin stays as it was unless a write expression stores it. Only expressions reach record filters, query projections and secondary index definitions over a computed value.

**Prefer**

- **`operate`** for **one key**, **N bins**, or **CDT paths** in one call
- **Batch** with **coalesced keys** and **per-key** result handling
- A **filter expression** for “read only if condition” or “write only if bin matches”, so a command applies only to matching records
- An **operation** to change one bin in place (normalize, append, trim, increment): it names the bin and is the shorter path
- A **read expression** to return a computed value under a response-only name, such as a derived field in a query projection, without storing it
- A **write expression** when the stored value is derived from more than one bin, which an operation cannot do
- Deeper reading: [operate-record-lock-read-write.md](aerospike-development-operate-record-lock-read-write.md), [operate-atomicity.md](aerospike-development-operate-atomicity.md), [batch-parallel-key-operations.md](aerospike-development-batch-parallel-key-operations.md), [expr-compute-to-data.md](aerospike-development-expr-compute-to-data.md)

**Avoid**

- **Parallel single-key** calls in a loop for **hundreds+** hot keys with **no** batching when the API is appropriate
- **read-modify-write in the app** for bins that the server can [operate or express](aerospike-development-expr-compute-to-data.md) into one request
- Expecting a **modify expression** to write: it returns the transformed value, and persisting it takes a write expression or the matching operation
- Treating an **unknown** result as harmless in an operation expression: a filter counts unknown as false, but an operation expression fails with error 26 unless the evaluate-no-fail flag is set, and the flag applies per operation, not per command
- Mixing read and write operations in one **query projection**: a foreground query accepts only read operations and expressions, a background query only write ones, and both reject a mix
- Expecting a classic expression to **loop or recurse**: it has conditional branching only, and iterating over nested collection elements needs path expressions

**See also**

- [cdt-server-side-ops.md](aerospike-development-cdt-server-side-ops.md) (collection operations inside `operate`)
- [Operations and expressions](https://aerospike.com/docs/develop/learn/operations-and-expressions/)
- [model-hot-keys.md](aerospike-development-model-hot-keys.md) (when one key is still the bottleneck)
