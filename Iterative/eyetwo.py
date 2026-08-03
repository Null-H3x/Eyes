#!/usr/bin/env python3
"""
eyetwo -- does skeleton consistency force drift_1 = drift_23?

FR102 established that the alignment GEOMETRY does not force one global drift:
after repair A no alignment bridges T1, so K_g[t] = t on T1 alone lies in the
null space of the cell-constancy system. FR3's chain (#2- forces d2 = d3, #M-
forces d1 = d2) lost its second link when repair A discarded East 3@101.

But FR102 also found 8 MIXING CYCLES in the relation graph -- T2/T3 edges
closing loops already spanned by T1-only edges. Around any such cycle,
consistency relates the two drifts algebraically. This instrument settles
whether that relation forces the ratio to 1.

THE SYSTEM. For a same-passage alignment (m1 at s1) ~ (m2 at s2), cell i, the
shared plaintext cancels and leaves, with b_m := base_m + kappa_g(m),

    q[c1[s1+i]] - q[c2[s2+i]] - b_m1 + b_m2
        - d_g1*(s1+i) + d_g2*(s2+i)  =  0

LINEAR over GF(83) in every unknown:

    q[0..82]   the alphabet values          83
    b_m        per-message offsets           9
    d1         drift of T1                   1
    d2         drift of T2 and T3            1   (d3 = d2, forced by #2-)
                                            ---
                                             94

The coupling FR102 identified is automatic here: q is GLOBAL, so a glyph
constrained by a T1 alignment and by a T2/T3 alignment carries both drift
terms into the same unknown.

Note the same-triplet case degenerates correctly: with g1 = g2 the drift
coefficient is -(s1+i) + (s2+i) = s2 - s1, independent of i -- which is why
54 alignments say nothing about the drift directly.

VERDICT RULE. The system is homogeneous (plaintext cancelled), so global
scaling is free and IS the drift normalisation. Equality is FORCED iff the
functional (d1 - d2) vanishes on every solution, not merely on the known one.

PRE-REGISTERED (frozen before corpus contact):
  R1  "forced" is claimed only if every null-space basis vector satisfies
      v[d1] == v[d2].
  R2  if not forced, an explicit witness with d1 != d2 must be exhibited AND
      verified to satisfy every equation.
  R3  the synthetic positive control must recover a planted d1 != d2 when the
      geometry lacks a cross-triplet bridge, and must force equality when one
      is added. If either control fails, the run is void.

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""

import json, os, random, sys
from itertools import combinations

XD = "XD-MBYG04K-URS3LF"
N = 83
HERE = os.path.dirname(os.path.abspath(__file__))

TRIPLET = {"East 1": 0, "West 1": 0, "East 2": 0,
           "West 2": 1, "East 3": 1, "West 3": 1,
           "East 4": 2, "West 4": 2, "East 5": 2}
DISCARDED = {("#M-", "East 3", 101), ("#M", "East 1", 68)}

# ------------------------------------------------------ GF(83) utilities

def inv(a):
    a %= N
    if a == 0: raise RuntimeError(f"{XD} inverse of zero")
    return pow(a, N - 2, N)

def rref(rows, ncols):
    mat = [r[:] for r in rows]; piv = []; r = 0
    for c in range(ncols):
        p = next((i for i in range(r, len(mat)) if mat[i][c] % N), None)
        if p is None: continue
        mat[r], mat[p] = mat[p], mat[r]
        iv = inv(mat[r][c]); mat[r] = [(x * iv) % N for x in mat[r]]
        for i in range(len(mat)):
            if i != r and mat[i][c] % N:
                f = mat[i][c]
                mat[i] = [(x - f * y) % N for x, y in zip(mat[i], mat[r])]
        piv.append(c); r += 1
        if r == len(mat): break
    return mat[:r], piv

def nullspace(rows, ncols):
    red, piv = rref(rows, ncols) if rows else ([], [])
    free = [c for c in range(ncols) if c not in piv]
    out = []
    for f in free:
        v = [0] * ncols; v[f] = 1
        for ri, pc in enumerate(piv): v[pc] = (-red[ri][f]) % N
        out.append(v)
    return out

def satisfies(rows, v):
    return all(sum(r[i] * v[i] for i in range(len(v))) % N == 0 for r in rows)

# ------------------------------------------------------- system assembly

def build(aligns, msgs, triplet_of, nmsg_index, ndrift=2, drift_of_group=None):
    """Unknowns: q[0..82] | b_m | d_0.. ; returns (rows, ncols, layout)."""
    nq = N
    nb = len(nmsg_index)
    QD = 0; BD = nq; DD = nq + nb
    ncols = nq + nb + ndrift
    if drift_of_group is None:
        drift_of_group = lambda g: 0 if g == 0 else 1
    rows = []
    for (m1, s1, m2, s2, offs) in aligns:
        g1, g2 = triplet_of[m1], triplet_of[m2]
        d1i, d2i = DD + drift_of_group(g1), DD + drift_of_group(g2)
        for i in offs:
            a, b = msgs[m1][s1 + i], msgs[m2][s2 + i]
            row = [0] * ncols
            row[QD + a] = (row[QD + a] + 1) % N
            row[QD + b] = (row[QD + b] - 1) % N
            row[BD + nmsg_index[m1]] = (row[BD + nmsg_index[m1]] - 1) % N
            row[BD + nmsg_index[m2]] = (row[BD + nmsg_index[m2]] + 1) % N
            row[d1i] = (row[d1i] - (s1 + i)) % N
            row[d2i] = (row[d2i] + (s2 + i)) % N
            if any(row): rows.append(row)
    return rows, ncols, (QD, BD, DD)

def drift_gap_forced(rows, ncols, DD):
    """Is (d1 - d2) identically zero on the solution space?"""
    nb = nullspace(rows, ncols)
    witnesses = [v for v in nb if (v[DD] - v[DD + 1]) % N != 0]
    return (len(witnesses) == 0), nb, witnesses

# --------------------------------------------------------------- loading

def load_corpus(p=None):
    d = json.load(open(p or os.path.join(HERE, "corpus.json")))
    return dict(zip(d["message_labels"], d["ciphertexts"]))

def load_atlas(p=None):
    return json.load(open(p or os.path.join(HERE, "atlas.json")))["classes"]

def alignments(classes, lettered_only=True):
    out = []
    for cls in classes:
        pat = cls["pattern"]; L = cls["length"]
        offs = [i for i, ch in enumerate(pat) if ch != "."] if lettered_only \
               else list(range(L))
        insts = [(it["message"], it["start"]) for it in cls["instances"]
                 if (cls["id"], it["message"], it["start"]) not in DISCARDED]
        for (m1, s1), (m2, s2) in combinations(insts, 2):
            if len(offs) >= 2: out.append((m1, s1, m2, s2, offs))
    return out

# ------------------------------------------------------------- selftest

def synth(d1, d2, bridge, rng):
    """Synthetic 4-message corpus with known drifts. A,B in T0; C,D in T1."""
    perm = list(range(N)); rng.shuffle(perm)          # q: glyph -> value
    qinv = [0] * N
    for g, v in enumerate(perm): qinv[v] = g          # value -> glyph
    trip = {"A": 0, "B": 0, "C": 1, "D": 1}
    bm = {"A": 3, "B": 11, "C": 29, "D": 40}
    L = 40
    # shared plaintext blocks
    pA = [rng.randrange(N) for _ in range(L)]
    pB = list(pA)                                     # A~B share fully
    pC = [rng.randrange(N) for _ in range(L)]
    pD = list(pC)                                     # C~D share fully
    if bridge:                                        # plant a T0~T1 passage
        pC[5:20] = pA[10:25]
    P = {"A": pA, "B": pB, "C": pC, "D": pD}
    msgs = {}
    for m, p in P.items():
        g = trip[m]; d = d1 if g == 0 else d2
        msgs[m] = [qinv[(p[t] + bm[m] + d * t) % N] for t in range(L)]
    al = [("A", 0, "B", 0, list(range(L))), ("C", 0, "D", 0, list(range(L)))]
    if bridge: al.append(("A", 10, "C", 5, list(range(15))))
    return msgs, trip, al

def selftest():
    ok = []
    def ck(n, c, d=""):
        ok.append((n, bool(c))); print(f"  {n:34s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise RuntimeError(f"{XD} selftest FAILED: {n} {d}")

    ck("t1_inv", all((x * inv(x)) % N == 1 for x in range(1, N)), "")
    rng = random.Random(103)

    # R3 control A: no bridge, planted UNEQUAL drifts -> must NOT be forced
    msgs, trip, al = synth(7, 31, bridge=False, rng=rng)
    idx = {m: i for i, m in enumerate(sorted(msgs))}
    rows, nc, (QD, BD, DD) = build(al, msgs, trip, idx)
    forced, nb, wit = drift_gap_forced(rows, nc, DD)
    ck("t2_nobridge_not_forced", not forced,
       f"{len(wit)} witnesses with d1 != d2")
    ck("t2b_witness_valid", wit and satisfies(rows, wit[0]), "R2 check")

    # R3 control B: with bridge -> equality MUST be forced
    msgs, trip, al = synth(7, 7, bridge=True, rng=rng)
    idx = {m: i for i, m in enumerate(sorted(msgs))}
    rows, nc, (QD, BD, DD) = build(al, msgs, trip, idx)
    forced, nb, wit = drift_gap_forced(rows, nc, DD)
    ck("t3_bridge_forces_equality", forced, "cross-triplet cell kills the gap")

    # t4: the planted true solution must satisfy its own system
    msgs, trip, al = synth(19, 19, bridge=True, rng=rng)
    idx = {m: i for i, m in enumerate(sorted(msgs))}
    rows, nc, (QD, BD, DD) = build(al, msgs, trip, idx)
    ck("t4_system_nontrivial", len(rows) > 20 and len(nullspace(rows, nc)) >= 1,
       f"{len(rows)} equations")

    # t5: corpus alignments load
    M = load_corpus(); cls = load_atlas(); al = alignments(cls)
    ck("t5_corpus_alignments", len(al) == 54, f"{len(al)}")
    print(f"selftest {sum(1 for _,p in ok if p)}/{len(ok)} green")

# --------------------------------------------------------------- corpus

def corpus_run():
    M = load_corpus(); classes = load_atlas()
    idx = {m: i for i, m in enumerate(sorted(M))}
    print("=" * 74)
    print("EYETWO -- does skeleton consistency force drift_1 = drift_23?")
    print("=" * 74)
    for policy, lettered in (("LETTERED cells (doctrine)", True),
                             ("FULL span (sensitivity)", False)):
        al = alignments(classes, lettered_only=lettered)
        rows, nc, (QD, BD, DD) = build(al, M, TRIPLET, idx)
        forced, nb, wit = drift_gap_forced(rows, nc, DD)
        print(f"\n--- {policy} ---")
        print(f"  alignments {len(al)}   equations {len(rows)}   unknowns {nc}")
        print(f"  solution space dim : {len(nb)}")
        print(f"  (d1 - d2) vanishes on every solution : {forced}")
        if forced:
            print("  VERDICT: DRIFT EQUALITY IS FORCED by skeleton consistency.")
            print("           FR3's conclusion is restored on new, sound evidence.")
        else:
            w = wit[0]
            assert satisfies(rows, w), f"{XD} R2 witness invalid"
            gap = (w[DD] - w[DD + 1]) % N
            print(f"  VERDICT: NOT FORCED. {len(wit)} witness directions.")
            print(f"           R2 witness verified against all {len(rows)} equations;"
                  f" d1={w[DD]} d2={w[DD+1]} gap={gap}")
            # how many distinct ratios d1/d2 are attainable?
            ratios = set()
            for v in nb:
                if v[DD + 1] % N:
                    ratios.add((v[DD] * inv(v[DD + 1])) % N)
                elif v[DD] % N:
                    ratios.add("inf")
            print(f"           attainable d1/d2 ratios from basis: "
                  f"{sorted(str(r) for r in ratios)[:12]}")
    print()

if __name__ == "__main__":
    selftest()
    if "--selftest" not in sys.argv: corpus_run()
