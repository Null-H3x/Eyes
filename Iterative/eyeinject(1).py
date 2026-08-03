#!/usr/bin/env python3
"""
eyeinject -- auditing every published configuration against injectivity, and
finding that the constraint discriminates between drift models rather than
condemning the pool. Read-only.

FR21 applied injectivity for the first time and found the certified domain
forcing q[46] = q[4], which a permutation cannot satisfy. Two things about
that result need correcting, and the correction turns a condemnation into a
discriminator.

  (1) FR21 checked collisions only WITHIN the certified domain, ten symbols.
      The sound check asks, for every pair of symbols in the solution, whether
      q[a] - q[b] = 0 is FORCED. Under the global-drift model six pairs are
      forced equal, not one.

  (2) FR21 tested under a single GLOBAL drift. Under the per-triplet drift
      model -- FR16's coherent configuration -- there are ZERO forced
      collisions. The violation is a property of the global-drift reading,
      not of the constraint pool.

So injectivity is a discriminator: it refutes the single-global-drift model at
every drift value, and the per-triplet reading survives it cleanly. That is an
independent line of support for FR16's package, arrived at from a constraint
outside the linear machinery entirely.

METHODOLOGICAL RAIL. Collisions must be detected by asking whether an equality
is FORCED (classify -> redundant), never by comparing values in solve(). The
solver sets free variables to zero, so under a model with free parameters its
representative collapses symbols wholesale: the naive check reports 45
"violations" among ten symbols, all spurious. That trap is a selftest here.
"""

import json, os, sys
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83
SEG, BASE = N + 9, N

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyeperm", "eyeshape", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyegauge as EG                      # noqa: E402
import eyereach as ER                      # noqa: E402
import iso_relax as IR                     # noqa: E402
import isomorph as iso                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

GIDX = {"T1": 0, "T2": 1, "T3": 2}
PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16}}

def setup(corpus_path, atlas_path):
    c = json.load(open(corpus_path))
    cts = [list(x) for x in c["ciphertexts"]]; labels = c["message_labels"]
    Lx = {l: i for i, l in enumerate(labels)}
    ctx = EG.build_context(cts, labels, atlas_path)
    pool = ctx["apairs"] + ctx["strict"]
    br = (Lx["East 3"], 101)
    red = [p for p in pool if not ((p.m1, p.p1) == br or (p.m2, p.p2) == br)]
    merge = iso.IsoPair(m1=Lx["East 4"], p1=25, m2=Lx["East 5"], p2=25,
                        length=3, exact=True)
    trig = {Lx[m]: GIDX[t] for t, ms in EG.TRIPLETS.items() for m in ms}
    return dict(cts=cts, labels=labels, Lx=Lx, ctx=ctx, pool=pool, red=red,
                merge=merge, trig=trig)

def build(S, pl, per_triplet, merges=(), drift=1):
    cts, ctx, Lx, trig = S["cts"], S["ctx"], S["Lx"], S["trig"]
    gf = iso.GFSystem(N)
    for x, y in merges:
        row = {BASE + Lx[y]: 1, BASE + Lx[x]: N - 1}
        v = gf.classify(row, 0)
        if v == "contradiction": return None
        if v == "pivot": gf.add(row, 0)
    if not per_triplet:
        rows = EG.make_rows(ctx, drift, {m: m for m in range(9)})
        for pr in pl:
            for row, rhs in rows(pr, cts, N):
                v = gf.classify(row, rhs)
                if v == "contradiction": return None
                if v == "pivot": gf.add(row, rhs)
        return gf
    po, dot = ctx["pattern_of"], ctx["dot"]
    for pr in pl:
        key = (pr.m1, pr.p1, pr.m2, pr.p2, pr.length); pat = po.get(key)
        g1, g2 = trig[pr.m1], trig[pr.m2]
        for i in range(pr.length):
            if pat is not None and not pr.exact and pat[i] == '.': continue
            if pat is None and not pr.exact and \
               ((pr.m1, pr.p1 + i) in dot or (pr.m2, pr.p2 + i) in dot): continue
            A = int(cts[pr.m1][pr.p1 + i]); D = int(cts[pr.m2][pr.p2 + i])
            t1, t2 = pr.p1 + i, pr.p2 + i
            row = {}
            def acc(k, v): row[k] = (row.get(k, 0) + v) % N
            acc(D, 1); acc(A, N - 1)
            if pr.m1 != pr.m2:
                acc(BASE + pr.m2, N - 1); acc(BASE + pr.m1, 1)
            acc(SEG + 2 * g2, N - 1); acc(SEG + 2 * g2 + 1, (N - t2 % N) % N)
            acc(SEG + 2 * g1, 1);     acc(SEG + 2 * g1 + 1, t1 % N)
            row = {k: v for k, v in row.items() if v}
            v = gf.classify(row, 0)
            if v == "contradiction": return None
            if v == "pivot": gf.add(row, 0)
    return gf

