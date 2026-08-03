#!/usr/bin/env python3
"""
eyestale -- checking whether figures computed against older skeletons are
still being quoted. Read-only.

WHY. The skeleton grew from 47 glyphs to 56 across FR33 and FR34, and several
results were withdrawn or superseded (FR35 in FR48, FR41 in FR42, FR22's
headline in FR23, FR17's orthogonality claim in FR26). Figures derived from
the older skeleton do not automatically update, and a doctrine that carries
them silently is quoting numbers that no longer hold.

WHAT WAS RECHECKED.
  * FR20's usable adjacent-pair count for the A-vs-B channel (published 464)
  * FR27's cross-component packing constraint (published 1.5e10 placements,
    147,000x pruning) and its residual curve (published 44 completions at nine
    anchors)

BOTH ARE STALE. The adjacent-pair count is 558, not 464. The packing
constraint is far TIGHTER than published: 9.4e7 valid placements rather than
1.5e10, a pruning factor of about 2.4e7 rather than 1.5e5 -- roughly 160 times
stronger, because the components grew and larger components pack harder.

A CAVEAT ON THE RESIDUAL CURVE. The estimator fixes each anchored component's
base at zero, which is an arbitrary choice and need not be a valid placement
in combination; the middle of the curve is consequently noisy and
non-monotonic. Only the endpoints -- two anchors and ten -- should be read as
reliable.
"""

import json, os, random, statistics, sys
from collections import Counter

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyestrict", "eyeclass2", "eyeaudit2", "eyecirc", "eyerepair2",
          "eyeaudit", "eyeinject", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyeaudit as EA                      # noqa: E402
import iso_relax as IR                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "published_adjacent": 464, "published_packing": 1.5e10,
          "published_tail": 44, "seed": 20260902}

def setup(corpus_path, atlas_path):
    cts, labels, Lx, ctx, pool, _ = EA.load(corpus_path, atlas_path)
    BR = (Lx["East 3"], 101); A1 = (Lx["East 1"], 68)
    red = [p for p in pool
           if not any((p.m1, p.p1) == k or (p.m2, p.p2) == k for k in (BR, A1))]
    gf = EA.build(cts, ctx, Lx, red)
    return cts, labels, Lx, ctx, red, EA.analyse(gf)

def adjacent_pairs(cts, linked):
    return sum(1 for m in cts for t in range(len(m) - 1)
               if m[t] in linked and m[t + 1] in linked)

def offsets(a):
    D = a["delta"]
    return [sorted((D[s] - D[c[0]]) % N for s in c) for c in a["comps"]]

