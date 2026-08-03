#!/usr/bin/env python3
"""
eyepair -- test an anchor PAIR against the repair space.

WHY THIS EXISTS. `eyecrib.py` is built on repair A, where glyph 36 is
UNDETERMINED, so it refuses glyph 36 as an anchor outright:

    RuntimeError: glyph 36 is undetermined; it carries no relation and
                  cannot be used as an anchor

Correct for repair A, but it means the existing verifier cannot test the
sharpest discriminator available: whether q[36] equals q[68]. Every
high-coverage repair FORCES that equality; repair A does not constrain it.

WHAT THIS DOES. Given externally-supplied values for the two glyphs:

    q[36] == q[68]  -> the non-bijective family stands; repair C and every
                       high-coverage reading remain live
    q[36] != q[68]  -> every high-coverage repair is REFUTED; repair A is
                       forced and triplet T1 becomes permanently unreadable

WHAT CANNOT BE DONE. The values cannot be brute-forced. Setting q[g] to any
of the 83 values is absorbed by that component's free base and never
contradicts (verified: 83 of 83 consistent for both glyphs). They must come
from OUTSIDE the corpus. This tool verifies; it does not search.

USAGE
  python3 eyepair.py 36=17 68=17
  python3 eyepair.py --selftest

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
XD = "XD-MBYG04K-URS3LF"; N = 83
import eyeaudit as AUD

REPAIRS = {"A": ("drop East 3@101 + East 1@68", [("East 3",101),("East 1",68)]),
           "C": ("drop East 1@68 only",         [("East 1",68)]),
           "R2":("drop East 4@51 only",         [("East 4",51)])}

def analyse(repair):
    cts, labels, Lx, ctx, pool, red = AUD.load(
        os.path.join(HERE,"corpus.json"), os.path.join(HERE,"atlas.json"))
    keys=[(Lx[m],s) for m,s in REPAIRS[repair][1]]
    pairs=[p for p in pool if not any((p.m1,p.p1)==k or (p.m2,p.p2)==k for k in keys)]
    gf=AUD.build(cts,ctx,Lx,pairs,drift=1)
    if gf is None: return None
    a=AUD.analyse(gf)
    comps=sorted((sorted(c) for c in a["comps"]),key=len,reverse=True)
    compof={}
    for i,c in enumerate(comps,1):
        for g in c: compof[g]=i
    return compof, {tuple(sorted(e)) for e in a["eq"]}, a["delta"], len(a["linked"])

def verdict(av, bv, ga=36, gb=68):
    same=(av%N)==(bv%N); out=[]
    for r in ("A","C","R2"):
        res=analyse(r)
        if res is None: out.append((r,"contradictory pool",None)); continue
        compof,eq,D,nl=res
        if tuple(sorted((ga,gb))) in eq:
            ok=same
            why=("forces q[36]=q[68]; anchors AGREE" if same
                 else "forces q[36]=q[68]; anchors DISAGREE")
        elif ga in compof and gb in compof and compof[ga]==compof[gb]:
            imp=(D[ga]-D[gb])%N; obs=(av-bv)%N; ok=(imp==obs)
            why=f"same component: implies q[36]-q[68]={imp}, observed {obs}"
        else:
            ok=True
            miss=[g for g in (ga,gb) if g not in compof]
            why=(f"glyph {miss[0]} undetermined; pair unconstrained" if miss
                 else "different components; pair unconstrained")
        out.append((r,why,ok))
    return same,out

def selftest():
    ok=[]
    def ck(n,c,d=""):
        ok.append((n,bool(c))); print(f"  {n:34s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise RuntimeError(f"{XD} selftest FAILED: {n} {d}")
    rA=analyse("A"); rC=analyse("C")
    ck("t1_repairA", rA and rA[3]==56 and 36 not in rA[0], "56 glyphs, 36 undetermined")
    ck("t2_repairC", rC and rC[3]==57 and (36,68) in rC[1], "57 glyphs, q[36]=q[68] forced")
    d=dict((r,o) for r,w,o in verdict(17,17)[1])
    ck("t3_equal_ok", d.get("C") is True, "equal -> repair C survives")
    d=dict((r,o) for r,w,o in verdict(17,40)[1])
    ck("t4_unequal_kills_C", d.get("C") is False, "unequal -> repair C refuted")
    ck("t5_unequal_spares_A", d.get("A") is True, "unequal -> repair A unaffected")
    print(f"selftest {sum(1 for _,p in ok if p)}/{len(ok)} green")

def main(argv):
    vals={}
    for a in argv:
        if a=="--selftest": selftest(); return
        if "=" not in a: raise RuntimeError(f"{XD} bad argument {a!r}; use g=value")
        g,v=a.split("=",1); vals[int(g)]=int(v)%N
    if set(vals)!={36,68}:
        raise RuntimeError(f"{XD} supply exactly q[36] and q[68]")
    same,out=verdict(vals[36],vals[68])
    print("="*66)
    print(f"  ANCHOR PAIR  q[36]={vals[36]}  q[68]={vals[68]}  "
          f"({'EQUAL' if same else 'DIFFERENT'})")
    print("="*66)
    for r,why,ok in out:
        print(f"  repair {r:2s} ({REPAIRS[r][0]:28s}) "
              f"{'SURVIVES' if ok else 'REFUTED '}  {why}")
    print()
    if same:
        print("  => the non-bijective family STANDS. Repair C and every")
        print("     high-coverage reading remain live; triplet T1 is readable.")
    else:
        print("  => every HIGH-COVERAGE repair is REFUTED. Repair A is forced,")
        print("     triplet T1 goes permanently dark, and the relative-plaintext")
        print("     reading falls from 191 positions to 108.")
    print()
    print("  NOTE: these values cannot be searched for. All 83 are internally")
    print("  consistent for each glyph. They must come from outside the corpus.")

if __name__ == "__main__":
    main(sys.argv[1:])
