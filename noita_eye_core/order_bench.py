"""Order-solve bench — batch crib → ordering recovery with ranked report.

Tier-2 wrapper around ``order_solve`` for tractable multi-phrase / wordlist runs
with structured output for dashboard and CLI consumption.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import ngram_solve as ng
import order_solve as os_
import refrain as rf


@dataclass
class OrderBenchHit:
    phrase: str
    offset: int
    z: float
    word_coverage: float
    symbols_pinned: int
    coverage: float
    consistent: bool
    contradiction_slot: Optional[Tuple[int, int]] = None
    plaintext: Dict[int, str] = field(default_factory=dict)


def run_bench(
    messages: Sequence[Sequence[int]],
    phrases: Sequence[str],
    N: int,
    *,
    labels: Optional[Sequence[str]] = None,
    region=None,
    region_len: Optional[int] = None,
    offset: Optional[int] = None,
    alphabet: Optional[str] = None,
    restarts: int = 4,
    iters: int = 2500,
    n_null: int = 30,
    top: int = 20,
) -> List[OrderBenchHit]:
    region = region or rf.DEFAULT_INSTANCES
    region_len = region_len or rf.DEFAULT_LEN
    alphabet = alphabet or rf.DEFAULT_ALPHABET
    model = ng.TrigramModel(alphabet, ng._ENGLISH)
    hits: List[OrderBenchHit] = []
    seen = set()

    for raw in phrases:
        phrase = "".join(c for c in raw.lower() if c.isalpha())
        if len(phrase) < 3 or len(phrase) > region_len:
            continue
        offs = [offset] if offset is not None else rf.viable_offsets(
            messages, phrase, region, region_len, N)
        if not offs:
            continue
        best: Optional[OrderBenchHit] = None
        for off in offs:
            key = (phrase, off)
            if key in seen:
                continue
            r = os_.solve(messages, phrase, off, N, alphabet=alphabet, model=model,
                          region=region, restarts=restarts, iters=iters, n_null=n_null)
            if not r.consistent:
                continue
            h = OrderBenchHit(
                phrase=phrase, offset=off, z=r.z, word_coverage=r.word_coverage,
                symbols_pinned=r.symbols_pinned, coverage=r.coverage,
                consistent=True, contradiction_slot=r.contradiction_slot,
                plaintext=dict(r.plaintext),
            )
            if best is None or h.z > best.z:
                best = h
        if best:
            seen.add((best.phrase, best.offset))
            hits.append(best)

    hits.sort(key=lambda h: (h.z, h.word_coverage), reverse=True)
    return hits[:top]


def format_report(
    hits: Sequence[OrderBenchHit],
    *,
    labels: Optional[Sequence[str]] = None,
) -> str:
    lines = [
        "=" * 72,
        "ORDER BENCH — crib → ordering recovery",
        "=" * 72,
        "",
        f"{'rank':>4}  {'z':>6}  {'wcov':>6}  {'pin':>4}  {'off':>3}  phrase",
        "-" * 72,
    ]
    for i, h in enumerate(hits, 1):
        lines.append(
            f"{i:4d}  {h.z:6.1f}  {h.word_coverage:6.1%}  {h.symbols_pinned:4d}  "
            f"{h.offset:3d}  {h.phrase[:32]!r}"
        )
    if hits and labels:
        best = hits[0]
        if best.z >= 6 or best.word_coverage >= 0.15:
            lines.append("")
            lines.append(f"--- best ({best.phrase!r} @ {best.offset}) ---")
            for mi in sorted(best.plaintext):
                lab = labels[mi] if mi < len(labels) else str(mi)
                lines.append(f"  {lab}: {best.plaintext[mi][:90]}")
    lines.append("")
    lines.append("READ: z + word-cov under order_solve — extend crib toward full refrain region.")
    return "\n".join(lines)


def selftest() -> List[Tuple[str, bool]]:
    import numpy as np

    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(3)
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

    hits = run_bench(msgs, [crib, "wrongphrasehere"], N, region=insts,
                     restarts=2, iters=800, n_null=10, top=5)
    out.append(("bench returns plant hit", any(h.phrase == crib for h in hits)))
    out.append(("plant hit high z", any(h.phrase == crib and h.z >= 6 for h in hits)))
    out.append(("empty phrases safe", run_bench(msgs, [], N) == []))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} order_bench checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
