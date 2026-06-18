"""Header-base constraint: what the literal universal (66,5) header forces, and a
contamination correction to the 'progressive refuted' verdict.

Facts:
  (F1) positions 1,2 carry the SAME ciphertext (66,5) in every message and read as
       LITERAL/SHARED (header_test: cross-agreement 1.00, p ~ 3e-12);
  (F2) position 0 is a DISTINCT per-message symbol.

Analytic deduction. Under PER-MESSAGE-PROGRESSIVE  x[c] = p + base_m + t, a literal
header (p[m][1] = h1 for all m) gives x[66] = h1 + base_m + 1, so
    base_m = x[66] - h1 - 1   is the SAME for every m  =>  ALL BASES EQUAL.
Equal bases collapse per-message-progressive to PURE PROGRESSIVE (one global
sliding alphabet). So a literal universal header REMOVES the per-message phase:
within the progressive family it forces the simplest member. (Equivalently, the
per-message bases that make chain_extract's per-msg-progressive permissive are
not free if the header is literal.)

Contamination correction. The earlier 'PROGRESSIVE REFUTED' verdict used
isomorph.progressive_chain on RAW find_isomorphs, which is contaminated. On the
contamination-filtered CLEAN set at the clean anchor (mr=4, shuffle-null ~ 0) pure
progressive has ZERO contradictions; the contradictions only appear once lower-
confidence (mr=3) isomorphs are mixed in. So progressive is NOT robustly refuted —
the trustworthy-clean isomorphs are consistent with it (though too localised, one
repeated passage, to confirm it). Status: OPEN, not refuted.

The alternative CIPHERTEXT-AUTOKEY reading p_t = c_t - c_{t-1} makes p[2] = 5-66
a constant plaintext symbol and p[1] = 66 - c[m][0] vary with the per-message
position-0 symbol — also consistent with the universal header, and (on clean
ground-truth pairs) genuinely NOT pure-progressive.
"""
from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

import isomorph as iso


def universal_positions(messages: Sequence[Sequence[int]]) -> List[Tuple[int, int]]:
    out = []
    L = min(len(m) for m in messages)
    for t in range(L):
        col = {m[t] for m in messages}
        if len(col) == 1:
            out.append((t, int(next(iter(col)))))
    return out


def autokey_header_reading(messages: Sequence[Sequence[int]], N: int) -> dict:
    p1 = [(int(m[1]) - int(m[0])) % N for m in messages]
    p2 = [(int(m[2]) - int(m[1])) % N for m in messages]
    return {"p1_per_message": p1, "p1_distinct": len(set(p1)),
            "p2_per_message": p2, "p2_constant": len(set(p2)) == 1,
            "p2_value": p2[0] if p2 else None}


def pure_progressive_contradictions(messages, pairs, N) -> Tuple[int, int]:
    """Chain isomorph pairs under PURE progressive x[D]-x[A] = (p2-p1) (no bases)."""
    gf = iso.GFSystem(N)
    con = tot = 0
    for pr in pairs:
        for i in range(pr.length):
            A = int(messages[pr.m1][pr.p1 + i])
            D = int(messages[pr.m2][pr.p2 + i])
            row: Dict[int, int] = {}
            row[D] = (row.get(D, 0) + 1) % N          # accumulate (A==D -> cancels)
            row[A] = (row.get(A, 0) + (N - 1)) % N
            row = {v: cc for v, cc in row.items() if cc}
            tot += 1
            if gf.add(row, (pr.p2 - pr.p1) % N) == "contradiction":
                con += 1
    return con, tot


# ---------------------------------------------------------------------------
# Selftest — prove the deduction on plants of known truth (clean ground-truth
# pairs, so contamination cannot confound).
# ---------------------------------------------------------------------------

