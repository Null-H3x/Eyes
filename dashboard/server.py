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

from dashboard.build import build_workbench  # noqa: E402
from dashboard.cipher_validate import (  # noqa: E402
    GLYPHS,
    catalog as cipher_catalog,
    parse_values,
    sweep_linear_modes,
    validate_cipher,
)
from dashboard.dataset_store import (  # noqa: E402
    get_active,
    get_active_id,
    import_and_save,
    list_datasets,
    preview_import,
    save_planted,
    set_active,
    _resolve_deck_size,
)
from dashboard.deck_infer import infer_active_dataset, infer_from_text  # noqa: E402
from dashboard.eye_puzzle import (  # noqa: E402
    analyze_dataset,
    convert_plaintext_to_ciphertext,
    parse_plaintext_messages,
    plant_dataset,
)
from dashboard.orchestrator import get_orchestrator  # noqa: E402
from dashboard.registry import load_tools  # noqa: E402
from dashboard.workflow_map import workflow_map_payload  # noqa: E402
from dashboard.workflow_report import (  # noqa: E402
    build_report_payload,
    render_report_html,
    write_workflow_report,
)
from dashboard.workflows import PRESETS  # noqa: E402
from dashboard import tier1_api  # noqa: E402
from dashboard import tier2_api  # noqa: E402


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

        if route == "/api/workflow-map":
            return _json_response(self, 200, workflow_map_payload())

        if route == "/api/cipher/catalog":
            return _json_response(self, 200, {"modes": cipher_catalog()})

        if route == "/api/datasets":
            active = get_active()
            return _json_response(self, 200, {
                "datasets": list_datasets(),
                "active_id": get_active_id(),
                "active": active.to_dict(include_messages=False),
            })

        if route == "/api/datasets/active":
            ds = get_active()
            out = ds.to_dict(include_messages=False)
            out["preview_glyphs"] = [
                "".join(GLYPHS[v] if 0 <= v < len(GLYPHS) else "?"
                        for v in ct[:80]) + ("…" if len(ct) > 80 else "")
                for ct in ds.ciphertexts
            ]
            out["analysis"] = analyze_dataset(ds).to_dict()
            return _json_response(self, 200, out)

        if route == "/api/datasets/analyze":
            return _json_response(self, 200, analyze_dataset(get_active()).to_dict())

        if route == "/api/datasets/infer-deck":
            try:
                return _json_response(self, 200, infer_active_dataset())
            except ValueError as e:
                return _json_response(self, 400, {"error": str(e)})

        if route == "/api/workflows":
            return _json_response(self, 200, orch.list_workflows())

        if route == "/api/tier1/alphabet":
            return _json_response(self, 200, {
                "alphabet": tier1_api.default_alphabet(),
                "length": len(tier1_api.default_alphabet()),
            })

        if route == "/api/jobs":
            qs = parse_qs(path.query)
            try:
                limit = int(qs.get("limit", ["40"])[0])
            except ValueError:
                return _json_response(self, 400, {"error": "invalid limit"})
            return _json_response(self, 200, {"jobs": orch.list_jobs(limit)})

        if route.startswith("/api/jobs/"):
            parts = route.split("/")
            if len(parts) == 4 and parts[3] not in ("stdout", "stderr"):
                try:
                    job = orch.get_job(parts[3])
                except ValueError:
                    return _json_response(self, 400, {"error": "invalid job id"})
                if not job:
                    return _json_response(self, 404, {"error": "job not found"})
                return _json_response(self, 200, job)
            if len(parts) == 5 and parts[3]:
                jid = parts[3]
                qs = parse_qs(path.query)
                try:
                    tail = int(qs.get("tail", ["0"])[0])
                except ValueError:
                    return _json_response(self, 400, {"error": "invalid tail"})
                try:
                    if parts[4] == "stdout":
                        return _text_response(self, 200, orch.get_stdout(jid, tail=tail))
                    if parts[4] == "stderr":
                        return _text_response(self, 200, orch.get_stderr(jid, tail=tail))
                except ValueError:
                    return _json_response(self, 400, {"error": "invalid job id"})

        if route.startswith("/api/workflows/") and route.count("/") == 3:
            wf_id = unquote(route.split("/")[-1])
            try:
                return _json_response(self, 200, orch.get_workflow(wf_id))
            except KeyError:
                return _json_response(self, 404, {"error": "workflow not found"})

        if route.startswith("/api/workflows/") and route.endswith("/report"):
            parts = [p for p in route.split("/") if p]
            if len(parts) >= 3:
                wf_id = unquote(parts[2])
                try:
                    wstate = orch.get_workflow(wf_id)
                except KeyError:
                    return _json_response(self, 404, {"error": "workflow not found"})
                from dashboard.dataset_store import get_active
                ds = get_active().to_dict(include_messages=False)
                payload = build_report_payload(wf_id, wstate, dataset=ds)
                return _json_response(self, 200, payload)

        if route.startswith("/dashboard/data/reports/") and route.endswith(".html"):
            rel = route.lstrip("/")
            candidate = (ROOT / rel).resolve()
            if candidate.is_file() and str(candidate).startswith(str(ROOT.resolve())):
                data = candidate.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

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
                rec = orch.start_tool(tool_id, dataset_id=body.get("dataset_id"))
                return _json_response(self, 200, rec.to_dict())
            except RuntimeError as e:
                return _json_response(self, 409, {"error": str(e)})
            except KeyError as e:
                return _json_response(self, 404, {"error": str(e)})

        if path == "/api/cancel":
            rec = orch.cancel_active()
            return _json_response(self, 200, {"cancelled": rec.to_dict() if rec else None})

        if path == "/api/cipher/validate":
            return self._cipher_validate(body)

        if path == "/api/cipher/sweep":
            return self._cipher_sweep(body)

        if path == "/api/datasets/active":
            try:
                ds = set_active(body.get("id", ""))
                return _json_response(self, 200, ds.to_dict(include_messages=False))
            except (KeyError, ValueError) as e:
                return _json_response(self, 404, {"error": str(e)})

        if path == "/api/datasets/import":
            return self._dataset_import(body)

        if path == "/api/datasets/preview":
            return self._dataset_preview(body)

        if path == "/api/datasets/infer-deck":
            return self._dataset_infer_deck(body)

        if path == "/api/datasets/plant":
            return self._dataset_plant(body)

        if path == "/api/datasets/convert":
            return self._dataset_convert(body)

        if path.startswith("/api/workflows/"):
            parts = [p for p in path.split("/") if p]
            # api, workflows, {id}, {action}
            if len(parts) >= 3:
                wf_id = unquote(parts[2])
                action = parts[3] if len(parts) > 3 else ""
                if action == "step":
                    try:
                        st = orch.run_workflow_step(
                            wf_id,
                            dataset_id=body.get("dataset_id"),
                            continue_on_fail=body.get("continue_on_fail"),
                        )
                        return _json_response(self, 200, st)
                    except (KeyError, RuntimeError) as e:
                        return _json_response(self, 409, {"error": str(e)})
                if action == "auto":
                    try:
                        orch.run_workflow_auto(
                            wf_id,
                            dataset_id=body.get("dataset_id"),
                            continue_on_fail=body.get("continue_on_fail"),
                        )
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
                if action == "report":
                    try:
                        wstate = orch.get_workflow(wf_id)
                        from dashboard.dataset_store import get_active
                        ds = get_active().to_dict(include_messages=False)
                        path = write_workflow_report(wf_id, wstate, dataset=ds)
                        payload = build_report_payload(wf_id, wstate, dataset=ds)
                        payload["report_path"] = str(path.relative_to(ROOT))
                        payload["report_url"] = f"/dashboard/data/reports/{wf_id}.html"
                        return _json_response(self, 200, payload)
                    except KeyError as e:
                        return _json_response(self, 404, {"error": str(e)})

        if path == "/api/tier1/ordering/preview":
            try:
                ordering = body.get("ordering")
                if not ordering or not isinstance(ordering, str):
                    return _json_response(self, 400, {"error": "ordering string required"})
                ds = get_active()
                out = tier1_api.ordering_preview(
                    list(ordering),
                    messages=[list(x) for x in ds.ciphertexts],
                    N=ds.deck_size,
                    labels=ds.labels,
                )
                return _json_response(self, 200, out)
            except ValueError as e:
                return _json_response(self, 400, {"error": str(e)})

        if path == "/api/tier1/rosetta":
            try:
                pins_raw = body.get("pins", [])
                pins = {}
                for p in pins_raw:
                    if isinstance(p, dict):
                        pins[int(p["value"])] = str(p["char"])[:1]
                    else:
                        v, ch = str(p).split(":", 1)
                        pins[int(v.strip())] = ch.strip()[:1]
                out = tier1_api.rosetta_propagate(
                    pins,
                    crib=body.get("crib"),
                    offset=int(body.get("offset", 0)),
                )
                return _json_response(self, 200, out)
            except (ValueError, KeyError) as e:
                return _json_response(self, 400, {"error": str(e)})

        if path == "/api/tier1/base-search":
            try:
                out = tier1_api.run_base_search(
                    mode=body.get("mode", "auto"),
                    phrase=body.get("crib"),
                    offset=int(body.get("offset", 0)),
                    top=int(body.get("top", 10)),
                )
                return _json_response(self, 200, out)
            except ValueError as e:
                return _json_response(self, 400, {"error": str(e)})

        if path == "/api/tier1/refrain-pipeline":
            try:
                out = tier1_api.run_refrain_pipeline_api(
                    anchors=body.get("anchors") or [],
                    top=int(body.get("top", 15)),
                )
                return _json_response(self, 200, out)
            except ValueError as e:
                return _json_response(self, 400, {"error": str(e)})

        if path == "/api/tier2/pos0-base":
            try:
                out = tier2_api.run_pos0_analysis()
                return _json_response(self, 200, out)
            except ValueError as e:
                return _json_response(self, 400, {"error": str(e)})

        if path == "/api/tier2/triplet-base-search":
            try:
                out = tier2_api.run_triplet_base_search(
                    mode=body.get("mode", "auto"),
                    phrase=body.get("crib"),
                    top=int(body.get("top", 5)),
                )
                return _json_response(self, 200, out)
            except ValueError as e:
                return _json_response(self, 400, {"error": str(e)})

        if path == "/api/tier2/order-bench":
            try:
                phrases = body.get("phrases") or body.get("phrase")
                if isinstance(phrases, str):
                    phrases = [phrases]
                out = tier2_api.run_order_bench(
                    phrases=phrases,
                    top=int(body.get("top", 15)),
                )
                return _json_response(self, 200, out)
            except ValueError as e:
                return _json_response(self, 400, {"error": str(e)})

        if path == "/api/tier2/compose-order":
            try:
                out = tier2_api.run_compose_order_api(
                    anchors=body.get("anchors") or [],
                    seed_phrases=body.get("seeds") or [],
                    top=int(body.get("top", 15)),
                )
                return _json_response(self, 200, out)
            except ValueError as e:
                return _json_response(self, 400, {"error": str(e)})

        if path == "/api/tier2/exhaust-bench":
            try:
                phrase = body.get("phrase") or body.get("crib")
                if not phrase:
                    return _json_response(self, 400, {"error": "phrase required"})
                out = tier2_api.run_exhaust_bench_api(
                    phrase=str(phrase),
                    offset=int(body.get("offset", 0)),
                )
                return _json_response(self, 200, out)
            except ValueError as e:
                return _json_response(self, 400, {"error": str(e)})

        if path == "/api/rebuild":
            build_workbench()
            return _json_response(self, 200, {"ok": True})

        return _json_response(self, 404, {"error": "not found"})

    def _load_active(self):
        ds = get_active()
        return ds, ds.ciphertexts, ds.labels, ds.deck_size

    def _cipher_validate(self, body: dict):
        try:
            ds, messages, labels, N = self._load_active()
            mode = body.get("mode", "add")
            plain = parse_values(body.get("plaintext", ""), N=N) if body.get("plaintext") else None
            key = parse_values(body.get("key", ""), N=N) if body.get("key") else []
            uct = (parse_values(body.get("user_ciphertext", ""), N=N)
                   if body.get("user_ciphertext") else None)
            msg = body.get("message", labels[0] if labels else "Message 1")
            if mode == "user_ciphertext":
                if not uct:
                    return _json_response(self, 400, {"error": "ciphertext required"})
                r = validate_cipher(
                    messages, labels, mode=mode, message=msg,
                    offset=int(body.get("offset", 0)),
                    user_ciphertext=uct, N=N)
            else:
                if not plain:
                    return _json_response(self, 400, {"error": "plaintext required"})
                r = validate_cipher(
                    messages, labels, mode=mode, message=msg,
                    offset=int(body.get("offset", 0)),
                    plaintext=plain, key=key,
                    base=int(body.get("base", 0)), N=N)
            out = r.to_dict()
            out["dataset_id"] = ds.id
            out["dataset_name"] = ds.name
            return _json_response(self, 200, out)
        except ValueError as e:
            return _json_response(self, 400, {"error": str(e)})
        except Exception as e:
            return _json_response(self, 500, {"error": str(e)})

    def _cipher_sweep(self, body: dict):
        try:
            ds, messages, labels, N = self._load_active()
            plain = parse_values(body.get("plaintext", ""), N=N)
            if not plain:
                return _json_response(self, 400, {"error": "plaintext required"})
            key = parse_values(body.get("key", ""), N=N) if body.get("key") else []
            rows = sweep_linear_modes(
                messages, labels,
                message=body.get("message", labels[0] if labels else "Message 1"),
                offset=int(body.get("offset", 0)),
                plaintext=plain, key=key,
                base=int(body.get("base", 0)), N=N)
            return _json_response(self, 200, rows)
        except ValueError as e:
            return _json_response(self, 400, {"error": str(e)})
        except Exception as e:
            return _json_response(self, 500, {"error": str(e)})

    def _dataset_preview(self, body: dict):
        try:
            deck_size = _resolve_deck_size(body.get("deck_size", 83))
            out = preview_import(
                body.get("content", ""),
                fmt=body.get("format", "auto"),
                deck_size=deck_size,
            )
            return _json_response(self, 200, out)
        except ValueError as e:
            return _json_response(self, 400, {"error": str(e)})

    def _dataset_infer_deck(self, body: dict):
        try:
            content = (body.get("content") or "").strip()
            if content:
                result = infer_from_text(
                    content,
                    fmt=body.get("format", "auto"),
                )
            else:
                result = infer_active_dataset()
            return _json_response(self, 200, result)
        except ValueError as e:
            return _json_response(self, 400, {"error": str(e)})

    def _dataset_import(self, body: dict):
        try:
            deck_size = _resolve_deck_size(body.get("deck_size", 83))
            ds = import_and_save(
                body.get("content", ""),
                fmt=body.get("format", "auto"),
                name=body.get("name", "Imported dataset"),
                deck_size=deck_size,
                activate=bool(body.get("activate", True)),
            )
            return _json_response(self, 200, {
                "dataset": ds.to_dict(include_messages=False),
                "analysis": analyze_dataset(ds).to_dict(),
                "import_diagnostics": ds.metadata.get("import_diagnostics"),
                "deck_inference": ds.metadata.get("deck_inference"),
            })
        except ValueError as e:
            return _json_response(self, 400, {"error": str(e)})

    def _dataset_plant(self, body: dict):
        try:
            N = int(body.get("deck_size", 83))
            if N < 2 or N > 256:
                raise ValueError("deck_size must be in [2, 256]")
            labels, plains = parse_plaintext_messages(
                body.get("plaintexts", ""), N=N)
            if not plains:
                return _json_response(self, 400, {"error": "plaintexts required"})
            keys_raw = body.get("keys", "")
            keys = []
            if keys_raw.strip():
                for line in keys_raw.strip().splitlines():
                    keys.append(parse_values(line, N=N))
            bases_raw = body.get("bases", [])
            if isinstance(bases_raw, list):
                bases = [int(x) for x in bases_raw]
            elif bases_raw in (None, "", []):
                bases = []
            else:
                raise ValueError("bases must be a JSON array of integers")
            if not bases:
                bases = [0] * len(plains)
            hdr = body.get("inject_header")
            inject = None
            if hdr:
                if isinstance(hdr, str):
                    hdr = json.loads(hdr)
                if isinstance(hdr, list):
                    inject = tuple(int(x) for x in hdr)
                else:
                    raise ValueError("inject_header must be a JSON array [pos,sym,...]")
            ds = plant_dataset(
                plains, labels,
                mode=body.get("mode", "add"),
                keys=keys or None,
                bases=bases,
                deck_size=N,
                name=body.get("name", "Planted eye-puzzle dataset"),
                inject_header=inject,
            )
            save_planted(ds, activate=bool(body.get("activate", True)))
            return _json_response(self, 200, {
                "dataset": ds.to_dict(include_messages=False),
                "analysis": analyze_dataset(ds).to_dict(),
                "preview_glyphs": [
                    "".join(GLYPHS[v] if 0 <= v < len(GLYPHS) else "?" for v in ct)
                    for ct in ds.ciphertexts
                ],
            })
        except ValueError as e:
            return _json_response(self, 400, {"error": str(e)})
        except TypeError as e:
            return _json_response(self, 400, {"error": str(e)})

    def _dataset_convert(self, body: dict):
        try:
            N = int(body.get("deck_size", 83))
            if N < 2 or N > 256:
                raise ValueError("deck_size must be in [2, 256]")
            out = convert_plaintext_to_ciphertext(
                body.get("plaintext", ""),
                mode=body.get("mode", "add"),
                key_text=body.get("key", ""),
                base=int(body.get("base", 0)),
                N=N,
            )
            return _json_response(self, 200, out)
        except ValueError as e:
            return _json_response(self, 400, {"error": str(e)})


def main() -> int:
    ap = argparse.ArgumentParser(description="EYES Workbench HTTP server")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--open", action="store_true", help="open workbench in browser")
    args = ap.parse_args()

    if not (ROOT / "workbench.html").is_file():
        print("Building workbench.html …")
        build_workbench()

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
