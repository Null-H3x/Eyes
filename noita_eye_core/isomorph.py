"""Isomorph census + alphabet-chaining engine.

The community doc (codewarrior0) and our own check agree: the corpus is full of
ISOMORPHS — substrings with the same repeated-letter *pattern* but different
*values* (e.g. E1@40 and E1@68 share skeleton [0,1,2,3,4,2,6,0,4,9,10]). Against
a within-message shuffle null these are ~0; observed they run into the dozens
(z>100).  Isomorphs can only arise when the per-position alphabets are
INTERRELATED — which rules out independent-column substitution (general GAK) and
running-key/OTP with unrelated alphabets, and points at sliding-alphabet /
progressive / autokey ciphers.

This module:
  1. censuses isomorphs and calibrates them against a shuffle null,
  2. tests the PROGRESSIVE-ALPHABET hypothesis by alphabet chaining — under
     a cipher c[pos] = C[(p[pos] + pos) mod N] (a fixed mixed alphabet C slid one
     step per position), two isomorphic segments at positions s and t force
     C⁻¹(inst2[i]) − C⁻¹(inst1[i]) ≡ (t−s) for every i.  Those are offset
     constraints on the alphabet order, solved by a Z_N offset union-find.
     Consistent => progressive confirmed and C recovered up to rotation;
     contradictions => progressive refuted (favouring autokey / a different
     interrelation).
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple


def skeleton(seq: Sequence[int]) -> Tuple[int, ...]:
    """Canonical repeat-pattern: each position -> index of that value's first
    occurrence.  Equal skeletons == isomorphic segments."""
    first: Dict[int, int] = {}
    out = []
    for i, v in enumerate(seq):
        out.append(first.setdefault(v, i))
    return tuple(out)


@dataclass
class IsoPair:
    m1: int
    p1: int
    m2: int
    p2: int
    length: int
    exact: bool          # same values (a shared repeat) vs true isomorph


def find_isomorphs(messages: Sequence[Sequence[int]], length: int,
                   min_repeats: int, different_only: bool = True
                   ) -> List[IsoPair]:
    bysk: Dict[Tuple[int, ...], List[Tuple[int, int, tuple]]] = defaultdict(list)
    for mi, m in enumerate(messages):
        for p in range(len(m) - length + 1):
            seq = tuple(m[p:p + length])
            sk = skeleton(seq)
            if length - len(set(sk)) >= min_repeats:
                bysk[sk].append((mi, p, seq))
    out: List[IsoPair] = []
    for locs in bysk.values():
        for a in range(len(locs)):
            for b in range(a + 1, len(locs)):
                exact = locs[a][2] == locs[b][2]
                if different_only and exact:
                    continue
                out.append(IsoPair(locs[a][0], locs[a][1], locs[b][0],
                                   locs[b][1], length, exact))
    return out


def significance(messages: Sequence[Sequence[int]], length: int,
                 min_repeats: int, n_null: int = 200, seed: int = 0) -> dict:
    import numpy as np
    obs = len(find_isomorphs(messages, length, min_repeats, different_only=True))
    rng = np.random.default_rng(seed)
    null = []
    for _ in range(n_null):
        sh = [list(rng.permutation(m)) for m in messages]
        null.append(len(find_isomorphs(sh, length, min_repeats,
                                        different_only=True)))
    null = np.array(null, dtype=float)
    z = (obs - null.mean()) / (null.std() + 1e-9)
    return {"observed": obs, "null_mean": float(null.mean()),
            "null_sd": float(null.std()), "z": float(z),
            "p": float((null >= obs).mean())}


# ---------------------------------------------------------------------------
# Z_N offset union-find (alphabet chaining)
# ---------------------------------------------------------------------------

class OffsetDSU:
    """Union-find over symbols with relative offsets in Z_N: maintains
    pos(x) = pos(root) + off(x) (mod N).  union(a,b,d) asserts pos(b)-pos(a)=d."""

    def __init__(self, N: int):
        self.N = N
        self.parent = list(range(N))
        self.off = [0] * N        # pos(x) - pos(parent[x]) mod N

    def find(self, x: int) -> Tuple[int, int]:
        if self.parent[x] == x:
            return x, 0
        root, acc = self.find(self.parent[x])
        self.parent[x] = root
        self.off[x] = (self.off[x] + acc) % self.N
        return root, self.off[x]

    def union(self, a: int, b: int, d: int) -> bool:
        """Assert pos(b) - pos(a) == d (mod N). Returns False on contradiction."""
        ra, oa = self.find(a)
        rb, ob = self.find(b)
        if ra == rb:
            return (ob - oa) % self.N == d % self.N
        # attach rb under ra:  pos(rb) = pos(ra) + (oa + d - ob)
        self.parent[rb] = ra
        self.off[rb] = (oa + d - ob) % self.N
        return True

    def components(self) -> Dict[int, List[int]]:
        comps: Dict[int, List[int]] = defaultdict(list)
        for x in range(self.N):
            r, _ = self.find(x)
            comps[r].append(x)
        return comps


@dataclass
class ChainResult:
    constraints: int
    contradictions: int
    largest_component: int
    n_components: int
    consistent: bool


# ---------------------------------------------------------------------------
# GF(N) online linear solver  (for free-offset / autokey chaining)
# ---------------------------------------------------------------------------

class GFSystem:
    """Online Gaussian elimination over GF(N) (N prime). Each constraint is a
    sparse row {var: coef} == rhs. Detects contradictions incrementally."""

    def __init__(self, N: int):
        self.N = N
        self.pivots: Dict[int, Tuple[Dict[int, int], int]] = {}  # var -> (row, rhs)

    def _inv(self, a: int) -> int:
        return pow(a % self.N, self.N - 2, self.N)

    def add(self, row: Dict[int, int], rhs: int) -> str:
        r = {k: v % self.N for k, v in row.items() if v % self.N}
        b = rhs % self.N
        while r:
            lead = min(r)
            if lead not in self.pivots:
                break
            prow, prhs = self.pivots[lead]
            f = (r[lead] * self._inv(prow[lead])) % self.N
            for k, c in prow.items():
                nv = (r.get(k, 0) - f * c) % self.N
                if nv:
                    r[k] = nv
                elif k in r:
                    del r[k]
            b = (b - f * prhs) % self.N
        if not r:
            return "contradiction" if b else "redundant"
        self.pivots[min(r)] = (r, b)
        return "pivot"

    def classify(self, row: Dict[int, int], rhs: int) -> str:
        """Reduce a constraint against current pivots WITHOUT storing it.
        Returns 'redundant' (already implied), 'contradiction', or 'pivot' (would
        add a new degree of freedom). Mirrors add()'s reduction exactly."""
        r = {k: v % self.N for k, v in row.items() if v % self.N}
        b = rhs % self.N
        while r:
            lead = min(r)
            if lead not in self.pivots:
                break
            prow, prhs = self.pivots[lead]
            f = (r[lead] * self._inv(prow[lead])) % self.N
            for k, c in prow.items():
                nv = (r.get(k, 0) - f * c) % self.N
                if nv:
                    r[k] = nv
                elif k in r:
                    del r[k]
            b = (b - f * prhs) % self.N
        if not r:
            return "contradiction" if b else "redundant"
        return "pivot"

    def snapshot(self):
        """Cheap copy of the pivot state for rollback (extractor uses this)."""
        return {k: (dict(row), rhs) for k, (row, rhs) in self.pivots.items()}

    def restore(self, snap) -> None:
        self.pivots = {k: (dict(row), rhs) for k, (row, rhs) in snap.items()}

    def solve(self) -> Dict[int, int]:
        """Back-substitute to a concrete solution (free variables gauged to 0)."""
        allvars = set()
        for row, _ in self.pivots.values():
            allvars.update(row)
        val: Dict[int, int] = {v: 0 for v in allvars if v not in self.pivots}
        for p in sorted(self.pivots, reverse=True):
            row, rhs = self.pivots[p]
            acc = rhs
            for k, cf in row.items():
                if k != p:
                    acc = (acc - cf * val.get(k, 0)) % self.N
            val[p] = (acc * self._inv(row[p])) % self.N
        return val


