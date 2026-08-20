#!/usr/bin/env python3
"""Measure whether the published skill's description fires when it should.

An agent harness decides whether to load a skill from its description alone,
before the skill's body is ever read. This runner reproduces exactly that
decision: it shows a model the skill name, the description, and one user
message, and records which of two answers comes back. It never loads the skill
body, so what it measures is the description and nothing else.

Offline mode replays recorded verdicts, so the corpus, parsing, and scoring can
be exercised with no API key and no network.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import pathlib
import sys

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.skills_compile.skillsrc import split_frontmatter  # noqa: E402

PUBLISHED_SKILL = REPO_ROOT / "compiled-skills" / "aerospike" / "SKILL.md"
CORPUS_DIR = REPO_ROOT / "tests" / "triggers"
NO_SKILL = "none"
UNPARSEABLE = "unparseable"
DEFAULT_MODEL = "composer-2.5"


@dataclasses.dataclass(frozen=True)
class TriggerCase:
    id: str
    prompt: str
    expect: str
    domain: str | None = None
    why: str = ""


@dataclasses.dataclass(frozen=True)
class Metrics:
    total: int
    correct: int
    true_positives: int
    false_positives: int
    false_negatives: int
    failures: tuple[tuple[str, str, str], ...]

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0

    @property
    def precision(self) -> float:
        fired = self.true_positives + self.false_positives
        return self.true_positives / fired if fired else 0.0

    @property
    def recall(self) -> float:
        wanted = self.true_positives + self.false_negatives
        return self.true_positives / wanted if wanted else 0.0


def load_published_skill(path: pathlib.Path = PUBLISHED_SKILL) -> tuple[str, str]:
    """Return the shipped skill's name and description, whitespace collapsed.

    Read from the compiled artifact rather than a copy, so the corpus always
    scores the description users actually install.
    """
    meta, _body = split_frontmatter(path.read_text(encoding="utf-8"))
    return meta["name"], " ".join(meta["description"].split())


def load_corpus(corpus_dir: pathlib.Path) -> list[TriggerCase]:
    cases: list[TriggerCase] = []
    seen: set[str] = set()
    for path in sorted(corpus_dir.glob("*.yaml")):
        for entry in yaml.safe_load(path.read_text(encoding="utf-8")) or []:
            case = TriggerCase(
                id=entry["id"],
                prompt=" ".join(entry["prompt"].split()),
                expect=entry["expect"],
                domain=entry.get("domain"),
                why=entry.get("why", ""),
            )
            if case.id in seen:
                raise ValueError(f"duplicate case id: {case.id} in {path.name}")
            seen.add(case.id)
            cases.append(case)

    if not cases:
        raise ValueError(f"no trigger cases found under {corpus_dir}")

    name, _description = load_published_skill()
    allowed = {name, NO_SKILL}
    for case in cases:
        if case.expect not in allowed:
            raise ValueError(f"{case.id}: expect must be one of {sorted(allowed)}")
    return cases


def build_router_prompt(name: str, description: str, user_prompt: str) -> str:
    return (
        "You are the skill router in an AI coding assistant. One skill is "
        "installed. Using only its description, decide whether to load it for "
        "the user's message.\n\n"
        f"Skill name: {name}\n"
        f"Description: {description}\n\n"
        f"User message: {user_prompt}\n\n"
        f"Answer with exactly one word: {name} to load the skill, or {NO_SKILL} "
        "to answer without it."
    )


def parse_verdict(raw: str, skill_name: str) -> str:
    """Reduce a reply to one allowed answer.

    Models add punctuation, emphasis, and a sentence of reasoning even when told
    not to, so match on the words present rather than demanding an exact reply.
    A reply naming the skill wins over one naming neither.
    """
    words = {word.strip(".,:;!?\"'`*_").lower() for word in (raw or "").split()}
    if skill_name.lower() in words:
        return skill_name
    if NO_SKILL in words:
        return NO_SKILL
    return UNPARSEABLE


def score(
    cases: list[TriggerCase], verdicts: dict[str, str], skill_name: str
) -> Metrics:
    correct = true_positives = false_positives = false_negatives = 0
    failures: list[tuple[str, str, str]] = []

    for case in cases:
        got = verdicts.get(case.id, UNPARSEABLE)
        if got == case.expect:
            correct += 1
            if got == skill_name:
                true_positives += 1
            continue
        failures.append((case.id, case.expect, got))
        if case.expect == NO_SKILL:
            false_positives += 1
        else:
            false_negatives += 1

    return Metrics(
        total=len(cases),
        correct=correct,
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives,
        failures=tuple(failures),
    )


def _ask_model(prompt: str, model: str) -> str:
    from cursor_sdk import Agent, AgentOptions, LocalAgentOptions

    api_key = os.environ.get("CURSOR_API_KEY")
    if not api_key:
        raise SystemExit(
            "CURSOR_API_KEY is not set. Set it, or pass --offline to score a "
            "recorded run."
        )
    result = Agent.prompt(
        prompt,
        AgentOptions(
            api_key=api_key,
            model=model,
            local=LocalAgentOptions(cwd=str(REPO_ROOT)),
        ),
    )
    return getattr(result, "result", "") or ""


def _collect_verdicts(
    cases: list[TriggerCase], name: str, description: str, model: str
) -> dict[str, str]:
    verdicts: dict[str, str] = {}
    for index, case in enumerate(cases, start=1):
        raw = _ask_model(build_router_prompt(name, description, case.prompt), model)
        verdicts[case.id] = parse_verdict(raw, name)
        print(f"  [{index}/{len(cases)}] {case.id}: {verdicts[case.id]}", flush=True)
    return verdicts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Score the published skill's description against trigger cases."
    )
    parser.add_argument("--corpus", type=pathlib.Path, default=CORPUS_DIR)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--offline",
        type=pathlib.Path,
        help="JSON file of {case_id: verdict}; scores without calling a model",
    )
    parser.add_argument(
        "--min-accuracy",
        type=float,
        default=0.0,
        help="exit 1 below this overall accuracy",
    )
    parser.add_argument("--json", type=pathlib.Path, help="write the report here")
    args = parser.parse_args(argv)

    cases = load_corpus(args.corpus)
    name, description = load_published_skill()

    if args.offline:
        verdicts = json.loads(args.offline.read_text(encoding="utf-8"))
    else:
        print(f"Routing {len(cases)} prompts through {args.model}")
        verdicts = _collect_verdicts(cases, name, description, args.model)

    metrics = score(cases, verdicts, name)

    print(
        f"\naccuracy {metrics.accuracy:.3f}  "
        f"precision {metrics.precision:.3f}  "
        f"recall {metrics.recall:.3f}  "
        f"({metrics.correct}/{metrics.total})"
    )
    for case_id, expected, got in metrics.failures:
        print(f"  FAIL {case_id}: expected {expected}, got {got}")

    if args.json:
        args.json.write_text(
            json.dumps(
                {
                    "model": args.model,
                    "skill": name,
                    "total": metrics.total,
                    "correct": metrics.correct,
                    "accuracy": metrics.accuracy,
                    "precision": metrics.precision,
                    "recall": metrics.recall,
                    "failures": [list(f) for f in metrics.failures],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    if metrics.accuracy < args.min_accuracy:
        print(
            f"\nBelow threshold: {metrics.accuracy:.3f} < {args.min_accuracy:.3f}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
