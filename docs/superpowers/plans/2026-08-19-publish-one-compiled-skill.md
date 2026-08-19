# Publish One Compiled Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compile the three authoring skills into one spec-valid published skill, fix the parser bug that corrupts it, and point registries, validators, and documentation at that single artifact.

**Architecture:** `skills/` stays the hand-maintained source of three skills. `scripts/compile-agents.py` renders them into a single published skill at `compiled-skills/aerospike/SKILL.md`, carrying hand-written YAML frontmatter so registries can validate it. The existing `compiled-skills/SKILLS.md` is replaced by that file. Both validators and both publish scripts move from iterating `skills/` to targeting the one published artifact.

**Tech Stack:** Python 3.10+ (3.12 in CI), PyYAML, pytest 7.4, bash, jq, GitHub Actions.

## Global Constraints

- Spec frontmatter allows only these keys: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. Anything else goes under `metadata`.
- `metadata` values must be strings. Quote dates (`"2026-08-19"`), or YAML parses them into date objects.
- A skill's YAML `name` must equal its parent folder name.
- Commit messages are Conventional Commits, enforced by commitlint (`@commitlint/config-conventional`): lowercase `type: subject`, no sentence-case subject, header under 100 characters.
- The stripped compile format is settled. Do not change what `render_stripped` emits beyond the parser fix in Task 1.
- `skills/` remains the source of truth and stays published as three authoring folders on disk; only what registries *receive* changes.
- Every task ends with the repository in a state where `python3 scripts/compile-agents.py --shape stripped --check` passes.

---

### Task 1: Restrict section labels to the canonical set

`labeled_sections` splits a reference file on *any* standalone bold line. Three files contain bold content lines — a bolded URL, seven enumerated headings, one "Gotcha" heading — so the parser reads them as section boundaries and truncates the rule they sit inside. 4,880 characters of rule content are currently misfiled. In the shipped artifact the visible damage is one rule truncated mid-sentence, losing the data-modeling guide URL.

The reference template defines exactly five labels. Restricting the split to that closed set fixes every case.

**Files:**
- Create: `pytest.ini`
- Create: `tests/unit/test_skillsrc.py`
- Modify: `scripts/skills_compile/skillsrc.py:20`
- Regenerate: `compiled-skills/SKILLS.md`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `skillsrc.CANONICAL_LABELS: tuple[str, ...]` equal to `("Rule", "Why", "Prefer", "Avoid", "See also")`. `labeled_sections(body: str) -> dict[str, str]` keeps its existing signature and returns only canonical keys.

- [ ] **Step 1: Add the pytest configuration**

Create `pytest.ini`:

```ini
[pytest]
# Tests import the compiler as `scripts.skills_compile.*`, matching how
# scripts/compile-agents.py imports it, so the repository root must be importable.
pythonpath = .
testpaths = tests/unit
```

- [ ] **Step 2: Write the failing tests**

Create `tests/unit/test_skillsrc.py`:

```python
"""The reference-file parser must treat only the template's five labels as
section boundaries. Bold content lines are content, not headings."""

from scripts.skills_compile.skillsrc import labeled_sections


def test_bolded_url_line_does_not_split_the_rule():
    body = (
        "**Rule**\n\n"
        "The full process lives in the\n"
        "**`https://github.com/aerospike/data-modeling-guide`**\n"
        "repository. Fetch it and follow its checklist.\n\n"
        "**Prefer**\n\n"
        "- Reading current values from the guide\n"
    )

    sections = labeled_sections(body)

    assert set(sections) == {"Rule", "Prefer"}
    assert "data-modeling-guide" in sections["Rule"]
    assert sections["Rule"].endswith("Fetch it and follow its checklist.")


def test_bolded_enumerated_headings_stay_inside_the_rule():
    body = (
        "**Rule**\n\n"
        "Each failure mode below has a detection test.\n\n"
        "**1. Record granularity from the entity list.**\n"
        "*Detect:* count the sets.\n\n"
        "**2. Secondary indexes as the primary query mechanism.**\n"
        "*Detect:* list every access pattern.\n\n"
        "**Avoid**\n\n"
        "- Running these only at the end\n"
    )

    sections = labeled_sections(body)

    assert set(sections) == {"Rule", "Avoid"}
    assert "1. Record granularity" in sections["Rule"]
    assert "2. Secondary indexes" in sections["Rule"]


def test_bolded_gotcha_heading_stays_inside_the_avoid_list():
    body = (
        "**Avoid**\n\n"
        "- Reading a whole record when one bin will do\n\n"
        "**Gotcha: bin-scoped ops vs whole-record reads**\n"
        "A bin-scoped operation still reads the whole record from device.\n"
    )

    sections = labeled_sections(body)

    assert set(sections) == {"Avoid"}
    assert "Gotcha" in sections["Avoid"]


def test_all_five_canonical_labels_still_split():
    body = (
        "**Rule**\n\nR\n\n"
        "**Why**\n\nW\n\n"
        "**Prefer**\n\n- p\n\n"
        "**Avoid**\n\n- a\n\n"
        "**See also**\n\n- s\n"
    )

    assert set(labeled_sections(body)) == {
        "Rule",
        "Why",
        "Prefer",
        "Avoid",
        "See also",
    }
```

- [ ] **Step 3: Run the tests and verify they fail**

Run: `python3 -m pytest tests/unit/test_skillsrc.py -v`

Expected: the first three tests FAIL. `test_bolded_url_line_does_not_split_the_rule` fails on
`assert set(sections) == {"Rule", "Prefer"}` because the parsed keys also include
`` `https://github.com/aerospike/data-modeling-guide` ``. `test_all_five_canonical_labels_still_split` PASSES already.

- [ ] **Step 4: Restrict the label pattern**

