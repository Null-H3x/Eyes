"""Generate HTML results reports for completed workflow runs."""
from __future__ import annotations

import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from dashboard import DATA_DIR, JOBS_DIR, ROOT
from dashboard.registry import tool_by_id
from dashboard.workflows import preset_by_id

REPORTS_DIR = DATA_DIR / "reports"

_CSS = """
:root{--bg:#0d0d12;--panel:#13131a;--ink:#c8d6e0;--dim:#4a5060;--cyan:#0ff0fc;
--green:#39ff14;--red:#ff4444;--orange:#ff8c00;--border:#1e1e2e;
--mono:"Share Tech Mono",monospace;--head:"Rajdhani",sans-serif}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--mono);
font-size:13px;line-height:1.55;padding:24px}
.wrap{max-width:960px;margin:0 auto}
h1{font-family:var(--head);letter-spacing:.15em;color:#fff;margin:0 0 8px}
.meta{color:var(--dim);font-size:.85rem;margin-bottom:20px}
.summary{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0}
.pill{padding:6px 12px;border-radius:4px;border:1px solid var(--border);font-size:.8rem}
.pill.ok{border-color:var(--green);color:var(--green)}
.pill.fail{border-color:var(--red);color:var(--red)}
.pill.warn{border-color:var(--orange);color:var(--orange)}
.step{margin:14px 0;padding:14px 16px;border:1px solid var(--border);
border-radius:8px;background:var(--panel)}
.step.completed{border-left:3px solid var(--green)}
.step.failed{border-left:3px solid var(--red)}
.step.pending{border-left:3px solid var(--dim);opacity:.7}
.step h3{margin:0 0 6px;font-family:var(--head);font-size:1rem;color:#fff}
.step .status{font-size:.75rem;text-transform:uppercase;letter-spacing:.08em}
.step .status.completed{color:var(--green)}
.step .status.failed{color:var(--red)}
.step .status.pending{color:var(--dim)}
pre.log{background:#080810;color:var(--green);padding:12px;border-radius:6px;
overflow:auto;max-height:320px;font-size:.72rem;white-space:pre-wrap;word-break:break-word}
a{color:var(--cyan)}
footer{margin-top:32px;color:var(--dim);font-size:.75rem;text-align:center}
"""


def _esc(s: Any) -> str:
    return html.escape("" if s is None else str(s))


def _read_job_stdout(job_id: Optional[str], tail: int = 80) -> str:
    if not job_id:
        return ""
    try:
        from dashboard.orchestrator import get_orchestrator
        return get_orchestrator().get_stdout(job_id, tail=tail)
    except Exception:
        p = JOBS_DIR / job_id / "stdout.log"
        if not p.is_file():
            return ""
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[-tail:])


def _tool_title(tool_id: str) -> str:
    tools = tool_by_id()
    if tool_id in tools:
        return tools[tool_id].title
    return tool_id


def build_report_payload(
    workflow_id: str,
    wstate: dict,
    *,
    dataset: Optional[dict] = None,
) -> dict:
    """Structured report data for JSON export or HTML rendering."""
    preset = preset_by_id().get(workflow_id)
    steps_out: List[dict] = []
    completed = failed = pending = 0
    for i, step in enumerate(wstate.get("steps", [])):
        st = step.get("status", "pending")
        if st == "completed":
            completed += 1
        elif st == "failed":
            failed += 1
        else:
            pending += 1
        jid = step.get("job_id")
        steps_out.append({
            "index": i,
            "tool_id": step.get("tool_id"),
            "title": _tool_title(step.get("tool_id", "")),
            "status": st,
            "exit_code": step.get("exit_code"),
            "job_id": jid,
            "stdout_tail": _read_job_stdout(jid, tail=60),
        })

    total = len(steps_out)
    return {
        "workflow_id": workflow_id,
        "title": wstate.get("title") or (preset.title if preset else workflow_id),
        "description": wstate.get("description") or (preset.description if preset else ""),
        "status": wstate.get("status", "idle"),
        "started_at": wstate.get("started_at"),
        "updated_at": wstate.get("updated_at"),
        "dataset_id": wstate.get("dataset_id") or (dataset or {}).get("id"),
        "dataset_name": (dataset or {}).get("name"),
        "summary": {
            "total": total,
            "completed": completed,
            "failed": failed,
            "pending": pending,
        },
        "steps": steps_out,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ"),
    }


