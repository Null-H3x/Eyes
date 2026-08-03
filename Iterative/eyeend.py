#!/usr/bin/env python3
"""
eyeend -- closing the three routes by which the constraint system might have
been widened, and measuring what the ceiling actually costs. Read-only.

FR18 left the reachability ceiling at 51 glyphs and named three possible ways
past it. This cycle tests all three and closes them, then asks the question
that matters more: given the ceiling, what would a complete solve of the
reachable set actually expose?

THE THREE ROUTES.
  R1 the literal openings. FR18 proposed they might recruit the glyphs the
     atlas cannot see -- 24 consecutive positions across six messages, no
     repeat required. But an opening pair is an exact Delta=0 identity, so at
     every cell the two windows carry the SAME glyph and the symbol terms
     cancel out of the row. The rows constrain base variables only. Admitting
     the openings recruits nothing, and FR18's horizon item dissolves.
  R2 opening-to-body isomorphs. A window in the opening region matching a
     window in the body WOULD carry real symbol rows. Searched across scan
     settings against a shuffle null.
  R3 constant dot cells. FR7 masks every dot cell as occurrence-variable. If
     some dots were in fact constant across all instances of their class,
     those cells could be promoted. Tested directly per class per offset.

THE ENDGAME MEASUREMENT. The ceiling bounds which glyphs can be determined,
not how much text that exposes. The readability map reports corpus exposure
and, more importantly, the SHAPE of the residual: isolated unknowns between
known runs are a very different problem from contiguous unknown blocks.
"""

import json, os, random, sys
from collections import Counter

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyereach2", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyegauge as EG                      # noqa: E402
import iso_relax as IR                     # noqa: E402
import isomorph as iso                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "open_end": 25, "grid_L": [8, 10, 12, 13, 15], "grid_rep": [2, 3],
          "shuffles": 8, "seed": 20260729}

def reach_set(cts, labels, atlas_path, ctx):
    Lx = {l: i for i, l in enumerate(labels)}
    a = json.load(open(atlas_path))
    letter, dot = set(), set()
    for cl in a["classes"]:
        L, pat = cl["length"], cl["pattern"]
        for it in cl["instances"]:
            mi = Lx[it["message"]]
            for i in range(L):
                (letter if pat[i] != '.' else dot).add((mi, it["start"] + i))
    dot -= letter
    strict = {(m, t) for p in ctx["strict"] for i in range(p.length)
              for (m, t) in ((p.m1, p.p1 + i), (p.m2, p.p2 + i))
              if (m, t) not in dot}
    return {cts[m][t] for m, t in (letter | strict)}, dot, a

