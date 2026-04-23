---
title: Size connection pools and warm up on startup
impact: MEDIUM
tags: client, pooling, warmup, min-conns, tend-interval, proto-fd-max, tls, reconnect
doc: https://www.aerospike.com/docs/develop/client/java/connect/
also:
  - https://aerospike.com/docs/develop/client/java/policies/
  - https://aerospike.com/docs/database/reference/config#service__proto-fd-max
last_verified: 2026-04-21
---

## Size connection pools and warm up on startup

**Rule**

Configure **minimum** and **maximum** connections per node (SDK-specific names such as **`minConnsPerNode`** / **`maxConnsPerNode`**) for your workload. **`maxConnsPerNode`** caps concurrent synchronous connections **to each cluster node** from **this** client instance. When the pool is exhausted, further requests can **fail** with a “no more connections”–class error (exact code varies by SDK) rather than blocking forever—size **max** for peak concurrency per node, or scale out clients.

**Aggregate limit:** Every client instance can open up to **`maxConnsPerNode`** connections **to every node** it uses. Roughly, **(number of concurrent client processes or instances) × `maxConnsPerNode`** contributes to connection load **on each node** from your application tier. That total—plus other apps, tools, and overhead—must **not** exceed what the server allows for client protocol connections, typically governed by **`proto-fd-max`** (and related service limits; confirm in your server version’s configuration reference). Size pools and instance counts so you stay **under** that budget with headroom.

**`minConnsPerNode`** keeps a **floor** of live connections so bursts after idle periods do not pay repeated connect cost; raising it increases steady **client-side** resource use. Setting **min equal to max** yields a **fixed** pool size and predictable footprint at the cost of flexibility.

A **high `minConnsPerNode`** means **many connections open at once** when the client **starts**, when pools are **warmed**, or after **network drops** that force **reconnect storms**. Each new connection costs work on **both** client and server; **TLS** adds certificate handshakes and noticeably raises **server CPU** during those bursts. Stagger deploys, keep **min** only as high as needed, or accept that reconnect events can briefly stress the cluster.

Use **connection warmup** APIs where available so the first application requests after startup do not pay cold-pool latency—while understanding warmup **concentrates** the same connect cost into startup unless you throttle or spread it operationally.

The client runs a **cluster tend** loop that refreshes topology on an interval (**`tendInterval`** or equivalent). Lower values detect membership changes sooner; higher values reduce background chatter. Tune only when you understand the tradeoff (defaults are usually fine).

**Why**

Under-provisioned pools serialize work or error under spike load; over-provisioned pools waste file descriptors and server sessions. Ignoring **aggregate** client connections vs **`proto-fd-max`** causes connection failures or instability cluster-wide. Large **`minConnsPerNode`** × many instances can **spike server CPU** during mass connect/reconnect (worse with **TLS**). Cold starts without warmup show as tail latency spikes after deploy.

**Prefer**

- Sizing **`maxConnsPerNode`** and **client instance count** so **(instances × maxConnsPerNode)** stays within **`proto-fd-max`** (and ops guidance) with margin for non-app traffic
- Pool sizing from **measured** concurrency per node and observed errors
- Warmup after client construction when tail latency after deploy matters
- **minConnsPerNode** when workloads have **idle gaps** then **bursts**—but not so high that startup or **reconnect** storms overload server CPU (monitor with TLS especially)

**Avoid**

- Default pool sizes for high-QPS services without measurement
- **maxConnsPerNode** so low that normal bursts hit **connection exhaustion**
- Scaling out **many** client replicas each with a **high** `maxConnsPerNode` without checking **per-node** **`proto-fd-max`** and total concurrent clients
- **Very high `minConnsPerNode`** combined with mass **simultaneous** client restarts or **network flaps**—expect **CPU** pressure on nodes when connections are re-established (**TLS** amplifies)

**See also**

- [client-singleton.md](client-singleton.md)
- [client-direct-node-access.md](client-direct-node-access.md)
- [client-error-rate-backoff.md](client-error-rate-backoff.md)
- [sec-client-tls-auth.md](sec-client-tls-auth.md)
