"""Falsifiable model verification for the refrain's cipher structure.

Before trusting the refrain template (dof=2, forced-same groups) we must confirm
the per-message-progressive model is REAL, not coincidental over-fit. The
falsifiable test:

  Under per-message-progressive c[m][t]=C[(p[t]+base_m+t)], if the 4 refrain
  instances are the SAME plaintext, an all-distinct crib stays GF-consistent over
  the whole refrain (no contradiction). The depth at which consistency breaks
  measures how much shared structure exists.

We compare three things:
  1. PER-MESSAGE-PROGRESSIVE consistent extent of the real refrain.
  2. PURE-PROGRESSIVE (no per-message base) consistent extent of the same window
     — a strictly stronger model; if the data needed the per-message base, pure
     fails far sooner.
  3. NULL: the per-message-progressive consistent extent of RANDOM 4-window sets
     (unrelated positions). If the refrain's extent is deep into the null's tail,
     the shared structure is real (p-value).

HONEST RESULT (real corpus): the refrain is per-message-progressive-consistent to
L=22, which is only modestly rare (empirical p ~ 0.003-0.006: a small fraction of
random 4-windows also reach L=22), pure-progressive reaches nearly as far (21 vs
22), and random windows that DO pass have as much/more over-determination. So these
consistency tests do NOT cleanly confirm per-message-progressive over alternatives;
the model is a flexible fit. What IS solid is that the 4 instances are the SAME
plaintext (isomorph significance z>100, see `isomorph`). Treat the dof=2 refrain
template as a model-DEPENDENT hypothesis, not a proven fact.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from isomorph import GFSystem

_ALPHA = ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
          "0123456789!@#$%^&*()_+-=[]")   # >= any L we use, all distinct


def consistent_extent(messages, instances, N, per_message: bool = True,
                      max_len: int = 30) -> int:
    """Max L for which an all-distinct crib is GF-consistent over `instances`
    under per-message-progressive (per_message=True) or pure-progressive (False)."""
    msgs = sorted({m for m, _ in instances})
    minlen = min(len(messages[m]) for m, _ in instances)
    best = 0
    for L in range(3, min(max_len, minlen - max(p for _, p in instances)) + 1):
        gf = GFSystem(N)
        bvar = {m: L + j for j, m in enumerate(msgs)}
        xbase = L + len(msgs)
        if per_message:
            gf.add({bvar[msgs[0]]: 1}, 0)            # gauge first base
        ok = True
        for (m, pos) in instances:
            for i in range(L):
                c = int(messages[m][pos + i])
                row = {xbase + c: 1, i: N - 1}
                if per_message:
                    row[bvar[m]] = (row.get(bvar[m], 0) + (N - 1)) % N
                row = {v: cc % N for v, cc in row.items() if cc % N}
                if gf.add(row, (pos + i) % N) == "contradiction":
                    ok = False
                    break
            if not ok:
                break
        if ok:
            best = L
        else:
            break
    return best


@dataclass
class ModelAudit:
    refrain_permsg: int
    refrain_pure: int
    null_mean: float
    null_sd: float
    null_max: int
    p_value: float                 # empirical P(null extent >= refrain extent)
    z: float
    n_null: int


def audit(messages, region, N, n_null: int = 300, seed: int = 0,
          max_len: int = 30) -> ModelAudit:
    import numpy as np
    permsg = consistent_extent(messages, region, N, True, max_len)
    pure = consistent_extent(messages, region, N, False, max_len)
    rng = np.random.default_rng(seed)
    n_msgs = len(messages)
    nulls = []
    for _ in range(n_null):
        a, b = [int(x) for x in rng.choice(n_msgs, 2, replace=False)]
        la, lb = len(messages[a]), len(messages[b])
        pa = [int(rng.integers(0, max(1, la - max_len))) for _ in range(2)]
        pb = [int(rng.integers(0, max(1, lb - max_len))) for _ in range(2)]
        reg = [(a, pa[0]), (a, pa[1]), (b, pb[0]), (b, pb[1])]
        nulls.append(consistent_extent(messages, reg, N, True, max_len))
    nulls = np.array(nulls)
    nm, nsd = float(nulls.mean()), float(nulls.std())
    p = float((nulls >= permsg).mean())
    return ModelAudit(permsg, pure, nm, nsd, int(nulls.max()), p,
                      (permsg - nm) / (nsd + 1e-9), n_null)


# ---------------------------------------------------------------------------
# Selftest — validate the method discriminates models on plants.
# ---------------------------------------------------------------------------

def selftest() -> List[Tuple[str, bool]]:
    import numpy as np
    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(0)
    C = list(rng.permutation(N))
    T = 120
    refrain = [int(v) for v in rng.permutation(N)[:24]]
    region = [(0, 30), (0, 62), (1, 35), (1, 70)]

    # (A) PER-MESSAGE-progressive plant (distinct per-message bases). per-message
    #     extent should reach the refrain length; pure should fall SHORT.
    bases = [7, 41]
    while bases[0] == bases[1]:
        bases = [int(b) for b in rng.integers(0, N, size=2)]
    msgs = [[], []]
    for m in range(2):
        p = [int(rng.integers(0, N)) for _ in range(T)]
        for (mm, pos) in region:
            if mm == m:
                p[pos:pos + len(refrain)] = refrain
        msgs[m] = [C[(p[t] + bases[m] + t) % N] for t in range(T)]
    a = audit(msgs, region, N, n_null=120)
    out.append(("per-msg plant: per-message extent reaches the refrain (>=20)",
                a.refrain_permsg >= 20))
    out.append(("per-msg plant: pure-progressive falls SHORT (< per-message)",
                a.refrain_pure < a.refrain_permsg))
    out.append(("per-msg plant: refrain extent beyond the null (empirical p<0.02)",
                a.p_value < 0.02))

    # (B) PURE-progressive plant (all bases equal). pure should reach refrain too.
    msgs2 = [[], []]
    for m in range(2):
        p = [int(rng.integers(0, N)) for _ in range(T)]
        for (mm, pos) in region:
            if mm == m:
                p[pos:pos + len(refrain)] = refrain
        msgs2[m] = [C[(p[t] + 0 + t) % N] for t in range(T)]   # base 0 for all
    pure2 = consistent_extent(msgs2, region, N, False)
    out.append(("pure plant: pure-progressive reaches the refrain (>=20)",
                pure2 >= 20))

    # (C) NULL behaves: random unrelated windows have SHORT extent
    out.append(("null windows have short extent (mean << refrain)",
                a.null_mean < 0.5 * a.refrain_permsg))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} model_audit checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
