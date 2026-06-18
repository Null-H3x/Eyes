#!/usr/bin/env python3
"""EyeWitness — pure-progressive alphabet recovery + decryption attempt.

The literal universal header forces PURE PROGRESSIVE (c[t]=C[(p[t]+t)]); under it
the whole corpus decrypts up to a single monoalphabetic relabel once the alphabet
x=C^{-1} is recovered, and IoC (relabel-invariant) tests whether the result is
language. This runs the attempt on the contamination-filtered CLEAN isomorphs.

Validated machinery (noita_eye_core/pureprog.py selftest 6/6): recovery matches a
planted alphabet up to one rotation; decryption with the true alphabet returns the
plaintext up to a constant; the IoC test separates language from uniform.

Run:
    python3 pure_progressive.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import chain_extract as ce    # noqa: E402
import chain_models as cm     # noqa: E402
import pureprog as pp         # noqa: E402
from isomorph import find_isomorphs  # noqa: E402


def main() -> int:
    c = corpus_mod.load()
    N = c.N
    M = [list(x) for x in c.ciphertexts]
    broad = find_isomorphs(M, 13, 3)

    print("=" * 70)
    print("EYEWITNESS — pure-progressive recovery + decryption attempt")
    print("=" * 70)
    print(f"corpus: {len(M)} messages, N={N}  (model: c[t] = C[(p[t]+t)])")

    print(f"\n  {'clean anchor':14s} {'pairs':>6} {'recovered':>9} {'distinct':>8} "
          f"{'decrypt%':>8} {'IoC':>7} {'null':>7} {'z':>6}")
    for label, amr in (("mr=4 (cleanest)", 4), ("mr=3", 3)):
        res = ce.extract(M, 13, broad_repeats=3, anchor_repeats=amr, N=N)
        clean = [pr for pr in broad
                 if ce._redundant(res._gf, pr, M, cm.per_msg_prog_rows, N)]
        r = pp.ioc_test(M, clean, N, n_null=400)
        print(f"  {label:14s} {len(clean):>6} {r['recovered']:>9} "
              f"{r['distinct_positions']:>8} {r['decrypt_frac']*100:>7.0f}% "
              f"{r['ioc']:>7.4f} {r['ioc_null_mean']:>7.4f} {r['ioc_z']:>6.2f}")
    print(f"  reference: uniform IoC = {1/N:.4f}; natural language ~ 0.06-0.07")

    print("\n" + "-" * 70)
    print("READ:")
    print("  The literal header makes PURE PROGRESSIVE the simplest live model, and")
    print("  the recovery+decrypt machinery is validated (pureprog selftest 6/6).")
    print("  BUT on this corpus recovery is UNDER-DETERMINED: the clean isomorphs are")
    print("  essentially one repeated passage, so x is pinned for too few symbols")
    print("  (distinct << 83) and the decrypted IoC sits at noise (z ~ 2, driven by")
    print("  that known repeat) — far below language. NOT a decryption.")
    print("  WALL: too few INDEPENDENT clean repeated structures to recover a usable")
    print("  alphabet. This is the re-runnable gate — more clean isomorphs (or an")
    print("  external glyph->letter anchor) would move the IoC z if the model holds.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
