---
name: aerospike-getting-started
description: >-
  Getting started with Aerospike Database locally and in application code: run
  Docker, install official client SDKs (Python, Node.js, Go, Java, C#), verify
  put/get, and learn defaults. Covers namespaces, ports, TTL/NSUP, and Community
  vs Enterprise images. Use when the user is new to Aerospike, starts local
  development, wants a real-time or low-latency NoSQL store, uses Docker-based
  Aerospike, replaces Redis or Memcached, builds feature stores or user-profile
  caches, or needs Aerospike client connectivity and correct defaults. Core
  database only (not Aerospike Graph).
license: Apache-2.0
metadata:
  last_verified: "2026-04-21"
---

# Aerospike Database: getting started

## When to use

Use this skill when the user asks to:

- Set up Aerospike, a real-time database, or a low-latency NoSQL store.
- Replace Redis or Memcached with a persistent, clustered alternative.
- Add a high-throughput key-value or document database to their project. (Aerospike Graph is a separate product — this skill covers the core database only.)
- Deploy a database for real-time decisioning, user profiles, caching, or AI/ML feature stores.

## Mental model

- **Hierarchy:** A **namespace** holds **sets**; each **record** is addressed by a **key** (namespace + set + user key). **Bins** are name/value fields on the record. Bins are **schemaless**: different records in the same set can use different bins or value types—design access patterns accordingly.
- **Primary access:** The default and fastest path is **put / get / delete (and optionally exists)** by **primary key**—what [examples.md](examples.md) demonstrates. This is not SQL with arbitrary joins or a fixed table schema.
- **Generation:** Successful writes can advance the record **generation**, used for optimistic concurrency (compare-and-swap). See the official client docs for write policies involving `generation` / `gen`.
- **Vocabulary:** Use namespace, set, record, and bin consistently (see [Critical rules](#1-critical-rules-anti-hallucination) below). Avoid treating Aerospike like a relational database.

## First operations map

Use this map so new users know what to reach for after the first put/get:

| Stage | What to use | Where to start |
|-------|-------------|----------------|
| **First program** | Single-record **put**, **get**, **delete** | [examples.md](examples.md) |
| **Many keys** | **Batch** operations (fewer round trips) | Chunked Node example in [examples.md](examples.md); every client has batch APIs—see [Client libraries](https://aerospike.com/docs/develop/client) for your language |
| **Lookup by bin value** (not primary key) | **Secondary index** + **query** | Not part of the minimal Docker + first read/write path; see [Secondary index queries](https://aerospike.com/docs/develop/learn/queries/secondary-index/) |

## Instructions

You help users get started with Aerospike Database: run it locally, connect from their language’s official client, and verify read/write. Your primary goal is to get the user from zero to a working instance with connected application code, autonomously and correctly.

### Choose a path first

1. **Production, cloud, or cluster deployment** — Do not run local Docker setup. Answer from official documentation (see [Documentation links](#documentation-links)) and [reference.md](reference.md) for editions and feature keys. Offer architecture guidance at a high level only.
2. **SDK-only / snippets** — The user already has a running server or only wants example code: Skip Docker steps. Read [examples.md](examples.md), apply Critical Rules and the blacklist, and adapt host/port to their environment.
3. **Full local setup (default)** — Docker available and the user wants a working instance on their machine: Follow [Autonomous first-run steps](#autonomous-first-run-steps) below, then [examples.md](examples.md).

### When to load supporting files (progressive disclosure)

- **[examples.md](examples.md):** Load for **local application code**—after the database is up (container healthy or path 2 with an existing server). Use for SDK snippets, put/get patterns, and language-specific examples. Not a substitute for the Docker and critical rules in this file when you are still bringing the server online.
- **[reference.md](reference.md):** Load when the task involves **Docker Compose**, **custom namespaces or persistence**, **Enterprise image or authentication**, **extended troubleshooting**, or **production- or cluster-oriented** setup. **Not** required for the default single-container Community path in this skill (Skill.md + `docker run` only).

### 1. Critical rules (anti-hallucination)

- **Docker image:** Default to `aerospike/aerospike-server` (Community Edition). Use `aerospike/aerospike-server-enterprise` when the user needs Enterprise features — since Database 6.1.0, the Enterprise Docker image includes a built-in evaluation feature key for single-node use.
- **Ports:** Always map the core service ports: `-p 3000-3002:3000-3002`. Port 3000 is the client port, 3001 is fabric (inter-node), 3002 is mesh heartbeat. Port **3003:** on Database **8.1.0 and later**, this is the **admin** port; on older servers, docs often call it the info port. Add `-p 3003:3003` when the user needs admin or legacy info access. Do not confuse these ports with HTTP or generic app ports like 8080.
- **Default namespace:** The default namespace is `test`. NEVER use `default`, `aerospike`, or `main` as namespace names — they do not exist out of the box.
- **Default set:** Sets are created dynamically on first write. No pre-creation needed.
- **Connection defaults:** Host `127.0.0.1`, port `3000` for local Docker deployments.
- **Config file path:** Inside the container, the config lives at `/etc/aerospike/aerospike.conf`. When mounting a custom config, mount to `/opt/aerospike/etc/aerospike.conf` and pass `--config-file /opt/aerospike/etc/aerospike.conf`.
- **TTL requires `nsup-period`:** By default, namespaces reject writes with a TTL, and NSUP does not run, but this behavior is configurable. `nsup-period` controls how often NSUP runs, and the default value `0` means NSUP does not run. If the user wants expiring records, configure `nsup-period` to a value greater than `0` (for example `nsup-period 10`) so NSUP runs and checks for expired records. When `nsup-period` is `0`, writes with a positive integer TTL require `allow-ttl-without-nsup true`, which Aerospike documents as a testing-only setting.
- **Key storage policy:** The Aerospike client docs describe the send-key policy this way: it stores the user defined key with the record, and returns it with read commands. The default Node.js key read policy is `Aerospike.policy.key.DIGEST`. If the user needs the user defined key returned with reads, set the write policy to send/store the key when writing records (for example, `key: Aerospike.policy.key.SEND` in Node.js, `key: aerospike.POLICY_KEY_SEND` in Python, or `policy.SendKey = true` in Go).
- **No auth by default:** Community Edition has no authentication. Do not generate username/password connection code unless the user is on Enterprise Edition.
- **Data model terminology:** Aerospike uses "namespace" (like a database), "set" (like a table), "record" (like a row), "bin" (like a column). Never use incorrect analogies.

### 2. Hallucination blacklist (never use these)

These are commonly hallucinated. Check generated code against this list:

- **Wrong:** `aerospike/aerospike-server-enterprise` when the user only needs Community features — **Use:** `aerospike/aerospike-server` for Community; Enterprise includes a built-in evaluation key but is a larger image.
- **Wrong:** Namespace `default` or `aerospike` — **Use:** `test`.
- **Wrong:** Port `8080` for Aerospike — **Use:** `3000-3002` for client/fabric/heartbeat; `3003` for admin (Database 8.1.0+, often described as info on older versions).
- **Wrong:** `client.connect()` as a required separate call in Python — `aerospike.client(config)` connects on instantiation. `.connect()` exists but is a no-op on a fresh client; it is only needed to reconnect after `client.close()`.
- **Wrong:** `aerospike.Client()` or `aerospike.client.Client()` in Python — **Use:** the factory function `aerospike.client({...})`.
- **Wrong:** `require('aerospike-client')` in Node.js — **Use:** `require('aerospike')`.
- **Wrong:** Setting a positive integer TTL while `nsup-period` is `0`, unless `allow-ttl-without-nsup` is explicitly enabled for testing.
- **Wrong:** Any REST API endpoints — Aerospike uses a binary wire protocol via client SDKs, not HTTP.
- **Wrong:** `CREATE NAMESPACE` or `CREATE SET` SQL-like commands — namespaces are defined in config; sets are auto-created.

### 3. Concept mapping

Translate user intent to the correct approach:

- "real-time database" / "low-latency store" / "fast database" → Docker quick setup with in-memory storage
- "cache replacement" / "replace Redis" / "replace Memcached" → In-memory namespace, emphasize sub-ms latency and clustering
- "persistent storage" / "durable database" → File-backed or device-backed namespace config (see [reference.md](reference.md))
- "production deployment" / "cloud deployment" → Official docs only; use [Choose a path first](#choose-a-path-first) path 1
- "time-series" / "TTL" / "expiring data" → `default-ttl` namespace config and per-record TTL in write policy
- "transactions" / "ACID" → Strong consistency mode (Enterprise feature) or record-level atomicity (Community)

### 4. Autonomous first-run steps

Follow these steps in order for **full local setup**. Do not ask the user for confirmation between steps unless something fails.

**Step 1: Verify Docker**

```bash
docker --version
```

If Docker is not available, tell the user to install Docker Desktop and stop.

**Step 2: Start Aerospike**

```bash
cat > /tmp/aerospike.conf << 'ASCONF'
service {
    proto-fd-max 15000
    cluster-name docker
}

logging {
    console {
        context any info
    }
}

network {
    service {
        address any
        port 3000
    }
    heartbeat {
        mode mesh
        port 3002
    }
    fabric {
        port 3001
    }
}

namespace test {
    replication-factor 1
    default-ttl 0
    nsup-period 10
    storage-engine memory {
        data-size 1G
    }
}
ASCONF

docker run -d --name aerospike \
  -p 3000-3002:3000-3002 \
  -v /tmp/aerospike.conf:/opt/aerospike/etc/aerospike.conf \
  aerospike/aerospike-server:latest \
  --config-file /opt/aerospike/etc/aerospike.conf
```

This custom config sets `cluster-name`, which is mandatory in Database 7.0.0 and later, and sets `nsup-period 10` so NSUP runs for the namespace instead of remaining disabled at the default `0`. For custom namespaces, Compose, and Enterprise images, see [reference.md](reference.md).

If a container named `aerospike` already exists, check if it is running:

```bash
docker ps -a --filter name=aerospike --format '{{.Status}}'
```

If stopped, start it with `docker start aerospike`. If it needs to be recreated, remove it first with `docker rm -f aerospike`.

**Step 3: Verify the database**

Wait 3 seconds for startup, then check:

```bash
docker logs aerospike 2>&1 | tail -5
```

Look for `service ready: soon there will be cake!` in the logs to confirm successful startup.

**Step 4: Detect language and install SDK**

Inspect the user's project to determine the language, then install the appropriate client:

| Language | Install command | Package |
|----------|----------------|---------|
| Python | `pip install aerospike` | [aerospike](https://pypi.org/project/aerospike/) |
| Node.js | `npm install aerospike` | [aerospike](https://www.npmjs.com/package/aerospike) |
| Go | `go get github.com/aerospike/aerospike-client-go/v8` | [aerospike-client-go](https://github.com/aerospike/aerospike-client-go) — check repo tags for current major version (`v8`, `v9`, etc.) |
| Java | See [examples.md](examples.md) | [aerospike-client-jdk21](https://central.sonatype.com/artifact/com.aerospike/aerospike-client-jdk21) |
| C# | `dotnet add package Aerospike.Client` | [Aerospike.Client](https://www.nuget.org/packages/Aerospike.Client) |

**Version pinning:** Always check the linked package registry for the latest stable version before installing. The install commands above omit version numbers intentionally — use the latest unless the user's project constrains it.

**Step 5: Generate application code**

Use the appropriate example in [examples.md](examples.md). Adapt the namespace, set name, and key/bin names to fit the user's domain.

**Step 6: Verify with a write-read test**

Run the generated code. Confirm the output shows a successful write followed by a successful read of the same data.

### 5. Further reading

- **SDK examples and Node batching:** [examples.md](examples.md)
- **Custom config, Compose, Enterprise, troubleshooting:** [reference.md](reference.md)

## Documentation links

- **Quick Start:** https://aerospike.com/docs/database/quick-start
- **Configuration Reference:** https://aerospike.com/docs/database/reference/config
- **Namespace Management:** https://aerospike.com/docs/database/manage/namespace
- **Client Libraries:** https://aerospike.com/docs/develop/client
  - [Python](https://aerospike.com/docs/develop/client/python)
  - [Node.js](https://aerospike.com/docs/develop/client/node)
  - [Go](https://aerospike.com/docs/develop/client/go)
  - [Java](https://aerospike.com/docs/develop/client/java)
  - [C#](https://aerospike.com/docs/develop/client/csharp)
- **Secondary index queries:** https://aerospike.com/docs/develop/learn/queries/secondary-index/
- **Docker Install:** https://aerospike.com/docs/database/install/docker
- **AeroLab (Dev Clusters):** https://github.com/aerospike/aerolab
- **Community Forum:** https://discuss.aerospike.com

## Repository layout

Repo index for humans lives at the **repository root** (`README.md`), outside this skill folder—agent tools load only files under this directory.
