#!/usr/bin/env python3
"""EyeCrack — per-triplet progressive-base search."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod       # noqa: E402
import triplet_base_search as tbs # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=("auto", "pure", "clustered"), default="auto")
    ap.add_argument("--crib", default=None)
    ap.add_argument("--top", type=int, default=5)
    args = ap.parse_args()

    c = corpus_mod.load()
    rep = tbs.search_all(
        [list(x) for x in c.ciphertexts], c.N,
        mode=args.mode, phrase=args.crib, top=args.top,
    )
    print(tbs.format_report(rep, labels=c.labels))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
