---
title: Do not shorten void-time carelessly—cold restart and retention semantics
impact: HIGH
tags: ttl, void-time, cold-start, retention, eviction, never-expire, delete
doc: https://aerospike.com/docs/database/manage/namespace/retention
also:
  - https://aerospike.com/docs/database/learn/architecture/durable-deletes
last_verified: 2026-04-21
---

## Do not shorten void-time carelessly—cold restart and retention semantics

**Rule**

**Do not reduce** a record’s remaining lifetime (**void-time**) on writes unless you intend it and accept cold-start risk. **Extending** void-time (later expiration, longer remaining TTL) is **fine** and does **not** cause the resurrection mismatch described below—the failure mode is **shortening** relative to older versions still on disk. To change bins only while keeping void-time, use **`-2`** on updates (see [single-ttl-nsup-default-ttl.md](single-ttl-nsup-default-ttl.md) for **`0` / `-1` / `-2`** and **NSUP**).

**Never-expire → finite TTL:** A record set to **never expire** (`-1`) is a long-lived commitment—**do not** later assign a **positive finite TTL** in normal paths; that is the same class of problem as shortening TTL for cold-start correctness. **Eviction** under pressure applies only to records with **non-zero void-time**; **never-expire** records are **not** eviction candidates—reclaim them with **delete** or other explicit strategies.

**Do not use a short TTL as a substitute for delete.** Use the client **delete** (and **durable delete** when needed—see [single-delete-durable-deletes.md](single-delete-durable-deletes.md)).

**Why**

On **cold restart**, the primary index is rebuilt from storage; **older versions** can remain until defragmentation overwrites them. If a **later** write **reduced** void-time but an **older** version still has a **later** void-time, that older version can **resurrect** after index rebuild. The server may mitigate some TTL reduction with **`apply-ttl-reduction`** (version specifics in the [retention](https://aerospike.com/docs/database/manage/namespace/retention) doc); application design should still avoid needless shortening. **Eviction** (when enabled) removes **non-zero void-time** records nearest expiration first. Expiration/eviction are **not** durable-delete tombstones—see [single-delete-durable-deletes.md](single-delete-durable-deletes.md).

**Prefer**

- Preserve void-time on updates unless shortening expiration is deliberate; clear **create vs update** policy
- Decide **finite TTL vs never-expire** per record and avoid flipping never-expire back to finite TTL except rare, deliberate migrations
- **Delete** for intentional removal; TTL for natural retention horizons

**Avoid**

- **Re-enabling expiration** on a never-expire record with a new positive TTL except deliberate, well-understood migrations
- Using **short TTL** instead of **delete** when you mean removal
- Routinely **smaller** TTL on every update to “refresh” without understanding void-time
- Expecting **eviction** to trim **never-expire** records
- Assuming expiration removed all on-disk history (vs **durable delete** semantics)

**See also**

- [single-ttl-nsup-default-ttl.md](single-ttl-nsup-default-ttl.md) (NSUP, **`default-ttl`**, error **22**, special TTL values)
- [single-record-operations.md](single-record-operations.md)
- [single-delete-durable-deletes.md](single-delete-durable-deletes.md)
- [policy-replace-whole-record.md](policy-replace-whole-record.md)
