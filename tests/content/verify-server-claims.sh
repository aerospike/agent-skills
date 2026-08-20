#!/usr/bin/env bash
# Verify the getting-started skill's factual claims against a real server.
#
# Reading documentation cannot catch guidance that was true two releases ago;
# booting the server can. Each check names the claim it verifies, so a drifted
# claim points at the file that makes it.
#
# Usage: tests/content/verify-server-claims.sh [--tag TAG]
set -euo pipefail

IMAGE="aerospike/aerospike-server"
TAG="latest"
CONTAINER="aerospike-claim-check-$$"
SKILL="skills/aerospike-getting-started/SKILL.md"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag) TAG="${2:?--tag needs a value}"; shift 2 ;;
    -h|--help) sed -n '2,9p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done

command -v docker >/dev/null 2>&1 || { echo "docker is required." >&2; exit 3; }

passed=0
failed=0

check() {
  # check <claim> <source> <command...>
  local claim="$1" source="$2"; shift 2
  if "$@" >/dev/null 2>&1; then
    echo "  ok    ${claim}  (${source})"
    passed=$((passed + 1))
  else
    echo "  FAIL  ${claim}  (${source})" >&2
    failed=$((failed + 1))
  fi
}

asinfo() { docker exec "${CONTAINER}" asinfo -v "$1"; }
asinfo_has() { asinfo "$1" | grep -qE "$2"; }

cleanup() { docker rm -f "${CONTAINER}" >/dev/null 2>&1 || true; }
trap cleanup EXIT

echo "Booting ${IMAGE}:${TAG}"
docker run -d --name "${CONTAINER}" -p 3000-3002:3000-3002 "${IMAGE}:${TAG}" >/dev/null

for _ in $(seq 1 60); do
  if docker logs "${CONTAINER}" 2>&1 | grep -q "service ready"; then break; fi
  sleep 1
done
docker logs "${CONTAINER}" 2>&1 | grep -q "service ready" || {
  echo "Server did not report 'service ready' within 60s." >&2
  docker logs "${CONTAINER}" 2>&1 | tail -20 >&2
  exit 1
}

build="$(asinfo build | tr -d '\r')"
echo "Server build: ${build}"
echo

# The image name the skill tells a new user to run.
check "Community image ${IMAGE} boots and serves" "${SKILL}" \
  asinfo_has "status" "ok"

# The declared floor is 7.0+; anything older invalidates the documented flow.
check "Build is 7.0 or newer" "${SKILL} metadata.server_versions" \
  bash -c "[[ \$(printf '%s\n7.0.0\n' '${build}' | sort -V | head -1) == '7.0.0' ]]"

# "The default namespace is test. NEVER use default, aerospike, or main."
check "Namespace 'test' exists out of the box" "${SKILL} critical rules" \
  asinfo_has "namespaces" "(^|;)test(;|$)"
check "Namespace 'default' does not exist" "${SKILL} critical rules" \
  bash -c "! docker exec ${CONTAINER} asinfo -v namespaces | grep -qE '(^|;)default(;|\$)'"

# cluster-name is mandatory from 7.0.0, which is why the floor is 7.0.
check "cluster-name is a service config key" "${SKILL} local config" \
  asinfo_has "get-config:context=service" "cluster-name="

# Expiry: nsup-period drives expiration, default-ttl sets the record default.
check "nsup-period governs expiration" "${SKILL} TTL and NSUP" \
  asinfo_has "get-config:context=namespace;id=test" "nsup-period="
check "default-ttl is a namespace config key" "${SKILL} TTL and NSUP" \
  asinfo_has "get-config:context=namespace;id=test" "default-ttl="

# The client port the skill tells users to map.
check "Client port 3000 is reachable from the host" "${SKILL} ports" \
  bash -c "exec 3<>/dev/tcp/127.0.0.1/3000"

echo
echo "${passed} claim(s) verified, ${failed} failed."
[[ "${failed}" -eq 0 ]]
