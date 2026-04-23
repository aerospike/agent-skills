# Example: Singleton client (Python)

Related rules: [client-singleton.md](client-singleton.md), [policy-reuse-timeouts-retries.md](policy-reuse-timeouts-retries.md)

**Official source (connect pattern):** [Python client — Create — Setup](https://aerospike.com/docs/develop/client/python/usage/atomic/create#setup)

**Docs:** [Python client](https://aerospike.com/docs/develop/client/python), [Client architecture](https://aerospike.com/docs/database/learn/architecture/client-architecture)

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
