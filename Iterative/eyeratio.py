#!/usr/bin/env python3
"""
eyeratio -- reproduce the surviving drift ratios on CANONICAL machinery,
then characterise them.

WHY THIS EXISTS. FR103 scanned drift ratios on a pool rebuilt from
corpus.json + atlas.json and reported 77 of 82 surviving. E6 withdrew that
figure: the atlas-only pool relates 64 skeleton pairs against the model's 384
relations and never touches 5 skeleton glyphs, so it is a strict weakening and
admits too many ratios. The FR104 cycle, using the restored canonical
machinery, reported 17. This instrument reproduces that number independently
before anything is built on it, then asks whether the 17 are arithmetically
structured.

THE PARAMETERISATION. eyegauge.make_rows puts the drift in exactly one place:

    rhs = (drift * (p2 - p1)) mod 83        per pool pair

Under two drift parameters the pair's rhs uses its own group's drift. The
parameterisation is EXACT provided no pool pair straddles T1 and T2/T3 -- for
a straddling pair the rhs would acquire an i-dependence and the row form would
no longer hold. That precondition is CHECKED, not assumed (gate t3).

VERDICT RULE. A ratio survives iff the rebuilt system is non-contradictory AND
injectivity-clean, exactly as the canonical audit tests the single-drift model.

PRE-REGISTERED (frozen before scanning):
  R1  the single-drift configuration (d1 = d2 = 1) must reproduce the canonical
      384 relations / 56 glyphs / 0 violations, or the run is VOID.
  R2  ratio 1 must be among the survivors; if it is not, the instrument is
      wrong, not the model.
  R3  the survivor count is reported as measured. If it differs from 17 the
      discrepancy is the finding and is NOT reconciled by adjusting the method.

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""

import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

XD = "XD-MBYG04K-URS3LF"
N = 83

import eyegauge as EG
import isomorph as iso
import eyeaudit as AUD

GI = {"T1": 0, "T2": 1, "T3": 2}


def group_map(labels):
    """message index -> triplet group index"""
    Lx = {l: i for i, l in enumerate(labels)}
    g = {}
    for t, ms in EG.TRIPLETS.items():
        for m in ms: g[Lx[m]] = GI[t]
    return g


def two_drift_rows(ctx, d1, d2, gmap, group=None, n_msgs=9):
    """Like EG.make_rows but the rhs uses the pair's own group drift.
    d1 applies to T1-internal pairs, d2 to all others."""
    pattern_of, dot = ctx["pattern_of"], ctx["dot"]
    if group is None: group = {m: m for m in range(n_msgs)}

    def rows(pr, messages, Nn):
        key = (pr.m1, pr.p1, pr.m2, pr.p2, pr.length)
        pat = pattern_of.get(key)
        g1t, g2t = gmap[pr.m1], gmap[pr.m2]
        if g1t != g2t and (g1t == 0 or g2t == 0):
            raise RuntimeError(f"{XD} pool pair straddles T1 and T2/T3; the "
                               f"two-drift row form does not hold for it")
        d = d1 if g1t == 0 else d2
        rhs = (d * (pr.p2 - pr.p1)) % Nn
        g1, g2 = group.get(pr.m1), group.get(pr.m2)
        for i in range(pr.length):
            if pat is not None and not pr.exact and pat[i] == '.': continue
            if pat is None and not pr.exact and \
               ((pr.m1, pr.p1 + i) in dot or (pr.m2, pr.p2 + i) in dot): continue
            A = int(messages[pr.m1][pr.p1 + i]); D = int(messages[pr.m2][pr.p2 + i])
            row = {}
            row[D] = (row.get(D, 0) + 1) % Nn
            row[A] = (row.get(A, 0) + Nn - 1) % Nn
            if g1 is not None and g2 is not None and g1 != g2:
                row[Nn + g2] = (row.get(Nn + g2, 0) + Nn - 1) % Nn
                row[Nn + g1] = (row.get(Nn + g1, 0) + 1) % Nn
            row = {v: cc for v, cc in row.items() if cc}
            yield row, rhs
    return rows


def build_two(cts, ctx, Lx, red, d1, d2, gmap, group=None, cells=AUD.CELLS):
    """AUD.build with per-group drift. The FR32/33 passage sits in T3 -> d2."""
    g = group or {m: m for m in range(9)}
    E4, W4 = Lx["East 4"], Lx["West 4"]
    gf = iso.GFSystem(N)
    row = {}
    if row and gf.classify(row, 0) == "pivot": gf.add(row, 0)
    rows = two_drift_rows(ctx, d1, d2, gmap, g)
    for pr in list(red):
        for rw, rhs in rows(pr, cts, N):
            k = gf.classify(rw, rhs)
            if k == "contradiction": return None
            if k == "pivot": gf.add(rw, rhs)
    for i in cells:                       # E4 x W4 passage: both T3 -> d2
        a = int(cts[E4][28 + i]); b = int(cts[W4][29 + i])
        rw = {b: 1, a: N - 1}
        if g[E4] != g[W4]:
            rw[N + g[W4]] = N - 1; rw[N + g[E4]] = 1
        rw = {k: v % N for k, v in rw.items() if v % N}
        k = gf.classify(rw, d2 % N)
        if k == "contradiction": return None
        if k == "pivot": gf.add(rw, d2 % N)
    return gf


def measure(gf):
    a = AUD.analyse(gf)
    rel = a["det"]; viol = len(a["eq"]); glyphs = len(a["linked"])
    comps = [len(c) for c in a["comps"]]
    return rel, viol, glyphs, comps


def selftest():
    ok = []
    def ck(n, c, d=""):
        ok.append((n, bool(c))); print(f"  {n:34s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise RuntimeError(f"{XD} selftest FAILED: {n} {d}")

    cts, labels, Lx, ctx, pool, red = AUD.load(
        os.path.join(HERE, "corpus.json"), os.path.join(HERE, "atlas.json"))
    gmap = group_map(labels)
    ck("t1_pool", len(pool) == 83 and len(red) == 67,
       f"pool {len(pool)} -> repaired {len(red)}")

    # t2 / R1: single-drift configuration must reproduce the canonical model
    gf = build_two(cts, ctx, Lx, red, 1, 1, gmap)
    ck("t2_builds", gf is not None, "d1=d2=1 non-contradictory")
    rel, viol, glyphs, comps = measure(gf)
    ck("t2b_R1_canonical", (rel, viol, glyphs) == (384, 0, 56)
       and comps == [25, 11, 7, 3, 2, 2, 2, 2, 2],
       f"{rel} rel, {viol} viol, {glyphs} glyphs, {comps}")

    # t3: the parameterisation's precondition -- no pool pair straddles T1
    straddle = [p for p in red
                if (gmap[p.m1] != gmap[p.m2]) and (gmap[p.m1] == 0 or gmap[p.m2] == 0)]
    ck("t3_no_T1_straddle", not straddle,
       f"{len(straddle)} straddling pairs (must be 0)")

    # t4: the two groups are both actually populated
    t1p = sum(1 for p in red if gmap[p.m1] == 0 and gmap[p.m2] == 0)
    ck("t4_groups_populated", 0 < t1p < len(red),
       f"T1-internal {t1p} of {len(red)}")

    # t5: a deliberately wrong ratio must change something
    gf2 = build_two(cts, ctx, Lx, red, 2, 1, gmap)
    changed = gf2 is None or measure(gf2)[:3] != (384, 0, 56)
    ck("t5_ratio_matters", changed, "d1=2,d2=1 differs from canonical")
    print(f"selftest {sum(1 for _,p in ok if p)}/{len(ok)} green")
    return cts, labels, Lx, ctx, pool, red, gmap


def corpus_run(env):
    cts, labels, Lx, ctx, pool, red, gmap = env
    print("=" * 74)
    print("EYERATIO -- surviving drift ratios on canonical machinery")
    print("=" * 74)
    surv = []; contradictory = 0; noninj = 0
    detail = {}
    for d1 in range(1, N):
        gf = build_two(cts, ctx, Lx, red, d1, 1, gmap)
        if gf is None:
            contradictory += 1; continue
        rel, viol, glyphs, comps = measure(gf)
        detail[d1] = (rel, viol, glyphs, tuple(comps))
        if viol == 0: surv.append(d1)
        else: noninj += 1
    print(f"\n  contradictory                 : {contradictory}")
    print(f"  consistent but injectivity fails: {noninj}")
    print(f"  CLEAN (surviving ratios)      : {len(surv)}")
    print(f"  survivors: {surv}")
    print(f"\n  [R2] ratio 1 present: {1 in surv}")
    print(f"  [R3] FR104 reported 17; measured {len(surv)}; "
          f"{'AGREES' if len(surv)==17 else 'DISAGREES -- this is the finding'}")

    # component structure invariance
    shapes = {v[3] for v in detail.values() if v[1] == 0}
    rels = {v[0] for v in detail.values() if v[1] == 0}
    print(f"\n  component shapes among survivors: {shapes}")
    print(f"  relation counts among survivors : {rels}")
    print(f"  -> structure is {'RATIO-INVARIANT' if len(shapes)==1 and len(rels)==1 else 'NOT invariant'}")

    # ---- characterisation of the survivors
    print("\n=== characterising the survivors ===")
    S = set(surv)
    neg = {(N - r) % N for r in surv}
    invs = {pow(r, N - 2, N) for r in surv}
    print(f"  closed under negation r -> -r : {S == neg}"
          f"   (overlap {len(S & neg)}/{len(S)})")
    print(f"  closed under inversion r -> r^-1: {S == invs}"
          f"   (overlap {len(S & invs)}/{len(S)})")
    sq = {(r * r) % N for r in surv}
    print(f"  closed under squaring          : {S == sq}"
          f"   (overlap {len(S & sq)}/{len(S)})")
    # multiplicative subgroup?
    prod_closed = all(((a * b) % N) in S for a in surv for b in surv)
    print(f"  closed under multiplication    : {prod_closed}")
    # quadratic residues
    QR = {(x * x) % N for x in range(1, N)}
    nqr = sum(1 for r in surv if r in QR)
    print(f"  quadratic residues among them  : {nqr}/{len(surv)} "
          f"(chance ~{len(surv)/2:.1f})")
    # orders
    def order(a):
        o = 1; x = a % N
        while x != 1: x = x * a % N; o += 1
        return o
    from collections import Counter
    oc = Counter(order(r) for r in surv)
    print(f"  multiplicative orders          : {dict(sorted(oc.items()))}")
    gaps = sorted(surv)
    print(f"  consecutive gaps               : {[gaps[i+1]-gaps[i] for i in range(len(gaps)-1)]}")
    print()


if __name__ == "__main__":
    env = selftest()
    if "--selftest" not in sys.argv: corpus_run(env)
