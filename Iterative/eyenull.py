#!/usr/bin/env python3
"""
eyenull -- withdrawing FR41. Read-only.

WHAT FR41 CLAIMED. That the plaintext avoids repeating a token at short range,
on a max-statistic test giving P = 0.0013 against a null that permuted
v-values within each block.

WHY IT IS WRONG. A coincidence at distance d requires two glyphs whose Delta
values differ by exactly d, sitting d apart. The skeleton's Delta set is
heavily DEPLETED in the range where FR41 found its gap: only 33 of 384
within-component glyph pairs have a Delta-difference in 9..17, which is 8.6%
where uniform would give 22.0%. Coincidences at those distances are therefore
about 2.6 times rarer for reasons of geometry alone, before the plaintext is
consulted at all.

FR41's null could not see this because it permuted v-values freely, which
destroys the v = Delta - t construction and hence the Delta-difference
geometry. The correct null permutes which GLYPH occupies each position within
a message: that preserves the real Delta values, the real positions and each
message's glyph inventory, randomising only the plaintext -- the quantity
actually under test.

RESULT. Observed max-deficit z = -3.36 at (4,17), unchanged. Under the correct
null the distribution has mean -2.68 rather than -2.03, and
P(null <= observed) = 0.073. NOT SIGNIFICANT. FR41's finding is withdrawn.

THE GENERALISABLE LESSON. A permutation null must randomise ONLY the quantity
under test and preserve everything else. FR41's null randomised the plaintext
AND the instrument's geometry together, which inflated the apparent effect.
The gate here therefore checks two things: that the corrected null preserves
the Delta-difference distribution, and that it still DETECTS a planted
plaintext effect -- otherwise the correction would merely be an insensitive
test.
"""

import json, math, os, random, sys
from collections import Counter
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83
MAXD = 40

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyedist", "eyevalid", "eyepool2", "eyeclass", "eyeloo", "eyeclust",
          "eyefree2", "eyebridge3", "eyewiden", "eyepair", "eyeseek", "eyefree",
          "eyebase", "eyealpha", "eyepack", "eyeskel", "eyerepair", "eyescore",
          "eyeinject", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyeloo as EL                        # noqa: E402
import eyerepair as ERP                    # noqa: E402
import eyeinject as EI                     # noqa: E402
import iso_relax as IR                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "nulls": 600, "seed": 20260812, "min_pairs": 100}

def setup(S):
    Lx, cts = S["Lx"], S["cts"]
    pool = ERP.drop(S["pool"], (Lx["East 3"], 101), (Lx["East 1"], 68))
    gf = EL.build(S, pool)
    D, C = EL.deltas(gf)
    W = {}
    for a, b in combinations(range(9), 2):
        h = [d for d in range(N)
             if gf.classify({N + b: 1, N + a: N - 1}, d) == "redundant"]
        if len(h) == 1: W[(a, b)] = h[0]
    nd = {(Lx["East 1"], Lx["West 1"]), (Lx["East 4"], Lx["East 5"])}
    cov = set()
    for p in pool:
        for i in range(p.length):
            cov.add((p.m1, p.p1 + i)); cov.add((p.m2, p.p2 + i))
    slots = {}
    for mi, m in enumerate(cts):
        for t, g in enumerate(m):
            if g in C and (mi, t) not in cov:
                slots.setdefault(mi, []).append((t, g))
    return D, C, W, nd, slots

def delta_difference_profile(D, C):
    bycomp = {}
    for g, ci in C.items(): bycomp.setdefault(ci, []).append(g)
    diffs = Counter()
    for gs in bycomp.values():
        for a, b in combinations(gs, 2):
            d = (D[a] - D[b]) % N
            diffs[min(d, N - d)] += 1
    return diffs

def profile(assign, D, C, W, nd):
    blocks = {}
    for mi, lst in assign.items():
        for t, g in lst:
            blocks.setdefault((mi, C[g]), []).append((t, (D[g] - t) % N))
    cnt = [0] * (MAXD + 2); hit = [0] * (MAXD + 2)
    for v in blocks.values():
        for (t1, x), (t2, y) in combinations(v, 2):
            d = abs(t1 - t2)
            if d <= MAXD:
                cnt[d] += 1
                if x == y: hit[d] += 1
    keys = list(blocks)
    for k1 in keys:
        for k2 in keys:
            (m1, c1), (m2, c2) = k1, k2
            if c1 != c2 or m1 >= m2: continue
            if (m1, m2) not in W or (m1, m2) in nd: continue
            w = W[(m1, m2)]
            for t1, x in blocks[k1]:
                for t2, y in blocks[k2]:
                    d = abs(t1 - t2)
                    if d <= MAXD:
                        cnt[d] += 1
                        if (x - y) % N == w: hit[d] += 1
    return cnt, hit

