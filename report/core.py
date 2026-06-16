"""Dashboard core: data model, scoring, inline-SVG charts, and the Grimoire
HTML renderer.

Design rules (the project's ethos, enforced structurally):
* The dashboard never computes its own cryptanalytic math — it only *renders*
  results produced by the selftested ``noita_eye_core`` modules.  Each card
  carries a validation badge tying it to that module's ground-truth selftest.
* Self-contained output: inline CSS + server-side inline SVG, no CDN, no chart
  libraries, no external fonts.  A skeptic can view-source every number and shape.
* Verified exclusions are first-class, scored alongside positive findings, and a
  dedicated ARTIFACT tier names results that are significant only before a
  confound control (so our own false leads are labelled, loudly).
"""
from __future__ import annotations

import html
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

VERDICTS = ("supported", "exclusion", "suggestive", "inconclusive", "artifact")


@dataclass
class Chart:
    kind: str                       # "bar" | "hist" | "heatmap"
    title: str
    labels: Sequence[str] = field(default_factory=list)
    values: Sequence[float] = field(default_factory=list)
    matrix: Optional[Sequence[Sequence[float]]] = None
    note: str = ""
    baseline: Optional[float] = None  # draws a reference line (bar/hist)


@dataclass
class HypothesisResult:
    id: str
    title: str
    group: str                      # tab name
    question: str
    verdict: str                    # one of VERDICTS
    strength: float                 # 0..1 evidence strength (author-supplied)
    leverage: int                   # 1..5 how much it narrows the problem
    statistic: str                  # human label of the key number
    null_desc: str
    formula: str
    validated_by: str               # e.g. "keystream_scope 7/7 ✓"
    reproduce: str
    interpretation: str
    charts: List[Chart] = field(default_factory=list)
    # filled by scoring
    score: int = 0
    tier: str = "inconclusive"


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

# tier key -> (label, color, glyph)
TIERS: Dict[str, Tuple[str, str, str]] = {
    "confirmed":    ("Confirmed",            "#3fb950", "●"),
    "exclusion":    ("Verified exclusion",   "#58a6ff", "⛔"),
    "suggestive":   ("Suggestive",           "#d29922", "◐"),
    "inconclusive": ("Inconclusive",         "#8b949e", "○"),
    "artifact":     ("Artifact / confounded", "#f85149", "✕"),
}


def sig_strength(z: float, robust: bool = True) -> float:
    """Evidence strength in [0,1] from a z-score, with a robustness penalty for
    results that do not survive their confound control."""
    s = 1.0 - math.exp(-max(0.0, z) / 6.0)
    if not robust:
        s *= 0.4
    return max(0.0, min(1.0, s))


def power_strength(powered: bool, margin: float = 1.0) -> float:
    """Strength of an EXCLUSION: high when the test was adequately powered and
    the effect is clearly absent; low when underpowered."""
    if not powered:
        return 0.2
    return max(0.0, min(1.0, 0.6 + 0.4 * min(1.0, margin)))


def tier_for(verdict: str, strength: float) -> str:
    if verdict == "artifact":
        return "artifact"
    if strength < 0.3:
        return "inconclusive"
    if verdict == "supported":
        return "confirmed" if strength >= 0.7 else "suggestive"
    if verdict == "exclusion":
        return "exclusion" if strength >= 0.7 else "suggestive"
    if verdict == "inconclusive":
        return "inconclusive"
    return "suggestive"


def score_value(strength: float, leverage: int) -> int:
    return int(round(100 * strength * (0.5 + 0.1 * max(1, min(5, leverage)))))


def apply_scoring(r: HypothesisResult) -> HypothesisResult:
    r.tier = tier_for(r.verdict, r.strength)
    r.score = score_value(r.strength, r.leverage)
    return r


# ---------------------------------------------------------------------------
# Inline SVG charts (deterministic, no JS)
# ---------------------------------------------------------------------------

_GOLD = "#c9a227"
_TEAL = "#4ec9b0"
_INK = "#e8dcc0"
_GRID = "#3a322210"


