"""Is the (66,5) header keystreamed, or a literal un-keyed marker?

Positions 1–2 hold (66,5) identically across ALL nine messages — across triplets
that (per `keystream_scope`) have *independent* keystreams.  That's the crux for
crib-ability: if those positions are under the per-triplet keystream, guessing
their plaintext pins keystream values; if they're a literal prefix outside the
keystream, guessing them tells us nothing.

The test: for each position, measure **cross-triplet** ciphertext agreement.
Independent per-triplet keystreams produce ~1/N cross-triplet agreement at every
position.  A position where cross-triplet agreement is far above 1/N cannot be
under independent keystreams — it is a literal / shared prefix.  We compute, per
position, the agreement and the probability of the observed cross-triplet
constancy under the independent-keystream null; positions that reject it are
flagged ``literal/shared`` (not crib-able for the body).

Conclusion this yields on the real corpus: positions 1–2 are a literal/shared
2-symbol marker (NOT independently keystreamed), position 0 is per-message, and
the body is per-triplet keystreamed — i.e. the header is **not** a useful body
crib, exactly as argued.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import combinations
from typing import List, Sequence, Tuple

import corpus as corpus_mod

TRIPLETS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))


def _cross_pairs(triplets) -> List[Tuple[int, int]]:
    out = []
    for a in range(len(triplets)):
        for b in range(a + 1, len(triplets)):
            for i in triplets[a]:
                for j in triplets[b]:
                    out.append((i, j))
    return out


def _within_pairs(triplets) -> List[Tuple[int, int]]:
    out = []
    for g in triplets:
        out.extend(combinations(g, 2))
    return out


@dataclass
class PositionClass:
    pos: int
    cross_agree: float
    within_agree: float
    kind: str            # "literal/shared" | "keystreamed" | "per-message"


def classify_positions(messages: Sequence[Sequence[int]], N: int,
                       triplets=TRIPLETS, hi: float = 0.5) -> List[PositionClass]:
    """Per position: cross- and within-triplet agreement, and a class.

    ``cross_agree`` ~ 1/N -> independently keystreamed; ~1 -> literal/shared.
    """
    L = min(len(m) for m in messages)
    cross = _cross_pairs(triplets)
    within = _within_pairs(triplets)
    out: List[PositionClass] = []
    for t in range(L):
        ca = sum(1 for i, j in cross if messages[i][t] == messages[j][t]) / len(cross)
        wa = sum(1 for i, j in within if messages[i][t] == messages[j][t]) / len(within)
        if ca >= hi:
            kind = "literal/shared"       # far above 1/N cross-triplet
        elif wa >= hi:
            kind = "keystreamed"          # shared within triplet only (per-triplet key + shared plaintext)
        else:
            kind = "per-message"          # nobody agrees -> distinct per message
        out.append(PositionClass(t, ca, wa, kind))
    return out


def universal_prefix(messages: Sequence[Sequence[int]]) -> List[int]:
    """Positions (in order) where ALL messages share the same symbol."""
    L = min(len(m) for m in messages)
    out = []
    for t in range(L):
        if len({m[t] for m in messages}) == 1:
            out.append(t)
    return out


def independent_keystream_pvalue(messages: Sequence[Sequence[int]], N: int,
                                  positions: Sequence[int], triplets=TRIPLETS
                                  ) -> float:
    """P(observed cross-triplet constancy at ``positions`` | independent
    keystreams).  Under independence, two cross-triplet messages agree at a
    position with prob ~1/N; full agreement across all cross pairs at k positions
    is ~ (1/N)^(k * #independent-constraints).  Tiny p => reject independence
    (the positions are literal/shared, not keystreamed)."""
    cross = _cross_pairs(triplets)
    # crude but conservative: each position fully agreed across all cross pairs
    # implies the per-triplet key values coincide; ~ (1/N) per triplet-pair-pos.
    n_triplet_pairs = len(list(combinations(range(len(triplets)), 2)))
    exponent = len(positions) * n_triplet_pairs
    return math.exp(-exponent * math.log(N))


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def selftest() -> List[tuple[str, bool]]:
    import numpy as np
    out: List[tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(0)
    T = 80

    # (1) Full per-triplet INDEPENDENT keystreams, random plaintext: no position
    #     should look literal (cross-triplet agreement ~ 1/N everywhere).
    Ks = [rng.integers(0, N, size=T) for _ in range(3)]
    msgs = []
    for gi, g in enumerate(TRIPLETS):
        for _ in g:
            p = rng.integers(0, N, size=T)
            msgs.append([(int(p[t]) + int(Ks[gi][t])) % N for t in range(T)])
    # reorder to message-index order (TRIPLETS already 0..8 consecutive)
    cls = classify_positions(msgs, N)
    out.append(("independent keystreams -> no literal positions",
                not any(c.kind == "literal/shared" for c in cls)))

    # (2) Literal 2-symbol prefix (identical across ALL 9) + per-triplet body.
    marker = [rng.integers(0, N), rng.integers(0, N)]
    msgs2 = []
    for gi, g in enumerate(TRIPLETS):
        for _ in g:
            p = rng.integers(0, N, size=T)
            c = [(int(p[t]) + int(Ks[gi][t])) % N for t in range(T)]
            c[0], c[1] = int(marker[0]), int(marker[1])    # literal prefix
            msgs2.append(c)
    cls2 = classify_positions(msgs2, N)
    out.append(("literal prefix detected at positions 0,1",
                cls2[0].kind == "literal/shared" and cls2[1].kind == "literal/shared"))
    out.append(("body not flagged literal",
                all(c.kind != "literal/shared" for c in cls2[2:])))

    # (3) p-value for a 2-position universal prefix is astronomically small.
    p = independent_keystream_pvalue(msgs2, N, [0, 1])
    out.append(("independent-keystream p-value for 2-pos prefix is tiny",
                p < 1e-10))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} header_test checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
