"""Every skill declares the server range its guidance targets, so "matches
current server behavior" has something concrete to be checked against."""

import pathlib

import pytest

from scripts.skills_compile.skillsrc import split_frontmatter

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SKILL_FILES = sorted(REPO_ROOT.glob("skills/*/SKILL.md")) + [
    REPO_ROOT / "compiled-skills" / "aerospike" / "SKILL.md"
]


def _ids(path):
    return path.parent.name


@pytest.mark.parametrize("skill_md", SKILL_FILES, ids=_ids)
def test_skill_declares_the_supported_server_range(skill_md):
    meta, _body = split_frontmatter(skill_md.read_text(encoding="utf-8"))

    assert meta["metadata"]["server_versions"] == "7.0+"


def test_every_skill_on_disk_is_covered():
    """Guards the parametrize list: a new skill folder must not slip past."""
    on_disk = set(REPO_ROOT.glob("skills/*/SKILL.md"))

    assert on_disk <= set(SKILL_FILES)
    assert len(SKILL_FILES) == 4


def test_published_last_verified_is_the_oldest_of_its_sources():
    """The published date must describe the weakest link, not the freshest part.

    The compiled skill is a union of three independently verified skills, so one
    date cannot be true of all of it. The floor is the only reading that never
    overstates: a consumer asking "how current is this guidance" is really asking
    about the oldest thing in the bundle.

    This is a guard, not a preference. The published value is hand-written in
    ``scripts/skills_compile/published_skill.yaml`` and derived from nothing, so
    re-verifying one source used to leave it silently wrong. Bumping a source now
    fails here until the published value follows.
    """
    sources = sorted(REPO_ROOT.glob("skills/*/SKILL.md"))
    assert sources, "no source skills found"

    dates = {}
    for path in sources:
        meta, _ = split_frontmatter(path.read_text(encoding="utf-8"))
        dates[path.parent.name] = meta["metadata"]["last_verified"]

    published_meta, _ = split_frontmatter(
        (REPO_ROOT / "compiled-skills" / "aerospike" / "SKILL.md").read_text(
            encoding="utf-8"
        )
    )
    published = published_meta["metadata"]["last_verified"]

    # ISO dates, so lexicographic order is chronological order.
    assert published == min(dates.values()), (
        f"published last_verified is {published}, but the oldest source is "
        f"{min(dates.values())}. Source dates: {dates}"
    )
