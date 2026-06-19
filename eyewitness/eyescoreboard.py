#!/usr/bin/env python3
"""EyeWitness — cipher candidate scoreboard (EyeScoreboard).

Ranks interrelated-alphabet cipher models on the eye corpus: plant discrimination,
clean extraction, refrain extent, and premise gates. Writes report/eyescoreboard.md
and report/eyescoreboard.json.

Run:
    python3 eyescoreboard.py
    python3 eyescoreboard.py --json-only
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CORE = ROOT / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import eyescoreboard as esb    # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--null", type=int, default=400,
                    help="random refrain-window nulls for per-msg audit")
    ap.add_argument("--json-only", action="store_true")
    args = ap.parse_args()

    c = corpus_mod.load()
    M = [list(x) for x in c.ciphertexts]
    sb = esb.build_scoreboard(M, c.N, n_null=args.null)

    md_path = ROOT / "report" / "eyescoreboard.md"
    json_path = ROOT / "report" / "eyescoreboard.json"
    md_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "premise": asdict(sb.premise),
        "methodology": asdict(sb.methodology),
        "ranked_ids": sb.ranked_ids,
        "candidates": [asdict(r) for r in sb.candidates],
        "reproduce": sb.reproduce,
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if not args.json_only:
        md_path.write_text(esb.render_markdown(sb), encoding="utf-8")
        print(f"Wrote {md_path}")

    print(f"Wrote {json_path}")
    print()
    print("=" * 70)
    print("EYESCOREBOARD — cipher candidate ranking")
    print("=" * 70)
    print(f"Premise tenable: {'YES' if sb.premise.premise_ok else 'WEAK'} "
          f"(isomorph z={sb.premise.isomorph_z:.1f})")
    print(f"Methodology audit: {'PASS' if sb.methodology.audit_pass else 'REVIEW'}")
    print(f"  real contra: per-msg {sb.methodology.per_msg_real_contra:.2%} | "
          f"pure {sb.methodology.pure_real_contra:.2%} | "
          f"free {sb.methodology.free_real_contra:.2%}")
    print()
    print(f"{'rank':>4}  {'id':22s}  {'verdict':12s}  {'score':>5}  notes")
    print("-" * 70)
    for r in sb.candidates:
        note = r.notes[0] if r.notes else ""
        print(f"{r.rank:4d}  {r.model_id:22s}  {r.verdict:12s}  {r.score:5d}  {note}")

    top_live = [r for r in sb.candidates
                if r.verdict not in ("EXCLUDED", "PERMISSIVE")][:3]
    print()
    if sb.premise.premise_ok:
        print("READ: Block-difference premise still holds (isomorphs + triplet depth).")
    else:
        print("READ: Premise gates weak — review premise_notes in report.")
    if top_live:
        print(f"Top non-permissive candidates: {', '.join(r.model_id for r in top_live)}")
    else:
        print("No candidate clears SUGGESTIVE — interrelated family fits but none unique.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
