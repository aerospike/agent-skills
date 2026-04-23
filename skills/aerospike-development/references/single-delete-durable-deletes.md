---
title: Use delete/remove correctly and opt into durable deletes when the app requires them
impact: HIGH
tags: delete, durable-delete, tombstone, enterprise
doc: https://aerospike.com/docs/develop/learn/single/#delete-a-record
also:
  - https://aerospike.com/docs/database/learn/architecture/durable-deletes
  - https://aerospike.com/docs/database/learn/policies/
last_verified: 2026-04-21
---

## Use delete/remove correctly and opt into durable deletes when the app requires them

**Rule**

Use the client’s **single-record delete** API (`delete` / `remove` per SDK) to remove a record by primary key, as described under [Delete a record](https://aerospike.com/docs/develop/learn/single/#delete-a-record). When deletes must **stay deleted across cold starts** and older on-disk versions must not **resurrect**, enable the **durable delete** flag on the **write policy** for that delete (and for any **write** or **`operate`** that removes the **last bin** and therefore deletes the record). **Durable deletes** are an **Enterprise Edition** capability: they generate a **tombstone** so conflict resolution and cold-start index rebuild behave correctly. The default client behavior keeps durable delete **off** for backward compatibility—turn it on explicitly where your correctness requirements need it.

**Why**

[Durable deletes](https://aerospike.com/docs/database/learn/architecture/durable-deletes) explains that without tombstones, deleted data can reappear when the primary index is rebuilt from storage. Tombstones consume index and storage resources; [capacity and tomb raider](https://aerospike.com/docs/database/learn/architecture/durable-deletes) behavior are operational concerns—link out rather than duplicating sizing here. Namespaces in **strong consistency** mode require durable deletes by default on the server; client policies must align with your namespace and edition.

In **strong consistency**, **regular** (non-durable) deletes—**expunges**—may be **blocked** unless the namespace allows them via **`strong-consistency-allow-expunge`** to relax that guarantee ([Policies — Durable Delete](https://aerospike.com/docs/database/learn/policies/)). Coordinate with operators before relying on plain deletes in SC.

**Prefer**

- Plain `delete` when resurrection on cold start is acceptable for the workload
- `durableDelete` / `durable_delete` (or equivalent) on the delete policy when you need tombstone semantics and run **Enterprise**
- Verifying server edition and namespace policy before relying on durable deletes in production

**Avoid**

- Assuming delete always creates a tombstone (it does **only** when durable delete is used appropriately on supported calls)
- Sending durable-delete policies to **Community Edition** servers (see compatibility in the architecture doc)
- Treating **SC** **expunge** semantics like AP without checking **`strong-consistency-allow-expunge`** and ops guidance

**See also**

- [single-ttl-expiration-retention.md](single-ttl-expiration-retention.md)
- [single-ttl-nsup-default-ttl.md](single-ttl-nsup-default-ttl.md)
- [single-record-operations.md](single-record-operations.md)
- [binop-operate-record-lock-read-write.md](binop-operate-record-lock-read-write.md) (`operate` delete path)
- [policy-reuse-timeouts-retries.md](policy-reuse-timeouts-retries.md)
