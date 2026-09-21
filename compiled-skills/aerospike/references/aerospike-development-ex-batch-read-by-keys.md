# Example: Batch read by keys (conceptual)

Related rules: [batch-parallel-key-operations.md](aerospike-development-batch-parallel-key-operations.md)

**All languages.** The linked documentation page carries this in tabbed examples, in the canonical tab order: **Java SDK, Python SDK, Rust, C#, Go, Node.js, C, Java (legacy), Python (legacy)**. Java, Python and C are on essentially every page, with Go, C# and Node.js close behind; **Java SDK, Python SDK and Rust are still rolling out** and are present on a minority of pages today. The snippets below are one or two languages for orientation — the documentation is the complete set, and the client's own repository is authoritative for its API surface ([client-source-of-truth.md](aerospike-development-client-source-of-truth.md)).

**Official batch links + minimal snippet:** [ex-official-batch.md](aerospike-development-ex-official-batch.md)

**Docs:** [Batch](https://aerospike.com/docs/develop/learn/batch/)

**Scenario:** Fetch many records by primary key in fewer round trips than one get per key.

Use your SDK’s batch API with a **list of keys** built from known identifiers—**each key at most once** per batch; dedupe or coalesce on the client, and use batch **`operate`** when one key needs multiple operations (see [batch-parallel-key-operations.md](aerospike-development-batch-parallel-key-operations.md)). Pseudocode:

```
keys    = [ Key(ns, set, id1), Key(ns, set, id2), ... ]
records = <your SDK's batch read>(keys)
```

Method names and argument order differ by language—Python is `client.batch_read(keys)`
returning a `BatchRecords`, Java is `client.get(batchPolicy, keys)` returning `Record[]`.
Take the real signature from [ex-official-batch.md](aerospike-development-ex-official-batch.md) rather than this
sketch.

Handle **per-key errors** in the result structure your client returns (not all languages surface failures the same way).

**Why:** Batch parallelizes work across the cluster for the key set and reduces client/server chatty patterns.

**Language entry points:** [Java](https://aerospike.com/docs/develop/client/java) · [Go](https://aerospike.com/docs/develop/client/go) · [Python](https://aerospike.com/docs/develop/client/python) · [Node.js](https://aerospike.com/docs/develop/client/node) · [C#](https://aerospike.com/docs/develop/client/csharp)