def estimate(OFF, fixed=None, trials=2000, seed=1):
    rng = random.Random(seed)
    fixed = dict(fixed or {})
    free = [i for i in range(len(OFF)) if i not in fixed]
    free.sort(key=lambda i: -len(OFF[i]))
    used = set()
    for i, b in fixed.items():
        used |= {(b + o) % N for o in OFF[i]}
    if not fixed and free:
        first = free.pop(0); used |= {o % N for o in OFF[first]}
    ests = []
    for _ in range(trials):
        u = set(used); e = 1.0; ok = True
        for i in free:
            O = OFF[i]; cand = []
            for b in range(N):
                vals = {(b + o) % N for o in O}
                if len(vals) == len(O) and not (vals & u): cand.append((b, vals))
            if not cand: ok = False; break
            e *= len(cand)
            b, vals = rng.choice(cand); u |= vals
        ests.append(e if ok else 0.0)
    return statistics.mean(ests)

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: skeleton state, counters, estimator sanity")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    cts, labels, Lx, ctx, red, a = setup(corpus, atlas)

    check("current skeleton is the 56-glyph one",
          a["det"] == 384 and len(a["linked"]) == 56,
          f"({a['det']} relations, {len(a['linked'])} glyphs)")

    adj = adjacent_pairs(cts, a["linked"])
    check("adjacent-pair counter is exact on a constructed case",
          adjacent_pairs([[1, 2, 3, 9]], {1, 2, 3}) == 2)
    check("published adjacent-pair figure is STALE",
          adj != PREREG["published_adjacent"],
          f"(published {PREREG['published_adjacent']}, current {adj})")

    OFF = offsets(a)
    m = estimate(OFF, trials=400, seed=2)
    check("packing estimate is finite and positive", m > 0, f"({m:.2e})")
    check("published packing figure is STALE (now tighter)",
          m < PREREG["published_packing"] / 10,
          f"(published {PREREG['published_packing']:.1e}, current {m:.2e})")

    full = {i: 0 for i in range(len(OFF))}
    check("fixing every component leaves exactly one placement",
          abs(estimate(OFF, full, trials=50) - 1.0) < 1e-9)

    c = json.load(open(corpus))
    cc = [list(x) for x in c["ciphertexts"]]
    r = IR.relax(cc, N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard", (r.linked_strict, r.distinct_strict, len(r.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    cts, labels, Lx, ctx, red, a = setup(corpus_path, atlas_path)
    freq = Counter(g for m in cts for g in m)
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")
    print(f"current skeleton: {a['det']} relations, {len(a['linked'])} glyphs, "
          f"components {[len(c) for c in a['comps']]}")

    print("\nT1 FR20's adjacent-pair count")
    adj = adjacent_pairs(cts, a["linked"])
    print(f"  published (47-glyph skeleton): {PREREG['published_adjacent']}")
    print(f"  current   (56-glyph skeleton): {adj}   -> STALE")
    print("  note: FR20's within-block channel was itself superseded by FR39's")
    print("  cross-message pooling (6,384 pairs), so this figure is doubly out")
    print("  of date and should not be quoted at all")

    print("\nT2 FR27's packing constraint")
    OFF = offsets(a)
    m = estimate(OFF, trials=2000, seed=PREREG["seed"])
    tot = N ** (len(OFF) - 1)
    print(f"  published (47 glyphs): 1.5e10 placements, ~1.5e5 pruning")
    print(f"  current   (56 glyphs): {m:.2e} placements, {tot/m:,.0f}x pruning")
    print(f"  -> STALE, and about {1.5e10/m:.0f}x TIGHTER than published:")
    print("     larger components pack harder, so the widening bought more")
    print("     than the relation count alone suggested")

    print("\nT3 the residual curve")
    order = sorted(range(len(OFF)), key=lambda i: -len(OFF[i]))
    fixed = {}; cov = 0
    print(f"  {'anchors':>8s} {'remaining':>12s} {'glyphs':>7s} {'corpus':>8s}")
    for k, idx in enumerate(order):
        fixed[idx] = 0
        cov += sum(freq[g] for g in a["comps"][idx])
        r = estimate(OFF, dict(fixed), trials=700, seed=PREREG["seed"] + k)
        print(f"  {k+2:8d} {r:12.3g} {sum(len(OFF[i]) for i in fixed):7d} "
              f"{100*cov/1036:7.1f}%")
    print(f"  published: 9 anchors -> {PREREG['published_tail']} completions")
    print("  CAVEAT: the estimator fixes each anchored base at zero, which is")
    print("  arbitrary and need not be jointly valid, so the MIDDLE of this")
    print("  curve is noisy and non-monotonic. Only the endpoints are reliable.")

    print("\nT4 what the doctrine should now carry")
    print(f"  * adjacent pairs for A-vs-B : use FR39's 6,384 pooled pairs,")
    print(f"    not FR20's within-block figure")
    print(f"  * packing                   : ~{m:.0e} placements, "
          f"{tot/m:,.0f}x pruning")
    print(f"  * two anchors in component 1: 25 glyphs, 31.2% of the corpus")
    print(f"  * ten anchors               : 56 glyphs, 74.1%")
    print("  the acquisition arithmetic is unchanged; the packing figure is")
    print("  simply stronger than previously recorded")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
