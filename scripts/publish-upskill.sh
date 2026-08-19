#!/usr/bin/env bash
# Submit every skill under skills/ to upskill (Autoloops).
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

mapfile -t skill_dirs < <(find "${ROOT}/skills" -mindepth 1 -maxdepth 1 -type d | sort)
[[ "${#skill_dirs[@]}" -gt 0 ]] || { echo "No skills found under skills/." >&2; exit 1; }

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
    if ! jq -e '.submissions == true' >/dev/null "${CONFIG_PATH}"; then
      echo "upskill submissions are still disabled in ${CONFIG_PATH}; refusing to" >&2
      echo "continue, because submit would silently no-op." >&2
      exit 1
    fi
    echo "Verified submissions are enabled in ${CONFIG_PATH}."
  else
    echo "::warning::Could not find ${CONFIG_PATH} to confirm submissions are enabled."
    echo "::warning::Treat this run's upskill results as unconfirmed and check the listing by hand."
  fi
fi

failures=0
for skill_dir in "${skill_dirs[@]}"; do
  [[ -f "${skill_dir}/SKILL.md" ]] || continue
  name="$(basename "${skill_dir}")"
  # Submit a branch URL rather than the release tag so the listing tracks later
  # updates instead of pinning to one release.
  target="${REPO_URL}/tree/${REF}/skills/${name}"

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