def render_report_html(payload: dict) -> str:
    s = payload["summary"]
    status = payload["status"]
    pill_class = "ok" if status == "completed" and s["failed"] == 0 else (
        "warn" if status == "completed_with_failures" else "fail" if s["failed"] else "ok")

    steps_html = []
    for step in payload["steps"]:
        cls = step["status"]
        log = _esc(step.get("stdout_tail") or "(no output captured)")
        job_link = ""
        if step.get("job_id"):
            job_link = (
                f'<p class="meta">Job: <code>{_esc(step["job_id"])}</code></p>')
        steps_html.append(f"""
<div class="step {cls}">
  <h3>{step["index"] + 1}. {_esc(step["title"])}</h3>
  <div class="status {cls}">{_esc(cls)}</div>
  <p class="meta">tool: <code>{_esc(step["tool_id"])}</code>
    · exit: {_esc(step.get("exit_code"))}</p>
  {job_link}
  <pre class="log">{log}</pre>
</div>""")

    ds_line = ""
    if payload.get("dataset_name"):
        ds_line = (
            f'<br>Dataset: <strong>{_esc(payload["dataset_name"])}</strong> '
            f'(<code>{_esc(payload.get("dataset_id"))}</code>)')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EYES Workflow Report — {_esc(payload["title"])}</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@500;700&display=swap" rel="stylesheet">
<style>{_CSS}</style>
</head>
<body>
<div class="wrap">
<h1>Workflow Report</h1>
<p class="meta">{_esc(payload["title"])} · {_esc(payload["workflow_id"])}<br>
Status: <strong>{_esc(status)}</strong> · Generated {_esc(payload["generated_at"])}{ds_line}</p>
<p class="meta">{_esc(payload.get("description", ""))}</p>
<div class="summary">
  <span class="pill {pill_class}">{s["completed"]}/{s["total"]} completed</span>
  <span class="pill {"fail" if s["failed"] else "ok"}">{s["failed"]} failed</span>
  <span class="pill">{s["pending"]} pending</span>
</div>
{"".join(steps_html)}
<footer>EYES Workbench · <a href="workbench.html">Return to workbench</a></footer>
</div>
</body>
</html>"""


def write_workflow_report(
    workflow_id: str,
    wstate: dict,
    *,
    dataset: Optional[dict] = None,
) -> Path:
    """Write HTML + JSON report files; return HTML path."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_report_payload(workflow_id, wstate, dataset=dataset)
    html_path = REPORTS_DIR / f"{workflow_id}.html"
    json_path = REPORTS_DIR / f"{workflow_id}.json"
    html_path.write_text(render_report_html(payload), encoding="utf-8")
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return html_path


def report_url(workflow_id: str) -> str:
    return f"/dashboard/data/reports/{workflow_id}.html"


def selftest() -> List[Tuple[str, bool]]:
    out: List[Tuple[str, bool]] = []
    payload = build_report_payload("quick-validate", {
        "title": "Quick Validate",
        "description": "test",
        "status": "completed",
        "steps": [
            {"tool_id": "validate-run-the-full-math-gate-validate-everything",
             "status": "completed", "exit_code": 0, "job_id": None},
            {"tool_id": "validate-passage-template-paranoia-audit-real-corpus-inva",
             "status": "failed", "exit_code": 1, "job_id": None},
        ],
    })
    out.append(("build_report_payload summary", payload["summary"]["total"] == 2))
    html_doc = render_report_html(payload)
    out.append(("render_report_html non-empty", len(html_doc) > 500))
    out.append(("render includes failed step", "failed" in html_doc))
    path = write_workflow_report("selftest-wf", {
        "title": "Selftest",
        "status": "completed",
        "steps": payload["steps"],
    })
    out.append(("write_workflow_report creates file", path.is_file()))
    return out


if __name__ == "__main__":
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n = sum(1 for _, ok in results if ok)
    print(f"\n{n}/{len(results)} workflow_report checks passed")
    sys.exit(0 if n == len(results) else 1)
