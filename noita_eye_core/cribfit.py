"""Crib-placement tester for repeated maximal-aligned-isomorph targets.

A target is a set of ciphertext instances (m, pos) of length L that the extractor
(chain_extract) has certified as the SAME plaintext (e.g. the 4x repeated 15-glyph
segment in West 1 / East 2). This module tests whether a hypothesised plaintext
fits, under the per-message-progressive model
    x[c_m[pos+i]] = p[i] + base_m + pos + i   (mod N),  x = C^{-1}.

Two modes, with VERY different power (both validated in selftest):

  VALUE mode  — you supply the plaintext VALUES p[i] (i.e. a phrase + a
                plaintext-alphabet ordering letter->Z_N). Placement at all
                instances + the already-extracted corpus alphabet is RAZOR-SHARP:
                a random phrase passes ~0% of the time. A pass that also stays
                consistent with the corpus is strong joint evidence for BOTH the
                phrase and the alphabet hypothesis.

  PATTERN mode — you supply only the letter-equality pattern (no values). This is
                PERMISSIVE: most patterns are consistent (~>90%), because the
                ciphertext repeat pattern of a sliding cipher reflects p[i]+i, not
                p[i]. So pattern alone does NOT decide — the tool reports this.

Every test is reported against a calibrated NULL (random phrases under the same
hypothesis), so a result can never be mistaken for significant when it is not.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from isomorph import GFSystem, IsoPair, find_isomorphs
import chain_models as cm
import chain_extract as ce


@dataclass
class Target:
    instances: List[Tuple[int, int]]   # (message, start position)
    length: int
    skeleton: Tuple[int, ...]          # ciphertext repeat pattern (shared)


def find_targets(messages, base_len: int = 13, broad_repeats: int = 3,
                 N: Optional[int] = None) -> List[Target]:
    """Group the extractor's clean maximal isomorphs into same-plaintext targets
    (instances sharing one ciphertext skeleton), largest first."""
    if N is None:
        N = max(int(max(m)) for m in messages) + 1
    res = ce.extract(messages, base_len=base_len, broad_repeats=broad_repeats, N=N)
    from collections import defaultdict
    groups: Dict[Tuple[int, ...], set] = defaultdict(set)
    for pr in res.clean_pairs:
        sk1 = _sk(messages[pr.m1][pr.p1:pr.p1 + pr.length])
        groups[sk1].add((pr.m1, pr.p1, pr.length))
        groups[sk1].add((pr.m2, pr.p2, pr.length))
    targets = []
    for sk, insts in groups.items():
        L = next(iter(insts))[2]
        targets.append(Target(sorted((m, p) for m, p, _ in insts), L, sk))
    targets.sort(key=lambda t: (len(t.instances), t.length), reverse=True)
    return targets


def _sk(seq) -> Tuple[int, ...]:
    first: Dict[int, int] = {}
    return tuple(first.setdefault(int(v), i) for i, v in enumerate(seq))


# ---------------------------------------------------------------------------
# Placement
# ---------------------------------------------------------------------------

def _value_rows(target: Target, p: Sequence[int], messages, N):
    """per-msg-progressive VALUE constraints: x[c] - base_m = p[i] + pos + i."""
    for (m, pos) in target.instances:
        for i in range(target.length):
            c = int(messages[m][pos + i])
            row = {c: 1, (N + m): (N - 1)}
            row = {v: cc % N for v, cc in row.items() if cc % N}
            yield row, (p[i] + pos + i) % N


def _pattern_rows(target: Target, patt: Sequence[int], messages, N):
    """Value-free constraints from a letter-equality pattern: for same-letter
    positions a,b, x[c_a] - x[c_b] = a - b at every instance."""
    from collections import defaultdict
    groups: Dict[int, List[int]] = defaultdict(list)
    for i, g in enumerate(patt):
        groups[g].append(i)
    for (m, pos) in target.instances:
        seg = messages[m][pos:pos + target.length]
        for idxs in groups.values():
            for a, b in zip(idxs, idxs[1:]):
                ca, cb = int(seg[a]), int(seg[b])
                row = {ca: 1, cb: N - 1}
                row = {v: cc % N for v, cc in row.items() if cc % N}
                yield row, (a - b) % N


def _consistent(gf: GFSystem, rows) -> bool:
    for row, rhs in rows:
        if gf.add(row, rhs) == "contradiction":
            return False
    return True


def _corpus_gf(messages, N, base_len=13, broad_repeats=3) -> GFSystem:
    """The extracted partial cipher alphabet, as a GF system to test cribs against."""
    res = ce.extract(messages, base_len=base_len, broad_repeats=broad_repeats, N=N)
    gf = GFSystem(N)
    for pr in res.clean_pairs:
        for row, rhs in cm.per_msg_prog_rows(pr, messages, N):
            gf.add(row, rhs)
    return gf


@dataclass
class FitResult:
    consistent: bool
    extends_corpus: Optional[bool]     # consistent with the extracted alphabet too?
    null_rate: float                   # fraction of random cribs that also pass
    mode: str


def test_value(target: Target, p: Sequence[int], messages, N,
               corpus_gf: Optional[GFSystem] = None,
               n_null: int = 500, seed: int = 0) -> FitResult:
    """Sharp test: place crib VALUES at all instances; optionally require
    consistency with the extracted corpus alphabet; calibrate against random."""
    gf = GFSystem(N)
    cons = _consistent(gf, _value_rows(target, p, messages, N))
    ext = None
    if corpus_gf is not None and cons:
        g2 = GFSystem(N)
        g2.restore(corpus_gf.snapshot())
        ext = _consistent(g2, _value_rows(target, p, messages, N))
    rng = random.Random(seed)
    npass = 0
    for _ in range(n_null):
        q = [rng.randrange(N) for _ in range(target.length)]
        if corpus_gf is not None:
            g3 = GFSystem(N); g3.restore(corpus_gf.snapshot())
            if _consistent(g3, _value_rows(target, q, messages, N)):
                npass += 1
        else:
            g3 = GFSystem(N)
            if _consistent(g3, _value_rows(target, q, messages, N)):
                npass += 1
    return FitResult(cons, ext, npass / n_null, "value")


def test_pattern(target: Target, patt: Sequence[int], messages, N,
                 n_null: int = 500, seed: int = 0) -> FitResult:
    """Value-free test (letter-equality pattern only). Permissive — reported with
    its null so it can't be mistaken for decisive."""
    gf = GFSystem(N)
    cons = _consistent(gf, _pattern_rows(target, patt, messages, N))
    rng = random.Random(seed)
    npass = 0
    for _ in range(n_null):
        q = _rand_pattern(target.length, len(set(patt)), rng)
        g = GFSystem(N)
        if _consistent(g, _pattern_rows(target, q, messages, N)):
            npass += 1
    return FitResult(cons, None, npass / n_null, "pattern")