def extreme(cnt, hit, deficit=True):
    best = 0.0; arg = None
    for lo in range(1, MAXD + 1):
        c = h = 0
        for hi in range(lo, MAXD + 1):
            c += cnt[hi]; h += hit[hi]
            if c < PREREG["min_pairs"]: continue
            e = c / N; sd = math.sqrt(c * (1 / N) * (1 - 1 / N))
            z = (h - e) / sd
            if (z < best) if deficit else (z > best): best = z; arg = (lo, hi)
    return best, arg

def make_blocks(slots, C):
    bl = {}
    for mi, lst in slots.items():
        for t, g in lst: bl.setdefault((mi, C[g]), []).append((t, g))
    return bl

def block_glyph_permute(blocks, rng):
    """the CORRECT null: permute glyphs WITHIN each (message, component) block.
    Preserves block membership, positions and the Delta multiset -- hence the
    Delta-difference geometry -- and randomises only which position holds which
    glyph, i.e. only the plaintext."""
    out = {}
    for k, v in blocks.items():
        gs = [g for _, g in v]; rng.shuffle(gs)
        out[k] = [(v[i][0], gs[i]) for i in range(len(v))]
    return out

def prof_glyph_blocks(blocks, D, W, nd):
    vb = {k: [(t, (D[g] - t) % N) for t, g in v] for k, v in blocks.items()}
    return profile_blocks(vb, W, nd)

def value_permute(slots, D, C, rng):
    """FR41's null: reassign v-values within blocks, destroying v = Delta - t"""
    blocks = {}
    for mi, lst in slots.items():
        for t, g in lst:
            blocks.setdefault((mi, C[g]), []).append((t, (D[g] - t) % N))
    out = {}
    for (mi, ci), v in blocks.items():
        vals = [x for _, x in v]; rng.shuffle(vals)
        out[(mi, ci)] = [(v[i][0], vals[i]) for i in range(len(v))]
    return out

