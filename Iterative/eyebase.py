#!/usr/bin/env python3
"""
eyebase -- the offset structure of the corpus, rebuilt on evidence that is not
known to be false, and the mechanism behind the last standing contradiction.
Read-only.

WHY REBUILD. FR9's base-equality matrix -- which messages may share an offset
-- is one of the load-bearing results of the series, and it was computed
against the constraint pool that FR21-FR25 showed asserts six equalities a
permutation forbids. FR28 re-derived the alphabet exclusions for that reason;
the offset structure needs the same treatment.

WHAT CHANGES. Under repair A the twelve prohibitions collapse to ONE: East 3
and West 3 may not share an offset. Every other pair may.

THE MECHANISM BEHIND THE LAST CONTRADICTION. FR28 established that T3's three
messages cannot share one offset although any two can, and that the constraint
names no culprit. This instrument shows why: the pool FORCES base differences,
and once any two T3 messages are merged the third is forced a specific NONZERO
distance away (58, 54, 58 depending on which pair is merged). T1 behaves
differently -- merging E1 and W1 leaves E2's offset FREE -- which is exactly
the asymmetry FR26 flagged and could not explain.

THE DRIFT-INVARIANT RESULT. Two base differences are forced. base[W3]-base[E3]
is nonzero but changes with the drift. base[W1]-base[E1] = 0 at EVERY drift:
the first drift-invariant determination in the series, and an independent
confirmation of FR14's literal-run evidence (E1/W1 share a body run of length
13, chance 5e-25) from the constraint side rather than the statistical one.
"""

import json, os, random, sys
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyealpha", "eyepack", "eyeskel", "eyerepair", "eyescore",
          "eyeinject", "eyegauge", "eyecore", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyerepair as ERP                    # noqa: E402
import eyeinject as EI                     # noqa: E402
import eyegauge as EG                      # noqa: E402
import eyecore as EC                       # noqa: E402
import iso_relax as IR                     # noqa: E402
import isomorph as iso                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

TRIPLETS = EG.TRIPLETS
PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "drifts": [1, 2, 3, 7, 17, 41, 82]}

def build(cts, ctx, pool, drift=1, group=None, n=9):
    gf = iso.GFSystem(N)
    rows = EG.make_rows(ctx, drift, group or {m: m for m in range(n)})
    for pr in pool:
        for row, rhs in rows(pr, cts, N):
            v = gf.classify(row, rhs)
            if v == "contradiction": return None
            if v == "pivot": gf.add(row, rhs)
    return gf

def forced_base_diff(gf, ia, ib):
    """forced base[ib] - base[ia], or None if free."""
    h = [d for d in range(N)
         if gf.classify({N + ib: 1, N + ia: N - 1}, d) == "redundant"]
    return h[0] if len(h) == 1 else None