def _rand_pattern(L: int, n_distinct: int, rng: random.Random) -> List[int]:
    while True:
        p = [rng.randrange(n_distinct) for _ in range(L)]
        if len(set(p)) == n_distinct:
            return p


def letters_to_values(text: str, alphabet: str) -> Optional[List[int]]:
    """Map a candidate phrase to plaintext Z_N values via an alphabet ordering
    (position in `alphabet` = value). Returns None if a letter is unmapped."""
    idx = {ch: i for i, ch in enumerate(alphabet)}
    out = []
    for ch in text:
        if ch not in idx:
            return None
        out.append(idx[ch])
    return out


def letter_pattern(text: str) -> List[int]:
    first: Dict[str, int] = {}
    return [first.setdefault(ch, i) for i, ch in enumerate(text)]


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def selftest() -> List[Tuple[str, bool]]:
    import numpy as np
    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(0)
    C = list(rng.permutation(N))
    patt = [0, 1, 2, 3, 4, 5, 6, 4, 8, 2, 6, 11, 3, 13, 14]
    vals = {g: int(rng.integers(0, N)) for g in set(patt)}
    W = [vals[patt[i]] for i in range(15)]
    insts = [(0, 38), (0, 68), (1, 43), (1, 78)]
    bases = [int(rng.integers(0, N)), int(rng.integers(0, N))]
    # build a 2-message corpus carrying the segment 4x, random elsewhere
    T = 120
    msgs = []
    for m in range(2):
        seq = [int(x) for x in rng.integers(0, N, size=T)]
        for (mm, pos) in insts:
            if mm == m:
                for i in range(15):
                    seq[pos + i] = C[(W[i] + bases[m] + pos + i) % N]
        msgs.append(seq)
    tgt = Target(insts, 15, _sk(msgs[0][38:53]))

    # VALUE mode is razor-sharp: true values consistent; random ~0%
    rv = test_value(tgt, W, msgs, N, n_null=400)
    out.append(("VALUE mode: true crib values are consistent", rv.consistent))
    out.append(("VALUE mode: random cribs almost never pass (null < 2%)",
                rv.null_rate < 0.02))

    # wrong values (true pattern, wrong numbers) should also fail sharply
    bad = [(W[i] + 1 + (i % 7)) % N for i in range(15)]
    rb = test_value(tgt, bad, msgs, N, n_null=1)
    out.append(("VALUE mode: a wrong-value crib is rejected", not rb.consistent))

    # PATTERN mode is PERMISSIVE (documented limit): true pattern consistent but
    # random patterns pass most of the time, so pattern alone is not decisive.
    rp = test_pattern(tgt, patt, msgs, N, n_null=400)
    out.append(("PATTERN mode: true pattern is consistent", rp.consistent))
    out.append(("PATTERN mode: is PERMISSIVE (null > 0.5) — documented, not a bug",
                rp.null_rate > 0.5))

    # letter helpers
    out.append(("letters_to_values maps via alphabet ordering",
                letters_to_values("bad", "abcd") == [1, 0, 3]))
    out.append(("letters_to_values rejects unmapped letters",
                letters_to_values("zoo", "abc") is None))
    out.append(("letter_pattern extracts repeat skeleton",
                letter_pattern("seer") == [0, 1, 1, 3]))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} cribfit checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
