_Auto-generated from `skills/aerospike-getting-started`, `skills/aerospike-development`, `skills/aerospike-data-modeling`. Edit the skills under `skills/`, not this file._

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
- query- -> Secondary indexes and query-oriented modeling
- batch- -> Many primary-key reads/writes; one key per batch entry, coalesce, batch operate
- binop- -> operate, one record lock, mixed read/write, atomic multi-bin updates
- single- -> Whole-record vs partial/bin operations; TTL void-time and NSUP/default-ttl; delete and durable deletes (EE)
- model- -> Keys, denormalization, access paths, record size vs index RAM and disk, hot keys and error 14 / KEY_BUSY
- sec- -> TLS and access control on the client

### Use batch APIs for many primary-key operations [MEDIUM]
- When reading or writing many records by known primary keys, use the client’s batch APIs instead of serial single-key calls, subject to reasonable batch sizes and error-handling needs.
- Prefer: Chunked batches if the SDK or service limits batch size; One entry per key per batch; merge or drop duplicates on the client before batch_*; Batch operate (or equivalent) when one key needs multiple operations atomically in the batch; After each batch: walk every entry’s result code or exception slot—partial success is normal for batch APIs; Retrying or compensating only for keys that actually failed (once you have per-key status)
- Avoid: Thousands of sequential gets when a batch interface exists; Duplicate keys in the same batch when you can coalesce or combine into operate—especially on keys that are already hot or latency-sensitive; Assuming no exception or overall OK means every key in the batch succeeded

### Use operate for multi-bin atomic updates on one key [HIGH]
- When a single logical update touches multiple bins or uses CDT ops on one record, use operate (multi-operation) so the server applies the sequence atomically for that record, rather than separate put/get cycles that can interleave with other writers.
- Prefer: One operate call combining the bin ops you need; Generations when you need compare-and-swap across clients
- Avoid: Multiple independent puts racing without coordination; Mixing a whole-record read with bin-scoped ops in one operate (use per-bin reads only; see binop-operate-record-lock-read-write.md)

### Use operate for one record lock, many ops, and mixed reads and writes [HIGH]
- Use the operate command when you need multiple bin-level changes on the same record key in one server round trip. The server acquires a record lock, runs an ordered list of bin operations atomically and in isolation against an in-memory copy of the record, then persists if any write occurred. Mix read and write operations in the same operate call when you need updated values back without a separate get: later operations see the effects of earlier ones in the list (including writes before reads). This cuts client/server chatter, reduces lock hold time versus separate get/put sequences from the app, and improves throughput and tail latency for hot keys compared to naïve multi-call patterns.
- Prefer: One operate with all bin ops (scalar, CDT, expressions as supported) for that unit of work; Mixed read+write lists when the response must reflect post-write state (e.g. increment then read counter); Filter expressions on operate when the doc pattern fits conditional updates
- Avoid: Chaining separate get → app logic → put when operate can express the same work on one key; Splitting independent bin updates on the same key into multiple commands without a concurrency story

### Keep lists and maps bounded [HIGH]
- Never grow lists or maps without bounds. Records have a maximum size; unbounded appends cause failures and hot records. Use trims, capped policies, rank/size-limited reads, or partition data across keys.
- Prefer: Server-side ops that trim or cap (where your model allows); Separate keys or sets when history must be long-lived at scale
- Avoid: Unbounded append to lists in hot paths

### Model nested lists and maps with CDT context, ordering, and expressions [HIGH]
- When you store lists of maps, maps of lists, or deeper nesting, use the official patterns in Working with nested collection data types: CDT operate APIs with context where you address a single slot, expression composition (ListExp / MapExp) for filters and computed reads, and path expressions (selectByPath / modifyByPath) when you traverse or change multiple nested elements in one shot. Path expressions require Aerospike Database 8.1.2 or later; use a client version that supports them (feature compatibility matrix). Build K-ordered maps (or the client equivalent) when the server must compare whole map values—for example ADD_UNIQUE on a list of vehicle maps—so wire representation matches and duplicate detection works.
- Prefer: One operate call with ListOperation / MapOperation and explicit list/map policies; Sorted maps and ordered unique lists where semantics allow—better CDT performance; see cdt-server-side-ops.md; Language-specific ordered map types when the docs require them (TreeMap, KeyOrderedDict, sorted MapPair slices in Go, etc.); The nesting guide’s full page for read/filter/index/query examples beyond a single insert
- Avoid: Path expression APIs on clusters below 8.1.2 (use context + ListOperation / MapOperation / composed expressions instead); Treating nested bins like JSON blobs updated only via full-record get/put under contention; Relying on duplicate suppression for list-of-maps if maps are not built in the ordered form the server compares

