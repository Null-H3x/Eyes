#!/usr/bin/env python3
"""
eyehomo -- CALIBRATED homophone simulation: can isomorph survival bound the
alphabet size?

WHY FR138's VERSION DOES NOT COUNT. It planted an arbitrary 60-glyph shared
head across all nine messages. Its own positive control fails:

    k=83 (no homophones)  ->  18.2 / 58.5 / 144.8
    real corpus           ->  53   / 73   /  93

3x low at L=12, 1.6x high at L=16. A simulation that cannot reproduce the
corpus at the alphabet size where it should agree BEST cannot bound k at all.

THE FIX. Use the corpus's REAL shared structure: the atlas's 13 classes at
their actual positions and lengths, planted as genuinely shared plaintext.

PRE-REGISTERED:
  R1  the k=83 control must land within a factor of 2 of the corpus at every
      measured length, or NO BOUND is reported. This is what FR138 skipped.
  R2  a k is disfavoured only where its simulated count is more than 2 sd
      below the observed count.
  R3  30 seeds per k, not 4.

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""
import os, sys, json, random, statistics
from collections import defaultdict
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
XD="XD-MBYG04K-URS3LF"; N=83; LENGTHS=(12,14,16)

def load():
    cj=json.load(open(os.path.join(HERE,"corpus.json")))
    at=json.load(open(os.path.join(HERE,"atlas.json")))["classes"]
    return cj["ciphertexts"], cj["message_labels"], at

def pat(w):
    pos=defaultdict(list)
    for i,v in enumerate(w): pos[v].append(i)
    reps=sorted((min(ps),ps) for v,ps in pos.items() if len(ps)>1)
    out=['.']*len(w)
    for k,(_,ps) in enumerate(reps):
        for p in ps: out[p]=chr(ord('A')+k)
    return "".join(out)

def iso_pairs(ms,L,minlet=3):
    b=defaultdict(list)
    for mi,ct in enumerate(ms):
        for s in range(len(ct)-L+1):
            p=pat(ct[s:s+L])
            if sum(1 for c in set(p) if c!='.')>=minlet: b[p].append((mi,s))
    return sum(len(v)*(len(v)-1)//2 for v in b.values() if len(v)>1)

def shared_spans(atlas,labels):
    Lx={l:i for i,l in enumerate(labels)}
    return [([(Lx[i["message"]],i["start"]) for i in c["instances"]], c["length"])
            for c in atlas if len(c["instances"])>1]

def simulate(k,spans,lengths,rng):
    slot=list(range(k))+[rng.randrange(k) for _ in range(N-k)]
    rng.shuffle(slot)
    inv=defaultdict(list)
    for g,s in enumerate(slot): inv[s].append(g)
    P=[[rng.randrange(k) for _ in range(L)] for L in lengths]
    for ins,L in spans:
        block=[rng.randrange(k) for _ in range(L)]
        for (m,s) in ins:
            for i in range(L):
                if s+i < len(P[m]): P[m][s+i]=block[i]
    out=[]
    for m,L in enumerate(lengths):
        bm=rng.randrange(N)
        out.append([(rng.choice(inv[P[m][t]])+bm+7*t)%N for t in range(L)])
    return out

def selftest():
    ok=[]
    def ck(n,c,d=""):
        ok.append((n,bool(c))); print(f"  {n:32s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise RuntimeError(f"{XD} selftest FAILED: {n} {d}")
    cts,labels,atlas=load()
    ck("t1_load", len(cts)==9 and len(atlas)==13, f"{len(cts)} msgs, {len(atlas)} classes")
    spans=shared_spans(atlas,labels)
    ck("t2_spans", len(spans)==13, f"{len(spans)} shared-span groups")
    m=simulate(83,spans,[len(c) for c in cts],random.Random(1))
    ck("t3_shape", [len(x) for x in m]==[len(c) for c in cts], "lengths match")
    ck("t4_alphabet", len({v for r in m for v in r})>70,
       f"{len({v for r in m for v in r})} glyphs at k=83")
    print(f"selftest {sum(1 for _,p in ok if p)}/{len(ok)} green")
    return cts,labels,atlas

def run(cts,labels,atlas):
    spans=shared_spans(atlas,labels); lengths=[len(c) for c in cts]
    real={L:iso_pairs(cts,L) for L in LENGTHS}
    print("="*72); print("EYEHOMO -- calibrated homophone simulation"); print("="*72)
    print(f"\n  atlas shared-span groups planted : {len(spans)}   seeds per k : 30\n")
    print("  REAL CORPUS   "+"  ".join(f"L={L} {real[L]:4d}" for L in LENGTHS)+"\n")
    print(f"  {'k':>4s} {'merges':>7s} "+"".join(f"{'L='+str(L):>17s}" for L in LENGTHS))
    print("  "+"-"*62)
    res={}
    for k in (83,80,75,70,65,60,56,50,40,30):
        acc={L:[] for L in LENGTHS}; rng=random.Random(1000+k)
        for s in range(30):
            m=simulate(k,spans,lengths,rng)
            for L in LENGTHS: acc[L].append(iso_pairs(m,L))
        res[k]={L:(statistics.mean(acc[L]),statistics.pstdev(acc[L])) for L in LENGTHS}
        print(f"  {k:4d} {83-k:7d} "+"".join(f"{res[k][L][0]:9.1f}+-{res[k][L][1]:<6.1f}" for L in LENGTHS))
    print("\n  [R1] POSITIVE CONTROL at k=83 (bijective, no homophones):")
    okc=True
    for L in LENGTHS:
        mu,sd=res[83][L]; r=real[L]; ratio=mu/r if r else 0
        good=0.5<=ratio<=2.0; okc&=good
        print(f"       L={L}: simulated {mu:6.1f}+-{sd:5.1f}  real {r:3d}"
              f"   ratio {ratio:4.2f}  {'OK' if good else 'FAIL'}")
    print()
    if not okc:
        print("  *** CONTROL FAILS -- the simulation cannot reproduce the corpus")
        print("      at k=83, so it cannot bound k. NO BOUND REPORTED.")
        print("      FR138's 'alphabet probably >=60' is WITHDRAWN.")
        return
    print("  [R2] control passes; bounds:")
    for k in sorted(res,reverse=True):
        low=[L for L in LENGTHS if res[k][L][0]+2*res[k][L][1] < real[L]]
        if low: print(f"       k={k}: below observed at L={low} -> disfavoured")

if __name__=="__main__":
    env=selftest()
    if "--selftest" not in sys.argv: run(*env)
