"""Dashboard selftest — registry, presets, orchestrator smoke."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def selftest(*, quick: bool = False) -> List[Tuple[str, bool]]:
    from dashboard.registry import load_tools
    from dashboard.workflows import PRESETS, validate_presets
    from dashboard.orchestrator import have_venv, get_orchestrator

    tools = load_tools()
    ids = [t.id for t in tools]
    out: List[Tuple[str, bool]] = []

    out.append(("registry loads tools from eyes.WORKFLOWS", len(tools) >= 40))
    out.append(("registry tool IDs are unique", len(ids) == len(set(ids))))
    missing = validate_presets(ids)
    out.append(("workflow presets reference valid tool IDs", len(missing) == 0))
    out.append(("at least 4 workflow presets", len(PRESETS) >= 4))

    orch = get_orchestrator()
    snap = orch.snapshot()
    out.append(("orchestrator snapshot has tools_count", snap.get("tools_count", 0) >= 40))
    out.append(("orchestrator list_workflows matches presets",
                len(orch.list_workflows()) == len(PRESETS)))

    from dashboard.build import _collect_snapshot, render_html
    from dashboard.cipher_validate import selftest as cv_selftest
    from dashboard.deck_infer import selftest as di_selftest
    from dashboard.import_parse import selftest as ip_selftest
    from dashboard.dataset_store import get_active_id, list_datasets, selftest as ds_selftest
    from dashboard.eye_puzzle import selftest as ep_selftest
    from dashboard.workflow_map import selftest as wm_selftest, workflow_map_payload

    data = _collect_snapshot()
    html = render_html(data)
    out.append(("build render_html non-empty", len(html) > 5000))
    out.append(("build HTML includes workflow map tab", "panel-map" in html))
    out.append(("build HTML includes cipher tab", "panel-ciphers" in html))
    out.append(("build HTML includes datasets tab", "panel-datasets" in html))
    out.append(("build HTML includes import preview", "ds-preview-btn" in html))
    out.append(("build HTML includes infer deck", "ds-infer-deck-btn" in html))
    out.append(("build HTML h3x dash header", "h3x-mark" in html))
    out.append(("workflow map has phases", len(workflow_map_payload()["phases"]) == 5))
    wm = wm_selftest()
    out.append(("workflow_map selftest", all(ok for _, ok in wm)))
    out.append(("tools have global numbers", all("num" in t for t in data["tools"])))
    out.append(("active dataset in snapshot", data.get("active_dataset_id") is not None))
    out.append(("dataset list includes builtin", any(
        d["id"] == "noita-eye-corpus" for d in list_datasets())))

    cv = cv_selftest()
    out.append(("cipher_validate selftest", all(ok for _, ok in cv)))
    ip = ip_selftest()
    out.append(("import_parse selftest", all(ok for _, ok in ip)))
    di = di_selftest()
    out.append(("deck_infer selftest", all(ok for _, ok in di)))
    ds = ds_selftest()
    out.append(("dataset_store selftest", all(ok for _, ok in ds)))
    ep = ep_selftest()
    out.append(("eye_puzzle selftest", all(ok for _, ok in ep)))

    # Optional live run when venv exists (fast tool only)
    if have_venv() and not quick:
        rec = orch.start_tool("validate-run-the-full-math-gate-validate-everything", wait=True)
        out.append(("orchestrator runs selftest job", rec.status == "completed"))
        out.append(("orchestrator captures stdout",
                    len(orch.get_stdout(rec.id)) > 100))
    else:
        out.append(("orchestrator run skipped (no .venv)", True))
        out.append(("orchestrator stdout skipped (no .venv)", True))

    return out


if __name__ == "__main__":
    import argparse
    import sys
    ap = argparse.ArgumentParser(description="Dashboard selftest")
    ap.add_argument("--quick", action="store_true",
                    help="skip live subprocess job (registry/build only)")
    args = ap.parse_args()
    results = selftest(quick=args.quick)
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n = sum(1 for _, ok in results if ok)
    print(f"\n{n}/{len(results)} dashboard checks passed")
    sys.exit(0 if n == len(results) else 1)