In `scripts/skills_compile/skillsrc.py`, replace line 20:

```python
_LABEL_RE = re.compile(r"^\*\*(.+?)\*\*\s*$", re.MULTILINE)
```

with:

```python
# The five labels references/_template.md defines. Matching a closed set keeps
# bold *content* lines -- an enumerated heading, a bolded URL -- from being read
# as section boundaries, which silently truncates the rule they sit inside.
CANONICAL_LABELS = ("Rule", "Why", "Prefer", "Avoid", "See also")
_LABEL_RE = re.compile(
    r"^\*\*(" + "|".join(re.escape(label) for label in CANONICAL_LABELS) + r")\*\*\s*$",
    re.MULTILINE,
)
```

- [ ] **Step 5: Run the tests and verify they pass**

Run: `python3 -m pytest tests/unit/test_skillsrc.py -v`

Expected: 4 passed.

- [ ] **Step 6: Regenerate the compiled output and confirm the diff is exactly one line**

Run:

```bash
python3 scripts/compile-agents.py --shape stripped --check || echo "stale as expected"
python3 scripts/compile-agents.py --shape stripped --write
git diff --stat compiled-skills/
```

Expected: `--check` reports `compiled-skills/SKILLS.md is out of date`, then
`git diff --stat` shows `1 file changed, 1 insertion(+), 1 deletion(-)`.

Run: `git diff compiled-skills/SKILLS.md`

Expected: the line beginning `- This skill carries the decision layer.` gains
`https://github.com/aerospike/data-modeling-guide repository. For a new application or a
redesign, fetch it and follow its checklist — do not produce a complete model from this
skill alone.` No other line changes.

- [ ] **Step 7: Commit**

```bash
git add pytest.ini tests/unit/test_skillsrc.py scripts/skills_compile/skillsrc.py compiled-skills/
git commit -m "fix: parse only canonical labels so bold content stops truncating rules"
```

---

### Task 2: Emit a spec-valid published skill and retire SKILLS.md

Registries validate against the Agent Skills specification, which requires YAML frontmatter. `compiled-skills/SKILLS.md` has none, so it cannot be submitted. The compiler emits `compiled-skills/aerospike/SKILL.md` instead — folder name matching the frontmatter `name`, as the spec convention and the skills CLI both require.

The `description` is hand-written in its own source file rather than generated. It is the only input to whether an agent loads this skill, so it is reviewed like code.

**Files:**
- Create: `scripts/skills_compile/published_skill.yaml`
- Create: `tests/unit/test_compile_published_skill.py`
- Modify: `scripts/compile-agents.py`
- Delete: `compiled-skills/SKILLS.md`
- Regenerate: `compiled-skills/aerospike/SKILL.md`, `compiled-skills/manifest.json`

**Interfaces:**
- Consumes: `skillsrc.labeled_sections` from Task 1, unchanged.
- Produces: `compile_agents.PUBLISHED_NAME = "aerospike"`; `compile_agents.SINGLE_OUT = "compiled-skills/aerospike/SKILL.md"`; `compile_agents.LEGACY_SINGLE_OUT = "compiled-skills/SKILLS.md"`; `compile_agents.REPO_URL = "https://github.com/aerospike/agent-skills"`; `compile_agents._frontmatter() -> str` returning a `---`-fenced block; `compile_outputs(shape: str, skill_dirs: list[str], layout: str) -> dict[str, str]` keeping its signature.

- [ ] **Step 1: Write the frontmatter source**

Create `scripts/skills_compile/published_skill.yaml`. It holds the frontmatter body only —
no `---` fences, and no YAML comments, because the file is emitted verbatim into `SKILL.md`:

```yaml
name: aerospike
description: >-
  Work with the Aerospike core database end to end: run a local instance with
  Docker and verify a first write and read, build or review client code with the
  official SDKs (Python, Node.js, Go, Java, C#), and design a data model from
  requirements. Covers namespaces, sets, bins, keys, TTL and NSUP, collection
  data types, expressions, secondary indexes, batch and scan workflows, client
  policies, connection pooling, record sizing, and schema deliverables. Use when
  the user sets up Aerospike, writes or debugs Aerospike client code, models data
  for it, or evaluates it as a persistent replacement for Redis or Memcached in
  real-time, low-latency, feature-store, or user-profile workloads. Core database
  only: not Aerospike Graph, and not cluster operations, sizing, XDR, or backup
  and restore, which belong to Aerospike Operations documentation.
license: Apache-2.0
metadata:
  last_verified: "2026-08-19"
```

- [ ] **Step 2: Write the failing tests**

Create `tests/unit/test_compile_published_skill.py`:

```python
"""The compiled artifact is what registries fetch, so it must be a valid skill:
frontmatter they can parse, a name matching its folder, and a header that tells
an agent where the rule files it cites actually live."""

import importlib.util
import pathlib

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SPEC_KEYS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}


def _load_compiler():
    spec = importlib.util.spec_from_file_location(
        "compile_agents", REPO_ROOT / "scripts" / "compile-agents.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def compiler():
    return _load_compiler()


@pytest.fixture(scope="module")
def published(compiler):
    outputs = compiler.compile_outputs("stripped", compiler.DEFAULT_SKILLS, "single")
    return outputs, outputs[compiler.SINGLE_OUT]


def test_published_skill_lands_in_a_folder_named_after_the_skill(compiler):
    assert compiler.SINGLE_OUT == "compiled-skills/aerospike/SKILL.md"


def test_skills_md_is_no_longer_emitted(published):
    outputs, _ = published
    assert "compiled-skills/SKILLS.md" not in outputs


def test_frontmatter_parses_and_uses_only_spec_keys(compiler, published):
    from scripts.skills_compile.skillsrc import split_frontmatter

    _, text = published
    meta, _body = split_frontmatter(text)

    assert meta, "SKILL.md must open with a YAML frontmatter block"
    assert set(meta) <= SPEC_KEYS
    assert meta["name"] == "aerospike"
    assert meta["license"] == "Apache-2.0"
    assert isinstance(meta["metadata"]["last_verified"], str)


def test_description_covers_all_three_source_domains(published):
    _, text = published
    lowered = text[: text.index("---", 4)].lower()

    for term in ("docker", "client code", "data model"):
        assert term in lowered, f"description should mention {term!r}"
    for excluded in ("graph", "xdr"):
        assert excluded in lowered, f"description should rule out {excluded!r}"


def test_header_carries_the_repository_url_for_cited_rule_files(compiler, published):
    _, text = published
    assert compiler.REPO_URL in text
    assert "skills/<skill>/references/" in text


def test_body_is_the_stripped_render(published):
    _, text = published
    assert "# Aerospike agent rules" in text
    assert "## aerospike-data-modeling" in text
```

