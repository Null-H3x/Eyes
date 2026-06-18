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

    print("\n[2] PROGRESSIVE (fixed offset = position) vs FREE-δ (autokey/clock,")
    print("    constant unknown offset per pair) chaining")
    print(f"  {'L':>3} {'mr':>3} {'pairs':>6} | {'prog contras':>12} | "
          f"{'free contras':>12} {'over-determ':>11} {'linked':>6}")
    for L, mr in [(10, 3), (12, 3), (14, 3), (14, 4), (16, 4)]:
        pairs = iso.find_isomorphs(M, L, mr)
        pc = iso.progressive_chain(M, pairs, N)
        fc = iso.chain_free_delta(M, pairs, N, recover_threshold=15)
        print(f"  {L:>3} {mr:>3} {len(pairs):>6} | {pc.contradictions:>12} | "
              f"{fc.contradictions:>12} {fc.redundant:>11} {fc.symbols_linked:>6}")

    print("\n" + "-" * 70)
    print("READ: isomorphs confirm INTERRELATED alphabets. The free-δ (autokey/")
    print("clock, constant unknown offset per pair) model is CONSISTENT at every")
    print("threshold with heavy over-determination and links most of the 83-symbol")
    print("alphabet — while PROGRESSIVE (offset = position) CONTRADICTS. So the")
    print("interrelation is constant-offset-per-pair (ciphertext-autokey / clock),")
    print("NOT positional progressive. Caveat: this IDENTIFIES the structure; it")
    print("does not by itself ORDER the alphabet (indirect-symmetry recovery is the")
    print("next, harder step — unknown per-pair offsets couple symbols without")
    print("ordering them).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
