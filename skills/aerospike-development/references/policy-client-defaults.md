---
title: Set client-level policy defaults per operation type
impact: MEDIUM
tags: policy, defaults, client-policy, batch-policy, scan, query
doc: https://aerospike.com/docs/database/learn/policies/
also:
  - https://aerospike.com/docs/develop/client/java/policies/
last_verified: 2026-04-21
---

## Set client-level policy defaults per operation type

**Rule**

Aerospike clients let you attach **default policies** to the **client object** so API calls that pass **`null`** (or use implicit defaults) still get **predictable** timeouts, retries, and behavior. Defaults are usually **per operation family**: for example separate defaults for **single-record read**, **single-record write**, **scan**, **query**, and **batch**—confirm structure in your SDK.

**Batch** is special: the client often has a **base batch policy** for batch reads, plus **separate** default objects for **batch write**, **batch delete**, and **batch UDF**—they may **not** all inherit from one shared type. To set defaults correctly you must configure **each** flavor your app uses; do not assume changing one batch default covers all batch APIs.

**Why**

Implicit defaults differ between **reads** and **writes** and between **single-key** and **long-running** work (queries/scans). Misconfigured defaults show up as wrong timeouts on one path only, or batch writes behaving differently from batch reads.

**Prefer**

- **Explicit** client-level defaults at startup for each operation class you rely on
- **Copy-from-default then mutate** patterns when overriding one field for a call (per SDK)
- Verifying **batch** default coverage for **read vs write vs delete vs UDF** if you use those APIs

**Avoid**

- Relying on “global” policy defaults without checking **scan** vs **get** vs **batch** behavior
- Assuming all **batch** sub-policies inherit the same base—**check the docs**

**See also**

- [client-singleton.md](client-singleton.md)
- [policy-reuse-timeouts-retries.md](policy-reuse-timeouts-retries.md)
- [batch-parallel-key-operations.md](batch-parallel-key-operations.md)
- [ex-policy-explicit-defaults.md](ex-policy-explicit-defaults.md)
