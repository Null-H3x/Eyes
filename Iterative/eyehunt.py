#!/usr/bin/env python3
"""eyehunt -- targeted compounding scanner (FR202 / V1).
Generates candidates AIMED at the residual dark structure -- the two small
components ([4] and [2] glyphs) and the 20 undetermined glyphs -- behind the
FR201-proven certifier. Two strata:
  A: full-skeleton groups at L=60..137 (beyond FR201's sweep ceiling)
  B: relaxed-dot letter-templates (>=2 repeat-pairs), anchored at target-glyph
     occurrences: partners must share ALL template equalities (extra repeats
     allowed); letters = template cells; the target cell must be a letter.
ADMIT: 0 contradictions AND implied_new>=3 (vs EXTENDED system+cells) AND
novel>=1. Gates: geometry-preserving control on stratum-B shapes; plant."""
import sys, os, json, copy, random
from collections import defaultdict, Counter
sys.path.insert(0, ".")
from eyescan3 import load_all, emit, judge, canon_key, scan as scan_base
from make_mandatory import N

XD = "XD-MBYG04K-URS3LF"

def extended_system():
    cts,e,cells,known = load_all()
    adm = json.load(open("scan3_admitted.json"))
    ej = copy.deepcopy(e); cellsx = set(cells)
    kx = set(known)
    for a in adm:
        L,letters,locs = a["L"],a["letters"],[tuple(x) for x in a["spans"]]
        rows=[]
        for x in range(len(locs)):
            for y in range(x+1,len(locs)):
                (m1,p1),(m2,p2)=locs[x],locs[y]
                for row,rhs,cell in emit(m1,p1,m2,p2,letters,cts):
                    ej.add(row,rhs); cellsx.add(cell); rows.append((row,rhs,cell))
        kx.add(canon_key(rows))
    return cts, ej, cellsx, kx

