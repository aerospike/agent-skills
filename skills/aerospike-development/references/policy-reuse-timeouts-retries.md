---
title: Reuse policies and set explicit timeouts and retries
impact: HIGH
tags: policy, timeouts, retries, socket-timeout, total-timeout, max-retries, idempotent, timeout-delay
doc: https://aerospike.com/docs/database/learn/policies/
also:
  - https://aerospike.com/docs/develop/learn/policies
  - https://aerospike.com/docs/develop/client/java/policies/
last_verified: 2026-04-21
---

## Reuse policies and set explicit timeouts and retries

**Rule**

Reuse read/write/operate policy objects (or set defaults on the client) instead of allocating new policy instances on hot paths. Configure **socket timeout**, **total timeout**, and **retry** behavior appropriate to the operation class (single-key vs batch vs query).

**Socket vs total:** **Socket timeout** is idle time on the connection while a command runs; when it fires, the client may retry if **maxRetries** and **totalTimeout** allow. **Total timeout** caps the whole attempt end-to-end on the client and is sent to the server. If both are non-zero and socket exceeds total, the client clamps socket to total. **Total timeout 0** means no client-side total limit—the server applies its default—see [Policies](https://aerospike.com/docs/database/learn/policies/).

**Retries and defaults:** Client defaults differ by operation class: **reads** typically allow **2** retries (initial attempt plus two retries—three tries total); **writes**, **queries**, and **scans** typically default to **0** retries. Confirm in your SDK—do not assume writes retry like reads.

**Non-idempotent writes**—such as numeric **add** or other operations unsafe if applied twice—must use **`maxRetries` 0** on a dedicated **WritePolicy** so a timeout cannot double-apply the mutation ([Policies — Max Retries](https://aerospike.com/docs/database/learn/policies/)).

**Sleep between retries (`sleepBetweenRetries`):** Sleep runs only on **connection errors** and **server timeouts** that suggest a node is down and the cluster is reforming—it does **not** run merely because the client’s **socketTimeout** (idle) fired. **`sleepBetweenRetries` is ignored** when **`maxRetries` is 0** and **ignored in async mode**. For **writes** with **`maxRetries` > 0**, set sleep high enough for the cluster to reform (often **≥ 500 ms** per [Policies](https://aerospike.com/docs/database/learn/policies/)).

**Timeout delay (`timeoutDelay`):** Some clients expose a **grace period after a timeout** before tearing down the socket: the app still receives the timeout immediately, but the client may **hold the connection** briefly in case a **late response** arrives—then it can return the connection to the pool instead of closing it. This matters most when new connections are expensive (for example **TLS** handshakes); see [sec-client-tls-auth.md](sec-client-tls-auth.md). Confirm field names in your SDK ([Java policies](https://aerospike.com/docs/develop/client/java/policies/) describe the idea).

**Why**

Per-call policy allocation adds GC pressure in managed languages and obscures which timeouts apply. Network-heavy or large scans need different limits than single-key gets. Wrong retry settings on non-idempotent operations cause duplicate side effects.

**Prefer**

- Client-level or module-level default policies
- Explicit timeouts for batch and query workloads
- **`maxRetries` 0** on write policies for non-idempotent operations
- Understanding **`totalTimeout` 0** vs server default before tuning latency
- Knowing read vs write **default retries** when debugging duplicate or missing effects

**Avoid**

- Relying on implicit defaults for long-running operations
- New policy objects inside tight loops
- Retrying writes that are not safe to repeat without idempotency guarantees
- Expecting **`sleepBetweenRetries`** to run on every socket-idle timeout (see [Policies](https://aerospike.com/docs/database/learn/policies/) semantics)

**See also**

- [policy-write-commit-level.md](policy-write-commit-level.md)
- [policy-generation-cas.md](policy-generation-cas.md)
- [policy-replace-whole-record.md](policy-replace-whole-record.md)
- [policy-read-replica-consistency.md](policy-read-replica-consistency.md)
- [ex-policy-explicit-defaults.md](ex-policy-explicit-defaults.md)
- [policy-client-defaults.md](policy-client-defaults.md)
- [sec-client-tls-auth.md](sec-client-tls-auth.md)
