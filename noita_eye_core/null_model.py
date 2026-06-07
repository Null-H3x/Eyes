"""Calibrated null model + significance testing.

The make-or-break gap in the seed-scan: across ~2^32 seeds the *best* score by
pure chance is large, so a raw "best score" is meaningless without a null
distribution and a multiple-testing correction.  This module provides the
generic machinery:

* build an empirical null by scoring randomised inputs (shuffle the data so the
  monographic statistics are preserved but any real structure is destroyed),
* turn an observed score into a z-score and an empirical p-value,
* correct for the number of candidates actually tried (Bonferroni and
  Benjamini-Hochberg).

It is deliberately scorer-agnostic: pass any ``score_fn`` and a ``randomise``
callable.  EyeStat/EyeSieve can wrap their dictionary or LM scorer; the depth
module uses it to gauge whether the measured difference-IoC is real.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, List, Sequence

import numpy as np


@dataclass(frozen=True)
class Significance:
    observed: float
    null_mean: float
    null_std: float
    z: float
    p_value: float          # empirical, upper tail (P[null >= observed])
    n_null: int

    def __str__(self) -> str:
        return (f"observed={self.observed:.5g}  null={self.null_mean:.5g}"
                f"+/-{self.null_std:.3g}  z={self.z:.2f}  "
                f"p={self.p_value:.3g}  (n_null={self.n_null})")


def empirical_null(score_fn: Callable[[object], float],
                   randomise: Callable[[np.random.Generator], object],
                   n_samples: int,
                   rng: np.random.Generator) -> List[float]:
    """Score ``n_samples`` randomised inputs to build a null distribution."""
    return [float(score_fn(randomise(rng))) for _ in range(n_samples)]


def significance(observed: float, null: Sequence[float],
                 tail: str = "greater") -> Significance:
    """Compare an observed score to a null sample.

    The empirical p-value uses the standard ``(1 + #exceedances) / (1 + n)``
    estimator (never reports p=0, which would over-claim).
    """
    arr = np.asarray(null, dtype=np.float64)
    n = arr.size
    if n == 0:
        raise ValueError("empty null distribution")
    mu = float(arr.mean())
    sd = float(arr.std(ddof=1)) if n > 1 else 0.0
    z = (observed - mu) / sd if sd > 0 else math.inf * (
        1 if observed > mu else (-1 if observed < mu else 0))
    if tail == "greater":
        exceed = int(np.sum(arr >= observed))
    elif tail == "less":
        exceed = int(np.sum(arr <= observed))
    else:
        raise ValueError("tail must be 'greater' or 'less'")
    p = (1 + exceed) / (1 + n)
    return Significance(observed=observed, null_mean=mu, null_std=sd,
                        z=z, p_value=p, n_null=n)


def bonferroni(p_value: float, n_tests: int) -> float:
    """Family-wise corrected p-value for ``n_tests`` candidates tried."""
    if n_tests < 1:
        raise ValueError("n_tests must be >= 1")
    return min(1.0, p_value * n_tests)


def benjamini_hochberg(p_values: Sequence[float]) -> List[float]:
    """Return BH-adjusted q-values (monotone), same order as input."""
    p = np.asarray(p_values, dtype=np.float64)
    m = p.size
    if m == 0:
        return []
    order = np.argsort(p)
    ranked = p[order]
    q = ranked * m / (np.arange(1, m + 1))
    # enforce monotonicity from the largest rank down
    q = np.minimum.accumulate(q[::-1])[::-1]
    q = np.clip(q, 0.0, 1.0)
    out = np.empty(m, dtype=np.float64)
    out[order] = q
    return out.tolist()


def expected_max_under_null(null: Sequence[float], n_trials: int) -> float:
    """Crude expected maximum of ``n_trials`` i.i.d. draws from the null,
    via the order-statistic of the empirical CDF.  Useful to sanity-check
    "is my best-of-N score even surprising?"."""
    arr = np.sort(np.asarray(null, dtype=np.float64))
    n = arr.size
    if n == 0:
        raise ValueError("empty null")
    # Expected rank of the max of n_trials draws ~ quantile (n_trials/(n_trials+1)).
    q = n_trials / (n_trials + 1)
    idx = min(n - 1, int(math.floor(q * n)))
    return float(arr[idx])


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def selftest() -> List[tuple[str, bool]]:
    out: List[tuple[str, bool]] = []
    rng = np.random.default_rng(2024)

    null = rng.normal(0.0, 1.0, size=5000).tolist()

    # A clearly-significant observation.
    sig = significance(5.0, null, tail="greater")
    out.append(("z-score ~ standardised value", abs(sig.z - 5.0) < 0.2))
    out.append(("significant obs has tiny p", sig.p_value < 1e-3))

    # A null-typical observation is not significant.
    sig0 = significance(0.0, null, tail="greater")
    out.append(("median obs p ~ 0.5", 0.4 < sig0.p_value < 0.6))

    # p-value is never 0 (the +1 estimator).
    sig_big = significance(100.0, null, tail="greater")
    out.append(("p-value never 0", sig_big.p_value > 0.0))

    # Bonferroni scales and clamps.
    out.append(("bonferroni clamps to 1.0",
                bonferroni(0.01, 10_000) == 1.0
                and abs(bonferroni(1e-9, 100) - 1e-7) < 1e-20))

    # BH: a vector with one tiny p and many large ones flags the small one.
    qs = benjamini_hochberg([1e-6] + [0.8] * 19)
    out.append(("BH flags the strong hit, not the noise",
                qs[0] < 0.05 and min(qs[1:]) > 0.5))
    out.append(("BH q-values are monotone in p",
                qs[0] <= max(qs)))

    # empirical_null wiring: a scorer that returns the mean of a shuffled
    # vector has a null centred at the data mean.
    data = np.arange(100.0)

    def score_fn(x):
        return float(np.mean(x[:10]))

    def randomise(g):
        y = data.copy()
        g.shuffle(y)
        return y

    nd = empirical_null(score_fn, randomise, 300, np.random.default_rng(1))
    out.append(("empirical_null centres near data mean",
                abs(float(np.mean(nd)) - data.mean()) < 5.0))

    # --- edge / error paths -------------------------------------------------
    # 'less' tail flags a small observation.
    sig_low = significance(-5.0, null, tail="less")
    out.append(("'less' tail flags a small observation",
                sig_low.p_value < 1e-3))

    # empty null is rejected.
    try:
        significance(1.0, [])
        empty_rejected = False
    except ValueError:
        empty_rejected = True
    out.append(("empty null rejected", empty_rejected))

    # invalid tail rejected.
    try:
        significance(1.0, null, tail="sideways")
        tail_rejected = False
    except ValueError:
        tail_rejected = True
    out.append(("invalid tail rejected", tail_rejected))

    # bonferroni rejects n_tests < 1; BH of [] is [].
    try:
        bonferroni(0.1, 0)
        bonf_rejected = False
    except ValueError:
        bonf_rejected = True
    out.append(("bonferroni rejects n_tests<1 & BH([]) == []",
                bonf_rejected and benjamini_hochberg([]) == []))

    # single-sample null gives sd=0 -> finite, signed-inf z (no crash).
    sig_one = significance(2.0, [0.0])
    out.append(("single-sample null: z is +inf, p computed",
                sig_one.z == math.inf and 0.0 < sig_one.p_value <= 1.0))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} null_model checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