- [ ] **Step 3: Run the tests and verify they fail**

Run: `python3 -m pytest tests/unit/test_compile_published_skill.py -v`

Expected: FAIL. `test_published_skill_lands_in_a_folder_named_after_the_skill` fails with
`AssertionError: assert 'compiled-skills/SKILLS.md' == 'compiled-skills/aerospike/SKILL.md'`,
and the tests reading `outputs[compiler.SINGLE_OUT]` fail because the emitted file has no
frontmatter.

- [ ] **Step 4: Update the compiler**

In `scripts/compile-agents.py`, change the module docstring line 5 from:

```python
script builds the published ``compiled-skills/SKILLS.md`` that end users download.
```

to:

```python
script builds the published ``compiled-skills/aerospike/SKILL.md`` that registries
fetch and end users download. Its frontmatter is hand-written in
``scripts/skills_compile/published_skill.yaml``.
```

Replace the constants at lines 20-21:

```python
COMPILED_DIR = "compiled-skills"
SINGLE_OUT = f"{COMPILED_DIR}/SKILLS.md"
```

with:

```python
COMPILED_DIR = "compiled-skills"
PUBLISHED_NAME = "aerospike"
# Folder name must equal the frontmatter `name`: the spec convention, and what the
# skills CLI uses as the install directory.
SINGLE_OUT = f"{COMPILED_DIR}/{PUBLISHED_NAME}/SKILL.md"
LEGACY_SINGLE_OUT = f"{COMPILED_DIR}/SKILLS.md"
REPO_URL = "https://github.com/aerospike/agent-skills"
SPEC_KEYS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
```

Add the third-party import as its own group after the stdlib block, so the imports read:

```python
import argparse
import json
import pathlib
import sys

import yaml
```

Then define the frontmatter loader immediately above `_header`:

```python
def _frontmatter() -> str:
    """Return the published skill's YAML frontmatter block.

    Emitted verbatim rather than re-serialized, so the author controls formatting
    and ``--check`` stays byte-stable across runs. Validated here so a malformed
    header fails the compile instead of a registry submission.
    """
    src = REPO_ROOT / "scripts" / "skills_compile" / "published_skill.yaml"
    text = src.read_text(encoding="utf-8").strip("\n")
    meta = yaml.safe_load(text) or {}

    missing = {"name", "description", "license"} - set(meta)
    if missing:
        raise ValueError(f"{src.name} is missing required key(s): {sorted(missing)}")
    extra = set(meta) - SPEC_KEYS
    if extra:
        raise ValueError(
            f"{src.name} has non-spec key(s): {sorted(extra)}. "
            f"The spec allows only {sorted(SPEC_KEYS)}."
        )
    if meta["name"] != PUBLISHED_NAME:
        raise ValueError(
            f"{src.name} declares name {meta['name']!r} but the published folder is "
            f"{PUBLISHED_NAME!r}; they must match."
        )
    return f"---\n{text}\n---\n"
```

Replace `_header` so it names the repository the cited rule files live in:

```python
def _header(skill_dirs: list[str]) -> str:
    return (
        f"_Auto-generated from `{'`, `'.join(skill_dirs)}` in {REPO_URL}. "
        f"Rule files cited below by bare filename live under "
        f"`skills/<skill>/references/` in that repository. "
        f"Edit the skills under `skills/`, not this file._\n"
    )
```

In `compile_outputs`, replace the `single` branch:

```python
    if layout == "single":
        body = render(skills).strip()
        out[SINGLE_OUT] = f"{_frontmatter()}\n{_header(skill_dirs)}\n{body}\n"
        return out
```

In `main`, update the `--layout` help text:

```python
        help="single -> compiled-skills/aerospike/SKILL.md; multi -> one .md per skill",
```

And in the `--check` branch, add a leftover-file check immediately after the
`for rel, expected in outputs.items():` loop:

```python
        if (REPO_ROOT / LEGACY_SINGLE_OUT).exists():
            stale.append(f"{LEGACY_SINGLE_OUT} (superseded by {SINGLE_OUT}; delete it)")
```

- [ ] **Step 5: Run the tests and verify they pass**

Run: `python3 -m pytest tests/unit/ -v`

Expected: 10 passed (4 from Task 1, 6 here).

- [ ] **Step 6: Regenerate, delete the legacy file, and verify**

Run:

```bash
git rm compiled-skills/SKILLS.md
python3 scripts/compile-agents.py --shape stripped --write
python3 scripts/compile-agents.py --shape stripped --check
head -20 compiled-skills/aerospike/SKILL.md
cat compiled-skills/manifest.json
```

Expected: `--check` prints `compiled-skills/ is up to date (single, stripped).` The `head`
output opens with `---`, the frontmatter, a closing `---`, then the `_Auto-generated ... in
https://github.com/aerospike/agent-skills.` header. `manifest.json` lists
`compiled-skills/aerospike/SKILL.md` and no longer lists `compiled-skills/SKILLS.md`.

