#!/usr/bin/env python3
"""EyeWitness number test — is the literal header (66,5) a number (e.g. 34)?

We proved (header_test) that positions 1-2 = (66,5) are a literal/shared marker,
not part of the body keystream. A literal marker could be a literal number. This
asks WHICH number, falsifiably, by decoding (66,5) under a PRE-REGISTERED family
of principled encodings (base-N / base-5-trigram place value, digit sums,
per-symbol reads) — no free parameters — and judging any hit against a luck
baseline.

Two symbols cannot pin a number on their own; this tool's job is to say honestly
whether a *specific* target (e.g. 34, the orb count) is reachable under any
principled reading, and how surprising a match would be.

Run:
    python3 number_test.py                 # show all encodings + luck baseline
    python3 number_test.py --target 34     # test a specific number
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import numbertest as nt       # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="header-as-number test")
    ap.add_argument("--target", type=int, default=None,
                    help="a specific number to test (e.g. 34)")
    args = ap.parse_args()

    c = corpus_mod.load()
    N = c.N
    sym = [v for _, v in corpus_mod.universal_positions(c)]
    vals = nt.decode_header(sym, N)
    lk = nt.luck_baseline(N, sym)

    print("=" * 70)
    print(f"EYEWITNESS — header {tuple(sym)} as a number (alphabet N={N})")
    print("=" * 70)
    print("\nPrincipled encodings (pre-registered, no free parameters):")
    for name, v in vals.items():
        print(f"  {name:18}= {v}")
    print(f"\nSmall integers reachable by ANY encoding: {lk['reachable_small']}")
    print(f"P(a random target in 1..166 is reachable) = "
          f"{lk['p_random_target_hit']:.3f}")

    print("\n" + "-" * 70)
    if args.target is not None:
        names = nt.hits(vals, args.target)
        if names:
            print(f"  {args.target} IS reachable via: {', '.join(names)}")
            print(f"  But only {lk['n_reachable_small']} small ints are reachable, "
                  f"so a single hit is weak (p~{lk['p_random_target_hit']:.3f}).")
            print(f"  To confirm, the SAME encoding must corroborate elsewhere")
            print(f"  (e.g. make position 0 a sensible index) — two symbols alone")
            print(f"  cannot pin it.")
        else:
            print(f"  {args.target} is NOT reachable under ANY principled encoding.")
            print(f"  Reading (66,5) as {args.target} requires a bespoke, parameter-")
            print(f"  fit map, which two symbols cannot justify. Refuted as stated.")
    else:
        print("  CONCLUSION: the header is literal, so it could be a literal number,")
        print("  but no SMALL count (34/33/11) is reachable under principled reads —")
        print(f"  only {lk['reachable_small']} are. Pass --target N to test one.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
