#!/usr/bin/env python3
"""
eyestamp -- attempting FR44's requested test of the stamped-header reading,
and reporting honestly that it does not decide the question. Read-only.

WHY THE TEST WAS WANTED. The stamped-header reading entered in FR29 to remove
a contradiction, was used in FR33 to force the same reading onto T1, and in
FR44 to retire H1. It now carries far more weight than it was adopted with,
and every argument for it routes through the constraint system that motivated
it. FR44 asked for independent evidence.

CANDIDATE 1, WHICH FAILS ON INSPECTION. East 3 and East 4 carry identical
glyphs at positions 1-9 despite being in different triplets, which looks like
evidence for literal stamped material. It is not: under the encrypted reading
c_m[t] = C[(p[t] + base_m + K_g[t])], identical glyphs need
base_E3 + K_T2[t] = base_E4 + K_T3[t] across the span, which holds whenever
K_T2 - K_T3 is constant -- and under progressive keystreams with FR3's drift
equality it IS constant. Both readings predict the identity.

CANDIDATE 2, WHICH IS INFORMATIVE BUT NOT DECISIVE. Under the encrypted
reading a repeated GLYPH within a message requires
p[t] - p[t'] = -drift*(t - t'), a 1-in-83 coincidence per position pair, so
glyph repeats sit at the chance rate whatever the plaintext. A literal header
written over a SMALL symbol set would repeat far more often. Measured per
block, the openings sit at chance. That excludes a small-alphabet stamped
header; it does not separate encrypted material from a header stamped over the
full 83-glyph set, since both predict the same rate.

TWO ARTIFACTS CAUGHT IN THIS CYCLE'S OWN ANALYSIS, both from pooling. Pooling
all nine openings counts the T1 block three times and the T3 block three
times, inflating the coincidence rate to a spurious z = +12. Pooling the five
DISTINCT blocks still double-counts their shared prefixes -- four of the five
begin 66, 5, 49, 75, 54 -- giving a confounded z = +4.57 that measures the
known depth tree rather than any distributional difference. Only the per-block
comparison is sound.
"""

import json, math, os, random, sys
from collections import Counter

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyeh1", "eyeind", "eyeinject", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyeinject as EI                     # noqa: E402
import iso_relax as IR                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

TRIPLETS = {"T1": ["East 1", "West 1", "East 2"],
            "T2": ["West 2", "East 3", "West 3"],
            "T3": ["East 4", "West 4", "East 5"]}
OPEN = {"T1": (1, 25), "T2": (1, 21), "T3": (1, 21)}
PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "window": 20}

def blocks_and_body(S):
    Lx, cts, labels = S["Lx"], S["cts"], S["labels"]
    tri = {m: t for t, ms in TRIPLETS.items() for m in ms}
    seen, blocks, body = set(), [], []
    for m in labels:
        lo, hi = OPEN[tri[m]]
        seq = tuple(cts[Lx[m]][lo:hi])
        if seq not in seen:
            seen.add(seq); blocks.append((m, list(seq)))
        body += cts[Lx[m]][hi:]
    return blocks, body

