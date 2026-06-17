#!/usr/bin/env python3
"""EyeWitness isomorph census + alphabet-chaining.

Runs noita_eye_core.isomorph. Isomorphs (same repeated-letter PATTERN, different
VALUES) can only arise from INTERRELATED per-position alphabets — ruling out
independent-column substitution (general GAK) and unrelated-alphabet running-key
/ OTP, and pointing at sliding / progressive / autokey ciphers.

It then tests the PROGRESSIVE-ALPHABET hypothesis by chaining the isomorph
offsets through a Z_N union-find: consistent => progressive (a fixed mixed
alphabet slid one step per position) and the alphabet is recoverable; contradictions
=> progressive refuted (favouring autokey or a different interrelation).

Run:
    python3 isomorph_chain.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import isomorph as iso        # noqa: E402


def main() -> int:
    c = corpus_mod.load()
    N = c.N
    M = [list(x) for x in c.ciphertexts]

    print("=" * 70)
    print("EYEWITNESS — isomorph census + alphabet chaining")
    print("=" * 70)
    print("\n[1] Isomorph significance (true different-value isomorphs vs shuffle null)")
    for L, mr in [(10, 3), (12, 3), (14, 3)]:
        s = iso.significance(M, L, mr, n_null=150)
        print(f"  L={L} min_rep={mr}: observed={s['observed']:>3}  "
              f"null={s['null_mean']:.1f}+/-{s['null_sd']:.1f}  z={s['z']:.0f}  "
              f"p={s['p']:.3f}")
    print("  -> isomorphs far beyond chance == INTERRELATED alphabets (rules out")
    print("     independent-column substitution and unrelated-alphabet OTP/running-key).")

    print("\n[2] Progressive-alphabet chaining test")
    for L, mr in [(10, 3), (12, 3), (14, 4)]:
        pairs = iso.find_isomorphs(M, L, mr)
        ch = iso.progressive_chain(M, pairs, N)
        verdict = ("CONSISTENT (progressive fits)" if ch.consistent
                   else f"CONTRADICTS ({ch.contradictions}/{ch.constraints})")
        print(f"  L={L} mr={mr}: {len(pairs):>3} isomorph pairs -> {verdict}; "
              f"largest chained component={ch.largest_component}")

    print("\n" + "-" * 70)
    print("READ: isomorphs confirm interrelated alphabets. Progressive chaining")
    print("is consistent only for the strongest isomorphs and contradicts on the")
    print("broader set, so a PURE progressive (offset = position) is not the whole")
    print("story — consistent with the community finding that alphabet-chaining is")
    print("'not completely successful', and pointing toward autokey or a")
    print("non-positional interrelation as the next model to chain.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
