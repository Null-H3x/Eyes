#!/usr/bin/env python3
"""
eyekey -- is the progressive keystream DERIVED or ASSUMED?

THE QUESTION (FR101 horizon item 1). The model is

    c[m][t] = C[ ( p[m][t] + base_m + K_g[t] ) mod 83 ]

with the tech ref (section 3.2, A2) taking K_g[t] = drift*t. A2 is marked
[MEASURED], and it is -- FR56 and FR91 tested for a PERIODIC component and
found none at any period 2..90, with z = +13.1 power. But "not periodic" is
not "linear". Aperiodic non-linear keystreams (polynomial, PRNG-driven,
autokey, arbitrary) were never in that alternative set.

THE STRUCTURAL TEST, which needs no statistics and no anchors. A certified
same-passage alignment between (m1 at s1) and (m2 at s2) over a set of cells
asserts, at every cell i,

    q[c1[s1+i]] - q[c2[s2+i]] = (base_m1 - base_m2) + (K_g1[s1+i] - K_g2[s2+i])

and the skeleton requires that quantity be CONSTANT across the alignment (this
is FR32's w, drift-free and forced for seven message pairs). Therefore

    K_g1[s1+i] - K_g2[s2+i] = const_a       for every cell i of alignment a

This is a homogeneous linear condition on K over GF(83), and it depends only on
the alignment GEOMETRY -- which triplets, which positions -- not on q, not on
the drift, not on the plaintext. So the space of keystreams consistent with the
corpus's own alignment evidence is computable exactly.

    If that space is exactly the linear family, LINEARITY IS DERIVED.
    If it is larger, linearity is an unforced choice and the extra freedom
    is precisely what the model has been assuming away.

Why it is load-bearing: FR30's one-parameter-family result, the entire drift
formalism, and "the skeleton is fixed by one scalar" all presuppose the linear
form. If K may bend, "the drift" is not even well defined as a single scalar.

THE LINEAR FAMILY in K-space is spanned by four vectors:
    L0: K_g[t] = t          for all g   (the drift direction)
    B1: K_g[t] = [g == 0]               (gauge: absorbed by base_m)
    B2: K_g[t] = [g == 1]               (gauge)
    B3: K_g[t] = [g == 2]               (gauge)
so dim 4, of which 3 are gauge and 1 is the physical drift.

Positions covered by no alignment are trivially free and are excluded from the
comparison; the question is whether K is forced linear WHERE THE EVIDENCE
REACHES.

CELL POLICY. The doctrine (FR6 -> FR7 -> FR19) is that same-passage regions
carry variable-interior cells, and only the pattern's LETTERED cells are sound.
Primary analysis uses lettered cells only. Full-span is reported as a
sensitivity check, never as the headline.

PRE-REGISTERED (frozen before corpus contact):
  R1  "linearity is DERIVED" is claimed only if the covered-restricted null
      space has dimension exactly equal to the covered-restricted linear
      family, on the LETTERED-cell system.
  R2  if the null space is larger, the excess dimension is reported as the
      unforced freedom, and at least one explicit non-linear witness must be
      exhibited and verified to satisfy every alignment constraint.
  R3  the linear family must lie inside the null space in every configuration;
      if it does not, the instrument is wrong and the run is void.

stdlib only. All exceptions carry XD-MBYG04K-URS3LF.
"""

import json, os, sys
from itertools import combinations

XD = "XD-MBYG04K-URS3LF"
N = 83
HERE = os.path.dirname(os.path.abspath(__file__))

TRIPLET = {"East 1": 0, "West 1": 0, "East 2": 0,
           "West 2": 1, "East 3": 1, "West 3": 1,
           "East 4": 2, "West 4": 2, "East 5": 2}
DISCARDED = {("#M-", "East 3", 101), ("#M", "East 1", 68)}   # repair A

# ------------------------------------------------------------------ loading

