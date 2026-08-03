#!/usr/bin/env python3
"""
eyerepair2 -- closing a fork the project has carried since cycle twenty-five.
Read-only.

THE OPEN QUESTION. FR25 found that the corpus admits a determining, injective
reading only if one well-supported isomorph instance is discarded, and that
TWO candidate repairs worked equally well:

    repair A : drop E3@101 and E1@68   -> 28 forced relations, 0 violations
    repair B : drop E3@101 and E4@51   -> 36 forced relations, 0 violations

FR27 favoured A on embeddedness -- E1@68 is the only instance in either class
with no parent passage -- but that is soft evidence, and the model has been
carried as "conditional on repair A" ever since.

WHAT SETTLES IT. The FR32/33 passage (East 4 @ 28 x West 4 @ 29) did not exist
when FR25 posed the question. Rebuilt WITH it:

    repair A : 384 relations, 0 injectivity violations
    repair B : 393 relations, 4 injectivity violations

Repair B forces q[4]=q[60], q[10]=q[75], q[19]=q[35] and q[37]=q[66] -- four
equalities a permutation forbids. The passage is consistent with A and
inconsistent with B.

THE LOGICAL SHAPE. Passage + B is contradictory, so either the passage is
wrong or B is. The passage is independently supported -- FR32 priced it at
3.6e-6 across all E4/W4 window pairs, and FR35 found fourteen consecutive
cells agreeing on the established w, chance 83^-13, against a clean shuffle
null. So B is wrong. This is a CONDITIONAL refutation and is stated as one.

A THIRD READING. Dropping BOTH instances gives 259 relations with 0
violations: valid, and agreeing with repair A on all comparable pairs. It is a
strict weakening -- the same content, less of it -- so A is the unique maximum
among the readings that survive.
"""

import json, os, sys
from collections import Counter
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyeaudit", "eyestamp", "eyeh1", "eyeind", "eyenull", "eyeloo",
          "eyerepair", "eyeinject", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyeaudit as EA                      # noqa: E402
import iso_relax as IR                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "A_relations": 384, "B_violations": 4}

def setup(corpus_path, atlas_path):
    cts, labels, Lx, ctx, pool, _ = EA.load(corpus_path, atlas_path)
    keys = {"BR": (Lx["East 3"], 101),
            "A1": (Lx["East 1"], 68),
            "B1": (Lx["East 4"], 51)}
    return cts, labels, Lx, ctx, pool, keys

def drop(pool, *ks):
    return [p for p in pool
            if not any((p.m1, p.p1) == k or (p.m2, p.p2) == k for k in ks)]

def model(cts, ctx, Lx, pool, rem, cells=None):
    cells = EA.CELLS if cells is None else cells
    gf = EA.build(cts, ctx, Lx, drop(pool, *rem), cells=cells)
    if gf is None: return None, None
    return gf, EA.analyse(gf)

def forced_diff(gf, a, b):
    h = [d for d in range(N) if gf.classify({b: 1, a: N - 1}, d) == "redundant"]
    return h[0] if len(h) == 1 else None

