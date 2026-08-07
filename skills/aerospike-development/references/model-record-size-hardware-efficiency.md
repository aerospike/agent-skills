---
title: Size records for primary-index overhead and disk bandwidth
impact: HIGH
tags: modeling, record-size, memory, disk, hybrid, all-flash, index, read-page-cache
doc: https://aerospike.com/docs/database/learn/architecture/data-storage/data-model
also:
  - https://aerospike.com/docs/develop/learn
  - https://aerospike.com/docs/database/reference/config#namespace__read-page-cache
  - https://support.aerospike.com/s/article/Buffering-and-Caching-in-Aerospike
last_verified: 2026-04-21
---

## Size records for primary-index overhead and disk bandwidth

**Rule**

Aerospike does **not** keep its **own large DRAM cache of whole record payloads** the way some application caches do. In typical **hybrid memory** and **all-flash** deployments, **reads still come from the storage path** (devices or related layers)—plan I/O accordingly.

**Read hot spots** (the same data read heavily) can **sometimes** be **mitigated on the node** by **namespace / storage** tuning—for example **`read-page-cache`**, which allows the **host OS page cache** to satisfy repeated block reads under the right **storage-engine** and kernel assumptions. See the [`read-page-cache`](https://aerospike.com/docs/database/reference/config#namespace__read-page-cache) parameter and [Buffering and Caching in Aerospike](https://support.aerospike.com/s/article/Buffering-and-Caching-in-Aerospike); validate in **staging** (not every workload benefits). This is **operations-level** tuning and **does not replace** good **key design** (e.g. [model-hot-keys.md](model-hot-keys.md)).

Each stored record costs about **64 bytes of RAM per replica** in the **primary index** (metadata to locate the object). **Hardware efficiency** depends on the **ratio** between **payload size** and that **fixed per-record overhead**: the band is **1–128 KiB** per record (the Goldilocks band), and it is a **distribution, not a target**. Design so the **bulk of records sit in single-digit KiB**; the upper end is headroom for **outliers** and **slowly-changing consolidated structures** (1:N and N:M relationship lists), not a size to aim for. **Above roughly 50 KiB, justify the record explicitly**—a sufficient justification names the per-record update rate and shows it is low ("rewritten when a subscription changes, a few times a month" clears the bar; "appended on every user action" does not).

- **Oversized records** drive **disk bandwidth** hard. Record data is stored **contiguously**, so every read fetches the **entire record** from storage and every write **rewrites the entire record**—Aerospike does not do in-place updates. Requesting a subset of bins trims what crosses the **network**, not what is read from **device**. A record in the tens of KiB spends tens of KiB of I/O on every access, however small the change (see [single-record-operations.md](single-record-operations.md)).
- **Undersized records** (tiny values) mean you spend **a lot of memory on index entries** (many **64-byte** slots per gigabyte of “useful” data) and can push **RAM** limits before capacity.
- **Size only hurts once multiplied by write frequency.** The same 100 KiB record is unremarkable rewritten once an hour and a device-saturation problem rewritten thousands of times a second. Ask **how often a large record is rewritten**, not just how big it is. Where writes are infrequent relative to reads, records near the upper end are a **legitimate design, not a compromise**—low write throughput, or a cluster with I/O and network headroom, genuinely buys room. On a hot write path the same size is a defect: a 100 KiB record touched by a 15-byte append still spends 100 KiB of write I/O, replication traffic, and defrag load on **every** write.

**Why**

Modeling ignores index overhead and device I/O until clusters hit **latency**, **device saturation**, or **memory for the index**. The **64-byte**-per-record **per replica** rule of thumb makes **micro-records** surprisingly expensive in RAM, while **multi-megabyte** blobs stress devices even for “small” logical updates.

This band is a design target derived from index-to-data ratio, I/O size, and
defragmentation cost — not a measured hard boundary. If benchmarking on your
hardware and workload shows a different range, replace it here with the
verified figures and note the test conditions. The internal
`aerospike/data-modeling-guide` repository holds the fuller treatment, including
the distinction between this target band, the configured `max-record-size`
limit, and the architectural ceiling.

**Prefer**

- **Single-digit KiB for the bulk of records**, with 1–128 KiB as the band that distribution spans; treat anything over ~**50 KiB** as a decision to justify rather than a default
- Splitting or denormalizing **huge** documents across keys when hot paths only need part of the data
- Capacity planning that includes **index RAM** (records × replicas × ~64 B) **and** **device throughput** for object size × QPS
- Coordinating with **operations** on **`read-page-cache`** and related **storage** settings when **read-heavy** access to the **same blocks** dominates latency (after confirming **namespace** layout and doc constraints)

**Avoid**

- Carrying **sizing intuition from other databases**: B-tree and document stores apply an incremental update without rewriting the whole object, and in-memory stores have no device I/O to amortize. Neither holds in Aerospike—every update rewrites the full record contiguously
- Assuming a **tiny** bin payload is “free” on the server—it still pays **index + full storage I/O** on access
- Expecting **`read-page-cache`** to fix **application-level** hot keys by itself—**shard or spread** keys where needed first
- **Megabyte-scale** records on **hot** keys without measuring **disk** and **replication** cost

**See also**

- [single-record-operations.md](single-record-operations.md)
- [cdt-bounded-collections.md](cdt-bounded-collections.md)
- [model-access-paths-denormalization.md](model-access-paths-denormalization.md)
- [model-hot-keys.md](model-hot-keys.md)
