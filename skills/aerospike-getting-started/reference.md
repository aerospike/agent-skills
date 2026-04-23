# Aerospike reference (configuration, editions, troubleshooting)

Companion to the getting started skill ([SKILL.md](SKILL.md)).

## Version notes

| Topic | Detail |
|-------|--------|
| Port `3003` | On Database **8.1.0** and later, this is the **admin** port (older docs often call it the info port). Map with `-p 3003:3003` when admin or legacy info access is needed. |
| `cluster-name` | Mandatory in the `service` stanza for Database **7.0.0** and later. |
| Go client import | Major version in path (e.g. `github.com/aerospike/aerospike-client-go/v8`); check [repo tags](https://github.com/aerospike/aerospike-client-go) for current major version. |
| Enterprise Docker | Since Database **6.1.0**, the Enterprise image includes a built-in evaluation feature key for single-node use. |

The canonical quick-start `aerospike.conf` (namespace `test`, in-memory) lives only in [SKILL.md](SKILL.md) Step 2 — use that for the default Docker flow. This file adds variants and operations that differ from that path.

## Custom `aerospike.conf` and Docker (project-relative mount)

When the user needs more than the defaults, place `aerospike.conf` in the project and run:

```bash
docker run -d --name aerospike \
  -p 3000-3002:3000-3002 \
  -v $(pwd)/aerospike.conf:/opt/aerospike/etc/aerospike.conf \
  aerospike/aerospike-server:latest \
  --config-file /opt/aerospike/etc/aerospike.conf
```

### Example: custom namespace `myapp`

Use the same `service`, `logging`, and `network` stanzas as in SKILL.md Step 2; only the `namespace` block differs:

```
namespace myapp {
    replication-factor 2
    default-ttl 0
    nsup-period 10
    storage-engine memory {
        data-size 4G
    }
}
```

Database `7.0.0` and later require `cluster-name` in the `service` stanza. `nsup-period` controls how often NSUP runs; default `0` disables NSUP for the namespace. For automatic expiration, set `nsup-period` to a value greater than `0`.

**Key config options:**

- `default-ttl 0` means records never expire. Set to `30d`, `24h`, etc. for automatic expiration.
- `storage-engine memory` stores data in RAM. For persistence, use `storage-engine device` with a file path.
- `data-size` controls how much memory this namespace can use.

## Docker Compose for multi-service apps

```yaml
services:
  aerospike:
    image: aerospike/aerospike-server:latest
    command: ["--config-file", "/opt/aerospike/etc/aerospike.conf"]
    ports:
      - "3000-3002:3000-3002"
    volumes:
      - ./aerospike.conf:/opt/aerospike/etc/aerospike.conf
      - aerospike-data:/opt/aerospike/data

  app:
    build: .
    depends_on:
      - aerospike
    environment:
      AEROSPIKE_HOST: aerospike
      AEROSPIKE_PORT: 3000

volumes:
  aerospike-data:
```

When using Docker Compose, the app connects to host `aerospike` (the service name) instead of `127.0.0.1`.

Ensure `aerospike.conf` includes `cluster-name` and any `nsup-period` setting you need (see SKILL.md Step 2 for a complete example).

## Community Edition vs Enterprise

Aerospike Community Edition is free and open source (AGPLv3) with the same core storage engine and client API as Enterprise. Key differences: max 2 namespaces, max 8 nodes, 2.5 TB cluster data limit, AP-only mode (no strong consistency), and no built-in authentication.

For current limits and a full feature comparison, see the [official editions page](https://aerospike.com/products/features-and-editions/).

### Free Enterprise evaluation

Since Database 6.1.0, the Enterprise Docker image ships with a built-in evaluation feature key that enables all features on a single node:

```bash
docker run -d --name aerospike -p 3000-3002:3000-3002 aerospike/aerospike-server-enterprise:latest
```

To use a custom feature key (e.g. production license), mount it from the host:

```bash
docker run -d --name aerospike \
  -p 3000-3002:3000-3002 \
  -v /path/to/features-dir:/opt/aerospike/etc/ \
  -e "FEATURE_KEY_FILE=/opt/aerospike/etc/features.conf" \
  aerospike/aerospike-server-enterprise:latest
```

Users can also [start a free Enterprise trial](https://aerospike.com/get-started-aerospike-database/) for extended evaluations. If the user mentions strong consistency, compression, security/authentication, or other Enterprise features, suggest the Enterprise image.

## Platform requirements and troubleshooting

Some Aerospike client SDKs include native (C/C++) extensions and have platform-specific build requirements. If an SDK install fails, check the table below before debugging further.

| SDK | Native extension? | Requirements | Common failure |
|-----|-------------------|-------------|----------------|
| **Python** | Yes (C client) | Prebuilt wheels available for macOS, Linux, and Windows (x64). A C compiler is only needed when building from source. Supports Python 3.10+. | `error: command 'gcc' failed` → building from source; install build tools and Python dev headers, or use `pip install aerospike` on a supported platform for a prebuilt wheel. |
| **Node.js** | Yes (C client via node-gyp) | Requires `node-gyp` build toolchain: C/C++ compiler, Python 3, `make`. On macOS, run `xcode-select --install`. On Windows, use WSL2 or install windows-build-tools. Install docs list Node.js `25`, `24` (LTS), `22` (LTS), and `20` (LTS) as compatible. | `gyp ERR! build error` → install documented prerequisites: `sudo apt install build-essential python3` (Linux) or `xcode-select --install` (macOS). If npm falls back to a source build, confirm a documented compatible Node.js version and toolchain. |
| **Go** | No (pure Go) | No special build dependencies. | Connection refused → container not running or wrong port. |
| **Java** | No (pure Java) | JDK 8+ (`aerospike-client-jdk8` for JDK 8-20, `aerospike-client-jdk21` for JDK 21+). | ClassNotFoundException → wrong artifact for the JDK version. |
| **C#** | No (managed .NET) | .NET 8.0+ (NuGet v8.2.0+ dropped .NET 6). | Connection refused → container not running or wrong port. |

### General troubleshooting

- **Container won't start:** Check if port 3000 is already in use: `lsof -i :3000` (macOS/Linux) or `netstat -ano | findstr :3000` (Windows). Kill the conflicting process or map to a different host port.
- **"Connection refused" from SDK:** The container may still be starting. Wait 5 seconds and retry. Verify with `docker logs aerospike 2>&1 | grep "service ready"`.
- **Apple Silicon (M1/M2/M3) Macs:** The `aerospike/aerospike-server` Docker image provides both `linux/amd64` and `linux/arm64` variants. It runs natively on Apple Silicon — no Rosetta emulation or extra flags needed.
- **SDK version mismatch with server:** Clients are generally backward-compatible with older servers. If you see protocol errors, ensure both client and server are reasonably current. See [client compatibility](https://aerospike.com/docs/develop/client).
