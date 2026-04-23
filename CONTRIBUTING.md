# Contributing

Thanks for helping improve this repository. It holds **Agent Skills** under [`skills/`](skills/); more packages will be added over time. Keep content **accurate**, **easy for newcomers**, and **small enough** for AI context—prefer links to official documentation over pasting long reference material.

## What belongs here

- **Repository:** Skill trees under `skills/<skill-name>/`, shared entrypoints ([`AGENTS.md`](AGENTS.md), [`README.md`](README.md)), Copilot instructions, CI validation, and helper scripts.
- **Each skill:** One folder per skill, with `SKILL.md` (required) and optional companion files per the [Agent Skills](https://agentskills.io/) conventions your target platforms expect. Scope and focus are **per skill**—see the skill’s own `SKILL.md` and any `references/` / flat companion files.

### Current skills (examples)

- **[`skills/aerospike-getting-started/`](skills/aerospike-getting-started/)** — Aerospike Database getting started: single-node local setup (Docker), ports/namespaces/TTL, official client snippets, Community vs Enterprise pointers, troubleshooting for new users, anti-hallucination rules. Not a substitute for full production or multi-region guides—link to [Aerospike documentation](https://aerospike.com/docs/) for that.
- **[`skills/aerospike-development/`](skills/aerospike-development/)** — Application-level client guidance: modular rules and `ex-*` examples under [`references/`](skills/aerospike-development/references/README.md), doc map in [`reference.md`](skills/aerospike-development/reference.md). Not cluster operations.

## Adding a new skill (especially Aerospike)

1. Create `skills/<skill-name>/` with a required `SKILL.md` at the skill root. YAML **`name`** must match the parent folder name; **`description`** explains what and when; optional **`last_verified`** after you validate facts. For frontmatter shape, see an existing skill such as [`skills/aerospike-getting-started/SKILL.md`](skills/aerospike-getting-started/SKILL.md).
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
| GitHub Copilot repo instructions | [.github/copilot-instructions.md](.github/copilot-instructions.md) |
| Human install path, checklist | [README.md](README.md) |

**Layout:** Each skill lives in its own directory under [`skills/`](skills/). The directory name must match the YAML `name` in that skill’s `SKILL.md`. Do not duplicate large config or command blocks across files unless you have a strong reason—keep **one canonical** source (often `SKILL.md`) and link or reference it.

**Cursor users** copy `skills/<skill-name>/` to `.cursor/skills/<skill-name>/` so discovery matches the frontmatter `name`. For Aerospike, if you still use the old top-level folder name `aerospike-database-setup`, rename it to `aerospike-getting-started`.

## Skill frontmatter (`SKILL.md`)

- **`name`:** Lowercase letters, numbers, hyphens; max 64 characters; must match the parent folder name.
- **`description`:** Third person; include **what** the skill does and **when** to use it (trigger phrases). Stay under **1024** characters.
- **`last_verified` (optional):** Bump this **ISO date** when you change commands, images, or product facts for **that skill**—after you have manually re-checked the documented flow.

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

   - Use `./scripts/validate-skill.sh --ci` only when you want **GitHub Actions-style** `::error` / `::warning` lines (e.g. debugging CI output); normally omit it locally.
   - **Raw one-liner** (equivalent flags):

     ```bash
     skill-validator check --strict --allow-flat-layouts --allow-extra-frontmatter skills/
     ```

   With `--strict`, warnings fail the run (exit `1`). Optional: [Homebrew install](https://github.com/agent-ecosystem/skill-validator#install-cli) (`brew tap agent-ecosystem/tap && brew install skill-validator`) if you prefer not to use `go install`.

**Note:** Skill markdown must not link **outside** the skill directory (e.g. no `../README.md`); describe repo-level files in prose instead.

## Before you open a pull request

1. **Fact-check** any product behavior you document against current **official** docs or release notes for that product—not only blog posts or old threads.
2. **Run** `./scripts/validate-skill.sh` (see above).
3. **Exercise the skill** you changed: follow the happy path in `SKILL.md` (e.g. commands, containers, client smoke test) when the skill includes procedural steps.
4. **Keep diffs focused**—one logical change per PR when possible (e.g. “fix port wording in Aerospike skill” vs mixing unrelated skills or refactors).

For **Aerospike** changes specifically: verify ports, namespaces, TTL/NSUP, and image names against [Aerospike documentation](https://aerospike.com/docs/); run the Docker flow and at least **one** client example from [`examples.md`](skills/aerospike-getting-started/examples.md) for a stack you have installed. Avoid duplicating the full `aerospike.conf` in multiple files—keep one canonical copy in [`SKILL.md`](skills/aerospike-getting-started/SKILL.md) unless you have a strong reason.

## Style

- **Concise:** The agent already knows generic programming; add only **Aerospike-oriented** or failure-prone detail when editing the Aerospike skill, and the same idea—product-oriented, non-generic detail—for other skills.
- **Consistent terminology** within a skill: follow the vocabulary the skill defines (for Aerospike: namespace, set, record, bin—not mixed SQL metaphors).
- **Links:** Prefer stable vendor doc URLs; if a URL might move, note the section name so maintainers can find a replacement.

### Token footprint (`ex-*` files)

Skills under [`skills/`](skills/) are checked with [skill-validator](https://github.com/agent-ecosystem/skill-validator); large pasted content triggers **high token-count** warnings. For **`references/ex-*`** files: use **link-first** tables pointing at official Aerospike **Code block** sections; add **at most one or two** short minimal snippets (e.g. Python and Java) when copy-paste anchors help—**not** a full mirror of every language. **Do not** paste the same multi-language tutorial in full here—that duplicates [Aerospike documentation](https://aerospike.com/docs/) and inflates agent context.

## Suggesting changes without a PR

Open an issue (if your host supports it) with: what you tried, what you expected, relevant product or client versions, and OS—so others can reproduce.
