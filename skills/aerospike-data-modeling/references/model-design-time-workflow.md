---
title: Work the design-time loop one entity group at a time
impact: HIGH
tags: modeling, workflow, clarification, entity-groups, review-gates, design-time
doc: https://aerospike.com/docs/develop/data-modeling/
also:
  - https://aerospike.com/docs/develop/data-modeling/relationships
last_verified: 2026-08-06
---

## Work the design-time loop one entity group at a time

**Rule**

Data model design is an interactive process with mandatory stop points, not a
document you fill in. Produce a written clarification document first, partition
the domain into entity groups, then design each group and pass its review before
starting the next.

The shape of the loop:

1. **Clarify.** Written clarification document listing every entity and
   relationship, and for each required input either the confirmed value and its
   source, or an explicit `MISSING — question: …`. This document *is* the
   deliverable for this step. Do not proceed with unresolved items unless they
   are recorded as approved assumptions.
2. **Entities and relationships.** Cardinality, who drives the read, and skew —
   most entities small, a few enormous.
3. **Access patterns.** Every read and write: by what key, how often, what
   latency target, what payload size.
4. **Entity-group plan.** Partition into groups that share relationships and get
   modeled together. This is a routing and status artifact, not a design one —
   it records which inputs are confirmed, not which patterns were chosen.
5. **Per group:** group-specific clarification → record design (granularity,
   keys, bins) → developer walkthrough → stakeholder checkpoint → update status.
6. **Then, across groups:** index strategy, server-side filtering, and a
   validation pass over every access pattern.

**Why**

An agent that reads a modeling checklist, extracts its headings, and fills them
in produces a document that looks compliant but was never validated at any
intermediate stage. The gates exist because relationship decisions interact: a
choice made for one entity group constrains the next, and catching that at a
checkpoint is far cheaper than after implementation.

Designing one group at a time also surfaces group-specific questions that are
invisible at the whole-domain level — which identifier enters a composite key,
what a notification payload needs for deep-link navigation, how a repost
propagates.

**Prefer**

- A written clarification document as the first artifact, before any schema
- Requirements-gap questions ("what is the p95 fan-out?") over mechanism-preference questions ("which pattern do you prefer?")
- The baseline shape by default — introduce a new set, split record, extra index, or materialized view only when a requirement cannot be met otherwise, or measurement shows the baseline misses an SLO
- Explicit assumptions with reconsider triggers when an input cannot be obtained
- A developer walkthrough per group: trace a create-and-read flow, a multi-record mutation, and a cleanup/cascade through the drafted schema

**Avoid**

- Producing a complete schema for every entity group with no clarifying question asked and no checkpoint held
- Pre-filling pattern choices into the entity-group plan — those are outputs of per-group design, not routing decisions
- Treating "we discussed the data model" as equivalent to having a schema guide

**See also**

- [model-deliverables-schema-guide-summary.md](model-deliverables-schema-guide-summary.md)
- [model-failure-modes-checklist.md](model-failure-modes-checklist.md)
- [ex-guide-escalation.md](ex-guide-escalation.md)
