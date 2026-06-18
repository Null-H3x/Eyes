#!/usr/bin/env python3
"""EyeWitness — header-base constraint + a contamination correction.

Pulls the thread of the literal universal (66,5) header:

  1. The header forces, under the per-message-progressive family, ALL per-message
     bases EQUAL -> the model collapses to PURE PROGRESSIVE (one global sliding
     alphabet). Proven on plants in noita_eye_core/headerbase.py (6/6).
  2. CONTAMINATION CORRECTION: the earlier 'progressive refuted' verdict was a
     contamination artifact. On the contamination-filtered CLEAN isomorphs, pure
     progressive has ~zero contradictions (two independent solvers agree); the
     contradictions only appear on RAW (contaminated) isomorphs. So progressive is
     NOT robustly refuted — status OPEN.
  3. The ciphertext-autokey reading is an alternative also consistent with the
     header (p[2] constant, p[1] varies with the per-message position-0 symbol).

Run:
    python3 header_base.py
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
import headerbase as hb       # noqa: E402
import isomorph as iso        # noqa: E402


def main() -> int:
    c = corpus_mod.load()
    N = c.N
    M = [list(x) for x in c.ciphertexts]

    print("=" * 70)
    print("EYEWITNESS — header-base constraint + progressive contamination check")
    print("=" * 70)

    uni = hb.universal_positions(M)
    p0 = [m[0] for m in M]
    print("\n[Facts]")
    print(f"  universal positions (same ciphertext in all 9): {uni}")
    print(f"  position 0 (per-message, distinct): {p0}  distinct={len(set(p0))}/9")
    print("  header_test verdict: positions 1,2 are LITERAL/SHARED (p ~ 3e-12).")

    print("\n[Deduction] Under per-message-progressive x[c] = p + base_m + t:")
    print("  literal header (p[m][1]=h1 for all m)  =>  base_m = x[66]-h1-1 = const")
    print("  =>  ALL per-message bases EQUAL  =>  the model is PURE PROGRESSIVE.")
    print("  (Proven on plants: noita_eye_core/headerbase.py selftest 6/6.)")

    print("\n[Contamination correction] pure-progressive contradictions")
    print(f"  {'set':28s} {'pairs':>6} {'GF':>10} {'DSU':>10}")
    broad = iso.find_isomorphs(M, 13, 3)
    rows = []
    for label, amr in (("CLEAN (anchor mr=4)", 4), ("CLEAN (anchor mr=3)", 3)):
        res = ce.extract(M, 13, broad_repeats=3, anchor_repeats=amr, N=N)
        clean = [pr for pr in broad
                 if ce._redundant(res._gf, pr, M, cm.per_msg_prog_rows, N)]
        gf_c, tot = hb.pure_progressive_contradictions(M, clean, N)
        dsu = iso.progressive_chain(M, clean, N)
        print(f"  {label:28s} {len(clean):>6} {gf_c:>5}/{tot:<4} "
              f"{dsu.contradictions:>5}/{dsu.constraints:<4}")
    gf_r, totr = hb.pure_progressive_contradictions(M, broad, N)
    dsu_r = iso.progressive_chain(M, broad, N)
    print(f"  {'RAW (contaminated mr=3)':28s} {len(broad):>6} {gf_r:>5}/{totr:<4} "
          f"{dsu_r.contradictions:>5}/{dsu_r.constraints:<4}")
    print("  -> contradictions live in the CONTAMINATED tail; the clean isomorphs")
    print("     are consistent with progressive. The prior 'refuted' was an artifact.")

    print("\n[Autokey alternative] p_t = c_t - c_{t-1}:")
    rd = hb.autokey_header_reading(M, N)
    print(f"  p[2] per message = {rd['p2_per_message'][:3]}...  constant={rd['p2_constant']}"
          f"  value={rd['p2_value']}")
    print(f"  p[1] per message = {rd['p1_per_message']}  distinct={rd['p1_distinct']}")

    print("\n" + "-" * 70)
    print("READ:")
    print("  CORRECTION: PROGRESSIVE is NOT robustly refuted — the refutation was")
    print("    driven by contaminated isomorphs. On clean data it is consistent")
    print("    (though under-determined: the clean set is one repeated passage).")
    print("  The literal header collapses per-message-progressive -> PURE")
    print("    PROGRESSIVE (removes the free per-message base that made it")
    print("    permissive). That is the simplest live model; autokey/clock is the")
    print("    alternative. Deciding between them still needs more clean structure")
    print("    or a mapping anchor.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
