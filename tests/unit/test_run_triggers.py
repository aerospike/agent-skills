"""The trigger runner's corpus handling, verdict parsing, and scoring must be
correct without a model in the loop, so they are tested with recorded verdicts."""

import json
import pathlib
import textwrap

import pytest

from tests.run_triggers import (
    NO_SKILL,
    Metrics,
    TriggerCase,
    build_router_prompt,
    load_corpus,
    load_published_skill,
    main,
    parse_verdict,
    score,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CORPUS_DIR = REPO_ROOT / "tests" / "triggers"


def _write_corpus(tmp_path, body):
    (tmp_path / "cases.yaml").write_text(textwrap.dedent(body), encoding="utf-8")
    return tmp_path


def test_load_corpus_reads_every_yaml_file_and_normalizes_whitespace(tmp_path):
    _write_corpus(
        tmp_path,
        """
        - id: a
          prompt: >-
            one
            two
          expect: aerospike
          domain: aerospike-development
          why: because
        """,
    )

    cases = load_corpus(tmp_path)

    assert cases == [
        TriggerCase(
            id="a",
            prompt="one two",
            expect="aerospike",
            domain="aerospike-development",
            why="because",
        )
    ]


def test_load_corpus_rejects_a_duplicate_id(tmp_path):
    _write_corpus(
        tmp_path,
        """
        - id: a
          prompt: one
          expect: none
        - id: a
          prompt: two
          expect: none
        """,
    )

    with pytest.raises(ValueError, match="duplicate case id: a"):
        load_corpus(tmp_path)


def test_load_corpus_rejects_an_unknown_expectation(tmp_path):
    _write_corpus(
        tmp_path,
        """
        - id: a
          prompt: one
          expect: maybe
        """,
    )

    with pytest.raises(ValueError, match="expect must be"):
        load_corpus(tmp_path)


def test_load_corpus_rejects_an_empty_directory(tmp_path):
    with pytest.raises(ValueError, match="no trigger cases"):
        load_corpus(tmp_path)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("aerospike", "aerospike"),
        ("  aerospike.  ", "aerospike"),
        ("none", NO_SKILL),
        ("**none**", NO_SKILL),
        ("I would load aerospike for this.", "aerospike"),
        ("Probably not relevant, so none.", NO_SKILL),
        ("", "unparseable"),
        ("I am not sure", "unparseable"),
    ],
)
def test_parse_verdict_tolerates_the_ways_models_actually_reply(raw, expected):
    assert parse_verdict(raw, "aerospike") == expected


def test_score_counts_each_outcome_and_records_failures():
    cases = [
        TriggerCase("p1", "x", "aerospike"),
        TriggerCase("p2", "x", "aerospike"),
        TriggerCase("n1", "x", NO_SKILL),
        TriggerCase("n2", "x", NO_SKILL),
    ]
    verdicts = {
        "p1": "aerospike",
        "p2": NO_SKILL,
        "n1": NO_SKILL,
        "n2": "aerospike",
    }

    metrics = score(cases, verdicts, "aerospike")

    assert (metrics.total, metrics.correct) == (4, 2)
    assert metrics.accuracy == 0.5
    assert (metrics.true_positives, metrics.false_positives) == (1, 1)
    assert metrics.false_negatives == 1
    assert metrics.precision == 0.5
    assert metrics.recall == 0.5
    assert metrics.failures == (("p2", "aerospike", NO_SKILL), ("n2", NO_SKILL, "aerospike"))


def test_metrics_do_not_divide_by_zero_on_an_all_negative_corpus():
    cases = [TriggerCase("n1", "x", NO_SKILL)]

    metrics = score(cases, {"n1": NO_SKILL}, "aerospike")

    assert metrics.accuracy == 1.0
    assert metrics.precision == 0.0
    assert metrics.recall == 0.0


def test_router_prompt_carries_the_description_and_offers_only_two_answers():
    prompt = build_router_prompt("aerospike", "Covers Docker and modeling.", "how do I start?")

    assert "Covers Docker and modeling." in prompt
    assert "how do I start?" in prompt
    assert "aerospike" in prompt
    assert NO_SKILL in prompt


def test_load_published_skill_reads_the_shipped_description():
    name, description = load_published_skill(
        REPO_ROOT / "compiled-skills" / "aerospike" / "SKILL.md"
    )

    assert name == "aerospike"
    assert "Aerospike" in description
    assert "\n" not in description


def test_the_committed_corpus_loads_and_covers_all_three_domains():
    cases = load_corpus(CORPUS_DIR)
    domains = {c.domain for c in cases if c.expect == "aerospike"}

    assert len(cases) >= 20
    assert domains == {
        "aerospike-getting-started",
        "aerospike-development",
        "aerospike-data-modeling",
    }
    assert any(c.expect == NO_SKILL for c in cases)


def test_main_scores_a_recorded_run_offline_and_gates_on_the_threshold(tmp_path):
    corpus = _write_corpus(
        tmp_path,
        """
        - id: a
          prompt: one
          expect: aerospike
          domain: aerospike-development
        - id: b
          prompt: two
          expect: none
        """,
    )
    recorded = tmp_path / "verdicts.json"
    recorded.write_text(json.dumps({"a": "aerospike", "b": "aerospike"}), encoding="utf-8")
    report = tmp_path / "report.json"

    failing = main(
        [
            "--corpus", str(corpus),
            "--offline", str(recorded),
            "--min-accuracy", "0.9",
            "--json", str(report),
        ]
    )
    passing = main(
        ["--corpus", str(corpus), "--offline", str(recorded), "--min-accuracy", "0.4"]
    )

    assert failing == 1
    assert passing == 0
    written = json.loads(report.read_text(encoding="utf-8"))
    assert written["accuracy"] == 0.5
    assert written["failures"] == [["b", "none", "aerospike"]]
