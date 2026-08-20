"""The compiled artifact is what registries fetch, so it must be a valid skill:
frontmatter they can parse, a name matching its folder, and a header that tells
an agent where the rule files it cites actually live."""

import importlib.util
import pathlib

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SPEC_KEYS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}


def _load_compiler():
    spec = importlib.util.spec_from_file_location(
        "compile_agents", REPO_ROOT / "scripts" / "compile-agents.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def compiler():
    return _load_compiler()


@pytest.fixture(scope="module")
def published(compiler):
    outputs = compiler.compile_outputs("stripped", compiler.DEFAULT_SKILLS, "single")
    return outputs, outputs[compiler.SINGLE_OUT]


def test_published_skill_lands_in_a_folder_named_after_the_skill(compiler):
    assert compiler.SINGLE_OUT == "compiled-skills/aerospike/SKILL.md"


def test_skills_md_is_no_longer_emitted(published):
    outputs, _ = published
    assert "compiled-skills/SKILLS.md" not in outputs


def test_frontmatter_parses_and_uses_only_spec_keys(compiler, published):
    from scripts.skills_compile.skillsrc import split_frontmatter

    _, text = published
    meta, _body = split_frontmatter(text)

    assert meta, "SKILL.md must open with a YAML frontmatter block"
    assert set(meta) <= SPEC_KEYS
    assert meta["name"] == "aerospike"
    assert meta["license"] == "Apache-2.0"
    assert isinstance(meta["metadata"]["last_verified"], str)


def test_description_covers_all_three_source_domains(published):
    _, text = published
    lowered = text[: text.index("---", 4)].lower()

    for term in ("docker", "client code", "data model"):
        assert term in lowered, f"description should mention {term!r}"
    for excluded in ("graph", "xdr"):
        assert excluded in lowered, f"description should rule out {excluded!r}"


def test_header_carries_the_repository_url_for_cited_rule_files(compiler, published):
    _, text = published
    assert compiler.REPO_URL in text
    assert "`skills/<skill>/` or its `references/` folder" in text


def test_body_is_the_stripped_render(compiler, published):
    _, text = published
    skills = [
        compiler.skillsrc.load_skill(compiler.REPO_ROOT / src)
        for src in compiler.DEFAULT_SKILLS
    ]
    expected_body = compiler.RENDERERS["stripped"](skills).strip()
    expected = (
        f"{compiler._frontmatter()}\n"
        f"{compiler._header(compiler.DEFAULT_SKILLS)}\n"
        f"{expected_body}\n"
    )
    assert text == expected