### Prefer server-side CDT operations over read-modify-write [HIGH]
- For updates to lists, maps, or nested documents modeled in CDTs, use operate with CDT operations so work runs atomically on the server. Avoid get → mutate in app → put for contended data.
- Prefer: Sorted maps by default unless the domain truly needs unsorted or arbitrary key order; Ordered list + unique-list semantics when you need uniqueness and can assign index meaning (see list ordering options); ListOperation / MapOperation (or equivalent) via operate, with list/map policy and write flags chosen deliberately; Generations when you truly need cross-bin transactional semantics in the client
- Avoid: Fetching entire large collections to append one element; Unordered map or unordered unique-list policies when sorted / ordered would match the model and improve performance

### Reach every cluster node directly (no proxy in the data path) [HIGH]
- The Aerospike client must have direct network reachability to every node in the cluster (not only to seed hosts). It automatically maintains the current node list (via seeds and ongoing tending) and works against the full cluster—partitioning, replica placement, and migrations direct traffic to the right nodes. Using a single seed for bootstrap does not limit the client to that node; in a cluster, work is not confined to the seed you picked.
- Prefer: Firewall and routing that allow the app tier to reach each node’s client-facing service port; Server network settings so advertised addresses match how clients actually reach the nodes; Multiple seed hosts for bootstrap resilience (still not a substitute for reaching all nodes)
- Avoid: Assuming traffic stays on the seed you configured—operations run across all nodes the client knows about; Treating the seed list as the only hosts that must be reachable; Inserting a proxy or LB between clients and nodes for normal database traffic; Assuming localhost or internal-only IPs work from a different network without access / alternate address configuration

### Use client error-rate backoff to protect the cluster under failure storms [MEDIUM]
- Many Aerospike clients support client-side error-rate limiting (sometimes described as backoff): if a node returns too many errors within a sliding window of client tend iterations, the client stops sending new commands to that node until the error rate drops—surfacing a backoff-style exception to the application instead of hammering a sick node.
- Prefer: Enabling error-rate backoff for large or autoscaled app tiers sharing one cluster; Pairing backoff awareness with metrics and alerts on the thrown exception class
- Avoid: Assuming every SDK exposes identical field names—read your client’s policy docs; Treating backoff as a substitute for fixing root cause (network, capacity, config)

### Size connection pools and warm up on startup [MEDIUM]
- Configure minimum and maximum connections per node (SDK-specific names such as minConnsPerNode / maxConnsPerNode) for your workload. maxConnsPerNode caps concurrent synchronous connections to each cluster node from this client instance. When the pool is exhausted, further requests can fail with a “no more connections”–class error (exact code varies by SDK) rather than blocking forever—size max for peak concurrency per node, or scale out clients.
- Prefer: Sizing maxConnsPerNode and client instance count so (instances × maxConnsPerNode) stays within proto-fd-max (and ops guidance) with margin for non-app traffic; Pool sizing from measured concurrency per node and observed errors; Warmup after client construction when tail latency after deploy matters; minConnsPerNode when workloads have idle gaps then bursts—but not so high that startup or reconnect storms overload server CPU (monitor with TLS especially)
- Avoid: Default pool sizes for high-QPS services without measurement; maxConnsPerNode so low that normal bursts hit connection exhaustion; Scaling out many client replicas each with a high maxConnsPerNode without checking per-node proto-fd-max and total concurrent clients; Very high minConnsPerNode combined with mass simultaneous client restarts or network flaps—expect CPU pressure on nodes when connections are re-established (TLS amplifies)