- [ ] **Step 7: Commit**

```bash
git add scripts/skills_compile/published_skill.yaml scripts/compile-agents.py \
        tests/unit/test_compile_published_skill.py compiled-skills/
git commit -m "feat: compile one spec-valid published skill, replacing SKILLS.md"
```

---

### Task 3: Validate the artifact we publish

Both validators are hardcoded to `skills/`, so the file registries actually fetch has never been checked. Extend both to cover the published skill while continuing to check the three authoring folders.

**Files:**
- Modify: `scripts/validate-spec.sh:14,29-39`
- Modify: `scripts/validate-skill.sh:6-8,40-44`
- Modify: `.github/workflows/spec-conformance.yml:17-24,63-75`
- Modify: `.github/workflows/skill-validator.yml:6-19,59-71`

**Interfaces:**
- Consumes: `compiled-skills/aerospike/SKILL.md` from Task 2.
- Produces: no code interface. `./scripts/validate-spec.sh` reports 4 skills checked; `./scripts/validate-skill.sh` checks both roots.

- [ ] **Step 1: Install both validators locally**

Run:

```bash
printf '\n# Local virtualenv for skills-ref, which has no PyPI release.\n.venv/\n' >> .gitignore
python3 -m venv .venv && . .venv/bin/activate
pip install "git+https://github.com/agentskills/agentskills.git@69ef37e9424c0a7ea9dd2293b559e43ec8176379#subdirectory=skills-ref"
go install github.com/agent-ecosystem/skill-validator/cmd/skill-validator@v1.5.5
export PATH="$PATH:$(go env GOPATH)/bin"
skills-ref --help && skill-validator --help
```

Expected: both print usage, and `git status --short` shows only the `.gitignore`
modification — no `.venv/` entry.

- [ ] **Step 2: Verify the published skill is currently unchecked**

Run: `./scripts/validate-spec.sh`

Expected: `All 3 skill(s) conform to the Agent Skills specification.` — three, not four,
confirming the published artifact is outside the gate.

- [ ] **Step 3: Extend the spec validator**

In `scripts/validate-spec.sh`, after line 14 (`SKILLS_DIR=...`) add:

```bash
# The compiled skill is what registries fetch and validate, so it must conform too.
PUBLISHED_DIR="${ROOT}/compiled-skills/aerospike"
```

Replace the loop at lines 31-39:

```bash
failed=()
checked=0
for skill_dir in "${SKILLS_DIR}"/*/; do
  [[ -f "${skill_dir}SKILL.md" ]] || continue
  checked=$((checked + 1))
  if ! skills-ref validate "${skill_dir%/}"; then
    failed+=("$(basename "${skill_dir%/}")")
  fi
done
```

with:

```bash
skill_dirs=()
for skill_dir in "${SKILLS_DIR}"/*/; do
  [[ -f "${skill_dir}SKILL.md" ]] && skill_dirs+=("${skill_dir%/}")
done
[[ -f "${PUBLISHED_DIR}/SKILL.md" ]] && skill_dirs+=("${PUBLISHED_DIR}")

failed=()
checked=0
for skill_dir in "${skill_dirs[@]}"; do
  checked=$((checked + 1))
  if ! skills-ref validate "${skill_dir}"; then
    failed+=("$(basename "${skill_dir}")")
  fi
done
```

- [ ] **Step 4: Verify the spec validator now covers four skills**

Run: `./scripts/validate-spec.sh`

Expected: `All 4 skill(s) conform to the Agent Skills specification.`

If it reports a failure for `aerospike`, the frontmatter from Task 2 is wrong — fix
`scripts/skills_compile/published_skill.yaml`, re-run
`python3 scripts/compile-agents.py --shape stripped --write`, and repeat.

- [ ] **Step 5: Extend the linter**

In `scripts/validate-skill.sh`, replace lines 7-8:

```bash
# Multi-skill root: skill-validator discovers each subdirectory that contains SKILL.md.
SKILL_DIR="${ROOT}/skills"
```

with:

```bash
# Multi-skill roots: skill-validator discovers each subdirectory containing SKILL.md.
# compiled-skills/ holds the published artifact, which must be linted like the sources.
SKILL_ROOTS=("${ROOT}/skills" "${ROOT}/compiled-skills")
```

Replace the `exec` at lines 40-44:

```bash
exec skill-validator check \
  "${strict_flag[@]}" \
  --allow-flat-layouts \
  "${extra_args[@]}" \
  "${SKILL_DIR}/"
```

with:

```bash
# Run per root and surface the worst exit code, so one clean root cannot mask a
# failure in the other. Exit 2 means warnings-only when --strict is off.
worst=0
for root in "${SKILL_ROOTS[@]}"; do
  set +e
  skill-validator check \
    "${strict_flag[@]}" \
    --allow-flat-layouts \
    "${extra_args[@]}" \
    "${root}/"
  code=$?
  set -e
  [[ "${code}" -gt "${worst}" ]] && worst="${code}"
done
exit "${worst}"
```

- [ ] **Step 6: Verify the linter covers both roots**

Run: `./scripts/validate-skill.sh --ci; echo "exit=$?"`

Expected: output for the three source skills and for `aerospike`, with `exit=0` or `exit=2`
(warnings-only). If `exit=1`, read the reported problem and fix it before continuing.

- [ ] **Step 7: Add compiled-skills to both workflows**

In `.github/workflows/spec-conformance.yml`, add `- "compiled-skills/**"` to the `paths`
list under both `pull_request` (after line 18) and `push` (after line 23). Then replace the
summary loop at lines 70-75:

