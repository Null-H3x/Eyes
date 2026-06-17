#!/usr/bin/env python3
"""EyeWitness header test — is (66,5) keystreamed, or a literal/shared marker?

Positions 1-2 hold (66,5) identically across all nine messages. Those messages
fall in three triplets with *independent* keystreams (see keystream_scope). The
question that decides whether the header can anchor a keystream crib:

  * If positions 1-2 are under the per-triplet keystream, guessing their
    plaintext pins keystream values (useful crib).
  * If they're a literal / shared prefix outside the divergent body keystream,
    guessing them tells us nothing about the body (useless as a body crib).

This runs `noita_eye_core.header_test`, which measures cross-triplet agreement
per position. Independent keystreams give ~1/N cross-triplet agreement; a
position far above that cannot be independently keystreamed -> literal/shared.

Run:
    python3 header_test.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import header_test as ht      # noqa: E402


def main() -> int:
    c = corpus_mod.load()
    N = c.N
    messages = [list(ct) for ct in c.ciphertexts]

    print("=" * 70)
    print("EYEWITNESS — header literal-vs-keystream test")
    print("=" * 70)
    cls = ht.classify_positions(messages, N)
    prefix = ht.universal_prefix(messages)
    print(f"\nuniform baseline (independent keystream) cross-agreement = 1/N "
          f"= {1.0 / N:.4f}")
    print(f"universal positions (same symbol in ALL nine): {prefix}\n")
    print(f"  {'pos':>3}  {'cross':>6}  {'within':>6}   class")
    for pc in cls[:12]:
        print(f"  {pc.pos:>3}  {pc.cross_agree:>6.2f}  {pc.within_agree:>6.2f}"
              f"   {pc.kind}")
    if len(cls) > 12:
        print("   ...")

    literal = [pc.pos for pc in cls if pc.kind == "literal/shared"]
    p = ht.independent_keystream_pvalue(messages, N, literal) if literal else 1.0

    print("\n" + "-" * 70)
    print("CONCLUSION:")
    if literal:
        print(f"  Positions {literal} are LITERAL / SHARED: cross-triplet")
        print(f"  agreement = 1.00 across independent keystreams, which has")
        print(f"  probability ~{p:.1e} under the independent-keystream null.")
        print(f"  => (66,5) is a literal 2-symbol marker, NOT part of the body")
        print(f"     keystream. Guessing its plaintext does NOT pin the")
        print(f"     per-triplet body keystream -> the header is not a body crib.")
        print(f"  Position 0 is per-message; positions {literal[-1]+1}+ are the")
        print(f"  per-triplet keystreamed body (within > cross agreement).")
    else:
        print("  No literal/shared positions detected — every position behaves")
        print("  like an independent keystream. The header would be keystreamed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