### Use one Aerospike client per process [HIGH]
- Instantiate the Aerospike client once per application process (or equivalent isolation boundary) and share it across threads/workers. Do not create and destroy a client per request.
- Prefer: A single global/module-level client initialized at startup; Graceful close only on shutdown; Explicit client logging in non-trivial deployments
- Avoid: new client / connect / close inside per-request handlers

### Use filter and operation expressions for compute-to-data [HIGH]
- Use filter expressions and operation expressions (and path expressions for nested bins) to evaluate and update data on the server when they fit the problem. Reach for Lua UDFs only when expressions cannot express the logic or product guidance requires server-side procedures.
- Prefer: Predicates and updates expressible as expressions; Path expressions for nested map/list updates where supported
- Avoid: UDF for arithmetic or filters that expressions cover

### Model for primary-key access paths and denormalize deliberately [HIGH]
- Design schemas around how data is read and written: namespace, set, and user key should make the common path a single primary-key operation. There are no server-side joins—duplicate or embed via bins and CDTs when that matches query needs.
- Prefer: Access-pattern-first key design; CDTs for embedded aggregates when reads are colocated by key
- Avoid: Join-shaped APIs in application code mirroring SQL without redesign

### Design and mitigate hot keys (error 14 / KEY_BUSY) [HIGH]
- When many clients hit the same primary key at once, that record becomes a hot key: work serializes on the server and you can see high latency, timeouts, or failures such as error code 14 / KEY_BUSY (exact name depends on the client—see the support article and your SDK). That usually means too much load on one key, not a random cluster bug.
- Prefer: Spreading work across more keys when the product allows—shard counters or aggregates instead of a single global row everyone updates; One operate (or one batch entry) per key when a key needs several changes—see batch-parallel-key-operations.md and binop-operate-record-lock-read-write.md; Read policies that spread read load when slightly stale data is OK—policy-read-replica-consistency.md (MASTER_PROLES, etc.); Server-side namespace tuning such as read-page-cache so the OS page cache can absorb repeated reads of the same device blocks—can ease read-heavy hot keys when storage layout fits; see model-record-size-hardware-efficiency.md and the read-page-cache reference (not a substitute for sharding hot keys in the app); Backoff with jitter on transient errors instead of tight spin loops
- Avoid: A single key as the only place for high-QPS writes (global sequence, one shared counter with no sharding); Blind retries without backoff when you see hot-key / busy errors

### Size records for primary-index overhead and disk bandwidth [HIGH]
- In hybrid memory architecture (HMA) and All Flash deployments, record data lives on device and reads generally come from the storage path—plan I/O accordingly. Aerospike does not keep an application-style DRAM cache of arbitrary records keyed by digest, so you cannot assume a hot record is free to re-read.
- Prefer: Single-digit KiB for the bulk of records, with 1–128 KiB as the band that distribution spans; treat anything over ~50 KiB as a decision to justify rather than a default; Splitting or denormalizing huge documents across keys when hot paths only need part of the data; Capacity planning that includes index RAM (records × replicas × ~64 B) and device throughput for object size × QPS; Storage compression (LZ4 or zstd; zstd usually the better ratio-to-CPU trade) when records are large. Smaller on-disk records cut bytes read and written per operation directly, fit more records per write block (better defrag efficiency), and stretch both the post-write cache and page cache further; Coordinating with operations on post-write-cache sizing and read-page-cache when read-heavy access to the same blocks dominates latency (after confirming namespace layout and the constraints above)
- Avoid: Carrying sizing intuition from other databases: B-tree and document stores apply an incremental update without rewriting the whole object, and in-memory stores have no device I/O to amortize. Neither holds in Aerospike—every update rewrites the full record contiguously; Assuming a tiny bin payload is “free” on the server—it still pays index + full storage I/O on access; Expecting read-page-cache to fix application-level hot keys by itself—shard or spread keys where needed first; Megabyte-scale records on hot keys without measuring disk and replication cost

### Set client-level policy defaults per operation type [MEDIUM]
- Aerospike clients let you attach default policies to the client object so API calls that pass null (or use implicit defaults) still get predictable timeouts, retries, and behavior. Defaults are usually per operation family: for example separate defaults for single-record read, single-record write, scan, query, and batch—confirm structure in your SDK.
- Prefer: Explicit client-level defaults at startup for each operation class you rely on; Copy-from-default then mutate patterns when overriding one field for a call (per SDK); Verifying batch default coverage for read vs write vs delete vs UDF if you use those APIs
- Avoid: Relying on “global” policy defaults without checking scan vs get vs batch behavior; Assuming all batch sub-policies inherit the same base—check the docs

