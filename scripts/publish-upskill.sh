#!/usr/bin/env bash
# Submit the compiled skill (compiled-skills/aerospike) to upskill (Autoloops).
#
# Called by .github/workflows/publish-registries.yml, and runnable by hand for
# debugging.
#
# Docs: https://github.com/Autoloops/upskill
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_URL=""
REF="main"
RECEIPTS=""
DRY_RUN=0
CONFIG_PATH="${UPSKILL_CONFIG:-${HOME}/.config/upskill/config.json}"

usage() {
  cat >&2 <<'EOF'
Usage: publish-upskill.sh --repo-url URL [options]

  --repo-url URL     Public GitHub URL of this repository (required).
  --ref REF          Branch or tag the submitted tree URLs point at. Default: main
  --receipts FILE    Append one JSON receipt per skill to FILE.
  --dry-run          Render the submissions; make no network calls.
EOF
  exit 2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-url) REPO_URL="${2:?--repo-url needs a value}"; shift 2 ;;
    --ref) REF="${2:?--ref needs a value}"; shift 2 ;;
    --receipts) RECEIPTS="${2:?--receipts needs a value}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage ;;
    *) echo "Unknown option: $1" >&2; usage ;;
  esac
done

[[ -n "${REPO_URL}" ]] || { echo "--repo-url is required." >&2; usage; }
command -v jq >/dev/null 2>&1 || { echo "jq is required." >&2; exit 3; }

# One published artifact, compiled from the three skills under skills/.
SKILL_NAME="aerospike"
SKILL_DIR_REL="compiled-skills/${SKILL_NAME}"
[[ -f "${ROOT}/${SKILL_DIR_REL}/SKILL.md" ]] || {
  echo "${SKILL_DIR_REL}/SKILL.md not found. Run: python3 scripts/compile-agents.py --write" >&2
  exit 1
}

if [[ "${DRY_RUN}" -eq 0 ]]; then
  command -v upskill >/dev/null 2>&1 || {
    echo "upskill not found on PATH. Install with: npm install -g @autoloops/upskill" >&2
    exit 3
  }

  upskill install
  # Submissions are disabled by default, and `upskill submit` exits 0 while doing
  # nothing when they are off. Without this the workflow reports a successful
  # publish that never happened, so verify the setting actually took effect.
  upskill config set submissions true

  if [[ -f "${CONFIG_PATH}" ]]; then
    # The CLI's setting is named "submissions" but persists as "submissionsEnabled".
    # Checking the display name found no key at all, read that as "disabled", and
    # aborted a correctly configured publish. Accept either spelling, and treat a
    # missing key as unknown rather than false: only an explicit false is grounds
    # to refuse, because only that means submit would no-op.
    # has() rather than `//`: jq's alternative operator treats false as absent, so
    # `.submissionsEnabled // "unknown"` would report an explicitly disabled config
    # as unknown and proceed -- losing the one case this check exists to catch.
    enabled="$(jq -r '
      if has("submissionsEnabled") then (.submissionsEnabled | tostring)
      elif has("submissions") then (.submissions | tostring)
      else "unknown" end' "${CONFIG_PATH}")"
    if [[ "${enabled}" == "false" ]]; then
      echo "upskill submissions are disabled in ${CONFIG_PATH}; refusing to" >&2
      echo "continue, because submit would silently no-op." >&2
      exit 1
    fi
    if [[ "${enabled}" == "true" ]]; then
      echo "Verified submissions are enabled in ${CONFIG_PATH}."
    else
      echo "::warning::Could not find a submissions setting in ${CONFIG_PATH}. The CLI may have renamed it."
      echo "::warning::Treat this run's upskill results as unconfirmed and check the listing by hand."
    fi
  else
    echo "::warning::Could not find ${CONFIG_PATH} to confirm submissions are enabled."
    echo "::warning::Treat this run's upskill results as unconfirmed and check the listing by hand."
  fi
fi

failures=0
for name in "${SKILL_NAME}"; do
  # Submit a branch URL rather than the release tag so the listing tracks later
  # updates instead of pinning to one release.
  target="${REPO_URL}/tree/${REF}/${SKILL_DIR_REL}"

  if [[ "${DRY_RUN}" -eq 1 ]]; then
    echo "DRY RUN ${name}: upskill submit ${target}"
    continue
  fi

  echo "Submitting ${name}"
  status="submitted"
  if ! upskill submit "${target}"; then
    echo "  ${name}: upskill submit failed." >&2
    failures=$((failures + 1))
    continue
  fi

  if [[ -n "${RECEIPTS}" ]]; then
    jq -cn \
      --arg registry "upskill" \
      --arg skill "${name}" \
      --arg status "${status}" \
      --arg target "${target}" \
      '{registry: $registry, skill: $skill, status: $status, target: $target}' \
      >>"${RECEIPTS}"
  fi
done

if [[ "${failures}" -gt 0 ]]; then
  echo "upskill: ${failures} skill(s) failed." >&2
  exit 1
fi

echo "upskill: done ($([[ "${DRY_RUN}" -eq 1 ]] && echo "dry run" || echo "submitted"))."
