#!/usr/bin/env python3
"""eyefuzz3 -- transcription screen, composite metric (FR200 / A2-screen).
Score(corpus) over [UNREPAIRED pool rows re-emitted from the corpus] +
[158 repair-C-survivor class rows, frozen at pristine values]:
    (contradictions during adds, forced glyph-glyph equalities)
Caveat carried: class rows frozen -> screening-level; airtight A2 needs span
regeneration via isomorph.find_isomorphs (located, logged as A2-full)."""
import sys, os, json, random
sys.path.insert(0, ".")
import eyeaudit as A, eyegauge as EG, eyerepair as ERP
from make_mandatory import parse_problem, Ech, N

XD = "XD-MBYG04K-URS3LF"
CORPUS = os.path.join("..","Eyes-main","noita_eye_core","corpus.json")
ATLAS  = os.path.join("..","Eyes-main","data","isomorph_atlas.json")

def base5(g): return (g//25, (g//5)%5, g%5)
def confusions(g):
    d = base5(g); out=[]
    for k in range(3):
        for v in range(5):
            if v==d[k]: continue
            nd=list(d); nd[k]=v; g2=nd[0]*25+nd[1]*5+nd[2]
            if g2 < N: out.append(g2)
    return out

def represent(e, col):
    """full substitution of pivot columns; returns (freeparts_key, const)."""
    v = {col: 1, "K": 0}
    changed = True
    while changed:
        changed = False
        for c in [c for c in list(v) if c != "K" and v.get(c, 0) % N]:
            r = e.piv.get(c)
            if r is None: continue
            x = v[c] % N; rr = e.rows[r]
            for k, val in rr.items():
                kk = "K" if k == 92 else k
                v[kk] = (v.get(kk, 0) - x*val) % N
            v[c] = 0; changed = True
    key = tuple(sorted((k, val % N) for k, val in v.items() if k != "K" and val % N))
    return key, v.get("K", 0) % N

def equalities(e):
    from collections import Counter, defaultdict
    groups = defaultdict(list)
    for g in e.used_glyphs():
        key, c = represent(e, g)
        groups[key].append(c)
    eq = 0
    for key, consts in groups.items():
        cc = Counter(consts)
        eq += sum(n*(n-1)//2 for n in cc.values())
    return eq

class F:
    def __init__(s):
        s.cts, s.labels, s.Lx, s.ctx, pool, red = A.load(CORPUS, ATLAS)
        s.pool_un = pool
        s.rows_fn = EG.make_rows(s.ctx, 1, None, 9)
        seeds0, classes = parse_problem("maxset_problem.txt")
        poolrows = parse_problem("mand/maxset_problem.txt")[0][15:]
        # recompute the 158 survivors exactly as eyeproof does
        base = Ech()
        for row, rhs in seeds0 + poolrows: base.add(row, rhs)
        import copy
        s.surv_rows = []
        for rows in classes:
            t = copy.deepcopy(base); ok = True
            for row, rhs in rows:
                if t.add(row, rhs) == -1: ok=False; break
            if ok: s.surv_rows += rows
        s.legacy = seeds0
        s.covered = set()
        for pr in pool:
            key=(pr.m1,pr.p1,pr.m2,pr.p2,pr.length); pat=s.ctx["pattern_of"].get(key)
            for i in range(pr.length):
                if pat is not None and not pr.exact and pat[i]=='.': continue
                if pat is None and not pr.exact and \
                   ((pr.m1,pr.p1+i) in s.ctx["dot"] or (pr.m2,pr.p2+i) in s.ctx["dot"]): continue
                s.covered.add((pr.m1,pr.p1+i)); s.covered.add((pr.m2,pr.p2+i))
        s.e168 = set()
        dropped=[p for p in pool if (p.m1,p.p1)==(0,68) or (p.m2,p.p2)==(0,68)]
        s.n_dropped=len(dropped)
        for pr in dropped:
            for i in range(pr.length):
                s.e168.add((pr.m1,pr.p1+i)); s.e168.add((pr.m2,pr.p2+i))

    def score(s, cts):
        e = Ech(); bad = 0
        for row, rhs in s.legacy:
            if e.add(row, rhs) == -1: bad += 1
        for pr in s.pool_un:
            for row, rhs in s.rows_fn(pr, cts, N):
                if e.add(row, rhs) == -1: bad += 1
        for row, rhs in s.surv_rows:
            if e.add(row, rhs) == -1: bad += 1
        return bad, equalities(e)

    def pert(s, m, t, g2):
        cts=[list(r) for r in s.cts]; cts[m][t]=g2; return cts

def main():
    F0 = F()
    B = F0.score(F0.cts)
    print(f"survivor class rows: {len(F0.surv_rows)}   pool-covered positions: {len(F0.covered)}")
    print(f"BASELINE (unrepaired pool + survivors): contradictions={B[0]}  forced-equalities={B[1]}")
    mode = sys.argv[1] if len(sys.argv)>1 else "gates"
    if mode=="gates":
        ok=True
        def chk(nm,c,note=""):
            nonlocal ok; ok&=bool(c); print(f"  [{'PASS' if c else 'FAIL'}] {nm} {note}")
        chk("determinism", F0.score(F0.cts)==B)
        rng=random.Random(83); worse=same=better=0; det=0; trials=120
        cov=sorted(F0.covered)
        for _ in range(trials):
            m,t=rng.choice(cov); g2=rng.choice(confusions(int(F0.cts[m][t])))
            sc=F0.score(F0.pert(m,t,g2))
            if sc!=B: det+=1
            if sc[0]>B[0] or (sc[0]==B[0] and sc[1]>B[1]): worse+=1
            elif sc==B: same+=1
            else: better+=1
        print(f"  null: worse {worse}/{trials}  same {same}/{trials}  better {better}/{trials}  (detectable {det}/{trials})")
        chk("random perturbations rarely improve", better<=3)
        m0,t0=cov[len(cov)//3]; g0=int(F0.cts[m0][t0]); gbad=confusions(g0)[0]
        Fb=F(); Fb.cts=F0.pert(m0,t0,gbad); Bb=Fb.score(Fb.cts)
        chk("plant is detectable", Bb!=B, f"(corrupt score {Bb} vs {B})")
        best=(None,Bb)
        for (m,t) in cov:
            if m!=m0: continue
            for g2 in confusions(int(Fb.cts[m][t])):
                sc=Fb.score(Fb.pert(m,t,g2))
                if sc<best[1]: best=((m,t,g2),sc)
        chk("planted error located exactly", best[0]==(m0,t0,g0) and best[1]==B,
            f"(found {best[0]} score {best[1]})")
        if not ok: raise SystemExit(f"{XD}: gate failure")
        print("  gates: ALL GREEN")
    elif mode=="tier1":
        hits=[]
        for (m,t) in sorted(F0.e168):
            for g2 in confusions(int(F0.cts[m][t])):
                sc=F0.score(F0.pert(m,t,g2))
                if sc<B: hits.append((m,t,int(F0.cts[m][t]),g2,sc))
        print(f"TIER1 E1@68 typo screen over {len(F0.e168)} positions:")
        if not hits: print(f"  NO single-eye misread improves on baseline {B}.")
        for m,t,g,g2,sc in sorted(hits,key=lambda x:x[4])[:10]:
            print(f"  IMPROVING: {F0.labels[m]}@{t}: {g}->{g2}  score {B} -> {sc}")
    elif mode=="tier2":
        a,b=int(sys.argv[2]),int(sys.argv[3]); out=open(f"fuzz3_{a}_{b}.jsonl","w")
        for (m,t) in sorted(F0.covered)[a:b]:
            best=None; worst=None
            for g2 in confusions(int(F0.cts[m][t])):
                sc=F0.score(F0.pert(m,t,g2))
                best=sc if best is None or sc<best else best
                worst=sc if worst is None or sc>worst else worst
            out.write(json.dumps({"m":m,"t":t,"g":int(F0.cts[m][t]),
                                  "best":best,"worst":worst})+"\n")
        out.close(); print(f"tier2 [{a}:{b}] done")

if __name__=="__main__":
    main()
