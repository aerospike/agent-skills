# Aerospike SDK examples

Companion to the getting started skill ([SKILL.md](SKILL.md)). Copy and adapt namespace, set name, and key/bin names for the user's domain. For connection host in Docker Compose, use the service name (e.g. `aerospike`) instead of `127.0.0.1`.

## Python

```python
import aerospike
from aerospike import exception as ex

config = {"hosts": [("127.0.0.1", 3000)]}
client = aerospike.client(config)

namespace = "test"
set_name = "demo"

write_policy = {"total_timeout": 5000}
key = (namespace, set_name, "user:1")
bins = {"name": "Alice", "age": 30}

try:
    client.put(key, bins, policy=write_policy)
    print("Write OK")

    read_policy = {"total_timeout": 5000}
    _, _, record = client.get(key, policy=read_policy)
    print(f"Read OK: {record}")
except ex.AerospikeError as e:
    print(f"Error: {e}")
finally:
    client.close()
```

## Node.js

```javascript
const Aerospike = require("aerospike");

async function main() {
  const client = await Aerospike.connect({ hosts: "127.0.0.1:3000" });

  const namespace = "test";
  const set = "demo";

  const key = new Aerospike.Key(namespace, set, "user:1");
  const bins = { name: "Alice", age: 30 };
  const writePolicy = new Aerospike.WritePolicy({ totalTimeout: 5000 });

  try {
    await client.put(key, bins, {}, writePolicy);
    console.log("Write OK");

    const readPolicy = new Aerospike.ReadPolicy({ totalTimeout: 5000 });
    const record = await client.get(key, readPolicy);
    console.log("Read OK:", record.bins);
  } catch (err) {
    console.error("Error:", err);
  } finally {
    client.close();
  }
}

main();
```

## Go

The import path includes the major version per Go module semantics (currently `v8`). Check [the repo](https://github.com/aerospike/aerospike-client-go) for the latest major version tag and update the import path accordingly.

```go
package main

import (
	"log"
	"time"

	aero "github.com/aerospike/aerospike-client-go/v8"
)

func main() {
	client, err := aero.NewClient("127.0.0.1", 3000)
	if err != nil {
		log.Fatal(err)
	}
	defer client.Close()

	namespace := "test"
	set := "demo"

	wp := aero.NewWritePolicy(0, 0)
	wp.TotalTimeout = 5000 * time.Millisecond

	key, err := aero.NewKey(namespace, set, "user:1")
	if err != nil {
		log.Fatal(err)
	}

	bins := aero.BinMap{"name": "Alice", "age": 30}
	err = client.Put(wp, key, bins)
	if err != nil {
		log.Fatal(err)
	}
	log.Println("Write OK")

	rp := aero.NewPolicy()
	rp.TotalTimeout = 5000 * time.Millisecond

	record, err := client.Get(rp, key)
	if err != nil {
		log.Fatal(err)
	}
	log.Printf("Read OK: %v", record.Bins)
}
```

## Java

Maven dependency — check [Maven Central](https://central.sonatype.com/artifact/com.aerospike/aerospike-client-jdk21) for the latest version:

```xml
<dependency>
    <groupId>com.aerospike</groupId>
    <artifactId>aerospike-client-jdk21</artifactId>
    <version>X.Y.Z</version> <!-- Replace with actual latest version from Maven Central -->
</dependency>
```

For JDK 8-20, use artifact `aerospike-client-jdk8` instead.

```java
import com.aerospike.client.*;
import com.aerospike.client.policy.*;

public class AerospikeDemo {
    public static void main(String[] args) {
        AerospikeClient client = new AerospikeClient("127.0.0.1", 3000);

        String namespace = "test";
        String set = "demo";

        WritePolicy wp = new WritePolicy();
        wp.totalTimeout = 5000;

        Key key = new Key(namespace, set, "user:1");
        Bin name = new Bin("name", "Alice");
        Bin age = new Bin("age", 30);

        try {
            client.put(wp, key, name, age);
            System.out.println("Write OK");

            Policy rp = new Policy();
            rp.totalTimeout = 5000;

            Record record = client.get(rp, key);
            System.out.println("Read OK: " + record.bins);
        } catch (AerospikeException e) {
            e.printStackTrace();
        } finally {
            client.close();
        }
    }
}
```

## C#

Top-level statements are shown below; wrap in `Main` if the project uses explicit entry points.

```csharp
using Aerospike.Client;

var client = new AerospikeClient("127.0.0.1", 3000);

var ns = "test";
var set = "demo";

var writePolicy = new WritePolicy { totalTimeout = 5000 };
var key = new Key(ns, set, "user:1");

try
{
    client.Put(writePolicy, key, new Bin("name", "Alice"), new Bin("age", 30));
    Console.WriteLine("Write OK");

    var readPolicy = new Policy { totalTimeout = 5000 };
    var record = client.Get(readPolicy, key);
    Console.WriteLine($"Read OK: name={record.GetString("name")}, age={record.GetInt("age")}");
}
catch (AerospikeException e)
{
    Console.WriteLine($"Error: {e.Message}");
}
finally
{
    client.Close();
}
```

## Bulk writes and connection limits (Node.js)

The connection tuning guide describes `maxConnsPerNode` as the ceiling limit for the total number of connections allowed per client, per node. It also notes that connections used include primary commands as well as parallel sub-commands from batch and query. For large parallel write workloads in Node.js, either batch writes in smaller chunks or raise `maxConnsPerNode` when the workload legitimately needs more concurrency.

**Solution A:** batch writes in smaller chunks so each wave stays below the connection limit.

```javascript
const BATCH_SIZE = 50;

for (let i = 0; i < records.length; i += BATCH_SIZE) {
  const batch = records.slice(i, i + BATCH_SIZE);

  const results = await Promise.allSettled(
    batch.map((record) => {
      const key = new Aerospike.Key(namespace, set, record.id);
      return client.put(key, record.bins);
    })
  );

  const failures = results.filter((result) => result.status === "rejected");
  if (failures.length > 0) {
    console.error("Batch write failures:", failures);
  }
}
```

**Solution B:** raise the client connection cap when the workload legitimately needs more concurrency.

```javascript
const client = await Aerospike.connect({
  hosts: "127.0.0.1:3000",
  maxConnsPerNode: 300,
});
```

This connection-limit behavior can surface in any async SDK, but Node.js users hit it most often because large `Promise.all(...)` batches are common.
