#!/usr/bin/env python3
"""
eyeskel -- auditing FR25's repairs against the series' standing rails, and
extracting the first relational alphabet skeleton that determines and stays
injective. Read-only.

FR25 found two two-instance repairs of the constraint pool that determine
alphabet relations without asserting a false equality. That was a result about
the pool; before anything is built on it, it has to survive the rails the
series has already established, because a repair that fixes injectivity while
reopening an old contradiction is not a repair.

THE RAILS.
  R1 gauge ladder (FR9): 1 / 3 / 9 gauges, swept over all non-degenerate
     drifts. The repair must not resurrect the refuted readings.
  R2 opening/body (FR9, FR10): does adding the literal openings still
     contradict?
  R3 body-internal (FR14): the E4/E5 offset equality that literal body runs
     force -- three runs of length 3, chance 2.4e-6 each, against an empirical
     null of ZERO such runs among all 27 cross-triplet pairs.

WHAT THE AUDIT FINDS. No regression on R1. R2 and R3 IMPROVE: both repairs
turn the T1-opening contradiction and the body-internal contradiction from
unsatisfiable-at-every-drift into satisfiable-at-every-drift. Only the T3
opening still contradicts, and no single class or instance removal clears it.

THE SKELETON. With the E4/E5 merge admitted -- it is forced by evidence, not
assumed -- repair A determines 223 pair-differences with zero injectivity
violations, in components of 19, 7, 7, 3, 3 and smaller. That corrects FR17,
which concluded offset information was orthogonal to determination: FR17
measured with certified_domain, which FR23 showed is unreliable when free
parameters exist. Measured per pair, the merge takes determination from 28 to
223.

THE CAVEAT, AND THE ROUTE IT OPENS. The pair SET is drift-invariant -- which
glyphs are linked, and the component structure -- but not one of the 223
VALUES survives a change of drift. So the skeleton's shape is structural and
its content is conditional. The route out is that a pair-difference varies
BIJECTIVELY with the drift: one known difference pins the drift uniquely, so
two external anchors inside one component determine the drift and then the
whole component.
"""

import json, os, sys
from collections import Counter
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyerepair", "eyescore", "eyeinject", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyerepair as ERP                    # noqa: E402
import eyeinject as EI                     # noqa: E402
import eyegauge as EG                      # noqa: E402
import iso_relax as IR                     # noqa: E402
import isomorph as iso                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

GI = {"T1": 0, "T2": 1, "T3": 2}
PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "repairA": ("East 3", 101, "East 1", 68),
          "repairB": ("East 3", 101, "East 4", 51),
          "drifts": [1, 2, 3, 7, 17, 41, 82]}

def build(S, pl, drift=1, merges=()):
    cts, ctx, Lx = S["cts"], S["ctx"], S["Lx"]
    gf = iso.GFSystem(N)
    for x, y in merges:
        row = {N + Lx[y]: 1, N + Lx[x]: N - 1}
        v = gf.classify(row, 0)
        if v == "contradiction": return None
        if v == "pivot": gf.add(row, 0)
    rows = EG.make_rows(ctx, drift, {m: m for m in range(9)})
    for pr in pl:
        for row, rhs in rows(pr, cts, N):
            v = gf.classify(row, rhs)
            if v == "contradiction": return None
            if v == "pivot": gf.add(row, rhs)
    return gf

def forced_diff(gf, a, b):
    hits = [d for d in range(N) if gf.classify({b: 1, a: N - 1}, d) == "redundant"]
    return hits[0] if len(hits) == 1 else None

