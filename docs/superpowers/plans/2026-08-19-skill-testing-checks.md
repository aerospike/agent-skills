# Skill Testing Checks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove the published Aerospike skill fires on the right prompts, states things that are true of a running server, and measurably beats no skill at all — with the checks committed and gating pull requests.

**Architecture:** Workstream A already made the published artifact a single spec-valid skill at `compiled-skills/aerospike/SKILL.md`. This plan tests it. A router-classifier runner under `tests/` measures whether that skill's one description fires correctly; a Docker-backed script asserts the getting-started claims against a real server; a task corpus closes the data-modeling gap in the evaluation harness. The corpus files live in this repository and the harness in `aerospike/agent-skills-eval` reads them through its `vendor/agent-skills` submodule.

**Tech Stack:** Python 3.10+ (3.12 in CI), PyYAML, pytest 7.4, `cursor-sdk`, bash, Docker, GitHub Actions.

## Global Constraints

- Conventional Commits, enforced by commitlint: lowercase `type: subject`, no sentence-case subject, header under 100 characters. Never `--no-verify`.
- The Agent Skills spec allows only these frontmatter keys: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. Everything else goes under `metadata`, and `metadata` values must be strings — quote versions and dates or YAML converts them.
- `skills/` is the authoring source of truth. `compiled-skills/aerospike/SKILL.md` is generated: never hand-edit it. After any change to `skills/` or `scripts/skills_compile/published_skill.yaml`, run `python3 scripts/compile-agents.py --shape stripped --write`.
- Every task ends with `python3 scripts/compile-agents.py --shape stripped --check` passing and the full suite green.
- The declared supported server range is `7.0+`, as the quoted string `"7.0+"`.
- The published skill's name is `aerospike`. The router's two allowed answers are `aerospike` and `none`.
- Model calls go through `cursor-sdk`, matching the evaluation harness: `Agent.prompt(prompt, AgentOptions(api_key=..., model=..., local=LocalAgentOptions(cwd=...)))`, with the reply text at `result.result`, and the key read from the `CURSOR_API_KEY` environment variable.
- Anything that calls a model must also run without one. Every runner takes an offline mode that scores a recorded run, so its logic is unit-testable with no key and no network.
- Docker is available locally. Tests that need it must skip cleanly when it is absent rather than fail.

---

### Task 1: Declare the supported server version range

"Guidance matches current server behavior" has no meaning until the skills say which server they target. The floor is 7.0.0 because the canonical local configuration sets `cluster-name`, which that release made mandatory — the documented flow cannot work below it. Newer capabilities stay gated inline where they already are.

**Files:**
- Modify: `skills/aerospike-getting-started/SKILL.md` (frontmatter `metadata`)
- Modify: `skills/aerospike-development/SKILL.md` (frontmatter `metadata`)
- Modify: `skills/aerospike-data-modeling/SKILL.md` (frontmatter `metadata`)
- Modify: `scripts/skills_compile/published_skill.yaml`
- Create: `tests/unit/test_skill_metadata.py`
- Regenerate: `compiled-skills/aerospike/SKILL.md`, `compiled-skills/manifest.json`

**Interfaces:**
- Consumes: `skillsrc.split_frontmatter(text) -> tuple[dict, str]`.
- Produces: every `SKILL.md` in the repository, including the published one, carries `metadata.server_versions` equal to the string `"7.0+"`.

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_skill_metadata.py`:

```python
"""Every skill declares the server range its guidance targets, so "matches
current server behavior" has something concrete to be checked against."""

import pathlib

import pytest

from scripts.skills_compile.skillsrc import split_frontmatter

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SKILL_FILES = sorted(REPO_ROOT.glob("skills/*/SKILL.md")) + [
    REPO_ROOT / "compiled-skills" / "aerospike" / "SKILL.md"
]


def _ids(path):
    return path.parent.name


@pytest.mark.parametrize("skill_md", SKILL_FILES, ids=_ids)
def test_skill_declares_the_supported_server_range(skill_md):
    meta, _body = split_frontmatter(skill_md.read_text(encoding="utf-8"))

    assert meta["metadata"]["server_versions"] == "7.0+"


def test_every_skill_on_disk_is_covered():
    """Guards the parametrize list: a new skill folder must not slip past."""
    on_disk = set(REPO_ROOT.glob("skills/*/SKILL.md"))

    assert on_disk <= set(SKILL_FILES)
    assert len(SKILL_FILES) == 4
```

- [ ] **Step 2: Run the test and verify it fails**

Run: `python3 -m pytest tests/unit/test_skill_metadata.py -v`

Expected: the four parametrized cases FAIL with `KeyError: 'server_versions'`.
`test_every_skill_on_disk_is_covered` PASSES.

- [ ] **Step 3: Declare the range in all four places**

In each of the three files `skills/aerospike-getting-started/SKILL.md`,
`skills/aerospike-development/SKILL.md`, and `skills/aerospike-data-modeling/SKILL.md`,
add one line to the existing `metadata` block, keeping each file's own `last_verified` value:

```yaml
metadata:
  last_verified: "2026-04-21"
  server_versions: "7.0+"
```

Then add the same `server_versions` line to the `metadata` block in
`scripts/skills_compile/published_skill.yaml`, whose `last_verified` is `"2026-04-21"`.

Quote the value. Unquoted, `7.0+` is still a string in YAML, but quoting keeps it consistent
with `last_verified`, which must be quoted, and states the intent.

- [ ] **Step 4: Confirm the three source skills pass**

Run: `python3 -m pytest tests/unit/test_skill_metadata.py -v`

Expected: 4 passed, 1 failed. The compiled-artifact case still raises `KeyError` — it is
generated, and regenerating is the next step.

- [ ] **Step 5: Regenerate and confirm the only compiled change is the frontmatter**

Run:

```bash
python3 scripts/compile-agents.py --shape stripped --write
git diff --stat compiled-skills/
git diff compiled-skills/aerospike/SKILL.md
```

Expected: `SKILL.md` gains exactly the one `server_versions` line inside its frontmatter, and
the rule body below the header is untouched. `manifest.json` byte count changes.

Re-run `python3 -m pytest tests/unit/test_skill_metadata.py -v`; all 5 now pass.

- [ ] **Step 6: Run the full suite and commit**

Run: `python3 -m pytest tests/unit -q`

Expected: 23 passed (18 existing, 5 here).

```bash
git add skills/ scripts/skills_compile/published_skill.yaml \
        tests/unit/test_skill_metadata.py compiled-skills/
git commit -m "feat: declare the supported server range on every skill"
```

---

### Task 2: Measure whether the description triggers correctly

One published skill means cross-triggering between our own skills is designed out rather than tested. What is left, and what now carries all the risk, is whether a single description fires across three domains and stays quiet outside them. The description is the only input an agent harness uses for that decision, so the runner shows a model exactly that and nothing else.

The corpus records the authoring folder each positive belongs to, so cross-triggering can be re-measured if the three folders are ever published separately.

The runner is `tests/run_triggers.py` with an underscore, not the hyphen the design sketched, so unit tests can import it.

**Files:**
- Create: `tests/triggers/positives.yaml`
- Create: `tests/triggers/negatives.yaml`
- Create: `tests/triggers/near-misses.yaml`
- Create: `tests/triggers/README.md`
- Create: `tests/run_triggers.py`
- Create: `tests/unit/test_run_triggers.py`
- Modify: `tests/README.md`

**Interfaces:**
- Consumes: `compiled-skills/aerospike/SKILL.md`, `skillsrc.split_frontmatter`.
- Produces, all importable from `tests.run_triggers`:
  - `TriggerCase` frozen dataclass: `id: str`, `prompt: str`, `expect: str`, `domain: str | None`, `why: str`
  - `Metrics` frozen dataclass: `total`, `correct`, `true_positives`, `false_positives`, `false_negatives` as `int`, `failures: tuple[tuple[str, str, str], ...]`, with `accuracy`, `precision`, `recall` properties returning `float`
  - `NO_SKILL: str = "none"`
  - `load_published_skill(path: pathlib.Path) -> tuple[str, str]` returning `(name, description)`
  - `load_corpus(corpus_dir: pathlib.Path) -> list[TriggerCase]`
  - `build_router_prompt(name: str, description: str, user_prompt: str) -> str`
  - `parse_verdict(raw: str, skill_name: str) -> str` returning the skill name, `"none"`, or `"unparseable"`
  - `score(cases: list[TriggerCase], verdicts: dict[str, str], skill_name: str) -> Metrics`
  - `main(argv: list[str] | None = None) -> int`

- [ ] **Step 1: Write the corpus**

Create `tests/triggers/positives.yaml`. Every case must load the skill. Four per domain,
because one description now has to serve all three:

```yaml
# Prompts the published skill must fire on. `domain` records which authoring
# folder under skills/ would have served the prompt, so cross-triggering can be
# re-measured if those folders are ever published separately.
- id: pos-gs-docker-local
  prompt: >-
    I'm new to Aerospike. How do I get a single node running locally with Docker
    and check that it actually started?
  expect: aerospike
  domain: aerospike-getting-started
  why: Local setup is the getting-started core.

