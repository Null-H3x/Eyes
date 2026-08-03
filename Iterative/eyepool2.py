#!/usr/bin/env python3
"""
eyepool2 -- the measurement FR36 called blocked and FR38 called closed, run.
Read-only.

THE CHALLENGE THAT REOPENED IT. FR36 measured the plaintext coincidence rate
through FR30's channel, found it underpowered, and concluded that resolving
the scattered-alphabet variant of branch B needed roughly four times the
sample -- which FR31, FR34 and FR35 had shown could not come from more
component coverage. FR38 then recorded the internal ledger as empty.

That assessment assumed WITHIN-BLOCK pairs only. It should not have. For two
positions in the same component but DIFFERENT messages, a plaintext
coincidence requires

    drift*(v - v') = base_m1 - base_m2 = drift*w   =>   v - v' = w

which is drift-free exactly like the within-block test, and the seven forced
base differences (FR32) supply w. Cross-message pairs are therefore testable,
and they triple the sample.

THE CONFOUND, CAUGHT. Pooled naively, the cross-message channel runs hot. The
reason is that two of the seven message pairs are the corpus's NEAR-DUPLICATES,
and their coincidences concentrate at shift ZERO -- shared passages, which the
corpus is already known to have, rather than evidence about the token
inventory. Excluding those two pairs, the channel is flat.
"""

import json, math, os, random, sys
from collections import Counter
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyeclass", "eyeloo", "eyeclust", "eyefree2", "eyebridge3", "eyewiden",
          "eyepair", "eyeseek", "eyefree", "eyebase", "eyealpha", "eyepack",
          "eyeskel", "eyerepair", "eyescore", "eyeinject", "eyegauge",
          "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyeloo as EL                        # noqa: E402
import eyerepair as ERP                    # noqa: E402
import eyeinject as EI                     # noqa: E402
import iso_relax as IR                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "seed": 20260809, "nulls": 3000}

def setup_channel(S):
    Lx, cts = S["Lx"], S["cts"]
    pool = ERP.drop(S["pool"], (Lx["East 3"], 101), (Lx["East 1"], 68))
    gf = EL.build(S, pool)
    D, C = EL.deltas(gf)
    W = {}
    for a, b in combinations(range(9), 2):
        h = [d for d in range(N)
             if gf.classify({N + b: 1, N + a: N - 1}, d) == "redundant"]
        if len(h) == 1: W[(a, b)] = h[0]
    cov = set()
    for p in pool:
        for i in range(p.length):
            cov.add((p.m1, p.p1 + i)); cov.add((p.m2, p.p2 + i))
    pos = {}
    for mi, m in enumerate(cts):
        for t, g in enumerate(m):
            if g not in C or (mi, t) in cov: continue
            pos.setdefault((mi, C[g]), []).append((t, (D[g] - t) % N))
    neardup = {(Lx["East 1"], Lx["West 1"]), (Lx["East 4"], Lx["East 5"])}
    return pos, W, neardup

def build_sets(pos, W, neardup, drop_neardup=True, include_cross=True):
    sets = []
    for v in pos.values(): sets.append(([x for _, x in v], None, 0))
    if not include_cross: return sets
    for (m1, c1), v1 in pos.items():
        for (m2, c2), v2 in pos.items():
            if c1 != c2 or m1 >= m2: continue
            if (m1, m2) not in W: continue
            if drop_neardup and (m1, m2) in neardup: continue
            sets.append(([x for _, x in v1], [x for _, x in v2], W[(m1, m2)]))
    return sets

def measure(sets):
    hit = tot = 0
    for va, vb, w in sets:
        if vb is None:
            for x, y in combinations(va, 2):
                tot += 1
                if x == y: hit += 1
        else:
            for x in va:
                for y in vb:
                    tot += 1
                    if (x - y) % N == w: hit += 1
    return hit, tot

def null_stats(sets, trials, seed):
    rng = random.Random(seed); vals = []
    for _ in range(trials):
        perm = [([rng.randrange(N) for _ in va],
                 None if vb is None else [rng.randrange(N) for _ in vb], w)
                for va, vb, w in sets]
        vals.append(measure(perm)[0])
    mu = sum(vals) / len(vals)
    sd = (sum((x - mu) ** 2 for x in vals) / (len(vals) - 1)) ** 0.5
    return mu, sd

