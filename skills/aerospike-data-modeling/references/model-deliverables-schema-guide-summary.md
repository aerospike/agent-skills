---
title: Produce a schema guide and a derived schema summary
impact: MEDIUM
tags: modeling, deliverables, schema-guide, schema-summary, documentation, design-time
doc: https://aerospike.com/docs/develop/data-modeling/
also:
  - https://aerospike.com/docs/develop/data-modeling/conventions
last_verified: 2026-08-06
---

## Produce a schema guide and a derived schema summary

**Rule**

Design work produces two documents, written to files. Know which one you are
writing at any moment, and never author the second independently of the first.

**Schema guide** — the complete design document, and the artifact every review
gate operates on:

- Entity and relationship map; access pattern matrix
- Key schema (namespace, set, key format, examples, cardinality, skew)
- Bin schema (names, types, constraints, size ranges, growth model, ownership)
- One JSON example record per set, placed with that set's schema
- Relationship and consolidation decisions, with completed sizing worksheets
- Index rationale — why each index exists, expected selectivity, memory impact
- Growth, overflow, and hot-key plan; validation and failure-mode test plan
- **The reasoning**: an assumptions log naming every judgment call, the
  alternatives rejected, and the evidence that would reopen each decision

**Schema summary** — the condensed contract, derived from the guide:

- One table per set: key format, bins, types, one-line purpose
- The index list
- Growth and overflow triggers

No rationale, no alternatives, no rejected options. This is what a developer
keeps open while implementing and what a reviewer diffs when the model changes.

**Why**

A schema without reasoning is a guess that someone will have to re-derive. Six
months later the question is never "what are the bins" — it is "why is this
consolidated, and what would make us change it." That belongs in the guide.

Conversely, an implementer does not want to read decision rationale to find a
bin type. Two documents with different jobs beat one that serves neither.

Keeping the summary **derived** is what stops them diverging. Two independently
authored documents describing the same schema will disagree within a release,
and nobody will know which is authoritative.

**Prefer**

- Writing both to files, not pasting a schema into chat
- Building the guide incrementally, one entity group at a time, and generating the summary only once every group is done
- Regenerating the summary from the guide whenever the model changes
- Stating explicitly, in the guide, which decisions were assumptions rather than confirmed inputs

**Avoid**

- Editing the schema summary directly when the model changes — update the guide, regenerate the summary
- Omitting the assumptions log because the model "seems obvious"
- Treating a chat-delivered schema as a deliverable

**See also**

- [model-design-time-workflow.md](model-design-time-workflow.md)
- [ex-guide-escalation.md](ex-guide-escalation.md)
