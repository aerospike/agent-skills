---
title: Use operate for multi-bin atomic updates on one key
impact: HIGH
tags: bin-operations, operate, atomicity
doc: https://aerospike.com/docs/develop/learn/bin-operations/
last_verified: 2026-04-21
---

## Use operate for multi-bin atomic updates on one key

**Rule**

When a single logical update touches multiple bins or uses CDT ops on one record, use `operate` (multi-operation) so the server applies the sequence atomically for that record, rather than separate put/get cycles that can interleave with other writers.

**Why**

Interleaved reads and writes on the same key from multiple clients produce lost updates unless you use generations or server-side combined operations.

**Prefer**

- One `operate` call combining the bin ops you need
- Generations when you need compare-and-swap across clients

**Avoid**

- Multiple independent puts racing without coordination
- Mixing a whole-record read with bin-scoped ops in one `operate` (use per-bin reads only; see [operate-record-lock-read-write.md](aerospike-development-operate-record-lock-read-write.md))

**See also**

- [operate-record-lock-read-write.md](aerospike-development-operate-record-lock-read-write.md) (record lock, mixed read/write, latency)
- [operate-mixed-read-write.md](https://github.com/aerospike/agent-skills/blob/main/skills/aerospike-development/examples/operate-mixed-read-write.md)
- [cdt-server-side-ops.md](aerospike-development-cdt-server-side-ops.md)
- [single-record-operations.md](aerospike-development-single-record-operations.md)
