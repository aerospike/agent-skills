---
title: Use operate for one record lock, many ops, and mixed reads and writes
impact: HIGH
tags: bin-operations, operate, read-write, latency, scalability
doc: https://aerospike.com/docs/develop/learn/bin-operations/
also:
  - https://aerospike.com/docs/develop/learn/queries/projection
last_verified: 2026-04-21
---

## Use operate for one record lock, many ops, and mixed reads and writes

**Rule**

Use the **`operate`** command when you need **multiple bin-level changes on the same record key** in **one server round trip**. The server **acquires a record lock**, runs an **ordered list** of bin operations **atomically and in isolation** against an in-memory copy of the record, then persists if any write occurred. **Mix read and write operations** in the same `operate` call when you need updated values back without a separate `get`: later operations **see the effects of earlier ones** in the list (including writes before reads). This cuts **client/server chatter**, reduces **lock hold time versus separate get/put sequences** from the app, and improves **throughput and tail latency** for hot keys compared to naïve multi-call patterns.

**Why**

[Bin operations](https://aerospike.com/docs/develop/learn/bin-operations/) documents that `operate` executes the full operation list under one record command; reads in the list are a form of **projection** and avoid an extra network hop to fetch bins after writes. Fewer round trips mean less work per logical update and less contention window for other clients waiting on the same key.

**Prefer**

- One `operate` with all bin ops (scalar, CDT, expressions as supported) for that unit of work
- Mixed read+write lists when the response must reflect post-write state (e.g. increment then read counter)
- Filter expressions on `operate` when the doc pattern fits conditional updates

**Avoid**

- Chaining separate `get` → app logic → `put` when `operate` can express the same work on one key
- Splitting independent bin updates on the same key into multiple commands without a concurrency story
- Mixing **bin-targeted** operations (bin writes or reads, increments, CDT ops) with a **whole-record** read in the same `operate`—you cannot increment a bin and request the full record in one call; use **named bin** read operations for every bin you need back
- Expecting “return everything” from an `operate` list—projection is **per operation**, so plan the list as **per-bin** reads and writes only

**See also**

- [binop-operate-atomicity.md](binop-operate-atomicity.md)
- [single-record-operations.md](single-record-operations.md)
- [cdt-server-side-ops.md](cdt-server-side-ops.md)
- [bin-operate-mixed-read-write.md](../examples/bin-operate-mixed-read-write.md)
