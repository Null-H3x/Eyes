"""Investigation workflow map — numbered phases and SVG diagram for the workbench.

Tool numbers follow investigation *sequencing* (not eyes.py list order):

  01 Datastream → 02 Family ID → 03 Anchors & templates → 04 Attack → 05 Validate
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, Tuple

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from dashboard.registry import Tool, load_tools


@dataclass(frozen=True)
class WorkflowPhase:
    id: str
    title: str
    subtitle: str
    color: str


PHASES: Tuple[WorkflowPhase, ...] = (
    WorkflowPhase(
        "datastream", "01 · Datastream",
        "Corpus integrity, provenance, deck size", "#58a6ff"),
    WorkflowPhase(
        "family", "02 · Family ID",
        "Cipher type & structural classification", "#d29922"),
    WorkflowPhase(
        "anchors", "03 · Anchors & templates",
        "Passage, refrain, viewer patterns", "#c9a227"),
    WorkflowPhase(
        "attack", "04 · Attack",
        "Cribs, ordering, seed scans", "#f85149"),
    WorkflowPhase(
        "validate", "05 · Validate",
        "Audits, math gate, integration", "#3fb950"),
)

# Tool title keywords → phase (first match wins).
_PHASE_RULES: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("datastream", (
        "datastream", "binary provenance", "infer deck size",
    )),
    ("family", (
        "cipher type", "keystream scope", "header test", "number test",
        "depth map", "salakieli aes", "repeat census", "trifid",
        "cipher fingerprint", "cipher-construction", "cipher lattice",
        "model verification", "keyspace ledger", "isomorph chain",
        "maximal-aligned", "triplet embedded", "triplet key",
        "structural fingerprint", "verify fingerprint", "header-base",
        "pure-progressive", "shared-structure", "depth / crib",
        "eyescoreboard", "eyewitness", "iso_extract",
    )),
    ("anchors", (
        "passage template", "viewer anchor", "refrain repeat-template",
        "refrain template", "show-template",
    )),
    ("attack", (
        "eyecrack", "crib", "refrain_attack", "refrain sweep",
        "refrain compose", "n-gram", "ordering", "keyscan",
        "globality", "seed", "salakieli crib", "calibrate",
        "structscan", "demo", "ordering exhaust", "crib-drag",
        "crib-placement", "crib-seeded", "crib->seed", "crib-globality",
    )),
    ("validate", (
        "paranoia audit", "math gate", "integration",
    )),
)


def _phase_for_tool(title: str, group: str) -> str:
    low = title.lower()
    for phase_id, needles in _PHASE_RULES:
        if any(n in low for n in needles):
            return phase_id
    if group == "Attack":
        return "attack"
    if group == "Validate":
        return "validate"
    return "family"


def annotate_tools(tools: Sequence[Tool] | None = None) -> List[dict]:
    """Return tool dicts numbered by investigation phase sequence."""
    tools = list(tools or load_tools())
    phase_order = {p.id: i for i, p in enumerate(PHASES)}

    indexed = [
        (orig, t, _phase_for_tool(t.title, t.group))
        for orig, t in enumerate(tools)
    ]
    indexed.sort(key=lambda x: (phase_order.get(x[2], 99), x[0]))

    out: List[dict] = []
    phase_counters = {p.id: 0 for p in PHASES}
    for seq_num, (orig, t, phase_id) in enumerate(indexed, start=1):
        phase_counters[phase_id] = phase_counters.get(phase_id, 0) + 1
        phase = next(p for p in PHASES if p.id == phase_id)
        phase_idx = phase_order[phase_id] + 1
        in_phase = phase_counters[phase_id]
        d = {**t.__dict__, "command": t.command}
        d["num"] = seq_num
        d["num_label"] = f"{seq_num:02d}"
        d["phase"] = phase_id
        d["phase_num"] = phase_idx
        d["phase_label"] = phase.title
        d["num_in_phase"] = in_phase
        d["seq_label"] = f"{phase_idx:02d}.{in_phase:02d}"
        d["phase_title"] = phase.title
        d["phase_color"] = phase.color
        d["orig_order"] = orig + 1
        out.append(d)
    return out


def workflow_map_payload(tools: Sequence[Tool] | None = None) -> dict:
    annotated = annotate_tools(tools)
    by_phase = {p.id: [] for p in PHASES}
    for t in annotated:
        by_phase[t["phase"]].append(t)
    return {
        "phases": [
            {"id": p.id, "title": p.title, "subtitle": p.subtitle, "color": p.color,
             "tools": by_phase[p.id]}
            for p in PHASES
        ],
        "edges": [
            ("datastream", "family"),
            ("family", "anchors"),
            ("anchors", "attack"),
            ("attack", "validate"),
        ],
        "tool_count": len(annotated),
        "sequence": [p.title for p in PHASES],
    }


def render_workflow_svg(payload: dict, *, width: int = 1100) -> str:
    """Inline SVG flowchart; each tool node shows its global sequence number."""
    phases = payload["phases"]
    row_h = 88
    pad_x = 24
    pad_y = 36
    height = pad_y * 2 + len(phases) * row_h
    nodes = []
    centers = {}

    for ri, phase in enumerate(phases):
        y = pad_y + ri * row_h + 28
        tools = phase["tools"]
        if not tools:
            continue
        n = len(tools)
        usable = width - 2 * pad_x
        step = min(118, usable // max(n, 1))
        start_x = pad_x + max(0, (usable - step * n) // 2)
        cx_phase = width // 2
        centers[phase["id"]] = (cx_phase, y)
        nodes.append(
            f'<text x="{cx_phase}" y="{y - 18}" text-anchor="middle" '
            f'font-size="11" fill="{phase["color"]}" font-weight="bold">'
            f'{phase["title"]}</text>'
        )
        nodes.append(
            f'<text x="{cx_phase}" y="{y - 6}" text-anchor="middle" '
            f'font-size="9" fill="#a99c80">{phase["subtitle"]}</text>'
        )
        for ti, tool in enumerate(tools):
            x = start_x + ti * step + step // 2
            num = tool["num_label"]
            short = _short_title(tool["title"])
            nodes.append(
                f'<g class="wf-node" data-num="{tool["num"]}" data-id="{tool["id"]}" '
                f'role="button" tabindex="0">'
                f'<rect x="{x - 22}" y="{y - 2}" width="44" height="44" rx="6" '
                f'fill="#1c160f" stroke="{phase["color"]}" stroke-width="1.2"/>'
                f'<text x="{x}" y="{y + 14}" text-anchor="middle" font-size="13" '
                f'fill="{phase["color"]}" font-weight="bold">{num}</text>'
                f'<title>{tool["seq_label"]} {tool["title"]} — {tool["command"]}</title>'
                f'</g>'
            )
            nodes.append(
                f'<text x="{x}" y="{y + 58}" text-anchor="middle" font-size="8" '
                f'fill="#e8dcc0" opacity="0.85">{_escape(short)}</text>'
            )

    edges = payload.get("edges", [])
    edge_lines = []
    for a, b in edges:
        if a in centers and b in centers:
            x1, y1 = centers[a]
            x2, y2 = centers[b]
            edge_lines.append(
                f'<line x1="{x1}" y1="{y1 + 44}" x2="{x2}" y2="{y2 - 22}" '
                f'stroke="#3a3220" stroke-width="1.5" marker-end="url(#arrow)"/>'
            )

    return (
        f'<svg class="workflow-svg" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="EYES investigation workflow">'
        f'<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" '
        f'orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#3a3220"/></marker></defs>'
        f'{"".join(edge_lines)}{"".join(nodes)}</svg>'
    )


def _short_title(title: str, max_len: int = 14) -> str:
    t = title.replace("EyeCrack — ", "").replace("EyeCrack ", "")
    if len(t) <= max_len:
        return t
    return t[: max_len - 1] + "…"


def _escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def selftest() -> List[Tuple[str, bool]]:
    from dashboard.registry import load_tools

    tools = load_tools()
    annotated = annotate_tools(tools)
    payload = workflow_map_payload(tools)
    out: List[Tuple[str, bool]] = []

    out.append(("five investigation phases", len(PHASES) == 5))
    out.append(("all tools numbered", len(annotated) == len(tools)))
    out.append(("numbers unique", len({t["num"] for t in annotated}) == len(tools)))

    # Numbers increase monotonically across phase order.
    phase_rank = {p.id: i for i, p in enumerate(PHASES)}
    mono = all(
        phase_rank[annotated[i]["phase"]] <= phase_rank[annotated[i + 1]["phase"]]
        for i in range(len(annotated) - 1)
    )
    out.append(("numbers follow phase sequence", mono))

    ds = [t for t in annotated if t["phase"] == "datastream"]
    fam = [t for t in annotated if t["phase"] == "family"]
    out.append(("datastream before family", ds and fam and ds[-1]["num"] < fam[0]["num"]))

    out.append(("datastream includes datastream check",
                any("datastream" in t["title"].lower() for t in ds)))
    out.append(("svg renders", "workflow-svg" in render_workflow_svg(payload)))

    return out


if __name__ == "__main__":
    import sys
    from pathlib import Path
    _root = Path(__file__).resolve().parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n = sum(1 for _, ok in results if ok)
    print(f"\n{n}/{len(results)} workflow_map checks passed")
    sys.exit(0 if n == len(results) else 1)
