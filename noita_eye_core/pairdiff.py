"""Pair-difference / edit-structure analysis.

The robust, assumption-light finding from the structure work: inside a triplet the
strongest signal is a **near-duplicate pair** of messages (e.g. East1 ~ West1 agree
on ~44% of positions) plus a **divergent third**.  Under the per-triplet shared
keystream, equal ciphertext == equal plaintext, so the pair are near-copies of the
same plaintext and their *difference* is "mostly zeros plus scattered edits".

This module characterises that precisely, without assuming the combiner is additive
or that the plaintext is language:

* which two messages form the near-duplicate pair (highest body agreement) and
  which is the odd one out;
* the agreement fraction vs the "unrelated in-depth" baseline (significance);
* the **edit structure**: are the differing positions clustered (block edits) or
  scattered (Wald-Wolfowitz runs test), and do the *difference values* at edits
  carry structure (a possible diff-encoded payload) or look uniform?

Everything here is keystream-free (it only compares ciphertexts), so it stands
regardless of whether we ever recover a key.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from itertools import combinations
from typing import List, Optional, Sequence, Tuple

import numpy as np

import corpus as corpus_mod
from stats import ioc_normalised

TRIPLETS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))


def _equal_positions(a: Sequence[int], b: Sequence[int], start: int = 0
                     ) -> Tuple[int, int]:
    L = min(len(a), len(b))
    eq = sum(1 for t in range(start, L) if a[t] == b[t])
    return eq, max(0, L - start)


def _runs_z(binary: Sequence[int]) -> float:
    """Wald-Wolfowitz runs-test z for a 0/1 sequence.  Negative z => fewer runs
    than chance => clustering of like values (block edits)."""
    n = len(binary)
    n1 = sum(binary)
    n0 = n - n1
    if n1 == 0 or n0 == 0 or n < 2:
        return 0.0
    runs = 1 + sum(1 for i in range(1, n) if binary[i] != binary[i - 1])
    mu = 2 * n1 * n0 / n + 1
    var = (2 * n1 * n0 * (2 * n1 * n0 - n)) / (n * n * (n - 1))
    if var <= 0:
        return 0.0
    return (runs - mu) / math.sqrt(var)


@dataclass
class PairStat:
    i: int
    j: int
    overlap: int
    body_overlap: int
    full_frac: float
    body_frac: float
    zero_frac_body: float          # = body_frac (kept for clarity)
    edit_count_body: int
    edit_value_ioc: float          # IoC*N of (a-b) at body edit positions
    edit_runs_z: float             # <0 clustered, ~0 scattered


@dataclass
class TripletDiff:
    triplet: Tuple[int, ...]
    pair: Tuple[int, int]
    odd: int
    pair_stat: PairStat
    baseline_frac: float           # mean body agreement of NON-pair couples
    z_vs_baseline: float
    verdict: str


def analyze_pair(a: Sequence[int], b: Sequence[int], N: int,
                 body_start: int = 0) -> PairStat:
    L = min(len(a), len(b))
    eq_full, ov_full = _equal_positions(a, b, 0)
    eq_body, ov_body = _equal_positions(a, b, body_start)
    body = list(range(body_start, L))
    binary = [1 if a[t] == b[t] else 0 for t in body]
    edits = [t for t in body if a[t] != b[t]]
    edit_vals = [(a[t] - b[t]) % N for t in edits]
    return PairStat(
        i=-1, j=-1, overlap=ov_full, body_overlap=ov_body,
        full_frac=eq_full / ov_full if ov_full else 0.0,
        body_frac=eq_body / ov_body if ov_body else 0.0,
        zero_frac_body=eq_body / ov_body if ov_body else 0.0,
        edit_count_body=len(edits),
        edit_value_ioc=ioc_normalised(edit_vals, N) if len(edit_vals) >= 2 else 0.0,
        edit_runs_z=_runs_z(binary),
    )


def analyze_triplet(messages: Sequence[Sequence[int]], triplet: Sequence[int],
                    N: int, body_start: int = 0,
                    baseline_rate: Optional[float] = None) -> TripletDiff:
    couples = list(combinations(triplet, 2))
    stats = {}
    for (i, j) in couples:
        ps = analyze_pair(messages[i], messages[j], N, body_start)
        ps.i, ps.j = i, j
        stats[(i, j)] = ps
    # The pair = couple with the highest body agreement.
    (pi, pj), best = max(stats.items(), key=lambda kv: kv[1].body_frac)
    odd = next(m for m in triplet if m not in (pi, pj))
    others = [s.body_frac for k, s in stats.items() if k != (pi, pj)]
    baseline = float(np.mean(others)) if others else 0.0

    # Significance vs the CHANCE / depth baseline for two *unrelated* in-depth
    # messages (keystream-scope showed body cross-pair agreement ~ 1/N), NOT vs
    # the sibling couples -- comparing the max-of-three to its siblings would be
    # selection-biased.  A Bonferroni factor of 3 covers the max-of-3 pick.
    q = min(max(baseline_rate if baseline_rate is not None else 1.0 / N,
                1e-9), 1 - 1e-9)
    n = best.body_overlap
    sd = math.sqrt(q * (1 - q) / n) if n else 0.0
    z = (best.body_frac - q) / sd if sd > 0 else 0.0

    edit_desc = ("clustered" if best.edit_runs_z < -2 else
                 "scattered" if abs(best.edit_runs_z) <= 2 else "dispersed")
    payload = ("structured edit-values (IoC*N="
               f"{best.edit_value_ioc:.2f})" if best.edit_value_ioc > 1.5
               else f"uniform edit-values (IoC*N={best.edit_value_ioc:.2f})")
    verdict = (f"near-duplicate pair ({pi},{pj}) body-agree {best.body_frac:.0%} "
               f"vs baseline {baseline:.0%} (z={z:.1f}); odd one = {odd}; "
               f"{best.edit_count_body} edits, {edit_desc}; {payload}")

    return TripletDiff(triplet=tuple(triplet), pair=(pi, pj), odd=odd,
                       pair_stat=best, baseline_frac=baseline, z_vs_baseline=z,
                       verdict=verdict)


def analyze_corpus(c: corpus_mod.Corpus, body_start: int = 25,
                   partition=TRIPLETS) -> List[TripletDiff]:
    messages = [list(ct) for ct in c.ciphertexts]
    return [analyze_triplet(messages, t, c.N, body_start) for t in partition]


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def selftest() -> List[tuple[str, bool]]:
    out: List[tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(53)
    T = 120

    # Plant: shared key; members 0,1 are near-duplicate plaintext (E scattered
    # edits); member 2 is a different plaintext.  Detect the pair + odd + edits.
    K = rng.integers(0, N, size=T)
    base_plain = rng.integers(0, N, size=T)
    p0 = base_plain.copy()
    p1 = base_plain.copy()
    n_edits = 18
    edit_pos = rng.choice(T, size=n_edits, replace=False)
    for t in edit_pos:
        p1[t] = (p1[t] + 1 + rng.integers(0, N - 1)) % N   # guaranteed change
    p2 = rng.integers(0, N, size=T)
    msgs = [[(int(p[t]) + int(K[t])) % N for t in range(T)] for p in (p0, p1, p2)]
    td = analyze_triplet(msgs, (0, 1, 2), N, body_start=0)
    out.append(("identifies the near-duplicate pair (0,1)", td.pair == (0, 1)))
    out.append(("identifies the odd member (2)", td.odd == 2))
    out.append(("pair agreement is highly significant", td.z_vs_baseline > 5))
    out.append(("recovers ~the planted edit count",
                abs(td.pair_stat.edit_count_body - n_edits) <= 3))

    # Control: all three independent -> no pair stands out (low z).
    ind = [rng.integers(0, N, size=T).tolist() for _ in range(3)]
    cipher = [[(ind[k][t] + int(K[t])) % N for t in range(T)] for k in range(3)]
    tc = analyze_triplet(cipher, (0, 1, 2), N, body_start=0)
    out.append(("no spurious pair when all independent", tc.z_vs_baseline < 4))

    # Structured edit-values: all edits add a CONSTANT -> edit_value_ioc high.
    p1b = base_plain.copy()
    for t in edit_pos:
        p1b[t] = (p1b[t] + 7) % N           # constant edit
    msgs_b = [[(int(p[t]) + int(K[t])) % N for t in range(T)]
              for p in (base_plain, p1b, p2)]
    tb = analyze_triplet(msgs_b, (0, 1, 2), N, body_start=0)
    out.append(("structured (constant) edit-values flagged",
                tb.pair_stat.edit_value_ioc > 5))

    # Clustering: edits in one contiguous block -> runs z strongly negative.
    p1c = base_plain.copy()
    for t in range(40, 58):
        p1c[t] = (p1c[t] + 3) % N
    msgs_c = [[(int(p[t]) + int(K[t])) % N for t in range(T)]
              for p in (base_plain, p1c, p2)]
    tcl = analyze_triplet(msgs_c, (0, 1, 2), N, body_start=0)
    out.append(("clustered edits detected (runs z < -2)",
                tcl.pair_stat.edit_runs_z < -2))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} pairdiff checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
