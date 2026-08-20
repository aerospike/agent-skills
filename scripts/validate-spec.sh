#!/usr/bin/env bash
# Check every skill under skills/ against the Agent Skills specification using the
# official reference validator (agentskills/agentskills, skills-ref).
#
# This is deliberately separate from scripts/validate-skill.sh: that script runs a
# third-party linter whose checks are a superset of the spec (links, token counts,
# file layout). This one answers only "does the frontmatter conform to the standard",
# which is what registries validate against.
#
# Keep SKILLS_REF_REF in sync with .github/workflows/spec-conformance.yml.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="${ROOT}/skills"
# The compiled skill is what registries fetch and validate, so it must conform too.
PUBLISHED_DIR="${ROOT}/compiled-skills/aerospike"
SKILLS_REF_REF="69ef37e9424c0a7ea9dd2293b559e43ec8176379"

if ! command -v skills-ref >/dev/null 2>&1; then
  cat >&2 <<EOF
skills-ref not found on PATH. It has no PyPI release, so install it from source
(requires Python 3.11+):

  python3 -m venv .venv && . .venv/bin/activate
  pip install "git+https://github.com/agentskills/agentskills.git@${SKILLS_REF_REF}#subdirectory=skills-ref"

EOF
  exit 3
fi

# skills-ref validates one directory per invocation, so loop and aggregate rather
# than exiting on the first failure -- one run should report every problem.
skill_dirs=()
for skill_dir in "${SKILLS_DIR}"/*/; do
  [[ -f "${skill_dir}SKILL.md" ]] && skill_dirs+=("${skill_dir%/}")
done
[[ -f "${PUBLISHED_DIR}/SKILL.md" ]] && skill_dirs+=("${PUBLISHED_DIR}")

failed=()
checked=0
for skill_dir in "${skill_dirs[@]}"; do
  checked=$((checked + 1))
  if ! skills-ref validate "${skill_dir}"; then
    failed+=("$(basename "${skill_dir}")")
  fi
done

if [[ "${checked}" -eq 0 ]]; then
  echo "No skills found under ${SKILLS_DIR}/ -- expected at least one SKILL.md." >&2
  exit 1
fi

if [[ "${#failed[@]}" -gt 0 ]]; then
  echo >&2
  echo "Spec conformance failed for ${#failed[@]} of ${checked} skill(s): ${failed[*]}" >&2
  echo "The spec allows only these frontmatter keys: name, description, license," >&2
  echo "compatibility, metadata, allowed-tools. Put anything else under metadata." >&2
  echo "See https://agentskills.io/specification" >&2
  exit 1
fi

echo "All ${checked} skill(s) conform to the Agent Skills specification."
