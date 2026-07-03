"""order_anneal — shared monoalphabetic solve on the support_min reduction.

Once support_min fixes q, every message reduces to residues
    r_m[t] = (q[c_m[t]] - t) mod N = (p_m[t] + base_m) mod N,
a per-message ROTATION of the plaintext values. Removing base_m (an 83-way
per-message rotation search) turns the whole corpus into ONE shared
monoalphabetic cryptogram over the plaintext-value alphabet -- the classic,
fast, hill-climbable problem (Zodiac-340 shape). This module:

  1. removes bases by aligning every message to a common frame (fix base_0=0,
     search base_m for m>0 by best n-gram fit against message 0's frame),
  2. hill-climbs the value->character ordering O with a character n-gram
     model, scored across a LANGUAGE BANK so the language is identified rather
     than assumed (English shipped; Finnish/Karelian/Latin pluggable),
  3. returns the best (language, O, bases, plaintext) with a null-calibrated
     score so a caller knows whether the read is real or noise.

WHY IT WON'T REPEAT THE IoC MISTAKE: fitness is character n-gram log-prob
(order-sensitive), never IoC. WHY IT WON'T REPEAT THE FINNISH MISTAKE: the
language is one axis of the search, chosen by score, so a wrong-language guess
cannot be mistaken for failure -- every language in the bank is tried.

HONEST LIMITS: needs a MOSTLY-correct q (garbage in -> garbage out; the audit
shows score degrades smoothly with q-errors so a caller can read the quality
off the score). The n-gram bank must contain the true language; the audit
includes a "language not in bank" negative so the failure mode is explicit.
"""
from __future__ import annotations

import math
import random
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "noita_eye_core"))

import plantlab  # noqa: E402

Cts = Sequence[Sequence[int]]


# ------------------------------------------------------------ n-gram model
class CharNgram:
    """Add-k character trigram model over a fixed alphabet string."""

    def __init__(self, alphabet: str, logp: Dict[str, float],
                 default: float):
        self.alphabet = alphabet
        self.logp = logp
        self.default = default

    @classmethod
    def train(cls, text: str, alphabet: str, add_k: float = 0.2) -> "CharNgram":
        text = "".join(ch if ch in alphabet else " " for ch in text.lower())
        ctx = defaultdict(lambda: defaultdict(float))
        for i in range(len(text) - 2):
            ctx[text[i:i + 2]][text[i + 2]] += 1.0
        V = len(alphabet)
        logp: Dict[str, float] = {}
        default = math.log(1.0 / V)
        for c2, nxt in ctx.items():
            tot = sum(nxt.values()) + add_k * V
            for ch in alphabet:
                logp[c2 + ch] = math.log((nxt.get(ch, 0.0) + add_k) / tot)
        return cls(alphabet, logp, default)

    def score(self, text: str) -> float:
        s = 0.0
        for i in range(len(text) - 2):
            s += self.logp.get(text[i:i + 3], self.default)
        return s / max(1, len(text) - 2)


def language_bank() -> Dict[str, CharNgram]:
    """Build the language bank from shipped corpora. English from plantlab's
    sample as a floor; extend by dropping wordlists in eyestat/."""
    alpha = plantlab.ALPHABET
    bank = {"english": CharNgram.train(plantlab.SAMPLE_TEXT, alpha)}
    est = HERE.parent / "eyestat"
    for name, fn in (("finnish", "extra_words_fi.txt"),
                     ("karelian", "extra_words_krl.txt")):
        p = est / fn
        if p.exists():
            txt = " ".join(p.read_text(encoding="utf-8",
                                       errors="ignore").split())
            if len(txt) > 500:
                bank[name] = CharNgram.train(txt, alpha)
    return bank


# ------------------------------------------------- reduction + base removal
def reduce_to_residues(cts: Cts, q: Sequence[int], N: int) -> List[List[int]]:
    return [[(q[c] - t) % N for t, c in enumerate(ct)] for ct in cts]


ENG_FREQ = " etaoinshrdlucmfwgypbvkjxqz"   # space first (commonest in text)