- id: pos-gs-default-namespace
  prompt: >-
    My Aerospike client keeps failing with a namespace error. What namespace does
    a fresh install actually have?
  expect: aerospike
  domain: aerospike-getting-started
  why: Namespace defaults are a named anti-hallucination rule.

- id: pos-gs-redis-replacement
  prompt: >-
    We're outgrowing Redis for our session store and need something that persists
    to disk at the same latency. Is Aerospike a fit, and how do I try it?
  expect: aerospike
  domain: aerospike-getting-started
  why: The Redis-replacement path is an explicit trigger in the description.

- id: pos-gs-first-put-get
  prompt: >-
    Write me the smallest possible Python program that connects to my local
    Aerospike and does one write and one read.
  expect: aerospike
  domain: aerospike-getting-started
  why: First put/get with an official SDK.

- id: pos-dev-cdt-map-update
  prompt: >-
    I have an Aerospike bin holding a map of vehicle IDs to their last known
    positions. How do I update one entry without reading and rewriting the whole
    map?
  expect: aerospike
  domain: aerospike-development
  why: Server-side collection operations are the development core.

- id: pos-dev-batch-reads
  prompt: >-
    What's the right way to read four hundred Aerospike records by key in one go
    from the Go client?
  expect: aerospike
  domain: aerospike-development
  why: Batch workflows and client policy.

- id: pos-dev-policy-timeouts
  prompt: >-
    Our Aerospike writes intermittently time out under load. Which client policy
    settings should I be looking at?
  expect: aerospike
  domain: aerospike-development
  why: Client policies and retry behavior.

- id: pos-dev-secondary-index
  prompt: >-
    Should I add a secondary index on the email bin so I can look users up by
    email in Aerospike?
  expect: aerospike
  domain: aerospike-development
  why: Index discipline, a rule with a strong opinion.

- id: pos-dm-greenfield-schema
  prompt: >-
    We're building a social feed on Aerospike and haven't designed the data model
    yet. Users, posts, follows, likes. Where do I start?
  expect: aerospike
  domain: aerospike-data-modeling
  why: Design-time modeling from requirements.

- id: pos-dm-key-design
  prompt: >-
    How should I choose primary keys for an Aerospike set that stores one record
    per user per day?
  expect: aerospike
  domain: aerospike-data-modeling
  why: Key design is a design-time decision.

- id: pos-dm-unbounded-collection
  prompt: >-
    My Aerospike record has a list bin of every event a user has ever fired and
    it keeps growing. Is that a problem?
  expect: aerospike
  domain: aerospike-data-modeling
  why: Unbounded collection growth is one of the seven failure modes.

- id: pos-dm-schema-review
  prompt: >-
    Here's the Aerospike schema we drafted: one set per entity, six secondary
    indexes, a bin per tag. Can you review it before we build?
  expect: aerospike
  domain: aerospike-data-modeling
  why: Schema review against the failure-mode checklist.
```

Create `tests/triggers/negatives.yaml`. Every case must NOT load the skill:

```yaml
# Prompts the published skill must stay quiet on. The first four are Aerospike
# topics the skill explicitly excludes; the rest are unrelated technology.
- id: neg-graph
  prompt: >-
    How do I write a Gremlin traversal against Aerospike Graph to find
    second-degree connections?
  expect: none
  domain: null
  why: Aerospike Graph is excluded by name.

- id: neg-xdr
  prompt: >-
    Configure XDR shipping from our Aerospike cluster in us-east to the new
    cluster in eu-west.
  expect: none
  domain: null
  why: XDR belongs to Aerospike Operations.

- id: neg-cluster-sizing
  prompt: >-
    How many nodes and how much RAM do we need for an Aerospike cluster holding
    twelve billion records?
  expect: none
  domain: null
  why: Cluster sizing belongs to Aerospike Operations.

- id: neg-backup-restore
  prompt: >-
    What's the procedure for restoring an Aerospike namespace from an asbackup
    archive taken last week?
  expect: none
  domain: null
  why: Backup and restore belongs to Aerospike Operations.

- id: neg-postgres-index
  prompt: >-
    My Postgres query does a sequential scan on a ten million row table. How do I
    get it to use the index?
  expect: none
  domain: null
  why: Unrelated database.

- id: neg-react-hooks
  prompt: >-
    Why does my React component re-render every time the parent state changes,
    even though I wrapped it in memo?
  expect: none
  domain: null
  why: Unrelated technology.

- id: neg-k8s-crashloop
  prompt: >-
    My pod is in CrashLoopBackOff and the logs are empty. How do I debug it?
  expect: none
  domain: null
  why: Unrelated infrastructure.

- id: neg-git-rebase
  prompt: >-
    I rebased onto main and now I have forty conflicts. What's the fastest way
    out of this?
  expect: none
  domain: null
  why: Unrelated tooling.
```

Create `tests/triggers/near-misses.yaml`. These mention Aerospike or its neighbourhood but
do not need the skill. They are the hardest cases and the ones most likely to move the
threshold:

```yaml
# Prompts that name Aerospike, or sit next to it, without needing the skill.
# These are where a broad description over-fires, so they carry the most signal.
- id: near-invoice-mentions-aerospike
  prompt: >-
    Draft an email to our vendor asking why the Aerospike licence invoice went up
    forty percent this year.
  expect: none
  domain: null
  why: Names Aerospike, needs no technical guidance.

- id: near-resume-bullet
  prompt: >-
    Rewrite this resume bullet to sound stronger: "Used Aerospike and Kafka to
    build a real-time pipeline."
  expect: none
  domain: null
  why: Copywriting that happens to name the product.

- id: near-generic-latency
  prompt: >-
    What does p99 latency actually mean and why is it more useful than an
    average?
  expect: none
  domain: null
  why: Adjacent vocabulary, no Aerospike content.

- id: near-cassandra-modeling
  prompt: >-
    How should I model a time series in Cassandra so partitions stay a reasonable
    size?
  expect: none
  domain: null
  why: Data modeling for a different database.

- id: near-dockerfile-generic
  prompt: >-
    How do I make my Dockerfile build faster by ordering layers better?
  expect: none
  domain: null
  why: Docker without Aerospike.
```

- [ ] **Step 2: Write the failing tests**

Create `tests/unit/test_run_triggers.py`. Every test runs offline — none calls a model:

```python
"""The trigger runner's corpus handling, verdict parsing, and scoring must be
correct without a model in the loop, so they are tested with recorded verdicts."""

import json
import pathlib
import textwrap

import pytest

