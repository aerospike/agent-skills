# Example: CDT list append (Java)

Related rules: [cdt-server-side-ops.md](cdt-server-side-ops.md), [cdt-bounded-collections.md](cdt-bounded-collections.md)

**Official sources:** [List data type](https://aerospike.com/docs/develop/data-types/collections/list), [Bin operations](https://aerospike.com/docs/develop/learn/bin-operations/), [Java client hub](https://aerospike.com/docs/develop/client/java) (atomic `operate` + CDT APIs for your SDK version).

**Scenario:** Append one item to a per-user click history without read-modify-write.

```java
import com.aerospike.client.AerospikeClient;
import com.aerospike.client.Key;
import com.aerospike.client.Value;
import com.aerospike.client.cdt.ListOperation;
import com.aerospike.client.policy.WritePolicy;

public void addClickHistory(
        AerospikeClient client,
        WritePolicy writePolicy,
        String userId,
        String clickedItem) {
    Key key = new Key("my_namespace", "users", userId);
    client.operate(
            writePolicy,
            key,
            ListOperation.append("click_history", Value.get(clickedItem)));
}
```

**Why:** `ListOperation.append` runs atomically on the server in one round trip.

**Other languages:** [Python](https://aerospike.com/docs/develop/client/python) · [Go](https://aerospike.com/docs/develop/client/go) · [Node.js](https://aerospike.com/docs/develop/client/node) · [C#](https://aerospike.com/docs/develop/client/csharp)
