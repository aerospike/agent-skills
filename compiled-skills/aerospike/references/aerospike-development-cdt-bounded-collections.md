---
title: Keep lists and maps bounded
impact: HIGH
tags: cdt, record-size, list, map
doc: https://aerospike.com/docs/develop/data-types/collections/list
also:
  - https://aerospike.com/docs/develop/data-types/collections/map
last_verified: 2026-04-21
---

## Keep lists and maps bounded

**Rule**

Never grow lists or maps without bounds. Records have a maximum size; unbounded appends cause failures and hot records. Use trims, capped policies, rank/size-limited reads, or partition data across keys.

**Why**

CDTs make it easy to append; operations teams see incidents when “history” or “feed” bins grow without limits. Large records also increase migration and I/O cost.

**Prefer**

- Server-side ops that trim or cap (where your model allows)
- Separate keys or sets when history must be long-lived at scale

**Avoid**

- Unbounded `append` to lists in hot paths

**See also**

- [model-record-size-hardware-efficiency.md](aerospike-development-model-record-size-hardware-efficiency.md)
- [cdt-nested-collections.md](aerospike-development-cdt-nested-collections.md)
- [cdt-server-side-ops.md](aerospike-development-cdt-server-side-ops.md)
- [cdt-list-append.md](../examples/aerospike-development-cdt-list-append.md)
- [cdt-map-nested-vehicles.md](../examples/aerospike-development-cdt-map-nested-vehicles.md)