from tests.run_triggers import (
    NO_SKILL,
    Metrics,
    TriggerCase,
    build_router_prompt,
    load_corpus,
    load_published_skill,
    main,
    parse_verdict,
    score,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CORPUS_DIR = REPO_ROOT / "tests" / "triggers"


def _write_corpus(tmp_path, body):
    (tmp_path / "cases.yaml").write_text(textwrap.dedent(body), encoding="utf-8")
    return tmp_path


def test_load_corpus_reads_every_yaml_file_and_normalizes_whitespace(tmp_path):
    _write_corpus(
        tmp_path,
        """
        - id: a
          prompt: >-
            one
            two
          expect: aerospike
          domain: aerospike-development
          why: because
        """,
    )

    cases = load_corpus(tmp_path)

    assert cases == [
        TriggerCase(
            id="a",
            prompt="one two",
            expect="aerospike",
            domain="aerospike-development",
            why="because",
        )
    ]


def test_load_corpus_rejects_a_duplicate_id(tmp_path):
    _write_corpus(
        tmp_path,
        """
        - id: a
          prompt: one
          expect: none
        - id: a
          prompt: two
          expect: none
        """,
    )

    with pytest.raises(ValueError, match="duplicate case id: a"):
        load_corpus(tmp_path)


def test_load_corpus_rejects_an_unknown_expectation(tmp_path):
    _write_corpus(
        tmp_path,
        """
        - id: a
          prompt: one
          expect: maybe
        """,
    )

    with pytest.raises(ValueError, match="expect must be"):
        load_corpus(tmp_path)


def test_load_corpus_rejects_an_empty_directory(tmp_path):
    with pytest.raises(ValueError, match="no trigger cases"):
        load_corpus(tmp_path)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("aerospike", "aerospike"),
        ("  aerospike.  ", "aerospike"),
        ("none", NO_SKILL),
        ("**none**", NO_SKILL),
        ("I would load aerospike for this.", "aerospike"),
        ("Probably not relevant, so none.", NO_SKILL),
        ("", "unparseable"),
        ("I am not sure", "unparseable"),
    ],
)
def test_parse_verdict_tolerates_the_ways_models_actually_reply(raw, expected):
    assert parse_verdict(raw, "aerospike") == expected


def test_score_counts_each_outcome_and_records_failures():
    cases = [
        TriggerCase("p1", "x", "aerospike"),
        TriggerCase("p2", "x", "aerospike"),
        TriggerCase("n1", "x", NO_SKILL),
        TriggerCase("n2", "x", NO_SKILL),
    ]
    verdicts = {
        "p1": "aerospike",
        "p2": NO_SKILL,
        "n1": NO_SKILL,
        "n2": "aerospike",
    }

    metrics = score(cases, verdicts, "aerospike")

    assert (metrics.total, metrics.correct) == (4, 2)
    assert metrics.accuracy == 0.5
    assert (metrics.true_positives, metrics.false_positives) == (1, 1)
    assert metrics.false_negatives == 1
    assert metrics.precision == 0.5
    assert metrics.recall == 0.5
    assert metrics.failures == (("p2", "aerospike", NO_SKILL), ("n2", NO_SKILL, "aerospike"))


def test_metrics_do_not_divide_by_zero_on_an_all_negative_corpus():
    cases = [TriggerCase("n1", "x", NO_SKILL)]

    metrics = score(cases, {"n1": NO_SKILL}, "aerospike")

    assert metrics.accuracy == 1.0
    assert metrics.precision == 0.0
    assert metrics.recall == 0.0


def test_router_prompt_carries_the_description_and_offers_only_two_answers():
    prompt = build_router_prompt("aerospike", "Covers Docker and modeling.", "how do I start?")

    assert "Covers Docker and modeling." in prompt
    assert "how do I start?" in prompt
    assert "aerospike" in prompt
    assert NO_SKILL in prompt


def test_load_published_skill_reads_the_shipped_description():
    name, description = load_published_skill(
        REPO_ROOT / "compiled-skills" / "aerospike" / "SKILL.md"
    )

    assert name == "aerospike"
    assert "Aerospike" in description
    assert "\n" not in description


def test_the_committed_corpus_loads_and_covers_all_three_domains():
    cases = load_corpus(CORPUS_DIR)
    domains = {c.domain for c in cases if c.expect == "aerospike"}

    assert len(cases) >= 20
    assert domains == {
        "aerospike-getting-started",
        "aerospike-development",
        "aerospike-data-modeling",
    }
    assert any(c.expect == NO_SKILL for c in cases)


def test_main_scores_a_recorded_run_offline_and_gates_on_the_threshold(tmp_path):
    corpus = _write_corpus(
        tmp_path,
        """
        - id: a
          prompt: one
          expect: aerospike
          domain: aerospike-development
        - id: b
          prompt: two
          expect: none
        """,
    )
    recorded = tmp_path / "verdicts.json"
    recorded.write_text(json.dumps({"a": "aerospike", "b": "aerospike"}), encoding="utf-8")
    report = tmp_path / "report.json"

    failing = main(
        [
            "--corpus", str(corpus),
            "--offline", str(recorded),
            "--min-accuracy", "0.9",
            "--json", str(report),
        ]
    )
    passing = main(
        ["--corpus", str(corpus), "--offline", str(recorded), "--min-accuracy", "0.4"]
    )

    assert failing == 1
    assert passing == 0
    written = json.loads(report.read_text(encoding="utf-8"))
    assert written["accuracy"] == 0.5
    assert written["failures"] == [["b", "none", "aerospike"]]