def _svg_bar(ch: Chart, w: int = 520, h: int = 200) -> str:
    vals = list(ch.values) or [0]
    labels = list(ch.labels) or [""] * len(vals)
    vmax = max(vals + ([ch.baseline] if ch.baseline else []) + [1e-9])
    pad_l, pad_b, pad_t = 40, 28, 10
    bw = (w - pad_l - 10) / max(1, len(vals))
    bars = []
    for i, v in enumerate(vals):
        bh = (h - pad_b - pad_t) * (v / vmax)
        x = pad_l + i * bw
        y = h - pad_b - bh
        bars.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw*0.8:.1f}" '
                    f'height="{bh:.1f}" fill="{_GOLD}" opacity="0.85"></rect>')
        if len(labels) <= 16:
            bars.append(f'<text x="{x+bw*0.4:.1f}" y="{h-pad_b+12:.0f}" '
                        f'font-size="9" fill="{_INK}" text-anchor="middle" '
                        f'opacity="0.7">{html.escape(str(labels[i]))}</text>')
    base = ""
    if ch.baseline:
        by = h - pad_b - (h - pad_b - pad_t) * (ch.baseline / vmax)
        base = (f'<line x1="{pad_l}" y1="{by:.1f}" x2="{w-10}" y2="{by:.1f}" '
                f'stroke="{_TEAL}" stroke-dasharray="4 3" stroke-width="1"></line>'
                f'<text x="{w-12}" y="{by-3:.1f}" font-size="9" fill="{_TEAL}" '
                f'text-anchor="end">baseline {ch.baseline:.3g}</text>')
    return (f'<svg viewBox="0 0 {w} {h}" class="chart" role="img">'
            f'<text x="{pad_l}" y="12" font-size="10" fill="{_INK}" '
            f'opacity="0.8">{html.escape(ch.title)}</text>'
            f'{"".join(bars)}{base}</svg>')


def _svg_heatmap(ch: Chart, cell: int = 34) -> str:
    M = ch.matrix or []
    n = len(M)
    labels = list(ch.labels) or [str(i) for i in range(n)]
    pad = 46
    w = pad + n * cell + 10
    h = pad + n * cell + 10
    vmax = max((max(row) for row in M), default=1e-9) or 1e-9
    cells = []
    for i in range(n):
        for j in range(n):
            v = M[i][j]
            inten = v / vmax
            # parchment->gold->teal ramp
            col = (f"rgba(78,201,176,{0.12+0.8*inten:.2f})" if i != j
                   else "rgba(201,162,39,0.30)")
            x = pad + j * cell
            y = pad + i * cell
            cells.append(f'<rect x="{x}" y="{y}" width="{cell-1}" '
                         f'height="{cell-1}" fill="{col}"></rect>')
            if n <= 10 and i != j:
                cells.append(f'<text x="{x+cell/2:.0f}" y="{y+cell/2+3:.0f}" '
                             f'font-size="8" fill="{_INK}" text-anchor="middle" '
                             f'opacity="0.75">{v:.2f}</text>')
    for k in range(n):
        cells.append(f'<text x="{pad+k*cell+cell/2:.0f}" y="{pad-6}" '
                     f'font-size="8" fill="{_GOLD}" text-anchor="middle">'
                     f'{html.escape(labels[k][:3])}</text>')
        cells.append(f'<text x="{pad-6}" y="{pad+k*cell+cell/2+3:.0f}" '
                     f'font-size="8" fill="{_GOLD}" text-anchor="end">'
                     f'{html.escape(labels[k][:3])}</text>')
    return (f'<svg viewBox="0 0 {w} {h}" class="chart" role="img">'
            f'<text x="{pad}" y="14" font-size="10" fill="{_INK}" opacity="0.8">'
            f'{html.escape(ch.title)}</text>{"".join(cells)}</svg>')


def render_chart(ch: Chart) -> str:
    if ch.kind == "heatmap":
        body = _svg_heatmap(ch)
    else:
        body = _svg_bar(ch)
    note = (f'<div class="chart-note">{html.escape(ch.note)}</div>'
            if ch.note else "")
    return f'<div class="chart-wrap">{body}{note}</div>'


