---
title: Choose write commit level deliberately (COMMIT_ALL vs COMMIT_MASTER)
impact: HIGH
tags: policy, write, commit-level, replication, ap, strong-consistency
doc: https://aerospike.com/docs/database/learn/policies/
also:
  - https://aerospike.com/docs/develop/learn/policies
last_verified: 2026-04-21
---

## Choose write commit level deliberately (COMMIT_ALL vs COMMIT_MASTER)

**Rule**

**`WritePolicy.commitLevel`** controls when the client gets success after a write:

| Level | Behavior |
|--------|----------|
| **`COMMIT_ALL`** (default) | Success after **all replicas** have the write—stronger durability before ack. |
| **`COMMIT_MASTER`** | Success after the **master** only; replicas catch up **asynchronously**—**lower latency**, but replicas can **lag**. |

**Strong-consistency (SC) namespaces require `COMMIT_ALL`**; otherwise writes fail. Server backpressure can still force **`COMMIT_ALL`** under load. Namespace **`write-commit-level-override`** may override the client (see [Policies](https://aerospike.com/docs/database/learn/policies/)).

**AP mode and `COMMIT_MASTER`:** Lag can show up as **inconsistent** views between master and a replica (e.g. read from a replica that has not applied the write yet). Use **`COMMIT_MASTER`** only when that **skew is acceptable**. In AP, it also **relaxes the usual replication network throttle**, so **sustained high throughput** can **saturate** links and surface **throttle/saturation errors**—capacity and monitoring matter; fall back toward **`COMMIT_ALL`** if needed.

**Why**

`COMMIT_MASTER` trades **replica freshness** (and built-in pacing) for **speed**. That is a real **consistency and load** tradeoff in AP, not a free latency win.

**Prefer**

- **`COMMIT_ALL`** for SC namespaces and when you need the write **durable on replicas** before the client proceeds
- **`COMMIT_MASTER`** in AP only when **replica lag** or **stale replica reads** are **acceptable**

**Avoid**

- **`COMMIT_MASTER`** in **SC** namespaces (invalid)
- **`COMMIT_MASTER`** in AP when the app **cannot** tolerate lag or stale replica reads
- **`COMMIT_MASTER`** in AP at **extreme** sustained write rates **without** headroom—watch for **network saturation**

**See also**

- [policy-read-replica-consistency.md](policy-read-replica-consistency.md)
- [policy-reuse-timeouts-retries.md](policy-reuse-timeouts-retries.md)
- [policy-generation-cas.md](policy-generation-cas.md) (orthogonal: optimistic concurrency on writes)
