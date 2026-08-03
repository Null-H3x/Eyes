#!/usr/bin/env python3
"""
eyewiden -- feeding FR32's supported passage into the pool, and the first
widening of the determined skeleton in the series. Read-only.

FR31 showed every internal route to enlarging the determined set was closed.
FR32 then found and supported one new same-passage region -- East 4 @ 28 x
West 4 @ 29 at shift +1, whose five informative cells all equal the
independently established w = 54 for that message pair (chance 3.6e-6). This
cycle feeds it in.

THE VARIABLE-INTERIOR CELL. Adding all thirteen cells as full-span rows
recruits every unknown glyph in the span but produces three injectivity
violations. Cell-by-cell, exactly ONE cell -- offset 4 -- violates on its own;
the other twelve are clean together. That is the structure FR6/FR7 established
for the atlas classes and FR19 verified exhaustively: same-passage regions
carry variable-interior cells, encoded in the atlas as pattern dots, and all
153 atlas dot offsets genuinely vary. A newly found passage has no published
pattern, so which cells are constant has to be determined, and injectivity is
the only available tool.

WHAT IT BUYS AND WHAT IT COSTS. Determination rises 223 -> 350, glyphs 47 ->
54, corpus exposure 64.6% -> 72.3%, and the largest component grows from 19 to
24 glyphs. Injectivity stays clean and the gauge ladder is unchanged. But the
T1 opening, which the repaired pool accepted at 82/82 drifts (FR26), now
contradicts at 0/82 -- so the widening forces the same stamped-header reading
onto T1 that FR29 proposed for T3.
"""

import json, os, sys
from collections import Counter
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyepair", "eyeseek", "eyefree", "eyebase", "eyealpha", "eyepack",
          "eyeskel", "eyerepair", "eyescore", "eyeinject", "eyegauge",
          "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyerepair as ERP                    # noqa: E402
import eyeinject as EI                     # noqa: E402
import eyegauge as EG                      # noqa: E402
import iso_relax as IR                     # noqa: E402
import isomorph as iso                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "passage": ("East 4", 28, "West 4", 29, 13),
          "H1": {"pair": (47, 1), "diff": 4}}

def build(S, pool, cells, drift=1, group=None, extra=()):
    cts, ctx, Lx = S["cts"], S["ctx"], S["Lx"]
    g = group or {m: m for m in range(9)}
    m1, p1, m2, p2, L = (Lx[PREREG["passage"][0]], PREREG["passage"][1],
                         Lx[PREREG["passage"][2]], PREREG["passage"][3],
                         PREREG["passage"][4])
    gf = iso.GFSystem(N)
    row = {N + g[Lx["East 5"]]: 1, N + g[Lx["East 4"]]: N - 1}
    row = {k: v for k, v in row.items() if v}
    if row and gf.classify(row, 0) == "pivot": gf.add(row, 0)
    rows = EG.make_rows(ctx, drift, g)
    for pr in list(pool) + list(extra):
        for r, rhs in rows(pr, cts, N):
            v = gf.classify(r, rhs)
            if v == "contradiction": return None
            if v == "pivot": gf.add(r, rhs)
    for i in cells:
        a = int(cts[m1][p1 + i]); b = int(cts[m2][p2 + i])
        r = {b: 1, a: N - 1}
        if g[m1] != g[m2]:
            r[N + g[m2]] = N - 1; r[N + g[m1]] = 1
        r = {k: v % N for k, v in r.items() if v % N}
        v = gf.classify(r, (drift * (p2 - p1)) % N)
        if v == "contradiction": return None
        if v == "pivot": gf.add(r, (drift * (p2 - p1)) % N)
    return gf

