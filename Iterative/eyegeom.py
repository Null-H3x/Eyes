#!/usr/bin/env python3
"""eyegeom -- FR57. Re-audit FR39's small-alphabet exclusion.
XD-MBYG04K-URS3LF prefix on all exceptions."""
import json, random, statistics, collections

class XD(Exception):
    def __init__(s, m): super().__init__("XD-MBYG04K-URS3LF " + m)

N = 83
C1 = {0:0,1:3,5:7,6:34,7:36,9:58,10:55,17:29,20:39,27:1,30:66,34:61,41:69,
      45:60,47:35,48:82,50:8,57:33,62:28,63:31,64:81,68:65,71:38,79:57,81:54}
C2 = {13:0,19:53,23:4,25:82,44:1,46:31,49:52,60:81,66:55,72:35,78:25}
C3 = {16:0,21:58,26:1,40:57,42:35,67:31,73:2}
C4 = {4:0,35:55,37:57}
DELTA, COMPOF = {}, {}
for i, C in enumerate([C1, C2, C3, C4]):
    for g, dv in C.items(): DELTA[g] = dv; COMPOF[g] = i
LAB = ['East 1','West 1','East 2','West 2','East 3','West 3','East 4','West 4','East 5']
IDX = {l:i for i,l in enumerate(LAB)}
PAIRS = [('East 1','East 2',77), ('West 1','East 2',77), ('East 4','West 4',54),
         ('West 4','East 5',29), ('East 3','West 3',54)]   # near-dups excluded per FR39

def blocks(m):
    b = {}
    for t,g in enumerate(m):
        if g in COMPOF: b.setdefault(COMPOF[g], []).append(t)
    return b

def coincidences(msgs, pairs):
    hit = tot = 0
    for a,b,w in pairs:
        m1,m2 = msgs[IDX[a]], msgs[IDX[b]]
        b1,b2 = blocks(m1), blocks(m2)
        for c in b1:
            if c not in b2: continue
            v1 = [(DELTA[m1[t]]-t) % N for t in b1[c]]
            v2 = [(DELTA[m2[t]]-t) % N for t in b2[c]]
            tot += len(v1)*len(v2); cnt = collections.Counter(v2)
            for x in v1: hit += cnt[(x-w) % N]
    return hit, tot

def binned(msgs, lo, hi):
    h = t = 0
    for m in msgs:
        for i in range(len(m)):
            for d in range(lo, hi+1):
                if i+d >= len(m): break
                a,b = m[i], m[i+d]
                if a in COMPOF and b in COMPOF and COMPOF[a]==COMPOF[b]:
                    t += 1
                    if (DELTA[b]-DELTA[a]) % N == d % N: h += 1
    return h, t

def diffs(msgs):
    """plaintext first-differences, known up to the drift scalar:
       p[t+1]-p[t] = drift * (Delta(g2)-Delta(g1)-1)"""
    out = []
    for m in msgs:
        for t in range(len(m)-1):
            a,b = m[t], m[t+1]
            if a in COMPOF and b in COMPOF and COMPOF[a]==COMPOF[b]:
                out.append((DELTA[b]-DELTA[a]-1) % N)
    return out

def null_geometry(msgs, rng):
    out = []
    for m in msgs:
        m = list(m)
        for c, idxs in blocks(m).items():
            gl = [m[t] for t in idxs]; rng.shuffle(gl)
            for t,g in zip(idxs, gl): m[t] = g
        out.append(m)
    return out

def z_of(obs, dr):
    mu = statistics.mean(dr); sd = statistics.pstdev(dr)
    if sd == 0: raise XD("degenerate null")
    return (obs-mu)/sd, mu, sd

def selftest():
    rng = random.Random(57); res = []
    def ck(nm, cond, det=""):
        res.append((nm, bool(cond), det))
        if not cond: raise XD("SELFTEST FAIL: %s %s" % (nm, det))
    lens = [99,103,118,102,137,124,119,120,114]
    glyphs = list(DELTA)
    byc = {}
    for g in glyphs: byc.setdefault(COMPOF[g], []).append(g)

    syn = [[rng.choice(glyphs) for _ in range(L)] for L in lens]
    p0 = sorted(DELTA[g] for m in syn for g in m)
    sh = null_geometry(syn, rng)
    ck("S1 Delta multiset preserved", p0 == sorted(DELTA[g] for m in sh for g in m))
    ck("S2 component membership preserved",
       all(COMPOF[a]==COMPOF[b] for x,y in zip(syn,sh) for a,b in zip(x,y)))

    S_ = set(rng.sample(range(N), 30))
    shifts = {'East 2':0,'East 1':(-77)%N,'West 1':(-77)%N,'West 4':0,
              'East 4':(-54)%N,'East 5':29,'West 3':0,'East 3':(-54)%N,'West 2':0}
    plant = []
    for mi,L in enumerate(lens):
        sm = shifts[LAB[mi]]; row=[]
        for t in range(L):
            c = rng.choice(list(byc))
            good = [g for g in byc[c] if (DELTA[g]-t+sm) % N in S_]
            row.append(rng.choice(good) if good else rng.choice(byc[c]))
        plant.append(row)
    hp,_ = coincidences(plant, PAIRS)
    drp = [coincidences(null_geometry(plant, rng), PAIRS)[0] for _ in range(200)]
    zp,mup,_ = z_of(hp, drp)
    ck("S3 planted small alphabet detected", zp > 3.0, "z=%+.2f" % zp)

    zl = []
    for sd_ in range(5):
        r2 = random.Random(9000+sd_)
        sy = [[r2.choice(glyphs) for _ in range(L)] for L in lens]
        hh,_ = coincidences(sy, PAIRS)
        dd = [coincidences(null_geometry(sy, r2), PAIRS)[0] for _ in range(150)]
        zl.append(z_of(hh, dd)[0])
    ck("S4 flat synthetic quiet (mean over 5 corpora)",
       abs(statistics.mean(zl)) < 1.5, "mean z=%+.2f" % statistics.mean(zl))

    # S5/S6 -- WHY FR42's lesson does not propagate back to FR39
    dep = [[rng.choice(byc[0]) for _ in range(L)] for L in lens]
    hd,td = coincidences(dep, PAIRS)
    md = statistics.mean([coincidences(null_geometry(dep,rng),PAIRS)[0] for _ in range(200)])
    agg = abs(md-td/N)/(td/N)
    ck("S5 AGGREGATE channel: geometry null == flat baseline", agg < 0.05,
       "geom=%.1f flat=%.1f (%+.1f%%)" % (md, td/N, 100*(md-td/N)/(td/N)))
    hb,tb = binned(dep,9,17)
    mb = statistics.mean([binned(null_geometry(dep,rng),9,17)[0] for _ in range(200)])
    bg = abs(mb-tb/N)/(tb/N)
    ck("S6 DISTANCE-BINNED channel: geometry null DIVERGES from flat", bg > 3*agg,
       "binned %+.0f%% vs aggregate %+.1f%%" % (100*(mb-tb/N)/(tb/N), 100*agg))
    return res

if __name__ == "__main__":
    print("=== eyegeom selftests (green before corpus contact) ===")
    for nm,ok,det in selftest():
        print("  %-52s %s  %s" % (nm, "PASS" if ok else "FAIL", det))
    print("ALL GREEN")
