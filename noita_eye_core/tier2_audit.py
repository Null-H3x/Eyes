"""Tier-2 paranoia audit — cross-module dependency and edge-case checks."""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Callable, List, Tuple

_REPO = Path(__file__).resolve().parent.parent
_CORE = _REPO / "noita_eye_core"
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
if str(_CORE) not in sys.path:
    sys.path.insert(0, str(_CORE))

TIER2_MODULES = (
    "pos0_base",
    "triplet_base_search",
    "order_bench",
    "compose_order",
    "exhaust_bench",
)

CLI_SCRIPTS = (
    "eyecrack/pos0_base.py",
    "eyecrack/triplet_base_search.py",
    "eyecrack/order_bench.py",
    "eyecrack/compose_order.py",
    "eyecrack/exhaust_bench.py",
)


def _import(name: str):
    return importlib.import_module(name)


def audit_imports() -> List[Tuple[str, bool]]:
    out = []
    for name in TIER2_MODULES:
        try:
            _import(name)
            out.append((f"import {name}", True))
        except Exception as exc:
            out.append((f"import {name}: {exc}", False))
    return out


def audit_tier1_deps() -> List[Tuple[str, bool]]:
    out = []
    try:
        import base_search
        import order_solve
        import ordering_exhaust
        import refrain_compose
        out.append(("tier1 deps import", True))
    except Exception as exc:
        out.append((f"tier1 deps: {exc}", False))
    try:
        import triplet_base_search as tbs
        out.append(("triplet_base_search uses base_search",
                      hasattr(tbs, "search_all")))
    except Exception as exc:
        out.append((f"triplet_base_search link: {exc}", False))
    return out


def audit_cli_exists() -> List[Tuple[str, bool]]:
    out = []
    for rel in CLI_SCRIPTS:
        p = _REPO / rel
        out.append((f"CLI {rel}", p.is_file()))
    return out


def audit_dashboard_api() -> List[Tuple[str, bool]]:
    out = []
    try:
        from dashboard import tier2_api
        out.append(("dashboard.tier2_api import", True))
        out.append(("run_order_bench callable", callable(tier2_api.run_order_bench)))
    except Exception as exc:
        out.append((f"dashboard.tier2_api: {exc}", False))
    return out


def audit_empty_corpus_edge() -> List[Tuple[str, bool]]:
    out = []
    try:
        import pos0_base as p0
        rep = p0.analyze([], 83)
        out.append(("pos0_base empty messages", rep.model == "empty"))
    except Exception as exc:
        out.append((f"pos0_base empty: {exc}", False))
    try:
        import order_bench as ob
        out.append(("order_bench empty phrases", ob.run_bench([], [], 83) == []))
    except Exception as exc:
        out.append((f"order_bench empty: {exc}", False))
    try:
        import triplet_base_search as tbs
        rep = tbs.search_all([], 83)
        out.append(("triplet_base_search empty corpus", rep.results == []))
    except Exception as exc:
        out.append((f"triplet_base_search empty: {exc}", False))
    return out


def audit_phrase_length_edge() -> List[Tuple[str, bool]]:
    import order_bench as ob
    out = []
    msgs = [[1, 2, 3] * 30]
    short = ob.run_bench(msgs, ["ab"], 83, region=[(0, 5)], region_len=22)
    out.append(("order_bench rejects short phrase", short == []))
    long_phrase = "a" * 30
    long = ob.run_bench(msgs, [long_phrase], 83, region=[(0, 5)], region_len=22)
    out.append(("order_bench rejects long phrase", long == []))
    return out


def audit_eyes_registration() -> List[Tuple[str, bool]]:
    out = []
    try:
        import eyes
        titles = [t[0] for t in eyes.WORKFLOWS]
        needed = ("Pos-0 base", "Triplet base search", "Order bench",
                  "Compose → order", "Ordering exhaust bench")
        for needle in needed:
            out.append((f"eyes.py registers {needle}",
                        any(needle.lower() in t.lower() for t in titles)))
    except Exception as exc:
        out.append((f"eyes.py: {exc}", False))
    return out


def run_all(include_module_selftests: bool = False) -> List[Tuple[str, bool]]:
    sections: List[Callable[[], List[Tuple[str, bool]]]] = [
        audit_imports,
        audit_tier1_deps,
        audit_cli_exists,
        audit_dashboard_api,
        audit_empty_corpus_edge,
        audit_phrase_length_edge,
        audit_eyes_registration,
    ]
    out: List[Tuple[str, bool]] = []
    if include_module_selftests:
        for fn in TIER2_MODULES:
            try:
                mod = _import(fn)
                if hasattr(mod, "selftest"):
                    out.extend(mod.selftest())
            except Exception as exc:
                out.append((f"{fn}.selftest import: {exc}", False))
    for sec in sections:
        out.extend(sec())
    return out


def main() -> int:
    results = run_all()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} tier2 paranoia checks passed")
    return 0 if n_ok == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
