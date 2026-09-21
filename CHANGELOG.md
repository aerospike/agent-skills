# Changelog

What changed in the published skill, `compiled-skills/aerospike`.

This file tracks the **artifact a consumer installs**, not every commit. The version
here is the one in the skill's own frontmatter (`metadata.version`) and the one a
release is tagged with; [`scripts/check-release-version.sh`](scripts/check-release-version.sh)
fails a release where those disagree.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions are
[semantic](https://semver.org/), with the caveat that this package is prose rather
than an API — see [What a version means here](#what-a-version-means-here).

## [Unreleased]

## [1.1.0] — unreleased

### Changed

- **`SKILL.md` is now a router, not the whole corpus.** It names each rule and states
  its instruction in one sentence; the reasoning, worked detail and documentation
  links live in a file shipped beside it. The always-loaded file dropped from roughly
  11,300 to 4,900 tokens, inside the Agent Skills spec's 5,000-token recommendation
  for the first time.
- **Rule names follow one prefix taxonomy.** `binop-operate-*` and `bin-operate-*`
  became `operate-*`, `singleton-client` became `client-singleton`, `official-put-get`
  became `single-put-get`, and `official-batch` became `batch-official-links`. Rules
  are grouped under their prefix in the listing.
- **Worked examples moved to `examples/`** and lost their `ex-` prefix. They are
  language-agnostic where they were previously Python-only, and name the full set of
  client languages in canonical order.

### Added

- **The package now ships 45 more files**: `references/` carries one file per rule and
  `examples/` carries eight worked examples. Previously the package was a single
  `SKILL.md`. A rule's file path is derivable from its heading — the header explains
  the rule — so an agent can navigate without a link.
- **The skill declares its own version** in `metadata.version`, so an installed copy
  can be identified without reference to the repository.
- A rule pointing agents at the Aerospike client repositories on GitHub and the
  `AI coding agent entry point` in each README, which is the authority for a client's
  API surface where the documentation is the authority for the operation.
- `references/aerospike-development-client-source-of-truth.md` and
  `references/aerospike-data-modeling-model-mental-model.md`.

### Fixed

- **The compiler no longer discards content silently.** It previously kept only the
  first paragraph of each rule, dropped every table, every `Why` and `See also`
  section, all prose inside `Prefer`/`Avoid`, and the continuation lines of wrapped
  bullets. Eighteen of thirty-five rules shipped truncated; one shipped a single
  sentence ending in a colon that introduced a table which had been removed. A
  coverage check now fails the build on these rather than letting them pass unnoticed.
- Nineteen documentation links that returned 404, from pages that moved under
  `aerospike.com/docs`. Every replacement was verified live.
- `scripts/validate-skill.sh` now runs on macOS (bash 3.2).

### Internal

- Release tags are checked against `metadata.version` in the published artifact, so a
  release cannot ship a skill that misreports its own version.
- openagentskill status tokens are redacted from the `registry-receipts` workflow
  artifact. See [`docs/PUBLISHING.md`](docs/PUBLISHING.md) for what the token is and
  why it is redacted regardless.

## [1.0.0] — 2026-08-26

First release, and the first submission to
[openagentskill](https://www.openagentskill.com/skills/aerospike-agent-skills-aerospike)
and upskill. A single compiled `SKILL.md` covering local setup, client development and
data-model design for the Aerospike core database.

## What a version means here

The package is documentation compiled into a skill, so the usual API reading of
semver does not map cleanly. What is used instead:

| Bump | Means |
|---|---|
| **Major** | A consumer's existing usage breaks — the skill is renamed or split, its description changes enough to alter when agents trigger it, or published file paths that rules cite are removed. |
| **Minor** | New rules, new reference or example files, or a restructuring of what ships that leaves the skill's name, description and purpose intact. |
| **Patch** | Corrections within existing rules: a wrong link, a stale fact, a typo. Nothing added or removed. |

Renaming a rule file is a **minor** bump when the old path was never published, and a
**major** one when it was. The 1.1.0 renames are minor for that reason — 1.0.0 shipped
`SKILL.md` alone, so no consumer could have depended on a reference path.

[1.1.0]: https://github.com/aerospike/agent-skills/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/aerospike/agent-skills/releases/tag/v1.0.0