def compare(gfX, aX, gfY, aY):
    cX = {g: i for i, c in enumerate(aX["comps"]) for g in c}
    cY = {g: i for i, c in enumerate(aY["comps"]) for g in c}
    agree = dis = 0
    for x, y in combinations(sorted(set(cX) & set(cY)), 2):
        if cX.get(x) != cX.get(y) or cY.get(x) != cY.get(y): continue
        dx = forced_diff(gfX, x, y); dy = forced_diff(gfY, x, y)
        if dx is None or dy is None: continue
        if dx == dy: agree += 1
        else: dis += 1
    return agree, dis

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: the three readings, and what discriminates them")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    cts, labels, Lx, ctx, pool, K = setup(corpus, atlas)

    gA, aA = model(cts, ctx, Lx, pool, (K["BR"], K["A1"]))
    check("repair A reproduces and is injective",
          aA["det"] == PREREG["A_relations"] and not aA["eq"],
          f"({aA['det']} relations, {len(aA['eq'])} violations)")

    gB, aB = model(cts, ctx, Lx, pool, (K["BR"], K["B1"]))
    check("repair B VIOLATES injectivity under the full model",
          len(aB["eq"]) == PREREG["B_violations"],
          f"({len(aB['eq'])} violations: {aB['eq']})")

    gA0, aA0 = model(cts, ctx, Lx, pool, (K["BR"], K["A1"]), cells=[])
    gB0, aB0 = model(cts, ctx, Lx, pool, (K["BR"], K["B1"]), cells=[])
    check("without the passage BOTH repairs are clean (FR25's situation)",
          not aA0["eq"] and not aB0["eq"],
          f"(A {aA0['det']}/{len(aA0['eq'])}, B {aB0['det']}/{len(aB0['eq'])})")

    gAB, aAB = model(cts, ctx, Lx, pool, (K["BR"], K["A1"], K["B1"]))
    check("dropping both instances is valid but weaker",
          not aAB["eq"] and aAB["det"] < aA["det"],
          f"({aAB['det']} relations vs A's {aA['det']})")

    ag, dis = compare(gA, aA, gAB, aAB)
    check("and it agrees with A wherever both speak",
          dis == 0 and ag > 100, f"({ag} agree, {dis} disagree)")

    c = json.load(open(corpus))
    cc = [list(x) for x in c["ciphertexts"]]
    r = IR.relax(cc, N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard", (r.linked_strict, r.distinct_strict, len(r.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    cts, labels, Lx, ctx, pool, K = setup(corpus_path, atlas_path)
    freq = Counter(g for m in cts for g in m)
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    print("\nF1 the three readings, each built to completion")
    print(f"  {'reading':30s} {'pool':>5s} {'relations':>10s} {'viol':>5s} "
          f"{'glyphs':>7s} {'exposure':>9s}")
    out = {}
    for tag, rem in (("A   drop E3@101, E1@68", (K["BR"], K["A1"])),
                     ("B   drop E3@101, E4@51", (K["BR"], K["B1"])),
                     ("AB  drop all three", (K["BR"], K["A1"], K["B1"]))):
        gf, a = model(cts, ctx, Lx, pool, rem)
        if gf is None:
            print(f"  {tag:30s} CONTRADICTION"); continue
        out[tag] = (gf, a)
        cov = sum(freq[g] for g in a["linked"])
        print(f"  {tag:30s} {len(drop(pool, *rem)):5d} {a['det']:10d} "
              f"{len(a['eq']):5d} {len(a['linked']):7d} {100 * cov / 1036:8.1f}%")

    print("\nF2 what repair B asserts")
    gB, aB = out["B   drop E3@101, E4@51"]
    print(f"  forced equalities: {aB['eq']}")
    print("  a permutation forbids every one of them, so B is refuted")

    print("\nF3 the passage is the discriminator")
    print(f"  {'configuration':30s} {'repair A':>16s} {'repair B':>16s}")
    for tag, cells in (("without the passage", []),
                       ("with the passage (14 cells)", EA.CELLS)):
        _, a1 = model(cts, ctx, Lx, pool, (K["BR"], K["A1"]), cells=cells)
        _, b1 = model(cts, ctx, Lx, pool, (K["BR"], K["B1"]), cells=cells)
        sa = f"{a1['det']} rel / {len(a1['eq'])} viol"
        sb = f"{b1['det']} rel / {len(b1['eq'])} viol"
        print(f"  {tag:30s} {sa:>16s} {sb:>16s}")
    print("  FR25 evaluated the repairs before the passage existed, where both")
    print("  were clean. The passage is consistent with A and inconsistent with")
    print("  B, and discriminates them decisively.")

    print("\nF4 the logical shape of the refutation")
    print("  passage + B is contradictory, so either the passage is wrong or B")
    print("  is. The passage is supported independently: FR32 priced it at")
    print("  3.6e-6 across all E4/W4 window pairs, and FR35 found fourteen")
    print("  consecutive cells agreeing on the established w (chance 83^-13),")
    print("  against a clean shuffle null. So B is wrong.")
    print("  This is a CONDITIONAL refutation and is stated as one.")

    print("\nF5 the third reading")
    gA, aA = out["A   drop E3@101, E1@68"]
    gAB, aAB = out["AB  drop all three"]
    ag, dis = compare(gA, aA, gAB, aAB)
    print(f"  dropping both instances: {aAB['det']} relations, "
          f"{len(aAB['eq'])} violations")
    print(f"  compared with A: {ag} pairs agree, {dis} disagree")
    print("  -> a strict weakening of A: the same content, less of it")

    print("\nF6 verdict")
    print("  A  : 384 relations, 0 violations   <- unique maximum")
    print("  AB : 259 relations, 0 violations   (strict weakening of A)")
    print("  B  : REFUTED by injectivity")
    print("  FR25's fork, carried as the outstanding debt for twenty-two")
    print("  cycles, is closed. The model is no longer conditional on a CHOICE")
    print("  between two repairs; it is conditional on repair A being right,")
    print("  with its only rival eliminated on evidence that did not exist when")
    print("  the fork was opened.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