### Use generation policy only for CAS (optimistic concurrency) [HIGH]
- WritePolicy.generationPolicy is for CAS: read → edit on the client → write that must fail if the record changed meanwhile. You must use EXPECT_GEN_EQUAL / EXPECT_GEN_GT (names vary by SDK) and pass the generation from the read on the write. NONE skips the check—typical writes that are not read–modify–verify do not need this.
- Prefer: EXPECT_GEN_* and the generation field from the read for client-side read–modify–write under contention (or use atomic operate / server-side updates when they cover the whole change); Retry after AS_ERR_GENERATION by repeating read → manipulate → write from scratch (not only re-issuing the write)
- Avoid: Generation policy without supplying the read generation on the write; CAS that assumes read-touch always bumps generation; Treating generation as a change counter (only same-read equality for CAS is valid); Blind retries of non-idempotent writes (policy-reuse-timeouts-retries.md); Retrying only the write after AS_ERR_GENERATION while reusing the same client-side edit computed from a stale read

### Set read replica, AP read mode, and SC read mode to match namespace semantics [HIGH]
- Configure Policy.replica, readModeAP (AP namespaces), and readModeSC (strong-consistency namespaces) so reads see the staleness and ordering guarantees your application needs. Defaults are not universally safe under migration or for hot keys—override deliberately.
- Prefer: MASTER or defaults when you need the simplest “read what the master has” mental model in AP; MASTER_PROLES when read scaling on a hot key is worth distributing across master and replicas (and semantics allow); ALL in AP when stale reads during migration are unacceptable and cost is acceptable; Aligning client policy with namespace mode (AP vs SC) and validating with Strong consistency docs when in doubt
- Avoid: RANDOM unless replication factor matches cluster topology as the doc recommends; Assuming ONE is always fresh while partitions are migrating

### Use replace semantics when overwriting an entire record [MEDIUM]
- Match recordExistsAction (or the SDK’s WritePolicy equivalent) to the real operation. When the application replaces all bins for a record (full overwrite), prefer REPLACE or REPLACE_ONLY so unspecified bins are removed; use UPDATE / UPDATE_ONLY / CREATE_ONLY when merge or insert-only semantics are intended.
- Prefer: CREATE_ONLY — insert; fail if the record exists; UPDATE_ONLY — update; fail if missing; merges bins into existing; UPDATE (common default) — upsert; merges bins if record exists; REPLACE — create or replace whole record; drops bins not in this write; REPLACE_ONLY — replace; fail if missing; drops bins not in this write; Generation-guarded updates when you need CAS (see policy-generation-cas.md)
- Avoid: Default write modes chosen without matching access pattern; Using UPDATE when you meant a full bin set replacement (use REPLACE)

### Reuse policies and set explicit timeouts and retries [HIGH]
- Reuse read/write/operate policy objects (or set defaults on the client) instead of allocating new policy instances on hot paths. Configure socket timeout, total timeout, and retry behavior appropriate to the operation class (single-key vs batch vs query).
- Prefer: Client-level or module-level default policies; Explicit timeouts for batch and query workloads; maxRetries 0 on write policies for non-idempotent operations; Understanding totalTimeout 0 vs server default before tuning latency; Knowing read vs write default retries when debugging duplicate or missing effects
- Avoid: Relying on implicit defaults for long-running operations; New policy objects inside tight loops; Retrying writes that are not safe to repeat without idempotency guarantees; Expecting sleepBetweenRetries to run on every socket-idle timeout (see Policies semantics)

### Understand sendKey when the stored user key matters [MEDIUM]
- Policy.sendKey controls whether the client sends the user-defined key alongside the digest on reads and writes. If enabled on a write, the key is stored with the record and can be returned on reads and secondary-index queries that surface keys. Once stored, it persists until the record is deleted—even if later writes omit sendKey—unless your application replaces behavior per doc.
- Prefer: Enabling sendKey when queries or clients must recover the original key field; Consistent policy for creates vs updates if your access pattern assumes the key is present
- Avoid: Assuming the key is stored without sendKey on the write path that created the record; Relying on sendKey toggles to “remove” a stored key without understanding persistence semantics

