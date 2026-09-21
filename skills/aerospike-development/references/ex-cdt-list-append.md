# Example: CDT list append

Related rules: [cdt-server-side-ops.md](cdt-server-side-ops.md), [cdt-bounded-collections.md](cdt-bounded-collections.md)

**All languages.** The linked documentation page carries this in tabbed examples, in the canonical tab order: **Java SDK, Python SDK, Rust, C#, Go, Node.js, C, Java (legacy), Python (legacy)**. Java, Python and C are on essentially every page, with Go, C# and Node.js close behind; **Java SDK, Python SDK and Rust are still rolling out** and are present on a minority of pages today. The snippets below are one or two languages for orientation — the documentation is the complete set, and the client's own repository is authoritative for its API surface ([client-source-of-truth.md](client-source-of-truth.md)).

**Official sources:** [`append` operation card](https://aerospike.com/docs/develop/data-types/collections/list/operations/#append) (args, return value, and a code tab per client), [List data type](https://aerospike.com/docs/develop/data-types/collections/list), [Bin operations](https://aerospike.com/docs/develop/learn/bin-operations/), [Java client hub](https://aerospike.com/docs/develop/client/java) (atomic `operate` + CDT APIs for your SDK version).

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
