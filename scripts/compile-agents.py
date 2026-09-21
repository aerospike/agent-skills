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
        f"**Reading a rule in full.** A rule is a `###` heading of the form "
        f"`<rule> — <title> [IMPACT]`; a `###` heading without that shape is a "
        f"section of the skill itself, not a rule. Each rule states its "
        f"instruction and nothing more — the reasoning, the worked detail and "
        f"the documentation links live in its own file, shipped in the "
        f"`references/` folder beside this one. That file is "
        f"`references/<skill>-<rule>.md`, where `<skill>` is the `##` heading "
        f"the rule sits under: `client-singleton` under `aerospike-development` "
        f"is `references/aerospike-development-client-singleton.md`. Rules cite "
        f"each other by bare filename and resolve the same way. Worked examples "
        f"named under `Worked examples` live in `examples/<skill>-<name>.md`, "
        f"the same naming one folder over._\n"
    )


_MD_LINK_RE = re.compile(r"(\[[^\]]*\]\()([^)]+)(\))")


def _portable_links(
    text: str,
    skill_dir: str,
    published: dict[str, tuple[str, str]],
    folder: str = "references",
    siblings: dict[str, tuple[str, str]] | None = None,
) -> str:
    """Make a rule file's relative links resolve inside the published package.

    Two rewrites, both of which exist because the package is flat where the
    source tree is nested per skill:

    - A citation of another published file becomes its published name, with
      ``../<folder>/`` in front when the target sits in the other folder. This
      is the same ``<skill>-<name>`` derivation the header states, so citations
      in the text and headings in SKILL.md resolve by one rule rather than two
      conventions.
    - A link that escapes the package (``../reference.md``) becomes a
      repository URL. Those links are correct where they were written, so they
      are fixed here rather than in the source.

    ``published`` maps a source basename to ``(folder, published name)``;
    ``folder`` is where the file being rewritten will live.
    """

    def fix(m: re.Match[str]) -> str:
        target = m.group(2)
        if "://" in target or target.startswith(("#", "mailto:")):
            return m.group(0)
        path, _, frag = target.partition("#")
        suffix = f"#{frag}" if frag else ""
        base = posixpath.basename(path)
        # A name may exist in both folders. Resolve to this file's own folder
        # first, so a citation means the nearest thing, then fall back to the
        # rules -- deterministic either way, never ambiguous.
        table = None
        if siblings and base in siblings and not path.startswith("../"):
            table = siblings
        elif base in published:
            table = published
        elif siblings and base in siblings:
            table = siblings
        if table is not None:
            dest_folder, name = table[base]
            prefix = "" if dest_folder == folder else f"../{dest_folder}/"
            return f"{m.group(1)}{prefix}{name}{suffix}{m.group(3)}"
        resolved = posixpath.normpath(posixpath.join(f"{skill_dir}/{folder}", path))
        if resolved.startswith(f"{skill_dir}/{folder}/"):
            return m.group(0)
        return f"{m.group(1)}{REPO_URL}/blob/main/{resolved}{suffix}{m.group(3)}"

    return _MD_LINK_RE.sub(fix, text)


def _reference_outputs(skills: list[skillsrc.SkillSource]) -> dict[str, str]:
    """Publish every rule file beside the artifact, flattened and prefixed.

    The flatten is only safe while basenames stay unique across skills, so a
    collision fails the compile rather than silently overwriting one rule with
    another from a different skill.
    """
    published: dict[str, tuple[str, str]] = {}
    for sk in skills:
        for ref in sk.refs:
            if ref.name in published:
                raise ValueError(
                    f"{ref.name} appears in more than one skill; the published "
                    "references/ folder is flat, so basenames must be unique "
                    "across skills for citations to resolve"
                )
            published[ref.name] = ("references", f"{skillsrc.rule_id(sk.name, ref.name)}.md")

    # A rule and its worked example may share a name -- references/client-singleton.md
    # and examples/client-singleton.md are the rule and the example of that rule,
    # and the pairing is the point: given one, the other is derivable. They land in
    # different folders, so nothing is overwritten. Examples are keyed separately so
    # a bare citation still resolves to exactly one file (see _portable_links).
    example_names: dict[str, tuple[str, str]] = {}
    for sk in skills:
        for ex in sk.examples:
            if ex.name in example_names:
                raise ValueError(
                    f"{ex.name} is an example in more than one skill; the published "
                    "examples/ folder is flat, so basenames must be unique across skills"
                )
            example_names[ex.name] = ("examples", f"{skillsrc.rule_id(sk.name, ex.name)}.md")

    out: dict[str, str] = {}
    for sk in skills:
        skill_dir = str(sk.dir.relative_to(REPO_ROOT))
        for ref in sk.refs:
            rel = f"{SINGLE_DIR}/references/{published[ref.name][1]}"
            out[rel] = _portable_links(ref.raw, skill_dir, published)
        for ex in sk.examples:
            rel = f"{SINGLE_DIR}/examples/{example_names[ex.name][1]}"
            out[rel] = _portable_links(
                ex.raw, skill_dir, published, folder="examples", siblings=example_names
            )
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
    ap.add_argument(
        "--coverage",
        action="store_true",
        help="report what SKILL.md defers to references/, and fail on content "
        "that left the package or that nothing points at",
    )
    args = ap.parse_args(argv)

    outputs = compile_outputs(args.shape, args.skills, args.layout)
    out_root = REPO_ROOT / COMPILED_DIR
    meta = {"shape": args.shape, "layout": args.layout, "sources": args.skills}

    if args.coverage:
        from scripts.skills_compile import coverage

        skills = [skillsrc.load_skill(REPO_ROOT / s) for s in args.skills]
        published = {p.split("/")[-1] for p in outputs if "/references/" in p}
        report = coverage.coverage_report(skills, published)
        print(report.summary())
        for defect in report.defects:
            print(f"::error::{defect}", file=sys.stderr)
        return 1 if report.defects else 0

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
