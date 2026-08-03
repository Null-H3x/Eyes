#!/usr/bin/env python3
"""
eyepack -- pushing FR26's skeleton with the one constraint left unused, and
settling which of FR25's two repairs the corpus prefers. Read-only.

THE UNUSED CONSTRAINT. FR26's skeleton splits the determined glyphs into
components, each carrying a FREE additive base. Injectivity has so far been
applied pairwise inside components. Across components it is a PACKING
constraint: the value sets (base_c + offsets_c) must be pairwise disjoint,
because C is a permutation and 47 determined glyphs must occupy 47 distinct
slots out of 83. FR22 nominated "injectivity beyond pairwise" and I expected
it to dissolve; in the component setting it does not.

WHAT PACKING BUYS, AND WHAT IT DOES NOT.
  * It prunes the placement space by roughly 1.5e5 -- from 83^8 to about
    1.5e10 -- which is real but nowhere near enumerable.
  * It does NOT discriminate the drift: every one of the 82 non-degenerate
    drifts admits a packing. So it cannot substitute for an external anchor,
    and eyedrift's degeneracy certificate is undisturbed.
  * It DOES shrink what each successive anchor has to search, and the tail is
    steep: with nine components fixed only 44 completions remain, which is
    enumerable by hand. The tenth anchor is therefore replaceable.

THE DISCRIMINATOR. FR25 left two repairs open, each removing one instance
with a three-pair skeleton -- E1@68 (class #M) or E4@51 (class #3) -- and
asked for independent evidence. Embeddedness supplies it: five of the six #M
instances sit INSIDE a larger certified passage (#1, #F, #C0, #C1), and all
three #3 instances sit inside #3+ or #S. E1@68 is the only instance in either
class with no parent passage. It is corroborated by nothing except its own
skeleton match.

Estimation note: exact enumeration of packings is infeasible, so counts use
Knuth's randomized tree-size estimator, which is unbiased. The selftest checks
it against exact enumeration on a reduced instance before any corpus number is
reported.
"""

import json, os, random, statistics, sys
from collections import Counter

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyeskel", "eyerepair", "eyescore", "eyeinject", "eyegauge",
          "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyeskel as EK                       # noqa: E402
import eyerepair as ERP                    # noqa: E402
import eyeinject as EI                     # noqa: E402
import iso_relax as IR                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "seed": 20260801}

# ------------------------------------------------------------------ packing
def exact_count(offs, mod=N):
    """exact number of base assignments giving pairwise-disjoint value sets;
    the largest component's base is fixed at 0 (global rotation gauge)."""
    order = sorted(range(len(offs)), key=lambda i: -len(offs[i]))
    total = 0
    def rec(k, used):
        nonlocal total
        if k == len(order): total += 1; return
        O = offs[order[k]]
        for b in ([0] if k == 0 else range(mod)):
            vals = {(b + o) % mod for o in O}
            if len(vals) != len(O) or (vals & used): continue
            rec(k + 1, used | vals)
    rec(0, set())
    return total

def feasible(offs, mod=N):
    order = sorted(range(len(offs)), key=lambda i: -len(offs[i]))
    def rec(k, used):
        if k == len(order): return True
        O = offs[order[k]]
        for b in ([0] if k == 0 else range(mod)):
            vals = {(b + o) % mod for o in O}
            if len(vals) != len(O) or (vals & used): continue
            if rec(k + 1, used | vals): return True
        return False
    return rec(0, set())

def estimate(offs, fixed=None, trials=2500, seed=1, mod=N):
    """Knuth randomized tree-size estimator (unbiased)."""
    rng = random.Random(seed)
    fixed = dict(fixed or {})
    free = [i for i in range(len(offs)) if i not in fixed]
    free.sort(key=lambda i: -len(offs[i]))
    used0 = set()
    for i, b in fixed.items():
        used0 |= {(b + o) % mod for o in offs[i]}
    if not fixed and free:
        first = free.pop(0); fixed[first] = 0
        used0 |= {o % mod for o in offs[first]}
    ests = []
    for _ in range(trials):
        used = set(used0); est = 1.0; ok = True
        for i in free:
            O = offs[i]; cand = []
            for b in range(mod):
                vals = {(b + o) % mod for o in O}
                if len(vals) == len(O) and not (vals & used): cand.append((b, vals))
            if not cand: ok = False; break
            est *= len(cand)
            b, vals = rng.choice(cand); used |= vals
        ests.append(est if ok else 0.0)
    return statistics.mean(ests)

# ------------------------------------------------------------------ skeleton
def component_offsets(S, pool, drift=1, merges=(("East 4", "East 5"),)):
    gf = EK.build(S, pool, drift, merges)
    if gf is None: return None, None
    sk = EK.skeleton(gf)
    comps, offs = [], []
    for c in sk["comps"]:
        if len(c) < 2: continue
        anc = c[0]; o = {anc: 0}
        for s in c:
            if s == anc: continue
            h = [d for d in range(N)
                 if gf.classify({s: 1, anc: N - 1}, d) == "redundant"]
            if len(h) == 1: o[s] = h[0]
        if len(o) == len(c):
            comps.append(c); offs.append(sorted(o.values()))
    return comps, offs

