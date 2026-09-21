# Example: Explicit write defaults

Related rules: [policy-reuse-timeouts-retries.md](../references/policy-reuse-timeouts-retries.md)

**All languages.** The linked documentation page carries this in tabbed examples, in the canonical tab order: **Java SDK, Python SDK, Rust, C#, Go, Node.js, C, Java (legacy), Python (legacy)**. Java, Python and C are on essentially every page, with Go, C# and Node.js close behind; **Java SDK, Python SDK and Rust are still rolling out** and are present on a minority of pages today. The snippets below are one or two languages for orientation — the documentation is the complete set, and the client's own repository is authoritative for its API surface ([client-source-of-truth.md](../references/client-source-of-truth.md)).

**Official sources:** [Policies](https://aerospike.com/docs/database/learn/policies/); per-call policy dicts follow the Python client’s policy fields as in [Create — Policies](https://aerospike.com/docs/develop/client/python/usage/atomic/create#policies) and [Read — Policies](https://aerospike.com/docs/develop/client/python/usage/atomic/read#policies).

**Docs:** [Python client](https://aerospike.com/docs/develop/client/python)

**Scenario:** Set default socket behavior and retries once at client configuration instead of per call.

```python
import aerospike

config = {
    "hosts": [("127.0.0.1", 3000)],
    "policies": {
        "total_timeout": 1000,
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
