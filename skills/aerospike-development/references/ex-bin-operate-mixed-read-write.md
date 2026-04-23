# Example: `operate` with mixed read and write (Java)

Related rules: [binop-operate-record-lock-read-write.md](binop-operate-record-lock-read-write.md), [binop-operate-atomicity.md](binop-operate-atomicity.md)

**Official source:** [Bin operations — Code example of the operate command](https://aerospike.com/docs/develop/learn/bin-operations/#code-example-of-the-operate-command)

**Scenario:** Increment a counter, append to a string, then **read back** the updated bins in **one** `operate` call (same record lock, one round trip).

```java
import com.aerospike.client.AerospikeClient;
import com.aerospike.client.Bin;
import com.aerospike.client.Key;
import com.aerospike.client.Operation;
import com.aerospike.client.Record;

AerospikeClient client = new AerospikeClient("127.0.0.1", 3000);
Key key = new Key("test", "demo", "op-example");

client.put(null, key,
    new Bin("name", "J. Smith"),
    new Bin("visits", 1));

Record record = client.operate(null, key,
    Operation.add(new Bin("visits", 1)),
    Operation.append(new Bin("name", " Jr.")),
    Operation.get("visits"),
    Operation.get("name"));

System.out.format("visits: %s%n", record.bins.get("visits"));
System.out.format("name: %s%n", record.bins.get("name"));

client.close();
```

**Why:** Writes run first in the list; the `get` operations return the post-update values without a second network call.

**Gotcha:** Do not combine bin-level updates with a **whole-record** read in the same `operate`. Use **explicit read ops per bin** (as in this example’s `Operation.get("visits")` and `Operation.get("name")`) instead of expecting one step to return the full record after a bin increment.

**More:** [Execution trace](https://aerospike.com/docs/develop/learn/bin-operations/#how-operate-executes) (mixed five-op walkthrough) · [Python / Go / Node.js tabs](https://aerospike.com/docs/develop/learn/bin-operations/#code-example-of-the-operate-command) on the same page
