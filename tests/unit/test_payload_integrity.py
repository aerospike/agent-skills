"""What we hand a registry must be self-contained and current: a skill folder
that links outside itself is broken the moment it is installed on its own."""

import pathlib
import re

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SKILL_DIRS = sorted(p.parent for p in REPO_ROOT.glob("skills/*/SKILL.md")) + [
    REPO_ROOT / "compiled-skills" / "aerospike"
]
# Markdown links, minus anything that is not a repository-relative path.
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def _relative_targets(text):
    for target in LINK.findall(text):
        target = target.split("#", 1)[0].strip()
        if not target or "://" in target or target.startswith("mailto:"):
            continue
        yield target


@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda p: p.name)
def test_no_skill_links_outside_its_own_folder(skill_dir):
    escapes = []
    for md in sorted(skill_dir.rglob("*.md")):
        for target in _relative_targets(md.read_text(encoding="utf-8")):
            resolved = (md.parent / target).resolve()
            if skill_dir.resolve() not in resolved.parents and resolved != skill_dir:
                escapes.append(f"{md.relative_to(REPO_ROOT)} -> {target}")

    assert escapes == []


@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda p: p.name)
def test_every_relative_link_resolves_to_a_file_that_exists(skill_dir):
    missing = []
    for md in sorted(skill_dir.rglob("*.md")):
        for target in _relative_targets(md.read_text(encoding="utf-8")):
            if not (md.parent / target).exists():
                missing.append(f"{md.relative_to(REPO_ROOT)} -> {target}")

    assert missing == []
