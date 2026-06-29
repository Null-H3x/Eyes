#!/usr/bin/env python3
"""EyeCrack — clustered progressive-base search."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod  # noqa: E402
import base_search as bs      # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=("auto", "pure", "clustered"), default="auto")
    ap.add_argument("--crib", default=None, help="optional refrain phrase for scoring")
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--max", type=int, default=500_000, dest="max_assignments")
    args = ap.parse_args()

    c = corpus_mod.load()
    mode, results = bs.run_search(
        [list(x) for x in c.ciphertexts],
        c.N,
        mode=args.mode,
        phrase=args.crib,
        offset=args.offset,
        top=args.top,
        max_assignments=args.max_assignments,
    )
    print(bs.format_report(mode, results, top=args.top))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
