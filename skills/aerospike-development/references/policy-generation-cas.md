---
title: Use generation policy only for CAS (optimistic concurrency)
impact: HIGH
tags: policy, write, generation, cas, optimistic-lock
doc: https://aerospike.com/docs/database/learn/policies/
also:
  - https://aerospike.com/docs/develop/learn/policies
  - https://aerospike.com/docs/database/reference/error-codes/#server-errors
last_verified: 2026-04-21
---

## Use generation policy only for CAS (optimistic concurrency)

**Rule**

**`WritePolicy.generationPolicy`** is for **CAS**: **read** → **edit on the client** → **write** that must **fail** if the record changed meanwhile. You must use **`EXPECT_GEN_EQUAL`** / **`EXPECT_GEN_GT`** (names vary by SDK) and pass the **generation from the read** on the write. **`NONE`** skips the check—typical writes that are not read–modify–verify do **not** need this.

The server stores a per-record **generation** on writes; ordinary reads do not bump it. Treat it as an **opaque token for equality checks only**—**not** a count of mutations. Values can **wrap** (e.g. AP **64K**, SC **1K** updates) and are **not** guaranteed to increase by one per logical change—do **not** use generation for metrics, ordering, or “how many edits.”

**Read-touch** (TTL extension via **`readTouchTtlPercent`**) **does not advance generation**, so CAS that only compares generation can disagree with TTL changes ([Policies](https://aerospike.com/docs/database/learn/policies/); [single-ttl-nsup-default-ttl.md](single-ttl-nsup-default-ttl.md)). On mismatch the write fails with **`AS_ERR_GENERATION` (error 3)**.

When the generation check **fails**, **restart the whole read–modify–write**: **read the record again** (new generation and bins), **recompute** your change from that fresh state, then **write** with the new generation. Do **not** resend the previous write with a tweaked policy—the in-memory “modification” may be wrong once another writer has changed the record.

**Why**

Without **policy + generation from the same read**, you do not have CAS—only a blind write. Misinterpreting generation as a monotonic change counter breaks when the value wraps or skips.

**Prefer**

- **`EXPECT_GEN_*`** **and** the **generation field from the read** for client-side read–modify–write under contention (or use atomic **`operate`** / server-side updates when they cover the whole change)
- **Retry** after **`AS_ERR_GENERATION`** by repeating **read → manipulate → write** from scratch (not only re-issuing the write)

**Avoid**

- **Generation policy** without supplying the **read generation** on the write
- **CAS** that assumes **read-touch** always bumps **generation**
- **Treating generation as a change counter** (only **same-read equality** for CAS is valid)
- **Blind retries** of non-idempotent writes ([policy-reuse-timeouts-retries.md](policy-reuse-timeouts-retries.md))
- **Retrying only the write** after **`AS_ERR_GENERATION`** while reusing the **same client-side edit** computed from a stale read

**See also**

- [policy-replace-whole-record.md](policy-replace-whole-record.md)
- [binop-operate-atomicity.md](binop-operate-atomicity.md)
- [policy-write-commit-level.md](policy-write-commit-level.md) (orthogonal: commit level vs CAS)