```bash
            for skill_dir in skills/*/; do
              [ -f "${skill_dir}SKILL.md" ] || continue
```

with:

```bash
            for skill_dir in skills/*/ compiled-skills/aerospike/; do
              [ -f "${skill_dir}SKILL.md" ] || continue
```

In `.github/workflows/skill-validator.yml`, add `- "compiled-skills/**"` to the `paths` list
under both `pull_request` (after line 8) and `push` (after line 17). Then replace the summary
command at lines 65-67:

```bash
            skill-validator check \
              --allow-flat-layouts \
              -o markdown skills/
```

with:

```bash
            skill-validator check \
              --allow-flat-layouts \
              -o markdown skills/ compiled-skills/
```

- [ ] **Step 8: Commit**

```bash
git add .gitignore scripts/validate-spec.sh scripts/validate-skill.sh \
        .github/workflows/spec-conformance.yml .github/workflows/skill-validator.yml
git commit -m "fix: validate the compiled skill registries fetch, not just sources"
```

---

### Task 4: Submit one skill to the registries

Both publish scripts iterate `skills/` and submit three payloads. They should submit the single compiled skill instead.

**Files:**
- Modify: `scripts/publish-openagentskill.sh:2,46-47,69-73`
- Modify: `scripts/publish-upskill.sh:2,43-44,72-77`
- Modify: `.github/workflows/publish-registries.yml:1,3`
- Create: `tests/unit/test_publish_scripts.py`

**Interfaces:**
- Consumes: `compiled-skills/aerospike/SKILL.md` from Task 2.
- Produces: both scripts emit exactly one dry-run payload. openagentskill `skillPath` is `compiled-skills/aerospike/SKILL.md`; upskill target is `<repo-url>/tree/<ref>/compiled-skills/aerospike`. Receipt `skill` field is `aerospike` for both.

- [ ] **Step 1: Write the failing tests**

Create `tests/unit/test_publish_scripts.py`:

```python
"""Both registries must receive exactly one submission: the compiled skill."""

import json
import pathlib
import shutil
import subprocess

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
REPO_URL = "https://github.com/aerospike/agent-skills"


def _run(script, *args):
    result = subprocess.run(
        [str(REPO_ROOT / "scripts" / script), "--repo-url", REPO_URL, "--dry-run", *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_openagentskill_submits_only_the_compiled_skill():
    out = _run("publish-openagentskill.sh")

    assert out.count("DRY RUN") == 1
    assert "DRY RUN aerospike:" in out
    for retired in ("aerospike-getting-started", "aerospike-development"):
        assert retired not in out


def test_openagentskill_payload_points_at_the_compiled_skill():
    out = _run("publish-openagentskill.sh")
    payload = json.loads(out[out.index("{"):out.rindex("}") + 1])

    assert payload["repository"] == REPO_URL
    assert payload["skillPath"] == "compiled-skills/aerospike/SKILL.md"
    assert payload["submissionSource"] == "agent"


def test_upskill_submits_only_the_compiled_skill():
    out = _run("publish-upskill.sh", "--ref", "main")

    assert out.count("DRY RUN") == 1
    assert f"{REPO_URL}/tree/main/compiled-skills/aerospike" in out
    assert "/skills/aerospike-development" not in out


@pytest.mark.parametrize("script", ["publish-openagentskill.sh", "publish-upskill.sh"])
def test_scripts_fail_when_the_compiled_skill_is_absent(script, tmp_path):
    """A missing artifact must fail loudly rather than report a successful no-op.

    Each script derives its root from its own location, so copying scripts/ alone
    into an empty tree is what makes the compiled skill genuinely absent.
    """
    shutil.copytree(REPO_ROOT / "scripts", tmp_path / "scripts")

    result = subprocess.run(
        [str(tmp_path / "scripts" / script), "--repo-url", REPO_URL, "--dry-run"],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "compile-agents.py --write" in result.stderr
```

- [ ] **Step 2: Run the tests and verify they fail**

Run: `python3 -m pytest tests/unit/test_publish_scripts.py -v`

Expected: FAIL. `test_openagentskill_submits_only_the_compiled_skill` fails on
`assert out.count("DRY RUN") == 1` because three payloads are rendered.

- [ ] **Step 3: Point openagentskill at the compiled skill**

In `scripts/publish-openagentskill.sh`, change the header comment on line 2 from
`# Submit every skill under skills/ to openagentskill.com.` to
`# Submit the compiled skill (compiled-skills/aerospike) to openagentskill.com.`

Replace lines 46-47:

```bash
mapfile -t skill_dirs < <(find "${ROOT}/skills" -mindepth 1 -maxdepth 1 -type d | sort)
[[ "${#skill_dirs[@]}" -gt 0 ]] || { echo "No skills found under skills/." >&2; exit 1; }
```

with:

```bash
# One published artifact, compiled from the three skills under skills/. The
# authoring folders are the source of truth, not what registries list.
SKILL_NAME="aerospike"
SKILL_PATH="compiled-skills/${SKILL_NAME}/SKILL.md"
[[ -f "${ROOT}/${SKILL_PATH}" ]] || {
  echo "${SKILL_PATH} not found. Run: python3 scripts/compile-agents.py --write" >&2
  exit 1
}
```

Replace the loop opening at lines 69-73:

```bash
for skill_dir in "${skill_dirs[@]}"; do
  skill_md="${skill_dir}/SKILL.md"
  [[ -f "${skill_md}" ]] || continue
  name="$(basename "${skill_dir}")"
  skill_path="skills/${name}/SKILL.md"
```

with:

```bash
for name in "${SKILL_NAME}"; do
  skill_path="${SKILL_PATH}"
```

Keep the loop even though it runs once. The body's receipt writing, duplicate handling, and
`failures` accounting all depend on it, and a second published skill would slot straight in.
Do not flatten it.

