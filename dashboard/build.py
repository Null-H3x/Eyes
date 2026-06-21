#!/usr/bin/env python3
"""Build the EYES Workbench HTML dashboard (static shell + embedded state).

    python3 dashboard/build.py [--out workbench.html] [--open]

When served via ``dashboard/server.py``, the page polls the API for live job
output and workflow progress.  Re-run this script to refresh the embedded
snapshot after offline job runs.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from dashboard.cipher_validate import catalog as cipher_catalog  # noqa: E402
from dashboard.dataset_store import get_active, get_active_id, list_datasets  # noqa: E402
from dashboard.eye_puzzle import analyze_dataset  # noqa: E402
from dashboard.orchestrator import get_orchestrator, have_venv  # noqa: E402
from dashboard.registry import load_tools  # noqa: E402
from dashboard.workflow_map import annotate_tools, render_workflow_svg, workflow_map_payload  # noqa: E402
from dashboard.workflows import PRESETS, validate_presets  # noqa: E402

OUT_DEFAULT = ROOT / "workbench.html"

_CSS = """
:root{--bg:#0f0d0a;--bg2:#17130d;--panel:#1c160f;--ink:#e8dcc0;--dim:#a99c80;
--gold:#c9a227;--teal:#4ec9b0;--red:#f85149;--blue:#58a6ff;--amber:#d29922;
--green:#3fb950;--term-bg:#0a0c0f;--term-ink:#c9d1d9;--term-gold:#e3b341;}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(circle at 50% -10%,#241c11,#0f0d0a 70%);
color:var(--ink);font-family:Georgia,'Times New Roman',serif;line-height:1.5}
a{color:var(--gold)}
.wrap{max-width:1200px;margin:0 auto;padding:24px 18px 80px}
header{text-align:center;border-bottom:1px solid #3a3220;padding-bottom:16px;margin-bottom:20px}
header h1{font-size:2rem;letter-spacing:.14em;margin:.2em 0;color:var(--gold);
text-shadow:0 0 16px rgba(201,162,39,.3)}
header .sub{color:var(--dim);font-style:italic}
.meta{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.72rem;color:var(--dim)}
.banner{margin:12px 0;padding:10px 14px;border-radius:6px;font-size:.9rem}
.banner.ok{border:1px solid #3fb95044;background:#3fb95018}
.banner.warn{border:1px solid #d2992244;background:#d2992218}
.banner.err{border:1px solid #f8514944;background:#f8514918}
nav.tabs{display:flex;flex-wrap:wrap;gap:6px;margin:18px 0 14px}
nav.tabs button{font:inherit;cursor:pointer;padding:8px 14px;border-radius:6px;
border:1px solid #3a3220;background:var(--panel);color:var(--dim)}
nav.tabs button.active{border-color:var(--gold);color:var(--gold);background:#2a2215}
.panel{display:none}.panel.active{display:block}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}
.card{background:var(--panel);border:1px solid #3a3220;border-radius:8px;padding:12px 14px}
.card h3{margin:0 0 6px;font-size:.95rem;color:var(--gold)}
.card .grp{font-size:.72rem;color:var(--teal);text-transform:uppercase;letter-spacing:.06em}
.card .cmd{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.68rem;
color:var(--dim);word-break:break-all;margin:8px 0}
.card .tags{margin:6px 0}
.tag{display:inline-block;font-size:.65rem;padding:2px 6px;border-radius:4px;
margin:0 4px 4px 0;background:#2a2215;color:var(--dim)}
.tag.fast{color:var(--green)}.tag.long{color:var(--amber)}
.btn{font:inherit;cursor:pointer;padding:6px 12px;border-radius:5px;border:1px solid #3a3220;
background:#2a2215;color:var(--ink);margin-right:6px}
.btn:hover{border-color:var(--gold);color:var(--gold)}
.btn.primary{border-color:var(--teal);color:var(--teal)}
.btn.danger{border-color:var(--red);color:var(--red)}
.btn:disabled{opacity:.45;cursor:not-allowed}
.wf-steps{margin:10px 0;padding:0;list-style:none}
.wf-steps li{padding:8px 10px;margin:6px 0;border-radius:6px;border:1px solid #3a3220;
display:flex;justify-content:space-between;align-items:center;gap:10px}
.wf-steps li.pending{opacity:.65}
.wf-steps li.running{border-color:var(--teal);background:#4ec9b010}
.wf-steps li.completed{border-color:var(--green);background:#3fb95010}
.wf-steps li.failed{border-color:var(--red);background:#f8514910}
.status{font-size:.75rem;font-family:ui-monospace,Menlo,Consolas,monospace}
.status.running{color:var(--teal)}.status.completed{color:var(--green)}
.status.failed{color:var(--red)}.status.pending{color:var(--dim)}
.layout-split{display:grid;grid-template-columns:320px 1fr;gap:14px;min-height:420px}
@media(max-width:900px){.layout-split{grid-template-columns:1fr}}
.job-list{max-height:520px;overflow:auto}
.job-item{padding:8px 10px;margin:4px 0;border-radius:6px;border:1px solid #3a3220;
cursor:pointer;font-size:.82rem}
.job-item:hover,.job-item.sel{border-color:var(--gold);background:#2a2215}
.job-item .title{color:var(--ink)}.job-item .meta{color:var(--dim);font-size:.7rem}
.terminal{background:var(--term-bg);color:var(--term-ink);font-family:ui-monospace,
Menlo,Consolas,'Courier New',monospace;font-size:.72rem;line-height:1.45;
padding:12px;border-radius:8px;border:1px solid #30363d;white-space:pre-wrap;
word-break:break-word;max-height:520px;overflow:auto;min-height:280px}
.terminal .prompt{color:var(--term-gold)}
.links a{display:block;margin:6px 0}
.filter{margin:8px 0;display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.filter input,.filter select{font:inherit;padding:6px 8px;border-radius:5px;
border:1px solid #3a3220;background:var(--bg2);color:var(--ink)}
.tool-num{display:inline-block;font-family:ui-monospace,Menlo,Consolas,monospace;
font-size:.72rem;font-weight:bold;color:var(--gold);border:1px solid var(--gold);
border-radius:4px;padding:1px 6px;margin-right:6px;vertical-align:middle}
.workflow-wrap{overflow:auto;border:1px solid #3a3220;border-radius:8px;
background:var(--panel);padding:12px;margin:12px 0}
.workflow-svg{width:100%;min-width:900px;height:auto}
.wf-node{cursor:pointer}.wf-node:hover rect{stroke-width:2.5;filter:drop-shadow(0 0 4px rgba(201,162,39,.4))}
.wf-node.sel rect{stroke:var(--gold);stroke-width:2.5}
.phase-list{margin:14px 0}
.phase-list h4{margin:10px 0 6px;color:var(--teal);font-size:.9rem}
.phase-tools{display:flex;flex-wrap:wrap;gap:6px}
.phase-tool{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.72rem;
padding:4px 8px;border-radius:5px;border:1px solid #3a3220;background:#2a2215;
cursor:pointer;color:var(--ink)}
.phase-tool:hover{border-color:var(--gold);color:var(--gold)}
.cipher-form label{display:block;margin:8px 0 4px;font-size:.82rem;color:var(--dim)}
.cipher-form input,.cipher-form select,.cipher-form textarea{width:100%;max-width:520px;
font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.78rem;padding:8px;
border-radius:6px;border:1px solid #3a3220;background:var(--bg2);color:var(--ink)}
.cipher-form textarea{min-height:64px;resize:vertical}
.cipher-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:900px){.cipher-grid{grid-template-columns:1fr}}
.cipher-pos{max-height:240px;overflow:auto;font-size:.68rem}
.cipher-pos table{width:100%;border-collapse:collapse}
.cipher-pos th,.cipher-pos td{border:1px solid #3a3220;padding:3px 6px;text-align:center}
.cipher-pos .ok{color:var(--green)}.cipher-pos .bad{color:var(--red)}
.dataset-active{margin:10px 0;padding:8px 12px;border-radius:6px;border:1px solid #3a3220;
background:#2a2215;font-size:.82rem}
.dataset-active strong{color:var(--gold)}
footer{margin-top:40px;text-align:center;color:var(--dim);font-size:.78rem}
"""


def _collect_snapshot() -> dict:
    sys.path.insert(0, str(ROOT / "noita_eye_core"))
    import corpus as corpus_mod  # noqa: E402,E401,F401

    tools = annotate_tools(load_tools())
    missing = validate_presets([t["id"] for t in tools])
    orch = get_orchestrator()
    active = get_active()
    wf = workflow_map_payload()
    return {
        "have_venv": have_venv(),
        "tools": tools,
        "workflow_map": wf,
        "workflow_svg": render_workflow_svg(wf),
        "cipher_catalog": cipher_catalog(),
        "message_labels": list(active.labels),
        "active_dataset_id": get_active_id(),
        "active_dataset": active.to_dict(include_messages=False),
        "datasets": list_datasets(),
        "dataset_analysis": analyze_dataset(active).to_dict(),
        "presets": [
            {"id": p.id, "title": p.title, "description": p.description,
             "steps": list(p.steps), "tags": list(p.tags)}
            for p in PRESETS
        ],
        "missing_preset_tools": missing,
        "snapshot": orch.snapshot(),
        "workflows": orch.list_workflows(),
        "jobs": orch.list_jobs(30),
        "links": [
            {"title": "Evidence Ledger (report.html)", "href": "report.html"},
            {"title": "State of the Solve", "href": "STATE_OF_THE_SOLVE.md"},
            {"title": "Fingerprint", "href": "FINGERPRINT.md"},
            {"title": "Passage template report", "href": "report/passage_template_report.md"},
            {"title": "Viewer anchor report", "href": "report/viewer_anchor_report.md"},
        ],
    }


def render_html(data: dict) -> str:
    payload = json.dumps(data, separators=(",", ":"))
    venv_banner = (
        '<div class="banner ok">Environment ready (.venv) — Run buttons work when the workbench server is active.</div>'
        if data["have_venv"] else
        '<div class="banner err">No .venv yet — run <code>python3 full-installer.py</code> or Setup from eyes.py before running tools.</div>'
    )
    missing = data.get("missing_preset_tools") or []
    preset_warn = ""
    if missing:
        preset_warn = (
            f'<div class="banner warn">Workflow preset tool IDs missing from registry: '
            f'{html.escape(", ".join(missing))}</div>'
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EYES Workbench</title>
<style>{_CSS}</style>
</head>
<body>
<div class="wrap">
<header>
<h1>E Y E S · WORKBENCH</h1>
<p class="sub">Run tools · saved job output · automated workflows</p>
<p class="meta" id="meta-status">Loading…</p>
</header>
{venv_banner}
{preset_warn}
<div id="server-banner" class="banner warn" style="display:none">
  Static snapshot — start the server for live runs:
  <code>python3 dashboard/server.py</code>
</div>
<div class="dataset-active" id="dataset-banner">Active dataset: loading…</div>
<nav class="tabs" role="tablist">
<button type="button" class="active" data-tab="map">Workflow Map</button>
<button type="button" data-tab="datasets">Datasets</button>
<button type="button" data-tab="tools">Tools</button>
<button type="button" data-tab="ciphers">Known Ciphers</button>
<button type="button" data-tab="workflows">Workflows</button>
<button type="button" data-tab="jobs">Jobs &amp; Output</button>
<button type="button" data-tab="links">Reports &amp; Links</button>
</nav>

<section id="panel-map" class="panel active">
<p class="meta">Global tool numbers match the investigation flow. Click a node to jump to that tool.</p>
<div class="workflow-wrap" id="workflow-svg-wrap"></div>
<div id="phase-list" class="phase-list"></div>
</section>

<section id="panel-datasets" class="panel">
<p class="meta">Import or <strong>plant</strong> eye-puzzle-like ciphertext (N=83). No universal header required — custom sets are first-class. Tool runs use the active dataset via <code>EYES_CORPUS_PATH</code>.</p>
<div class="cipher-grid">
<div class="card cipher-form">
<h3>Active dataset</h3>
<select id="ds-active-select"></select>
<button type="button" class="btn primary" id="ds-set-active">Set active</button>
<button type="button" class="btn" id="ds-analyze">Analyze structure</button>
<h3>Import ciphertext</h3>
<label for="ds-import-name">Name</label>
<input type="text" id="ds-import-name" value="My puzzle corpus">
<label for="ds-import-format">Format</label>
<select id="ds-import-format">
<option value="auto">Auto-detect</option>
<option value="corpus_json">Corpus JSON</option>
<option value="lines">Decimal lines (one message per line)</option>
<option value="glyphs">Glyph lines</option>
</select>
<label for="ds-import-n">Deck size N</label>
<input type="number" id="ds-import-n" value="83" min="2" max="256">
<label for="ds-import-body">Ciphertext data</label>
<textarea id="ds-import-body" rows="8" placeholder="# decimals per line, or full corpus.json, or glyph strings&#10;10 20 30 40&#10;Msg2: 15 25 35"></textarea>
<button type="button" class="btn primary" id="ds-import-btn">Import &amp; activate</button>
<h3>Plant (convert plaintext → ciphertext)</h3>
<label for="ds-plant-mode">Cipher mode</label>
<select id="ds-plant-mode">
<option value="add">add (Vigenère)</option>
<option value="sub">sub</option>
<option value="beaufort">beaufort</option>
<option value="pure_progressive">pure progressive</option>
<option value="per_msg_progressive">per-message progressive</option>
</select>
<label for="ds-plant-plain">Plaintext messages (one per line; optional Label: values)</label>
<textarea id="ds-plant-plain" rows="5" placeholder="A: 10 20 30 40&#10;B: 11 21 31 41"></textarea>
<label for="ds-plant-keys">Per-message keys (one line each, optional)</label>
<textarea id="ds-plant-keys" rows="2" placeholder="7 3&#10;8 4"></textarea>
<label for="ds-plant-bases">Per-message bases (JSON array, optional)</label>
<input type="text" id="ds-plant-bases" placeholder="[0, 3]">
<label for="ds-plant-header">Inject header symbols (JSON [pos,sym,...] optional)</label>
<input type="text" id="ds-plant-header" placeholder="[1, 66, 2, 5] for Noita header">
<button type="button" class="btn primary" id="ds-plant-btn">Plant &amp; activate</button>
<h3>Quick convert (single message, preview only)</h3>
<label for="ds-convert-mode">Mode</label>
<select id="ds-convert-mode">
<option value="add">add</option>
<option value="sub">sub</option>
<option value="beaufort">beaufort</option>
<option value="pure_progressive">pure progressive</option>
<option value="per_msg_progressive">per-message progressive</option>
</select>
<label for="ds-convert-plain">Plaintext</label>
<input type="text" id="ds-convert-plain" placeholder="10 20 30 or glyphs">
<label for="ds-convert-key">Key</label>
<input type="text" id="ds-convert-key" placeholder="7 3 (optional)">
<label for="ds-convert-base">Base</label>
<input type="number" id="ds-convert-base" value="0" min="0" max="82">
<button type="button" class="btn" id="ds-convert-btn">Convert &amp; show output</button>
<pre class="terminal" id="ds-convert-out" style="margin-top:8px;min-height:72px">(single-message cipher output)</pre>
</div>
<div>
<div class="meta" id="ds-findings-header">Structure findings</div>
<pre class="terminal" id="ds-findings">(import or analyze a dataset)</pre>
<pre class="terminal" id="ds-preview" style="margin-top:10px;min-height:120px">(message preview)</pre>
</div>
</div>
</section>

<section id="panel-tools" class="panel">
<div class="filter">
<input type="search" id="tool-search" placeholder="Search tools…" aria-label="Search tools">
<select id="tool-group"><option value="">All groups</option></select>
<select id="tool-duration"><option value="">Any duration</option>
<option value="fast">Fast</option><option value="medium">Medium</option><option value="long">Long (GPU/seed scans)</option></select>
</div>
<div id="tool-grid" class="grid"></div>
</section>

<section id="panel-ciphers" class="panel">
<p class="meta">Validate a known cipher against the <strong>active dataset</strong> (not limited to Noita headers). Plant test data in the Datasets tab, then verify your implementation matches.</p>
<div class="cipher-grid">
<div class="cipher-form card">
<label for="cv-mode">Cipher mode</label>
<select id="cv-mode"></select>
<label for="cv-message">Message</label>
<select id="cv-message"></select>
<label for="cv-offset">Start offset</label>
<input type="number" id="cv-offset" value="0" min="0" max="200">
<label for="cv-base">Base (progressive modes)</label>
<input type="number" id="cv-base" value="0" min="0" max="82">
<label for="cv-plain">Plaintext values (0–82, glyphs, or spaces)</label>
<textarea id="cv-plain" placeholder="e.g. 50 66 5  or  o % 5"></textarea>
<label for="cv-key">Key values (repeating if shorter)</label>
<textarea id="cv-key" placeholder="e.g. 7 3 7 3"></textarea>
<label for="cv-ct">Optional: your ciphertext output (compare mode)</label>
<textarea id="cv-ct" placeholder="Paste external cipher output to compare"></textarea>
<button type="button" class="btn primary" id="cv-run">Validate against corpus</button>
<button type="button" class="btn" id="cv-sweep">Sweep add / sub / beaufort</button>
</div>
<div>
<div class="meta" id="cv-header">Results appear here</div>
<pre class="terminal" id="cv-output">(run a validation)</pre>
<div class="cipher-pos" id="cv-pos"></div>
</div>
</div>
</section>

<section id="panel-workflows" class="panel">
<p class="meta">Automated pipelines run one step at a time. Progress is saved to <code>dashboard/data/state.json</code>.</p>
<div id="workflow-grid" class="grid"></div>
</section>

<section id="panel-jobs" class="panel">
<div style="margin-bottom:10px">
<button type="button" class="btn danger" id="btn-cancel">Cancel active job</button>
<button type="button" class="btn" id="btn-refresh-jobs">Refresh</button>
</div>
<div class="layout-split">
<div class="job-list" id="job-list"></div>
<div>
<div class="meta" id="job-header">Select a job</div>
<pre class="terminal" id="job-output"></pre>
</div>
</div>
</section>

<section id="panel-links" class="panel">
<div class="card links" id="link-list"></div>
<p class="meta">Rebuild evidence ledger: <code>python3 report/build.py --open</code></p>
</section>

<footer>EYES Workbench · re-run <code>python3 dashboard/build.py</code> to refresh embedded snapshot</footer>
</div>

<script>
const DATA = {payload};
const API = "";  // same origin when served by dashboard/server.py

let activeJobId = DATA.snapshot.active_job_id || null;
let pollTimer = null;

function esc(s) {{
  const d = document.createElement("div");
  d.textContent = s == null ? "" : String(s);
  return d.innerHTML;
}}

async function api(path, opts) {{
  const r = await fetch(API + path, opts);
  if (!r.ok) throw new Error(await r.text());
  const ct = r.headers.get("content-type") || "";
  if (ct.includes("application/json")) return r.json();
  return r.text();
}}

function serverLive() {{
  return fetch(API + "/api/health").then(r => r.ok).catch(() => false);
}}

function setMeta(text) {{
  document.getElementById("meta-status").textContent = text;
}}

function initTabs() {{
  document.querySelectorAll("nav.tabs button").forEach(btn => {{
    btn.addEventListener("click", () => {{
      document.querySelectorAll("nav.tabs button").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById("panel-" + btn.dataset.tab).classList.add("active");
    }});
  }});
}}

function renderTools() {{
  const grid = document.getElementById("tool-grid");
  const groups = [...new Set(DATA.tools.map(t => t.group))];
  const sel = document.getElementById("tool-group");
  groups.forEach(g => {{
    const o = document.createElement("option");
    o.value = g; o.textContent = g;
    sel.appendChild(o);
  }});
  function draw() {{
    const q = (document.getElementById("tool-search").value || "").toLowerCase();
    const g = document.getElementById("tool-group").value;
    const d = document.getElementById("tool-duration").value;
    const numFilter = window._toolNumFilter || null;
    grid.innerHTML = "";
    DATA.tools.filter(t => {{
      if (numFilter && t.num !== numFilter) return false;
      if (g && t.group !== g) return false;
      if (d && t.duration !== d) return false;
      if (q && !(t.title + t.id + t.command + t.num_label).toLowerCase().includes(q)) return false;
      return true;
    }}).forEach(t => {{
      const el = document.createElement("div");
      el.className = "card";
      el.id = "tool-card-" + t.num;
      el.innerHTML = `
        <div class="grp">${{esc(t.num_label)}} · ${{esc(t.group)}} · ${{esc(t.phase_title || "")}}</div>
        <h3><span class="tool-num">${{esc(t.num_label)}}</span>${{esc(t.title)}}</h3>
        <div class="cmd">${{esc(t.command)}}</div>
        <div class="tags">
          <span class="tag ${{t.duration}}">${{esc(t.duration)}}</span>
          ${{(t.tags||[]).map(x => `<span class="tag">${{esc(x)}}</span>`).join("")}}
        </div>
        <button type="button" class="btn primary run-tool" data-id="${{esc(t.id)}}">Run</button>`;
      grid.appendChild(el);
    }});
    grid.querySelectorAll(".run-tool").forEach(btn => {{
      btn.addEventListener("click", () => runTool(btn.dataset.id));
    }});
  }}
  window._renderToolsDraw = draw;
  ["input","change"].forEach(ev => {{
    document.getElementById("tool-search").addEventListener(ev, () => {{
      if (ev === "input") window._toolNumFilter = null;
      draw();
    }});
    document.getElementById("tool-group").addEventListener(ev, draw);
    document.getElementById("tool-duration").addEventListener(ev, draw);
  }});
  draw();
}}

function focusToolByNum(num) {{
  window._toolNumFilter = num;
  document.getElementById("tool-search").value = "";
  document.querySelector('[data-tab="tools"]').click();
  if (window._renderToolsDraw) window._renderToolsDraw();
  const card = document.getElementById("tool-card-" + num);
  if (card) card.scrollIntoView({{behavior:"smooth", block:"center"}});
  document.querySelectorAll(".wf-node").forEach(n => {{
    n.classList.toggle("sel", parseInt(n.dataset.num, 10) === num);
  }});
}}

function renderWorkflowMap() {{
  const wrap = document.getElementById("workflow-svg-wrap");
  wrap.innerHTML = DATA.workflow_svg || "";
  wrap.querySelectorAll(".wf-node").forEach(node => {{
    const num = parseInt(node.dataset.num, 10);
    node.addEventListener("click", () => focusToolByNum(num));
    node.addEventListener("keydown", e => {{
      if (e.key === "Enter" || e.key === " ") {{ e.preventDefault(); focusToolByNum(num); }}
    }});
  }});
  const list = document.getElementById("phase-list");
  list.innerHTML = "";
  (DATA.workflow_map.phases || []).forEach(phase => {{
    const block = document.createElement("div");
    block.innerHTML = `<h4 style="color:${{esc(phase.color)}}">${{esc(phase.title)}} — ${{esc(phase.subtitle)}}</h4>`;
    const row = document.createElement("div");
    row.className = "phase-tools";
    (phase.tools || []).forEach(t => {{
      const b = document.createElement("button");
      b.type = "button";
      b.className = "phase-tool";
      b.textContent = t.num_label + " " + t.title.slice(0, 36);
      b.title = t.title;
      b.addEventListener("click", () => focusToolByNum(t.num));
      row.appendChild(b);
    }});
    block.appendChild(row);
    list.appendChild(block);
  }});
}}

function renderDatasetBanner(ds) {{
  const el = document.getElementById("dataset-banner");
  const a = ds || DATA.active_dataset || {{}};
  const an = DATA.dataset_analysis || {{}};
  el.innerHTML = `<strong>Active dataset:</strong> ${{esc(a.name || DATA.active_dataset_id || "?")}}` +
    ` · ${{a.num_messages || "?"}} msgs · N=${{a.deck_size || 83}}` +
    (an.has_noita_header ? ` · <span style="color:var(--green)">Noita header</span>` :
     ` · <span style="color:var(--amber)">no universal 66,5 header</span>`);
}}

function _fillMessageSelect(selId, labels) {{
  const sel = document.getElementById(selId);
  if (!sel) return;
  const cur = sel.value;
  sel.innerHTML = "";
  (labels || []).forEach(l => {{
    const o = document.createElement("option");
    o.value = l; o.textContent = l;
    sel.appendChild(o);
  }});
  if (cur && [...sel.options].some(o => o.value === cur)) sel.value = cur;
}}

function initDatasets() {{
  const sel = document.getElementById("ds-active-select");
  (DATA.datasets || []).forEach(d => {{
    const o = document.createElement("option");
    o.value = d.id;
    o.textContent = d.name + " (" + d.num_messages + " msgs)";
    if (d.id === DATA.active_dataset_id) o.selected = true;
    sel.appendChild(o);
  }});
  renderDatasetBanner(DATA.active_dataset);
  _renderDatasetFindings(DATA.dataset_analysis, DATA.active_dataset);
  document.getElementById("ds-set-active").addEventListener("click", async () => {{
    try {{
      const r = await api("/api/datasets/active", {{
        method: "POST",
        headers: {{"Content-Type": "application/json"}},
        body: JSON.stringify({{id: document.getElementById("ds-active-select").value}}),
      }});
      await refreshDatasets();
    }} catch (e) {{ alert(e.message); }}
  }});
  document.getElementById("ds-analyze").addEventListener("click", async () => {{
    try {{
      const a = await api("/api/datasets/analyze");
      _renderDatasetFindings(a, DATA.active_dataset);
    }} catch (e) {{ alert(e.message); }}
  }});
  document.getElementById("ds-import-btn").addEventListener("click", async () => {{
    try {{
      const r = await api("/api/datasets/import", {{
        method: "POST",
        headers: {{"Content-Type": "application/json"}},
        body: JSON.stringify({{
          name: document.getElementById("ds-import-name").value,
          format: document.getElementById("ds-import-format").value,
          deck_size: parseInt(document.getElementById("ds-import-n").value, 10) || 83,
          content: document.getElementById("ds-import-body").value,
          activate: true,
        }}),
      }});
      await refreshDatasets();
      _renderDatasetFindings(r.analysis, r.dataset);
    }} catch (e) {{ alert(e.message); }}
  }});
  document.getElementById("ds-plant-btn").addEventListener("click", async () => {{
    try {{
      let bases = [];
      const btxt = document.getElementById("ds-plant-bases").value.trim();
      if (btxt) bases = JSON.parse(btxt);
      let hdr = null;
      const htxt = document.getElementById("ds-plant-header").value.trim();
      if (htxt) hdr = JSON.parse(htxt);
      const r = await api("/api/datasets/plant", {{
        method: "POST",
        headers: {{"Content-Type": "application/json"}},
        body: JSON.stringify({{
          name: "Planted " + document.getElementById("ds-plant-mode").value,
          mode: document.getElementById("ds-plant-mode").value,
          plaintexts: document.getElementById("ds-plant-plain").value,
          keys: document.getElementById("ds-plant-keys").value,
          bases: bases,
          inject_header: hdr,
          activate: true,
        }}),
      }});
      await refreshDatasets();
      _renderDatasetFindings(r.analysis, r.dataset);
      if (r.preview_glyphs) {{
        document.getElementById("ds-preview").textContent =
          r.preview_glyphs.map((g, i) => (r.dataset.labels || [])[i] + ": " + g).join("\\n");
      }}
    }} catch (e) {{ alert(e.message); }}
  }});
  document.getElementById("ds-convert-btn").addEventListener("click", async () => {{
    try {{
      const r = await api("/api/datasets/convert", {{
        method: "POST",
        headers: {{"Content-Type": "application/json"}},
        body: JSON.stringify({{
          mode: document.getElementById("ds-convert-mode").value,
          plaintext: document.getElementById("ds-convert-plain").value,
          key: document.getElementById("ds-convert-key").value,
          base: parseInt(document.getElementById("ds-convert-base").value, 10) || 0,
          deck_size: parseInt(document.getElementById("ds-import-n").value, 10) || 83,
        }}),
      }});
      document.getElementById("ds-convert-out").textContent =
        "mode: " + r.mode + "\\n" +
        "length: " + r.length + "\\n" +
        "glyphs: " + r.glyphs + "\\n" +
        "decimal: " + r.decimal;
    }} catch (e) {{ alert(e.message); }}
  }});
}}

function _renderDatasetFindings(analysis, meta) {{
  if (!analysis) return;
  const lines = [
    "deck_size: " + analysis.deck_size,
    "messages: " + analysis.num_messages,
    "total glyphs: " + analysis.total_glyphs,
    "pooled IoC: " + (analysis.pooled_ioc || 0).toFixed(4),
    "symbols used: " + analysis.symbol_usage,
    "has_noita_header: " + analysis.has_noita_header,
    "universal positions: " + (analysis.universal_positions || []).length,
  ];
  (analysis.universal_positions || []).slice(0, 12).forEach(u => {{
    lines.push("  @" + u.position + " = " + u.symbol + " (" + u.glyph + ")");
  }});
  (analysis.eye_puzzle_notes || []).forEach(n => lines.push("note: " + n));
  document.getElementById("ds-findings").textContent = lines.join("\\n");
  document.getElementById("ds-findings-header").textContent =
    "Structure findings — " + (meta && meta.name ? meta.name : "active");
}}

async function refreshDatasets() {{
  try {{
    const pack = await api("/api/datasets");
    DATA.datasets = pack.datasets;
    DATA.active_dataset_id = pack.active_id;
    DATA.active_dataset = pack.active;
    const full = await api("/api/datasets/active");
    DATA.dataset_analysis = full.analysis;
    DATA.message_labels = full.labels || DATA.message_labels;
    const sel = document.getElementById("ds-active-select");
    sel.innerHTML = "";
    DATA.datasets.forEach(d => {{
      const o = document.createElement("option");
      o.value = d.id; o.textContent = d.name + " (" + d.num_messages + " msgs)";
      if (d.id === DATA.active_dataset_id) o.selected = true;
      sel.appendChild(o);
    }});
    renderDatasetBanner(DATA.active_dataset);
    _fillMessageSelect("cv-message", DATA.message_labels);
    if (full.preview_glyphs) {{
      document.getElementById("ds-preview").textContent =
        full.preview_glyphs.map((g, i) => (full.labels || [])[i] + ": " + g).join("\\n");
    }}
    _renderDatasetFindings(full.analysis, full);
  }} catch (_) {{
    renderDatasetBanner(DATA.active_dataset);
  }}
}}

function initCipherForm() {{
  const modeSel = document.getElementById("cv-mode");
  (DATA.cipher_catalog || []).forEach(c => {{
    const o = document.createElement("option");
    o.value = c.id; o.textContent = c.label || c.id;
    modeSel.appendChild(o);
  }});
  const msgSel = document.getElementById("cv-message");
  (DATA.message_labels || []).forEach(l => {{
    const o = document.createElement("option");
    o.value = l; o.textContent = l;
    msgSel.appendChild(o);
  }});
  document.getElementById("cv-run").addEventListener("click", runCipherValidate);
  document.getElementById("cv-sweep").addEventListener("click", runCipherSweep);
}}

function _cvPayload() {{
  return {{
    mode: document.getElementById("cv-mode").value,
    message: document.getElementById("cv-message").value,
    offset: parseInt(document.getElementById("cv-offset").value, 10) || 0,
    base: parseInt(document.getElementById("cv-base").value, 10) || 0,
    plaintext: document.getElementById("cv-plain").value,
    key: document.getElementById("cv-key").value,
    user_ciphertext: document.getElementById("cv-ct").value,
  }};
}}

function _renderCipherResult(r) {{
  document.getElementById("cv-header").textContent =
    r.verdict + " · " + r.message + " @ " + r.offset + " · " +
    (r.matches + "/" + r.length) + " (" + Math.round(r.match_rate * 100) + "%)";
  const lines = [
    "mode: " + r.mode,
    "verdict: " + r.verdict,
    "match: " + r.matches + "/" + r.length,
    "corpus:  " + (r.corpus_glyphs || r.corpus_slice.join(" ")),
    "computed:" + (r.computed_glyphs || r.computed.join(" ")),
  ];
  if (r.round_trip_ok != null) lines.push("round_trip: " + r.round_trip_ok);
  if (r.decrypt_ioc != null) lines.push("decrypt_ioc: " + r.decrypt_ioc.toFixed(4));
  (r.notes || []).forEach(n => lines.push("note: " + n));
  document.getElementById("cv-output").textContent = lines.join("\\n");
  const pos = document.getElementById("cv-pos");
  if (!r.positions || !r.positions.length) {{ pos.innerHTML = ""; return; }}
  const rows = r.positions.map(p =>
    `<tr class="${{p.match ? "ok" : "bad"}}"><td>${{p.i}}</td><td>${{p.abs}}</td>` +
    `<td>${{p.plain != null ? p.plain : ""}}</td><td>${{p.expected}}</td>` +
    `<td>${{p.observed}}</td><td>${{p.exp_glyph}}</td><td>${{p.obs_glyph}}</td>` +
    `<td>${{p.match ? "✓" : "✗"}}</td></tr>`).join("");
  pos.innerHTML = `<table><thead><tr><th>i</th><th>pos</th><th>plain</th>` +
    `<th>exp</th><th>obs</th><th>exp_g</th><th>obs_g</th><th>ok</th></tr></thead><tbody>${{rows}}</tbody></table>`;
}}

async function runCipherValidate() {{
  try {{
    const r = await api("/api/cipher/validate", {{
      method: "POST",
      headers: {{"Content-Type": "application/json"}},
      body: JSON.stringify(_cvPayload()),
    }});
    _renderCipherResult(r);
  }} catch (e) {{
    document.getElementById("cv-output").textContent = "Error: " + e.message;
  }}
}}

async function runCipherSweep() {{
  try {{
    const p = _cvPayload();
    p.mode = "add";
    const rows = await api("/api/cipher/sweep", {{
      method: "POST",
      headers: {{"Content-Type": "application/json"}},
      body: JSON.stringify(p),
    }});
    document.getElementById("cv-header").textContent = "Linear mode sweep (best first)";
    document.getElementById("cv-output").textContent = rows.map(r =>
      r.mode + ": " + r.verdict + " " + r.matches + "/" + r.length +
      " (" + Math.round(r.match_rate * 100) + "%)").join("\\n");
    if (rows.length) _renderCipherResult(rows[0]);
  }} catch (e) {{
    document.getElementById("cv-output").textContent = "Error: " + e.message;
  }}
}}

function renderWorkflows(wflows) {{
  const grid = document.getElementById("workflow-grid");
  grid.innerHTML = "";
  (wflows || DATA.workflows).forEach(wf => {{
    const done = wf.steps.filter(s => s.status === "completed").length;
    const total = wf.steps.length;
    const steps = wf.steps.map((s, i) => {{
      const tool = DATA.tools.find(t => t.id === s.tool_id);
      const title = tool ? tool.title : s.tool_id;
      return `<li class="${{esc(s.status)}}"><span>${{i+1}}. ${{esc(title)}}</span>
        <span class="status ${{esc(s.status)}}">${{esc(s.status)}}</span></li>`;
    }}).join("");
    const el = document.createElement("div");
    el.className = "card";
    el.innerHTML = `
      <h3>${{esc(wf.title)}}</h3>
      <p class="meta">${{esc(wf.description || "")}}</p>
      <p class="meta">Progress: ${{done}} / ${{total}} · status: <span class="status ${{esc(wf.status)}}">${{esc(wf.status)}}</span></p>
      <ul class="wf-steps">${{steps}}</ul>
      <button type="button" class="btn primary wf-next" data-id="${{esc(wf.id)}}">Run next step</button>
      <button type="button" class="btn wf-auto" data-id="${{esc(wf.id)}}">Run all</button>
      <button type="button" class="btn wf-reset" data-id="${{esc(wf.id)}}">Reset</button>`;
    grid.appendChild(el);
  }});
  grid.querySelectorAll(".wf-next").forEach(b => b.addEventListener("click", () => wfStep(b.dataset.id)));
  grid.querySelectorAll(".wf-auto").forEach(b => b.addEventListener("click", () => wfAuto(b.dataset.id)));
  grid.querySelectorAll(".wf-reset").forEach(b => b.addEventListener("click", () => wfReset(b.dataset.id)));
}}

function renderJobs(jobs) {{
  const list = document.getElementById("job-list");
  list.innerHTML = "";
  (jobs || DATA.jobs).forEach(j => {{
    const el = document.createElement("div");
    el.className = "job-item" + (j.id === activeJobId ? " sel" : "");
    el.dataset.id = j.id;
    el.innerHTML = `<div class="title">${{esc(j.title)}}</div>
      <div class="meta">${{esc(j.id)}} · <span class="status ${{esc(j.status)}}">${{esc(j.status)}}</span>
      ${{j.exit_code != null ? "· exit " + j.exit_code : ""}}</div>`;
    el.addEventListener("click", () => selectJob(j.id));
    list.appendChild(el);
  }});
}}

function renderLinks() {{
  const box = document.getElementById("link-list");
  box.innerHTML = (DATA.links || []).map(l =>
    `<a href="${{esc(l.href)}}">${{esc(l.title)}}</a>`).join("");
}}

async function runTool(id) {{
  try {{
    const j = await api("/api/run", {{
      method: "POST",
      headers: {{"Content-Type": "application/json"}},
      body: JSON.stringify({{tool_id: id}}),
    }});
    activeJobId = j.id;
    document.querySelector('[data-tab="jobs"]').click();
    await refreshAll();
  }} catch (e) {{
    alert("Run failed: " + e.message + "\\n\\nStart server: python3 dashboard/server.py");
  }}
}}

async function wfStep(id) {{
  try {{
    await api("/api/workflows/" + encodeURIComponent(id) + "/step", {{method: "POST"}});
    await refreshAll();
  }} catch (e) {{ alert(e.message); }}
}}

async function wfAuto(id) {{
  try {{
    await api("/api/workflows/" + encodeURIComponent(id) + "/auto", {{method: "POST"}});
    await refreshAll();
  }} catch (e) {{ alert(e.message); }}
}}

async function wfReset(id) {{
  if (!confirm("Reset saved progress for this workflow?")) return;
  try {{
    await api("/api/workflows/" + encodeURIComponent(id) + "/reset", {{method: "POST"}});
    await refreshAll();
  }} catch (e) {{ alert(e.message); }}
}}

async function selectJob(id) {{
  activeJobId = id;
  document.querySelectorAll(".job-item").forEach(el => {{
    el.classList.toggle("sel", el.dataset.id === id);
  }});
  const j = DATA.jobs.find(x => x.id === id) || {{}};
  document.getElementById("job-header").textContent =
    (j.title || id) + " · " + (j.status || "") + (j.command ? " · " + j.command : "");
  try {{
    const out = await api("/api/jobs/" + encodeURIComponent(id) + "/stdout");
    document.getElementById("job-output").textContent = out || "(no output yet)";
  }} catch (_) {{
    document.getElementById("job-output").textContent = "(start server to stream output)";
  }}
}}

async function refreshAll() {{
  try {{
    const snap = await api("/api/snapshot");
    DATA.snapshot = snap;
    DATA.jobs = snap.recent_jobs;
    activeJobId = snap.active_job_id || activeJobId;
    const wfs = await api("/api/workflows");
    DATA.workflows = wfs;
    await refreshDatasets();
    renderJobs(DATA.jobs);
    renderWorkflows(DATA.workflows);
    if (activeJobId) await selectJob(activeJobId);
    setMeta("Live · updated " + (snap.updated_at || ""));
    document.getElementById("server-banner").style.display = "none";
  }} catch (_) {{
    renderJobs(DATA.jobs);
    renderWorkflows(DATA.workflows);
    renderDatasetBanner(DATA.active_dataset);
    if (activeJobId) {{
      const j = DATA.jobs.find(x => x.id === activeJobId);
      if (j) {{
        document.getElementById("job-header").textContent = j.title + " · " + j.status;
      }}
    }}
    document.getElementById("server-banner").style.display = "block";
    setMeta("Static snapshot · " + (DATA.snapshot.updated_at || "embedded"));
  }}
}}

function startPolling() {{
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = setInterval(refreshAll, 2000);
}}

document.getElementById("btn-cancel").addEventListener("click", async () => {{
  try {{ await api("/api/cancel", {{method: "POST"}}); await refreshAll(); }}
  catch (e) {{ alert(e.message); }}
}});
document.getElementById("btn-refresh-jobs").addEventListener("click", refreshAll);

initTabs();
renderWorkflowMap();
initDatasets();
renderTools();
initCipherForm();
renderWorkflows(DATA.workflows);
renderJobs(DATA.jobs);
renderLinks();
renderDatasetBanner(DATA.active_dataset);
serverLive().then(live => {{
  if (live) {{ refreshAll(); startPolling(); }}
  else {{
    setMeta("Static snapshot · start python3 dashboard/server.py for live runs");
    document.getElementById("server-banner").style.display = "block";
    if (DATA.jobs.length) selectJob(DATA.jobs[0].id);
  }}
}});
</script>
</body>
</html>
"""


def build_workbench(out: Path | str | None = None) -> Path:
    """Build workbench HTML; safe to call from server (no argparse)."""
    missing = validate_presets([t.id for t in load_tools()])
    if missing:
        print("WARNING: workflow presets reference missing tool IDs:")
        for m in missing:
            print(f"  - {m}")
    data = _collect_snapshot()
    out_path = Path(out) if out else OUT_DEFAULT
    out_path.write_text(render_html(data), encoding="utf-8")
    print(f"Wrote {out_path} ({len(data['tools'])} tools, {len(data['presets'])} workflows)")
    return out_path


def main() -> int:
    ap = argparse.ArgumentParser(description="Build EYES Workbench HTML dashboard")
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    ap.add_argument("--open", action="store_true")
    args = ap.parse_args()

    build_workbench(args.out)
    print("  Live mode: python3 dashboard/server.py")
    if args.open:
        webbrowser.open(Path(args.out).resolve().as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
