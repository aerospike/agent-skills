# AI assistant guidance (tool-agnostic)

Agent Skills live under [`skills/`](skills/). This repository ships **multiple** Aerospike-related skills today; more may appear under `skills/` over time. The canonical index is [`skills/README.md`](skills/README.md).

| User or task needs… | Start with |
|---------------------|------------|
| Local Docker, namespaces/ports/TTL/NSUP, first put/get, Community vs Enterprise images, troubleshooting for a new dev instance | [`skills/aerospike-getting-started/SKILL.md`](skills/aerospike-getting-started/SKILL.md) |
| CDTs, expressions, secondary indexes, batch/scan/query, client policies, performance-oriented client guidance, modeling against a schema that already exists | [`skills/aerospike-development/SKILL.md`](skills/aerospike-development/SKILL.md) |
| Design-time data modeling — deriving a schema from requirements when none exists yet, or redesigning one | [`skills/aerospike-data-modeling/SKILL.md`](skills/aerospike-data-modeling/SKILL.md) |
| First program **after** you already have a running instance | Getting-started [`examples.md`](skills/aerospike-getting-started/examples.md); then development skill if the work goes beyond basic I/O |
| Unsure which skill applies | [`skills/README.md`](skills/README.md), then open the matching `SKILL.md` |

Core database only (not Aerospike Graph). For cluster operations, sizing, or XDR, the development skill defers to Aerospike Operations documentation—see its [`reference.md`](skills/aerospike-development/reference.md).

## When to use these instructions

Apply when the user (or task) involves **Aerospike**, **Docker-based Aerospike**, **client SDK** usage (Python, Node.js, Go, Java, C#, etc.), or **replacing Redis/Memcached** with Aerospike for persistence or scale—then route using the table above.

## Read order

**Fast path:** [`compiled-skills/aerospike/SKILL.md`](compiled-skills/aerospike/SKILL.md) — published rules for the getting-started, development, and data-modeling skills in one file, updated on every merge to `main`. [Install guide](compiled-skills/README.md).

**More detail** (optional, under `skills/`):

1. [`skills/README.md`](skills/README.md) — Which skill folder to open (especially as the repo grows).
2. **Getting started (local + defaults + first I/O):** [`skills/aerospike-getting-started/SKILL.md`](skills/aerospike-getting-started/SKILL.md) → [`skills/aerospike-getting-started/examples.md`](skills/aerospike-getting-started/examples.md) → [`skills/aerospike-getting-started/reference.md`](skills/aerospike-getting-started/reference.md) as needed.
3. **Application development:** [`skills/aerospike-development/SKILL.md`](skills/aerospike-development/SKILL.md) → [`skills/aerospike-development/references/README.md`](skills/aerospike-development/references/README.md) → [`skills/aerospike-development/reference.md`](skills/aerospike-development/reference.md) / [`skills/aerospike-development/examples.md`](skills/aerospike-development/examples.md) as needed.
4. **Design-time data modeling:** [`skills/aerospike-data-modeling/SKILL.md`](skills/aerospike-data-modeling/SKILL.md) → [`skills/aerospike-data-modeling/references/`](skills/aerospike-data-modeling/references/) → [`skills/aerospike-data-modeling/reference.md`](skills/aerospike-data-modeling/reference.md) as needed.

Do not invent REST APIs, SQL DDL, or wrong package names; follow the blacklist in [`skills/aerospike-getting-started/SKILL.md`](skills/aerospike-getting-started/SKILL.md) / [`compiled-skills/aerospike/SKILL.md`](compiled-skills/aerospike/SKILL.md).

## Humans

See [`README.md`](README.md) for install paths, checklists, and how to use this repo with specific tools (Cursor, Copilot, etc.).
