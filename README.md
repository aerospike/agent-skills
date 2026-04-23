# Aerospike agent skills

This repository holds **Aerospike-related Agent Skills** under [`skills/`](skills/). Each skill is a self-contained folder you can copy into **Cursor**, add to **GitHub Copilot** context via repo instructions, or use with **Claude** and other assistants. Skills focus on the **core Aerospike Database** (not Aerospike Graph).

**Plain-language topics:** real-time / low-latency key-value storage, Redis or Memcached–style patterns with persistence, feature stores, user profiles, client-side modeling and policies.

The **canonical list of skills** (and what to copy) is [`skills/README.md`](skills/README.md). More Aerospike skills may appear there over time.

**Layout note:** If you previously used `aerospike-getting-started/` at the **repository root**, it now lives at **`skills/aerospike-getting-started/`**. Copy from `skills/<skill-name>/` when installing into an agent.

## Skills in this repository

| Skill folder | Purpose | Entry |
|--------------|---------|--------|
| `aerospike-getting-started` | Local Docker, namespaces/ports/TTL, first put/get, official client snippets, Community vs Enterprise, troubleshooting for new users | [`skills/aerospike-getting-started/SKILL.md`](skills/aerospike-getting-started/SKILL.md) |
| `aerospike-development` | Application development: modeling, CDTs, expressions, indexes, batch/scan, policies, modular rules under `references/` | [`skills/aerospike-development/SKILL.md`](skills/aerospike-development/SKILL.md) |

**Choosing a skill:** Use **getting-started** when you need a dev instance, correct defaults, or a first verified read/write. Use **development** when you are designing access patterns, tuning client code, or working through CDTs/policies/expressions. You can install **both**; they complement each other.

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
| [AGENTS.md](AGENTS.md) | Short read order and routing for any AI assistant |
| [.github/copilot-instructions.md](.github/copilot-instructions.md) | GitHub Copilot repository instructions |

The **canonical** `aerospike.conf` and commands for local setup live in [`skills/aerospike-getting-started/SKILL.md`](skills/aerospike-getting-started/SKILL.md) (not duplicated here).

## Using with AI assistants

Copy **one or more** folders from `skills/<skill-name>/` into your tool’s skills location. The directory name on disk must match the YAML `name` in that skill’s `SKILL.md` (for example `aerospike-getting-started` or `aerospike-development`).

| Tool | What to do |
|------|----------------|
| **Cursor** | Copy `skills/aerospike-getting-started` and/or `skills/aerospike-development` to `<project>/.cursor/skills/<same-folder-name>/` (or `~/.cursor/skills/` for all projects). Restart Cursor. Each skill is discovered via its YAML `description` in `SKILL.md`. |
| **GitHub Copilot** | Uses [`.github/copilot-instructions.md`](.github/copilot-instructions.md) in supported clients; see also [AGENTS.md](AGENTS.md). |
| **Claude Code / similar** | Open [CLAUDE.md](CLAUDE.md) and [AGENTS.md](AGENTS.md); skill bodies live under `skills/*/`. |
| **Other chats (Claude, ChatGPT, etc.)** | Add the skill folder(s) or this whole repo to a **project** / **knowledge** set, or paste the path to the relevant `SKILL.md` when asking questions. |

## Install for Cursor (optional)

1. Copy the entire folder for each skill you want—for example `skills/aerospike-getting-started` and/or `skills/aerospike-development`—into either location:
   - **Project skills (recommended for sharing with a repo):**  
     `<your-project>/.cursor/skills/<skill-folder-name>/`
   - **Personal skills (all projects on this machine):**  
     `~/.cursor/skills/<skill-folder-name>/`
2. Restart Cursor or reload the window if a skill does not appear.
3. In chat, describe your task (local Docker vs client modeling); the agent can match skills using each `SKILL.md` YAML `description`.

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

- **`last_verified`:** Each skill’s `SKILL.md` may include `last_verified`. When you change Docker images, client commands, or major facts for **that** skill, re-check the documented flow and update the date.
- **Linting skills:** Run `./scripts/validate-skill.sh` (see [CONTRIBUTING.md](CONTRIBUTING.md#validate-the-skill-package-skill-validator)); CI runs the same check via [`.github/workflows/skill-validator.yml`](.github/workflows/skill-validator.yml).
- **Contributing:** See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add or edit skills and keep root docs in sync.
- **Redistribution:** Add a `LICENSE` file to the repository if you want explicit terms for copying this package; this README does not impose a license by itself.

## Official documentation

Links to Aerospike docs (quick start, configuration, clients, Docker) are collected in the **Documentation links** section at the bottom of [`skills/aerospike-getting-started/SKILL.md`](skills/aerospike-getting-started/SKILL.md). The development skill’s [`reference.md`](skills/aerospike-development/reference.md) points to additional client and operations documentation where relevant.
