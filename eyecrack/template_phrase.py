#!/usr/bin/env python3
"""EyeCrack — template-constrained refrain phrase generator."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import template_phrase as tpg  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max", type=int, default=5000, dest="max_phrases")
    ap.add_argument("--top", type=int, default=30)
    ap.add_argument("--all", action="store_true", help="include non-viable fills")
    args = ap.parse_args()

    c = corpus_mod.load()
    cands = tpg.generate_candidates(
        [list(x) for x in c.ciphertexts],
        c.N,
        max_phrases=args.max_phrases,
        require_viable=not args.all,
    )
    print("=" * 70)
    print("TEMPLATE PHRASE GENERATOR")
    print("=" * 70)
    print(f"viable candidates: {len(cands)}")
    for i, cand in enumerate(cands[: args.top], 1):
        print(f"  {i:3d}. {cand.phrase!r} @ offset {cand.offset}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
