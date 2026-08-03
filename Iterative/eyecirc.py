#!/usr/bin/env python3
"""
eyecirc -- correcting a circular measurement, and re-pricing the conclusion
that rested on it. Read-only.

THE ERROR. FR35 reported that the widened skeleton makes the FR32/33 passage
"far better attested" -- fourteen consecutive cells agreeing on w = 54, chance
83^-13. That measurement is CIRCULAR. The widened skeleton was built by adding
the passage's own cells as constraints, so those cells agree by construction.
Nine of the fourteen are constraints being asked whether they hold.

THE HONEST MEASURE. On the skeleton built WITHOUT the passage, exactly five of
its cells are informative -- offsets 1, 7, 10, 11, 12 -- and all five equal the
independently established w = 54. That is FR32's original figure: 83^-5 per
alignment, 3.6e-6 across all 14,280 E4/W4 window pairs. Adding part of the
passage never makes further cells testable, because the added cells RECRUIT
glyphs rather than expose them; leave-one-cell-out confirms the same five and
predicts all five correctly.

WHY IT MATTERS. FR47 refuted repair B by observing that passage + B is
contradictory and citing the passage's support. It cited 83^-13. The correct
figure is 3.6e-6 -- still strong, but seven orders of magnitude weaker, and a
conclusion should not rest on an inflated number even when it survives the
correction.

IT DOES SURVIVE, and the corrected framing is cleaner. Repair A requires one
three-pair skeleton match (E1@68) to be spurious: roughly 1 in 600. Repair B
requires a different three-pair match (E4@51) to be spurious AND the passage to
be spurious as well, since B contradicts it: roughly 1 in 600 times 3.6e-6.
The likelihood ratio favours A by about 2.8e5.
"""

import json, os, sys
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyerepair2", "eyeaudit", "eyestamp", "eyeh1", "eyeind", "eyenull",
          "eyeloo", "eyerepair", "eyeinject", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyeaudit as EA                      # noqa: E402
import iso_relax as IR                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "w": 54, "skeleton_match_odds": 600.0}

def setup(corpus_path, atlas_path):
    cts, labels, Lx, ctx, pool, _ = EA.load(corpus_path, atlas_path)
    BR = (Lx["East 3"], 101); A1 = (Lx["East 1"], 68)
    red = [p for p in pool
           if not any((p.m1, p.p1) == k or (p.m2, p.p2) == k for k in (BR, A1))]
    return cts, labels, Lx, ctx, pool, red

def passage_cells(cts, Lx, gf_analysis, offsets=range(20)):
    """which passage offsets are informative under a given skeleton, and what
    value they give"""
    E4, W4 = Lx["East 4"], Lx["West 4"]
    D = gf_analysis["delta"]
    comp = {g: i for i, c in enumerate(gf_analysis["comps"]) for g in c}
    out = []
    for i in offsets:
        if 28 + i >= len(cts[E4]) or 29 + i >= len(cts[W4]): break
        x = cts[E4][28 + i]; y = cts[W4][29 + i]
        if x == y or x not in comp or y not in comp or comp[x] != comp[y]:
            continue
        out.append((i, (D[y] - D[x] - 1) % N))
    return out

