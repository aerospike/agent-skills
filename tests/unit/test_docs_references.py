"""No document may point at the retired SKILLS.md, and the install table must
cover every platform we claim to support."""

import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
TRACKED_SUFFIXES = {".md", ".json", ".yml", ".sh", ".py"}
SKIP_DIRS = {".git", "eval", "results", "docs/superpowers", ".venv", ".superpowers"}

# These name the retired path on purpose: one asserts the compiler no longer
# emits it, and the other is this guard's own search string.
SKIP_FILES = {
    "tests/unit/test_compile_published_skill.py",
    "tests/unit/test_docs_references.py",
}


def _tracked_files():
    for path in REPO_ROOT.rglob("*"):
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel in SKIP_FILES:
            continue
        if any(rel == d or rel.startswith(f"{d}/") for d in SKIP_DIRS):
            continue
        if path.is_file() and path.suffix in TRACKED_SUFFIXES:
            yield rel, path


def test_nothing_references_the_retired_compiled_file():
    offenders = [
        rel
        for rel, path in _tracked_files()
        if "compiled-skills/SKILLS.md" in path.read_text(encoding="utf-8")
        or "](SKILLS.md)" in path.read_text(encoding="utf-8")
    ]
    assert offenders == []


def test_install_docs_cover_claude_cursor_and_gemini_cli():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    compiled = (REPO_ROOT / "compiled-skills" / "README.md").read_text(encoding="utf-8")
    assert "-a gemini-cli" in readme, "README must document the Gemini CLI install"
    for flag in ("-a claude-code", "-a cursor", "-a gemini-cli"):
        assert flag in compiled, f"compiled-skills README must document {flag}"


def test_registry_manifest_lists_the_single_published_skill():
    manifest = json.loads((REPO_ROOT / "skills.sh.json").read_text(encoding="utf-8"))
    skills = [s for g in manifest["groupings"] for s in g["skills"]]
    assert skills == ["aerospike"]
