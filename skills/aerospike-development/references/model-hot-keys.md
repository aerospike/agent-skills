---
title: Design and mitigate hot keys (error 14 / KEY_BUSY)
impact: HIGH
tags: hot-key, contention, key-busy, error-14, throughput, read-page-cache
doc: https://support.aerospike.com/s/article/Why-does-my-client-return-Error-code-14-Hot-key
also:
  - https://aerospike.com/docs/database/reference/error-codes/
  - https://aerospike.com/docs/database/reference/config#namespace__read-page-cache
last_verified: 2026-04-21
---

## Design and mitigate hot keys (error 14 / KEY_BUSY)

**Rule**

When **many clients** hit the **same primary key** at once, that record becomes a **hot key**: work **serializes** on the server and you can see **high latency**, **timeouts**, or failures such as **error code 14** / **`KEY_BUSY`** (exact name depends on the **client**—see the [support article](https://support.aerospike.com/s/article/Why-does-my-client-return-Error-code-14-Hot-key) and your SDK). That usually means **too much load on one key**, not a random cluster bug.

**Why**

One key lives on **one partition**; concurrent reads and writes **queue** behind the same record lock. Extreme fan-in causes **retries** and **wasted work** under load.

**Prefer**

- **Spreading** work across **more keys** when the product allows—**shard** counters or aggregates instead of a **single** global row everyone updates
- **One** `operate` (or **one** batch entry) **per key** when a key needs several changes—see [batch-parallel-key-operations.md](batch-parallel-key-operations.md) and [binop-operate-record-lock-read-write.md](binop-operate-record-lock-read-write.md)
- **Read** policies that **spread read load** when **slightly stale** data is OK—[policy-read-replica-consistency.md](policy-read-replica-consistency.md) (**MASTER_PROLES**, etc.)
- **Server-side** namespace tuning such as **`read-page-cache`** so the **OS page cache** can absorb **repeated reads** of the same device blocks—can **ease read-heavy hot keys** when storage layout fits; see [model-record-size-hardware-efficiency.md](model-record-size-hardware-efficiency.md) and the [`read-page-cache`](https://aerospike.com/docs/database/reference/config#namespace__read-page-cache) reference (not a substitute for **sharding** hot keys in the app)
- **Backoff with jitter** on transient errors instead of tight spin loops

**Avoid**

- A **single** key as the only place for **high-QPS** writes (global sequence, one shared counter with no sharding)
- **Blind retries** without backoff when you see hot-key / busy errors

**See also**

- [model-record-size-hardware-efficiency.md](model-record-size-hardware-efficiency.md) (read **page cache** and storage context)
- [batch-parallel-key-operations.md](batch-parallel-key-operations.md)
- [model-access-paths-denormalization.md](model-access-paths-denormalization.md)
- [policy-reuse-timeouts-retries.md](policy-reuse-timeouts-retries.md)
