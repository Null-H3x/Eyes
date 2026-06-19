#!/usr/bin/env python3
"""EyeCrack — residual ordering exhaust (Phase 2 after refrain_sweep).

When pin_structure leaves <= N free ordering slots, exhaustively permute the
residual; otherwise fall back to parallel hill-climb.

Usage:
    python3 ordering_exhaust.py --phrase "..." --offset 0
    python3 ordering_exhaust.py --phrase "..." --exhaust-if-free 12
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import ordering_exhaust as oe # noqa: E402
import refrain as rf          # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--phrase", required=True)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--exhaust-if-free", type=int, default=12)
    ap.add_argument("--max-perms", type=int, default=500_000)
    args = ap.parse_args()

    c = corpus_mod.load()
    M = [list(x) for x in c.ciphertexts]
    print("=" * 70)
    print("EYECRACK — residual ordering exhaust")
    print("=" * 70)
    r = oe.exhaust_ordering(
        M, args.phrase, args.offset, c.N,
        exhaust_if_free=args.exhaust_if_free,
        max_perms=args.max_perms,
    )
    print(f"phrase: {args.phrase[:40]}  offset: {args.offset}")
    print(f"consistent: {r.consistent}  method: {r.method}  free_slots: {r.free_slots}")
    print(f"pinned: {r.symbols_pinned}  z: {r.z:.2f}  word-cov: {r.word_coverage:.1%}")
    if r.plaintext:
        for mi, txt in r.plaintext.items():
            print(f"  {c.labels[mi]}: {txt[:80]}...")
    return 0 if r.consistent else 1


if __name__ == "__main__":
    sys.exit(main())
