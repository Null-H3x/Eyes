"""Aggregate selftest for the whole noita_eye_core package.

Runs every module's selftest and reports a single pass/fail summary.  Exit code
0 iff all checks pass.  This is the math gate for the package.
"""
from __future__ import annotations

import sys
from typing import Callable, List, Tuple

import calibrate
import cipher_fingerprint
import cipher_ops
import classify
import corpus
import cribdrag
import depth
import depthmap
import globality
import embedded_key
import grouping
import header_test
import keyscan
import keystream_scope
import langdetect
import lm
import numbertest
import null_model
import oracle
import pairdiff
import chain_models
import chain_extract
import cribfit
import headerbase
import pureprog
import trifid
import provenance
import refrain
import ngram_solve
import order_solve
import template
import model_audit
import isomorph
import prng
import repeats
import salakieli
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
    ("embedded_key", embedded_key.selftest),
    ("keystream_scope", keystream_scope.selftest),
    ("header_test", header_test.selftest),
    ("numbertest", numbertest.selftest),
    ("depthmap", depthmap.selftest),
    ("globality", globality.selftest),
    ("pairdiff", pairdiff.selftest),
    ("langdetect", langdetect.selftest),
    ("cribdrag", cribdrag.selftest),
    ("cipher_fingerprint", cipher_fingerprint.selftest),
    ("keyscan", keyscan.selftest),
    ("calibrate", calibrate.selftest),
    ("salakieli", salakieli.selftest),
    ("repeats", repeats.selftest),
    ("isomorph", isomorph.selftest),
    ("chain_models", chain_models.selftest),
    ("chain_extract", chain_extract.selftest),
    ("cribfit", cribfit.selftest),
    ("headerbase", headerbase.selftest),
    ("pureprog", pureprog.selftest),
    ("trifid", trifid.selftest),
    ("provenance", provenance.selftest),
    ("refrain", refrain.selftest),
    ("ngram_solve", ngram_solve.selftest),
    ("order_solve", order_solve.selftest),
    ("template", template.selftest),
    ("model_audit", model_audit.selftest),
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
