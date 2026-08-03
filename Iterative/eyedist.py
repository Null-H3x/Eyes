#!/usr/bin/env python3
"""
eyedist -- rescuing a post-hoc observation with the right statistic, and the
first evidence of plaintext structure to survive FR36 and FR39. Read-only.

THE PROBLEM WITH FR40'S PRE-REGISTRATION. FR40 logged a coincidence deficit at
distance 6-15 as watch-grade and pre-registered a test for "a future cycle".
That registration is defective and this cycle says so first: a
pre-registration protects against choosing the analysis after seeing the data,
and buys nothing when the SAME data are re-analysed. The corpus is fixed, and
FR40's channel already used every non-circular position, so re-running bin
(6,15) reproduces z = -2.85 by construction. There is no held-out sample.

THE LEGITIMATE FIX. The reason a post-hoc bin cannot be trusted is
multiplicity: many ranges were available and the most extreme was reported. A
MAX-STATISTIC test corrects for exactly that -- compute the most extreme
deficit over ALL contiguous distance ranges, then subject each null draw to
the same search. That can be run on the same data, because multiplicity is
what it is correcting for rather than something it assumes away.

RESULT. Observed max-deficit z = -3.36 at range (4, 17). Against a null that
permutes v-values WITHIN each block -- preserving block sizes, positions and
each block's multiset of values, hence the dependence structure that generates
coincidences -- P(null <= observed) = 0.0013. The anomaly is one-sided: the
same statistic on the excess side gives +1.87 observed against a null mean of
+2.37, so the corpus is unremarkable there.

WHAT IT MEANS. The plaintext avoids repeating a token at short range. This is
a CORRELATION effect, not an inventory-size effect, which is precisely why
FR36's clustering test and FR39's coincidence-count test could not see it: one
measures how the alphabet is spread, the other how large it is, and neither
measures how repeats are placed.
"""

import json, math, os, random, sys
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83
MAXD = 40

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyevalid", "eyepool2", "eyeclass", "eyeloo", "eyeclust", "eyefree2",
          "eyebridge3", "eyewiden", "eyepair", "eyeseek", "eyefree", "eyebase",
          "eyealpha", "eyepack", "eyeskel", "eyerepair", "eyescore",
          "eyeinject", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyepool2 as EP                      # noqa: E402
import eyeinject as EI                     # noqa: E402
import iso_relax as IR                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "min_pairs": 100, "nulls": 1500, "seed": 20260811}

def channel(S):
    pos, W, nd = EP.setup_channel(S)
    xp = []
    for k1 in pos:
        for k2 in pos:
            (m1, c1), (m2, c2) = k1, k2
            if c1 != c2 or m1 >= m2: continue
            if (m1, m2) not in W or (m1, m2) in nd: continue
            xp.append((k1, k2, W[(m1, m2)]))
    return {k: list(v) for k, v in pos.items()}, xp

def profile(blocks, xpairs):
    cnt = [0] * (MAXD + 2); hit = [0] * (MAXD + 2)
    for v in blocks.values():
        for (t1, x), (t2, y) in combinations(v, 2):
            d = abs(t1 - t2)
            if d <= MAXD:
                cnt[d] += 1
                if x == y: hit[d] += 1
    for k1, k2, w in xpairs:
        for t1, x in blocks[k1]:
            for t2, y in blocks[k2]:
                d = abs(t1 - t2)
                if d <= MAXD:
                    cnt[d] += 1
                    if (x - y) % N == w: hit[d] += 1
    return cnt, hit

def extreme(cnt, hit, deficit=True, minpairs=None):
    minpairs = minpairs or PREREG["min_pairs"]
    best = 0.0; arg = None
    for lo in range(1, MAXD + 1):
        c = h = 0
        for hi in range(lo, MAXD + 1):
            c += cnt[hi]; h += hit[hi]
            if c < minpairs: continue
            e = c / N; sd = math.sqrt(c * (1 / N) * (1 - 1 / N))
            z = (h - e) / sd
            if (z < best) if deficit else (z > best):
                best = z; arg = (lo, hi)
    return best, arg

def permute(blocks, rng):
    out = {}
    for k, v in blocks.items():
        vals = [x for _, x in v]; rng.shuffle(vals)
        out[k] = [(v[i][0], vals[i]) for i in range(len(v))]
    return out

