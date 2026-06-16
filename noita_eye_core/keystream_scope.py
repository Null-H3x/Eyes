"""Keystream scope — one global keystream, or one per triplet?

EyeWitness established the messages group as triplets and that they are in depth.
But *depth* was measured by pooling all 36 message pairs.  That leaves a decisive
open question for EyeCrack's aim:

* **GLOBAL keystream:** a single position keystream ``K[t]`` shared by all nine
  messages.  Then *every* pair — within a triplet AND across triplets — satisfies
  ``c_i[t] - c_j[t] == p_i[t] - p_j[t]`` (the key cancels), so cross-triplet pairs
  also show an elevated difference-IoC.
* **PER-TRIPLET keystreams:** each triplet ``g`` has its own ``K_g[t]``.  Then
  within-triplet pairs still cancel (same ``K_g``), but a cross-triplet pair keeps
  a leftover: ``c_i - c_j == (p_i - p_j) + (K_g - K_h)``.  If the per-triplet
  keystreams are unrelated, ``K_g - K_h`` is ~uniform, so the cross-triplet
  difference-IoC collapses to the ``1/N`` baseline.

So the test is simply: **is the cross-triplet difference-IoC elevated (global) or at
the uniform baseline (per-triplet)?**, with the within-triplet difference-IoC as the
positive control.

Confound control.  Triplets share long *identical openings* and there is a
universal 2-symbol header, which inflate difference-IoC near the start for both
within- and cross-triplet pairs.  The verdict is therefore taken on the message
**body** (positions ``>= body_start``, stripping the opening zone) as well as the
full overlap, so a "global" verdict cannot be an artifact of shared preambles.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import List, Optional, Sequence, Tuple

import numpy as np

import corpus as corpus_mod
from null_model import Significance, significance
from stats import ioc

Partition = Tuple[Tuple[int, ...], ...]
TRIPLETS: Partition = ((0, 1, 2), (3, 4, 5), (6, 7, 8))


def _pair_diff_ioc(a: Sequence[int], b: Sequence[int], N: int,
                   start: int = 0) -> Optional[float]:
    L = min(len(a), len(b))
    d = [(a[t] - b[t]) % N for t in range(start, L)]
    return ioc(d) if len(d) >= 2 else None


def _mean_diff_ioc(messages: Sequence[Sequence[int]],
                   pairs: Sequence[Tuple[int, int]], N: int,
                   start: int = 0) -> float:
    vals = [v for (i, j) in pairs
            if (v := _pair_diff_ioc(messages[i], messages[j], N, start)) is not None]
    return float(np.mean(vals)) if vals else 0.0


def _within_pairs(partition: Partition) -> set:
    s = set()
    for g in partition:
        for a, b in combinations(sorted(g), 2):
            s.add((a, b))
    return s


@dataclass
class ScopeReport:
    body_start: int
    within_mean: float
    cross_mean: float
    uniform_baseline: float
    within_sig: Significance
    cross_sig: Significance
    n_within: int
    n_cross: int
    verdict: str


def scope_report(messages: Sequence[Sequence[int]], N: int,
                 partition: Partition = TRIPLETS, body_start: int = 0,
                 n_null: int = 500, seed: int = 0) -> ScopeReport:
    """Within- vs cross-group difference-IoC, each vs a within-message-shuffle
    null, on positions ``>= body_start``."""
    n = len(messages)
    within = _within_pairs(partition)
    all_pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    within_pairs = [p for p in all_pairs if p in within]
    cross_pairs = [p for p in all_pairs if p not in within]

    obs_within = _mean_diff_ioc(messages, within_pairs, N, body_start)
    obs_cross = _mean_diff_ioc(messages, cross_pairs, N, body_start)

    rng = np.random.default_rng(seed)
    arrs = [np.asarray(m) for m in messages]
    null_within: List[float] = []
    null_cross: List[float] = []
    for _ in range(n_null):
        sh = [rng.permutation(a).tolist() for a in arrs]
        null_within.append(_mean_diff_ioc(sh, within_pairs, N, body_start))
        null_cross.append(_mean_diff_ioc(sh, cross_pairs, N, body_start))

    within_sig = significance(obs_within, null_within, tail="greater")
    cross_sig = significance(obs_cross, null_cross, tail="greater")

    # Verdict.  Within is the positive control (must be in depth at all).
    if within_sig.z < 5:
        verdict = "INCONCLUSIVE (within-triplet depth not significant here)"
    elif cross_sig.z >= 5:
        verdict = ("GLOBAL keystream — cross-triplet pairs are ALSO in depth "
                   f"(cross z={cross_sig.z:.1f}); one keystream spans all nine")
    elif cross_sig.z < 3:
        verdict = ("PER-TRIPLET keystreams — only within-triplet pairs are in "
                   f"depth (cross z={cross_sig.z:.1f}, at the uniform baseline); "
                   "each triplet has its own keystream")
    else:
        verdict = (f"AMBIGUOUS — cross z={cross_sig.z:.1f} sits between thresholds "
                   "(partial sharing or underpowered)")

    return ScopeReport(body_start=body_start, within_mean=obs_within,
                       cross_mean=obs_cross, uniform_baseline=1.0 / N,
                       within_sig=within_sig, cross_sig=cross_sig,
                       n_within=len(within_pairs), n_cross=len(cross_pairs),
                       verdict=verdict)


# ---------------------------------------------------------------------------
# Selftest — planted global vs planted per-triplet keystreams
# ---------------------------------------------------------------------------

def _zipf(k: int, N: int, T: int, rng: np.random.Generator) -> np.ndarray:
    w = np.zeros(N)
    w[:k] = 1.0 / np.arange(1, k + 1)
    w /= w.sum()
    return rng.choice(N, size=T, p=w)


def selftest() -> List[tuple[str, bool]]:
    out: List[tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(41)
    T = 120

    # (1) GLOBAL: one keystream for all nine.
    Kg = rng.integers(0, N, size=T)
    plains = [_zipf(30, N, T, rng) for _ in range(9)]
    glob = [[(int(plains[i][t]) + int(Kg[t])) % N for t in range(T)]
            for i in range(9)]
    rg = scope_report(glob, N, n_null=300, seed=1)
    out.append(("GLOBAL: cross-triplet pairs are in depth (z>5)",
                rg.cross_sig.z > 5))
    out.append(("GLOBAL: verdict says GLOBAL", rg.verdict.startswith("GLOBAL")))

    # (2) PER-TRIPLET: independent keystream per triplet.
    Ks = [rng.integers(0, N, size=T) for _ in range(3)]
    per = []
    for gi, g in enumerate(TRIPLETS):
        for m in g:
            p = _zipf(30, N, T, rng)
            per.append((m, [(int(p[t]) + int(Ks[gi][t])) % N for t in range(T)]))
    per.sort(key=lambda x: x[0])
    per_msgs = [c for _, c in per]
    rp = scope_report(per_msgs, N, n_null=300, seed=2)
    out.append(("PER-TRIPLET: within-triplet pairs in depth (z>5)",
                rp.within_sig.z > 5))
    out.append(("PER-TRIPLET: cross-triplet pairs NOT in depth (z<3)",
                rp.cross_sig.z < 3))
    out.append(("PER-TRIPLET: verdict says PER-TRIPLET",
                rp.verdict.startswith("PER-TRIPLET")))

    # (3) PER-TRIPLET keys + a SHARED opening across all nine (the real-corpus
    #     trap): full overlap falsely reads GLOBAL, the body correctly reads
    #     PER-TRIPLET.  This validates the confound control.
    O = 20
    shared_open = rng.integers(0, N, size=O)
    per2 = []
    for gi, g in enumerate(TRIPLETS):
        for m in g:
            p = _zipf(30, N, T, rng)
            c = [(int(p[t]) + int(Ks[gi][t])) % N for t in range(T)]
            c[:O] = [int(x) for x in shared_open]   # identical preamble for ALL
            per2.append((m, c))
    per2.sort(key=lambda x: x[0])
    msgs2 = [c for _, c in per2]
    r_full = scope_report(msgs2, N, body_start=0, n_null=300, seed=3)
    r_body = scope_report(msgs2, N, body_start=O, n_null=300, seed=4)
    out.append(("shared-opening trap: full overlap is fooled (GLOBAL)",
                r_full.cross_sig.z > 5))
    out.append(("shared-opening trap: BODY recovers the truth (PER-TRIPLET)",
                r_body.verdict.startswith("PER-TRIPLET")))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} keystream_scope checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
