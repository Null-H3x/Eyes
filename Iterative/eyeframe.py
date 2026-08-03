#!/usr/bin/env python3
"""eyeframe -- FR58. Re-run FR28's algebraic battery over every glyph-labeling
frame the corpus permits.

XD-MBYG04K-URS3LF prefix on all exceptions.

FR28 excluded affine / power / keyword-mixed alphabets, but tested them in the
CURRENT base-5 trigram frame. The frame is a community reading of glyph pictures
(3 visual features x 5 states); which feature is the most significant digit and
which state means 0 are choices, not facts.

The frame group is S5 wr S3, order 6*120^3 = 10,368,000. But the corpus uses
exactly the labels {0..82} with no gaps, so an alternative frame can differ only
by a relabeling that STABILISES {0..82}. That stabiliser has order 432 and forces
the digit ordering to the identity.

All tests here are DRIFT-FREE. Within a component q[g2]-q[g1] = drift*(D2-D1).
  affine  q[g] = a*g+b   =>  (D2-D1)/(rho(g2)-rho(g1)) constant over all pairs
  power   q[g] = g^k     =>  (rho(g2)^k - rho(g1)^k)/(D2-D1) constant
"""
from itertools import permutations, combinations
import random

class XD(Exception):
    def __init__(s, m): super().__init__("XD-MBYG04K-URS3LF " + m)

N = 83
C1 = {0:0,1:3,5:7,6:34,7:36,9:58,10:55,17:29,20:39,27:1,30:66,34:61,41:69,
      45:60,47:35,48:82,50:8,57:33,62:28,63:31,64:81,68:65,71:38,79:57,81:54}
C2 = {13:0,19:53,23:4,25:82,44:1,46:31,49:52,60:81,66:55,72:35,78:25}
C3 = {16:0,21:58,26:1,40:57,42:35,67:31,73:2}
C4 = {4:0,35:55,37:57}
COMPS = [C1, C2, C3, C4]

INV = [0] * N
for x in range(1, N):
    INV[x] = pow(x, N - 2, N)


def digits(g): return (g // 25, (g // 5) % 5, g % 5)


def build_stabiliser():
    perms5 = list(permutations(range(5)))
    out = []
    for pi in permutations(range(3)):
        for ta in perms5:
            for tb in perms5:
                for tc in perms5:
                    m = [0] * N; ok = True
                    for g in range(N):
                        d = digits(g)
                        ng = 25 * ta[d[pi[0]]] + 5 * tb[d[pi[1]]] + tc[d[pi[2]]]
                        if ng > 82: ok = False; break
                        m[g] = ng
                    if ok: out.append(tuple(m))
    if not out:
        raise XD("empty stabiliser -- frame model is wrong")
    return out


def relations(comps):
    """(g1, g2, Ddiff) for every within-component pair"""
    rel = []
    for C in comps:
        for a, b in combinations(sorted(C), 2):
            rel.append((a, b, (C[b] - C[a]) % N))
    return rel


def affine_multipliers(rel, rho):
    """distinct values of (D2-D1)/(rho(g2)-rho(g1)); size 1 => affine fits"""
    s = set()
    for a, b, D in rel:
        den = (rho[b] - rho[a]) % N
        if den == 0:
            raise XD("degenerate relabeling: distinct glyphs collide")
        s.add((D * INV[den]) % N)
    return s


def power_fits(rel, rho):
    """exponents k for which q[g]=g^k is consistent (constant drift)"""
    hits = []
    for k in range(1, N - 1):
        s = set(); ok = True
        for a, b, D in rel:
            if D == 0: ok = False; break
            num = (pow(rho[b], k, N) - pow(rho[a], k, N)) % N
            s.add((num * INV[D]) % N)
            if len(s) > 1: ok = False; break
        if ok and len(s) == 1: hits.append(k)
    return hits


def ordered_tail(rel, rho):
    """keyword-mixed signature: relations with D == rho(g2)-rho(g1)"""
    return sum(1 for a, b, D in rel if D == (rho[b] - rho[a]) % N)


# ------------------------------------------------------------------ selftests
def selftest():
    rng = random.Random(58); res = []

    def ck(nm, cond, det=""):
        res.append((nm, bool(cond), det))
        if not cond: raise XD("SELFTEST FAIL: %s %s" % (nm, det))

    stab = build_stabiliser()
    ck("S1 stabiliser non-trivial and small", len(stab) == 432, "n=%d" % len(stab))
    ck("S2 identity is in the stabiliser", tuple(range(N)) in stab)
    ck("S3 every frame is a bijection on 0..82",
       all(len(set(m)) == N for m in stab))

    rel = relations(COMPS)
    ck("S4 relation count matches FR53 skeleton minus 2-glyph comps",
       len(rel) == 379, "n=%d" % len(rel))

    # S5 -- POSITIVE CONTROL: plant an affine alphabet in a KNOWN frame and
    # verify the sweep recovers exactly that frame with a single multiplier.
    rho0 = stab[rng.randrange(len(stab))]
    a0 = rng.randrange(1, N)
    planted = []
    for C in COMPS:
        base = rng.randrange(N)
        planted.append({g: (a0 * rho0[g] + base) % N for g in C})
    prel = relations(planted)
    hit = [i for i, m in enumerate(stab) if len(affine_multipliers(prel, m)) == 1]
    ck("S5 planted affine recovered", stab.index(rho0) in hit,
       "frames fitting=%d" % len(hit))

    # S6 -- NEGATIVE CONTROL: a random alphabet must fit NO frame
    rnd = []
    for C in COMPS:
        rnd.append({g: rng.randrange(N) for g in C})
    rrel = relations(rnd)
    bad = [i for i, m in enumerate(stab) if len(affine_multipliers(rrel, m)) == 1]
    ck("S6 random alphabet fits no frame", len(bad) == 0, "fits=%d" % len(bad))

    # S7 -- power detector recovers a planted power alphabet (identity frame)
    k0 = 5
    pw = []
    for C in COMPS:
        pw.append({g: pow(g, k0, N) for g in C})
    # power test needs q differences to be exact, so build relations from q
    prel2 = []
    for C in pw:
        for a, b in combinations(sorted(C), 2):
            prel2.append((a, b, (C[b] - C[a]) % N))
    ck("S7 planted power alphabet recovered",
       k0 in power_fits(prel2, tuple(range(N))), "")
    return res, stab, rel


if __name__ == "__main__":
    print("=== eyeframe selftests (green before corpus contact) ===")
    r, stab, rel = selftest()
    for nm, ok, det in r:
        print("  %-52s %s  %s" % (nm, "PASS" if ok else "FAIL", det))
    print("ALL GREEN")
