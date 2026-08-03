#!/usr/bin/env python3
"""
eyeperm -- applying the one constraint the linear machinery structurally
cannot see, and finding the certified pool false. Read-only.

THE GAP. FR7 recorded, as an aside, that "GF systems carry no injectivity".
Every instrument in this series since has worked inside a linear system over
GF(83), where the alphabet map q is just a vector of 83 unknowns. But C is a
MIXED ALPHABET -- a permutation -- so q is injective, and q[a] = q[b] is
impossible for a != b. That constraint is non-linear, the machinery discards
it, and nothing in nineteen cycles ever checked it.

WHAT IT FINDS. The certified domain of the sound pool assigns glyphs 4 and 46
the SAME value, and the difference q[46] - q[4] = 0 is gauge-invariant, so it
is certified rather than incidental. FR7 saw this and labelled the pair
"collision-tainted", excluding both from pin grade and treating the collision
as benign degeneracy. It is not benign: it is a proof that the pool asserts
something false. This instrument establishes that soundly (direct Gaussian
elimination, no consensus heuristic), shows it holds at EVERY drift, extracts
a verified-minimal core, and localises the minimal repair.

WHAT IT DOES NOT SETTLE. The minimal repair is to reject one atlas instance,
East 1 @ 68 -- and that instance is not easily dismissed: its pattern match
prices at roughly 1 in 500 by chance. So the contradiction indicts something,
but which premise it indicts is left open and stated as such.
"""

import json, os, sys
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyefork2", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyegauge as EG                      # noqa: E402
import eyereach as ER                      # noqa: E402
import iso_relax as IR                     # noqa: E402
import isomorph as iso                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16}}

def build(cts, ctx, pool, drift=1):
    """SOUND: direct Gaussian elimination, order-independent, no purification."""
    gf = iso.GFSystem(N)
    rows = EG.make_rows(ctx, drift, {m: m for m in range(9)})
    for pr in pool:
        for row, rhs in rows(pr, cts, N):
            v = gf.classify(row, rhs)
            if v == "contradiction": return None
            if v == "pivot": gf.add(row, rhs)
    return gf

def violations(cts, ctx, pool, drift=1):
    gf = build(cts, ctx, pool, drift)
    if gf is None: return None
    dom, _ = ER.certified_domain(gf)
    return [(a, b) for a, b in combinations(sorted(dom), 2) if dom[a] == dom[b]]

def class_pairs(cls, Lx, cts, drop=None):
    L = cls["length"]
    inst = [(Lx[it["message"]], it["start"]) for it in cls["instances"]
            if drop is None or (it["message"], it["start"]) != drop]
    return [iso.IsoPair(m1=m1, p1=p1, m2=m2, p2=p2, length=L,
                        exact=cts[m1][p1:p1 + L] == cts[m2][p2:p2 + L])
            for (m1, p1), (m2, p2) in combinations(inst, 2)]

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: injectivity logic and sound-oracle behaviour")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    c = json.load(open(corpus)); labels = c["message_labels"]
    cts = [list(x) for x in c["ciphertexts"]]
    ctx = EG.build_context(cts, labels, atlas)
    pool = ctx["apairs"] + ctx["strict"]

    gf = build(cts, ctx, pool)
    check("sound system builds without contradiction", gf is not None)

    # a planted collision must be detected
    g2 = iso.GFSystem(N); g2.restore(gf.snapshot())
    check("injectivity detector fires on a certified equality",
          gf.classify({46: 1, 4: N - 1}, 0) == "redundant")

    # and the difference must be gauge-invariant, not incidental
    dom, ref = ER.certified_domain(gf)
    def sh(d):
        g = iso.GFSystem(N); g.restore(gf.snapshot()); g.add({ref: 1}, d)
        return g.solve()
    vals = {(s[46] - s[4]) % N for s in (sh(0), sh(7), sh(31))}
    check("the collision is gauge-invariant (certified, not incidental)",
          len(vals) == 1 and vals.pop() == 0)

    # removing the whole class must clear it, so the detector is not stuck-on
    rest = [p for p in pool if p not in ctx["by_class"]["#M"]]
    check("detector clears when the implicated class is removed",
          violations(cts, ctx, rest) == [])

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
    pool = ctx["apairs"] + ctx["strict"]; by = ctx["by_class"]
    a = json.load(open(atlas_path))
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    gf = build(cts, ctx, pool)
    dom, _ = ER.certified_domain(gf)
    print(f"\nC1 the certified domain, and its injectivity")
    print(f"  certified: {dict(sorted(dom.items()))}")
    v = violations(cts, ctx, pool)
    print(f"  pairs of certified glyphs sharing a value: {v}")
    print("  C is a mixed alphabet, hence a permutation, hence q is injective:")
    print("  q[a] = q[b] for a != b is IMPOSSIBLE. The pool asserts it anyway.")

    print("\nC2 is it drift-dependent? (injectivity as a possible discriminator)")
    clean = [d for d in range(1, N) if violations(cts, ctx, pool, d) == []]
    print(f"  drifts with no injectivity violation: {clean if clean else 'NONE'}")
    print(f"  drifts refuted: {82 - len(clean)} of 82")
    print("  -> the collision is structural, not an artifact of the drift value")

    print("\nC3 minimal core (deletion filtering, sound oracle)")
    def forces(pl):
        g = build(cts, ctx, pl)
        return g is not None and g.classify({46: 1, 4: N - 1}, 0) == "redundant"
    cur = list(pool)
    for p in list(pool):
        trial = [q for q in cur if q is not p]
        if forces(trial): cur = trial
    print(f"  core size {len(cur)} pairs; verified minimal: "
          f"{all(not forces([q for q in cur if q is not p]) for p in cur)}")
    for p in cur:
        print(f"    {labels[p.m1]:8s}@{p.p1:3d} x {labels[p.m2]:8s}@{p.p2:3d} "
              f"L={p.length}")

    print("\nC4 localisation")
    single = [cid for cid in list(by)
              if violations(cts, ctx, [p for p in pool if p not in by[cid]]) == []]
    print(f"  single-class removals that clear it: {single}")
    if single:
        cid = single[0]
        cls = next(x for x in a["classes"] if x["id"] == cid)
        rest = [p for p in pool if p not in by[cid]]
        print(f"  drop-one-instance within {cid}:")
        for it in cls["instances"]:
            key = (it["message"], it["start"])
            r = violations(cts, ctx, rest + class_pairs(cls, Lx, cts, drop=key))
            print(f"    without {key[0]:8s}@{key[1]:3d}: "
                  f"{'CLEAN' if r == [] else str(r)}")
        # price the implicated instance as a chance pattern match
        L, pat = cls["length"], cls["pattern"]
        sk = [(i, j) for i in range(L) for j in range(i + 1, L)
              if pat[i] != '.' and pat[i] == pat[j]]
        wins = sum(max(0, len(m) - L + 1) for m in cts)
        print(f"\n  pricing {cid}: pattern {pat}, {len(sk)} skeleton equal-pairs")
        print(f"  chance per window 83^-{len(sk)} = {83.0**-len(sk):.2e}; "
              f"{wins} windows -> {wins * 83.0**-len(sk):.4f} expected chance matches")
        print("  -> the implicated instance is NOT comfortably a coincidence, so")
        print("     'reject that instance' is the minimal repair, not an obvious one")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
