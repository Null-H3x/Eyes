#!/usr/bin/env python3
"""eyeorder -- FR62. Structured (non-algebraic) alphabet orderings.

XD-MBYG04K-URS3LF prefix on all exceptions.

FR59 left "irreducible three-feature construction" open and called it probably
untestable. That was too pessimistic: FR61's filter has selectivity ~83^-378, so
bulk hypothesis trawling carries no multiple-comparison cost. This cycle
generates structured orderings from every source available and runs all of them.

NOTE (proved below, gate S2): the filter is INVARIANT under affine
post-composition -- if q passes with drift d then a*q+b passes with drift a*d.
So only affine PRE-composition on glyph labels needs sweeping.
"""
import os, re, json
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
INV = [0] * N
for x in range(1, N): INV[x] = pow(x, N - 2, N)
REL = []
for C in COMPS:
    for a, b in combinations(sorted(C), 2):
        d = (C[b] - C[a]) % N
        if d: REL.append((a, b, d))

def skeleton_ok(q):
    a, b, d = REL[0]
    drift = ((q[b] - q[a]) % N) * INV[d] % N
    if drift == 0: return False
    for a, b, d in REL:
        if (q[b] - q[a]) % N != drift * d % N: return False
    return True

def invert(p):
    o = [0] * N
    for i, v in enumerate(p): o[v] = i
    return o

def digs(g): return (g // 25, (g // 5) % 5, g % 5)

# --------------------------------------------------------- base orderings
def base_orderings():
    """(name, permutation) pairs -- structured, non-PRNG candidates"""
    out = []
    ident = list(range(N))
    out.append(("identity", ident))
    out.append(("reverse", ident[::-1]))

    # base-5 digit manipulations (structure-preserving but non-affine)
    out.append(("digit-reverse", sorted(range(N), key=lambda g: digs(g)[::-1])))
    out.append(("digit-sum", sorted(range(N), key=lambda g: (sum(digs(g)), g))))
    out.append(("digit-prod", sorted(range(N), key=lambda g: (digs(g)[0]*digs(g)[1]*digs(g)[2], g))))
    out.append(("digit-max", sorted(range(N), key=lambda g: (max(digs(g)), g))))
    out.append(("digit-min", sorted(range(N), key=lambda g: (min(digs(g)), g))))
    out.append(("digit-sort-asc", sorted(range(N), key=lambda g: (tuple(sorted(digs(g))), g))))

    # base-5 reflected Gray code
    def gray5(g):
        d = list(digs(g)); o = []; shift = 0
        for x in d:
            o.append((x + shift) % 5); shift += 5 - o[-1]
        return tuple(o)
    out.append(("gray5", sorted(range(N), key=lambda g: (gray5(g), g))))

    # bit-reversal (7-bit)
    def brev(g):
        r = 0
        for i in range(7):
            r = (r << 1) | ((g >> i) & 1)
        return r
    out.append(("bit-reverse", sorted(range(N), key=lambda g: (brev(g), g))))

    # quadratic residues first
    qr = {(x * x) % N for x in range(1, N)}
    out.append(("quad-residues", sorted(range(N), key=lambda g: (0 if g in qr else 1, g))))

    # DISCRETE EXPONENTIATION -- g -> a^g mod 83. Not affine, not a power map;
    # a genuinely distinct algebraic structure FR28/FR58 did not cover.
    for a in (2, 3, 5, 6, 8, 10, 12, 14, 15, 18, 20, 22, 24, 26, 28, 30):
        seen = set(); p = [0] * N; ok = True
        for g in range(1, N):
            v = pow(a, g, N)
            if v in seen: ok = False; break
            seen.add(v); p[g] = v
        if ok and len(seen) == N - 1:
            out.append(("dexp-base%d" % a, p))

    # multiplicative inverse ordering
    p = [0] * N
    for g in range(1, N): p[g] = INV[g]
    out.append(("mult-inverse", p))

    return out

def game_orderings(root):
    """orderings harvested from the Noita data folder, truncated to 83"""
    out = []
    if not root or not os.path.isdir(root): return out
    cand = [
        ("materials.xml", "materials.xml", r'name="([^"]+)"'),
        ("gun_actions-dir", "ui_gfx/gun_actions", None),
        ("perk_icons-dir", "ui_gfx/perk_icons", None),
        ("perks-dir", "items_gfx/perks", None),
        ("wands-dir", "items_gfx/wands", None),
        ("material_icons", "generated/material_icons", None),
        ("sprite_uv_maps", "generated/sprite_uv_maps", None),
    ]
    for nm, rel, pat in cand:
        p = os.path.join(root, rel)
        items = []
        if pat and os.path.isfile(p):
            items = re.findall(pat, open(p, encoding='utf-8', errors='ignore').read())
        elif os.path.isdir(p):
            items = sorted(os.listdir(p))
        if len(items) < N: continue
        # three truncations: first 83, last 83, and alphabetical first 83
        for tag, seq in (("head", items[:N]), ("tail", items[-N:]),
                         ("alpha", sorted(items)[:N])):
            order = sorted(range(N), key=lambda i: seq[i])
            out.append(("%s-%s" % (nm, tag), order))
    return out

def affine_variants(p):
    """q[g] = p[(a*g+b) mod 83] -- affine PRE-composition on glyph labels"""
    for a in range(1, N):
        for b in range(N):
            yield [p[(a * g + b) % N] for g in range(N)]

# ------------------------------------------------------------- selftests
def selftest():
    out = []
    def ck(nm, c, d=""):
        out.append((nm, bool(c), d))
        if not c: raise XD("SELFTEST FAIL: %s %s" % (nm, d))

    ck("S1 relation count", len(REL) == 379, "n=%d" % len(REL))

    # S2 -- prove affine POST-composition invariance (so we need not sweep it)
    q = [0] * N
    for C in COMPS:
        for g in C: q[g] = (11 + 37 * C[g]) % N
    ck("S2 base alphabet accepted", skeleton_ok(q))
    inv_ok = all(skeleton_ok([(a * v + b) % N for v in q])
                 for a in (1, 2, 7, 41, 82) for b in (0, 5, 60))
    ck("S2b affine POST-composition invariance holds", inv_ok)

    # S3 -- every generated ordering is a genuine permutation
    allo = base_orderings()
    ck("S3 all base orderings are permutations",
       all(sorted(p) == list(range(N)) for _, p in allo), "n=%d" % len(allo))

    # S4 -- NEGATIVE CONTROL: none of a large affine family of a random-ish
    # ordering passes (guards against a filter that accepts too much)
    import random
    rng = random.Random(62)
    r = list(range(N)); rng.shuffle(r)
    hits = sum(1 for v in affine_variants(r) if skeleton_ok(v))
    ck("S4 random ordering: 0 hits over 6,806 affine variants", hits == 0,
       "hits=%d" % hits)

    # S5 -- PLANT: an affine pre-composition of a valid q must be FOUND
    tgt = [q[(7 * g + 19) % N] for g in range(N)]
    found = any(skeleton_ok(v) for v in affine_variants(tgt))
    ck("S5 planted affine pre-composition recovered", found)
    return out

if __name__ == "__main__":
    print("=== eyeorder selftests (green before sweeping) ===")
    for nm, ok, d in selftest():
        print("  %-56s %s  %s" % (nm, "PASS" if ok else "FAIL", d))
    print("ALL GREEN")
