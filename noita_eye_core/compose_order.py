"""Compose → order_solve ranked shortlist — Phase 2 crib/ordering chain.

Runs ``refrain_compose`` anchor beam search, then ``order_solve`` on each survivor.
Lighter than the full refrain pipeline (no template enumeration pass).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import refrain as rf
import refrain_compose as rc
import template as tp
import order_bench as ob


@dataclass
class ComposeOrderHit:
    phrase: str
    offset: int
    z: float
    word_coverage: float
    symbols_pinned: int
    compose_score: float
    plaintext: Dict[int, str] = field(default_factory=dict)


def run_compose_order(
    messages: Sequence[Sequence[int]],
    N: int,
    *,
    labels: Optional[Sequence[str]] = None,
    region=None,
    anchors: Sequence[str] = (),
    seed_phrases: Sequence[str] = (),
    compose_top: int = 20,
    order_restarts: int = 3,
    order_iters: int = 1500,
    n_null: int = 20,
    top: int = 20,
) -> Tuple[List[ComposeOrderHit], dict]:
    region = region or rf.DEFAULT_INSTANCES
    tmpl = tp.extract(messages, region, rf.DEFAULT_LEN, N)
    meta = {
        "template_dof": tmpl.dof,
        "template_consistent": tmpl.consistent,
        "region_len": rf.DEFAULT_LEN,
    }
    hits: List[ComposeOrderHit] = []
    if not tmpl.consistent:
        return hits, meta

    composed = list(rc.compose(tmpl, anchors=anchors, top=compose_top))
    phrases = list(seed_phrases) + [c.text for c in composed]
    compose_scores = {c.text: c.combined for c in composed}
    for s in seed_phrases:
        compose_scores.setdefault(s, 0.0)

    bench_hits = ob.run_bench(
        messages, phrases, N, region=region,
        restarts=order_restarts, iters=order_iters, n_null=n_null, top=top,
    )
    for h in bench_hits:
        hits.append(ComposeOrderHit(
            phrase=h.phrase,
            offset=h.offset,
            z=h.z,
            word_coverage=h.word_coverage,
            symbols_pinned=h.symbols_pinned,
            compose_score=compose_scores.get(h.phrase, 0.0),
            plaintext=dict(h.plaintext),
        ))
    hits.sort(key=lambda x: (x.z, x.word_coverage, x.compose_score), reverse=True)
    return hits[:top], meta


def format_report(
    hits: Sequence[ComposeOrderHit],
    meta: dict,
    labels: Optional[Sequence[str]] = None,
) -> str:
    lines = [
        "=" * 72,
        "COMPOSE → ORDER — anchored refrain shortlist",
        "=" * 72,
        f"template dof={meta.get('template_dof')}  consistent={meta.get('template_consistent')}",
        "",
        f"{'rank':>4}  {'z':>6}  {'wcov':>6}  {'cmp':>6}  phrase @off",
        "-" * 72,
    ]
    for i, h in enumerate(hits, 1):
        lines.append(
            f"{i:4d}  {h.z:6.1f}  {h.word_coverage:6.1%}  {h.compose_score:6.2f}  "
            f"{h.phrase[:28]!r} @{h.offset}"
        )
    if hits and labels:
        best = hits[0]
        if best.z >= 6 or best.word_coverage >= 0.1:
            lines.append("")
            lines.append(f"--- best ({best.phrase!r} @ {best.offset}) ---")
            for mi in sorted(best.plaintext):
                lab = labels[mi] if mi < len(labels) else str(mi)
                lines.append(f"  {lab}: {best.plaintext[mi][:90]}")
    lines.append("")
    lines.append("READ: compose survivors ranked by order_solve z + word-coverage.")
    return "\n".join(lines)


def selftest() -> List[Tuple[str, bool]]:
    import numpy as np
    import ngram_solve as ng

    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(3)
    alphabet = rf.DEFAULT_ALPHABET
    aidx = {ch: i for i, ch in enumerate(alphabet)}
    eng = [aidx[ch] for ch in ng._ENGLISH if ch in aidx]
    crib = "trueknowledgeofthegods"
    cv = [aidx[ch] for ch in crib]
    insts = [(0, 30), (0, 70), (1, 35), (1, 75)]
    C = list(rng.permutation(N))
    bases = [int(b) for b in rng.integers(0, N, size=4)]
    T = 110
    msgs = []
    pos0 = 0
    for m in range(4):
        p = [eng[(pos0 + i) % len(eng)] for i in range(T)]
        pos0 += T
        for (mm, ps) in insts:
            if mm == m:
                p[ps: ps + len(cv)] = cv
        msgs.append([C[(p[t] + bases[m] + t) % N] for t in range(T)])

    hits, meta = run_compose_order(
        msgs, N, region=insts, seed_phrases=[crib],
        anchors=[], compose_top=5, top=10,
        order_restarts=2, order_iters=800, n_null=10,
    )
    out.append(("compose_order meta present", "template_dof" in meta))
    out.append(("seed phrase in hits", any(h.phrase == crib for h in hits)))
    out.append(("seed hit high z", any(h.phrase == crib and h.z >= 6 for h in hits)))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} compose_order checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
