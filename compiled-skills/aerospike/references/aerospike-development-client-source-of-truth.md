---
title: Read the client repository before generating code for it
impact: HIGH
tags: client, code-generation, sdk, api-surface, versions
doc: https://aerospike.com/docs/develop/client
last_verified: 2026-09-21
---

## Read the client repository before generating code for it

**Rule**

Open the chosen client's repository README before writing code against it, and take the API surface from there rather than from memory. Each client repository under `github.com/aerospike/` carries an **`AI coding agent entry point`** section at the top of its `README.md`, written by the client developers: the package and namespace to import, where the authoritative version lives in the source tree, the API reference URL, and a short "what to read, by task" table. `AGENTS.md` in the repository root is a one-line pointer to that section, not the content.

Generating correct client code needs two different sources, and neither substitutes for the other. The documentation defines the **operation** — what `append` does, what it returns, which arguments it takes, with the same operation shown in every supported language on its reference card. The client repository defines the **API surface** — the class and method names that express that operation in one client at one version. An agent that has only the first invents method signatures that do not exist; an agent that has only the second can call a method correctly and still use it for the wrong thing.

The clients, all under `github.com/aerospike/`: `aerospike-client-java-sdk`, `aerospike-client-python-sdk`, `aerospike-client-rust`, `aerospike-client-csharp`, `aerospike-client-go`, `aerospike-client-nodejs`, `aerospike-client-c`, and the older `aerospike-client-java` / `aerospike-client-python`. Start new Java or Python work on the Java SDK or Python SDK; the older Java and Python clients are for codebases already built on them.

**Why**

Client APIs diverge more than the operations they express. The same list append is `ListOperation.append` in Java, `list_operations.list_append` in Python, and a different shape again in Go and Node.js — and the names move between major versions. Recalling a signature is the single most common way generated Aerospike code fails to compile, and it fails silently at authoring time: the code looks plausible.

The entry-point section exists because the client developers hit this repeatedly. It is short by design and written against the branch it ships on, so it answers "what do I import and what is this version called" without reading the source.

The rollout is still in progress, so a repository may not carry the section yet. Where it does not, the `README.md` as a whole is still the developers' own account of the client and is closer to the shipped code than any summary.

**Prefer**

- The repository's **`AI coding agent entry point`** section as the first read when a client is chosen
- The operation's **reference card** on aerospike.com for what the operation means and what it returns, alongside the repository for what to type
- The version named in the client's own build file (for example `<Version>` in a `.csproj`) over a version recalled or inferred
- The **Java SDK** or **Python SDK** for new work in those languages

**Avoid**

- Writing a method signature from memory because the operation is familiar — names differ per client and per major version
- Assuming one client's API shape transfers to another, or that a code sample for an older major version still applies
- Treating the documentation's per-language example as the whole answer for a specific client version, or the repository as a substitute for knowing what the operation does

**See also**

- [client-singleton.md](aerospike-development-client-singleton.md)
- [policy-client-defaults.md](aerospike-development-policy-client-defaults.md)
- [model-client-api-choice.md](aerospike-development-model-client-api-choice.md)