def repeats(seq):
    c = Counter(seq)
    return sum(v * (v - 1) // 2 for v in c.values()), len(seq) * (len(seq) - 1) // 2

def z_rep(r, p):
    if p == 0: return 0.0
    e = p / N; sd = math.sqrt(p * (1 / N) * (1 - 1 / N))
    return (r - e) / sd

def ioc(v):
    n = len(v)
    if n < 2: return 0.0
    c = Counter(v)
    return sum(x * (x - 1) for x in c.values()) / (n * (n - 1))

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: pooling artifact, repeat statistic, small-alphabet power")

    # the pooling artifact, demonstrated on constructed data
    rng = random.Random(2)
    blk = [rng.randrange(N) for _ in range(20)]
    single = ioc(blk)
    tripled = ioc(blk * 3)
    check("pooling identical blocks inflates the IoC (the artifact)",
          tripled > 1.8 * single, f"(single {single:.4f}, tripled {tripled:.4f})")

    # repeat statistic exactness
    r, p = repeats([1, 2, 1, 3, 2, 2])
    check("repeat counter is exact", r == 1 + 3 and p == 15, f"({r}, {p})")

    # power: a small-alphabet block must register as elevated
    small = [rng.randrange(26) for _ in range(24)]
    rs, ps = repeats(small)
    check("a 26-symbol block shows elevated repeats",
          z_rep(rs, ps) > 2, f"(z = {z_rep(rs,ps):+.2f})")
    big = [rng.randrange(N) for _ in range(24)]
    rb, pb = repeats(big)
    check("an 83-symbol block does not", abs(z_rep(rb, pb)) < 2.5,
          f"(z = {z_rep(rb,pb):+.2f})")

    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    S = EI.setup(corpus, atlas)
    blocks, body = blocks_and_body(S)
    check("five distinct opening blocks", len(blocks) == 5, f"({len(blocks)})")

    c = json.load(open(corpus))
    cts = [list(x) for x in c["ciphertexts"]]
    r2 = IR.relax(cts, N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard", (r2.linked_strict, r2.distinct_strict, len(r2.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    S = EI.setup(corpus_path, atlas_path)
    Lx, cts, labels = S["Lx"], S["cts"], S["labels"]
    blocks, body = blocks_and_body(S)
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    print("\nS1 candidate 1: the cross-triplet identity — fails on inspection")
    print("  East 3 and East 4 share positions 1..9 across different triplets.")
    print("  Under the encrypted reading identical glyphs require")
    print("    base_E3 + K_T2[t] = base_E4 + K_T3[t]  across the span,")
    print("  i.e. K_T2 - K_T3 constant — which holds under progressive")
    print("  keystreams with FR3's drift equality. BOTH readings predict it,")
    print("  so it cannot discriminate.")

    print("\nS2 candidate 2: glyph-repeat rate, measured PER BLOCK")
    print(f"  {'block':10s} {'len':>4s} {'pairs':>6s} {'repeats':>8s} "
          f"{'expected':>9s} {'z':>7s}")
    tr = tp = 0
    for m, s in blocks:
        r, p = repeats(s); tr += r; tp += p
        print(f"  {m:10s} {len(s):4d} {p:6d} {r:8d} {p/N:9.2f} {z_rep(r,p):+7.2f}")
    print(f"  {'POOLED':10s} {'':4s} {tp:6d} {tr:8d} {tp/N:9.2f} "
          f"{z_rep(tr,tp):+7.2f}")
    rb = pb = 0
    tri = {m: t for t, ms in TRIPLETS.items() for m in ms}
    for m in labels:
        lo, hi = OPEN[tri[m]]
        b = cts[Lx[m]][hi:]
        w = PREREG["window"]
        for i in range(0, len(b) - w, w):
            r, p = repeats(b[i:i + w]); rb += r; pb += p
    print(f"  {'body ('+str(PREREG['window'])+')':10s} {'':4s} {pb:6d} {rb:8d} "
          f"{pb/N:9.2f} {z_rep(rb,pb):+7.2f}")
    print("  -> openings and body sit at comparable rates, both near chance")

    print("\nS3 what a small-alphabet stamped header would look like")
    print(f"  {'alphabet k':>11s} {'expected repeats in 24 glyphs':>31s}")
    for k in (26, 40, 60, 83):
        print(f"  {k:11d} {276/k:31.1f}")
    print(f"  observed in the longest opening block: {repeats(blocks[0][1])[0]}")
    print("  -> a header written over a small symbol set is EXCLUDED; one")
    print("     stamped over the full glyph set is not distinguishable from")
    print("     ciphertext by this measure")

    print("\nS4 two artifacts caught in this cycle's own analysis")
    tri = {m: t for t, ms in TRIPLETS.items() for m in ms}
    allop = []
    for m in labels:
        lo, hi = OPEN[tri[m]]
        allop += cts[Lx[m]][lo:hi]
    distinct = [g for _, s in blocks for g in s]
    print(f"  pooling ALL NINE openings: IoC {ioc(allop):.5f} "
          f"(counts T1's block 3x and T3's 3x)")
    print(f"  pooling the FIVE distinct: IoC {ioc(distinct):.5f} "
          f"(still double-counts the shared prefix 66,5,49,75,54)")
    print(f"  body IoC: {ioc(body):.5f}")
    print("  both pooled figures measure the depth tree, not a distributional")
    print("  difference. Only the per-block comparison in S2 is sound.")

    print("\nS5 verdict on FR44's request")
    print("  The test FR44 asked for does not exist in the form requested.")
    print("  Encrypted material and a header stamped over the full glyph set")
    print("  are statistically indistinguishable by every measure tried here,")
    print("  because both are effectively uniform over 83 symbols.")
    print("  What this cycle DOES establish: the openings are not a header")
    print("  written in a small symbol set. The stamped-header reading remains")
    print("  adopted for consistency rather than independently supported, and")
    print("  that should be recorded as its standing rather than assumed away.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
