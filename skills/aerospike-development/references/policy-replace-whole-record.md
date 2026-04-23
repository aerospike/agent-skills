---
title: Use replace semantics when overwriting an entire record
impact: MEDIUM
tags: policy, write, replace, record-exists-action
doc: https://aerospike.com/docs/database/learn/policies/
also:
  - https://aerospike.com/docs/develop/learn/policies
last_verified: 2026-04-21
---

## Use replace semantics when overwriting an entire record

**Rule**

Match **`recordExistsAction`** (or the SDK’s `WritePolicy` equivalent) to the real operation. When the application replaces **all** bins for a record (full overwrite), prefer **REPLACE** or **REPLACE_ONLY** so unspecified bins are removed; use **UPDATE** / **UPDATE_ONLY** / **CREATE_ONLY** when merge or insert-only semantics are intended.

**Why**

A blind full-record overwrite that behaves like “merge with existing” can force extra I/O and leave stale bins. The [Policies](https://aerospike.com/docs/database/learn/policies/) **Write mode** section defines each action.

**Prefer**

- **`CREATE_ONLY`** — insert; fail if the record exists
- **`UPDATE_ONLY`** — update; fail if missing; merges bins into existing
- **`UPDATE`** (common default) — upsert; merges bins if record exists
- **`REPLACE`** — create or replace whole record; drops bins not in this write
- **`REPLACE_ONLY`** — replace; fail if missing; drops bins not in this write
- Generation-guarded updates when you need CAS (see [policy-generation-cas.md](policy-generation-cas.md))

**Avoid**

- Default write modes chosen without matching access pattern
- Using **UPDATE** when you meant a full bin set replacement (use **REPLACE**)

**See also**

- [single-record-operations.md](single-record-operations.md)
- [policy-generation-cas.md](policy-generation-cas.md)
- [policy-reuse-timeouts-retries.md](policy-reuse-timeouts-retries.md)
