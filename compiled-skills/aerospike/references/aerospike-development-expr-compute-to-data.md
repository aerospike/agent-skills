---
title: Use filter and operation expressions for compute-to-data
impact: HIGH
tags: expressions, udf, server-side
doc: https://aerospike.com/docs/develop/expressions/path/
also:
  - https://aerospike.com/docs/develop/learn/bin-operations/
  - https://aerospike.com/docs/develop/data-types/string
  - https://aerospike.com/docs/database/advanced/udf/security
last_verified: 2026-10-01
---

## Use filter and operation expressions for compute-to-data

**Rule**

Use filter expressions and operation expressions (and path expressions for nested bins) to evaluate and update data on the server when they fit the problem. Reach for Lua UDFs only when expressions cannot express the logic or product guidance requires server-side procedures. From Database 8.2.0, server-side string operations (substring, find, case, trim, replace and regex) cover text transforms as operations and expressions, so they no longer need a UDF or a client-side read-modify-write.

**Why**

Expressions are integrated with record operations and avoid shipping large payloads to the client for simple predicates or field updates. UDFs add operational and versioning considerations.

Database 8.2.0 also runs UDFs in a hardened Lua sandbox by default, because `mod-lua.allow-unsafe-lua` now defaults to `false`. The setting is static, so changing it takes a restart of each node, and during a rolling restart nodes disagree about it. Check which mode the target cluster runs before depending on a UDF.

**Prefer**

- Predicates and updates expressible as expressions
- Path expressions for nested map/list updates where supported
- Passing the values a UDF needs, such as the current time, from the client as arguments, because `os.time()` is a runtime error under the hardened default

**Avoid**

- UDF for arithmetic, filters or text transforms that expressions or string operations cover
- UDFs on 8.2.0 and later that call `os`, `io`, `debug`, `dofile`, `loadfile`, `load` or `loadstring`, ship a native `.so` module or precompiled bytecode, or register under an uppercase `.LUA` extension, unless operations has set `mod-lua.allow-unsafe-lua` to `true`

**See also**

- [cdt-nested-collections.md](aerospike-development-cdt-nested-collections.md)
- [cdt-server-side-ops.md](aerospike-development-cdt-server-side-ops.md)
- [Nested collection data types](https://aerospike.com/docs/develop/expressions/nesting)
- [Path expressions](https://aerospike.com/docs/develop/expressions/path/)
- [String operations](https://aerospike.com/docs/develop/data-types/string)
- [UDF security and sandbox hardening](https://aerospike.com/docs/database/advanced/udf/security)
