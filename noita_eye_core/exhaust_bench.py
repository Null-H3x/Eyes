"""Ordering exhaust bench — Phase 2 residual ordering search wrapper.

Thin Tier-2 layer over ``ordering_exhaust`` with formatted reports for CLI and
dashboard consumption.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import ordering_exhaust as oe
import refrain as rf


def run_exhaust(
    messages: Sequence[Sequence[int]],
    crib: str,
    offset: int,
    N: int,
    *,
    region=None,
    exhaust_if_free: int = 12,
    max_perms: int = 500_000,
    hillclimb_restarts: int = 20,
    n_null: int = 30,
) -> oe.ExhaustResult:
    return oe.exhaust_ordering(
        messages, crib, offset, N,
        region=region or rf.DEFAULT_INSTANCES,
        exhaust_if_free=exhaust_if_free,
        max_perms=max_perms,
        hillclimb_restarts=hillclimb_restarts,
        n_null=n_null,
    )


def format_report(
    result: oe.ExhaustResult,
    *,
    crib: str = "",
    offset: int = 0,
    labels: Optional[Sequence[str]] = None,
) -> str:
    lines = [
        "=" * 72,
        "ORDERING EXHAUST — Phase 2 residual search",
        "=" * 72,
        f"phrase: {crib!r}  offset: {offset}",
        f"consistent: {result.consistent}  method: {result.method}  "
        f"free_slots: {result.free_slots}",
        f"pinned: {result.symbols_pinned}  z: {result.z:.2f}  "
        f"word-cov: {result.word_coverage:.1%}",
    ]
    if result.plaintext and labels:
        lines.append("")
        for mi in sorted(result.plaintext):
            lab = labels[mi] if mi < len(labels) else str(mi)
            lines.append(f"  {lab}: {result.plaintext[mi][:90]}")
    lines.append("")
    lines.append("READ: exhaustive when free_slots small; else hill-climb fallback.")
    return "\n".join(lines)


def selftest() -> List[Tuple[str, bool]]:
    import numpy as np
    import ngram_solve as ng

    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(0)
    alphabet = rf.DEFAULT_ALPHABET
    aidx = {ch: i for i, ch in enumerate(alphabet)}
    eng = [aidx[ch] for ch in ng._ENGLISH if ch in aidx]
    crib = "trueknowledgeofthegods"
    cv = [aidx[ch] for ch in crib]
    insts = [(0, 30), (0, 70), (1, 35), (1, 75)]
    C = list(rng.permutation(N))
    bases = [int(b) for b in rng.integers(0, N, size=4)]
    T = 110
    msgs = []
    pos0 = 0
    for m in range(4):
        p = [eng[(pos0 + i) % len(eng)] for i in range(T)]
        pos0 += T
        for (mm, ps) in insts:
            if mm == m:
                p[ps: ps + len(cv)] = cv
        msgs.append([C[(p[t] + bases[m] + t) % N] for t in range(T)])

    r = run_exhaust(msgs, crib, 0, N, region=insts,
                    exhaust_if_free=12, max_perms=5000,
                    hillclimb_restarts=2, n_null=10)
    out.append(("exhaust bench consistent on plant", r.consistent))
    out.append(("exhaust bench z>=6", r.z >= 6))
    out.append(("format_report non-empty", "ORDERING EXHAUST" in format_report(r, crib=crib)))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} exhaust_bench checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
