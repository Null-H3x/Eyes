#!/usr/bin/env python3
"""
eyeinvar -- closing the packing question deductively, and building the
mechanism FR52 asked for. Read-only.

THE QUESTION FR52 IMPLIED. FR27 tested whether cross-component packing can
discriminate the drift, found that every drift packs, and recorded it as an
empirical negative. FR52 then showed the packing constraint is about 160 times
TIGHTER than published, because the components grew. A tighter constraint
might have changed the answer.

IT CANNOT, AND THE REASON IS A PROOF. Let {b_c} be a valid packing for offset
sets {S_c}, so the value sets b_c + S_c are pairwise disjoint. Multiplication
by an invertible d is a bijection of Z/83, so

    d*(b_c + S_c) = (d*b_c) + (d*S_c)

are also pairwise disjoint. Hence {d*b_c} packs {d*S_c}, and the map is
invertible, giving a BIJECTION between the packings at drift 1 and those at
any drift d. Feasibility is preserved and so is the COUNT -- verified exactly
on a reduced instance, 275 packings at every drift tested.

So no amount of tightening can ever make packing discriminate the drift.
FR27's empirical finding and FR52's tightening are both instances of one
structural fact, and this closes the question permanently rather than for the
current skeleton.

THE MECHANISM. FR52 found two figures that had gone stale when the skeleton
grew, and noted nothing prevents a third. This instrument derives every
downstream figure the doctrine quotes from the current skeleton in one pass,
so they cannot drift apart again.
"""

import json, os, random, statistics, sys
from collections import Counter
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyestale", "eyestrict", "eyeclass2", "eyeaudit2", "eyecirc",
          "eyerepair2", "eyeaudit", "eyeinject", "eyegauge", "eyestem",
          "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyeaudit as EA                      # noqa: E402
import eyegauge as EG                      # noqa: E402
import iso_relax as IR                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

GI = {"T1": 0, "T2": 1, "T3": 2}
PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "seed": 20260903}

def setup(corpus_path, atlas_path):
    cts, labels, Lx, ctx, pool, _ = EA.load(corpus_path, atlas_path)
    BR = (Lx["East 3"], 101); A1 = (Lx["East 1"], 68)
    red = [p for p in pool
           if not any((p.m1, p.p1) == k or (p.m2, p.p2) == k for k in (BR, A1))]
    gf = EA.build(cts, ctx, Lx, red)
    return cts, labels, Lx, ctx, red, gf, EA.analyse(gf)

def offsets(a):
    D = a["delta"]
    return [sorted((D[s] - D[c[0]]) % N for s in c) for c in a["comps"]]

def exact_count(offs, mod=N):
    order = sorted(range(len(offs)), key=lambda i: -len(offs[i]))
    tot = 0
    def rec(k, used):
        nonlocal tot
        if k == len(order): tot += 1; return
        O = offs[order[k]]
        for b in ([0] if k == 0 else range(mod)):
            vals = {(b + o) % mod for o in O}
            if len(vals) != len(O) or (vals & used): continue
            rec(k + 1, used | vals)
    rec(0, set())
    return tot

def feasible(offs):
    order = sorted(range(len(offs)), key=lambda i: -len(offs[i]))
    def rec(k, used):
        if k == len(order): return True
        O = offs[order[k]]
        for b in ([0] if k == 0 else range(N)):
            vals = {(b + o) % N for o in O}
            if len(vals) != len(O) or (vals & used): continue
            if rec(k + 1, used | vals): return True
        return False
    return rec(0, set())

