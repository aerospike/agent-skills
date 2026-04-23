---
title: Know single-record CRUD vs bin-level operations
impact: MEDIUM
tags: single-record, crud, put, get, storage, record-size, metadata
doc: https://aerospike.com/docs/develop/learn/single/
last_verified: 2026-04-21
---

## Know single-record CRUD vs bin-level operations

**Rule**

Distinguish whole-record **put/get/delete** from **bin operations** and **`operate`**. Choose the narrowest API that matches the access pattern to limit data movement and clarify semantics.

**Server-side cost:** A **write** still **materializes the whole record** on the server for persistence: the engine typically **reads and rewrites** the full record image for that key, even for a **metadata-only** change (for example **TTL** / **touch** / read-touch behavior) or a **single-bin** `operate`. A “small” client operation is **not** necessarily a small amount of **disk or replication** work when the **record is large**—plan for full-record read/write cost at the storage layer unless you have measured otherwise for your deployment.

**Why**

Fetching or writing entire records when only one bin changes wastes bandwidth at the **client**. At the **server**, partial-looking updates can still imply **full-record** I/O for the stored object. Whole-record **put** semantics differ from merge/replace policies, but **record size** dominates cost for any write path.

**Prefer**

- `get`/`put` when the unit of work is the full record
- `operate` with bin ops when updating parts of a record or using CDTs
- **Smaller records** when the workload issues many **touch** / **TTL** / single-bin updates—large blobs amplify hidden full-record I/O

**Avoid**

- Habitual full-record reads for small field changes
- Assuming a **bin-level** or **TTL-only** API guarantees **partial** storage writes—it usually does **not** at the record level

**See also**

- [model-record-size-hardware-efficiency.md](model-record-size-hardware-efficiency.md)
- [single-ttl-expiration-retention.md](single-ttl-expiration-retention.md)
- [single-ttl-nsup-default-ttl.md](single-ttl-nsup-default-ttl.md)
- [single-delete-durable-deletes.md](single-delete-durable-deletes.md)
- [binop-operate-record-lock-read-write.md](binop-operate-record-lock-read-write.md)
- [binop-operate-atomicity.md](binop-operate-atomicity.md)
- [policy-replace-whole-record.md](policy-replace-whole-record.md)
