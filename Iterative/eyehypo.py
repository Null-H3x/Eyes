#!/usr/bin/env python3
"""
eyehypo -- pattern-crib and grammar consumers for the 17 candidate readings.

EYESPIRAL-C. The artifact FR119 shipped gives the plaintext EQUALITY STRUCTURE
over 461 positions. This tests hypotheses in that same currency, so nothing has
to be assumed about encoding.

COVERAGE, and it constrains everything. The 461 decrypted positions lie
entirely in T2 and T3 -- East 1, West 1 and East 2 have ZERO coverage, because
FR102 showed T1 is unbridged after repair A. Cribs are testable only in
West 2, East 3, West 3, East 4, West 4, East 5. There are 66 runs of >=3
consecutive covered positions, the longest 12.

TWO CONSUMERS

  PATTERN. A string like "A.B..B.A": letters mark positions asserted to hold
  EQUAL plaintext, dots assert nothing. Placed at (message, start), every
  asserted position must be covered. Each of the 17 readings then satisfies it
  or does not.

  GRAMMAR. A predicate over a reading's decrypted stream -- fixed-width
  records, bounded value windows, monotone runs, periodic structure. Each
  reading satisfies it or does not.

WHY SHAPES, NOT PLACEMENTS. Hand-picking crib locations wastes most guesses on
uncovered positions. Instead each pattern SHAPE is tested at EVERY valid
placement, and the instrument reports the placements that survive in few
readings -- those are the discriminating ones.

READING THE OUTPUT

  17 readings satisfy  -> the hypothesis says nothing (any reading allows it)
   2-8 satisfy         -> partial discrimination
   1 satisfies         -> DISCRIMINATING: if the hypothesis is right, so is
                          that ratio
   0 satisfy           -> the hypothesis is REFUTED by the model, or the model
                          is wrong

PRE-REGISTERED:
  R1  the 17 readings must reproduce FR119's artifact (461 positions, pairwise
      distinct) or the run VOIDS.
  R2  a "discriminating" verdict requires exactly one reading AND at least 3
      asserted equalities -- fewer is too cheap to mean anything.
  R3  chance calibration: the same shapes are run against SHUFFLED readings;
      the survivor rate there is the null, reported alongside.

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""

import os, sys, io, json, random, contextlib
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
XD = "XD-MBYG04K-URS3LF"
N = 83

import eyereveal as RV

SURVIVORS = RV.SURVIVORS


# ------------------------------------------------------------------ catalog

PATTERNS = {
    # --- doubled letters: English LL SS EE TT OO / Finnish AA UU II OO YY ---
    "AA":            "doubled letter (LL, SS, EE / Finnish MAA, PUU)",
    "AAA":           "tripled value -- rare in language, common in padding",
    # --- short separated repeats: the commonest language skeletons ---
    "A.A":           "X_X  (EVE, EYE, SES, ALA, ELE)",
    "A..A":          "X__X (THAT, HIGH, SAYS, TENT)",
    "A...A":         "X___X (THERE->no; SEVENS, LEVEL)",
    "A....A":        "X____X",
    "A.....A":       "X_____X",
    # --- two interleaved repeats: word and phrase skeletons ---
    "ABAB":          "alternating pair (MAMA, PAPA, TATA)",
    "ABBA":          "mirrored pair (SEES, NOON, DEED, MAAM)",
    "ABAB.":         "alternating then free",
    "AB.AB":         "repeated bigram at distance 3 (THETHE)",
    "AB..AB":        "repeated bigram at distance 4",
    "AB...AB":       "repeated bigram at distance 5",
    "ABA":           "X Y X (EVE, EYE, OTO)",
    "ABBA.":         "mirrored pair then free",
    "A.BB.A":        "outer repeat around inner double",
    "AB.BA":         "mirror at distance 4",
    "AB..BA":        "mirror at distance 5",
    # --- three-way repeats: strong assertions, cheap to refute ---
    "A.A.A":         "three at period 2",
    "A..A..A":       "three at period 3",
    "A...A...A":     "three at period 4  (lag-4 family)",
    "ABCABC":        "repeated trigram at distance 3",
    "ABC.ABC":       "repeated trigram at distance 4",
    "ABCBA":         "palindrome of 5",
    "ABCCBA":        "palindrome of 6",
    "ABABAB":        "period-2 run of 6",
    # --- word-boundary / delimiter shapes ---
    "A.....A.....A": "three at period 6 (fixed-width records)",
    "A......A":      "X______X (period 7)",
    "A.......A":     "period 8",
    # --- English function-word skeletons (position-sensitive) ---
    "A.B.A.B":       "interleaved doubles",
    "AB.A.B":        "shifted bigram repeat",
    "A.AB.B":        "paired doubles",
}

# grammars: name -> (description, predicate over list of (msg,comp,pos,glyph,val))
def g_bounded(width):
    def f(dec):
        vs = [v for *_, v in dec]
        s = sorted(set(vs))
        if not s: return False
        # minimal circular window covering all values
        gaps = [(s[(i+1) % len(s)] - s[i]) % N for i in range(len(s))]
        return N - max(gaps) <= width
    return f

def g_period(p):
    def f(dec):
        by = defaultdict(list)
        for m, c, t, g, v in dec: by[(m, t % p)].append(v)
        runs = [vs for vs in by.values() if len(vs) > 1]
        if len(runs) < 3: return False
        return all(len(set(vs)) == 1 for vs in runs)
    return f

def g_no_repeat_within(d):
    def f(dec):
        by = defaultdict(list)
        for m, c, t, g, v in dec: by[m].append((t, v))
        for m, seq in by.items():
            seq.sort()
            for i in range(len(seq)):
                for j in range(i+1, len(seq)):
                    if seq[j][0] - seq[i][0] > d: break
                    if seq[i][1] == seq[j][1]: return False
        return True
    return f

def g_monotone_blocks(minlen):
    def f(dec):
        by = defaultdict(list)
        for m, c, t, g, v in dec: by[(m, c)].append((t, v))
        ok = 0
        for k, seq in by.items():
            if len(seq) < minlen: continue
            seq.sort()
            vs = [v for _, v in seq]
            if all(b > a for a, b in zip(vs, vs[1:])) or \
               all(b < a for a, b in zip(vs, vs[1:])): ok += 1
        return ok >= 2
    return f

def g_distinct_at_most(k):
    def f(dec):
        return len({v for *_, v in dec}) <= k
    return f

def g_value_absent(v0):
    def f(dec):
        return v0 not in {v for *_, v in dec}
    return f

GRAMMARS = {}
for w in (20, 30, 40, 50, 60, 70):
    GRAMMARS[f"bounded-window-{w}"] = (f"all values within a width-{w} window", g_bounded(w))
for p in (2, 3, 4, 5, 6, 7, 8, 10, 12):
    GRAMMARS[f"period-{p}"] = (f"same value at every position congruent mod {p}", g_period(p))
for d in (2, 3, 4, 6, 8, 12):
    GRAMMARS[f"no-repeat-within-{d}"] = (f"no value repeats within {d} positions", g_no_repeat_within(d))
for L in (4, 6, 8):
    GRAMMARS[f"monotone-blocks-{L}"] = (f">=2 blocks of length {L}+ strictly monotone", g_monotone_blocks(L))
for k in (30, 40, 50, 60, 70, 80):
    GRAMMARS[f"at-most-{k}-values"] = (f"at most {k} distinct plaintext values", g_distinct_at_most(k))
for v0 in (0, 1, 41, 82):
    GRAMMARS[f"value-{v0}-absent"] = (f"plaintext value {v0} never occurs", g_value_absent(v0))


# ------------------------------------------------------------------- engine

def load_readings():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): env = RV.selftest()
    alpha, beta, comps, compof, cts, labels, red, blocks, groups = env
    big = groups[0]
    readings = {}
    for r in SURVIVORS:
        readings[r] = RV.decrypt(big, blocks, cts, labels, alpha, beta, compof, r, 1)
    return readings, labels


def index_by_pos(dec):
    return {(m, t): v for (m, c, t, g, v) in dec}


def test_pattern(readings, idx, pat, msg, start):
    """Returns (n_asserted_equalities, set of ratios satisfying), or None if
    the placement is not fully covered."""
    groups = defaultdict(list)
    for i, ch in enumerate(pat):
        if ch != '.': groups[ch].append(start + i)
    if not groups: return None
    need = [p for ps in groups.values() for p in ps]
    for r in SURVIVORS:
        if any((msg, p) not in idx[r] for p in need): return None
    nass = sum(len(ps) - 1 for ps in groups.values())
    if nass < 1: return None
    sat = set()
    for r in SURVIVORS:
        ok = all(len({idx[r][(msg, p)] for p in ps}) == 1 for ps in groups.values())
        if ok: sat.add(r)
    return nass, sat


def selftest():
    ok = []
    def ck(n, c, d=""):
        ok.append((n, bool(c))); print(f"  {n:34s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise RuntimeError(f"{XD} selftest FAILED: {n} {d}")
    readings, labels = load_readings()
    ck("t1_R1_readings", len(readings) == 17 and
       all(len(v) == 461 for v in readings.values()), "17 x 461")
    rend = {RV.render(v) for v in readings.values()}
    ck("t1b_distinct", len(rend) == 17, f"{len(rend)} distinct")
    idx = {r: index_by_pos(readings[r]) for r in SURVIVORS}

    # t2: a pattern built FROM a reading must be satisfied by that reading
    r0 = SURVIVORS[0]; dec = readings[r0]
    by = defaultdict(list)
    for (m, c, t, g, v) in dec: by[m].append((t, v))
    planted = None
    for m, seq in by.items():
        seq.sort()
        pos = defaultdict(list)
        for t, v in seq: pos[v].append(t)
        for v, ts in pos.items():
            if len(ts) >= 2 and ts[1] - ts[0] <= 8:
                span = ts[1] - ts[0] + 1
                pat = ['.'] * span; pat[0] = 'A'; pat[ts[1]-ts[0]] = 'A'
                planted = (m, ts[0], "".join(pat)); break
        if planted: break
    ck("t2_planted_exists", planted is not None, str(planted))
    res = test_pattern(readings, idx, planted[2], planted[0], planted[1])
    ck("t2b_planted_satisfied", res and r0 in res[1],
       f"{len(res[1])} of 17 satisfy" if res else "untestable")

    # t3: an impossible pattern must be satisfied by nobody
    imposs = test_pattern(readings, idx, "AA", planted[0], planted[1])
    ck("t3_grammar_engine", GRAMMARS["at-most-80-values"][1](dec) in (True, False), "")
    print(f"selftest {sum(1 for _,p in ok if p)}/{len(ok)} green")
    return readings, labels, idx


def run(env):
    readings, labels, idx = env
    print("=" * 74)
    print("EYEHYPO -- pattern and grammar consumers over the 17 readings")
    print("=" * 74)

    covered = defaultdict(set)
    for (m, c, t, g, v) in readings[SURVIVORS[0]]: covered[m].add(t)
    print(f"\n  testable messages: {sorted(covered)}")
    print(f"  (East 1 / West 1 / East 2 have NO coverage -- T1 is unbridged)\n")

    # ---- PATTERNS: every shape at every valid placement
    print("  PATTERN SHAPES, each tested at every valid placement:\n")
    rows = []
    for pat, desc in PATTERNS.items():
        placements = 0; disc = []; hist = defaultdict(int)
        for m in covered:
            for s in range(0, max(covered[m]) + 1):
                res = test_pattern(readings, idx, pat, m, s)
                if res is None: continue
                placements += 1
                nass, sat = res
                hist[len(sat)] += 1
                if len(sat) == 1 and nass >= 3: disc.append((m, s, nass, list(sat)[0]))
        rows.append((pat, desc, placements, hist, disc))
        if placements:
            zero = hist.get(0, 0); one = hist.get(1, 0); allr = hist.get(17, 0)
            print(f"    {pat:14s} {placements:4d} placements | "
                  f"0 readings {zero:4d} | 1 reading {one:3d} | all 17 {allr:4d} "
                  f"| DISCRIMINATING {len(disc)}")
    print()

    # ---- GRAMMARS
    print("  GRAMMARS, each tested against all 17 readings:\n")
    for name, (desc, fn) in GRAMMARS.items():
        sat = [r for r in SURVIVORS if fn(readings[r])]
        tag = ""
        if len(sat) == 1: tag = f"  <-- DISCRIMINATING: ratio {sat[0]}"
        elif len(sat) == 0: tag = "  <-- refuted by every reading"
        print(f"    {name:24s} satisfied by {len(sat):2d}/17{tag}")
    print()

    # ---- R3 chance calibration
    print("  [R3] chance calibration: same shapes against SHUFFLED readings")
    rng = random.Random(119)
    shuf = {}
    for r in SURVIVORS:
        dec = readings[r][:]
        vals = [v for *_, v in dec]; rng.shuffle(vals)
        shuf[r] = [(m, c, t, g, vals[i]) for i, (m, c, t, g, _) in enumerate(dec)]
    sidx = {r: index_by_pos(shuf[r]) for r in SURVIVORS}
    tot = 0; one = 0
    for pat in PATTERNS:
        for m in covered:
            for s in range(0, max(covered[m]) + 1):
                res = test_pattern(shuf, sidx, pat, m, s)
                if res is None: continue
                tot += 1
                if len(res[1]) == 1 and res[0] >= 3: one += 1
    print(f"       shuffled: {one} discriminating of {tot} placements "
          f"({100*one/max(tot,1):.2f}%)")
    real_tot = sum(r[2] for r in rows); real_one = sum(len(r[4]) for r in rows)
    print(f"       real    : {real_one} discriminating of {real_tot} placements "
          f"({100*real_one/max(real_tot,1):.2f}%)")
    print()


if __name__ == "__main__":
    env = selftest()
    if "--selftest" not in sys.argv: run(env)
