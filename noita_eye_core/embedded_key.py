"""Embedded-key test — does a triplet hide its own keystream? (Model B)

The community observation (yours): within each triplet two messages stay paired
while the third "drops out" in some regions, and the identity of the odd-one-out
rotates.  That is the fingerprint of **pair + key**: maybe each triplet is two
messages plus an embedded keystream, so 9 = 3 x (2 messages + 1 key).

Two competing models:

* **Model A (global keystream):** every message is ``p_i + K`` for one external,
  position-indexed ``K`` shared by all nine.  The three members of a triplet are
  *symmetric* — none is "the key".  Differencing any pair gives a difference of
  plaintexts.
* **Model B (embedded key):** within a triplet ``{a, b, key}`` the third member's
  ciphertext **is** the keystream, so ``decrypt(c_a, c_key) == p_a`` is *readable
  plaintext*, and likewise for ``c_b``.

The discriminating, language-agnostic question: is there a choice of *which
member is the key* (and which combiner) that makes the **other two** decrypt to
genuinely structured (non-uniform) streams — and does that choice clearly beat the
alternatives and a random-key null?

Scoring.  Each candidate assignment ``(key, mode)`` is scored by the **minimum**
structure (alphabet-normalised IoC) across its two implied decrypts: the embedded
key must turn *both* partners into plaintext, so a correct key maximises the worse
of the two.  A wrong key leaves at least one decrypt as a difference-of-plaintexts
(less structured), dragging the minimum down.  Model B is *detected* only when the
best assignment both clears a random-key null and clearly separates from the
runner-up.

Honesty about power (read this before trusting a negative).
-----------------------------------------------------------
This test can only see structure the metric can measure.  The real corpus has a
**near-uniform unigram** (``classify`` found it reaches ~9% of language-like), so
even a *correct* embedded key would yield a decrypt whose unigram is almost flat —
and the test will (correctly) report *inconclusive*, not *false*.  That is the
honest state of the evidence: confirming Model B needs a **crib** (one known word
turns a decrypt readable), not more statistics.  The selftest proves the machinery
recovers a planted embedded key when the plaintext *does* carry unigram signal; it
does not claim the real triplets do.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

import numpy as np

import cipher_ops
import corpus as corpus_mod
from stats import ioc_normalised

# The three consecutive triplets (same as grouping.TRIPLETS).
CONSEC_TRIPLETS: Tuple[Tuple[int, int, int], ...] = ((0, 1, 2), (3, 4, 5),
                                                     (6, 7, 8))
MODES = ("add", "sub", "beaufort")


def decrypt_with_member(messages: Sequence[Sequence[int]], target: int,
                        key: int, mode: str, N: int,
                        region: Optional[Tuple[int, int]] = None) -> List[int]:
    """``decrypt(c_target[t], c_key[t])`` over the overlap (optionally a region).

    If the key member's ciphertext *is* the keystream, this returns ``p_target``.
    """
    comb = cipher_ops.get_mode(mode)
    L = min(len(messages[target]), len(messages[key]))
    seq = [comb.decrypt(messages[target][t], messages[key][t], N)
           for t in range(L)]
    if region is not None:
        seq = seq[region[0]:region[1]]
    return seq


def _structure(seq: Sequence[int], N: int) -> float:
    """Alphabet-normalised IoC: 1.0 = uniform, > 1 = peaked/structured."""
    return ioc_normalised(seq, N)


@dataclass
class Assignment:
    key: int
    mode: str
    min_structure: float
    structures: List[float]
    targets: List[int]


@dataclass
class TripletReport:
    triplet: Tuple[int, ...]
    ranked: List[Assignment]
    best: Assignment
    runner_up: Assignment
    null_mean: float
    null_std: float
    threshold: float
    detected: bool
    reason: str = ""
    overlap: int = 0


def score_assignment(messages: Sequence[Sequence[int]], triplet: Sequence[int],
                     key: int, mode: str, N: int,
                     region: Optional[Tuple[int, int]] = None) -> Assignment:
    targets = [m for m in triplet if m != key]
    structs: List[float] = []
    for tg in targets:
        d = decrypt_with_member(messages, tg, key, mode, N, region)
        structs.append(_structure(d, N))
    return Assignment(key=key, mode=mode, min_structure=min(structs),
                      structures=structs, targets=targets)


def _null_structure(L: int, N: int, n_null: int,
                    rng: np.random.Generator) -> Tuple[float, float]:
    """Structure of length-``L`` uniform-random streams (= decrypt of any message
    with a random key)."""
    vals = [_structure(rng.integers(0, N, size=L).tolist(), N)
            for _ in range(n_null)]
    return float(np.mean(vals)), float(np.std(vals, ddof=1))


def test_triplet(messages: Sequence[Sequence[int]], triplet: Sequence[int],
                 N: int, modes: Sequence[str] = MODES, n_null: int = 1000,
                 seed: int = 0, region: Optional[Tuple[int, int]] = None,
                 separation: float = 1.5) -> TripletReport:
    rng = np.random.default_rng(seed)
    results = [score_assignment(messages, triplet, key, mode, N, region)
               for key in triplet for mode in modes]
    results.sort(key=lambda a: -a.min_structure)
    best = results[0]
    # The runner-up for SEPARATION must be a different key member: add/beaufort
    # under the *same* key both recover +/-plaintext, so comparing modes of one
    # key is not a real alternative.  A genuine embedded key must beat the best
    # *rival key*.
    rivals = [a for a in results if a.key != best.key]
    runner = rivals[0] if rivals else results[1]

    L = (min(len(messages[m]) for m in triplet) if region is None
         else region[1] - region[0])
    nm, ns = _null_structure(L, N, n_null, rng)
    threshold = nm + 4.0 * ns

    beats_null = best.min_structure > threshold
    separated = best.min_structure > separation * runner.min_structure
    detected = bool(beats_null and separated)
    if detected:
        reason = (f"key=msg{best.key} ({best.mode}) makes both partners "
                  f"structured (min IoC*N={best.min_structure:.2f}) — clears null "
                  f"{threshold:.2f} and beats runner-up {runner.min_structure:.2f}")
    elif not beats_null:
        reason = (f"no assignment clears the random-key null "
                  f"(best min IoC*N={best.min_structure:.2f} <= {threshold:.2f}); "
                  f"underpowered if the plaintext unigram is flat")
    else:
        reason = (f"best ({best.min_structure:.2f}) does not clearly separate "
                  f"from runner-up ({runner.min_structure:.2f}) — symmetric, as "
                  f"Model A (global keystream) predicts")
    return TripletReport(triplet=tuple(triplet), ranked=results, best=best,
                         runner_up=runner, null_mean=nm, null_std=ns,
                         threshold=threshold, detected=detected, reason=reason,
                         overlap=L)


# ---------------------------------------------------------------------------
# Selftest — plant Model B and Model A, prove the test tells them apart
# ---------------------------------------------------------------------------

def _zipf_plain(k: int, N: int, T: int, rng: np.random.Generator) -> List[int]:
    w = np.zeros(N)
    w[:k] = 1.0 / np.arange(1, k + 1)
    w /= w.sum()
    return rng.choice(N, size=T, p=w).tolist()


def selftest() -> List[tuple[str, bool]]:
    out: List[tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(31)
    T = 120

    # --- Model B: member 2 IS the raw keystream; 0 and 1 are p+K ---
    K = rng.integers(0, N, size=T)
    p0 = _zipf_plain(30, N, T, rng)
    p1 = _zipf_plain(30, N, T, rng)
    cB = [[(p0[t] + int(K[t])) % N for t in range(T)],
          [(p1[t] + int(K[t])) % N for t in range(T)],
          [int(K[t]) for t in range(T)]]
    repB = test_triplet(cB, (0, 1, 2), N, n_null=400, seed=1)
    out.append(("Model B: embedded key detected", repB.detected))
    out.append(("Model B: identifies the key member (msg 2)",
                repB.best.key == 2))
    # add-mode decrypt of a partner with the true key recovers the plaintext
    rec = decrypt_with_member(cB, 0, 2, "add", N)
    out.append(("Model B: decrypt with key recovers planted plaintext",
                rec == p0))

    # --- Model A: all three are p_i + one global K; NO embedded key ---
    p2 = _zipf_plain(30, N, T, rng)
    cA = [[(p0[t] + int(K[t])) % N for t in range(T)],
          [(p1[t] + int(K[t])) % N for t in range(T)],
          [(p2[t] + int(K[t])) % N for t in range(T)]]
    repA = test_triplet(cA, (0, 1, 2), N, n_null=400, seed=2)
    out.append(("Model A: no embedded key detected (symmetric)",
                not repA.detected))

    # --- Flat-unigram realism: even a TRUE embedded key over flat plaintext is
    #     correctly reported inconclusive (the honest negative). ---
    pf0 = rng.integers(0, N, size=T).tolist()   # uniform plaintext (flat)
    pf1 = rng.integers(0, N, size=T).tolist()
    cF = [[(pf0[t] + int(K[t])) % N for t in range(T)],
          [(pf1[t] + int(K[t])) % N for t in range(T)],
          [int(K[t]) for t in range(T)]]
    repF = test_triplet(cF, (0, 1, 2), N, n_null=400, seed=3)
    out.append(("flat plaintext -> embedded key NOT falsely detected",
                not repF.detected))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} embedded_key checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