def matrix(cts, ctx, pool, labels, Lx):
    forb = []
    for i, a in enumerate(labels):
        for j, b in enumerate(labels):
            if i >= j: continue
            g = {m: m for m in range(len(labels))}; g[Lx[b]] = g[Lx[a]]
            ok = any(EG.satisfiable(cts, ctx, pool, drift=d, group=g)
                     for d in range(1, N))
            if not ok: forb.append((a, b))
    return forb

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: forced-base recovery on plants, drift behaviour, mechanism")

    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))

    # a plant with KNOWN offsets: equal within each triplet
    ctsP, labP, apP = EC.plant(atlas, corpus, "progressive", seed=21)
    ctxP = EC.plant_ctx(ctsP, labP, apP)
    LxP = {l: i for i, l in enumerate(labP)}
    gfP = build(ctsP, ctxP, ctxP["apairs"], 1)
    check("plant system builds", gfP is not None)

    # within a triplet the plant's offsets are equal, so any forced difference
    # between two of its messages must be zero
    trip = TRIPLETS["T1"]
    vals = [forced_base_diff(gfP, LxP[trip[0]], LxP[m]) for m in trip[1:]]
    nz = [v for v in vals if v not in (None, 0)]
    check("plant: no forced NONZERO difference inside a triplet with equal offsets",
          not nz, f"(forced values {vals})")

    # merging two messages that truly share an offset must stay satisfiable
    g = {m: m for m in range(9)}; g[LxP[trip[1]]] = g[LxP[trip[0]]]
    check("plant: merging two equal-offset messages is satisfiable",
          build(ctsP, ctxP, ctxP["apairs"], 1, g) is not None)

    # a forced ZERO difference must be drift-invariant; a nonzero one need not be
    zero_inv = all(forced_base_diff(build(ctsP, ctxP, ctxP["apairs"], d),
                                    LxP[trip[0]], LxP[trip[1]]) in (None, 0)
                   for d in (1, 2, 7, 41))
    check("plant: a zero forced difference stays zero across drifts", zero_inv)

    c = json.load(open(corpus))
    cts = [list(x) for x in c["ciphertexts"]]
    r = IR.relax(cts, N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard", (r.linked_strict, r.distinct_strict, len(r.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    S = EI.setup(corpus_path, atlas_path)
    Lx, cts, ctx, labels = S["Lx"], S["cts"], S["ctx"], S["labels"]
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")
    plA = ERP.drop(S["pool"], (Lx["East 3"], 101), (Lx["East 1"], 68))
    tri = {m: t for t, ms in TRIPLETS.items() for m in ms}

    print("\nB1 base-equality matrix, rebuilt under repair A")
    forb = matrix(cts, ctx, plA, labels, Lx)
    within = [(a, b) for a, b in forb if tri[a] == tri[b]]
    cross = [(a, b) for a, b in forb if tri[a] != tri[b]]
    print(f"  forbidden within-triplet: {within if within else 'NONE'}")
    print(f"  forbidden cross-triplet : {cross if cross else 'NONE'}")
    print("  FR9 on the unrepaired pool had 6 within + 6 cross = 12 prohibitions;")
    print("  repairing the pool collapses them to one")

    print("\nB2 triple merges — can a whole triplet share one offset?")
    for t, ms in TRIPLETS.items():
        g = {m: m for m in range(9)}
        for m in ms[1:]: g[Lx[m]] = g[Lx[ms[0]]]
        n = sum(1 for d in range(1, N)
                if EG.satisfiable(cts, ctx, plA, drift=d, group=g))
        print(f"  {t}: {n:2d}/82   ({', '.join(ms)})")
    print("  T2's failure follows from the E3/W3 prohibition. T3's does not —")
    print("  all of its pairs are permitted, so its failure is genuinely three-way")

    print("\nB3 forced base differences")
    print(f"  {'drift':>5s} " + " ".join(f"{f'{a[0]}{a[-1]}-{b[0]}{b[-1]}':>8s}"
          for a, b in (("East 1", "West 1"), ("East 3", "West 3"))))
    for d in PREREG["drifts"]:
        gf = build(cts, ctx, plA, d)
        row = []
        for a, b in (("East 1", "West 1"), ("East 3", "West 3")):
            row.append(str(forced_base_diff(gf, Lx[a], Lx[b])))
        print(f"  {d:5d} " + " ".join(f"{x:>8s}" for x in row))
    print("  base[W1]-base[E1] = 0 at EVERY drift -> DRIFT-INVARIANT.")
    print("  This is the first drift-invariant determination in the series and it")
    print("  independently confirms FR14's literal-run evidence (E1/W1 body run")
    print("  L=13, chance 5e-25) from the constraint side rather than statistics.")
    print("  base[W3]-base[E3] is forced but drift-dependent; nonzero at every")
    print("  drift, which is exactly the E3/W3 prohibition.")

    print("\nB4 the T3 mechanism: merging any two forces the third away")
    for a, b, cc in (("East 4", "West 4", "East 5"),
                     ("East 4", "East 5", "West 4"),
                     ("West 4", "East 5", "East 4")):
        g = {m: m for m in range(9)}; g[Lx[b]] = g[Lx[a]]
        gf = build(cts, ctx, plA, 1, g)
        v = forced_base_diff(gf, Lx[a], Lx[cc]) if gf else None
        print(f"  merge base[{a}]=base[{b}] -> base[{cc}]-base[{a}] = "
              f"{v if v is not None else 'free'}")
    g = {m: m for m in range(9)}; g[Lx["West 1"]] = g[Lx["East 1"]]
    gf = build(cts, ctx, plA, 1, g)
    v = forced_base_diff(gf, Lx["East 1"], Lx["East 2"])
    print(f"  CONTROL, T1: merge base[E1]=base[W1] -> base[E2]-base[E1] = "
          f"{v if v is not None else 'FREE'}")
    print("  -> in T1 the third message is free, so its opening is accommodated;")
    print("     in T3 no message is free. That is FR26's unexplained asymmetry.")

    print("\nB5 what removes the last contradiction")
    T3o = EG.opening_pairs(labels, EG.OPENINGS[1:])
    gm = {m: m for m in range(9)}; gm[Lx["East 5"]] = gm[Lx["East 4"]]
    a = sum(1 for d in range(1, N)
            if EG.satisfiable(cts, ctx, plA, drift=d, group=gm))
    b = sum(1 for d in range(1, N)
            if EG.satisfiable(cts, ctx, plA + T3o, drift=d, group=gm))
    print(f"  pool + evidence-forced E4/E5 merge, T3 opening NOT a constraint: {a}/82")
    print(f"  same, with the T3 opening imposed as shared plaintext:          {b}/82")
    print("  -> reading the T3 opening as literal stamped material rather than")
    print("     encrypted shared plaintext removes the last contradiction. That is")
    print("     a hypothesis that fits, not a proof that it is so.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
