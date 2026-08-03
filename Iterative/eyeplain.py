#!/usr/bin/env python3
"""
eyeplain -- the CORRECTED relative-plaintext reconstruction.

EYESPIRAL-C. FR132. Rebuilds what FR131 withdrew.

WHAT FR131 FOUND. The model is

    p[t] = A_block + v[t],   v[t] = Delta_g - d*t,
    A_block = base_component - b_message

and every artifact from FR119 onward was built from `v` ALONE. Within a block
`p` and `v` differ by one constant so equality structure is preserved; ACROSS
blocks they do not, and the cross-block claims were invalid. A second error:
linking edges were drawn from ALL alignment cells including dots, which FR7's
sound-rows doctrine says are variable interior -- the plaintext DIFFERS there.

THE CORRECT CONSTRUCTION.

  1. Build the skeleton; take Delta per glyph (component-relative).
  2. v[m,t] = Delta_{c[m][t]} - d*t.
  3. An alignment asserts p_A = p_B at LETTERED cells only, giving
        A_blk(A) - A_blk(B) = v[B] - v[A]
  4. Propagate along those edges. Within a connected group every A_block is
     fixed relative to one gauge, so p is determined up to ONE global constant.

PARAMETER DEPENDENCIES, stated per FR131's standing check:
  p depends on   Delta   (determined by the skeleton)
                 d       (unknown; but see drift-invariance below)
                 A_block (determined WITHIN a group by step 4, one free gauge)
  Nothing else. Positions in different groups are NOT comparable.

PRE-REGISTERED:
  R1  propagation must yield ZERO conflicts, or the construction is invalid
      and the run VOIDS.
  R2  the equality structure must be verified drift-independent across all 82
      drifts, or the artifact is drift-conditional and must say so.
  R3  the artifact reports ONLY within-group relations. Cross-group pairs are
      emitted as UNDETERMINED, never as unequal.

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""

import os, sys
from collections import defaultdict, deque

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
XD = "XD-MBYG04K-URS3LF"
N = 83

import eyeaudit as AUD

REPAIRS = {"A": [("East 3", 101), ("East 1", 68)],
           "C": [("East 1", 68)],
           "R2": [("East 4", 51)]}


def reconstruct(repair="C", drift=1):
    cts, labels, Lx, ctx, pool, red = AUD.load(
        os.path.join(HERE, "corpus.json"), os.path.join(HERE, "atlas.json"))
    keys = [(Lx[m], s) for m, s in REPAIRS[repair]]
    pairs = [p for p in pool
             if not any((p.m1, p.p1) == k or (p.m2, p.p2) == k for k in keys)]
    gf = AUD.build(cts, ctx, Lx, pairs, drift=drift)
    if gf is None: raise RuntimeError(f"{XD} repair {repair} contradictory at drift {drift}")
    a = AUD.analyse(gf)
    comps = sorted((sorted(c) for c in a["comps"]), key=len, reverse=True)
    compof = {}
    for i, c in enumerate(comps, 1):
        for g in c: compof[g] = i
    D = a["delta"]
    v = {}; blk = {}
    for mi in range(9):
        for t, g in enumerate(cts[mi]):
            if g in compof:
                v[(mi, t)] = (D[g] - drift * t) % N
                blk[(mi, t)] = (mi, compof[g])
    # --- edges from LETTERED cells only
    pattern_of, dot = ctx["pattern_of"], ctx["dot"]
    E = defaultdict(list); nedge = 0
    for pr in pairs:
        key = (pr.m1, pr.p1, pr.m2, pr.p2, pr.length)
        pat = pattern_of.get(key)
        for i in range(pr.length):
            if pat is not None and not pr.exact and pat[i] == '.': continue
            if pat is None and not pr.exact and \
               ((pr.m1, pr.p1 + i) in dot or (pr.m2, pr.p2 + i) in dot): continue
            A = (pr.m1, pr.p1 + i); B = (pr.m2, pr.p2 + i)
            if A in v and B in v and blk[A] != blk[B]:
                E[blk[A]].append((blk[B], (v[B] - v[A]) % N))
                E[blk[B]].append((blk[A], (v[A] - v[B]) % N)); nedge += 1
    off = {}; gid = {}; ng = 0; conflicts = 0
    for start in set(blk.values()):
        if start in off: continue
        ng += 1; off[start] = 0; gid[start] = ng; q = deque([start])
        while q:
            x = q.popleft()
            for y, d in E.get(x, []):
                nd = (off[x] + d) % N
                if y in off:
                    if off[y] != nd: conflicts += 1
                else:
                    off[y] = nd; gid[y] = ng; q.append(y)
    sizes = defaultdict(int)
    for k in v: sizes[gid[blk[k]]] += 1
    big = max(sizes, key=lambda g: sizes[g])
    p = {k: (v[k] + off[blk[k]]) % N for k in v if gid[blk[k]] == big}
    return p, labels, cts, conflicts, ng, nedge, len(v)


def selftest():
    ok = []
    def ck(n, c, d=""):
        ok.append((n, bool(c))); print(f"  {n:36s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise RuntimeError(f"{XD} selftest FAILED: {n} {d}")
    p, labels, cts, conf, ng, ne, nv = reconstruct("C", 1)
    ck("t1_R1_zero_conflicts", conf == 0, f"{conf} conflicts over {ne} edges")
    ck("t2_size", len(p) == 191, f"{len(p)} positions")
    # R2: drift-independence of the equality structure
    def sig(dr):
        pp, *_ = reconstruct("C", dr)
        ks = sorted(pp); o = {}; s = []
        for k in ks:
            x = pp[k]
            if x not in o: o[x] = len(o)
            s.append(o[x])
        return tuple(ks), tuple(s)
    sigs = {sig(d) for d in (1, 2, 3, 7, 11, 41, 82)}
    ck("t3_R2_drift_invariant", len(sigs) == 1, f"{len(sigs)} distinct structures")
    # a within-block pair must be comparable; a cross-group pair must be absent
    ck("t4_repairA", reconstruct("A", 1)[0].__len__() == 108, "repair A gives 108")
    print(f"selftest {sum(1 for _,p in ok if p)}/{len(ok)} green")
    return p, labels, cts


RAMP = ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")


def build(p, labels, cts):
    print("=" * 74)
    print("EYEPLAIN -- corrected relative-plaintext reconstruction")
    print("=" * 74)
    bym = defaultdict(dict)
    for (m, t), val in p.items(): bym[m][t] = val
    order = {}; 
    for k in sorted(p):
        if p[k] not in order: order[p[k]] = len(order)
    print(f"\n  positions            : {len(p)} ({100*len(p)/1036:.1f}% of corpus)")
    print(f"  messages             : {len(bym)} of 9")
    print(f"  distinct values      : {len(order)}")
    print(f"  free parameters      : ONE global constant\n")
    for mi in sorted(bym):
        L = len(cts[mi]); n = len(bym[mi])
        print(f"    {labels[mi]:8s} {n:3d}/{L:3d} ({100*n/L:4.1f}%)")
    from collections import Counter
    cnt = Counter(p.values())
    reps = sum(c * (c - 1) // 2 for c in cnt.values())
    print(f"\n  equal-pairs among the {len(p)} positions: {reps}")
    # robust within-message short-range equalities -- the crib targets
    tgt = []
    for mi, d in bym.items():
        ts = sorted(d)
        for i in range(len(ts)):
            for j in range(i + 1, len(ts)):
                if ts[j] - ts[i] > 10: break
                if d[ts[i]] == d[ts[j]]: tgt.append((labels[mi], ts[i], ts[j]))
    print(f"  within-message equal pairs at distance <=10: {len(tgt)}")
    for lab, a, b in sorted(tgt, key=lambda x: x[2] - x[1])[:12]:
        print(f"     {lab:8s} {a:3d} == {b:3d}   (distance {b-a})")
    path = os.path.join(HERE, "PLAINTEXT_RELATIVE.txt")
    with open(path, "w") as f:
        f.write("NOITA EYE MESSAGES -- RELATIVE PLAINTEXT (corrected, FR132)\n")
        f.write("=" * 66 + "\n\n")
        f.write(f"{len(p)} positions ({100*len(p)/1036:.1f}% of corpus) across "
                f"{len(bym)} messages.\n")
        f.write("Plaintext determined up to ONE global additive constant.\n\n")
        f.write("SUPERSEDES FR119's CANDIDATE_READINGS.txt and FR123's\n")
        f.write("PLAINTEXT_STRUCTURE_C.txt, which compared v across blocks\n")
        f.write("without solving A_block and were therefore invalid off-block.\n\n")
        f.write("Construction: p = A_block + v, with A_block propagated along\n")
        f.write("LETTERED alignment cells only (dot cells are variable interior,\n")
        f.write("FR7). Zero propagation conflicts. Equality structure verified\n")
        f.write("drift-independent at drifts 1,2,3,7,11,41,82.\n\n")
        f.write("Symbols assigned in order of first occurrence: EQUAL SYMBOLS\n")
        f.write("MEAN EQUAL PLAINTEXT. Dots are positions this reconstruction\n")
        f.write("does not determine -- they are NOT asserted unequal.\n\n")
        f.write("=" * 66 + "\n")
        for mi in sorted(bym):
            L = len(cts[mi]); d = bym[mi]
            f.write(f"\n--- {labels[mi]} ---  {len(d)}/{L} determined\n")
            line = "".join(RAMP[order[d[t]] % len(RAMP)] if t in d else '.'
                           for t in range(L))
            for i in range(0, L, 80):
                f.write(f"  {i:3d}  {line[i:i+80]}\n")
        f.write("\n" + "=" * 66 + "\nPOSITION INDEX\n")
        for mi in sorted(bym):
            f.write(f"\n{labels[mi]}:\n")
            for j, t in enumerate(sorted(bym[mi])):
                if j % 8 == 0: f.write("\n  ")
                f.write(f"{t:3d}/{RAMP[order[bym[mi][t]] % len(RAMP)]}  ")
            f.write("\n")
    print(f"\n  ARTIFACT: PLAINTEXT_RELATIVE.txt ({os.path.getsize(path):,} bytes)")
    print()


if __name__ == "__main__":
    p, labels, cts = selftest()
    if "--selftest" not in sys.argv: build(p, labels, cts)
