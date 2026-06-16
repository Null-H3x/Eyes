"""Aggregate selftest for the whole noita_eye_core package.

Runs every module's selftest and reports a single pass/fail summary.  Exit code
0 iff all checks pass.  This is the math gate for the package.
"""
from __future__ import annotations

import sys
from typing import Callable, List, Tuple

import cipher_ops
import classify
import corpus
import depth
import grouping
import lm
import null_model
import oracle
import prng
import stats
import trigram

MODULES: List[Tuple[str, Callable[[], List[Tuple[str, bool]]]]] = [
    ("corpus", corpus.selftest),
    ("cipher_ops", cipher_ops.selftest),
    ("stats", stats.selftest),
    ("lm", lm.selftest),
    ("null_model", null_model.selftest),
    ("prng", prng.selftest),
    ("trigram", trigram.selftest),
    ("depth", depth.selftest),
    ("classify", classify.selftest),
    ("grouping", grouping.selftest),
    ("oracle", oracle.selftest),
]


def main() -> int:
    total = 0
    passed = 0
    failures: List[str] = []
    for name, fn in MODULES:
        results = fn()
        n_ok = sum(1 for _, ok in results if ok)
        total += len(results)
        passed += n_ok
        status = "OK  " if n_ok == len(results) else "FAIL"
        print(f"[{status}] {name:12} {n_ok}/{len(results)}")
        for label, ok in results:
            if not ok:
                failures.append(f"{name}: {label}")

    print("-" * 56)
    print(f"  total : {total}")
    print(f"  ok    : {passed}")
    print("-" * 56)
    if failures:
        print("FAILURES:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("ALL GREEN — noita_eye_core math checks pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
