"""Joint multi-message verification oracle — the EyeCrack core.

A single message at ``N=83`` and ~115 symbols cannot tell a real keystream from
one of millions of chance high-scorers: the language signal per message is tiny.
The corpus's saving grace is **depth** — the nine messages share one
position-indexed keystream — which converts "score one decrypt" into "score nine
decrypts under the SAME keystream **simultaneously**".  That joint constraint is
the multiplier that makes a brute-force hit *trustworthy*.

This module provides that oracle, scorer-agnostic and calibrated:

* :class:`JointOracle` decrypts every in-depth message with one candidate
  keystream and returns a single pooled per-symbol log-likelihood (plus the
  per-message breakdown).
* It builds an **empirical null** from random keystreams (wrong key -> gibberish
  plaintext -> low score) and turns any candidate's score into a z / p-value, and
  a **Bonferroni-corrected** q-value given how many candidates were actually
  tried.  This is the make-or-break "is this hit even surprising?" gate the
  unconstrained seed scans lack.

Why pooling helps (the property the selftest proves)
---------------------------------------------------
Under the true keystream every message becomes language-like, so each contributes
positive log-likelihood and the pooled z-score grows ~ ``sqrt(total_symbols)``.
Scoring nine messages jointly is therefore far more powerful than scoring one —
the selftest verifies the true keystream's joint z is much larger than its single
message z, and that the true seed is the unique Bonferroni-significant hit in a
scan of decoy seeds.

Honesty
-------
The oracle is only as good as the supplied language model.  In *symbol space*
(integers ``0..N-1``) a model needs symbol-space training text, which for the real
corpus is unknown without a rune->letter mapping (EyeStat's Hungarian mapping +
dictionary scorer is the production answer there).  So on the real corpus this
oracle's trustworthy uses are (a) the exact crib-drag propagation (no LM needed)
and (b) a calibrated *backend* once a mapping/LM is supplied.  The selftest plants
a known symbol-space language so correctness is provable end-to-end; it does not
claim the real plaintext.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, List, Optional, Sequence

import numpy as np

import cipher_ops
from lm import MarkovModel
from null_model import Significance, bonferroni, significance


def _normal_upper_p(z: float) -> float:
    """Upper-tail p-value of a standard normal at ``z``.  The pooled per-symbol
    score is a mean over ~1000 symbols, so by the CLT the null is ~normal and a
    z-derived p-value (unlike an empirical one) is not floored at ``1/(n+1)`` —
    which matters because a real hit must survive Bonferroni over a huge seed
    budget."""
    if math.isinf(z):
        return 0.0 if z > 0 else 1.0
    return 0.5 * math.erfc(z / math.sqrt(2))


@dataclass
class JointScore:
    keystream_len: int
    total_logprob: float
    total_symbols: int
    per_symbol: float                  # pooled total_logprob / total_symbols
    per_message: List[float]           # per-symbol logprob for each message

    def __str__(self) -> str:
        return (f"per_symbol={self.per_symbol:.4f}  "
                f"total={self.total_logprob:.1f}  "
                f"symbols={self.total_symbols}")


@dataclass
class CandidateVerdict:
    score: JointScore
    significance: Significance
    p_analytic: float                  # normal-tail p from the z-score (CLT)
    q_bonferroni: float                # p_analytic corrected for n_trials
    n_trials: int

    @property
    def trustworthy(self) -> bool:
        return self.q_bonferroni < 0.01


# A scorer maps a decrypted message (symbols) to a *total* log-probability.
Scorer = Callable[[Sequence[int]], float]


class JointOracle:
    """Score a candidate keystream against all in-depth messages at once."""

    def __init__(self, messages: Sequence[Sequence[int]], N: int,
                 scorer: Scorer, mode: str = "add",
                 in_depth_set: Optional[Sequence[int]] = None):
        self.N = N
        self.mode = mode
        self.combiner = cipher_ops.get_mode(mode)
        idx = list(in_depth_set) if in_depth_set is not None \
            else list(range(len(messages)))
        self.indices = idx
        self.messages = [list(messages[i]) for i in idx]
        self.scorer = scorer
        self.max_len = max(len(m) for m in self.messages)
        self._null: Optional[np.ndarray] = None

    # -- core scoring -----------------------------------------------------
    def decrypt(self, keystream: Sequence[int]) -> List[List[int]]:
        if len(keystream) < self.max_len:
            raise ValueError(f"keystream length {len(keystream)} < longest "
                             f"message {self.max_len}")
        dec = self.combiner.decrypt
        N = self.N
        return [[dec(m[t], keystream[t], N) for t in range(len(m))]
                for m in self.messages]

    def raw_score(self, keystream: Sequence[int]) -> JointScore:
        plains = self.decrypt(keystream)
        per_msg_total = [self.scorer(p) for p in plains]
        per_msg_persym = [(per_msg_total[k] / len(plains[k]))
                          if plains[k] else 0.0
                          for k in range(len(plains))]
        total = float(sum(per_msg_total))
        nsym = int(sum(len(p) for p in plains))
        return JointScore(keystream_len=len(keystream), total_logprob=total,
                          total_symbols=nsym,
                          per_symbol=total / nsym if nsym else 0.0,
                          per_message=per_msg_persym)

    # -- calibration ------------------------------------------------------
    def build_null(self, n_null: int = 1000,
                   rng: Optional[np.random.Generator] = None) -> np.ndarray:
        """Empirical null of the pooled per-symbol score under random
        keystreams (wrong key -> gibberish)."""
        rng = rng or np.random.default_rng(0)
        scores = np.empty(n_null, dtype=np.float64)
        for i in range(n_null):
            ks = rng.integers(0, self.N, size=self.max_len).tolist()
            scores[i] = self.raw_score(ks).per_symbol
        self._null = scores
        return scores

    def significance(self, keystream: Sequence[int]) -> Significance:
        if self._null is None:
            raise RuntimeError("call build_null() first")
        return significance(self.raw_score(keystream).per_symbol,
                            self._null.tolist(), tail="greater")

    def evaluate(self, keystream: Sequence[int], n_trials: int = 1
                 ) -> CandidateVerdict:
        """Full verdict for a candidate: score, significance vs the null, and a
        Bonferroni q-value for ``n_trials`` candidates tried."""
        sc = self.raw_score(keystream)
        sig = self.significance(keystream)
        p_an = _normal_upper_p(sig.z)
        q = bonferroni(p_an, max(1, n_trials))
        return CandidateVerdict(score=sc, significance=sig, p_analytic=p_an,
                                q_bonferroni=q, n_trials=n_trials)


# ---------------------------------------------------------------------------
# Convenience: build a symbol-space scorer from a MarkovModel
# ---------------------------------------------------------------------------

def markov_scorer(model: MarkovModel) -> Scorer:
    return lambda seq: model.logprob(seq)


# ---------------------------------------------------------------------------
# Selftest — plant a keystream, prove joint scoring recovers/validates it
# ---------------------------------------------------------------------------

def _planted_language_model(N: int, seed: int) -> MarkovModel:
    """A symbol-space 1st-order chain with real bigram structure (peaky rows)
    so decrypted plaintext is clearly distinguishable from gibberish."""
    rng = np.random.default_rng(seed)
    bi = np.zeros((N, N))
    for a in range(N):
        # each symbol strongly prefers a couple of successors
        row = rng.random(N) ** 8
        row[(a + 1) % N] += 5.0
        row[(a * 7 + 3) % N] += 3.0
        bi[a] = row / row.sum()
    uni = np.full(N, 1.0 / N)
    return MarkovModel(N, np.log(uni), np.log(bi))


def _emit(model: MarkovModel, T: int, rng: np.random.Generator) -> List[int]:
    N = model.N
    bi = np.exp(model.bi_logp)
    s = int(rng.integers(0, N))
    out = [s]
    for _ in range(T - 1):
        s = int(rng.choice(N, p=bi[s]))
        out.append(s)
    return out


def selftest() -> List[tuple[str, bool]]:
    out: List[tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(123)
    model = _planted_language_model(N, seed=1)
    scorer = markov_scorer(model)

    # Build 9 in-depth messages: shared keystream, language-like plaintext.
    M, lengths = 9, [99, 103, 118, 102, 137, 124, 119, 120, 114]
    Lmax = max(lengths)
    true_key = rng.integers(0, N, size=Lmax).tolist()
    plains = [_emit(model, lengths[i], rng) for i in range(M)]
    cipher = [[(plains[i][t] + true_key[t]) % N for t in range(lengths[i])]
              for i in range(M)]

    oracle = JointOracle(cipher, N, scorer, mode="add")
    oracle.build_null(n_null=600, rng=np.random.default_rng(2))

    # (1) True keystream scores far above the random-keystream null.
    v_true = oracle.evaluate(true_key, n_trials=1)
    out.append(("true keystream is hugely significant",
                v_true.significance.z > 8))
    out.append(("true keystream beats a random keystream",
                oracle.raw_score(true_key).per_symbol
                > oracle.raw_score(rng.integers(0, N, size=Lmax).tolist()).per_symbol))

    # (2) Joint (9-message) z >> single-message z: pooling is the multiplier.
    single = JointOracle(cipher, N, scorer, mode="add", in_depth_set=[0])
    single.build_null(n_null=600, rng=np.random.default_rng(3))
    z_single = single.significance(true_key).z
    out.append(("joint z exceeds single-message z",
                v_true.significance.z > z_single))

    # (3) A wrong keystream is NOT significant.
    wrong = rng.integers(0, N, size=Lmax).tolist()
    out.append(("wrong keystream is not significant",
                oracle.significance(wrong).z < 5))

    # (4) Bonferroni: the true key stays significant even after correcting for a
    #     large trial budget; a null-typical score does not.
    v_budget = oracle.evaluate(true_key, n_trials=1_000_000)
    out.append(("true key survives Bonferroni over 1e6 trials",
                v_budget.q_bonferroni < 0.01 and v_budget.trustworthy))

    # (5) Mini seed-scan: among decoy keystreams + the true one, the true one is
    #     the unique trustworthy hit after correction.
    candidates = [rng.integers(0, N, size=Lmax).tolist() for _ in range(200)]
    candidates.append(true_key)
    n_trials = len(candidates)
    verdicts = [oracle.evaluate(k, n_trials=n_trials) for k in candidates]
    trustworthy = [i for i, v in enumerate(verdicts) if v.trustworthy]
    out.append(("seed-scan: exactly one trustworthy hit",
                trustworthy == [len(candidates) - 1]))

    # (6) decrypt round-trip: true key recovers the planted plaintext exactly.
    dec = oracle.decrypt(true_key)
    out.append(("true key decrypts to the planted plaintext",
                dec[0] == plains[0] and dec[4] == plains[4]))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} oracle checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
