"""Shared statistics: Index of Coincidence, chi-squared / L2 against uniform,
and the depth-relevant difference IoC.

These formulas are currently duplicated in EyeStat (shape filter), EyeSieve
(``compute_ic``) and the workbench (``ioc()``).  One tested implementation here
is the convergence target.

Conventions
-----------
* ``ioc`` returns the *raw* index of coincidence
  ``sum_s n_s (n_s - 1) / (T (T - 1))`` -- the probability that two symbols
  drawn without replacement are equal.  For a uniform alphabet of size ``N``
  this tends to ``1/N``.
* ``ioc_normalised`` multiplies by ``N`` so that "looks uniform" sits at ~1.0
  and natural language sits well above 1.0, independent of alphabet size.  The
  English benchmark ``~1.73`` (``0.0667 * 26``) is alphabet-independent in this
  normalised form -- which is exactly the bug the workbench patch fixed by
  making the reference N-aware.
"""
from __future__ import annotations

from collections import Counter
from typing import Dict, List, Sequence


def ioc(seq: Sequence[int]) -> float:
    """Raw index of coincidence.  Returns 0.0 for sequences shorter than 2."""
    T = len(seq)
    if T < 2:
        return 0.0
    counts = Counter(seq)
    num = sum(n * (n - 1) for n in counts.values())
    return num / (T * (T - 1))


def ioc_normalised(seq: Sequence[int], N: int) -> float:
    """IoC scaled by alphabet size ``N`` (uniform -> ~1.0)."""
    return ioc(seq) * N


def uniform_ioc(N: int) -> float:
    """Expected IoC of a uniform random stream over ``N`` symbols."""
    return 1.0 / N


def difference(a: Sequence[int], b: Sequence[int], N: int) -> List[int]:
    """Position-wise ``(a - b) mod N`` over the common prefix length."""
    L = min(len(a), len(b))
    return [(a[t] - b[t]) % N for t in range(L)]


def difference_ioc(a: Sequence[int], b: Sequence[int], N: int) -> float:
    """IoC of the difference stream.

    For two ciphertexts in depth under a linear stream cipher (shared key),
    the difference is the difference of the two *plaintexts*, so this is the
    plaintext difference IoC -- well above ``1/N`` for natural language and
    ~``1/N`` for messages that are NOT in depth.  This is the core depth test.
    """
    return ioc(difference(a, b, N))


def chi2_uniform(seq: Sequence[int], N: int) -> float:
    """Pearson chi-squared of the symbol histogram against the uniform
    expectation over ``N`` symbols."""
    T = len(seq)
    if T == 0:
        return 0.0
    counts = Counter(seq)
    expected = T / N
    return sum((counts.get(s, 0) - expected) ** 2 / expected
               for s in range(N))


def histogram(seq: Sequence[int], N: int) -> List[int]:
    counts = Counter(seq)
    return [counts.get(s, 0) for s in range(N)]


def frequencies(seq: Sequence[int], N: int) -> List[float]:
    T = len(seq)
    if T == 0:
        return [0.0] * N
    counts = Counter(seq)
    return [counts.get(s, 0) / T for s in range(N)]


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def selftest() -> List[tuple[str, bool]]:
    import random
    out: List[tuple[str, bool]] = []

    # Hand KAT: AABB -> pairs equal: (A,A) and (B,B) out of C(4,2)=6 -> 2/6.
    out.append(("ioc hand KAT (AABB = 1/3)",
                abs(ioc([0, 0, 1, 1]) - (2 / 6)) < 1e-12))

    # All-same -> IoC 1.0 ; all-distinct -> 0.0.
    out.append(("ioc all-equal = 1.0", abs(ioc([7] * 10) - 1.0) < 1e-12))
    out.append(("ioc all-distinct = 0.0", ioc(list(range(10))) == 0.0))

    # Short sequences are defined as 0.0.
    out.append(("ioc len<2 = 0.0", ioc([3]) == 0.0 and ioc([]) == 0.0))

    # Uniform random stream IoC ~ 1/N (statistical, generous band).
    rng = random.Random(99)
    N = 83
    big = [rng.randrange(N) for _ in range(60000)]
    got = ioc(big)
    out.append(("uniform random IoC ~ 1/N",
                abs(got - 1.0 / N) < 0.0015))
    out.append(("ioc_normalised uniform ~ 1.0",
                abs(ioc_normalised(big, N) - 1.0) < 0.13))

    # difference cancels a shared additive key: build two streams with the
    # same key and check difference_ioc equals plaintext difference IoC.
    plain1 = [rng.randrange(N) for _ in range(4000)]
    plain2 = [rng.randrange(N) for _ in range(4000)]
    key = [rng.randrange(N) for _ in range(4000)]
    c1 = [(plain1[t] + key[t]) % N for t in range(4000)]
    c2 = [(plain2[t] + key[t]) % N for t in range(4000)]
    direct = ioc(difference(plain1, plain2, N))
    via_cipher = difference_ioc(c1, c2, N)
    out.append(("difference IoC is key-invariant",
                abs(direct - via_cipher) < 1e-12))

    # chi2 of a uniform stream is small relative to its dof (N-1).
    out.append(("chi2 uniform random < 2*(N-1)",
                chi2_uniform(big, N) < 2 * (N - 1)))

    # frequencies sum to 1.
    f = frequencies(big, N)
    out.append(("frequencies sum to 1.0", abs(sum(f) - 1.0) < 1e-9))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} stats checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
