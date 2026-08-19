# Testing the agent skills, and fixing what publishing ships

**Ticket:** [AIE-16](https://aerospike.atlassian.net/browse/AIE-16) — Test the agent skills before publishing
**Parent:** [AIE-4](https://aerospike.atlassian.net/browse/AIE-4) — Publish our agent skills
**Branch:** `feat/AIE-16-skill-testing`, stacked on `feat/AIE-13-registry-publishing`
**Date:** 2026-08-19

## Goal

Confirm the skills work — correct triggering, accurate content, clean install — before
registries, documentation, and a blog post point at them.

Investigation reshaped the ticket. AIE-16 was written assuming we publish three
separately-installable skill folders, and its triggering and install criteria follow from
that assumption. We are changing what we publish, which changes what needs testing. The
scope below reflects the corrected target.

## What we found before designing

Eight findings drove the design. Each carries a decision; the ledger in workstream F
tracks them through to resolution.

| # | Finding | Decision |
|---|---------|----------|
| F1 | `compiled-skills/SKILLS.md` cites 19 reference files by bare filename (33 mentions) and carries zero URLs, against 246 in the source | **Accept.** The stripped digest shape is deliberate and measured. Mitigate by giving the file a resolvable home. |
| F2 | `labeled_sections` misparses a standalone bold line as a section label, truncating a rule mid-sentence and discarding its content | **Fix.** |
| F3 | Publishing submits three skill folders rather than the one compiled artifact the evaluation validated | **Fix in this branch.** |
| F4 | Both validators are hardcoded to `skills/`, so the artifact we publish is never validated | **Fix.** |
| F5 | The README install table has no Gemini row, though AIE-16 requires a verified Gemini install | **Fix.** |
| F6 | No skill declares a supported server version range, so "current server behavior" has no target | **Fix.** |
| F7 | `aerospike-data-modeling` has never been measured — absent from the harness `source_skills` and from all 61 tasks | **Fix.** |
| F8 | Skill folders are self-contained; no relative link escapes its own folder | **Pass.** Lock in with a check. |

### F1 in detail, and why we accept it

The June evaluation (run `20260623-101343`, 61 tasks, Composer 2.5) measured five packaging
shapes against a no-skill baseline. The stripped single-file compile scored 95% accuracy at
roughly 8.5k total tokens, tying the full monolith within the confidence interval at about
3.7× fewer tokens, and clearing every trap task. Ship stripped, author modular was the
recorded decision, and it stands.

A digest that names its sources without inlining them is therefore intended, not broken.
Once the repository is public an agent can fetch a named file when it needs the detail. The
residual gap is that nothing in the compiled output says *where* those files live, which the
publishing rework fixes as a side effect.

### F2 in detail, because it is systematic

`labeled_sections` splits a rule file on any line matching `^\*\*(.+?)\*\*\s*$`. In
`skills/aerospike-data-modeling/references/ex-guide-escalation.md` the guide URL sits on its
own line as bold code, so the parser reads it as a section heading. Everything after it —
the URL, the `gh repo clone` command, a ten-row routing table — lands in a section named
after the URL that no renderer emits. The published output is a sentence fragment:

    - This skill carries the decision layer. The full design-time process lives in the

The bug is not specific to that file. Any standalone bold line inside a rule body silently
truncates the rule. It went unnoticed because the only affected rule is in the one skill the
evaluation never covered (F7).

## Decisions taken

Settled with the ticket owner during design:

1. Test prompts live in `agent-skills/tests/` as the source of truth; the evaluation harness
   in `citrusleaf/agent-skills-eval` consumes them through its existing vendor submodule.
2. Work is phased — automatable checks first, judgment-based checks after.
3. Triggering is measured with a router-classifier: a model sees only skill descriptions plus
   the prompt, and reports what it would load.
4. Each skill declares an explicit supported server version range; the content check targets
   the newest release in that range.
5. Content accuracy is executable where practical — a script boots the claimed image and
   asserts the skill's own claims.
6. We do not test third-party installers. We verify our own payload.
7. The stripped compile format is settled and out of scope.
8. Registries receive **one** compiled skill, not three folders. This corrects a gap in
   AIE-13 and lands in this branch, since nothing has been submitted yet.

## Workstream A — reshape publishing to one compiled skill

The largest piece, and a prerequisite for the rest: triggering and payload checks must test
what we actually ship.

**Compiler.** `scripts/compile-agents.py` gains a target emitting a spec-valid skill
directory at `compiled-skills/aerospike/SKILL.md`. The folder name matches the frontmatter
`name`, as CONTRIBUTING requires and as the skills CLI assumes when it uses the folder as an
install directory. Frontmatter carries `name: aerospike`, a hand-written `description`,
`license: Apache-2.0`, and `metadata.last_verified`. The body is the existing stripped render
of all three source skills, unchanged in shape.

**The description is written by hand, not generated.** It becomes the single highest-leverage
string in the repository — the only input to whether the skill fires. It must cover local
setup, client development, and design-time modeling in one sentence set, while excluding
Aerospike Graph, cluster operations, sizing, and XDR. Workstream B measures whether it works.

**`SKILLS.md` is replaced** rather than kept alongside. The new file's body is identical, so
keeping both means two generated artifacts that can drift, two staleness checks, and a reader
who has to be told which one they want. The advertised raw URL moves, which would normally be
a real cost and here is not: the repository is private and no registry has been submitted to.
*(This is the one decision not explicitly confirmed by the ticket owner — settle it at spec
review. Keeping both files is a small, contained alternative.)*

**Publishing.** `publish-registries.yml`, `publish-openagentskill.sh`, and
`publish-upskill.sh` submit the single skill path. `skills.sh.json` collapses to one entry.
The four existing gates are untouched.

**Validation.** `validate-spec.sh` and `validate-skill.sh` extend past `skills/` to cover the
generated skill, so the published artifact is validated rather than only its sources. Both
still validate the three authoring folders, which remain the maintained source of truth.

**Correctness.** Fix `labeled_sections` (F2) and re-run the compile. Resolve F1 by having the
generated header carry the repository URL, so a cited filename such as
`single-ttl-nsup-default-ttl.md` can be resolved to
`https://github.com/aerospike/agent-skills/blob/main/skills/<skill>/references/<file>` once the
repository is public.

**Documentation.** `README.md`, `compiled-skills/README.md`, `AGENTS.md`, `CLAUDE.md`, and
`CONTRIBUTING.md` describe one published skill and three authoring folders. Add the Gemini
row (F5).

## Workstream B — trigger accuracy

With one published skill, cross-triggering between our own skills is designed out rather than
tested. What remains is whether the single description fires across all three domains and
stays quiet outside them.

`tests/triggers/*.yaml` holds cases of prompt plus expected outcome (`aerospike` or `none`):

- **Positives** spanning all three domains, since one description must now serve a Docker
  setup question, a CDT operation question, and a greenfield schema question alike.
- **Negatives** it must ignore: Aerospike Graph, cluster sizing, XDR, backup and restore, and
  unrelated technology.
- **Near-misses** that mention Aerospike incidentally without needing the skill.

A runner presents a model with only the skill description and the prompt, mirroring how an
agent harness decides, and reports per-outcome precision and recall. Because the three
authoring folders keep their own descriptions and stay installable for anyone who wants them,
the corpus also records the expected folder, so cross-triggering can be re-checked if we ever
publish them.

## Workstream C — end-to-end lift

Extend the existing harness rather than build a second one. It already provides the no-skill
control the acceptance criterion asks for.

Add `aerospike-data-modeling` to `source_skills` in `eval/config.yaml` and write
`tests/tasks/data-modeling.yaml` covering the design-time workflow, the schema guide and
summary deliverables, the seven failure-mode checks, and guide escalation — the last of which
exercises the rule F2 truncates, so it would have caught that bug.

Add a variant matching the published shape so we measure the artifact we ship, not only the
shapes compared in June. Prompts live in `tests/`; the harness reads them through its vendor
submodule.

Carry forward one open item from the June run: `dev-ttl-void-time` failed on every variant
including monolith, which the report attributes to a rubric or grader problem rather than a
skill defect. Resolve or record it.

## Workstream D — content accuracy

Declare the version range first, so the check has a target. Each `SKILL.md` gains
`metadata.server_versions: "7.0+"` as a quoted string, because the canonical local
configuration sets `cluster-name`, mandatory since Database 7.0.0, so the documented flow
cannot work below it. Newer capabilities stay gated inline where they already are — the 8.1.0
admin port, 8.1.2 path expressions, and the 7.1.0 `post-write-queue` rename.

`tests/content/verify-server-claims.sh` boots the claimed image and asserts the
getting-started skill's own claims: image name, the 3000-3002 port mapping, `cluster-name`
being mandatory, `nsup-period` governing expiry, `default-ttl` behavior, and port 3003 on
8.1.0 and later. Each assertion cites the line it verifies, so a drifted claim names its own
source.

Client API signatures get a manual pass against official SDK sources, recorded in the ledger.
Automating that is not worth the cost.

## Workstream E — CI

Trigger checks and payload integrity join `spec-conformance.yml` and `skill-validator.yml` as
pull-request gates. Payload integrity is deterministic and free: the compiled skill parses as
valid frontmatter, no skill folder links outside itself (F8), and the compiled output is not
stale.

The trigger check needs a model call, so it runs on pull requests touching `skills/`,
`compiled-skills/`, or `tests/triggers/`, against a pinned model. Its pass threshold is
recorded in `tests/triggers/README.md` and CI fails below it. The initial value is set from
the first measured run rather than guessed, and demanding a perfect score is explicitly not
the goal — model selection is stochastic.

The end-to-end run stays manual and periodic in the evaluation repository. It costs real money
and takes too long to gate a pull request.

## Workstream F — findings ledger

`tests/FINDINGS.md` records every finding with its decision: fixed and where, deferred with a
ticket, or accepted with a reason. It starts with the eight above and grows as the other
workstreams run. This satisfies the final acceptance criterion, which asks for findings to be
fixed *or triaged with a decision recorded*.

## Layout

```
tests/
  README.md                     how to run each check
  FINDINGS.md                   the ledger
  triggers/*.yaml               prompt -> expected skill, or none
  tasks/data-modeling.yaml      end-to-end tasks for the unmeasured skill
  content/verify-server-claims.sh
  run-triggers.py               router-classifier runner
```

## Acceptance criteria

| Criterion | Where it is met |
|-----------|-----------------|
| Trigger accuracy verified, cross-triggering checked | B — cross-triggering designed out by A; corpus retains folder expectations |
| Content spot-checked against current server behavior | D |
| Clean install verified on Claude, Gemini, Cursor | A — payload integrity and documented locations, no installer testing |
| End-to-end runs show clear improvement over baseline | C — against the existing `v0` control |
| Test prompts committed to the repo | B and C, under `tests/` |
| All findings fixed or triaged with a decision recorded | F |

## Out of scope

Third-party installer behavior; the stripped compile format; retiring the three authoring
folders, which remain the maintained source; making the repository public ([AIE-17](https://aerospike.atlassian.net/browse/AIE-17));
documentation references ([AIE-14](https://aerospike.atlassian.net/browse/AIE-14)); the blog post ([AIE-15](https://aerospike.atlassian.net/browse/AIE-15)).

## Risks

**A is a prerequisite for B and C.** Testing before the publishing shape is settled means
testing the wrong artifact. Sequence A first.

**One description carrying three domains may over-fire.** It has to cover more ground than any
of the three it replaces, and breadth invites false positives on adjacent database questions.
Workstream B measures exactly this; if precision is poor, the description is the fix, not the
architecture.

**The evaluation harness lives in another repository.** Prompts under `tests/` are consumed
through a submodule, so a prompt change and a harness change land in different pull requests.
Acceptable, but the vendored pointer must be refreshed when prompts change.
