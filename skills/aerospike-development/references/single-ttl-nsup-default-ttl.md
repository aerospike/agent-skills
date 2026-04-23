---
title: Align client TTL with NSUP, default-ttl, and special write TTL values
impact: HIGH
tags: ttl, nsup, default-ttl, error-22, read-touch, retention
doc: https://aerospike.com/docs/database/manage/namespace/retention
also:
  - https://aerospike.com/docs/develop/learn/policies
  - https://aerospike.com/docs/database/learn/policies/
last_verified: 2026-04-21
---

## Align client TTL with NSUP, default-ttl, and special write TTL values

**Rule**

**Namespace Supervisor (NSUP)** must be configured consistently with how the app sends **TTL** on writes. When NSUP is enabled and the namespace allows TTL-backed writes, a **write** or **`Touch`** (or equivalent) that uses **client TTL `0`** tells the server to set void-time from **`default-ttl`**, with **set-level `default-ttl` overriding namespace** when both exist. **Each** such call can **re-apply** that horizon to the record; to change bins only without resetting void-time, use **`-2`** or an explicit TTL. **Reads** that extend TTL via **read-touch** use **`default-read-touch-ttl-pct`** and client read policies—that is **separate** from **`default-ttl`** on writes.

Know the **special client TTL values** the server understands (see [Configuring namespace data retention](https://aerospike.com/docs/database/manage/namespace/retention)): **`0`** → use `default-ttl` for void-time; **`-1`** → never expire (void-time 0); **`-2`** → on an **update**, do not change void-time (on a **create**, `default-ttl` applies). Positive integers are seconds until expiration from “now.”

If **NSUP is not running** (`nsup-period` 0, the default), the server **rejects writes that set a positive integer TTL** with **`AEROSPIKE_ERR_FAIL_FORBIDDEN`** (**error code 22**), often surfaced as **“Operation not allowed at this time”** (exact client string may vary). **`allow-ttl-without-nsup`** is for narrow/testing scenarios only. **Remediation:** run NSUP (`nsup-period` > 0) when the app uses positive TTLs, or stop sending positive TTLs until the namespace is configured for them.

**Why**

[Configuring namespace data retention](https://aerospike.com/docs/database/manage/namespace/retention) ties **expiration** and **eviction** to **NSUP** and documents client TTL behavior, **`default-ttl`**, and compatibility when NSUP is off. Expiring records need NSUP to scan for expired entries; read-touch and `apply-ttl-reduction` version specifics stay in the official doc. **TTL and touch-style updates still rewrite the full record** on the server for storage purposes—**large records** make “metadata-only” changes expensive; see [single-record-operations.md](single-record-operations.md).

**Prefer**

- **`nsup-period` > 0** when using **positive integer TTLs** on writes, unless operations explicitly align with the doc’s exceptions
- Knowing whether every write with **TTL `0`** re-bases the record to **`default-ttl`** (set vs namespace) before relying on “refresh” behavior
- Checking **`nsup-period`** when you see **error 22** on TTL writes before blaming application logic
- Using **`-2`** on updates when only bin data should change and void-time must stay as-is

**Avoid**

- Assuming **unspecified** client TTL behaves the same across SDKs—confirm whether the default maps to **`0`** (server `default-ttl`) or something else
- Conflating **read-touch** TTL extension with **`default-ttl`** on writes
- Using **`allow-ttl-without-nsup`** outside the doc’s intended testing-only scope

**See also**

- [single-ttl-expiration-retention.md](single-ttl-expiration-retention.md) (void-time shortening, cold restart, never-expire transitions)
- [single-record-operations.md](single-record-operations.md)
- [single-delete-durable-deletes.md](single-delete-durable-deletes.md)
