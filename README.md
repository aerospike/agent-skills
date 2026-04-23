# Agent skills (Aerospike getting started)

This repository holds **Agent Skills** under [`skills/`](skills/). Today the main package is **getting-started Aerospike Database** content: a **single-node** local instance (Docker), correct defaults (namespaces, ports, TTL/NSUP), and official **client examples** (Python, Node.js, Go, Java, C#). Use it yourself in any editor, or wire it into **Cursor**, **GitHub Copilot**, **Claude**, or other tools that read repo instructions.

**Plain-language topics:** Aerospike, real-time / low-latency key-value storage, Redis or Memcached–style caching with persistence, feature stores, user profiles. This material covers the **core database** only (not Aerospike Graph).

**Layout change:** If you previously used `aerospike-getting-started/` at the **repository root**, it now lives at **`skills/aerospike-getting-started/`**. Copy from that path when installing into an agent.

## Who this is for

- Developers and evaluators who want a **working dev instance** and a **first write/read** with correct defaults.
- Teams that want **consistent AI-assisted** answers when working with Aerospike in this repo.

**Out of scope here:** production topology, full operations runbooks, Kubernetes/Helm, or cloud-specific deployment guides. For that, use the [official documentation](#official-documentation) linked from the skill package.

## What’s in the repo

| Path | Purpose |
|------|---------|
| [skills/README.md](skills/README.md) | Index of skills in this repository |
| [skills/aerospike-getting-started/SKILL.md](skills/aerospike-getting-started/SKILL.md) | Main instructions: critical rules, anti-hallucination checklist, Docker steps, documentation links (includes Cursor skill YAML frontmatter) |
| [skills/aerospike-getting-started/examples.md](skills/aerospike-getting-started/examples.md) | Client SDK examples and Node.js batching notes |
| [skills/aerospike-getting-started/reference.md](skills/aerospike-getting-started/reference.md) | Custom config, Docker Compose, Community vs Enterprise, troubleshooting |
| [AGENTS.md](AGENTS.md) | Short read order and scope for any AI assistant |
| [.github/copilot-instructions.md](.github/copilot-instructions.md) | GitHub Copilot repository instructions |

The **canonical** `aerospike.conf` and commands for local setup live in `SKILL.md` (not duplicated here).

## Using with AI assistants

| Tool | What to do |
|------|----------------|
| **Cursor** | Copy the folder `skills/aerospike-getting-started` to `<project>/.cursor/skills/aerospike-getting-started/` (or `~/.cursor/skills/` for all projects). Restart Cursor. The skill is discovered via the YAML `description` in `SKILL.md`. |
| **GitHub Copilot** | Uses [`.github/copilot-instructions.md`](.github/copilot-instructions.md) automatically in supported clients; see also [AGENTS.md](AGENTS.md). |
| **Claude Code / similar** | Open [CLAUDE.md](CLAUDE.md) and [AGENTS.md](AGENTS.md); full detail is under `skills/aerospike-getting-started/`. |
| **Other chats (Claude, ChatGPT, etc.)** | Add the `skills/aerospike-getting-started/` files (or this whole repo) to a **project** / **knowledge** set, or paste the path to `SKILL.md` when asking questions. |

## Install for Cursor (optional)

1. Copy the entire folder `skills/aerospike-getting-started` into either location:
   - **Project skill (recommended for sharing with a repo):**  
     `<your-project>/.cursor/skills/aerospike-getting-started/`
   - **Personal skill (all projects on this machine):**  
     `~/.cursor/skills/aerospike-getting-started/`
2. Restart Cursor or reload the window if the skill does not appear.
3. In chat, ask for help with Aerospike getting started, Docker, or client code—the agent can use the skill based on its YAML `description` in `SKILL.md`.

## Use without AI tools (any editor)

Follow this order:

1. Read **Critical rules** and **Hallucination blacklist** in [SKILL.md](skills/aerospike-getting-started/SKILL.md).
2. Run **Autonomous first-run steps** in the same file (Docker + config + verify logs).
3. Pick your language in [examples.md](skills/aerospike-getting-started/examples.md) and run a write/read test.
4. For Compose, Enterprise evaluation, or troubleshooting, see [reference.md](skills/aerospike-getting-started/reference.md).

## First-hour checklist

- [ ] Docker is installed and `docker --version` works.
- [ ] Aerospike container is running per `SKILL.md` (ports `3000–3002` mapped; add `3003` if you need admin access on Database **8.1.0+**—see `SKILL.md`).
- [ ] Logs show the ready line described in `SKILL.md` (successful startup).
- [ ] Client SDK installed for your language; write/read example prints success.
- [ ] (Optional) Skim [Documentation links](skills/aerospike-getting-started/SKILL.md#documentation-links) in `SKILL.md` for next steps.

## Maintenance and distribution

- **`last_verified`:** The skill frontmatter in [SKILL.md](skills/aerospike-getting-started/SKILL.md) includes `last_verified`. When you change Docker images, client commands, or major facts, re-run the Docker flow and one client example, then update that date.
- **Linting skills:** Run `./scripts/validate-skill.sh` (see [CONTRIBUTING.md](CONTRIBUTING.md#validate-the-skill-package-skill-validator)); CI runs the same check via [`.github/workflows/skill-validator.yml`](.github/workflows/skill-validator.yml).
- **Contributing:** See [CONTRIBUTING.md](CONTRIBUTING.md) for scope, which file to edit, and PR expectations.
- **Redistribution:** Add a `LICENSE` file to the repository if you want explicit terms for copying this package; this README does not impose a license by itself.

## Official documentation

Links to Aerospike docs (quick start, configuration, clients, Docker) are collected in the **Documentation links** section at the bottom of [SKILL.md](skills/aerospike-getting-started/SKILL.md).
