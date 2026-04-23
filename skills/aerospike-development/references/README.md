# Reference pack (`aerospike-development`)

**Rules:** one concern per file; YAML frontmatter (`title`, `impact`, `tags`, `doc`). **`ex-*`:** link-first pointers to Aerospike docs (repository **CONTRIBUTING.md**, *Token footprint*). `_` prefix = templates. **`doc`:** [Aerospike Documentation](https://aerospike.com/docs/).

## Example walkthroughs

| File | Topic |
|------|--------|
| [ex-cdt-list-append.md](ex-cdt-list-append.md) | CDT list append (Java) |
| [ex-cdt-map-nested-vehicles.md](ex-cdt-map-nested-vehicles.md) | Nested maps / vehicles (Java + Python) |
| [ex-singleton-client-python.md](ex-singleton-client-python.md) | Singleton client (Python) |
| [ex-policy-explicit-defaults.md](ex-policy-explicit-defaults.md) | Policy defaults (Python) |
| [ex-batch-read-by-keys.md](ex-batch-read-by-keys.md) | Batch reads (conceptual) |
| [ex-official-put-get.md](ex-official-put-get.md) | Create/Read **links** + minimal Python/Java |
| [ex-official-batch.md](ex-official-batch.md) | Batch **links** + minimal Python/Java |
| [ex-bin-operate-mixed-read-write.md](ex-bin-operate-mixed-read-write.md) | `operate` mixed R/W (Java) |

TOC: [examples.md](../examples.md).

## Impact legend

| Level | Meaning |
|-------|---------|
| HIGH | Wrong pattern often causes outages, severe latency, or data races at scale |
| MEDIUM | Performance or correctness issues in common conditions |
| LOW | Style, clarity, or incremental tuning |

## By prefix

| Prefix | Topic |
|--------|--------|
| `client-` | Singleton client, pools, warmup, tend, error-rate backoff, direct node reachability |
| `policy-` | Policies: timeouts/retries, client defaults, replica & read modes, sendKey, commit level, generation/CAS, replace |
| `cdt-` | Lists/maps, nesting, bounded growth, server-side collection ops |
| `expr-` | Filter and operation expressions; compute-to-data |
| `query-` | Queries, secondary indexes, cardinality, index choices from access paths |
| `batch-` | Batch reads/writes across keys; dedupe keys, `operate` per key |
| `binop-` | `operate`, record lock, mixed read/write, bin-level atomicity |
| `single-` | Single-record CRUD, TTL/void-time, NSUP/default-ttl, delete, durable deletes (EE) |
| `model-` | Keys, namespace/set boundaries, flat bins vs CDT vs multiple records, denormalization, access paths, record size vs index and disk, hot keys, client API choice |
| `sec-` | App-facing security (TLS, auth); not cluster ops |

## Rule files

### client-

- [client-singleton.md](client-singleton.md)
- [client-pools-warmup.md](client-pools-warmup.md)
- [client-direct-node-access.md](client-direct-node-access.md)
- [client-error-rate-backoff.md](client-error-rate-backoff.md)

### policy-

- [policy-reuse-timeouts-retries.md](policy-reuse-timeouts-retries.md)
- [policy-client-defaults.md](policy-client-defaults.md)
- [policy-read-replica-consistency.md](policy-read-replica-consistency.md)
- [policy-send-key.md](policy-send-key.md)
- [policy-write-commit-level.md](policy-write-commit-level.md)
- [policy-generation-cas.md](policy-generation-cas.md)
- [policy-replace-whole-record.md](policy-replace-whole-record.md)

### single-

- [single-record-operations.md](single-record-operations.md)
- [single-ttl-expiration-retention.md](single-ttl-expiration-retention.md)
- [single-ttl-nsup-default-ttl.md](single-ttl-nsup-default-ttl.md)
- [single-delete-durable-deletes.md](single-delete-durable-deletes.md)

### model-

- [model-access-paths-denormalization.md](model-access-paths-denormalization.md)
- [model-namespace-set-boundaries.md](model-namespace-set-boundaries.md)
- [model-bin-cdt-multiple-records.md](model-bin-cdt-multiple-records.md)
- [model-client-api-choice.md](model-client-api-choice.md)
- [model-record-size-hardware-efficiency.md](model-record-size-hardware-efficiency.md)
- [model-hot-keys.md](model-hot-keys.md)

### cdt-

- [cdt-bounded-collections.md](cdt-bounded-collections.md)
- [cdt-nested-collections.md](cdt-nested-collections.md)
- [cdt-server-side-ops.md](cdt-server-side-ops.md)

### expr-

- [expr-compute-to-data.md](expr-compute-to-data.md)

### query-

- [query-secondary-index-discipline.md](query-secondary-index-discipline.md)
- [query-sindex-by-access-path.md](query-sindex-by-access-path.md)

### batch-

- [batch-parallel-key-operations.md](batch-parallel-key-operations.md)

### binop-

- [binop-operate-record-lock-read-write.md](binop-operate-record-lock-read-write.md)
- [binop-operate-atomicity.md](binop-operate-atomicity.md)

### sec-

- [sec-client-tls-auth.md](sec-client-tls-auth.md)
