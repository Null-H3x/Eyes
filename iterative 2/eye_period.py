#!/usr/bin/env python3
# ============================================================================
# eye_period.py  -  a KEY FREE bound on the keystream period
#                   pure standard library, no pip install, Windows ready
#
# THE IDEA
#   If the keystream has period P, two positions i and j with i congruent to j
#   mod P use the SAME keystream value.  So if the plaintext repeats a 3 gram
#   at two such positions, the CIPHERTEXT repeats it too, whatever the key is.
#
#   The real difference stream, with the keystream still on, contains exactly
#   2 repeated 3 grams at distinct positions.  Chance expectation is about 0.9.
#   So measure: for a source that repeats content, and a random keystream of
#   period P, what does the RAW ciphertext score?  Wherever that is reliably
#   above 2, that combination of source and period is excluded WITH NO SEARCH.
#
#   This covers every period at once, which no 83 to the P search can do.
#
# WHAT IT DOES NOT DO
#   It cannot exclude a source that barely repeats, because such a source
#   leaves nothing behind at any period.  That is exactly the region where a
#   keystream search still has to do the work, and the frontier command prints
#   the band where each tool is the only one that reaches.
#
# COMMANDS   (copy paste these)
#
#   python eye_period.py selftest
#   python eye_period.py sweep      [--reps 60]
#   python eye_period.py frontier   [--reps 50]
#
# ALWAYS run selftest first.
#
# A NOTE ON THE GENERATOR, WHICH IS WHERE THE FIRST VERSION WENT WRONG
#   The first cut used a source with words of a FIXED length of 5.  That puts
#   every word boundary at a position congruent to 0 mod 5, so every period
#   that is a multiple of 5 lines up with the word structure and the score
#   jumps.  Period 10 scored 190 against period 6 at 102, which is impossible
#   under the mechanism being measured, and that impossibility is what exposed
#   the artefact.  Word lengths here are drawn from 2 to 9.
# ============================================================================

import sys, math, os

NMSG = 9
NSYM = 83

MSG, MLEN, DIF, DLEN = [], [], [], []


def build():
    global MSG, MLEN, DIF, DLEN
    MSG, MLEN, DIF, DLEN = [], [], [], []
    for name in ORDER:
        body = RAW[name][1:]              # element 0 is the header, outside the cipher
        MSG.append(body)
        MLEN.append(len(body))
        d = [(body[i + 1] - body[i]) % NSYM for i in range(len(body) - 1)]
        DIF.append(d)
        DLEN.append(len(d))


M64 = (1 << 64) - 1


def _rotl(x, k):
    return ((x << k) | (x >> (64 - k))) & M64


class Rng(object):
    __slots__ = ('s',)

    def __init__(self, seed):
        s = seed & M64
        st = []
        for _ in range(4):
            s = (s + 0x9E3779B97F4A7C15) & M64
            z = s
            z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
            z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
            st.append(z ^ (z >> 31))
        self.s = st
        for _ in range(16):
            self.next()

    def next(self):
        s = self.s
        res = (_rotl((s[0] + s[3]) & M64, 23) + s[0]) & M64
        t = (s[1] << 17) & M64
        s[2] ^= s[0]; s[3] ^= s[1]; s[1] ^= s[2]; s[0] ^= s[3]
        s[2] ^= t; s[3] = _rotl(s[3], 45)
        return res

    def rint(self, n):
        return self.next() % n


def score_ngram(stream, length):
    """3 grams occurring at two or more DISTINCT positions.  Same position in
    different messages is the shared prefix and must not be counted."""
    first = {}
    counted = set()
    total = 0
    for m in range(NMSG):
        row = stream[m]
        for i in range(length[m] - 2):
            k = (row[i] * NSYM + row[i + 1]) * NSYM + row[i + 2]
            fp = first.get(k, -1)
            if fp < 0:
                first[k] = i
            elif fp != i and k not in counted:
                counted.add(k)
                total += 1
    return total


