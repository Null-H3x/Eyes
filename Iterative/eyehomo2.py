#!/usr/bin/env python3
"""
eyehomo2 -- does planting ALL the corpus's shared structure close the
isomorph-density gap?

FR141 found the corpus carries ~10x more long-isomorph structure than a
progressive cipher over independent plaintext generates, even with the atlas's
13 classes planted as shared plaintext. Three candidate explanations; the
cheapest is that the atlas records 13 of the 208 distinct classes FR136 found,
so planting 13 under-plants badly.

METHOD. Planting overlapping spans by assignment would let later classes
overwrite earlier ones and silently destroy the sharing. Instead: union-find
over POSITIONS. For every class, every instance pair, every offset, merge the
two positions. Then draw one plaintext value per equivalence class. That plants
every co-plaintext assertion consistently, however the spans overlap.

PRE-REGISTERED:
  R1  the k=83 control must land within a factor of 2 of the corpus at every
      measured length, or no bound is reported (unchanged from FR141).
  R2  report the 13-class and 208-class plantings side by side, so the effect
      of the extra structure is visible rather than inferred.
  R3  30 seeds per configuration.

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""
import os, sys, json, random, statistics, math
from collections import defaultdict
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
XD="XD-MBYG04K-URS3LF"; N=83; LENGTHS=(12,14,16)

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

def kass(p):
    from collections import Counter
    c=Counter(ch for ch in p if ch!='.'); return sum(v-1 for v in c.values())

def all_classes(cts):
    """every distinct instance set, deduplicated, k>=2, >=2 instances"""
    best={}
    for L in range(8,40):
        b=defaultdict(list)
        for mi,ct in enumerate(cts):
            for s in range(len(ct)-L+1): b[pat(ct[s:s+L])].append((mi,s))
        for p,inst in b.items():
            if kass(p)<2 or len(inst)<2: continue
            key=frozenset(inst)
            if key not in best or L>best[key][0]: best[key]=(L,p)
    return [(sorted(k),v[0]) for k,v in best.items()]

def atlas_classes(atlas,labels):
    Lx={l:i for i,l in enumerate(labels)}
    return [([(Lx[i["message"]],i["start"]) for i in c["instances"]], c["length"])
            for c in atlas if len(c["instances"])>1]

def plant(classes, lengths):
    """union-find over positions; returns parent map"""
    par={}
    def f(x):
        par.setdefault(x,x)
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for ins,L in classes:
        for a in range(len(ins)):
            for b in range(a+1,len(ins)):
                (m1,s1),(m2,s2)=ins[a],ins[b]
                for i in range(L):
                    p1,p2=(m1,s1+i),(m2,s2+i)
                    if s1+i>=lengths[m1] or s2+i>=lengths[m2]: continue
                    r1,r2=f(p1),f(p2)
                    if r1!=r2: par[r1]=r2
    return f

def simulate(k, find, lengths, rng):
    slot=list(range(k))+[rng.randrange(k) for _ in range(N-k)]
    rng.shuffle(slot)
    inv=defaultdict(list)
    for g,s in enumerate(slot): inv[s].append(g)
    val={}
    P=[]
    for m,L in enumerate(lengths):
        row=[]
        for t in range(L):
            r=find((m,t))
            if r not in val: val[r]=rng.randrange(k)
            row.append(val[r])
        P.append(row)
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
    cj=json.load(open(os.path.join(HERE,"corpus.json")))
    cts=cj["ciphertexts"]; labels=cj["message_labels"]
    atlas=json.load(open(os.path.join(HERE,"atlas.json")))["classes"]
    ck("t1_load", len(cts)==9, f"{len(cts)} messages")
    ac=atlas_classes(atlas,labels)
    ck("t2_atlas", len(ac)==13, f"{len(ac)} atlas classes")
    allc=all_classes(cts)
    ck("t3_all", len(allc)>150, f"{len(allc)} distinct classes found")
    lengths=[len(c) for c in cts]
    f13=plant(ac,lengths); fall=plant(allc,lengths)
    n13=len({f13((m,t)) for m,L in enumerate(lengths) for t in range(L)})
    nall=len({fall((m,t)) for m,L in enumerate(lengths) for t in range(L)})
    ck("t4_planting_binds", nall<n13, f"13-class: {n13} free values, all: {nall}")
    print(f"selftest {sum(1 for _,p in ok if p)}/{len(ok)} green")
    return cts,labels,atlas,ac,allc,lengths

def run(cts,labels,atlas,ac,allc,lengths):
    real={L:iso_pairs(cts,L) for L in LENGTHS}
    print("="*72); print("EYEHOMO2 -- planting ALL shared structure"); print("="*72)
    print(f"\n  atlas classes {len(ac)}   all distinct classes {len(allc)}")
    print(f"  REAL CORPUS   "+"  ".join(f"L={L} {real[L]:4d}" for L in LENGTHS)+"\n")
    for label,classes in (("13 atlas classes",ac),("ALL %d classes"%len(allc),allc)):
        find=plant(classes,lengths)
        free=len({find((m,t)) for m,L in enumerate(lengths) for t in range(L)})
        print(f"  --- planting {label}  ({free} free plaintext values of {sum(lengths)}) ---")
        print(f"  {'k':>4s} "+"".join(f"{'L='+str(L):>17s}" for L in LENGTHS))
        res={}
        for k in (83,75,65,56,40):
            acc={L:[] for L in LENGTHS}; rng=random.Random(2000+k)
            for s in range(30):
                m=simulate(k,find,lengths,rng)
                for L in LENGTHS: acc[L].append(iso_pairs(m,L))
            res[k]={L:(statistics.mean(acc[L]),statistics.pstdev(acc[L])) for L in LENGTHS}
            print(f"  {k:4d} "+"".join(f"{res[k][L][0]:9.1f}+-{res[k][L][1]:<6.1f}" for L in LENGTHS))
        print(f"  [R1] control at k=83:", end=" ")
        okc=True
        for L in LENGTHS:
            mu,_=res[83][L]; r=real[L]; ratio=mu/r
            okc &= (0.5<=ratio<=2.0)
            print(f"L={L} ratio {ratio:.2f}", end="  ")
        print(f"-> {'PASSES' if okc else 'FAILS'}\n")

if __name__=="__main__":
    env=selftest()
    if "--selftest" not in sys.argv: run(*env)
