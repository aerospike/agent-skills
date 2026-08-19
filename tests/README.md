# Tests

| Path | What it covers | How to run |
|------|----------------|------------|
| `unit/` | The compiler, the publish scripts, and documentation references | `python3 -m pytest tests/unit -v` |
| `unit/test_payload_integrity.py` | That every skill folder is self-contained — no link leaves its own folder, and every relative link resolves | `python3 -m pytest tests/unit/test_payload_integrity.py -v` |
| `triggers/` | Whether the published description fires on the right prompts | `python3 tests/run_triggers.py` — see [`triggers/README.md`](triggers/README.md) |
| `content/verify-server-claims.sh` | The getting-started skill's claims against a real server | `./tests/content/verify-server-claims.sh` (needs Docker) |
| `tasks/` | End-to-end task prompts, read by the evaluation harness through its submodule | `python3 -m pytest tests/unit/test_task_corpus.py -v` for their shape; the prompts themselves run in [`agent-skills-eval`](https://github.com/citrusleaf/agent-skills-eval) |
| `FINDINGS.md` | Ledger of findings from pre-publication testing, with decisions | — |

`verify-server-claims.sh` boots `aerospike/aerospike-server:latest`, the Community image the
skill tells a new user to run, and removes the container when it exits. Pass `--tag` to check
the claims against a specific release instead. It binds host ports 3000-3002, so stop any
Aerospike already holding them first. Not every published tag ships `asinfo` — eight
simultaneous failures mean the tool is missing from the image, not that eight claims drifted
at once.

## Before publishing

```bash
python3 -m pytest tests/unit -v                        # compiler, publishing, docs
python3 scripts/compile-agents.py --shape stripped --check
./scripts/validate-spec.sh                             # needs skills-ref
./scripts/validate-skill.sh                            # needs skill-validator
./tests/content/verify-server-claims.sh                # needs Docker

# Trigger accuracy. Manual because it needs a model API key, which this project
# does not put in CI. Exits non-zero below the threshold in triggers/README.md.
set -a && . ./agent_api_key.env && set +a              # gitignored; holds CURSOR_API_KEY
python3 tests/run_triggers.py --model composer-2.5 --min-accuracy 0.88
```

`skills-ref` needs Python 3.11 or newer; create its virtualenv with `python3.11 -m venv .venv`.

### Checks a person has to run

These are not automated, and nothing in CI will notice if they are skipped.

- **A live evaluation run** in [`agent-skills-eval`](https://github.com/citrusleaf/agent-skills-eval). The mock run in CI measures plumbing, not accuracy. A live run costs real money, so it is a deliberate act. Check `n_tasks` against the expected total — a stale submodule pointer silently scores the old corpus (see [F19](FINDINGS.md)).
- **The client API signature pass.** Compare the constructor, `put`, `get`, `operate`, and the batch read entry point in each skill's `examples.md` and `references/` against current official SDK documentation. Record the date, the SDK versions, and anything that drifted, as [F20](FINDINGS.md) does.
- **These two URLs resolve** (skill-validator skips link checks on `compiled-skills/`; both 404 until the repositories are public — see [F10](FINDINGS.md)):
  - `https://github.com/aerospike/agent-skills`
  - `https://github.com/aerospike/data-modeling-guide`
