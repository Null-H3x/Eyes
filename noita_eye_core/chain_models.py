"""Model-constrained alphabet chaining — autokey vs per-message progressive.

Free-δ chaining (isomorph.chain_free_delta) is PERMISSIVE: one free offset per
isomorph pair absorbs anything (it is consistent even on two-alphabet and random
controls).  To pin the interrelation / order the alphabet we must CONSTRAIN the
per-pair offset with a model that has FEW free parameters, then test consistency
+ over-determination AND verify the model REJECTS controls it should (the lesson
that free-δ failed).

Two models, with a proof and a warning:

  * AUTOKEY (offset k).  yₜ = C⁻¹(cₜ); autokey-k means yₜ − yₜ₋ₖ = Pₜ (plaintext).
    For an isomorph pair the constraint reduces to fᵢ = fᵢ₋ₖ where
    fᵢ = x[c_{m2}[p2+i]] − x[c_{m1}[p1+i]].  For k=1 this is fᵢ = fᵢ₋₁ ⟹ fᵢ = const
    — IDENTICAL to free-δ.  **Autokey-1 chaining ≡ free-δ chaining**: permissive,
    NOT a discriminator.  We implement it only to demonstrate that equivalence
    (the selftest proves the two give identical consistency), so it is never
    mistaken for new signal.

  * PER-MESSAGE PROGRESSIVE.  cₜ at position t in message m is C[(Pₜ + baseₘ + t)].
    Then x[c] = Pₜ + baseₘ + t, so for an isomorph pair the per-pair offset is
    FORCED to δ = (p2 − p1) + (base_{m2} − base_{m1}) with only M (=9) free
    message bases — far fewer than the per-pair free offsets of free-δ.  This is
    genuinely discriminating: data not of this form over-determines the 9 bases
    and contradicts.  (base_m is also the natural home for the position-0
    "indicator".)

Every "consistent" result is gated by a DISCRIMINATION AUDIT: each model is run
against planted corpora of itself and of the other models / nulls; a model is
trustworthy only if it fits its own plant AND contradicts the controls.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from isomorph import GFSystem, IsoPair, find_isomorphs


@dataclass
class ChainStat:
    model: str
    constraints: int
    contradictions: int
    redundant: int
    rank: int
    symbols_linked: int
    consistent: bool


def _accum(row: Dict[int, int], var: int, coef: int, N: int) -> None:
    row[var] = (row.get(var, 0) + coef) % N


def _solve_stat(model: str, gf: GFSystem, constraints: int, contradictions: int,
                redundant: int, parent: List[int], touched: set) -> ChainStat:
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    comps: Dict[int, int] = defaultdict(int)
    for s in touched:
        comps[find(s)] += 1
    linked = max(comps.values()) if comps else 0
    return ChainStat(model, constraints, contradictions, redundant,
                     len(gf.pivots), linked, contradictions == 0)


# ---------------------------------------------------------------------------
# Model A: autokey offset-k  (k=1 is provably == free-δ; permissive)
# ---------------------------------------------------------------------------

def autokey_chain(messages: Sequence[Sequence[int]], pairs: List[IsoPair],
                  N: int, k: int = 1) -> ChainStat:
    gf = GFSystem(N)
    parent = list(range(N))

    def union(a, b):
        ra, rb = a, b
        while parent[ra] != ra:
            ra = parent[ra]
        while parent[rb] != rb:
            rb = parent[rb]
        parent[ra] = rb
    constraints = contradictions = redundant = 0
    touched: set = set()
    for pr in pairs:
        for i in range(k, pr.length):
            i1a, i1b = pr.p1 + i, pr.p1 + i - k
            i2a, i2b = pr.p2 + i, pr.p2 + i - k
            if i1b < 0 or i2b < 0:
                continue
            A = int(messages[pr.m1][i1a]); B = int(messages[pr.m1][i1b])
            D = int(messages[pr.m2][i2a]); E = int(messages[pr.m2][i2b])
            row: Dict[int, int] = {}
            _accum(row, A, 1, N); _accum(row, B, N - 1, N)
            _accum(row, D, N - 1, N); _accum(row, E, 1, N)
            row = {v: c for v, c in row.items() if c}
            constraints += 1
            res = gf.add(row, 0)
            if res == "contradiction":
                contradictions += 1
            elif res == "redundant":
                redundant += 1
            for s in (A, B, D, E):
                touched.add(s)
            union(A, B); union(D, E); union(A, D)
    return _solve_stat(f"autokey-{k}", gf, constraints, contradictions,
                       redundant, parent, touched)


# ---------------------------------------------------------------------------
# Model B: per-message progressive  (M free message bases; discriminating)
# ---------------------------------------------------------------------------

def per_message_progressive_chain(messages: Sequence[Sequence[int]],
                                  pairs: List[IsoPair], N: int) -> ChainStat:
    M = len(messages)
    gf = GFSystem(N)
    parent = list(range(N))

    def union(a, b):
        ra, rb = a, b
        while parent[ra] != ra:
            ra = parent[ra]
        while parent[rb] != rb:
            rb = parent[rb]
        parent[ra] = rb
    constraints = contradictions = redundant = 0
    touched: set = set()
    for pr in pairs:
        bm1, bm2 = N + pr.m1, N + pr.m2     # base variables (indices N..N+M-1)
        for i in range(pr.length):
            A = int(messages[pr.m1][pr.p1 + i])
            D = int(messages[pr.m2][pr.p2 + i])
            row: Dict[int, int] = {}
            _accum(row, D, 1, N); _accum(row, A, N - 1, N)
            if pr.m1 != pr.m2:
                _accum(row, bm2, N - 1, N); _accum(row, bm1, 1, N)
            # same message: base terms cancel (bm1==bm2) -> nothing added
            row = {v: c for v, c in row.items() if c}
            rhs = (pr.p2 - pr.p1) % N
            constraints += 1
            res = gf.add(row, rhs)
            if res == "contradiction":
                contradictions += 1
            elif res == "redundant":
                redundant += 1
            touched.add(A); touched.add(D)
            union(A, D)
    return _solve_stat("per-msg-progressive", gf, constraints, contradictions,
                       redundant, parent, touched)


def per_message_progressive_recover(messages, pairs, N):
    """Solve the per-message-progressive system; return {symbol: position} (up to
    a global rotation) for the largest linked symbol component, or {} if
    inconsistent."""
    stat = per_message_progressive_chain(messages, pairs, N)
    if not stat.consistent:
        return {}
    M = len(messages)
    gf = GFSystem(N)
    parent = list(range(N))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for pr in pairs:
        bm1, bm2 = N + pr.m1, N + pr.m2
        for i in range(pr.length):
            A = int(messages[pr.m1][pr.p1 + i])
            D = int(messages[pr.m2][pr.p2 + i])
            row: Dict[int, int] = {}
            _accum(row, D, 1, N); _accum(row, A, N - 1, N)
            if pr.m1 != pr.m2:
                _accum(row, bm2, N - 1, N); _accum(row, bm1, 1, N)
            row = {v: c for v, c in row.items() if c}
            gf.add(row, (pr.p2 - pr.p1) % N)
            parent[find(A)] = find(D)
    val = gf.solve()
    comp: Dict[int, List[int]] = defaultdict(list)
    for s in range(N):
        if s in val:
            comp[find(s)].append(s)
    if not comp:
        return {}
    big = max(comp.values(), key=len)
    return {s: val[s] for s in big}


# ---------------------------------------------------------------------------
# Plants for the discrimination audit
# ---------------------------------------------------------------------------

# Plants place a fixed plaintext word W at several KNOWN positions in each
# message, so we can build GROUND-TRUTH isomorph pairs directly (clean: exactly
# the same plaintext at every position), bypassing find_isomorphs' partial/
# misaligned contamination. Using DIFFERENT positions is essential — per-message
# progressive's position-dependence (δ = (p2-p1)+base-diff) only bites across
# differing positions, whereas autokey gives a constant offset there.

_WORD_POS = (10, 30, 55)
_WLEN = 16


def _word_sliding(rng, N):
    """A word whose (word[i]+i) collide at several i, so a SLIDING-alphabet cipher
    (progressive / per-msg-progressive) produces a high-repeat ciphertext skeleton
    that find_isomorphs detects across positions."""
    base = 20
    w = [int(x) for x in rng.integers(0, N, size=_WLEN)]
    for j in (0, 3, 6, 9, 12):
        w[j] = (base - j) % N
    return w


def _word_autokey(rng, N):
    """A word whose internal partial sums collide, so a CIPHERTEXT-AUTOKEY cipher
    (c_t = p_t + c_{t-1}) produces a high-repeat ciphertext skeleton."""
    S = [int(x) for x in rng.integers(0, N, size=_WLEN)]
    for j in (3, 7, 11, 15):
        S[j] = S[0]
    return [S[0]] + [(S[i] - S[i - 1]) % N for i in range(1, _WLEN)]


def clean_pairs(M: int, positions=_WORD_POS, L: int = _WLEN) -> List[IsoPair]:
    inst = [(m, p) for m in range(M) for p in positions]
    pairs = []
    for a in range(len(inst)):
        for b in range(a + 1, len(inst)):
            (m1, p1), (m2, p2) = inst[a], inst[b]
            pairs.append(IsoPair(m1, p1, m2, p2, L, False))
    return pairs


def plant_per_msg_progressive(N, rng, M=6, T=80, C=None):
    if C is None:
        C = list(rng.permutation(N))
    bases = [int(x) for x in rng.integers(0, N, size=M)]
    W = _word_sliding(rng, N)
    msgs = []
    for m in range(M):
        P = list(rng.integers(0, N, size=T))
        for p in _WORD_POS:
            P[p:p + _WLEN] = W
        msgs.append([C[(P[t] + bases[m] + t) % N] for t in range(T)])
    return msgs, C, bases


def plant_autokey(N, rng, M=6, T=80, k=1):
    W = _word_autokey(rng, N)
    msgs = []
    for _ in range(M):
        P = list(rng.integers(0, N, size=T))
        for p in _WORD_POS:
            P[p:p + _WLEN] = W
        c = []
        prev = [int(rng.integers(0, N)) for _ in range(k)]
        for t in range(T):
            cc = (P[t] + prev[t % k]) % N
            c.append(cc); prev[t % k] = cc
        msgs.append(c)
    return msgs


def plant_two_alphabet(N, rng, M=6, T=80):
    C1 = list(rng.permutation(N)); C2 = list(rng.permutation(N))
    W = _word_sliding(rng, N)
    msgs = []
    for m in range(M):
        Cg = C1 if m < M // 2 else C2
        P = list(rng.integers(0, N, size=T))
        for p in _WORD_POS:
            P[p:p + _WLEN] = W
        msgs.append([Cg[(P[t] + t) % N] for t in range(T)])
    return msgs


def discrimination_audit(N, seed=0) -> Dict[str, Dict[str, object]]:
    """Run each model against each plant using GROUND-TRUTH clean pairs. A model
    is trustworthy iff it is consistent on its OWN plant and CONTRADICTS the
    others. (Uses clean pairs to isolate model behaviour from find_isomorphs
    contamination.)"""
    import numpy as np
    rng = np.random.default_rng(seed)
    M = 6
    corpora = {
        "per-msg-prog": plant_per_msg_progressive(N, rng, M=M)[0],
        "autokey": plant_autokey(N, rng, M=M),
        "two-alphabet": plant_two_alphabet(N, rng, M=M),
    }
    pairs = clean_pairs(M)
    out: Dict[str, Dict[str, object]] = {}
    for cname, corp in corpora.items():
        out[cname] = {
            "autokey-1": autokey_chain(corp, pairs, N, k=1),
            "per-msg-prog": per_message_progressive_chain(corp, pairs, N),
        }
    return out


# ---------------------------------------------------------------------------
# Selftest — solver KATs, model recovery on own plant, free-δ equivalence,
# and the discrimination matrix (the paranoia centerpiece).
# ---------------------------------------------------------------------------

def selftest() -> List[tuple[str, bool]]:
    import numpy as np
    import isomorph as iso
    out: List[tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(7)

    # Solver KATs.
    gf = GFSystem(N)
    out.append(("GF solve: x1-x0=5, x2-x1=7 -> x2-x0=12",
                gf.add({1: 1, 0: N - 1}, 5) == "pivot"
                and gf.add({2: 1, 1: N - 1}, 7) == "pivot"))
    sol = gf.solve()
    out.append(("GF solve back-substitution correct",
                (sol.get(2, 0) - sol.get(0, 0)) % N == 12))

    M = 6
    cp = clean_pairs(M)   # ground-truth aligned isomorph pairs (clean by construction)

    # (A) autokey-1 chaining == free-δ chaining (PROOF, empirical).
    mk = plant_autokey(N, rng, M=M, k=1)
    a1 = autokey_chain(mk, cp, N, k=1)
    fd = iso.chain_free_delta(mk, cp, N)
    out.append(("autokey-1 == free-δ (same contradictions)",
                a1.contradictions == fd.contradictions))
    out.append(("autokey-1 == free-δ (same redundancy)",
                a1.redundant == fd.redundant))

    # (B) per-message-progressive: fits its OWN plant and RECOVERS C up to rotation.
    mp, C, bases = plant_per_msg_progressive(N, rng, M=M)
    bstat = per_message_progressive_chain(mp, cp, N)
    out.append(("per-msg-prog: consistent on its own plant", bstat.consistent))
    out.append(("per-msg-prog: over-determined on its own plant",
                bstat.redundant >= 20))
    rec = per_message_progressive_recover(mp, cp, N)
    Cinv = {sym: idx for idx, sym in enumerate(C)}
    syms = [s for s in rec if s in Cinv]
    ok_rot = len(syms) >= 4 and all(
        (rec[syms[0]] - Cinv[syms[0]]) % N == (rec[s] - Cinv[s]) % N for s in syms)
    out.append(("per-msg-prog: recovers C up to rotation on its own plant", ok_rot))

    # (C) DISCRIMINATION (the paranoia centerpiece): per-msg-prog must REJECT
    #     autokey / two-alphabet; autokey-1 (=free-δ) is permissive (accepts all).
    audit = discrimination_audit(N, seed=1)
    out.append(("DISCRIM: per-msg-prog CONSISTENT on per-msg-prog plant",
                audit["per-msg-prog"]["per-msg-prog"].consistent))
    out.append(("DISCRIM: per-msg-prog CONTRADICTS autokey plant",
                not audit["autokey"]["per-msg-prog"].consistent))
    out.append(("DISCRIM: per-msg-prog CONTRADICTS two-alphabet plant",
                not audit["two-alphabet"]["per-msg-prog"].consistent))
    out.append(("DISCRIM: autokey-1 permissive (consistent on per-msg-prog plant)",
                audit["per-msg-prog"]["autokey-1"].consistent))
    out.append(("DISCRIM: autokey-1 permissive (consistent on two-alphabet plant)",
                audit["two-alphabet"]["autokey-1"].consistent))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} chain_models checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