- [ ] **Step 4: Point upskill at the compiled skill**

In `scripts/publish-upskill.sh`, change line 2 from
`# Submit every skill under skills/ to upskill (Autoloops).` to
`# Submit the compiled skill (compiled-skills/aerospike) to upskill (Autoloops).`

Replace lines 43-44:

```bash
mapfile -t skill_dirs < <(find "${ROOT}/skills" -mindepth 1 -maxdepth 1 -type d | sort)
[[ "${#skill_dirs[@]}" -gt 0 ]] || { echo "No skills found under skills/." >&2; exit 1; }
```

with:

```bash
# One published artifact, compiled from the three skills under skills/.
SKILL_NAME="aerospike"
SKILL_DIR_REL="compiled-skills/${SKILL_NAME}"
[[ -f "${ROOT}/${SKILL_DIR_REL}/SKILL.md" ]] || {
  echo "${SKILL_DIR_REL}/SKILL.md not found. Run: python3 scripts/compile-agents.py --write" >&2
  exit 1
}
```

Replace the loop opening at lines 72-77:

```bash
for skill_dir in "${skill_dirs[@]}"; do
  [[ -f "${skill_dir}/SKILL.md" ]] || continue
  name="$(basename "${skill_dir}")"
  # Submit a branch URL rather than the release tag so the listing tracks later
  # updates instead of pinning to one release.
  target="${REPO_URL}/tree/${REF}/skills/${name}"
```

with:

```bash
for name in "${SKILL_NAME}"; do
  # Submit a branch URL rather than the release tag so the listing tracks later
  # updates instead of pinning to one release.
  target="${REPO_URL}/tree/${REF}/${SKILL_DIR_REL}"
```

- [ ] **Step 5: Run the tests and verify they pass**

Run: `python3 -m pytest tests/unit/test_publish_scripts.py -v`

Expected: 5 passed.

- [ ] **Step 6: Verify both dry runs by hand**

Run:

```bash
./scripts/publish-openagentskill.sh --repo-url https://github.com/aerospike/agent-skills --dry-run
./scripts/publish-upskill.sh --repo-url https://github.com/aerospike/agent-skills --ref main --dry-run
```

Expected: one `DRY RUN aerospike:` block each. The openagentskill payload shows
`"skillPath": "compiled-skills/aerospike/SKILL.md"`; the upskill line ends
`/tree/main/compiled-skills/aerospike`.

- [ ] **Step 7: Update the workflow's description**

In `.github/workflows/publish-registries.yml`, change line 1 from
`# Publish skills/ to agent-skill registries on release.` to
`# Publish the compiled skill (compiled-skills/aerospike) to agent-skill registries on release.`

On line 3, change `This is the only path that contacts a registry` to
`This is the only path that contacts a registry. One skill is submitted: the artifact
compiled from the three authoring folders under skills/.`

- [ ] **Step 8: Commit**

```bash
git add scripts/publish-openagentskill.sh scripts/publish-upskill.sh \
        .github/workflows/publish-registries.yml tests/unit/test_publish_scripts.py
git commit -m "feat: submit the single compiled skill to registries"
```

---

### Task 5: Update the registry manifest and all documentation

Nineteen references across seven files still describe `SKILLS.md` and three published skills. The README install table is also missing Gemini, which AIE-16 requires.

**Files:**
- Modify: `skills.sh.json`
- Modify: `README.md:43,56,58,60,61`
- Modify: `compiled-skills/README.md:3,7,14,17,31-34`
- Modify: `AGENTS.md:21,30`
- Modify: `CLAUDE.md:5`
- Modify: `CONTRIBUTING.md:38`
- Modify: `.github/copilot-instructions.md:5`
- Modify: `docs/PUBLISHING.md:57-66,85,97`
- Create: `tests/unit/test_docs_references.py`

**Interfaces:**
- Consumes: `compile_agents.SINGLE_OUT` and `LEGACY_SINGLE_OUT` from Task 2.
- Produces: no code interface.

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_docs_references.py`:

```python
"""No document may point at the retired SKILLS.md, and the install table must
cover every platform we claim to support."""

import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
TRACKED_SUFFIXES = {".md", ".json", ".yml", ".sh", ".py"}
SKIP_DIRS = {".git", "eval", "results", "docs/superpowers", ".venv"}


def _tracked_files():
    for path in REPO_ROOT.rglob("*"):
        rel = path.relative_to(REPO_ROOT).as_posix()
        if any(rel == d or rel.startswith(f"{d}/") for d in SKIP_DIRS):
            continue
        if path.is_file() and path.suffix in TRACKED_SUFFIXES:
            yield rel, path


def test_nothing_references_the_retired_compiled_file():
    offenders = [
        rel
        for rel, path in _tracked_files()
        if "compiled-skills/SKILLS.md" in path.read_text(encoding="utf-8")
        or "](SKILLS.md)" in path.read_text(encoding="utf-8")
    ]
    assert offenders == []


def test_readme_install_table_covers_all_three_platforms():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    for platform in ("Claude", "Cursor", "Gemini"):
        assert platform in readme, f"README must document installing for {platform}"


def test_registry_manifest_lists_the_single_published_skill():
    manifest = json.loads((REPO_ROOT / "skills.sh.json").read_text(encoding="utf-8"))
    skills = [s for g in manifest["groupings"] for s in g["skills"]]
    assert skills == ["aerospike"]