### Choose write commit level deliberately (COMMIT_ALL vs COMMIT_MASTER) [HIGH]
- WritePolicy.commitLevel controls when the client gets success after a write:
- Prefer: COMMIT_ALL for SC namespaces and when you need the write durable on replicas before the client proceeds; COMMIT_MASTER in AP only when replica lag or stale replica reads are acceptable
- Avoid: COMMIT_MASTER in SC namespaces (invalid); COMMIT_MASTER in AP when the app cannot tolerate lag or stale replica reads; COMMIT_MASTER in AP at extreme sustained write rates without headroom—watch for network saturation

### Design secondary indexes for query paths—not for every column [HIGH]
- Use secondary indexes for predicates that match a planned query path at sensible cardinality. Do not index high-cardinality values (for example unique UUIDs per row) as a substitute for a primary key redesign. Prefer primary-key access when the key is known.
- Prefer: Modeling that answers “how do I look this up?” with PK when possible; Indexes on fields that partition the key space usefully for queries
- Avoid: “Index everything” patterns carried over from relational databases

### Terminate TLS and apply access credentials in the client [MEDIUM]
- When the cluster requires TLS or access control, configure the client with the correct TLS context and credentials per official security guides—not custom shortcuts. Treat credentials as secrets; never embed them in repos.
- Prefer: Follow the security docs for your client version; Separate configs per environment
- Avoid: Disabling verification or using shared prod keys in dev without understanding risk

### Use delete/remove correctly and opt into durable deletes when the app requires them [HIGH]
- Use the client’s single-record delete API (delete / remove per SDK) to remove a record by primary key, as described under Delete a record. When deletes must stay deleted across cold starts and older on-disk versions must not resurrect, enable the durable delete flag on the write policy for that delete (and for any write or operate that removes the last bin and therefore deletes the record). Durable deletes are an Enterprise Edition capability: they generate a tombstone so conflict resolution and cold-start index rebuild behave correctly. The default client behavior keeps durable delete off for backward compatibility—turn it on explicitly where your correctness requirements need it.
- Prefer: Plain delete when resurrection on cold start is acceptable for the workload; durableDelete / durable_delete (or equivalent) on the delete policy when you need tombstone semantics and run Enterprise; Verifying server edition and namespace policy before relying on durable deletes in production
- Avoid: Assuming delete always creates a tombstone (it does only when durable delete is used appropriately on supported calls); Sending durable-delete policies to Community Edition servers (see compatibility in the architecture doc); Treating SC expunge semantics like AP without checking strong-consistency-allow-expunge and ops guidance

### Know single-record CRUD vs bin-level operations [MEDIUM]
- Distinguish whole-record put/get/delete from bin operations and operate. Choose the narrowest API that matches the access pattern to limit data movement and clarify semantics.
- Prefer: get/put when the unit of work is the full record; operate with bin ops when updating parts of a record or using CDTs; Smaller records when the workload issues many touch / TTL / single-bin updates—large blobs amplify hidden full-record I/O
- Avoid: Habitual full-record reads for small field changes; Assuming a bin-level or TTL-only API guarantees partial storage writes—it usually does not at the record level

### Do not shorten void-time carelessly—cold restart and retention semantics [HIGH]
- Do not reduce a record’s remaining lifetime (void-time) on writes unless you intend it and accept cold-start risk. Extending void-time (later expiration, longer remaining TTL) is fine and does not cause the resurrection mismatch described below—the failure mode is shortening relative to older versions still on disk. To change bins only while keeping void-time, use -2 on updates (see single-ttl-nsup-default-ttl.md for 0 / -1 / -2 and NSUP).
- Prefer: Preserve void-time on updates unless shortening expiration is deliberate; clear create vs update policy; Decide finite TTL vs never-expire per record and avoid flipping never-expire back to finite TTL except rare, deliberate migrations; Delete for intentional removal; TTL for natural retention horizons
- Avoid: Re-enabling expiration on a never-expire record with a new positive TTL except deliberate, well-understood migrations; Using short TTL instead of delete when you mean removal; Routinely smaller TTL on every update to “refresh” without understanding void-time; Expecting eviction to trim never-expire records; Assuming expiration removed all on-disk history (vs durable delete semantics)

