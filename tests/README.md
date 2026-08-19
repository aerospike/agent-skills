# Tests

| Path | What it covers | How to run |
|------|----------------|------------|
| `unit/` | The compiler, the publish scripts, and documentation references | `python3 -m pytest tests/unit -v` |
| `unit/test_payload_integrity.py` | That every skill folder is self-contained — no link leaves its own folder, and every relative link resolves | `python3 -m pytest tests/unit/test_payload_integrity.py -v` |
| `triggers/` | Whether the published description fires on the right prompts | `python3 tests/run_triggers.py` — see [`triggers/README.md`](triggers/README.md) |
| `FINDINGS.md` | Ledger of findings from pre-publication testing, with decisions | — |

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
