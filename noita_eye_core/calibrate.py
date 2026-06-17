"""Calibrated language scoring — the missing trust gate for the seed-scan.

EyeStat's dictionary scorer counts how many wordlist words appear as substrings
of a candidate decrypt.  Against a large, short-word-dense Finnish list that
metric is **uncalibrated**: a random 300-symbol string contains many 4-letter
Finnish substrings by pure chance, so gibberish scores "17 Finnish words" and the
scan drowns in false positives (every survivor's best language is Finnish, the
matches are 4-letter scraps, and the z-distribution is a smooth tail).  The
convergence audit flagged exactly this; this module supplies the fix.

Two tools:

* **Decoy calibration** — shuffle a decrypt's own symbols (preserving its unigram,
  destroying order) and re-score.  Real plaintext *loses* its words when shuffled
  (a word needs ordered letters); chance substrings survive.  So
  ``matches(text) ≫ matches(shuffle(text))`` is the signature of real language,
  and ``matches(text) ≈ matches(shuffle(text))`` is the signature of noise.  The
  calibrated z answers "is this hit real?" with a number.

* **Char n-gram LM score** — per-character log-likelihood under a model trained on
  the language's wordlist.  Unlike substring-counting it rewards readable
  *sequences*, so scattered short matches don't inflate it.

Both are validated against synthetic real-language vs. gibberish in :func:`selftest`.
"""
from __future__ import annotations

import random
from pathlib import Path
from typing import List, Optional, Sequence, Set, Tuple

from lm import CharModel
from null_model import significance


# ---------------------------------------------------------------------------
# Wordlist + substring matching
# ---------------------------------------------------------------------------

def load_wordset(path: Path | str, min_len: int = 4, limit: Optional[int] = None
                 ) -> Set[str]:
    out: Set[str] = set()
    with Path(path).open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            w = line.strip().lower()
            if len(w) >= min_len and w.isalpha():
                out.add(w)
                if limit and len(out) >= limit:
                    break
    return out


def count_matches(text: str, wordset: Set[str], min_len: int = 4,
                  max_len: int = 12) -> int:
    """Number of DISTINCT wordset words occurring as substrings of ``text``."""
    text = text.lower()
    n = len(text)
    found: Set[str] = set()
    for i in range(n):
        for L in range(min_len, min(max_len, n - i) + 1):
            sub = text[i:i + L]
            if sub in wordset:
                found.add(sub)
    return len(found)


def shuffle_null(text: str, wordset: Set[str], n_null: int = 200,
                 seed: int = 0, min_len: int = 4) -> List[int]:
    """Match counts for ``n_null`` shuffles of ``text`` (unigram preserved,
    order destroyed)."""
    rng = random.Random(seed)
    chars = list(text.lower())
    out = []
    for _ in range(n_null):
        rng.shuffle(chars)
        out.append(count_matches("".join(chars), wordset, min_len))
    return out


def calibrated(observed: float, null: Sequence[float]) -> Tuple[float, float]:
    sig = significance(observed, list(null), tail="greater")
    return sig.z, sig.p_value


# ---------------------------------------------------------------------------
# Char n-gram LM scorer
# ---------------------------------------------------------------------------

def train_charlm(wordlist: Sequence[str], add_k: float = 0.5) -> CharModel:
    return CharModel.train([" ".join(wordlist)], add_k=add_k)


def lm_per_char(text: str, model: CharModel) -> float:
    return model.score(text)


# ---------------------------------------------------------------------------
# One-call verdict for a candidate decrypt
# ---------------------------------------------------------------------------

