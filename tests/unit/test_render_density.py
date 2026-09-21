"""Per-skill density: how much of each rule reaches the always-loaded file.

The skills are unequal -- one carries 35 rules and the others four and none --
so density is declared per skill rather than globally. A large skill can thin
itself without costing a small one its instructions.
"""

import pathlib

import pytest

from scripts.skills_compile import skillsrc
from scripts.skills_compile.render import (
    DENSITIES,
    _imperative,
    render_stripped,
    skill_density,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


@pytest.fixture
def skills():
    return [
        skillsrc.load_skill(REPO_ROOT / "skills" / name)
        for name in (
            "aerospike-getting-started",
            "aerospike-development",
            "aerospike-data-modeling",
        )
    ]


def test_density_defaults_to_imperative(skills):
    assert all(skill_density(sk) == "imperative" for sk in skills)


def test_an_unknown_density_raises_rather_than_falling_back(skills):
    sk = skills[0]
    sk.skill_md_meta.setdefault("metadata", {})["density"] = "terse"
    with pytest.raises(ValueError, match="terse"):
        skill_density(sk)


def test_one_skill_going_bare_does_not_thin_the_others(skills):
    """The bug this guards: rebinding the default inside the render loop.

    A skill declaring `bare` would then become the default for every skill
    compiled after it, silently stripping instructions from unrelated skills.
    """
    skills[1].skill_md_meta.setdefault("metadata", {})["density"] = "bare"

    assert skill_density(skills[0]) == "imperative"
    assert skill_density(skills[1]) == "bare"
    assert skill_density(skills[2]) == "imperative"

    body = render_stripped(skills)
    # A rule from a skill still at imperative keeps its instruction bullet.
    lines = body.splitlines()
    heads = [i for i, ln in enumerate(lines) if ln.startswith("### ex-guide-escalation — ")]
    assert heads, "expected a data-modeling rule heading"
    assert lines[heads[0] + 1].startswith("- "), "imperative was stripped from the wrong skill"


def test_bare_drops_a_duplicate_not_a_fact(skills):
    """Everything `bare` removes is still the first sentence of Rule in the
    shipped reference file, so the instruction stays reachable."""
    sk = next(s for s in skills if s.name == "aerospike-development")
    ref = next(r for r in sk.refs if r.name == "client-singleton.md")
    imperative = _imperative(skillsrc.labeled_sections(ref.body)["Rule"])

    assert imperative
    stripped = ref.body.replace("**", "").replace("`", "")
    assert imperative.split(".")[0] in stripped


def test_every_declared_density_renders(skills):
    for density in DENSITIES:
        assert render_stripped(skills, density).strip()
