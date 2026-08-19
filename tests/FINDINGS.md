# Findings ledger

Every finding from testing the skills before publication, with the decision taken.
Opened for [AIE-16](https://aerospike.atlassian.net/browse/AIE-16). Design:
[`docs/superpowers/specs/2026-08-19-skill-testing-and-publish-shape-design.md`](../docs/superpowers/specs/2026-08-19-skill-testing-and-publish-shape-design.md).

| # | Finding | Decision | Status |
|---|---------|----------|--------|
| F1 | The compiled artifact cites 19 reference files by bare filename (33 mentions) and carries no URLs, against 246 in the source. | **Accepted.** The stripped digest is the measured, intended shape — 95% accuracy at ~8.5k tokens, tying the full monolith within its confidence interval. Mitigated by naming the repository in the generated header so a cited filename resolves once the repo is public. | Closed |
| F2 | `labeled_sections` split reference files on any standalone bold line, so a bolded URL, seven enumerated headings, and a "Gotcha" heading were read as section boundaries. 4,880 characters of rule content were misfiled across three files. Only one line of shipped output changed when fixed — the stripped renderer keeps a rule's first paragraph and its bullet lists — but that line is the pointer to the data-modeling guide. | **Fixed.** Only the five labels in `references/_template.md` split a file. | Closed |
| F3 | Publishing submitted three skill folders rather than the one compiled artifact the evaluation validated. | **Fixed.** Registries receive `compiled-skills/aerospike/SKILL.md`. The three folders remain the authoring source. | Closed |
| F4 | Both validators were hardcoded to `skills/`, so the artifact registries fetch was never checked. | **Fixed.** Both now cover `compiled-skills/aerospike/`. | Closed |
| F5 | The README install table omitted Gemini, though AIE-16 requires a verified Gemini install. | **Fixed.** Gemini CLI documented alongside Claude Code and Cursor. | Closed |
| F6 | No skill declares a supported server version range, leaving "current server behavior" without a target. | **Fix planned.** Declare `metadata.server_versions: "7.0+"`; the canonical local config sets `cluster-name`, mandatory since 7.0.0. | Open — testing plan |
| F7 | `aerospike-data-modeling` has never been measured: absent from the evaluation harness `source_skills` and from all 61 tasks. | **Fix planned.** Add it to the harness with its own task file. | Open — testing plan |
| F8 | Skill folders are self-contained; no relative link escapes its own folder. | **No action.** Verified across `skills/`. A check will lock it in. | Open — testing plan |
| F9 | `dev-ttl-void-time` failed on every variant including the baseline in evaluation run `20260623-101343`, attributed to the task rubric rather than a skill defect. | **Carried forward.** Re-examine when the harness is next run. | Open — testing plan |
| F10 | The compiled skill cites two GitHub URLs that return HTTP 404 to a link checker: `https://github.com/aerospike/agent-skills` in the generated header, and `https://github.com/aerospike/data-modeling-guide` in a data-modeling rule. Neither repository is public yet. | **Open.** `validate-skill.sh` now exits 1 on these, so the skill-validator CI job stays red until both repositories are public. Publishing is already gated on this repository being public; the guide repository needs the same confirmation. | Open — needs a decision |
| F11 | `skill-validator` warns that the published description reads as a keyword list (13 comma-separated segments). | **Accepted.** The description is the only input to whether an agent loads the skill, so breadth of matchable phrasing is the point. | Closed |
| F12 | `skill-validator` warns the published body is 9,163 tokens against a recommended 5,000. | **Accepted.** Measured, not incidental: the evaluation sized the stripped digest at roughly 8.5k tokens and found it as accurate as the full monolith. | Closed |
| F13 | `skills-ref` requires Python 3.11 or newer, but the repository's other tooling runs on the system Python, which is 3.10 here. | **Fixed.** Contributor setup names `python3.11` explicitly when creating the validator virtualenv. | Closed |
