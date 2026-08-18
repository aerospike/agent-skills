# Skills in this repository

| Folder | Purpose |
|--------|---------|
| [aerospike-getting-started/](aerospike-getting-started/SKILL.md) | Aerospike Database: local Docker, official clients, put/get, defaults (getting started). |
| [aerospike-development/](aerospike-development/SKILL.md) | Aerospike app development: [`SKILL.md`](aerospike-development/SKILL.md), [`references/`](aerospike-development/references/README.md) (rules + thin `ex-*` link tables), [`examples.md`](aerospike-development/examples.md). Keep `ex-*` small—see [CONTRIBUTING.md](../CONTRIBUTING.md#token-footprint-ex-files). Implementation-time: writing and reviewing code against a model that already exists. Not cluster ops. |
| [aerospike-data-modeling/](aerospike-data-modeling/SKILL.md) | Aerospike data model design: [`SKILL.md`](aerospike-data-modeling/SKILL.md), [`references/`](aerospike-data-modeling/references/), [`reference.md`](aerospike-data-modeling/reference.md). Design-time: deriving a schema from requirements, or redesigning one, producing a schema guide and schema summary. Escalates to the `https://github.com/aerospike/data-modeling-guide` repository for the full workflow. |

Copy any skill folder (e.g. `aerospike-getting-started`) into your agent’s skills directory; the leaf folder name must match the YAML `name` in `SKILL.md`.
