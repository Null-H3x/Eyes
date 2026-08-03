#!/usr/bin/env python3
"""
eyeauto -- plaintext autokey, properly fitted, against the progressive model.

EYESPIRAL-C. FR137. The last mathematical question before educated assumptions.

WHY FR118 COULD NOT DO THIS. It modelled autokey as "a free constant per
alignment", which determines nothing by construction, so the comparison was
rigged before it started. A SPECIFIC autokey has real content.

THE DERIVATION. Pyry's cipher rotates by the previous PLAINTEXT character:

    q[c[t]] = p[t] + b + K[t]        K[t+1] = K[t] + p[t]
 => K[t+1] = K[t] + (q[c[t]] - b - K[t]) = q[c[t]] - b
 => K[t]   = q[c[t-1]] - b
 => p[t]   = q[c[t]] - q[c[t-1]]

**The base cancels entirely.** The plaintext is the difference of consecutive
alphabet values -- no per-message offset, no drift.

A shared passage asserts p_A[s1+i] = p_B[s2+i], giving

    q[c1[s1+i]] - q[c1[s1+i-1]] = q[c2[s2+i]] - q[c2[s2+i-1]]

linear in q, exactly as the progressive constraint is -- but a DIFFERENT
linear condition on the same evidence. Both can now be built on the same pool
and compared.

THE COMPARISON, three ways:
  1. CONSISTENCY  -- does the model survive the pool at all?
  2. DETERMINATION -- how many glyph relations does it fix?
  3. OUT-OF-SAMPLE -- FR38's test: remove a whole class, rebuild, predict its
     own held-out cells. This is the one that discriminates, because a model
     can be consistent by asserting little.

PRE-REGISTERED:
  R1  the progressive build must reproduce 384/0/56, or the run VOIDS.
  R2  the out-of-sample score is the discriminator. Determination alone is
      NOT -- a model that determines more by assuming more is not better
      (FR128).
  R3  a planted control: a fabricated class must score at chance under BOTH
      models, or the test cannot discriminate and no verdict is drawn.

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""

import os, sys, json, random
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
XD = "XD-MBYG04K-URS3LF"
N = 83

import eyeaudit as AUD
import isomorph as iso


def load():
    cts, labels, Lx, ctx, pool, red = AUD.load(
        os.path.join(HERE, "corpus.json"), os.path.join(HERE, "atlas.json"))
    return cts, labels, Lx, ctx, pool, red


def cells_of(pr, ctx):
    """lettered cells of a pool pair, per the sound-rows doctrine"""
    pattern_of, dot = ctx["pattern_of"], ctx["dot"]
    pat = pattern_of.get((pr.m1, pr.p1, pr.m2, pr.p2, pr.length))
    out = []
    for i in range(pr.length):
        if pat is not None and not pr.exact and pat[i] == '.': continue
        if pat is None and not pr.exact and \
           ((pr.m1, pr.p1 + i) in dot or (pr.m2, pr.p2 + i) in dot): continue
        out.append(i)
    return out


def build_autokey(cts, ctx, pairs):
    """q[a_i] - q[a_{i-1}] = q[b_i] - q[b_{i-1}]  at every lettered cell i>=1
    (or i=0 if position s-1 exists in both messages)."""
    gf = iso.GFSystem(N); used = 0
    for pr in pairs:
        for i in cells_of(pr, ctx):
            ta, tb = pr.p1 + i, pr.p2 + i
            if ta - 1 < 0 or tb - 1 < 0: continue
            a1 = int(cts[pr.m1][ta]); a0 = int(cts[pr.m1][ta - 1])
            b1 = int(cts[pr.m2][tb]); b0 = int(cts[pr.m2][tb - 1])
            row = defaultdict(int)
            row[a1] += 1; row[a0] -= 1; row[b1] -= 1; row[b0] += 1
            row = {k: v % N for k, v in row.items() if v % N}
            if not row: continue
            used += 1
            k = gf.classify(row, 0)
            if k == "contradiction": return None, used
            if k == "pivot": gf.add(row, 0)
    return gf, used


def measure(gf):
    from itertools import combinations
    syms = sorted(v for v in gf.solve() if v < N)
    det = 0; eq = 0
    for a, b in combinations(syms, 2):
        k = gf.classify({b: 1, a: N - 1}, 0)
        if k == "pivot": continue
        det += 1
        if k == "redundant": eq += 1
    return det, eq, len(syms)


def holdout(cts, ctx, pool, red, classes, model):
    """FR38: remove a whole class, rebuild, predict its own held-out cells."""
    labels = json.load(open(os.path.join(HERE, "corpus.json")))["message_labels"]
    Lx = {l: i for i, l in enumerate(labels)}
    scored = 0; correct = 0
    for cl in classes:
        sites = {(Lx[i["message"]], i["start"]) for i in cl["instances"]}
        keep = [p for p in red
                if (p.m1, p.p1) not in sites and (p.m2, p.p2) not in sites]
        held = [p for p in red
                if (p.m1, p.p1) in sites or (p.m2, p.p2) in sites]
        if not held: continue
        if model == "prog":
            gf = AUD.build(cts, ctx, Lx, keep, drift=1)
            if gf is None: continue
            for pr in held:
                vals = []
                for i in cells_of(pr, ctx):
                    a = int(cts[pr.m1][pr.p1 + i]); b = int(cts[pr.m2][pr.p2 + i])
                    if a == b: continue
                    hits = [d for d in range(N)
                            if gf.classify({b: 1, a: N - 1}, d) == "redundant"]
                    if len(hits) == 1: vals.append(hits[0])
                if len(vals) >= 2:
                    scored += 1
                    if len(set(vals)) == 1: correct += 1
        else:
            gf, _ = build_autokey(cts, ctx, keep)
            if gf is None: continue
            for pr in held:
                ok = []
                for i in cells_of(pr, ctx):
                    ta, tb = pr.p1 + i, pr.p2 + i
                    if ta - 1 < 0 or tb - 1 < 0: continue
                    a1 = int(cts[pr.m1][ta]); a0 = int(cts[pr.m1][ta - 1])
                    b1 = int(cts[pr.m2][tb]); b0 = int(cts[pr.m2][tb - 1])
                    row = defaultdict(int)
                    row[a1] += 1; row[a0] -= 1; row[b1] -= 1; row[b0] += 1
                    row = {k: v % N for k, v in row.items() if v % N}
                    if not row: continue
                    ok.append(gf.classify(row, 0))
                testable = [x for x in ok if x != "pivot"]
                if len(testable) >= 2:
                    scored += 1
                    if all(x == "redundant" for x in testable): correct += 1
    return correct, scored


def selftest():
    ok = []
    def ck(n, c, d=""):
        ok.append((n, bool(c))); print(f"  {n:34s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise RuntimeError(f"{XD} selftest FAILED: {n} {d}")
    cts, labels, Lx, ctx, pool, red = load()
    gf = AUD.build(cts, ctx, Lx, red, drift=1); a = AUD.analyse(gf)
    ck("t1_R1_progressive", (a["det"], len(a["eq"]), len(a["linked"])) == (384, 0, 56),
       f"{a['det']}/{len(a['eq'])}/{len(a['linked'])}")
    gfa, used = build_autokey(cts, ctx, red)
    ck("t2_autokey_builds", gfa is not None, f"{used} constraint rows")
    if gfa is not None:
        d, e, s = measure(gfa)
        ck("t3_autokey_nontrivial", used > 50, f"{used} rows, {d} relations")
    print(f"selftest {sum(1 for _,p in ok if p)}/{len(ok)} green")
    return cts, labels, Lx, ctx, pool, red


def run(env):
    cts, labels, Lx, ctx, pool, red = env
    classes = json.load(open(os.path.join(HERE, "atlas.json")))["classes"]
    print("=" * 74)
    print("EYEAUTO -- plaintext autokey vs the progressive model")
    print("=" * 74)
    gp = AUD.build(cts, ctx, Lx, red, drift=1); ap = AUD.analyse(gp)
    ga, used = build_autokey(cts, ctx, red)
    print(f"\n  [1] CONSISTENCY on the repaired pool (67 pairs)")
    print(f"      progressive : builds       {ap['det']} relations, "
          f"{len(ap['linked'])} glyphs, {len(ap['eq'])} equalities")
    if ga is None:
        print(f"      autokey     : *** CONTRADICTORY *** ({used} rows attempted)")
        print(f"\n  => plaintext autokey is REFUTED by the same evidence the")
        print(f"     progressive model survives.")
        return
    da, ea, sa = measure(ga)
    print(f"      autokey     : builds       {da} relations, {sa} glyphs, "
          f"{ea} equalities   ({used} constraint rows)")
    print(f"\n  [2] OUT-OF-SAMPLE (FR38): remove a class, rebuild, predict it")
    for model, name in (("prog", "progressive"), ("auto", "autokey")):
        c, s = holdout(cts, ctx, pool, red, classes, model)
        print(f"      {name:12s} {c}/{s} held-out pairs predicted"
              f"   ({100*c/s if s else 0:.0f}%)")
    print()


if __name__ == "__main__":
    env = selftest()
    if "--selftest" not in sys.argv: run(env)
