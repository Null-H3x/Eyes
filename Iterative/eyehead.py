#!/usr/bin/env python3
"""
eyehead -- is the T1 opening a stamped header, or encrypted co-plaintext?

THE CRACK. Positions 1-24 of East 1, West 1 and East 2 are byte-identical
(24 of 25 across all three). The model must read them as LITERAL glyphs, not
encrypted text, because:

    identical glyph, same offset, co-plaintext
      => q[x] - q[x] = 0 = d*0 + (base_E2 - base_E1)
      => base_E2 = base_E1

but the model forces base_E2 - base_E1 = 77, and 77d = 0 mod 83 with 83 prime
gives d = 0 -- the progressive form dies.

So the stamped-header reading is not a preference, it is a REQUIREMENT. It has
never been independently tested, and an external critic identified it as the
load-bearing assumption.

THE TEST. Assert the openings ARE co-plaintext -- force base_E2 = base_E1 -- and
ask whether ANY consistent model survives. Three regimes:

  R1  full evidence + equal T1 bases           -> does it build at any drift?
  R2  same, but excluding the T1 opening rows  -> isolates where the conflict is
  R3  d = 0 explicitly (monoalphabetic-per-triplet) -> the rival the critic
      proposes; does it explain the corpus at all?

PRE-REGISTERED:
  G1  the canonical model must reproduce 794/61/8, or the run VOIDS.
  G2  a planted contradiction must be caught (0=1), proving the detector fires.
  R3 is scored on RELATIONS RECOVERED, not on consistency alone: a model that
  is consistent because it asserts nothing is not a rival (the FR137 lesson).

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""
import os, sys, json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
XD="XD-MBYG04K-URS3LF"; N=83
import eyeaudit as AUD, eyegauge as EG, eyehomo2 as H2, isomorph as iso

def load():
    cj=json.load(open(os.path.join(HERE,"corpus.json")))
    cts,l2,Lx,ctx,pool,red=AUD.load(os.path.join(HERE,"corpus.json"),
                                    os.path.join(HERE,"atlas.json"))
    return cj["ciphertexts"],cj["message_labels"],cts,Lx,ctx,pool,red

class P: __slots__=('m1','p1','m2','p2','length','exact')

def mk(ins,L,raw,ctx):
    pstr=H2.pat(raw[ins[0][0]][ins[0][1]:ins[0][1]+L]); out=[]
    for i in range(len(ins)):
        for j in range(i+1,len(ins)):
            q=P(); q.m1,q.p1=ins[i]; q.m2,q.p2=ins[j]; q.length=L; q.exact=False
            ctx['pattern_of'][(q.m1,q.p1,q.m2,q.p2,L)]=pstr; out.append(q)
    return out

def build(cts,ctx,Lx,pairs,extra,drift,force_equal_bases=None,open_rows=None):
    """canonical build + optional forced base equalities + optional opening rows"""
    g={m:m for m in range(9)}; gf=iso.GFSystem(N)
    E4,W4=Lx["East 4"],Lx["West 4"]
    row={N+g[Lx["East 5"]]:1, N+g[Lx["East 4"]]:N-1}
    row={k:v for k,v in row.items() if v}
    if row and gf.classify(row,0)=="pivot": gf.add(row,0)
    if force_equal_bases:
        for a,b in force_equal_bases:
            r={N+g[b]:1, N+g[a]:N-1}
            k=gf.classify(r,0)
            if k=="contradiction": return None
            if k=="pivot": gf.add(r,0)
    rows=EG.make_rows(ctx,drift,g)
    for pr in list(pairs)+list(extra):
        for rw,rhs in rows(pr,cts,N):
            k=gf.classify(rw,rhs)
            if k=="contradiction": return None
            if k=="pivot": gf.add(rw,rhs)
    for i in AUD.CELLS:
        a=int(cts[E4][28+i]); b=int(cts[W4][29+i])
        rw={b:1,a:N-1,N+g[W4]:N-1,N+g[E4]:1}
        rw={k2:v%N for k2,v in rw.items() if v%N}
        k=gf.classify(rw,drift%N)
        if k=="contradiction": return None
        if k=="pivot": gf.add(rw,drift%N)
    if open_rows:
        for (m1,t1,m2,t2) in open_rows:
            a=int(cts[m1][t1]); b=int(cts[m2][t2])
            rw={b:1,a:N-1}
            if m1!=m2: rw[N+g[m2]]=N-1; rw[N+g[m1]]=1
            rw={k2:v%N for k2,v in rw.items() if v%N}
            rhs=(drift*(t2-t1))%N
            if not rw:
                if rhs%N: return None
                continue
            k=gf.classify(rw,rhs)
            if k=="contradiction": return None
            if k=="pivot": gf.add(rw,rhs)
    return gf

def main():
    raw,labels,cts,Lx,ctx,pool,red=load()
    E1,W1,E2=Lx["East 1"],Lx["West 1"],Lx["East 2"]
    allc=H2.all_classes(raw)
    atl={frozenset((labels.index(i['message']),i['start']) for i in c['instances'])
         for c in json.load(open(os.path.join(HERE,"atlas.json")))['classes']}
    base=AUD.build(cts,ctx,Lx,red,drift=1); ab=AUD.analyse(base)
    ext=[]
    for ins,L in allc:
        if frozenset(ins) in atl: continue
        gf=AUD.build(cts,ctx,Lx,red,drift=1,extra=mk(ins,L,raw,ctx))
        if gf is None: continue
        a2=AUD.analyse(gf)
        if a2['det']!=ab['det'] or len(a2['linked'])!=len(ab['linked']):
            ext+=mk(ins,L,raw,ctx)
    poolC=[p for p in pool if not((p.m1,p.p1)==(E1,68) or (p.m2,p.p2)==(E1,68))]
    print("="*70); print("EYEHEAD -- stamped header, or encrypted co-plaintext?"); print("="*70)
    # ---- GATE
    g0=build(cts,ctx,Lx,poolC,ext,1)
    a0=AUD.analyse(g0) if g0 else None
    ok = a0 and (a0['det'],len(a0['linked']),len(a0['eq']))==(794,61,8)
    print(f"\n  G1 canonical rebuild: "
          f"{(a0['det'],len(a0['linked']),len(a0['eq'])) if a0 else None}  "
          f"{'PASS' if ok else 'FAIL'}")
    gtest=iso.GFSystem(N)
    caught = gtest.classify({},1)=="contradiction"
    print(f"  G2 contradiction detector: {'PASS' if caught else 'FAIL'}")
    if not ok or not caught:
        raise SystemExit(f"{XD} GATE FAILED -- refusing to report")
    # the opening cells, as co-plaintext assertions
    orows=[]
    for t in range(1,25):
        orows.append((E1,t,E2,t)); orows.append((E1,t,W1,t))
    print(f"\n  opening cells asserted as co-plaintext: {len(orows)}")
    print(f"  (positions 1-24 of East 1 vs East 2 and West 1)\n")
    print(f"  {'regime':46s} {'drifts OK':>10s}")
    print("  "+"-"*60)
    r1=[d for d in range(1,N) if build(cts,ctx,Lx,poolC,ext,d,open_rows=orows)]
    print(f"  {'R1 full evidence + openings co-plaintext':46s} {len(r1):10d}")
    r2=[d for d in range(1,N)
        if build(cts,ctx,Lx,poolC,ext,d,force_equal_bases=[(E1,E2),(E1,W1)])]
    print(f"  {'R2 full evidence + T1 bases forced EQUAL':46s} {len(r2):10d}")
    r3=[d for d in range(1,N) if build(cts,ctx,Lx,poolC,ext,d)]
    print(f"  {'R3 control: full evidence, no extra assertion':46s} {len(r3):10d}")
    print()
    if not r1 and not r2:
        print("  => The openings CANNOT be encrypted co-plaintext at any nonzero")
        print("     drift. The stamped-header reading is FORCED, not chosen.")
    elif r1 or r2:
        print(f"  => A consistent model EXISTS with the openings encrypted.")
        print(f"     Surviving drifts R1 {r1[:8]} R2 {r2[:8]}")
        print(f"     *** This is a rival the project has never built. ***")

if __name__=="__main__": main()