def held_out(cts, ctx, Lx, red, added):
    gf = EA.build(cts, ctx, Lx, red, cells=added)
    if gf is None: return None
    a = EA.analyse(gf)
    cells = passage_cells(cts, Lx, a)
    return a["det"], [(i, w) for i, w in cells if i not in added]

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: the circularity, the honest count, held-out prediction")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    cts, labels, Lx, ctx, pool, red = setup(corpus, atlas)

    gf0 = EA.build(cts, ctx, Lx, red, cells=[])
    a0 = EA.analyse(gf0)
    c0 = passage_cells(cts, Lx, a0)
    check("pre-passage skeleton reproduces", a0["det"] == 223, f"({a0['det']})")
    check("exactly five passage cells are informative without the passage",
          len(c0) == 5, f"({[i for i,_ in c0]})")
    check("and all five give the established w",
          all(w == PREREG["w"] for _, w in c0), f"({[w for _,w in c0]})")

    gf1 = EA.build(cts, ctx, Lx, red)
    a1 = EA.analyse(gf1)
    c1 = passage_cells(cts, Lx, a1)
    check("WITH the passage, fourteen cells 'agree' — the circular figure",
          len(c1) == 14, f"({len(c1)})")
    added = set(EA.CELLS)
    check("nine of those fourteen were themselves the constraints",
          len([i for i, _ in c1 if i in added]) >= 9,
          f"({len([i for i,_ in c1 if i in added])} of {len(c1)})")

    # leave-one-cell-out
    okc = n = 0
    for i in EA.CELLS:
        gf = EA.build(cts, ctx, Lx, red, cells=[c for c in EA.CELLS if c != i])
        if gf is None: continue
        a = EA.analyse(gf)
        cc = dict(passage_cells(cts, Lx, a, [i]))
        if i in cc:
            n += 1
            if cc[i] == PREREG["w"]: okc += 1
    check("leave-one-cell-out predicts every testable cell", n > 0 and okc == n,
          f"({okc}/{n})")

    c = json.load(open(corpus))
    cc2 = [list(x) for x in c["ciphertexts"]]
    r = IR.relax(cc2, N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard", (r.linked_strict, r.distinct_strict, len(r.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    cts, labels, Lx, ctx, pool, red = setup(corpus_path, atlas_path)
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    print("\nC1 the circular measurement, exhibited")
    for tag, cells in (("skeleton WITHOUT the passage", []),
                       ("skeleton WITH the passage", EA.CELLS)):
        gf = EA.build(cts, ctx, Lx, red, cells=cells)
        a = EA.analyse(gf)
        cc = passage_cells(cts, Lx, a)
        added = set(cells)
        own = [i for i, _ in cc if i in added]
        print(f"  {tag}")
        print(f"    {a['det']} relations, informative passage cells: "
              f"{[i for i,_ in cc]}")
        print(f"    of which were themselves constraints: {own}")
    print("  -> FR35's fourteen-cell figure counts nine cells that were the")
    print("     constraints. It is withdrawn.")

    print("\nC2 the honest support, and it cannot be improved")
    print(f"  {'cells added':22s} {'relations':>10s} {'held-out testable':>18s} "
          f"{'agree':>6s}")
    for tag, sub in (("none", []), ("offsets 0-3", [0, 1, 2, 3]),
                     ("offsets 0-6", [0, 1, 2, 3, 5, 6]),
                     ("offsets 0-9", [0, 1, 2, 3, 5, 6, 7, 8, 9])):
        r = held_out(cts, ctx, Lx, red, sub)
        if r is None: continue
        det, out = r
        print(f"  {tag:22s} {det:10d} {len(out):18d} "
              f"{sum(1 for _,w in out if w == PREREG['w']):6d}")
    print("  adding part of the passage never makes NEW cells testable: the")
    print("  added cells recruit glyphs rather than expose them")

    print("\nC3 leave-one-cell-out")
    okc = n = 0; fails = []
    for i in EA.CELLS:
        gf = EA.build(cts, ctx, Lx, red, cells=[c for c in EA.CELLS if c != i])
        if gf is None: continue
        a = EA.analyse(gf)
        cc = dict(passage_cells(cts, Lx, a, [i]))
        if i in cc:
            n += 1
            if cc[i] == PREREG["w"]: okc += 1
            else: fails.append((i, cc[i]))
    print(f"  testable when held out: {n}; predicted correctly: {okc}; "
          f"failures: {fails if fails else 'none'}")
    tot = len(cts[Lx["East 4"]]) * len(cts[Lx["West 4"]])
    print(f"  chance for {okc} cells to hit the specific value {PREREG['w']}: "
          f"83^-{okc} = {83.0**-okc:.2e}")
    print(f"  across {tot:,} E4/W4 window pairs: {tot*83.0**-okc:.2e}")

    print("\nC4 re-pricing FR47's refutation of repair B")
    p_pass = tot * 83.0 ** -okc
    p_skel = 1.0 / PREREG["skeleton_match_odds"]
    print(f"  repair A requires: E1@68 spurious            ~ {p_skel:.2e}")
    print(f"  repair B requires: E4@51 spurious            ~ {p_skel:.2e}")
    print(f"                 AND the passage spurious      ~ {p_pass:.2e}")
    print(f"  likelihood ratio favouring A: {p_skel/(p_skel*p_pass):.1e}")
    print("  -> FR47's conclusion SURVIVES the correction, and on a cleaner")
    print("     footing: it is now a comparison of what each repair must")
    print("     assert, rather than an appeal to one inflated number.")

    print("\nC5 what this changes")
    print("  FR35's claim that the widened skeleton makes the passage 'far")
    print("  better attested' is withdrawn — the skeleton cannot corroborate a")
    print("  passage it was built from. The passage's support is unchanged at")
    print("  FR32's original 3.6e-6, which is where it has actually stood since")
    print("  cycle 32. The repair fork stays closed.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
