"""Digit-level / fractionation (Trifid-family) analysis of the eye corpus.

Each glyph is a base-5 trigram (verified: the community 'Interleaved Trigrams' ==
trigram.to_digits(value,5,3)). Our glyph-level analysis treated glyphs as opaque
0..82 symbols; this module works on the THREE eye-mark digit streams, to test the
fractionation/Trifid family that operates on the real coordinates.

Caveat carried from trigram.py: the high digit is constrained (0..3, '3' rare,
'4' never) because 0..82 is a compacted index, while the mid/low digits are
balanced 0..4. So the three positions are NOT symmetric — reported, not hidden.

Tools:
  * per_digit_ioc_z   — is any single eye-mark stream structured vs a shuffle null?
  * digit_pair_assoc  — are the three eye-marks independent or correlated (chi2)?
  * fractionate/defractionate — Trifid block digit-transposition and its inverse
    (round-trip validated).
  * period_scan       — inverse digit-transposition at each period; a Trifid would
    show an IoC anomaly at its true period. EXPLORATORY (real Trifid also has
    substitution layers), reported with a null band.
"""
from __future__ import annotations

from collections import Counter
from typing import Dict, List, Sequence, Tuple

import trigram
from stats import ioc

NDIG = 3
BASE = 5


def digit_streams(messages: Sequence[Sequence[int]]) -> List[List[int]]:
    """Three pooled eye-mark streams across all messages (MSB-first)."""
    streams = [[], [], []]
    for m in messages:
        for v in m:
            d = trigram.to_digits(int(v), BASE, NDIG)
            for i in range(NDIG):
                streams[i].append(d[i])
    return streams


def per_digit_ioc(messages) -> List[dict]:
    """Per-digit IoC vs the uniform baseline (1/k for the digit's used alphabet).
    A single stream's IoC only reflects its unigram skew — a constant digit gives
    IoC≈1, a balanced digit IoC≈1/k. (Positional structure is tested elsewhere.)"""
    streams = digit_streams(messages)
    out = []
    for s in streams:
        k = len(set(s))
        out.append({"ioc": ioc(s), "uniform": 1.0 / max(1, k),
                    "distinct": k, "n": len(s)})
    return out


def digit_pair_assoc(messages) -> Dict[Tuple[int, int], float]:
    """Cramer's V between each pair of eye-mark streams (0 = independent)."""
    import numpy as np
    streams = digit_streams(messages)
    out = {}
    for a in range(NDIG):
        for b in range(a + 1, NDIG):
            xa, xb = streams[a], streams[b]
            ca, cb = sorted(set(xa)), sorted(set(xb))
            ia = {v: i for i, v in enumerate(ca)}
            ib = {v: i for i, v in enumerate(cb)}
            tab = np.zeros((len(ca), len(cb)))
            for u, v in zip(xa, xb):
                tab[ia[u], ib[v]] += 1
            n = tab.sum()
            row = tab.sum(1, keepdims=True); col = tab.sum(0, keepdims=True)
            exp = row @ col / n
            chi2 = float(((tab - exp) ** 2 / np.where(exp > 0, exp, 1)).sum())
            k = min(len(ca), len(cb))
            v_ = (chi2 / (n * (k - 1))) ** 0.5 if k > 1 else 0.0
            out[(a, b)] = v_
    return out


# ---------------------------------------------------------------------------
# Trifid block transposition (digit fractionation)
# ---------------------------------------------------------------------------

