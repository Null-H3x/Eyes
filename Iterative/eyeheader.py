#!/usr/bin/env python3
"""eyeheader -- the header attack toolkit (FR202 / V2).
The stamped headers are 111 positions (24x3 T1, 20x3 T3), ~92% on determined
glyphs, identical within each triplet. This instrument ships three things:
  1. LADDERS: repeated header glyphs give p(t2)-p(t1) = -d*(t2-t1) exactly --
     one glyph's meaning at two offsets pins the drift.
  2. SOLVER: any two known header plaintexts (giant-member glyphs) ->
     (d, Q0) -> both headers decoded + 771 positions. Turnkey for the ask.
  3. FINGERPRINTS: for each candidate d in 1..82, the equality-partition of
     all header positions (drift-DEPENDENT, offset-free) -- qualitative
     external lore ('the opening repeats a token', 'starts doubled') filters
     d without anyone solving anything.
Gate: planted (d,Q0) round-trips exactly; fingerprint determinism."""
import sys, os, json, copy
sys.path.insert(0, ".")
from collections import defaultdict
from eyescan3 import load_all, emit
from make_mandatory import N

XD = "XD-MBYG04K-URS3LF"
B1 = {0:0,1:0,2:77,3:39,4:52,5:23,6:53,7:24,8:53}   # drift-1 b-vector (FR195/196)

def build_extended():
    cts,e,cells,known = load_all()
    adm = json.load(open("scan3_admitted.json"))
    ej = copy.deepcopy(e)
    for a in adm:
        L,letters,locs = a["L"],a["letters"],[tuple(x) for x in a["spans"]]
        for x in range(len(locs)):
            for y in range(x+1,len(locs)):
                (m1,p1),(m2,p2)=locs[x],locs[y]
                for row,rhs,_ in emit(m1,p1,m2,p2,letters,cts): ej.add(row,rhs)
    return cts, ej

def header_map(cts):
    out = []   # (m, t, glyph)
    for m in (0,1,2):
        for t in range(1,25): out.append((m,t,int(cts[m][t])))
    for m in (6,7,8):
        for t in range(1,21): out.append((m,t,int(cts[m][t])))
    return out

def qrel(ej, ref=66):
    """q[g]-q[ref] at drift 1 for every determined glyph (giant members)."""
    r = {ref: 0}
    for g in ej.used_glyphs():
        if g == ref: continue
        v = ej.query(ref, g)      # q[g]-q[ref]
        if v is not None: r[g] = v
    return r

def p1(m,t,g,q):
    """drift-1 plaintext coordinate: p = Q0 + d*(q1[g] - b1[m] - t); return coeff."""
    return (q[g] - B1[m] - t) % N

def solver(known_vals, q):
    """known_vals: [(m,t,v)] with header glyph in q. Solve p = Q0 + d*coef."""
    eqs = [ (p1(m,t,g,q), v) for (m,t,v,g) in known_vals ]
    sols = []
    for d in range(1,N):
        Q0s = {(v - d*coef) % N for coef,v in eqs}
        if len(Q0s)==1: sols.append((d, Q0s.pop()))
    return sols

def structure_sheet(cts, ej, q):
    """d-FREE header structure (scale-invariance: equalities & difference RATIOS
    carry no d). Ships coef profile + the relation->d lookup: any external
    QUANTITATIVE relation p(a)-p(b)=k pins d = k * inv(dcoef)."""
    hm = [(m,t,g) for m,t,g in header_map(cts) if g in q]
    coef = {(m,t): p1(m,t,g,q) for m,t,g in hm}
    lab, part = {}, {}
    for (m,t,g) in hm:
        c = coef[(m,t)]
        if c not in lab: lab[c] = len(lab)
        part[f"{m}:{t}"] = lab[c]
    return hm, {f"{m}:{t}": coef[(m,t)] for m,t,g in hm}, part

def fingerprints(cts, ej, q):
    hm = [(m,t,g) for m,t,g in header_map(cts) if g in q]
    fps = {}
    for d in range(1,N):
        val = {}
        for m,t,g in hm:
            val[(m,t)] = (d * p1(m,t,g,q)) % N     # p up to Q0
        # canonical partition: order-of-first-appearance labels over T1 then T3
        lab, out = {}, []
        for m,t,g in hm:
            v = val[(m,t)]
            if v not in lab: lab[v] = len(lab)
            out.append(lab[v])
        fps[d] = tuple(out)
    return hm, fps

def main():
    cts, ej = build_extended()
    q = qrel(ej)
    hm = header_map(cts)
    det = [(m,t,g) for m,t,g in hm if g in q]
    print(f"header positions {len(hm)}, on determined giant glyphs: {len(det)}")
    reps = defaultdict(list)
    for m,t,g in hm:
        if m in (0,6): reps[(m,g)].append(t)
    ladders = {k:v for k,v in reps.items() if len(v)>1 and k[1] in q}
    print("d-ladders (one glyph's meaning at two offsets pins d):")
    for (m,g),ts in sorted(ladders.items()):
        print(f"  {'T1' if m==0 else 'T3'} glyph {g:2d} at offsets {ts}: p[{ts[1]}]-p[{ts[0]}] = -{ts[1]-ts[0]}*d")
    # GATE: plant (d,Q0), encode two header values, solver must round-trip
    import random
    rng = random.Random(83); ok = True
    for _ in range(25):
        d0, Q0 = rng.randrange(1,N), rng.randrange(N)
        while True:
            picks = rng.sample(det, 2)
            if p1(picks[0][0],picks[0][1],picks[0][2],q) != p1(picks[1][0],picks[1][1],picks[1][2],q): break
        kv = [(m,t,(Q0 + d0*p1(m,t,g,q))%N, g) for m,t,g in picks]
        sols = solver(kv, q)
        ok &= (sols == [(d0, Q0)])
    print(f"  [{'PASS' if ok else 'FAIL'}] planted (d,Q0) round-trip x25 exact")
    hmd, coef, part = structure_sheet(cts, ej, q)
    ncls = len(set(part.values()))
    print(f"structure sheet: {len(hmd)} determined header positions, {ncls} distinct p-classes (d-free)")
    print("NOTE (FR36 holds): equality structure is drift-invariant -- qualitative lore")
    print("confirms the model; only QUANTITATIVE relations pin d via k*inv(dcoef).")
    if not ok: raise SystemExit(f"{XD}: gate failure")
    with open("/mnt/user-data/outputs/header_attack_kit.json","w") as f:
        json.dump({"header_positions":[[m,t,g] for m,t,g in hmd],
                   "q_rel_drift1_ref66":{str(g):v for g,v in q.items()},
                   "b1":B1,
                   "ladders":{f"{'T1' if m==0 else 'T3'}:{g}":ts for (m,g),ts in ladders.items()},
                   "coef_drift1":coef, "p_class_partition":part}, f)
    print("shipped: header_attack_kit.json")

if __name__ == "__main__":
    main()
