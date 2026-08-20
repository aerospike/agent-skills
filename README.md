# Aerospike agent skills

This repository holds **Aerospike-related Agent Skills** under [`skills/`](skills/). Each skill is a self-contained folder you can copy into **Cursor**, add to **GitHub Copilot** context via repo instructions, or use with **Claude** and other assistants. Skills focus on the **core Aerospike Database** (not Aerospike Graph).

**Plain-language topics:** real-time / low-latency key-value storage, Redis or Memcached–style patterns with persistence, feature stores, user profiles, client-side modeling and policies.

The **canonical list of skills** (and what to copy) is [`skills/README.md`](skills/README.md). More Aerospike skills may appear there over time.

**Layout note:** If you previously used `aerospike-getting-started/` at the **repository root**, it now lives at **`skills/aerospike-getting-started/`**. That folder is for **contributors** who edit the skill sources; users install the compiled skill from [`compiled-skills/`](compiled-skills/README.md).

## Skills in this repository

| Skill folder | Purpose | Entry |
|--------------|---------|--------|
| `aerospike-getting-started` | Local Docker, namespaces/ports/TTL, first put/get, official client snippets, Community vs Enterprise, troubleshooting for new users | [`skills/aerospike-getting-started/SKILL.md`](skills/aerospike-getting-started/SKILL.md) |
| `aerospike-development` | Application development: CDTs, expressions, indexes, batch/scan, policies, modeling against an existing schema, modular rules under `references/` | [`skills/aerospike-development/SKILL.md`](skills/aerospike-development/SKILL.md) |
| `aerospike-data-modeling` | Design-time data modeling: deriving a schema from requirements when none exists yet, or redesigning one | [`skills/aerospike-data-modeling/SKILL.md`](skills/aerospike-data-modeling/SKILL.md) |

**Choosing a skill:** Use **getting-started** when you need a dev instance, correct defaults, or a first verified read/write. Use **development** when you are writing or reviewing client code against a model that already exists. Use **data-modeling** when the schema itself is the deliverable. You can install **all**; they complement each other.

