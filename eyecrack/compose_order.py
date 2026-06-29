#!/usr/bin/env python3
"""EyeCrack — compose → order_solve ranked shortlist."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import compose_order as co    # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--anchor", action="append", default=[])
    ap.add_argument("--seed", action="append", default=[], dest="seeds")
    ap.add_argument("--compose-top", type=int, default=20)
    ap.add_argument("--top", type=int, default=20)
    args = ap.parse_args()

    c = corpus_mod.load()
    hits, meta = co.run_compose_order(
        [list(x) for x in c.ciphertexts], c.N,
        labels=c.labels,
        anchors=args.anchor,
        seed_phrases=args.seeds,
        compose_top=args.compose_top,
        top=args.top,
    )
    print(co.format_report(hits, meta, labels=c.labels))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
