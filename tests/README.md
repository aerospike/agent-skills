# Tests

| Path | What it covers | How to run |
|------|----------------|------------|
| `unit/` | The compiler, the publish scripts, and documentation references | `python3 -m pytest tests/unit -v` |
| `FINDINGS.md` | Ledger of findings from pre-publication testing, with decisions | — |

Trigger-accuracy prompts, end-to-end task files, and the server-claim verification
script arrive with the testing plan; see
[`docs/superpowers/specs/2026-08-19-skill-testing-and-publish-shape-design.md`](../docs/superpowers/specs/2026-08-19-skill-testing-and-publish-shape-design.md).

## Before publishing

```bash
python3 -m pytest tests/unit -v                        # compiler, publishing, docs
python3 scripts/compile-agents.py --shape stripped --check
./scripts/validate-spec.sh                             # needs skills-ref
./scripts/validate-skill.sh                            # needs skill-validator
```

Confirm these two URLs resolve (skill-validator skips link checks on `compiled-skills/`; both 404 until the repositories are public):

- `https://github.com/aerospike/agent-skills`
- `https://github.com/aerospike/data-modeling-guide`

`skills-ref` needs Python 3.11 or newer; create its virtualenv with `python3.11 -m venv .venv`.
