---
title: Fetch the data modeling guide before designing a full model
impact: HIGH
tags: modeling, escalation, data-modeling-guide, design-time, links
doc: https://aerospike.com/docs/develop/data-modeling/
also:
  - https://aerospike.com/docs/develop/data-modeling/collections
last_verified: 2026-08-06
---

## Fetch the data modeling guide before designing a full model

**Rule**

This skill carries the decision layer. The full design-time process lives in the
**`https://github.com/aerospike/data-modeling-guide`**
repository. For a new application or a redesign, fetch it and follow its
checklist — do not produce a complete model from this skill alone.

```bash
gh repo clone aerospike/data-modeling-guide
```

Read `AGENTS.md` first: it carries the hard rules, the routing table, and the
version gates. Then `new-app-modeling-checklist.md`, which is the required first
read for a new application.

**Why**

**Routing**

| Task | File |
|---|---|
| New model from scratch | `new-app-modeling-checklist.md` |
| Core concepts, record sizing, indexes, applied patterns | `concepts-and-patterns.md` |
| 1:N pattern selection | `one-to-many-relationships.md` |
| Lists that grow very large; sharding, overflow, pagination | `follow-relationship-scale.md` |
| List vs map, ordering, persisted indexes, complexity | `cdt-api.md` |
| Filter and operation expressions, expression indexes | `expressions.md` |
| Nested CDT querying, list-of-structs | `path-expressions.md` |
| Matching a workload to a known shape and sizing profile | `workload-archetypes.md` |
| Reviewing a drafted model | `modeling-failure-modes.md` |
| Identifier formats; timestamp bin naming | `id-selection-guidance.md`, `timestamp-bin-naming-guidance.md` |

The guide holds material that changes on server releases — version gates,
operation complexity tables, configuration limits and their current defaults.
Copying those values into a skill guarantees they go stale, and a stale copy is
worse than a pointer because nothing signals that it is wrong. Read them from
the guide at the time you need them.

**Prefer**

- Reading current values (version minimums, size limits, complexity) from the guide rather than recalling them
- Naming the specific guide file you used, so a reviewer can retrace the decision

**Avoid**

- Presenting a model as complete when the guide's checklist and sizing worksheets were never applied
- Quoting a version gate or size limit from memory
- Silently substituting your own process when the guide is unreachable — say so plainly, deliver what this skill supports (the mental model, the seven failure-mode checks, a clarification document, a first pass at entity groups), and flag that the decision packs, sizing worksheets and version-gate table were not applied

**See also**

- [model-design-time-workflow.md](aerospike-data-modeling-model-design-time-workflow.md)
- [model-failure-modes-checklist.md](aerospike-data-modeling-model-failure-modes-checklist.md)