def src_gen(r, nvoc, homophonic):
    """A source that repeats content.  Word lengths 2 to 9 so that boundaries
    do not align with any particular period."""
    codes = list(range(NSYM))
    for i in range(NSYM - 1, 0, -1):
        j = r.rint(i + 1)
        codes[i], codes[j] = codes[j], codes[i]
    alpha = 30 if homophonic else 27
    voc = [[r.rint(alpha) for _ in range(2 + r.rint(8))] for _ in range(nvoc)]
    out = []
    for m in range(NMSG):
        ctr = [0] * 40
        row = []
        n = DLEN[m]
        while len(row) < n:
            for L in voc[r.rint(nvoc)]:
                if len(row) >= n:
                    break
                if homophonic:
                    h = 2 + (L % 2)
                    row.append(codes[(L * 3 + (ctr[L] % h)) % NSYM])
                    ctr[L] += 1
                else:
                    row.append(codes[L])
        out.append(row)
    return out


def apply_period(s, P, r):
    k = [r.rint(NSYM) for _ in range(P)]
    return [[(s[m][i] - k[i % P]) % NSYM for i in range(len(s[m]))]
            for m in range(NMSG)]


def stats(s):
    """distinct repeated 3 gram keys, and mean occurrences among them"""
    d = {}
    for m in range(NMSG):
        row = s[m]
        for i in range(DLEN[m] - 2):
            d.setdefault((row[i], row[i + 1], row[i + 2]), set()).add(i)
    rep = [len(v) for v in d.values() if len(v) > 1]
    return len(rep), (sum(rep) / float(len(rep)) if rep else 0.0)


