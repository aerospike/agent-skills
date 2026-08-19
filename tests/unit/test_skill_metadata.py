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