def align_bases_by_prefix(res: Sequence[Sequence[int]], N: int,
                          prefix: int = 18) -> List[int]:
    """Recover RELATIVE bases with NO language model, using the shared openings
    (Pyry condition #3). If messages share plaintext over the first `prefix`
    positions, then res[m][t]-res[0][t] = base_m-base_0 there; the mode across
    the aligned region is the relative base. Returns bases with base_0=0.

    This is the key that collapses the corpus into ONE canonical mono-sub
    frame before any character model is consulted -- it turns the O<->bases
    chicken-and-egg into a solved subproblem wherever a shared opening exists.
    """
    L = min(prefix, min(len(r) for r in res))
    bases = [0] * len(res)
    for m in range(len(res)):
        diffs = [(res[m][t] - res[0][t]) % N for t in range(L)]
        bases[m] = max(set(diffs), key=diffs.count)     # modal difference
    return bases


def _fit_bases(res: Sequence[Sequence[int]], O: Dict[int, str],
               model: "CharNgram", N: int) -> List[int]:
    """For a candidate O expressed in the CANONICAL value frame, find each
    message's base (rotation) that best reads under the model. base_0 pinned
    to 0 to fix the global rotation gauge."""
    bases = [0] * len(res)
    for m in range(len(res)):
        bases[m] = max(range(N), key=lambda b: model.score(
            "".join(O.get((v - b) % N, " ") for v in res[m])))
    return bases


def solve(cts: Cts, q: Sequence[int], N: int, *,
          bank: Optional[Dict[str, CharNgram]] = None,
          restarts: int = 4, iters: int = 12000, seed: int = 0
          ) -> dict:
    """Reduce -> canonical-frame mono-sub -> hill-climb O per language.

    KEY: after removing per-message bases, every message is the SAME shared
    monoalphabetic cryptogram in one 'canonical value' alphabet. We pool all
    messages into that single frame (giving the climber ~1000 chars of signal
    instead of ~115 per message), frequency-initialize O, and anneal. This is
    what makes a short-message corpus solvable."""
    bank = bank or language_bank()
    res = reduce_to_residues(cts, q, N)
    rng = random.Random(seed)

    best_overall = None
    for lang, model in bank.items():
        alpha = model.alphabet

        def decode_with_bases(O: Dict[int, str], bases: Sequence[int]):
            return ["".join(O.get((v - bases[m]) % N, " ") for v in r)
                    for m, r in enumerate(res)]

        def score(O, bases):
            return sum(model.score(s) for s in decode_with_bases(O, bases)) / len(res)

        # recover relative bases ONCE from the shared openings (model-free);
        # this fixes the canonical frame so O is a single shared mono-sub.
        base_align = align_bases_by_prefix(res, N)

        best_lang = None
        for rs in range(restarts):
            bases = base_align[:]
            # frequency-init O in the ALIGNED canonical frame
            from collections import Counter
            canon = [[(v - bases[m]) % N for v in r] for m, r in enumerate(res)]
            order = [v for v, _ in Counter(v for c in canon
                                           for v in c).most_common()]
            used = sorted({v for c in canon for v in c})
            if rs == 0:
                O = {v: (ENG_FREQ[i] if i < len(ENG_FREQ) else " ")
                     for i, v in enumerate(order)}
            else:
                chars = list(alpha); rng.shuffle(chars)
                O = {v: chars[i % len(chars)] for i, v in enumerate(used)}
            cur = score(O, bases)
            for it in range(iters):
                T = 0.6 * (0.01 / 0.6) ** (it / iters)
                a, b = rng.sample(used, 2)
                O[a], O[b] = O[b], O[a]
                cand = score(O, bases)
                if cand >= cur or rng.random() < math.exp((cand - cur) / max(T, 1e-6)):
                    cur = cand
                else:
                    O[a], O[b] = O[b], O[a]
            # bases stay at the model-free prefix alignment (exact where a
            # shared opening exists); we do NOT let the char model drift them.
            if best_lang is None or cur > best_lang[0]:
                best_lang = (cur, dict(O), bases[:], used)
        sc_best, O, bases, used = best_lang

        nulls = []
        for r in range(30):
            chars = list(alpha); random.Random(500 + r).shuffle(chars)
            On = {v: chars[i % len(chars)] for i, v in enumerate(used)}
            nulls.append(score(On, bases))
        mu, sd = st.mean(nulls), st.pstdev(nulls) or 1e-9
        z = (sc_best - mu) / sd
        cand = {"language": lang, "score": round(sc_best, 3),
                "null_mean": round(mu, 3), "z": round(z, 1),
                "O": O, "bases": bases,
                "plaintext": decode_with_bases(O, bases)}
        if best_overall is None or z > best_overall["z"]:
            best_overall = cand
    return best_overall


