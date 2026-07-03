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
    from dashboard.workflows import PRESETS, validate_presets, preset_by_id
    from dashboard.orchestrator import have_venv, get_orchestrator, selftest as orch_selftest
    from dashboard.dataset_store import BUILTIN_ID, get_active_id, list_datasets, selftest as ds_selftest

    tools = load_tools()
    ids = [t.id for t in tools]
    out: List[Tuple[str, bool]] = []

    out.append(("registry loads tools from eyes.WORKFLOWS", len(tools) >= 40))
    out.append(("registry tool IDs are unique", len(ids) == len(set(ids))))
    missing = validate_presets(ids)
    out.append(("workflow presets reference valid tool IDs", len(missing) == 0))
    out.append(("at least 5 workflow presets", len(PRESETS) >= 5))
    practice = preset_by_id().get("practice-corpus")
    out.append(("practice-corpus preset exists", practice is not None))
    if practice:
        out.append(("practice-corpus has deck infer first",
                    practice.steps[0] == "validate-infer-deck-size-n-active-corpus-alphabet"))

    ochecks = orch_selftest()
    out.append(("orchestrator selftest", all(ok for _, ok in ochecks)))

    # Dependency wiring — import every dashboard module without cycles.
    try:
        import dashboard.build  # noqa: F401
        import dashboard.cipher_validate  # noqa: F401
        import dashboard.dataset_store  # noqa: F401
        import dashboard.deck_infer  # noqa: F401
        import dashboard.eye_puzzle  # noqa: F401
        import dashboard.import_parse  # noqa: F401
        import dashboard.orchestrator  # noqa: F401
        import dashboard.registry  # noqa: F401
        import dashboard.server  # noqa: F401
        import dashboard.workflow_map  # noqa: F401
        import dashboard.workflows  # noqa: F401
        import dashboard.workflow_report  # noqa: F401
        import dashboard.cut_recipe  # noqa: F401
        out.append(("dashboard modules import cleanly", True))
    except Exception as exc:
        out.append(("dashboard modules import cleanly", False))
        out.append((f"import error: {exc}", False))

    orch = get_orchestrator()
    snap = orch.snapshot()
    out.append(("orchestrator snapshot has tools_count", snap.get("tools_count", 0) >= 40))
    out.append(("orchestrator list_workflows matches presets",
                len(orch.list_workflows()) == len(PRESETS)))
    qv = orch.get_workflow("quick-validate")
    preset = preset_by_id()["quick-validate"]
    out.append(("workflow steps sync with preset ids",
                [s["tool_id"] for s in qv["steps"]] == list(preset.steps)))

    from dashboard.build import _collect_snapshot, render_html
    from dashboard.cipher_validate import selftest as cv_selftest
    from dashboard.deck_infer import selftest as di_selftest
    from dashboard.import_parse import selftest as ip_selftest
    from dashboard.workflow_report import selftest as wr_selftest
    from dashboard.eye_puzzle import selftest as ep_selftest
    from dashboard.cut_recipe import selftest as cr_selftest
    from dashboard.workflow_map import selftest as wm_selftest, workflow_map_payload
    out.extend(cr_selftest())

    data = _collect_snapshot()
    html = render_html(data)
    out.append(("build render_html non-empty", len(html) > 5000))
    out.append(("build HTML includes workflow map tab", "panel-map" in html))
    out.append(("build HTML includes cipher tab", "panel-ciphers" in html))
    out.append(("build HTML includes datasets tab", "panel-datasets" in html))
    out.append(("build HTML includes cut recipe tab", "panel-cut-recipe" in html))
    out.append(("build HTML includes import preview", "ds-preview-btn" in html))
    out.append(("build HTML includes infer deck", "ds-infer-deck-btn" in html))
    out.append(("build HTML h3x dash header", "h3x-mark" in html))
    out.append(("build HTML includes corpus bridge", "ensureActiveDataset" in html))
    out.append(("build HTML workflow corpus banner", "wf-corpus-banner" in html))
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
    wr = wr_selftest()
    out.append(("workflow_report selftest", all(ok for _, ok in wr)))
    out.append(("build HTML format options", "digit_stream" in html))
    out.append(("build HTML workflow report btn", "wf-report" in html))
    di = di_selftest()
    out.append(("deck_infer selftest", all(ok for _, ok in di)))
    ds = ds_selftest()
    out.append(("dataset_store selftest", all(ok for _, ok in ds)))
    ep = ep_selftest()
    out.append(("eye_puzzle selftest", all(ok for _, ok in ep)))

    # Optional live run when venv exists (fast tool only; always use Noita builtin)
    if have_venv() and not quick:
        from dashboard.dataset_store import set_active
        saved_active = get_active_id()
        rec = orch.start_tool(
            "validate-run-the-full-math-gate-validate-everything",
            dataset_id=BUILTIN_ID,
            wait=True,
        )
        out.append(("orchestrator runs selftest job", rec.status == "completed"))
        out.append(("orchestrator job uses builtin corpus",
                    rec.dataset_id == BUILTIN_ID))
        out.append(("orchestrator captures stdout",
                    len(orch.get_stdout(rec.id)) > 100))
        set_active(saved_active)
        out.append(("orchestrator restores active after math gate",
                    get_active_id() == saved_active))
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