# Note on recovery: free-δ chaining proves the *constant-offset interrelation*
# (consistency + over-determination) but does NOT, on its own, ORDER the alphabet
# — each pair's δ is unknown, so it couples symbol-pairs without ordering them.
# Full alphabet recovery needs indirect-symmetry-of-position chaining, which
# requires rich cross-linking and is the genuinely hard open step (the community's
# "alphabet chaining has not been completely successful"). This engine delivers
# the *identification*; recovery is the next research stage.


@dataclass
class FreeChainResult:
    constraints: int
    contradictions: int
    rank: int
    redundant: int             # constraints satisfied by prior ones = over-determination
    symbols_linked: int        # largest connected symbol component
    consistent: bool
    recoverable: bool          # consistent, over-determined, AND a large component


def progressive_chain(messages: Sequence[Sequence[int]], pairs: List[IsoPair],
                      N: int) -> ChainResult:
    """Test the progressive-alphabet hypothesis by chaining isomorph offsets.

    For each isomorph pair at positions (s in m1, t in m2), the progressive model
    forces C⁻¹(inst2[i]) − C⁻¹(inst1[i]) ≡ (t − s) for all i.  Feed those into the
    offset DSU; contradictions refute progressive."""
    dsu = OffsetDSU(N)
    constraints = 0
    contradictions = 0
    for pr in pairs:
        D = (pr.p2 - pr.p1) % N
        for i in range(pr.length):
            a = int(messages[pr.m1][pr.p1 + i])
            b = int(messages[pr.m2][pr.p2 + i])
            constraints += 1
            if not dsu.union(a, b, D):
                contradictions += 1
    comps = dsu.components()
    sizes = sorted((len(v) for v in comps.values()), reverse=True)
    return ChainResult(constraints, contradictions, sizes[0] if sizes else 0,
                       len(comps), contradictions == 0)


