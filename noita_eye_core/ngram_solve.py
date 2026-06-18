"""Crib-seeded English n-gram solver for the per-message-progressive eye cipher.

Model (corrected): c[m][t] = C[(p[m][t] + base_m + t) mod N], so
    char[m][t] = O[(q[c[m][t]] - base_m - t) mod N],   q = C^{-1}, O = value->char.

Why n-gram, not IoC: maximising IoC is degenerate (order-blind) — a plant test
recovers a WRONG alphabet at near-true IoC. n-gram log-probability captures letter
ORDER and identifies language, so it is not fooled that way.

Why crib-seeded: a blind solve needs TWO coupled 83-permutations (q and O). A
correct refrain crib + an ordering hypothesis O pins q on ~59 of 83 symbols
(per-message-progressive), collapsing the search to the ~24 residual symbols +
per-message bases. THAT is tractable, and n-gram fitness over the whole corpus
(refrain region anchored to the crib) discriminates the right residual.

This solver therefore takes (crib phrase, offset, ordering O) and:
  1. pins q from the refrain (rejecting crib/O that contradict),
  2. hill-climbs the residual q-entries (a permutation of the unused values),
  3. scores English character trigrams of the full decryption, searching each
     message's base (83) — base search is per message, trigram-scored.
A correct (crib, O) lights the corpus up as English; nulls do not.

Honest scope: it needs the ORDERING O (default = the noita-alphabet2 char order);
a wrong O fails even with the right crib. Validated on an English plant below.
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import refrain as rf

# Compact English training text for the character trigram model (prose; the solver
# only needs relative letter-order statistics, not a huge corpus).
_ENGLISH = (
    "the truth is that there is nothing more valuable than knowledge and those who "
    "seek it in the dark beneath the world will find that the gods are watching. we "
    "see a true seeker of knowledge and you are so close to being enlightened now. "
    "do you believe yourself nearer the gods by solving this message. when you have "
    "nothing left to seek the people will rejoice and dance for the great work is "
    "done and the secrets of the all seeing eye are revealed to the worthy alone. "
    "whoever would give everything for true knowledge must first prove devotion to "
    "the old ones who came before and shaped the heavens and the deep places of "
    "stone and water and fire and the eternal night that waits beyond the stars. "
    "three eyes are watching you always and they know the name you have forgotten."
) * 3


def _alphabet_default() -> str:
    return rf.DEFAULT_ALPHABET


class TrigramModel:
    """Character trigram log-prob with add-k smoothing over a fixed alphabet."""

    def __init__(self, alphabet: str, text: str, add_k: float = 0.2):
        self.alphabet = alphabet
        self.idx = {ch: i for i, ch in enumerate(alphabet)}
        A = len(alphabet)
        self.A = A
        seq = [self.idx[ch] for ch in text if ch in self.idx]
        self.uni = math.log(1.0 / A)
        bi = defaultdict(lambda: add_k)
        bi_tot = defaultdict(lambda: add_k * A)
        tri = defaultdict(lambda: add_k)
        tri_tot = defaultdict(lambda: add_k * A)
        for i in range(len(seq)):
            if i >= 1:
                bi[(seq[i - 1], seq[i])] += 1.0
                bi_tot[seq[i - 1]] += 1.0
            if i >= 2:
                tri[(seq[i - 2], seq[i - 1], seq[i])] += 1.0
                tri_tot[(seq[i - 2], seq[i - 1])] += 1.0
        self.bi, self.bi_tot, self.tri, self.tri_tot = bi, bi_tot, tri, tri_tot
        self.add_k = add_k

    def score_idx(self, seq: Sequence[int]) -> float:
        """Mean trigram log-prob per char (chars given as alphabet indices)."""
        if len(seq) < 3:
            return -1e9
        total = 0.0
        for i in range(2, len(seq)):
            a, b, c = seq[i - 2], seq[i - 1], seq[i]
            num = self.tri.get((a, b, c), self.add_k)
            den = self.tri_tot.get((a, b), self.add_k * self.A)
            total += math.log(num / den)
        return total / (len(seq) - 2)


@dataclass
class SolveResult:
    consistent: bool
    score: float                       # mean trigram log-prob of best decryption
    null_mean: float
    null_sd: float
    z: float
    pinned: int                        # q entries pinned by the crib
    plaintext: Dict[int, str] = field(default_factory=dict)   # message idx -> text
    bases: Dict[int, int] = field(default_factory=dict)


def _decrypt_msg_chars(msg, qmap, base, alphabet, N):
    return [(qmap[int(c)] - base - t) % N for t, c in enumerate(msg) if int(c) in qmap]


def _best_base_score(msg, qmap, alphabet, model, N):
    """Search the per-message base (0..N-1) maximising the trigram score."""
    best_b, best_s, best_seq = 0, -1e9, []
    # decrypt to values up to base: u[t] = q[c]-t ; char index = (u - base) mod N
    u = [(qmap[int(c)] - t) % N for t, c in enumerate(msg) if int(c) in qmap]
    if len(u) < 3:
        return 0, -1e9, []
    for b in range(N):
        seq = [(x - b) % N for x in u]
        s = model.score_idx(seq)
        if s > best_s:
            best_s, best_b, best_seq = s, b, seq
    return best_b, best_s, best_seq


def solve(messages, crib, offset, N, alphabet=None, model=None,
          region=None, restarts: int = 6, iters: int = 1500, seed: int = 0,
          n_null: int = 60) -> SolveResult:
    import numpy as np
    if alphabet is None:
        alphabet = _alphabet_default()
    if model is None:
        model = TrigramModel(alphabet, _ENGLISH)
    if region is None:
        region = rf.DEFAULT_INSTANCES
    P = len(crib)
    inst = [(m, p + offset) for (m, p) in region]
    pv = rf.phrase_to_values(crib, alphabet, N)
    if pv is None:
        return SolveResult(False, 0, 0, 0, 0, 0)
    pinned, contra = rf.pin_from_refrain(messages, pv, inst, N)
    if contra is not None:
        return SolveResult(False, 0, 0, 0, 0, len(pinned))

    used_vals = set(pinned.values())
    all_syms = set(int(s) for m in messages for s in m)
    free_syms = [s for s in all_syms if s not in pinned]
    free_vals = [v for v in range(N) if v not in used_vals]
    rng = np.random.default_rng(seed)

    def total_score(qmap):
        s = 0.0
        cnt = 0
        for m in messages:
            _, sc, seq = _best_base_score(m, qmap, alphabet, model, N)
            if seq:
                s += sc * len(seq); cnt += len(seq)
        return s / max(1, cnt)

    best = None
    for r in range(restarts):
        perm = list(free_vals)
        rng.shuffle(perm)
        qmap = dict(pinned)
        for s, v in zip(free_syms, perm):
            qmap[s] = v
        cur = total_score(qmap)
        for _ in range(iters):
            i, j = int(rng.integers(0, len(free_syms))), int(rng.integers(0, len(free_syms)))
            if i == j:
                continue
            si, sj = free_syms[i], free_syms[j]
            qmap[si], qmap[sj] = qmap[sj], qmap[si]
            ns = total_score(qmap)
            if ns >= cur:
                cur = ns
            else:
                qmap[si], qmap[sj] = qmap[sj], qmap[si]
        if best is None or cur > best[0]:
            best = (cur, dict(qmap))

    qmap = best[1]
    # Decrypt the corpus under the best alphabet (per-message best base).
    plaintext, bases, dec_seqs = {}, {}, []
    for mi, m in enumerate(messages):
        b, _, seq = _best_base_score(m, qmap, alphabet, model, N)
        bases[mi] = b
        dec_seqs.append(seq)
        plaintext[mi] = "".join(alphabet[x] if x < len(alphabet) else "·" for x in seq)

    # NULL: shuffle each decrypted message (destroys trigram ORDER but keeps the
    # symbol multiset) and rescore. A genuine English decryption scores far above
    # its shuffles; gibberish scores ~the same. This is the order-sensitive test
    # (random-crib nulls are useless here: they almost all contradict).
    nulls = []
    for _ in range(n_null):
        s = 0.0; cnt = 0
        for seq in dec_seqs:
            if len(seq) >= 3:
                sh = list(seq); rng.shuffle(sh)
                s += model.score_idx(sh) * len(sh); cnt += len(sh)
        nulls.append(s / max(1, cnt))
    nm = float(np.mean(nulls)) if nulls else 0.0
    nsd = float(np.std(nulls)) if nulls else 1e-9
    return SolveResult(True, best[0], nm, nsd, (best[0] - nm) / (nsd + 1e-9),
                       len(pinned), plaintext, bases)


# ---------------------------------------------------------------------------
# Selftest — recover planted English under per-message-progressive with the crib.
# ---------------------------------------------------------------------------

def selftest() -> List[Tuple[str, bool]]:
    import numpy as np
    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(0)
    alphabet = _alphabet_default()
    model = TrigramModel(alphabet, _ENGLISH)
    idx = {ch: i for i, ch in enumerate(alphabet)}

    # build English-plaintext messages; embed a fixed refrain at 4 positions in 2 msgs
    eng = [idx[ch] for ch in _ENGLISH if ch in idx]
    T, Mn = 110, 5
    O = list(range(N))                       # plaintext ordering = identity over the
    # alphabet indexing (so value v renders as alphabet[v]); this IS O.
    C = list(rng.permutation(N))             # secret cipher alphabet
    bases = [int(b) for b in rng.integers(0, N, size=Mn)]
    crib_chars = "trueknowledge"
    crib_vals = [idx[ch] for ch in crib_chars]
    insts = [(0, 38), (0, 68), (1, 43), (1, 78)]
    msgs = []
    pos0 = 0
    for m in range(Mn):
        p = [eng[(pos0 + i) % len(eng)] for i in range(T)]
        pos0 += T
        for (mm, ps) in insts:
            if mm == m:
                p[ps:ps + len(crib_vals)] = crib_vals
        msgs.append([C[(p[t] + bases[m] + t) % N] for t in range(T)])

    # CORRECT crib at offset 0 -> consistent, high trigram z, refrain reads as crib
    res = solve(msgs, crib_chars, 0, N, alphabet=alphabet, model=model,
                region=insts, restarts=3, iters=600, n_null=40)
    out.append(("correct crib is consistent", res.consistent))
    out.append(("correct crib pins many symbols (>=30)", res.pinned >= 30))
    out.append(("correct crib scores well above null (z>=4)", res.z >= 4))
    # the refrain region should read back as the crib in the decryption
    reads_crib = crib_chars[:6] in res.plaintext.get(0, "") or \
        crib_chars[:6] in res.plaintext.get(1, "")
    out.append(("decryption reproduces the crib text somewhere", reads_crib))

    # WRONG crib -> rejected OR low z
    bad = solve(msgs, "zzzqxkjwvbfgh"[:len(crib_chars)], 0, N, alphabet=alphabet,
                model=model, region=insts, restarts=2, iters=300, n_null=30)
    out.append(("a wrong crib is rejected OR scores low (z<3)",
                (not bad.consistent) or bad.z < 3))

    # trigram model sanity: English scores higher than shuffled
    eng_idx = [idx[ch] for ch in "thetruthisthatthereisnothing" if ch in idx]
    import random as _r
    sh = eng_idx[:]; _r.Random(1).shuffle(sh)
    out.append(("trigram model: English > shuffled",
                model.score_idx(eng_idx) > model.score_idx(sh)))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} ngram_solve checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
