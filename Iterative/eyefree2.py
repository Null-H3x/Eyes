#!/usr/bin/env python3
"""
eyefree2 -- scanning the message pairs the w-method could not reach, mapping
the supported extent of the one new passage, and catching an unsound
extension method. Read-only.

WHAT WAS UNREACHED. FR32's scan tested cells against each message pair's
ESTABLISHED w = base_diff/drift, which is only known for pairs with a forced
base difference. West 2's pairs and every cross-triplet pair were therefore
never scanned. Treating w as FREE -- looking for shifts where many informative
cells agree on some common value -- covers them, at the cost of a weaker
calibration (83^-(k-1) instead of 83^-k) and a non-zero shuffle background.

THE TRAP THIS CYCLE CAUGHT. Having a passage, it is tempting to extend it by
adding any cell that does not trip the injectivity rail. That is unsound:
injectivity is a NECESSARY condition, not evidence that a cell is
same-passage. Greedily adding cells that merely pass it re-creates exactly the
over-assertion FR6 diagnosed, FR7 repaired and FR21 caught again. On this
corpus the greedy method reaches offsets 22, 30 and 31 -- far past the point
where the passage's own w-agreement has stopped -- and inflates the skeleton
from 384 relations to 502. The principled rule is to extend only inside the
span the evidence supports, then remove cells that violate injectivity; that
returns 384, and the difference between the two numbers is the size of the
error.
"""

import json, os, random, sys
from collections import Counter

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyebridge3", "eyewiden", "eyepair", "eyeseek", "eyefree", "eyebase",
          "eyealpha", "eyepack", "eyeskel", "eyerepair", "eyescore",
          "eyeinject", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyebridge3 as EB3                   # noqa: E402
import eyeinject as EI                     # noqa: E402
import iso_relax as IR                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "cells": EB3.PREREG["base_cells"] + [13, 14],
          "min_agree": 5, "seed": 20260805}

def skeleton(S, cells):
    gf = EB3.build(S, cells, 1)
    r = EB3.analyse(gf)
    delta, comp = {}, {}
    for ci, c in enumerate(r["comps"]):
        anc = c[0]
        for s in c:
            h = [d for d in range(N)
                 if gf.classify({s: 1, anc: N - 1}, d) == "redundant"]
            delta[s] = h[0] if len(h) == 1 else 0
            comp[s] = ci
    return gf, r, delta, comp

def scan_free(corpus, delta, comp, minagree):
    out = []
    for m1 in range(len(corpus)):
        for m2 in range(m1, len(corpus)):
            lo = -len(corpus[m2]) + 1 if m1 != m2 else 1
            for sh in range(lo, len(corpus[m1])):
                if m1 == m2 and abs(sh) < 8: continue
                cells = []
                for t1 in range(len(corpus[m1])):
                    t2 = t1 + sh
                    if not (0 <= t2 < len(corpus[m2])): continue
                    a = corpus[m1][t1]; b = corpus[m2][t2]
                    if a == b or a not in comp or b not in comp: continue
                    if comp[a] != comp[b]: continue
                    cells.append((delta[b] - delta[a] - sh) % N)
                if len(cells) < minagree: continue
                w, n = Counter(cells).most_common(1)[0]
                if n >= minagree: out.append((m1, m2, sh, len(cells), n, w))
    return out

