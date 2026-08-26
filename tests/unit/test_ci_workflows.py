"""Guards for CI mistakes that got past review.

The common shape is a fact restated in two places, then drifting.
"""

import pathlib
import re

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
TESTS = REPO_ROOT / "tests"


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


def test_no_workflow_expects_a_model_api_key():
    """Trigger accuracy is measured by hand, by decision, not by omission.

    This project does not put a model API key in CI, so the measurement is a
    documented pre-publish step. A workflow reaching for the key would either
    fail on every run or quietly skip and gate nothing.
    """
    offenders = [
        path.name
        for path in sorted(WORKFLOWS.glob("*.yml"))
        if "CURSOR_API_KEY" in path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_neither_registry_submission_can_block_the_other():
    """The two registries are independent; a failure in one must not skip the other.

    A step without `continue-on-error` skips every later step when it fails, so an
    openagentskill problem meant upskill was never attempted at all -- one
    registry's defect became a publish to neither. Each submission now runs
    regardless, and a final gate step turns a rejection back into a failed build,
    because continue-on-error would otherwise leave the job green.
    """
    workflow = yaml.safe_load(
        (WORKFLOWS / "publish-registries.yml").read_text(encoding="utf-8")
    )
    steps = workflow["jobs"]["publish"]["steps"]
    by_id = {s["id"]: s for s in steps if "id" in s}

    for registry in ("openagentskill", "upskill"):
        assert registry in by_id, f"the {registry} step needs an id for the gate below"
        assert by_id[registry].get("continue-on-error") is True, (
            f"{registry} must not skip the other registry's step when it fails"
        )

    gate = [s for s in steps if "outcome" in str(s.get("env", ""))]
    assert gate, "a step must read both outcomes and fail the job on a rejection"
    assert gate[-1] is steps[-1], "the gate must run last, after receipts are uploaded"
    assert gate[-1].get("if") == "always()"


def test_the_documented_trigger_threshold_is_the_one_people_run():
    """The bar and the command that enforces it must not drift apart.

    `tests/triggers/README.md` explains where the number came from; the
    pre-publish checklist is what someone actually types. If they disagree, the
    explanation is describing a check nobody runs.
    """
    documented = re.search(
        r"The bar is \*\*([\d.]+)\*\*",
        (TESTS / "triggers" / "README.md").read_text(encoding="utf-8"),
    )
    invoked = re.search(
        r"run_triggers\.py[^\n]*--min-accuracy ([\d.]+)",
        (TESTS / "README.md").read_text(encoding="utf-8"),
    )

    assert documented is not None
    assert invoked is not None
    assert float(invoked.group(1)) == float(documented.group(1))