# ---------------------------------------------------------------------------
# HTML render (Grimoire)
# ---------------------------------------------------------------------------

_CSS = """
:root{--bg:#0f0d0a;--bg2:#17130d;--panel:#1c160f;--ink:#e8dcc0;--dim:#a99c80;
--gold:#c9a227;--teal:#4ec9b0;--red:#f85149;--blue:#58a6ff;--amber:#d29922;}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(circle at 50% -10%,#241c11,#0f0d0a 70%);
color:var(--ink);font-family:Georgia,'Times New Roman',serif;line-height:1.5}
a{color:var(--gold)}
.wrap{max-width:1080px;margin:0 auto;padding:28px 20px 80px}
header.grim{text-align:center;border-bottom:1px solid #3a3220;padding-bottom:18px}
header.grim h1{font-size:2.4rem;letter-spacing:.18em;margin:.2em 0;
text-shadow:0 0 18px rgba(201,162,39,.35);color:var(--gold)}
header.grim .sub{color:var(--dim);font-style:italic;letter-spacing:.05em}
.meta{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.72rem;
color:var(--dim);margin-top:10px;word-break:break-all}
.banner{margin:16px 0;padding:10px 14px;border-radius:6px;text-align:center;
font-weight:bold;letter-spacing:.05em}
.banner.ok{background:rgba(63,185,80,.12);border:1px solid #3fb95055;color:#7ee787}
.banner.bad{background:rgba(248,81,73,.12);border:1px solid #f8514955;color:#ffa198}
.summary{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin:16px 0}
.pill{padding:6px 12px;border-radius:20px;font-size:.8rem;border:1px solid #ffffff14}
.tabs{margin-top:20px}
.tabs input{display:none}
.tabbar{display:flex;flex-wrap:wrap;gap:6px;border-bottom:1px solid #3a3220;
margin-bottom:18px}
.tabbar label{padding:8px 16px;cursor:pointer;color:var(--dim);
border:1px solid transparent;border-bottom:none;letter-spacing:.06em;font-size:.9rem}
.tabbar label:hover{color:var(--ink)}
.panel{display:none}
#t0:checked~.tabbar label[for=t0],#t1:checked~.tabbar label[for=t1],
#t2:checked~.tabbar label[for=t2],#t3:checked~.tabbar label[for=t3]{
color:var(--gold);border-color:#3a3220;border-radius:6px 6px 0 0;
background:var(--panel)}
#t0:checked~#p0,#t1:checked~#p1,#t2:checked~#p2,#t3:checked~#p3{display:block}
.card{background:linear-gradient(180deg,var(--panel),#140f0a);
border:1px solid #2d2615;border-radius:10px;padding:18px 20px;margin:0 0 18px;
box-shadow:0 2px 14px #00000055}
.card h3{margin:.1em 0;color:var(--ink);font-size:1.2rem}
.card .q{color:var(--dim);font-style:italic;margin:.2em 0 .8em}
.row{display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start}
.col{flex:1;min-width:260px}
.tier{display:inline-block;padding:3px 10px;border-radius:14px;font-size:.78rem;
font-weight:bold;letter-spacing:.04em}
.score{font-family:ui-monospace,monospace;font-size:1.5rem;float:right;color:var(--gold)}
.kv{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.78rem;
color:var(--ink);margin:.25em 0}
.kv b{color:var(--teal)}
.formula{font-family:ui-monospace,monospace;font-size:.76rem;color:#cdbfa0;
background:#0c0a07;border-left:2px solid var(--gold);padding:6px 10px;margin:8px 0;
white-space:pre-wrap;border-radius:0 4px 4px 0}
.badge{font-size:.72rem;color:#7ee787}
.repro{font-family:ui-monospace,monospace;font-size:.72rem;color:var(--dim);
background:#0c0a07;padding:5px 9px;border-radius:4px;margin-top:8px;display:inline-block}
.interp{margin-top:10px;color:var(--ink)}
.chart-wrap{margin:8px 0}
svg.chart{width:100%;height:auto;background:#0c0a07;border:1px solid #241d10;
border-radius:6px;padding:4px}
.chart-note{font-size:.72rem;color:var(--dim);margin-top:2px}
footer{margin-top:40px;text-align:center;color:var(--dim);font-size:.74rem}
"""