def components(ej):
    gl = ej.used_glyphs(); par = {g:g for g in gl}
    def find(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for i in range(len(gl)):
        for j in range(i+1,len(gl)):
            if ej.query(gl[i],gl[j]) is not None: par[find(gl[i])]=find(gl[j])
    comp = defaultdict(list)
    for g in gl: comp[find(g)].append(g)
    return sorted(comp.values(), key=len, reverse=True)

def repeat_set(w):
    idx = defaultdict(list)
    for i,g in enumerate(w): idx[g].append(i)
    T = set()
    for g,ps in idx.items():
        for a in range(len(ps)):
            for b in range(a+1,len(ps)): T.add((ps[a],ps[b]))
    return frozenset(T)

def matches(w, T):
    return all(w[i]==w[j] for (i,j) in T)

def gen_stratumB(cts, targets, Ls=(10,14,18,22,26), cap=40):
    """PAIR-level generator: (anchor window containing a target at a letter,
    partner sharing the full template). Returns list of (L, letters, [w1,w2])."""
    tocc = [(mi,p) for mi,m in enumerate(cts) for p,g in enumerate(m) if g in targets]
    seen = set(); pairs = []
    win = {L: [(mi,p,tuple(m[p:p+L])) for mi,m in enumerate(cts)
              for p in range(len(m)-L+1)] for L in Ls}
    for (tm,tp) in tocc:
        for L in Ls:
            for p in range(max(0,tp-L+1), min(tp, len(cts[tm])-L)+1):
                if p+L > len(cts[tm]): continue
                w = tuple(cts[tm][p:p+L]); T = repeat_set(w)
                if len(T) < 2: continue
                letters = sorted({i for pr in T for i in pr})
                if (tp - p) not in letters: continue
                if (L, T) in seen: continue
                seen.add((L, T))
                mates = [(mi,pp) for (mi,pp,ww) in win[L]
                         if (mi,pp)!=(tm,p) and matches(ww, T)][:cap]
                for (mi,pp) in mates:
                    key = tuple(sorted([(tm,p),(mi,pp)])) + (L, T)
                    pairs.append((L, letters, [(tm,p),(mi,pp)]))
    # dedupe unordered pairs across anchors
    out, sp = [], set()
    for L, letters, locs in pairs:
        k = (L, tuple(letters), tuple(sorted(locs)))
        if k in sp: continue
        sp.add(k); out.append((L, letters, locs, None))
    return out

def rows_of(L, letters, locs, cts):
    out=[]
    for x in range(len(locs)):
        for y in range(x+1,len(locs)):
            (m1,p1),(m2,p2)=locs[x],locs[y]
            out += emit(m1,p1,m2,p2,letters,cts)
    return out

def judge_pair(ej, cellsx, rows):
    ok, tal = judge(ej, cellsx, rows)
    return (tal["contra"]==0 and tal["implied_new"]>=4 and tal["novel"]>=1), tal

def main():
    cts, ej, cellsx, kx = extended_system()
    comps = components(ej)
    small = [g for c in comps[1:] for g in c]
    dark = [g for g in range(N) if g not in set(ej.used_glyphs())]
    targets = set(small) | set(dark)
    print(f"targets: {len(small)} small-component glyphs {sorted(small)} + {len(dark)} dark")
    mode = sys.argv[1] if len(sys.argv)>1 else "run"
    rng = random.Random(4194)
    if mode == "gates":
        ok = True
        def chk(nm,c,note=""):
            nonlocal ok; ok &= bool(c); print(f"  [{'PASS' if c else 'FAIL'}] {nm} {note}")
        groups = gen_stratumB(cts, targets)
        print(f"  stratum-B groups generated: {len(groups)}")
        fab=0; ntr=0
        for (L,letters,locs,T) in groups[:150]:
            plocs=[(m,rng.randrange(0,len(cts[m])-L+1)) for (m,_) in locs]
            frows = rows_of(L,letters,plocs,cts)
            ntr+=1
            if judge_pair(ej,cellsx,frows)[0]: fab+=1
        chk("geometry-preserving control ~0", fab<=1, f"({fab}/{ntr})")
        # SYNTHETIC plant: build a genuine co-plaintext window pair from the
        # solved system: q[h]-q[g] = Dq for determined pairs, one dark glyph
        # on the partner side for novelty. Not byte-identical, template-shared.
        qh = {}
        gl = ej.used_glyphs()
        for i in range(len(gl)):
            for j in range(len(gl)):
                if i==j: continue
                v = ej.query(gl[i], gl[j])   # q[gl[j]] - q[gl[i]]
                if v is not None: qh.setdefault(v, []).append((gl[i], gl[j]))
        B1 = {0:0,1:0,2:77,3:39,4:52,5:23,6:53,7:24,8:53}
        mA, pA, mB, L = 8, 95, 3, 14
        pB, Dq = None, None
        for cand in range(40, 80):
            dq = ((cand-pA) + B1[mB] - B1[mA]) % N
            if len(qh.get(dq, [])) >= 2: pB, Dq = cand, dq; break
        (g1,h1),(g2,h2) = qh[Dq][0], qh[Dq][1]
        hdark = [g for g in range(N) if g not in set(gl)][0]
        gd = gl[5]
        cts2=[list(r) for r in cts]
        fill = [g for g in range(N) if g not in {g1,g2,gd,h1,h2,hdark}]
        w1 = [fill[0],fill[1],g1,fill[2],gd,g2,fill[3],g1,fill[4],gd,fill[5],g2,fill[6],fill[7]]
        w2 = [fill[7],fill[8],h1,fill[9],hdark,h2,fill[10],h1,fill[11],hdark,fill[12],h2,fill[13],fill[14]]
        cts2[mA][pA:pA+L]=w1; cts2[mB][pB:pB+L]=w2
        g2 = gen_stratumB(cts2, {hdark})
        found = 0
        for (Lg,letters,locs,T) in g2:
            if (mA,pA) in locs and (mB,pB) in locs:
                if judge_pair(ej,cellsx,rows_of(Lg,letters,locs,cts2))[0]: found += 1
        chk("synthetic co-plaintext pair generated AND admitted", found>0,
            f"({found} admitted groups contain both planted windows; {len(g2)} groups)")
        if not ok: raise SystemExit(f"{XD}: gate failure")
        print("  gates: ALL GREEN")
    else:
        results=[]
        # stratum A: full-skeleton groups beyond the FR201 ceiling
        from isomorph import skeleton
        for L in range(60,138):
            bysk=defaultdict(list)
            for mi,m in enumerate(cts):
                for p in range(len(m)-L+1):
                    sk=skeleton(tuple(m[p:p+L]))
                    if L-len(set(sk))>=1: bysk[sk].append((mi,p))
            for sk,locs in bysk.items():
                if len(locs)<2: continue
                cnt=Counter(sk); letters=[i for i,s in enumerate(sk) if cnt[s]>=2]
                rows=rows_of(L,letters,locs,cts)
                k=canon_key(rows)
                if k in kx: continue
                ok,tal=judge(ej,cellsx,rows)
                if ok:
                    results.append({"stratum":"A","L":L,"letters":letters,
                                    "spans":[list(x) for x in locs],"tal":dict(tal)})
        print(f"stratum A (L 60-137): {len(results)} admitted")
        groups = gen_stratumB(cts, targets)
        print(f"stratum B: {len(groups)} candidate groups")
        tally=Counter()
        for (L,letters,locs,T) in groups:
            rows = rows_of(L,letters,locs,cts)
            k = canon_key(rows)
            if k in kx: tally["known"]+=1; continue
            ok,tal = judge_pair(ej,cellsx,rows)
            if ok:
                results.append({"stratum":"B","L":L,"letters":letters,
                                "spans":[list(x) for x in locs],"tal":dict(tal)})
                tally["ADMITTED"]+=1
            elif tal["contra"]>0: tally["contra"]+=1
            elif tal["novel"]==0: tally["redundant"]+=1
            else: tally[f"weak({tal['implied_new']})"]+=1
        print("stratum B tally:", dict(tally))
        for r in results: print("  ADMIT", r["stratum"], r["L"], len(r["spans"]), r["tal"])
        json.dump(results, open("hunt_admitted.json","w"))

if __name__=="__main__":
    main()
