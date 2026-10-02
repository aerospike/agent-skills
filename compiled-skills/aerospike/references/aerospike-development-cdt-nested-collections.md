---
title: Model nested lists and maps with CDT context, ordering, and expressions
impact: HIGH
tags: cdt, nesting, map, list, context, k-order, path-expressions
doc: https://aerospike.com/docs/develop/expressions/nesting
also:
  - https://aerospike.com/docs/develop/expressions/path/
  - https://aerospike.com/docs/develop/data-types/collections/context
  - https://aerospike.com/docs/develop/data-types/collections/map#element-ordering
  - https://aerospike.com/docs/develop/client-matrix#full-clientserver-feature-compatibility
last_verified: 2026-10-01
---

## Model nested lists and maps with CDT context, ordering, and expressions

**Rule**

When you store **lists of maps**, **maps of lists**, or deeper nesting, use the official patterns in [Working with nested collection data types](https://aerospike.com/docs/develop/expressions/nesting): **CDT `operate` APIs** with [context](https://aerospike.com/docs/develop/data-types/collections/context/) where you address a single slot, **expression composition** (`ListExp` / `MapExp`) for filters and computed reads, and **[path expressions](https://aerospike.com/docs/develop/expressions/path/)** (`selectByPath` / `modifyByPath`) when you traverse or change **multiple** nested elements in one shot. **Path expressions require Aerospike Database 8.1.2 or later**; use a **client version** that supports them ([feature compatibility matrix](https://aerospike.com/docs/develop/client-matrix#full-clientserver-feature-compatibility)). Build **K-ordered** maps (or the client equivalent) for CDT performance on every version. Below 8.2.0 they are also needed whenever the server must compare whole map values, such as `ADD_UNIQUE` on a list of vehicle maps; from 8.2.0 the server compares maps by content whatever their ordering, and the arguments need not be K-ordered.

**Why**

On servers below 8.2.0, unordered map construction from the client can omit the K-ordered flag or reorder keys so equality checks against stored maps fail; from 8.2.0 equality is by content, and K-ordered maps remain recommended for performance. Deep nesting increases record size and operation cost; the nesting guide explains list ordering choices (e.g. unordered list with semantic index positions) versus map key order.

**Prefer**

- One `operate` call with `ListOperation` / `MapOperation` and explicit list/map policies
- **Sorted** maps and **ordered** unique lists where semantics allow—**better CDT performance**; see [cdt-server-side-ops.md](aerospike-development-cdt-server-side-ops.md)
- Language-specific **ordered** map types (`TreeMap`, `KeyOrderedDict`, sorted `MapPair` slices in Go, etc.) to build K-ordered maps
- The nesting guide’s full page for read/filter/index/query examples beyond a single insert

**Avoid**

- **Path expression** APIs on clusters **below 8.1.2** (use context + `ListOperation` / `MapOperation` / composed expressions instead)
- Treating nested bins like JSON blobs updated only via full-record `get`/`put` under contention
- Relying on duplicate suppression for list-of-maps on servers below 8.2.0 if maps are not built in the **ordered** form the server compares
- Nesting deeper than 64 levels on 8.2.0 and later; see [cdt-nesting-depth-limit.md](aerospike-development-cdt-nesting-depth-limit.md)

**See also**

- [cdt-map-nested-vehicles.md](https://github.com/aerospike/agent-skills/blob/main/skills/aerospike-development/examples/cdt-map-nested-vehicles.md)
- [cdt-list-append.md](https://github.com/aerospike/agent-skills/blob/main/skills/aerospike-development/examples/cdt-list-append.md)
- [cdt-server-side-ops.md](aerospike-development-cdt-server-side-ops.md)
- [cdt-bounded-collections.md](aerospike-development-cdt-bounded-collections.md)
- [cdt-nesting-depth-limit.md](aerospike-development-cdt-nesting-depth-limit.md)
- [expr-compute-to-data.md](aerospike-development-expr-compute-to-data.md)
