---
title: Design from access patterns, not from an entity list
impact: HIGH
tags: modeling, mental-model, record-size, access-patterns, batch
doc: https://aerospike.com/docs/database/learn/architecture/data-storage/data-model
last_verified: 2026-04-21
---

## Design from access patterns, not from an entity list

**Rule**

Derive the model from the read and write paths the application actually runs, never from an entity list or a normalized schema. Aerospike is neither a relational database nor a document database, and six properties decide every modeling choice that follows.

- **Records are semi-structured.** A record is a collection of strongly typed bins, typed per bin per record — there is no set-level schema. Two records in the same set can carry entirely different bins and the server enforces nothing. Absent bins cost nothing, so sparse and heterogeneous shapes are cheap. The consequence: the data model is an **application-level contract** — namespace, set, key format, bin names and bin types that every client agrees on — and nothing in the database stops a client writing a different shape. Write it down; that is what the schema guide is for.
- **Records are the unit of I/O.** Record data is stored contiguously, so every read fetches the entire record from storage and every write rewrites it — there are no in-place updates. Requesting a subset of bins trims what crosses the *network*, not what is read from *device*. A record in the tens of KiB spends tens of KiB of I/O on every access, however small the change. Record size is an I/O budget, not a storage number.
- **There are no server-side joins.** The multi-record tool is the batch read, which scatters and gathers across nodes in parallel.
- **Every record costs about 64 bytes of primary index metadata**, per replica, usually in RAM. Many tiny records spend more memory on index than on data.
- **Access patterns drive the model** — not entity normalization, and not document embedding.
- **Consolidate, but bound it.** Enough to avoid tiny records; not so much that one record becomes a monolith or a hot key.

**Why**

If your instinct is a table per entity and a row per sub-entity, or one giant embedded document, you will produce a bad Aerospike model. Both instincts come from systems that can join or index their way out of a poor layout; Aerospike cannot, so the layout has to match the access path from the start.

Record sizing has three bounds that are easy to conflate: the target band, the configured `max-record-size` limit, and the architectural ceiling. Do not carry a number from memory — read the current values from the data modeling guide (see [ex-guide-escalation.md](ex-guide-escalation.md)).

Whatever the band's endpoints are, read it as a **distribution, not a target**: design so the bulk of records sit at the low end (single-digit KiB), and treat the upper end as headroom for outliers and slowly-changing consolidated structures — 1:N and N:M relationship lists, where one record per edge would cost more. Size only hurts once multiplied by write frequency: a large record on a hot write path is a defect even when it fits, because every update rewrites it in full, while the same size where writes are infrequent relative to reads is a legitimate design rather than a compromise. Ask for the update rate, not just the byte count.

**Prefer**

- Enumerating read and write paths before naming a single set
- Treating the model as a written contract every client honours, since the server enforces none of it
- Asking for a record's **update rate** alongside its size
- Consolidating 1:N and N:M relationships into bounded collections rather than one record per edge

**Avoid**

- A set per entity and a record per sub-entity, which is a relational schema wearing different names
- One large embedded document per aggregate, which turns every read and write into full-record I/O
- Quoting a size band, `max-record-size`, or the architectural ceiling from memory — read the current values
- Judging a record size without its write frequency

**See also**

- [model-design-time-workflow.md](model-design-time-workflow.md)
- [model-failure-modes-checklist.md](model-failure-modes-checklist.md)
- [ex-guide-escalation.md](ex-guide-escalation.md)
