#!/usr/bin/env python3
"""
eyewords -- batch word-crib testing against the 17 candidate readings.

EYESPIRAL-C. FR121. FR120 showed a blind pattern sweep cannot win: any shape
strong enough to discriminate is too strong to arise by chance. What can win is
a hypothesis with independent reason to hold at a specific place. This tests a
vocabulary of such hypotheses.

THE COVERAGE PROBLEM, learned the hard way. Testing TODELLINENTIETO returned
zero -- but it was testable at exactly ONE of 628 placements (0.2%), because a
15-character word needs 13 specific positions covered and coverage is 44.5% and
fragmented. **A zero from an untestable word is not evidence.** Every word here
is therefore reported with its POWER: testable placements and the chance-hit
expectation, so a negative can be read correctly.

WHAT HAS POWER. Short words (span <= 12) with k >= 3 assertions, landing inside
one of the 12 long covered runs:

    East 4  59-70 (12)   East 5  68-78 (11)   West 4  35-44 (10)
    West 4  53-61  (9)   East 5  84-91  (8)   East 3 127-134 (8)
    East 3  70-77  (8)   West 4 107-113 (7)   West 3  73-79  (7)
    East 5  60-66  (7)   East 4  97-103 (7)   West 4  96-101 (6)

MATCHING is EXACT ISOMORPHISM: same letter -> same plaintext value, and
DIFFERENT letters -> DIFFERENT values. Finnish a/o/y are kept distinct from
a/o/y, since they would be distinct plaintext symbols.

PRE-REGISTERED:
  R1  every word is reported with testable-placement count and chance
      expectation. A zero with expectation < 0.01 is recorded as NO POWER, not
      as evidence.
  R2  a hit is INTERESTING only if the word had k >= 3 and the chance
      expectation was < 0.05.
  R3  the same vocabulary is run against SHUFFLED readings as a null.

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""

import os, sys, io, random, contextlib
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
XD = "XD-MBYG04K-URS3LF"
N = 83

import eyehypo as H

SURV = H.SURVIVORS

VOCAB = {
 # --- Noita core nouns -------------------------------------------------
 "noita":"witch","silma":"eye","silmat":"eyes","kuolema":"death","tuli":"fire",
 "vesi":"water","maa":"earth","ilma":"air","velho":"wizard","taika":"magic",
 "loitsu":"spell","sauva":"wand","juoma":"potion","kammio":"chamber",
 "luola":"cave","vuori":"mountain","metsa":"forest","suo":"swamp",
 # --- cosmology / lore --------------------------------------------------
 "maailma":"world","kaikkeus":"universe","luonto":"nature","taivas":"sky",
 "helvetti":"hell","tuonela":"underworld","alkemia":"alchemy",
 "kulta":"gold","hopea":"silver","elohopea":"mercury","rikki":"sulphur",
 "suola":"salt","smaragdi":"emerald","tabletti":"tablet",
 # --- knowledge / secrecy ----------------------------------------------
 "tieto":"knowledge","totuus":"truth","viisaus":"wisdom","salaisuus":"secret",
 "salattu":"hidden","tositieto":"true knowledge","todellinen":"true",
 "oppi":"doctrine","sana":"word","kirja":"book","teksti":"text",
 "merkki":"sign","kuva":"image","nimi":"name",
 # --- being / spirit ----------------------------------------------------
 "jumala":"god","henki":"spirit","sielu":"soul","elama":"life","kuolla":"die",
 "ihminen":"human","olento":"being","haamu":"ghost","hiisi":"goblin",
 "perkele":"devil","paholainen":"devil",
 # --- qualities / direction --------------------------------------------
 "pyha":"holy","kirous":"curse","siunaus":"blessing","valo":"light",
 "pimeys":"darkness","varjo":"shadow","suuri":"great","pieni":"small",
 "ikuinen":"eternal","alku":"beginning","loppu":"end","ensimmainen":"first",
 "viimeinen":"last","ylhaalla":"above","alhaalla":"below","sisalla":"within",
 # --- Kalevala ----------------------------------------------------------
 "kalevala":"Kalevala","vainamoinen":"Vainamoinen","ilmarinen":"Ilmarinen",
 "louhi":"Louhi","sampo":"Sampo","pohjola":"Pohjola","lemminkainen":"Lemminkainen",
 # --- English -----------------------------------------------------------
 "knowledge":"","wisdom":"","secret":"","truth":"","eternal":"","emerald":"",
 "tablet":"","alchemy":"","creation":"","beginning":"","ending":"",
 "above":"","below":"","within":"","without":"","spirit":"","shadow":"",
 "mercury":"","sulphur":"","dissolve":"","separate":"","essence":"",
 "seeker":"","hidden":"","forbidden":"","remember":"","between":"",
 "thoth":"","hermes":"","tabula":"","smaragdina":"","secretorum":"",
}

LONG_RUNS = [("East 4",59,70),("East 5",68,78),("West 4",35,44),("West 4",53,61),
             ("East 5",84,91),("East 3",127,134),("East 3",70,77),
             ("West 4",107,113),("West 3",73,79),("East 5",60,66),
             ("East 4",97,103),("West 4",96,101)]


def pat_of(w):
    w = w.upper().replace(" ", "")
    pos = {}
    for i, ch in enumerate(w): pos.setdefault(ch, []).append(i)
    out = ['.'] * len(w); nxt = 0
    for _, k, v in sorted([(min(v), k, v) for k, v in pos.items() if len(v) > 1]):
        L = chr(ord('A') + nxt); nxt += 1
        for p in v: out[p] = L
    return "".join(out), sum(len(v) - 1 for v in pos.values() if len(v) > 1)


def scan(pat, idx, covered, ratios):
    groups = defaultdict(list)
    for i, ch in enumerate(pat):
        if ch != '.': groups[ch].append(i)
    hits = []; testable = 0
    ref = ratios[0]
    for m in covered:
        mx = max(covered[m])
        for s in range(0, mx + 1):
            need = [s + i for ps in groups.values() for i in ps]
            if any((m, p) not in idx[ref] for p in need): continue
            testable += 1
            sat = []
            for r in ratios:
                vals = {}; ok = True
                for L, ps in groups.items():
                    vs = {idx[r][(m, s + p)] for p in ps}
                    if len(vs) != 1: ok = False; break
                    vals[L] = vs.pop()
                if ok and len(set(vals.values())) == len(vals): sat.append(r)
            if sat: hits.append((m, s, sat))
    return testable, hits


def selftest():
    ok = []
    def ck(n, c, d=""):
        ok.append((n, bool(c))); print(f"  {n:32s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise RuntimeError(f"{XD} selftest FAILED: {n} {d}")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): env = H.selftest()
    readings, labels, idx = env
    ck("t1_readings", len(readings) == 17, f"{len(readings)}")
    p, k = pat_of("MAAILMA")
    ck("t2_pattern", (p, k) == ("ABB..AB", 3), f"{p} k={k}  M@0,5 A@1,2,6")
    p2, k2 = pat_of("SILMA")
    ck("t3_norepeat", k2 == 0, f"{p2} k={k2}")
    covered = defaultdict(set)
    for (m, c, t, g, v) in readings[SURV[0]]: covered[m].add(t)
    t, h = scan("A..A.", idx, covered, SURV)
    ck("t4_scan_runs", t > 100, f"{t} testable placements for A..A.")
    print(f"selftest {sum(1 for _,p in ok if p)}/{len(ok)} green")
    return readings, labels, idx, covered


def run(env):
    readings, labels, idx, covered = env
    print("=" * 78)
    print("EYEWORDS -- vocabulary batch against the 17 readings")
    print("=" * 78)
    rows = []
    for w, gloss in VOCAB.items():
        pat, k = pat_of(w)
        if k < 1: continue
        testable, hits = scan(pat, idx, covered, SURV)
        chance = 17 * testable * (N ** -k)
        rows.append((w, gloss, pat, k, testable, chance, hits))

    rows.sort(key=lambda r: (-r[3], -r[4]))
    print(f"\n  {'word':16s} {'k':>2s} {'span':>4s} {'test':>5s} {'chance':>9s}  {'hits':>4s}  verdict")
    print("  " + "-" * 74)
    powered = []
    for w, gl, pat, k, testable, chance, hits in rows:
        if k < 3: continue
        if chance < 0.01 and testable < 5:
            verdict = "NO POWER"
        elif hits:
            verdict = f"HIT x{len(hits)}"
            if k >= 3 and chance < 0.05: powered.append((w, hits, chance, k))
        else:
            verdict = "clean" if chance >= 0.01 else "no power"
        print(f"  {w:16s} {k:2d} {len(pat):4d} {testable:5d} {chance:9.2e}  "
              f"{len(hits):4d}  {verdict}")

    print("\n  --- words with k<3 (too weak to discriminate, listed for completeness) ---")
    weak = [r for r in rows if r[3] < 3]
    print(f"    {len(weak)} words, {sum(len(r[6]) for r in weak)} hits total "
          f"(chance expectation {sum(r[5] for r in weak):.1f})")

    print(f"\n  [R2] INTERESTING hits (k>=3 and chance < 0.05): {len(powered)}")
    for w, hits, ch, k in powered:
        for m, s, sat in hits:
            print(f"      {w.upper()} at {m} @{s}  k={k}  satisfied by "
                  f"{len(sat)} reading(s) {sat if len(sat)<=4 else ''}  "
                  f"(chance {ch:.1e})")

    # R3 null
    rng = random.Random(121)
    shuf = {}
    for r in SURV:
        dec = readings[r][:]
        vals = [v for *_, v in dec]; rng.shuffle(vals)
        shuf[r] = [(m, c, t, g, vals[i]) for i, (m, c, t, g, _) in enumerate(dec)]
    sidx = {r: {(m, t): v for (m, c, t, g, v) in shuf[r]} for r in SURV}
    nh = 0; nt = 0
    for w, gl, pat, k, testable, chance, hits in rows:
        if k < 3: continue
        t2, h2 = scan(pat, sidx, covered, SURV)
        nt += t2; nh += len(h2)
    print(f"\n  [R3] shuffled null, k>=3 words: {nh} hits over {nt} placements")

    # coverage of the long runs
    print(f"\n  LONG-RUN COVERAGE -- words that fit entirely inside a long run:")
    fits = 0
    for w, gl, pat, k, testable, chance, hits in rows:
        if k < 3: continue
        for (m, a, b) in LONG_RUNS:
            if len(pat) <= (b - a + 1):
                fits += 1; break
    print(f"    {fits} of {sum(1 for r in rows if r[3]>=3)} k>=3 words are short "
          f"enough for at least one long run")
    print()


if __name__ == "__main__":
    env = selftest()
    if "--selftest" not in sys.argv: run(env)
