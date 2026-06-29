"""Per-triplet progressive-base search — keyspace ledger priority #1 scoped.

Runs clustered / pure base search independently on each triplet (3 messages),
then merges results with global message indices restored.  Tractable when global
9-message search is too coarse: each triplet has at most ~83² clustered assignments.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import base_search as bs
import pairdiff as pd

TRIPLETS = pd.TRIPLETS


@dataclass
class TripletResult:
    triplet: int
    members: Tuple[int, ...]
    mode: str
    best: Optional[bs.BaseAssignment]
    top: List[bs.BaseAssignment] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


@dataclass
class TripletSearchReport:
    results: List[TripletResult] = field(default_factory=list)
    merged_bases: Dict[int, int] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)


def _slice_triplet(messages, triplet: Tuple[int, ...]) -> List[List[int]]:
    return [list(messages[i]) for i in triplet]


def search_triplet(
    messages: Sequence[Sequence[int]],
    triplet_idx: int,
    N: int,
    *,
    mode: str = "auto",
    phrase: Optional[str] = None,
    offset: int = 0,
    region=None,
    top: int = 5,
    max_assignments: int = 500_000,
) -> TripletResult:
    g = TRIPLETS[triplet_idx]
    sub = _slice_triplet(messages, g)
    mode_used, results = bs.run_search(
        sub, N, mode=mode, phrase=phrase, offset=offset,
        region=region, top=top, max_assignments=max_assignments,
    )
    best = results[0] if results else None
    notes = []
    td = pd.analyze_triplet(messages, g, N)
    if td.pair and best:
        i, j = td.pair
        li, lj = g.index(i), g.index(j)
        if best.bases.get(li) == best.bases.get(lj):
            notes.append(f"near-dup pair {i}/{j} share base in sub-search")
        else:
            notes.append(f"near-dup pair {i}/{j} split bases in sub-search")
    return TripletResult(triplet_idx + 1, g, mode_used, best, list(results), notes)


def search_all(
    messages: Sequence[Sequence[int]],
    N: int,
    *,
    mode: str = "auto",
    phrase: Optional[str] = None,
    offset: int = 0,
    top: int = 5,
    max_assignments: int = 500_000,
) -> TripletSearchReport:
    rep = TripletSearchReport()
    merged: Dict[int, int] = {}
    for ti in range(len(TRIPLETS)):
        if max(TRIPLETS[ti]) >= len(messages):
            continue
        tr = search_triplet(
            messages, ti, N, mode=mode, phrase=phrase, offset=offset,
            top=top, max_assignments=max_assignments,
        )
        rep.results.append(tr)
        if tr.best:
            for local, global_m in enumerate(tr.members):
                merged[global_m] = tr.best.bases.get(local, 0)
    rep.merged_bases = merged
    if len(rep.results) >= 2:
        uniq = len(set(rep.merged_bases.values()))
        rep.notes.append(f"merged assignment: {uniq} distinct bases across corpus")
    return rep


def format_report(rep: TripletSearchReport, labels: Optional[Sequence[str]] = None) -> str:
    labels = labels or [str(i) for i in range(9)]
    lines = [
        "=" * 72,
        "TRIPLET BASE SEARCH — per-triplet progressive-base hypothesis",
        "=" * 72,
    ]
    for tr in rep.results:
        lines.append("")
        mem = "/".join(labels[m] for m in tr.members)
        lines.append(f"Triplet {tr.triplet} ({mem})  mode={tr.mode}")
        if tr.best:
            b = tr.best
            lines.append(
                f"  best score={b.score:.2f} refrain={b.refrain_consistent} "
                f"nd={b.near_dup_agreement:.1%} bases={dict(sorted(
                    (tr.members[i], b.bases.get(i, 0)) for i in range(len(tr.members))
                ))}"
            )
        for n in tr.notes:
            lines.append(f"    • {n}")
    if rep.merged_bases:
        lines.append("")
        lines.append("Merged global bases (msg→base):")
        for m in sorted(rep.merged_bases):
            lab = labels[m] if m < len(labels) else str(m)
            lines.append(f"  {lab}: {rep.merged_bases[m]}")
    for n in rep.notes:
        lines.append(f"  • {n}")
    lines.append("")
    lines.append("READ: per-triplet scores are local — cross-triplet base alignment is heuristic.")
    return "\n".join(lines)


def selftest() -> List[Tuple[str, bool]]:
    import numpy as np

    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(53)
    T = 100
    C = list(rng.permutation(N))
    bases_global = {0: 5, 1: 5, 2: 9, 3: 12, 4: 12, 5: 20, 6: 3, 7: 3, 8: 11}

    msgs = []
    for m in range(9):
        p = [int(rng.integers(0, N)) for _ in range(T)]
        msgs.append([C[(p[t] + bases_global[m] + t) % N] for t in range(T)])

    # near-dup within triplet 1: messages 0,1 share plaintext with edits
    base_plain = [int(rng.integers(0, N)) for _ in range(T)]
    for m in (0, 1):
        p = base_plain.copy()
        if m == 1:
            for t in rng.choice(T, size=12, replace=False):
                p[t] = (p[t] + 1) % N
        msgs[m] = [C[(p[t] + bases_global[m] + t) % N] for t in range(T)]

    rep = search_all(msgs, N, mode="clustered", top=5, max_assignments=100_000)
    out.append(("search_all returns 3 triplets", len(rep.results) == 3))
    out.append(("merged bases cover 9 messages", len(rep.merged_bases) == 9))
    t1 = rep.results[0]
    out.append(("triplet1 near-dup bases equal in best",
                t1.best is not None and t1.best.bases.get(0) == t1.best.bases.get(1)))
    out.append(("format_report non-empty", "TRIPLET BASE SEARCH" in format_report(rep)))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} triplet_base_search checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
