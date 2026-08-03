#!/usr/bin/env python3
"""
eyerefork -- does FR47's closure of the repair fork survive two drifts?

(Named to avoid the archive's `eyerepair.py`, `eyerepair2.py` and `eyefork.py`.)

THE SETUP. FR25 opened the repair fork: the corpus admits a determining,
injective reading only if one well-supported isomorph instance is discarded,
and two repairs worked equally well --

    repair A : drop East 3@101 and East 1@68
    repair B : drop East 3@101 and East 4@51

FR47 closed it. With the FR32/33 passage included, repair A gave 384 relations
and ZERO injectivity violations; repair B gave 393 relations and FOUR. B was
refuted BY INJECTIVITY, and repair A has underwritten every figure since --
the components, the 74.1% exposure, the entire acquisition specification.

THE GAUGE QUESTION (FR107's error class). At what drift was that evaluated?

Under ONE drift the question is moot: FR53's P1 proves injectivity is
SCALE-INVARIANT, so any single drift settles it and the gauge is free.

Under TWO drifts injectivity is NOT ratio-invariant. That is exactly what
FR104/FR105 found -- 65 of 82 ratios fail injectivity and 17 pass. Injectivity
became a discriminator precisely where P1 had proved it useless.

    => repair B was refuted by a test now known to be ratio-dependent,
       evaluated at a single ratio. If B is injectivity-clean at ANY other
       ratio, FR47's closure is gauge-contaminated and the fork REOPENS.

WHAT IS TESTED. For each of repair A, repair B, and the both-dropped reading
AB, scan all 82 ratios (d2 = 1 by the scale gauge, which IS free here because
we compare like with like across repairs) and record relations, injectivity
violations, glyph count and component shape.

PRE-REGISTERED (frozen before the scan):
  R1  repair A at ratio 1 must reproduce 384 relations / 0 violations / 56
      glyphs, or the run is VOID.
  R2  repair B at ratio 1 must reproduce FR47's four injectivity violations,
      or the reconstruction of repair B is wrong and the run is VOID.
  R3  the fork REOPENS if and only if repair B is injectivity-clean at one or
      more ratios. The count is reported as measured, in whichever direction.
  R4  if the fork reopens, no conclusion about WHICH repair is correct is drawn
      in this cycle; reopening is the finding, adjudication is separate.

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""

import os, sys, io, json, contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

XD = "XD-MBYG04K-URS3LF"
N = 83

import eyeaudit as AUD
import eyeratio as ER
import isomorph as iso


def load_pool():
    c = json.load(open(os.path.join(HERE, "corpus.json")))
    cts = [list(x) for x in c["ciphertexts"]]
    labels = c["message_labels"]
    Lx = {l: i for i, l in enumerate(labels)}
    import eyegauge as EG
    ctx = EG.build_context(cts, labels, os.path.join(HERE, "atlas.json"))
    pool = ctx["apairs"] + ctx["strict"]
    return cts, labels, Lx, ctx, pool


def repaired(pool, Lx, drops):
    keys = [(Lx[m], p) for m, p in drops]
    return [p for p in pool
            if not any((p.m1, p.p1) == k or (p.m2, p.p2) == k for k in keys)]


REPAIRS = {
    "A":  [("East 3", 101), ("East 1", 68)],
    "B":  [("East 3", 101), ("East 4", 51)],
    "AB": [("East 3", 101), ("East 1", 68), ("East 4", 51)],
}


def build_scan(cts, ctx, Lx, red, gmap, d1, d2):
    gf = ER.build_two(cts, ctx, Lx, red, d1, d2, gmap)
    if gf is None: return None
    a = AUD.analyse(gf)
    return (a["det"], len(a["eq"]), len(a["linked"]),
            tuple(len(c) for c in a["comps"]))


def selftest():
    ok = []
    def ck(n, c, d=""):
        ok.append((n, bool(c))); print(f"  {n:34s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise RuntimeError(f"{XD} selftest FAILED: {n} {d}")

    cts, labels, Lx, ctx, pool = load_pool()
    gmap = ER.group_map(labels)
    ck("t1_pool", len(pool) == 83, f"{len(pool)} sound pairs")

    redA = repaired(pool, Lx, REPAIRS["A"])
    redB = repaired(pool, Lx, REPAIRS["B"])
    ck("t2_repairA_size", len(redA) == 67, f"{len(redA)} after repair A")
    ck("t2b_repairB_size", len(redB) > 0, f"{len(redB)} after repair B")

    # R1: repair A at ratio 1 must be the canonical model
    rA = build_scan(cts, ctx, Lx, redA, gmap, 1, 1)
    ck("t3_R1_canonical", rA is not None and rA[:3] == (384, 0, 56), str(rA))

    # R2: repair B at ratio 1 must reproduce FR47's four violations
    rB = build_scan(cts, ctx, Lx, redB, gmap, 1, 1)
    ck("t4_R2_repairB_FR47", rB is not None and rB[1] == 4,
       f"{rB} (FR47: 393 relations, 4 violations)")
    print(f"selftest {sum(1 for _,p in ok if p)}/{len(ok)} green")
    return cts, labels, Lx, ctx, pool, gmap


def corpus_run(env):
    cts, labels, Lx, ctx, pool, gmap = env
    print("=" * 74)
    print("EYEREFORK -- does FR47's closure survive the two-drift model?")
    print("=" * 74)
    results = {}
    for name, drops in REPAIRS.items():
        red = repaired(pool, Lx, drops)
        clean = []; contradictory = 0; dirty = 0; shapes = set()
        for d1 in range(1, N):
            r = build_scan(cts, ctx, Lx, red, gmap, d1, 1)
            if r is None: contradictory += 1; continue
            rel, viol, gl, shape = r
            if viol == 0:
                clean.append((d1, rel, gl, shape)); shapes.add((rel, gl, shape))
            else: dirty += 1
        results[name] = clean
        print(f"\n  repair {name} ({len(red)} pool pairs, drops {drops}):")
        print(f"      contradictory ratios      : {contradictory}")
        print(f"      injectivity-failing ratios: {dirty}")
        print(f"      CLEAN ratios              : {len(clean)}")
        if clean:
            print(f"      clean ratio list          : {[c[0] for c in clean]}")
            print(f"      (relations, glyphs, shape) among clean: {sorted(shapes)}")

    print("\n" + "=" * 74)
    nB = len(results["B"])
    print(f"[R3] repair B is injectivity-clean at {nB} ratio(s).")
    if nB == 0:
        print("     FORK STAYS CLOSED. FR47's refutation of repair B is NOT")
        print("     gauge-contaminated: B fails injectivity at every ratio, so")
        print("     evaluating it at one was sufficient after all.")
    else:
        print("     *** FORK REOPENS ***  FR47 refuted B at a single ratio using")
        print("     a test now known to be ratio-dependent. B survives elsewhere.")
        print("     [R4] no adjudication in this cycle; reopening is the finding.")
    nAB = len(results["AB"])
    print(f"\n  the both-dropped reading AB is clean at {nAB} ratio(s)"
          f" (FR47 called it a strict weakening of A).")
    print()


if __name__ == "__main__":
    env = selftest()
    if "--selftest" not in sys.argv: corpus_run(env)
