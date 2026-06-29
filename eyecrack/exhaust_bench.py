#!/usr/bin/env python3
"""EyeCrack — ordering exhaust bench (Phase 2 residual search)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import exhaust_bench as eb     # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--phrase", required=True)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--exhaust-if-free", type=int, default=12)
    ap.add_argument("--max-perms", type=int, default=500_000)
    args = ap.parse_args()

    c = corpus_mod.load()
    r = eb.run_exhaust(
        [list(x) for x in c.ciphertexts], args.phrase, args.offset, c.N,
        exhaust_if_free=args.exhaust_if_free,
        max_perms=args.max_perms,
    )
    print(eb.format_report(r, crib=args.phrase, offset=args.offset, labels=c.labels))
    return 0 if r.consistent else 1


if __name__ == "__main__":
    raise SystemExit(main())
