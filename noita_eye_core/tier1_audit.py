"""Tier-1 paranoia audit — cross-module dependency and edge-case checks."""
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

# Modules that must import cleanly and expose selftest
TIER1_MODULES = (
    "rosetta",
    "template_phrase",
    "base_search",
    "refrain_pipeline",
    "alphabet_brute",
)

# CLI entrypoints (relative to repo root)
CLI_SCRIPTS = (
    "eyecrack/rosetta.py",
    "eyecrack/template_phrase.py",
    "eyecrack/base_search.py",
    "eyecrack/refrain_pipeline.py",
    "eyecrack/alphabet_brute.py",
)


def _import(name: str):
    return importlib.import_module(name)


def audit_imports() -> List[Tuple[str, bool]]:
    out = []
    for name in TIER1_MODULES:
        try:
            _import(name)
            out.append((f"import {name}", True))
        except Exception as exc:
            out.append((f"import {name}: {exc}", False))
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
        from dashboard import tier1_api
        out.append(("dashboard.tier1_api import", True))
        out.append(("default_alphabet len>=83",
                      len(tier1_api.default_alphabet()) >= 83))
    except Exception as exc:
        out.append((f"dashboard.tier1_api: {exc}", False))
    return out


def audit_empty_corpus_edge() -> List[Tuple[str, bool]]:
    out = []
    try:
        import rosetta as rs
        rep = rs.analyze([], {}, 83)
        out.append(("rosetta empty messages", rep.pinned_values == 0))
    except Exception as exc:
        out.append((f"rosetta empty: {exc}", False))
    try:
        import template_phrase as tp
        cands = tp.generate_candidates([], 83, max_phrases=10)
        out.append(("template_phrase empty corpus", cands == []))
    except Exception as exc:
        out.append((f"template_phrase empty: {exc}", False))
    return out


def audit_pin_parse_edge() -> List[Tuple[str, bool]]:
    import rosetta as rs
    out = []
    try:
        rs.parse_pins(["0:a", "1:b"])
        out.append(("parse_pins valid", True))
    except Exception:
        out.append(("parse_pins valid", False))
    try:
        rs.parse_pins(["bad"])
        out.append(("parse_pins rejects bad", False))
    except ValueError:
        out.append(("parse_pins rejects bad", True))
    try:
        rs.parse_pins(["99:x"])
        rs.build_ordering({99: "x"}, 83)
        out.append(("build_ordering rejects OOB", False))
    except ValueError:
        out.append(("build_ordering rejects OOB", True))
    return out


def audit_eyes_registration() -> List[Tuple[str, bool]]:
    out = []
    try:
        import eyes
        titles = [t[0] for t in eyes.WORKFLOWS]
        needed = ("Rosetta", "Refrain pipeline", "Template phrase", "Base search")
        for needle in needed:
            out.append((f"eyes.py registers {needle}",
                        any(needle.lower() in t.lower() for t in titles)))
    except Exception as exc:
        out.append((f"eyes.py: {exc}", False))
    return out


def run_all(include_module_selftests: bool = False) -> List[Tuple[str, bool]]:
    sections: List[Callable[[], List[Tuple[str, bool]]]] = [
        audit_imports,
        audit_cli_exists,
        audit_dashboard_api,
        audit_empty_corpus_edge,
        audit_pin_parse_edge,
        audit_eyes_registration,
    ]
    out: List[Tuple[str, bool]] = []
    if include_module_selftests:
        for fn in TIER1_MODULES:
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
    print(f"\n{n_ok}/{len(results)} tier1 paranoia checks passed")
    return 0 if n_ok == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
