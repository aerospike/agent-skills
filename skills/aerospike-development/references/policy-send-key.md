---
title: Understand sendKey when the stored user key matters
impact: MEDIUM
tags: policy, send-key, primary-key, secondary-index
doc: https://aerospike.com/docs/database/learn/policies/
also:
  - https://aerospike.com/docs/develop/learn/policies
last_verified: 2026-04-21
---

## Understand sendKey when the stored user key matters

**Rule**

**`Policy.sendKey`** controls whether the client sends the **user-defined key** alongside the digest on reads and writes. If enabled on a **write**, the key is **stored with the record** and can be returned on reads and secondary-index queries that surface keys. Once stored, it **persists** until the record is deleted—even if later writes omit **sendKey**—unless your application replaces behavior per doc.

**Why**

The server indexes by digest; without storing the key, APIs that need the original key value may not have it. Secondary-index and query workflows that return human-readable keys depend on this. See [Policies — Send Key](https://aerospike.com/docs/database/learn/policies/).

How often a write **reads** an existing record depends on **`recordExistsAction`** when **sendKey** is off—see [policy-replace-whole-record.md](policy-replace-whole-record.md). For example, **`REPLACE`** / **`REPLACE_ONLY`** can skip that read. With **sendKey** on, the server still **reads** the record when one exists so it can **verify the sent user key against the digest** (and persist or update the stored key)—even when the exist action would otherwise avoid a merge read.

**Prefer**

- Enabling **sendKey** when queries or clients must recover the **original key** field
- Consistent policy for creates vs updates if your access pattern assumes the key is present

**Avoid**

- Assuming the key is stored without **sendKey** on the write path that created the record
- Relying on sendKey toggles to “remove” a stored key without understanding persistence semantics

**See also**

- [policy-replace-whole-record.md](policy-replace-whole-record.md)
- [query-secondary-index-discipline.md](query-secondary-index-discipline.md)
- [single-record-operations.md](single-record-operations.md)
