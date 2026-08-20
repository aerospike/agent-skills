---
name: aerospike-data-modeling
description: >-
  Designs a new Aerospike data model from requirements, producing a schema guide
  and schema summary: record granularity, key design, bin structure, relationship
  and consolidation decisions, and index strategy. Use when no schema exists yet,
  when redesigning an existing model, or when reviewing a proposed schema for
  structural defects. This is design-time work that precedes code. For writing or
  reviewing client code against a model that already exists, or for client APIs,
  policies, CDT operations, and expression usage, use aerospike-development
  instead. Core database only; not Aerospike Graph.
license: Apache-2.0
metadata:
  last_verified: "2026-08-06"
  server_versions: "7.0+"
---

# Aerospike: data model design

## Role

Act as a data architect. Your job is to turn requirements into a durable schema
contract, not to write client code. The output is documents that a team reviews
and implements against.

## When to use this skill

Use it when the starting point is **requirements without a schema**:

- A new application or service with no Aerospike model yet.
- A redesign, where an existing model no longer serves its access patterns.
- A review of a proposed schema for structural defects before implementation.

**Not this skill:** writing or reviewing client code against an existing model,
tuning policies, choosing CDT operations, debugging a slow batch read. That is
`aerospike-development`. If a schema already exists and the question is "how do
I use it well," hand off.

## What you produce

Two documents. Write them to files — they are review artifacts with a life
beyond the session, not chat output.

| Deliverable | Contents |
|---|---|
| **Schema guide** | The full design: entity and relationship map, access pattern matrix, key schema, bin schema, one JSON example record per set, relationship and consolidation decisions, sizing worksheets, index rationale, growth and hot-key plan, validation plan. Plus the **reasoning** — an assumptions log, the alternatives rejected, and what evidence would reopen each decision. |
| **Schema summary** | The condensed contract derived from the guide: one table per set with key format, bins, types, and a one-line purpose; the index list; growth and overflow triggers. No rationale. |

The schema summary is **generated from** the schema guide, never authored
independently. If they disagree, the schema guide wins and the summary is
regenerated.

See [references/model-deliverables-schema-guide-summary.md](references/model-deliverables-schema-guide-summary.md).

## Mental model for data architects

Aerospike is neither a relational database nor a document database.

- **Records are semi-structured.** A record is a collection of **strongly typed
  bins**, and the typing is per bin per record — there is no set-level schema.
  Two records in the same set can have entirely different bins, and the server
  enforces nothing. Absent bins cost nothing, so sparse and heterogeneous shapes
  are cheap rather than wasteful. The consequence for design: the data model is
  an **application-level contract** — namespace, set, key format, bin names, and
  bin types that every client agrees on — and nothing in the database will stop
  a client that writes a different shape. Write the contract down; that is what
  the schema guide is for.
- **Records are the unit of I/O.** Record data is stored **contiguously**, so
  every read fetches the **entire record** from storage, and every write
  **rewrites the entire record** — Aerospike does not do in-place updates.
  Requesting a subset of bins trims what crosses the *network*, not what is read
  from *device*. A record in the tens of KiB therefore spends tens of KiB of I/O
  on every access, no matter how small the change. Record size is an I/O budget,
  not just a storage number.
- **There are no server-side joins.** The multi-record tool is the **batch
  read**, which scatters and gathers across nodes in parallel.
- **Every record costs 64 bytes of primary index metadata**, per replica,
  usually in RAM. Many tiny records spend more memory on index than on data.
- **Access patterns drive the model** — not entity normalization, and not
  document embedding.
- **Consolidate, but bound it.** Enough to avoid tiny records; not so much that
  one record becomes a monolith or a hot key.

If your instinct is a table per entity and a row per sub-entity, or one giant
embedded document, you will produce a bad Aerospike model.

**Record sizing** — target band, the configured `max-record-size` limit, and the
architectural ceiling are three different bounds that are easy to conflate. Do
not carry a number from memory; read the current values from the data modeling
guide (see Escalation below).

Whatever the band's endpoints are, read it as a **distribution, not a target**:
design so the **bulk of records sit at the low end** (single-digit KiB), and
treat the upper end as headroom for **outliers** and **slowly-changing
consolidated structures** — 1:N and N:M relationship lists, where one record per
edge would cost more. Size only hurts once multiplied by **write frequency**: a large record on a
**hot write path** is a design defect even when it fits, because every update
rewrites it in full — but the same size where writes are infrequent relative to
reads is a legitimate design, not a compromise. Ask for the **update rate**, not
just the byte count.

