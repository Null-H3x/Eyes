"""Constraint-propagation crib-drag over an unknown alphabet (two-time-pad style).

The cipher is depth (a shared keystream within each triplet) over an **unknown
symbol->letter mapping**.  That is exactly a two-time-pad with an unknown
alphabet, and the textbook attack is crib-dragging — adapted here so it needs no
mapping up front.

Key algebra (additive combiner, shared per-triplet key K):

    cᵢ[t] − cⱼ[t]  ==  pᵢ[t] − pⱼ[t]   (mod N)        # key-free, exact

So if member i reads word Wᵢ and member j reads word Wⱼ over a span, then for
every offset o:

    σ(Wⱼ[o]) − σ(Wᵢ[o])  ==  (cⱼ − cᵢ)[span][o]      # σ = letter→symbol

That is a **linear system in the unknown symbol values σ(letter)**.  It needs no
brute force over the alphabet: weighted union-find over the letters (potentials in
Z_N) either finds it *consistent* (one free offset per connected component) or
*contradictory*.  A word-tuple assigned to the members of a triplet that is
**mutually consistent** under one σ — especially a long one, and especially when
all three members read words at once — is a strong, low-false-positive crib hit,
and it pins the keystream over the span (up to the per-component offsets, which a
third member or a seed search resolves).

This module is mapping-agnostic and keystream-free: it only ever uses ciphertext
*differences*.  It plugs into EyeCrack's seed filter (``structscan --crib``) once a
placement resolves the offsets.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from typing import Dict, List, Optional, Sequence, Tuple

import corpus as corpus_mod

TRIPLETS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))

# The user's candidate vocabulary (Noita static-message themes + rune words),
# plus low-cost neighbours that strengthen the cascade cross-check.
DEFAULT_WORDS = [
    "devoted", "answers", "treasure", "god", "gods", "free", "will", "secret",
    "egg", "tree", "three", "blood", "technology",
    "eye", "eyes", "the", "and", "of", "free", "will", "god",
]


# ---------------------------------------------------------------------------
# Weighted union-find over Z_N (the linear-offset solver)
# ---------------------------------------------------------------------------

class OffsetDSU:
    """Union-find with potentials in Z_N: tracks σ(x) − σ(root) for each letter.

    ``union(a, b, d)`` asserts ``σ(b) − σ(a) == d (mod N)`` and returns False on
    contradiction.
    """

    def __init__(self, N: int):
        self.N = N
        self.parent: Dict[str, str] = {}
        self.off: Dict[str, int] = {}      # σ(x) − σ(parent[x])  (mod N)

    def _add(self, x: str) -> None:
        if x not in self.parent:
            self.parent[x] = x
            self.off[x] = 0

    def find(self, x: str) -> Tuple[str, int]:
        self._add(x)
        root = x
        acc = 0
        while self.parent[root] != root:
            acc = (acc + self.off[root]) % self.N
            root = self.parent[root]
        # path-compress
        cur, coff = x, 0
        while self.parent[cur] != cur:
            nxt = self.parent[cur]
            noff = self.off[cur]
            self.parent[cur] = root
            self.off[cur] = (acc - coff) % self.N
            coff = (coff + noff) % self.N
            cur = nxt
        return root, acc

    def union(self, a: str, b: str, d: int) -> bool:
        """σ(b) − σ(a) == d (mod N)."""
        self._add(a)
        self._add(b)
        ra, oa = self.find(a)
        rb, ob = self.find(b)
        if ra == rb:
            # need (σ(b)−σ(a)) == d  i.e. (ob − oa) == d
            return (ob - oa) % self.N == d % self.N
        # attach rb under ra: σ(rb) − σ(ra) = oa + d − ob
        self.parent[rb] = ra
        self.off[rb] = (oa + d - ob) % self.N
        return True

    def components(self) -> int:
        return sum(1 for x in self.parent if self.parent[x] == x)


# ---------------------------------------------------------------------------
# Consistency of a word-tuple assigned to a triplet at a span
# ---------------------------------------------------------------------------

@dataclass
class Placement:
    family: Tuple[int, ...]
    start: int
    length: int
    words: Tuple[str, ...]              # word per member, aligned to `family`
    free_components: int               # mapping DOF left (per-component offset)
    distinct_words: int
    redundant: int                     # independent 1/N coincidences survived
    score: float = 0.0


def _diff(ci: Sequence[int], cj: Sequence[int], s: int, L: int, N: int
          ) -> List[int]:
    return [(cj[s + o] - ci[s + o]) % N for o in range(L)]


def tuple_consistent(messages: Sequence[Sequence[int]], family: Sequence[int],
                     words: Sequence[str], start: int, N: int
                     ) -> Optional[Tuple[OffsetDSU, int]]:
    """Is assigning ``words[k]`` to member ``family[k]`` over ``[start, start+L)``
    consistent under ONE letter→symbol map?  Returns ``(dsu, redundant)`` or None.

    Uses only ciphertext differences between members (key-free); the additive
    identity pⱼ−pᵢ = cⱼ−cᵢ turns each column into σ(wⱼ[o])−σ(wᵢ[o]) = diff.

    ``redundant`` = number of constraints whose two letters were ALREADY linked
    (cycles + same-letter columns).  Each such constraint had a ~1/N chance of
    being satisfied by accident, so it is the real evidence: a vacuously-consistent
    tuple of all-distinct letters has redundant=0; a true crib survives many."""
    L = len(words[0])
    if any(len(w) != L for w in words):
        return None
    if any(start + L > len(messages[m]) for m in family):
        return None
    dsu = OffsetDSU(N)
    base = family[0]
    base_word = words[0]
    redundant = 0
    for k in range(1, len(family)):
        d = _diff(messages[base], messages[family[k]], start, L, N)
        wk = words[k]
        same_word = (wk == base_word)
        for o in range(L):
            a, b = base_word[o], wk[o]
            if a == b:
                # same letter -> needs equal ciphertext there.
                if d[o] % N != 0:
                    return None
                # Evidence ONLY if the two words DIFFER overall: two *different*
                # words sharing a letter exactly where the ciphertext agrees is a
                # real coincidence; the SAME word on identical members is a
                # tautology (it just restates that the members are duplicates).
                if not same_word:
                    redundant += 1
                dsu._add(a)
                continue
            ra, _ = dsu.find(a)
            rb, _ = dsu.find(b)
            if ra == rb:
                redundant += 1            # genuine cross-word cycle
            if not dsu.union(a, b, d[o]):
                return None
    # Injectivity: a substitution alphabet maps distinct letters to distinct
    # symbols.  Two DISTINCT letters in the same component with the same potential
    # (offset to root) would share a symbol -> reject.  This kills the trivial
    # shared-opening hits (identical ciphertext forces unrelated words to collapse
    # their letters onto one symbol).
    seen: Dict[Tuple[str, int], str] = {}
    for letter in {ch for w in words for ch in w}:
        root, off = dsu.find(letter)
        key = (root, off)
        if key in seen and seen[key] != letter:
            return None
        seen[key] = letter
    return dsu, redundant


def keystream_skeleton(messages: Sequence[Sequence[int]], family: Sequence[int],
                       words: Sequence[str], start: int, N: int,
                       anchor: Optional[Dict[str, int]] = None) -> List[int]:
    """Recover K[start:start+L] given a consistent tuple.  Letters are anchored to
    symbol 0 by default (one free offset per component) — supply ``anchor`` to pin
    chosen letters to chosen symbols and resolve the keystream absolutely."""
    L = len(words[0])
    sol = tuple_consistent(messages, family, words, start, N)
    if sol is None:
        raise ValueError("tuple is not consistent")
    dsu, _ = sol
    sigma: Dict[str, int] = {}
    anchor = anchor or {}
    for letter in set("".join(words)):
        root, off = dsu.find(letter)
        base = anchor.get(root, 0)
        sigma[letter] = (base + off) % N
    base = family[0]
    return [(messages[base][start + o] - sigma[words[0][o]]) % N
            for o in range(L)]


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search_family(messages: Sequence[Sequence[int]], family: Sequence[int],
                  words: Sequence[str], N: int, min_len: int = 4,
                  require_distinct: int = 2, min_redundant: int = 2
                  ) -> List[Placement]:
    """All positions × word-tuples that are mutually consistent for a triplet.

    ``require_distinct`` filters trivial all-identical tuples; ``min_redundant``
    keeps only tuples carrying real evidence (>= that many 1/N coincidences)."""
    words = sorted(set(words))
    by_len: Dict[int, List[str]] = {}
    for w in words:
        if len(w) >= min_len:
            by_len.setdefault(len(w), []).append(w)
    Lmin = min(len(messages[m]) for m in family)
    out: List[Placement] = []
    n = len(family)
    import math
    for L, wl in by_len.items():
        for s in range(0, Lmin - L + 1):
            for combo in product(wl, repeat=n):
                if len(set(combo)) < require_distinct:
                    continue
                sol = tuple_consistent(messages, family, combo, s, N)
                if sol is None:
                    continue
                dsu, redundant = sol
                if redundant < min_redundant:
                    continue
                free = dsu.components()
                # Evidence dominates: each redundant constraint is ~log10(N)
                # decimal orders of surprise; length is a mild tie-breaker.
                score = redundant * math.log10(N) + 0.1 * L
                out.append(Placement(family=tuple(family), start=s, length=L,
                                     words=tuple(combo), free_components=free,
                                     distinct_words=len(set(combo)),
                                     redundant=redundant, score=score))
    out.sort(key=lambda p: -p.score)
    return out


def search_corpus(c: corpus_mod.Corpus, words: Sequence[str] = DEFAULT_WORDS,
                  min_len: int = 4, require_distinct: int = 2,
                  min_redundant: int = 2, partition=TRIPLETS, top: int = 20
                  ) -> List[Placement]:
    messages = [list(ct) for ct in c.ciphertexts]
    found: List[Placement] = []
    for fam in partition:
        found.extend(search_family(messages, fam, words, c.N, min_len,
                                    require_distinct, min_redundant))
    found.sort(key=lambda p: -p.score)
    return found[:top]


def decoy_rate(messages: Sequence[Sequence[int]], family: Sequence[int],
               N: int, lengths: Sequence[int], n_decoys: int = 200,
               seed: int = 0, require_distinct: int = 2) -> float:
    """Chance that a random word-tuple (same lengths) is consistent at a random
    position — the false-positive baseline for the trust gate."""
    import random
    rng = random.Random(seed)
    Lmin = min(len(messages[m]) for m in family)
    alpha = "abcdefghijklmnopqrstuvwxyz"
    hits = 0
    trials = 0
    for _ in range(n_decoys):
        L = rng.choice(list(lengths))
        if Lmin - L < 1:
            continue
        s = rng.randrange(0, Lmin - L + 1)
        combo = tuple("".join(rng.choice(alpha) for _ in range(L))
                      for _ in family)
        if len(set(combo)) < require_distinct:
            continue
        trials += 1
        sol = tuple_consistent(messages, family, combo, s, N)
        if sol is not None and sol[1] >= 2:      # consistent with real evidence
            hits += 1
    return hits / trials if trials else 0.0


# ---------------------------------------------------------------------------
# Selftest — plant a two-time-pad triplet and recover the crib
# ---------------------------------------------------------------------------

def selftest() -> List[tuple[str, bool]]:
    import random
    out: List[tuple[str, bool]] = []
    N = 83
    rng = random.Random(7)

    # --- DSU contradiction / consistency KATs ---
    dsu = OffsetDSU(N)
    out.append(("dsu: σ(b)-σ(a)=5 then =6 is a contradiction",
                dsu.union("a", "b", 5) and not dsu.union("a", "b", 6)))
    dsu2 = OffsetDSU(N)
    ok = dsu2.union("a", "b", 5) and dsu2.union("b", "c", 10) \
        and dsu2.union("a", "c", 15)         # 5+10=15 consistent
    out.append(("dsu: transitive offsets compose (5+10=15)", ok))
    dsu3 = OffsetDSU(N)
    out.append(("dsu: same-letter with nonzero offset is a contradiction",
                not dsu3.union("e", "e", 3)))

    # --- Plant a triplet two-time-pad ---
    letters = "abcdefghijklmnopqrstuvwxyz"
    sigma = {ch: i for i, ch in enumerate(rng.sample(range(N), len(letters)))}
    sigma = {ch: sigma_i for ch, sigma_i in
             zip(letters, rng.sample(range(N), len(letters)))}
    T = 60
    K = [rng.randrange(N) for _ in range(T)]

    def enc(word_at_span, span_start):
        p = [rng.randrange(N) for _ in range(T)]
        for o, ch in enumerate(word_at_span):
            p[span_start + o] = sigma[ch]
        return [(p[t] + K[t]) % N for t in range(T)], p

    # Three members read real words over the SAME span (a planted crib triple).
    span = 20
    wa, wb, wc = "tree", "free", "glee"
    ca, pa = enc(wa, span)
    cb, pb = enc(wb, span)
    cc, pc = enc(wc, span)
    msgs = [ca, cb, cc]
    wordlist = ["tree", "free", "glee", "blood", "three", "stone", "water"]

    res = search_family(msgs, (0, 1, 2), wordlist, N, min_len=4,
                        require_distinct=2)
    out.append(("planted crib triple is found", len(res) >= 1))
    top = res[0] if res else None
    out.append(("top hit is at the planted span",
                top is not None and top.start == span))
    out.append(("top hit recovers the planted word tuple",
                top is not None and set(top.words) == {"tree", "free", "glee"}))

    # Keystream recovery (TRUE assignment): pinned up to one free offset per
    # letter-component; resolve the offsets with the true mapping (as a third
    # member / seed search would) and the recovered keystream must be EXACT.
    true_tuple = ("tree", "free", "glee")
    dsu, _ = tuple_consistent(msgs, (0, 1, 2), true_tuple, span, N)
    anchor: Dict[str, int] = {}
    for letter in set("".join(true_tuple)):
        root, off = dsu.find(letter)
        anchor[root] = (sigma[letter] - off) % N
    ks = keystream_skeleton(msgs, (0, 1, 2), true_tuple, span, N, anchor=anchor)
    out.append(("offset-resolved keystream is exact (true tuple)",
                ks == K[span:span + 4]))

    # HONESTY: tree/free share the repeat-skeleton `_ree` and differ only at a
    # non-evidence column, so the difference structure cannot say which member is
    # which -- both orderings score identically.  Document that as a property.
    s1 = tuple_consistent(msgs, (0, 1, 2), ("tree", "free", "glee"), span, N)
    s2 = tuple_consistent(msgs, (0, 1, 2), ("free", "tree", "glee"), span, N)
    out.append(("repeat-skeleton ambiguity is real (tree/free interchange)",
                s1 is not None and s2 is not None and s1[1] == s2[1]))

    # --- Null: random plaintext (no words) yields a low decoy consistency rate
    #     at length 4 (so real long hits stand out). ---
    rate = decoy_rate(msgs, (0, 1, 2), N, [4], n_decoys=300, seed=1)
    out.append(("decoy consistency rate at L=4 is low (<5%)", rate < 0.05))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} cribdrag checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
