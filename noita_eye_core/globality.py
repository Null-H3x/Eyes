"""Crib-globality test — is the keystream GLOBAL (one for all nine) or LOCAL?

The depth map showed we can prove keystream-sharing only where ciphertext
coincides; whether the BODY keystream is global is undetermined from ciphertext
statistics (the flat unigram defeats every key-free test).  A crib breaks the
stalemate — but NOT on its own.  A crib pins the keystream only over its ~8-symbol
span, and over so few columns the implied plaintext is just the (flat) ciphertext
columns shifted, so a generator-free crib carries no globality signal.  (The
selftest proves this powerlessness explicitly.)

The version with power routes through a GENERATOR: a crib in one message filters
candidate seeds (the keyscan crib bridge); a seed yields the keystream
*everywhere*, so we can decrypt ALL nine messages and ask whether they *jointly*
become structured.

  * One seed (from a crib in one message) makes the WHOLE corpus structured
    -> GLOBAL keystream; depth opens up to nine.
  * It makes only the crib's own triplet structured -> LOCAL (per-triplet).
  * Nothing -> no seed in range for these generators (an exclusion).

This assumes a generator family (a real assumption), but it reuses validated
machinery (keyscan decrypt + repeat-pattern crib filter) and is calibrated
against a random-seed null so a verdict is trustworthy rather than wishful.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

import keyscan

N_DEFAULT = 83
TRIPLETS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))


def per_message_structure(decrypts: Sequence[Sequence[int]], body_start: int = 0
                          ) -> List[float]:
    return [keyscan.structure_score([d], body_start) for d in decrypts]


def repeat_filter_seeds(message: Sequence[int], word: str, position: int,
                        generator: str, seed_start: int, count: int, N: int,
                        Lmax: int) -> List[int]:
    """Seeds whose keystream is consistent with ``word``'s repeat pattern sitting
    at ``position`` in ``message`` (mapping-free, additive)."""
    cons = keyscan.repeat_constraints(word)
    req = [(i, j, (message[position + i] - message[position + j]) % N)
           for (i, j) in cons]
    genfn = keyscan.SCALAR_GENERATORS[generator]
    out: List[int] = []
    for s in range(seed_start, seed_start + count):
        ks = genfn(s, N, Lmax)
        if all((ks[position + i] - ks[position + j]) % N == d for (i, j, d) in req):
            out.append(s)
    return out


@dataclass
class GlobalityResult:
    seed: int
    structured: List[bool]          # per message: decrypt clears the null?
    z: List[float]
    n_structured: int
    verdict: str                    # "global" | "local" | "partial" | "none"
    crib_triplet: Tuple[int, ...] = ()


def score_seed(messages: Sequence[Sequence[int]], seed: int, generator: str,
               combiner: str, N: int, body_start: int,
               mu: Sequence[float], sd: Sequence[float], crib_member: int,
               z_thr: float = 3.0) -> GlobalityResult:
    dec = keyscan.decrypt_triplet(messages, seed, generator, combiner, N)
    sc = per_message_structure(dec, body_start)
    z = [(sc[i] - mu[i]) / (sd[i] or 1e-9) for i in range(len(messages))]
    structured = [zi > z_thr for zi in z]
    n = sum(structured)
    crib_trip = next((t for t in TRIPLETS if crib_member in t), ())
    in_trip = sum(1 for i in crib_trip if structured[i])
    if n >= len(messages) - 1:
        verdict = "global"
    elif in_trip == len(crib_trip) and n <= len(crib_trip) + 1:
        verdict = "local"
    elif n >= 2:
        verdict = "partial"
    else:
        verdict = "none"
    return GlobalityResult(seed, structured, z, n, verdict, crib_trip)


def crib_globality_test(messages: Sequence[Sequence[int]], word: str,
                        position: int, member: int, generator: str,
                        combiner: str, seed_start: int, count: int,
                        N: int = N_DEFAULT, body_start: int = 0,
                        decoy_seeds: int = 200, z_thr: float = 3.0
                        ) -> List[GlobalityResult]:
    msgs = [list(m) for m in messages]
    Lmax = max(len(m) for m in msgs)
    # Per-message decoy null over random seeds.
    rng = np.random.default_rng(0)
    decoy = rng.integers(1_000_000_000, 2_000_000_000, size=decoy_seeds)
    cols = [[] for _ in msgs]
    for s in decoy:
        dec = keyscan.decrypt_triplet(msgs, int(s), generator, combiner, N)
        sc = per_message_structure(dec, body_start)
        for i, v in enumerate(sc):
            cols[i].append(v)
    mu = [float(np.mean(c)) for c in cols]
    sd = [float(np.std(c, ddof=1) or 1e-9) for c in cols]
    # Crib-filtered candidate seeds, scored across ALL messages.
    seeds = repeat_filter_seeds(msgs[member], word, position, generator,
                                seed_start, count, N, Lmax)
    results = [score_seed(msgs, s, generator, combiner, N, body_start, mu, sd,
                          member, z_thr) for s in seeds]
    results.sort(key=lambda r: (-r.n_structured, -max(r.z, default=0)))
    return results


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def _planted_corpus(N: int, T: int, rng, keystreams: List[List[int]],
                    word: str, sigma: Dict[str, int], pos: int, conc: float = 80.0):
    """Build 9 Markov messages; ``keystreams[k]`` is the additive key for message
    k (pass the same list 9× for GLOBAL, or per-triplet for LOCAL).  Plant the
    crib word (with symbols ``sigma``) into message 0."""
    plains = [keyscan._markov(N, T, rng, conc=conc) for _ in range(9)]
    for o, ch in enumerate(word):
        plains[0][pos + o] = sigma[ch]
    return [[(plains[k][t] + keystreams[k][t]) % N for t in range(T)]
            for k in range(9)]


def selftest() -> List[tuple[str, bool]]:
    out: List[tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(11)
    T = 160
    word = "sisaltaa"                      # 3 repeat constraints -> tight filter
    letters = sorted(set(word))
    sigma = {ch: (i * 11 + 4) % N for i, ch in enumerate(letters)}
    pos = 30

    # ---- GLOBAL plant: one seed/keystream for all nine. ----
    S = 5151515
    Kg = keyscan.gen_nolla(S, N, T)
    msgs_g = _planted_corpus(N, T, rng, [Kg] * 9, word, sigma, pos)
    resg = crib_globality_test(msgs_g, word, pos, member=0, generator="nolla",
                               combiner="add", seed_start=S - 3000, count=6000,
                               N=N, body_start=0, decoy_seeds=80)
    out.append(("global plant: true seed recovered by the crib filter",
                any(r.seed == S for r in resg)))
    top_g = next((r for r in resg if r.seed == S), None)
    out.append(("global plant: true seed decrypts (almost) ALL nine to structure",
                top_g is not None and top_g.n_structured >= 8))
    out.append(("global plant: verdict is GLOBAL",
                top_g is not None and top_g.verdict == "global"))

    # ---- LOCAL plant: a different keystream per triplet. ----
    seeds3 = [4242424, 7373737, 9191919]
    Ks = [keyscan.gen_nolla(seeds3[ti], N, T) for ti in range(3)]
    per_msg_keys = [Ks[0], Ks[0], Ks[0], Ks[1], Ks[1], Ks[1], Ks[2], Ks[2], Ks[2]]
    msgs_l = _planted_corpus(N, T, rng, per_msg_keys, word, sigma, pos)
    resl = crib_globality_test(msgs_l, word, pos, member=0, generator="nolla",
                               combiner="add", seed_start=seeds3[0] - 3000,
                               count=6000, N=N, body_start=0, decoy_seeds=80)
    top_l = next((r for r in resl if r.seed == seeds3[0]), None)
    out.append(("local plant: crib's seed found",
                top_l is not None))
    out.append(("local plant: it lights up ONLY the crib's own triplet",
                top_l is not None and all(top_l.structured[i] for i in (0, 1, 2))
                and top_l.n_structured <= 4))
    out.append(("local plant: verdict is LOCAL (not global)",
                top_l is not None and top_l.verdict == "local"))

    # ---- Honesty: generator-free has no power on a FLAT corpus. With uniform
    #      plaintext under one global key, the crib-span columns are still ~1/N,
    #      so cross-message column structure cannot discriminate global vs local.
    from collections import Counter
    Pflat = [list(rng.integers(0, N, size=T)) for _ in range(9)]
    Kf = keyscan.gen_nolla(999, N, T)
    flat = [[(Pflat[k][t] + Kf[t]) % N for t in range(T)] for k in range(9)]

    def col_ioc(M, a, b):
        vals = []
        for t in range(a, b):
            col = [M[i][t] for i in range(len(M))]
            cnt = Counter(col); n = len(col)
            vals.append(sum(v * (v - 1) for v in cnt.values()) / (n * (n - 1)))
        return float(np.mean(vals))
    out.append(("honesty: under a flat corpus the crib-span column IoC is ~1/N, "
                "so a generator-free globality test has no power",
                col_ioc(flat, pos, pos + len(word)) < 3.0 / N))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} globality checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