def assess(text: str, wordset: Set[str], charlm: CharModel, n_null: int = 200,
           seed: int = 0) -> dict:
    """Calibrated verdict: is ``text`` real language or a chance-substring
    artifact?  Returns match count, its shuffle-null z, the LM score and its
    shuffle-null z, and a verdict string."""
    obs = count_matches(text, wordset)
    null = shuffle_null(text, wordset, n_null, seed)
    z_dict, p_dict = calibrated(obs, null)

    lm_obs = lm_per_char(text, charlm)
    rng = random.Random(seed + 1)
    chars = list(text.lower())
    lm_null = []
    for _ in range(n_null):
        rng.shuffle(chars)
        lm_null.append(lm_per_char("".join(chars), charlm))
    z_lm, p_lm = calibrated(lm_obs, lm_null)

    # The verdict relies on the char-LM (sequence) z, NOT the dictionary z.
    # Reason: if the decrypt came from a scorer that OPTIMISED the rune->letter
    # mapping to maximise word matches (EyeStat's Hungarian step), its words beat
    # a shuffle tautologically -> z_dict is inflated and unreliable. The char-LM
    # measures whole-text bigram structure, which a word-planting mapping cannot
    # manufacture, so z_lm is the mapping-robust signal.
    real = z_lm > 5
    if real:
        verdict = "READS AS LANGUAGE — char-LM far above the shuffle null"
    elif z_dict > 5:
        verdict = ("NOISE — dictionary matches beat shuffle but the char-LM does "
                   "NOT (z_lm={:.1f}): the mapping planted scattered words, the "
                   "text has no Finnish sequence structure".format(z_lm))
    else:
        verdict = ("NOISE — match count and LM are both at the shuffle null "
                   "(chance substrings, not ordered text)")
    return {"matches": obs, "z_dict": z_dict, "lm": lm_obs, "z_lm": z_lm,
            "real": real, "verdict": verdict}


# ---------------------------------------------------------------------------
# Selftest — real language vs gibberish, both decoy- and LM-calibrated
# ---------------------------------------------------------------------------

_FI = Path(__file__).resolve().parent.parent / "eyestat" / "extra_words_fi.txt"


def selftest() -> List[tuple[str, bool]]:
    out: List[tuple[str, bool]] = []
    rng = random.Random(0)

    # Without the Finnish wordlist we can only run the alphabet-agnostic checks.
    if not _FI.exists():
        out.append(("(fi wordlist absent — skipping language checks)", True))
        return out

    words = sorted(load_wordset(_FI, min_len=4, limit=40000))
    wordset = set(words)
    alphabet = sorted(set("".join(words)))
    charlm = train_charlm(words)

    # Real "Finnish" text: a run of real words (ordered letters -> real bigrams).
    real = " ".join(rng.choice(words) for _ in range(40))
    # Gibberish at realistic Finnish LETTER FREQUENCIES (this is what produces the
    # ~17 chance 4-letter matches seen in the actual EyeStat reports).
    from collections import Counter
    freq = Counter(c for w in words for c in w)
    letters, weights = zip(*freq.items())
    gib = "".join(rng.choices(letters, weights=weights, k=len(real)))

    a_real = assess(real, wordset, charlm, n_null=150, seed=1)
    a_gib = assess(gib, wordset, charlm, n_null=150, seed=2)

    # Decoy calibration: real words DON'T survive shuffling -> high z_dict;
    # gibberish substrings DO survive -> z_dict ~ 0.
    out.append(("real text: matches beat the shuffle null (z_dict>5)",
                a_real["z_dict"] > 5))
    out.append(("gibberish: matches at the shuffle null (z_dict<3)",
                a_gib["z_dict"] < 3))

    # LM: real text far more likely than gibberish, and above its own shuffle null.
    out.append(("LM: real text scores above gibberish",
                a_real["lm"] > a_gib["lm"]))
    out.append(("LM: real text beats its shuffle null (z_lm>5)",
                a_real["z_lm"] > 5))

    # Verdicts.
    out.append(("verdict: real text -> language", a_real["real"]))
    out.append(("verdict: gibberish -> NOISE", not a_gib["real"]))

    # The artifact itself: gibberish still racks up SOME raw matches (the trap)
    # but they are NOT significant once calibrated.
    out.append(("gibberish racks up raw matches yet is NOT significant",
                a_gib["matches"] >= 3 and not a_gib["real"]))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} calibrate checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