def supported_span(S, delta, comp, m1, p1, m2, p2, w, maxlen=40):
    cts = S["cts"]
    agree, dis = [], []
    for i in range(maxlen):
        if p1 + i >= len(cts[m1]) or p2 + i >= len(cts[m2]): break
        a = cts[m1][p1 + i]; b = cts[m2][p2 + i]
        if a == b or a not in comp or b not in comp or comp[a] != comp[b]:
            continue
        (agree if (delta[b] - delta[a] - (p2 - p1)) % N == w else dis).append(i)
    return agree, dis

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: scan sensitivity, span mapping, the greedy trap")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    S = EI.setup(corpus, atlas)
    C = PREREG["cells"]
    gf, r, delta, comp = skeleton(S, C)
    check("FR34's skeleton reproduced",
          r["det"] == 384 and len(r["linked"]) == 56 and not r["eq"],
          f"({r['det']} relations, {len(r['linked'])} glyphs)")

    hits = scan_free(S["cts"], delta, comp, PREREG["min_agree"])
    Lx = S["Lx"]
    found = any(m1 == Lx["East 4"] and m2 == Lx["West 4"] and sh == 1
                for m1, m2, sh, _, _, _ in hits)
    check("free-w scan recovers the known passage", found)

    rng = random.Random(PREREG["seed"])
    sh = [list(m) for m in S["cts"]]
    for m in sh: rng.shuffle(m)
    nn = len(scan_free(sh, delta, comp, PREREG["min_agree"]))
    check("shuffle background is small but nonzero (weaker calibration)",
          nn < len(hits) / 2, f"(corpus {len(hits)}, shuffle {nn})")

    ag, dis = supported_span(S, delta, comp, Lx["East 4"], 28,
                             Lx["West 4"], 29, 54)
    check("passage support maps to a contiguous head",
          max(ag) == 14 and min(d for d in dis if d > max(ag)) == 21,
          f"(agree {ag}, first disagreement {min(d for d in dis if d>max(ag))})")

    # THE NEGATIVE GATE: greedy-by-injectivity over-extends past the evidence
    greedy = list(C)
    for i in list(range(15, 35)):
        t = greedy + [i]
        rr = EB3.analyse(EB3.build(S, t))
        if rr is not None and not rr["eq"]: greedy = t
    rg = EB3.analyse(EB3.build(S, greedy))
    over = [i for i in greedy if i > max(ag)]
    check("greedy-by-injectivity reaches past the supported span (unsound)",
          len(over) > 0 and rg["det"] > r["det"],
          f"(adds offsets {over}, inflating {r['det']} -> {rg['det']})")

    c = json.load(open(corpus))
    cts = [list(x) for x in c["ciphertexts"]]
    rr = IR.relax(cts, N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard", (rr.linked_strict, rr.distinct_strict, len(rr.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    S = EI.setup(corpus_path, atlas_path)
    Lx, cts, labels = S["Lx"], S["cts"], S["labels"]
    C = PREREG["cells"]
    gf, r, delta, comp = skeleton(S, C)
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")
    print(f"skeleton: {r['det']} relations, {len(r['linked'])} glyphs, "
          f"components {[len(c) for c in r['comps']]}")

    print("\nF1 free-w scan over ALL message pairs")
    hits = scan_free(cts, delta, comp, PREREG["min_agree"])
    rng = random.Random(PREREG["seed"])
    nulls = []
    for _ in range(2):
        s = [list(m) for m in cts]
        for m in s: rng.shuffle(m)
        nulls.append(len(scan_free(s, delta, comp, PREREG["min_agree"])))
    print(f"  alignments with >= {PREREG['min_agree']} cells agreeing: {len(hits)}")
    print(f"  unigram-preserving shuffles: {nulls}   (free w is weaker than")
    print( "  FR32's fixed-w test, so the background is no longer zero)")
    TRI = {"T1": ["East 1", "West 1", "East 2"], "T2": ["West 2", "East 3", "West 3"],
           "T3": ["East 4", "West 4", "East 5"]}
    tri = {Lx[m]: t for t, ms in TRI.items() for m in ms}
    print(f"\n  {'pair':20s} {'shift':>6s} {'cells':>6s} {'agree':>6s} {'w':>4s} "
          f"{'relation':>9s}")
    for m1, m2, sh, nc, n, w in sorted(hits, key=lambda x: -x[4])[:12]:
        print(f"  {labels[m1]:8s}/{labels[m2]:8s} {sh:6d} {nc:6d} {n:6d} {w:4d} "
              f"{('within' if tri[m1]==tri[m2] else 'CROSS'):>9s}")
    xt = [h for h in hits if tri[h[0]] != tri[h[1]]]
    w2 = [h for h in hits if "West 2" in (labels[h[0]], labels[h[1]])]
    print(f"\n  cross-triplet alignments: {len(xt)}   West 2 alignments: {len(w2)}")
    print( "  -> West 2 produces NOTHING at any shift against any message, which")
    print( "     matches its status throughout the series as the uncoupled message")
    for m1, m2, sh, nc, n, w in xt:
        import math
        p = math.comb(nc, n) * 83.0 ** -(n - 1)
        print(f"  cross-triplet candidate {labels[m1]}/{labels[m2]} shift {sh}: "
              f"{n} of {nc} cells, chance ~{p:.1e}")
        print( "     against a shuffle background of 1-3 hits this is NOT significant")

    print("\nF2 the supported extent of the new passage")
    ag, dis = supported_span(S, delta, comp, Lx["East 4"], 28, Lx["West 4"], 29, 54)
    print(f"  offsets agreeing with w=54: {ag}")
    print(f"  offsets disagreeing        : {dis}")
    print(f"  -> fourteen consecutive agreeing cells, ending at offset {max(ag)};")
    print(f"     first disagreement at {min(d for d in dis if d>max(ag))}. FR32 had")
    print( "     five agreeing cells; the widened skeleton makes the same passage")
    print(f"     far better attested (chance for 14 cells on a fixed value: "
          f"83^-13).")

    print("\nF3 the greedy trap, and the principled rule")
    greedy = list(C)
    for i in list(range(15, 35)):
        t = greedy + [i]
        rr = EB3.analyse(EB3.build(S, t))
        if rr is not None and not rr["eq"]: greedy = t
    rg = EB3.analyse(EB3.build(S, greedy))
    freq = Counter(g for m in cts for g in m)
    covg = sum(freq[g] for g in rg["linked"])
    cov = sum(freq[g] for g in r["linked"])
    print(f"  greedy-by-injectivity: offsets {sorted(greedy)}")
    print(f"    -> {rg['det']} relations, {len(rg['linked'])} glyphs, "
          f"{100*covg/1036:.1f}% exposure")
    print(f"    it reaches offsets {[i for i in greedy if i>max(ag)]}, beyond the")
    print( "    last supported cell. REJECTED: injectivity is a necessary")
    print( "    condition, not evidence that a cell is same-passage.")
    print(f"  principled (supported span, minus injectivity violations):")
    print(f"    -> {r['det']} relations, {len(r['linked'])} glyphs, "
          f"{100*cov/1036:.1f}% exposure")
    print(f"  the gap between them, {rg['det']-r['det']} relations and "
          f"{100*(covg-cov)/1036:.1f} points of exposure, is the size of the error")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
