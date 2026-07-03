"""eyeforward aggregate selftest — runs every module's paranoia audit.

Usage:  python3 selftest.py           (all modules)
        python3 selftest.py --fast    (skip the slow order_anneal solve checks)

House format: each module exposes selftest() -> List[(name, ok)]. This runner
collects them, prints a ledger, and exits nonzero on any failure.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "noita_eye_core"))

MODULES = ["plantlab", "pyry_gate", "support_min", "order_anneal",
           "order_gpu", "iso_relax", "model_power"]
SLOW = {"order_anneal", "model_power"}   # heavy: full plant read / MC plants


def main() -> int:
    fast = "--fast" in sys.argv
    total = failed = 0
    for name in MODULES:
        if fast and name in SLOW:
            print(f"-- {name}: SKIPPED (--fast)")
            continue
        mod = __import__(name)
        t0 = time.time()
        results = mod.selftest()
        dt = time.time() - t0
        ok_n = sum(1 for _, ok in results if ok)
        print(f"-- {name}: {ok_n}/{len(results)} ok  ({dt:.1f}s)")
        for check, ok in results:
            total += 1
            if not ok:
                failed += 1
                print(f"   [FAIL] {check}")
    print(f"\n{total - failed}/{total} checks passed"
          + (f"  ({failed} FAILURES)" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
