#!/usr/bin/env python3
"""
eyeverify -- test a candidate Noita Eye alphabet against everything the
project has established. Self-contained: no corpus, no model rebuild.

WHY THIS EXISTS. The project's three existing verifiers each answer a
different question and none answers the one an outside solver has:

    "I have a candidate alphabet C. Is it refuted?"

`eyecrib.py` is repair-A based and rejects glyph 36 outright. `eyepair.py`
tests one pair. `eyemodel.py` rebuilds the model rather than testing a guess.

WHAT THIS TESTS. Two INVARIANT CORES -- sets of glyph-difference relations
that hold no matter which reading of the corpus is correct:

  ATLAS CORE  (13 relations)
      invariant across all 64 viable repairs of the 13 community-certified
      isomorph classes. Requires NO class this project selected.

  EXTENDED CORE (19 relations)
      invariant across all 68 maximal readings of the extended model.

They are largely disjoint (1 shared relation) but fully consistent: where they
overlap they agree, and the extended skeleton satisfies all 13 atlas relations.

  *** A candidate violating EITHER core is refuted, whichever of the 68
      readings is correct. ***

THE DRIFT. Relations are stated at drift 1. Under drift d every right-hand
side scales by d (FR30), so by default every d in 1..82 is tried and the
surviving set reported. A candidate is refuted only if NO drift works.

USAGE
  python3 eyeverify.py --alphabet "0:17,1:44,2:9,..."     partial is fine
  python3 eyeverify.py --file myalphabet.txt             one "glyph:value" per line
  python3 eyeverify.py --selftest

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""
import sys, os
XD="XD-MBYG04K-URS3LF"; N=83

# (a, b, value) meaning q[a] - q[b] = value  (mod 83, at drift 1)
ATLAS_CORE=[(5,10,48),(6,41,35),(13,19,53),(13,72,35),(16,42,35),(17,48,53),
            (19,72,65),(23,49,48),(26,67,30),(27,81,53),(44,46,30),(47,68,30),
            (57,64,48)]
EXT_CORE=[(1,27,81),(2,26,1),(2,73,2),(6,57,82),(9,79,82),(13,19,53),(13,66,55),
          (17,63,2),(19,66,2),(21,40,82),(22,62,30),(22,64,0),(25,60,82),
          (26,73,1),(32,59,30),(34,45,82),(35,37,2),(36,68,0),(62,64,53)]
HOMOPHONES=[(22,64),(36,68)]

def check(alpha, core, d):
    """returns (tested, passed, failures) for this core at drift d"""
    tested=0; ok=0; fails=[]
    for a,b,v in core:
        if a not in alpha or b not in alpha: continue
        tested+=1
        want=(v*d)%N
        got=(alpha[a]-alpha[b])%N
        if got==want: ok+=1
        else: fails.append((a,b,want,got))
    return tested,ok,fails

def parse(s):
    out={}
    for tok in s.replace("\n",",").split(","):
        tok=tok.strip()
        if not tok: continue
        if ":" not in tok: raise SystemExit(f"{XD} bad token {tok!r}; use glyph:value")
        g,v=tok.split(":",1)
        g=int(g); v=int(v)%N
        if not 0<=g<N: raise SystemExit(f"{XD} glyph {g} out of range 0..82")
        out[g]=v
    return out

def report(alpha):
    print("="*66)
    print(f"  CANDIDATE ALPHABET: {len(alpha)} of 83 glyphs specified")
    print("="*66)
    inj = len(set(alpha.values()))==len(alpha)
    print(f"\n  injective on the specified glyphs: {'yes' if inj else 'NO'}")
    if not inj:
        dup={}
        for g,v in alpha.items(): dup.setdefault(v,[]).append(g)
        col=[gs for gs in dup.values() if len(gs)>1]
        print(f"     colliding glyph groups: {col}")
        print(f"     (not fatal -- the model carries homophones)")
    surv=[]
    for d in range(1,N):
        ta,oa,fa=check(alpha,ATLAS_CORE,d)
        te,oe,fe=check(alpha,EXT_CORE,d)
        if not fa and not fe: surv.append((d,ta,te))
    print(f"\n  {'core':10s} {'relations testable':>19s}")
    ta,_,_=check(alpha,ATLAS_CORE,1); te,_,_=check(alpha,EXT_CORE,1)
    print(f"  {'atlas':10s} {ta:>10d} of 13")
    print(f"  {'extended':10s} {te:>10d} of 19")
    if ta+te==0:
        print(f"\n  *** NO CORE RELATION IS TESTABLE. Supply values for more of")
        print(f"      these glyphs to get a verdict:")
        need=sorted({g for a,b,_ in ATLAS_CORE+EXT_CORE for g in (a,b)})
        print(f"      {need}")
        return
    print(f"\n  drifts surviving BOTH cores: {len(surv)} of 82")
    if surv:
        print(f"     {[d for d,_,_ in surv][:20]}{' ...' if len(surv)>20 else ''}")
        print(f"\n  *** NOT REFUTED. ***")
    else:
        print(f"\n  *** REFUTED at every drift. ***")
        d=1
        ta,oa,fa=check(alpha,ATLAS_CORE,d); te,oe,fe=check(alpha,EXT_CORE,d)
        print(f"     example failures at drift 1:")
        for a,b,want,got in (fa+fe)[:6]:
            print(f"       q[{a}]-q[{b}]: core requires {want}, candidate gives {got}")
    for a,b in HOMOPHONES:
        if a in alpha and b in alpha:
            eq = alpha[a]==alpha[b]
            print(f"\n  homophone q[{a}]=q[{b}]: candidate says "
                  f"{'EQUAL (consistent)' if eq else 'DIFFERENT -- this refutes the'}"
                  f"{'' if eq else ' entire non-bijective family'}")

def selftest():
    ok=[]
    def ck(n,c,d=""):
        ok.append(c); print(f"  {n:34s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise SystemExit(f"{XD} selftest FAILED: {n}")
    ck("t1_cores_loaded", len(ATLAS_CORE)==13 and len(EXT_CORE)==19,
       f"{len(ATLAS_CORE)}, {len(EXT_CORE)}")
    # a synthetic alphabet built to satisfy the extended core at drift 1
    alpha={}; 
    import collections
    adj=collections.defaultdict(list)
    for a,b,v in EXT_CORE: adj[a].append((b,-v)); adj[b].append((a,v))
    seen={}
    for start in list(adj):
        if start in seen: continue
        seen[start]=0; st=[start]
        while st:
            x=st.pop()
            for y,w in adj[x]:
                if y not in seen: seen[y]=(seen[x]+w)%N; st.append(y)
    t,o,f=check(seen,EXT_CORE,1)
    ck("t2_constructed_passes", not f, f"{o}/{t} extended relations")
    bad=dict(seen); k=EXT_CORE[0][0]; bad[k]=(bad[k]+1)%N
    t,o,f=check(bad,EXT_CORE,1)
    ck("t3_perturbation_caught", len(f)>0, f"{len(f)} failures detected")
    surv=[d for d in range(1,N) if not check(seen,EXT_CORE,d)[2]]
    ck("t4_drift_scaling", 1 in surv, f"drift 1 survives; {len(surv)} total")
    print(f"selftest {sum(ok)}/{len(ok)} green")

def main(argv):
    if not argv or "--selftest" in argv: selftest(); return
    if argv[0]=="--alphabet" and len(argv)>1: report(parse(argv[1]))
    elif argv[0]=="--file" and len(argv)>1:
        if not os.path.exists(argv[1]): raise SystemExit(f"{XD} no such file {argv[1]}")
        report(parse(open(argv[1]).read()))
    else:
        print(__doc__)

if __name__=="__main__": main(sys.argv[1:])
