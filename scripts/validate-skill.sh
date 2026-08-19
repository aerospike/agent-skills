#!/usr/bin/env bash
# Validate the packaged Agent Skill with agent-ecosystem/skill-validator.
# Version is pinned to match .github/workflows/skill-validator.yml and CONTRIBUTING.md.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Multi-skill roots: skill-validator discovers each subdirectory containing SKILL.md.
# compiled-skills/ holds the published artifact, which must be linted like the sources.
SKILL_ROOTS=("${ROOT}/skills" "${ROOT}/compiled-skills")

usage() {
  echo "Usage: $0 [--ci | --summary]" >&2
  echo "  --ci        GitHub Actions: --emit-annotations and no --strict (warnings exit 2)." >&2
  echo "  --summary   Markdown report for a job summary: no --strict, no annotations." >&2
  echo "              Default local run uses --strict so warnings fail the script." >&2
  exit 2
}

extra_args=()
strict_flag=(--strict)
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ci)
      extra_args+=(--emit-annotations)
      strict_flag=()
      ;;
    --summary)
      # No annotations: they would be interleaved into the markdown report.
      extra_args+=(-o markdown)
      strict_flag=()
      ;;
    -h|--help) usage ;;
    *) echo "Unknown option: $1" >&2; usage ;;
  esac
  shift
done

if ! command -v skill-validator >/dev/null 2>&1; then
  echo "skill-validator not found on PATH. Install with:" >&2
  echo "  go install github.com/agent-ecosystem/skill-validator/cmd/skill-validator@v1.5.5" >&2
  echo "and ensure \$(go env GOPATH)/bin is on your PATH." >&2
  exit 3
fi

# No --allow-extra-frontmatter: the Agent Skills spec allows only six frontmatter
# keys, so an unexpected key must surface here rather than being waived.
# Run per root and surface the worst exit code, so one clean root cannot mask a
# failure in the other. Exit 2 means warnings-only when --strict is off.
worst=0
for root in "${SKILL_ROOTS[@]}"; do
  skip_args=()
  # Skip only the links group for compiled-skills/. The compiled body's links
  # are inherited from skills/, which this loop still link-checks in full, and
  # two of the URLs (github.com/aerospike/agent-skills and
  # github.com/aerospike/data-modeling-guide) cannot resolve until those
  # repositories are public. A blanket --skip links on both roots would hide
  # real authoring bugs in skills/.
  if [[ "${root}" == "${ROOT}/compiled-skills" ]]; then
    skip_args+=(--skip links)
  fi
  set +e
  skill-validator check \
    "${strict_flag[@]}" \
    --allow-flat-layouts \
    "${skip_args[@]}" \
    "${extra_args[@]}" \
    "${root}/"
  code=$?
  set -e
  # skill-validator exits 1 for errors and 2 for warnings-only, so 1 outranks 2.
  # A numeric max would let warnings in one root mask errors in another.
  if [[ "${code}" -eq 1 || "${worst}" -eq 1 ]]; then
    worst=1
  elif [[ "${code}" -ne 0 ]]; then
    worst="${code}"
  fi
done
exit "${worst}"
