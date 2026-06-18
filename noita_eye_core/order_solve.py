"""Ordering-search solver: recover the plaintext-alphabet ordering from a crib.

Unlike ngram_solve (which needs the ordering O as input), this searches O too.

Pipeline (per-message-progressive, c[m][t]=C[(p[m][t]+base_m+t)]):
  1. PIN STRUCTURE, ordering-FREE. From the crib's letter-PATTERN (same letter ->
     same plaintext value) + the ciphertext, solve a GF(83) system over variables
     {x[symbol]=C^{-1}, base_m, P[i]=refrain plaintext values} with constraints
     x[c]=P[i]+base_m+(pos+i) and P[i]=P[j] for equal crib letters. A contradiction
     here means the crib's letter-pattern is INCOMPATIBLE with the ciphertext
     (reported with the offending slot) — this needs NO ordering.
  2. DECRYPT covered positions to plaintext VALUES (p[t]=x[c]-t), per message up to
     a constant shift.
  3. HILL-CLIMB the ordering O (value->char) + per-message shifts to maximise
     English character-trigram likelihood; report dictionary word-coverage as the
     acceptance gate. The crib's letters anchor O at the refrain.

Scoring is n-gram likelihood (order-sensitive), NOT IoC (IoC is degenerate). A wrong
crib still yields diagnostics: contradiction slot, score-vs-null gradient, partial
word hits, and which symbols got pinned.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from isomorph import GFSystem
import refrain as rf
import ngram_solve as ng

# A small common-English word set for the acceptance gate (word-coverage).
_WORDS = set((
    "the of and to in is that it for as with was his he be not by but are this "
    "from or have an they which one you were her all she there would their we him "
    "been has when who will more no if out so what up its about into them can only "
    "other new some could time these two may then do first any my now such like our "
    "over man me even most made after also did many before must through back where "
    "much your way well down should because each just those people how too little "
    "state good very make world still see own men work long here both life being "
    "under never day same know while last might great old year off come since "
    "against go came right used take three eyes eye god gods truth true knowledge "
    "seek seeker secret message death dark light deep stone water fire night star "
    "watch watching nothing everything devotion sacred ancient soul mind name "
    "believe yourself nearer solving worthy revealed wisdom power blood gold "
    "above below heaven hell abyss void cosmos within without beyond"
).split())


@dataclass
class OrderSolveResult:
    consistent: bool
    contradiction_slot: Optional[Tuple[int, int]]
    symbols_pinned: int
    coverage: float
    score: float                 # best trigram log-prob
    null_mean: float
    null_sd: float
    z: float
    word_coverage: float         # fraction of decrypted tokens that are real words
    plaintext: Dict[int, str] = field(default_factory=dict)


def pin_structure(messages, crib, instances, N):
    """Ordering-free GF pin. Returns (x:{symbol->C^{-1} value}, contradiction_slot).
    Variables: symbols 0..N-1; bases N+j (j over distinct refrain messages);
    P[i] = N + M + i (refrain plaintext values)."""
    msgs_in = sorted({m for m, _ in instances})
    base_var = {m: N + j for j, m in enumerate(msgs_in)}
    M = len(msgs_in)
    L = len(crib)
    P_var = {i: N + M + i for i in range(L)}
    gf = GFSystem(N)
    # gauge: first base = 0
    gf.add({base_var[msgs_in[0]]: 1}, 0)
    # crib letter equalities P[i]=P[j]
    first = {}
    for i, ch in enumerate(crib):
        if ch in first:
            gf.add({P_var[first[ch]]: 1, P_var[i]: N - 1}, 0)
        else:
            first[ch] = i
    # core relations x[c] - P[i] - base_m = pos+i
    for inst, (m, pos) in enumerate(instances):
        for i in range(L):
            c = int(messages[m][pos + i])
            row = {c: 1, P_var[i]: N - 1, base_var[m]: N - 1}
            row = {v: cc % N for v, cc in row.items() if cc % N}
            if gf.add(row, (pos + i) % N) == "contradiction":
                return {}, (inst, i), {}
    val = gf.solve()
    x = {s: val[s] for s in range(N) if s in val}
    bases = {m: val.get(base_var[m], 0) % N for m in msgs_in}
    return x, None, bases


def _decrypt_values(messages, x, N):
    out = []
    for m in messages:
        out.append([(x[int(c)] - t) % N if int(c) in x else None
                    for t, c in enumerate(m)])
    return out


def _render(seq_vals, O, shift, N):
    chars = []
    for v in seq_vals:
        if v is None:
            chars.append(" ")
        else:
            idx = (v - shift) % N
            chars.append(O[idx] if idx < len(O) else "·")
    return "".join(chars)


_LONGWORDS = sorted((w for w in _WORDS if len(w) >= 4), key=len, reverse=True)


def _word_coverage(text: str) -> float:
    """Readability proxy robust to gaps: fraction of characters covered by
    dictionary words (len>=4) found as substrings (gaps stripped)."""
    t = "".join(ch for ch in text.lower() if ch.isalpha())
    if len(t) < 4:
        return 0.0
    covered = [False] * len(t)
    for w in _LONGWORDS:
        start = 0
        while True:
            k = t.find(w, start)
            if k < 0:
                break
            for p in range(k, k + len(w)):
                covered[p] = True
            start = k + 1
    return sum(covered) / len(covered)


def _word_hits(text: str, min_len: int = 4) -> List[str]:
    t = "".join(ch for ch in text.lower() if ch.isalpha())
    return sorted({w for w in _LONGWORDS if len(w) >= min_len and w in t}, key=len,
                  reverse=True)


def solve(messages, crib, offset, N, alphabet=None, model=None, region=None,
          restarts: int = 6, iters: int = 2500, seed: int = 0,
          n_null: int = 40) -> OrderSolveResult:
    import numpy as np
    if alphabet is None:
        alphabet = rf.DEFAULT_ALPHABET
    if model is None:
        model = ng.TrigramModel(alphabet, ng._ENGLISH)
    if region is None:
        region = rf.DEFAULT_INSTANCES
    inst = [(m, p + offset) for (m, p) in region]
    x, contra, fixed_bases = pin_structure(messages, crib, inst, N)
    if contra is not None:
        return OrderSolveResult(False, contra, len(x), 0, 0, 0, 0, 0, 0)

    vals = _decrypt_values(messages, x, N)
    aidx = {ch: i for i, ch in enumerate(alphabet)}
    A = len(alphabet)
    rng = np.random.default_rng(seed)

    def _msg_shifts(seq, Oi, mi):
        present = [v for v in seq if v is not None]
        if mi in fixed_bases:               # refrain message: shift is pinned
            return fixed_bases[mi], present
        best, bsh = -1e9, 0                  # else search the per-message shift
        for sh in range(N):
            s = model.score_idx([Oi[(v - sh) % N] for v in present])
            if s > best:
                best, bsh = s, sh
        return bsh, present

    def score_O(O):
        Oi = [aidx[ch] for ch in O]
        total = 0.0; cnt = 0
        for mi, seq in enumerate(vals):
            present = [v for v in seq if v is not None]
            if len(present) < 3:
                continue
            sh, _ = _msg_shifts(seq, Oi, mi)
            idxs = [Oi[(v - sh) % N] for v in present]
            total += model.score_idx(idxs) * len(present); cnt += len(present)
        return total / max(1, cnt)

    # Seed O from the crib: the first refrain instance's values map to crib chars,
    # so anchor those slots and fill the rest. This puts the hill-climb near the
    # solution instead of in random 83! space.
    m0, p0 = inst[0]
    rv = [(x[int(messages[m0][p0 + i])] - (p0 + i)) % N for i in range(len(crib))]
    seed_O = [None] * N
    for i, ch in enumerate(crib):
        seed_O[rv[i] % N] = ch
    leftover = [ch for ch in alphabet if ch not in set(crib)]
    # pad leftover pool to fill all N slots (alphabet may be < N or chars reused)
    pool = leftover + [ch for ch in alphabet]
    pi = 0
    for v in range(N):
        if seed_O[v] is None:
            seed_O[v] = pool[pi % len(pool)]; pi += 1

    best = None
    for r in range(restarts):
        if r == 0:
            O = list(seed_O)                 # crib-anchored seed
        else:
            O = list(seed_O)
            # perturb only the non-anchored slots
            free_slots = [v for v in range(N) if v % N not in {rr % N for rr in rv}]
            sub = [O[v] for v in free_slots]
            rng.shuffle(sub)
            for v, ch in zip(free_slots, sub):
                O[v] = ch
        cur = score_O(O)
        anchored = {rr % N for rr in rv}
        free = [v for v in range(N) if v not in anchored]
        for _ in range(iters):
            i = free[int(rng.integers(0, len(free)))]
            j = free[int(rng.integers(0, len(free)))]
            if i == j:
                continue
            O[i], O[j] = O[j], O[i]
            s = score_O(O)
            if s >= cur:
                cur = s
            else:
                O[i], O[j] = O[j], O[i]
        if best is None or cur > best[0]:
            best = (cur, list(O))

    bestO = best[1]
    Oi = [aidx[bestO[v]] for v in range(N)]
    plaintext = {}
    all_text = []
    for mi, seq in enumerate(vals):
        sh, _ = _msg_shifts(seq, Oi, mi)
        txt = _render(seq, bestO, sh, N)
        plaintext[mi] = txt
        all_text.append(txt)
    wcov = _word_coverage(" ".join(all_text))

    # null: shuffled decryption (order destroyed)
    nulls = []
    for _ in range(n_null):
        sc = 0.0; cnt = 0
        for seq in vals:
            present = [Oi[v] for v in seq if v is not None]
            if len(present) >= 3:
                sh = list(present); rng.shuffle(sh)
                sc += model.score_idx(sh) * len(sh); cnt += len(sh)
        nulls.append(sc / max(1, cnt))
    nm = float(np.mean(nulls)) if nulls else 0.0
    nsd = float(np.std(nulls)) if nulls else 1e-9
    tot = sum(len(m) for m in messages)
    cov = sum(1 for seq in vals for v in seq if v is not None) / tot
    return OrderSolveResult(True, None, len(x), cov, best[0], nm, nsd,
                            (best[0] - nm) / (nsd + 1e-9), wcov, plaintext)


# ---------------------------------------------------------------------------
# Selftest — recover ordering from a crib on a per-message-progressive English plant
# ---------------------------------------------------------------------------

def selftest() -> List[Tuple[str, bool]]:
    import numpy as np
    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(0)
    alphabet = rf.DEFAULT_ALPHABET
    model = ng.TrigramModel(alphabet, ng._ENGLISH)
    aidx = {ch: i for i, ch in enumerate(alphabet)}

    eng = [aidx[ch] for ch in ng._ENGLISH if ch in aidx]
    T, Mn = 110, 4
    C = list(rng.permutation(N))
    bases = [int(b) for b in rng.integers(0, N, size=Mn)]
    # a full-region (~25-glyph) crib: enough to pin DISTINCT plaintext values
    # (a 13-char crib under-determines the alphabet -> the search can't read out).
    crib = "trueknowledgeofthegodsabo"
    cv = [aidx[ch] for ch in crib]
    insts = [(0, 30), (0, 70), (1, 35), (1, 75)]
    msgs = []; pos0 = 0
    for m in range(Mn):
        p = [eng[(pos0 + i) % len(eng)] for i in range(T)]; pos0 += T
        for (mm, ps) in insts:
            if mm == m:
                p[ps:ps + len(cv)] = cv
        msgs.append([C[(p[t] + bases[m] + t) % N] for t in range(T)])

    # structure pins ordering-free, with DISTINCT values for distinct crib letters
    x, contra, _ = pin_structure(msgs, crib, insts, N)
    out.append(("structure pin: correct crib is consistent (no contradiction)",
                contra is None))
    out.append(("structure pin: covers many symbols (>=45)", len(x) >= 45))
    m0, p0 = insts[0]
    rv = [(x[int(msgs[m0][p0 + i])] - (p0 + i)) % N for i in range(len(crib))]
    distinct_ok = len(set(rv)) == len({ch for ch in crib})
    out.append(("structure pin: distinct crib letters get distinct values "
                "(sufficient crib)", distinct_ok))

    # full ordering solve: recovers readable English
    res = solve(msgs, crib, 0, N, alphabet=alphabet, model=model, region=insts,
                restarts=3, iters=3000, n_null=25)
    out.append(("ordering solve scores far above null (z>=8)", res.z >= 8))
    hits = _word_hits(" ".join(res.plaintext.values()))
    out.append(("ordering solve recovers real English words (>=4 distinct, len>=4)",
                len(hits) >= 4))

    # WRONG-crib diagnostic: incompatible letter-pattern -> contradiction (value!)
    x2, contra2, _ = pin_structure(msgs, "a" * len(crib), insts, N)
    out.append(("wrong crib (all-same letters) -> contradiction with a located slot",
                contra2 is not None))

    # WRONG but consistent crib -> few/no words (not a false hit)
    bad_crib = ("qzxjvkwbfgpmhdc" * 2)[:len(crib)]
    res3 = solve(msgs, bad_crib, 0, N, alphabet=alphabet, model=model, region=insts,
                 restarts=2, iters=800, n_null=20)
    bad_hits = _word_hits(" ".join(res3.plaintext.values())) if res3.consistent else []
    out.append(("wrong consistent crib -> few real words (<4) or rejected",
                (not res3.consistent) or len(bad_hits) < 4))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} order_solve checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
