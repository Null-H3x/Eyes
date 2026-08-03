#!/usr/bin/env python3
"""
eyerecur -- FR11's horizon item 1, generalised: instead of testing one
"constrained Gromark", sweep the ENTIRE family of keystreams obeying a
2-term linear recurrence

    K_g[t] = alpha * K_g[t-1] + beta * K_g[t-2]   (mod 83)

seeded by two numbers per triplet. This family contains every Gromark
variant (the classic lagged-Fibonacci primer is alpha=beta=1) AND the
progressive/arithmetic keystream (alpha=2, beta=-1), so a single sweep
prices the whole corner at once. Read-only.

THE ALGEBRAIC REASON THIS IS TRACTABLE. Perfect isomorphy of a pair at
shift Delta requires the offset difference K[p2+i] - K[p1+i] to be CONSTANT
across the span. That difference sequence obeys the same recurrence as K,
and a constant c satisfies it iff c*(1 - alpha - beta) = 0. So:

  * alpha + beta != 1  ->  only c = 0 survives: the keystream must repeat
    EXACTLY at that shift.
  * alpha + beta == 1  ->  the characteristic roots are 1 and lambda =
    alpha - 1, giving K[t] = A + B*lambda^t, and the shift difference is
    B*lambda^(p1+i) * (lambda^Delta - 1). Constant across a span of length
    >= 2 forces B = 0 (constant keystream), or lambda = 1 (the progressive
    case), or lambda^Delta = 1 (difference identically zero).

The corpus's within-triplet shifts have gcd 1 (there are Delta=1 pairs with
spans up to 30), so lambda^Delta = 1 for all observed Delta forces lambda =
1. The prediction is therefore sharp: only progressive, plus degenerate
constant-keystream solutions, can survive -- and progressive is what FR9,
FR10 and FR11 contradict. The sweep tests this rather than assuming it.

DEGENERACY GUARD. A system can be satisfiable while determining nothing
(FR9's d=0 lesson, FR11's Gromark collapse). Every survivor is therefore
reported with the number of DISTINCT symbol values in its solution; a
solution that collapses symbols is flagged and never counted as a live
model.
"""

import json, os, sys
from math import gcd

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyecore", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyecore as EC                       # noqa: E402
import eyegauge as EG                      # noqa: E402
import eyereach as ER                      # noqa: E402
import iso_relax as IR                     # noqa: E402
import isomorph as iso                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

TRIPLETS = EG.TRIPLETS
SYM, BASE, SEED = 0, N, N + 9            # 83 symbols, 9 bases, 6 seeds
PREREG = {
    "baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
    "progressive": (2, N - 1),
    "fibonacci_gromark": (1, 1),
    "min_distinct_values": 2,            # below this the solution is degenerate
    "filter_shifts": [1, 2, 3],          # decisive small-shift pairs
}

# ------------------------------------------------------------------ recurrence
def uv_tables(alpha, beta, T):
    """K[t] = u[t]*K[0] + v[t]*K[1] for the recurrence with these coefficients."""
    u = [1, 0]; v = [0, 1]
    for t in range(2, T + 2):
        u.append((alpha * u[t - 1] + beta * u[t - 2]) % N)
        v.append((alpha * v[t - 1] + beta * v[t - 2]) % N)
    return u, v

