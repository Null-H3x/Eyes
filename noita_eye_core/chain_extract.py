"""Contamination-resistant maximal-aligned-isomorph extractor.

PROBLEM.  find_isomorphs matches by skeleton, so it returns partial/misaligned
pairs (same repeat-pattern, *different* plaintext at the singleton positions).
Those inject false alphabet constraints that defeat strict chaining
(chain_models.per_message_progressive_chain): on the real corpus the raw chain
"contradicts" mostly because of contamination, not because the model is wrong.

KEY FACT (verified, see selftest `oracle_*`).  Given the CORRECT alphabet, the
per-message-progressive constraints separate genuine fully-aligned isomorphs from
contaminated ones essentially perfectly: every genuine pair reduces to
'redundant' (already implied) and ~every contaminated pair reduces to
'contradiction'.  So the whole game is bootstrapping a correct alphabet.

ALGORITHM (anchor-then-classify).
  1. CALIBRATE a clean anchor threshold: the highest `min_repeats` at which the
     isomorph set is still statistically clean (shuffle-null count / observed is
     tiny).  High-repeat skeletons are specific to genuine repeats; chance/partial
     matches mostly vanish, so the anchor set is nearly contamination-free.
  2. BUILD the consensus alphabet from the anchor set by purify-to-fixed-point:
     greedily solve (dropping contradictions), then keep only pairs that are
     fully 'redundant' against the solution, re-solve, repeat to a fixed point.
  3. CLASSIFY a much broader isomorph set against the anchored alphabet — a pair
     is clean iff every constraint is 'redundant', contaminated iff any
     'contradiction'.  This filters contamination even at high outlier rates.
  4. MAXIMALISE: merge clean fixed-length pairs that share (m1, m2, p2-p1) and
     overlap into maximal aligned runs, and recover the alphabet up to rotation.

Validation (paranoia) lives in selftest(): it (a) shows the oracle separation,
(b) recovers the planted alphabet up to a single rotation from contaminated data
with high precision/recall against ground truth, and (c) checks discrimination —
under per-message-progressive, WRONG-model (autokey) data does NOT yield a large
single-rotation alphabet, so a large recovery is meaningful rather than a
permissive artifact.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from isomorph import GFSystem, IsoPair, find_isomorphs, skeleton
import chain_models as cm


def free_delta_rows(pr: IsoPair, messages: Sequence[Sequence[int]], N: int):
    """δ-eliminated free-offset (autokey/clock) constraints: subtract position-0
    so the unknown constant offset cancels: x[Dᵢ]-x[Aᵢ]-x[D₀]+x[A₀]=0. This is the
    WEAKEST interrelation; it is permissive (rarely contradicts), so under it the
    extractor flags almost no contamination — the contrast that shows
    per-message-progressive is genuinely selective rather than fitting anything."""
    A0 = int(messages[pr.m1][pr.p1])
    D0 = int(messages[pr.m2][pr.p2])
    for i in range(1, pr.length):
        A = int(messages[pr.m1][pr.p1 + i])
        D = int(messages[pr.m2][pr.p2 + i])
        row: Dict[int, int] = {}
        for v, c in ((D, 1), (A, N - 1), (D0, N - 1), (A0, 1)):
            row[v] = (row.get(v, 0) + c) % N
        row = {v: c for v, c in row.items() if c}
        yield row, 0


# ---------------------------------------------------------------------------
# Maximal aligned isomorphs
# ---------------------------------------------------------------------------

def maximalise(pairs: Sequence[IsoPair]) -> List[IsoPair]:
    """Merge fixed-length pairs that share (m1, m2, p2-p1) and overlap/abut into
    maximal aligned runs.  Two windows with the same offset (p2-p1) and
    overlapping position ranges describe the SAME aligned segment seen through
    different sliding windows; the maximal run is their union."""
    groups: Dict[Tuple[int, int, int], List[IsoPair]] = defaultdict(list)
    for pr in pairs:
        groups[(pr.m1, pr.m2, (pr.p2 - pr.p1))].append(pr)
    out: List[IsoPair] = []
    for (m1, m2, off), grp in groups.items():
        grp.sort(key=lambda p: p.p1)
        cs, ce = grp[0].p1, grp[0].p1 + grp[0].length
        cexact = grp[0].exact
        for pr in grp[1:]:
            s, e = pr.p1, pr.p1 + pr.length
            if s <= ce:                      # overlap or abut -> extend run
                ce = max(ce, e)
                cexact = cexact and pr.exact
            else:
                out.append(IsoPair(m1, cs, m2, cs + off, ce - cs, cexact))
                cs, ce, cexact = s, e, pr.exact
        out.append(IsoPair(m1, cs, m2, cs + off, ce - cs, cexact))
    out.sort(key=lambda p: p.length, reverse=True)
    return out


# ---------------------------------------------------------------------------
# Consensus alphabet (purify to fixed point)
# ---------------------------------------------------------------------------

def _build(messages, pairs, idxs, rows_fn, N) -> GFSystem:
    gf = GFSystem(N)
    for j in sorted(idxs, key=lambda j: pairs[j].length, reverse=True):
        snap = gf.snapshot()
        ok = True
        for row, rhs in rows_fn(pairs[j], messages, N):
            if gf.add(row, rhs) == "contradiction":
                ok = False
                break
        if not ok:
            gf.restore(snap)
    return gf


def _redundant(gf: GFSystem, pr, messages, rows_fn, N) -> bool:
    saw = False
    for row, rhs in rows_fn(pr, messages, N):
        v = gf.classify(row, rhs)
        if v == "contradiction":
            return False
        if v == "pivot":
            return False
        saw = True
    return saw


def consensus_alphabet(messages, pairs, N, rows_fn=cm.per_msg_prog_rows,
                       max_rounds: int = 8) -> Tuple[GFSystem, set]:
    """Purify-to-fixed-point: solve, keep only fully-redundant pairs, repeat."""
    cur = set(range(len(pairs)))
    gf = _build(messages, pairs, cur, rows_fn, N)
    for _ in range(max_rounds):
        nxt = {j for j in range(len(pairs))
               if _redundant(gf, pairs[j], messages, rows_fn, N)}
        gf = _build(messages, pairs, nxt, rows_fn, N)
        if nxt == cur:
            break
        cur = nxt
    return gf, cur


# ---------------------------------------------------------------------------
# Cleanliness calibration
# ---------------------------------------------------------------------------

def _null_ratio(messages, length, min_repeats, n_shuffle=24, seed=0) -> float:
    import numpy as np
    obs = len(find_isomorphs(messages, length, min_repeats))
    if obs == 0:
        return float("inf")
    rng = np.random.default_rng(seed)
    nulls = [len(find_isomorphs([list(rng.permutation(m)) for m in messages],
                                length, min_repeats)) for _ in range(n_shuffle)]
    return (sum(nulls) / len(nulls)) / obs


def calibrate_anchor(messages, length, min_anchor=8, max_repeats=8,
                     clean_ratio=0.10, seed=0) -> int:
    """Highest min_repeats giving >= min_anchor pairs at a clean null ratio."""
    best = None
    for mr in range(max_repeats, 1, -1):
        pairs = find_isomorphs(messages, length, mr)
        if len(pairs) < min_anchor:
            continue
        if _null_ratio(messages, length, mr, seed=seed) <= clean_ratio:
            return mr
        if best is None:
            best = mr
    return best if best is not None else 3


# ---------------------------------------------------------------------------
# Top-level extraction
# ---------------------------------------------------------------------------

@dataclass
class ExtractResult:
    clean_pairs: List[IsoPair]          # maximal, aligned, consensus-consistent
    n_clean_windows: int                # fixed-length clean windows before merge
    n_flagged: int                      # isomorph windows rejected as contaminated
    anchor_repeats: int
    anchor_null_ratio: float
    symbols_recovered: int              # symbols linked in the largest component
    positions: Dict[int, int]           # symbol -> recovered alphabet position
    positions_distinct: int             # distinct determined positions in component
    recovery_ratio: float               # distinct/linked: 1.0 = ordered (injective)
    _gf: Optional[GFSystem] = field(default=None, repr=False)


def extract(messages: Sequence[Sequence[int]], base_len: int = 13,
            broad_repeats: int = 3, rows_fn: Callable = cm.per_msg_prog_rows,
            anchor_repeats: Optional[int] = None, seed: int = 0) -> ExtractResult:
    N = max(int(max(m)) for m in messages) + 1
    if anchor_repeats is None:
        anchor_repeats = calibrate_anchor(messages, base_len, seed=seed)
    nr = _null_ratio(messages, base_len, anchor_repeats, seed=seed)

    anchor = find_isomorphs(messages, base_len, anchor_repeats)
    gf, _ = consensus_alphabet(messages, anchor, N, rows_fn)

    broad = find_isomorphs(messages, base_len, broad_repeats)
    clean_idx, flagged = [], 0
    for i, pr in enumerate(broad):
        if _redundant(gf, pr, messages, rows_fn, N):
            clean_idx.append(i)
        else:
            flagged += 1
    clean = [broad[i] for i in clean_idx]
    maximal = maximalise(clean)

    # recover alphabet up to rotation: largest connected component of symbols
    val = gf.solve()
    parent = list(range(N))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for pr in clean:
        for i in range(pr.length):
            a = int(messages[pr.m1][pr.p1 + i])
            d = int(messages[pr.m2][pr.p2 + i])
            parent[find(a)] = find(d)
    comp: Dict[int, List[int]] = defaultdict(list)
    for s in range(N):
        if s in val:
            comp[find(s)].append(s)
    big = max(comp.values(), key=len) if comp else []
    positions = {s: val[s] for s in big}

    # Honest recovery measure: an alphabet is a BIJECTION, so a genuine recovery
    # gives DISTINCT positions for distinct symbols (up to one global rotation).
    # Free (under-determined) variables get gauged to 0 and collapse onto each
    # other, so a low distinct/linked ratio means the alphabet is NOT actually
    # ordered — only transitively linked.  (Validated: plant -> ratio ~1.0;
    # real corpus -> ratio << 1, i.e. ordering remains open.)
    distinct = len(set(positions.values()))
    ratio = distinct / len(big) if big else 0.0

    return ExtractResult(maximal, len(clean), flagged, anchor_repeats, nr,
                         len(positions), positions, distinct, ratio, _gf=gf)


# ---------------------------------------------------------------------------
# Selftest — paranoia audit
# ---------------------------------------------------------------------------

def _aligned(pr) -> bool:
    WP, WL = cm._WORD_POS, cm._WLEN

    def woff(p):
        for q in WP:
            if q <= p < q + WL:
                return p - q
        return None

    def iw(p, L):
        return any(q <= p and p + L <= q + WL for q in WP)
    return (iw(pr.p1, pr.length) and iw(pr.p2, pr.length)
            and woff(pr.p1) == woff(pr.p2))


def selftest() -> List[Tuple[str, bool]]:
    import numpy as np
    out: List[Tuple[str, bool]] = []
    N = 83

    # ---- oracle separation: with the true alphabet, per-msg-prog is decisive
    rng = np.random.default_rng(2024)
    mp, C, bases = cm.plant_per_msg_progressive(N, rng, M=9, T=110)
    monster = find_isomorphs(mp, 12, 3)
    gf_oracle = GFSystem(N)
    for pr in monster:
        if _aligned(pr):
            for row, rhs in cm.per_msg_prog_rows(pr, mp, N):
                gf_oracle.add(row, rhs)
    al_red = sum(1 for pr in monster if _aligned(pr)
                 and _redundant(gf_oracle, pr, mp, cm.per_msg_prog_rows, N))
    con_red = sum(1 for pr in monster if not _aligned(pr)
                  and _redundant(gf_oracle, pr, mp, cm.per_msg_prog_rows, N))
    n_al = sum(_aligned(pr) for pr in monster)
    out.append(("oracle: all genuine pairs are redundant under true alphabet",
                al_red == n_al))
    out.append(("oracle: <1% of contaminated pairs survive the true alphabet",
                con_red <= 0.01 * (len(monster) - n_al) + 1))

    # ---- end-to-end extraction from contaminated data
    res = extract(mp, base_len=13, broad_repeats=3)
    gens = sum(_aligned(pr) for pr in monster)
    out.append(("anchor calibrated to a clean threshold (null ratio < 0.1)",
                res.anchor_null_ratio < 0.10))
    out.append(("extractor flags the bulk of contamination",
                res.n_flagged > res.n_clean_windows))
    # recovered alphabet matches planted C up to ONE rotation
    Cinv = {s: i for i, s in enumerate(C)}
    rot = Counter((res.positions[s] - Cinv[s]) % N
                  for s in res.positions if s in Cinv)
    dom = rot.most_common(1)[0][1] if rot else 0
    out.append(("recovers a large alphabet up to a SINGLE rotation",
                dom >= 60 and dom == sum(rot.values())))
    out.append(("recovery is INJECTIVE on clean data (distinct positions, ratio ~1)",
                res.recovery_ratio >= 0.95))

    # precision/recall of clean windows vs ground truth (re-derive on broad set)
    broad = find_isomorphs(mp, 13, 3)
    clean = [pr for pr in broad
             if _redundant(res._gf, pr, mp, cm.per_msg_prog_rows, N)]
    ka = sum(_aligned(pr) for pr in clean)
    prec = ka / max(1, len(clean))
    out.append(("clean set is high-precision (>= 0.95) against ground truth",
                prec >= 0.95))

    # ---- discrimination: WRONG model (autokey) must not yield a big alphabet
    rng2 = np.random.default_rng(99)
    ma = cm.plant_autokey(N, rng2, M=9, T=110)
    resa = extract(ma, base_len=13, broad_repeats=3, rows_fn=cm.per_msg_prog_rows)
    out.append(("per-msg-prog yields far fewer clean windows on autokey data "
                "(discrimination preserved)",
                resa.n_clean_windows <= res.n_clean_windows // 4))
    out.append(("autokey alphabet is NOT injectively recovered "
                "(low distinct-position ratio vs true-model data)",
                resa.recovery_ratio < 0.95))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} chain_extract checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