```

- [ ] **Step 2: Run the test and verify it fails**

Run: `python3 -m pytest tests/unit/test_docs_references.py -v`

Expected: all three FAIL — `offenders` lists seven files, `Gemini` is absent from the README,
and `skills.sh.json` still lists three names.

- [ ] **Step 3: Collapse the registry manifest**

Replace `skills.sh.json` with:

```json
{
  "$schema": "https://skills.sh/schemas/skills.sh.schema.json",
  "notGrouped": "bottom",
  "groupings": [
    {
      "title": "Aerospike",
      "description": "Agent skill for the Aerospike core database: local setup, application development, and design-time data modeling. Core database only, not Aerospike Graph.",
      "skills": [
        "aerospike"
      ]
    }
  ]
}
```

- [ ] **Step 4: Update compiled-skills/README.md**

Replace the file body with:

```markdown
# Published Aerospike skill

This directory holds the **published** Aerospike agent skill — one file compiled from the three authoring folders under [`skills/`](../skills/). CI fails any pull request whose compiled output is stale, so this always matches the source skills on `main`.

| File | Purpose |
|------|---------|
| [`aerospike/SKILL.md`](aerospike/SKILL.md) | **Download this** — getting-started, application development, and data-modeling rules in one file, with frontmatter registries can validate |

## Quick install

