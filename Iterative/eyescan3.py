#!/usr/bin/env python3
"""eyescan3 -- deep scan with cell-provenance certification (FR201 / A3).
Fixes eyescan2's control failure: (1) 'implied' now counts only rows at
CELL-PAIRS absent from the certified system's generating set (pool letter
cells + all 208 classes via spans_208.json) -- confirmations through shared
cells are logged but carry no admission weight; (2) the fabricated control
is geometry-preserving (same L, letter template, instance count, messages;
random positions), per the FR41/FR42 null doctrine.
ADMIT iff 0 contradictions AND implied_new >= 3 AND novel >= 1."""
import sys, os, json, random
from collections import defaultdict, Counter
sys.path.insert(0, ".")
import eyeaudit as A, eyegauge as EG
from make_mandatory import parse_problem, Ech, N
sys.path.insert(0, "../Eyes-main/noita_eye_core")
from isomorph import skeleton

XD = "XD-MBYG04K-URS3LF"
CORPUS = os.path.join("..","Eyes-main","noita_eye_core","corpus.json")
ATLAS  = os.path.join("..","Eyes-main","data","isomorph_atlas.json")

def emit(m1,p1,m2,p2,letters,cts):
    out=[]
    for i in letters:
        Aa=int(cts[m1][p1+i]); D=int(cts[m2][p2+i]); row={}
        row[D]=(row.get(D,0)+1)%N; row[Aa]=(row.get(Aa,0)+N-1)%N
        if m1!=m2:
            row[N+m2]=(row.get(N+m2,0)+N-1)%N; row[N+m1]=(row.get(N+m1,0)+1)%N
        cell=frozenset(((m1,p1+i),(m2,p2+i)))
        out.append(({c:v for c,v in row.items() if v},(p2-p1)%N,cell))
    return out

def canon_key(rows):
    return tuple(sorted(Counter((tuple(sorted(r.items())),rhs) for r,rhs,_ in rows).items()))

def classify(e,row,rhs):
    v=dict(row); v[92]=rhs%N
    c,v=e._reduce(v)
    if c is None: return "contra" if v.get(92,0)%N else "implied"
    return "novel"

def load_all():
    cj=json.load(open(CORPUS)); cts=[list(r) for r in cj["ciphertexts"]]
    _,_,_,ctx,pool,_ = A.load(CORPUS, ATLAS)
    seeds0, classes = parse_problem("maxset_problem.txt")
    poolrows = parse_problem("mand/maxset_problem.txt")[0][15:]
    e = Ech()
    for row,rhs in seeds0+poolrows: e.add(row,rhs)
    import copy
    for rows in classes:
        t=copy.deepcopy(e); ok=True
        for row,rhs in rows:
            if t.add(row,rhs)==-1: ok=False; break
        if ok: e=t
    # certified cell-pair set
    cells=set()
    for pr in pool:
        key=(pr.m1,pr.p1,pr.m2,pr.p2,pr.length); pat=ctx["pattern_of"].get(key)
        for i in range(pr.length):
            if pat is not None and not pr.exact and pat[i]=='.': continue
            if pat is None and not pr.exact and \
               ((pr.m1,pr.p1+i) in ctx["dot"] or (pr.m2,pr.p2+i) in ctx["dot"]): continue
            cells.add(frozenset(((pr.m1,pr.p1+i),(pr.m2,pr.p2+i))))
    spans=json.load(open("spans_208.json"))
    for ci,info in spans.items():
        L=info["L"]; letters=info["letters"]; locs=[tuple(x) for x in info["spans"]]
        for a in range(len(locs)):
            for b in range(a+1,len(locs)):
                (m1,p1),(m2,p2)=locs[a],locs[b]
                for i in letters:
                    cells.add(frozenset(((m1,p1+i),(m2,p2+i))))
    known={ canon_key([({c:v for c,v in row.items() if v},rhs,None) for row,rhs in bl]) for bl in classes }
    return cts,e,cells,known