def estimate(OFF, trials=1500, seed=1):
    rng = random.Random(seed)
    order = sorted(range(len(OFF)), key=lambda i: -len(OFF[i]))
    ests = []
    for _ in range(trials):
        used = set(); e = 1.0; ok = True
        for k, i in enumerate(order):
            O = OFF[i]; cand = []
            for b in ([0] if k == 0 else range(N)):
                vals = {(b + o) % N for o in O}
                if len(vals) == len(O) and not (vals & used): cand.append((b, vals))
            if not cand: ok = False; break
            e *= len(cand)
            b, vals = rng.choice(cand); used |= vals
        ests.append(e if ok else 0.0)
    return statistics.mean(ests)

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: the scale-invariance proof, and the derivation")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    cts, labels, Lx, ctx, red, gf, a = setup(corpus, atlas)
    check("skeleton is the current one",
          a["det"] == 384 and len(a["linked"]) == 56 and not a["eq"],
          f"({a['det']} relations, {len(a['linked'])} glyphs)")

    OFF = offsets(a)
    small = sorted(OFF, key=len, reverse=True)[:4]
    base = exact_count(small)
    counts = {d: exact_count([sorted((d * x) % N for x in S) for S in small])
              for d in (1, 2, 3, 7, 41, 82)}
    check("packing count is IDENTICAL at every drift (the proof, verified)",
          all(c == base for c in counts.values()),
          f"({base} at every drift)")

    # scaling by a NON-invertible factor would break it -- but 0 is the only
    # such factor mod a prime, so the claim is that every d in 1..82 works
    check("every nonzero scalar is invertible mod 83 (why the proof holds)",
          all(pow(d, N - 2, N) * d % N == 1 for d in range(1, N)))

    check("feasibility is preserved under scaling",
          all(feasible([sorted((d * x) % N for x in S) for S in OFF])
              == feasible(OFF) for d in (5, 29, 61)))

    # the derivation must reproduce the audited figures
    freq = Counter(g for m in cts for g in m)
    cov = sum(freq[g] for g in a["linked"])
    check("derived exposure matches the audited figure",
          abs(100 * cov / 1036 - 74.1) < 0.15, f"({100*cov/1036:.1f}%)")
    c1 = a["comps"][0]
    check("derived two-anchor yield matches",
          len(c1) == 25 and abs(100 * sum(freq[g] for g in c1) / 1036 - 31.2) < 0.2,
          f"({len(c1)} glyphs, {100*sum(freq[g] for g in c1)/1036:.1f}%)")

    c = json.load(open(corpus))
    cc = [list(x) for x in c["ciphertexts"]]
    r = IR.relax(cc, N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard", (r.linked_strict, r.distinct_strict, len(r.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    cts, labels, Lx, ctx, red, gf, a = setup(corpus_path, atlas_path)
    freq = Counter(g for m in cts for g in m)
    OFF = offsets(a)
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    print("\nI1 does the tightened packing constraint discriminate the drift?")
    bad = []
    for d in range(1, N):
        gd = EA.build(cts, ctx, Lx, red, drift=d)
        if gd is None: continue
        od = offsets(EA.analyse(gd))
        if not feasible(od): bad.append(d)
    print(f"  drifts admitting no packing: {bad if bad else 'NONE'}")
    print("  same answer as FR27 gave on the 47-glyph skeleton, despite the")
    print("  constraint being ~160x tighter (FR52)")

    print("\nI2 why tightening cannot help — the proof")
    print("  let {b_c} pack {S_c}, so the sets b_c + S_c are pairwise disjoint.")
    print("  multiplication by an invertible d is a bijection of Z/83, so")
    print("      d*(b_c + S_c) = (d*b_c) + (d*S_c)")
    print("  are also pairwise disjoint. {d*b_c} therefore packs {d*S_c}, and")
    print("  the map is invertible: a BIJECTION between the packings at drift 1")
    print("  and those at drift d.")
    small = sorted(OFF, key=len, reverse=True)[:4]
    print(f"\n  verified exactly on the four largest components "
          f"{[len(x) for x in small]}:")
    print(f"  {'drift':>6s} {'exact packings':>16s}")
    for d in (1, 2, 3, 5, 7, 17, 31, 41, 82):
        print(f"  {d:6d} {exact_count([sorted((d*x)%N for x in S) for S in small]):16,d}")
    print("  -> the count is the same for every drift. Packing carries ZERO")
    print("     information about it, permanently, not just at this skeleton.")

    print("\nI3 canonical derivation — every downstream figure, from this skeleton")
    cov = sum(freq[g] for g in a["linked"])
    m = estimate(OFF, seed=PREREG["seed"])
    tot = N ** (len(OFF) - 1)
    c1 = a["comps"][0]
    adj = sum(1 for msg in cts for t in range(len(msg) - 1)
              if msg[t] in a["linked"] and msg[t + 1] in a["linked"])
    gauges = {"1": {mm: 0 for mm in range(9)},
              "3": {Lx[mm]: GI[t] for t, ms in EG.TRIPLETS.items() for mm in ms},
              "9": {mm: mm for mm in range(9)}}
    ladder = tuple(sum(1 for d in range(1, N)
                       if EA.build(cts, ctx, Lx, red, d, g) is not None)
                   for g in gauges.values())
    rows = [
        ("determined relations", f"{a['det']}"),
        ("injectivity violations", f"{len(a['eq'])}"),
        ("glyphs in components", f"{len(a['linked'])}"),
        ("component sizes", f"{[len(c) for c in a['comps']]}"),
        ("corpus exposure", f"{cov}/1036 = {100*cov/1036:.1f}%"),
        ("gauge ladder (1/3/9)", f"{ladder[0]}/82, {ladder[1]}/82, {ladder[2]}/82"),
        ("packing placements", f"{m:.2e}"),
        ("packing pruning", f"{tot/m:,.0f}x"),
        ("2 anchors in component 1", f"{len(c1)} glyphs, "
         f"{100*sum(freq[g] for g in c1)/1036:.1f}%"),
        ("all anchors", f"{len(a['linked'])} glyphs, {100*cov/1036:.1f}%"),
        ("adjacent pairs (superseded)", f"{adj}  — use FR39's 6,384 pooled"),
    ]
    print(f"  {'figure':30s} {'value':>34s}")
    for k, v in rows:
        print(f"  {k:30s} {v:>34s}")
    print("\n  every number above is computed from the corpus in this run. Any")
    print("  figure quoted elsewhere that disagrees with this table is stale.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
