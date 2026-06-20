#!/usr/bin/env python3
"""EyeWitness — Isomorph Viewer patterns → anchor candidacy (steps 1–2).

Replicates https://tomster12.github.io/isomorph-viewer/ discovery on the Eyes
corpus, classifies each pattern via chain_extract consensus GF, and ranks anchor
candidates for alphabet-ordering work.

Run:
    python3 viewer_anchor.py
    python3 viewer_anchor.py --audit
    python3 viewer_anchor.py --html
    python3 viewer_anchor.py --top 15
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
import viewer_anchor as va    # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--max-length", type=int, default=30)
    ap.add_argument("--min-values", type=int, default=2)
    ap.add_argument("--shared-sections", action="store_true")
    ap.add_argument("--remove-overlaps", action="store_true")
    ap.add_argument("--top", type=int, default=0, help="show only top N (0=all)")
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--html", action="store_true",
                    help="write report/viewer_anchor_report.md")
    args = ap.parse_args()

    c = corpus_mod.load()
    M = [list(x) for x in c.ciphertexts]
    N = c.N

    if args.audit:
        print("=" * 70)
        print("VIEWER ANCHOR — paranoia audit (real corpus)")
        print("=" * 70)
        checks = va.run_paranoia_audit(M, c.labels, N)
        n_ok = sum(1 for _, ok in checks if ok)
        for label, ok in checks:
            print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
        print("-" * 70)
        print(f"  {n_ok}/{len(checks)} audit checks passed")
        return 0 if n_ok == len(checks) else 1

    patterns = va.discover_viewer_patterns(
        M, max_length=args.max_length, min_values=args.min_values,
        allow_shared_sections=args.shared_sections,
        remove_overlaps=args.remove_overlaps, alphabet_size=N)
    ranked = va.rank_viewer_patterns(M, patterns, N=N)

    print("=" * 70)
    print("VIEWER ANCHOR — pattern discovery + chain_extract classification")
    print("=" * 70)
    print(f"Discovered {len(patterns)} viewer pattern(s); ranked by anchor candidacy\n")
    print(f"{'tier':12s} {'pattern':26s} {'L':>3} {'inst':>4} {'clean':>7} "
          f"{'score':>6} {'ref':>3}  instances")
    print("-" * 70)

    show = ranked if args.top <= 0 else ranked[:args.top]
    for p in show:
        clean = f"{p.clean_pairs}/{p.total_pairs}"
        locs = ", ".join(f"{c.labels[m]}@{pos}" for m, pos in p.instances[:3])
        if len(p.instances) > 3:
            locs += f", +{len(p.instances) - 3}"
        nest = f"  nested→{p.nested_in[:12]}" if p.nested_in else ""
        print(f"{p.tier:12s} {p.pattern:26s} {p.length:3d} {p.n_instances:4d} "
              f"{clean:>7} {p.score:6.1f} {p.refrain_overlap:3d}  {locs}{nest}")

    tiers = {}
    for p in ranked:
        tiers[p.tier] = tiers.get(p.tier, 0) + 1
    print("\nTier summary:", ", ".join(f"{k}={v}" for k, v in sorted(tiers.items())))

    if args.html:
        REPORT.mkdir(parents=True, exist_ok=True)
        path = REPORT / "viewer_anchor_report.md"
        path.write_text(va.render_report(ranked, c.labels), encoding="utf-8")
        print(f"\nWrote {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
