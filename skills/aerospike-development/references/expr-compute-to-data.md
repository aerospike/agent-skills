---
title: Use filter and operation expressions for compute-to-data
impact: HIGH
tags: expressions, udf, server-side
doc: https://aerospike.com/docs/develop/expressions/path/
also:
  - https://aerospike.com/docs/develop/learn/bin-operations/
last_verified: 2026-04-21
---

## Use filter and operation expressions for compute-to-data

**Rule**

Use filter expressions and operation expressions (and path expressions for nested bins) to evaluate and update data on the server when they fit the problem. Reach for Lua UDFs only when expressions cannot express the logic or product guidance requires server-side procedures.

**Why**

Expressions are integrated with record operations and avoid shipping large payloads to the client for simple predicates or field updates. UDFs add operational and versioning considerations.

**Prefer**

- Predicates and updates expressible as expressions
- Path expressions for nested map/list updates where supported

**Avoid**

- UDF for arithmetic or filters that expressions cover

**See also**

- [cdt-nested-collections.md](cdt-nested-collections.md)
- [cdt-server-side-ops.md](cdt-server-side-ops.md)
- [Nested collection data types](https://aerospike.com/docs/develop/expressions/nesting)
- [Path expressions](https://aerospike.com/docs/develop/expressions/path/)
