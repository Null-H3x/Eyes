"""Tool catalog — mirrors ``eyes.py`` WORKFLOWS with stable IDs and metadata."""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Sequence, Tuple

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import eyes  # noqa: E402


@dataclass(frozen=True)
class Tool:
    id: str
    title: str
    group: str
    cwd: str
    argv: Tuple[str, ...]
    duration: str = "medium"          # fast | medium | long
    tags: Tuple[str, ...] = field(default_factory=tuple)

    @property
    def command(self) -> str:
        return f"python3 {self.cwd}/{' '.join(self.argv)}"

    @property
    def alphabet_dependent(self) -> bool:
        from dashboard.cut_recipe import is_alphabet_dependent_tool
        return is_alphabet_dependent_tool(self.argv)


_GROUP_PREFIX = {
    "Map the structure": "map",
    "Attack": "attack",
    "Validate": "validate",
}

_DURATION_HINTS = (
    (("selftest", "audit", "verify", "list-targets", "show-template", "--doubles"),
     "fast"),
    (("1000000", "100000000", "structscan", "seedscan", "globality_gpu"), "long"),
)


def _slug(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:48] or "tool"


def _duration(argv: Sequence[str]) -> str:
    joined = " ".join(argv)
    for needles, label in _DURATION_HINTS:
        if any(n in joined for n in needles):
            return label
    return "medium"


def _make_id(group: str, title: str, used: set) -> str:
    base = f"{_GROUP_PREFIX.get(group, 'tool')}-{_slug(title)}"
    tid = base
    n = 2
    while tid in used:
        tid = f"{base}-{n}"
        n += 1
    used.add(tid)
    return tid


def _tags(group: str, title: str, argv: Sequence[str]) -> Tuple[str, ...]:
    t = {group.lower().replace(" ", "-")}
    low = title.lower()
    if "refrain" in low:
        t.add("refrain")
    if "audit" in low or "validate" in group.lower():
        t.add("audit")
    if "seed" in low or "globality" in low or "gpu" in low:
        t.add("heavy")
    if "template" in low or "viewer" in low or "passage" in low:
        t.add("template")
    if any("html" in a for a in argv):
        t.add("report")
    if any(m in " ".join(argv) for m in (
        "order_solve.py", "refrain_attack.py", "ngram_solve.py",
        "refrain_sweep.py", "crib_fit.py", "deck_sweep.py",
    )):
        t.add("alphabet")
    return tuple(sorted(t))


def load_tools() -> List[Tool]:
    used: set = set()
    out: List[Tool] = []
    for title, group, cwd, argv in eyes.WORKFLOWS:
        tid = _make_id(group, title, used)
        out.append(Tool(
            id=tid,
            title=title,
            group=group,
            cwd=cwd,
            argv=tuple(argv),
            duration=_duration(argv),
            tags=_tags(group, title, argv),
        ))
    return out


def tool_by_id(tools: Sequence[Tool] | None = None) -> dict:
    tools = tools or load_tools()
    return {t.id: t for t in tools}


def tool_index(tools: Sequence[Tool] | None = None) -> dict:
    return tool_by_id(tools)
