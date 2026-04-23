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

Each stored record costs about **64 bytes of RAM per replica** in the **primary index** (metadata to locate the object). **Hardware efficiency** depends on the **ratio** between **payload size** and that **fixed per-record overhead**: the **sweet spot** is often on the order of **a few kilobytes (roughly 1–10 KiB)** for many workloads, but it **depends on throughput**:

- **Oversized records** drive **disk bandwidth** hard—every read/write touches the full object on storage (see [single-record-operations.md](single-record-operations.md)).
- **Undersized records** (tiny values) mean you spend **a lot of memory on index entries** (many **64-byte** slots per gigabyte of “useful” data) and can push **RAM** limits before capacity.
- **Lower throughput** tolerates **larger** objects per key and stays efficient; **higher throughput** generally favors **smaller** objects in that **1–10 KiB** band so disk and replication keep up.

**Why**

Modeling ignores index overhead and device I/O until clusters hit **latency**, **device saturation**, or **memory for the index**. The **64-byte**-per-record **per replica** rule of thumb makes **micro-records** surprisingly expensive in RAM, while **multi-megabyte** blobs stress devices even for “small” logical updates.

**Prefer**

- **A few kilobytes per record** as a starting design point when it fits the access pattern; tune toward **smaller** objects when **read/write rates** rise
- Splitting or denormalizing **huge** documents across keys when hot paths only need part of the data
- Capacity planning that includes **index RAM** (records × replicas × ~64 B) **and** **device throughput** for object size × QPS
- Coordinating with **operations** on **`read-page-cache`** and related **storage** settings when **read-heavy** access to the **same blocks** dominates latency (after confirming **namespace** layout and doc constraints)

**Avoid**

- Assuming a **tiny** bin payload is “free” on the server—it still pays **index + full storage I/O** on access
- Expecting **`read-page-cache`** to fix **application-level** hot keys by itself—**shard or spread** keys where needed first
- **Megabyte-scale** records on **hot** keys without measuring **disk** and **replication** cost

**See also**

- [single-record-operations.md](single-record-operations.md)
- [cdt-bounded-collections.md](cdt-bounded-collections.md)
- [model-access-paths-denormalization.md](model-access-paths-denormalization.md)
- [model-hot-keys.md](model-hot-keys.md)
