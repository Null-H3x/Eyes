#!/usr/bin/env python3
"""eyesep -- FR59. Is C digit-separable?  q[g] = F(d2)+G(d1)+H(d0) mod 83.

XD-MBYG04K-URS3LF prefix on all exceptions.

Frame-INVARIANT: permuting digit positions or state labels merely permutes
F,G,H, so one test covers the whole frame group (FR58's 432 stabiliser and the
full 10,368,000 group alike).

Drift-free: within a component q[g2]-q[g1] = drift*(D2-D1); absorbing drift into
F,G,H gives  F(a2)-F(a1) + G(b2)-G(b1) + H(c2)-H(c1) = D2-D1.

Strictly contains FR28's affine family (F(a)=25am, G(b)=5bm, H(c)=cm).
"""
from itertools import combinations
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

def digits(g): return (g // 25, (g // 5) % 5, g % 5)

def row_for(g1, g2, rhs):
    """15 unknowns: F0..F4, G0..G4, H0..H4"""
    r = [0] * 16
    a1, b1, c1 = digits(g1); a2, b2, c2 = digits(g2)
    r[a2] = (r[a2] + 1) % N;      r[a1] = (r[a1] - 1) % N
    r[5 + b2] = (r[5 + b2] + 1) % N;  r[5 + b1] = (r[5 + b1] - 1) % N
    r[10 + c2] = (r[10 + c2] + 1) % N; r[10 + c1] = (r[10 + c1] - 1) % N
    r[15] = rhs % N
    return r

def build_system(comps):
    rows = []
    for C in comps:
        for a, b in combinations(sorted(C), 2):
            rows.append(row_for(a, b, (C[b] - C[a]) % N))
    return rows

def solve(rows, nvar=15):
    """Gaussian elimination over GF(83). Returns (consistent, rank, contradictions)."""
    M = [r[:] for r in rows]
    piv = 0; rank = 0; contra = 0
    for col in range(nvar):
        sel = None
        for i in range(piv, len(M)):
            if M[i][col] % N:
                sel = i; break
        if sel is None:
            continue
        M[piv], M[sel] = M[sel], M[piv]
        inv = pow(M[piv][col], N - 2, N)
        M[piv] = [(x * inv) % N for x in M[piv]]
        for i in range(len(M)):
            if i != piv and M[i][col] % N:
                f = M[i][col]
                M[i] = [(M[i][j] - f * M[piv][j]) % N for j in range(nvar + 1)]
        piv += 1; rank += 1
    for i in range(len(M)):
        if all(M[i][j] % N == 0 for j in range(nvar)) and M[i][nvar] % N:
            contra += 1
    return contra == 0, rank, contra

# ------------------------------------------------------------------ selftests
def selftest():
    rng = random.Random(59); out = []
    def ck(nm, c, d=""):
        out.append((nm, bool(c), d))
        if not c: raise XD("SELFTEST FAIL: %s %s" % (nm, d))

    # S1 -- planted SEPARABLE alphabet must be consistent
    F = [rng.randrange(N) for _ in range(5)]
    G = [rng.randrange(N) for _ in range(5)]
    H = [rng.randrange(N) for _ in range(5)]
    q = {g: (F[digits(g)[0]] + G[digits(g)[1]] + H[digits(g)[2]]) % N for g in range(N)}
    sep = [{g: q[g] for g in C} for C in COMPS]
    ok, rank, contra = solve(build_system(sep))
    ck("S1 planted separable alphabet is consistent", ok, "rank=%d contra=%d" % (rank, contra))
    # rank 11, not 12: d2=4 is structurally impossible (those trigrams label
    # 100..124, above the ceiling of 82), so F(4) is vacuous. Null space =
    # 3 gauge constants + 1 vacuous variable.
    ck("S2 rank is 11 (3 gauge + F(4) vacuous: d2=4 exceeds the label ceiling)",
       rank == 11, "rank=%d" % rank)

    # S3 -- AFFINE is a special case: must also be consistent
    a0, b0 = rng.randrange(1, N), rng.randrange(N)
    aff = [{g: (a0 * g + b0) % N for g in C} for C in COMPS]
    ok2, _, _ = solve(build_system(aff))
    ck("S3 affine alphabet (subset of separable) is consistent", ok2)

    # S4 -- NEGATIVE CONTROL: random alphabet must be inconsistent
    rnd = [{g: rng.randrange(N) for g in C} for C in COMPS]
    ok3, _, c3 = solve(build_system(rnd))
    ck("S4 random alphabet rejected", (not ok3) and c3 > 0, "contradictions=%d" % c3)

    # S5 -- detector must not be vacuous: one planted violation must break it
    bad = [dict(d) for d in sep]
    k = sorted(bad[0])[0]
    bad[0][k] = (bad[0][k] + 1) % N
    ok4, _, c4 = solve(build_system(bad))
    ck("S5 single planted violation is detected", not ok4, "contradictions=%d" % c4)

    # S6 -- null rate: how often does a random alphabet pass by chance?
    passes = 0
    for _ in range(200):
        r = [{g: rng.randrange(N) for g in C} for C in COMPS]
        if solve(build_system(r))[0]: passes += 1
    ck("S6 null pass rate is zero", passes == 0, "%d/200" % passes)
    return out

if __name__ == "__main__":
    print("=== eyesep selftests (green before corpus contact) ===")
    for nm, ok, d in selftest():
        print("  %-52s %s  %s" % (nm, "PASS" if ok else "FAIL", d))
    print("ALL GREEN")
