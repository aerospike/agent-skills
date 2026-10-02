---
title: Use filter and operation expressions for compute-to-data
impact: HIGH
tags: expressions, udf, server-side, string
doc: https://aerospike.com/docs/develop/expressions/path/
also:
  - https://aerospike.com/docs/develop/learn/bin-operations/
  - https://aerospike.com/docs/develop/data-types/string
  - https://aerospike.com/docs/develop/data-types/string/regex-syntax
  - https://aerospike.com/docs/database/advanced/special-upgrades/820-upgrade#string-operations-and-utf-8-validation
  - https://aerospike.com/docs/database/advanced/udf/security
last_verified: 2026-10-01
---

## Use filter and operation expressions for compute-to-data

**Rule**

Use filter expressions and operation expressions (plus path expressions for nested bins and, from Database 8.2.0, string operations for text) to evaluate and update data on the server when they fit the problem. Reach for Lua UDFs only when expressions cannot express the logic or product guidance requires server-side procedures. String operations need Database 8.2.0 on every node and a client version that supports them ([feature compatibility matrix](https://aerospike.com/docs/develop/client-matrix#full-clientserver-feature-compatibility)); an older node answers with a generic parameter error, so check the cluster build rather than branching on the error.

**Why**

Expressions are integrated with record operations and avoid shipping large payloads to the client for simple predicates or field updates. UDFs add operational and versioning considerations.

A string operation transforms text in place on the server, which removes a fetch-modify-write round trip. String modify operations return no value, and a suppressed one looks identical to an applied one, so the response alone never confirms the change.

Database 8.2.0 also runs UDFs in a hardened Lua sandbox by default, because `mod-lua.allow-unsafe-lua` now defaults to `false`. The setting is static, so changing it takes a restart of each node, and during a rolling restart nodes disagree about it. Check which mode the target cluster runs before depending on a UDF.

**Prefer**

- Predicates and updates expressible as expressions
- Path expressions for nested map/list updates where supported
- String operations on 8.2.0 and later for text transforms (substring, search, case, trim, pad, replace, split, regex and conversion) instead of get, edit, put
- A read of the same bin in the same `operate` to get the transformed text, because string modify operations return no value
- `normalize_nfc` on write, or on both sides of a comparison, when text can arrive in mixed Unicode forms: search operations treat canonically equivalent spellings as equal, but expression comparison orders by UTF-8 bytes
- A bin-type filter expression to guard a string write when the bin's type is not certain
- Passing the values a UDF needs, such as the current time, from the client as arguments, because `os.time()` is a runtime error under the hardened default

**Avoid**

- UDF for arithmetic, filters or text transforms that expressions or string operations cover
- UDFs on 8.2.0 and later that call `os`, `io`, `debug`, `dofile`, `loadfile`, `load` or `loadstring`, ship a native `.so` module or precompiled bytecode, or register under an uppercase `.LUA` extension, unless operations has set `mod-lua.allow-unsafe-lua` to `true`
- Counting string positions or lengths in bytes: string operations count Unicode codepoints
- Expecting `NO_FAIL` to cover a non-String bin, invalid UTF-8 or malformed arguments: it suppresses none of them, and where it does suppress a failure (the 8 MiB result cap, for example) the call succeeds and leaves the bin unchanged
- String operations on legacy bins that may hold invalid UTF-8: plain writes accept it, but an operation rejects it with `AS_ERR_INVALID_ENCODING` (29) and a filter expression silently drops the record
- PCRE or the legacy POSIX `cmp_regex` syntax in string regex: 8.2.0 uses ICU, and patterns past its evaluation limits fail with `AS_ERR_OP_NOT_APPLICABLE`
- Passing write flags where regex flags belong, or the reverse: both are integers, so the wrong one is accepted and silently changes behavior

**See also**

- [cdt-nested-collections.md](cdt-nested-collections.md)
- [cdt-server-side-ops.md](cdt-server-side-ops.md)
- [Nested collection data types](https://aerospike.com/docs/develop/expressions/nesting)
- [Path expressions](https://aerospike.com/docs/develop/expressions/path/)
- [String operations](https://aerospike.com/docs/develop/data-types/string)
- [Regular expression syntax](https://aerospike.com/docs/develop/data-types/string/regex-syntax)
- [Upgrade to Database 8.2.0: string operations and UTF-8 validation](https://aerospike.com/docs/database/advanced/special-upgrades/820-upgrade#string-operations-and-utf-8-validation) (finding and repairing legacy bins)
- [UDF security and sandbox hardening](https://aerospike.com/docs/database/advanced/udf/security)
