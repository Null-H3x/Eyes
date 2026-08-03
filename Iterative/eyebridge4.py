#!/usr/bin/env python3
"""eyebridge4 -- FR74. Can any message-base group be merged from inside the corpus?

XD-MBYG04K-URS3LF prefix on all exceptions.

FR73: the seven forced base differences leave FOUR message groups and three free
base parameters (19.13 bits). Any relation linking two groups removes one.

For a shared passage between messages m1, m2 at shift D, every cell whose two
glyphs lie in ONE known component must agree on

    w = (Delta_c2 - Delta_c1 - D) mod 83   =   (base_2 - base_1) / drift

which is drift-free. A run of agreeing cells at one shift is a candidate bridge.
"""
import json, random, collections, statistics

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
    for g, d in C.items():
        DELTA[g] = d; COMPOF[g] = i

LAB = ['East 1','West 1','East 2','West 2','East 3','West 3','East 4','West 4','East 5']
GROUP = {'East 1':1,'West 1':1,'East 2':1,'West 2':2,'East 3':3,'West 3':3,
         'East 4':4,'West 4':4,'East 5':4}


def cells(m1, m2, D):
    """(w) for each informative cell: both glyphs known, same component,
    and DIFFERENT glyphs (identical glyphs give w trivially -- FR31's filter)."""
    out = []
    for t in range(len(m1)):
        u = t + D
        if not (0 <= u < len(m2)):
            continue
        a, b = m1[t], m2[u]
        if a not in COMPOF or b not in COMPOF:
            continue
        if COMPOF[a] != COMPOF[b] or a == b:
            continue
        out.append((DELTA[b] - DELTA[a] - D) % N)
    return out


def best_shift(m1, m2, minagree=4):
    """largest number of cells agreeing on one w, over all shifts"""
    best = (0, None, None)
    for D in range(-(len(m1) - 1), len(m2)):
        w = cells(m1, m2, D)
        if len(w) < minagree:
            continue
        c = collections.Counter(w)
        k, n = c.most_common(1)[0]
        if n > best[0]:
            best = (n, D, k)
    return best


def selftest():
    rng = random.Random(74); res = []
    def ck(nm, c, d=""):
        res.append((nm, bool(c), d))
        if not c: raise XD("SELFTEST FAIL: %s %s" % (nm, d))

    gl = sorted(DELTA)
    # S1 -- PLANT a shared passage between two synthetic messages
    L = 120; D0 = 7; W0 = 31
    m1 = [rng.choice(gl) for _ in range(L)]
    m2 = [rng.choice(gl) for _ in range(L)]
    bycd = {}
    for g in gl:
        bycd[(COMPOF[g], DELTA[g])] = g
    # place BOTH ends of each cell: pick a pair (a,b) in one component whose
    # Delta difference is exactly w + D, so the cell is informative by construction
    pairs = []
    for g in gl:
        for h in gl:
            if g != h and COMPOF[g] == COMPOF[h] and (DELTA[h] - DELTA[g]) % N == (W0 + D0) % N:
                pairs.append((g, h))
    planted = 0
    for t in range(30, 60):
        u = t + D0
        if not (0 <= u < L) or not pairs: continue
        a, b = rng.choice(pairs)
        m1[t] = a; m2[u] = b; planted += 1
    ck("S1a plant produced cells", planted > 12, "planted=%d" % planted)
    n, D, w = best_shift(m1, m2)
    ck("S1 planted bridge recovered", D == D0 and w == W0 and n >= 12,
       "found n=%d D=%s w=%s" % (n, D, w))

    # S2 -- NEGATIVE CONTROL: random pair yields only chance agreement
    peak = []
    for _ in range(20):
        a = [rng.choice(gl) for _ in range(L)]
        b = [rng.choice(gl) for _ in range(L)]
        peak.append(best_shift(a, b)[0])
    # calibration, not a threshold: chance agreement is higher than intuition
    ck("S2 null calibrated and bounded", max(peak) <= 15,
       "random-pair peak mean %.1f max %d over 20 pairs" % (statistics.mean(peak), max(peak)))
    ck("S3 plant clears the null comfortably", n > max(peak),
       "plant %d vs null max %d" % (n, max(peak)))
    return res, statistics.mean(peak), max(peak)


if __name__ == "__main__":
    print("=== eyebridge4 selftests ===")
    r, mu, mx = selftest()
    for nm, ok, d in r:
        print("  %-40s %s  %s" % (nm, "PASS" if ok else "FAIL", d))
    print("  random-pair peak: mean %.1f, max %d" % (mu, mx))
    print("ALL GREEN")
