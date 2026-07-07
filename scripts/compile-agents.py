#!/usr/bin/env python3
"""Compile the skills/ source-of-truth into compiled-skills/ consumption artifacts.

The modular files under ``skills/`` are the source of truth for authors; this
script builds the published ``compiled-skills/SKILLS.md`` that end users download.

Usage (maintainers):
    python scripts/compile-agents.py --write
    python scripts/compile-agents.py --check
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
COMPILED_DIR = "compiled-skills"
SINGLE_OUT = f"{COMPILED_DIR}/SKILLS.md"

sys.path.insert(0, str(REPO_ROOT))

from scripts.skills_compile import skillsrc  # noqa: E402
from scripts.skills_compile.render import render_monolith, render_stripped  # noqa: E402

DEFAULT_SKILLS = [
    "skills/aerospike-getting-started",
    "skills/aerospike-development",
]

RENDERERS = {
    "stripped": render_stripped,
    "monolith": render_monolith,
}


def _header(skill_dirs: list[str]) -> str:
    return (
        f"_Auto-generated from `{'`, `'.join(skill_dirs)}`. "
        f"Edit the skills under `skills/`, not this file._\n"
    )


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
        out[SINGLE_OUT] = f"{_header(skill_dirs)}\n{body}\n"
        return out

    if layout == "multi":
        for sk, src in zip(skills, skill_dirs):
            rel = f"{COMPILED_DIR}/{sk.name}.md"
            body = render([sk]).strip()
            out[rel] = f"{_header([src])}\n{body}\n"
        return out

    raise ValueError(f"Unknown layout: {layout!r}")


def _write_manifest(out_dir: pathlib.Path, outputs: dict[str, str], meta: dict) -> None:
    manifest = {
        **meta,
        "files": {path: len(content) for path, content in sorted(outputs.items())},
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Compile skills/ into compiled-skills/.")
    ap.add_argument("--shape", choices=list(RENDERERS), default="stripped")
    ap.add_argument(
        "--layout",
        choices=["single", "multi"],
        default="single",
        help="single -> compiled-skills/SKILLS.md; multi -> one .md per skill",
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
        manifest_path = out_root / "manifest.json"
        if manifest_path.exists():
            try:
                on_disk = json.loads(manifest_path.read_text(encoding="utf-8"))
                if on_disk.get("shape") != args.shape or on_disk.get("layout") != args.layout:
                    stale.append("manifest.json (metadata)")
            except json.JSONDecodeError:
                stale.append("manifest.json")
        elif not stale:
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
