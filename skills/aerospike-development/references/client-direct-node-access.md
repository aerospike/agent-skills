---
title: Reach every cluster node directly (no proxy in the data path)
impact: HIGH
tags: client, network, topology, seeds, access-address
doc: https://aerospike.com/docs/database/manage/network
also:
  - https://www.aerospike.com/docs/develop/client/java/connect/
  - https://aerospike.com/docs/database/reference/config#network__alternate-access-address
last_verified: 2026-04-21
---

## Reach every cluster node directly (no proxy in the data path)

**Rule**

The Aerospike client must have **direct network reachability to every node** in the cluster (not only to seed hosts). It **automatically maintains** the current node list (via seeds and ongoing tending) and **works against the full cluster**—partitioning, replica placement, and migrations direct traffic to the **right** nodes. **Using a single seed for bootstrap does not limit** the client to **that** node; in a cluster, work is **not** confined to the seed you picked.

After a successful seed connection, the client learns membership and opens connections to **each** node for database traffic and cluster tending. **There is no supported proxy or connection concentrator** between application clients and database nodes on the service path—do not put an HTTP reverse proxy, generic TCP load balancer, or “database gateway” in front of the cluster and expect correct behavior.

If the **address the node advertises** (e.g. internal IP) is **not** reachable from the application network, fix it with **server network config**, not a proxy: set **`access-address`** / **`alternate-access-address`** (and **`access-port`** / **`alternate-access-port`** when ports differ) so the cluster publishes **routable** endpoints. Clients that must use **alternate** addresses typically set **`useServicesAlternate`** (or the SDK equivalent) in **ClientPolicy** ([Network configuration](https://aerospike.com/docs/database/manage/network), [alternate-access-address](https://aerospike.com/docs/database/reference/config#network__alternate-access-address)).

**Why**

The protocol assumes **peer-style** connectivity to each node. Hiding nodes behind a single VIP breaks discovery, partition handling, and per-node connection semantics—symptoms include connection failures, partial cluster views, and unstable performance.

**Prefer**

- Firewall and routing that allow the app tier to reach **each node’s client-facing service port**
- Server **network** settings so advertised addresses match **how clients actually reach** the nodes
- Multiple **seed** hosts for bootstrap resilience (still not a substitute for reaching **all** nodes)

**Avoid**

- Assuming traffic stays on the **seed** you configured—operations run across **all** nodes the client knows about
- Treating the seed list as the only hosts that must be reachable
- Inserting a **proxy** or **LB** between clients and nodes for normal database traffic
- Assuming **localhost** or internal-only IPs work from a different network without **access** / **alternate** address configuration

**See also**

- [client-singleton.md](client-singleton.md)
- [policy-client-defaults.md](policy-client-defaults.md)
- [client-pools-warmup.md](client-pools-warmup.md)
- [sec-client-tls-auth.md](sec-client-tls-auth.md)
