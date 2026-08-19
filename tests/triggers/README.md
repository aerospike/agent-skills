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

CI fails below **0.88** overall accuracy, against `composer-2.5`.

That is the worst measured run minus one case, not a target chosen in advance. The
margin is deliberate and it is not a softer goal: routing is stochastic, and the runs
below show one or two cases flipping between identical invocations. A threshold set at
the measurement would go red on that noise alone, which trains people to ignore it.
One case is 0.04 across 25 cases. Raise it when a description change earns it.

| Date | Model | Accuracy | Precision | Recall | Failed |
|------|-------|----------|-----------|--------|--------|
| 2026-08-19 | composer-2.5 | 0.920 | 1.000 | 0.833 | `pos-dm-key-design`, `pos-dm-schema-review` |
| 2026-08-19 | composer-2.5 | 0.960 | 1.000 | 0.917 | `pos-dev-policy-timeouts` |
| 2026-08-19 | composer-2.5 | 0.920 | 1.000 | 0.833 | `pos-dev-cdt-map-update`, `pos-dm-schema-review` |

The first run used the original description. Both of its failures were data-modeling
positives while nothing over-fired, which said the description under-reached
design-time modeling rather than reaching too far: it offered to review client *code*
and to design a model *from requirements*, so reviewing an existing model fell between
those clauses, and key selection appeared only as a noun in the covered-concepts list.

Runs two and three followed a description that names both. `pos-dm-key-design` and
`pos-dm-schema-review` went from failing both times to passing three of four, and
precision stayed at 1.000, so the wider reach cost no over-firing. Read that as
suggestive rather than settled — it is four case-observations.

What runs two and three mainly establish is the variance. Their failures are different
cases, and neither is one the description change touched, so they are noise. That is
what the threshold's margin is sized against.

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
