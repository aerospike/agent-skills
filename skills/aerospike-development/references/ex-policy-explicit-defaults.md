# Example: Explicit write defaults (Python)

Related rules: [policy-reuse-timeouts-retries.md](policy-reuse-timeouts-retries.md)

**Official sources:** [Policies (develop/learn)](https://aerospike.com/docs/develop/learn/policies) · [Policies (database/learn)](https://aerospike.com/docs/database/learn/policies/); per-call policy dicts follow the Python client’s policy fields as in [Create — Policies](https://aerospike.com/docs/develop/client/python/usage/atomic/create#policies) and [Read — Policies](https://aerospike.com/docs/develop/client/python/usage/atomic/read#policies).

**Docs:** [Python client](https://aerospike.com/docs/develop/client/python)

**Scenario:** Set default socket behavior and retries once at client configuration instead of per call.

```python
import aerospike

config = {
    "hosts": [("127.0.0.1", 3000)],
    "policies": {
        "timeout": 1000,
        "write": {
            "socket_timeout": 500,
            "max_retries": 2,
            "sleep_between_retries": 10,
        },
        "read": {
            "socket_timeout": 500,
            "max_retries": 2,
        },
    },
}

client = aerospike.client(config).connect()
```

Tune values for your SLA and network; treat defaults as a starting point, not universal constants.

**Why:** Centralizing policy defaults keeps hot paths allocation-free and makes timeout/retry behavior auditable.

**Other languages:** [Java policies](https://aerospike.com/docs/develop/client/java) (see client policy classes in your SDK version)
