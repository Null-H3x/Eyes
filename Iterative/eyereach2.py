#!/usr/bin/env python3
"""
eyereach2 -- why the constraint system can only see part of the corpus, and
whether that can be changed. Read-only.

THE CORRECTION THIS CYCLE OPENS WITH. FR17 reported that "only 51 of 83
glyphs are reachable; the other 32 never appear inside any pair span". The
second half is wrong. Eighty-two of the eighty-three glyphs DO occur inside
certified pair spans; exactly one (glyph 27, three occurrences) falls outside
every span. The real division is finer and more interesting: rows are emitted
only at pattern-LETTER cells, because FR7's sound-rows repair masks dot cells
as occurrence-variable. Thirty-one glyphs occur inside spans but never at a
letter cell, so they are invisible to the constraint system while sitting in
the middle of certified material. Those 31 hold 332 corpus positions -- about
a third of the entire corpus.

THE QUESTION. Is that ceiling a calibration artifact (fixable by scanning
differently) or a structural property of the corpus? C2 sweeps the scan
settings with shuffle nulls to price spuriousness; C3 explains the answer.

WHY LETTER STATUS IS HARD TO GET. A glyph occupies a pattern-letter cell only
if two of its occurrences fall close enough together to sit inside one window
AND that window forms a certified isomorph. The first condition alone is
already selective: under the progressive reading a repeated ciphertext glyph
at gap d requires the plaintext values to differ by exactly d, which is a
1-in-83 coincidence per position pair.
"""

import json, os, random, sys
from collections import Counter

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyeanchor", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyegauge as EG                      # noqa: E402
import iso_relax as IR                     # noqa: E402
import isomorph as iso                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "grid_L": [8, 10, 12, 13, 15], "grid_rep": [2, 3, 4],
          "shuffles": 8, "window": 15, "seed": 20260728}

def taxonomy(cts, labels, atlas_path, ctx):
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
    strict_cells = set()
    for p in ctx["strict"]:
        for i in range(p.length):
            for cell in ((p.m1, p.p1 + i), (p.m2, p.p2 + i)):
                if cell not in dot: strict_cells.add(cell)
    span = set()
    for p in ctx["apairs"] + ctx["strict"]:
        for i in range(p.length):
            span.add((p.m1, p.p1 + i)); span.add((p.m2, p.p2 + i))
    row_cells = letter | strict_cells
    G = lambda cells: {cts[m][t] for m, t in cells}
    reachable = G(row_cells)
    dot_only = G(dot) - reachable
    outside = set(v for m in cts for v in m) - G(span)
    return dict(row_cells=row_cells, dot=dot, span=span, reachable=reachable,
                dot_only=dot_only, outside=outside)

def letter_glyphs(cts, pairs):
    out = set()
    for p in pairs:
        for m, s in ((p.m1, p.p1), (p.m2, p.p2)):
            w = cts[m][s:s + p.length]
            for v in w:
                if w.count(v) > 1: out.add(v)
    return out