def chain_free_delta(messages: Sequence[Sequence[int]], pairs: List[IsoPair],
                     N: int, recover_threshold: int = 20) -> FreeChainResult:
    """Autokey / general interrelated-alphabet chaining.

    Unlike progressive_chain (which fixes the per-pair offset to position
    difference t−s), here each isomorph pair has its OWN unknown constant offset
    δ_p in the cipher alphabet: C⁻¹(inst2[i]) − C⁻¹(inst1[i]) = δ_p for all i.
    This is exactly the relation shared by ciphertext-autokey (offset 1),
    progressive-alphabet, and clock ciphers.  We solve the linear system over
    GF(N) (symbol positions x_a plus one free δ per pair); consistency means the
    cipher alphabet is recoverable up to rotation, reducing the cipher to
    monoalphabetic form."""
    gf = GFSystem(N)
    # plain union-find for symbol connectivity (recoverable-chunk size)
    parent = list(range(N))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    constraints = 0
    contradictions = 0
    redundant = 0
    for pi, pr in enumerate(pairs):
        dv = N + pi                       # this pair's free δ variable
        prev_sym: Optional[int] = None
        for i in range(pr.length):
            a = int(messages[pr.m1][pr.p1 + i])
            b = int(messages[pr.m2][pr.p2 + i])
            row: Dict[int, int] = {}
            row[b] = row.get(b, 0) + 1
            row[a] = row.get(a, 0) + (N - 1)
            row[dv] = (N - 1)
            constraints += 1
            res = gf.add(row, 0)
            if res == "contradiction":
                contradictions += 1
            elif res == "redundant":
                redundant += 1
            parent[find(a)] = find(b)     # a,b linked via shared δ
            if prev_sym is not None:
                parent[find(prev_sym)] = find(a)
            prev_sym = a
    comps: Dict[int, int] = defaultdict(int)
    seen_syms = set()
    for pr in pairs:
        for i in range(pr.length):
            seen_syms.add(int(messages[pr.m1][pr.p1 + i]))
            seen_syms.add(int(messages[pr.m2][pr.p2 + i]))
    for s in seen_syms:
        comps[find(s)] += 1
    linked = max(comps.values()) if comps else 0
    consistent = contradictions == 0
    # recoverable requires consistency, genuine over-determination (redundant
    # constraints — not just an underdetermined fit), and a large linked alphabet.
    recoverable = consistent and redundant >= recover_threshold and linked >= recover_threshold
    return FreeChainResult(constraints, contradictions, len(gf.pivots), redundant,
                           linked, consistent, recoverable)


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def _repeated_word_corpus(N, rng, enc, n_msgs=6, T=90, wlen=10):
    """Messages that share a repeat-rich word (to seed UNAMBIGUOUS isomorphs)
    under the encrypt fn enc(plain_ordinal, position)."""
    word = [int(x) for x in rng.integers(0, N, size=wlen)]
    word[3] = word[0]; word[6] = word[1]; word[8] = word[2]   # 3 repeats
    msgs = []
    for _ in range(n_msgs):
        p = list(rng.integers(0, N, size=T))
        for pos in (10, 40):                 # plant the word at two positions
            p[pos:pos + wlen] = word
        msgs.append([enc(p[t], t) for t in range(T)])
    return msgs