```

- [ ] **Step 3: Run the tests and verify they fail**

Run: `python3 -m pytest tests/unit/test_run_triggers.py -v`

Expected: collection FAILS with `ModuleNotFoundError: No module named 'tests.run_triggers'`.

- [ ] **Step 4: Write the runner**

Create `tests/run_triggers.py`:

```python
#!/usr/bin/env python3
"""Measure whether the published skill's description fires when it should.

An agent harness decides whether to load a skill from its description alone,
before the skill's body is ever read. This runner reproduces exactly that
decision: it shows a model the skill name, the description, and one user
message, and records which of two answers comes back. It never loads the skill
body, so what it measures is the description and nothing else.

Offline mode replays recorded verdicts, so the corpus, parsing, and scoring can
be exercised with no API key and no network.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import pathlib
import sys

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.skills_compile.skillsrc import split_frontmatter  # noqa: E402

PUBLISHED_SKILL = REPO_ROOT / "compiled-skills" / "aerospike" / "SKILL.md"
CORPUS_DIR = REPO_ROOT / "tests" / "triggers"
NO_SKILL = "none"
UNPARSEABLE = "unparseable"
DEFAULT_MODEL = "composer-2.5"


@dataclasses.dataclass(frozen=True)
class TriggerCase:
    id: str
    prompt: str
    expect: str
    domain: str | None = None
    why: str = ""


@dataclasses.dataclass(frozen=True)
class Metrics:
    total: int
    correct: int
    true_positives: int
    false_positives: int
    false_negatives: int
    failures: tuple[tuple[str, str, str], ...]

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0

    @property
    def precision(self) -> float:
        fired = self.true_positives + self.false_positives
        return self.true_positives / fired if fired else 0.0

    @property
    def recall(self) -> float:
        wanted = self.true_positives + self.false_negatives
        return self.true_positives / wanted if wanted else 0.0


def load_published_skill(path: pathlib.Path = PUBLISHED_SKILL) -> tuple[str, str]:
    """Return the shipped skill's name and description, whitespace collapsed.

    Read from the compiled artifact rather than a copy, so the corpus always
    scores the description users actually install.
    """
    meta, _body = split_frontmatter(path.read_text(encoding="utf-8"))
    return meta["name"], " ".join(meta["description"].split())


def load_corpus(corpus_dir: pathlib.Path) -> list[TriggerCase]:
    cases: list[TriggerCase] = []
    seen: set[str] = set()
    for path in sorted(corpus_dir.glob("*.yaml")):
        for entry in yaml.safe_load(path.read_text(encoding="utf-8")) or []:
            case = TriggerCase(
                id=entry["id"],
                prompt=" ".join(entry["prompt"].split()),
                expect=entry["expect"],
                domain=entry.get("domain"),
                why=entry.get("why", ""),
            )
            if case.id in seen:
                raise ValueError(f"duplicate case id: {case.id} in {path.name}")
            seen.add(case.id)
            cases.append(case)

    if not cases:
        raise ValueError(f"no trigger cases found under {corpus_dir}")

    name, _description = load_published_skill()
    allowed = {name, NO_SKILL}
    for case in cases:
        if case.expect not in allowed:
            raise ValueError(f"{case.id}: expect must be one of {sorted(allowed)}")
    return cases


def build_router_prompt(name: str, description: str, user_prompt: str) -> str:
    return (
        "You are the skill router in an AI coding assistant. One skill is "
        "installed. Using only its description, decide whether to load it for "
        "the user's message.\n\n"
        f"Skill name: {name}\n"
        f"Description: {description}\n\n"
        f"User message: {user_prompt}\n\n"
        f"Answer with exactly one word: {name} to load the skill, or {NO_SKILL} "
        "to answer without it."
    )


def parse_verdict(raw: str, skill_name: str) -> str:
    """Reduce a reply to one allowed answer.

    Models add punctuation, emphasis, and a sentence of reasoning even when told
    not to, so match on the words present rather than demanding an exact reply.
    A reply naming the skill wins over one naming neither.
    """
    words = {word.strip(".,:;!?\"'`*_").lower() for word in (raw or "").split()}
    if skill_name.lower() in words:
        return skill_name
    if NO_SKILL in words:
        return NO_SKILL
    return UNPARSEABLE


def score(
    cases: list[TriggerCase], verdicts: dict[str, str], skill_name: str
) -> Metrics:
    correct = true_positives = false_positives = false_negatives = 0
    failures: list[tuple[str, str, str]] = []

    for case in cases:
        got = verdicts.get(case.id, UNPARSEABLE)
        if got == case.expect:
            correct += 1
            if got == skill_name:
                true_positives += 1
            continue
        failures.append((case.id, case.expect, got))
        if case.expect == NO_SKILL:
            false_positives += 1
        else:
            false_negatives += 1

    return Metrics(
        total=len(cases),
        correct=correct,
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives,
        failures=tuple(failures),
    )


def _ask_model(prompt: str, model: str) -> str:
    from cursor_sdk import Agent, AgentOptions, LocalAgentOptions

    api_key = os.environ.get("CURSOR_API_KEY")
    if not api_key:
        raise SystemExit(
            "CURSOR_API_KEY is not set. Set it, or pass --offline to score a "
            "recorded run."
        )
    result = Agent.prompt(
        prompt,
        AgentOptions(
            api_key=api_key,
            model=model,
            local=LocalAgentOptions(cwd=str(REPO_ROOT)),
        ),
    )
    return getattr(result, "result", "") or ""


def _collect_verdicts(
    cases: list[TriggerCase], name: str, description: str, model: str
) -> dict[str, str]:
    verdicts: dict[str, str] = {}
    for index, case in enumerate(cases, start=1):
        raw = _ask_model(build_router_prompt(name, description, case.prompt), model)
        verdicts[case.id] = parse_verdict(raw, name)
        print(f"  [{index}/{len(cases)}] {case.id}: {verdicts[case.id]}", flush=True)
    return verdicts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Score the published skill's description against trigger cases."
    )
    parser.add_argument("--corpus", type=pathlib.Path, default=CORPUS_DIR)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--offline",
        type=pathlib.Path,
        help="JSON file of {case_id: verdict}; scores without calling a model",
    )
    parser.add_argument(
        "--min-accuracy",
        type=float,
        default=0.0,
        help="exit 1 below this overall accuracy",
    )
    parser.add_argument("--json", type=pathlib.Path, help="write the report here")
    args = parser.parse_args(argv)

    cases = load_corpus(args.corpus)
    name, description = load_published_skill()

    if args.offline:
        verdicts = json.loads(args.offline.read_text(encoding="utf-8"))
    else:
        print(f"Routing {len(cases)} prompts through {args.model}")
        verdicts = _collect_verdicts(cases, name, description, args.model)

    metrics = score(cases, verdicts, name)

    print(
        f"\naccuracy {metrics.accuracy:.3f}  "
        f"precision {metrics.precision:.3f}  "
        f"recall {metrics.recall:.3f}  "
        f"({metrics.correct}/{metrics.total})"
    )
    for case_id, expected, got in metrics.failures:
        print(f"  FAIL {case_id}: expected {expected}, got {got}")

    if args.json:
        args.json.write_text(
            json.dumps(
                {
                    "model": args.model,
                    "skill": name,
                    "total": metrics.total,
                    "correct": metrics.correct,
                    "accuracy": metrics.accuracy,
                    "precision": metrics.precision,
                    "recall": metrics.recall,
                    "failures": [list(f) for f in metrics.failures],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    if metrics.accuracy < args.min_accuracy:
        print(
            f"\nBelow threshold: {metrics.accuracy:.3f} < {args.min_accuracy:.3f}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Run the tests and verify they pass**

Run: `python3 -m pytest tests/unit/test_run_triggers.py -v`

Expected: 18 passed (8 of them the parametrized `parse_verdict` cases).

If the import fails because `tests` is not a package, add an empty `tests/__init__.py` and
`tests/unit/__init__.py`, then re-run. Do not change `pytest.ini`'s `pythonpath`.

- [ ] **Step 6: Take the first live measurement and record the threshold**

This step needs `CURSOR_API_KEY`. If you do not have one, stop and report NEEDS_CONTEXT
rather than inventing a number — the threshold must come from a measurement.

Run:

```bash
python3 tests/run_triggers.py --model composer-2.5 --json /tmp/triggers.json
```

Record the actual accuracy, precision, and recall, and every failing case.

Then create `tests/triggers/README.md`, filling in the measured numbers and the date:

```markdown
# Trigger accuracy

One skill is published, so cross-triggering between our own skills is designed out
rather than measured. What remains is whether a single description fires across all
three domains and stays quiet outside them.

`../run_triggers.py` shows a model only the published skill's name and description
plus one user message, which is the same information an agent harness has when it
decides whether to load a skill. It does not load the skill body.

## Corpus

| File | Cases | Expectation |
|------|-------|-------------|
| `positives.yaml` | 12 | Must load the skill — four per authoring domain |
| `negatives.yaml` | 8 | Must not load it — excluded Aerospike topics and unrelated technology |
| `near-misses.yaml` | 5 | Must not load it — names Aerospike without needing guidance |

`domain` on each positive records which folder under `skills/` would have served the
prompt, so cross-triggering can be re-measured if those folders are ever published
separately.

## Threshold

CI fails below **<MEASURED>** overall accuracy, against `composer-2.5`.

That number is the first measured run rounded down, not a target chosen in advance.
A perfect score is explicitly not the goal: routing is stochastic, and a threshold set
at 1.0 would fail on noise. Raise it when a description change earns it.

| Date | Model | Accuracy | Precision | Recall |
|------|-------|----------|-----------|--------|
| <DATE> | composer-2.5 | <A> | <P> | <R> |

## Running it

```bash
export CURSOR_API_KEY=cursor_...
python3 tests/run_triggers.py --model composer-2.5 --json /tmp/triggers.json
```

Without a key, score a recorded run instead:

```bash
python3 tests/run_triggers.py --offline recorded-verdicts.json
```

## When a case fails

A failing positive means the description does not reach that domain. A failing negative
or near-miss means it reaches too far. Either way the fix is the description in
`scripts/skills_compile/published_skill.yaml`, not the corpus — do not edit a case to
make the run green.
```

- [ ] **Step 7: Document the runner in the tests guide and commit**

Add a row to the table in `tests/README.md`:

```markdown
| `triggers/` | Whether the published description fires on the right prompts | `python3 tests/run_triggers.py` — see [`triggers/README.md`](triggers/README.md) |
```

Delete the paragraph beneath that table saying trigger prompts, task files, and the
server-claim script "arrive with the testing plan". Two of the three now exist, and the rest
arrive in the tasks below.

Run: `python3 -m pytest tests/unit -q`

Expected: 36 passed (23 after Task 1, plus 18 here — the corpus test raises the count only
if you added cases beyond the 25 specified).

```bash
git add tests/triggers tests/run_triggers.py tests/unit/test_run_triggers.py tests/README.md
git commit -m "feat: measure trigger accuracy for the published description"
```

---

### Task 3: Gate pull requests on triggering and payload integrity

Three checks, one workflow file each where they differ in what they need. Payload integrity is deterministic and free, so it runs everywhere. The trigger check costs a model call, so it runs only where it can change the answer, against a pinned model, with a secret.

Finding F8 — no skill folder links outside itself — was verified by hand during design and never locked in. It belongs here.

**Files:**
- Create: `tests/unit/test_payload_integrity.py`
- Create: `.github/workflows/triggers.yml`
- Modify: `.github/workflows/publish-registries.yml`
- Modify: `tests/README.md`

**Interfaces:**
- Consumes: `tests.run_triggers.main`, `compile_agents.SINGLE_OUT`.
- Produces: no new code interface.

- [ ] **Step 1: Write the failing tests**

Create `tests/unit/test_payload_integrity.py`:

```python
"""What we hand a registry must be self-contained and current: a skill folder
that links outside itself is broken the moment it is installed on its own."""

import pathlib
import re

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SKILL_DIRS = sorted(p.parent for p in REPO_ROOT.glob("skills/*/SKILL.md")) + [
    REPO_ROOT / "compiled-skills" / "aerospike"
]
# Markdown links, minus anything that is not a repository-relative path.
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def _relative_targets(text):
    for target in LINK.findall(text):
        target = target.split("#", 1)[0].strip()
        if not target or "://" in target or target.startswith("mailto:"):
            continue
        yield target


@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda p: p.name)
def test_no_skill_links_outside_its_own_folder(skill_dir):
    escapes = []
    for md in sorted(skill_dir.rglob("*.md")):
        for target in _relative_targets(md.read_text(encoding="utf-8")):
            resolved = (md.parent / target).resolve()
            if skill_dir.resolve() not in resolved.parents and resolved != skill_dir:
                escapes.append(f"{md.relative_to(REPO_ROOT)} -> {target}")

    assert escapes == []


@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda p: p.name)
def test_every_relative_link_resolves_to_a_file_that_exists(skill_dir):
    missing = []
    for md in sorted(skill_dir.rglob("*.md")):
        for target in _relative_targets(md.read_text(encoding="utf-8")):
            if not (md.parent / target).exists():
                missing.append(f"{md.relative_to(REPO_ROOT)} -> {target}")

    assert missing == []
```

- [ ] **Step 2: Run the tests and verify they pass or reveal a real defect**

Run: `python3 -m pytest tests/unit/test_payload_integrity.py -v`

Expected: 8 passed — two checks across four skill folders. These lock in behavior verified by hand during design, so passing on
first run is the expected outcome — that is what makes them a regression guard rather than
a bug report.

If either fails, you have found a real defect. Do not weaken the test. Report what it found
and stop.

- [ ] **Step 3: Add the trigger workflow**

Create `.github/workflows/triggers.yml`, following the structure and pinned action SHAs
already used by `.github/workflows/tests.yml`:

```yaml
# Measures whether the published skill's description fires on the prompts it should.
#
# This is the only workflow that spends money, so it runs just where the answer can
# change: the description, the compiled artifact, or the corpus. The threshold lives in
# tests/triggers/README.md and is set from a measured run, not chosen in advance.
name: triggers

on:
  pull_request:
    paths:
      - "skills/**"
      - "compiled-skills/**"
      - "scripts/skills_compile/published_skill.yaml"
      - "tests/triggers/**"
      - "tests/run_triggers.py"
      - ".github/workflows/triggers.yml"

permissions:
  contents: read

jobs:
  triggers:
    runs-on: ubuntu-latest
    # Without a key the run cannot happen; skip rather than fail, so a fork PR
    # does not report a broken build for a secret it was never going to have.
    if: ${{ github.event.pull_request.head.repo.full_name == github.repository }}
    env:
      TRIGGER_MODEL: composer-2.5
      MIN_ACCURACY: "<MEASURED>"
    steps:
      - name: Harden the runner (Audit all outbound calls)
        uses: step-security/harden-runner@9af89fc71515a100421586dfdb3dc9c984fbf411 # v2.19.4
        with:
          egress-policy: audit

      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - run: pip install -r scripts/requirements-compile.txt cursor-sdk

      - name: Score the published description
        env:
          CURSOR_API_KEY: ${{ secrets.CURSOR_API_KEY }}
        run: |
          python3 tests/run_triggers.py \
            --model "${TRIGGER_MODEL}" \
            --min-accuracy "${MIN_ACCURACY}" \
            --json triggers.json

      - name: Append the score to the job summary
        if: always()
        run: |
          {
            echo "## Trigger accuracy"
            echo
            if [[ -f triggers.json ]]; then
              jq -r '"Model: `" + .model + "`  \nAccuracy: **" + (.accuracy|tostring) + "**  \nPrecision: " + (.precision|tostring) + "  \nRecall: " + (.recall|tostring)' triggers.json
              echo
              if [[ "$(jq '.failures | length' triggers.json)" != "0" ]]; then
                echo "| Case | Expected | Got |"
                echo "|---|---|---|"
                jq -r '.failures[] | "| " + .[0] + " | " + .[1] + " | " + .[2] + " |"' triggers.json
              fi
            else
              echo "No score was produced."
            fi
          } >> "$GITHUB_STEP_SUMMARY"
```

Replace `<MEASURED>` with the threshold recorded in `tests/triggers/README.md` in Task 2.
The two must agree.

- [ ] **Step 4: Gate publishing on a fresh compiled artifact**

`publish-registries.yml` gates on spec conformance and the linter, but nothing checks that
the compiled artifact matches its sources — so a stale artifact could be submitted, and
neither registry documents a way to delete a submission.

In `.github/workflows/publish-registries.yml`, add a third gate job alongside `gate-spec`
and `gate-lint`:

```yaml
  gate-compiled:
    uses: ./.github/workflows/compile-agents.yml
```

Then add it to the `preflight` job's `needs` list, which becomes:

```yaml
    needs: [gate-spec, gate-lint, gate-compiled]
```

For `compile-agents.yml` to be callable this way it needs a `workflow_call` trigger. Add one
to its `on:` block, matching how `spec-conformance.yml` does it:

```yaml
  # Called by publish-registries.yml so a release cannot publish a stale artifact.
  workflow_call:
```

- [ ] **Step 5: Verify the workflows are valid and the suite is green**

Run:

```bash
python3 -c "import yaml; [yaml.safe_load(open(f)) for f in ['.github/workflows/triggers.yml','.github/workflows/publish-registries.yml','.github/workflows/compile-agents.yml']]; print('valid')"
python3 -m pytest tests/unit -q
```

Expected: `valid`, then 44 passed.

- [ ] **Step 6: Document and commit**

Add a row to `tests/README.md`'s table for `unit/test_payload_integrity.py`, describing it
as the check that skill folders are self-contained and their links resolve.

```bash
git add tests/unit/test_payload_integrity.py tests/README.md \
        .github/workflows/triggers.yml .github/workflows/publish-registries.yml \
        .github/workflows/compile-agents.yml
git commit -m "ci: gate on trigger accuracy, payload integrity, and a fresh artifact"
```

---

### Task 4: Verify the getting-started claims against a running server

The failure mode this addresses is guidance that was correct two releases ago. Reading the docs cannot catch it; booting the server can. Each assertion names the claim it verifies, so a drifted claim points at its own source.

**Files:**
- Create: `tests/content/verify-server-claims.sh`
- Modify: `tests/README.md`

**Interfaces:**
- Consumes: the declared range `7.0+` from Task 1.
- Produces: an executable script, exit 0 when every claim holds.

- [ ] **Step 1: Write the script**

Create `tests/content/verify-server-claims.sh` and make it executable with `chmod +x`:

```bash
#!/usr/bin/env bash
# Verify the getting-started skill's factual claims against a real server.
#
# Reading documentation cannot catch guidance that was true two releases ago;
# booting the server can. Each check names the claim it verifies, so a drifted
# claim points at the file that makes it.
#
# Usage: tests/content/verify-server-claims.sh [--tag TAG]
set -euo pipefail

IMAGE="aerospike/aerospike-server"
TAG="latest"
CONTAINER="aerospike-claim-check-$$"
SKILL="skills/aerospike-getting-started/SKILL.md"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag) TAG="${2:?--tag needs a value}"; shift 2 ;;
    -h|--help) sed -n '2,9p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done

command -v docker >/dev/null 2>&1 || { echo "docker is required." >&2; exit 3; }

passed=0
failed=0

check() {
  # check <claim> <source> <command...>
  local claim="$1" source="$2"; shift 2
  if "$@" >/dev/null 2>&1; then
    echo "  ok    ${claim}  (${source})"
    passed=$((passed + 1))
  else
    echo "  FAIL  ${claim}  (${source})" >&2
    failed=$((failed + 1))
  fi
}

asinfo() { docker exec "${CONTAINER}" asinfo -v "$1"; }
asinfo_has() { asinfo "$1" | grep -qE "$2"; }

cleanup() { docker rm -f "${CONTAINER}" >/dev/null 2>&1 || true; }
trap cleanup EXIT

echo "Booting ${IMAGE}:${TAG}"
docker run -d --name "${CONTAINER}" -p 3000-3002:3000-3002 "${IMAGE}:${TAG}" >/dev/null

for _ in $(seq 1 60); do
  if docker logs "${CONTAINER}" 2>&1 | grep -q "service ready"; then break; fi
  sleep 1
done
docker logs "${CONTAINER}" 2>&1 | grep -q "service ready" || {
  echo "Server did not report 'service ready' within 60s." >&2
  docker logs "${CONTAINER}" 2>&1 | tail -20 >&2
  exit 1
}

build="$(asinfo build | tr -d '\r')"
echo "Server build: ${build}"
echo

# The image name the skill tells a new user to run.
check "Community image ${IMAGE} boots and serves" "${SKILL}" \
  asinfo_has "status" "ok"

# The declared floor is 7.0+; anything older invalidates the documented flow.
check "Build is 7.0 or newer" "${SKILL} metadata.server_versions" \
  bash -c "[[ \$(printf '%s\n7.0.0\n' '${build}' | sort -V | head -1) == '7.0.0' ]]"

# "The default namespace is test. NEVER use default, aerospike, or main."
check "Namespace 'test' exists out of the box" "${SKILL} critical rules" \
  asinfo_has "namespaces" "(^|;)test(;|$)"
check "Namespace 'default' does not exist" "${SKILL} critical rules" \
  bash -c "! docker exec ${CONTAINER} asinfo -v namespaces | grep -qE '(^|;)default(;|\$)'"

# cluster-name is mandatory from 7.0.0, which is why the floor is 7.0.
check "cluster-name is a service config key" "${SKILL} local config" \
  asinfo_has "get-config:context=service" "cluster-name="

# Expiry: nsup-period drives expiration, default-ttl sets the record default.
check "nsup-period governs expiration" "${SKILL} TTL and NSUP" \
  asinfo_has "get-config:context=namespace;id=test" "nsup-period="
check "default-ttl is a namespace config key" "${SKILL} TTL and NSUP" \
  asinfo_has "get-config:context=namespace;id=test" "default-ttl="

# The client port the skill tells users to map.
check "Client port 3000 is reachable from the host" "${SKILL} ports" \
  bash -c "exec 3<>/dev/tcp/127.0.0.1/3000"

echo
echo "${passed} claim(s) verified, ${failed} failed."
[[ "${failed}" -eq 0 ]]
```

- [ ] **Step 2: Run it and record the output**

Run: `chmod +x tests/content/verify-server-claims.sh && ./tests/content/verify-server-claims.sh`

Expected: the server boots, the build is printed, and every check reports `ok`, ending
`8 claim(s) verified, 0 failed.`

If a check fails, that is the point of the script: the skill's claim has drifted from server
behavior. Record which claim, which server build, and what the server actually reported.
Do not weaken the check to make it pass — report it, and it becomes a finding in Task 6.

- [ ] **Step 3: Confirm it cleans up after itself**

Run: `docker ps -a --filter "name=aerospike-claim-check" --format '{{.Names}}'`

Expected: no output. The `trap cleanup EXIT` removed the container.

- [ ] **Step 4: Document and commit**

Add a row to `tests/README.md`'s table:

```markdown
| `content/verify-server-claims.sh` | The getting-started skill's claims against a real server | `./tests/content/verify-server-claims.sh` (needs Docker) |
```

Note beneath the table that the script boots `aerospike/aerospike-server:latest` and that
`--tag` targets a specific release.

```bash
git add tests/content/verify-server-claims.sh tests/README.md
git commit -m "test: verify getting-started claims against a running server"
```

---

### Task 5: Write the data-modeling task corpus

`aerospike-data-modeling` has never been measured: it is absent from the evaluation harness's `source_skills` and from all 61 tasks. This task writes the prompts. Task 6 wires the harness to read them.

The corpus deliberately includes guide escalation, which exercises the rule the parser bug truncated — had this task existed, it would have caught that bug.

**Files:**
- Create: `tests/tasks/data-modeling.yaml`
- Create: `tests/unit/test_task_corpus.py`
- Modify: `tests/README.md`

**Interfaces:**
- Consumes: the harness's task schema — `id`, `prompt`, `skill`, `category`, `required_all`, `required_any`, `forbidden`, `rubric`, `expected_refs`, `weight`. Regex fields are case-insensitive and searched against the whole output.
- Produces: `tests/tasks/data-modeling.yaml`, a YAML list of task dicts, all with `skill: aerospike-data-modeling`.

- [ ] **Step 1: Write the corpus**

Create `tests/tasks/data-modeling.yaml`:

```yaml
# End-to-end tasks for aerospike-data-modeling, the skill no evaluation run has
# ever measured. Schema matches the harness in aerospike/agent-skills-eval,
# which reads this file through its vendor/agent-skills submodule.
- id: dm-design-time-workflow
  skill: aerospike-data-modeling
  category: data-modeling
  prompt: >-
    We're starting a new service on Aerospike and have no schema yet. Walk me
    through how to get from our requirements to a data model.
  required_all:
    - "access pattern"
    - "key"
  required_any:
    - "entit(y|ies)"
    - "cardinality"
    - "read|write path"
  forbidden:
    - "CREATE TABLE"
    - "\\bJOIN\\b"
  rubric:
    - "Starts from access patterns rather than an entity-relationship diagram"
    - "Covers record granularity, key design, and bin structure"
    - "Names the deliverables the process produces"
  expected_refs:
    - model-design-time-workflow.md
  weight: 1.0

- id: dm-guide-escalation
  skill: aerospike-data-modeling
  category: data-modeling
  prompt: >-
    We need a complete Aerospike data model for a new product, not just advice.
    What's the authoritative process, and is there something more detailed than
    this skill?
  required_all:
    - "data-modeling-guide"
  required_any:
    - "github\\.com/aerospike"
    - "fetch|clone|repository"
  forbidden:
    - "no (additional|further) (guide|resource)"
  rubric:
    - "Points at the external data modeling guide repository by name"
    - "Says a full model should not be produced from this skill alone"
  expected_refs:
    - ex-guide-escalation.md
  weight: 1.0

- id: dm-failure-modes-review
  skill: aerospike-data-modeling
  category: data-modeling
  prompt: >-
    Review this Aerospike design before we build. One set per domain noun, six
    secondary indexes for our main queries, a separate bin per tag, and a
    followers list bin per user with no cap.
  required_all:
    - "secondary index|SI"
    - "unbounded|cap|grow"
  required_any:
    - "bin per tag|bins like columns"
    - "key lookup|primary key"
  forbidden:
    - "looks (good|fine)"
    - "no (issues|problems) "
  rubric:
    - "Flags secondary indexes used as the primary query mechanism"
    - "Flags the unbounded followers collection"
    - "Flags a bin count that scales with data rather than schema"
  expected_refs:
    - model-failure-modes-checklist.md
  weight: 1.0

- id: dm-record-granularity
  skill: aerospike-data-modeling
  category: data-modeling
  prompt: >-
    We have users, and each user has a stream of events. Should events be their
    own Aerospike set, or live inside the user record?
  required_all:
    - "cardinality|how many|growth"
  required_any:
    - "access pattern"
    - "record size"
    - "unbounded"
  forbidden:
    - "\\bJOIN\\b"
  rubric:
    - "Makes the decision follow cardinality and the read path, not the noun list"
    - "Raises record size or unbounded growth as the deciding constraint"
  # No expected_refs: granularity, denormalization, and hot keys are argued in the
  # development skill's references, not the data-modeling skill's four. One skill
  # ships, so the split does not reach a user, and naming a file across skills
  # would assert a layout we do not have.
  weight: 1.0

- id: dm-denormalization
  skill: aerospike-data-modeling
  category: data-modeling
  prompt: >-
    Rendering one post in our Aerospike feed needs the author's display name. Do
    I read the user record too, or store the name on the post?
  required_all:
    - "denormaliz|duplicat"
  required_any:
    - "no joins|there are no joins"
    - "round trip"
  forbidden:
    - "\\bJOIN\\b the"
    - "foreign key"
  rubric:
    - "Chooses duplication over a second read, and says why"
    - "Notes the update cost duplication creates"
  weight: 1.0

- id: dm-hot-key
  skill: aerospike-data-modeling
  category: data-modeling
  prompt: >-
    I want one Aerospike record holding a global counter that every request
    increments. Any problem with that?
  required_all:
    - "hot key|hotspot|hot spot"
  required_any:
    - "shard|split|partition"
    - "single (record|key)"
  forbidden:
    - "that (works|is fine) well"
  rubric:
    - "Identifies the single-record hot key"
    - "Offers sharding the counter across records as the fix"
  weight: 1.0

- id: dm-deliverables
  skill: aerospike-data-modeling
  category: data-modeling
  prompt: >-
    When you finish designing an Aerospike data model for us, what documents
    should we end up with?
  required_all:
    - "schema (guide|summary)"
  required_any:
    - "schema summary"
    - "schema guide"
  forbidden:
    - "\\bERD\\b"
  rubric:
    - "Names the schema guide and the schema summary as the deliverables"
    - "Describes what each one is for"
  expected_refs:
    - model-deliverables-schema-guide-summary.md
  weight: 1.0
```

- [ ] **Step 2: Write the failing test**

Create `tests/unit/test_task_corpus.py`:

```python
"""The task corpus is consumed by a harness in another repository, so its shape
is validated here rather than discovered there."""

import pathlib
import re

import pytest
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
TASKS_DIR = REPO_ROOT / "tests" / "tasks"
SCHEMA_KEYS = {
    "id",
    "prompt",
    "skill",
    "category",
    "required_all",
    "required_any",
    "forbidden",
    "rubric",
    "expected_refs",
    "blacklist_targets",
    "weight",
}


def _tasks():
    for path in sorted(TASKS_DIR.glob("*.yaml")):
        for entry in yaml.safe_load(path.read_text(encoding="utf-8")) or []:
            yield path.name, entry


def test_the_corpus_is_not_empty():
    assert list(_tasks())


@pytest.mark.parametrize(
    "filename,task",
    list(_tasks()),
    ids=lambda v: v["id"] if isinstance(v, dict) else v,
)
def test_task_uses_only_schema_keys(filename, task):
    assert set(task) <= SCHEMA_KEYS, f"{task['id']} in {filename}"


def test_task_ids_are_unique():
    ids = [task["id"] for _name, task in _tasks()]

    assert len(ids) == len(set(ids))


def test_every_regex_field_compiles():
    bad = []
    for _name, task in _tasks():
        for field in ("required_all", "required_any", "forbidden"):
            for pattern in task.get(field, []):
                try:
                    re.compile(pattern)
                except re.error as exc:
                    bad.append(f"{task['id']}.{field}: {pattern!r} ({exc})")

    assert bad == []


def test_expected_refs_name_files_that_exist():
    missing = []
    for _name, task in _tasks():
        skill_dir = REPO_ROOT / "skills" / task["skill"]
        for ref in task.get("expected_refs", []):
            if not (skill_dir / "references" / ref).exists() and not (skill_dir / ref).exists():
                missing.append(f"{task['id']} -> {ref}")

    assert missing == []


def test_data_modeling_is_covered():
    skills = {task["skill"] for _name, task in _tasks()}

    assert "aerospike-data-modeling" in skills
```

- [ ] **Step 3: Run the tests**

Run: `python3 -m pytest tests/unit/test_task_corpus.py -v`

Expected: all pass. If `test_expected_refs_name_files_that_exist` fails, a task names a
reference file that does not exist — fix the task's `expected_refs`, not the test.

If the `ids=` lambda errors during collection, drop the `ids` argument. The identifier is a
convenience, not a requirement.

- [ ] **Step 4: Document and commit**

Add a row to `tests/README.md`:

```markdown
| `tasks/` | End-to-end task prompts, read by the evaluation harness through its submodule | See [`agent-skills-eval`](https://github.com/aerospike/agent-skills-eval) |
```

Run: `python3 -m pytest tests/unit -q`

Expected: 56 passed — 44 after Task 3, plus 12 here (five checks and one parametrized over
the seven tasks).

```bash
git add tests/tasks tests/unit/test_task_corpus.py tests/README.md
git commit -m "test: add data-modeling task corpus for the evaluation harness"
```

---

### Task 6: Extend the evaluation harness

**This task changes a different repository.** It lands as its own pull request in `aerospike/agent-skills-eval`, on a branch there. Nothing in this task touches `agent-skills`.

The harness currently generates variants from two source skills, holds all 61 tasks in its own `eval/tasks/`, and compares five structural variants — none of which is the shape we now publish.

**Files** (all under `/home/lyndon/github/agent-skills-eval`):
- Modify: `eval/config.yaml`
- Modify: `eval/lib/io.py`
- Modify: `eval/variants/generate.py`
- Modify: `eval/tasks/development-extended.yaml`
- Modify: `README.md`

**Interfaces:**
- Consumes: `tests/tasks/data-modeling.yaml` from `agent-skills`, visible at `vendor/agent-skills/tests/tasks/data-modeling.yaml`.
- Produces: a `v5_published` variant whose manifest `kind` is `monolith`, so the existing preamble builder handles it with no runner change.

- [ ] **Step 1: Create the branch and refresh the submodule**

```bash
cd /home/lyndon/github/agent-skills-eval
git checkout -b feat/AIE-16-measure-data-modeling
git submodule update --init --recursive
git -C vendor/agent-skills fetch origin
git -C vendor/agent-skills checkout origin/feat/AIE-16-skill-tests
ls vendor/agent-skills/tests/tasks/data-modeling.yaml
```

Expected: the file lists. If it does not, the `agent-skills` branch has not been pushed yet —
stop and report NEEDS_CONTEXT.

- [ ] **Step 2: Add the third source skill and the published variant**

In `eval/config.yaml`, add the data-modeling skill to `source_skills`:

```yaml
source_skills:
  - vendor/agent-skills/skills/aerospike-development
  - vendor/agent-skills/skills/aerospike-getting-started
  - vendor/agent-skills/skills/aerospike-data-modeling
```

Add the new variant to the `variants` list, after `v4_hybrid`, and extend the comment block
above it with one line:

```yaml
#   v5_published - the artifact we actually ship: compiled-skills/aerospike/SKILL.md
```

```yaml
variants:
  - v0_baseline
  - v1_modular
  - v2_monolith
  - v3_stripped
  - v4_hybrid
  - v5_published
```

- [ ] **Step 3: Build the published variant**

In `eval/variants/generate.py`, add a builder that copies the shipped artifact rather than
re-deriving it, so the variant is the file users install and not a lookalike. It takes
`skills` and ignores it, because `generate()` passes that argument to every builder except
`v0_baseline`. Place it after `build_hybrid` and register it in `_BUILDERS`:

```python
def build_published(out: pathlib.Path, skills: list[skillsrc.SkillSource]) -> dict:
    """The artifact we actually publish, copied rather than re-rendered.

    Every other variant is generated from ``skills`` so the comparison isolates
    structure. This one exists to measure the exact file users install, so
    re-deriving it would defeat the point -- hence the unused argument.
    """
    src = REPO_ROOT / "vendor/agent-skills/compiled-skills/aerospike/SKILL.md"
    tok = _write(out / "SKILL.md", src.read_text(encoding="utf-8"))
    return {
        "variant": out.name,
        "kind": "monolith",
        "entries": {},
        "monolith": {"rel": "SKILL.md", "tokens": tok},
        "loadable": {},
        "total_tokens": tok,
    }
```

```python
_BUILDERS = {
    "v0_baseline": build_baseline,
    "v1_modular": build_modular,
    "v2_monolith": build_monolith,
    "v3_stripped": build_stripped,
    "v4_hybrid": build_hybrid,
    "v5_published": build_published,
}
```

`kind: "monolith"` is what makes this work without touching the runner: the preamble builder
already knows how to put a monolith variant in context.

- [ ] **Step 4: Read tasks from the submodule as well as locally**

`load_tasks(tasks_dir=None)` currently globs one directory, skips files whose names start
with `_`, and already raises on a duplicate id. Extend it to walk two directories instead of
one, keeping both behaviors — the duplicate check then covers the two directories for free,
so one file cannot silently shadow the other.

When `tasks_dir` is passed explicitly, keep reading only that directory: callers that pass a
path mean it, and tests rely on it.

Add a comment saying task prompts for newer skills are authored in `agent-skills` and
consumed here through the submodule, so a prompt change and a harness change land in separate
pull requests.

- [ ] **Step 5: Fix the `dev-ttl-void-time` rubric**

This task failed on every variant including the no-skill baseline in run `20260623-101343`.
The cause is its second `forbidden` pattern:

```yaml
    - "flip[^.]{0,30}never-?expire[^.]{0,30}(short|finite|ttl)"
```

The prompt itself asks about flipping never-expire records to a short TTL, so a correct
answer that warns against doing it still echoes that wording and trips the trap. "Flipping
never-expire records to a short finite TTL is risky" fails, while the reference good answer
passes only because it avoids the word "flip".

In `eval/tasks/development-extended.yaml`, replace that pattern with one that fires only on
endorsement, and add a comment recording why:

```yaml
  forbidden:
    - "short(er)? (ttl|void.?time)[^.]{0,40}\\b(fine|safe)\\b"
    # Only an endorsement is a failure. The prompt invites the words "flip",
    # "never-expire", and "short TTL", so matching them alone failed correct
    # answers that warn against the plan -- which is what run 20260623-101343 hit.
    - "flip[^.]{0,30}never-?expire[^.]{0,40}\\b(fine|safe|no (risk|problem)|recommend)\\b"
```

- [ ] **Step 6: Verify with a mock run**

Mock mode needs no key and no network.

```bash
cd eval
python3 -m pip install -r requirements.txt
make all
```

Expected: generate, run, grade, and report all succeed. Then confirm the new inputs took
effect:

```bash
python3 -c "
import json, pathlib
meta = json.loads((pathlib.Path('out/runs')/open('out/LATEST').read().strip()/'meta.json').read_text())
print('variants:', meta['variants'])
print('tasks:', meta['n_tasks'])
"
ls out/variants/v5_published/
```

Expected: `variants` includes `v5_published`; `n_tasks` is 68, the previous 61 plus the seven
data-modeling tasks; and `out/variants/v5_published/SKILL.md` exists and opens with the
`---` frontmatter fence.

Also confirm the rubric fix does not break the task it touches:

```bash
python3 -m runner.run_eval --mode mock --task dev-ttl-void-time --trials 1
python3 -m grader.grade --judge off
```

Expected: the run completes and the good mock answer still grades `correctness` 1.0.

- [ ] **Step 7: Commit and open the pull request**

Update `README.md` to say task prompts for `aerospike-data-modeling` live in the
`agent-skills` repository under `tests/tasks/` and are read through the submodule, and that
the submodule pointer must be refreshed when those prompts change.

```bash
git add eval/config.yaml eval/lib/io.py eval/variants/generate.py \
        eval/tasks/development-extended.yaml README.md
git commit -m "feat: measure data modeling and the published variant"
git push -u origin feat/AIE-16-measure-data-modeling
```

Do not commit the submodule pointer move to a feature branch of `agent-skills`; leave
`vendor/agent-skills` unstaged and note in the pull request that the pointer moves once the
`agent-skills` branch merges.

Report the pull request URL. Do not run a live evaluation — it costs real money and is a
separate, deliberate act.

---

### Task 7: Close the findings ledger

The final acceptance criterion asks that every finding be fixed or triaged with a decision recorded. Four are still open, and this plan resolves three of them.

**Files:**
- Modify: `tests/FINDINGS.md`
- Modify: `tests/README.md`

**Interfaces:**
- Consumes: outcomes of Tasks 1 through 6.
- Produces: no code interface.

- [ ] **Step 1: Update the open findings**

In `tests/FINDINGS.md`, rewrite the decision and status cells for the findings this plan
closes. Use what actually happened, not what was planned — if a task turned up something
different, record that instead.

- **F6** (no declared server version range) — Fixed in Task 1. Record the declared value
  `"7.0+"`, that all four skills carry it, and the reason for the floor: `cluster-name`
  became mandatory in Database 7.0.0, so the documented local flow cannot work below it.
- **F7** (`aerospike-data-modeling` never measured) — Record the seven tasks added in Task 5
  and the harness pull request from Task 6. It stays open until that pull request merges and
  a live run reports numbers; say so, and link the pull request.
- **F8** (skill folders self-contained) — Fixed in Task 3. Record that
  `tests/unit/test_payload_integrity.py` now locks it in for all four skills, and that it
  also checks every relative link resolves.
- **F9** (`dev-ttl-void-time` failed on every variant) — Fixed in Task 6. Record the actual
  cause: the second `forbidden` pattern matched vocabulary the prompt itself invites, so
  answers that correctly warned against the user's plan were failed for echoing it. Note it
  was a grader defect, not a skill defect, which is what the original run's report suspected.

Then add rows for anything Tasks 2 and 4 turned up:

- The trigger run's measured accuracy, precision, and recall, and any case that failed. If a
  positive failed, the description does not reach that domain; if a negative or near-miss
  failed, it reaches too far. Either is a finding with a decision, not a number to bury.
- Any claim `verify-server-claims.sh` found to have drifted from server behavior, with the
  server build it was checked against.

If a task produced no finding, do not invent one. A clean run is a result.

- [ ] **Step 2: Record the manual client API pass**

The design says client API signatures get a manual check against official SDK sources,
because automating it is not worth the cost. Do that pass now for the signatures the skills
actually show — the Python and Node.js client constructor, `put`, `get`, `operate`, and the
batch read entry point — against the current official client documentation.

Add one ledger row recording the date, which SDK versions you checked against, what you
verified, and anything that had drifted. If everything matches, record that; a verified-clean
manual check is the evidence the acceptance criterion asks for.

- [ ] **Step 3: Note what remains manual**

In `tests/README.md`, under the "Before publishing" section, list the checks that are not
automated and must be run by a person: the live evaluation run in the harness repository,
the client API signature pass, and verifying the two GitHub URLs in F10 resolve once both
repositories are public.

- [ ] **Step 4: Verify and commit**

Run:

```bash
python3 -m pytest tests/unit -q
python3 scripts/compile-agents.py --shape stripped --check
```

Expected: all pass, artifact current.

```bash
git add tests/FINDINGS.md tests/README.md
git commit -m "docs: close the findings this plan resolves"
```

---

## Verification after all tasks

```bash
python3 -m pytest tests/unit -v
python3 scripts/compile-agents.py --shape stripped --check
./scripts/validate-spec.sh
./scripts/validate-skill.sh --ci; echo "exit=$?"
./tests/content/verify-server-claims.sh
python3 tests/run_triggers.py --model composer-2.5 --min-accuracy <THRESHOLD>
git status --short
```

Expected: every suite passes, the linter exits 0 or 2, every server claim verifies, the
trigger run meets its recorded threshold, and the working tree is clean.

## Acceptance criteria coverage

| AIE-16 criterion | Where this plan meets it |
|------------------|--------------------------|
| Trigger accuracy verified, cross-triggering checked | Task 2 — cross-triggering designed out by publishing one skill; the corpus keeps per-domain expectations so it can be re-measured |
| Content spot-checked against current server behavior | Tasks 1 and 4 — a declared range, then executable verification against a booted server |
| Clean install verified on Claude, Gemini, Cursor | Met in the previous branch: payload integrity plus documented, corrected install locations |
| End-to-end runs show clear improvement over baseline | Tasks 5 and 6 — against the harness's existing `v0_baseline` control |
| Test prompts committed to the repo | Tasks 2 and 5, under `tests/` |
| All findings fixed or triaged with a decision recorded | Task 7 |

## Out of scope

Making either repository public ([AIE-17](https://aerospike.atlassian.net/browse/AIE-17)),
documentation references ([AIE-14](https://aerospike.atlassian.net/browse/AIE-14)), the blog
post ([AIE-15](https://aerospike.atlassian.net/browse/AIE-15)), retiring the three authoring
folders, the stripped compile format, and running a live evaluation, which costs real money
and is a deliberate separate act.
