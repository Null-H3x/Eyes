#!/usr/bin/env python3
"""EyeCrack — Rosetta partial mapping propagator.

Usage:
    python3 rosetta.py --pin 42:a --pin 17:e
    python3 rosetta.py --pin 42:a --crib trueknowledgeofthegods
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod  # noqa: E402
import rosetta as rs         # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pin", action="append", default=[], metavar="VALUE:CHAR")
    ap.add_argument("--crib", default=None)
    ap.add_argument("--offset", type=int, default=0)
    args = ap.parse_args()

    c = corpus_mod.load()
    pins = rs.parse_pins(args.pin) if args.pin else {}
    rep = rs.analyze(
        [list(x) for x in c.ciphertexts],
        pins,
        c.N,
        labels=c.labels,
        crib=args.crib,
        offset=args.offset,
    )
    print(rs.format_report(rep, labels=c.labels))
    return 0 if (not args.crib or rep.crib_consistent) else 1


if __name__ == "__main__":
    raise SystemExit(main())