**With the [`skills` CLI](https://skills.sh):**

```bash
npx skills add aerospike/agent-skills
```

**Raw file URL (use `main` or a release tag):**

```
https://raw.githubusercontent.com/aerospike/agent-skills/main/compiled-skills/aerospike/SKILL.md
```

1. Download [`aerospike/SKILL.md`](aerospike/SKILL.md) (or use the raw URL above).
2. Add it to your agent's **always-on context** (project rules, system prompt, knowledge base, or repo instructions), or drop the `aerospike/` folder into your agent's skills directory.
3. See [`AGENTS.md`](../AGENTS.md) for a short overview.

## By tool

| Tool | What to do |
|------|------------|
| **Claude Code** | `npx skills add aerospike/agent-skills -a claude-code`, which installs to `.claude/skills/aerospike/`. Or add the file to project instructions. |
| **Cursor** | `npx skills add aerospike/agent-skills -a cursor`, which installs to `.agents/skills/aerospike/` (globally, `~/.cursor/skills/`). Or copy the file into a project rule such as `.cursor/rules/aerospike.mdc`. |
| **Gemini CLI** | `npx skills add aerospike/agent-skills -a gemini-cli`, which installs to `.agents/skills/aerospike/` (globally, `~/.gemini/skills/`). |
| **GitHub Copilot** | This repo's [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) already points at the compiled skill. |
| **ChatGPT / other chats** | Upload `aerospike/SKILL.md` to a project knowledge set, or paste the raw URL when working on Aerospike. |

**Prefer the modular sources?** The three authoring folders under [`skills/`](../skills/) stay maintained and installable by copying a folder; the compiled skill is what registries list.

For more install options, see the [repository README](../README.md#using-with-ai-assistants).
```

- [ ] **Step 5: Update the remaining documents**

In `README.md`:
- Line 43: change the table row to `| [compiled-skills/aerospike/SKILL.md](compiled-skills/aerospike/SKILL.md) | Published agent skill, compiled from `skills/` into one file |`
- Line 56: change to `| **Any agent (recommended)** | Add [`compiled-skills/aerospike/SKILL.md`](compiled-skills/aerospike/SKILL.md) to always-on context. [Install guide](compiled-skills/README.md). Raw URL: `https://raw.githubusercontent.com/aerospike/agent-skills/main/compiled-skills/aerospike/SKILL.md` |`
- Line 57: change to `| **`skills` CLI (any supported agent)** | `npx skills add aerospike/agent-skills` installs the published skill for you. |`
- After line 58 (the Cursor row), insert a Gemini row:
  `| **Gemini CLI** | `npx skills add aerospike/agent-skills -a gemini-cli` installs to `.agents/skills/aerospike/` (globally `~/.gemini/skills/`). |`
- Lines 60-61: replace both `compiled-skills/SKILLS.md` references with `compiled-skills/aerospike/SKILL.md`.
- Line 103: change to ``- **Compiled skill:** `compiled-skills/` is generated from `skills/`. After editing any skill, run `python3 scripts/compile-agents.py --write`; CI fails the PR if the compiled output is stale. Frontmatter for the published skill lives in `scripts/skills_compile/published_skill.yaml`.``

In `AGENTS.md` lines 21 and 30, and `CLAUDE.md` line 5, and
`.github/copilot-instructions.md` line 5: replace every
`compiled-skills/SKILLS.md` path and link target with `compiled-skills/aerospike/SKILL.md`.

In `CONTRIBUTING.md` line 38: change to
`| Compiled published skill (auto-generated from skills) | [compiled-skills/aerospike/SKILL.md](compiled-skills/aerospike/SKILL.md) |`

In `docs/PUBLISHING.md`:
- Line 57: change `then submits one payload per skill:` to `then submits one payload for the compiled skill:`
- Lines 60-66: change the JSON `skillPath` value to `"compiled-skills/aerospike/SKILL.md"`.
- Line 85: change to `Submitted URLs point at the **default branch**, not the release tag, so a listing keeps tracking updates rather than freezing at one release.` (unchanged text; verify the surrounding paragraph no longer implies three submissions).
- Line 97: change to ``Ship [`skills.sh.json`](../skills.sh.json) so the repository page presents our published skill sensibly once it appears. This is display-only and does not affect whether we are listed.``
- Line 122: after the existing sentence, add: `Both also cover `compiled-skills/aerospike/`, the artifact registries actually fetch.`

- [ ] **Step 6: Run the test and verify it passes**

Run: `python3 -m pytest tests/unit/ -v`

Expected: 18 passed.

- [ ] **Step 7: Verify no stale links remain**

Run: `grep -rn "SKILLS\.md" --include="*.md" --include="*.yml" --include="*.json" --include="*.sh" --include="*.py" . | grep -v docs/superpowers`

Expected: no output.

- [ ] **Step 8: Commit**

```bash
git add skills.sh.json README.md compiled-skills/README.md AGENTS.md CLAUDE.md \
        CONTRIBUTING.md .github/copilot-instructions.md docs/PUBLISHING.md \
        tests/unit/test_docs_references.py
git commit -m "docs: point every install path at the single published skill"
```

---

### Task 6: Open the findings ledger

AIE-16's final acceptance criterion requires every finding to be fixed or triaged with a decision recorded. Five of the eight findings from the design close in this plan; the ledger records all of them and carries the rest into the testing plan.

**Files:**
- Create: `tests/FINDINGS.md`
- Create: `tests/README.md`

**Interfaces:**
- Consumes: outcomes of Tasks 1-5.
- Produces: no code interface.

- [ ] **Step 1: Write the ledger**

Create `tests/FINDINGS.md`:

```markdown
# Findings ledger

Every finding from testing the skills before publication, with the decision taken.
Opened for [AIE-16](https://aerospike.atlassian.net/browse/AIE-16). Design:
[`docs/superpowers/specs/2026-08-19-skill-testing-and-publish-shape-design.md`](../docs/superpowers/specs/2026-08-19-skill-testing-and-publish-shape-design.md).

| # | Finding | Decision | Status |
|---|---------|----------|--------|
| F1 | The compiled artifact cites 19 reference files by bare filename (33 mentions) and carries no URLs, against 246 in the source. | **Accepted.** The stripped digest is the measured, intended shape — 95% accuracy at ~8.5k tokens, tying the full monolith within its confidence interval. Mitigated by naming the repository in the generated header so a cited filename resolves once the repo is public. | Closed |
| F2 | `labeled_sections` split reference files on any standalone bold line, so a bolded URL, seven enumerated headings, and a "Gotcha" heading were read as section boundaries. 4,880 characters of rule content were misfiled across three files; the shipped artifact carried a rule truncated mid-sentence, losing the data-modeling guide URL. | **Fixed.** Only the five labels in `references/_template.md` split a file. | Closed |
| F3 | Publishing submitted three skill folders rather than the one compiled artifact the evaluation validated. | **Fixed.** Registries receive `compiled-skills/aerospike/SKILL.md`. The three folders remain the authoring source. | Closed |
| F4 | Both validators were hardcoded to `skills/`, so the artifact registries fetch was never checked. | **Fixed.** Both now cover `compiled-skills/aerospike/`. | Closed |
| F5 | The README install table omitted Gemini, though AIE-16 requires a verified Gemini install. | **Fixed.** Gemini CLI documented alongside Claude Code and Cursor. | Closed |
| F6 | No skill declares a supported server version range, leaving "current server behavior" without a target. | **Fix planned.** Declare `metadata.server_versions: "7.0+"`; the canonical local config sets `cluster-name`, mandatory since 7.0.0. | Open — testing plan |
| F7 | `aerospike-data-modeling` has never been measured: absent from the evaluation harness `source_skills` and from all 61 tasks. | **Fix planned.** Add it to the harness with its own task file. | Open — testing plan |
| F8 | Skill folders are self-contained; no relative link escapes its own folder. | **No action.** Verified across `skills/`. A check will lock it in. | Open — testing plan |
| F9 | `dev-ttl-void-time` failed on every variant including the baseline in evaluation run `20260623-101343`, attributed to the task rubric rather than a skill defect. | **Carried forward.** Re-examine when the harness is next run. | Open — testing plan |
```

- [ ] **Step 2: Write the tests directory guide**

Create `tests/README.md`:

```markdown
# Tests

| Path | What it covers | How to run |
|------|----------------|------------|
| `unit/` | The compiler, the publish scripts, and documentation references | `python3 -m pytest tests/unit -v` |
| `FINDINGS.md` | Ledger of findings from pre-publication testing, with decisions | — |

Trigger-accuracy prompts, end-to-end task files, and the server-claim verification
script arrive with the testing plan; see
[`docs/superpowers/specs/2026-08-19-skill-testing-and-publish-shape-design.md`](../docs/superpowers/specs/2026-08-19-skill-testing-and-publish-shape-design.md).

## Before publishing

```bash
python3 -m pytest tests/unit -v                        # compiler, publishing, docs
python3 scripts/compile-agents.py --shape stripped --check
./scripts/validate-spec.sh                             # needs skills-ref
./scripts/validate-skill.sh                            # needs skill-validator
```
```

- [ ] **Step 3: Run the whole suite**

Run:

```bash
python3 -m pytest tests/unit -v
python3 scripts/compile-agents.py --shape stripped --check
```

Expected: 18 passed, and `compiled-skills/ is up to date (single, stripped).`

- [ ] **Step 4: Commit**

```bash
git add tests/FINDINGS.md tests/README.md
git commit -m "docs: record pre-publication findings and their decisions"
```

---

## Verification after all tasks

```bash
python3 -m pytest tests/unit -v
python3 scripts/compile-agents.py --shape stripped --check
./scripts/validate-spec.sh
./scripts/validate-skill.sh --ci; echo "exit=$?"
./scripts/publish-openagentskill.sh --repo-url https://github.com/aerospike/agent-skills --dry-run
./scripts/publish-upskill.sh --repo-url https://github.com/aerospike/agent-skills --ref main --dry-run
git status --short
```

Expected: 18 tests pass; compiled output current; 4 skills conform; linter exits 0 or 2; each
publish script renders exactly one `aerospike` payload; working tree clean.

## What this plan does not do

Workstreams B through F of the design — trigger accuracy, data-modeling end-to-end coverage,
the server-claim verification script, the version-range declaration, and the CI gates for
trigger and payload checks — belong to a second plan that builds on this one. Findings F6
through F9 stay open until then.
