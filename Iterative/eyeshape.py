#!/usr/bin/env python3
"""
eyeshape -- what shape must the keystream have? Two results from one idea.
Read-only; repo machinery unmodified.

THE IDEA. FR12 excluded every 2-term linear-recurrence keystream by sweeping
the family. But the corpus constrains K's SHAPE directly, with no keystream
model at all. A perfect isomorph pair inside one triplet, at shift D over a
span of length L, forces

    K_g[t + D] - K_g[t]  =  constant   for t in [p1, p1 + L)

because the two messages share K_g and their per-message bases contribute a
single constant. Nothing else is assumed: no recurrence, no drift, no
alphabet, no PRNG. In particular a pair at D = 1 forces the FIRST DIFFERENCE
of K_g to be constant across its whole span -- i.e. K_g is ARITHMETIC there.
C1 maps every such range.

C2 then asks the natural follow-up. FR9-FR12 showed a globally affine
keystream (progressive) cannot carry both the certified atlas classes and
the literal openings. So how much departure from affine is needed? Model K
as piecewise affine with break-points (a key reset), sweep the break
positions, and find the minimum. C3 measures how much determination
survives, because five cycles of this series have now shown that a model can
buy consistency by going vacuous.

DEGENERACY GUARD, HARD-WON. A segment's slope counts as evidence only if
that slope variable SURVIVES in some row after cancellation. Two bugs in
this cycle came from ignoring that: segments containing no pair cells, and
segments touched only by Delta = 0 opening pairs whose keystream terms
cancel identically. Both made unconstrained variables read as "structure".
The rule is general: in a linear model test, a variable absent from every
row is free by construction, and asking whether it is forced always answers
no.
"""

import json, os, sys
from collections import Counter

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyegauge as EG                      # noqa: E402
import iso_relax as IR                     # noqa: E402
import isomorph as iso                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

TRIPLETS = EG.TRIPLETS
GIDX = {"T1": 0, "T2": 1, "T3": 2}
GNAME = {0: "T1", 1: "T2", 2: "T3"}
BASE, SEG = N, N + 9
PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "sweep_range": (18, 110)}

# ------------------------------------------------------------------ C1
def merge(spans):
    out = []
    for lo, hi in sorted(spans):
        if out and lo <= out[-1][1]: out[-1] = (out[-1][0], max(out[-1][1], hi))
        else: out.append((lo, hi))
    return out

def shape_map(pool, tri):
    """for each triplet, the shift-D ranges where K's D-difference is forced
    constant. D = 1 means K is arithmetic on that range."""
    cov = {g: {} for g in range(3)}
    for p in pool:
        if tri[p.m1] != tri[p.m2]: continue
        d = p.p2 - p.p1
        if d == 0: continue
        lo = min(p.p1, p.p2)
        cov[tri[p.m1]].setdefault(abs(d), []).append((lo, lo + p.length))
    return {g: {d: merge(v) for d, v in cov[g].items()} for g in range(3)}

