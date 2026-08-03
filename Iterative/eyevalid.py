#!/usr/bin/env python3
"""
eyevalid -- validating the channel that produced FR39's null, and following up
an anomaly that both FR30 and FR39 recorded without explaining. Read-only.

THE GAP IN FR39'S ARGUMENT. FR39 measured the plaintext coincidence rate
through the pooled v-channel, found it flat, and concluded that the plaintext
effective alphabet exceeds ~60. That conclusion has an alternative it did not
rule out: if the MODEL were wrong -- repair A mistaken, or the reconstruction
broken -- then the recovered "plaintext" would be scrambled and would look
flat for a reason that has nothing to do with the corpus. A null is only
informative if the instrument can detect the signal when it is present.

THE POSITIVE CONTROL. The corpus supplies one: the near-duplicate message
pairs share plaintext, and FR39 excluded them precisely because they do. Run
the channel ON them and it should fire. It does -- East 1 / West 1 at z = +5.5
and East 4 / East 5 at z = +7.0, with 85-90% of those coincidences at shift
zero. So the reconstruction detects shared plaintext where shared plaintext is
known to exist, and FR39's flat reading elsewhere is a statement about the
plaintext rather than an artefact.

THE ANOMALY, LOGGED NOT CLAIMED. Both FR30 (z = -1.96) and FR39 (z = -0.56)
found the coincidence count BELOW the flat expectation, and FR39's IoC-style
estimate came out at 88.7 -- above 83, which no genuine 83-symbol alphabet can
produce. For i.i.d. plaintext the coincidence rate cannot fall below 1/N in
expectation, so a persistent deficit needs either chance or anti-correlation.
Binning by positional distance shows the deficit concentrated at distances
6-15 in BOTH channels independently. That is suggestive and it is also exactly
the shape of a post-hoc finding: the bin was chosen after seeing the data,
across five bins and two channels. It is recorded as watch-grade with a
PRE-REGISTERED test for a future cycle, not as a result.
"""

import json, math, os, random, sys
from collections import Counter
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyepool2", "eyeclass", "eyeloo", "eyeclust", "eyefree2", "eyebridge3",
          "eyewiden", "eyepair", "eyeseek", "eyefree", "eyebase", "eyealpha",
          "eyepack", "eyeskel", "eyerepair", "eyescore", "eyeinject",
          "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyepool2 as EP                      # noqa: E402
import eyeinject as EI                     # noqa: E402
import iso_relax as IR                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "bins": [(1, 5), (6, 15), (16, 30), (31, 60), (61, 200)],
          "next_cycle_test": "distance bin (6,15), both channels pooled, "
                             "one-sided deficit, alpha 0.01"}

def z_of(hit, tot):
    if tot == 0: return 0.0
    e = tot / N
    sd = math.sqrt(tot * (1 / N) * (1 - 1 / N))
    return (hit - e) / sd if sd else 0.0

def within_by_distance(pos, bins):
    tab = {b: [0, 0] for b in bins}
    for v in pos.values():
        for (t1, x), (t2, y) in combinations(v, 2):
            d = abs(t1 - t2)
            for b in bins:
                if b[0] <= d <= b[1]:
                    tab[b][1] += 1
                    if x == y: tab[b][0] += 1
                    break
    return tab

