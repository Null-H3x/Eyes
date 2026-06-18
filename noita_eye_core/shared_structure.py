"""Model-independent shared-structure map.

Everything here depends ONLY on 'same glyph = same glyph' (isomorph skeletons) —
no cipher-model assumption. It maps where the corpus repeats the SAME plaintext:

  * opening_extent_matrix: for each message pair, the isomorph extent from the
    body opening (pos 3, after the (66,5) header) — how long they share plaintext.
  * triplet_openings: the three natural triplets' 3-way shared-opening extents,
    null-calibrated against random aligned starts.
  * repeated_passages: a census of maximal repeated passages anywhere in the
    corpus (merged sliding windows), grouped into same-plaintext families.

Isomorphs (same repeat-pattern, different values) require interrelated alphabets
but the FACT of the repeat is model-free; this is the safe structural juice that
licenses no model.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple


def _skel(seq) -> Tuple[int, ...]:
    first: Dict[int, int] = {}
    return tuple(first.setdefault(int(v), i) for i, v in enumerate(seq))


def iso_extent(messages, m1, p1, m2, p2) -> int:
    L = 0
    a, b = messages[m1], messages[m2]
    while p1 + L < len(a) and p2 + L < len(b):
        if _skel(a[p1:p1 + L + 1]) != _skel(b[p2:p2 + L + 1]):
            break
        L += 1
    return L


def kway_extent(messages, starts) -> int:
    L = 0
    while all(p + L < len(messages[m]) for m, p in starts):
        if len({_skel(messages[m][p:p + L + 1]) for m, p in starts}) > 1:
            break
        L += 1
    return L


def opening_extent_matrix(messages, start: int = 3) -> List[List[int]]:
    n = len(messages)
    return [[0 if i == j else iso_extent(messages, i, start, j, start)
             for j in range(n)] for i in range(n)]


@dataclass
class TripletResult:
    name: str
    members: Tuple[int, ...]
    extent: int
    null_mean: float
    significant: bool


def triplet_openings(messages, triplets, start: int = 3, n_null: int = 300,
                     seed: int = 0) -> List[TripletResult]:
    import numpy as np
    rng = np.random.default_rng(seed)
    n = len(messages)
    nulls = []
    for _ in range(n_null):
        st = [(m, int(rng.integers(start, len(messages[m]) - 10))) for m in range(n)]
        # 3-way null: random aligned starts among 3 random messages
        pick = list(rng.choice(n, 3, replace=False))
        nulls.append(kway_extent(messages, [(int(m), st[m][1]) for m in pick]))
    nm = float(np.mean(nulls))
    out = []
    for name, members in triplets:
        ext = kway_extent(messages, [(m, start) for m in members])
        out.append(TripletResult(name, tuple(members), ext, nm, ext > nm + 2 * float(np.std(nulls))))
    return out


def repeated_passages(messages, min_len: int = 12) -> List[dict]:
    """Maximal repeated passages (>= min_len) grouped into same-plaintext families."""
    # collect isomorph pairs at min_len, then extend each to maximal and merge
    bysk = defaultdict(list)
    for m, msg in enumerate(messages):
        for p in range(len(msg) - min_len + 1):
            sk = _skel(msg[p:p + min_len])
            if min_len - len(set(sk)) >= 2:        # require internal repeat
                bysk[sk].append((m, p))
    # for each family of >=2 starts, extend to the maximal common extent
    fams = []
    seen = set()
    for starts in bysk.values():
        if len(starts) < 2:
            continue
        key = tuple(sorted(starts))
        if key in seen:
            continue
        seen.add(key)
        ext = kway_extent(messages, starts)
        fams.append({"occurrences": sorted(starts), "count": len(starts),
                     "length": ext,
                     "messages": sorted({m for m, _ in starts})})
    # dedup overlapping (keep the longest per occurrence-set signature)
    fams.sort(key=lambda f: (f["length"], f["count"]), reverse=True)
    # merge families that are sliding windows of the same passage
    merged = []
    used = []
    for f in fams:
        dup = False
        for g in merged:
            # same message-set and overlapping start ranges -> same passage
            if f["messages"] == g["messages"]:
                close = all(any(abs(p - q) <= g["length"] for q, _ in
                                [(qq, mm) for mm, qq in g["occurrences"] if mm == m])
                            for m, p in f["occurrences"])
                if close:
                    dup = True
                    break
        if not dup:
            merged.append(f)
    return merged


# ---------------------------------------------------------------------------
# Selftest — recover planted shared openings + a mid-message repeat.
# ---------------------------------------------------------------------------

def selftest() -> List[Tuple[str, bool]]:
    import numpy as np
    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(0)
    C = list(rng.permutation(N))

    def enc_permsg(p, base):
        return [C[(p[t] + base + t) % N] for t in range(len(p))]
    # 6 messages in 2 triplets; triplet A shares a 20-glyph opening, triplet B a 16.
    T = 90
    openA = [int(v) for v in rng.integers(0, N, size=20)]
    openB = [int(v) for v in rng.integers(0, N, size=16)]
    msgs = []
    bases = [int(b) for b in rng.integers(0, N, size=6)]
    for m in range(6):
        p = [int(rng.integers(0, N)) for _ in range(T)]
        op = openA if m < 3 else openB
        p[3:3 + len(op)] = op            # shared opening per triplet
        msgs.append(enc_permsg(p, bases[m]))

    # opening matrix: within-triplet extents high, cross-triplet low
    mat = opening_extent_matrix(msgs)
    within_A = min(mat[i][j] for i in range(3) for j in range(3) if i != j)
    cross = max(mat[i][j] for i in range(3) for j in range(3, 6))
    out.append(("opening matrix: triplet A shares its opening (>=18)", within_A >= 18))
    out.append(("opening matrix: cross-triplet extent is short (< within)",
                cross < within_A))

    tr = triplet_openings(msgs, [("A", (0, 1, 2)), ("B", (3, 4, 5))], n_null=150)
    out.append(("triplet A opening is significant", tr[0].significant))
    out.append(("triplet B opening is significant", tr[1].significant))

    # mid-message repeat: plant the same 14-glyph passage mid-message in 2 messages
    mid = [int(v) for v in rng.integers(0, N, size=14)]
    p0 = [int(rng.integers(0, N)) for _ in range(T)]; p0[50:64] = mid
    p1 = [int(rng.integers(0, N)) for _ in range(T)]; p1[40:54] = mid
    msgs2 = [enc_permsg(p0, 5), enc_permsg(p1, 9)]
    passages = repeated_passages(msgs2, min_len=12)
    out.append(("repeated_passages finds the mid-message repeat (len>=12)",
                any(f["length"] >= 12 and f["count"] >= 2 for f in passages)))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} shared_structure checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
