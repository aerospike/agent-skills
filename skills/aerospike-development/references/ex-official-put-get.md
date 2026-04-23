# Official doc examples: create (put) and read (get)

Related rules: [single-record-operations.md](single-record-operations.md), [policy-reuse-timeouts-retries.md](policy-reuse-timeouts-retries.md)

Aerospike publishes **full runnable Create/Read samples** on each language page (ufodata-style tutorials with GeoJSON, policies, etc.). **Do not duplicate** those long listings here—use the links below. The **minimal Python and Java** snippets only show connect → put → get shape.

**Official guides (Create + Read — use each page’s Code block for the full program):**

| Language | Create | Read |
|----------|--------|------|
| Java | [Create](https://aerospike.com/docs/develop/client/java/usage/atomic/create#code-block) | [Read](https://aerospike.com/docs/develop/client/java/usage/atomic/read#code-block) |
| Python | [Create](https://aerospike.com/docs/develop/client/python/usage/atomic/create#code-block) | [Read](https://aerospike.com/docs/develop/client/python/usage/atomic/read#code-block) |
| Go | [Create](https://aerospike.com/docs/develop/client/go/usage/atomic/create#code-block) | [Read](https://aerospike.com/docs/develop/client/go/usage/atomic/read#code-block) |
| Node.js | [Create](https://aerospike.com/docs/develop/client/node/usage/atomic/create#code-block) | [Read](https://aerospike.com/docs/develop/client/node/usage/atomic/read#code-block) |
| C# | [Create](https://aerospike.com/docs/develop/client/csharp/usage/atomic/create#code-block) | [Read](https://aerospike.com/docs/develop/client/csharp/usage/atomic/read#code-block) |
| Rust | [Create](https://aerospike.com/docs/develop/client/rust/usage/atomic/create) | [Read](https://aerospike.com/docs/develop/client/rust/usage/atomic/read) |

## Minimal examples

Full runnable samples live on each linked page.

### Python

```python
import aerospike

config = {"hosts": [("127.0.0.1", 3000)]}
client = aerospike.client(config).connect()

key = ("test", "demo", "user-1")
client.put(key, {"name": "Ada", "score": 42})
_, _, bins = client.get(key)
print(bins)

client.close()
```

### Java

```java
import com.aerospike.client.AerospikeClient;
import com.aerospike.client.Bin;
import com.aerospike.client.Key;
import com.aerospike.client.Record;

AerospikeClient client = new AerospikeClient("127.0.0.1", 3000);
try {
    Key key = new Key("test", "demo", "user-1");
    client.put(null, key, new Bin("name", "Ada"), new Bin("score", 42));
    Record record = client.get(null, key);
    System.out.println(record.bins);
} finally {
    client.close();
}
```

Hubs: [Python client](https://aerospike.com/docs/develop/client/python) · [Java client](https://aerospike.com/docs/develop/client/java).
