"""Parse the source skills into a structured form the variant generator can reshape.

A skill on disk is ``SKILL.md`` (with YAML frontmatter) plus optional companion
markdown (``examples.md``, ``reference.md``) and an optional ``references/``
folder of one-concern rule files. We parse just enough structure -- frontmatter,
headings, and the ``**Rule** / **Prefer** / **Avoid**`` labels -- to emit the
monolith, stripped, and hybrid shapes from the same content.
"""

from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass, field
from typing import Any

import yaml

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
_LABEL_RE = re.compile(r"^\*\*(.+?)\*\*\s*$", re.MULTILINE)
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)

# Reference-folder files that are scaffolding rather than knowledge.
_SKIP_REFS = {"README.md", "_template.md"}


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Return (frontmatter_dict, body). Missing/!invalid frontmatter -> ({}, text)."""
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except Exception:
        meta = {}
    return (meta if isinstance(meta, dict) else {}), text[m.end():]


def labeled_sections(body: str) -> dict[str, str]:
    """Split a reference body on ``**Label**`` lines into {label: content}."""
    out: dict[str, str] = {}
    matches = list(_LABEL_RE.finditer(body))
    for i, m in enumerate(matches):
        label = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        out[label] = body[start:end].strip()
    return out


def heading_sections(body: str) -> list[tuple[int, str, str]]:
    """Return [(level, title, content)] for each markdown heading in order."""
    out: list[tuple[int, str, str]] = []
    matches = list(_HEADING_RE.finditer(body))
    for i, m in enumerate(matches):
        level = len(m.group(1))
        title = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        out.append((level, title, body[start:end].strip()))
    return out


@dataclass
class RefFile:
    name: str  # basename, e.g. client-singleton.md
    prefix: str  # e.g. "client"
    rel: str  # path relative to skill dir, e.g. references/client-singleton.md
    meta: dict[str, Any]
    body: str  # frontmatter stripped
    raw: str  # original text


@dataclass
class CompanionFile:
    name: str
    rel: str
    raw: str


@dataclass
class SkillSource:
    name: str
    dir: pathlib.Path
    skill_md_raw: str
    skill_md_meta: dict[str, Any]
    skill_md_body: str
    companions: list[CompanionFile] = field(default_factory=list)
    refs: list[RefFile] = field(default_factory=list)


def load_skill(skill_dir: str | pathlib.Path) -> SkillSource:
    d = pathlib.Path(skill_dir)
    skill_md = (d / "SKILL.md").read_text(encoding="utf-8")
    meta, body = split_frontmatter(skill_md)
    name = meta.get("name", d.name)

    companions: list[CompanionFile] = []
    for md in sorted(d.glob("*.md")):
        if md.name == "SKILL.md":
            continue
        companions.append(
            CompanionFile(name=md.name, rel=md.name, raw=md.read_text(encoding="utf-8"))
        )

    refs: list[RefFile] = []
    ref_dir = d / "references"
    if ref_dir.is_dir():
        for md in sorted(ref_dir.glob("*.md")):
            if md.name in _SKIP_REFS:
                continue
            raw = md.read_text(encoding="utf-8")
            rmeta, rbody = split_frontmatter(raw)
            refs.append(
                RefFile(
                    name=md.name,
                    prefix=md.stem.split("-")[0],
                    rel=f"references/{md.name}",
                    meta=rmeta,
                    body=rbody,
                    raw=raw,
                )
            )
    return SkillSource(
        name=name,
        dir=d,
        skill_md_raw=skill_md,
        skill_md_meta=meta,
        skill_md_body=body,
        companions=companions,
        refs=refs,
    )
