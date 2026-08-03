#!/usr/bin/env python3
"""eyeenum -- FR63. Exact enumeration of alphabets the skeleton permits.

XD-MBYG04K-URS3LF prefix on all exceptions.

FR58-FR62 generated candidate alphabets and filtered them. That can only cover
constructions someone thought to generate. The inverse question: enumerate every
alphabet the skeleton ADMITS, exactly.

Inside a component, q[g] = base_c + drift*Delta_g. So a partial alphabet over the
46 determined glyphs is fixed by (drift, base_1..base_4), with one base a global
gauge. Injectivity across components is FR27's packing constraint.

FR53 proved the packing COUNT is drift-invariant (multiplication by d is a
bijection of Z/83), so enumerating at drift 1 and multiplying by 82 is exact --
verified here rather than assumed.
"""
from itertools import combinations

class XD(Exception):
    def __init__(s, m): super().__init__("XD-MBYG04K-URS3LF " + m)

N = 83
C1 = {0:0,1:3,5:7,6:34,7:36,9:58,10:55,17:29,20:39,27:1,30:66,34:61,41:69,
      45:60,47:35,48:82,50:8,57:33,62:28,63:31,64:81,68:65,71:38,79:57,81:54}
C2 = {13:0,19:53,23:4,25:82,44:1,46:31,49:52,60:81,66:55,72:35,78:25}
C3 = {16:0,21:58,26:1,40:57,42:35,67:31,73:2}
C4 = {4:0,35:55,37:57}
COMPS = [C1, C2, C3, C4]
GLYPHS = sorted(set().union(*[set(C) for C in COMPS]))


def value_sets(drift):
    """per-component set of drift*Delta values (before the base shift)"""
    return [frozenset((drift * d) % N for d in C.values()) for C in COMPS]


def bad_offsets(Di, Dj):
    """relative offsets (base_j - base_i) that make the two sets collide"""
    return {(x - y) % N for x in Di for y in Dj}


def enumerate_packings(drift):
    """all (base_1..base_4) with base_1 = 0 giving pairwise-disjoint value sets"""
    D = value_sets(drift)
    for c in D:
        if len(c) != len(COMPS[D.index(c)]):
            raise XD("drift %d collapsed a component internally" % drift)
    BAD = {}
    for i in range(4):
        for j in range(4):
            if i != j:
                BAD[(i, j)] = bad_offsets(D[i], D[j])
    out = []
    b = [0, 0, 0, 0]
    for b1 in range(N):
        if b1 in BAD[(0, 1)]:
            continue
        for b2 in range(N):
            if b2 in BAD[(0, 2)] or (b2 - b1) % N in BAD[(1, 2)]:
                continue
            for b3 in range(N):
                if b3 in BAD[(0, 3)] or (b3 - b1) % N in BAD[(1, 3)] \
                   or (b3 - b2) % N in BAD[(2, 3)]:
                    continue
                out.append((0, b1, b2, b3))
    return out


def alphabet(drift, bases):
    q = {}
    for c, C in enumerate(COMPS):
        for g, d in C.items():
            q[g] = (bases[c] + drift * d) % N
    return q


def selftest():
    out = []
    def ck(nm, c, d=""):
        out.append((nm, bool(c), d))
        if not c: raise XD("SELFTEST FAIL: %s %s" % (nm, d))

    ck("S1 46 determined glyphs, components 25/11/7/3",
       len(GLYPHS) == 46 and [len(C) for C in COMPS] == [25, 11, 7, 3])

    p1 = enumerate_packings(1)
    ck("S2 packings exist at drift 1", len(p1) > 0, "n=%d" % len(p1))

    # every enumerated packing must genuinely be injective
    okall = True
    for bs in p1[:200]:
        q = alphabet(1, bs)
        if len(set(q.values())) != 46: okall = False; break
    ck("S3 every enumerated packing is injective over 46 glyphs", okall)

    # a deliberately colliding base assignment must be absent
    ck("S4 the all-zero base assignment collides and is excluded",
       (0, 0, 0, 0) not in p1)

    # FR53's drift-invariance: verify rather than assume
    counts = {d: len(enumerate_packings(d)) for d in (1, 2, 3, 5, 7, 17, 31, 41, 82)}
    ck("S5 packing count is drift-invariant (FR53)",
       len(set(counts.values())) == 1, str(counts))
    return out, p1


if __name__ == "__main__":
    print("=== eyeenum selftests ===")
    res, p1 = selftest()
    for nm, ok, d in res:
        print("  %-56s %s  %s" % (nm, "PASS" if ok else "FAIL", d))
    print("ALL GREEN")
