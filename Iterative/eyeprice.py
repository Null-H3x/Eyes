#!/usr/bin/env python3
"""
eyeprice -- FR54's anchor ordering, re-derived on canonical machinery under
the two-drift model.

FR54 priced acquisition under a single drift: two anchors in component 1 fix
base and drift together (25 glyphs, 31.2%), then one anchor per remaining
component, ten in total for 56 glyphs and 74.1%. FR107 changed the opening
move to THREE anchors. Three cycles have circled the re-derivation without
executing it.

CHALLENGE I -- what a mechanical "+1 to every count" would miss:

  * FR107 measured that 42 of 56 glyphs have alpha_s != 0, i.e. depend on d1.
    FOURTEEN DO NOT. A component whose glyphs are ALL d1-independent cannot
    resolve d1 no matter how many anchors it receives -- three anchors there
    pin base_C and d2 and leave d1 free. Such a component CANNOT OPEN.
    FR54 never had to ask this because under one drift every component could.
  * So the ordering question becomes "largest component that CAN open", not
    "largest component".
  * After the opening resolves both drifts, every other component costs exactly
    one anchor, so the total is 3 + (k-1) and only the CURVE depends on order.
  * FR54's per-component position counts were computed on a skeleton this
    archive could not rebuild until FR104 restored the machinery; they are
    re-measured here rather than inherited.

MEASURES, all from the canonical build:
  * per-component glyph and corpus-position counts
  * per-component d1-dependence (how many glyphs have alpha != 0)
  * OPENING ELIGIBILITY, verified by planted-truth simulation rather than by
    the alpha count alone
  * the corrected cumulative anchors -> exposure table

PRE-REGISTERED (frozen before measurement):
  R1  the canonical single-drift build must reproduce 384/0/56 or the run VOIDS.
  R2  opening eligibility is decided by SIMULATION (does some 3-anchor set in
      that component leave exactly one (d1,d2)?), not by inspecting alpha.
  R3  if the re-measured per-component position counts differ from FR54's
      published figures, the discrepancy is the finding and is reported as
      such, not reconciled.

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""

import os, sys, io, json, random, contextlib
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

XD = "XD-MBYG04K-URS3LF"
N = 83

import eyeaudit as AUD
import eyeratio as ER

SURVIVORS = [1, 8, 9, 15, 22, 28, 35, 40, 48, 51, 53, 55, 74, 76, 77, 78, 82]
VALID = [((r * l) % N, l % N) for r in SURVIVORS for l in range(1, N)]

# FR54's published per-component yields, for the R3 comparison
FR54 = {1: (25, 323, 31.2), 2: (11, 179, 17.3), 3: (7, 104, 10.0)}


def coefficients(env):
    """alpha_s, beta_s with D_s = alpha*d1 + beta*d2, plus the partition."""
    cts, labels, Lx, ctx, pool, red, gmap = env
    a11 = AUD.analyse(ER.build_two(cts, ctx, Lx, red, 1, 1, gmap))
    a21 = AUD.analyse(ER.build_two(cts, ctx, Lx, red, 2, 1, gmap))
    D1, D2 = a11["delta"], a21["delta"]
    gs = sorted(set(D1) & set(D2))
    alpha = {g: (D2[g] - D1[g]) % N for g in gs}
    beta = {g: (2 * D1[g] - D2[g]) % N for g in gs}
    # verify at an independent point (R-guard, not optional)
    a53 = AUD.analyse(ER.build_two(cts, ctx, Lx, red, 5, 3, gmap))["delta"]
    for g in gs:
        if g in a53 and (alpha[g] * 5 + beta[g] * 3) % N != a53[g] % N:
            raise RuntimeError(f"{XD} linearity check failed at glyph {g}")
    comps = sorted((sorted(c) for c in a11["comps"]), key=len, reverse=True)
    return alpha, beta, comps


def positions(cts, comp):
    return sum(1 for ct in cts for v in ct if v in set(comp))


def can_open(comp, alpha, beta, rng, trials=40):
    """R2: does SOME 3-anchor set in this component resolve (d1,d2) uniquely?"""
    if len(comp) < 3: return False, None
    def D(g, d1, d2): return (alpha[g] * d1 + beta[g] * d2) % N
    best = None
    cands = list(combinations(comp, 3))
    rng.shuffle(cands)
    for gs in cands[:200]:
        ok = True
        for _ in range(6):
            d1t, d2t = rng.choice(VALID); base = rng.randrange(N)
            A = {g: (base + D(g, d1t, d2t)) % N for g in gs}
            g0 = gs[0]
            surv = sum(1 for (d1, d2) in VALID
                       if all((A[g] - A[g0]) % N == (D(g, d1, d2) - D(g0, d1, d2)) % N
                              for g in gs[1:]))
            if surv != 1: ok = False; break
        if ok: return True, gs
    return False, None


def selftest():
    ok = []
    def ck(n, c, d=""):
        ok.append((n, bool(c))); print(f"  {n:32s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise RuntimeError(f"{XD} selftest FAILED: {n} {d}")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): env = ER.selftest()
    ck("t1_env_gate", "6/6 green" in buf.getvalue(), "eyeratio gate green")
    cts, labels, Lx, ctx, pool, red, gmap = env
    rel, viol, glyphs, comps = ER.measure(ER.build_two(cts, ctx, Lx, red, 1, 1, gmap))
    ck("t2_R1_canonical", (rel, viol, glyphs) == (384, 0, 56), f"{rel}/{viol}/{glyphs}")
    alpha, beta, cs = coefficients(env)
    ck("t3_linearity", len(alpha) == 56, f"{len(alpha)} coefficients, verified at (5,3)")
    ck("t4_partition", [len(c) for c in cs] == [25, 11, 7, 3, 2, 2, 2, 2, 2],
       str([len(c) for c in cs]))
    # t5: a synthetic all-d1-independent component must be ineligible to open
    fake = [900, 901, 902]
    fa = {g: 0 for g in fake}; fb = {g: (i + 1) * 7 for i, g in enumerate(fake)}
    okk, _ = can_open(fake, fa, fb, random.Random(1))
    ck("t5_d1blind_cannot_open", not okk, "alpha==0 component cannot resolve d1")
    print(f"selftest {sum(1 for _,p in ok if p)}/{len(ok)} green")
    return env


def corpus_run(env):
    cts = env[0]
    alpha, beta, comps = coefficients(env)
    rng = random.Random(108)
    print("=" * 74)
    print("EYEPRICE -- FR54's ordering re-derived under two drifts")
    print("=" * 74)
    rows = []
    print("\n  per component (canonical build):")
    for ci, comp in enumerate(comps, 1):
        pos = positions(cts, comp)
        dep = sum(1 for g in comp if alpha[g] % N)
        opens, wit = can_open(comp, alpha, beta, rng)
        rows.append((ci, comp, pos, dep, opens, wit))
        pub = FR54.get(ci)
        flag = ""
        if pub:
            flag = ("  [FR54 %d/%d/%.1f%% -> %s]" %
                    (pub[0], pub[1], pub[2],
                     "MATCHES" if (len(comp), pos) == (pub[0], pub[1]) else "DIFFERS"))
        print(f"    C{ci}: {len(comp):2d} glyphs, {pos:3d} positions "
              f"({100*pos/1036:4.1f}%), d1-dependent {dep:2d}/{len(comp):2d}, "
              f"can open: {opens}{flag}")
        if opens and ci <= 3:
            print(f"          witness opening triple: {wit}")

    eligible = [r for r in rows if r[4]]
    print(f"\n  components that CAN open: {[r[0] for r in eligible]}")
    print(f"  components that CANNOT  : {[r[0] for r in rows if not r[4]]}")

    # corrected cumulative table: open with the largest eligible component,
    # then take remaining components by decreasing position yield.
    opener = max(eligible, key=lambda r: r[2])
    rest = sorted([r for r in rows if r[0] != opener[0]], key=lambda r: -r[2])
    print(f"\n  opening component: C{opener[0]} "
          f"({len(opener[1])} glyphs, {opener[2]} positions) at 3 anchors")
    print("\n  CORRECTED CUMULATIVE TABLE (two drifts):")
    print("    anchors | glyphs | positions | exposure | (FR54 one-drift)")
    cum_g = len(opener[1]); cum_p = opener[2]; a = 3
    fr54_a = a - 1
    print(f"      {a:5d} | {cum_g:6d} | {cum_p:9d} | {100*cum_p/1036:7.1f}% | "
          f"{fr54_a} anchors")
    for r in rest:
        a += 1; fr54_a += 1
        cum_g += len(r[1]); cum_p += r[2]
        print(f"      {a:5d} | {cum_g:6d} | {cum_p:9d} | {100*cum_p/1036:7.1f}% | "
              f"{fr54_a} anchors")
    print(f"\n  TOTAL: {a} anchors for {cum_g} glyphs / {100*cum_p/1036:.1f}% "
          f"(FR54 published {fr54_a} anchors for the same yield)")
    print()


if __name__ == "__main__":
    env = selftest()
    if "--selftest" not in sys.argv: corpus_run(env)
