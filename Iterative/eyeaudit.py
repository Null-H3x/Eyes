#!/usr/bin/env python3
"""
eyeaudit -- rebuilding the entire model in one pass from the raw corpus, and
exhibiting exactly what it determines. Read-only.

WHY THIS CYCLE. The model was assembled across forty-five reports by a
succession of instruments, and several of its steps were later corrected
(FR32's forced-base count, FR33's regression, FR35's greedy extension) or
overturned outright (FR41 withdrawn in FR42). Every published figure has been
verified in the cycle that produced it; none has been verified against a
rebuild that starts from the corpus and applies every step in order. That is a
test the model could fail, and after this many corrections it should be run.

WHAT IS REBUILT. Baseline guard, sound pool, repair A, the FR32/33 passage
with its variable-interior cell excluded, the evidence-forced E4/E5 merge, and
then every published number: determined relations, injectivity, glyph count,
component sizes, corpus exposure, the gauge ladder, and both opening
contradictions.

WHAT IS EXHIBITED. The Delta tables themselves -- the actual content of the
result. Inside a component q[s] = base_C + drift*Delta_s, with the Delta values
fixed by the corpus and base_C and the drift not. That makes the
success-criterion question concrete: two anchors in component 1 determine 25
glyphs and 31.2% of positions, ten anchors determine 56 glyphs and 74.1%, and
the output is 768 plaintext VALUES in 0..82 rather than a reading.
"""

import json, os, sys
from collections import Counter
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyestamp", "eyeh1", "eyeind", "eyenull", "eyeloo", "eyerepair",
          "eyeinject", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyegauge as EG                      # noqa: E402
import iso_relax as IR                     # noqa: E402
import isomorph as iso                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

GI = {"T1": 0, "T2": 1, "T3": 2}
PUBLISHED = {"guard": (22, 19, 16), "pool": 83, "repaired": 67,
             "relations": 384, "violations": 0, "glyphs": 56,
             "components": [25, 11, 7, 3, 2, 2, 2, 2, 2],
             "exposure": 74.1, "gauge": (0, 0, 82)}