def analyse(gf):
    if gf is None: return None
    syms = sorted(v for v in gf.solve() if v < N)
    det = []; eq = []
    for a, b in combinations(syms, 2):
        k = gf.classify({b: 1, a: N - 1}, 0)
        if k == "pivot": continue
        det.append((a, b))
        if k == "redundant": eq.append((a, b))
    par = {s: s for s in syms}
    def f(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for a, b in det: par[f(a)] = f(b)
    comps = {}
    for s in syms: comps.setdefault(f(s), []).append(s)
    big = sorted((sorted(c) for c in comps.values() if len(c) > 1),
                 key=len, reverse=True)
    linked = {s for c in big for s in c}
    return dict(det=len(det), eq=eq, comps=big, linked=linked)

def clean_cells(S, pool, L=13):
    out = []
    for i in range(L):
        r = analyse(build(S, pool, [i]))
        if r is not None and not r["eq"]: out.append(i)
    return out

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: cell selection, injectivity rail, recruitment accounting")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    S = EI.setup(corpus, atlas)
    Lx = S["Lx"]
    plA = ERP.drop(S["pool"], (Lx["East 3"], 101), (Lx["East 1"], 68))

    base = analyse(build(S, plA, []))
    check("baseline reproduces FR26's skeleton",
          base["det"] == 223 and not base["eq"] and len(base["comps"][0]) == 19,
          f"({base['det']} determined, {len(base['eq'])} violations)")

    full = analyse(build(S, plA, list(range(13))))
    check("full-span rows violate injectivity (over-assertion)",
          full is not None and len(full["eq"]) > 0,
          f"({len(full['eq'])} violations)")

    cc = clean_cells(S, plA)
    check("exactly one cell is individually unsafe", len(cc) == 12,
          f"(clean cells {cc})")

    kept = analyse(build(S, plA, cc))
    check("the twelve clean cells are jointly clean",
          kept is not None and not kept["eq"], f"({len(kept['eq'])} violations)")
    check("and they recruit glyphs", len(kept["linked"]) > len(base["linked"]),
          f"({len(base['linked'])} -> {len(kept['linked'])})")

    n9 = sum(1 for d in range(1, N)
             if build(S, plA, cc, d, {m: m for m in range(9)}) is not None)
    n1 = sum(1 for d in range(1, N)
             if build(S, plA, cc, d, {m: 0 for m in range(9)}) is not None)
    check("gauge ladder unchanged (9 gauges live, 1 gauge dead)",
          n9 == 82 and n1 == 0, f"({n9}/82, {n1}/82)")

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
    Lx, cts, labels = S["Lx"], S["cts"], S["labels"]
    freq = Counter(g for m in cts for g in m)
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")
    plA = ERP.drop(S["pool"], (Lx["East 3"], 101), (Lx["East 1"], 68))

    print("\nW1 the passage, cell by cell")
    m1, p1, m2, p2, L = (Lx["East 4"], 28, Lx["West 4"], 29, 13)
    base = analyse(build(S, plA, []))
    for i in range(L):
        a = cts[m1][p1 + i]; b = cts[m2][p2 + i]
        r = analyse(build(S, plA, [i]))
        st = "CONTRADICTION" if r is None else \
             ("violates injectivity" if r["eq"] else "clean")
        rec = sorted(r["linked"] - base["linked"]) if r else []
        print(f"  offset {i:2d}: E4 {a:2d} / W4 {b:2d}  {st:22s} recruits {rec}")
    cc = clean_cells(S, plA)
    print(f"  individually clean cells: {cc}")

    print("\nW2 the widened skeleton")
    kept = analyse(build(S, plA, cc))
    print(f"  {'':14s} {'determined':>11s} {'violations':>11s} {'glyphs':>7s} "
          f"{'exposure':>9s}")
    for tag, r in (("baseline", base), ("+ passage", kept)):
        cov = sum(freq[g] for g in r["linked"])
        print(f"  {tag:14s} {r['det']:11d} {len(r['eq']):11d} "
              f"{len(r['linked']):7d} {100*cov/1036:8.1f}%")
    print(f"  components: {[len(c) for c in kept['comps']]}")
    print(f"  newly recruited glyphs: "
          f"{sorted(kept['linked'] - base['linked'])}")

    print("\nW3 rails")
    GI = {"T1": 0, "T2": 1, "T3": 2}
    for gname, g in (("1 gauge", {m: 0 for m in range(9)}),
                     ("3 gauges", {Lx[m]: GI[t]
                                   for t, ms in EG.TRIPLETS.items() for m in ms}),
                     ("9 gauges", {m: m for m in range(9)})):
        n = sum(1 for d in range(1, N) if build(S, plA, cc, d, g) is not None)
        print(f"  {gname:10s}: {n:2d}/82")
    T1o = EG.opening_pairs(labels, EG.OPENINGS[:1])
    T3o = EG.opening_pairs(labels, EG.OPENINGS[1:])
    for tag, ex in (("+ T1 openings", T1o), ("+ T3 openings", T3o)):
        n = sum(1 for d in range(1, N) if build(S, plA, cc, d, extra=ex) is not None)
        print(f"  {tag:10s}: {n:2d}/82"
              f"{'   <== REGRESSION: FR26 had 82/82 here' if tag.endswith('T1 openings') and n == 0 else ''}")

    print("\nW4 FR5's H1, now expressible")
    gf = build(S, plA, cc, 1)
    a, b = PREREG["H1"]["pair"]
    h = [d for d in range(N) if gf.classify({b: 1, a: N - 1}, d) == "redundant"]
    if len(h) == 1:
        v = h[0]; want = PREREG["H1"]["diff"]
        dstar = (want * pow(v, N - 2, N)) % N
        print(f"  q[{b}] - q[{a}] = {v} at drift 1, hence {v}*d at drift d")
        print(f"  H1 predicts {want}, which holds at exactly drift d* = {dstar}")
        print("  BUT THE TEST CANNOT FAIL: the coefficient is invertible, so some")
        print("  drift always satisfies H1. Consistency here is NOT support. The")
        print("  value is that H1 is now a specific, falsifiable claim about the")
        print("  drift -- it becomes a real test the moment a second hypothesis")
        print("  or an external anchor pins the drift independently.")
    print("  H3 (q[5]-q[66]=1) stays uncheckable: 5 and 66 are in different")
    print("  components, so their difference is not determined.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