def load_corpus(path=None):
    d = json.load(open(path or os.path.join(HERE, "corpus.json")))
    M = dict(zip(d["message_labels"], d["ciphertexts"]))
    if sum(len(v) for v in M.values()) != 1036:
        raise RuntimeError(f"{XD} corpus length != 1036")
    return M

def load_atlas(path=None):
    return json.load(open(path or os.path.join(HERE, "atlas.json")))["classes"]

# ------------------------------------------------- alignment extraction

def alignments(classes, lettered_only=True, include_discarded=False):
    """Every pair of instances of a class is a certified same-passage
    alignment. Returns [(m1,s1,m2,s2,[cell offsets])]."""
    out = []
    for cls in classes:
        pat = cls["pattern"]; L = cls["length"]
        offs = [i for i, ch in enumerate(pat) if ch != "."] if lettered_only \
               else list(range(L))
        insts = [(it["message"], it["start"]) for it in cls["instances"]
                 if include_discarded
                 or (cls["id"], it["message"], it["start"]) not in DISCARDED]
        for (m1, s1), (m2, s2) in combinations(insts, 2):
            if len(offs) >= 2:
                out.append((m1, s1, m2, s2, offs))
    return out

# --------------------------------------------------- GF(83) linear algebra

def inv(a):
    a %= N
    if a == 0: raise RuntimeError(f"{XD} inverse of zero")
    return pow(a, N - 2, N)

def rref(rows, ncols):
    """Row-reduce over GF(83). Returns (reduced rows, pivot columns)."""
    mat = [r[:] for r in rows]
    piv = []; r = 0
    for c in range(ncols):
        p = None
        for i in range(r, len(mat)):
            if mat[i][c] % N: p = i; break
        if p is None: continue
        mat[r], mat[p] = mat[p], mat[r]
        iv = inv(mat[r][c])
        mat[r] = [(x * iv) % N for x in mat[r]]
        for i in range(len(mat)):
            if i != r and mat[i][c] % N:
                f = mat[i][c]
                mat[i] = [(x - f * y) % N for x, y in zip(mat[i], mat[r])]
        piv.append(c); r += 1
        if r == len(mat): break
    return mat[:r], piv

def nullspace_dim(rows, ncols):
    if not rows: return ncols
    _, piv = rref(rows, ncols)
    return ncols - len(piv)

def nullspace_basis(rows, ncols):
    red, piv = rref(rows, ncols) if rows else ([], [])
    free = [c for c in range(ncols) if c not in piv]
    basis = []
    for f in free:
        v = [0] * ncols; v[f] = 1
        for ri, pc in enumerate(piv):
            v[pc] = (-red[ri][f]) % N
        basis.append(v)
    return basis

# ------------------------------------------------------- system building

def build_system(aligns, msg_len, lettered_only=True):
    """Unknowns are K_g[t]. Returns (rows, ncols, index, covered)."""
    # triplet length = max message length in that triplet
    tlen = {}
    for m, L in msg_len.items():
        g = TRIPLET[m]; tlen[g] = max(tlen.get(g, 0), L)
    index = {}; k = 0
    for g in sorted(tlen):
        for t in range(tlen[g]):
            index[(g, t)] = k; k += 1
    ncols = k
    rows = []; covered = set()
    for (m1, s1, m2, s2, offs) in aligns:
        g1, g2 = TRIPLET[m1], TRIPLET[m2]
        i0 = offs[0]
        a0, b0 = (g1, s1 + i0), (g2, s2 + i0)
        if a0 not in index or b0 not in index: continue
        for i in offs[1:]:
            a, b = (g1, s1 + i), (g2, s2 + i)
            if a not in index or b not in index: continue
            row = [0] * ncols
            row[index[a]] = (row[index[a]] + 1) % N
            row[index[b]] = (row[index[b]] - 1) % N
            row[index[a0]] = (row[index[a0]] - 1) % N
            row[index[b0]] = (row[index[b0]] + 1) % N
            if any(row):
                rows.append(row)
                covered.update([a, b, a0, b0])
    return rows, ncols, index, covered