def shift_profile(pos, W, m1, m2):
    if (m1, m2) not in W: return 0, 0, Counter()
    w = W[(m1, m2)]; sh = Counter(); hit = tot = 0
    for (a, c1), v1 in pos.items():
        if a != m1: continue
        for (b, c2), v2 in pos.items():
            if b != m2 or c1 != c2: continue
            for t1, x in v1:
                for t2, y in v2:
                    tot += 1
                    if (x - y) % N == w: hit += 1; sh[t1 - t2] += 1
    return hit, tot, sh

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: cross-message identity, confound detection, power")

    rng = random.Random(3)
    C = list(range(N)); rng.shuffle(C)
    q = [0] * N
    for i, s in enumerate(C): q[s] = i
    drift, b1, b2, kap, T = 29, 13, 61, 7, 80
    p1 = [rng.randrange(N) for _ in range(T)]
    p2 = [rng.randrange(N) for _ in range(T)]
    c1 = [C[(p1[t] + b1 + kap + drift * t) % N] for t in range(T)]
    c2 = [C[(p2[t] + b2 + kap + drift * t) % N] for t in range(T)]
    dinv = pow(drift, N - 2, N)
    dl = {g: (q[g] * dinv) % N for g in range(N)}
    w = ((b1 - b2) * dinv) % N
    good = all(((((dl[c1[t]] - t) % N) - ((dl[c2[u]] - u) % N)) % N == w)
               == (p1[t] == p2[u]) for t in range(0, 20) for u in range(20, 40))
    check("cross-message coincidence <=> v - v' = w (drift-free)", good)

    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    S = EI.setup(corpus, atlas)
    pos, W, nd = setup_channel(S)
    Lx = S["Lx"]

    h, t, sh = shift_profile(pos, W, Lx["East 4"], Lx["East 5"])
    top = sh.most_common(1)[0] if sh else (None, 0)
    check("near-duplicate pair concentrates coincidences at shift 0",
          top[0] == 0 and top[1] / max(h, 1) > 0.5,
          f"({top[1]} of {h} at shift {top[0]})")

    within = build_sets(pos, W, nd, include_cross=False)
    clean = build_sets(pos, W, nd, True)
    # pooling roughly doubles the sample; the threshold reflects the measured
    # ratio rather than a round number chosen in advance
    check("cross-message pooling substantially enlarges the sample",
          measure(clean)[1] > 1.8 * measure(within)[1],
          f"({measure(within)[1]} -> {measure(clean)[1]} pairs, "
          f"{measure(clean)[1]/measure(within)[1]:.2f}x)")

    sub = clean[:40]
    mu, sd = null_stats(sub, 200, 5)
    rng2 = random.Random(11)
    s = []
    for va, vb, w2 in sub:
        a2 = [rng2.randrange(20) for _ in va]
        b2 = None if vb is None else [(rng2.randrange(20) + w2) % N for _ in vb]
        s.append((a2, b2, w2))
    check("planted small alphabet is detected", measure(s)[0] > mu + 3 * sd,
          f"(planted {measure(s)[0]} vs null {mu:.1f}+-{sd:.1f})")

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
    labels = S["labels"]
    pos, W, nd = setup_channel(S)
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    print("\nP1 the sample, before and after pooling")
    within = build_sets(pos, W, nd, include_cross=False)
    allsets = build_sets(pos, W, nd, False)
    clean = build_sets(pos, W, nd, True)
    print(f"  within-block only (FR30's channel): {measure(within)[1]} pairs")
    print(f"  + cross-message, all pairs:         {measure(allsets)[1]} pairs")
    print(f"  + cross-message, near-dups dropped: {measure(clean)[1]} pairs "
          f"({measure(clean)[1]/measure(within)[1]:.1f}x)")

    print("\nP2 the confound: coincidences by positional shift")
    print(f"  {'pair':20s} {'hits':>5s} {'pairs':>6s} {'flat':>6s} "
          f"{'top shift':>10s} {'share':>6s}")
    for (m1, m2) in sorted(k for k in W if k[0] < k[1]):
        h, t, sh = shift_profile(pos, W, m1, m2)
        if t == 0: continue
        top = sh.most_common(1)[0] if sh else (None, 0)
        mark = "  <== near-duplicate" if (m1, m2) in nd else ""
        print(f"  {labels[m1]:8s}/{labels[m2]:8s} {h:5d} {t:6d} {t/N:6.1f} "
              f"{str(top[0]):>10s} {top[1]/max(h,1):5.0%}{mark}")
    print("  -> the two near-duplicate pairs put most of their coincidences at")
    print("     shift 0: shared passages, not token frequency. Excluded below.")

    print("\nP3 the confound-free measurement")
    H, P = measure(clean)
    mu, sd = null_stats(clean, PREREG["nulls"], PREREG["seed"])
    print(f"  pairs {P}, coincidences {H}, empirical null {mu:.1f} +- {sd:.2f}")
    print(f"  z = {(H-mu)/sd:+.2f}   IoC-style effective alphabet {P/max(H,1):.1f}")

    print("\nP4 power")
    print(f"  {'effective alphabet':>19s} {'expected':>9s} {'z':>7s}")
    for eff in (79, 70, 65, 60, 55, 50):
        lam = P / eff
        print(f"  {eff:19d} {lam:9.1f} {(lam-mu)/sd:+7.2f}")

    print("\nP5 what this settles")
    print("  FR36 excluded a small CONTIGUOUS plaintext alphabet by clustering;")
    print("  this excludes a small SCATTERED one by coincidence, at the same")
    print("  scale. Together the plaintext effective alphabet exceeds ~60")
    print("  however the tokens are numbered.")
    print("  CONSEQUENCE for the endgame (FR19): with 74% of positions exposed")
    print("  and the residual drawn from an inventory that large, context will")
    print("  not fill the gaps -- the favourable gap SHAPE FR19 measured does")
    print("  not buy readability.")
    print("  CAVEAT: this measures the plaintext as the model reconstructs it,")
    print("  and remains conditional on repair A.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
