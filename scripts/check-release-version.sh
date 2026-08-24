#!/usr/bin/env bash
# Check that a release tag is a stable semantic version that moves the project forward.
#
# Called by .github/workflows/release-version.yml, the gate publish-registries.yml runs
# before it contacts a registry. Also runnable by hand before cutting a release:
#
#   ./scripts/check-release-version.sh --tag v1.2.0
#
# Three rules, checked in this order so the failure names the actual problem:
#
#   1. Format    exactly vMAJOR.MINOR.PATCH -- decimal, no leading zeros.
#   2. Stability no prerelease suffix, no build metadata, and the release is not
#                flagged as a prerelease on GitHub. A release publishes to registries
#                and neither registry documents a way to delete a submission, so a
#                release candidate must not be able to reach one.
#   3. Ordering  strictly greater than the highest tag already in the repository.
#                Needs the full tag list, which a shallow checkout does not have.
#
# Keep the rules here rather than in the workflow, so cutting a release is not the
# first time anyone finds out the tag is wrong. See docs/PUBLISHING.md.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TAG=""
FLAGGED_PRERELEASE="false"
CHECK_ORDERING=1

# The one definition of an acceptable tag. Alternation rather than [0-9]+ rejects the
# leading zeros the spec forbids: v1.02.3 is not v1.2.3 by another name.
STABLE='^v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'

usage() {
  cat >&2 <<'EOF'
Usage: check-release-version.sh --tag vX.Y.Z [options]

  --tag TAG                  Release tag to check (required).
  --flagged-prerelease BOOL  Whether GitHub marked the release a prerelease.
                             true or false. Default: false
  --skip-ordering            Check format and stability only. For a tree without
                             the full tag history.
EOF
  exit 2
}

# Single ? on purpose: an omitted value is a caller bug, but an empty one is what an
# unset workflow expression looks like, and that deserves this script's own message.
while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag) TAG="${2?--tag needs a value}"; shift 2 ;;
    --flagged-prerelease) FLAGGED_PRERELEASE="${2?--flagged-prerelease needs a value}"; shift 2 ;;
    --skip-ordering) CHECK_ORDERING=0; shift ;;
    -h|--help) usage ;;
    *) echo "Unknown option: $1" >&2; usage ;;
  esac
done

[[ -n "${TAG}" ]] || { echo "--tag is required." >&2; usage; }

# Anything other than the two literals is a caller bug, most likely an unset workflow
# expression. Rejecting it keeps a typo from reading as "not a prerelease".
case "${FLAGGED_PRERELEASE}" in
  true|false) ;;
  *) echo "--flagged-prerelease takes true or false, got \"${FLAGGED_PRERELEASE}\"." >&2; exit 2 ;;
esac

# Compares two vX.Y.Z tags numerically. Equal is not newer.
newer_than() {
  local IFS=.
  local -a new old
  read -r -a new <<<"${1#v}"
  read -r -a old <<<"${2#v}"

  local i
  for i in 0 1 2; do
    if ((new[i] > old[i])); then return 0; fi
    if ((new[i] < old[i])); then return 1; fi
  done
  return 1
}

if [[ ! "${TAG}" =~ ${STABLE} ]]; then
  echo "Release tag \"${TAG}\" is not a stable semantic version." >&2
  echo >&2
  if [[ "${TAG}" =~ ^v?(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)[-+] ]]; then
    echo "It carries a prerelease or build suffix. This repository releases stable" >&2
    echo "versions only, because a release submits to registries and no registry" >&2
    echo "documents a way to delete a submission." >&2
  elif [[ "${TAG}" =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]]; then
    echo "Add the v prefix: v${TAG}" >&2
  else
    echo "Expected exactly vMAJOR.MINOR.PATCH, for example v1.4.0: no prerelease" >&2
    echo "suffix, no build metadata, no leading zeros, no extra components." >&2
  fi
  exit 1
fi

if [[ "${FLAGGED_PRERELEASE}" == "true" ]]; then
  echo "Release ${TAG} is flagged as a prerelease on GitHub." >&2
  echo >&2
  echo "The tag is well formed, but this repository releases stable versions only." >&2
  echo "Clear \"Set as a pre-release\" on the release, or cut it as a draft instead:" >&2
  echo "a draft publishes nothing until it is released." >&2
  exit 1
fi

if [[ "${CHECK_ORDERING}" -eq 0 ]]; then
  echo "${TAG} is a stable semantic version. Ordering not checked (--skip-ordering)."
  exit 0
fi

if ! git -C "${ROOT}" rev-parse --git-dir >/dev/null 2>&1; then
  echo "${ROOT} is not a git repository, so the ordering check cannot run." >&2
  echo "Pass --skip-ordering to check the tag format alone." >&2
  exit 3
fi

# Tags that predate this check, or that some other tooling created, are not the thing
# being released -- ignore them rather than fail on them.
highest=""
while read -r existing; do
  [[ -n "${existing}" ]] || continue
  # A release creates its tag before this runs, so the tag under test is already in
  # the list and cannot be compared against itself. The cost is that re-releasing a
  # version that already exists reads as new; git cannot tell the two apart.
  [[ "${existing}" == "${TAG}" ]] && continue
  [[ "${existing}" =~ ${STABLE} ]] || continue
  if [[ -z "${highest}" ]] || newer_than "${existing}" "${highest}"; then
    highest="${existing}"
  fi
done < <(git -C "${ROOT}" tag --list 'v*')

if [[ -z "${highest}" ]]; then
  echo "${TAG} is a stable semantic version, and the first release. Nothing to compare."
  exit 0
fi

if ! newer_than "${TAG}" "${highest}"; then
  echo "Release tag ${TAG} does not move the version forward." >&2
  echo >&2
  echo "The highest tag already in this repository is ${highest}. Bump the major," >&2
  echo "minor, or patch above it. If ${highest} looks wrong, a shallow clone without" >&2
  echo "the full tag history reports the wrong answer here." >&2
  exit 1
fi

echo "${TAG} is a stable semantic version and supersedes ${highest}."
