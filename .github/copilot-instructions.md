# Repository instructions for GitHub Copilot

For a short overview and read order, see [`AGENTS.md`](../AGENTS.md) at the repository root and the skill index [`skills/README.md`](../skills/README.md).

**Fast path:** the published rules for all skills are compiled into [`compiled-skills/aerospike/SKILL.md`](../compiled-skills/aerospike/SKILL.md).

When the user’s task involves **Aerospike Database**, route as follows:

- **Docker / local single-node setup**, namespaces, ports, TTL/NSUP, first put/get, Community vs Enterprise, or troubleshooting for a new dev instance: follow [`skills/aerospike-getting-started/SKILL.md`](../skills/aerospike-getting-started/SKILL.md) with [`examples.md`](../skills/aerospike-getting-started/examples.md) and [`reference.md`](../skills/aerospike-getting-started/reference.md) as needed.
- **Application-level client work** (CDTs, expressions, secondary indexes, batch/scan/query, policies, client tuning, modeling against a schema that already exists): follow [`skills/aerospike-development/SKILL.md`](../skills/aerospike-development/SKILL.md) and the modular rules under [`skills/aerospike-development/references/README.md`](../skills/aerospike-development/references/README.md); use [`reference.md`](../skills/aerospike-development/reference.md) and [`examples.md`](../skills/aerospike-development/examples.md) when deeper pointers or examples help.
- **Design-time data modeling** (deriving a schema from requirements when none exists, or redesigning one): follow [`skills/aerospike-data-modeling/SKILL.md`](../skills/aerospike-data-modeling/SKILL.md) and its [`references/`](../skills/aerospike-data-modeling/references/).

Do not invent REST APIs, SQL DDL, or wrong package names; follow the blacklist in the getting-started `SKILL.md`.