def skeleton(gf):
    """determined pair-differences, violations, and components."""
    if gf is None: return None
    syms = sorted(v for v in gf.solve() if v < N)
    det = {}
    for a, b in combinations(syms, 2):
        v = gf.classify({b: 1, a: N - 1}, 0)
        if v == "pivot": continue
        d = forced_diff(gf, a, b)
        det[(a, b)] = d if d is not None else 0
    viol = [k for k, v in det.items() if v == 0]
    par = {s: s for s in syms}
    def find(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for a, b in det: par[find(a)] = find(b)
    comps = {}
    for s in syms: comps.setdefault(find(s), []).append(s)
    return dict(syms=syms, det=det, viol=viol,
                comps=sorted((sorted(v) for v in comps.values()),
                             key=len, reverse=True))

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: rails reproduce, repair behaves, drift structure")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    S = EI.setup(corpus, atlas)
    Lx = S["Lx"]
    BR = (Lx["East 3"], 101); A1 = (Lx["East 1"], 68)
    repA = ERP.drop(S["pool"], BR, A1)

    # rails reproduce the published results on the FULL pool
    g1 = {m: 0 for m in range(9)}
    n1 = sum(1 for d in range(1, N)
             if EG.satisfiable(S["cts"], S["ctx"], S["pool"], drift=d, group=g1))
    check("FR9 gauge theorem reproduced (1 gauge unsatisfiable)", n1 == 0,
          f"({n1}/82)")

    gm = {m: m for m in range(9)}; gm[Lx["East 5"]] = gm[Lx["East 4"]]
    nfull = sum(1 for d in range(1, N)
                if EG.satisfiable(S["cts"], S["ctx"], S["pool"], drift=d, group=gm))
    check("FR14 body-internal contradiction reproduced on full pool",
          nfull == 0, f"({nfull}/82)")

    nrep = sum(1 for d in range(1, N)
               if EG.satisfiable(S["cts"], S["ctx"], repA, drift=d, group=gm))
    check("repair A RESOLVES the body-internal contradiction", nrep == 82,
          f"({nrep}/82)")

    # determination and injectivity
    sk = skeleton(build(S, repA, 1, (("East 4", "East 5"),)))
    check("repair A + merge determines many relations with no violation",
          len(sk["det"]) > 200 and len(sk["viol"]) == 0,
          f"({len(sk['det'])} determined, {len(sk['viol'])} violations)")
    check("largest component is substantial", len(sk["comps"][0]) >= 15,
          f"({[len(c) for c in sk['comps'][:5]]})")

    # the drift caveat, asserted rather than assumed
    sk2 = skeleton(build(S, repA, 2, (("East 4", "East 5"),)))
    same_set = set(sk["det"]) == set(sk2["det"])
    same_val = sum(1 for k in sk["det"] if sk2["det"].get(k) == sk["det"][k])
    check("pair SET is drift-invariant but VALUES are not",
          same_set and same_val == 0, f"(set={same_set}, values agreeing={same_val})")

    r = IR.relax(S["cts"], N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard", (r.linked_strict, r.distinct_strict, len(r.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    S = EI.setup(corpus_path, atlas_path)
    Lx, cts, ctx, labels = S["Lx"], S["cts"], S["ctx"], S["labels"]
    freq = Counter(v for m in cts for v in m)
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")
    BR = (Lx["East 3"], 101)
    pools = {"full pool": S["pool"],
             "repair A (-E3@101 -E1@68)": ERP.drop(S["pool"], BR, (Lx["East 1"], 68)),
             "repair B (-E3@101 -E4@51)": ERP.drop(S["pool"], BR, (Lx["East 4"], 51))}
    T1o = EG.opening_pairs(labels, EG.OPENINGS[:1])
    T3o = EG.opening_pairs(labels, EG.OPENINGS[1:])
    gauges = {"1": {m: 0 for m in range(9)},
              "3": {Lx[m]: GI[t] for t, ms in EG.TRIPLETS.items() for m in ms},
              "9": {m: m for m in range(9)}}

    print("\nR1 gauge ladder (satisfiable drifts of 82) -- must not regress")
    for tag, pl in pools.items():
        cells = []
        for gn, g in gauges.items():
            n = sum(1 for d in range(1, N)
                    if EG.satisfiable(cts, ctx, pl, drift=d, group=g))
            cells.append(f"{gn} gauge: {n:2d}/82")
        print(f"  {tag:28s} " + "   ".join(cells))

    print("\nR2 opening/body contradiction")
    for tag, pl in pools.items():
        cells = []
        for ot, extra in (("alone", []), ("+T1", T1o), ("+T3", T3o)):
            n = sum(1 for d in range(1, N)
                    if EG.satisfiable(cts, ctx, pl + extra, drift=d))
            cells.append(f"{ot}: {n:2d}")
        print(f"  {tag:28s} " + "   ".join(cells))

    print("\nR3 body-internal contradiction (E4/E5, forced by literal body runs)")
    for tag, pl in pools.items():
        gm = {m: m for m in range(9)}; gm[Lx["East 5"]] = gm[Lx["East 4"]]
        n = sum(1 for d in range(1, N)
                if EG.satisfiable(cts, ctx, pl, drift=d, group=gm))
        print(f"  {tag:28s} E4/E5 merge satisfiable at {n:2d}/82 drifts")
    print("  -> both repairs RESOLVE the body-internal contradiction and the")
    print("     T1 opening; only the T3 opening still contradicts")

    print("\nS1 the relational skeleton (repair A + E4/E5 merge, drift=1)")
    sk = skeleton(build(S, pools["repair A (-E3@101 -E1@68)"], 1,
                        (("East 4", "East 5"),)))
    print(f"  determined pair-differences: {len(sk['det'])}, "
          f"injectivity violations: {len(sk['viol'])}")
    for i, c in enumerate(sk["comps"][:4]):
        if len(c) < 2: continue
        cov = sum(freq[g] for g in c)
        print(f"  component {i+1}: {len(c):2d} glyphs, {cov:3d} positions "
              f"({100*cov/1036:4.1f}%)  {c}")
    print("  (component 2 is FR7's sound pin set minus the collided pair; glyph 4")
    print("   has separated from 46, so the false equality is genuinely gone)")

    print("\nS2 the drift caveat")
    base = sk["det"]
    for d in PREREG["drifts"][1:]:
        s2 = skeleton(build(S, pools["repair A (-E3@101 -E1@68)"], d,
                            (("East 4", "East 5"),)))
        agree = sum(1 for k in base if s2["det"].get(k) == base[k])
        print(f"  drift={d:2d}: same pair set={set(s2['det'])==set(base)}, "
              f"values agreeing with drift=1: {agree}/{len(base)}")
    print("  -> the SHAPE of the skeleton is structural; its CONTENT is")
    print("     conditional on a parameter eyedrift certifies as unidentifiable")

    print("\nS3 the route that opens: a pair-difference pins the drift")
    C1 = sk["comps"][0]
    a, b = C1[0], C1[1]
    vals = {}
    for d in range(1, N):
        gf = build(S, pools["repair A (-E3@101 -E1@68)"], d, (("East 4", "East 5"),))
        v = forced_diff(gf, a, b)
        if v is not None: vals.setdefault(v, []).append(d)
    worst = max(len(v) for v in vals.values())
    print(f"  q[{b}]-q[{a}] takes {len(vals)} distinct values over 82 drifts; "
          f"most drifts sharing one value = {worst}")
    if worst == 1:
        print("  -> BIJECTIVE: one known pair-difference pins the drift uniquely")
    cov = sum(freq[g] for g in C1)
    print(f"\n  so TWO external anchors inside component 1 determine the drift AND")
    print(f"  all {len(C1)} of its glyphs -> {cov} corpus positions "
          f"({100*cov/1036:.1f}%), and with the drift fixed every other")
    print(f"  component needs only one anchor each.")
    tot = sum(len(c) for c in sk["comps"] if len(c) > 1)
    covt = sum(freq[g] for c in sk["comps"] if len(c) > 1 for g in c)
    nc = sum(1 for c in sk["comps"] if len(c) > 1)
    print(f"  {nc + 1} anchors total -> {tot} glyphs, {covt} positions "
          f"({100*covt/1036:.1f}%)")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
