---
title: Run the seven failure-mode detection tests against a drafted model
impact: HIGH
tags: modeling, review, failure-modes, checklist, schema-review, design-time
doc: https://aerospike.com/docs/develop/data-modeling/
also:
  - https://aerospike.com/docs/develop/data-modeling/record-sizing
last_verified: 2026-08-06
---

## Run the seven failure-mode detection tests against a drafted model

**Rule**

Each failure mode below has a **detection test** — something you can run against
a draft and get a yes/no answer. Use them twice: as priming before designing,
and as a review rubric against a drafted schema. These are not LLM-specific;
they are relational and document-database habits applied to an architecture that
rewards neither.

**1. Record granularity from the entity list.**
*Detect:* count the sets. If each maps 1:1 to a domain noun (comment, follow,
event, like), the model came from an ER diagram rather than from access
patterns. Granularity should follow cardinality and who drives the read.

**2. Secondary indexes as the primary query mechanism.**
*Detect:* list every access pattern and mark how each resolves. If more than one
or two resolve via SI query rather than key lookup or bounded batch read, the
key design is wrong — fix the keys, not the indexes. Reserve SIs for inverse
lookups and genuinely unknown key sets; use a lookup-table record for unique-ID
resolution.

**3. Ignoring CDT capabilities.**
*Detect:* trace each write. Any operation that reads a bin, changes part of it
in application code, and writes the whole bin back is a read-modify-write that a
server-side collection operation should have replaced — and it loses atomicity
as well as speed.

**4. Treating bins like columns.**
*Detect:* look for bin counts that scale with data rather than with schema — a
bin per tag, per day, per counter. Also flag any bin name truncated past
readability. Bin names cap at 15 characters; start descriptive and abbreviate
only on hitting the limit, keeping type-carrying suffixes intact.

**5. Normalizing instead of denormalizing.**
*Detect:* find any read that must fetch a second record purely to assemble a
response — a follower count read from the follower-list record, a display name
read from the user record. Each is a normalization the model should have
collapsed. There are no joins; the alternative to duplication is a round trip.

**6. Unbounded collection growth.**
*Detect:* for each collection bin, ask what caps its element count. If the answer
is user behavior rather than a design decision — followers, comments, events,
notifications — it is unbounded. Ask for p99 cardinality three years out; if
nobody can answer, that is a blocking missing input, not a detail to settle
later. Pagination bounds the *response*; you still need a pattern that bounds
the *record*.

**7. Small independent entities without a sizing decision.**
*Detect:* find sets whose records are a few hundred bytes and that participate in
no relationship. Compare total index overhead against total payload. If index
cost is a double-digit percentage of data, it is unresolved — and consolidating
all of them into a single record is the opposite error, creating a hot key.

**Why**

Stated as warnings, these are unactionable during design. Stated as tests, they
are checkable against a draft — which is the difference between guidance that
gets followed and guidance that gets nodded at.

**Prefer**

- Running all seven against the drafted schema before the stakeholder review
- Treating an unanswerable growth question as a blocker, not a footnote

**Avoid**

- Running these only at the end — most are cheaper to fix during design than after

**See also**

- [model-design-time-workflow.md](model-design-time-workflow.md)
- [ex-guide-escalation.md](ex-guide-escalation.md) — the guide carries the full
  version of each, with the corrective pattern and worked examples
