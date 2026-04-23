---
title: Draw namespace and set boundaries for retention, security, and operations
impact: HIGH
tags: modeling, namespace, set, sc, ttl, operations
doc: https://aerospike.com/docs/database/learn/architecture/data-storage/data-model
also:
  - https://aerospike.com/docs/operations
last_verified: 2026-04-23
---

## Draw namespace and set boundaries for retention, security, and operations

**Rule**

Use **one namespace** when a single set of cluster-scoped options (replication, strong consistency vs AP mode where applicable, default TTL, NSUP behavior) and one operational “slice” of data fits the workload. **Split into multiple namespaces** when you need different **retention/expiration policy**, different **consistency or replication expectations** that the product exposes at namespace level, or **isolation** for security, chargeback, or operational boundaries (for example different backup/restore or admin concerns). **Sets** group records within a namespace: treat them like **logical tables** or type groupings, not a substitute for key design. Do **not** use sets to solve cross-key transactions, joins, or independent tuning knobs that are actually namespace- or cluster-level; those belong in the model, operations hand-off, and official Operations docs.

**Why**

Namespace configuration binds deeply to how records expire, how the namespace is maintained, and how the cluster resources that namespace. Set boundaries affect query and index scope and developer ergonomics but do not add join semantics. Wrong boundaries create forced scans, muddled TTL/NSUP behavior, or operability pain.

**Prefer**

- **One namespace** for one **product domain** when options and ops model align
- **Clear set names** aligned with access paths and [primary-key design](model-access-paths-denormalization.md)
- **Explicit** TTL, default TTL, and NSUP alignment with the client; see [single-ttl-nsup-default-ttl.md](single-ttl-nsup-default-ttl.md) and [single-ttl-expiration-retention.md](single-ttl-expiration-retention.md)
- Asking **Operations** for **cluster-** and **node-level** placement, replication, and security when the split is for infra—not modeling it only in the app

**Avoid**

- **Many namespaces** “because we have many services” when a single namespace with sets and a consistent policy would suffice—each extra namespace adds operational surface
- **Treating a set** as a **shard** or **partitioning** mechanism; **user key** and partition distribution drive that, not the set name alone
- **Expecting** namespace or set to enforce **row-level** app security without **access control and TLS** configuration; see [sec-client-tls-auth.md](sec-client-tls-auth.md) and official Operations documentation for the deployment

**See also**

- [model-access-paths-denormalization.md](model-access-paths-denormalization.md) (namespace, set, and key in one path)
- [query-secondary-index-discipline.md](query-secondary-index-discipline.md) (index scope and cost)
- [reference.md](../reference.md) (official map toward Operations and server configuration)