def linear_family(index, ncols):
    """Basis of the linear family: drift direction plus per-triplet gauge."""
    vecs = []
    v = [0] * ncols
    for (g, t), k in index.items(): v[k] = t % N
    vecs.append(("drift t", v))
    for gg in sorted({g for (g, _) in index}):
        v = [0] * ncols
        for (g, t), k in index.items():
            if g == gg: v[k] = 1
        vecs.append((f"gauge g{gg}", v))
    return vecs

def restrict(vec, cols):
    return [vec[c] for c in cols]

def satisfies(rows, v):
    return all(sum(r[i] * v[i] for i in range(len(v))) % N == 0 for r in rows)

# ------------------------------------------------------------- selftest

def selftest():
    checks = []
    def ck(name, cond, detail=""):
        checks.append((name, bool(cond)))
        print(f"  {name:34s} {'PASS' if cond else 'FAIL'} {detail}")
        if not cond: raise RuntimeError(f"{XD} selftest FAILED: {name} {detail}")

    # T1 GF(83) algebra
    rows = [[1, 2, 3], [2, 4, 6], [1, 0, 1]]
    ck("t1_rank", nullspace_dim(rows, 3) == 1, "rank 2 of 3")
    ck("t1_inv", all((x * inv(x)) % N == 1 for x in range(1, N)), "")

    # T2 dense synthetic geometry MUST force linearity
    ml = {"A": 12, "B": 12}
    trip_backup = dict(TRIPLET)
    TRIPLET.clear(); TRIPLET.update({"A": 0, "B": 1})
    al = [("A", 0, "B", 0, list(range(12))),
          ("A", 0, "A", 1, list(range(11))),
          ("B", 0, "B", 1, list(range(11)))]
    rws, nc, idx, cov = build_system(al, ml)
    cols = sorted(idx[c] for c in cov)
    lf = linear_family(idx, nc)
    for nm, v in lf:
        ck(f"t3_linear_in_null[{nm}]", satisfies(rws, v), "R3 guard")
    nb = nullspace_basis(rws, nc)
    sub = [restrict(v, cols) for v in nb]
    dim_cov = nullspace_dim([r for r in rref(sub, len(cols))[0]], len(cols)) \
        if False else len(rref([restrict(v, cols) for v in nb], len(cols))[1])
    lfsub = [restrict(v, cols) for _, v in lf]
    dim_lf = len(rref(lfsub, len(cols))[1])
    ck("t2_dense_forces_linear", dim_cov == dim_lf,
       f"null_cov={dim_cov} linear={dim_lf}")

    # T4 sparse synthetic geometry must NOT force linearity
    al2 = [("A", 0, "B", 0, [0, 1, 2])]
    rws2, nc2, idx2, cov2 = build_system(al2, ml)
    cols2 = sorted(idx2[c] for c in cov2)
    nb2 = nullspace_basis(rws2, nc2)
    dim_cov2 = len(rref([restrict(v, cols2) for v in nb2], len(cols2))[1])
    lf2 = [restrict(v, cols2) for _, v in linear_family(idx2, nc2)]
    dim_lf2 = len(rref(lf2, len(cols2))[1])
    ck("t4_sparse_leaves_freedom", dim_cov2 > dim_lf2,
       f"null_cov={dim_cov2} linear={dim_lf2}")
    TRIPLET.clear(); TRIPLET.update(trip_backup)

    # T5 corpus alignment extraction sanity
    M = load_corpus(); classes = load_atlas()
    al = alignments(classes)
    ck("t5_alignments", len(al) > 20 and all(len(o) >= 2 for *_, o in al),
       f"{len(al)} certified alignments")

    # T6 a planted BENT keystream must be caught by a system that forces linear
    ml3 = {"A": 10, "B": 10}
    TRIPLET.clear(); TRIPLET.update({"A": 0, "B": 1})
    al3 = [("A", 0, "B", 0, list(range(10))), ("A", 0, "A", 1, list(range(9)))]
    rws3, nc3, idx3, _ = build_system(al3, ml3)
    bent = [0] * nc3
    for (g, t), k in idx3.items(): bent[k] = (t * t) % N
    ck("t6_bent_rejected", not satisfies(rws3, bent), "quadratic K violates")
    TRIPLET.clear(); TRIPLET.update(trip_backup)

    print(f"selftest {sum(1 for _,p in checks if p)}/{len(checks)} green")