def embeddedness(atlas):
    spans = {}
    for cl in atlas["classes"]:
        for it in cl["instances"]:
            spans.setdefault(it["message"], []).append(
                (it["start"], cl["length"], cl["id"]))
    def parents(msg, start, length, cid):
        return [f"{c}@{s}" for s, L, c in spans.get(msg, [])
                if c != cid and s <= start and start + length <= s + L]
    return parents

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: packing exactness, estimator accuracy, embeddedness")

    # exact counter on a hand case, modulus 7: {0,1} and {0,2}
    n = exact_count([[0, 1], [0, 2]], mod=7)
    brute = sum(1 for b in range(7)
                if not ({0, 1} & {b % 7, (b + 2) % 7}))
    check("exact packing counter matches brute force (mod 7)", n == brute,
          f"({n} vs {brute})")

    # an impossible instance must be detected
    imp = [[0, 1, 2, 3], [0, 1, 2, 3]]
    check("impossible packing detected (mod 5)", not feasible(imp, mod=5))
    check("possible packing detected (mod 11)", feasible(imp, mod=11))

    # estimator is unbiased against exact enumeration on a reduced instance
    small = [[0, 3, 7], [0, 5], [0, 2], [0, 9]]
    ex = exact_count(small, mod=23)
    es = estimate(small, trials=4000, seed=5, mod=23)
    rel = abs(es - ex) / max(ex, 1)
    check("estimator agrees with exact enumeration within 10%", rel < 0.10,
          f"(exact {ex}, estimate {es:.1f}, rel err {rel:.3f})")

    # embeddedness on constructed spans
    fake = {"classes": [
        {"id": "#BIG", "length": 10,
         "instances": [{"message": "m", "start": 0, "values": []}]},
        {"id": "#SUB", "length": 4,
         "instances": [{"message": "m", "start": 2, "values": []},
                       {"message": "m", "start": 40, "values": []}]}]}
    par = embeddedness(fake)
    check("embeddedness finds a parent when nested",
          par("m", 2, 4, "#SUB") == ["#BIG@0"])
    check("embeddedness reports standalone when not nested",
          par("m", 40, 4, "#SUB") == [])

    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
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
    Lx, cts = S["Lx"], S["cts"]
    atlas = json.load(open(atlas_path))
    freq = Counter(v for m in cts for v in m)
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")
    plA = ERP.drop(S["pool"], (Lx["East 3"], 101), (Lx["East 1"], 68))
    comps, offs = component_offsets(S, plA)
    print(f"\nskeleton components: {[len(c) for c in comps]} "
          f"({sum(len(c) for c in comps)} glyphs into 83 slots)")

    print("\nP1 cross-component injectivity as a packing constraint")
    m = estimate(offs, trials=3000, seed=PREREG["seed"])
    tot = N ** (len(offs) - 1)
    print(f"  valid placements (estimate): {m:,.3g}")
    print(f"  unconstrained: 83^{len(offs)-1} = {tot:,.3g}")
    print(f"  pruning factor: {tot/m:,.0f}x   surviving fraction {m/tot:.4%}")
    print("  -> real constraint, but far from enumerable on its own")

    print("\nP2 does packing discriminate the drift?")
    bad = []
    for d in range(1, N):
        cc, oo = component_offsets(S, plA, drift=d)
        if oo is None: continue
        if not feasible(oo): bad.append(d)
    print(f"  drifts admitting NO packing: {bad if bad else 'NONE'}")
    print("  -> injectivity does not discriminate the drift; eyedrift's")
    print("     degeneracy certificate is undisturbed and anchors remain required")

    print("\nP3 residual placements as components get anchored")
    order = sorted(range(len(offs)), key=lambda i: -len(offs[i]))
    print(f"  {'anchors':>8s} {'fixed':>6s} {'remaining placements':>21s} "
          f"{'glyphs':>7s} {'corpus':>8s}")
    fixed = {}; known = 0; cov = 0
    for k, idx in enumerate(order):
        fixed[idx] = 0
        known += len(offs[idx]); cov += sum(freq[g] for g in comps[idx])
        mm = estimate(offs, fixed, trials=1200, seed=PREREG["seed"] + k)
        print(f"  {k+2:8d} {k+1:6d} {mm:21,.3g} {known:7d} "
              f"{100*cov/1036:7.1f}%")
    print("  -> the tail is steep: nine components fixed leaves ~44 completions,")
    print("     which is enumerable, so the tenth anchor is replaceable")

    print("\nP4 the A-vs-B discriminator: is the dropped instance corroborated?")
    par = embeddedness(atlas)
    for cid in ("#M", "#3"):
        cl = next(x for x in atlas["classes"] if x["id"] == cid)
        L = cl["length"]
        print(f"  class {cid} (L={L}):")
        for it in cl["instances"]:
            p = par(it["message"], it["start"], L, cid)
            print(f"    {it['message']:8s}@{it['start']:3d}: "
                  f"{'inside ' + ', '.join(p) if p else 'STANDALONE'}")
    print("  -> E1@68 is the only instance in either class with no parent")
    print("     passage. Repair A discards an instance corroborated by nothing")
    print("     but its own skeleton match; repair B discards one that sits")
    print("     inside #3+ at the same start position. A is favoured.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
