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

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} isomorph checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
