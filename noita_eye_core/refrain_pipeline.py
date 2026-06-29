"""Refrain pipeline — compose / template-generate → order_solve → ranked report.

Glues existing Tier-1 components into one tractable attack chain:

  1. ``refrain_compose.compose`` (anchor beam search)
  2. ``template_phrase.generate_candidates`` (template enumeration)
  3. ``order_solve.solve`` on each survivor (ordering-free crib pin + hill-climb)

Output is a ranked shortlist with z, word-coverage, and partial decrypts — not a
final reading (glyph→char ordering still required for a full readout).
"""
from __future__ import annotations

import html as html_mod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import refrain as rf
import refrain_compose as rc
import template as tp
import template_phrase as tpg
import order_solve as os_
import ngram_solve as ng


@dataclass
class PipelineHit:
    phrase: str
    offset: int
    source: str
    z: float
    word_coverage: float
    symbols_pinned: int
    consistent: bool
    plaintext: Dict[int, str] = field(default_factory=dict)


def _solve_phrase(messages, phrase, offset, N, *, region, model, alphabet,
                    restarts, iters, n_null) -> Optional[PipelineHit]:
    if len(phrase) < 3:
        return None
    r = os_.solve(messages, phrase, offset, N, alphabet=alphabet, model=model,
                  region=region, restarts=restarts, iters=iters, n_null=n_null)
    if not r.consistent:
        return None
    return PipelineHit(
        phrase=phrase,
        offset=offset,
        source="",
        z=r.z,
        word_coverage=r.word_coverage,
        symbols_pinned=r.symbols_pinned,
        consistent=True,
        plaintext=dict(r.plaintext),
    )


def run_pipeline(
    messages: Sequence[Sequence[int]],
    N: int,
    *,
    labels: Optional[Sequence[str]] = None,
    region=None,
    anchors: Sequence[str] = (),
    seed_phrases: Sequence[str] = (),
    compose_top: int = 15,
    template_max: int = 500,
    order_restarts: int = 3,
    order_iters: int = 1500,
    n_null: int = 20,
    top: int = 20,
) -> Tuple[List[PipelineHit], dict]:
    region = region or rf.DEFAULT_INSTANCES
    alphabet = rf.DEFAULT_ALPHABET
    model = ng.TrigramModel(alphabet, ng._ENGLISH)
    tmpl = tp.extract(messages, region, rf.DEFAULT_LEN, N)

    meta = {
        "template_dof": tmpl.dof,
        "template_consistent": tmpl.consistent,
        "region_len": rf.DEFAULT_LEN,
    }
    hits: List[PipelineHit] = []
    seen = set()

    for phrase in seed_phrases:
        if len(phrase) < 3:
            continue
        for off in rf.viable_offsets(messages, phrase, region, rf.DEFAULT_LEN, N):
            key = (phrase, off)
            if key in seen:
                continue
            seen.add(key)
            h = _solve_phrase(messages, phrase, off, N, region=region,
                              model=model, alphabet=alphabet,
                              restarts=order_restarts, iters=order_iters,
                              n_null=n_null)
            if h:
                h.source = "seed"
                hits.append(h)
            break

    if tmpl.consistent:
        for c in rc.compose(tmpl, anchors=anchors, top=compose_top):
            for off in rf.viable_offsets(messages, c.text, region, rf.DEFAULT_LEN, N):
                key = (c.text, off)
                if key in seen:
                    continue
                seen.add(key)
                h = _solve_phrase(messages, c.text, off, N, region=region,
                                  model=model, alphabet=alphabet,
                                  restarts=order_restarts, iters=order_iters,
                                  n_null=n_null)
                if h:
                    h.source = "compose"
                    hits.append(h)
                break

        for cand in tpg.generate_candidates(messages, N, region=region,
                                            max_phrases=template_max):
            key = (cand.phrase, cand.offset)
            if key in seen:
                continue
            seen.add(key)
            h = _solve_phrase(messages, cand.phrase, cand.offset, N, region=region,
                              model=model, alphabet=alphabet,
                              restarts=order_restarts, iters=order_iters,
                              n_null=n_null)
            if h:
                h.source = "template"
                hits.append(h)

    hits.sort(key=lambda h: (h.z, h.word_coverage), reverse=True)
    return hits[:top], meta


def format_report(hits: Sequence[PipelineHit], meta: dict,
                  labels: Optional[Sequence[str]] = None) -> str:
    lines = [
        "=" * 72,
        "REFRAIN PIPELINE — compose → order_solve",
        "=" * 72,
        f"template dof={meta.get('template_dof')}  consistent={meta.get('template_consistent')}",
        "",
        f"{'rank':>4}  {'z':>6}  {'wcov':>6}  {'pin':>4}  {'src':>8}  phrase @off",
        "-" * 72,
    ]
    for i, h in enumerate(hits, 1):
        lines.append(
            f"{i:4d}  {h.z:6.1f}  {h.word_coverage:5.1%}  {h.symbols_pinned:4d}  "
            f"{h.source:>8}  {h.phrase[:28]!r} @{h.offset}"
        )
    if hits and labels:
        best = hits[0]
        if best.z >= 4 or best.word_coverage >= 0.1:
            lines.append("")
            lines.append(f"--- best ({best.phrase!r} @ {best.offset}) ---")
            for mi in sorted(best.plaintext):
                lab = labels[mi] if mi < len(labels) else str(mi)
                lines.append(f"  {lab}: {best.plaintext[mi][:90]}")
    lines.append("")
    lines.append("READ: high z + word-cov under order_solve = promising (crib, ordering).")
    return "\n".join(lines)


def write_html(path: str, hits: Sequence[PipelineHit], meta: dict) -> None:
    rows = []
    for i, h in enumerate(hits, 1):
        rows.append(
            f"<tr><td>{i}</td><td>{html_mod.escape(h.phrase)}</td><td>{h.offset}</td>"
            f"<td>{h.source}</td><td>{h.z:.2f}</td><td>{h.word_coverage:.1%}</td>"
            f"<td>{h.symbols_pinned}</td></tr>"
        )
    doc = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Refrain pipeline</title>
<style>body{{font-family:system-ui;background:#0d0d12;color:#c8d6e0;padding:2rem}}
table{{border-collapse:collapse;width:100%}} th,td{{border:1px solid #333;padding:.4rem}}
th{{color:#0ff0fc}}</style></head><body>
<h1>Refrain pipeline report</h1>
<p>template dof={meta.get('template_dof')} consistent={meta.get('template_consistent')}</p>
<table><thead><tr><th>#</th><th>phrase</th><th>off</th><th>src</th><th>z</th><th>wcov</th><th>pinned</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table></body></html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)


def selftest() -> List[Tuple[str, bool]]:
    import numpy as np

    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(3)
    alphabet = rf.DEFAULT_ALPHABET
    aidx = {ch: i for i, ch in enumerate(alphabet)}
    eng = [aidx[ch] for ch in ng._ENGLISH if ch in aidx]
    crib = "trueknowledgeofthegods"  # DEFAULT_LEN=22
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

    hits, meta = run_pipeline(msgs, N, region=insts, seed_phrases=[crib],
                              compose_top=5, template_max=200, top=10,
                              order_restarts=2, order_iters=800, n_null=10)
    out.append(("pipeline returns hits on plant", len(hits) >= 1))
    out.append(("plant crib in hits or high z",
                any(h.phrase == crib for h in hits) or (hits and hits[0].z >= 6)))
    out.append(("meta has template dof", "template_dof" in meta))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} refrain_pipeline checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
