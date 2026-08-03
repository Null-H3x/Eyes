#!/usr/bin/env python3
"""
eyeresolve -- which anchor pairs resolve the 17-way drift-ratio ambiguity?

(Named to avoid collision with the archive's FR16-era `eyeanchor.py`, which
addresses a different question.)

FR105 left the ambiguity at seventeen candidate readings, arithmetically
irreducible, and nominated "identify which anchors are cross-group" as the next
item. CHALLENGE I retires that framing. Pool-pair provenance is what makes a
component's Delta table ratio-dependent, but on the acquisition side the
question is different and simpler.

WHAT AN ANCHOR RESOLVES. In the scale gauge d2 = 1 the unknowns are d1 (17
candidates) and one free base per component.

  * Two anchors in DIFFERENT components each pin their own component's base and
    produce no cross-constraint -- the inter-component offset is free (FR27
    packing). They discriminate NOTHING about the ratio.
  * Two anchors in the SAME component pin the base and then supply a known
    pair-difference q[a] - q[b], which the model predicts as a function of d1.
    Different d1 gives a different prediction. Discrimination comes from
    WITHIN-component pairs and only from them.

THE SHARP QUESTION. FR54's programme already opens with two anchors in
component 1. If that pair's predicted difference is distinct across all
seventeen ratios, the ambiguity resolves AT NO EXTRA COST, and FR103's "one
more anchor" and FR104's "17-way enumeration" are both over-charges.

MEASURE. For every within-component pair (a, b) the model predicts
q[a] - q[b] = Delta_a - Delta_b at each surviving ratio. Count distinct
predictions: 17 => the pair fully resolves; k => narrows 17 to about 17/k;
1 => blind to the ratio.

PRE-REGISTERED (frozen before measurement):
  R1  the canonical single-drift build must reproduce 384/0/56 or the run VOIDS.
  R2  "resolving pair" means 17 distinct predictions over the SURVIVING ratios
      only, not over all 82.
  R3  the headline -- whether FR54's opening move resolves the ratio for free --
      is reported from component 1's pair statistics as measured, in whichever
      direction they fall.

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


def delta_tables(env, ratios):
    """ratio -> {glyph: Delta}; also returns the (ratio-invariant) partition."""
    cts, labels, Lx, ctx, pool, red, gmap = env
    out = {}; parts = set()
    for d1 in ratios:
        gf = ER.build_two(cts, ctx, Lx, red, d1, 1, gmap)
        if gf is None:
            raise RuntimeError(f"{XD} ratio {d1} contradictory; not a survivor")
        a = AUD.analyse(gf)
        if a["eq"]:
            raise RuntimeError(f"{XD} ratio {d1} not injectivity-clean")
        out[d1] = a["delta"]
        parts.add(tuple(tuple(sorted(c)) for c in a["comps"]))
    if len(parts) != 1:
        raise RuntimeError(f"{XD} component partition not ratio-invariant")
    return out, [list(c) for c in parts.pop()]


def pair_power(tables, comp, ratios):
    res = {}
    for a, b in combinations(sorted(comp), 2):
        preds = {(tables[r][a] - tables[r][b]) % N for r in ratios}
        res[(a, b)] = len(preds)
    return res


def selftest():
    ok = []
    def ck(n, c, d=""):
        ok.append((n, bool(c))); print(f"  {n:32s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise RuntimeError(f"{XD} selftest FAILED: {n} {d}")

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        env = ER.selftest()
    ck("t1_env_gate", "6/6 green" in buf.getvalue(), "eyeratio gate green")

    cts, labels, Lx, ctx, pool, red, gmap = env
    gf = ER.build_two(cts, ctx, Lx, red, 1, 1, gmap)
    rel, viol, glyphs, comps = ER.measure(gf)
    ck("t2_R1_canonical", (rel, viol, glyphs) == (384, 0, 56),
       f"{rel}/{viol}/{glyphs}")

    bad = next(r for r in range(2, N) if r not in SURVIVORS)
    gf2 = ER.build_two(cts, ctx, Lx, red, bad, 1, gmap)
    ck("t3_nonsurvivor_dirty", gf2 is None or ER.measure(gf2)[1] > 0,
       f"ratio {bad} correctly rejected")

    fake = {1: {10: 0, 20: 5}, 2: {10: 0, 20: 5}, 3: {10: 0, 20: 9}}
    ck("t4_pair_power", pair_power(fake, [10, 20], [1, 2, 3])[(10, 20)] == 2, "")
    fake2 = {r: {10: 0, 20: 7} for r in (1, 2, 3)}
    ck("t5_blind_pair",
       pair_power(fake2, [10, 20], [1, 2, 3])[(10, 20)] == 1, "")
    print(f"selftest {sum(1 for _,p in ok if p)}/{len(ok)} green")
    return env


def corpus_run(env):
    print("=" * 74)
    print("EYERESOLVE -- which anchor pairs resolve the 17-way ambiguity?")
    print("=" * 74)
    tables, comps = delta_tables(env, SURVIVORS)
    comps = sorted(comps, key=len, reverse=True)
    print(f"\n  surviving ratios : {len(SURVIVORS)}")
    print(f"  component sizes  : {[len(c) for c in comps]} (ratio-invariant)\n")

    total_full = 0; total_pairs = 0
    for ci, comp in enumerate(comps, 1):
        if len(comp) < 2: continue
        pp = pair_power(tables, comp, SURVIVORS)
        vals = sorted(pp.values(), reverse=True)
        full = sum(1 for v in pp.values() if v == len(SURVIVORS))
        blind = sum(1 for v in pp.values() if v == 1)
        total_full += full; total_pairs += len(pp)
        print(f"  component {ci} ({len(comp):2d} glyphs, {len(pp):3d} pairs): "
              f"fully-resolving {full:3d} ({100*full/len(pp):3.0f}%)  "
              f"blind {blind}  max {vals[0]}  min {vals[-1]}")

    print(f"\n  ACROSS ALL COMPONENTS: {total_full} of {total_pairs} within-component "
          f"pairs fully resolve ({100*total_full/total_pairs:.0f}%)")

    c1 = comps[0]
    pp1 = pair_power(tables, c1, SURVIVORS)
    full1 = sum(1 for v in pp1.values() if v == len(SURVIVORS))
    worst = min(pp1.values())
    print(f"\n[R3] FR54's opening move is TWO anchors in component 1.")
    print(f"     component 1: {len(pp1)} pairs, {full1} fully resolving, "
          f"weakest pair gives {worst} distinct.")
    if full1 == len(pp1):
        print("     EVERY pair resolves -> the ratio comes FREE with FR54's first")
        print("     move; the 17-way ambiguity costs nothing.")
    elif full1 > 0:
        print(f"     random pair resolves with probability {full1/len(pp1):.2f};")
        print(f"     worst case still narrows 17 -> ~{len(SURVIVORS)/worst:.1f}.")
    else:
        print("     NO component-1 pair resolves -> genuinely needs more evidence.")

    # blind pairs anywhere are the acquisition trap worth naming
    blind_all = []
    for ci, comp in enumerate(comps, 1):
        if len(comp) < 2: continue
        for p, v in pair_power(tables, comp, SURVIVORS).items():
            if v == 1: blind_all.append((ci, p))
    print(f"\n  blind pairs across all components: {len(blind_all)}"
          f"{'  -> ' + str(blind_all[:8]) if blind_all else '  (none)'}")
    print()


if __name__ == "__main__":
    env = selftest()
    if "--selftest" not in sys.argv: corpus_run(env)
