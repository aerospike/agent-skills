"""Report what the compiler drops, and fail on the drops that are defects.

Two tiers, and the distinction is the whole design:

- Content dropped from ``SKILL.md`` but still shipped in ``references/`` is
  **reported**. The artifact is a router; the rule file is the full text. That
  is progressive disclosure working, not a bug.
- Content absent from the published package, or present but unreachable, is a
  **defect**. Nothing points at it, so for a consumer it does not exist.

The checker runs the real renderer and diffs word multisets rather than
re-implementing the rendering rules. A future change to ``render.py`` therefore
shows up here as a word-count delta without anyone editing this file -- which
is the only way a check like this survives contact with the code it guards.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from scripts.skills_compile import render, skillsrc

# Matches a rendered rule heading: `### <rule> — <title> [IMPACT]`.
_RULE_HEAD_RE = re.compile(r"^### (?P<rule>\S+) — (?P<title>.*?)(?: \[(?P<impact>\w+)\])?$")
_WORD_RE = re.compile(r"\w+")


@dataclass
class Defect:
    kind: str
    where: str
    detail: str

    def __str__(self) -> str:  # pragma: no cover - formatting only
        return f"{self.kind}: {self.where} — {self.detail}"


@dataclass
class Report:
    defects: list[Defect] = field(default_factory=list)
    deferred: Counter = field(default_factory=Counter)

    def summary(self) -> str:
        lines = [
            f"deferred to references/: "
            + ", ".join(f"{k} {v:,} words" for k, v in sorted(self.deferred.items()))
        ]
        lines.append(f"defects: {len(self.defects)}")
        lines.extend(f"  {d}" for d in self.defects)
        return "\n".join(lines)


def _words(text: str) -> Counter:
    """Normalised word bag, modelling the losses `_clean_inline` makes on purpose."""
    text = render._LINK_RE.sub(r"\1", text)
    return Counter(w.lower() for w in _WORD_RE.findall(text))


def _rule_slices(body: str) -> dict[str, str]:
    """Split the rendered body into {rule name: its lines}."""
    out: dict[str, list[str]] = {}
    current = None
    for line in body.splitlines():
        m = _RULE_HEAD_RE.match(line)
        if m:
            current = m.group("rule")
            out[current] = []
        elif line.startswith("### ") or line.startswith("## "):
            current = None
        elif current is not None:
            out[current].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def coverage_report(skills: list[skillsrc.SkillSource], published: set[str]) -> Report:
    """Compare each rule's source against what the artifact shipped for it.

    ``published`` is the set of reference filenames the compile emitted, used to
    decide whether a dropped block is deferred (fine) or gone (a defect).
    """
    rep = Report()
    body = render.render_stripped(skills)
    slices = _rule_slices(body)

    for sk in skills:
        # Examples carry no instruction, but a shipped file that SKILL.md never
        # names cannot be found by a reader -- the same guarantee the rules get.
        listed = next(
            (ln for ln in body.splitlines() if ln.startswith("- Runnable code for a task")),
            "",
        )
        for ex in sk.examples:
            stem = ex.name[:-3] if ex.name.endswith(".md") else ex.name
            if f"{skillsrc.rule_id(sk.name, ex.name)}.md" in published and stem not in listed:
                rep.defects.append(
                    Defect(
                        "unreachable-example",
                        ex.name,
                        "shipped but not named in the Worked examples list",
                    )
                )
        for ref in sk.refs:
            secs = skillsrc.labeled_sections(ref.body)
            rule = secs.get("Rule", "").strip()
            stem = ref.name[:-3] if ref.name.endswith(".md") else ref.name
            ident = f"{skillsrc.rule_id(sk.name, ref.name)}.md"

            if not rule:
                # Worked examples have no **Rule** and so carry no instruction,
                # but they still ship -- and a shipped file that no heading
                # names cannot be found by a reader of SKILL.md.
                if ident in published and stem not in slices:
                    rep.defects.append(
                        Defect(
                            "unreachable-rule-file",
                            ref.name,
                            "shipped but no heading in SKILL.md names it",
                        )
                    )
                continue

            if ident not in published:
                rep.defects.append(
                    Defect("unpublished-rule-file", ref.name, "cited but not shipped")
                )
                continue

            emitted = slices.get(stem)
            if emitted is None:
                rep.defects.append(
                    Defect("missing-heading", ref.name, "has a Rule but no heading")
                )
                continue

            # A rule line that ends in a colon promises something underneath it.
            for i, line in enumerate(emitted.splitlines()):
                if line.startswith("- ") and line.rstrip().endswith(":"):
                    rest = emitted.splitlines()[i + 1 :]
                    if not rest or not rest[0].startswith("  "):
                        rep.defects.append(
                            Defect(
                                "dangling-colon",
                                ref.name,
                                f"{line.strip()[:60]!r} introduces content that did not ship",
                            )
                        )

            dropped = _words(rule) - _words(emitted)
            if dropped:
                rep.deferred["Rule"] += sum(dropped.values())
            for label in ("Why", "See also"):
                if secs.get(label):
                    rep.deferred[label] += sum(_words(secs[label]).values())

            # Prose in Prefer/Avoid is dropped by _bullets_inline and, unlike a
            # Rule paragraph, has no indented form that would carry it.
            for label in ("Prefer", "Avoid"):
                section = secs.get(label, "")
                if not section:
                    continue
                bullets = "\n".join(render._list_items(section))
                lost = _words(section) - _words(bullets)
                if sum(lost.values()) > 5:
                    rep.defects.append(
                        Defect(
                            "dropped-prose",
                            ref.name,
                            f"{sum(lost.values())} words of non-bullet prose in **{label}**",
                        )
                    )
    return rep
