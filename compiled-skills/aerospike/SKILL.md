---
name: aerospike
description: Work with the Aerospike core database end to end — run a local instance with Docker and verify a first write and read, build or review client code with the official SDKs (Python, Node.js, Go, Java, C#), and design or review a data model, whether from requirements or against a schema that already exists. Covers namespaces, sets, bins, primary key design, TTL and NSUP, collection data types, expressions, secondary indexes, batch and scan workflows, client policies, connection pooling, record sizing, and schema deliverables. Use when the user sets up Aerospike, writes or debugs Aerospike client code, chooses keys or models data for it, reviews an Aerospike schema before building, or evaluates it as a persistent replacement for Redis or Memcached in real-time, low-latency, feature-store, or user-profile workloads. Core database only — not Aerospike Graph, and not cluster operations, sizing, XDR, or backup and restore, which belong to Aerospike Operations documentation.
license: Apache-2.0
metadata:
  last_verified: "2026-04-21"
  server_versions: "7.0+"
---

_Auto-generated from `skills/aerospike-getting-started`, `skills/aerospike-development`, `skills/aerospike-data-modeling` in https://github.com/aerospike/agent-skills. Edit the skills under `skills/`, not this file._

**Reading a rule in full.** Rules are grouped under a `###` heading naming their filename prefix (`client-`, `policy-`, …), explained in the skill's own prefix table. Each rule is a `####` heading of the form `<rule> — <title> [IMPACT]`. Each states its instruction and nothing more — the reasoning, the worked detail and the documentation links live in its own file, shipped in the `references/` folder beside this one. That file is `references/<skill>-<rule>.md`, where `<skill>` is the `##` heading the rule sits under: `client-singleton` under `aerospike-development` is `references/aerospike-development-client-singleton.md`. Rules cite each other by bare filename and resolve the same way. Worked examples named under `Worked examples` live in `examples/<skill>-<name>.md`, the same naming one folder over._

# Aerospike agent rules


## aerospike-getting-started


### 1. Critical rules (anti-hallucination)
- Docker image: Default to aerospike/aerospike-server (Community Edition). Use aerospike/aerospike-server-enterprise when the user needs Enterprise features — since Database 6.1.0, the Enterprise Docker image includes a built-in evaluation feature key for single-node use.
- Ports: Always map the core service ports: -p 3000-3002:3000-3002. Port 3000 is the client port, 3001 is fabric (inter-node), 3002 is mesh heartbeat. Port 3003: on Database 8.1.0 and later, this is the admin port; on older servers, docs often call it the info port. Add -p 3003:3003 when the user needs admin or legacy info access. Do not confuse these ports with HTTP or generic app ports like 8080.
- Default namespace: The default namespace is test. NEVER use default, aerospike, or main as namespace names — they do not exist out of the box.
- Default set: Sets are created dynamically on first write. No pre-creation needed.
- Connection defaults: Host 127.0.0.1, port 3000 for local Docker deployments.
- Config file path: Inside the container, the config lives at /etc/aerospike/aerospike.conf. When mounting a custom config, mount to /opt/aerospike/etc/aerospike.conf and pass --config-file /opt/aerospike/etc/aerospike.conf.
- TTL requires nsup-period: By default, namespaces reject writes with a TTL, and NSUP does not run, but this behavior is configurable. nsup-period controls how often NSUP runs, and the default value 0 means NSUP does not run. If the user wants expiring records, configure nsup-period to a value greater than 0 (for example nsup-period 10) so NSUP runs and checks for expired records. When nsup-period is 0, writes with a positive integer TTL require allow-ttl-without-nsup true, which Aerospike documents as a testing-only setting.
- Key storage policy: The Aerospike client docs describe the send-key policy this way: it stores the user defined key with the record, and returns it with read commands. The default Node.js key read policy is Aerospike.policy.key.DIGEST. If the user needs the user defined key returned with reads, set the write policy to send/store the key when writing records (for example, key: Aerospike.policy.key.SEND in Node.js, key: aerospike.POLICY_KEY_SEND in Python, or policy.SendKey = true in Go).
- No auth by default: Community Edition has no authentication. Do not generate username/password connection code unless the user is on Enterprise Edition.
- Data model terminology: Aerospike uses "namespace" (like a database), "set" (like a table), "record" (like a row), "bin" (like a column). Never use incorrect analogies.

### 2. Hallucination blacklist (never use these)
- Wrong: aerospike/aerospike-server-enterprise when the user only needs Community features — Use: aerospike/aerospike-server for Community; Enterprise includes a built-in evaluation key but is a larger image.
- Wrong: Namespace default or aerospike — Use: test.
- Wrong: Port 8080 for Aerospike — Use: 3000-3002 for client/fabric/heartbeat; 3003 for admin (Database 8.1.0+, often described as info on older versions).
- Wrong: client.connect() as a required separate call in Python — aerospike.client(config) connects on instantiation. .connect() exists but is a no-op on a fresh client; it is only needed to reconnect after client.close().
- Wrong: aerospike.Client() or aerospike.client.Client() in Python — Use: the factory function aerospike.client({...}).
- Wrong: require('aerospike-client') in Node.js — Use: require('aerospike').
- Wrong: Setting a positive integer TTL while nsup-period is 0, unless allow-ttl-without-nsup is explicitly enabled for testing.
- Wrong: Any REST API endpoints — Aerospike uses a binary wire protocol via client SDKs, not HTTP.
- Wrong: CREATE NAMESPACE or CREATE SET SQL-like commands — namespaces are defined in config; sets are auto-created.

### 3. Concept mapping
- "real-time database" / "low-latency store" / "fast database" → Docker quick setup with in-memory storage
- "cache replacement" / "replace Redis" / "replace Memcached" → In-memory namespace, emphasize sub-ms latency and clustering
- "persistent storage" / "durable database" → File-backed or device-backed namespace config (see reference.md)
- "production deployment" / "cloud deployment" → Official docs only; use Choose a path first path 1
- "time-series" / "TTL" / "expiring data" → default-ttl namespace config and per-record TTL in write policy
- "transactions" / "ACID" → Strong consistency mode (Enterprise feature) or record-level atomicity (Community)

## aerospike-development


### Client best practices (enforce in generated or reviewed code)
- Singleton client: One AerospikeClient (or language equivalent) per process; it is thread-safe and holds pools and cluster state. Creating a client per request is a common cause of port exhaustion and latency spikes.
- Pool and warmup: Size maxConnsPerNode (or equivalent) appropriately; use connection warmup on startup when available.
- Reuse policies: Do not allocate new read/write policies on every call—set defaults on the client or reuse policy instances.
- Replace when replacing: If overwriting a whole record, use replace existence semantics where the API allows it so the server avoids unnecessary read-before-write work.
- Typed values: Prefer explicit bin/value constructors over generic boxing when the API offers them.
- Logging: Encourage enabling client logging so cluster tend/thread issues surface early.
- Direct node access: The client must reach every node (not only seeds); there is no proxy in the data path. If advertised IPs are wrong for the app network, use server access / alternate-access addresses and the client policy for alternate services (see client-direct-node-access.md).
- Client source of truth: Read the chosen client's repository README — its AI coding agent entry point section — before generating code against it, and take the API surface from there rather than from memory (see client-source-of-truth.md).

### Common pitfalls
- Load balancer or proxy only to seeds; app cannot reach all node addresses -> Clients need direct TCP to every node; use access-address / alternate-access-address (and client useServicesAlternate when needed)—not a proxy in the data path; see client-direct-node-access.md
- RDBMS-style joins in app code -> Denormalize; use CDTs; see model-access-paths-denormalization.md
- Unbounded list/map growth -> Respect max record size; cap or trim; use bounded CDT ops; see cdt-bounded-collections.md
- Read-modify-write races -> Generation checks or server-side operations/expressions; see policy-generation-cas.md, expr-compute-to-data.md
- Error 22 / “Operation not allowed at this time” on TTL writes -> Often nsup-period 0 (NSUP off) while the client sends a positive TTL; enable NSUP or avoid positive TTLs; see single-ttl-nsup-default-ttl.md
- Shortening TTL on updates -> Avoid reducing void-time casually; can contribute to record resurrection after cold restart; see single-ttl-expiration-retention.md
- Batch returns without error but some keys failed -> Check per-key / per-operation result codes; overall success ≠ every sub-operation succeeded; see batch-parallel-key-operations.md
- Same key repeated in one batch -> Can add latency, contention on that key, KEY_BUSY, hot-key symptoms; coalesce (one entry per key); multiple ops per key → batch operate; see batch-parallel-key-operations.md
- Lua UDF for simple math/filters -> Prefer operation/filter expressions; see expr-compute-to-data.md

### Rule set
- client- -> Connection lifecycle, pools, warmup, tend, error-rate backoff, direct node reachability
- policy- -> Timeouts/retries, client-level defaults, replica & AP/SC read modes, sendKey, commit level, generation/CAS, replace
- cdt- -> Lists/maps, nesting (K-order, context), growth limits, server-side collection ops
- expr- -> Filter/operation/path expressions vs heavier alternatives
- query- -> Secondary indexes, cardinality/cost, and deriving index needs from access paths
- batch- -> Many primary-key reads/writes; one key per batch entry, coalesce, batch operate
- operate- -> operate: one record lock, mixed read/write, atomic multi-bin updates
- single- -> Whole-record vs partial/bin operations; TTL void-time and NSUP/default-ttl; delete and durable deletes (EE)
- model- -> Namespace and set boundaries; flat bins vs CDTs vs multiple records; keys, denormalization, access paths; operate / batch / expressions; record size vs index RAM and disk; hot keys and error 14 / KEY_BUSY
- sec- -> TLS and access control on the client

### Worked examples
- Runnable code for a task, in `examples/`: batch-official-links, batch-read-by-keys, cdt-list-append, cdt-map-nested-vehicles, client-singleton, operate-mixed-read-write, policy-explicit-defaults, single-put-get

### client-

#### client-direct-node-access — Reach every cluster node directly (no proxy in the data path) [HIGH]
- The Aerospike client must have direct network reachability to every node in the cluster (not only to seed hosts).

#### client-error-rate-backoff — Use client error-rate backoff to protect the cluster under failure storms [MEDIUM]
- Many Aerospike clients support client-side error-rate limiting (sometimes described as backoff): if a node returns too many errors within a sliding window of client tend iterations, the client stops sending new commands to that node until the error rate drops—surfacing a backoff-style exception to the application instead of hammering a sick node.

#### client-pools-warmup — Size connection pools and warm up on startup [MEDIUM]
- Configure minimum and maximum connections per node (SDK-specific names such as minConnsPerNode / maxConnsPerNode) for your workload.

#### client-singleton — Use one Aerospike client per process [HIGH]
- Instantiate the Aerospike client once per application process (or equivalent isolation boundary) and share it across threads/workers.

#### client-source-of-truth — Read the client repository before generating code for it [HIGH]
- Open the chosen client's repository README before writing code against it, and take the API surface from there rather than from memory.

### policy-

#### policy-client-defaults — Set client-level policy defaults per operation type [MEDIUM]
- Aerospike clients let you attach default policies to the client object so API calls that pass null (or use implicit defaults) still get predictable timeouts, retries, and behavior.

#### policy-generation-cas — Use generation policy only for CAS (optimistic concurrency) [HIGH]
- WritePolicy.generationPolicy is for CAS: read → edit on the client → write that must fail if the record changed meanwhile.

#### policy-read-replica-consistency — Set read replica, AP read mode, and SC read mode to match namespace semantics [HIGH]
- Configure Policy.replica, readModeAP (AP namespaces), and readModeSC (strong-consistency namespaces) so reads see the staleness and ordering guarantees your application needs.

#### policy-replace-whole-record — Use replace semantics when overwriting an entire record [MEDIUM]
- Match recordExistsAction (or the SDK’s WritePolicy equivalent) to the real operation.

#### policy-reuse-timeouts-retries — Reuse policies and set explicit timeouts and retries [HIGH]
- Reuse read/write/operate policy objects (or set defaults on the client) instead of allocating new policy instances on hot paths.

#### policy-send-key — Understand sendKey when the stored user key matters [MEDIUM]
- Policy.sendKey controls whether the client sends the user-defined key alongside the digest on reads and writes.

#### policy-write-commit-level — Choose write commit level deliberately (COMMIT_ALL vs COMMIT_MASTER) [HIGH]
- Choose WritePolicy.commitLevel deliberately — it controls when the client gets success after a write, and the two levels differ in durability, not just latency.

### cdt-

#### cdt-bounded-collections — Keep lists and maps bounded [HIGH]
- Never grow lists or maps without bounds.

#### cdt-nested-collections — Model nested lists and maps with CDT context, ordering, and expressions [HIGH]
- When you store lists of maps, maps of lists, or deeper nesting, use the official patterns in Working with nested collection data types: CDT operate APIs with context where you address a single slot, expression composition (ListExp / MapExp) for filters and computed reads, and path expressions (selectByPath / modifyByPath) when you traverse or change multiple nested elements in one shot.

#### cdt-server-side-ops — Prefer server-side CDT operations over read-modify-write [HIGH]
- For updates to lists, maps, or nested documents modeled in CDTs, use operate with CDT operations so work runs atomically on the server.

### expr-

#### expr-compute-to-data — Use filter and operation expressions for compute-to-data [HIGH]
- Use filter expressions and operation expressions (and path expressions for nested bins) to evaluate and update data on the server when they fit the problem.

### query-

#### query-secondary-index-discipline — Design secondary indexes for query paths—not for every column [HIGH]
- Use secondary indexes for predicates that match a planned query path at sensible cardinality.

#### query-sindex-by-access-path — Derive secondary index needs from read and write access paths [HIGH]
- Before adding a secondary index, list access paths (one line each: who reads, predicate, key known or not, latency budget).

### batch-

#### batch-parallel-key-operations — Use batch APIs for many primary-key operations [MEDIUM]
- When reading or writing many records by known primary keys, use the client’s batch APIs instead of serial single-key calls, subject to reasonable batch sizes and error-handling needs.

### operate-

#### operate-atomicity — Use operate for multi-bin atomic updates on one key [HIGH]
- When a single logical update touches multiple bins or uses CDT ops on one record, use operate (multi-operation) so the server applies the sequence atomically for that record, rather than separate put/get cycles that can interleave with other writers.

#### operate-record-lock-read-write — Use operate for one record lock, many ops, and mixed reads and writes [HIGH]
- Use the operate command when you need multiple bin-level changes on the same record key in one server round trip.

### single-

#### single-delete-durable-deletes — Use delete/remove correctly and opt into durable deletes when the app requires them [HIGH]
- Use the client’s single-record delete API (delete / remove per SDK) to remove a record by primary key, as described under Delete a record.

#### single-record-operations — Know single-record CRUD vs bin-level operations [MEDIUM]
- Distinguish whole-record put/get/delete from bin operations and operate.

#### single-ttl-expiration-retention — Do not shorten void-time carelessly—cold restart and retention semantics [HIGH]
- Do not reduce a record’s remaining lifetime (void-time) on writes unless you intend it and accept cold-start risk.

#### single-ttl-nsup-default-ttl — Align client TTL with NSUP, default-ttl, and special write TTL values [HIGH]
- Namespace Supervisor (NSUP) must be configured consistently with how the app sends TTL on writes.

### model-

#### model-access-paths-denormalization — Model for primary-key access paths and denormalize deliberately [HIGH]
- Design schemas around how data is read and written: namespace, set, and user key should make the common path a single primary-key operation.

#### model-bin-cdt-multiple-records — Choose flat bins, nested CDTs, or multiple records for one logical entity [HIGH]
- Flat bins: prefer when fields are read or written together under one primary key, record size stays within bounds, and you do not need deep partial structure.

#### model-client-api-choice — Pick client APIs by key cardinality and work done per request [MEDIUM]
- One key, multiple bins or a record-shaped update: prefer operate (and record lock / mixed R/W semantics) so the server does one round-trip and you avoid get/put races.

#### model-hot-keys — Design and mitigate hot keys (error 14 / KEY_BUSY) [HIGH]
- When many clients hit the same primary key at once, that record becomes a hot key: work serializes on the server and you can see high latency, timeouts, or failures such as error code 14 / KEY_BUSY (exact name depends on the client—see the support article and your SDK).

#### model-namespace-set-boundaries — Draw namespace and set boundaries for retention, security, and operations [HIGH]
- Use one namespace when a single set of cluster-scoped options (replication, strong consistency vs AP mode where applicable, default TTL, NSUP behavior) and one operational “slice” of data fits the workload.

#### model-record-size-hardware-efficiency — Size records for primary-index overhead and disk bandwidth [HIGH]
- In hybrid memory architecture (HMA) and All Flash deployments, record data lives on device and reads generally come from the storage path—plan I/O accordingly.

### sec-

#### sec-client-tls-auth — Terminate TLS and apply access credentials in the client [MEDIUM]
- When the cluster requires TLS or access control, configure the client with the correct TLS context and credentials per official security guides—not custom shortcuts.

## aerospike-data-modeling


### Critical deliverables: schema guide and schema summary
- Design produces two documents, written to files: a schema guide (the full design and its reasoning) and a schema summary (the condensed contract, generated from the guide, never authored independently). Both are required before any code. Contents and the regeneration rule: references/model-deliverables-schema-guide-summary.md.

### Critical rules: the mental model for data architects
- Required reading before designing anything. Aerospike is neither relational nor document: records are semi-structured and are the unit of I/O, there are no server-side joins, every record costs about 64 bytes of index per replica, and access patterns drive the model. The six properties and the record-sizing bounds: references/model-mental-model.md.

### Clarification rules: do not design without clarifying first
- The first deliverable is a written clarification document, not a schema. Ask requirements-gap questions, never mechanism-preference ones; stop rather than assume; record an input you cannot obtain as an explicit assumption with a reconsider trigger; design one entity group at a time and pass its review before the next. The full loop: references/model-design-time-workflow.md.

### Common pitfalls: failure modes to check while drafting
- Seven ways Aerospike models go wrong — record granularity from the entity list, secondary indexes as the primary query path, ignoring CDTs, bins used as columns, normalizing instead of denormalizing, unbounded collection growth, and small entities with no sizing decision. Check them during design, not after. Each with a detection test you can run: references/model-failure-modes-checklist.md.

### Escalation mapping: use the data modeling guide
- New model from scratch (required first read) -> new-app-modeling-checklist.md
- Core concepts, record sizing, indexes, applied patterns -> concepts-and-patterns.md
- 1:N pattern selection -> one-to-many-relationships.md
- A list that grows very large; sharding and overflow -> follow-relationship-scale.md
- List vs map, ordering, persisted indexes -> cdt-api.md
- Server-side filtering, computed bins, expression indexes -> expressions.md
- Nested CDT querying, list-of-structs -> path-expressions.md
- Matching a workload to a known shape and its sizing profile -> workload-archetypes.md
- Reviewing a drafted model -> modeling-failure-modes.md
- Identifier format / timestamp naming -> id-selection-guidance.md, timestamp-bin-naming-guidance.md

### Version-gate rules
- Path expressions — nested CDT filtering and indexing.
- Expression indexes — sparse or computed-value indexing.
- Multi-record transactions — atomic multi-record updates; require a strong-consistency namespace, and carry limits that rule them out for wide cascades. See concepts-and-patterns.md § Multi-record consistency.

### ex-

#### ex-guide-escalation — Fetch the data modeling guide before designing a full model [HIGH]
- This skill carries the decision layer.

### model-

#### model-deliverables-schema-guide-summary — Produce a schema guide and a derived schema summary [MEDIUM]
- Design work produces two documents, written to files.

#### model-design-time-workflow — Work the design-time loop one entity group at a time [HIGH]
- Data model design is an interactive process with mandatory stop points, not a document you fill in.

#### model-failure-modes-checklist — Run the seven failure-mode detection tests against a drafted model [HIGH]
- Each failure mode below has a detection test — something you can run against a draft and get a yes/no answer.

#### model-mental-model — Design from access patterns, not from an entity list [HIGH]
- Derive the model from the read and write paths the application actually runs, never from an entity list or a normalized schema.
