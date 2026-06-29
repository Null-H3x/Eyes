"""Position-0 indicator → per-message base analysis (keyspace ledger priority #3).

Under per-message progressive ``c[m][t]=C[(p[m][t]+base_m+t) mod N]``, position 0
carries a distinct per-message ciphertext symbol.  When pos-0 plaintext values follow
a simple indicator (e.g. message ordinal), progressive unwrap yields tractable
constraints on ``base_m``.

This module scans small pos-0 plaintext models and scores candidate base assignments.
It does **not** recover absolute bases without an external anchor — it ranks relative
base patterns for triplet near-dup clusters.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import pairdiff as pd

TRIPLETS = pd.TRIPLETS


@dataclass
class Pos0Row:
    msg: int
    label: str
    pos0_ct: int
    assumed_p0: int
    implied_base: int


@dataclass
class Pos0Report:
    model: str
    model_score: float
    rows: List[Pos0Row] = field(default_factory=list)
    bases: Dict[int, int] = field(default_factory=dict)
    triplet_notes: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def _build_inv(C: Sequence[int]) -> List[int]:
    inv = [0] * len(C)
    for i, v in enumerate(C):
        inv[int(v)] = i
    return inv


def _pos0_plaintext(msg: int, model: str, step: int, offset: int, N: int) -> int:
    if model == "ordinal":
        return (msg * step + offset) % N
    if model == "constant":
        return offset % N
    raise ValueError(f"unknown pos0 model {model!r}")


def infer_bases(
    messages: Sequence[Sequence[int]],
    inv_C: Sequence[int],
    N: int,
    *,
    model: str = "ordinal",
    step: int = 1,
    offset: int = 0,
    labels: Optional[Sequence[str]] = None,
) -> Pos0Report:
    """Infer bases from pos-0 ciphertext + assumed pos-0 plaintext model."""
    labels = labels or [str(i) for i in range(len(messages))]
    rows: List[Pos0Row] = []
    bases: Dict[int, int] = {}
    for m, msg in enumerate(messages):
        if not msg:
            continue
        ct = int(msg[0])
        p0 = _pos0_plaintext(m, model, step, offset, N)
        base = (inv_C[ct] - p0) % N
        rows.append(Pos0Row(m, labels[m], ct, p0, base))
        bases[m] = base
    return Pos0Report(model=f"{model}(step={step},off={offset})", model_score=0.0,
                      rows=rows, bases=bases)


def _cluster_base_variance(bases: Dict[int, int], triplet: Tuple[int, ...]) -> float:
    vals = [bases[m] for m in triplet if m in bases]
    if len(vals) < 2:
        return 0.0
    mean = sum(vals) / len(vals)
    return sum((v - mean) ** 2 for v in vals) / len(vals)


def _near_dup_base_penalty(
    messages: Sequence[Sequence[int]],
    bases: Dict[int, int],
    triplet: Tuple[int, ...],
    N: int,
) -> float:
    td = pd.analyze_triplet(messages, triplet, N)
    if not td.pair:
        return 0.0
    i, j = td.pair
    if bases.get(i) == bases.get(j):
        return 0.0
    return 5.0


def scan_models(
    messages: Sequence[Sequence[int]],
    inv_C: Sequence[int],
    N: int,
    *,
    labels: Optional[Sequence[str]] = None,
    step_range: range = range(1, 12),
    offset_range: range = range(0, 83, 7),
) -> Pos0Report:
    """Scan small ordinal pos-0 models; pick lowest triplet variance + near-dup penalty."""
    labels = labels or [str(i) for i in range(len(messages))]
    best: Optional[Pos0Report] = None
    best_score = 1e18

    for step in step_range:
        for offset in offset_range:
            rep = infer_bases(messages, inv_C, N, model="ordinal",
                              step=step, offset=offset, labels=labels)
            score = 0.0
            for g in TRIPLETS:
                if max(g) >= len(messages):
                    continue
                score += _cluster_base_variance(rep.bases, g)
                score += _near_dup_base_penalty(messages, rep.bases, g, N)
            rep.model_score = score
            if score < best_score:
                best_score = score
                best = rep

    assert best is not None
    best.notes.append("lower model_score = tighter pos-0 base clustering")
    for gi, g in enumerate(TRIPLETS):
        if max(g) >= len(messages):
            continue
        td = pd.analyze_triplet(messages, g, N)
        if td.pair:
            i, j = td.pair
            bi, bj = best.bases.get(i), best.bases.get(j)
            best.triplet_notes.append(
                f"triplet {gi+1} near-dup {labels[i]}/{labels[j]}: "
                f"bases {bi}/{bj} {'equal' if bi == bj else 'split'}"
            )
    return best


def analyze(
    messages: Sequence[Sequence[int]],
    N: int,
    *,
    labels: Optional[Sequence[str]] = None,
    C: Optional[Sequence[int]] = None,
) -> Pos0Report:
    """Analyze pos-0 indicators.  When ``C`` is unknown, build inv from identity trial."""
    if not messages:
        return Pos0Report(model="empty", model_score=0.0, notes=["no messages"])
    if C is None:
        # Without external alphabet, use identity trial map ct -> ct for relative ranking.
        inv = list(range(N))
    else:
        inv = _build_inv(C)
    return scan_models(messages, inv, N, labels=labels)


def score_bases(
    messages: Sequence[Sequence[int]],
    bases: Dict[int, int],
    inv_C: Sequence[int],
    N: int,
    *,
    model: str = "ordinal",
    step: int = 1,
    offset: int = 0,
) -> float:
    """Score a candidate base assignment against pos-0 ordinal model."""
    err = 0.0
    for m, msg in enumerate(messages):
        if m not in bases or not msg:
            continue
        p0 = _pos0_plaintext(m, model, step, offset, N)
        expect_ct = None
        # find ct such that inv_C[ct] == (p0 + bases[m]) % N
        target = (p0 + bases[m]) % N
        for ct in range(N):
            if inv_C[ct] == target:
                expect_ct = ct
                break
        if expect_ct is None:
            err += 10.0
        elif int(msg[0]) != expect_ct:
            err += 1.0
    return -err


def format_report(rep: Pos0Report) -> str:
    lines = [
        "=" * 72,
        "POS-0 BASE — position-0 indicator → base_m",
        "=" * 72,
        f"model: {rep.model}   score: {rep.model_score:.3f}",
        "",
        f"{'msg':>4}  {'label':>6}  {'pos0':>4}  {'p0':>4}  {'base':>4}",
        "-" * 72,
    ]
    for r in rep.rows:
        lines.append(f"{r.msg:4d}  {r.label:>6}  {r.pos0_ct:4d}  {r.assumed_p0:4d}  {r.implied_base:4d}")
    if rep.triplet_notes:
        lines.append("")
        for n in rep.triplet_notes:
            lines.append(f"  • {n}")
    for n in rep.notes:
        lines.append(f"  • {n}")
    lines.append("")
    lines.append("READ: pos-0 bases are model-dependent — validate with triplet near-dup pairs.")
    return "\n".join(lines)


def selftest() -> List[Tuple[str, bool]]:
    import numpy as np

    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(11)
    M = 9
    T = 80
    step, off = 7, 3
    base_true = 17
    C = list(rng.permutation(N))
    inv = _build_inv(C)
    msgs = []
    for m in range(M):
        p0 = (m * step + off) % N
        p = [int(rng.integers(0, N)) for _ in range(T)]
        p[0] = p0
        msgs.append([C[(p[t] + base_true + t) % N] for t in range(T)])

    rep = scan_models(msgs, inv, N, step_range=range(5, 10), offset_range=range(0, 10))
    out.append(("scan finds low-variance model", rep.model_score < 20))
    out.append(("recovers planted step in model", "step=7" in rep.model))
    out.append(("implied bases constant",
                len(set(rep.bases.values())) == 1))

    # empty edge
    empty = analyze([], N)
    out.append(("empty messages safe", empty.model == "empty"))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} pos0_base checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
