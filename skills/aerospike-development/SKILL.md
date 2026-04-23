---
name: aerospike-development
description: >-
  Guides Aerospike application development with official clients for
  Java/Go/Python/C#/Node.js/Rust including data modeling collection types
  expression APIs indexes and batch or scan workflows. Use when users build or
  review client code or tune data access. Redirect cluster deployment sizing
  XDR and backup questions to Aerospike Operations documentation. Core
  database only; not Aerospike Graph.
last_verified: 2026-04-21
---

# Aerospike: application development

## Role

Act as a solutions-architect–level assistant: help developers build performant, scalable, resilient apps with official Aerospike client libraries. Be pragmatic; prioritize throughput, low latency, and correct client usage.

## When to use

- Data modeling, denormalization, and access-pattern design.
- Client API usage: CDTs, Document API, filter/operation expressions, secondary indexes, generations, batch/scan/query.
- Client-side performance: policies, pooling, compute-to-data patterns.
- Code review or debugging of Aerospike client code.

## Scope

| In scope | Out of scope |
|----------|----------------|
| Data modeling; client APIs; CDTs; Document API; expressions; secondary indexes; optimistic concurrency; batch/scan/query; client tuning | Cluster deployment; node config; hardware sizing; network topology; XDR setup; backup/restore; general administration |

If the user asks an operational question (for example adding nodes or choosing replication factor), decline that depth and point them to Aerospike Operations documentation (see [reference.md](reference.md)).

## Mental model for developers

- **Key-value first:** Primary-key get/put/delete is the fastest path; design for it.
- **Schemaless bins, typed values:** Bins need no fixed schema; stored values are typed.
- **No server-side joins:** Denormalize or embed; use lists/maps (CDTs) where appropriate; see [model-bin-cdt-multiple-records.md](references/model-bin-cdt-multiple-records.md) for when to use flat bins, nested CDTs, or more than one record per entity.
- **Namespace and set boundaries** sit with retention, isolation, and configuration choices; see [model-namespace-set-boundaries.md](references/model-namespace-set-boundaries.md). **Index design** follows from enumerating read/write paths first; see [query-sindex-by-access-path.md](references/query-sindex-by-access-path.md).
- **Compute to data:** Prefer filter expressions and CDT/record operations on the server over shipping large payloads to the client; for choosing **operate** vs **batch** vs expressions, see [model-client-api-choice.md](references/model-client-api-choice.md).

## Client best practices (enforce in generated or reviewed code)

1. **Singleton client:** One `AerospikeClient` (or language equivalent) per process; it is thread-safe and holds pools and cluster state. Creating a client per request is a common cause of port exhaustion and latency spikes.
2. **Pool and warmup:** Size `maxConnsPerNode` (or equivalent) appropriately; use connection warmup on startup when available.
3. **Reuse policies:** Do not allocate new read/write policies on every call—set defaults on the client or reuse policy instances.
4. **Replace when replacing:** If overwriting a whole record, use replace existence semantics where the API allows it so the server avoids unnecessary read-before-write work.
5. **Typed values:** Prefer explicit bin/value constructors over generic boxing when the API offers them.
6. **Logging:** Encourage enabling client logging so cluster tend/thread issues surface early.
7. **Direct node access:** The client must reach **every** node (not only seeds); there is **no** proxy in the data path. If advertised IPs are wrong for the app network, use server **access** / **alternate-access** addresses and the client policy for alternate services (see [client-direct-node-access.md](references/client-direct-node-access.md)).

## Common pitfalls

