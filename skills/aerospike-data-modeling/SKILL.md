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

## Critical deliverables: schema guide and schema summary

- Design produces **two documents, written to files**: a **schema guide** (the full design and its reasoning) and a **schema summary** (the condensed contract, generated from the guide, never authored independently). Both are required before any code. Contents and the regeneration rule: [references/model-deliverables-schema-guide-summary.md](references/model-deliverables-schema-guide-summary.md).

## Critical rules: the mental model for data architects

- **Required reading before designing anything.** Aerospike is neither relational nor document: records are semi-structured and are the unit of I/O, there are no server-side joins, every record costs about 64 bytes of index per replica, and access patterns drive the model. The six properties and the record-sizing bounds: [references/model-mental-model.md](references/model-mental-model.md).

## Clarification rules: do not design without clarifying first

- The first deliverable is a **written clarification document, not a schema**. Ask requirements-gap questions, never mechanism-preference ones; stop rather than assume; record an input you cannot obtain as an explicit assumption with a reconsider trigger; design one entity group at a time and pass its review before the next. The full loop: [references/model-design-time-workflow.md](references/model-design-time-workflow.md).

## Common pitfalls: failure modes to check while drafting

- Seven ways Aerospike models go wrong — record granularity from the entity list, secondary indexes as the primary query path, ignoring CDTs, bins used as columns, normalizing instead of denormalizing, unbounded collection growth, and small entities with no sizing decision. Check them **during** design, not after. Each with a detection test you can run: [references/model-failure-modes-checklist.md](references/model-failure-modes-checklist.md).

## Escalation mapping: use the data modeling guide

This skill covers the decision layer; the full workflow lives in the
**`https://github.com/aerospike/data-modeling-guide`** repository. **For a new
application, fetch the guide and follow its checklist — do not design a complete
model from this skill alone.** Routing and the unreachable-guide fallback:
[references/ex-guide-escalation.md](references/ex-guide-escalation.md).

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

## Version-gate rules

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