**Out of scope for these skills:** production cluster topology, full operations runbooks, Kubernetes/Helm, or cloud-specific deployment—for that, use [Aerospike documentation](https://aerospike.com/docs/) (links also appear in the getting-started skill).

## Who this is for

- Developers who want a **working local instance** and **first client I/O** (getting-started).
- Developers building or reviewing **Aerospike client applications** (development skill).
- Teams that want **consistent AI-assisted** answers when working with Aerospike.

## What’s in the repo

| Path | Purpose |
|------|---------|
| [skills/README.md](skills/README.md) | Index of skills in this repository (update this when adding a skill) |
| [skills/aerospike-getting-started/SKILL.md](skills/aerospike-getting-started/SKILL.md) | Getting started: critical rules, anti-hallucination checklist, Docker steps, documentation links (YAML frontmatter for Cursor) |
| [skills/aerospike-getting-started/examples.md](skills/aerospike-getting-started/examples.md) | Per-language put/get examples and Node.js batching notes |
| [skills/aerospike-getting-started/reference.md](skills/aerospike-getting-started/reference.md) | Custom config, Docker Compose, Community vs Enterprise, troubleshooting |
| [skills/aerospike-development/SKILL.md](skills/aerospike-development/SKILL.md) | Development skill: role, scope, mental model, pointers into references |
| [skills/aerospike-development/references/README.md](skills/aerospike-development/references/README.md) | TOC of modular rules and thin `ex-*` example tables |
| [skills/aerospike-development/reference.md](skills/aerospike-development/reference.md) | Doc map and deeper pointers for client work |
| [skills/aerospike-development/examples.md](skills/aerospike-development/examples.md) | Additional examples for the development skill |
| [skills/aerospike-data-modeling/SKILL.md](skills/aerospike-data-modeling/SKILL.md) | Data modeling skill: design-time workflow, mental model, pointers into references |
| [AGENTS.md](AGENTS.md) | Short read order and routing for any AI assistant |
| [compiled-skills/aerospike/SKILL.md](compiled-skills/aerospike/SKILL.md) | Published agent skill, compiled from `skills/` into one file |
| [.github/copilot-instructions.md](.github/copilot-instructions.md) | GitHub Copilot repository instructions |

Skill packaging evaluation (structure A/B tests, coverage gates) lives in the separate [agent-skills-eval](https://github.com/citrusleaf/agent-skills-eval) repository.

The **canonical** `aerospike.conf` and commands for local setup live in [`skills/aerospike-getting-started/SKILL.md`](skills/aerospike-getting-started/SKILL.md) (not duplicated here).

## Using with AI assistants

We publish **one** skill: [`compiled-skills/aerospike/SKILL.md`](compiled-skills/aerospike/SKILL.md), compiled from the three authoring folders under [`skills/`](skills/). Registries list that artifact only. The folders under `skills/` are maintained for editing and compilation, not as separate install targets.

| Tool | What to do |
|------|----------------|
| **Any agent (recommended)** | Add [`compiled-skills/aerospike/SKILL.md`](compiled-skills/aerospike/SKILL.md) to always-on context. [Install guide](compiled-skills/README.md). Raw URL: `https://raw.githubusercontent.com/aerospike/agent-skills/main/compiled-skills/aerospike/SKILL.md` |
| **`skills` CLI (any supported agent)** | `npx skills add https://github.com/aerospike/agent-skills/tree/main/compiled-skills/aerospike` installs the published skill. Do not use the repository root URL — the CLI discovers `skills/` first and would install the uncompiled authoring folders. |
| **Gemini CLI** | `npx skills add https://github.com/aerospike/agent-skills/tree/main/compiled-skills/aerospike -a gemini-cli` installs to `.agents/skills/aerospike/` (globally `~/.gemini/skills/`). |
| **GitHub Copilot** | Uses [`.github/copilot-instructions.md`](.github/copilot-instructions.md) in supported clients; see also [AGENTS.md](AGENTS.md). |
| **Claude Code / similar** | Open [CLAUDE.md](CLAUDE.md) and [AGENTS.md](AGENTS.md); add [`compiled-skills/aerospike/SKILL.md`](compiled-skills/aerospike/SKILL.md) to project instructions or skills. |
| **Other chats (Claude, ChatGPT, etc.)** | Upload or link [`compiled-skills/aerospike/SKILL.md`](compiled-skills/aerospike/SKILL.md). |

## Use without AI tools (any editor)

### Path A: First local instance and first put/get

1. Read **Critical rules** and **Hallucination blacklist** in [`skills/aerospike-getting-started/SKILL.md`](skills/aerospike-getting-started/SKILL.md).
2. Run **Autonomous first-run steps** in the same file (Docker + config + verify logs).
3. Pick your language in [`examples.md`](skills/aerospike-getting-started/examples.md) and run a write/read test.
4. For Compose, Enterprise evaluation, or troubleshooting, see [`reference.md`](skills/aerospike-getting-started/reference.md).

### Path B: Application development (modeling, CDTs, policies)

1. Read [`skills/aerospike-development/SKILL.md`](skills/aerospike-development/SKILL.md) for scope and mental model.
2. Use [`skills/aerospike-development/references/README.md`](skills/aerospike-development/references/README.md) for the rules and example TOC; [`reference.md`](skills/aerospike-development/reference.md) and [`examples.md`](skills/aerospike-development/examples.md) as needed.

## First-hour checklist (getting-started skill)

Use this when your goal is a **running local database** and a **verified first client write/read**.

- [ ] Docker is installed and `docker --version` works.
- [ ] Aerospike container is running per [`skills/aerospike-getting-started/SKILL.md`](skills/aerospike-getting-started/SKILL.md) (ports `3000–3002` mapped; add `3003` if you need admin access on Database **8.1.0+**—see that file).
- [ ] Logs show the ready line described in `SKILL.md` (successful startup).
- [ ] Client SDK installed for your language; write/read example prints success.
- [ ] (Optional) Skim **Documentation links** in the same `SKILL.md` for next steps.

## Maintenance and distribution

- **`metadata.last_verified`:** Each skill’s `SKILL.md` may carry `last_verified` under `metadata`. When you change Docker images, client commands, or major facts for **that** skill, re-check the documented flow and update the date.
- **Linting skills:** Run `./scripts/validate-skill.sh` (see [CONTRIBUTING.md](CONTRIBUTING.md#validate-the-skill-package-skill-validator)); CI runs the same check via [`.github/workflows/skill-validator.yml`](.github/workflows/skill-validator.yml).
- **Spec conformance:** Run `./scripts/validate-spec.sh` to check `SKILL.md` frontmatter against the [Agent Skills specification](https://agentskills.io/specification); CI runs it via [`.github/workflows/spec-conformance.yml`](.github/workflows/spec-conformance.yml).
- **Publishing:** Registry submission is automated on release—see [`docs/PUBLISHING.md`](docs/PUBLISHING.md).
- **Compiled skill:** `compiled-skills/` is generated from `skills/`. After editing any skill, run `python3 scripts/compile-agents.py --write`; CI fails the PR if the compiled output is stale. Frontmatter for the published skill lives in `scripts/skills_compile/published_skill.yaml`.
- **Contributing:** See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add or edit skills and keep root docs in sync.
- **Redistribution:** This repository is licensed under the [Apache License 2.0](LICENSE), matching [aerospike/data-modeling-guide](https://github.com/aerospike/data-modeling-guide).

## Official documentation

Links to Aerospike docs (quick start, configuration, clients, Docker) are collected in the **Documentation links** section at the bottom of [`skills/aerospike-getting-started/SKILL.md`](skills/aerospike-getting-started/SKILL.md). The development skill’s [`reference.md`](skills/aerospike-development/reference.md) points to additional client and operations documentation where relevant.