## Do not design without clarifying first

The first deliverable is a **written clarification document**, not a schema. Ask
requirements-gap questions — "what is the p95 fan-out?", "is eventual
consistency acceptable here?" — never mechanism-preference questions like "which
pattern do you prefer?". If deterministic guidance already resolves a choice,
apply it instead of asking.

Do not fill gaps with assumptions and continue. When entity ownership,
lifecycle, cardinality, or an access path is unclear, stop and ask. Where an
input cannot be obtained, record it as an explicit assumption with a reconsider
trigger rather than burying it.

Design **one entity group at a time** and pass its review before starting the
next. See [references/model-design-time-workflow.md](references/model-design-time-workflow.md).

## Failure modes to check while drafting

Seven ways Aerospike models go wrong. Check them **during** design, not after.
Each has a detection test in
[references/model-failure-modes-checklist.md](references/model-failure-modes-checklist.md).

1. **Record granularity comes from cardinality and who drives the read** — never
   from the entity list. One set per domain noun means the model came from an ER
   diagram.
2. **The most frequent reads must be key lookups or bounded batch reads.** If
   more than one or two access patterns resolve via secondary-index query, fix
   the keys, not the indexes.
3. **Single-element mutations happen server-side, in place.** Any
   read-modify-write of a whole bin should have been a CDT operation.
4. **A bin is a container, not a field.** Bin counts that scale with data rather
   than schema belong in one CDT bin. Bin names cap at 15 characters.
5. **Duplicate data deliberately** when two access patterns need it in two
   shapes. A second round trip purely to assemble a response is a normalization
   you should have collapsed.
6. **Every collection bin needs a growth ceiling and a decided behavior at it.**
   If element count is driven by user behavior rather than a design decision, it
   is unbounded.
7. **Small independent entities still need an explicit sizing decision.** Index
   overhead against a small payload is real cost; consolidating all of them into
   one record is the opposite error.

## Escalation: use the data modeling guide

This skill covers the decision layer. The full workflow — the clarification
gates, the per-relationship decision packs, the sizing worksheets, the
stakeholder checkpoints — lives in the **`https://github.com/aerospike/data-modeling-guide`**
repository.

**For a new application, fetch the guide and follow its checklist. Do not design
a complete model from this skill alone.**

```bash
gh repo clone aerospike/data-modeling-guide
```

Then read its `AGENTS.md` first — it carries the routing table and the hard
rules — followed by `new-app-modeling-checklist.md`.

| Task | Guide file |
|---|---|
| New model from scratch (required first read) | `new-app-modeling-checklist.md` |
| Core concepts, record sizing, indexes, applied patterns | `concepts-and-patterns.md` |
| 1:N pattern selection | `one-to-many-relationships.md` |
| A list that grows very large; sharding and overflow | `follow-relationship-scale.md` |
| List vs map, ordering, persisted indexes | `cdt-api.md` |
| Server-side filtering, computed bins, expression indexes | `expressions.md` |
| Nested CDT querying, list-of-structs | `path-expressions.md` |
| Matching a workload to a known shape and its sizing profile | `workload-archetypes.md` |
| Reviewing a drafted model | `modeling-failure-modes.md` |
| Identifier format / timestamp naming | `id-selection-guidance.md`, `timestamp-bin-naming-guidance.md` |

**If you cannot reach the guide** — no access, no `gh` auth, offline — say so
plainly and state what that limits. Deliver what this skill supports (the mental
model, the failure-mode checks, a clarification document) and flag that the
sizing worksheets and decision packs were not applied. Do not improvise a
complete model and present it as if the full process ran.

## Version-gated features

Several patterns depend on server version. Confirm the target version and client
support before recommending any of them; the guide's checklist has a version
gate table with fallbacks for each.

- **Path expressions** — nested CDT filtering and indexing.
- **Expression indexes** — sparse or computed-value indexing.
- **Multi-record transactions** — atomic multi-record updates; require a
  strong-consistency namespace, and carry limits that rule them out for wide
  cascades. See `concepts-and-patterns.md` § Multi-record consistency.

Do not state a specific minimum version from memory. Read it from the guide or
the [client matrix](https://aerospike.com/docs/develop/client-matrix).

## See also

- [reference.md](reference.md) — external links.
- `aerospike-development` — implementation-time work against an existing model.
