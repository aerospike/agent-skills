---
title: Set client-level policy defaults per operation type
impact: MEDIUM
tags: policy, defaults, client-policy, batch-policy, scan, query
doc: https://aerospike.com/docs/database/learn/policies/
also:
  - https://aerospike.com/docs/develop/client/java/policies/
  - https://aerospike.com/docs/database/reference/error-details
  - https://aerospike.com/docs/database/reference/error-subcodes
last_verified: 2026-10-01
---

## Set client-level policy defaults per operation type

**Rule**

Aerospike clients let you attach **default policies** to the **client object** so API calls that pass **`null`** (or use implicit defaults) still get **predictable** timeouts, retries, and behavior. Defaults are usually **per operation family**: for example separate defaults for **single-record read**, **single-record write**, **scan**, **query**, and **batch**—confirm structure in your SDK.

**Batch** is special: the client often has a **base batch policy** for batch reads, plus **separate** default objects for **batch write**, **batch delete**, and **batch UDF**—they may **not** all inherit from one shared type. To set defaults correctly you must configure **each** flavor your app uses; do not assume changing one batch default covers all batch APIs.

**Why**

Implicit defaults differ between **reads** and **writes** and between **single-key** and **long-running** work (queries/scans). Misconfigured defaults show up as wrong timeouts on one path only, or batch writes behaving differently from batch reads.

Database 8.2.0 adds optional error details, which a client requests through a policy field (the name varies by client). Verbosity 0 returns the status alone, 1 adds a subcode, 2 adds a message, and 3 adds an expression trace for failures that involve an expression. The effective level is the lower of the client's level and the server's `error-details-max-verbosity`, which operations can lower, and the server omits the subcode when a failure has none worth dispatching on.

**Prefer**

- **Explicit** client-level defaults at startup for each operation class you rely on
- **Copy-from-default then mutate** patterns when overriding one field for a call (per SDK)
- Verifying **batch** default coverage for **read vs write vs delete vs UDF** if you use those APIs
- On Database 8.2.0 and later, error-detail verbosity 1 as a client default, with levels 2 and 3 only while debugging, because messages and traces can contain set names, bin names and record values
- Branching on the `(status, subcode)` pair, never on the subcode alone and never on message text, and testing for an absent subcode with the client's own idiom rather than comparing against 0

**Avoid**

- Relying on “global” policy defaults without checking **scan** vs **get** vs **batch** behavior
- Assuming all **batch** sub-policies inherit the same base—**check the docs**
- Showing error messages or traces to application end users who have no database access of their own

**See also**

- [client-singleton.md](client-singleton.md)
- [policy-reuse-timeouts-retries.md](policy-reuse-timeouts-retries.md)
- [batch-parallel-key-operations.md](batch-parallel-key-operations.md)
- [policy-explicit-defaults.md](../examples/policy-explicit-defaults.md)
- [Server error details](https://aerospike.com/docs/database/reference/error-details)
- [Error subcodes](https://aerospike.com/docs/database/reference/error-subcodes)
