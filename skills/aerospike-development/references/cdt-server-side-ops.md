---
title: Prefer server-side CDT operations over read-modify-write
impact: HIGH
tags: cdt, operate, atomicity, ordering, sorted-map, unique-list
doc: https://aerospike.com/docs/develop/learn/bin-operations/
also:
  - https://aerospike.com/docs/develop/data-types/collections/list
  - https://aerospike.com/docs/develop/expressions/nesting
  - https://aerospike.com/docs/develop/client/java/policies/
last_verified: 2026-04-21
---

## Prefer server-side CDT operations over read-modify-write

**Rule**

For updates to lists, maps, or nested documents modeled in CDTs, use `operate` with CDT operations so work runs atomically on the server. Avoid get → mutate in app → put for contended data.

**List and map policies:** CDT APIs accept **policy objects** (names vary by SDK) that control **ordering**, **duplicate-key** behavior, and **write flags** for “key already exists” cases. Use explicit policies when defaults do not match your data model; see collection docs and your client’s **policies** overview ([Policies](https://aerospike.com/docs/database/learn/policies/)).

**Ordering and performance:** In general, prefer **sorted** maps (key-ordered / K-ordered semantics per the [map](https://aerospike.com/docs/develop/data-types/collections/map) docs) when the application can supply keys in a **stable sort order**. For **unique** lists, prefer an **ordered** list policy when semantics allow—**unordered** uniqueness is more expensive on the server. Both choices **improve performance** versus arbitrary order when your model does not require random key or insert order.

**Why**

Read-modify-write costs two round trips and loses races unless you add generation checks. Server-side ops reduce bandwidth and combine updates into one atomic step where the API allows. **Sorted maps** and **ordered unique lists** reduce work for the CDT engine when the access pattern matches.

**Prefer**

- **Sorted** maps by default unless the domain truly needs unsorted or arbitrary key order
- **Ordered** list + **unique**-list semantics when you need uniqueness and can assign index meaning (see [list](https://aerospike.com/docs/develop/data-types/collections/list) ordering options)
- `ListOperation` / `MapOperation` (or equivalent) via `operate`, with **list/map policy** and **write flags** chosen deliberately
- Generations when you truly need cross-bin transactional semantics in the client

**Avoid**

- Fetching entire large collections to append one element
- **Unordered** map or **unordered** unique-list policies when **sorted** / **ordered** would match the model and improve performance

**See also**

- [cdt-nested-collections.md](cdt-nested-collections.md)
- [cdt-bounded-collections.md](cdt-bounded-collections.md)
- [binop-operate-atomicity.md](binop-operate-atomicity.md)
- [ex-cdt-list-append.md](ex-cdt-list-append.md)
- [ex-cdt-map-nested-vehicles.md](ex-cdt-map-nested-vehicles.md)
- [policy-generation-cas.md](policy-generation-cas.md)
- [policy-client-defaults.md](policy-client-defaults.md)
