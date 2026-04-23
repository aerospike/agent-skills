#!/usr/bin/env bash
# Validate the packaged Agent Skill with agent-ecosystem/skill-validator.
# Version is pinned to match .github/workflows/skill-validator.yml and CONTRIBUTING.md.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Multi-skill root: skill-validator discovers each subdirectory that contains SKILL.md.
SKILL_DIR="${ROOT}/skills"

usage() {
  echo "Usage: $0 [--ci]" >&2
  echo "  --ci   Add --emit-annotations for GitHub Actions (noisy locally)." >&2
  exit 2
}

extra_args=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ci) extra_args+=(--emit-annotations) ;;
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

exec skill-validator check --strict \
  --allow-flat-layouts --allow-extra-frontmatter \
  "${extra_args[@]}" \
  "${SKILL_DIR}/"
