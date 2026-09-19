# Reference

## Operational and out-of-scope questions

For deployment, sizing, replication, XDR, backup/restore, and node operations, use Aerospike **database** and **operations** documentation—not this development skill.

## Building with Aerospike (`develop/learn`)

Hub: [Building with Aerospike](https://aerospike.com/docs/develop/learn)

| Area | Entry |
|------|--------|
| Overview (data models, command types) | [develop/learn](https://aerospike.com/docs/develop/learn) |
| Single record | [Single record](https://aerospike.com/docs/develop/learn/single/) |
| Bin operations / `operate` | [Bin operations](https://aerospike.com/docs/develop/learn/bin-operations/) |
| Batch | [Batch](https://aerospike.com/docs/develop/learn/batch/) |
| Queries | [Queries](https://aerospike.com/docs/develop/learn/queries/) |
| Policies | [Policies (develop/learn)](https://aerospike.com/docs/develop/learn/policies) · [Policies (database/learn)](https://aerospike.com/docs/database/learn/policies/) |
| Security (developer-facing) | [Security](https://aerospike.com/docs/develop/learn/security/) |
| Best practices | [Best practices](https://aerospike.com/docs/develop/learn/best-practices) |
| Strong consistency | [Strong consistency](https://aerospike.com/docs/develop/learn/strong-consistency) |
| Transactions | [Create and use transactions](https://aerospike.com/docs/develop/learn/create-and-use-transactions) |

## Data types and expressions

| Topic | Entry |
|-------|--------|
| Map | [Map](https://aerospike.com/docs/develop/data-types/collections/map) |
| List | [List](https://aerospike.com/docs/develop/data-types/collections/list) |
| Nested context / paths | [Context](https://aerospike.com/docs/develop/data-types/collections/context) |
| Path expressions | [Path expressions](https://aerospike.com/docs/develop/expressions/path/) |
| Nested lists and maps (CDTs + expressions) | [Nesting](https://aerospike.com/docs/develop/expressions/nesting) |

## Architecture (conceptual, for app design)

| Topic | Entry |
|-------|--------|
| Data model | [Data model](https://aerospike.com/docs/database/learn/architecture/data-storage/data-model) |
| Primary index | [Primary index](https://aerospike.com/docs/database/learn/architecture/data-storage/primary-index) |
| Secondary index | [Secondary index](https://aerospike.com/docs/database/learn/architecture/data-storage/secondary-index) |
| Client architecture | [Client architecture](https://aerospike.com/docs/database/learn/architecture/client-architecture) |
| Durable deletes (tombstones, EE) | [Durable deletes](https://aerospike.com/docs/database/learn/architecture/durable-deletes) |

## Language clients (`develop/client`)

Hub: [Client development](https://aerospike.com/docs/develop/client)

| Language | Entry |
|----------|--------|
| Java | [Java](https://aerospike.com/docs/develop/client/java) |
| Python | [Python](https://aerospike.com/docs/develop/client/python) |
| Go | [Go](https://aerospike.com/docs/develop/client/go) |
| Node.js | [Node.js](https://aerospike.com/docs/develop/client/node) |
| C# | [C#](https://aerospike.com/docs/develop/client/csharp) |
| Rust | [Rust](https://aerospike.com/docs/develop/client/rust) |

### Client source repositories

The pages above document the API. The client source lives on GitHub, in the `aerospike` organization—read a repository when you need the version that is authoritative for a release, a build recipe, or behavior the API reference does not spell out.

| Client | Repository | When to use |
|--------|------------|-------------|
| Java SDK | [github.com/aerospike/aerospike-client-java-sdk](https://github.com/aerospike/aerospike-client-java-sdk) | Use for new Java projects |
| Python SDK | [github.com/aerospike/aerospike-client-python-sdk](https://github.com/aerospike/aerospike-client-python-sdk) | Use for new Python projects |
| Rust | [github.com/aerospike/aerospike-client-rust](https://github.com/aerospike/aerospike-client-rust) |  |
| C# | [github.com/aerospike/aerospike-client-csharp](https://github.com/aerospike/aerospike-client-csharp) |  |
| Go | [github.com/aerospike/aerospike-client-go](https://github.com/aerospike/aerospike-client-go) |  |
| Node.js | [github.com/aerospike/aerospike-client-nodejs](https://github.com/aerospike/aerospike-client-nodejs) |  |
| C | [github.com/aerospike/aerospike-client-c](https://github.com/aerospike/aerospike-client-c) |  |
| Java (legacy) | [github.com/aerospike/aerospike-client-java](https://github.com/aerospike/aerospike-client-java) | Existing codebases already on it; new work uses the Java SDK |
| Python (legacy) | [github.com/aerospike/aerospike-client-python](https://github.com/aerospike/aerospike-client-python) | Existing codebases already on it; new work uses the Python SDK |

Java and Python each have two clients. The **Java SDK** and **Python SDK** are the current line and where new projects start; the older `aerospike-client-java` and `aerospike-client-python` remain supported for codebases already built on them, and are not the choice for new work.

**Read the repository's `README.md` before generating code against a client.** Each carries an **`AI coding agent entry point`** section near the top, written by the client developers: the package and namespace to import, where the authoritative version lives in the source tree, the API reference URL, and a short "what to read, by task" table. `AGENTS.md` in the repository root is a one-line pointer to that section, not the content.

The section is rolling out across the clients, so a repository may not carry one yet. Where it does not, read the `README.md` as a whole—it is the developers' own account of the client, and closer to the shipped code than any summary here.

## Namespace retention (TTL, expiration, eviction)

| Topic | Entry |
|-------|--------|
| Data retention, TTL, NSUP, cold restart | [Configuring namespace data retention](https://aerospike.com/docs/database/manage/namespace/retention) |

## Database hub (ops boundary)

[Database documentation](https://aerospike.com/docs/database/) — configuration, clustering, and operations when leaving pure application development.
