# Example: Nested list of maps — insert a vehicle at index 0 (Java + Python)

Related rules: [cdt-nested-collections.md](cdt-nested-collections.md), [cdt-server-side-ops.md](cdt-server-side-ops.md), [cdt-bounded-collections.md](cdt-bounded-collections.md)

**Official source:** [Working with nested collection data types — Add a new vehicle as the default](https://aerospike.com/docs/develop/expressions/nesting#add-a-new-vehicle-as-the-default)

The doc models a `vehicles` bin as a **list of maps** (each map is a vehicle). This sample inserts a new map at index `0` with `ListOrder.UNORDERED` and `ADD_UNIQUE | NO_FAIL` so duplicates are rejected without failing the call—see the nesting guide for why **K-ordered** maps matter for `ADD_UNIQUE` comparison.

## Java

```java
import java.util.TreeMap;
import com.aerospike.client.AerospikeClient;
import com.aerospike.client.Key;
import com.aerospike.client.Operation;
import com.aerospike.client.Record;
import com.aerospike.client.Value;
import com.aerospike.client.cdt.ListOperation;
import com.aerospike.client.cdt.ListOrder;
import com.aerospike.client.cdt.ListPolicy;
import com.aerospike.client.cdt.ListWriteFlags;

// key = new Key(...); client = ...

TreeMap<String, Object> vehicle = new TreeMap<>();
vehicle.put("color", "red");
vehicle.put("license", "5DEF456");
vehicle.put("make", "Ford");
vehicle.put("model", "Mustang");

ListPolicy policy = new ListPolicy(ListOrder.UNORDERED,
    ListWriteFlags.ADD_UNIQUE | ListWriteFlags.NO_FAIL);

Record record = client.operate(null, key,
    ListOperation.insert(policy, "vehicles", 0, Value.get(vehicle)),
    Operation.get("vehicles"));
```

## Python

**Official source:** same page, Python tab.

```python
import aerospike
from aerospike import KeyOrderedDict
from aerospike_helpers.operations import list_operations

vehicle = KeyOrderedDict({
    "color": "red",
    "license": "5DEF456",
    "make": "Ford",
    "model": "Mustang"
})

policy = {
    "list_order": aerospike.LIST_UNORDERED,
    "write_flags": aerospike.LIST_WRITE_ADD_UNIQUE | aerospike.LIST_WRITE_NO_FAIL
}

ops = [
    list_operations.list_insert("vehicles", 0, vehicle, policy)
]

(key, meta, bins) = client.operate(key, ops)
```

**Why:** Server-side `operate` updates the nested structure atomically; `TreeMap` / `KeyOrderedDict` match the **K-ordered** map wire form the server expects for reliable map equality checks.

**More:** [Context (CDT paths)](https://aerospike.com/docs/develop/data-types/collections/context/) · [Path expressions](https://aerospike.com/docs/develop/expressions/path/) · [Go / C# / Node.js tabs](https://aerospike.com/docs/develop/expressions/nesting#add-a-new-vehicle-as-the-default) on the same page
