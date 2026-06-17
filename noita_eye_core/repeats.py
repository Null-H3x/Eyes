"""Repeated-substring census — stream vs block/periodic/transposition, densely.

The most data-dense mapping-free probe we can run.  It enumerates every k-gram
across all nine messages and classifies the collisions, because *where* repeats
fall pins the cipher mode:

  * ALIGNED collisions (same k-gram at the SAME position in two messages) are
    DEPTH: equal plaintext under a shared per-column bijection.  Expected inside
    the shared openings / near-duplicate blocks; an aligned collision OUTSIDE
    those — especially CROSS-GROUP — would be a new shared passage or a global-
    key signal.
  * OFFSET collisions (same k-gram at DIFFERENT positions, within or across
    messages) are the mode discriminator.  Under a pure aperiodic stream they
    occur only at the chance rate (~ pairs / N^k, which is <<1 for k>=4).  An
    excess means the key/plaintext repeats at a lag (periodic / running-key) or a
    block was moved (transposition / cut / shuffle) or reused (ECB-like).

So: offset collisions ~ chance  =>  pure aperiodic stream (no block/cut/period).
    offset collisions >> chance  =>  block / periodic / transposition in play.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Dict, List, Sequence, Tuple

TRIPLETS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))


def _group(mi: int, partition=TRIPLETS) -> int:
    for gi, g in enumerate(partition):
        if mi in g:
            return gi
    return -1


def kgram_index(messages: Sequence[Sequence[int]], k: int
                ) -> Dict[Tuple[int, ...], List[Tuple[int, int]]]:
    idx: Dict[Tuple[int, ...], List[Tuple[int, int]]] = {}
    for mi, m in enumerate(messages):
        for p in range(len(m) - k + 1):
            idx.setdefault(tuple(m[p:p + k]), []).append((mi, p))
    return idx


@dataclass
class Census:
    k: int
    n_instances: int
    aligned: List[tuple]        # (value, (m1,p), (m2,p))  same position
    offset: List[tuple]         # (value, (m1,p1), (m2,p2)) different positions
    n_pairs_aligned: int        # # position-pairs at equal position (depth slots)
    n_pairs_offset: int         # # position-pairs at different positions
    exp_aligned: float          # chance collisions among aligned slots
    exp_offset: float           # chance collisions among offset slots


def census(messages: Sequence[Sequence[int]], N: int, k: int,
           opening_end: int = 25) -> Census:
    idx = kgram_index(messages, k)
    n_inst = sum(len(v) for v in idx.values())
    # count position-aligned vs offset PAIR opportunities (for the chance model)
    by_pos: Dict[int, int] = {}
    for m in messages:
        for p in range(len(m) - k + 1):
            by_pos[p] = by_pos.get(p, 0) + 1
    n_pairs_aligned = sum(cnt * (cnt - 1) // 2 for cnt in by_pos.values())
    n_pairs_total = n_inst * (n_inst - 1) // 2
    n_pairs_offset = n_pairs_total - n_pairs_aligned
    aligned: List[tuple] = []
    offset: List[tuple] = []
    for v, locs in idx.items():
        if len(locs) < 2:
            continue
        for (m1, p1), (m2, p2) in combinations(locs, 2):
            if p1 == p2 and m1 != m2:
                aligned.append((v, (m1, p1), (m2, p2)))
            elif p1 != p2:
                offset.append((v, (m1, p1), (m2, p2)))
    Nk = float(N) ** k
    return Census(k, n_inst, aligned, offset, n_pairs_aligned, n_pairs_offset,
                  n_pairs_aligned / Nk, n_pairs_offset / Nk)


def offset_excess(messages: Sequence[Sequence[int]], N: int, k: int) -> tuple:
    """(observed offset collisions, expected by chance, ratio)."""
    cen = census(messages, N, k)
    obs = len(cen.offset)
    return obs, cen.exp_offset, (obs / cen.exp_offset if cen.exp_offset > 0 else
                                 float("inf") if obs else 0.0)


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def selftest() -> List[tuple[str, bool]]:
    import numpy as np
    out: List[tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(0)
    T = 100

    # (1) Pure aperiodic stream + shared opening: aligned repeats in the opening,
    #     offset collisions at chance (~0 for k=5).
    K = [rng.integers(0, N, size=T) for _ in range(3)]
    opening = list(rng.integers(0, N, size=20))
    msgs = []
    for gi, g in enumerate(TRIPLETS):
        for _ in g:
            p = opening + list(rng.integers(0, N, size=T - 20))
            msgs.append([(p[t] + int(K[gi][t])) % N for t in range(T)])
    cen5 = census(msgs, N, 5)
    out.append(("stream: aligned collisions exist (shared opening)",
                len(cen5.aligned) > 0))
    out.append(("stream: offset collisions ~ chance (none for k=5)",
                len(cen5.offset) == 0))

    # (2) Transposition: copy a block to another position in one message ->
    #     an OFFSET collision must appear.
    msgs2 = [list(m) for m in msgs]
    block = msgs2[0][30:40]
    msgs2[0][60:70] = block            # duplicate a 10-long block at a new position
    cen5b = census(msgs2, N, 5)
    out.append(("transposition/duplicated block -> offset collision detected",
                len(cen5b.offset) > len(cen5.offset)))

    # (3) Periodic key + periodic plaintext -> offset collisions at the period.
    d = 10
    Kper = [int(x) for x in rng.integers(0, N, size=d)] * (T // d + 1)
    pcyc = [int(x) for x in rng.integers(0, N, size=d)] * (T // d + 1)
    cipher = [[(pcyc[t] + Kper[t]) % N for t in range(T)] for _ in range(2)]
    cen5p = census(cipher, N, 5)
    out.append(("periodic key+plaintext -> many offset collisions",
                len(cen5p.offset) > 20))

    # (4) chance model sanity: pure random corpus, k=5 offset ~ expected (<1).
    rndc = [list(rng.integers(0, N, size=T)) for _ in range(9)]
    obs, exp, ratio = offset_excess(rndc, N, 5)
    out.append(("random corpus: offset collisions near chance expectation",
                obs <= 3 and exp < 1.0))

    # (5) aligned classification: a planted same-position cross-message 5-gram.
    out.append(("aligned collisions are same-position cross-message",
                all(a[1][1] == a[2][1] and a[1][0] != a[2][0] for a in cen5.aligned)))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} repeats checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
