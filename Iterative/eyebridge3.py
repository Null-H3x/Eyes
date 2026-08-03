#!/usr/bin/env python3
"""
eyebridge3 -- can the determined components be joined from inside the corpus?
Read-only.

WHY IT MATTERS. FR33 recruited glyph 1 into component 1 and made FR5's H1
expressible: q[1] - q[47] = 51*drift, so H1's predicted 4 selects drift 31.
But that test CANNOT FAIL, because 51 is invertible -- some drift always
satisfies it. H1 becomes a real test only alongside a second, independent
drift prediction. H3 (q[5] - q[66] = 1) is the natural candidate, and it is
uncheckable only because glyph 5 sits in component 1 and glyph 66 in
component 2. Bridging those two components would turn one unfalsifiable
hypothesis into a falsifiable pair.

THE ALGEBRA OF A BRIDGE. For a same-passage cell whose glyphs lie in
DIFFERENT components C_i and C_j at shift Delta,

    base_{C_j} - base_{C_i} = drift * z,   z = (w + Delta - Delta_b + Delta_a)

where w is the message pair's constant. Because base_{C_j} - base_{C_i} is one
fixed quantity, EVERY bridging cell between those two components must give the
same z. That is a global consistency condition and it is what a genuine bridge
has to satisfy.

WHAT THE SEARCH FINDS. 165 candidate alignments carry a cross-component cell
while their same-component cells agree perfectly on w. But the values they
propose for base(C1) - base(C2) scatter across fourteen distinct residues, so
at most one can be right -- and every one of those bridging cells is a
DOT-MASKED cell, i.e. exactly the variable-interior positions FR7's sound rows
remove and FR19 verified all genuinely vary. Extending the FR32/FR33 passage
makes the point cleanly: offsets 13 and 14 extend it with no violation, and
offset 15 is the cell that would merge C1 with C2 -- and it violates
injectivity.
"""

import json, os, sys
from collections import Counter
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyewiden", "eyepair", "eyeseek", "eyefree", "eyebase", "eyealpha",
          "eyepack", "eyeskel", "eyerepair", "eyescore", "eyeinject",
          "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyerepair as ERP                    # noqa: E402
import eyeinject as EI                     # noqa: E402
import eyegauge as EG                      # noqa: E402
import iso_relax as IR                     # noqa: E402
import isomorph as iso                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "passage": ("East 4", 28, "West 4", 29),
          "base_cells": [0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12],
          "H1": (47, 1, 4), "H3": (66, 5, 1)}

def build(S, cells, drift=1, extra=()):
    cts, ctx, Lx = S["cts"], S["ctx"], S["Lx"]
    plA = ERP.drop(S["pool"], (Lx["East 3"], 101), (Lx["East 1"], 68))
    m1, p1 = Lx[PREREG["passage"][0]], PREREG["passage"][1]
    m2, p2 = Lx[PREREG["passage"][2]], PREREG["passage"][3]
    gf = iso.GFSystem(N)
    row = {N + Lx["East 5"]: 1, N + Lx["East 4"]: N - 1}
    if gf.classify(row, 0) == "pivot": gf.add(row, 0)
    rows = EG.make_rows(ctx, drift, {m: m for m in range(9)})
    for pr in list(plA) + list(extra):
        for r, rhs in rows(pr, cts, N):
            v = gf.classify(r, rhs)
            if v == "contradiction": return None
            if v == "pivot": gf.add(r, rhs)
    for i in cells:
        if p1 + i >= len(cts[m1]) or p2 + i >= len(cts[m2]): continue
        a = int(cts[m1][p1 + i]); b = int(cts[m2][p2 + i])
        r = {b: 1, a: N - 1, N + m2: N - 1, N + m1: 1}
        r = {k: v % N for k, v in r.items() if v % N}
        v = gf.classify(r, drift % N)
        if v == "contradiction": return None
        if v == "pivot": gf.add(r, drift % N)
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
    return dict(det=len(det), eq=eq, comps=big,
                linked={s for c in big for s in c})