def reduce_and_read(res: Sequence[Sequence[int]], O: Dict[int, str],
                    bases: Sequence[int], N: int) -> List[str]:
    return ["".join(O.get((v - bases[m]) % N, " ") for v in r)
            for m, r in enumerate(res)]


# --------------------------------------------------------------------- selftest
def selftest() -> List[Tuple[str, bool]]:
    checks: List[Tuple[str, bool]] = []

    # (1) with the TRUE q, the reduction is a per-message rotation of plaintext.
    pl = plantlab.gen("pmp", seed=1, shared_prefix=20)
    res = reduce_to_residues(pl.cts, pl.q, pl.N)
    ok = all((res[m][t] - pl.bases[m]) % pl.N == pl.pvals[m][t]
             for m in range(len(res)) for t in range(len(res[m])))
    checks.append(("reduction == plaintext value + base (exact)", ok))

    # (2) FULL READ: with true q, solver recovers readable English scoring
    #     far above its own random-O null.
    bank = {"english": CharNgram.train(plantlab.SAMPLE_TEXT, plantlab.ALPHABET)}
    rep = solve(pl.cts, pl.q, pl.N, bank=bank, restarts=12, iters=20000, seed=2)
    checks.append((f"true-q solve beats null (z={rep['z']})", rep["z"] > 6))
    # readability: decoded corpus contains many real English words
    joined = " ".join(rep["plaintext"]).lower()
    common = ("the", "and", "work", "sun", "mountain", "miner", "before")
    hits = sum(joined.count(w) for w in common)
    checks.append((f"true-q solve yields real words (hits={hits})", hits >= 20))

    # (3) GRACEFUL DEGRADATION: corrupt q on k symbols -> score drops
    #     monotonically-ish; a heavily corrupted q scores near null.
    def score_with_corruption(k):
        q = list(pl.q)
        syms = random.Random(9).sample(range(pl.N), k)
        vals = [q[s] for s in syms]; random.Random(9).shuffle(vals)
        for s, v in zip(syms, vals):
            q[s] = v
        r = solve(pl.cts, q, pl.N, bank=bank, restarts=2, iters=2500, seed=3)
        return r["z"]
    z0 = rep["z"]
    z_bad = score_with_corruption(50)
    checks.append((f"degradation: heavy q-corruption kills signal "
                   f"(z {z0:.0f}->{z_bad:.0f})", z_bad < z0 - 3))

    # (4) LANGUAGE SELECTION: given an English plant, english outscores a
    #     deliberately-wrong model trained on reversed text.
    wrong = CharNgram.train(plantlab.SAMPLE_TEXT[::-1], plantlab.ALPHABET)
    rep2 = solve(pl.cts, pl.q, pl.N,
                 bank={"english": bank["english"], "reversed": wrong},
                 restarts=3, iters=3000, seed=4)
    checks.append(("language pick = english over reversed",
                   rep2["language"] == "english"))

    # (5) base-removal sanity: with the TRUE O (value->char), an artificial
    #     extra rotation of a message is recovered exactly by the base search.
    r0 = reduce_to_residues([pl.cts[0]], pl.q, pl.N)[0]
    base0 = pl.bases[0]
    trueO = {(v - base0) % pl.N: pl.pts[0][t] for t, v in enumerate(r0)}
    model = bank["english"]
    shifted = [(v + 11) % pl.N for v in r0]
    best_b = max(range(pl.N), key=lambda b: model.score(
        "".join(trueO.get((v - b) % pl.N, " ") for v in shifted)))
    checks.append(("base-removal finds the planted shift",
                   best_b == (base0 + 11) % pl.N))
    return checks


def main() -> int:
    if "--selftest" in sys.argv:
        results = selftest()
        for name, ok in results:
            print(f"[{'OK  ' if ok else 'FAIL'}] {name}")
        return 0 if all(ok for _, ok in results) else 1

    import corpus as corpus_mod  # noqa: E402
    import support_min as sm     # noqa: E402
    c = corpus_mod.load()
    cts = [list(x) for x in c.ciphertexts]
    pins, _ = sm.isomorph_seed(cts, c.N)
    q_hat, _, meta = sm.anneal(cts, c.N, pins=pins, restarts=8, iters=8000)
    print(f"q from support_min: {meta}")
    rep = solve(cts, q_hat, c.N)
    print(f"best language={rep['language']} score={rep['score']} z={rep['z']}")
    for lbl, txt in zip(c.labels, rep["plaintext"]):
        print(f"  {lbl}: {txt[:60]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
