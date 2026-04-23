---
title: Use client error-rate backoff to protect the cluster under failure storms
impact: MEDIUM
tags: client, backoff, circuit-breaker, errors, max-error-rate
doc: https://aerospike.com/docs/database/learn/policies/
also:
  - https://aerospike.com/docs/develop/client/java/policies/
last_verified: 2026-04-21
---

## Use client error-rate backoff to protect the cluster under failure storms

**Rule**

Many Aerospike clients support **client-side error-rate limiting** (sometimes described as **backoff**): if a node returns **too many errors** within a **sliding window** of client tend iterations, the client **stops sending new commands** to that node until the error rate drops—surfacing a **backoff**-style exception to the application instead of hammering a sick node.

Typical knobs (names vary by SDK): a **maximum error count** per window and an **error-rate window** length (often measured in **tend intervals**). When the limit is **disabled** (zero / off), no backoff is applied.

**Why**

Under partial outages or misconfiguration, an unbounded client can amplify load on failing nodes and worsen cluster recovery. Backoff bounds blast radius and gives operators time to heal the cluster.

**Prefer**

- Enabling error-rate backoff for **large** or **autoscaled** app tiers sharing one cluster
- Pairing backoff awareness with **metrics and alerts** on the thrown exception class

**Avoid**

- Assuming every SDK exposes identical field names—**read your client’s policy docs**
- Treating backoff as a substitute for fixing **root cause** (network, capacity, config)

**See also**

- [client-pools-warmup.md](client-pools-warmup.md)
- [policy-reuse-timeouts-retries.md](policy-reuse-timeouts-retries.md)
- [client-direct-node-access.md](client-direct-node-access.md)
