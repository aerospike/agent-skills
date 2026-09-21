"""Compile skills into monolith or stripped markdown (used by compile-agents.py)."""

from __future__ import annotations

import re

from scripts.skills_compile import skillsrc

_BULLET_RE = re.compile(r"^\s*(?:[-*]|\d+\.)\s+(.*)$")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_ITALIC_RE = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_FENCE_RE = re.compile(r"^\s*```")
_LONE_BOLD_RE = re.compile(r"^\*\*(.+)\*\*$")
_SECTION_KEYS = ("rule", "blacklist", "pitfall", "practice", "critical", "mapping")


def _clean_inline(text: str) -> str:
    text = _LINK_RE.sub(r"\1", text)
    text = _BOLD_RE.sub(r"\1", text)
    text = _ITALIC_RE.sub(r"\1", text)
    text = text.replace("`", "")
    return re.sub(r"\s+", " ", text).strip()


def split_blocks(text: str) -> list[str]:
    """Blank-line-separated blocks, never splitting inside a fenced code block.

    A fence can legally contain blank lines and lines starting with ``|`` or
    ``-``; splitting or classifying those as markdown would mangle a literal
    command into table rows.
    """
    blocks: list[str] = []
    cur: list[str] = []
    in_fence = False
    for line in text.strip().splitlines():
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            cur.append(line)
            continue
        if not line.strip() and not in_fence:
            if cur:
                blocks.append("\n".join(cur))
                cur = []
            continue
        cur.append(line)
    if cur:
        blocks.append("\n".join(cur))
    return blocks


def _block_kind(block: str) -> str:
    """Classify a block by its first non-blank line: fence, table, list or para.

    Classifying a list by its first line only is deliberate -- continuation
    lines are indented prose, and inspecting every line would demote a wrapped
    list back to a paragraph.
    """
    lines = [ln for ln in block.splitlines() if ln.strip()]
    if not lines:
        return "para"
    if _FENCE_RE.match(lines[0]):
        return "fence"
    if lines[0].lstrip().startswith("|"):
        return "table"
    if _BULLET_RE.match(lines[0]):
        return "list"
    return "para"


def _rule_lines(rule: str) -> list[str]:
    """Render a whole ``**Rule**`` section, not just its first paragraph.

    Paragraphs become top-level bullets; tables, lists and fenced code are
    indented under the bullet above them, which preserves the "these belong to
    the sentence I just read" relation that a flat list destroys. Every Rule
    section in the corpus opens with a paragraph, so an indented run always has
    a parent.
    """
    lines: list[str] = []
    for block in split_blocks(rule):
        kind = _block_kind(block)
        if kind == "fence":
            # Verbatim: _clean_inline would strip the backticks that make it code.
            lines.extend(f"  {ln}".rstrip() for ln in block.splitlines())
        elif kind == "table":
            lines.extend(f"  - {row}" for row in _extract_table_rows(block))
        elif kind == "list":
            lines.extend(f"  - {item}" for item in _list_items(block))
        else:
            stripped = block.strip()
            lone = _LONE_BOLD_RE.match(stripped)
            if lone and "\n" not in stripped:
                # A bold-only line is a sub-heading the compiler cannot see as a
                # section; emit it as a label so what follows reads under it.
                text = f"{_clean_inline(lone.group(1))}:"
            else:
                text = _clean_inline(block.replace("\n", " "))
            if text:
                lines.append(f"- {text}")
    return lines


def _list_items(content: str) -> list[str]:
    """Group list lines into items, folding continuation lines into their item.

    ``_BULLET_RE`` matches one line at a time, so a hard-wrapped bullet used to
    ship only its first physical line, and a ``**bold**`` run spanning the wrap
    left a stray ``**`` behind. A non-bullet line directly under a bullet, with
    no blank line between, is a continuation and belongs to it.

    A blank line closes the item, so prose that merely follows a list is still
    dropped rather than being glued onto the last bullet -- that separate loss
    is reported by the coverage check, not silently papered over here.
    """
    items: list[list[str]] = []
    open_item = False
    for line in content.splitlines():
        if not line.strip():
            open_item = False
            continue
        if line.lstrip().startswith("|"):
            open_item = False
            continue
        m = _BULLET_RE.match(line)
        if m:
            items.append([m.group(1)])
            open_item = True
        elif open_item:
            items[-1].append(line.strip())
    out: list[str] = []
    for parts in items:
        cleaned = _clean_inline(" ".join(parts))
        if cleaned:
            out.append(cleaned)
    return out


def _extract_bullets(content: str) -> list[str]:
    return _list_items(content)


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
            chunk = [head, *_rule_lines(rule)]
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