# ------------------------------------------------------------------ C2/C3
def analyse(cts, ctx, tri, pool, breaks):
    """breaks: dict triplet -> list of break positions. Returns
    (status, n_unforced_slopes, n_exercised_slopes)."""
    pattern_of, dot = ctx["pattern_of"], ctx["dot"]
    ns = {g: len(breaks.get(g, [])) + 1 for g in range(3)}
    off = {}; nxt = SEG
    for g in range(3):
        off[g] = nxt; nxt += 2 * ns[g]
    def seg(g, t):
        s = 0
        for b in breaks.get(g, []):
            if t >= b: s += 1
        return s
    def var(g, s, w): return off[g] + 2 * s + w
    slopes = {var(g, s, 1) for g in range(3) for s in range(ns[g])}
    gf = iso.GFSystem(N); touched = set()
    for pr in pool:
        key = (pr.m1, pr.p1, pr.m2, pr.p2, pr.length)
        pat = pattern_of.get(key)
        g1, g2 = tri[pr.m1], tri[pr.m2]
        for i in range(pr.length):
            if pat is not None and not pr.exact and pat[i] == '.': continue
            if pat is None and not pr.exact and \
               ((pr.m1, pr.p1 + i) in dot or (pr.m2, pr.p2 + i) in dot): continue
            A = int(cts[pr.m1][pr.p1 + i]); D = int(cts[pr.m2][pr.p2 + i])
            t1, t2 = pr.p1 + i, pr.p2 + i
            s1, s2 = seg(g1, t1), seg(g2, t2)
            row = {}
            def acc(k, v): row[k] = (row.get(k, 0) + v) % N
            acc(D, 1); acc(A, N - 1)
            if pr.m1 != pr.m2:
                acc(BASE + pr.m2, N - 1); acc(BASE + pr.m1, 1)
            acc(var(g2, s2, 0), N - 1); acc(var(g2, s2, 1), (N - t2 % N) % N)
            acc(var(g1, s1, 0), 1);     acc(var(g1, s1, 1), t1 % N)
            row = {k: v for k, v in row.items() if v}
            touched |= (set(row) & slopes)      # only surviving coefficients
            verdict = gf.classify(row, 0)
            if verdict == "contradiction": return "CONTRA", 0, len(touched)
            if verdict == "pivot": gf.add(row, 0)
    free = [v for v in sorted(touched) if gf.classify({v: 1}, 0) != "redundant"]
    return ("LIVE" if free else "DEGENERATE"), len(free), len(touched)

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: shape algebra, touched-set logic, corpus controls")

    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    c = json.load(open(corpus)); labels = c["message_labels"]
    cts = [list(x) for x in c["ciphertexts"]]
    Lx = {lab: i for i, lab in enumerate(labels)}
    tri = {Lx[m]: GIDX[t] for t, ms in TRIPLETS.items() for m in ms}
    ctx = EG.build_context(cts, labels, atlas)
    pool = ctx["apairs"] + ctx["strict"]
    T1o = EG.opening_pairs(labels, EG.OPENINGS[:1])
    T3o = EG.opening_pairs(labels, EG.OPENINGS[1:])

    # (1) the shape algebra on a constructed sequence: an arithmetic K has
    #     constant first difference; a non-arithmetic one does not
    K = [(5 + 7 * t) % N for t in range(40)]
    d1 = {(K[t + 1] - K[t]) % N for t in range(30)}
    K2 = [(5 + 7 * t + (t * t)) % N for t in range(40)]
    d2 = {(K2[t + 1] - K2[t]) % N for t in range(30)}
    check("shift-1 constancy characterises arithmetic keystreams",
          len(d1) == 1 and len(d2) > 1)

    # (2) touched-set regression: a Delta=0 pair's keystream terms cancel, so
    #     it must NOT mark any slope as exercised
    _, _, tz = analyse(cts, ctx, tri, T3o, {})
    check("Delta=0 opening pairs exercise no slope (regression)", tz == 0,
          f"(touched={tz})")

    # (3) corpus controls: pool alone LIVE with one free slope per triplet;
    #     pool+openings DEGENERATE under a globally affine keystream
    s0, f0, t0 = analyse(cts, ctx, tri, pool, {})
    check("pool alone, globally affine: LIVE with 3 free slopes",
          s0 == "LIVE" and f0 == 3, f"({s0}, free={f0}, exercised={t0})")
    s1, f1, _ = analyse(cts, ctx, tri, pool + T1o + T3o, {})
    check("pool + openings, globally affine: DEGENERATE (FR9-FR12)",
          s1 == "DEGENERATE" and f1 == 0, f"({s1}, free={f1})")

    # (4) shape map finds the Delta=1 ranges and they are non-empty for T3
    sm = shape_map(pool, tri)
    check("shape map: T3 has shift-1 ranges", 1 in sm[2] and sm[2][1],
          f"({sm[2].get(1)})")

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    c = json.load(open(corpus_path))
    cts = [list(x) for x in c["ciphertexts"]]; labels = c["message_labels"]
    Lx = {lab: i for i, lab in enumerate(labels)}
    tri = {Lx[m]: GIDX[t] for t, ms in TRIPLETS.items() for m in ms}

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
    full = pool + T1o + T3o

    print("\nC1 model-free keystream shape (no recurrence, drift or alphabet assumed):")
    sm = shape_map(pool, tri)
    for g in range(3):
        print(f"  {GNAME[g]}:")
        if not sm[g]: print("    (no within-triplet shifted pairs)"); continue
        for d in sorted(sm[g]):
            tag = "   <== K IS ARITHMETIC HERE" if d == 1 else ""
            print(f"    shift {d:2d}: difference constant on {sm[g][d]}{tag}")
    print("\n  provably arithmetic ranges:")
    for g in range(3):
        if 1 in sm[g]:
            span = sum(hi - lo for lo, hi in sm[g][1])
            print(f"    {GNAME[g]}: {sm[g][1]}  ({span} positions)")
        else:
            print(f"    {GNAME[g]}: no shift-1 pair; shape constrained only at "
                  f"higher shifts")

    print("\nC2 piecewise-affine keystream: how many break-points (key resets)?")
    s0, f0, _ = analyse(cts, ctx, tri, pool, {})
    s1, f1, _ = analyse(cts, ctx, tri, full, {})
    print(f"  0 breaks, pool alone      : {s0} (free slopes {f0}/3)")
    print(f"  0 breaks, pool + openings : {s1} (free slopes {f1})   "
          f"<-- the FR9-FR12 contradiction")
    lo, hi = PREREG["sweep_range"]
    glob = {s: analyse(cts, ctx, tri, full, {0: [s], 1: [s], 2: [s]})
            for s in range(lo, hi)}
    live = [s for s, v in glob.items() if v[0] == "LIVE"]
    print(f"  1 global break: LIVE at {len(live)}/{hi-lo} positions; "
          f"status counts {dict(Counter(v[0] for v in glob.values()))}")
    print("  1 break in a SINGLE triplet:")
    for g in range(3):
        hits = [s for s in range(lo, hi)
                if analyse(cts, ctx, tri, full, {g: [s]})[0] == "LIVE"]
        shown = hits if len(hits) <= 14 else hits[:14] + ["..."]
        print(f"    {GNAME[g]} only: LIVE at {shown}  ({len(hits)} positions)")

    print("\nC3 how much determination survives (free slopes = model health):")
    print(f"  no openings, globally affine : {f0} free slopes of 3 exercised")
    for s in (40, 60, 95):
        st, fr, tc = analyse(cts, ctx, tri, full, {0: [s], 1: [s], 2: [s]})
        print(f"  openings + global break @{s:3d}: {st}, {fr} free of {tc} exercised")
    print("  -> a single reset restores formal consistency, but the openings "
          "flatten\n     most segments: consistency is again bought with lost "
          "determination")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