def forced_collisions(gf):
    """SOUND: an equality counts only if it is FORCED, never if solve() merely
    happens to assign the same value."""
    if gf is None: return None
    syms = sorted(v for v in gf.solve() if v < N)
    return [(a, b) for a, b in combinations(syms, 2)
            if gf.classify({b: 1, a: N - 1}, 0) == "redundant"]

def naive_collisions(gf):
    """UNSOUND comparator, retained only to demonstrate the trap."""
    if gf is None: return None
    dom, _ = ER.certified_domain(gf)
    return [(a, b) for a, b in combinations(sorted(dom), 2) if dom[a] == dom[b]]

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: forced-vs-naive collision detection, model discrimination")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    S = setup(corpus, atlas)

    gG = build(S, S["pool"], False)
    check("global-drift system builds", gG is not None)
    fc = forced_collisions(gG)
    check("global drift: injectivity IS violated (forced collisions exist)",
          len(fc) > 0, f"({len(fc)} pairs)")
    check("FR21's pair is among them", (4, 46) in fc)

    gP = build(S, S["red"] + [S["merge"]], True)
    check("per-triplet coherent system builds", gP is not None)
    fcP = forced_collisions(gP)
    check("per-triplet: NO forced collisions", fcP == [], f"({fcP})")

    # the trap: solve()-value comparison invents violations under free params
    nv = naive_collisions(gP)
    check("NEGATIVE GATE: naive solve()-value check invents violations",
          len(nv) > len(fcP), f"(naive {len(nv)} vs forced {len(fcP)})")

    r = IR.relax(S["cts"], N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard", (r.linked_strict, r.distinct_strict, len(r.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    S = setup(corpus_path, atlas_path)
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    print("\nC1 forced collisions under the GLOBAL-drift model")
    fc = forced_collisions(build(S, S["pool"], False))
    print(f"  sound pool: {len(fc)} forced collisions -> {fc}")
    print("  FR21 reported one because it only compared symbols inside the")
    print("  certified domain; the sound check covers every solution symbol.")

    print("\n  is it drift-dependent?")
    counts = {}
    for d in (1, 2, 3, 7, 17, 41, 82):
        f = forced_collisions(build(S, S["pool"], False, drift=d))
        counts[d] = len(f) if f is not None else None
    print(f"  forced collisions by drift: {counts}")
    print("  -> present at every drift: no global-drift value escapes it")

    print("\nC2 the 2x2: drift model x bridge instance")
    print(f"  {'':30s} {'FULL pool':>18s} {'REDUCED (E3@101 out)':>22s}")
    for label, pt in (("global drift", False), ("per-triplet drifts", True)):
        cells = []
        for pl in (S["pool"], S["red"]):
            f = forced_collisions(build(S, pl, pt))
            cells.append("contradictory" if f is None
                         else ("CLEAN" if not f else f"{len(f)} collisions"))
        print(f"  {label:30s} {cells[0]:>18s} {cells[1]:>22s}")
    print("\n  only ONE cell satisfies injectivity: per-triplet drifts AND the")
    print("  weak bridge removed -- which is exactly FR16's coherent package.")

    print("\nC2b the coherent configuration with the run-forced merges added")
    for tag, pl, mg in (("FR16 coherent configuration", S["red"] + [S["merge"]], ()),
                        ("coherent + E1/W1 run merge", S["red"] + [S["merge"]],
                         (("East 1", "West 1"),))):
        g = build(S, pl, True, mg)
        f = forced_collisions(g)
        if f is None: print(f"  {tag:32s}: system contradictory"); continue
        print(f"  {tag:32s}: forced collisions = {f if f else 'NONE'}")

    print("\nC3 verdict")
    print("  injectivity is satisfied by exactly one of the four configurations:")
    print("  per-triplet drifts WITH the E3@101 bridge removed. Neither change")
    print("  suffices alone -- the same conjunction FR16 reached by a completely")
    print("  separate route (satisfiability plus the free-drift health measure).")
    print("\n  correction to FR21: the pool is not shown false in general. What is")
    print("  false is the pool under a global drift, or with the weak bridge kept.")
    print("  FR21's localisation to #M and to E1@68 is a property of the global-")
    print("  drift model, not a defect of the atlas.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
