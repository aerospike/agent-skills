---
title: Reuse policies and set explicit timeouts and retries
impact: HIGH
tags: policy, timeouts, retries, socket-timeout, total-timeout, max-retries, idempotent, timeout-delay
doc: https://aerospike.com/docs/database/learn/policies/
also:
  - https://aerospike.com/docs/develop/client/java/policies/
  - https://aerospike.com/docs/database/manage/cluster/smd-readiness
last_verified: 2026-10-01
---

## Reuse policies and set explicit timeouts and retries

**Rule**

Reuse read/write/operate policy objects (or set defaults on the client) instead of allocating new policy instances on hot paths. Configure **socket timeout**, **total timeout**, and **retry** behavior appropriate to the operation class (single-key vs batch vs query).

**Socket vs total:** **Socket timeout** is idle time on the connection while a command runs; when it fires, the client may retry if **maxRetries** and **totalTimeout** allow. **Total timeout** caps the whole attempt end-to-end on the client and is sent to the server. If both are non-zero and socket exceeds total, the client clamps socket to total. **Total timeout 0** means no client-side total limit—the server applies its default—see [Policies](https://aerospike.com/docs/database/learn/policies/).

**Retries and defaults:** Client defaults differ by operation class: **reads** typically allow **2** retries (initial attempt plus two retries—three tries total); **writes**, **queries**, and **scans** typically default to **0** retries. Confirm in your SDK—do not assume writes retry like reads.

**Non-idempotent writes**—such as numeric **add** or other operations unsafe if applied twice—must use **`maxRetries` 0** on a dedicated **WritePolicy** so a timeout cannot double-apply the mutation ([Policies — Max Retries](https://aerospike.com/docs/database/learn/policies/)).

**Sleep between retries (`sleepBetweenRetries`):** Sleep runs only on **connection errors** and **server timeouts** that suggest a node is down and the cluster is reforming—it does **not** run merely because the client’s **socketTimeout** (idle) fired. **`sleepBetweenRetries` is ignored** when **`maxRetries` is 0** and **ignored in async mode**. For **writes** with **`maxRetries` > 0**, set sleep high enough for the cluster to reform (often **≥ 500 ms** per [Policies](https://aerospike.com/docs/database/learn/policies/)).

**Why**

**Timeout delay (`timeoutDelay`):** Some clients expose a **grace period after a timeout** before tearing down the socket: the app still receives the timeout immediately, but the client may **hold the connection** briefly in case a **late response** arrives—then it can return the connection to the pool instead of closing it. This matters most when new connections are expensive (for example **TLS** handshakes); see [sec-client-tls-auth.md](aerospike-development-sec-client-tls-auth.md). Confirm field names in your SDK ([Java policies](https://aerospike.com/docs/develop/client/java/policies/) describe the idea).

Per-call policy allocation adds GC pressure in managed languages and obscures which timeouts apply. Network-heavy or large scans need different limits than single-key gets. Wrong retry settings on non-idempotent operations cause duplicate side effects.

On Database 8.2.0 and later, a node that is joining or restarting completes the TCP handshake and then answers nothing until its initial system metadata (SMD) sync finishes, so requests to it time out instead of being refused. The wait applies only once every node runs 8.2.0 or later and has no timeout of its own, and the last node upgraded from an earlier release is the first to wait.

**Prefer**

- Client-level or module-level default policies
- Explicit timeouts for batch and query workloads
- **`maxRetries` 0** on write policies for non-idempotent operations
- Understanding **`totalTimeout` 0** vs server default before tuning latency
- Knowing read vs write **default retries** when debugging duplicate or missing effects
- On Database 8.2.0 and later, retry decisions that branch on `(status, subcode)`: `AS_ERR_UNAVAILABLE` (11) separates unresolved initial partition balance, an unavailable replica and a node that is shutting down; enable error details per [policy-client-defaults.md](aerospike-development-policy-client-defaults.md)

**Avoid**

- Relying on implicit defaults for long-running operations
- New policy objects inside tight loops
- Retrying writes that are not safe to repeat without idempotency guarantees
- Expecting **`sleepBetweenRetries`** to run on every socket-idle timeout (see [Policies](https://aerospike.com/docs/database/learn/policies/) semantics)
- Treating a successful TCP connection to a node, or its `service ready` log line, as proof an 8.2.0 node answers requests: the `initial SMD sync done` log line, or a request that completes, is the signal

**See also**

- [policy-write-commit-level.md](aerospike-development-policy-write-commit-level.md)
- [policy-generation-cas.md](aerospike-development-policy-generation-cas.md)
- [policy-replace-whole-record.md](aerospike-development-policy-replace-whole-record.md)
- [policy-read-replica-consistency.md](aerospike-development-policy-read-replica-consistency.md)
- [policy-explicit-defaults.md](https://github.com/aerospike/agent-skills/blob/main/skills/aerospike-development/examples/policy-explicit-defaults.md)
- [policy-client-defaults.md](aerospike-development-policy-client-defaults.md)
- [sec-client-tls-auth.md](aerospike-development-sec-client-tls-auth.md)
- [System metadata readiness on node join](https://aerospike.com/docs/database/manage/cluster/smd-readiness)