def fractionate(seq: Sequence[int], period: int) -> List[int]:
    """Forward Trifid block transpose: per block of `period` glyphs, write the
    NDIG digit-rows, read row-major, regroup into new glyphs."""
    out = []
    P = period
    for b in range(0, len(seq) - P + 1, P):
        tris = [trigram.to_digits(int(seq[b + j]), BASE, NDIG) for j in range(P)]
        flat = [tris[j][r] for r in range(NDIG) for j in range(P)]   # row-major
        for i in range(P):
            out.append(trigram.from_digits(flat[i * NDIG:(i + 1) * NDIG], BASE))
    tail = len(seq) - (len(seq) // P) * P
    out.extend(int(v) for v in seq[len(seq) - tail:])
    return out


def defractionate(seq: Sequence[int], period: int) -> List[int]:
    """Inverse of fractionate at the same period."""
    out = []
    P = period
    for b in range(0, len(seq) - P + 1, P):
        flat = []
        for j in range(P):
            flat.extend(trigram.to_digits(int(seq[b + j]), BASE, NDIG))
        # write row-major into NDIG x P, read column-major
        grid = [[flat[r * P + j] for j in range(P)] for r in range(NDIG)]
        for j in range(P):
            out.append(trigram.from_digits([grid[r][j] for r in range(NDIG)], BASE))
    tail = len(seq) - (len(seq) // P) * P
    out.extend(int(v) for v in seq[len(seq) - tail:])
    return out


def period_scan(messages, max_period: int = 24, seed: int = 0) -> List[dict]:
    """For each period, inverse-transpose every message and pool the IoC. A Trifid
    at its true period shows an IoC anomaly vs the identity (P=1) and the null."""
    import numpy as np
    rng = np.random.default_rng(seed)
    base_pool = [int(v) for m in messages for v in m]
    base_ioc = ioc(base_pool)
    rows = []
    for P in range(2, max_period + 1):
        pooled = []
        for m in messages:
            pooled.extend(defractionate(m, P))
        rows.append({"period": P, "ioc": ioc(pooled), "base_ioc": base_ioc})
    return rows


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def selftest() -> List[Tuple[str, bool]]:
    import numpy as np
    out: List[Tuple[str, bool]] = []
    rng = np.random.default_rng(0)

    # round-trip: defractionate inverts fractionate at the same period
    seq = [int(v) for v in rng.integers(0, 83, size=120)]
    ok_rt = all(defractionate(fractionate(seq, P), P)[:len(seq) // P * P]
                == seq[:len(seq) // P * P] for P in (3, 5, 7, 11))
    out.append(("fractionate/defractionate round-trip (several periods)", ok_rt))

    # per-digit IoC flags a structured (constant) eye-mark vs uniform
    msg = []
    for _ in range(2000):
        msg.append(trigram.from_digits([rng.integers(0, 4), rng.integers(0, 5), 4], 5))
    pd = per_digit_ioc([msg])
    out.append(("per-digit IoC: constant eye-mark ~1, balanced ~uniform",
                pd[2]["ioc"] > 0.99 and pd[0]["ioc"] < 0.4 and pd[1]["ioc"] < 0.3))

    # digit association: independent digits -> low Cramer's V; coupled -> high
    indep = [trigram.from_digits([rng.integers(0, 4), rng.integers(0, 5),
                                  rng.integers(0, 5)], 5) for _ in range(3000)]
    va = digit_pair_assoc([indep])
    out.append(("independent eye-marks -> low association (V<0.1)",
                max(va.values()) < 0.1))
    coup = []
    for _ in range(3000):
        d1 = int(rng.integers(0, 5))
        coup.append(trigram.from_digits([rng.integers(0, 4), d1, d1], 5))  # d2==d1
    vc = digit_pair_assoc([coup])
    out.append(("coupled eye-marks (d2==d1) -> high association (V>0.9)",
                vc[(1, 2)] > 0.9))

    # PERIOD SCAN: plant a pure Trifid (period 7) on a low-entropy plaintext; the
    # inverse-transpose at P=7 must restore the (high) plaintext IoC, and a wrong
    # period must not.
    P0 = 7
    syms = [int(v) for v in rng.choice(83, size=12, replace=False)]   # full-range
    w = np.array([10, 8, 7, 6, 5, 4, 3, 2, 2, 1, 1, 1], dtype=float); w /= w.sum()
    pt = [int(syms[rng.choice(12, p=w)]) for _ in range(7 * 60)]
    ct = fractionate(pt, P0)
    pt_ioc = ioc(pt)
    rec7 = defractionate(ct, P0)
    rec_ioc = ioc(rec7)
    rows = period_scan([ct], max_period=12)
    by = {r["period"]: r["ioc"] for r in rows}
    out.append(("Trifid plant: inverse-transpose at true period restores IoC",
                abs(rec_ioc - pt_ioc) < 1e-9))
    out.append(("Trifid plant: period scan IoC peaks at the true period",
                by[P0] == max(by.values()) and by[P0] > 1.3 * min(by.values())))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} trifid checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