def scan(cts,known):
    cands={}
    for L in range(6,60):
        bysk=defaultdict(list)
        for mi,m in enumerate(cts):
            for p in range(len(m)-L+1):
                sk=skeleton(tuple(m[p:p+L]))
                if L-len(set(sk))>=1: bysk[sk].append((mi,p))
        for sk,locs in bysk.items():
            if len(locs)<2: continue
            cnt=Counter(sk); letters=[i for i,s in enumerate(sk) if cnt[s]>=2]
            if not letters: continue
            rows=[]
            for a in range(len(locs)):
                for b in range(a+1,len(locs)):
                    (m1,p1),(m2,p2)=locs[a],locs[b]
                    rows+=emit(m1,p1,m2,p2,letters,cts)
            k=canon_key(rows)
            if k in known or k in cands: continue
            cands[k]=(L,letters,locs,rows)
    return cands

def judge(e,cells,rows):
    tal=Counter()
    for row,rhs,cell in rows:
        cl=classify(e,row,rhs)
        if cl=="implied" and cell is not None and cell not in cells: cl="implied_new"
        tal[cl]+=1
    ok = tal["contra"]==0 and tal["implied_new"]>=3 and tal["novel"]>=1
    return ok,tal

def main():
    cts,e,cells,known = load_all()
    mode=sys.argv[1] if len(sys.argv)>1 else "run"
    rng=random.Random(83)
    if mode=="gates":
        ok=True
        def chk(nm,c,note=""):
            nonlocal ok; ok&=bool(c); print(f"  [{'PASS' if c else 'FAIL'}] {nm} {note}")
        # planted: copy a 12-window to a fresh location -> genuine co-plaintext
        cts2=[list(r) for r in cts]; cts2[2][80:92]=list(cts2[2][30:42])
        cands=scan(cts2,known); adm=sum(1 for k,v in cands.items() if judge(e,cells,v[3])[0])
        chk("planted structure admitted", adm>0, f"({len(cands)} cands, {adm} admitted)")
        # geometry-preserving fabrication on REAL candidates
        cands0=scan(cts,known); fab=0; ntr=0
        for k,(L,letters,locs,rows) in list(cands0.items())[:150]:
            plocs=[]
            for (m,_) in locs:
                plocs.append((m, rng.randrange(0, len(cts[m])-L+1)))
            frows=[]
            for a in range(len(plocs)):
                for b in range(a+1,len(plocs)):
                    (m1,p1),(m2,p2)=plocs[a],plocs[b]
                    if m1==m2 and p1==p2: continue
                    frows+=emit(m1,p1,m2,p2,letters,cts)
            ntr+=1
            if judge(e,cells,frows)[0]: fab+=1
        chk("geometry-preserving control false-admit ~0", fab<=1, f"({fab}/{ntr})")
        if not ok: raise SystemExit(f"{XD}: gate failure")
        print("  gates: ALL GREEN")
    else:
        cands=scan(cts,known)
        print(f"candidates beyond the 208: {len(cands)}")
        tally=Counter(); admitted=[]
        for k,(L,letters,locs,rows) in cands.items():
            ok,tal=judge(e,cells,rows)
            if ok: admitted.append((L,letters,locs,dict(tal))); tally["ADMITTED"]+=1
            elif tal["contra"]>0: tally["contradicting"]+=1
            elif tal["novel"]==0: tally["fully-redundant"]+=1
            else: tally[f"implied_new={tal['implied_new']}"]+=1
        print("tally:", dict(tally))
        for L,letters,locs,tal in admitted[:12]:
            print(f"  ADMIT L={L} inst={len(locs)} letters={len(letters)} {tal}")
        json.dump([{"L":L,"letters":letters,"spans":[list(x) for x in locs],"tal":tal}
                   for L,letters,locs,tal in admitted], open("scan3_admitted.json","w"))

if __name__=="__main__":
    main()