def _clean_pairs(M, positions, L):
    inst = [(m, p) for m in range(M) for p in positions]
    out = []
    for a in range(len(inst)):
        for b in range(a + 1, len(inst)):
            (m1, p1), (m2, p2) = inst[a], inst[b]
            out.append(iso.IsoPair(m1, p1, m2, p2, L, False))
    return out


def _plant_progressive(N, rng, M, T, bases, header=(40, 41), wpos=(30, 60), wlen=12):
    C = list(rng.permutation(N))
    h1, h2 = header
    W = [int(x) for x in rng.integers(0, N, size=wlen)]
    for j in (0, 3, 6, 9):
        W[j] = (20 - j) % N
    msgs = []
    for m in range(M):
        p = [int(x) for x in rng.integers(0, N, size=T)]
        p[0] = (m * 7 + 3) % N
        p[1], p[2] = h1, h2
        for pos in wpos:
            p[pos:pos + wlen] = W
        msgs.append([C[(p[t] + bases[m] + t) % N] for t in range(T)])
    return msgs, C


def selftest() -> List[Tuple[str, bool]]:
    import numpy as np
    import chain_models as cm
    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(0)
    M, T = 9, 120
    wpos, wlen = (30, 60), 12

    # (1a) per-msg-prog + literal header + DIFFERENT bases -> header NOT universal
    diff = [int(x) for x in rng.integers(0, N, size=M)]
    while len(set(diff)) < M:
        diff = [int(x) for x in rng.integers(0, N, size=M)]
    md, _ = _plant_progressive(N, rng, M, T, diff, wpos=wpos, wlen=wlen)
    ud = [p for p, _ in universal_positions(md)]
    out.append(("per-msg-prog + literal header + DIFFERENT bases -> header NOT "
                "universal", 1 not in ud and 2 not in ud))

    # (1b) EQUAL bases -> header universal  (=> 'universal literal header' <=> equal bases)
    me, _ = _plant_progressive(N, rng, M, T, [17] * M, wpos=wpos, wlen=wlen)
    ue = [p for p, _ in universal_positions(me)]
    out.append(("per-msg-prog + literal header + EQUAL bases -> header universal",
                1 in ue and 2 in ue))

    # (2) equal-base corpus IS pure progressive: pure-prog on GROUND-TRUTH clean
    #     pairs has 0 contradictions.
    cp = _clean_pairs(M, wpos, wlen)
    con_e, tot_e = pure_progressive_contradictions(me, cp, N)
    out.append(("equal-base corpus IS pure progressive (0 contradictions on clean "
                "pairs)", con_e == 0 and tot_e > 0))

    # (3) autokey is genuinely NOT pure-progressive on clean pairs (discrimination)
    rng2 = np.random.default_rng(5)
    ak = cm.plant_autokey(N, rng2, M=M, T=T)
    cpa = cm.clean_pairs(M)              # ground-truth clean pairs for the plant word
    con_a, tot_a = pure_progressive_contradictions(ak, cpa, N)
    out.append(("autokey corpus CONTRADICTS pure progressive on clean pairs "
                "(genuinely not progressive)", con_a > 0))

    # (4) autokey header reading: p[2] constant, p[1] varies (constructed corpus)
    C2 = list(rng.permutation(N))
    akh = []
    for m in range(M):
        c = [(m * 9 + 5) % N, 66]            # per-message IV, then universal 66
        c.append((22 + c[1]) % N)            # p[2]=22 fixed -> c[2]=22+66 universal
        for t in range(3, T):
            c.append((int(rng.integers(0, N)) + c[t - 1]) % N)
        akh.append(c)
    uh = [p for p, _ in universal_positions(akh)]
    rd = autokey_header_reading(akh, N)
    out.append(("autokey + per-message IV -> header (1,2) universal naturally",
                1 in uh and 2 in uh))
    out.append(("autokey header reading: p[2] constant & p[1] varies",
                rd["p2_constant"] and rd["p1_distinct"] > 1))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} headerbase checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
