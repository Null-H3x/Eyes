#!/usr/bin/env python3
"""EyeCrack cipher-fingerprint — does a keyless transform-stack reveal structure?

Tests the "combination of cipher types, with or without a cut" hypothesis by
searching transposition/sequence stacks that maximise restored sequential
structure (substitution is order-invisible, so it is not resolvable by this
signal — that is stated, not hidden).  A *negative* result is informative: it is
evidence for a keystream cipher (crib-drag's model).

    python3 cipher_fingerprint.py                 # length-1 stacks
    python3 cipher_fingerprint.py --max-len 2     # also 2-stacks
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import cipher_fingerprint as cf   # noqa: E402
import corpus as corpus_mod       # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="keyless transform-stack fingerprint")
    ap.add_argument("--max-len", type=int, default=1, help="max stack length (1-3)")
    ap.add_argument("--body-start", type=int, default=25,
                    help="skip the shared openings")
    ap.add_argument("--top", type=int, default=12)
    args = ap.parse_args()

    c = corpus_mod.load()
    msgs = [list(ct) for ct in c.ciphertexts]
    res = cf.fingerprint(msgs, c.N, max_len=args.max_len,
                         body_start=args.body_start, n_decoy=100, seed=0,
                         top=args.top)

    print("=" * 70)
    print("EYECRACK — cipher fingerprint (keyless transform-stack hypothesis)")
    print("=" * 70)
    print("score = mean per-message order predictability (bits); higher = more "
          "sequential structure restored.\n")
    print("  stack                                        score    z   detected")
    for r in res:
        st = " -> ".join(f"{n}({p})" if n not in
                         ("identity", "reverse", "delta", "cumsum")
                         else n for (n, p) in r.stack)
        print(f"  {st:42} {r.score:6.3f}  {r.z:5.2f}   {r.detected}")

    any_det = any(r.detected for r in res)
    print()
    if any_det:
        print("=> A transform stack restores structure — INVESTIGATE (apply it, "
              "then run crib-drag on the result).")
    else:
        print("=> No keyless transform-stack restores sequential structure. That "
              "is evidence FOR a keystream cipher (crib-drag's model) and AGAINST "
              "the keyless-stack hypothesis, within the searched transposition/\n"
              "   sequence space. (Substitution is order-invisible and not "
              "resolvable by this signal.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
