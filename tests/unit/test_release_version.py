"""Release tags are stable semantic versions that move forward.

The gate is only worth having if it fails on the tags it is meant to catch, so these
exercise the script itself rather than asserting on its source.
"""

import pathlib
import shutil
import subprocess

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check-release-version.sh"
WORKFLOWS = REPO_ROOT / ".github" / "workflows"


def _check(*args, repo=None):
    """Run the script, optionally the copy inside a scratch repository."""
    return subprocess.run(
        [str(SCRIPT if repo is None else repo / "scripts" / SCRIPT.name), *args],
        capture_output=True,
        text=True,
    )


@pytest.fixture
def tagged_repo(tmp_path):
    """A copy of scripts/ in a real repository, so tags are the only variable.

    The script derives its root from its own location, which is what makes a copied
    tree the tag history it reads.
    """
    shutil.copytree(REPO_ROOT / "scripts", tmp_path / "scripts")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit",
         "-q", "--allow-empty", "-m", "root"],
        cwd=tmp_path,
        check=True,
    )

    def tag(*names):
        for name in names:
            subprocess.run(["git", "tag", name], cwd=tmp_path, check=True)
        return tmp_path

    return tag


@pytest.mark.parametrize("tag", ["v0.1.0", "v1.4.0", "v10.20.30"])
def test_stable_versions_pass(tag):
    result = _check("--tag", tag, "--skip-ordering")

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "tag",
    [
        "1.4.0",  # missing the v prefix
        "v1.4",  # not three components
        "v1.4.0.1",
        "v1.04.0",  # leading zero
        "v1.x.0",
        "release-1.4.0",
        "latest",
    ],
)
def test_malformed_tags_fail(tag):
    result = _check("--tag", tag, "--skip-ordering")

    assert result.returncode != 0
    assert "vMAJOR.MINOR.PATCH" in result.stderr or "v prefix" in result.stderr


def test_an_empty_tag_reports_a_missing_argument():
    """What an unset workflow expression looks like, so it needs its own message
    rather than a shell parameter error."""
    result = _check("--tag", "", "--skip-ordering")

    assert result.returncode != 0
    assert "--tag is required" in result.stderr


@pytest.mark.parametrize("tag", ["v1.4.0-rc.1", "v1.4.0-beta", "v1.4.0+build.3"])
def test_prerelease_and_build_metadata_fail(tag):
    """Stable versions only: a submission cannot be withdrawn from a registry."""
    result = _check("--tag", tag, "--skip-ordering")

    assert result.returncode != 0
    assert "stable" in result.stderr


def test_a_well_formed_tag_flagged_prerelease_on_github_fails():
    """The flag matters as much as the tag; either one can mean "not ready"."""
    result = _check("--tag", "v1.4.0", "--flagged-prerelease", "true", "--skip-ordering")

    assert result.returncode != 0
    assert "prerelease" in result.stderr


def test_an_unresolved_prerelease_expression_is_not_read_as_false():
    """An empty workflow expression must fail loudly, not silently permit."""
    result = _check("--tag", "v1.4.0", "--flagged-prerelease", "", "--skip-ordering")

    assert result.returncode != 0


def test_the_first_release_has_nothing_to_compare_against(tagged_repo):
    repo = tagged_repo()

    result = _check("--tag", "v0.1.0", repo=repo)

    assert result.returncode == 0, result.stderr
    assert "first release" in result.stdout


@pytest.mark.parametrize("tag", ["v1.4.1", "v1.5.0", "v2.0.0"])
def test_increasing_versions_pass(tagged_repo, tag):
    repo = tagged_repo("v1.0.0", "v1.4.0")

    result = _check("--tag", tag, repo=repo)

    assert result.returncode == 0, result.stderr
    assert "v1.4.0" in result.stdout


@pytest.mark.parametrize("tag", ["v1.3.9", "v0.9.0", "v1.0.0"])
def test_versions_that_do_not_move_forward_fail(tagged_repo, tag):
    repo = tagged_repo("v1.0.0", "v1.4.0")

    result = _check("--tag", tag, repo=repo)

    assert result.returncode != 0
    assert "v1.4.0" in result.stderr


def test_ordering_compares_numerically_not_lexically(tagged_repo):
    """v1.10.0 is above v1.9.0, though it sorts below it as text."""
    repo = tagged_repo("v1.9.0")

    assert _check("--tag", "v1.10.0", repo=repo).returncode == 0
    assert _check("--tag", "v1.2.0", repo=repo).returncode != 0


def test_the_tag_under_test_is_not_compared_against_itself(tagged_repo):
    """A release event creates the tag before this check runs, so it is already
    present in the history it reads. Comparing it to itself would reject every
    release as "not moving forward"."""
    repo = tagged_repo("v1.0.0", "v1.4.0", "v1.5.0")

    result = _check("--tag", "v1.5.0", repo=repo)

    assert result.returncode == 0, result.stderr
    assert "v1.4.0" in result.stdout


def test_a_tree_without_tag_history_fails_rather_than_guessing(tmp_path):
    """Silently treating a missing history as "first release" would wave through
    any version at all."""
    shutil.copytree(REPO_ROOT / "scripts", tmp_path / "scripts")

    result = _check("--tag", "v0.0.1", repo=tmp_path)

    assert result.returncode != 0
    assert "--skip-ordering" in result.stderr


def test_the_gate_is_wired_into_publishing():
    """A gate that no job needs is decorative."""
    publish = (WORKFLOWS / "publish-registries.yml").read_text(encoding="utf-8")

    assert "uses: ./.github/workflows/release-version.yml" in publish
    assert "needs: [gate-version," in publish


def test_the_version_workflow_fetches_the_full_tag_history():
    """A shallow release checkout makes every release look like the first one."""
    workflow = (WORKFLOWS / "release-version.yml").read_text(encoding="utf-8")

    assert "fetch-depth: 0" in workflow
    assert "check-release-version.sh" in workflow
