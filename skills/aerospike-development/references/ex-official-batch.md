# Official doc examples: batch reads

Related rules: [batch-parallel-key-operations.md](batch-parallel-key-operations.md)

**Concept:** [Batched commands](https://aerospike.com/docs/develop/learn/batch). Full **Setup + policies + `BatchResults`** samples live on each language’s **Batched commands** page—use the linked **Code block**, not a copy here.

**Official batch read guides:**

| Language | Batched commands (read + full example) |
|----------|----------------------------------------|
| Java | [Batch](https://aerospike.com/docs/develop/client/java/usage/multi/batch#code-block) |
| Python | [Batch](https://aerospike.com/docs/develop/client/python/usage/multi/batch#code-block) |
| Go | [Batch](https://aerospike.com/docs/develop/client/go/usage/multi/batch#code-block) |
| Node.js | [Batch](https://aerospike.com/docs/develop/client/node/usage/multi/batch) |
| C# | [Batch](https://aerospike.com/docs/develop/client/csharp/usage/multi/batch) |
| Rust | [Rust client hub](https://aerospike.com/docs/develop/client/rust) — batch APIs per crate version |

## Minimal examples

See each language’s **Batched commands** page for `batchPolicy`, error handling, and advanced batch APIs.

### Python

```python
import aerospike

config = {"hosts": [("127.0.0.1", 3000)]}
client = aerospike.client(config).connect()

keys = [("sandbox", "ufodata", i) for i in range(1, 11)]
brs = client.batch_read(keys)
for br in brs.batch_records:
    _, _, bins = br.record
    print(bins)

client.close()
```

### Java

```java
import com.aerospike.client.AerospikeClient;
import com.aerospike.client.Key;
import com.aerospike.client.Record;
import com.aerospike.client.policy.BatchPolicy;

AerospikeClient client = new AerospikeClient("127.0.0.1", 3000);
try {
    BatchPolicy bp = new BatchPolicy();
    Key[] keys = new Key[10];
    for (int i = 0; i < 10; i++) {
        keys[i] = new Key("sandbox", "ufodata", i + 1);
    }
    Record[] records = client.get(bp, keys);
    for (Record rec : records) {
        if (rec != null) {
            System.out.println(rec.bins);
        }
    }
} finally {
    client.close();
}
```
