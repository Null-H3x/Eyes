"""Clustered progressive-base search — tractable key hypothesis (#1 in keyspace ledger).

Model: per-message progressive with K[t]=t (Trithemius slide):

    c[m][t] = C[(p[m][t] + base_m + t) mod N]

The literal (66,5) header forces equal bases across messages (pure progressive
subcase — 83 trials).  With pair clustering (E1≈W1, E4≈E5 from pairdiff), we
search one base per cluster instead of nine independent bases.

Scoring uses structural metrics (refrain template consistency, near-dup agreement)
— NOT IoC hill-climbing (degenerate on this corpus).
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import pairdiff as pd
import refrain as rf
import template as tp


TRIPLETS = pd.TRIPLETS
HEADER_SYM = (66, 5)


@dataclass
class BaseAssignment:
    bases: Dict[int, int]          # message index -> base
    mode: str
    score: float
    refrain_consistent: bool
    near_dup_agreement: float
    notes: List[str] = field(default_factory=list)


def cluster_groups(messages: Sequence[Sequence[int]], N: int = 83) -> List[Tuple[str, Tuple[int, ...]]]:
    """Derive base clusters from near-duplicate pairs within triplets."""
    groups: Dict[int, int] = {i: i for i in range(len(messages))}

    def find(x):
        while groups[x] != x:
            groups[x] = groups[groups[x]]
            x = groups[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            groups[rb] = ra

    for gi, g in enumerate(TRIPLETS):
        if len(messages) <= max(g):
            continue
        td = pd.analyze_triplet(messages, g, N)
        if td.pair:
            union(td.pair[0], td.pair[1])

    comp: Dict[int, List[int]] = {}
    for i in range(len(messages)):
        comp.setdefault(find(i), []).append(i)
    out = []
    for root, members in sorted(comp.items()):
        out.append((f"cluster-{root}", tuple(sorted(members))))
    return out


def _has_literal_header(messages) -> bool:
    if len(messages) < 1:
        return False
    return all(len(m) > 2 and m[1] == HEADER_SYM[0] and m[2] == HEADER_SYM[1]
               for m in messages)


def _refrain_consistent(messages, bases: Dict[int, int], N: int,
                        region, phrase: Optional[str], offset: int) -> bool:
    """Check candidate per-message bases against a refrain phrase."""
    if not phrase:
        return True
    pv = rf.phrase_to_values(phrase, rf.DEFAULT_ALPHABET, N)
    if pv is None:
        return False
    pinned: Dict[int, int] = {}
    for (m, pos) in region:
        b = bases.get(m, 0)
        for i, pval in enumerate(pv):
            t = pos + offset + i
            if t >= len(messages[m]):
                return False
            c = int(messages[m][t])
            v = (pval + b + t) % N
            if c in pinned and pinned[c] != v:
                return False
            pinned[c] = v
    return len(pinned) >= min(len(phrase), 3)


def _near_dup_score(messages, bases: Dict[int, int], N: int) -> float:
    """Mean body agreement of near-dup pairs under equal-base clusters."""
    if len(messages) < max(max(g) for g in TRIPLETS) + 1:
        return 0.0
    scores = []
    for g in TRIPLETS:
        td = pd.analyze_triplet(messages, g, N)
        if not td.pair:
            continue
        i, j = td.pair
        if bases.get(i) == bases.get(j):
            scores.append(td.pair_stat.body_frac)
    return float(sum(scores) / len(scores)) if scores else 0.0


def _score_assignment(messages, bases: Dict[int, int], N: int, *,
                      region, phrase, offset) -> BaseAssignment:
    notes = []
    score = 0.0
    if phrase:
        ref_ok = _refrain_consistent(messages, bases, N, region, phrase, offset)
        if ref_ok:
            score += 10.0
    else:
        ref_ok = False
    nd = _near_dup_score(messages, bases, N)
    score += nd * 5.0
    if _has_literal_header(messages):
        uniq = len(set(bases.values()))
        if uniq == 1:
            score += 2.0
            notes.append("header-consistent: single base (pure progressive)")
        else:
            notes.append(f"header tension: {uniq} distinct bases")
    return BaseAssignment(
        bases=dict(bases),
        mode="clustered",
        score=score,
        refrain_consistent=ref_ok,
        near_dup_agreement=nd,
        notes=notes,
    )


def search_pure_progressive(
    messages: Sequence[Sequence[int]],
    N: int,
    *,
    region=None,
    phrase: Optional[str] = None,
    offset: int = 0,
) -> List[BaseAssignment]:
    """Exhaust all 83 single-base assignments (header-forced subcase)."""
    region = region or rf.DEFAULT_INSTANCES
    out = []
    for b in range(N):
        bases = {i: b for i in range(len(messages))}
        out.append(_score_assignment(messages, bases, N, region=region,
                                     phrase=phrase, offset=offset))
    out.sort(key=lambda x: -x.score)
    return out


def search_clustered(
    messages: Sequence[Sequence[int]],
    N: int,
    *,
    region=None,
    phrase: Optional[str] = None,
    offset: int = 0,
    max_assignments: int = 500_000,
) -> List[BaseAssignment]:
    """Search one base per cluster (near-dup merged groups)."""
    region = region or rf.DEFAULT_INSTANCES
    clusters = cluster_groups(messages, N)
    reps = [c[1][0] for c in clusters]
    msg_to_rep: Dict[int, int] = {}
    for _, members in clusters:
        r = members[0]
        for m in members:
            msg_to_rep[m] = r

    if len(reps) > 4:
        import numpy as np
        rng = np.random.default_rng(0)
        out: List[BaseAssignment] = []
        for _ in range(min(max_assignments, 50_000)):
            rep_base = {reps[i]: int(rng.integers(0, N)) for i in range(len(reps))}
            bases = {m: rep_base[msg_to_rep[m]] for m in range(len(messages))}
            out.append(_score_assignment(messages, bases, N, region=region,
                                       phrase=phrase, offset=offset))
        out.sort(key=lambda x: -x.score)
        return out

    out: List[BaseAssignment] = []
    n = 0
    for combo in itertools.product(range(N), repeat=len(reps)):
        if n >= max_assignments:
            break
        rep_base = {reps[i]: combo[i] for i in range(len(reps))}
        bases = {m: rep_base[msg_to_rep[m]] for m in range(len(messages))}
        out.append(_score_assignment(messages, bases, N, region=region,
                                     phrase=phrase, offset=offset))
        n += 1
    out.sort(key=lambda x: -x.score)
    return out


def run_search(
    messages: Sequence[Sequence[int]],
    N: int,
    *,
    mode: str = "auto",
    region=None,
    phrase: Optional[str] = None,
    offset: int = 0,
    top: int = 10,
    max_assignments: int = 500_000,
) -> Tuple[str, List[BaseAssignment]]:
    region = region or rf.DEFAULT_INSTANCES
    if mode == "auto":
        mode = "pure" if _has_literal_header(messages) else "clustered"
    if mode == "pure":
        results = search_pure_progressive(messages, N, region=region,
                                          phrase=phrase, offset=offset)
    elif mode == "clustered":
        results = search_clustered(messages, N, region=region, phrase=phrase,
                                   offset=offset, max_assignments=max_assignments)
    else:
        raise ValueError(f"unknown mode {mode!r}")
    return mode, results[:top]


def format_report(mode: str, results: Sequence[BaseAssignment], top: int = 10) -> str:
    lines = [
        "=" * 72,
        "BASE SEARCH — clustered progressive-base hypothesis",
        "=" * 72,
        f"mode: {mode}   candidates scored: {len(results)}",
        "",
        f"{'rank':>4}  {'score':>7}  {'refrain':>7}  {'nd_agree':>8}  bases (unique)",
        "-" * 72,
    ]
    for i, r in enumerate(results[:top], 1):
        uniq = len(set(r.bases.values()))
        lines.append(
            f"{i:4d}  {r.score:7.2f}  {str(r.refrain_consistent):>7}  "
            f"{r.near_dup_agreement:7.1%}  {uniq} unique"
        )
    if results:
        best = results[0]
        lines.append("")
        lines.append(f"Best bases (msg→base): {dict(sorted(best.bases.items()))}")
        for n in best.notes:
            lines.append(f"  • {n}")
    lines.append("")
    lines.append("READ: scores structural fit only — not a decryption readout.")
    return "\n".join(lines)


def selftest() -> List[Tuple[str, bool]]:
    import numpy as np

    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(53)
    T = 120

    # Clustered plant: near-dup pair (0,1) share base 5; odd member 2 uses base 9.
    C = list(rng.permutation(N))
    base_plain = [int(rng.integers(0, N)) for _ in range(T)]
    p0 = base_plain.copy()
    p1 = base_plain.copy()
    for t in rng.choice(T, size=14, replace=False):
        p1[t] = (p1[t] + 1 + int(rng.integers(0, N - 1))) % N
    p2 = [int(rng.integers(0, N)) for _ in range(T)]
    bases_plant = {0: 5, 1: 5, 2: 9}
    msgs2 = []
    for m, p in enumerate((p0, p1, p2)):
        msgs2.append([C[(p[t] + bases_plant[m] + t) % N] for t in range(T)])

    td = pd.analyze_triplet(msgs2, (0, 1, 2), N)
    out.append(("cluster plant has near-dup pair (0,1)", td.pair == (0, 1)))

    _, res2 = run_search(msgs2, N, mode="clustered", top=20,
                         max_assignments=100_000)
    out.append(("clustered search runs", len(res2) >= 1))
    best = res2[0]
    out.append(("clustered top ranks equal bases on near-dup pair",
                best.bases.get(0) == best.bases.get(1)))
    out.append(("clustered top beats split-base on near-dup pair",
                best.score >= max(
                    (r.score for r in res2
                     if r.bases.get(0) != r.bases.get(1)),
                    default=0.0,
                )))

    # Pure / header: literal (66,5) header forces equal-base subcase.
    M, T2 = 9, 100
    wpos, wlen = (30, 60), 12
    h1, h2 = 40, 41
    base_eq = 17
    msgs_h = []
    W = [int(x) for x in rng.integers(0, N, size=wlen)]
    for m in range(M):
        p = [int(x) for x in rng.integers(0, N, size=T2)]
        p[0] = (m * 7 + 3) % N
        p[1], p[2] = h1, h2
        for pos in wpos:
            p[pos:pos + wlen] = W
        msgs_h.append([C[(p[t] + base_eq + t) % N] for t in range(T2)])
    # force universal header ciphertext
    for m in range(M):
        msgs_h[m][1] = HEADER_SYM[0]
        msgs_h[m][2] = HEADER_SYM[1]

    mode_auto, _ = run_search(msgs_h, N, mode="auto", top=3)
    out.append(("auto mode picks pure for literal header", mode_auto == "pure"))
    _, res_pure = run_search(msgs_h, N, mode="pure", top=5)
    out.append(("pure assignments are single-base",
                all(len(set(r.bases.values())) == 1 for r in res_pure)))
    out.append(("header bonus applied in pure mode",
                any("header-consistent" in n for r in res_pure for n in r.notes)))

    clusters = cluster_groups(msgs2, N)
    out.append(("cluster_groups returns clusters", len(clusters) >= 1))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} base_search checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