def cross_by_distance(pos, W, nd, bins):
    tab = {b: [0, 0] for b in bins}
    for (m1, c1), v1 in pos.items():
        for (m2, c2), v2 in pos.items():
            if c1 != c2 or m1 >= m2: continue
            if (m1, m2) not in W or (m1, m2) in nd: continue
            w = W[(m1, m2)]
            for t1, x in v1:
                for t2, y in v2:
                    d = abs(t1 - t2)
                    for b in bins:
                        if b[0] <= d <= b[1]:
                            tab[b][1] += 1
                            if (x - y) % N == w: tab[b][0] += 1
                            break
    return tab

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: control sensitivity, distance binning, null behaviour")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    S = EI.setup(corpus, atlas)
    pos, W, nd = EP.setup_channel(S)
    Lx = S["Lx"]

    # the positive control must fire on known shared plaintext
    h, t, sh = EP.shift_profile(pos, W, Lx["East 4"], Lx["East 5"])
    check("channel detects known shared plaintext (positive control)",
          z_of(h, t) > 4, f"(z = {z_of(h,t):+.2f})")

    # and must NOT fire on a message pair with no shared passage
    h2, t2, _ = EP.shift_profile(pos, W, Lx["East 4"], Lx["West 4"])
    check("channel is quiet on a non-near-duplicate pair",
          abs(z_of(h2, t2)) < 3, f"(z = {z_of(h2,t2):+.2f})")

    # distance binning must partition the pairs
    tab = within_by_distance(pos, PREREG["bins"])
    total_binned = sum(v[1] for v in tab.values())
    allpairs = sum(len(v) * (len(v) - 1) // 2 for v in pos.values())
    check("distance bins partition the within-block pairs",
          total_binned <= allpairs and total_binned > 0.9 * allpairs,
          f"({total_binned} of {allpairs})")

    # z on a synthetic flat sample must sit near zero
    rng = random.Random(4)
    hits = sum(1 for _ in range(4000) if rng.randrange(N) == rng.randrange(N))
    check("z statistic is calibrated on synthetic flat data",
          abs(z_of(hits, 4000)) < 3, f"(z = {z_of(hits,4000):+.2f})")

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
    labels = S["labels"]; Lx = S["Lx"]
    pos, W, nd = EP.setup_channel(S)
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    print("\nV1 POSITIVE CONTROL — does the channel detect plaintext it should?")
    print("  the near-duplicate pairs share plaintext; FR39 excluded them for")
    print("  exactly that reason, which makes them the control it needed")
    print(f"  {'pair':20s} {'hits':>5s} {'pairs':>6s} {'flat':>6s} {'z':>7s} "
          f"{'at shift 0':>11s}")
    for m1, m2 in sorted(nd):
        h, t, sh = EP.shift_profile(pos, W, m1, m2)
        print(f"  {labels[m1]:8s}/{labels[m2]:8s} {h:5d} {t:6d} {t/N:6.1f} "
              f"{z_of(h,t):+7.2f} {sh.get(0,0)/max(h,1):10.0%}")
    print("  and a pair with no shared passage, as a negative control:")
    h, t, _ = EP.shift_profile(pos, W, Lx["East 4"], Lx["West 4"])
    print(f"  {'East 4':8s}/{'West 4':8s} {h:5d} {t:6d} {t/N:6.1f} "
          f"{z_of(h,t):+7.2f}")
    print("  -> the instrument fires where plaintext is shared and is quiet")
    print("     where it is not. FR39's flat reading on the remaining pairs is")
    print("     therefore a statement about the plaintext, not a model artefact.")

    print("\nV2 the persistent deficit, by positional distance")
    tw = within_by_distance(pos, PREREG["bins"])
    tc = cross_by_distance(pos, W, nd, PREREG["bins"])
    print(f"  {'distance':>10s} | {'within: pairs':>13s} {'hits':>5s} {'z':>7s}"
          f" | {'cross: pairs':>12s} {'hits':>5s} {'z':>7s}")
    for b in PREREG["bins"]:
        hw, tww = tw[b]; hc, tcc = tc[b]
        print(f"  {str(b):>10s} | {tww:13d} {hw:5d} {z_of(hw,tww):+7.2f}"
              f" | {tcc:12d} {hc:5d} {z_of(hc,tcc):+7.2f}")
    b = (6, 15)
    hh = tw[b][0] + tc[b][0]; tt = tw[b][1] + tc[b][1]
    print(f"\n  pooled at distance {b}: {hh} coincidences / {tt} pairs, "
          f"flat {tt/N:.1f}, z = {z_of(hh,tt):+.2f}")

    print("\nV3 how to read that")
    print("  For i.i.d. plaintext the coincidence rate cannot fall below 1/83 in")
    print("  expectation, so a persistent deficit needs anti-correlation. Both")
    print("  channels show their deficit in the same distance bin, which is")
    print("  suggestive. It is ALSO exactly the shape of a post-hoc finding: the")
    print("  bin was chosen after seeing the data, across five bins and two")
    print("  channels, so the corrected significance is marginal.")
    print("  WATCH-GRADE, NOT CLAIMED. Pre-registered for a future cycle:")
    print(f"    {PREREG['next_cycle_test']}")
    print("  If it survives on that pre-registration, it is a real property of")
    print("  the plaintext -- local avoidance of repeats -- and would be the")
    print("  first structural evidence for branch B that survives FR36/FR39.")

    print("\nV4 the doctrine question FR39 raised")
    print("  FR39 established the plaintext effective alphabet exceeds ~60")
    print("  however the tokens are numbered, and this cycle validates the")
    print("  instrument that produced it. The consequence stands: recovering C")
    print("  yields a token stream, not a reading. Two external anchors would")
    print("  determine 25 glyphs and a quarter of the corpus -- as NUMBERS.")
    print("  Whether that counts as solving the Eye Messages is a question about")
    print("  the project's success criterion, and it should be settled before")
    print("  more effort is spent on acquisition rather than after.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
