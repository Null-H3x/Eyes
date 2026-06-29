#!/usr/bin/env python3
"""EyeCrack — order-solve bench (batch crib → ordering recovery)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod  # noqa: E402
import order_bench as ob     # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("phrases", nargs="*")
    ap.add_argument("--wordlist")
    ap.add_argument("--top", type=int, default=20)
    args = ap.parse_args()

    phrases = list(args.phrases)
    if args.wordlist:
        phrases += [ln.strip() for ln in Path(args.wordlist).read_text().splitlines()
                    if ln.strip()]

    c = corpus_mod.load()
    hits = ob.run_bench(
        [list(x) for x in c.ciphertexts], phrases or ["trueknowledgeofthegods"],
        c.N, labels=c.labels, top=args.top,
    )
    print(ob.format_report(hits, labels=c.labels))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
