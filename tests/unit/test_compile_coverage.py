"""The compiler drops content by design; this fails when a drop is a defect.

Content that moves to ``references/`` is deferred, not lost -- the artifact is a
router. Content that leaves the package, or that stays in it with nothing
pointing at it, is gone as far as any reader is concerned. Only the second kind
fails here.
"""

import importlib.util
import pathlib

import pytest

from scripts.skills_compile import coverage, skillsrc

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def compiler():
    spec = importlib.util.spec_from_file_location(
        "compile_agents", REPO_ROOT / "scripts" / "compile-agents.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def report(compiler):
    skills = [
        skillsrc.load_skill(REPO_ROOT / d) for d in compiler.DEFAULT_SKILLS
    ]
    outputs = compiler.compile_outputs("stripped", compiler.DEFAULT_SKILLS, "single")
    published = {p.split("/")[-1] for p in outputs if "/references/" in p}
    return coverage.coverage_report(skills, published)


def test_no_content_is_lost_rather_than_deferred(report):
    assert report.defects == [], "\n" + report.summary()


def test_the_check_can_still_see_deferred_content(report):
    """Guards the guard.

    A checker that reports nothing deferred is not passing -- it has stopped
    measuring. Why and See also never ship by design, so their word counts
    should always be substantial.
    """
    assert report.deferred["Why"] > 1000
    assert report.deferred["See also"] > 100


def test_a_dangling_colon_is_a_defect(compiler):
    """The authoring rule tier 1 depends on: a Rule's first sentence stands alone.

    At imperative density only that sentence ships, so a Rule that opens by
    announcing a table leaves a colon pointing at nothing. This is exactly how
    policy-write-commit-level read before it was rewritten.
    """
    skill = skillsrc.load_skill(REPO_ROOT / "skills" / "aerospike-development")
    broken = skillsrc.RefFile(
        name="synthetic-dangling.md",
        prefix="synthetic",
        rel="references/synthetic-dangling.md",
        meta={"title": "Synthetic", "impact": "HIGH"},
        body="**Rule**\n\nThe levels are:\n\n| A | B |\n| --- | --- |\n| x | y |\n",
        raw="",
    )
    skill.refs = [broken]
    report = coverage.coverage_report([skill], {"aerospike-development-synthetic-dangling.md"})
    assert any(d.kind == "dangling-colon" for d in report.defects), report.summary()