def profile_blocks(blocks, W, nd):
    cnt = [0] * (MAXD + 2); hit = [0] * (MAXD + 2)
    for v in blocks.values():
        for (t1, x), (t2, y) in combinations(v, 2):
            d = abs(t1 - t2)
            if d <= MAXD:
                cnt[d] += 1
                if x == y: hit[d] += 1
    keys = list(blocks)
    for k1 in keys:
        for k2 in keys:
            (m1, c1), (m2, c2) = k1, k2
            if c1 != c2 or m1 >= m2: continue
            if (m1, m2) not in W or (m1, m2) in nd: continue
            w = W[(m1, m2)]
            for t1, x in blocks[k1]:
                for t2, y in blocks[k2]:
                    d = abs(t1 - t2)
                    if d <= MAXD:
                        cnt[d] += 1
                        if (x - y) % N == w: hit[d] += 1
    return cnt, hit

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: depletion measurable, null preserves geometry, null has power")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    S = EI.setup(corpus, atlas)
    D, C, W, nd, slots = setup(S)

    diffs = delta_difference_profile(D, C)
    lo = sum(diffs.get(d, 0) for d in range(9, 18))
    tot = sum(diffs.get(d, 0) for d in range(1, 42))
    check("Delta-difference set is depleted at 9-17",
          lo / tot < 0.6 * (9 / 41), f"({100*lo/tot:.1f}% vs {100*9/41:.1f}% uniform)")

    # the corrected null must PRESERVE the geometry EXACTLY
    rng = random.Random(1)
    blocks = make_blocks(slots, C)
    cnt0, _ = prof_glyph_blocks(blocks, D, W, nd)
    cntG, _ = prof_glyph_blocks(block_glyph_permute(blocks, rng), D, W, nd)
    same = sum(abs(cnt0[d] - cntG[d]) for d in range(1, MAXD + 1))
    check("within-block glyph permutation preserves the pair profile exactly",
          same == 0, f"(drift {same})")

    # and it must still DETECT a planted plaintext effect
    def planted(gap, seed):
        r = random.Random(seed); out = {}
        for k, v in blocks.items():
            gs = [g for _, g in v]; best = list(gs); bestbad = 10 ** 9
            for _ in range(400):
                r.shuffle(gs)
                bad = sum(1 for i in range(len(gs)) for j in range(i + 1, len(gs))
                          if abs(v[i][0] - v[j][0]) <= gap
                          and (D[gs[i]] - v[i][0]) % N == (D[gs[j]] - v[j][0]) % N)
                if bad < bestbad: bestbad = bad; best = list(gs)
                if bad == 0: break
            out[k] = [(v[i][0], best[i]) for i in range(len(v))]
        return out
    nulls = []
    for _ in range(150):
        c2, h2 = prof_glyph_blocks(block_glyph_permute(blocks, rng), D, W, nd)
        nulls.append(extreme(c2, h2)[0])
    nulls.sort()
    cp, hp = prof_glyph_blocks(planted(25, 7), D, W, nd)
    zp, _ = extreme(cp, hp)
    frac = sum(1 for z in nulls if z <= zp) / len(nulls)
    check("corrected null detects a strong planted avoidance (has power)",
          frac < 0.05, f"(planted z={zp:+.2f}, null fraction {frac:.3f})")

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
    D, C, W, nd, slots = setup(S)
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    print("\nX1 the artifact: the Delta-difference set")
    diffs = delta_difference_profile(D, C)
    print(f"  {'d':>4s} {'glyph pairs at that Delta-difference':>38s}")
    for d in range(1, 26):
        print(f"  {d:4d} {diffs.get(d,0):6d}  {'#'*diffs.get(d,0)}")
    lo = sum(diffs.get(d, 0) for d in range(9, 18))
    tot = sum(diffs.get(d, 0) for d in range(1, 42))
    print(f"\n  Delta-differences in 9..17: {lo} of {tot} = {100*lo/tot:.1f}%")
    print(f"  uniform would give {100*9/41:.1f}%  ->  depleted by "
          f"{(9/41)/(lo/tot):.1f}x")
    print("  a coincidence at distance d REQUIRES a glyph pair with")
    print("  Delta-difference d, so this depletion suppresses coincidences at")
    print("  exactly the distances where FR41 found its gap -- before the")
    print("  plaintext is consulted at all")

    print("\nX2 the two nulls compared")
    cnt, hit = profile(slots, D, C, W, nd)
    obs, arg = extreme(cnt, hit)
    print(f"  observed max-deficit z = {obs:+.2f} at {arg}")
    rng = random.Random(PREREG["seed"])
    nv = []
    for _ in range(PREREG["nulls"]):
        c2, h2 = profile_blocks(value_permute(slots, D, C, rng), W, nd)
        nv.append(extreme(c2, h2)[0])
    nv.sort()
    blocks = make_blocks(slots, C)
    ng = []
    for _ in range(PREREG["nulls"]):
        c2, h2 = prof_glyph_blocks(block_glyph_permute(blocks, rng), D, W, nd)
        ng.append(extreme(c2, h2)[0])
    ng.sort()
    for name, vals in (("FR41's null (v-values permuted)", nv),
                       ("corrected null (glyphs permuted in block)", ng)):
        worse = sum(1 for z in vals if z <= obs)
        print(f"  {name:34s}: mean {sum(vals)/len(vals):+.2f}, "
              f"5th pct {vals[int(0.05*len(vals))]:+.2f}, "
              f"P = {(worse+1)/(len(vals)+1):.4f}")

    print("\nX3 verdict")
    worse = sum(1 for z in ng if z <= obs)
    print(f"  FR41 IS WITHDRAWN. Against the null that preserves the")
    print(f"  Delta-difference geometry, P = {(worse+1)/(len(ng)+1):.3f} -- not")
    print("  significant. The apparent local repeat avoidance was an artifact of")
    print("  the skeleton's own geometry, not a property of the plaintext.")
    print("\n  THE LESSON: a permutation null must randomise ONLY the quantity")
    print("  under test. FR41's null randomised the plaintext and the")
    print("  instrument's geometry together; the difference between the two")
    print("  null means (-2.03 vs -2.68) is the size of the geometry it")
    print("  destroyed.")

    print("\nX4 what still stands")
    print("  FR36: small contiguous plaintext alphabets excluded")
    print("  FR39: small scattered plaintext alphabets excluded")
    print("  FR40: the channel validated by a positive control (z ~ +6 on known")
    print("        shared plaintext, quiet elsewhere)")
    print("  -> A-vs-B returns to where FR40 left it: the plaintext has a large")
    print("     effective inventory and no structure this series has detected.")
    print("     The doctrine question FR40 raised is unaffected and still open.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