CELLS = [0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

def load(corpus_path, atlas_path):
    c = json.load(open(corpus_path))
    cts = [list(x) for x in c["ciphertexts"]]; labels = c["message_labels"]
    Lx = {l: i for i, l in enumerate(labels)}
    ctx = EG.build_context(cts, labels, atlas_path)
    pool = ctx["apairs"] + ctx["strict"]
    br = (Lx["East 3"], 101); a1 = (Lx["East 1"], 68)
    red = [p for p in pool
           if not any((p.m1, p.p1) == k or (p.m2, p.p2) == k for k in (br, a1))]
    return cts, labels, Lx, ctx, pool, red

def build(cts, ctx, Lx, red, drift=1, group=None, extra=(), cells=CELLS):
    g = group or {m: m for m in range(9)}
    E4, W4 = Lx["East 4"], Lx["West 4"]
    gf = iso.GFSystem(N)
    row = {N + g[Lx["East 5"]]: 1, N + g[Lx["East 4"]]: N - 1}
    row = {k: v for k, v in row.items() if v}
    if row and gf.classify(row, 0) == "pivot": gf.add(row, 0)
    rows = EG.make_rows(ctx, drift, g)
    for pr in list(red) + list(extra):
        for rw, rhs in rows(pr, cts, N):
            k = gf.classify(rw, rhs)
            if k == "contradiction": return None
            if k == "pivot": gf.add(rw, rhs)
    for i in cells:
        a = int(cts[E4][28 + i]); b = int(cts[W4][29 + i])
        rw = {b: 1, a: N - 1}
        if g[E4] != g[W4]:
            rw[N + g[W4]] = N - 1; rw[N + g[E4]] = 1
        rw = {k: v % N for k, v in rw.items() if v % N}
        k = gf.classify(rw, drift % N)
        if k == "contradiction": return None
        if k == "pivot": gf.add(rw, drift % N)
    return gf

def analyse(gf):
    syms = sorted(v for v in gf.solve() if v < N)
    det, eq = [], []
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
    D = {}
    for c in big:
        anc = c[0]
        for s in c:
            h = [d for d in range(N)
                 if gf.classify({s: 1, anc: N - 1}, d) == "redundant"]
            D[s] = h[0] if len(h) == 1 else 0
    return dict(det=len(det), eq=eq, comps=big,
                linked={s for c in big for s in c}, delta=D)

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: the end-to-end reproduction IS the gate")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    cts, labels, Lx, ctx, pool, red = load(corpus, atlas)

    r = IR.relax(cts, N, seed=0)
    check("baseline guard reproduces",
          (r.linked_strict, r.distinct_strict, len(r.pins)) == PUBLISHED["guard"],
          f"({(r.linked_strict, r.distinct_strict, len(r.pins))})")
    check("sound pool size reproduces", len(pool) == PUBLISHED["pool"],
          f"({len(pool)})")
    check("repair A removes the expected pairs",
          len(red) == PUBLISHED["repaired"], f"({len(pool)} -> {len(red)})")

    gf = build(cts, ctx, Lx, red)
    check("E4/E5 merge is admissible under repair A", gf is not None)
    a = analyse(gf)
    check("determined relations reproduce", a["det"] == PUBLISHED["relations"],
          f"({a['det']} vs {PUBLISHED['relations']})")
    check("injectivity clean", len(a["eq"]) == PUBLISHED["violations"],
          f"({len(a['eq'])})")
    check("glyph count reproduces", len(a["linked"]) == PUBLISHED["glyphs"],
          f"({len(a['linked'])})")
    check("component sizes reproduce",
          [len(c) for c in a["comps"]] == PUBLISHED["components"],
          f"({[len(c) for c in a['comps']]})")

    freq = Counter(g for m in cts for g in m)
    cov = sum(freq[g] for g in a["linked"])
    check("corpus exposure reproduces",
          abs(100 * cov / 1036 - PUBLISHED["exposure"]) < 0.15,
          f"({100*cov/1036:.1f}%)")

    gauges = {"1": {m: 0 for m in range(9)},
              "3": {Lx[m]: GI[t] for t, ms in EG.TRIPLETS.items() for m in ms},
              "9": {m: m for m in range(9)}}
    got = tuple(sum(1 for d in range(1, N)
                    if build(cts, ctx, Lx, red, d, g) is not None)
                for g in gauges.values())
    check("gauge ladder reproduces", got == PUBLISHED["gauge"], f"({got})")

    T1o = EG.opening_pairs(labels, EG.OPENINGS[:1])
    T3o = EG.opening_pairs(labels, EG.OPENINGS[1:])
    n1 = sum(1 for d in range(1, N)
             if build(cts, ctx, Lx, red, d, extra=T1o) is not None)
    n3 = sum(1 for d in range(1, N)
             if build(cts, ctx, Lx, red, d, extra=T3o) is not None)
    check("both openings still contradict", n1 == 0 and n3 == 0, f"({n1}, {n3})")

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- the published model does not reproduce")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    cts, labels, Lx, ctx, pool, red = load(corpus_path, atlas_path)
    gf = build(cts, ctx, Lx, red)
    a = analyse(gf)
    freq = Counter(g for m in cts for g in m)
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    print("\nA1 the reproduction, step by step")
    print(f"  sound pool                  : {len(pool)} pairs")
    print(f"  repair A (E3@101, E1@68 out): {len(red)} pairs")
    print(f"  FR32/33 passage             : {len(CELLS)} cells "
          f"(offset 4 excluded, variable interior)")
    print(f"  E4/E5 merge                 : admissible")
    print(f"  determined relations        : {a['det']}")
    print(f"  injectivity violations      : {len(a['eq'])}")
    print(f"  glyphs in components        : {len(a['linked'])}")
    print(f"  component sizes             : {[len(c) for c in a['comps']]}")
    cov = sum(freq[g] for g in a["linked"])
    print(f"  corpus exposure             : {cov}/1036 = {100*cov/1036:.1f}%")
    print("  every published figure reproduces from the raw corpus in one pass")

    print("\nA2 the deliverable: the Delta tables")
    print("  inside a component, q[s] = base_C + drift * Delta_s;")
    print("  the Delta values are fixed by the corpus, base_C and drift are not")
    for i, c in enumerate(a["comps"]):
        if len(c) < 3: continue
        cv = sum(freq[g] for g in c)
        print(f"\n  component {i+1}: {len(c)} glyphs, {cv} positions "
              f"({100*cv/1036:.1f}%)")
        line = [f"{g:2d}:{a['delta'][g]:2d}" for g in c]
        for j in range(0, len(line), 8):
            print("     " + "  ".join(line[j:j + 8]))

    print("\nA3 what anchors would buy")
    c1 = a["comps"][0]
    cv1 = sum(freq[g] for g in c1)
    print(f"  2 anchors in component 1 (fixing base_C1 and the drift):")
    print(f"    {len(c1)} glyphs, {cv1} positions ({100*cv1/1036:.1f}%)")
    n = len(a["comps"])
    print(f"  + 1 anchor per remaining component ({n-1} more, {n+1} total):")
    print(f"    {len(a['linked'])} glyphs, {cov} positions ({100*cov/1036:.1f}%)")
    print(f"  FR27's packing tail makes the last anchor redundant (9 anchors")
    print(f"  leave 44 enumerable completions)")

    print("\nA4 what they would not buy")
    print(f"  the output is {cov} plaintext VALUES in 0..82. FR36, FR39 and FR40")
    print(f"  established the effective inventory exceeds ~60, so those values")
    print(f"  are not letters of a small alphabet, and the remaining")
    print(f"  {1036-cov} positions cannot be filled by context.")
    print("  Recovering C yields a token stream, not a reading. That is the")
    print("  success-criterion question in concrete numbers, and it is a")
    print("  question about the project's goal rather than about the corpus.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
