---
title: Keep List and Map nesting within 64 levels
impact: HIGH
tags: cdt, nesting, depth-limit, upgrade, xdr
doc: https://aerospike.com/docs/develop/data-types/collections/#nesting-depth-limit
also:
  - https://aerospike.com/docs/database/advanced/special-upgrades/820-upgrade#cdt-nesting-depth-limit
  - https://aerospike.com/docs/database/release/8-2-0#cdt-nesting-depth-limited-to-64-levels
last_verified: 2026-10-01
---

## Keep List and Map nesting within 64 levels

**Rule**

On Database 8.2.0 and later, keep every List and Map value within 64 levels of nesting, counting the bin's top-level collection as level 1, because the server rejects a deeper value in any request. Values already stored deeper than 64 levels stay readable, but any request that sends one back is rejected, including a read-modify-write, an XDR shipment to a destination running 8.2.0 or later, and a restore of an older backup.

**Why**

Depth grows quietly: recursive trees and JSON-derived documents work until the first write after the upgrade, then fail on records that were valid before. The server checks depth when a value arrives, not when it is stored, and it does not scan stored data, so existing deep values stay hidden until something re-sends them. The check covers whole-bin writes, CDT operation values and context paths, and expression literals; `selectByPath` and `modifyByPath` also refuse a context deeper than 64.

The failure carries no subcode. A whole-bin write returns `AS_ERR_UNKNOWN` (1), and a CDT operation or an expression literal returns `AS_ERR_PARAMETER` (4). The text `list/map nested too deeply` reaches the client only at error-detail verbosity 2 or higher. When XDR ships such a record to an 8.2.0 or later destination the source abandons it rather than retrying. Some clients also enforce the limit themselves.

Most models stay within 2 to 4 levels. A node that holds a collection of its children spends two levels per tree level, so a recursive tree reaches the cap at roughly 30 tree levels, not 64. Depth also adds record size and operation cost, so a shallow model is the better design regardless of the cap.

**Prefer**

- Shallow models; when nesting grows, flatten it or split it across records per [model-bin-cdt-multiple-records.md](model-bin-cdt-multiple-records.md)
- An adjacency map keyed by node ID, one record per node, or one record per subtree for tree-shaped data
- Counting depth in the application before writing caller-supplied or JSON-derived values
- Flattening existing values deeper than 64 levels at the source before upgrading the cluster or an XDR destination; the server will not find them for you

**Avoid**

- Storing a recursive tree or an arbitrary JSON document as one nested value
- CDT context paths deeper than 64 levels, including ones that create levels with `MAP_KEY_CREATE` or `LIST_INDEX_CREATE`

**See also**

- [cdt-nested-collections.md](cdt-nested-collections.md)
- [cdt-bounded-collections.md](cdt-bounded-collections.md)
- [model-bin-cdt-multiple-records.md](model-bin-cdt-multiple-records.md)
- [model-access-paths-denormalization.md](model-access-paths-denormalization.md)
