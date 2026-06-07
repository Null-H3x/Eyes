"""Character n-gram language model (Markov) used both as a *scorer* and as the
*emission/transition model* for the depth solver.

Why this is the right primitive
--------------------------------
EyeStat currently scores candidates by counting dictionary substring hits +
Zipf weighting.  That is brittle: short random strings rack up substring hits.
A character n-gram log-likelihood is the standard, calibrated alternative and --
critically -- it is exactly the objective the depth Viterbi optimises (a 1st
order model gives a per-symbol *unigram* emission term and a *bigram* transition
term, both as log-probabilities).

The model lives in *symbol space* (integers ``0..N-1``) so it can serve the
mod-83 depth attack directly.  :class:`CharModel` wraps it for ordinary letter
text (used to score a decrypt once a rune->letter mapping is applied).

Smoothing is add-k (Laplace) with explicit, tested normalisation: every bigram
row sums to 1 and every log-prob is finite, so the Viterbi DP never sees -inf.
"""
from __future__ import annotations

import math
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np


class MarkovModel:
    """1st-order Markov model over symbols ``0..N-1`` with add-k smoothing.

    Attributes
    ----------
    N : int
    uni_logp : np.ndarray, shape (N,)
        Smoothed unigram log-probabilities.
    bi_logp : np.ndarray, shape (N, N)
        ``bi_logp[a, b] = log P(b | a)``; every row normalises to 1.
    """

    def __init__(self, N: int, uni_logp: np.ndarray, bi_logp: np.ndarray):
        self.N = N
        self.uni_logp = uni_logp
        self.bi_logp = bi_logp

    @classmethod
    def from_int_sequences(cls, sequences: Sequence[Sequence[int]], N: int,
                           add_k: float = 0.5) -> "MarkovModel":
        if add_k <= 0:
            raise ValueError("add_k must be > 0 to keep log-probs finite")
        uni = np.full(N, add_k, dtype=np.float64)
        bi = np.full((N, N), add_k, dtype=np.float64)
        for seq in sequences:
            prev = None
            for s in seq:
                if not (0 <= s < N):
                    raise ValueError(f"symbol {s} outside [0,{N})")
                uni[s] += 1.0
                if prev is not None:
                    bi[prev, s] += 1.0
                prev = s
        uni_logp = np.log(uni / uni.sum())
        bi_logp = np.log(bi / bi.sum(axis=1, keepdims=True))
        return cls(N, uni_logp, bi_logp)

    def logprob(self, seq: Sequence[int]) -> float:
        """Total log-probability of ``seq`` under the model."""
        if len(seq) == 0:
            return 0.0
        total = float(self.uni_logp[seq[0]])
        for i in range(1, len(seq)):
            total += float(self.bi_logp[seq[i - 1], seq[i]])
        return total

    def logprob_per_symbol(self, seq: Sequence[int]) -> float:
        if len(seq) == 0:
            return 0.0
        return self.logprob(seq) / len(seq)


class CharModel:
    """A :class:`MarkovModel` over a fixed character alphabet, for scoring
    ordinary text (e.g. a decrypt after a rune->letter mapping)."""

    def __init__(self, alphabet: str, model: MarkovModel):
        self.alphabet = alphabet
        self.index = {ch: i for i, ch in enumerate(alphabet)}
        self.model = model

    @classmethod
    def train(cls, texts: Sequence[str], add_k: float = 0.5,
              alphabet: Optional[str] = None) -> "CharModel":
        if alphabet is None:
            seen = sorted({ch for t in texts for ch in t})
            alphabet = "".join(seen)
        index = {ch: i for i, ch in enumerate(alphabet)}
        N = len(alphabet)
        seqs = [[index[ch] for ch in t if ch in index] for t in texts]
        model = MarkovModel.from_int_sequences(seqs, N, add_k=add_k)
        return cls(alphabet, model)

    def encode(self, text: str) -> List[int]:
        return [self.index[ch] for ch in text if ch in self.index]

    def score(self, text: str) -> float:
        """Average log-probability per character (higher = more language-like)."""
        return self.model.logprob_per_symbol(self.encode(text))


def load_wordlist(path: Path | str, limit: Optional[int] = None,
                  lowercase: bool = True) -> List[str]:
    out: List[str] = []
    with Path(path).open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            w = line.strip()
            if not w:
                continue
            if lowercase:
                w = w.lower()
            out.append(w)
            if limit is not None and len(out) >= limit:
                break
    return out


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

# A tiny deterministic "language": repeated structured words.  Enough to make
# bigram structure measurable without any external file.
_TRAIN_TEXT = (
    "the eye sees all the secrets of the cave below the surface "
    "the seeker reads the runes and the eye reveals the hidden way "
    "secret runes guard the deep cave where the eye sees the seeker"
)


def selftest() -> List[tuple[str, bool]]:
    out: List[tuple[str, bool]] = []

    # Bigram rows normalise to 1 and all log-probs are finite.
    words = _TRAIN_TEXT.split()
    cm = CharModel.train([" ".join(words)])
    rowsum = np.exp(cm.model.bi_logp).sum(axis=1)
    out.append(("bigram rows normalise to 1.0",
                bool(np.allclose(rowsum, 1.0))))
    out.append(("all log-probs finite",
                bool(np.all(np.isfinite(cm.model.bi_logp))
                     and np.all(np.isfinite(cm.model.uni_logp)))))

    # In-language text scores higher than a shuffled version of the same chars.
    import random
    rng = random.Random(7)
    probe = "the eye sees the secret runes"
    chars = list(probe)
    rng.shuffle(chars)
    shuffled = "".join(chars)
    out.append(("in-language scores above shuffled",
                cm.score(probe) > cm.score(shuffled)))

    # Symbol-space model recovers a planted strong bigram: in a chain where 0
    # is almost always followed by 1, P(1|0) must dominate.
    seqs = [[0, 1] * 50, [0, 1] * 50]
    mm = MarkovModel.from_int_sequences(seqs, 3, add_k=0.5)
    out.append(("planted bigram P(1|0) is the row max",
                int(np.argmax(mm.bi_logp[0])) == 1))

    # KAT: tiny corpus, exact add-k arithmetic.  Sequence [0,0,1] over N=2,
    # add_k=1.  Bigram counts: (0->0)=1, (0->1)=1, (1->*)=0.
    # Row 0: [1+1, 1+1]/(2+2) = [0.5,0.5]; row1: [1,1]/2 = [0.5,0.5].
    kat = MarkovModel.from_int_sequences([[0, 0, 1]], 2, add_k=1.0)
    out.append(("add-k bigram KAT",
                abs(math.exp(kat.bi_logp[0, 0]) - 0.5) < 1e-12
                and abs(math.exp(kat.bi_logp[1, 1]) - 0.5) < 1e-12))

    # Optional: train on the real English wordlist if the archive is present.
    eng = Path(__file__).resolve().parent.parent / "eyestat" / "eng-wordlist.txt"
    if eng.exists():
        ws = load_wordlist(eng, limit=20000)
        big = CharModel.train([" ".join(ws)])
        good = big.score("the secret of the ancient cave")
        bad = big.score("xqzjkvwbxqzjkvwbxqzjkvwb")
        out.append(("real English LM: words >> gibberish", good > bad))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} lm checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
