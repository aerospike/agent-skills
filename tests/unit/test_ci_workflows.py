"""Guards for two CI failures that got past review.

Both were the same mistake in different clothes: a workflow restating a fact
that already lives somewhere else, then drifting from it.
"""

import pathlib
import re

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"


def test_skill_validator_workflow_delegates_to_the_script():
    """`skill-validator check` takes exactly one path.

    The workflow used to pass `skills/ compiled-skills/` and was rejected with
    "accepts 1 arg(s), received 2". Calling the script instead keeps the root
    list and the compiled-skills link-skip in one place.
    """
    text = (WORKFLOWS / "skill-validator.yml").read_text(encoding="utf-8")

    direct_calls = re.findall(r"^\s*skill-validator check\b.*$", text, re.MULTILINE)

    assert direct_calls == []
    assert "./scripts/validate-skill.sh --ci" in text
    assert "./scripts/validate-skill.sh --summary" in text


def test_trigger_threshold_matches_the_recorded_measurement():
    """The gate and the number it is derived from must not drift apart.

    tests/triggers/README.md explains where the threshold came from; the
    workflow only enforces it. If they disagree, the explanation is wrong.
    """
    workflow = yaml.safe_load((WORKFLOWS / "triggers.yml").read_text(encoding="utf-8"))
    documented = re.search(
        r"CI fails below \*\*([\d.]+)\*\*",
        (REPO_ROOT / "tests" / "triggers" / "README.md").read_text(encoding="utf-8"),
    )

    assert documented is not None
    assert float(workflow["jobs"]["triggers"]["env"]["MIN_ACCURACY"]) == float(
        documented.group(1)
    )


def test_trigger_scoring_is_skipped_when_the_key_is_absent():
    """A missing credential is a configuration gap, not a skill defect.

    The job-level `if` only rules out forks, so a same-repo PR reached the
    scoring step with an empty secret and failed there.
    """
    workflow = yaml.safe_load((WORKFLOWS / "triggers.yml").read_text(encoding="utf-8"))
    steps = workflow["jobs"]["triggers"]["steps"]
    scoring = next(s for s in steps if s.get("name") == "Score the published description")

    assert scoring["if"] == "steps.key.outputs.present == 'true'"