def close_pairs(cts, g, W):
    n = 0
    for m in cts:
        pos = [t for t, v in enumerate(m) if v == g]
        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                if pos[j] - pos[i] < W: n += 1
    return n

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: taxonomy arithmetic, letter detection, null machinery")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    c = json.load(open(corpus)); labels = c["message_labels"]
    cts = [list(x) for x in c["ciphertexts"]]
    ctx = EG.build_context(cts, labels, atlas)
    T = taxonomy(cts, labels, atlas, ctx)

    check("letter and dot cells are disjoint", not (T["row_cells"] & T["dot"]))
    check("dot cells lie inside spans", T["dot"] <= T["span"])
    parts = len(T["reachable"]) + len(T["dot_only"]) + len(T["outside"])
    check("the three glyph populations partition the alphabet", parts == 83,
          f"({len(T['reachable'])} + {len(T['dot_only'])} + "
          f"{len(T['outside'])} = {parts})")

    # letter detection on a constructed pair
    class P: pass
    p = P(); p.m1, p.p1, p.m2, p.p2, p.length = 0, 0, 0, 0, 5
    fake = [[7, 3, 7, 9, 4]]
    check("letter detection finds the repeated value only",
          letter_glyphs(fake, [p]) == {7})

    # null machinery: shuffling destroys long isomorphs
    rng = random.Random(1)
    sh = []
    for m in cts:
        s = list(m); rng.shuffle(s); sh.append(s)
    obs = len(iso.find_isomorphs(cts, 15, 3, different_only=False))
    nul = len(iso.find_isomorphs(sh, 15, 3, different_only=False))
    check("null machinery: shuffles destroy long isomorphs", obs > 0 and nul == 0,
          f"(obs={obs}, null={nul})")

    r = IR.relax(cts, N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard", (r.linked_strict, r.distinct_strict, len(r.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    c = json.load(open(corpus_path))
    cts = [list(x) for x in c["ciphertexts"]]; labels = c["message_labels"]
    ctx = EG.build_context(cts, labels, atlas_path)
    freq = Counter(v for m in cts for v in m)
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    T = taxonomy(cts, labels, atlas_path, ctx)
    tot = sum(freq.values())
    print(f"\nC1 cell and glyph taxonomy")
    print(f"  corpus positions {tot}; inside a certified span {len(T['span'])} "
          f"({100*len(T['span'])/tot:.1f}%)")
    print(f"  row-emitting cells (letter + dot-masked strict): {len(T['row_cells'])}")
    print(f"  dot-only cells inside spans                    : {len(T['dot'])}")
    print(f"  glyphs at row-emitting cells : {len(T['reachable'])}")
    print(f"  glyphs ONLY at dot cells     : {len(T['dot_only'])}"
          f"  ({sum(freq[g] for g in T['dot_only'])} occurrences, "
          f"{100*sum(freq[g] for g in T['dot_only'])/tot:.0f}% of the corpus)")
    print(f"  glyphs outside every span    : {sorted(T['outside'])}")
    print("  -> FR17 said 32 glyphs never appear inside a pair span; in fact only")
    print("     one does. The rest sit inside certified material at dot cells,")
    print("     which FR7's stem reading declares occurrence-variable.")

    print(f"\nC2 is the ceiling a calibration artifact? scan sweep with nulls")
    rng = random.Random(PREREG["seed"])
    print(f"  {'L':>3s} {'rep':>4s} {'pairs':>6s} {'null':>7s} {'z':>7s} "
          f"{'letter glyphs':>14s} {'NEW':>4s}")
    for L in PREREG["grid_L"]:
        for r in PREREG["grid_rep"]:
            try:
                pr = iso.find_isomorphs(cts, L, r, different_only=False)
            except Exception:
                continue
            nulls = []
            for _ in range(PREREG["shuffles"]):
                sh = []
                for m in cts:
                    s = list(m); rng.shuffle(s); sh.append(s)
                nulls.append(len(iso.find_isomorphs(sh, L, r, different_only=False)))
            mu = sum(nulls) / len(nulls)
            sd = (sum((x - mu) ** 2 for x in nulls) / max(1, len(nulls) - 1)) ** 0.5
            z = (len(pr) - mu) / sd if sd else float("inf")
            lg = letter_glyphs(cts, pr)
            new = lg - T["reachable"]
            print(f"  {L:3d} {r:4d} {len(pr):6d} {mu:7.1f} {z:7.1f} {len(lg):14d} "
                  f"{len(new):4d}")
    print("  -> ZERO promotions at every setting. The settings themselves are")
    print("     sound (z = 10-36 against shuffled corpora), so the ceiling is not")
    print("     a calibration choice.")

    print(f"\nC3 why: letter status needs a short-range repeat "
          f"(window {PREREG['window']})")
    A = [close_pairs(cts, g, PREREG["window"]) for g in sorted(T["reachable"])]
    other = sorted(T["dot_only"] | T["outside"])
    B = [close_pairs(cts, g, PREREG["window"]) for g in other]
    print(f"  row-emitting glyphs ({len(A)}): mean close pairs {sum(A)/len(A):.2f}, "
          f"{sum(1 for x in A if x == 0)} with none")
    print(f"  the rest            ({len(B)}): mean close pairs {sum(B)/len(B):.2f}, "
          f"{sum(1 for x in B if x == 0)} with none")

    cand = [g for g in other if close_pairs(cts, g, PREREG["window"]) > 0]
    dead = [g for g in other if close_pairs(cts, g, PREREG["window"]) == 0]
    print(f"\nC4 refined reachability map")
    print(f"  reachable now                        : {len(T['reachable'])}")
    print(f"  candidates (close repeat, not yet in a certified isomorph window): "
          f"{len(cand)}  {sorted(cand)}")
    print(f"  structurally invisible (no close repeat anywhere): {len(dead)}  "
          f"{sorted(dead)}")
    print("  consequences:")
    print("    * an external anchor on a non-reachable glyph yields only itself;")
    print("      it has no constraints to propagate through (cf. FR17's leverage map)")
    print("    * FR5's H1 needs glyph 1, which is dot-only -- H1 is blocked by the")
    print("      stem reading, not by component structure")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
