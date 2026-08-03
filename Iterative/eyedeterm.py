#!/usr/bin/env python3
"""
eyedeterm -- measuring what each model actually DETERMINES, and correcting
FR22's reading of injectivity. Read-only.

FR22 reported that injectivity selects FR16's coherent package: of the four
cells in the 2x2 (drift model x bridge instance) only per-triplet drifts with
E3@101 removed showed no forced collisions. This cycle asks the obvious
follow-up question that FR22 did not: how much does each of those cells
DETERMINE? The answer changes the verdict.

THE MEASURE. certified_domain pins the reference symbol to two values and
keeps whatever co-shifts. That is sound when the global rotation is the only
gauge freedom, and unsound otherwise -- FR8 and FR9 both recorded the
principle, and under the per-triplet model there are thirteen free parameters
rather than nine. The gauge-invariant question is per PAIR: is q[b] - q[a] = d
implied by the constraints for exactly one d? That is what "certified" has to
mean, and it is what this instrument counts.

WHAT IT FINDS. The global-drift pool determines 276 pair-differences across 49
symbols -- and is refuted by injectivity. The per-triplet full pool determines
6, which are exactly the six false equalities. The coherent package determines
ZERO. So the package does not satisfy injectivity on positive grounds; it
satisfies it because a system that forces no differences cannot force an
equality. Passing a consistency check by determining nothing is not
corroboration, and FR22 read it as such.
"""

import json, os, sys
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyeinject", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyeinject as EI                     # noqa: E402
import eyereach as ER                      # noqa: E402
import iso_relax as IR                     # noqa: E402
import isomorph as iso                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16}}

def forced_diff(gf, a, b):
    hits = [d for d in range(N) if gf.classify({b: 1, a: N - 1}, d) == "redundant"]
    return hits[0] if len(hits) == 1 else None

def census(gf):
    """sound determination census: pairs with a forced difference, and the
    symbols they involve."""
    syms = sorted(v for v in gf.solve() if v < N)
    det = []
    for a, b in combinations(syms, 2):
        d = forced_diff(gf, a, b)
        if d is not None: det.append((a, b, d))
    involved = {x for a, b, _ in det for x in (a, b)}
    zeros = [(a, b) for a, b, d in det if d == 0]
    return dict(syms=syms, det=det, involved=involved, zeros=zeros)

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: determination measure and the certified_domain discrepancy")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    S = EI.setup(corpus, atlas)

    gG = EI.build(S, S["pool"], False)
    cG = census(gG)
    check("global-drift pool determines many pair-differences",
          len(cG["det"]) > 100, f"({len(cG['det'])} pairs)")
    check("and its forced equalities are the injectivity violations",
          len(cG["zeros"]) == 6, f"({cG['zeros']})")

    gC = EI.build(S, S["red"], True)
    cC = census(gC)
    check("coherent package determines NOTHING", len(cC["det"]) == 0,
          f"({len(cC['det'])} pairs)")
    check("so it cannot force an equality either", len(cC["zeros"]) == 0)

    # the measure discrepancy that motivates this cycle
    dom, _ = ER.certified_domain(gC)
    check("certified_domain over-reports when free parameters exist",
          len(dom) > 0 and len(cC["det"]) == 0,
          f"(claims {len(dom)} symbols, 0 forced differences)")

    r = IR.relax(S["cts"], N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard", (r.linked_strict, r.distinct_strict, len(r.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    S = EI.setup(corpus_path, atlas_path)
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    print("\nC1 determination census (sound: forced pair-differences)")
    print(f"  {'configuration':38s} {'symbols':>8s} {'cert_dom':>9s} "
          f"{'FORCED':>7s} {'involved':>9s} {'equalities':>11s}")
    rowspec = [("global drift, full pool [doctrine]", S["pool"], False),
               ("global drift, reduced", S["red"], False),
               ("per-triplet, full pool", S["pool"], True),
               ("COHERENT package", S["red"], True),
               ("coherent + E4/E5 run merge", S["red"] + [S["merge"]], True)]
    results = {}
    for tag, pl, pt in rowspec:
        gf = EI.build(S, pl, pt)
        if gf is None:
            print(f"  {tag:38s} contradictory"); continue
        cs = census(gf); dom, _ = ER.certified_domain(gf)
        results[tag] = cs
        print(f"  {tag:38s} {len(cs['syms']):8d} {len(dom):9d} "
              f"{len(cs['det']):7d} {len(cs['involved']):9d} "
              f"{len(cs['zeros']):11d}")

    print("\nC2 the correction to FR22")
    print("  FR22 read 'no forced collisions' in the coherent package as")
    print("  injectivity SELECTING that configuration. But the same system")
    print("  forces no differences at all, so it cannot force an equality:")
    print("  it passes the check vacuously. Under the per-triplet FULL pool the")
    print("  only six differences the model determines are exactly the six")
    print("  false equalities -- remove the bridge and both vanish together.")

    print("\nC3 what this costs the doctrine")
    print("  the pin inventory the project carries -- 16 strict pins, and FR7's")
    print("  10 certified / 8 pin-grade -- is computed under the GLOBAL-drift")
    print("  model, which FR21/FR22 refute by injectivity. Under the model that")
    print("  survives, the corpus determines no alphabet relation at all.")
    print("\n  the wall, stated exactly: the models that determine things are")
    print("  refuted, and the model that survives determines nothing. Every")
    print("  configuration in this series has bought consistency with")
    print("  determination, and this is the sharpest form of that trade yet.")

    print("\nC4 methodological note")
    print("  certified_domain perturbs only the global rotation, so it")
    print("  over-reports whenever other gauge freedoms exist: on the coherent")
    print("  package it claims 10 certified symbols in a system with zero forced")
    print("  differences. Determination must be measured per pair, via classify.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
