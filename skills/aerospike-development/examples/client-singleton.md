# Example: Singleton client

Related rules: [client-singleton.md](../references/client-singleton.md), [policy-reuse-timeouts-retries.md](../references/policy-reuse-timeouts-retries.md)

**All languages.** The linked documentation page carries this in tabbed examples, in the canonical tab order: **Java SDK, Python SDK, Rust, C#, Go, Node.js, C, Java (legacy), Python (legacy)**. Java, Python and C are on essentially every page, with Go, C# and Node.js close behind; **Java SDK, Python SDK and Rust are still rolling out** and are present on a minority of pages today. The snippets below are one or two languages for orientation — the documentation is the complete set, and the client's own repository is authoritative for its API surface ([client-source-of-truth.md](../references/client-source-of-truth.md)).

**Official source (connect pattern):** [Python client — Create — Setup](https://aerospike.com/docs/develop/client/python/usage/atomic/create#setup)

**Docs:** [Python client](https://aerospike.com/docs/develop/client/python), [Client architecture](https://aerospike.com/docs/database/learn/architecture/clients)

**Scenario:** One long-lived client per process; avoid connect/close per request.

```python
import sys
import aerospike

config = {
    "hosts": [("127.0.0.1", 3000)],
    "policies": {
        "write": {"max_retries": 2, "socket_timeout": 1000},
    },
}

try:
    global_client = aerospike.client(config).connect()
except Exception as e:
    print(f"Failed to connect to the cluster: {e}")
    sys.exit(1)


def write_data(key_tuple, bin_dict):
    try:
        global_client.put(key_tuple, bin_dict)
    except aerospike.exception.AerospikeError as e:
        print(f"Write failed: {e}")


# Close global_client only on application shutdown.
```

**Why:** The client maintains connection pools and cluster tending; reuse avoids socket churn and repeated topology work.

**Other languages:** [Java](https://aerospike.com/docs/develop/client/java) · [Go](https://aerospike.com/docs/develop/client/go) · [Node.js](https://aerospike.com/docs/develop/client/node)
