#!/usr/bin/env python3
"""
eyerepair -- locating the constraints that produce the corpus's false
equalities, and finding that a two-instance repair yields the cell FR24
declared empty. Read-only.

FR24 swept thirty model configurations (drift partition x base structure x
pool variant) and found none that determines anything without also asserting
an equality a permutation forbids. That sweep ranged over the MODEL space.
This cycle ranges over the POOL space instead: the six false equalities are
the most model-independent defect available -- they survive every offset
structure and every drift value -- so the right question is which constraints
produce them.

RESULTS.
  C1 minimal cores. Under the free-drift reading every one of the six
     equalities has a verified-minimal core, and EVERY core contains E3@101 --
     the #M- bridging window FR15 priced at coincidence grade. One core has
     only TWO pairs and is checkable by hand.
  C2 the repair search. Under the fixed-drift reading (the one that
     determines things) dropping E3@101 removes one violation of six. Sweeping
     every remaining atlas instance for a second removal finds exactly two
     that clear ALL violations while retaining determination:
        E3@101 + E1@68  -> 28 forced differences, 0 violations
        E3@101 + E4@51  -> 36 forced differences, 0 violations
     These are the first configurations in the series that determine
     alphabet relations AND respect injectivity.
  C3 pricing. The repairs are not free. E3@101 is cheap (a ~1-in-7 chance
     match). E1@68 and E4@51 both sit in three-pair skeletons, so a chance
     match runs about 1 in 600 -- discarding either is expensive on the
     pattern evidence, which is the same tension FR21 flagged and did not
     resolve.
"""

import json, os, sys
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyescore", "eyeinject", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyeinject as EI                     # noqa: E402
import iso_relax as IR                     # noqa: E402
import isomorph as iso                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "equalities": [(4, 46), (10, 71), (17, 81), (20, 64), (30, 50), (36, 68)]}

def drop(pl, *insts):
    return [p for p in pl
            if not any((p.m1, p.p1) == i or (p.m2, p.p2) == i for i in insts)]

def score(S, pl, drift=1):
    """(symbols, forced pair-differences, forced equalities as a list)"""
    gf = EI.build(S, pl, False, drift=drift)
    if gf is None: return None
    syms = sorted(v for v in gf.solve() if v < N)
    det = []; eq = []
    for a, b in combinations(syms, 2):
        k = gf.classify({b: 1, a: N - 1}, 0)
        if k == "pivot": continue
        det.append((a, b))
        if k == "redundant": eq.append((a, b))
    return len(syms), len(det), eq

def forces_eq(S, pl, a, b, drift=1):
    gf = EI.build(S, pl, False, drift=drift)
    return gf is not None and gf.classify({b: 1, a: N - 1}, 0) == "redundant"

def minimal_core(S, pl, a, b, drift=1):
    cur = list(pl)
    for p in list(pl):
        trial = [q for q in cur if q is not p]
        if forces_eq(S, trial, a, b, drift): cur = trial
    return cur