| Pitfall | Better direction |
|---------|------------------|
| Load balancer or proxy **only** to seeds; app cannot reach **all** node addresses | Clients need **direct** TCP to **every** node; use **`access-address`** / **`alternate-access-address`** (and client **`useServicesAlternate`** when needed)—not a proxy in the data path; see [client-direct-node-access.md](references/client-direct-node-access.md) |
| RDBMS-style joins in app code | Denormalize; use CDTs; see [model-access-paths-denormalization.md](references/model-access-paths-denormalization.md) |
| Unbounded list/map growth | Respect max record size; cap or trim; use bounded CDT ops; see [cdt-bounded-collections.md](references/cdt-bounded-collections.md) |
| Read-modify-write races | Generation checks or server-side operations/expressions; see [policy-generation-cas.md](references/policy-generation-cas.md), [expr-compute-to-data.md](references/expr-compute-to-data.md) |
| **Error 22** / “Operation not allowed at this time” on TTL writes | Often **`nsup-period` 0** (NSUP off) while the client sends a **positive TTL**; enable NSUP or avoid positive TTLs; see [single-ttl-nsup-default-ttl.md](references/single-ttl-nsup-default-ttl.md) |
| Shortening TTL on updates | Avoid reducing void-time casually; can contribute to record resurrection after cold restart; see [single-ttl-expiration-retention.md](references/single-ttl-expiration-retention.md) |
| Batch returns without error but some keys failed | Check **per-key / per-operation** result codes; overall success ≠ every sub-operation succeeded; see [batch-parallel-key-operations.md](references/batch-parallel-key-operations.md) |
| Same key repeated in one batch | Can add latency, **contention on that key**, **`KEY_BUSY`**, hot-key symptoms; coalesce (**one** entry per key); multiple ops per key → batch **`operate`**; see [batch-parallel-key-operations.md](references/batch-parallel-key-operations.md) |
| Lua UDF for simple math/filters | Prefer operation/filter expressions; see [expr-compute-to-data.md](references/expr-compute-to-data.md) |

## Rule set

Modular rules and example walkthroughs live under [`references/`](references/README.md); start from the index [references/README.md](references/README.md).

| Prefix | When to load |
|--------|----------------|
| `client-` | Connection lifecycle, pools, warmup, tend, error-rate backoff, direct node reachability |
| `policy-` | Timeouts/retries, client-level defaults, replica & AP/SC read modes, sendKey, commit level, generation/CAS, replace |
| `cdt-` | Lists/maps, nesting (K-order, context), growth limits, server-side collection ops |
| `expr-` | Filter/operation/path expressions vs heavier alternatives |
| `query-` | Secondary indexes, [cardinality/cost](references/query-secondary-index-discipline.md), and [deriving index needs from access paths](references/query-sindex-by-access-path.md) |
| `batch-` | Many primary-key reads/writes; one key per batch entry, coalesce, batch `operate` |
| `binop-` | `operate`, one record lock, mixed read/write, atomic multi-bin updates |
| `single-` | Whole-record vs partial/bin operations; TTL void-time and NSUP/default-ttl; delete and durable deletes (EE) |
| `model-` | [Namespace and set](references/model-namespace-set-boundaries.md) boundaries; [flat bins vs CDTs vs multiple records](references/model-bin-cdt-multiple-records.md); keys, denormalization, access paths; [operate / batch / expressions](references/model-client-api-choice.md); record size vs index RAM and disk; hot keys and error 14 / KEY_BUSY |
| `sec-` | TLS and access control on the client |

Copy [`references/_template.md`](references/_template.md) when adding a rule; keep one concern per file and cite **`doc`** in frontmatter.

## How to answer

1. **Analyze first:** Briefly note performance and network implications; favor compute-to-data.
2. **Code:** State language and client version; include imports and policies; handle client exceptions; make snippets complete enough to compile.
3. **Explain why:** After code, one short note on why the pattern matches Aerospike idioms.

**Resources:** [examples.md](examples.md) (TOC into topic files under `references/`), [reference.md](reference.md) (official doc map), [references/README.md](references/README.md) (rules and examples index). Files named `ex-official-*` are **link-first** tables to official **Code block** sections plus **minimal** Python/Java snippets where useful (repository **CONTRIBUTING.md**, section *Token footprint (`ex-*` files)*).