### Align client TTL with NSUP, default-ttl, and special write TTL values [HIGH]
- Namespace Supervisor (NSUP) must be configured consistently with how the app sends TTL on writes. When NSUP is enabled and the namespace allows TTL-backed writes, a write or Touch (or equivalent) that uses client TTL 0 tells the server to set void-time from default-ttl, with set-level default-ttl overriding namespace when both exist. Each such call can re-apply that horizon to the record; to change bins only without resetting void-time, use -2 or an explicit TTL. Reads that extend TTL via read-touch use default-read-touch-ttl-pct and client read policies—that is separate from default-ttl on writes.
- Prefer: nsup-period > 0 when using positive integer TTLs on writes, unless operations explicitly align with the doc’s exceptions; Knowing whether every write with TTL 0 re-bases the record to default-ttl (set vs namespace) before relying on “refresh” behavior; Checking nsup-period when you see error 22 on TTL writes before blaming application logic; Using -2 on updates when only bin data should change and void-time must stay as-is
- Avoid: Assuming unspecified client TTL behaves the same across SDKs—confirm whether the default maps to 0 (server default-ttl) or something else; Conflating read-touch TTL extension with default-ttl on writes; Using allow-ttl-without-nsup outside the doc’s intended testing-only scope

## aerospike-data-modeling


### Fetch the data modeling guide before designing a full model [HIGH]
- This skill carries the decision layer. The full design-time process lives in the
- Prefer: Reading current values (version minimums, size limits, complexity) from the guide rather than recalling them; Naming the specific guide file you used, so a reviewer can retrace the decision
- Avoid: Presenting a model as complete when the guide's checklist and sizing worksheets were never applied; Quoting a version gate or size limit from memory

### Produce a schema guide and a derived schema summary [MEDIUM]
- Design work produces two documents, written to files. Know which one you are writing at any moment, and never author the second independently of the first.
- Prefer: Writing both to files, not pasting a schema into chat; Building the guide incrementally, one entity group at a time, and generating the summary only once every group is done; Regenerating the summary from the guide whenever the model changes; Stating explicitly, in the guide, which decisions were assumptions rather than confirmed inputs
- Avoid: Editing the schema summary directly when the model changes — update the guide, regenerate the summary; Omitting the assumptions log because the model "seems obvious"; Treating a chat-delivered schema as a deliverable

### Work the design-time loop one entity group at a time [HIGH]
- Data model design is an interactive process with mandatory stop points, not a document you fill in. Produce a written clarification document first, partition the domain into entity groups, then design each group and pass its review before starting the next.
- Prefer: A written clarification document as the first artifact, before any schema; Requirements-gap questions ("what is the p95 fan-out?") over mechanism-preference questions ("which pattern do you prefer?"); The baseline shape by default — introduce a new set, split record, extra index, or materialized view only when a requirement cannot be met otherwise, or measurement shows the baseline misses an SLO; Explicit assumptions with reconsider triggers when an input cannot be obtained; A developer walkthrough per group: trace a create-and-read flow, a multi-record mutation, and a cleanup/cascade through the drafted schema
- Avoid: Producing a complete schema for every entity group with no clarifying question asked and no checkpoint held; Pre-filling pattern choices into the entity-group plan — those are outputs of per-group design, not routing decisions; Treating "we discussed the data model" as equivalent to having a schema guide

### Run the seven failure-mode detection tests against a drafted model [HIGH]
- Each failure mode below has a detection test — something you can run against a draft and get a yes/no answer. Use them twice: as priming before designing, and as a review rubric against a drafted schema. These are not LLM-specific; they are relational and document-database habits applied to an architecture that rewards neither.
- Prefer: Running all seven against the drafted schema before the stakeholder review; Treating an unanswerable growth question as a blocker, not a footnote
- Avoid: Running these only at the end — most are cheaper to fix during design than after
