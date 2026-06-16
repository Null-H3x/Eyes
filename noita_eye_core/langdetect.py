"""Key-free structure / language profiler.

The existential question that gates everything downstream: **is there detectable
linguistic (or any non-random) structure here at all?**  We cannot decrypt, but we
can measure structure in *key-free* observables — the raw ciphertexts and the
within-triplet pair *difference* streams (under an additive combiner, a difference
is the difference of two plaintexts, computable with no key).

Three complementary, language-agnostic metrics, each against an appropriate null:

* **unigram non-uniformity** — IoC*N vs a uniform-random null (detects a peaked
  symbol distribution; for a difference of near-duplicates this fires on the
  zero-spike, i.e. *duplication*, which is structure but not necessarily language);
* **order predictability** — ``H(X) - H(X | prev)`` vs a *shuffle* null
  (shuffling preserves the marginal and destroys order, so it calibrates the
  small-sample bias; positive = the next symbol is predictable from the previous,
  the signature of language);
* **compressibility** — zlib savings vs a shuffle null.

Honesty about power (critical — read before trusting a negative)
----------------------------------------------------------------
A *null* result here does NOT exclude linguistic plaintext.  Under an aperiodic
keystream the difference of two natural-language texts can itself be near-flat
(order structure washes out), so language can be present and invisible to these
key-free metrics.  This profiler reports what is *measurable*; only a crib or the
key can settle the question definitively.  The selftest proves the metrics
*discriminate* structured from random text when structure is directly present.
"""
from __future__ import annotations

import math
import zlib
from collections import Counter
from dataclasses import dataclass
from typing import List, Optional, Sequence

import numpy as np

from stats import ioc_normalised


def order_predictability(seq: Sequence[int], add_k: float = 0.5) -> float:
    """``H(X) - H(X | prev)`` in bits (>= 0).  ~0 for orderless data, positive
    when the next symbol is predictable from the previous one."""
    n = len(seq)
    if n < 3:
        return 0.0
    uni = Counter(seq)
    H_uni = -sum((cnt / n) * math.log2(cnt / n) for cnt in uni.values())
    # Conditional entropy H(X|prev) with add-k smoothing over observed contexts.
    ctx: dict = {}
    for a, b in zip(seq[:-1], seq[1:]):
        ctx.setdefault(a, Counter())[b] += 1
    total_pairs = n - 1
    H_cond = 0.0
    for a, dist in ctx.items():
        ca = sum(dist.values())
        k = len(dist)
        denom = ca + add_k * k
        h = -sum(((cnt + add_k) / denom) * math.log2((cnt + add_k) / denom)
                 for cnt in dist.values())
        H_cond += (ca / total_pairs) * h
    return max(0.0, H_uni - H_cond)


def compress_savings(seq: Sequence[int]) -> float:
    if not seq:
        return 0.0
    raw = bytes(int(x) & 0xFF for x in seq)
    comp = zlib.compress(raw, 9)
    return 1.0 - len(comp) / len(raw)


@dataclass
class StructResult:
    label: str
    n: int
    ioc_n: float
    ioc_z: float
    predictability: float
    predictability_z: float
    compress_savings: float
    compress_z: float
    mode_frac: float                 # fraction of the single most common symbol
    residual_pred_z: float           # order structure AFTER removing that symbol
    verdict: str


def _z(obs: float, null: Sequence[float]) -> float:
    arr = np.asarray(null, dtype=float)
    sd = arr.std(ddof=1)
    return float((obs - arr.mean()) / sd) if sd > 0 else 0.0


