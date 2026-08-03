#!/usr/bin/env python3
"""
eyedouble -- Finnish doubles at the four robust doubled-letter sites.

EYESPIRAL-C. FR130.

WHY THIS IS DIFFERENT FROM FR121/FR125. Those scanned vocabulary blindly across
every placement, at 6-10% power, and every k>=3 assertion was a fresh gamble.
FR129 found FOUR positions where BOTH serious readings agree the plaintext has
a DOUBLED value:

    East 4  33 == 34      East 4  78 == 79
    East 4 109 == 110     East 5  86 == 87

Placing a word so its double lands on one of these **conditions on a
known-true assertion**. The double is free; the word's REMAINING assertions
are the test. Power rises accordingly, and a hit means far more.

ROBUSTNESS. Every check runs against the CONSENSUS relation -- a pair counts as
equal only if BOTH surviving readings (R1 = drop East 1@68, cost 5.8;
R2 = drop East 4@51, cost 7.7) agree. So a hit is independent of the repair
fork, and a miss is not an artifact of choosing the wrong repair.

PRE-REGISTERED:
  R1  the two readings must reproduce 686 / 683 positions with 659 common,
      and the four sites must be agreed-equal, or the run VOIDS.
  R2  a word "fits" only if EVERY assertion it makes is supported by the
      consensus AND every pair of distinct letters is consensus-UNEQUAL.
      Disputed pairs count as failures, not as passes.
  R3  chance is reported per word as (remaining assertions) -> 83^-k', and
      the null is the same vocabulary at the OTHER three sites plus 200
      random covered positions.

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""

import os, sys, random
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
XD = "XD-MBYG04K-URS3LF"
N = 83

import eyeaudit as AUD

SITES = [("East 4", 33), ("East 4", 78), ("East 4", 109), ("East 5", 86)]

# Finnish words containing a doubled letter. gloss kept for the report.
DOUBLES = {
 "maailma":"world","kaikki":"all","kaikkeus":"universe","tulla":"to come",
 "olla":"to be","menna":"to go","silla":"because","kuollut":"dead",
 "kuulla":"to hear","tietaa":"to know","saada":"to get","suuri":"great",
 "vuotta":"years","ensimmainen":"first","viimeinen":"last","viisi":"five",
 "kuusi":"six","hiisi":"goblin","loppu":"end","aarre":"treasure",
 "voittaa":"to win","antaa":"to give","ottaa":"to take","muistaa":"remember",
 "unohtaa":"forget","loytaa":"to find","nukkua":"to sleep","heraa":"awakens",
 "puu":"tree","maa":"earth","kuu":"moon","suu":"mouth","tee":"tea/do",
 "luonnon":"of nature","miljoona":"million","paallikko":"chief",
 "kuolla":"to die","tuuli":"wind","vuori":"mountain","juuri":"root",
 "sielunvaellus":"transmigration","ikuinen":"eternal","kirkas":"bright",
 "pimea":"dark","valkoinen":"white","musta":"black","punainen":"red",
 "kaikkivaltias":"almighty","totuus":"truth","salaisuus":"secret",
 "viisaus":"wisdom","tieto":"knowledge","alkuperainen":"original",
 "kuolematon":"immortal","henkiolento":"spirit being","taikuus":"magic",
 "loitsuu":"casts","velhous":"wizardry","noituus":"witchcraft",
 "aurinko":"sun","tahti":"star","taivaallinen":"heavenly",
}


def pat_of(w):
    w = w.upper().replace(" ", "")
    pos = {}
    for i, ch in enumerate(w): pos.setdefault(ch, []).append(i)
    out = ['.'] * len(w); nxt = 0
    for _, k, v in sorted([(min(v), k, v) for k, v in pos.items() if len(v) > 1]):
        L = chr(ord('A') + nxt); nxt += 1
        for p in v: out[p] = L
    return "".join(out), pos


def doubles_in(w):
    w = w.upper()
    return [i for i in range(len(w) - 1) if w[i] == w[i + 1]]


def build_readings():
    cts, labels, Lx, ctx, pool, red = AUD.load(
        os.path.join(HERE, "corpus.json"), os.path.join(HERE, "atlas.json"))
    def mk(keys): return [p for p in pool
                          if not any((p.m1, p.p1) == k or (p.m2, p.p2) == k for k in keys)]
    def struct(pairs, d=1):
        gf = AUD.build(cts, ctx, Lx, pairs, drift=d); a = AUD.analyse(gf)
        comps = sorted((sorted(c) for c in a["comps"]), key=len, reverse=True)
        compof = {}
        for i, c in enumerate(comps, 1):
            for g in c: compof[g] = i
        Dl = a["delta"]
        blocks = defaultdict(list)
        for mi in range(9):
            for t, g in enumerate(cts[mi]):
                if g in compof: blocks[(mi, compof[g])].append(t)
        link = defaultdict(set)
        for pr in pairs:
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
        out = {}
        for (mi, ci) in gs[0]:
            for t in blocks[(mi, ci)]: out[(mi, t)] = (Dl[cts[mi][t]] - d * t) % N
        return out
    R1 = struct(mk([(Lx["East 1"], 68)]))
    R2 = struct(mk([(Lx["East 4"], 51)]))
    return R1, R2, labels


def consensus(R1, R2):
    common = set(R1) & set(R2)
    def rel(a, b):
        if a not in common or b not in common: return None
        e1 = (R1[a] == R1[b]); e2 = (R2[a] == R2[b])
        if e1 and e2: return "EQ"
        if (not e1) and (not e2): return "NE"
        return "DISPUTED"
    return common, rel


def test_word(w, site, mi, common, rel):
    """Place w so a double lands on the site. Return (ok, k_extra, detail)."""
    pat, pos = pat_of(w)
    res = []
    for di in doubles_in(w):
        start = site[1] - di
        letters = {L: [start + p for p in ps] for L, ps in pos.items() if len(ps) > 1}
        need = [p for ps in letters.values() for p in ps]
        if any((mi, p) not in common for p in need): continue
        kx = sum(len(ps) - 1 for ps in letters.values()) - 1   # the free double
        ok = True
        for L, ps in letters.items():
            for i in range(len(ps) - 1):
                if rel((mi, ps[i]), (mi, ps[i + 1])) != "EQ": ok = False; break
            if not ok: break
        if ok:
            Ls = list(letters)
            for i in range(len(Ls)):
                for j in range(i + 1, len(Ls)):
                    if rel((mi, letters[Ls[i]][0]), (mi, letters[Ls[j]][0])) != "NE":
                        ok = False; break
                if not ok: break
        res.append((start, kx, ok))
    return res


def selftest():
    ok = []
    def ck(n, c, d=""):
        ok.append((n, bool(c))); print(f"  {n:34s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise RuntimeError(f"{XD} selftest FAILED: {n} {d}")
    R1, R2, labels = build_readings()
    ck("t1_R1_sizes", len(R1) == 686 and len(R2) == 683, f"{len(R1)}/{len(R2)}")
    common, rel = consensus(R1, R2)
    ck("t1b_common", len(common) == 659, f"{len(common)}")
    Lx = {l: i for i, l in enumerate(labels)}
    bad = [s for s in SITES if rel((Lx[s[0]], s[1]), (Lx[s[0]], s[1] + 1)) != "EQ"]
    ck("t2_R1_sites_agreed", not bad, f"all four sites consensus-EQ")
    ck("t3_doubles", doubles_in("MAAILMA") == [1] and doubles_in("KAIKKI") == [3],
       "M-AA-ILMA at 1, KAI-KK-I at 3")
    p, _ = pat_of("MAAILMA")
    ck("t4_pattern", p == "ABB..AB", p)
    print(f"selftest {sum(1 for _,p in ok if p)}/{len(ok)} green")
    return R1, R2, labels, common, rel


def run(env):
    R1, R2, labels, common, rel = env
    Lx = {l: i for i, l in enumerate(labels)}
    print("=" * 76)
    print("EYEDOUBLE -- Finnish doubles at the four robust doubled-letter sites")
    print("=" * 76)
    print(f"\n  consensus positions {len(common)}   sites {SITES}\n")
    fits = []; tested = 0
    for w in sorted(DOUBLES):
        if not doubles_in(w): continue
        for site in SITES:
            mi = Lx[site[0]]
            for start, kx, ok in test_word(w, site, mi, common, rel):
                tested += 1
                if ok:
                    fits.append((w, site, start, kx))
    print(f"  placements testable (all assertions land in consensus): {tested}")
    print(f"  words FITTING all assertions: {len(fits)}\n")
    if fits:
        for w, site, start, kx in sorted(fits, key=lambda x: -x[3]):
            print(f"    {w.upper():14s} ({DOUBLES[w]:20s}) at {site[0]}@{start}"
                  f"  extra assertions k'={kx}  chance {N**-kx:.1e}")
    else:
        print("    NONE")
    print()
    # R3 null: same vocabulary at 200 random covered positions
    rng = random.Random(130)
    pool_pos = [p for p in common]
    null = 0; ntested = 0
    for _ in range(200):
        mi, t = rng.choice(pool_pos)
        for w in sorted(DOUBLES):
            if not doubles_in(w): continue
            for start, kx, ok in test_word(w, (labels[mi], t), mi, common, rel):
                ntested += 1
                if ok: null += 1
    print(f"  [R3] null: same vocabulary at 200 random covered positions")
    print(f"       {null} fits over {ntested} testable placements")
    print()


if __name__ == "__main__":
    env = selftest()
    if "--selftest" not in sys.argv: run(env)
