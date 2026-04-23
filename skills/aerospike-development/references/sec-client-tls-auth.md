---
title: Terminate TLS and apply access credentials in the client
impact: MEDIUM
tags: security, tls, authentication
doc: https://aerospike.com/docs/develop/learn/security/
last_verified: 2026-04-21
---

## Terminate TLS and apply access credentials in the client

**Rule**

When the cluster requires TLS or access control, configure the client with the correct TLS context and credentials per official security guides—not custom shortcuts. Treat credentials as secrets; never embed them in repos.

**Why**

Misconfigured TLS or auth causes intermittent failures that look like “cluster flaps.” Security posture is a joint dev/ops concern; this rule covers **client-side** configuration only.

**Prefer**

- Follow the security docs for your client version
- Separate configs per environment

**Avoid**

- Disabling verification or using shared prod keys in dev without understanding risk

**See also**

- [reference.md](../reference.md) (documentation map)
