#!/usr/bin/env python3
"""Compile the skills/ source-of-truth into compiled-skills/ consumption artifacts.

The modular files under ``skills/`` are the source of truth for authors; this
script builds the published ``compiled-skills/aerospike/SKILL.md`` that registries
fetch and end users download. Its frontmatter is hand-written in
``scripts/skills_compile/published_skill.yaml``.

Usage (maintainers):
    python scripts/compile-agents.py --write
    python scripts/compile-agents.py --check
"""

from __future__ import annotations

import argparse
import json
import pathlib
import posixpath
import re
import sys

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
COMPILED_DIR = "compiled-skills"
PUBLISHED_NAME = "aerospike"
# Folder name must equal the frontmatter `name`: the spec convention, and what the
# skills CLI uses as the install directory.
SINGLE_DIR = f"{COMPILED_DIR}/{PUBLISHED_NAME}"
SINGLE_OUT = f"{SINGLE_DIR}/SKILL.md"
LEGACY_SINGLE_OUT = f"{COMPILED_DIR}/SKILLS.md"
REPO_URL = "https://github.com/aerospike/agent-skills"
SPEC_KEYS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}

sys.path.insert(0, str(REPO_ROOT))

from scripts.skills_compile import skillsrc  # noqa: E402
from scripts.skills_compile.render import render_monolith, render_stripped  # noqa: E402

DEFAULT_SKILLS = [
    "skills/aerospike-getting-started",
    "skills/aerospike-development",
    "skills/aerospike-data-modeling",
]

RENDERERS = {
    "stripped": render_stripped,
    "monolith": render_monolith,
}


def _frontmatter() -> str:
    """Return the published skill's YAML frontmatter block.

    Emitted verbatim rather than re-serialized, so the author controls formatting
    and ``--check`` stays byte-stable across runs. Validated here so a malformed
    header fails the compile instead of a registry submission.
    """
    src = REPO_ROOT / "scripts" / "skills_compile" / "published_skill.yaml"
    text = src.read_text(encoding="utf-8").strip("\n")
    meta = yaml.safe_load(text) or {}

    missing = {"name", "description", "license"} - set(meta)
    if missing:
        raise ValueError(f"{src.name} is missing required key(s): {sorted(missing)}")
    extra = set(meta) - SPEC_KEYS
    if extra:
        raise ValueError(
            f"{src.name} has non-spec key(s): {sorted(extra)}. "
            f"The spec allows only {sorted(SPEC_KEYS)}."
        )
    if meta["name"] != PUBLISHED_NAME:
        raise ValueError(
            f"{src.name} declares name {meta['name']!r} but the published folder is "
            f"{PUBLISHED_NAME!r}; they must match."
        )
    return f"---\n{text}\n---\n"


def _header(skill_dirs: list[str]) -> str:
    return (
        f"_Auto-generated from `{'`, `'.join(skill_dirs)}` in {REPO_URL}. "
        f"Edit the skills under `skills/`, not this file._\n"
        f"\n"
        f"**Reading a rule in full.** Each rule below states its instruction and "
        f"nothing more; the reasoning, the worked detail and the documentation "
        f"links live in its own file, shipped in the `references/` folder beside "
        f"this one. A rule's file is `references/<skill>-<rule>.md`, where "
        f"`<skill>` is the `##` heading it sits under and `<rule>` is its own "
        f"`###` heading — so `client-singleton` under `aerospike-development` is "
        f"`references/aerospike-development-client-singleton.md`. Rules cite each "
        f"other by bare filename and resolve the same way._\n"
    )


_MD_LINK_RE = re.compile(r"(\[[^\]]*\]\()([^)]+)(\))")


def _portable_links(text: str, skill_dir: str, published: dict[str, str]) -> str:
    """Make a rule file's relative links resolve inside the published package.

    Two rewrites, both of which exist because the package is flat where the
    source tree is nested per skill:

    - A sibling citation (``policy-generation-cas.md``) becomes its published
      name (``aerospike-development-policy-generation-cas.md``). This is the
      same ``<skill>-<rule>`` derivation the header states, so the citations in
      the rule text and the headings in SKILL.md resolve by one rule rather
      than two conventions.
    - A link that escapes ``references/`` (``../reference.md``) becomes a
      repository URL. Those links are correct where they were written, so they
      are fixed here rather than in the source.
    """

    def fix(m: re.Match[str]) -> str:
        target = m.group(2)
        if "://" in target or target.startswith(("#", "mailto:")):
            return m.group(0)
        path, _, frag = target.partition("#")
        suffix = f"#{frag}" if frag else ""
        if path in published:
            return f"{m.group(1)}{published[path]}{suffix}{m.group(3)}"
        resolved = posixpath.normpath(posixpath.join(f"{skill_dir}/references", path))
        if resolved.startswith(f"{skill_dir}/references/"):
            return m.group(0)
        return f"{m.group(1)}{REPO_URL}/blob/main/{resolved}{suffix}{m.group(3)}"

    return _MD_LINK_RE.sub(fix, text)


def _reference_outputs(skills: list[skillsrc.SkillSource]) -> dict[str, str]:
    """Publish every rule file beside the artifact, flattened and prefixed.

    The flatten is only safe while basenames stay unique across skills, so a
    collision fails the compile rather than silently overwriting one rule with
    another from a different skill.
    """
    published: dict[str, str] = {}
    for sk in skills:
        for ref in sk.refs:
            if ref.name in published:
                raise ValueError(
                    f"{ref.name} appears in more than one skill; the published "
                    "references/ folder is flat, so basenames must be unique "
                    "across skills for citations to resolve"
                )
            published[ref.name] = f"{skillsrc.rule_id(sk.name, ref.name)}.md"

    out: dict[str, str] = {}
    for sk in skills:
        skill_dir = str(sk.dir.relative_to(REPO_ROOT))
        for ref in sk.refs:
            rel = f"{SINGLE_DIR}/references/{published[ref.name]}"
            out[rel] = _portable_links(ref.raw, skill_dir, published)
    return out


