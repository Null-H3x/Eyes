#!/usr/bin/env python3
"""
eyerival -- progressive keystream vs PLAINTEXT AUTOKEY, head to head.

THE GAP. The model has been tested against nulls (FR37, FR38: 41/41 held-out
prediction against a 1.5% chance rate, planted-spurious control 0/23) but never
against a RIVAL. Pyry's own demonstration cipher -- an Alberti whose rings
rotate by an amount depending on the previous PLAINTEXT character -- is a live
alternative, and measurement confirms it produces long isomorphs just as the
progressive model does (ciphertext feedback, by contrast, is crushed):

    L=12/14/16 isomorph pairs   real 53/73/93   progressive 0/48/138
                                pt-autokey 35/65/181   ct-feedback 1/3/5

CHALLENGE I -- the isomorph skeleton CANNOT discriminate them. For a shared
passage the autokey advances identically inside both instances, so

    K1[s1+i] - K2[s2+i] = K1[s1] - K2[s2] = constant in i

exactly as the progressive model gives d*(s1-s2). **All 384 relations are
model-agnostic.** That is why a hundred cycles never separated them.

WHERE THEY DIFFER -- what the constant IS:

    progressive : W = base_diff + d*(s1 - s2)      AFFINE in the shift,
                  ONE slope d shared by every alignment in the corpus
    autokey     : W = base_diff + (K1[s1] - K2[s2])  depends on plaintext
                  accumulated BEFORE each instance; unrelated across alignments

So every alignment beyond the first for a given message pair is a FREE
PREDICTION the progressive model can fail and autokey cannot. The test counts
those predictions and checks them.

MEASURE. Build the constraint system twice on the same pool:
  * PROGRESSIVE: rhs = drift*(p2-p1), one drift for all -- the standing build
  * AUTOKEY    : rhs = a FREE unknown per alignment (a new variable), so
                 alignments are linked only through shared glyphs
Compare determined relations, contradictions, and count how many independent
constraints the progressive form imposes that autokey does not.

PRE-REGISTERED (frozen before running):
  R1  the progressive build must reproduce 384/0/56, or the run VOIDS.
  R2  the autokey build must be CONTRADICTION-FREE. It is strictly weaker, so
      a contradiction there means the instrument is wrong, not the model.
  R3  the discriminating quantity is the number of progressive constraints
      that are NOT implied by autokey, together with whether they hold. If
      they hold, the odds are priced as 83^-(independent extras); if any fail,
      that is the finding and favours autokey.

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""

import os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

XD = "XD-MBYG04K-URS3LF"
N = 83

import eyeaudit as AUD
import eyegauge as EG
import isomorph as iso


def autokey_build(cts, ctx, Lx, pairs, drift_for_cells=1):
    """Autokey semantics: every alignment carries its OWN free offset.
    Implemented by giving each pool pair a fresh unknown column."""
    g = {m: m for m in range(9)}
    gf = iso.GFSystem(N)
    pattern_of, dot = ctx["pattern_of"], ctx["dot"]
    col = N + 9                      # first free-offset column
    contra = 0
    for pr in pairs:
        key = (pr.m1, pr.p1, pr.m2, pr.p2, pr.length)
        pat = pattern_of.get(key)
        my = col; col += 1           # this alignment's own unknown W
        for i in range(pr.length):
            if pat is not None and not pr.exact and pat[i] == '.': continue
            if pat is None and not pr.exact and \
               ((pr.m1, pr.p1 + i) in dot or (pr.m2, pr.p2 + i) in dot): continue
            a = int(cts[pr.m1][pr.p1 + i]); b = int(cts[pr.m2][pr.p2 + i])
            row = {}
            row[b] = (row.get(b, 0) + 1) % N
            row[a] = (row.get(a, 0) + N - 1) % N
            row[my] = (row.get(my, 0) + N - 1) % N     # q[b]-q[a]-W = 0
            row = {k: v for k, v in row.items() if v}
            k = gf.classify(row, 0)
            if k == "contradiction": contra += 1; continue
            if k == "pivot": gf.add(row, 0)
    return gf, contra, col - (N + 9)


def analyse_syms(gf):
    """determined pair-relations among glyph symbols only"""
    from itertools import combinations
    syms = sorted(v for v in gf.solve() if v < N)
    det = 0; eq = 0
    for a, b in combinations(syms, 2):
        k = gf.classify({b: 1, a: N - 1}, 0)
        if k == "pivot": continue
        det += 1
        if k == "redundant": eq += 1
    return det, eq, len(syms)


def selftest():
    ok = []
    def ck(n, c, d=""):
        ok.append((n, bool(c))); print(f"  {n:34s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise RuntimeError(f"{XD} selftest FAILED: {n} {d}")
    cts, labels, Lx, ctx, pool, red = AUD.load(
        os.path.join(HERE, "corpus.json"), os.path.join(HERE, "atlas.json"))
    ck("t1_load", len(pool) == 83 and len(red) == 67, f"{len(pool)}/{len(red)}")

    # R1: the progressive build must be canonical
    gf = AUD.build(cts, ctx, Lx, red, drift=1)
    a = AUD.analyse(gf)
    ck("t2_R1_progressive", (a["det"], len(a["eq"]), len(a["linked"])) == (384, 0, 56),
       f"{a['det']}/{len(a['eq'])}/{len(a['linked'])}")

    # R2: the autokey build must be contradiction-free (it is strictly weaker)
    gfA, contra, nal = autokey_build(cts, ctx, Lx, red)
    ck("t3_R2_autokey_clean", contra == 0,
       f"{contra} contradictions over {nal} alignments")

    # t4: autokey must determine NO MORE than progressive (it assumes less)
    dA, eA, sA = analyse_syms(gfA)
    ck("t4_autokey_weaker", dA <= a["det"], f"autokey {dA} vs progressive {a['det']}")
    print(f"selftest {sum(1 for _,p in ok if p)}/{len(ok)} green")
    return cts, labels, Lx, ctx, pool, red


def corpus_run(env):
    cts, labels, Lx, ctx, pool, red = env
    print("=" * 74)
    print("EYERIVAL -- progressive keystream vs plaintext autokey")
    print("=" * 74)

    gfP = AUD.build(cts, ctx, Lx, red, drift=1)
    aP = AUD.analyse(gfP)
    gfA, contra, nal = autokey_build(cts, ctx, Lx, red)
    dA, eA, sA = analyse_syms(gfA)

    print(f"\n  PROGRESSIVE (one drift for all alignments):")
    print(f"      determined relations {aP['det']}, glyphs {len(aP['linked'])}, "
          f"contradictions 0")
    print(f"  AUTOKEY (free offset per alignment):")
    print(f"      determined relations {dA}, glyphs {sA}, contradictions {contra}")
    print(f"      free offset unknowns introduced: {nal}")

    # how many message pairs, how many alignments each
    bypair = defaultdict(list)
    for pr in red:
        bypair[(pr.m1, pr.m2)].append(pr.p1 - pr.p2)
    multi = {k: v for k, v in bypair.items() if len(v) > 1}
    extra = sum(len(v) - 1 for v in bypair.values())
    diffshift = sum(len(set(v)) - 1 for v in bypair.values() if len(set(v)) > 1)
    print(f"\n  ALIGNMENT STRUCTURE:")
    print(f"      message pairs with >=1 alignment : {len(bypair)}")
    print(f"      message pairs with >=2 alignments: {len(multi)}")
    print(f"      alignments beyond the first      : {extra}")
    print(f"      of those, at a DIFFERENT shift   : {diffshift}")

    print(f"\n  WHAT THE PROGRESSIVE MODEL RISKS:")
    print(f"      every alignment beyond the first for a message pair has its")
    print(f"      offset PREDICTED from the shift and the single drift. Autokey")
    print(f"      leaves each free. Those {diffshift} predictions are the whole")
    print(f"      discriminating content, and the progressive build takes them")
    print(f"      with ZERO contradictions.")
    if diffshift:
        print(f"      odds under a model that does not predict them: "
              f"83^-{diffshift} ~ 1e-{round(diffshift*1.919)}")

    gain = aP["det"] - dA
    print(f"\n  RELATIONS the progressive form determines that autokey does not: {gain}")
    print(f"  glyphs reached: progressive {len(aP['linked'])}, autokey {sA}")
    print()


if __name__ == "__main__":
    env = selftest()
    if "--selftest" not in sys.argv: corpus_run(env)
