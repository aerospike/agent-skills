---
title: Set read replica, AP read mode, and SC read mode to match namespace semantics
impact: HIGH
tags: policy, replica, read-mode-ap, read-mode-sc, consistency
doc: https://aerospike.com/docs/database/learn/policies/
also:
  - https://aerospike.com/docs/develop/learn/policies
  - https://aerospike.com/docs/develop/learn/strong-consistency
last_verified: 2026-04-21
---

## Set read replica, AP read mode, and SC read mode to match namespace semantics

**Rule**

Configure **`Policy.replica`**, **`readModeAP`** (AP namespaces), and **`readModeSC`** (strong-consistency namespaces) so reads see the staleness and ordering guarantees your application needs. Defaults are not universally safe under migration or for hot keys—override deliberately.

**Replica** chooses which node serves a read (writes always go to the master for the partition). Options include **SEQUENCE** (try master, then replicas on retry), **MASTER**, **MASTER_PROLES** (round-robin across master and replicas—can spread load on **hot keys**), **RANDOM**, **PREFER_RACK**, etc. For **strong consistency**, the replica policy is **ignored** unless **SC read mode** is **ALLOW_REPLICA** or **ALLOW_UNAVAILABLE** (see [Policies](https://aerospike.com/docs/database/learn/policies/)).

**AP read mode:** **ONE** reads a single replica (default); during cluster **rebalance**, you may see a **stale** version. **ALL** consults all replicas holding the partition—more consistent under migration, higher cost. Namespace **`read-consistency-level-override`** can force behavior server-side.

**SC read mode:** **SESSION** and **LINEARIZE** enforce strict ordering of versions for the client or globally; **replica** is ignored. **ALLOW_REPLICA** / **ALLOW_UNAVAILABLE** relax guarantees and **combine with replica policy** for where reads may be served.

**Why**

Wrong read policies cause subtle staleness, extra load on the master, or unnecessary cross-replica reads. Hot keys benefit from spreading reads when the model allows (see doc tip on **MASTER_PROLES**).

**Prefer**

- **MASTER** or defaults when you need the simplest “read what the master has” mental model in AP
- **MASTER_PROLES** when read scaling on a hot key is worth distributing across master and replicas (and semantics allow)
- **ALL** in AP when stale reads during migration are unacceptable and cost is acceptable
- Aligning client policy with namespace mode (AP vs SC) and validating with [Strong consistency](https://aerospike.com/docs/develop/learn/strong-consistency) docs when in doubt

**Avoid**

- **RANDOM** unless replication factor matches cluster topology as the doc recommends
- Assuming **ONE** is always fresh while partitions are migrating

**See also**

- [policy-reuse-timeouts-retries.md](policy-reuse-timeouts-retries.md)
- [single-ttl-nsup-default-ttl.md](single-ttl-nsup-default-ttl.md) (read-touch TTL and reads)
- [binop-operate-atomicity.md](binop-operate-atomicity.md)