# --------------------------------------------------------------- corpus

def corpus_run():
    M = load_corpus(); classes = load_atlas()
    msg_len = {m: len(c) for m, c in M.items()}
    print("=" * 74)
    print("EYEKEY -- is the progressive keystream K_g[t] = drift*t DERIVED?")
    print("=" * 74)

    for policy, lettered in (("LETTERED cells (doctrine, primary)", True),
                             ("FULL span (sensitivity only)", False)):
        al = alignments(classes, lettered_only=lettered)
        rows, ncols, index, covered = build_system(al, msg_len, lettered)
        cols = sorted(index[c] for c in covered)
        lf = linear_family(index, ncols)

        # R3 guard
        bad = [nm for nm, v in lf if not satisfies(rows, v)]
        if bad:
            raise RuntimeError(f"{XD} R3 VIOLATED: linear family outside null "
                               f"space ({bad}) -- instrument wrong, run void")

        nb = nullspace_basis(rows, ncols)
        dim_cov = len(rref([restrict(v, cols) for v in nb], len(cols))[1])
        dim_lf = len(rref([restrict(v, cols) for _, v in lf], len(cols))[1])

        print(f"\n--- {policy} ---")
        print(f"  alignments                : {len(al)}")
        print(f"  constraint rows           : {len(rows)}")
        print(f"  K unknowns (all)          : {ncols}")
        print(f"  K unknowns covered        : {len(cols)}")
        print(f"  null space dim (covered)  : {dim_cov}")
        print(f"  linear family dim (cov)   : {dim_lf}")
        excess = dim_cov - dim_lf
        print(f"  EXCESS FREEDOM            : {excess}")
        print(f"  verdict: linearity is "
              f"{'DERIVED (forced by the geometry)' if excess == 0 else 'ASSUMED -- geometry admits non-linear K'}")

        if excess > 0 and lettered:
            # R2: exhibit an explicit non-linear witness
            witness = None
            lfsub = [restrict(v, cols) for _, v in lf]
            base_rank = len(rref(lfsub, len(cols))[1])
            for v in nb:
                trial = lfsub + [restrict(v, cols)]
                if len(rref(trial, len(cols))[1]) > base_rank:
                    witness = v; break
            if witness is None:
                raise RuntimeError(f"{XD} R2: excess reported but no witness")
            ok = satisfies(rows, witness)
            nz = [(g, t, witness[k]) for (g, t), k in index.items()
                  if witness[k] % N and (g, t) in covered]
            print(f"  R2 witness: satisfies all {len(rows)} constraints = {ok}")
            print(f"     non-linear witness touches {len(nz)} covered positions;"
                  f" sample {nz[:6]}")
            # how badly does it bend? second differences along one triplet
            g0 = min(g for g, _ in covered)
            series = sorted((t, witness[index[(g0, t)]] % N)
                            for (g, t) in covered if g == g0)
            if len(series) >= 3:
                sd = [(series[i+2][1] - 2*series[i+1][1] + series[i][1]) % N
                      for i in range(len(series) - 2)]
                print(f"     second differences on triplet {g0} (0 => linear): "
                      f"{'all zero' if all(x == 0 for x in sd) else 'NONZERO -> genuinely bent'}")
    print()

if __name__ == "__main__":
    selftest()
    if "--selftest" not in sys.argv:
        corpus_run()
