# Example: Batch read by keys (conceptual)

Related rules: [batch-parallel-key-operations.md](batch-parallel-key-operations.md)

**Official batch links + minimal snippet:** [ex-official-batch.md](ex-official-batch.md)

**Docs:** [Batch](https://aerospike.com/docs/develop/learn/batch/)

**Scenario:** Fetch many records by primary key in fewer round trips than one get per key.

Use your SDK’s batch API with a **list of keys** built from known identifiers—**each key at most once** per batch; dedupe or coalesce on the client, and use batch **`operate`** when one key needs multiple operations (see [batch-parallel-key-operations.md](batch-parallel-key-operations.md)). Pseudocode:

```
keys = [ Key(ns, set, id1), Key(ns, set, id2), ... ]
records = client.batch_get(policy, keys)
```

Handle **per-key errors** in the result structure your client returns (not all languages surface failures the same way).

**Why:** Batch parallelizes work across the cluster for the key set and reduces client/server chatty patterns.

**Language entry points:** [Java](https://aerospike.com/docs/develop/client/java) · [Go](https://aerospike.com/docs/develop/client/go) · [Python](https://aerospike.com/docs/develop/client/python) · [Node.js](https://aerospike.com/docs/develop/client/node) · [C#](https://aerospike.com/docs/develop/client/csharp)