def pctile5(nvoc, ho, P, reps, seed=4242):
    r = Rng(seed + nvoc * 131 + P * 7717 + ho)
    v = []
    for _ in range(reps):
        s = src_gen(r, nvoc, ho)
        v.append(score_ngram(apply_period(s, P, r), DLEN))
    v.sort()
    return v[len(v) // 20], sum(v) / float(len(v))


REAL = None
PS = [2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 25, 30, 40, 50, 60, 80, 100]
MODELS = [(20, 0), (60, 0), (150, 0), (400, 0),
          (30, 1), (60, 1), (150, 1), (400, 1), (1000, 1)]


def selftest():
    ok = True
    print("corpus       : body lengths " + " ".join(str(x) for x in MLEN))
    print("             : expected     98 102 117 101 136 123 118 119 113")
    ok = ok and MLEN == [98, 102, 117, 101, 136, 123, 118, 119, 113]
    bad = sum(1 for m in range(NMSG) for x in DIF[m] if x == 0)
    print("no doubles   : %d zero steps, expected 0" % bad)
    ok = ok and bad == 0
    print("observed     : raw difference stream scores %d, expected 2" % REAL)
    ok = ok and REAL == 2

    # chance level: shuffle each message, destroying content but keeping symbols
    r = Rng(11)
    v = []
    for _ in range(400):
        sh = []
        for m in range(NMSG):
            row = list(DIF[m])
            for i in range(len(row) - 1, 0, -1):
                j = r.rint(i + 1)
                row[i], row[j] = row[j], row[i]
            sh.append(row)
        v.append(score_ngram(sh, DLEN))
    mu = sum(v) / float(len(v))
    print("chance level : shuffled corpus scores %.2f on average, observed %d"
          % (mu, REAL))
    print("             : so the observed 2 is AT chance, not below it")

    # the generator must not favour any period.  A structureless source must
    # score near zero at every period, and a repeating source must fall
    # MONOTONICALLY with P.  Non monotonicity is the fixed-word-length bug.
    r2 = Rng(77)
    flat = [[r2.rint(NSYM) for _ in range(DLEN[m])] for m in range(NMSG)]
    print("flat source  : scores %d, expected 0 to 2" % score_ngram(flat, DLEN))

    seq = []
    for P in [2, 4, 6, 8, 12, 16, 24, 32]:
        _, mn = pctile5(60, 0, P, 25)
        seq.append((P, mn))
    print("monotone     : mean score by period, must fall throughout")
    print("             : " + "  ".join("P%d=%.0f" % (p, m) for p, m in seq))
    mono = all(seq[i][1] >= seq[i + 1][1] * 0.92 for i in range(len(seq) - 1))
    print("             : %s" % ("monotone, OK" if mono
                                 else "*** NOT MONOTONE - generator artefact ***"))
    ok = ok and mono
    print("SELF TEST %s" % ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


def sweep(reps):
    print("real ciphertext, keystream still on, repeated 3 gram score = %d\n" % REAL)
    print("  P     plain 60 words              homophonic 60 words        excluded?")
    for P in PS:
        a5, am = pctile5(60, 0, P, reps)
        b5, bm = pctile5(60, 1, P, reps)
        tag = "EXCLUDED" if b5 > REAL else ("plain only" if a5 > REAL else "-")
        print("  %-5d %6.1f  p5 %-4d           %6.1f  p5 %-4d          %s"
              % (P, am, a5, bm, b5, tag))
    return 0


def frontier(reps):
    print("observed: the raw ciphertext, keystream still on, scores %d\n" % REAL)
    print("  R alone does not decide this.  A 20 word vocabulary has a LOW")
    print("  distinct key count but a HIGH multiplicity per key, and it is")
    print("  multiplicity that decides whether two occurrences of a 3 gram")
    print("  land on the same residue mod P.  Both are printed.\n")
    print("  source model              R    mean occ   largest P excluded")
    for nv, ho in MODELS:
        r = Rng(1)
        acc = [stats(src_gen(r, nv, ho)) for _ in range(8)]
        R = sum(a[0] for a in acc) / 8.0
        occ = sum(a[1] for a in acc) / 8.0
        big = 0
        for P in PS:
            if pctile5(nv, ho, P, reps)[0] > REAL:
                big = P
        print("  %-4d words %-11s %6.0f   %5.2f      %s"
              % (nv, "homophonic" if ho else "plain", R, occ,
                 ("P <= %d" % big) if big else "none, could hide at any period"))
    print()
    print("  READ IT THIS WAY.  A keystream SEARCH detects the true key only if")
    print("  the source's own R beats the search threshold, about 15 for a")
    print("  period 6 space.  This table excludes the strongly repeating")
    print("  sources at short period for free.  What is left for a search is")
    print("  the band between those two limits, and that band is what a period")
    print("  6 or 7 run actually buys.")
    return 0


USAGE = """eye_period.py  -  key free bound on the keystream period

  python eye_period.py selftest
  python eye_period.py sweep    [--reps 60]
  python eye_period.py frontier [--reps 50]
"""


def main(argv):
    global REAL
    build()
    REAL = score_ngram(DIF, DLEN)
    reps = None
    pos = []
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == '--reps':
            reps = int(argv[i + 1]); i += 1
        elif a.startswith('--'):
            print("unknown option %s" % a); return 2
        else:
            pos.append(a)
        i += 1
    if not pos:
        print(USAGE); return 2
    if pos[0] == 'selftest':
        return selftest()
    if pos[0] == 'sweep':
        return sweep(reps or 60)
    if pos[0] == 'frontier':
        return frontier(reps or 50)
    print(USAGE)
    return 2


# ---------------------------------------------------------------- data ----
# The corpus, embedded.  This file opens no other file.

RAW = {
  'East 1': [50, 66, 5, 48, 62, 13, 75, 29, 24, 61, 42, 70, 66, 62, 32, 14, 81, 8, 15, 78, 2, 29, 13, 49, 1, 80, 82, 40, 63, 81, 21, 19, 0, 40, 51, 65, 26, 14, 21, 70, 47, 44, 48, 42, 19, 48, 13, 47, 19, 49, 72, 31, 5, 24, 3, 43, 59, 67, 33, 49, 41, 60, 21, 26, 30, 5, 25, 20, 71, 11, 74, 56, 4, 74, 19, 71, 4, 51, 41, 43, 80, 72, 54, 63, 79, 81, 15, 16, 44, 31, 30, 12, 33, 57, 28, 13, 64, 43, 48],
  'West 1': [80, 66, 5, 48, 62, 13, 75, 29, 24, 61, 42, 70, 66, 62, 32, 14, 81, 8, 15, 78, 2, 29, 13, 49, 1, 29, 11, 30, 52, 81, 21, 19, 0, 25, 26, 54, 20, 14, 21, 70, 47, 44, 48, 42, 19, 48, 13, 47, 19, 49, 44, 26, 59, 77, 64, 43, 79, 28, 72, 64, 1, 30, 73, 23, 67, 6, 33, 25, 64, 81, 68, 46, 17, 36, 13, 17, 21, 68, 13, 9, 46, 67, 57, 34, 62, 82, 15, 10, 73, 62, 2, 11, 65, 72, 37, 44, 10, 43, 68, 62, 9, 34, 18],
  'East 2': [36, 66, 5, 48, 62, 13, 75, 29, 24, 61, 42, 70, 66, 62, 32, 14, 81, 8, 15, 78, 2, 29, 13, 49, 1, 69, 76, 52, 9, 48, 66, 80, 22, 64, 57, 40, 49, 78, 3, 16, 56, 19, 47, 40, 80, 6, 13, 64, 29, 49, 64, 63, 6, 49, 31, 13, 16, 10, 45, 24, 26, 77, 10, 60, 81, 61, 34, 54, 70, 21, 15, 4, 66, 77, 42, 37, 30, 22, 0, 11, 41, 72, 57, 20, 23, 57, 65, 41, 23, 18, 72, 42, 5, 3, 26, 78, 8, 5, 54, 45, 77, 25, 64, 61, 16, 44, 54, 51, 20, 63, 25, 11, 26, 45, 53, 60, 38, 34],
  'West 2': [76, 66, 5, 49, 75, 54, 69, 46, 32, 1, 42, 60, 26, 48, 50, 80, 32, 24, 55, 61, 47, 12, 21, 12, 49, 54, 34, 25, 36, 15, 56, 55, 20, 9, 8, 62, 13, 82, 9, 44, 29, 60, 53, 82, 42, 80, 5, 43, 71, 3, 80, 77, 47, 78, 34, 25, 62, 18, 10, 49, 62, 64, 52, 81, 11, 66, 62, 13, 47, 17, 52, 70, 26, 23, 32, 31, 64, 23, 35, 32, 50, 6, 1, 25, 8, 37, 47, 43, 26, 76, 65, 68, 80, 17, 7, 45, 63, 14, 53, 63, 60, 16],
  'East 3': [63, 66, 5, 49, 75, 54, 2, 60, 29, 40, 78, 47, 60, 75, 67, 71, 60, 2, 65, 7, 47, 14, 45, 74, 59, 41, 80, 13, 60, 13, 81, 22, 35, 50, 40, 39, 2, 59, 48, 31, 76, 2, 80, 75, 1, 56, 67, 11, 21, 8, 40, 65, 45, 75, 55, 39, 60, 42, 13, 3, 22, 57, 2, 6, 58, 9, 70, 1, 58, 56, 63, 68, 25, 79, 7, 20, 19, 64, 2, 66, 73, 30, 71, 16, 12, 30, 65, 37, 20, 13, 22, 63, 18, 46, 64, 59, 41, 81, 82, 22, 78, 36, 47, 17, 4, 6, 17, 5, 36, 79, 63, 1, 64, 69, 15, 43, 4, 58, 56, 31, 14, 64, 58, 18, 44, 78, 69, 1, 0, 46, 20, 71, 73, 25, 35, 8, 24],
  'West 3': [34, 66, 5, 49, 75, 54, 23, 74, 11, 13, 28, 26, 19, 48, 67, 57, 37, 60, 34, 28, 74, 10, 17, 32, 11, 18, 19, 43, 19, 81, 42, 4, 62, 9, 46, 49, 32, 51, 76, 58, 4, 43, 47, 17, 67, 79, 21, 32, 44, 16, 30, 37, 26, 28, 41, 68, 57, 34, 51, 10, 69, 70, 8, 6, 46, 43, 18, 39, 47, 43, 15, 13, 33, 30, 35, 62, 37, 0, 37, 5, 38, 55, 37, 13, 40, 25, 9, 21, 11, 64, 5, 79, 42, 68, 11, 71, 11, 48, 3, 67, 61, 40, 22, 14, 35, 50, 61, 39, 11, 2, 66, 49, 51, 53, 17, 73, 36, 75, 74, 54, 24, 30, 54, 70],
  'East 4': [27, 66, 5, 49, 75, 54, 2, 60, 29, 40, 2, 55, 9, 15, 59, 18, 68, 3, 36, 5, 47, 77, 44, 38, 1, 18, 28, 76, 4, 34, 60, 63, 58, 80, 17, 54, 79, 75, 48, 54, 55, 19, 62, 64, 14, 47, 51, 70, 75, 5, 11, 47, 45, 58, 68, 69, 79, 25, 38, 45, 73, 47, 68, 50, 34, 45, 78, 26, 79, 57, 4, 56, 22, 60, 18, 75, 43, 60, 59, 67, 63, 42, 49, 33, 40, 65, 79, 77, 7, 3, 26, 62, 31, 78, 26, 57, 69, 40, 4, 23, 26, 13, 67, 42, 38, 72, 11, 39, 65, 60, 25, 6, 80, 66, 68, 77, 59, 78, 19],
  'West 4': [77, 66, 5, 49, 75, 54, 2, 60, 29, 40, 2, 55, 9, 15, 59, 18, 68, 3, 36, 5, 47, 60, 21, 80, 1, 72, 55, 16, 82, 35, 57, 19, 1, 66, 18, 27, 39, 17, 74, 81, 39, 14, 78, 0, 25, 65, 43, 66, 64, 38, 81, 23, 24, 50, 57, 30, 71, 75, 26, 68, 54, 57, 56, 50, 71, 73, 14, 21, 8, 32, 26, 63, 5, 37, 19, 43, 66, 47, 53, 34, 66, 23, 73, 31, 54, 38, 77, 67, 11, 63, 79, 6, 22, 21, 51, 69, 74, 21, 5, 17, 67, 37, 29, 21, 60, 14, 82, 44, 30, 4, 20, 42, 35, 1, 31, 54, 46, 20, 40, 30],
  'East 5': [33, 66, 5, 49, 75, 54, 2, 60, 29, 40, 2, 55, 9, 15, 59, 18, 68, 3, 36, 5, 47, 33, 21, 59, 44, 18, 28, 76, 59, 34, 60, 63, 79, 27, 12, 54, 5, 49, 48, 54, 55, 52, 62, 72, 69, 10, 57, 22, 58, 48, 67, 53, 7, 34, 32, 30, 31, 19, 26, 8, 34, 46, 7, 30, 71, 55, 34, 75, 54, 9, 6, 60, 5, 23, 25, 45, 42, 80, 25, 12, 22, 76, 20, 51, 62, 21, 40, 9, 41, 10, 44, 73, 8, 33, 70, 73, 6, 31, 21, 72, 5, 40, 61, 51, 42, 66, 64, 74, 61, 25, 63, 42, 24, 41],
}

ORDER = ['East 1', 'West 1', 'East 2', 'West 2', 'East 3',
         'West 3', 'East 4', 'West 4', 'East 5']

if __name__ == '__main__':
    sys.exit(main(sys.argv))
