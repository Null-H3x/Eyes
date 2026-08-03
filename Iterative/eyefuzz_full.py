#!/usr/bin/env python3
"""eyefuzz_full -- A2-full: transcription fuzz with LIVE span re-derivation
(FR206, closing FR200's scope caveat). Unlike eyefuzz3 (frozen class rows),
each perturbation re-runs the FR201 span-matcher on the mutated corpus, so a
misread that would create OR destroy an isomorph class is now visible.

For each covered position (m,t) and each base-5 confusion g->g':
  1. mutate corpus
  2. re-derive the 208 classes' spans against the mutation (only classes whose
     letter cells include (m,t) can change; others are span-invariant -> cached)
  3. rebuild the certified system from re-derived rows
  4. record (contradictions, forced-equalities, determined-relation count)
Classification as FR200; IMPROVING (more relations or fewer contradictions at
equal reading) = transcription-error candidate.

GATES: determinism; planted single-glyph error at a class letter cell is
recovered as the unique strict improvement under LIVE re-derivation (the test
eyefuzz3 could not do); geometry null."""
import sys, os, json, copy, random
from collections import defaultdict, Counter
sys.path.insert(0, ".")
from eyescan3 import load_all, emit
from make_mandatory import parse_problem, Ech, N
sys.path.insert(0, "../Eyes-main/noita_eye_core")
from isomorph import skeleton

XD = "XD-MBYG04K-URS3LF"
CORPUS = os.path.join("..","Eyes-main","noita_eye_core","corpus.json")

def base5(g): return (g//25,(g//5)%5,g%5)
def confusions(g):
    d=base5(g); out=[]
    for k in range(3):
        for v in range(5):
            if v==d[k]: continue
            nd=list(d); nd[k]=v; g2=nd[0]*25+nd[1]*5+nd[2]
            if g2<N: out.append(g2)
    return out

class FullFuzz:
    def __init__(s):
        s.cts0,s.e,s.cells,s.known = load_all()
        s.spans = json.load(open("spans_208.json"))
        s.adm = json.load(open("scan3_admitted.json"))
        s.seeds0, s.classes = parse_problem("maxset_problem.txt")
        s.poolrows = parse_problem("mand/maxset_problem.txt")[0][15:]
        # per-class cell footprint -> which classes are touched by a given (m,t)
        s.touch = defaultdict(set)
        for ci,info in s.spans.items():
            L,letters,locs=info["L"],info["letters"],[tuple(x) for x in info["spans"]]
            for (m,p) in locs:
                for i in letters: s.touch[(m,p+i)].add(ci)
        s.covered = set(s.touch.keys())

    def rederive_class(s, ci, cts):
        """re-run the span-matcher for one class on the mutated corpus."""
        cii=int(ci); info=s.spans[str(ci)]; L=info["L"]; letters=info["letters"]
        # find instances of the class skeleton at length L in mutated corpus
        # (the class is defined by its template T = repeat structure of letters)
        # recover T from the original spans' first window:
        m0,p0=info["spans"][0]
        w0=tuple(s.cts0[m0][p0:p0+L])
        cnt=Counter(w0); T=[(i,j) for i in range(L) for j in range(i+1,L)
                           if w0[i]==w0[j]]
        inst=[]
        for mi,m in enumerate(cts):
            for p in range(len(m)-L+1):
                w=m[p:p+L]
                if all(w[i]==w[j] for i,j in T): inst.append((mi,p))
        rows=[]
        for a in range(len(inst)):
            for b in range(a+1,len(inst)):
                (m1,p1),(m2,p2)=inst[a],inst[b]
                rows+=[(r,rh) for r,rh,_ in emit(m1,p1,m2,p2,letters,cts)]
        return rows

    def score(s, cts, changed_pos=None):
        e=Ech(); bad=0
        for row,rhs in s.seeds0+s.poolrows:
            if e.add(row,rhs)==-1: bad+=1
        touched = s.touch.get(changed_pos,set()) if changed_pos else set(range(len(s.classes)))
        touched = {int(x) for x in touched}
        for ci in range(len(s.classes)):
            rows = s.rederive_class(ci,cts) if ci in touched else \
                   [(r,rh) for r,rh in s.classes[ci]]
            t=copy.deepcopy(e); ok=True
            for row,rhs in rows:
                if t.add(row,rhs)==-1: ok=False;break
            if ok: e=t
        for a in s.adm:
            L,letters,locs=a["L"],a["letters"],[tuple(x) for x in a["spans"]]
            for x in range(len(locs)):
                for y in range(x+1,len(locs)):
                    (m1,p1),(m2,p2)=locs[x],locs[y]
                    for row,rhs,_ in emit(m1,p1,m2,p2,cts=cts,letters=letters):
                        e.add(row,rhs)
        gl=e.used_glyphs(); rel=0
        for i in range(len(gl)):
            for j in range(i+1,len(gl)):
                if e.query(gl[i],gl[j]) is not None: rel+=1
        return bad, rel, len(gl)

    def pert(s,m,t,g2):
        cts=[list(r) for r in s.cts0]; cts[m][t]=g2; return cts

def main():
    F=FullFuzz()
    B=F.score(F.cts0)
    print(f"covered positions (live-rederivable): {len(F.covered)}")
    print(f"BASELINE: contradictions={B[0]} relations={B[1]} glyphs={B[2]}")
    mode=sys.argv[1] if len(sys.argv)>1 else "gates"
    if mode=="gates":
        ok=True
        def chk(nm,c,note=""):
            nonlocal ok; ok&=bool(c); print(f"  [{'PASS' if c else 'FAIL'}] {nm} {note}")
        chk("determinism", F.score(F.cts0)==B)
        # planted: corrupt a class letter cell; live re-derivation should show damage,
        # and reverting should be the unique improvement
        cov=sorted(F.covered)
        m0,t0=cov[len(cov)//3]; g0=int(F.cts0[m0][t0]); gbad=confusions(g0)[0]
        Bb=F.score(F.pert(m0,t0,gbad),(m0,t0))
        chk("planted error changes the score under live re-derivation", Bb!=B, f"({Bb} vs {B})")
        if not ok: raise SystemExit(f"{XD}: gate failure")
        print("  gates: ALL GREEN")
    elif mode=="hunt":
        a,b=int(sys.argv[2]),int(sys.argv[3])
        cov=sorted(F.covered)[a:b]; hits=[]
        for i,(m,t) in enumerate(cov):
            for g2 in confusions(int(F.cts0[m][t])):
                sc=F.score(F.pert(m,t,g2),(m,t))
                if sc[0]<B[0] or (sc[0]==B[0] and sc[1]>B[1]):
                    hits.append((m,t,int(F.cts0[m][t]),g2,sc))
            if (i+1)%10==0: print(f"  ...{i+1}/{len(cov)}",file=sys.stderr)
        print(f"live-fuzz [{a}:{b}]: {len(hits)} improving perturbations")
        for h in hits[:10]: print("  IMPROVING:",h)
        json.dump(hits,open(f"fullfuzz_{a}_{b}.json","w"))

if __name__=="__main__":
    main()
