#!/usr/bin/env python3
"""
eyepack3 -- is the packing constraint ratio-invariant?

(Named to avoid the archive's `eyepack.py`.)

FR53 proved P1: packing is invariant under scaling, so it "carries ZERO drift
information, PERMANENTLY". That proof is about a SINGLE GLOBAL SCALE --
multiplying every component's values by an invertible d preserves pairwise
disjointness, and the map is a bijection on packings.

**A ratio between two independent scales is not a global scaling.** That is
exactly the gap FR104 exploited to make injectivity informative again after
FR53 had proved it useless. The same gap may apply to packing, and FR105
measured that the Delta values differ at every one of the 17 clean ratios --
so the packing count has every reason to move with the ratio.

WHY IT MATTERS. FR27's residual curve ("nine anchors leave 44 enumerable
completions") is computed from packing and is carried into
ACQUISITION_SPEC.md. If the curve is ratio-dependent, that figure is
conditional and the spec needs amending.

THE TEST, exact rather than sampled. For two components A and B with value
offsets S_A = {Delta_s : s in A} and S_B, the relative placement
delta = base_B - base_A is FORBIDDEN exactly when

    delta  in  { a - b : a in S_A, b in S_B }

so the count of allowed relative placements is 83 - |{a-b}|. This is exact,
cheap, and computed per component pair at every clean ratio.

  * If the counts are identical at every ratio, packing is ratio-invariant and
    FR53's P1 extends; FR27's curve is safe.
  * If they move, P1's scope is narrower than the doctrine records and every
    packing-derived figure is conditional on the ratio.

PRE-REGISTERED (frozen before measurement):
  R1  the canonical single-drift build must reproduce 384/0/56 or the run VOIDS.
  R2  the verdict is decided by whether the pairwise allowed-placement counts
      are IDENTICAL across the 17 clean ratios. A single differing pair
      suffices to show ratio-dependence.
  R3  a global-scaling control must be run: scaling BOTH drifts by the same
      factor must leave the counts unchanged, confirming P1 itself and showing
      the instrument is not merely noisy.

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""

import os, sys, io, contextlib
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

XD = "XD-MBYG04K-URS3LF"
N = 83

import eyeaudit as AUD
import eyeratio as ER

SURVIVORS = [1, 8, 9, 15, 22, 28, 35, 40, 48, 51, 53, 55, 74, 76, 77, 78, 82]


def tables(env, d1, d2):
    cts, labels, Lx, ctx, pool, red, gmap = env
    gf = ER.build_two(cts, ctx, Lx, red, d1, d2, gmap)
    if gf is None: return None, None
    a = AUD.analyse(gf)
    comps = sorted((sorted(c) for c in a["comps"]), key=len, reverse=True)
    return a["delta"], comps


def allowed_counts(delta, comps):
    """Per component pair: how many relative placements are allowed."""
    out = {}
    for i, j in combinations(range(len(comps)), 2):
        SA = {delta[s] % N for s in comps[i]}
        SB = {delta[s] % N for s in comps[j]}
        forbidden = {(a - b) % N for a in SA for b in SB}
        out[(i + 1, j + 1)] = N - len(forbidden)
    return out


def selftest():
    ok = []
    def ck(n, c, d=""):
        ok.append((n, bool(c))); print(f"  {n:34s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise RuntimeError(f"{XD} selftest FAILED: {n} {d}")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): env = ER.selftest()
    ck("t1_env", "6/6 green" in buf.getvalue(), "eyeratio gate green")

    cts, labels, Lx, ctx, pool, red, gmap = env
    rel, viol, glyphs, comps = ER.measure(ER.build_two(cts, ctx, Lx, red, 1, 1, gmap))
    ck("t2_R1_canonical", (rel, viol, glyphs) == (384, 0, 56), f"{rel}/{viol}/{glyphs}")

    # t3: the allowed-count formula on a hand case
    d = {0: 0, 1: 5, 2: 9, 3: 40}
    cs = [[0, 1], [2, 3]]
    got = allowed_counts(d, cs)[(1, 2)]
    forb = len({(a - b) % N for a in (0, 5) for b in (9, 40)})
    ck("t3_formula", got == N - forb, f"{got} == {N-forb}")

    # t4 / R3: GLOBAL scaling must leave counts unchanged (P1 itself)
    dA, cA = tables(env, 1, 1)
    dB, cB = tables(env, 7, 7)          # both drifts scaled by 7
    ck("t4_R3_global_scale", allowed_counts(dA, cA) == allowed_counts(dB, cB),
       "scaling both drifts leaves packing unchanged -> P1 confirmed")
    print(f"selftest {sum(1 for _,p in ok if p)}/{len(ok)} green")
    return env


def corpus_run(env):
    print("=" * 74)
    print("EYEPACK3 -- is packing ratio-invariant, or only scale-invariant?")
    print("=" * 74)
    counts = {}
    for r in SURVIVORS:
        d, c = tables(env, r, 1)
        if d is None: continue
        counts[r] = allowed_counts(d, c)

    ref = counts[SURVIVORS[0]]
    pairs = sorted(ref)
    print(f"\n  allowed relative placements per component pair, by ratio")
    print(f"  (showing the four largest components)\n")
    show = [p for p in pairs if p[0] <= 4 and p[1] <= 4]
    hdr = "  ratio | " + " | ".join(f"C{a}-C{b}" for a, b in show)
    print(hdr); print("  " + "-" * (len(hdr) - 2))
    for r in SURVIVORS:
        row = " | ".join(f"{counts[r][p]:5d}" for p in show)
        print(f"  {r:5d} | {row}")

    # [R2] verdict
    distinct = {tuple(counts[r][p] for p in pairs) for r in SURVIVORS}
    print(f"\n[R2] distinct allowed-count profiles across the 17 ratios: {len(distinct)}")
    if len(distinct) == 1:
        print("     PACKING IS RATIO-INVARIANT. FR53's P1 extends to the")
        print("     two-drift model; FR27's residual curve is safe.")
    else:
        print("     *** PACKING IS RATIO-DEPENDENT ***")
        print("     FR53's P1 covers global scaling only. Every packing-derived")
        print("     figure -- including FR27's residual curve and the '44")
        print("     completions at nine anchors' in ACQUISITION_SPEC.md -- is")
        print("     conditional on the drift ratio.")
        # quantify the spread
        for p in show:
            vals = sorted({counts[r][p] for r in SURVIVORS})
            if len(vals) > 1:
                print(f"       pair C{p[0]}-C{p[1]}: allowed placements range "
                      f"{min(vals)}..{max(vals)} over {len(vals)} distinct values")
    # joint pruning estimate at each ratio, exactly as FR27 framed it
    print("\n  joint pruning (product of pairwise allowed fractions, log10):")
    import math
    for r in SURVIVORS[:6]:
        lg = sum(math.log10(max(counts[r][p], 1) / N) for p in pairs)
        print(f"    ratio {r:2d}: log10(surviving fraction) = {lg:.2f}")
    print()


if __name__ == "__main__":
    env = selftest()
    if "--selftest" not in sys.argv: corpus_run(env)
