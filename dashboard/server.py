#!/usr/bin/env python3
"""EYES Workbench — local HTTP server for live tool runs and job polling.

    python3 dashboard/server.py [--port 8765] [--open]

Serves workbench.html, report.html, and JSON API endpoints.  One job runs at a
time; stdout is streamed to ``dashboard/jobs/{id}/stdout.log``.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dashboard.build import main as build_dashboard  # noqa: E402
from dashboard.orchestrator import get_orchestrator  # noqa: E402
from dashboard.registry import load_tools  # noqa: E402
from dashboard.workflows import PRESETS  # noqa: E402

# Ensure dashboard exists on first launch
if not (ROOT / "workbench.html").is_file():
    build_dashboard()


def _json_response(handler: BaseHTTPRequestHandler, code: int, obj) -> None:
    body = json.dumps(obj, indent=2).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body)


def _text_response(handler: BaseHTTPRequestHandler, code: int, text: str,
                   content_type: str = "text/plain; charset=utf-8") -> None:
    body = text.encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class WorkbenchHandler(BaseHTTPRequestHandler):
    server_version = "EYESWorkbench/1.0"

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path)
        route = path.path.rstrip("/") or "/"

        if route == "/api/health":
            return _json_response(self, 200, {"ok": True})

        orch = get_orchestrator()

        if route == "/api/snapshot":
            return _json_response(self, 200, orch.snapshot())

        if route == "/api/tools":
            tools = [t.__dict__ for t in load_tools()]
            return _json_response(self, 200, {"tools": tools})

        if route == "/api/workflows":
            return _json_response(self, 200, orch.list_workflows())

        if route == "/api/jobs":
            qs = parse_qs(path.query)
            limit = int(qs.get("limit", ["40"])[0])
            return _json_response(self, 200, {"jobs": orch.list_jobs(limit)})

        if route.startswith("/api/jobs/"):
            parts = route.split("/")
            if len(parts) == 4 and parts[3] not in ("stdout", "stderr"):
                job = orch.get_job(parts[3])
                if not job:
                    return _json_response(self, 404, {"error": "job not found"})
                return _json_response(self, 200, job)
            if len(parts) == 5 and parts[3]:
                jid = parts[3]
                qs = parse_qs(path.query)
                tail = int(qs.get("tail", ["0"])[0])
                if parts[4] == "stdout":
                    return _text_response(self, 200, orch.get_stdout(jid, tail=tail))
                if parts[4] == "stderr":
                    return _text_response(self, 200, orch.get_stderr(jid, tail=tail))

        if route.startswith("/api/workflows/") and route.count("/") == 3:
            wf_id = unquote(route.split("/")[-1])
            try:
                return _json_response(self, 200, orch.get_workflow(wf_id))
            except KeyError:
                return _json_response(self, 404, {"error": "workflow not found"})

        # Static files from repo root
        rel = route.lstrip("/")
        if rel in ("", "workbench.html"):
            rel = "workbench.html"
        candidate = (ROOT / rel).resolve()
        if not str(candidate).startswith(str(ROOT.resolve())):
            return _text_response(self, 403, "forbidden")
        if candidate.is_file():
            ctype = mimetypes.guess_type(str(candidate))[0] or "application/octet-stream"
            data = candidate.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        return _text_response(self, 404, "not found")

    def do_POST(self):
        path = urlparse(self.path).path.rstrip("/")
        orch = get_orchestrator()
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            body = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            return _json_response(self, 400, {"error": "invalid JSON"})

        if path == "/api/run":
            tool_id = body.get("tool_id")
            if not tool_id:
                return _json_response(self, 400, {"error": "tool_id required"})
            try:
                rec = orch.start_tool(tool_id)
                return _json_response(self, 200, rec.to_dict())
            except RuntimeError as e:
                return _json_response(self, 409, {"error": str(e)})
            except KeyError as e:
                return _json_response(self, 404, {"error": str(e)})

        if path == "/api/cancel":
            rec = orch.cancel_active()
            return _json_response(self, 200, {"cancelled": rec.to_dict() if rec else None})

        if path.startswith("/api/workflows/"):
            parts = [p for p in path.split("/") if p]
            # api, workflows, {id}, {action}
            if len(parts) >= 3:
                wf_id = unquote(parts[2])
                action = parts[3] if len(parts) > 3 else ""
                if action == "step":
                    try:
                        st = orch.run_workflow_step(wf_id)
                        return _json_response(self, 200, st)
                    except (KeyError, RuntimeError) as e:
                        return _json_response(self, 409, {"error": str(e)})
                if action == "auto":
                    try:
                        orch.run_workflow_auto(wf_id)
                        st = orch.get_workflow(wf_id)
                        return _json_response(self, 200, st)
                    except KeyError as e:
                        return _json_response(self, 404, {"error": str(e)})
                if action == "reset":
                    try:
                        st = orch.reset_workflow(wf_id)
                        return _json_response(self, 200, st)
                    except KeyError as e:
                        return _json_response(self, 404, {"error": str(e)})

        if path == "/api/rebuild":
            build_dashboard()
            return _json_response(self, 200, {"ok": True})

        return _json_response(self, 404, {"error": "not found"})


def main() -> int:
    ap = argparse.ArgumentParser(description="EYES Workbench HTTP server")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--open", action="store_true", help="open workbench in browser")
    args = ap.parse_args()

    if not (ROOT / "workbench.html").is_file():
        print("Building workbench.html …")
        build_dashboard()

    url = f"http://{args.host}:{args.port}/workbench.html"
    httpd = ThreadingHTTPServer((args.host, args.port), WorkbenchHandler)
    print(f"EYES Workbench serving at {url}")
    print(f"  Tools: {len(load_tools())}  Workflows: {len(PRESETS)}")
    print("  Ctrl+C to stop")
    if args.open:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
