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
last_verified: 2026-04-21
---

## Model nested lists and maps with CDT context, ordering, and expressions

**Rule**

When you store **lists of maps**, **maps of lists**, or deeper nesting, use the official patterns in [Working with nested collection data types](https://aerospike.com/docs/develop/expressions/nesting): **CDT `operate` APIs** with [context](https://aerospike.com/docs/develop/data-types/collections/context/) where you address a single slot, **expression composition** (`ListExp` / `MapExp`) for filters and computed reads, and **[path expressions](https://aerospike.com/docs/develop/expressions/path/)** (`selectByPath` / `modifyByPath`) when you traverse or change **multiple** nested elements in one shot. **Path expressions require Aerospike Database 8.1.2 or later**; use a **client version** that supports them ([feature compatibility matrix](https://aerospike.com/docs/develop/client-matrix#full-clientserver-feature-compatibility)). Build **K-ordered** maps (or the client equivalent) when the server must compare whole map values—for example `ADD_UNIQUE` on a list of vehicle maps—so wire representation matches and duplicate detection works.

**Why**

Unordered map construction from the client can omit the K-ordered flag or reorder keys so equality checks against stored maps fail. Deep nesting increases record size and operation cost; the nesting guide explains list ordering choices (e.g. unordered list with semantic index positions) versus map key order.

**Prefer**

- One `operate` call with `ListOperation` / `MapOperation` and explicit list/map policies
- **Sorted** maps and **ordered** unique lists where semantics allow—**better CDT performance**; see [cdt-server-side-ops.md](cdt-server-side-ops.md)
- Language-specific **ordered** map types when the docs require them (`TreeMap`, `KeyOrderedDict`, sorted `MapPair` slices in Go, etc.)
- The nesting guide’s full page for read/filter/index/query examples beyond a single insert

**Avoid**

- **Path expression** APIs on clusters **below 8.1.2** (use context + `ListOperation` / `MapOperation` / composed expressions instead)
- Treating nested bins like JSON blobs updated only via full-record `get`/`put` under contention
- Relying on duplicate suppression for list-of-maps if maps are not built in the **ordered** form the server compares

**See also**

- [ex-cdt-map-nested-vehicles.md](ex-cdt-map-nested-vehicles.md)
- [ex-cdt-list-append.md](ex-cdt-list-append.md)
- [cdt-server-side-ops.md](cdt-server-side-ops.md)
- [cdt-bounded-collections.md](cdt-bounded-collections.md)
- [expr-compute-to-data.md](expr-compute-to-data.md)
