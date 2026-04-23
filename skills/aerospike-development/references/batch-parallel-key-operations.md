---
title: Use batch APIs for many primary-key operations
impact: MEDIUM
tags: batch, throughput, keys, deduplication, operate, contention, key-busy
doc: https://aerospike.com/docs/develop/learn/batch/
last_verified: 2026-04-21
---

## Use batch APIs for many primary-key operations

**Rule**

When reading or writing many records **by known primary keys**, use the client’s batch APIs instead of serial single-key calls, subject to reasonable batch sizes and error-handling needs.

**Batch policies** (parallelism, timeouts, and write-specific options) are separate from single-record policies—set **defaults per batch flavor** on the client when your SDK splits them (see [policy-client-defaults.md](policy-client-defaults.md)). For **batch writes**, configure **`commitLevel`** (or equivalent) and, for **batch deletes**, **durable delete** flags to match namespace and correctness needs ([policy-write-commit-level.md](policy-write-commit-level.md), [single-delete-durable-deletes.md](single-delete-durable-deletes.md)).

**Do not list the same key more than once in a single batch request.** Build the batch so each primary key appears at most once: **coalesce** multiple intended changes on the client before sending. If you need **several bin-level updates (or mixed read/write)** for **one** key in one round trip, use **`operate`** in the batch (or the SDK’s batch variant that carries multiple operations per key)—not multiple duplicate entries for that key.

**Per-key results:** A batch call can **complete without throwing** (or report an overall “success”) while **some keys or sub-operations fail**—for example not found, generation mismatch, **`KEY_BUSY`**, or policy errors on individual entries. After the batch returns, **inspect the status or result for each batch entry** (names vary by SDK: per-key records, arrays of results, iterators). Do **not** infer that every operation succeeded from the **top-level** outcome alone.

**Why**

Batch APIs reduce round trips and let the cluster process key groups in parallel compared to naive loops. Repeating the same key in one batch is ambiguous or order-dependent across clients and wastes work; coalescing preserves clear semantics. Duplicate keys can also drive **extra latency** and **contention on that key** (the same record): the server may serialize or retry work on it repeatedly, worsening **hot-key** behavior and surfacing errors such as **`KEY_BUSY`** (or the client equivalent) under load. Multi-bin or mixed semantics for a single key belong in one **`operate`** chain per key (see [binop-operate-record-lock-read-write.md](binop-operate-record-lock-read-write.md)).

**Prefer**

- Chunked batches if the SDK or service limits batch size
- **One entry per key** per batch; merge or drop duplicates on the client before `batch_*`
- **Batch `operate`** (or equivalent) when one key needs multiple operations atomically in the batch
- **After each batch:** walk **every** entry’s result code or exception slot—partial success is normal for batch APIs
- Retrying or compensating only for keys that **actually** failed (once you have per-key status)

**Avoid**

- Thousands of sequential gets when a batch interface exists
- **Duplicate keys** in the same batch when you can coalesce or combine into **`operate`**—especially on keys that are already hot or latency-sensitive
- Assuming **no exception** or **overall OK** means **every** key in the batch succeeded

**See also**

- [model-hot-keys.md](model-hot-keys.md)
- [policy-client-defaults.md](policy-client-defaults.md)
- [policy-write-commit-level.md](policy-write-commit-level.md)
- [single-delete-durable-deletes.md](single-delete-durable-deletes.md)
- [binop-operate-record-lock-read-write.md](binop-operate-record-lock-read-write.md)
- [ex-batch-read-by-keys.md](ex-batch-read-by-keys.md)
- [policy-reuse-timeouts-retries.md](policy-reuse-timeouts-retries.md)
