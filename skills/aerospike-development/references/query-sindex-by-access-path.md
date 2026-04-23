---
title: Derive secondary index needs from read and write access paths
impact: HIGH
tags: query, secondary-index, access-path, modeling
doc: https://aerospike.com/docs/develop/learn/queries/
also:
  - https://aerospike.com/docs/database/learn/architecture/data-storage/secondary-index
last_verified: 2026-04-23
---

## Derive secondary index needs from read and write access paths

**Rule**

Before adding a secondary index, **list access paths** (one line each: who reads, predicate, key known or not, latency budget). For each path: (1) **If the primary key is knowable,** use PK get/`operate`/[batch](batch-parallel-key-operations.md) first. (2) **If the path needs a duplicate of data** already stored elsewhere, **denormalize** to a key that already exists; see [model-access-paths-denormalization.md](model-access-paths-denormalization.md). (3) **Add a secondary index** only for predicates with **viable** cardinality and a **true query** path, per [query-secondary-index-discipline.md](query-secondary-index-discipline.md). (4) **Narrow the candidate set** with the index predicate; use **query + filter** for stricter server-side checks when the doc pattern fits. (5) **Re-fetch by PK** when the query should return or drive updates for specific keys—[sendKey](policy-send-key.md) if stored keys are required in results.

**Why**

Designing from paths avoids “index the column” thinking that creates high-cardinality, write-heavy, low-value indexes. The fastest work remains **one primary-key operation**; indexes are a **query** cost trade-off.

**Prefer**

- A short **ordered checklist** in design reviews: path → PK/denorm → sindex only if needed
- **Batch get** to hydrate rows after a query that returns key material you can use
- [policy-send-key.md](policy-send-key.md) when query APIs must return **user keys** that are not in bin values

**Avoid**

- An index per **field** that appears in **WHERE** in a relational dump without cardinality analysis
- **Query** as a substitute for **a known key**; redesign keys first

**See also**

- [query-secondary-index-discipline.md](query-secondary-index-discipline.md) (cardinality, cost, “not index everything”)
- [model-access-paths-denormalization.md](model-access-paths-denormalization.md) (key-first modeling)
- [model-bin-cdt-multiple-records.md](model-bin-cdt-multiple-records.md) (when the entity span affects query vs PK paths)