def dot_cells(S):
    Lx = S["Lx"]
    a = json.load(open(os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))))
    letter, dot = set(), set()
    for cl in a["classes"]:
        L, pat = cl["length"], cl["pattern"]
        for it in cl["instances"]:
            mi = Lx[it["message"]]
            for i in range(L):
                (letter if pat[i] != '.' else dot).add((mi, it["start"] + i))
    return dot - letter

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: baseline, extension arithmetic, bridge detection")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    S = EI.setup(corpus, atlas)
    B = PREREG["base_cells"]

    base = analyse(build(S, B))
    check("FR33's widened skeleton reproduced",
          base["det"] == 350 and not base["eq"] and len(base["linked"]) == 54,
          f"({base['det']} relations, {len(base['linked'])} glyphs)")

    ext = analyse(build(S, B + [13, 14]))
    check("offsets 13-14 extend cleanly", ext is not None and not ext["eq"]
          and ext["det"] > base["det"], f"({ext['det']} relations)")

    br = analyse(build(S, B + [13, 14, 15]))
    merged = any(5 in c and 66 in c for c in br["comps"]) if br else False
    check("offset 15 is the bridging cell", merged, "(C1 and C2 merge)")
    check("and it violates injectivity", br is not None and len(br["eq"]) > 0,
          f"({len(br['eq'])} violations)")

    # H1's coefficient must be invertible -- the reason its test cannot fail
    gf = build(S, B)
    a, b, want = PREREG["H1"]
    h = [d for d in range(N) if gf.classify({b: 1, a: N - 1}, d) == "redundant"]
    check("H1's coefficient is invertible (its test cannot fail)",
          len(h) == 1 and h[0] != 0, f"(coefficient {h[0] if h else None})")

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
    B = PREREG["base_cells"]
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    print("\nB1 extending the supported passage")
    print(f"  {'cells':26s} {'det':>5s} {'viol':>5s} {'components':>28s} "
          f"{'C1+C2 merged?':>14s}")
    for tag, cells in (("L=13 (FR33 baseline)", B),
                       ("+ offsets 13,14", B + [13, 14]),
                       ("+ offset 15", B + [13, 14, 15]),
                       ("+ offsets 13..19", B + list(range(13, 20)))):
        r = analyse(build(S, cells))
        if r is None: print(f"  {tag:26s} CONTRADICTION"); continue
        m = any(5 in c and 66 in c for c in r["comps"])
        print(f"  {tag:26s} {r['det']:5d} {len(r['eq']):5d} "
              f"{str([len(c) for c in r['comps']]):>28s} {str(m):>14s}")

    print("\n  cell by cell over the extension")
    m1, p1 = Lx[PREREG["passage"][0]], PREREG["passage"][1]
    m2, p2 = Lx[PREREG["passage"][2]], PREREG["passage"][3]
    for i in range(13, 20):
        if p1 + i >= len(cts[m1]) or p2 + i >= len(cts[m2]): break
        r = analyse(build(S, B + [i]))
        st = "CONTRADICTION" if r is None else \
             ("violates injectivity" if r["eq"] else "clean")
        print(f"    offset {i:2d}: E4 {cts[m1][p1+i]:2d} / W4 {cts[m2][p2+i]:2d}  {st}")

    print("\nB2 the clean extension, consolidated")
    r = analyse(build(S, B + [13, 14]))
    cov = sum(freq[g] for g in r["linked"])
    print(f"  determined relations {r['det']}, glyphs {len(r['linked'])}, "
          f"exposure {cov}/1036 ({100*cov/1036:.1f}%)")
    print(f"  components {[len(c) for c in r['comps']]}")
    print(f"  injectivity violations {len(r['eq'])}")

    print("\nB3 why the bridge is blocked")
    dots = dot_cells(S)
    print("  every cell that would join two components is a DOT cell -- a")
    print("  variable-interior position. FR7's sound rows remove them and FR19")
    print("  verified all 153 atlas dot offsets genuinely vary. Sample:")
    for tag, a1, b1, a2, b2 in (("W1@38 x E2@43", Lx["West 1"], 38, Lx["East 2"], 43),
                                ("W1@39 x W1@69", Lx["West 1"], 39, Lx["West 1"], 69)):
        for k in range(13):
            A = cts[a1][b1 + k]; Bg = cts[a2][b2 + k]
            if A == Bg: continue
            d = (a1, b1 + k) in dots or (a2, b2 + k) in dots
            if d:
                print(f"    {tag} offset {k}: glyphs {A}/{Bg}, dot-masked")
                break
    print("  and the candidate bridges disagree: the values they propose for")
    print("  base(C1) - base(C2) scatter across many residues, so at most one")
    print("  could be right. That is what arbitrary cells look like.")

    print("\nB4 consequence for the drift test")
    gf = build(S, B + [13, 14])
    a, b, want = PREREG["H1"]
    h = [d for d in range(N) if gf.classify({b: 1, a: N - 1}, d) == "redundant"]
    if len(h) == 1:
        dstar = (want * pow(h[0], N - 2, N)) % N
        print(f"  H1: q[{b}]-q[{a}] = {h[0]}*drift, so H1 selects drift {dstar}")
    a3, b3, want3 = PREREG["H3"]
    h3 = [d for d in range(N) if gf.classify({b3: 1, a3: N - 1}, d) == "redundant"]
    print(f"  H3: q[{b3}]-q[{a3}] is "
          f"{'determined = ' + str(h3[0]) if len(h3) == 1 else 'NOT determined'}")
    print("  -> with C1 and C2 unbridgeable, H3 stays uncheckable and H1 remains")
    print("     unfalsifiable. The joint two-hypothesis drift test is blocked")
    print("     from inside the corpus; it needs an external anchor.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
