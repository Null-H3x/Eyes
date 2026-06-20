#!/usr/bin/env python3
"""EyeWitness — passage template pipeline (stages 3–6).

Discovers repeat-anchor targets, extends length until template contradicts,
extracts forced-SAME letter classes, and optionally runs sharp crib validation.

Run:
    python3 passage_template.py
    python3 passage_template.py --audit
    python3 passage_template.py --phrase godseektruth --alphabet abc...
    python3 passage_template.py --top 5 --html
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CORE = ROOT / "noita_eye_core"
REPORT = ROOT / "report"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import passage_template as pt   # noqa: E402
import template as tp           # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--top", type=int, default=0,
                    help="analyse only top N discovered targets (0=all)")
    ap.add_argument("--max-extra", type=int, default=15,
                    help="max glyphs to extend beyond base L")
    ap.add_argument("--min-passage", type=int, default=12)
    ap.add_argument("--no-refrain", action="store_true")
    ap.add_argument("--phrase", action="append", default=[],
                    help="stage-6 crib phrase(s) to validate")
    ap.add_argument("--alphabet", default="abcdefghijklmnopqrstuvwxyz",
                    help="plaintext ordering for VALUE-mode crib test")
    ap.add_argument("--audit", action="store_true",
                    help="run paranoia invariant audit only")
    ap.add_argument("--html", action="store_true",
                    help="write report/passage_template_report.md")
    ap.add_argument("--null", type=int, default=200)
    args = ap.parse_args()

    c = corpus_mod.load()
    M = [list(x) for x in c.ciphertexts]
    N = c.N

    if args.audit:
        print("=" * 70)
        print("PASSAGE TEMPLATE — paranoia audit (real corpus)")
        print("=" * 70)
        checks = pt.run_paranoia_audit(M, c.labels, N)
        n_ok = sum(1 for _, ok in checks if ok)
        for label, ok in checks:
            print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
        print("-" * 70)
        print(f"  {n_ok}/{len(checks)} audit checks passed")
        return 0 if n_ok == len(checks) else 1

    targets = pt.discover_targets(
        M, labels=c.labels, min_passage_len=args.min_passage,
        include_refrain=not args.no_refrain, N=N)
    if args.top:
        targets = targets[:args.top]

    print("=" * 70)
    print("PASSAGE TEMPLATE — discover · extend · template · validate")
    print("=" * 70)
    print(f"Discovered {len(targets)} target(s)\n")

    analyses = pt.analyze_all(M, targets, N, max_extra=args.max_extra)
    validations = None
    if args.phrase:
        validations = pt.validate_phrases(
            analyses, args.phrase, M, N, args.alphabet, n_null=args.null)

    for a in analyses:
        t = a.target
        locs = ", ".join(f"{c.labels[m]}@{p}" for m, p in t.instances[:5])
        if len(t.instances) > 5:
            locs += f", +{len(t.instances) - 5}"
        print(f"## {t.name} [{t.source}]")
        print(f"   instances ({len(t.instances)}): {locs}")
        print(f"   L: {t.base_length} -> max {a.max_L}", end="")
        if a.redundant_with:
            print(f"  (redundant with: {', '.join(a.redundant_with)})", end="")
        print()
        if a.max_template:
            tmpl = a.max_template
            print(f"   dof={tmpl.dof}  same_groups={tmpl.same_groups}")
            print(f"   free={tmpl.free_positions}")
            print(f"   skeleton: {tp.skeleton_string(tmpl)}")
            print(f"   collisions: {pt.format_collision_line(a.collisions)}")
        else:
            print("   INCONSISTENT at base length")
        print()

    if validations:
        print("-" * 70)
        print("Stage 6 — crib validation (VALUE mode, hypothesis alphabet)")
        print(f"{'target':20s} {'phrase':22s} {'VALUE':>5} {'+corp':>5}  verdict")
        for v in validations:
            val = "yes" if v.value_consistent else "no"
            ext = ("yes" if v.extends_corpus else "no") if v.value_consistent else "-"
            print(f"{v.target_name:20s} {v.phrase[:22]:22s} {val:>5} {ext:>5}  {v.verdict}")

    if args.html:
        REPORT.mkdir(parents=True, exist_ok=True)
        path = REPORT / "passage_template_report.md"
        path.write_text(pt.render_report(analyses, validations, c.labels),
                         encoding="utf-8")
        print(f"\nWrote {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