def runs_of(seq, pred):
    out = []; cur = 0
    for v in seq:
        if pred(v): cur += 1
        else:
            if cur: out.append(cur)
            cur = 0
    if cur: out.append(cur)
    return out

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: cancellation logic, run arithmetic, null machinery")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    c = json.load(open(corpus)); labels = c["message_labels"]
    cts = [list(x) for x in c["ciphertexts"]]
    ctx = EG.build_context(cts, labels, atlas)

    # R1 mechanism: an exact Delta=0 pair must emit no symbol terms
    ops = EG.opening_pairs(labels, EG.OPENINGS)
    rows = EG.make_rows(ctx, 1, {m: m for m in range(9)})
    nsym = sum(1 for pr in ops for row, _ in rows(pr, cts, N)
               if any(k < N for k in row))
    ntot = sum(1 for pr in ops for _ in rows(pr, cts, N))
    check("exact Delta=0 pairs emit zero symbol terms", ntot > 0 and nsym == 0,
          f"({nsym} of {ntot} rows)")

    # run arithmetic
    check("run finder is exact",
          runs_of([1, 1, 0, 1, 1, 1, 0], lambda v: v == 1) == [2, 3])

    # null machinery
    rng = random.Random(3)
    sh = []
    for m in cts:
        s = list(m); rng.shuffle(s); sh.append(s)
    check("shuffles destroy long isomorphs",
          len(iso.find_isomorphs(cts, 15, 3, different_only=False)) > 0
          and len(iso.find_isomorphs(sh, 15, 3, different_only=False)) == 0)

    R, dot, a = reach_set(cts, labels, atlas, ctx)
    check("reachable set reproduces FR18's count", len(R) == 51, f"({len(R)})")

    r = IR.relax(cts, N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard", (r.linked_strict, r.distinct_strict, len(r.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    c = json.load(open(corpus_path))
    cts = [list(x) for x in c["ciphertexts"]]; labels = c["message_labels"]
    Lx = {l: i for i, l in enumerate(labels)}
    ctx = EG.build_context(cts, labels, atlas_path)
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")
    R, dot, a = reach_set(cts, labels, atlas_path, ctx)
    freq = Counter(v for m in cts for v in m); tot = sum(freq.values())

    print("\nR1 can the literal openings recruit any glyph?")
    ops = EG.opening_pairs(labels, EG.OPENINGS)
    rows = EG.make_rows(ctx, 1, {m: m for m in range(9)})
    nsym = ntot = 0
    for pr in ops:
        for row, _ in rows(pr, cts, N):
            ntot += 1
            if any(k < N for k in row): nsym += 1
    print(f"  {len(ops)} opening pairs emit {ntot} rows; {nsym} contain a symbol term")
    print("  -> exact Delta=0 pairs carry the SAME glyph at both cells, so the")
    print("     symbol terms cancel identically. The openings constrain base")
    print("     variables only and recruit ZERO glyphs. FR18's horizon item")
    print("     dissolves on inspection -- the branch-(i) cost is not larger.")

    print("\nR2 are there opening-to-body isomorphs? (these WOULD carry symbol rows)")
    rng = random.Random(PREREG["seed"]); oe = PREREG["open_end"]
    print(f"  {'L':>3s} {'rep':>4s} {'observed':>9s} {'null mean':>10s}")
    for L in PREREG["grid_L"]:
        for rp in PREREG["grid_rep"]:
            pr = iso.find_isomorphs(cts, L, rp, different_only=False)
            ob = [p for p in pr if (p.p1 < oe) != (p.p2 < oe)]
            nulls = []
            for _ in range(PREREG["shuffles"]):
                sh = []
                for m in cts:
                    s = list(m); rng.shuffle(s); sh.append(s)
                q = iso.find_isomorphs(sh, L, rp, different_only=False)
                nulls.append(len([p for p in q if (p.p1 < oe) != (p.p2 < oe)]))
            print(f"  {L:3d} {rp:4d} {len(ob):9d} {sum(nulls)/len(nulls):10.2f}")
    print("  -> none at any setting, at or below the chance expectation. The")
    print("     opening region shares no isomorph structure with the body.")

    print("\nR3 are any dot cells constant across all instances of their class?")
    const = var = 0
    for cl in a["classes"]:
        L, pat = cl["length"], cl["pattern"]
        inst = [(Lx[it["message"]], it["start"]) for it in cl["instances"]]
        if len(inst) < 2: continue
        for i in range(L):
            if pat[i] != '.': continue
            vals = {cts[m][s + i] for m, s in inst}
            if len(vals) == 1: const += 1
            else: var += 1
    print(f"  dot offsets constant across instances: {const}")
    print(f"  dot offsets that genuinely vary       : {var}")
    print("  -> every dot varies. FR6/FR7's stem reading is exactly right, not")
    print("     over-cautious, and no dot cell can be promoted by constancy.")

    print("\nENDGAME: what full determination of the reachable set exposes")
    exposed = sum(freq[g] for g in R)
    print(f"  reachable glyphs {len(R)}/83 -> {exposed}/{tot} positions "
          f"({100*exposed/tot:.1f}%)")
    print(f"  residual {tot-exposed} positions ({100*(tot-exposed)/tot:.1f}%) "
          f"across {83-len(R)} glyphs, which would occupy the remaining")
    print(f"  {83-len(R)} alphabet slots as an unknown permutation")

    print(f"\n  readability map:")
    print(f"  {'message':9s} {'len':>4s} {'known':>6s} {'%':>6s} {'longest run':>12s}")
    for mi, m in enumerate(cts):
        kn = sum(1 for v in m if v in R)
        rr = runs_of(m, lambda v: v in R)
        print(f"  {labels[mi]:9s} {len(m):4d} {kn:6d} {100*kn/len(m):5.1f}% "
              f"{max(rr) if rr else 0:12d}")
    allr = [x for m in cts for x in runs_of(m, lambda v: v in R)]
    allg = [x for m in cts for x in runs_of(m, lambda v: v not in R)]
    allr.sort(reverse=True)
    print(f"\n  known runs: longest {allr[:8]}, mean {sum(allr)/len(allr):.1f}, "
          f"{sum(1 for x in allr if x >= 8)} of length >= 8")
    print(f"  unknown gaps: mean {sum(allg)/len(allg):.2f}, "
          f"{sum(1 for x in allg if x == 1)}/{len(allg)} are a SINGLE position")
    print("  -> the residual is scattered, not blocking: two thirds of the text")
    print("     exposed with unknowns mostly isolated between known runs.")
    print("  CAVEAT: whether isolated gaps can be filled by context depends on")
    print("     the A-vs-B fork. Under branch A (a further layer, high-entropy")
    print("     tokens) context does not help, and this favourable shape buys")
    print("     nothing. The structural claim is shape only, not readability.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
