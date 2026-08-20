"""Both registries must receive exactly one submission: the compiled skill."""

import json
import pathlib
import shutil
import subprocess

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
REPO_URL = "https://github.com/aerospike/agent-skills"


def _run(script, *args):
    result = subprocess.run(
        [str(REPO_ROOT / "scripts" / script), "--repo-url", REPO_URL, "--dry-run", *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_openagentskill_submits_only_the_compiled_skill():
    out = _run("publish-openagentskill.sh")

    assert out.count("DRY RUN") == 1
    assert "DRY RUN aerospike:" in out
    for retired in ("aerospike-getting-started", "aerospike-development"):
        assert retired not in out


def test_openagentskill_payload_points_at_the_compiled_skill():
    out = _run("publish-openagentskill.sh")
    payload = json.loads(out[out.index("{"):out.rindex("}") + 1])

    assert payload["repository"] == REPO_URL
    assert payload["skillPath"] == "compiled-skills/aerospike/SKILL.md"
    assert payload["submissionSource"] == "agent"


def test_upskill_submits_only_the_compiled_skill():
    out = _run("publish-upskill.sh", "--ref", "main")

    assert out.count("DRY RUN") == 1
    assert f"{REPO_URL}/tree/main/compiled-skills/aerospike" in out
    assert "/skills/aerospike-development" not in out


@pytest.mark.parametrize("script", ["publish-openagentskill.sh", "publish-upskill.sh"])
def test_scripts_fail_when_the_compiled_skill_is_absent(script, tmp_path):
    """A missing artifact must fail loudly rather than report a successful no-op.

    Each script derives its root from its own location, so copying scripts/ alone
    into an empty tree is what makes the compiled skill genuinely absent.
    """
    shutil.copytree(REPO_ROOT / "scripts", tmp_path / "scripts")

    result = subprocess.run(
        [str(tmp_path / "scripts" / script), "--repo-url", REPO_URL, "--dry-run"],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "compile-agents.py --write" in result.stderr