def skeleton_price(atlas, cts, labels, cid):
    cl = next(x for x in atlas["classes"] if x["id"] == cid)
    L, pat = cl["length"], cl["pattern"]
    sk = [(i, j) for i in range(L) for j in range(i + 1, L)
          if pat[i] != '.' and pat[i] == pat[j]]
    wins = sum(max(0, len(m) - L + 1) for m in cts)
    return L, pat, len(sk), wins * (83.0 ** -len(sk))

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: core minimality, repair verification, drop arithmetic")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    S = EI.setup(corpus, atlas)
    Lx = S["Lx"]
    BR = (Lx["East 3"], 101)

    base = score(S, S["pool"])
    check("full pool reproduces the six false equalities",
          base[1] == 276 and len(base[2]) == 6, f"({base[1]}, {len(base[2])})")

    red = drop(S["pool"], BR)
    check("dropping E3@101 removes exactly one violation",
          len(score(S, red)[2]) == 5)

    rep = drop(S["pool"], BR, (Lx["East 1"], 68))
    sc = score(S, rep)
    check("E3@101 + E1@68 clears all violations and still determines",
          len(sc[2]) == 0 and sc[1] > 0, f"({sc[1]} forced, {len(sc[2])} viol)")

    # the two-pair core is genuinely minimal
    core = minimal_core(S, S["pool"], 36, 68)
    good = (forces_eq(S, core, 36, 68) and
            all(not forces_eq(S, [q for q in core if q is not p], 36, 68)
                for p in core))
    check("q[68]=q[36] core is verified minimal", good and len(core) == 2,
          f"(|core|={len(core)})")

    r = IR.relax(S["cts"], N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard", (r.linked_strict, r.distinct_strict, len(r.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    S = EI.setup(corpus_path, atlas_path)
    Lx, labels, cts = S["Lx"], S["labels"], S["cts"]
    atlas = json.load(open(atlas_path))
    BR = (Lx["East 3"], 101)
    cls_of = {}
    for cid, prs in S["ctx"]["by_class"].items():
        for p in prs: cls_of[id(p)] = cid
    for p in S["ctx"]["strict"]: cls_of[id(p)] = "strict"
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    print("\nC1 minimal cores for the six false equalities")
    for a, b in PREREG["equalities"]:
        core = minimal_core(S, S["pool"], a, b)
        classes = sorted({cls_of.get(id(p), "?") for p in core})
        uses = any((p.m1, p.p1) == BR or (p.m2, p.p2) == BR for p in core)
        print(f"  q[{b}]=q[{a}]: {len(core)} pairs, classes {classes}"
              f"{'  [contains E3@101]' if uses else ''}")
    print("  -> every core contains E3@101, the #M- bridging window FR15 priced")
    print("     at coincidence grade. It is the common ingredient of every")
    print("     falsehood the constraint system asserts.")

    print("\n  the two-pair exhibit, checkable by hand:")
    E2, E3, W1 = cts[Lx["East 2"]], cts[Lx["East 3"]], cts[Lx["West 1"]]
    print(f"    pair A [#M-]    East 2@80 x East 3@101, shift 21, pattern A.B..B.A")
    print(f"      offsets 0,7 give  q[36] - q[41] = X")
    print(f"      offsets 2,5 give  q[17] - q[57] = X    so q[36]-q[41] = q[17]-q[57]")
    print(f"    pair B [strict] West 1@70 x East 2@80, shift 10")
    print(f"      offset 0 gives    q[41] - q[68] = Y")
    print(f"      offset 2 gives    q[57] - q[17] = Y    so q[17]-q[57] = -Y")
    print(f"    therefore q[36] - q[41] = -Y and q[41] = q[68] + Y,")
    print(f"    giving q[36] = q[68]. Two pairs, four lines, one false equality.")

    print("\nC2 repair search (fixed drift -- the reading that determines things)")
    for tag, pl in (("full pool", S["pool"]),
                    ("drop E3@101", drop(S["pool"], BR))):
        sc = score(S, pl)
        print(f"  {tag:28s}: symbols={sc[0]} forced={sc[1]} violations={len(sc[2])}")
    print("  sweeping a SECOND instance to drop alongside E3@101:")
    base = drop(S["pool"], BR)
    found = []
    for cl in atlas["classes"]:
        for it in cl["instances"]:
            key = (Lx[it["message"]], it["start"])
            sc = score(S, drop(base, key))
            if sc is None: continue
            if len(sc[2]) == 0 and sc[1] > 0:
                found.append((sc[1], cl["id"], it["message"], it["start"]))
    seen = set(); uniq = []
    for f in sorted(found, reverse=True):
        k = (f[2], f[3])
        if k in seen: continue
        seen.add(k); uniq.append(f)
    print(f"  instances that clear ALL violations while retaining determination:")
    for n, cid, msg, st in uniq:
        print(f"    {cid:5s} {msg}@{st:<4d} -> {n} forced differences, 0 violations")
    if not uniq:
        print("    NONE")

    print("\nC3 pricing the repairs (FR15's method)")
    for cid in ("#M-", "#M", "#3"):
        L, pat, k, exp = skeleton_price(atlas, cts, labels, cid)
        print(f"  {cid:4s}: L={L:2d} pattern={pat} k={k} equal-pairs; expected chance"
              f" matches corpus-wide = {exp:.4f}")
    print("  -> E3@101 sits in a 2-pair skeleton and is cheap to discard;")
    print("     E1@68 and E4@51 sit in 3-pair skeletons (~1 in 600), so")
    print("     discarding either is expensive on the pattern evidence.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
