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

from dashboard.orchestrator import get_orchestrator, have_venv  # noqa: E402
from dashboard.registry import load_tools  # noqa: E402
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
footer{margin-top:40px;text-align:center;color:var(--dim);font-size:.78rem}
"""


def _collect_snapshot() -> dict:
    tools = load_tools()
    missing = validate_presets([t.id for t in tools])
    orch = get_orchestrator()
    return {
        "have_venv": have_venv(),
        "tools": [t.__dict__ for t in tools],
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
<nav class="tabs" role="tablist">
<button type="button" class="active" data-tab="tools">Tools</button>
<button type="button" data-tab="workflows">Workflows</button>
<button type="button" data-tab="jobs">Jobs &amp; Output</button>
<button type="button" data-tab="links">Reports &amp; Links</button>
</nav>

<section id="panel-tools" class="panel active">
<div class="filter">
<input type="search" id="tool-search" placeholder="Search tools…" aria-label="Search tools">
<select id="tool-group"><option value="">All groups</option></select>
<select id="tool-duration"><option value="">Any duration</option>
<option value="fast">Fast</option><option value="medium">Medium</option><option value="long">Long (GPU/seed scans)</option></select>
</div>
<div id="tool-grid" class="grid"></div>
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
    grid.innerHTML = "";
    DATA.tools.filter(t => {{
      if (g && t.group !== g) return false;
      if (d && t.duration !== d) return false;
      if (q && !(t.title + t.id + t.command).toLowerCase().includes(q)) return false;
      return true;
    }}).forEach(t => {{
      const el = document.createElement("div");
      el.className = "card";
      el.innerHTML = `
        <div class="grp">${{esc(t.group)}}</div>
        <h3>${{esc(t.title)}}</h3>
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
  ["input","change"].forEach(ev => {{
    document.getElementById("tool-search").addEventListener(ev, draw);
    document.getElementById("tool-group").addEventListener(ev, draw);
    document.getElementById("tool-duration").addEventListener(ev, draw);
  }});
  draw();
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
    renderJobs(DATA.jobs);
    renderWorkflows(DATA.workflows);
    if (activeJobId) await selectJob(activeJobId);
    setMeta("Live · updated " + (snap.updated_at || ""));
    document.getElementById("server-banner").style.display = "none";
  }} catch (_) {{
    renderJobs(DATA.jobs);
    renderWorkflows(DATA.workflows);
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
renderTools();
renderWorkflows(DATA.workflows);
renderJobs(DATA.jobs);
renderLinks();
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


def main() -> int:
    ap = argparse.ArgumentParser(description="Build EYES Workbench HTML dashboard")
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    ap.add_argument("--open", action="store_true")
    args = ap.parse_args()

    missing = validate_presets([t.id for t in load_tools()])
    if missing:
        print("WARNING: workflow presets reference missing tool IDs:")
        for m in missing:
            print(f"  - {m}")

    data = _collect_snapshot()
    out_path = Path(args.out)
    out_path.write_text(render_html(data), encoding="utf-8")
    print(f"Wrote {out_path} ({len(data['tools'])} tools, {len(data['presets'])} workflows)")
    print("  Live mode: python3 dashboard/server.py")
    if args.open:
        webbrowser.open(out_path.resolve().as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