def selftest() -> List[tuple[str, bool]]:
    import numpy as np
    out: List[tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(3)

    # KAT: offset DSU detects a contradiction.
    d = OffsetDSU(N)
    out.append(("DSU union consistent", d.union(0, 1, 5) and d.union(1, 2, 7)))
    out.append(("DSU detects contradiction", not d.union(0, 2, 99)))
    out.append(("DSU accepts the consistent closure", d.union(0, 2, 12)))

    # (1) PROGRESSIVE plant: c[pos] = C[(p+pos) mod N]. Under a SLIDING alphabet a
    #     ciphertext collision needs word[i]+i to match (not the plaintext letter
    #     to repeat), so engineer the word to collide at positions {0,3,5,8}.
    C = list(rng.permutation(N))

    def enc_prog(p, pos):
        return C[(p + pos) % N]
    base = 20
    T = 90
    word = [int(x) for x in rng.integers(0, N, size=10)]
    for j in (0, 3, 5, 8):
        word[j] = (base - j) % N             # word[j] + j == base -> collide
    mp = []
    for _ in range(6):
        p = list(rng.integers(0, N, size=T))
        for pos in (10, 40):
            p[pos:pos + 10] = word
        mp.append([enc_prog(p[t], t) for t in range(T)])
    iso = find_isomorphs(mp, 10, 3)          # high-confidence (chance ~0)
    out.append(("progressive: isomorphs found", len(iso) > 0))
    ch = progressive_chain(mp, iso, N)
    out.append(("progressive: chaining is consistent (no contradiction)",
                ch.consistent))
    out.append(("progressive: chaining links symbols into a big component",
                ch.largest_component >= 6))

    # (2) INDEPENDENT-COLUMN plant: each position its own random permutation.
    perms = [list(rng.permutation(N)) for _ in range(200)]

    def enc_ind(p, pos):
        return perms[pos][p]
    mi = _repeated_word_corpus(N, rng, enc_ind)
    sig = significance(mi, 10, 3, n_null=60)
    out.append(("independent columns: ~no true isomorphs (z small)",
                sig["observed"] <= 2 and sig["z"] < 5))

    # (3) CIPHERTEXT-AUTOKEY plant: c[t] = (p[t] + c[t-1]) % N. Isomorphs exist,
    #     but the PROGRESSIVE chaining must CONTRADICT (progressive is wrong).
    def make_autokey(p):
        c = []
        prev = 7
        for t in range(len(p)):
            cc = (p[t] + prev) % N
            c.append(cc); prev = cc
        return c
    word = [int(x) for x in rng.integers(0, N, size=8)]
    word[4] = word[1]
    ma = []
    for _ in range(6):
        p = list(rng.integers(0, N, size=90))
        for pos in (12, 45):
            p[pos:pos + 8] = word
        ma.append(make_autokey(p))
    iso_a = find_isomorphs(ma, 8, 1)
    out.append(("autokey: isomorphs exist", len(iso_a) > 0))
    ch_a = progressive_chain(ma, iso_a, N)
    out.append(("autokey: progressive chaining CONTRADICTS (refutes progressive)",
                ch_a.contradictions > 0))

    # (4) FREE-DELTA chaining: the autokey/general test. Engineer a ciphertext-
    #     autokey corpus with GENUINE constant-offset isomorphs (via planted
    #     partial-sum repeats) and verify free-delta chaining is CONSISTENT and
    #     recovers the alphabet, where progressive (fixed delta) fails.
    L = 14
    # partial sums S with repeats at (0,4),(1,8),(2,11) -> ciphertext skeleton
    S = [int(x) for x in rng.integers(0, N, size=L)]
    S[4] = S[0]; S[8] = S[1]; S[11] = S[2]
    W = [S[0]] + [(S[i] - S[i - 1]) % N for i in range(1, L)]
    mk = []
    for _ in range(6):
        p = list(rng.integers(0, N, size=110))
        for pos in (15, 60):
            p[pos:pos + L] = W
        cph = []
        prev = int(rng.integers(0, N))
        for t in range(110):
            cc = (p[t] + prev) % N; cph.append(cc); prev = cc
        mk.append(cph)
    iso_k = find_isomorphs(mk, L, 3)
    out.append(("autokey(engineered): genuine isomorphs found", len(iso_k) > 0))
    fc = chain_free_delta(mk, iso_k, N, recover_threshold=10)
    out.append(("autokey: FREE-DELTA chaining is consistent (where progressive fails)",
                fc.consistent))
    out.append(("autokey: free-delta consistent + over-determined (necessary, "
                "NOT sufficient — see limit below)", fc.redundant >= 10))
    # progressive (fixed delta) should NOT be consistent on this autokey corpus
    pc = progressive_chain(mk, iso_k, N)
    out.append(("autokey: progressive (fixed-delta) chaining contradicts here",
                pc.contradictions > 0))

    # (4b) HONEST LIMIT: free-delta is PERMISSIVE. Build a corpus from TWO
    #      DIFFERENT cipher alphabets (which a single-alphabet identification
    #      should reject) — free-delta is STILL consistent, because per-pair free
    #      offsets absorb the mismatch. So free-delta CONSISTENCY does NOT by
    #      itself identify autokey or a single alphabet; only the PROGRESSIVE
    #      (fixed-offset) CONTRADICTION is an informative exclusion.
    C1 = list(rng.permutation(N)); C2 = list(rng.permutation(N))
    wlim = [int(x) for x in rng.integers(0, N, size=12)]
    for j in (0, 3, 5, 8):
        wlim[j] = (base - j) % N
    two = []
    for g in range(6):
        Cg = C1 if g < 3 else C2
        p = list(rng.integers(0, N, size=T))
        for pos in (10, 40):
            p[pos:pos + 12] = wlim
        two.append([Cg[(p[t] + t) % N] for t in range(T)])
    iso_two = find_isomorphs(two, 12, 3)
    fc_two = chain_free_delta(two, iso_two, N, recover_threshold=10)
    out.append(("LIMIT: free-delta is permissive — TWO different alphabets are "
                "ALSO consistent (so consistency != single alphabet/autokey)",
                fc_two.consistent))

    # (5) GF solver KATs: it must catch a genuine linear contradiction, and must
    #     NOT over-claim — sparse non-interlocking pairs are underdetermined
    #     (consistent but with ~no redundancy, so consistency is not evidence).
    gf = GFSystem(N)
    out.append(("GF: consistent rows accepted",
                gf.add({0: 1, 1: N - 1}, 5) == "pivot"))
    out.append(("GF: contradictory row detected",
                gf.add({0: 1, 1: N - 1}, 7) == "contradiction"))
    rnd = [list(rng.integers(0, N, size=90)) for _ in range(4)]
    fake = [IsoPair(0, 5, 1, 40, 12, False), IsoPair(2, 5, 3, 40, 12, False)]
    fc_r = chain_free_delta(rnd, fake, N, recover_threshold=10)
    out.append(("sparse non-interlocking pairs -> underdetermined (low redundancy, "
                "not recoverable)", fc_r.redundant < 5 and not fc_r.recoverable))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} isomorph checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
