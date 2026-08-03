#!/usr/bin/env python3
"""
eywordsC -- vocabulary batch against the UNIQUE repair-C structure.

EYESPIRAL-C. FR125.

WHAT CHANGED SINCE FR121. That batch tested against 17 candidate readings over
461 positions, so a "hit" only narrowed the candidate set and chance was 17x
inflated. Repair C (FR122-124, audited 7/7) gives:

  * ONE structure, not 17  -- so a hit is DECISIVE, not discriminating
  * 686 positions, not 461 -- 66.2% of the corpus
  * all NINE messages      -- T1 (East 1, West 1, East 2) was entirely dark

Chance per placement therefore drops by 17x, and the testable surface grows.

MATCHING is EXACT ISOMORPHISM: same letter -> same plaintext value, and
DIFFERENT letters -> DIFFERENT values. Finnish a/o/y are distinct symbols.

POWER vs FALSE POSITIVES -- the FR121 correction, kept:
  POWER      = testable placements / possible placements
               (a word at a testable position IS satisfied by the true reading)
  FALSE POS  = testable placements x 83^-k
Both are reported for every word so a zero can be read correctly.

PRE-REGISTERED:
  R1  the repair-C structure must reproduce 686 positions and one forced
      equality q[36]=q[68], or the run VOIDS.
  R2  a hit is INTERESTING only if k >= 3 and the false-positive expectation
      is < 0.05.
  R3  the same vocabulary runs against a SHUFFLED structure as a null.

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""

import os, sys, random
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
XD = "XD-MBYG04K-URS3LF"
N = 83

import eyeaudit as AUD

VOCAB = {
 # --- Noita nouns -------------------------------------------------------
 "noita":"witch","silma":"eye","kuolema":"death","tuli":"fire","vesi":"water",
 "maa":"earth","ilma":"air","velho":"wizard","taika":"magic","loitsu":"spell",
 "sauva":"wand","juoma":"potion","kammio":"chamber","luola":"cave",
 "vuori":"mountain","metsa":"forest","kivi":"stone","veri":"blood",
 # --- cosmology ---------------------------------------------------------
 "maailma":"world","kaikkeus":"universe","luonto":"nature","taivas":"sky",
 "helvetti":"hell","tuonela":"underworld","alkemia":"alchemy","kulta":"gold",
 "hopea":"silver","elohopea":"mercury","rikki":"sulphur","suola":"salt",
 "smaragdi":"emerald","tabletti":"tablet","aurinko":"sun","kuu":"moon",
 # --- knowledge ---------------------------------------------------------
 "tieto":"knowledge","totuus":"truth","viisaus":"wisdom","salaisuus":"secret",
 "salattu":"hidden","tositieto":"true knowledge","todellinen":"true",
 "oppi":"doctrine","sana":"word","kirja":"book","teksti":"text",
 "merkki":"sign","nimi":"name","kysymys":"question","vastaus":"answer",
 # --- being -------------------------------------------------------------
 "jumala":"god","henki":"spirit","sielu":"soul","elama":"life","kuolla":"die",
 "ihminen":"human","olento":"being","haamu":"ghost","hiisi":"goblin",
 "perkele":"devil","kuollut":"dead","elava":"alive",
 # --- qualities ---------------------------------------------------------
 "pyha":"holy","kirous":"curse","siunaus":"blessing","valo":"light",
 "pimeys":"darkness","varjo":"shadow","suuri":"great","pieni":"small",
 "ikuinen":"eternal","alku":"beginning","loppu":"end","ensimmainen":"first",
 "viimeinen":"last","ylhaalla":"above","alhaalla":"below","sisalla":"within",
 "kaikki":"all","paljon":"many","vahan":"few",
 # --- Finnish function words / doubles ---------------------------------
 "olla":"to be","tulla":"to come","menna":"to go","silla":"because",
 "joka":"which","kuin":"as","mutta":"but","koska":"because","sitten":"then",
 "kunnes":"until","aina":"always","tassa":"here","tuolla":"there",
 # --- numbers -----------------------------------------------------------
 "yksi":"one","kaksi":"two","kolme":"three","nelja":"four","viisi":"five",
 "kuusi":"six","seitseman":"seven","kahdeksan":"eight","yhdeksan":"nine",
 # --- Kalevala ----------------------------------------------------------
 "kalevala":"","vainamoinen":"","ilmarinen":"","louhi":"","sampo":"",
 "pohjola":"","lemminkainen":"","kullervo":"","marjatta":"","aino":"",
 # --- English -----------------------------------------------------------
 "knowledge":"","wisdom":"","secret":"","truth":"","eternal":"","emerald":"",
 "tablet":"","alchemy":"","creation":"","beginning":"","ending":"",
 "above":"","below":"","within":"","without":"","spirit":"","shadow":"",
 "mercury":"","sulphur":"","dissolve":"","separate":"","essence":"",
 "seeker":"","hidden":"","forbidden":"","remember":"","between":"",
 "thoth":"","hermes":"","tabula":"","smaragdina":"","secretorum":"",
}


def pat_of(w):
    w = w.upper().replace(" ", "")
    pos = {}
    for i, ch in enumerate(w): pos.setdefault(ch, []).append(i)
    out = ['.'] * len(w); nxt = 0
    for _, k, v in sorted([(min(v), k, v) for k, v in pos.items() if len(v) > 1]):
        L = chr(ord('A') + nxt); nxt += 1
        for p in v: out[p] = L
    return "".join(out), sum(len(v) - 1 for v in pos.values() if len(v) > 1)


def repairC_structure(drift=1):
    cts, labels, Lx, ctx, pool, red = AUD.load(
        os.path.join(HERE, "corpus.json"), os.path.join(HERE, "atlas.json"))
    E1 = (Lx["East 1"], 68)
    poolC = [p for p in pool if not ((p.m1, p.p1) == E1 or (p.m2, p.p2) == E1)]
    gf = AUD.build(cts, ctx, Lx, poolC, drift=drift)
    if gf is None: raise RuntimeError(f"{XD} repair C contradictory at drift {drift}")
    a = AUD.analyse(gf)
    comps = sorted((sorted(c) for c in a["comps"]), key=len, reverse=True)
    compof = {}
    for i, c in enumerate(comps, 1):
        for g in c: compof[g] = i
    D = a["delta"]
    blocks = defaultdict(list)
    for mi in range(9):
        for t, g in enumerate(cts[mi]):
            if g in compof: blocks[(mi, compof[g])].append(t)
    link = defaultdict(set)
    for pr in poolC:
        for i in range(pr.length):
            g1 = cts[pr.m1][pr.p1 + i]; g2 = cts[pr.m2][pr.p2 + i]
            if g1 in compof and g2 in compof:
                k1 = (pr.m1, compof[g1]); k2 = (pr.m2, compof[g2])
                if k1 != k2: link[k1].add(k2); link[k2].add(k1)
    seen = set(); gs = []
    for k in blocks:
        if k in seen: continue
        st = [k]; grp = set()
        while st:
            x = st.pop()
            if x in seen: continue
            seen.add(x); grp.add(x); st.extend(link[x] - seen)
        gs.append(grp)
    gs.sort(key=lambda g: -sum(len(blocks[k]) for k in g))
    big = gs[0]
    val = {}
    for (mi, ci) in big:
        for t in blocks[(mi, ci)]:
            val[(mi, t)] = (D[cts[mi][t]] - drift * t) % N
    return val, labels, len(a["eq"]), sorted(map(tuple, map(sorted, a["eq"])))


def scan(pat, val, labels):
    groups = defaultdict(list)
    for i, ch in enumerate(pat):
        if ch != '.': groups[ch].append(i)
    cov = defaultdict(set)
    for (m, t) in val: cov[m].add(t)
    testable = 0; possible = 0; hits = []
    for m in cov:
        L = max(cov[m]) + 1
        for s in range(0, L - len(pat) + 1):
            possible += 1
            need = [s + i for ps in groups.values() for i in ps]
            if any((m, p) not in val for p in need): continue
            testable += 1
            vals = {}; ok = True
            for Lt, ps in groups.items():
                vs = {val[(m, s + p)] for p in ps}
                if len(vs) != 1: ok = False; break
                vals[Lt] = vs.pop()
            if ok and len(set(vals.values())) == len(vals):
                hits.append((labels[m], s))
    return testable, possible, hits


def selftest():
    ok = []
    def ck(n, c, d=""):
        ok.append((n, bool(c))); print(f"  {n:32s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise RuntimeError(f"{XD} selftest FAILED: {n} {d}")
    val, labels, neq, eqs = repairC_structure(1)
    ck("t1_R1_positions", len(val) == 686, f"{len(val)} positions")
    ck("t1b_R1_equality", neq == 1 and eqs == [(36, 68)], f"{eqs}")
    ck("t2_all_nine", len({m for m, t in val}) == 9, "all nine messages present")
    p, k = pat_of("MAAILMA")
    ck("t3_pattern", (p, k) == ("ABB..AB", 3), f"{p} k={k}")
    t, po, h = scan("A..A.", val, labels)
    ck("t4_scan", t > 200, f"{t} testable of {po}")
    print(f"selftest {sum(1 for _,p in ok if p)}/{len(ok)} green")
    return val, labels


def run(val, labels):
    print("=" * 78)
    print("EYWORDSC -- vocabulary against the UNIQUE repair-C structure")
    print("=" * 78)
    print(f"\n  positions {len(val)} (66.2%)  messages {len({m for m,t in val})}"
          f"  candidate structures 1\n")
    rows = []
    for w in VOCAB:
        pat, k = pat_of(w)
        if k < 1: continue
        t, po, h = scan(pat, val, labels)
        rows.append((w, pat, k, t, po, t / max(po, 1), t * (N ** -k), h))
    strong = [r for r in rows if r[2] >= 3]
    strong.sort(key=lambda r: -r[5])
    print(f"  k>=3 WORDS ({len(strong)}):\n")
    print(f"  {'word':16s} {'k':>2s} {'span':>4s} {'testable':>8s} {'POWER':>7s} {'falsepos':>9s} {'hits':>5s}")
    print("  " + "-" * 66)
    for w, pat, k, t, po, pw, fp, h in strong:
        flag = "  <-- HIT" if h else ""
        print(f"  {w:16s} {k:2d} {len(pat):4d} {t:8d} {100*pw:6.1f}% {fp:9.2e} {len(h):5d}{flag}")
        if h and k >= 3 and fp < 0.05:
            for lab, s in h[:6]: print(f"        {lab} @{s}")
    mp = sum(r[5] for r in strong) / len(strong)
    print(f"\n  mean POWER over k>=3 words: {100*mp:.1f}%")
    tot_hits = sum(len(r[7]) for r in strong)
    tot_fp = sum(r[6] for r in strong)
    print(f"  total k>=3 hits {tot_hits}  vs false-positive expectation {tot_fp:.3f}")

    weak = [r for r in rows if r[2] < 3]
    wh = sum(len(r[7]) for r in weak); wfp = sum(r[6] for r in weak)
    print(f"  k<3 words: {wh} hits vs {wfp:.1f} expected (cannot discriminate)")

    rng = random.Random(125)
    keys = list(val); vals = [val[k] for k in keys]; rng.shuffle(vals)
    sval = {k: vals[i] for i, k in enumerate(keys)}
    sh = 0
    for w, pat, k, t, po, pw, fp, h in strong:
        _, _, h2 = scan(pat, sval, labels); sh += len(h2)
    print(f"\n  [R3] shuffled null, k>=3 words: {sh} hits")
    print()


if __name__ == "__main__":
    val, labels = selftest()
    if "--selftest" not in sys.argv: run(val, labels)
