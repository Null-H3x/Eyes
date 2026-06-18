"""Refrain repeat-template extractor.

Blind phrase-guessing is hopeless (random phrases pass the structural filter at
~0/300, any language) because only a phrase matching the refrain's EXACT
repeat-structure survives. This module extracts that structure, ordering-free, so
candidates can be GENERATED/filtered to match it.

Under per-message-progressive c[m][t]=C[(p[t]+base_m+t)], the ciphertext imposes
LINEAR constraints on the plaintext values p[0..L-1] (and per-message bases).
Solving the GF(N) system and querying every position-pair gives, for each (i,j),
whether p[i]-p[j] is FORCED to a constant g:
   g == 0  -> positions i,j MUST be the SAME letter,
   g != 0  -> positions i,j MUST be DIFFERENT letters,
   not forced -> FREE (either).
The forced-same classes + forced-different pairs are the template a real refrain
must obey; the count of free plaintext degrees of freedom measures how constrained
(and thus how searchable) the refrain is.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from isomorph import GFSystem


@dataclass
class Template:
    L: int
    consistent: bool
    same_groups: List[List[int]]                 # positions forced to share a letter
    diff_pairs: List[Tuple[int, int, int]]       # (i, j, gap) forced different
    free_positions: List[int]                    # positions in no forced relation
    dof: int                                     # free plaintext degrees of freedom
    contradiction: Optional[Tuple[int, int]] = None


def _build_gf(messages, instances, L, N):
    msgs = sorted({m for m, _ in instances})
    M = len(msgs)
    bvar = {m: L + j for j, m in enumerate(msgs)}
    xbase = L + M
    gf = GFSystem(N)
    gf.add({bvar[msgs[0]]: 1}, 0)                 # gauge first base = 0
    for (m, pos) in instances:
        for i in range(L):
            c = int(messages[m][pos + i])
            row = {xbase + c: 1, i: N - 1, bvar[m]: N - 1}
            row = {v: cc % N for v, cc in row.items() if cc % N}
            if gf.add(row, (pos + i) % N) == "contradiction":
                return None, (instances.index((m, pos)), i)
    return gf, None


def extract(messages, instances, L, N) -> Template:
    gf, contra = _build_gf(messages, instances, L, N)
    if gf is None:
        return Template(L, False, [], [], list(range(L)), L, contra)
    val = gf.solve()
    # forced pairwise relations among p[0..L-1]
    parent = list(range(L))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    diff_pairs = []
    forced_pairs = []
    for i in range(L):
        for j in range(i + 1, L):
            g = (val.get(i, 0) - val.get(j, 0)) % N
            if gf.classify({i: 1, j: N - 1}, g) == "redundant":
                forced_pairs.append((i, j, g))
                if g == 0:
                    parent[find(i)] = find(j)
                else:
                    diff_pairs.append((i, j, g))
    comp = defaultdict(list)
    for i in range(L):
        comp[find(i)].append(i)
    same_groups = [sorted(v) for v in comp.values() if len(v) > 1]
    in_relation = set()
    for (i, j, _) in forced_pairs:
        in_relation.add(i); in_relation.add(j)
    free_positions = [i for i in range(L) if i not in in_relation]
    # degrees of freedom = L minus (rank of forced relations among p positions)
    # approximate via connected components under ALL forced pairs (same or diff):
    parent2 = list(range(L))

    def find2(x):
        while parent2[x] != x:
            parent2[x] = parent2[parent2[x]]
            x = parent2[x]
        return x
    for (i, j, _) in forced_pairs:
        parent2[find2(i)] = find2(j)
    roots = {find2(i) for i in range(L)}
    dof = len(roots)
    return Template(L, True, same_groups, diff_pairs, free_positions, dof, None)


def fits(messages, instances, L, phrase, N) -> bool:
    """Full check: does this phrase's letter-pattern survive the structure?
    (Adds the phrase's letter-equalities to the GF.)"""
    if len(phrase) < L:
        return False
    phrase = phrase[:L]
    gf, contra = _build_gf(messages, instances, L, N)
    if gf is None:
        return False
    # add letter-equalities P[i]=P[j] for equal phrase letters
    first = {}
    for i, ch in enumerate(phrase):
        if ch in first:
            if gf.add({first[ch]: 1, i: N - 1}, 0) == "contradiction":
                return False
        else:
            first[ch] = i
    return True


def skeleton_string(tmpl: Template) -> str:
    """A human pattern: assign a letter to each forced-same group, '.' to free."""
    label = ["?"] * tmpl.L
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    li = 0
    for g in tmpl.same_groups:
        for p in g:
            label[p] = letters[li]
        li += 1
    for p in tmpl.free_positions:
        label[p] = "."
    return "".join(label)


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def selftest() -> List[Tuple[str, bool]]:
    import numpy as np
    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(0)
    C = list(rng.permutation(N))
    bases = [int(b) for b in rng.integers(0, N, size=2)]
    L = 18
    # Plant a refrain with ENGINEERED ciphertext collisions: same plaintext at
    # DIFFERENT positions does NOT collide (different positions -> different
    # ciphertext), so the structure only "sees" collisions where p[a]+a == p[b]+b.
    # Engineer collisions at (2,7) and (4,11): set p[7]=p[2]+(2-7), p[11]=p[4]+(4-11).
    vals = [int(v) for v in rng.permutation(N)[:L]]
    vals[7] = (vals[2] + (2 - 7)) % N          # -> c[2]==c[7] (gap 7-2=5)
    vals[11] = (vals[4] + (4 - 11)) % N         # -> c[4]==c[11] (gap 11-4=7)
    region = [(0, 30), (0, 60), (1, 35), (1, 70)]
    T = 110
    msgs = [[], []]
    for m in range(2):
        p = [int(rng.integers(0, N)) for _ in range(T)]
        for (mm, pos) in region:
            if mm == m:
                p[pos:pos + L] = vals
        msgs[m] = [C[(p[t] + bases[m] + t) % N] for t in range(T)]

    tmpl = extract(msgs, region, L, N)
    out.append(("template extraction is consistent on a valid plant", tmpl.consistent))
    # the engineered collisions must appear as forced-DIFFERENT pairs with right gaps
    dp = {(i, j): g for (i, j, g) in tmpl.diff_pairs}
    out.append(("forced-different recovers engineered collision (2,7) gap 5",
                dp.get((2, 7)) == 5))
    out.append(("forced-different recovers engineered collision (4,11) gap 7",
                dp.get((4, 11)) == 7))
    # a phrase matching the structure fits (all-distinct trivially fits)
    out.append(("an all-distinct phrase fits (no forbidden repeats)",
                fits(msgs, region, L, "abcdefghijklmnopqr", N)))
    # a phrase that repeats a letter on a forced-different pair is rejected
    bad = list("abcdefghijklmnopqr"); bad[7] = bad[2]    # equal on forced-diff (2,7)
    out.append(("a phrase repeating a letter on a forced-different pair is rejected",
                not fits(msgs, region, L, "".join(bad), N)))
    out.append(("dof < L (collisions remove freedom)", tmpl.dof < L))
    # forced-same is (correctly) empty here: same plaintext at different positions
    # does not collide, so the structure cannot force two positions equal.
    out.append(("forced-same is empty (same plaintext at diff positions never "
                "collides)", len(tmpl.same_groups) == 0))
    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} template checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
