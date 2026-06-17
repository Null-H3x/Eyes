"""Keystream-sharing / depth map — how much depth do we actually have?

Earlier tools said "per-triplet keystream", but that verdict can't separate two
explanations of "within-triplet looks more related than cross-triplet":
  (a) the keystreams really are per-triplet, or
  (b) one shared keystream + plaintext that is merely more related within a
      triplet (the near-duplicate pairs).
The shared openings break the tie: messages from *different* triplets share long
identical ciphertext prefixes (e.g. East 3 with East 4/West 4/East 5 for 9
symbols past the header), which independent keystreams could not produce
(~(1/N)^7).  So keystreams are shared across messages over the openings.

The identifiability boundary (the honest core of this module)
-------------------------------------------------------------
From ciphertext alone, with c = p + K and an unknown alphabet:
  * Two messages with **identical ciphertext** over a run share BOTH plaintext
    and keystream there (a long run can't be a plaintext/keystream cancellation
    coincidence).  -> PROVES shared keystream.
  * Two messages whose ciphertext is **equal far more often than 1/N** over a
    region share a keystream there AND have related plaintext (if the keystream
    differed, equality would fall to ~1/N even with equal plaintext).
    -> PROVES shared keystream.
  * Where plaintexts **differ**, shared vs independent keystream is INVISIBLE:
    both give equality ~1/N.  -> UNDETERMINED.  We can NEVER prove independence.

Consequence: exploitable depth (shared keystream where plaintexts also differ,
so the key-free difference c_i - c_j = p_i - p_j carries information) only exists
where we can prove sharing — i.e. on the near-duplicate pairs.  This map reports
exactly that, and flags the one question whose answer would unlock the body:
**is the body keystream global?** (testable by a crib, not by ciphertext stats).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from itertools import combinations
from typing import List, Sequence, Tuple

import corpus as corpus_mod

# z above which elevated equality is treated as proof of shared keystream.
Z_PROVE = 6.0
# an identical run (past the header) this long alone proves shared keystream.
RUN_PROVE = 4


def equality(a: Sequence[int], b: Sequence[int]) -> List[bool]:
    L = min(len(a), len(b))
    return [a[t] == b[t] for t in range(L)]


def identical_prefix(a: Sequence[int], b: Sequence[int], start: int = 1) -> int:
    """Length of the identical run starting at ``start`` (default 1, skipping the
    per-message index at position 0)."""
    n = 0
    for t in range(start, min(len(a), len(b))):
        if a[t] == b[t]:
            n += 1
        else:
            break
    return n


def _binom_z(k: int, n: int, p: float) -> float:
    if n == 0:
        return 0.0
    mu = n * p
    sd = math.sqrt(n * p * (1.0 - p)) or 1e-9
    return (k - mu) / sd


@dataclass
class PairEvidence:
    i: int
    j: int
    n: int                 # comparable length (excl. position 0)
    prefix: int            # identical run past the header
    equal: int             # total equal positions (excl. pos 0)
    body_equal: int        # equal positions after the identical prefix
    body_n: int
    z_body: float          # equality elevation in the body vs 1/N
    opening_proven: bool   # shared keystream over the opening run
    body_proven: bool      # shared keystream persists INTO the body
    verdict: str
    exploitable: int       # body positions with body-proven shared-K AND differing p


def pair_evidence(a: Sequence[int], b: Sequence[int], N: int) -> PairEvidence:
    eqs = equality(a, b)[1:]            # drop position 0 (per-message index)
    n = len(eqs)
    pref = identical_prefix(a, b)
    body = eqs[pref:]
    body_n = len(body)
    body_equal = sum(body)
    z_body = _binom_z(body_equal, body_n, 1.0 / N)
    equal = sum(eqs)
    opening_proven = pref >= RUN_PROVE
    body_proven = z_body >= Z_PROVE
    if body_proven:
        verdict = "shared through body (proven)"
    elif opening_proven:
        verdict = "shared opening only (proven); body undetermined"
    else:
        verdict = "undetermined"
    # Exploitable depth: ONLY where body sharing is proven do the differing
    # positions yield key-free plaintext differences (c_i-c_j = p_i-p_j).
    exploitable = (body_n - body_equal) if body_proven else 0
    return PairEvidence(0, 0, n, pref, equal, body_equal, body_n, z_body,
                        opening_proven, body_proven, verdict, exploitable)


def _components(pairs: List[PairEvidence], n: int, scope: str) -> List[List[int]]:
    """Union-find over proven shared-keystream pairs at the given ``scope``
    ('opening' or 'body')."""
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for ev in pairs:
        ok = ev.body_proven if scope == "body" else (ev.opening_proven or ev.body_proven)
        if ok:
            parent[find(ev.i)] = find(ev.j)
    comps: dict = {}
    for x in range(n):
        comps.setdefault(find(x), []).append(x)
    return sorted((sorted(v) for v in comps.values()), key=lambda c: -len(c))


@dataclass
class DepthMap:
    pairs: List[PairEvidence]
    opening_components: List[List[int]]   # share a keystream over openings
    body_components: List[List[int]]      # share a keystream INTO the body
    exploitable_total: int                # key-free plaintext-diff positions
    undetermined: int                     # pairs we cannot resolve from ciphertext


def build(messages: Sequence[Sequence[int]], N: int) -> DepthMap:
    n = len(messages)
    pairs: List[PairEvidence] = []
    for i, j in combinations(range(n), 2):
        ev = pair_evidence(messages[i], messages[j], N)
        ev.i, ev.j = i, j
        pairs.append(ev)
    exploitable_total = sum(ev.exploitable for ev in pairs)
    undet = sum(1 for ev in pairs if ev.verdict == "undetermined")
    return DepthMap(pairs, _components(pairs, n, "opening"),
                    _components(pairs, n, "body"), exploitable_total, undet)


# ---------------------------------------------------------------------------
# Selftest — plant ground truth and verify the honesty boundary holds.
# ---------------------------------------------------------------------------

def _related(base: List[int], n_edits: int, rng, N: int) -> List[int]:
    out = list(base)
    pos = rng.choice(len(out), size=n_edits, replace=False)
    for p in pos:
        out[p] = int(rng.integers(0, N))
    return out


def selftest() -> List[tuple[str, bool]]:
    import numpy as np
    out: List[tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(7)
    T = 90

    # ---- Plant 1: ONE GLOBAL keystream; tree-structured plaintexts. ----
    K = rng.integers(0, N, size=T)
    base = list(rng.integers(0, N, size=T))
    # group X: 3 near-duplicate messages (share opening + related body)
    X = [list(base) for _ in range(3)]
    for m in X:
        for t in range(20, T):                 # diverge after a 20-long opening
            if rng.random() < 0.5:
                m[t] = int(rng.integers(0, N))
    # group Y: 2 unrelated messages (independent plaintext) under the SAME key
    Y = [list(rng.integers(0, N, size=T)) for _ in range(2)]
    # prepend the universal header so position 0..2 behaves like the corpus
    plains = X + Y
    for m in plains:
        m[0] = int(rng.integers(0, N))          # per-message index
    msgs = [[(plains[k][t] + int(K[t])) % N for t in range(T)] for k in range(5)]

    dm = build(msgs, N)
    # near-duplicate group X all in one proven component (body-persistent)
    compX = [c for c in dm.body_components if 0 in c][0]
    out.append(("global-key: near-duplicate group proven shared (all 3 together)",
                set([0, 1, 2]).issubset(set(compX))))
    # the two UNRELATED messages (share the key but differ in plaintext) must be
    # UNDETERMINED — the honest limit: we cannot prove their (real) sharing...
    ev34 = next(e for e in dm.pairs if e.i == 3 and e.j == 4)
    out.append(("global-key: unrelated pair (truly shared) -> UNDETERMINED",
                ev34.verdict == "undetermined"))
    # ...and we must NEVER emit a 'proven-independent' verdict.
    out.append(("no verdict ever claims independence",
                all("independent" not in e.verdict for e in dm.pairs)))

    # ---- Plant 2: PER-GROUP keystreams; unrelated plaintext everywhere. ----
    K1 = rng.integers(0, N, size=T); K2 = rng.integers(0, N, size=T)
    g1 = [list(rng.integers(0, N, size=T)) for _ in range(3)]
    g2 = [list(rng.integers(0, N, size=T)) for _ in range(3)]
    m1 = [[(g1[k][t] + int(K1[t])) % N for t in range(T)] for k in range(3)]
    m2 = [[(g2[k][t] + int(K2[t])) % N for t in range(T)] for k in range(3)]
    allm = m1 + m2
    dm2 = build(allm, N)
    # unrelated plaintext -> nobody is provably shared (equality ~1/N), even the
    # within-group pairs that DO share a key. Honest under-claim.
    out.append(("per-group + unrelated plaintext: no false proven-sharing",
                all(e.verdict == "undetermined" for e in dm2.pairs)))

    # ---- Plant 3: identical-run detection is exact. ----
    a = list(rng.integers(0, N, size=T)); b = list(a)
    for t in range(10, T):
        b[t] = int(rng.integers(0, N))
    a[0], b[0] = 1, 2                            # differing index at pos 0
    out.append(("identical prefix measured past the index position",
                identical_prefix(a, b) == 9))    # positions 1..9
    eviab = pair_evidence(a, b, N)
    out.append(("long identical run alone proves shared keystream (opening)",
                eviab.opening_proven))

    # ---- Plant 4: exploitable depth counts differing positions of a body-proven pair.
    out.append(("exploitable depth > 0 for a body-proven near-duplicate pair",
                any(e.exploitable > 0 for e in dm.pairs if e.body_proven)))
    out.append(("exploitable depth = 0 where body sharing is not proven",
                all(e.exploitable == 0 for e in dm.pairs if not e.body_proven)))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} depthmap checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
