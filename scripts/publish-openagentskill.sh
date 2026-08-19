#!/usr/bin/env bash
# Submit every skill under skills/ to openagentskill.com.
#
# Called by .github/workflows/publish-registries.yml, and runnable by hand for
# debugging. Submission is idempotent: a duplicate response counts as success, so
# re-running on a later release refreshes rather than errors.
#
# Docs: https://www.openagentskill.com/submit
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API="${OAS_API:-https://openagentskill.com/api}"
REPO_URL=""
AGENT_ID="aerospike-agent-skills-ci"
RECEIPTS=""
DRY_RUN=0

usage() {
  cat >&2 <<'EOF'
Usage: publish-openagentskill.sh --repo-url URL [options]

  --repo-url URL     Public GitHub URL of this repository (required).
  --agent-id ID      Value for submittedByAgent. Default: aerospike-agent-skills-ci
  --receipts FILE    Append one JSON receipt per skill to FILE.
  --dry-run          Render and check payloads; make no network calls.
EOF
  exit 2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-url) REPO_URL="${2:?--repo-url needs a value}"; shift 2 ;;
    --agent-id) AGENT_ID="${2:?--agent-id needs a value}"; shift 2 ;;
    --receipts) RECEIPTS="${2:?--receipts needs a value}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage ;;
    *) echo "Unknown option: $1" >&2; usage ;;
  esac
done

[[ -n "${REPO_URL}" ]] || { echo "--repo-url is required." >&2; usage; }
for tool in curl jq; do
  command -v "${tool}" >/dev/null 2>&1 || { echo "${tool} is required." >&2; exit 3; }
done

mapfile -t skill_dirs < <(find "${ROOT}/skills" -mindepth 1 -maxdepth 1 -type d | sort)
[[ "${#skill_dirs[@]}" -gt 0 ]] || { echo "No skills found under skills/." >&2; exit 1; }

# The /validate endpoint fetches SKILL.md over the public URL, so it cannot succeed
# while the repository is private or internal. Skipped in dry-run for that reason:
# calling it before the repo is public reports a failure that looks like our bug.
if [[ "${DRY_RUN}" -eq 0 ]]; then
  echo "Resolving skill paths via ${API}/skills/validate"
  validate_body="$(jq -cn --arg repository "${REPO_URL}" '{repository: $repository}')"
  validate_out="$(curl -sS -X POST "${API}/skills/validate" \
    -H 'Content-Type: application/json' \
    -d "${validate_body}" \
    -w '\n%{http_code}')"
  validate_code="$(tail -n1 <<<"${validate_out}")"
  if [[ "${validate_code}" != 2* ]]; then
    echo "Registry could not read ${REPO_URL} (HTTP ${validate_code})." >&2
    echo "This usually means the repository is not publicly readable yet." >&2
    sed '$d' <<<"${validate_out}" >&2
    exit 1
  fi
fi

failures=0
for skill_dir in "${skill_dirs[@]}"; do
  skill_md="${skill_dir}/SKILL.md"
  [[ -f "${skill_md}" ]] || continue
  name="$(basename "${skill_dir}")"
  skill_path="skills/${name}/SKILL.md"

  payload="$(jq -cn \
    --arg repository "${REPO_URL}" \
    --arg skillPath "${skill_path}" \
    --arg agent "${AGENT_ID}" \
    '{repository: $repository, skillPath: $skillPath, submissionSource: "agent", submittedByAgent: $agent}')"

  if [[ "${DRY_RUN}" -eq 1 ]]; then
    # Assert the payload carries what the API documents as required, so a dry run
    # catches a malformed request instead of deferring it to the real submission.
    if ! jq -e '(.repository | length > 0) and (.skillPath | length > 0)' >/dev/null <<<"${payload}"; then
      echo "DRY RUN: payload for ${name} is missing required fields." >&2
      failures=$((failures + 1))
      continue
    fi
    echo "DRY RUN ${name}: POST ${API}/skills/submit"
    jq . <<<"${payload}"
    continue
  fi

  echo "Submitting ${name}"
  response="$(curl -sS -X POST "${API}/skills/submit" \
    -H 'Content-Type: application/json' \
    -d "${payload}" \
    -w '\n%{http_code}')"
  code="$(tail -n1 <<<"${response}")"
  body="$(sed '$d' <<<"${response}")"

  status="submitted"
  if [[ "${code}" != 2* ]]; then
    # Re-submitting an existing skill is the expected steady state on every release
    # after the first, so treat it as success rather than failing the workflow.
    if grep -qiE 'already|duplicate|exists' <<<"${body}"; then
      status="already-listed"
      echo "  ${name}: already listed, nothing to do."
    else
      echo "  ${name}: submission failed (HTTP ${code})." >&2
      echo "  ${body}" >&2
      failures=$((failures + 1))
      continue
    fi
  fi

  if [[ -n "${RECEIPTS}" ]]; then
    jq -cn \
      --arg registry "openagentskill" \
      --arg skill "${name}" \
      --arg status "${status}" \
      --argjson response "$(jq -c '.' <<<"${body}" 2>/dev/null || echo '{}')" \
      '{registry: $registry, skill: $skill, status: $status, response: $response}' \
      >>"${RECEIPTS}"
  fi

  # The status token is the only way to poll this submission later, but it is
  # private -- keep it out of logs and let the caller archive the receipts file.
  jq -r '"  " + (.submission.status // "submitted") + " id=" + (.submission.id // "unknown")' \
    <<<"${body}" 2>/dev/null || true
done

if [[ "${failures}" -gt 0 ]]; then
  echo "openagentskill: ${failures} skill(s) failed." >&2
  exit 1
fi

echo "openagentskill: done ($([[ "${DRY_RUN}" -eq 1 ]] && echo "dry run" || echo "submitted"))."