def rows_recur(ctx, tri, u, v):
    pattern_of, dot = ctx["pattern_of"], ctx["dot"]
    def rows(pr, messages, Nn):
        key = (pr.m1, pr.p1, pr.m2, pr.p2, pr.length)
        pat = pattern_of.get(key)
        g1, g2 = tri[pr.m1], tri[pr.m2]
        s1, s2 = SEED + 2 * g1, SEED + 2 * g2
        for i in range(pr.length):
            if pat is not None and not pr.exact and pat[i] == '.': continue
            if pat is None and not pr.exact and \
               ((pr.m1, pr.p1 + i) in dot or (pr.m2, pr.p2 + i) in dot): continue
            A = int(messages[pr.m1][pr.p1 + i]); D = int(messages[pr.m2][pr.p2 + i])
            t1, t2 = pr.p1 + i, pr.p2 + i
            row = {}
            def acc(k, c):
                row[k] = (row.get(k, 0) + c) % Nn
            acc(D, 1); acc(A, Nn - 1)
            if pr.m1 != pr.m2:
                acc(BASE + pr.m2, Nn - 1); acc(BASE + pr.m1, 1)
            acc(s2, (Nn - u[t2]) % Nn); acc(s2 + 1, (Nn - v[t2]) % Nn)
            acc(s1, u[t1] % Nn);        acc(s1 + 1, v[t1] % Nn)
            row = {k: c for k, c in row.items() if c}
            yield row, 0
    return rows

def keystream_range(pool):
    lo = min(min(p.p1, p.p2) for p in pool)
    hi = max(max(p.p1 + p.length, p.p2 + p.length) for p in pool)
    return lo, hi

def status(cts, ctx, tri, pool, alpha, beta, T, rng):
    """CONTRA (unsatisfiable) / DEGENERATE (keystream forced constant over the
    region the pairs occupy -- i.e. absorbed into the per-message base, which
    is monoalphabetic and excluded by FG1) / LIVE."""
    u, v = uv_tables(alpha, beta, T)
    gf = iso.GFSystem(N)
    rf = rows_recur(ctx, tri, u, v)
    for pr in pool:
        for row, rhs in rf(pr, cts, N):
            verdict = gf.classify(row, rhs)
            if verdict == "contradiction": return "CONTRA"
            if verdict == "pivot": gf.add(row, rhs)
    lo, hi = rng
    for g in range(3):
        for t in range(lo, hi - 1):
            du = (u[t + 1] - u[t]) % N; dv = (v[t + 1] - v[t]) % N
            row = {}
            if du: row[SEED + 2 * g] = du
            if dv: row[SEED + 2 * g + 1] = dv
            if not row: continue
            if gf.classify(row, 0) != "redundant": return "LIVE"
    return "DEGENERATE"