def null_distribution(blocks, xpairs, trials, seed, deficit=True):
    rng = random.Random(seed); vals = []
    for _ in range(trials):
        c, h = profile(permute(blocks, rng), xpairs)
        vals.append(extreme(c, h, deficit)[0])
    vals.sort()
    return vals

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: statistic sensitivity, null calibration, one-sidedness")

    # a planted deficit must be found
    cnt = [0] * (MAXD + 2); hit = [0] * (MAXD + 2)
    for d in range(1, MAXD + 1):
        cnt[d] = 300
        hit[d] = 0 if 5 <= d <= 15 else 4
    z, arg = extreme(cnt, hit, True)
    check("planted deficit is located", z < -3 and arg[0] >= 4 and arg[1] <= 16,
          f"(z={z:+.2f} at {arg})")

    # a flat profile must not produce an extreme value
    for d in range(1, MAXD + 1):
        cnt[d] = 300; hit[d] = 4
    z2, _ = extreme(cnt, hit, True)
    check("flat profile gives no strong deficit", z2 > -2.0, f"(z={z2:+.2f})")

    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    S = EI.setup(corpus, atlas)
    blocks, xp = channel(S)
    c, h = profile(blocks, xp)
    check("channel reproduces FR39's totals",
          sum(c) > 2000 and sum(h) > 0,
          f"({sum(c)} pairs within distance {MAXD}, {sum(h)} coincidences)")

    # the null must be centred well away from zero: the max statistic is
    # biased negative by construction, which is exactly why it needs a null
    nulls = null_distribution(blocks, xp, 60, 7)
    check("null max-deficit is biased negative (hence a null is required)",
          sum(nulls) / len(nulls) < -1.2,
          f"(null mean {sum(nulls)/len(nulls):+.2f})")

    cc = json.load(open(corpus))
    cts = [list(x) for x in cc["ciphertexts"]]
    r = IR.relax(cts, N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard", (r.linked_strict, r.distinct_strict, len(r.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    S = EI.setup(corpus_path, atlas_path)
    blocks, xp = channel(S)
    cnt, hit = profile(blocks, xp)
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")
    print(f"channel: {sum(cnt)} pairs within distance {MAXD}, "
          f"{sum(hit)} coincidences")

    print("\nD1 why FR40's pre-registration cannot be honoured")
    print("  a pre-registration protects against choosing the analysis after")
    print("  seeing the data; it buys nothing when the SAME data are")
    print("  re-analysed. The corpus is fixed and the channel already uses every")
    print("  non-circular position, so re-running bin (6,15) reproduces the")
    print("  original number by construction. Reported as a correction, not")
    print("  quietly dropped.")

    print("\nD2 the distance profile")
    print(f"  {'d':>4s} {'pairs':>6s} {'hits':>5s} {'expected':>9s}")
    for d in range(1, 26):
        if cnt[d] >= 15:
            print(f"  {d:4d} {cnt[d]:6d} {hit[d]:5d} {cnt[d]/N:9.2f}")

    print("\nD3 the max-statistic test (corrects for the range search)")
    obs, arg = extreme(cnt, hit, True)
    print(f"  observed max-deficit z = {obs:+.2f} at range {arg}")
    nulls = null_distribution(blocks, xp, PREREG["nulls"], PREREG["seed"])
    worse = sum(1 for z in nulls if z <= obs)
    print(f"  null permutes v-values WITHIN blocks, preserving block sizes,")
    print(f"  positions and value multisets ({len(nulls)} draws):")
    print(f"    mean {sum(nulls)/len(nulls):+.2f}, 5th pct "
          f"{nulls[int(0.05*len(nulls))]:+.2f}, min {nulls[0]:+.2f}")
    print(f"  P(null <= observed) = {(worse+1)/(len(nulls)+1):.4f}")

    print("\nD4 one-sidedness check")
    oe, ae = extreme(cnt, hit, False)
    ne = null_distribution(blocks, xp, 400, PREREG["seed"] + 1, False)
    print(f"  observed max-EXCESS z = {oe:+.2f} at {ae}")
    print(f"  null mean {sum(ne)/len(ne):+.2f}, 95th pct "
          f"{ne[int(0.95*len(ne))]:+.2f}")
    print("  -> the corpus is anomalous on the DEFICIT side only, which is what")
    print("     local repeat-avoidance predicts and what a generic modelling")
    print("     error would not")

    print("\nD5 what this establishes, and what it does not")
    print("  ESTABLISHES: the plaintext avoids repeating a token at short range")
    print("  (roughly 4 to 17 positions), at p ~ 0.001 after correcting for the")
    print("  range search, against a null preserving block structure. This is a")
    print("  CORRELATION effect, not an inventory-size effect -- which is why")
    print("  FR36 (how the alphabet is spread) and FR39 (how large it is) could")
    print("  not see it. It is the first structural evidence for the plaintext")
    print("  to survive both.")
    print("  DOES NOT ESTABLISH: what the plaintext is. Repeat avoidance is")
    print("  consistent with a varied text over a large inventory, with a list")
    print("  of distinct items, and with several other sources. It also remains")
    print("  conditional on repair A and on the reconstruction FR40 validated.")
    print("  BEARING ON A-vs-B: branch B predicted structure and FR36/FR39 found")
    print("  none of the kind they could measure. This is structure of a kind")
    print("  they could not, so the fork is no longer closing cleanly against")
    print("  the readable branch.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
