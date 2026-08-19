# Trigger accuracy

One skill is published, so cross-triggering between our own skills is designed out
rather than measured. What remains is whether a single description fires across all
three domains and stays quiet outside them.

`../run_triggers.py` shows a model only the published skill's name and description
plus one user message, which is the same information an agent harness has when it
decides whether to load a skill. It does not load the skill body.

## Corpus

| File | Cases | Expectation |
|------|-------|-------------|
| `positives.yaml` | 12 | Must load the skill — four per authoring domain |
| `negatives.yaml` | 8 | Must not load it — excluded Aerospike topics and unrelated technology |
| `near-misses.yaml` | 5 | Must not load it — names Aerospike without needing guidance |

`domain` on each positive records which folder under `skills/` would have served the
prompt, so cross-triggering can be re-measured if those folders are ever published
separately.

## Threshold

CI fails below **0.92** overall accuracy, against `composer-2.5`.

That number is the first measured run rounded down, not a target chosen in advance.
A perfect score is explicitly not the goal: routing is stochastic, and a threshold set
at 1.0 would fail on noise. Raise it when a description change earns it.

| Date | Model | Accuracy | Precision | Recall |
|------|-------|----------|-----------|--------|
| 2026-08-19 | composer-2.5 | 0.920 | 1.000 | 0.833 |

The first run's two failures were both data-modeling positives, `pos-dm-key-design`
and `pos-dm-schema-review`: nothing over-fired, so the description under-reaches
design-time modeling rather than reaching too far.

## Running it

```bash
export CURSOR_API_KEY=cursor_...
python3 tests/run_triggers.py --model composer-2.5 --json /tmp/triggers.json
```

Without a key, score a recorded run instead:

```bash
python3 tests/run_triggers.py --offline recorded-verdicts.json
```

## When a case fails

A failing positive means the description does not reach that domain. A failing negative
or near-miss means it reaches too far. Either way the fix is the description in
`scripts/skills_compile/published_skill.yaml`, not the corpus — do not edit a case to
make the run green.
