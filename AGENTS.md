# AI assistant guidance (tool-agnostic)

Agent Skills live under [`skills/`](skills/); additional skills may appear there over time. This repo’s primary skill today is **vetted Aerospike Database** getting-started material: local Docker, correct defaults (namespaces, ports, TTL/NSUP), and official client examples. It is aimed at **single-node development** and first read/write—not production cluster design. For **application-level** Aerospike client work (CDTs, policies, modular rules, and modeling against an existing schema), see [`skills/aerospike-development/`](skills/aerospike-development/SKILL.md) and [`skills/aerospike-development/references/README.md`](skills/aerospike-development/references/README.md). For **design-time data modeling** — deriving a schema from requirements when none exists yet, or redesigning one — see [`skills/aerospike-data-modeling/`](skills/aerospike-data-modeling/SKILL.md).

## When to use these instructions

Apply when the user (or task) involves **Aerospike**, **Docker-based Aerospike**, **client SDK** usage (Python, Node.js, Go, Java, C#), or **replacing Redis/Memcached** with Aerospike for persistence or scale. Core database only (not Aerospike Graph).

## Read order

1. [`skills/aerospike-getting-started/SKILL.md`](skills/aerospike-getting-started/SKILL.md) — Critical rules, hallucination blacklist, autonomous first-run Docker steps, documentation links.
2. [`skills/aerospike-getting-started/examples.md`](skills/aerospike-getting-started/examples.md) — Per-language put/get examples and Node.js batching notes.
3. [`skills/aerospike-getting-started/reference.md`](skills/aerospike-getting-started/reference.md) — Custom config, Docker Compose, Community vs Enterprise, troubleshooting.

Do not invent REST APIs, SQL DDL, or wrong package names; follow the blacklist in `SKILL.md`.

## Humans

See [`README.md`](README.md) for install paths, checklists, and how to use this repo with specific tools (Cursor, Copilot, etc.).