def compile_outputs(
    shape: str,
    skill_dirs: list[str],
    layout: str,
) -> dict[str, str]:
    """Return {repo-relative path: content} for every artifact this run produces."""
    skills = [skillsrc.load_skill(REPO_ROOT / s) for s in skill_dirs]
    render = RENDERERS[shape]
    out: dict[str, str] = {}

    if layout == "single":
        body = render(skills).strip()
        out[SINGLE_OUT] = f"{_frontmatter()}\n{_header(skill_dirs)}\n{body}\n"
        out.update(_reference_outputs(skills))
        return out

    if layout == "multi":
        for sk, src in zip(skills, skill_dirs):
            rel = f"{COMPILED_DIR}/{sk.name}.md"
            body = render([sk]).strip()
            out[rel] = f"{_header([src])}\n{body}\n"
        return out

    raise ValueError(f"Unknown layout: {layout!r}")


def _manifest(outputs: dict[str, str], meta: dict) -> dict:
    """The manifest both --write and --check compare against.

    Sizes are bytes, not characters: that is what a registry downloads and what
    ``wc -c`` reports. The previous character count read 45,422 for a
    45,701-byte file.
    """
    return {
        **meta,
        "files": {
            path: len(content.encode("utf-8"))
            for path, content in sorted(outputs.items())
        },
    }


def _write_manifest(out_dir: pathlib.Path, outputs: dict[str, str], meta: dict) -> None:
    (out_dir / "manifest.json").write_text(
        json.dumps(_manifest(outputs, meta), indent=2) + "\n", encoding="utf-8"
    )


def _orphans(outputs: dict[str, str], layout: str) -> list[str]:
    """Published files under a root this layout owns that this compile did not emit.

    ``--write`` was purely additive, so deleting a source rule left its copy in
    the package for good. Pruning is scoped to roots the layout owns, which is
    why ``compiled-skills/README.md`` and ``manifest.json`` -- both outside
    ``SINGLE_DIR`` -- can never be reached by it.
    """
    if layout != "single":
        return []
    root = REPO_ROOT / SINGLE_DIR
    if not root.is_dir():
        return []
    expected = set(outputs)
    found = (p for p in root.rglob("*") if p.is_file())
    return sorted(
        str(p.relative_to(REPO_ROOT))
        for p in found
        if str(p.relative_to(REPO_ROOT)) not in expected
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Compile skills/ into compiled-skills/.")
    ap.add_argument("--shape", choices=list(RENDERERS), default="stripped")
    ap.add_argument(
        "--layout",
        choices=["single", "multi"],
        default="single",
        help="single -> compiled-skills/aerospike/SKILL.md; multi -> one .md per skill",
    )
    ap.add_argument("--skills", nargs="*", default=DEFAULT_SKILLS)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    outputs = compile_outputs(args.shape, args.skills, args.layout)
    out_root = REPO_ROOT / COMPILED_DIR
    meta = {"shape": args.shape, "layout": args.layout, "sources": args.skills}

    if args.check:
        stale: list[str] = []
        for rel, expected in outputs.items():
            path = REPO_ROOT / rel
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                stale.append(rel)
        if (REPO_ROOT / LEGACY_SINGLE_OUT).exists():
            stale.append(f"{LEGACY_SINGLE_OUT} (superseded by {SINGLE_OUT}; delete it)")
        stale.extend(f"{rel} (orphan; run --write to prune)" for rel in _orphans(outputs, args.layout))
        manifest_path = out_root / "manifest.json"
        if manifest_path.exists():
            try:
                on_disk = json.loads(manifest_path.read_text(encoding="utf-8"))
                # Compare the whole manifest: `files` and `sources` went
                # unchecked before, so a published file could drift or vanish
                # without the drift check noticing.
                if on_disk != _manifest(outputs, meta):
                    stale.append("manifest.json")
            except json.JSONDecodeError:
                stale.append("manifest.json")
        else:
            stale.append("manifest.json")

        if stale:
            for rel in stale:
                print(
                    f"::error file={rel}::{rel} is out of date. "
                    f"Run `python scripts/compile-agents.py --write`.",
                    file=sys.stderr,
                )
            return 1
        print(f"compiled-skills/ is up to date ({args.layout}, {args.shape}).")
        return 0

    if args.write:
        out_root.mkdir(parents=True, exist_ok=True)
        for rel, content in outputs.items():
            path = REPO_ROOT / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        for rel in _orphans(outputs, args.layout):
            (REPO_ROOT / rel).unlink()
            print(f"  pruned {rel}")
        if (REPO_ROOT / LEGACY_SINGLE_OUT).exists():
            (REPO_ROOT / LEGACY_SINGLE_OUT).unlink()
            print(f"  pruned {LEGACY_SINGLE_OUT}")
        _write_manifest(out_root, outputs, meta)
        print(f"Wrote {len(outputs)} file(s) to {COMPILED_DIR}/ ({args.layout}, {args.shape}).")
        for rel in sorted(outputs):
            print(f"  {rel}")
        return 0

    for rel in sorted(outputs):
        sys.stdout.write(f"--- {rel} ---\n")
        sys.stdout.write(outputs[rel])
        if not outputs[rel].endswith("\n"):
            sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