_GROUPS = [("Cipher type", 0), ("Structure & grouping", 1),
           ("Attack readiness", 2), ("Foundations", 3)]


def _card_html(r: HypothesisResult) -> str:
    label, color, glyph = TIERS[r.tier]
    charts = "".join(render_chart(c) for c in r.charts)
    return f"""
<div class="card">
  <span class="score">{r.score}</span>
  <h3>{html.escape(r.title)}</h3>
  <div class="q">{html.escape(r.question)}</div>
  <span class="tier" style="background:{color}22;border:1px solid {color}77;color:{color}">{glyph} {label}</span>
  <div class="row">
    <div class="col">
      <div class="kv"><b>statistic</b> &nbsp;{html.escape(r.statistic)}</div>
      <div class="kv"><b>null</b> &nbsp;{html.escape(r.null_desc)}</div>
      <div class="kv"><b>leverage</b> &nbsp;{r.leverage}/5 &nbsp; <b>strength</b> {r.strength:.2f}</div>
      <div class="formula">{html.escape(r.formula)}</div>
      <div class="badge">✓ machinery validated: {html.escape(r.validated_by)}</div>
      <div class="repro">{html.escape(r.reproduce)}</div>
    </div>
    <div class="col">{charts}</div>
  </div>
  <div class="interp">{html.escape(r.interpretation)}</div>
</div>"""


def render_report(results: List[HypothesisResult], meta: Dict[str, str],
                  gate_ok: bool, gate_summary: str) -> str:
    counts = {k: 0 for k in TIERS}
    for r in results:
        counts[r.tier] += 1
    pills = "".join(
        f'<span class="pill" style="border-color:{TIERS[k][1]}77;color:{TIERS[k][1]}">'
        f'{TIERS[k][2]} {TIERS[k][0]}: {counts[k]}</span>'
        for k in TIERS if counts[k])

    tabs_inputs = "".join(
        f'<input type="radio" name="tabs" id="t{i}"{" checked" if i==0 else ""}>'
        for _, i in _GROUPS)
    tabbar = "".join(f'<label for="t{i}">{html.escape(name)}</label>'
                     for name, i in _GROUPS)
    panels = []
    for name, i in _GROUPS:
        cards = "".join(_card_html(r) for r in results if r.group == name)
        if not cards:
            cards = '<div class="q">No hypotheses in this section yet.</div>'
        panels.append(f'<div class="panel" id="p{i}">{cards}</div>')

    banner = (f'<div class="banner ok">MATH GATE GREEN — {html.escape(gate_summary)}</div>'
              if gate_ok else
              f'<div class="banner bad">MATH GATE FAILING — {html.escape(gate_summary)} '
              '— results below are NOT trustworthy until fixed</div>')

    meta_line = " &nbsp;·&nbsp; ".join(
        f"{html.escape(k)}: {html.escape(str(v))}" for k, v in meta.items())

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EYES — evidence ledger</title><style>{_CSS}</style></head>
<body><div class="wrap">
<header class="grim"><div class="sub">the noita eye cipher · evidence ledger</div>
<h1>E Y E S</h1>
<div class="sub">every dart, where it landed, with its receipts</div>
<div class="meta">{meta_line}</div></header>
{banner}
<div class="summary">{pills}</div>
<div class="tabs">{tabs_inputs}<div class="tabbar">{tabbar}</div>
{''.join(panels)}</div>
<footer>Self-contained · inline SVG · no external calls. Every number is rendered
from a ground-truth-tested <code>noita_eye_core</code> module; reproduce any claim
with the command on its card.</footer>
</div></body></html>"""