def analyze(seq: Sequence[int], N: int, label: str = "", n_null: int = 300,
            rng: Optional[np.random.Generator] = None) -> StructResult:
    rng = rng or np.random.default_rng(0)
    seq = list(seq)
    n = len(seq)

    ioc_obs = ioc_normalised(seq, N)
    pred_obs = order_predictability(seq)
    comp_obs = compress_savings(seq)

    # IoC null: uniform random (shuffle would preserve the marginal -> useless).
    ioc_null = [ioc_normalised(rng.integers(0, N, size=n).tolist(), N)
                for _ in range(n_null)]
    # Order-metric nulls: shuffle (preserve marginal, destroy order).
    arr = np.asarray(seq)
    pred_null, comp_null = [], []
    for _ in range(n_null):
        rng.shuffle(arr)
        sh = arr.tolist()
        pred_null.append(order_predictability(sh))
        comp_null.append(compress_savings(sh))

    ioc_z = _z(ioc_obs, ioc_null)
    pred_z = _z(pred_obs, pred_null)
    comp_z = _z(comp_obs, comp_null)

    # Duplication guard: if one symbol dominates, any "order structure" is likely
    # that peak (and its clustering), not language.  Re-test order on the residual
    # (the sequence with the dominant symbol removed).
    cnt = Counter(seq)
    mode_sym, mode_cnt = cnt.most_common(1)[0]
    mode_frac = mode_cnt / n if n else 0.0
    residual = [s for s in seq if s != mode_sym]
    res_pred_z = 0.0
    if len(residual) >= 30:
        rp_obs = order_predictability(residual)
        ra = np.asarray(residual)
        rp_null = []
        for _ in range(n_null):
            rng.shuffle(ra)
            rp_null.append(order_predictability(ra.tolist()))
        res_pred_z = _z(rp_obs, rp_null)

    order = pred_z > 5 or comp_z > 5
    unigram = ioc_z > 5
    dominated = mode_frac > 0.10        # >> uniform 1/N for these alphabets
    if order and dominated and res_pred_z <= 5:
        verdict = (f"order structure attributable to a dominant symbol "
                   f"(mode_frac={mode_frac:.0%}, duplication/clustering); residual "
                   f"is orderless (z={res_pred_z:.1f}) — NOT language")
    elif order and (not dominated or res_pred_z > 5):
        verdict = "ORDER structure present (language-like sequential dependence)"
    elif unigram:
        verdict = ("UNIGRAM structure only (peaked distribution / duplication) — "
                   "not sequential; not necessarily language")
    else:
        verdict = ("no key-free structure detected (NOTE: does not exclude "
                   "language — differences can hide it under an aperiodic key)")
    return StructResult(label=label, n=n, ioc_n=ioc_obs, ioc_z=ioc_z,
                        predictability=pred_obs, predictability_z=pred_z,
                        compress_savings=comp_obs, compress_z=comp_z,
                        mode_frac=mode_frac, residual_pred_z=res_pred_z,
                        verdict=verdict)


# ---------------------------------------------------------------------------
# Selftest — the metrics must DISCRIMINATE structure from randomness
# ---------------------------------------------------------------------------

def _markov(N: int, T: int, rng: np.random.Generator) -> List[int]:
    bi = np.zeros((N, N))
    for a in range(N):
        row = rng.random(N) ** 6
        row[(a + 1) % N] += 6.0
        bi[a] = row / row.sum()
    s = int(rng.integers(0, N))
    out = [s]
    for _ in range(T - 1):
        s = int(rng.choice(N, p=bi[s]))
        out.append(s)
    return out


def selftest() -> List[tuple[str, bool]]:
    out: List[tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(61)

    # (1) Markov text: ORDER structure must be detected.
    text = _markov(N, 1500, rng)
    r = analyze(text, N, "markov", n_null=200, rng=np.random.default_rng(1))
    out.append(("Markov text -> order structure detected",
                r.predictability_z > 5 or r.compress_z > 5))

    # (2) Uniform random: NO structure on any axis.
    uni = rng.integers(0, N, size=1500).tolist()
    ru = analyze(uni, N, "uniform", n_null=200, rng=np.random.default_rng(2))
    out.append(("uniform -> no order structure",
                ru.predictability_z < 5 and ru.compress_z < 5))
    out.append(("uniform -> no unigram structure", ru.ioc_z < 5))

    # (3) Duplication difference (mostly zeros, scattered): UNIGRAM structure
    #     (peaked at 0) but NOT order structure -> must be distinguished.
    dup = rng.integers(0, N, size=1500)
    mask = rng.random(1500) < 0.3
    diff = np.where(mask, dup, 0).tolist()       # 70% zeros, 30% random
    rd = analyze(diff, N, "dup", n_null=200, rng=np.random.default_rng(3))
    out.append(("duplication diff -> unigram structure flagged", rd.ioc_z > 5))
    out.append(("duplication diff -> verdict does NOT claim language",
                "language-like" not in rd.verdict.lower()))

    # (4) raw predictability is higher for Markov than uniform (the shuffle null
    #     removes the shared small-sample bias -- hence pred_z, not the raw value,
    #     is what the verdict uses).
    out.append(("Markov raw predictability exceeds uniform",
                order_predictability(text) > order_predictability(uni)))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} langdetect checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
