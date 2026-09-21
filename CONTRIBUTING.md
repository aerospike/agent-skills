# Contributing

Thanks for helping improve this repository. It holds **Agent Skills** under [`skills/`](skills/); more packages will be added over time. Keep content **accurate**, **easy for newcomers**, and **small enough** for AI context—prefer links to official documentation over pasting long reference material.

## What belongs here

- **Repository:** Skill trees under `skills/<skill-name>/`, curated entrypoints ([`AGENTS.md`](AGENTS.md), [`README.md`](README.md)), compiled artifacts ([`compiled-skills/`](compiled-skills/)), Copilot instructions, CI validation, and helper scripts.
- **Each skill:** One folder per skill, with `SKILL.md` (required) and optional companion files per the [Agent Skills](https://agentskills.io/) conventions your target platforms expect. Scope and focus are **per skill**—see the skill’s own `SKILL.md` and any `references/` / flat companion files.

### Current skills (examples)

- **[`skills/aerospike-getting-started/`](skills/aerospike-getting-started/)** — Aerospike Database getting started: single-node local setup (Docker), ports/namespaces/TTL, official client snippets, Community vs Enterprise pointers, troubleshooting for new users, anti-hallucination rules. Not a substitute for full production or multi-region guides—link to [Aerospike documentation](https://aerospike.com/docs/) for that.
- **[`skills/aerospike-development/`](skills/aerospike-development/)** — Application-level client guidance: modular rules and `ex-*` examples under [`references/`](skills/aerospike-development/references/README.md), doc map in [`reference.md`](skills/aerospike-development/reference.md). Not cluster operations.

## Adding a new skill (especially Aerospike)

1. Create `skills/<skill-name>/` with a required `SKILL.md` at the skill root. YAML **`name`** must match the parent folder name; **`description`** explains what and when; optional **`metadata.last_verified`** after you validate facts. For frontmatter shape, see an existing skill such as [`skills/aerospike-getting-started/SKILL.md`](skills/aerospike-getting-started/SKILL.md).
2. Add any companion files inside that folder only (skill markdown must not link outside the skill directory—see validator note below).
3. Run [`./scripts/validate-skill.sh`](scripts/validate-skill.sh) from the repo root and fix reported issues.
4. Update [`skills/README.md`](skills/README.md) with a table row linking to the new `SKILL.md`.
5. Keep human and assistant entrypoints in sync so the skill is discoverable:
   - [`README.md`](README.md) — skill catalog and “what’s in the repo” as appropriate.
   - [`AGENTS.md`](AGENTS.md) — routing or read order when the new skill has a distinct trigger.
   - [`.github/copilot-instructions.md`](.github/copilot-instructions.md) — when GitHub Copilot should follow the new skill, add a routing bullet (same relative-link rules as today).
6. Add a bullet under **Current skills** in this file (above) summarizing scope and out-of-scope in one line each.
7. Open a PR with a focused diff; re-run the validator after edits.

## Where to edit

| Change | Prefer |
|--------|--------|
| New or existing skill content | [`skills/<skill-name>/`](skills/) (see [`skills/README.md`](skills/README.md); new skills: checklist **Adding a new skill** above) |
| Aerospike workflow, critical rules, Docker happy path | [skills/aerospike-getting-started/SKILL.md](skills/aerospike-getting-started/SKILL.md) |
| Aerospike language examples, batching patterns | [skills/aerospike-getting-started/examples.md](skills/aerospike-getting-started/examples.md) |
| Aerospike Compose, custom config, editions, platform notes | [skills/aerospike-getting-started/reference.md](skills/aerospike-getting-started/reference.md) |
| Aerospike app development rules, examples TOC | [skills/aerospike-development/references/README.md](skills/aerospike-development/references/README.md), [skills/aerospike-development/examples.md](skills/aerospike-development/examples.md) |
| Tool-agnostic AI entry (read order, scope) | [AGENTS.md](AGENTS.md) |
| Compiled published skill (auto-generated body; do not hand-edit) | [compiled-skills/aerospike/SKILL.md](compiled-skills/aerospike/SKILL.md) |
| Published skill frontmatter (hand-written) | [scripts/skills_compile/published_skill.yaml](scripts/skills_compile/published_skill.yaml) |
| GitHub Copilot repo instructions | [.github/copilot-instructions.md](.github/copilot-instructions.md) |
| Human install path, checklist | [README.md](README.md) |

**Layout:** Each skill lives in its own directory under [`skills/`](skills/). The directory name must match the YAML `name` in that skill’s `SKILL.md`. Do not duplicate large config or command blocks across files unless you have a strong reason—keep **one canonical** source (often `SKILL.md`) and link or reference it.

**Cursor users** copy `skills/<skill-name>/` to `.cursor/skills/<skill-name>/` so discovery matches the frontmatter `name`. For Aerospike, if you still use the old top-level folder name `aerospike-database-setup`, rename it to `aerospike-getting-started`.

## Skill frontmatter (`SKILL.md`)

The [Agent Skills specification](https://agentskills.io/specification) defines a **closed** set of six frontmatter keys. Only these are allowed in a `SKILL.md`, and the official validator rejects anything else:

`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`

- **`name`:** Lowercase letters, numbers, hyphens; 1–64 characters; no leading, trailing, or consecutive hyphens; must match the parent folder name.
- **`description`:** Third person; include **what** the skill does and **when** to use it (trigger phrases). 1–1024 characters.
- **`license` (optional):** `Apache-2.0` for skills in this repository, matching [LICENSE](LICENSE). Registries factor license clarity into trust scoring.
- **`metadata` (optional):** The spec's extension point—a map of string keys to **string** values. Anything not in the six keys above belongs here.
- **`metadata.last_verified`:** Bump this **ISO date** when you change commands, images, or product facts for **that skill**—after you have manually re-checked the documented flow. **Quote it** (`"2026-04-21"`), because an unquoted YAML date parses to a date object and `metadata` values must be strings.

```yaml
---
name: aerospike-getting-started
description: >-
  What the skill does, and when an agent should reach for it.
license: Apache-2.0
metadata:
  last_verified: "2026-04-21"
---
```

This closed key set applies to `SKILL.md` only. Companion files under `references/` are not skill manifests, so their frontmatter is free-form.

## Writing rule files (`references/`)

A rule file is compiled into [`compiled-skills/aerospike/SKILL.md`](compiled-skills/aerospike/SKILL.md) by [`scripts/compile-agents.py`](scripts/compile-agents.py), and **the compiler keeps far less of it than the file contains**. Where you put a sentence decides whether it ships.

### What the published package looks like

`SKILL.md` is a **router**, not a manual. Per the [Agent Skills spec's progressive disclosure](https://agentskills.io/specification), it loads whenever the skill activates and should stay under 5,000 tokens; the rule files ship beside it in `references/` and are read only when a rule applies. So:

1. **Tier 1 — `SKILL.md`.** Each rule contributes a heading and **the first sentence of its `Rule`**. That is the instruction, and nothing else.
2. **Tier 2 — `references/<skill>-<rule>.md`.** The whole rule file, verbatim, including everything tier 1 omits.
3. **Tier 3 — aerospike.com/docs**, reached from tier 2.

A rule's file is named by its skill and its own filename, and the artifact's header states that derivation. Rules cite each other by bare filename and resolve the same way.

### Section markers

Five labels, each **bold and alone on its line**. The set is closed—[`skillsrc.py`](scripts/skills_compile/skillsrc.py) matches these and nothing else, so **a bold line that is not one of them is not a section**: it is absorbed into whichever section precedes it, and its content ships or vanishes accordingly.

| Marker | Ships to `SKILL.md` | Notes |
|---|---|---|
| `**Rule**` | **First sentence only** | Must stand alone as the instruction. |
| `**Prefer**` | Bullets only | Joined with `;`. Prose here ships nothing. |
| `**Avoid**` | Bullets only | Same. |
| `**Why**` | No | Rationale. Ships in `references/`. |
| `**See also**` | No | Bibliography. Ships in `references/`. |

A file with **no `**Rule**`** gets a stub heading pointing at it and contributes no instruction—correct for the `ex-*` worked examples, a mistake for anything else.

### Transforms that silently change what ships

- **The first sentence of `Rule` must stand alone.** It is all of `Rule` that reaches tier 1. A sentence ending in a colon announces content that will not be there; [`coverage.py`](scripts/skills_compile/coverage.py) fails the build on it.
- **A bullet must be one physical line**, or a `**bold**` run spanning the wrap leaves a stray `**`. (Continuations are folded, but do not rely on it for readability.)
- **Prose in `Prefer`/`Avoid` ships nothing.** Only bullets are extracted. This is a hard failure in the coverage check.
- **Tables never survive a rule file's `Rule`, `Prefer` or `Avoid`.** Put them under a `##` heading in `SKILL.md`, or under `**Why**`.
- **Links lose their URL** and **backticks and bold are stripped**—identifiers survive as bare words, so write `ListExp.append`, not "the append expression".
- **Prose in `SKILL.md` does not ship at all.** Only bullets and table rows, and only from headings containing `rule`, `blacklist`, `pitfall`, `practice`, `critical`, or `mapping`. Prose is how you keep something useful to a reader of the source without paying for it on every invocation.

### Deciding where a sentence goes

> If this sentence were deleted, would a competent agent produce **different or wrong** code?

**Yes** → `Rule`, `Prefer`, or `Avoid`: constraints, identifiers, version floors, sizing arithmetic, failure conditions. **No, it only makes the reader more confident** → `**Why**`.

One corollary, because a third of this corpus once failed it: **content already carried by a `Prefer` or `Avoid` bullet does not belong in `Rule` as well.** State a constraint once.

Worked examples, all real:

- "Strong-consistency namespaces require `COMMIT_ALL`; otherwise writes fail" — changes the output. **Essential.**
- "(concurrent client processes × maxConnsPerNode) counts against each node's `proto-fd-max`" — changes the sizing decision. **Essential.**
- "Typical knobs (names vary by SDK): a maximum error count and a window length" — nothing typeable. **`Why`.**
- `post-write-cache` defaults and cgroup interactions — operations tuning, not schema or client work. **`Why`.**

### Before you open the PR

- [ ] `Rule` opens with a standalone imperative—no colon introducing content that lives elsewhere
- [ ] Every claim an agent would act on is in `Rule`, `Prefer`, or `Avoid`
- [ ] No tables and no prose paragraphs in `Prefer` / `Avoid`
- [ ] `impact:` is set, and `doc:` points at the canonical Aerospike page
- [ ] Any sibling rule needed *to act* is named inline in `Prefer` / `Avoid`, not left to `See also`
- [ ] New file added to [`references/README.md`](skills/aerospike-development/references/README.md)
- [ ] `python scripts/compile-agents.py --coverage` reports **0 defects**
- [ ] Do **not** bump `last_verified` for a pure reformat—moving a sentence re-verifies nothing

## Validate the skill package (skill-validator)

CI runs [agent-ecosystem/skill-validator](https://github.com/agent-ecosystem/skill-validator) on [`skills/`](skills/) (all skill subdirectories)—see [`.github/workflows/skill-validator.yml`](.github/workflows/skill-validator.yml). Run the same check locally before you push:

1. Install [Go](https://go.dev/dl/) (toolchain **1.25+** matches CI; `go install` may download a newer toolchain automatically).
2. Install the pinned CLI (keep the version in sync with the workflow env `SKILL_VALIDATOR_VERSION`):

   ```bash
   go install github.com/agent-ecosystem/skill-validator/cmd/skill-validator@v1.5.5
   ```

   Ensure `$(go env GOPATH)/bin` is on your `PATH`.

3. From the repository root:

   ```bash
   ./scripts/validate-skill.sh
   ```

   - Use `./scripts/validate-skill.sh --ci` to match **CI** (annotations, **no** `--strict`; the workflow treats validator exit `2` warnings-only as success).
   - **Local default** uses **`--strict`**, so warnings are reported as exit `1` like errors.
   - **Raw one-liner** (strict, same as local script default):

     ```bash
     skill-validator check --strict --allow-flat-layouts skills/
     ```

   `--allow-flat-layouts` is intentional: `examples.md` and `reference.md` beside `SKILL.md` are spec-legal, and only this third-party tool objects to them. There is deliberately **no** `--allow-extra-frontmatter`, so an unexpected frontmatter key fails here instead of being waived.

   Optional: [Homebrew install](https://github.com/agent-ecosystem/skill-validator#install-cli) (`brew tap agent-ecosystem/tap && brew install skill-validator`) if you prefer not to use `go install`.

**Note:** Skill markdown must not link **outside** the skill directory (e.g. no `../README.md`); describe repo-level files in prose instead.

## Check spec conformance (skills-ref)

Registries validate against the [Agent Skills specification](https://agentskills.io/specification), so this check is separate from the linter above: it answers only "does this frontmatter conform to the standard." CI runs it via [`.github/workflows/spec-conformance.yml`](.github/workflows/spec-conformance.yml).

```bash
python3 -m venv .venv && . .venv/bin/activate   # requires Python 3.11+
pip install "git+https://github.com/agentskills/agentskills.git@69ef37e9424c0a7ea9dd2293b559e43ec8176379#subdirectory=skills-ref"
./scripts/validate-spec.sh
```

The commit is pinned because `skills-ref` has no PyPI release. Keep the pin in [`scripts/validate-spec.sh`](scripts/validate-spec.sh) and the workflow in sync.

## Publishing to registries

Submission is automated on release and gated behind a stable semantic version tag, conformance, public visibility, and a kill-switch variable. Do not submit by hand—see [`docs/PUBLISHING.md`](docs/PUBLISHING.md).

Release tags are `vMAJOR.MINOR.PATCH` with no prerelease suffix, and must exceed the previous tag. Check one before cutting a release:

```bash
./scripts/check-release-version.sh --tag v1.4.0
```

## Before you open a pull request

1. **Fact-check** any product behavior you document against current **official** docs or release notes for that product—not only blog posts or old threads.
2. **Run** `python3 -m pytest tests/unit -v` (see [tests/README.md](tests/README.md)).
3. **Run** `./scripts/validate-skill.sh` (see above).
4. **Exercise the skill** you changed: follow the happy path in `SKILL.md` (e.g. commands, containers, client smoke test) when the skill includes procedural steps.
5. **If you changed `skills/` or [`scripts/skills_compile/published_skill.yaml`](scripts/skills_compile/published_skill.yaml)**, regenerate compiled output: `python scripts/compile-agents.py --write` (or let CI on `main` do it). PRs run a drift check — stale `compiled-skills/` fails CI.
6. **Keep diffs focused**—one logical change per PR when possible (e.g. “fix port wording in Aerospike skill” vs mixing unrelated skills or refactors).

For **Aerospike** changes specifically: verify ports, namespaces, TTL/NSUP, and image names against [Aerospike documentation](https://aerospike.com/docs/); run the Docker flow and at least **one** client example from [`examples.md`](skills/aerospike-getting-started/examples.md) for a stack you have installed. Avoid duplicating the full `aerospike.conf` in multiple files—keep one canonical copy in [`SKILL.md`](skills/aerospike-getting-started/SKILL.md) unless you have a strong reason.

### Commit messages

Commits follow [Conventional Commits](https://www.conventionalcommits.org/):

```text
type(scope): description
```

Common types here are `docs` (skill content), `feat` (a new skill or capability), `fix`, and `chore` (tooling and repo plumbing). The rules come from `@commitlint/config-conventional` via [`commitlint.config.mjs`](commitlint.config.mjs), matching [aerospike/data-modeling-guide](https://github.com/aerospike/data-modeling-guide).

### Pull request titles

The PR title follows the same convention and is checked in CI by
[`pr-hygiene.yml`](.github/workflows/pr-hygiene.yml), which must pass before
merge. Dependabot, StepSecurity, and revert titles are allowlisted.

**No JIRA reference is required, on any PR type.** Outside contributors cannot
see or open Aerospike tickets. Aerospike engineers may include one for their own
tracking, but no check enforces it.

### Local hooks

Hooks live in [`.pre-commit-config.yaml`](.pre-commit-config.yaml): secret scanning (gitleaks), shellcheck, whitespace fixes, and commitlint. They are **not** active until you install them:

```bash
pip install pre-commit          # or: brew install pre-commit
pre-commit install --hook-type pre-commit --hook-type commit-msg
```

The `--hook-type commit-msg` part is required for commitlint — without it, the message check never runs.

### Reviews

The default branch requires a pull request with one approving review from a [code owner](.github/CODEOWNERS). Any one owner satisfies it, and GitHub does not let a pull request author approve their own.

## Style

- **Concise:** The agent already knows generic programming; add only **Aerospike-oriented** or failure-prone detail when editing the Aerospike skill, and the same idea—product-oriented, non-generic detail—for other skills.
- **Consistent terminology** within a skill: follow the vocabulary the skill defines (for Aerospike: namespace, set, record, bin—not mixed SQL metaphors).
- **Links:** Prefer stable vendor doc URLs; if a URL might move, note the section name so maintainers can find a replacement.

### Token footprint (`ex-*` files)

This governs **weight**; [Writing rule files](#writing-rule-files-references) governs **shape**—what compiles and where it lands. The concern here is skill-validator's per-file warning, not the compiled artifact: `ex-*` files carry no `**Rule**`, so they contribute no instruction to `SKILL.md` and their size is felt only when an agent opens one.

Skills under [`skills/`](skills/) are checked with [skill-validator](https://github.com/agent-ecosystem/skill-validator); large pasted content triggers **high token-count** warnings. For **`references/ex-*`** files: use **link-first** tables pointing at official Aerospike **Code block** sections; add **at most one or two** short minimal snippets (e.g. Python and Java) when copy-paste anchors help—**not** a full mirror of every language. **Do not** paste the same multi-language tutorial in full here—that duplicates [Aerospike documentation](https://aerospike.com/docs/) and inflates agent context.

## Suggesting changes without a PR

Open an issue (if your host supports it) with: what you tried, what you expected, relevant product or client versions, and OS—so others can reproduce.
