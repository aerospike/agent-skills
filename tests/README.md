# Tests

| Path | What it covers | How to run |
|------|----------------|------------|
| `unit/` | The compiler, the publish scripts, and documentation references | `python3 -m pytest tests/unit -v` |
| `unit/test_payload_integrity.py` | That every skill folder is self-contained — no link leaves its own folder, and every relative link resolves | `python3 -m pytest tests/unit/test_payload_integrity.py -v` |
| `triggers/` | Whether the published description fires on the right prompts | `python3 tests/run_triggers.py` — see [`triggers/README.md`](triggers/README.md) |
| `content/verify-server-claims.sh` | The getting-started skill's claims against a real server | `./tests/content/verify-server-claims.sh` (needs Docker) |
| `tasks/` | End-to-end task prompts, read by the evaluation harness through its submodule | `python3 -m pytest tests/unit/test_task_corpus.py -v` for their shape; the prompts themselves run in [`agent-skills-eval`](https://github.com/aerospike/agent-skills-eval) |
| `FINDINGS.md` | Ledger of findings from pre-publication testing, with decisions | — |

`verify-server-claims.sh` boots `aerospike/aerospike-server:latest`, the Community image the
skill tells a new user to run, and removes the container when it exits. Pass `--tag` to check
the claims against a specific release instead. It binds host ports 3000-3002, so stop any
Aerospike already holding them first.

Why these checks exist, and what else was considered, is in
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
