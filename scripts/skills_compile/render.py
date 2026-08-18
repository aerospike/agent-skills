"""Compile skills into monolith or stripped markdown (used by compile-agents.py)."""

from __future__ import annotations

import re

from scripts.skills_compile import skillsrc

_BULLET_RE = re.compile(r"^\s*(?:[-*]|\d+\.)\s+(.*)$")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_SECTION_KEYS = ("rule", "blacklist", "pitfall", "practice", "critical", "mapping")


def _clean_inline(text: str) -> str:
    text = _LINK_RE.sub(r"\1", text)
    text = _BOLD_RE.sub(r"\1", text)
    text = text.replace("`", "")
    return re.sub(r"\s+", " ", text).strip()


def _collapse(text: str) -> str:
    para = text.strip().split("\n\n", 1)[0]
    return _clean_inline(para.replace("\n", " "))


def _extract_bullets(content: str) -> list[str]:
    out: list[str] = []
    for line in content.splitlines():
        if line.lstrip().startswith("|"):
            continue
        m = _BULLET_RE.match(line)
        if m:
            cleaned = _clean_inline(m.group(1))
            if cleaned:
                out.append(cleaned)
    return out


def _extract_table_rows(content: str) -> list[str]:
    rows: list[str] = []
    lines = [ln for ln in content.splitlines() if ln.strip().startswith("|")]
    for i, line in enumerate(lines):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells:
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        if i + 1 < len(lines):
            nxt = [c.strip() for c in lines[i + 1].strip().strip("|").split("|")]
            if nxt and all(set(c) <= set("-: ") for c in nxt):
                continue
        cells = [_clean_inline(c) for c in cells if c]
        if len(cells) >= 2:
            rows.append(f"{cells[0]} -> {'; '.join(cells[1:])}")
        elif cells:
            rows.append(cells[0])
    return rows


def _bullets_inline(content: str) -> str:
    return "; ".join(_extract_bullets(content))


def render_monolith(skills: list[skillsrc.SkillSource]) -> str:
    """Flatten everything into one document, reasoning retained."""
    parts = ["# Aerospike agent guide (compiled, full)\n"]
    for sk in skills:
        parts.append(f"\n# {sk.name}\n")
        parts.append(sk.skill_md_body.strip())
        for comp in sk.companions:
            _, body = skillsrc.split_frontmatter(comp.raw)
            parts.append(f"\n## (companion) {comp.name}\n")
            parts.append(body.strip())
        for ref in sk.refs:
            parts.append(f"\n## (rule) {ref.name}\n")
            parts.append(ref.body.strip())
    return "\n".join(parts)


def render_stripped(skills: list[skillsrc.SkillSource]) -> str:
    """Compile to imperative IF/THEN rules with reasoning removed."""
    parts = ["# Aerospike agent rules\n"]
    for sk in skills:
        parts.append(f"\n## {sk.name}\n")
        for _level, title, content in skillsrc.heading_sections(sk.skill_md_body):
            if not any(k in title.lower() for k in _SECTION_KEYS):
                continue
            items = _extract_bullets(content) + _extract_table_rows(content)
            if items:
                parts.append(f"\n### {title}")
                parts.extend(f"- {it}" for it in items)
        for ref in sk.refs:
            secs = skillsrc.labeled_sections(ref.body)
            rule = secs.get("Rule", "").strip()
            if not rule:
                continue
            title = ref.meta.get("title") or ref.name
            impact = ref.meta.get("impact", "")
            head = f"\n### {title}" + (f" [{impact}]" if impact else "")
            chunk = [head, f"- {_collapse(rule)}"]
            if secs.get("Prefer"):
                pref = _bullets_inline(secs["Prefer"])
                if pref:
                    chunk.append(f"- Prefer: {pref}")
            if secs.get("Avoid"):
                avoid = _bullets_inline(secs["Avoid"])
                if avoid:
                    chunk.append(f"- Avoid: {avoid}")
            parts.extend(chunk)
    return "\n".join(parts)