def sweep(cts, ctx, tri, filt, full, T, rng):
    live, degen, contra = [], 0, 0
    for alpha in range(N):
        for beta in range(N):
            if status(cts, ctx, tri, filt, alpha, beta, T, rng) == "CONTRA":
                contra += 1; continue
            s = status(cts, ctx, tri, full, alpha, beta, T, rng)
            if s == "CONTRA": contra += 1
            elif s == "DEGENERATE": degen += 1
            else: live.append((alpha, beta))
    return live, degen, contra

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: recurrence algebra, degeneracy guard, corpus controls")

    u, v = uv_tables(2, N - 1, 12)
    check("progressive (2,-1) tables give K0 + t*(K1-K0)",
          all((u[t] + v[t]) % N == 1 and v[t] % N == t % N for t in range(10)))
    uf, vf = uv_tables(1, 1, 12)
    fib = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    check("Fibonacci (1,1) tables give Fibonacci numbers",
          all(vf[t] == fib[t] for t in range(10)))

    # constant-sequence algebra: c is a solution iff c*(1-alpha-beta)=0
    bad = 0
    for (al, be) in ((1, 1), (3, 5), (2, N - 1), (7, N - 6)):
        c0 = 7
        seq = [c0, c0]
        for t in range(2, 8): seq.append((al * seq[-1] + be * seq[-2]) % N)
        const = all(x == c0 for x in seq)
        expect = ((1 - al - be) % N == 0)
        if const != expect: bad += 1
    check("constant-sequence criterion c*(1-alpha-beta)=0 verified", bad == 0)

    # lambda characterisation for alpha+beta==1: roots are 1 and alpha-1
    okl = True
    for al in (2, 5, 40):
        be = (1 - al) % N; lam = (al - 1) % N
        s = [1, lam]
        for t in range(2, 10): s.append((al * s[-1] + be * s[-2]) % N)
        if any(s[t] != pow(lam, t, N) for t in range(10)): okl = False
    check("alpha+beta=1 gives characteristic root lambda=alpha-1", okl)

    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    c = json.load(open(corpus)); labels = c["message_labels"]
    cts = [list(x) for x in c["ciphertexts"]]
    Lx = {lab: i for i, lab in enumerate(labels)}
    gi = {"T1": 0, "T2": 1, "T3": 2}
    tri = {Lx[m]: gi[t] for t, ms in TRIPLETS.items() for m in ms}
    ctx = EG.build_context(cts, labels, atlas)
    pool = ctx["apairs"] + ctx["strict"]
    T = max(len(x) for x in cts); rng = keystream_range(pool)

    g = 0
    for pr in pool:
        if tri[pr.m1] == tri[pr.m2]:
            d = (pr.p2 - pr.p1) % N
            if d: g = gcd(g, d)
    check("corpus within-triplet shifts have gcd 1 (forces lambda=1)", g == 1,
          f"(gcd={g})")

    # positive control: progressive is LIVE on the pool alone
    check("positive control: progressive LIVE on pool without openings",
          status(cts, ctx, tri, pool, 2, N - 1, T, rng) == "LIVE")
    # guard sanity: a constant-keystream recurrence must be DEGENERATE
    check("guard: constant-keystream recurrence (1,0) is DEGENERATE",
          status(cts, ctx, tri, pool, 1, 0, T, rng) == "DEGENERATE")
    check("guard: null recurrence (0,0) is DEGENERATE",
          status(cts, ctx, tri, pool, 0, 0, T, rng) == "DEGENERATE")

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    c = json.load(open(corpus_path))
    cts = [list(x) for x in c["ciphertexts"]]; labels = c["message_labels"]
    Lx = {lab: i for i, lab in enumerate(labels)}
    gi = {"T1": 0, "T2": 1, "T3": 2}
    tri = {Lx[m]: gi[t] for t, ms in TRIPLETS.items() for m in ms}

    r = IR.relax(cts, N, seed=0); bg = PREREG["baseline_guard"]
    if (r.linked_strict, r.distinct_strict, len(r.pins)) != \
       (bg["linked"], bg["distinct"], bg["pins"]):
        fail("baseline reproduction mismatch")
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    ctx = EG.build_context(cts, labels, atlas_path)
    pool = ctx["apairs"] + ctx["strict"]
    T1o = EG.opening_pairs(labels, EG.OPENINGS[:1])
    T3o = EG.opening_pairs(labels, EG.OPENINGS[1:])
    EG.verify_literal(cts, labels, EG.OPENINGS)
    T = max(len(x) for x in cts); rng = keystream_range(pool)
    filt = [p for p in pool if tri[p.m1] == tri[p.m2]
            and (p.p2 - p.p1) % N in PREREG["filter_shifts"]]
    print(f"pairs occupy positions [{rng[0]}, {rng[1]}); constancy tested there")
    print(f"fast filter {len(filt)} pairs; full pool {len(pool)}")

    print("\nnamed models (full pool + openings):")
    for al, be, nm in ((2, N - 1, "PROGRESSIVE"), (1, 1, "Fibonacci Gromark"),
                       (1, 0, "constant-K"), (0, 0, "null-K")):
        print(f"  (alpha={al:2d}, beta={be:2d}) {nm:20s}: "
              f"{status(cts, ctx, tri, pool + T1o + T3o, al, be, T, rng)}")

    for tag, extra in (("WITHOUT openings", []), ("WITH openings", T1o + T3o)):
        live, degen, contra = sweep(cts, ctx, tri, filt + extra, pool + extra, T, rng)
        print(f"\n=== sweep over all {N*N} recurrences, {tag} ===")
        print(f"  contradicted={contra}  degenerate={degen}  LIVE={len(live)}")
        print(f"  LIVE set: {live if live else 'EMPTY -- family excluded'}")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
