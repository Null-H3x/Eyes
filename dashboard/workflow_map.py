"""Investigation workflow map — numbered phases and SVG diagram for the workbench."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

from dashboard.registry import Tool, load_tools


@dataclass(frozen=True)
class WorkflowPhase:
    id: str
    title: str
    subtitle: str
    color: str


PHASES: Tuple[WorkflowPhase, ...] = (
    WorkflowPhase("corpus", "Corpus & provenance", "Data integrity, binary source", "#58a6ff"),
    WorkflowPhase("family", "Cipher family", "Rule out mono / transposition / AES", "#d29922"),
    WorkflowPhase("structure", "Structure mining", "Isomorphs, triplets, depth", "#4ec9b0"),
    WorkflowPhase("anchors", "Anchors & templates", "Passage, refrain, viewer patterns", "#c9a227"),
    WorkflowPhase("attack", "Attacks", "Cribs, ordering, seed scans", "#f85149"),
    WorkflowPhase("validate", "Validate", "Audits and math gate", "#3fb950"),
)

# Tool title keywords → phase (first match wins; order follows eyes.py WORKFLOWS).
_PHASE_RULES: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("corpus", ("datastream", "binary provenance", "provenance")),
    ("family", ("cipher type", "keystream scope", "header test", "number test",
                "depth map", "salakieli aes", "repeat census", "trifid",
                "cipher fingerprint", "cipher-construction", "cipher lattice",
                "model verification", "keyspace ledger")),
    ("structure", ("isomorph", "triplet", "fingerprint", "eyewitness",
                   "verify fingerprint", "header-base", "pure-progressive",
                   "shared-structure", "depth / crib", "eyescoreboard")),
    ("anchors", ("passage template", "viewer anchor", "refrain repeat-template",
                 "refrain template", "maximal-aligned")),
    ("attack", ("eyecrack", "crib", "refrain", "n-gram", "ordering",
                 "keyscan", "globality", "seed", "salakieli crib",
                 "calibrate", "structscan", "demo")),
    ("validate", ("paranoia audit", "math gate", "integration")),
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
    return "structure"


def annotate_tools(tools: Sequence[Tool] | None = None) -> List[dict]:
    """Return tool dicts with global ``num`` and ``phase`` metadata."""
    tools = tools or load_tools()
    out = []
    for i, t in enumerate(tools, start=1):
        d = {**t.__dict__, "command": t.command}
        d["num"] = i
        d["num_label"] = f"{i:02d}"
        d["phase"] = _phase_for_tool(t.title, t.group)
        phase = next(p for p in PHASES if p.id == d["phase"])
        d["phase_title"] = phase.title
        d["phase_color"] = phase.color
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
            ("corpus", "family"),
            ("family", "structure"),
            ("structure", "anchors"),
            ("anchors", "attack"),
            ("attack", "validate"),
        ],
        "tool_count": len(annotated),
    }


def render_workflow_svg(payload: dict, *, width: int = 1100) -> str:
    """Inline SVG flowchart; each tool node shows its global number."""
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
        # phase label
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
                f'<title>{tool["title"]} — {tool["command"]}</title>'
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
