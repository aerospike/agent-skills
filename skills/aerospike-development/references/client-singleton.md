---
title: Use one Aerospike client per process
impact: HIGH
tags: client, connection-pool, singleton
doc: https://www.aerospike.com/docs/develop/client/java/connect/
also:
  - https://aerospike.com/docs/develop/learn/policies
  - https://aerospike.com/docs/database/learn/policies/
  - https://aerospike.com/docs/develop/client/java/policies/
last_verified: 2026-04-21
---

## Use one Aerospike client per process

**Rule**

Instantiate the Aerospike client once per application process (or equivalent isolation boundary) and share it across threads/workers. Do not create and destroy a client per request.

**Why**

The client maintains connection pools to cluster nodes, background tending for topology changes, and other shared state. Per-request lifecycle causes socket churn, port exhaustion, repeated discovery work, and unstable latency.

**Prefer**

- A single global/module-level client initialized at startup
- Graceful `close` only on shutdown
- Explicit client logging in non-trivial deployments

**Avoid**

- `new client` / `connect` / `close` inside per-request handlers

**See also**

- [client-direct-node-access.md](client-direct-node-access.md)
- [client-pools-warmup.md](client-pools-warmup.md)
- [client-error-rate-backoff.md](client-error-rate-backoff.md)
- [policy-client-defaults.md](policy-client-defaults.md)
- [policy-reuse-timeouts-retries.md](policy-reuse-timeouts-retries.md)
- [ex-singleton-client-python.md](ex-singleton-client-python.md)
