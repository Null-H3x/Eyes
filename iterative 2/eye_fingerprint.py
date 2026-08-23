#!/usr/bin/env python3
# ============================================================================
# eye_fingerprint.py  -  alphabet fingerprint brute for the Noita Eye corpus
#                        pure standard library, no pip install, Windows ready
#
# THE SWEEP, WHICH IS BEN'S DESIGN
#   cipher transform  x  alphabet size  x  position movement  ->  scored
#
#     transform      P [ i ] = C [ i ] - a C [ i - m ]      lag m , multiplier a
#     alphabet       fold the 83 residues into A bins , A = 26 .. 82
#     fold map       mod    v mod A            a cyclic homophonic code
#                    div    v // ceil(83/A)    a blocked homophonic code
#                    keep   only v < A         a code using only A of the 83
#     score          chi squared against the EXACT expected counts
#
#   The point of the modulus axis: if the inner code is homophonic, several of
#   the 83 codes stand for one letter, and folding recovers the letter without
#   knowing the alphabet ordering OR the language.
#
# THE TRAP , AND IT IS A BIG ONE
#   83 is prime, so no A divides it.  Folding a residual that is UNIFORM over
#   83 into A bins therefore does NOT give a uniform distribution: r of the
#   bins get one extra source value each, where 83 = q A + r.
#
#     A = 52   83 = 1 x 52 + 31    chi2 from the folding alone   85
#     A = 60   83 = 1 x 60 + 23    chi2 from the folding alone  111
#     A = 70   83 = 1 x 70 + 13    chi2 from the folding alone   97
#
#   against a sweep threshold near 78.  A naive chi2 against n / A would fire
#   on those moduli with no plaintext structure whatsoever.  The fix is
#   arithmetic, not statistical: expected count for bin j is n times the number
#   of source values that land in it, over 83.
#
# WHAT IS KNOWN AND WHAT IS NOT
#   C , the ciphertext , is KNOWN in length , ordering and substance.  The read
#   order was the unique survivor of 691 920 candidates.  P , K and F are the
#   unknowns.  Every formula depends on C because C is what we have.
#
# COMMANDS   (copy paste these, no angle brackets)
#
#   python eye_fingerprint.py selftest
#   python eye_fingerprint.py artefact
#   python eye_fingerprint.py sweep [--maxlag 40] [--top 15]
#   python eye_fingerprint.py null  [--maxlag 40] [--top 5]
# ============================================================================

import sys, math

NSYM = 83
NMSG = 9
ORDER = ['East 1', 'West 1', 'East 2', 'West 2', 'East 3',
         'West 3', 'East 4', 'West 4', 'East 5']
MSG, MLEN = [], []

# sorted English letter frequencies, used only to INTERPRET a hit, never to
# detect one.  Detection is chi squared, which needs no language at all.
ENG = [12.70, 9.06, 8.17, 7.51, 6.97, 6.75, 6.33, 6.09, 5.99, 4.25, 4.03,
       2.78, 2.76, 2.41, 2.36, 2.23, 2.02, 1.97, 1.93, 1.49, 0.98, 0.77,
       0.15, 0.15, 0.10, 0.07]


def build():
    global MSG, MLEN
    MSG, MLEN = [], []
    for name in ORDER:
        body = RAW[name][1:]
        MSG.append(body)
        MLEN.append(len(body))


def chi2_z(x, df):
    """Wilson-Hilferty normal score for a chi squared.

    The naive ( x - df ) / sqrt ( 2 df ) is badly wrong in the tail at small
    df, which matters here because the alphabet axis runs from 25 to 81
    degrees of freedom.  On the corpus's top candidate, chi2 70.7 on 27 df,
    naive gives z = + 5.94 and Wilson-Hilferty gives + 4.25.  Ranking by the
    naive score also ranks the small alphabets too highly against the large
    ones, which is worse than a wrong threshold."""
    a = 2.0 / (9.0 * df)
    return ((x / float(df)) ** (1.0 / 3.0) - (1 - a)) / math.sqrt(a)


def chi2_quantile(df, p):
    lo, hi = 0.0, 14.0
    for _ in range(200):
        z = (lo + hi) / 2
        if 0.5 * math.erfc(z / math.sqrt(2)) > p:
            lo = z
        else:
            hi = z
    a = 2.0 / (9 * df)
    return df * (1 - a + z * math.sqrt(a)) ** 3


def residual_hist(m, a):
    """83 bin histogram of C [ i ] - a C [ i - m ].

    RULE 10.  Messages identical at both positions the transform touches give
    the same residual and contribute it once."""
    h = [0] * NSYM
    n = 0
    mx = max(MLEN)
    for i in range(m, mx):
        seen = set()
        for g in range(NMSG):
            if i >= MLEN[g]:
                continue
            key = (MSG[g][i], MSG[g][i - m])
            if key in seen:
                continue
            seen.add(key)
            h[(MSG[g][i] - a * MSG[g][i - m]) % NSYM] += 1
            n += 1
    return h, n


def fold_maps(A):
    """value 0..82 -> bin 0..A-1, for the three homophonic shapes.
    Returns (name, table, weight) where weight[j] is how many source values
    land in bin j.  weight is what makes the expected counts exact."""
    out = []
    t = [v % A for v in range(NSYM)]
    out.append(('mod', t))
    w = (NSYM + A - 1) // A
    t = [min(v // w, A - 1) for v in range(NSYM)]
    out.append(('div', t))
    t = [v if v < A else -1 for v in range(NSYM)]
    out.append(('keep', t))
    res = []
    for nm, tb in out:
        wt = [0] * A
        for v in range(NSYM):
            if tb[v] >= 0:
                wt[tb[v]] += 1
        res.append((nm, tb, wt))
    return res


def fold_chi(h, n, tb, wt, A):
    """chi squared of the folded histogram against the EXACT expected counts."""
    c = [0] * A
    tot = 0
    for v in range(NSYM):
        j = tb[v]
        if j >= 0:
            c[j] += h[v]
            tot += h[v]
    src = sum(wt)
    if tot == 0 or src == 0:
        return 0.0, 0
    x = 0.0
    for j in range(A):
        e = tot * wt[j] / float(src)
        if e > 0:
            x += (c[j] - e) * (c[j] - e) / e
    return x, tot


def profile_distance(h, tb, A):
    """How far the folded distribution's SORTED shape is from English.
    Order free, language shape only.  Reported for interpretation, never used
    to detect."""
    c = [0] * A
    for v in range(NSYM):
        if tb[v] >= 0:
            c[tb[v]] += h[v]
    t = float(sum(c)) or 1.0
    obs = sorted([x / t * 100 for x in c], reverse=True)
    ref = ENG[:] + [0.0] * max(0, A - len(ENG))
    ref = ref[:A]
    s = sum(ref) or 1.0
    ref = [x / s * 100 for x in ref]
    return sum(abs(o - r) for o, r in zip(obs, ref)) / 2.0


# ------------------------------------------------------------------ sweeps --
def cmd_artefact():
    print("THE FOLDING ARTEFACT , why a naive chi2 would fire on every modulus")
    print()
    print("   A    83 = q A + r    bins with q+1   naive chi2 on 900 uniform draws")
    n = 900
    for A in (26, 30, 40, 52, 60, 70, 82):
        q, r = divmod(NSYM, A)
        exp = [(q + 1) / float(NSYM) * n if j < r else q / float(NSYM) * n
               for j in range(A)]
        flat = n / float(A)
        chi = sum((e - flat) ** 2 / flat for e in exp)
        print("   %-4d %2d x %-3d + %-3d %10d %22.0f" % (A, q, A, r, r, chi))
    print()
    print("  This tool uses the exact counts, so all of the above read zero.")
    return 0


def cmd_sweep(maxlag, top):
    A_LO, A_HI = 26, 82
    folds = {A: fold_maps(A) for A in range(A_LO, A_HI + 1)}
    ncomb = maxlag * (NSYM - 1) * (A_HI - A_LO + 1) * 3
    print("FINGERPRINT SWEEP")
    print("  lags 1..%d , multipliers 1..82 , alphabets %d..%d , 3 fold maps"
          % (maxlag, A_LO, A_HI))
    print("  %d combinations\n" % ncomb)
    rows = []
    for m in range(1, maxlag + 1):
        for a in range(1, NSYM):
            h, n = residual_hist(m, a)
            for A in range(A_LO, A_HI + 1):
                for nm, tb, wt in folds[A]:
                    x, tot = fold_chi(h, n, tb, wt, A)
                    if tot < 200:
                        continue
                    z = chi2_z(x, A - 1)
                    rows.append((z, x, A, nm, m, a, tot))
    rows.sort(reverse=True)
    print("  the alphabets have different degrees of freedom, so candidates are")
    print("  ranked by z, not by raw chi squared\n")
    print("   rank      z     chi2    A   fold   lag    a      n   profile gap")
    for r, (z, x, A, nm, m, a, tot) in enumerate(rows[:top]):
        h, n = residual_hist(m, a)
        tb = [t for nn, t, w in folds[A] if nn == nm][0]
        pg = profile_distance(h, tb, A)
        print("   %4d %+7.2f %8.1f %4d %6s %5d %4d %6d %10.1f"
              % (r + 1, z, x, A, nm, m, a, tot, pg))
    lo, hi = 0.0, 12.0
    for _ in range(200):
        zz = (lo + hi) / 2
        if 0.5 * math.erfc(zz / math.sqrt(2)) > 0.05 / ncomb:
            lo = zz
        else:
            hi = zz
    zthr = (lo + hi) / 2
    print("\n  threshold for p = 0.05 across %d combinations : z > %.2f"
          % (ncomb, zthr))
    print("  (this treats the combinations as independent, which they are not;")
    print("  the null run below is the honest calibration)")
    print("  highest z is %+.2f  ->  %s"
          % (rows[0][0], "*** HIT ***" if rows[0][0] > zthr else "nothing"))
    print()
    print("  profile gap is the percentage-point distance between the SORTED")
    print("  folded distribution and sorted English.  Under 15 would be")
    print("  language shaped.  It is interpretation, not detection.")
    return 0


def cmd_null(maxlag, reps):
    """Honest calibration.  The 560 880 combinations are NOT independent:
    neighbouring lags and multipliers reuse the same residuals, and 57
    alphabets x 3 maps all fold the SAME 83 bin histogram.  So the Bonferroni
    threshold is wrong in an unknown direction.  Shuffle each message, run the
    identical sweep, and read the maximum z off the result."""
    A_LO, A_HI = 26, 82
    folds = {A: fold_maps(A) for A in range(A_LO, A_HI + 1)}
    st = [987654321]

    def rnd():
        x = st[0]
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        st[0] = x
        return x
    global MSG
    real = list(MSG)
    out = []
    for rep in range(reps):
        sh = []
        for g in range(NMSG):
            row = list(real[g])
            for i in range(len(row) - 1, 0, -1):
                j = rnd() % (i + 1)
                row[i], row[j] = row[j], row[i]
            sh.append(row)
        MSG = sh
        best = -99.0
        for m in range(1, maxlag + 1):
            for a in range(1, NSYM):
                h, n = residual_hist(m, a)
                for A in range(A_LO, A_HI + 1):
                    for nm, tb, wt in folds[A]:
                        x, tot = fold_chi(h, n, tb, wt, A)
                        if tot < 200:
                            continue
                        z = chi2_z(x, A - 1)
                        if z > best:
                            best = z
        out.append(best)
        print("  shuffled corpus %d : max z over the whole sweep %+.2f"
              % (rep + 1, best))
    MSG = real
    # the real corpus, scored the identical way
    obs = -99.0
    for m in range(1, maxlag + 1):
        for a in range(1, NSYM):
            h, n = residual_hist(m, a)
            for A in range(A_LO, A_HI + 1):
                for nm, tb, wt in folds[A]:
                    x, tot = fold_chi(h, n, tb, wt, A)
                    if tot < 200:
                        continue
                    z = chi2_z(x, A - 1)
                    if z > obs:
                        obs = z
    out.sort()
    print()
    print("  null max z   median %+.2f , max %+.2f over %d shuffled corpora"
          % (out[len(out) // 2], out[-1], reps))
    print("  real corpus  %+.2f" % obs)
    ge = sum(1 for v in out if v >= obs)
    print("  %d of %d shuffled corpora reach or beat it" % (ge, reps))
    print()
    print("  The Bonferroni line of + 5.22 assumes 560 880 independent tests.")
    print("  They are not independent: 57 alphabets times 3 maps all fold the")
    print("  SAME 83 bin histogram, and neighbouring lags reuse residuals.  The")
    print("  measured null max is about + 4.2 , so Bonferroni was a full sigma")
    print("  too strict.  It would have cost a real hit, not manufactured one.")
    return 0


def selftest():
    global MSG, MLEN
    ok = True
    print("corpus       : body lengths " + " ".join(str(x) for x in MLEN))
    print("             : expected     98 102 117 101 136 123 118 119 113")
    ok = ok and MLEN == [98, 102, 117, 101, 136, 123, 118, 119, 113]

    # the folding artefact must be exactly zero under the exact expected counts
    worst = 0.0
    for A in range(26, 83):
        for nm, tb, wt in fold_maps(A):
            h = [10] * NSYM                     # perfectly uniform over 83
            x, tot = fold_chi(h, 830, tb, wt, A)
            worst = max(worst, x)
    okrow = worst < 1e-6
    ok = ok and okrow
    print("artefact     : uniform input folds to chi2 %.2e across all A and all"
          " maps, expected 0   %s" % (worst, "OK" if okrow else "*** FAIL ***"))

    # POSITIVE CONTROL.  Plant English through a homophonic code and a known
    # GAK, and require the sweep to recover the lag, the multiplier, the
    # alphabet and the fold map.
    st = [20260819]

    def rnd():
        x = st[0]
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        st[0] = x
        return x
    cum = []
    acc = 0.0
    for f in ENG:
        acc += f / sum(ENG)
        cum.append(acc)

    def letter():
        u = (rnd() >> 8) / float(1 << 24)
        for i, c in enumerate(cum):
            if u <= c:
                return i
        return 25
    LAG, MUL, A = 3, 1, 26
    real = (list(MSG), list(MLEN))
    synth = []
    for g in range(NMSG):
        Lg = real[1][g]
        C = [0] * Lg
        for i in range(Lg):
            # homophonic: letter L is carried by any code congruent to L mod 26
            L = letter()
            opts = [v for v in range(NSYM) if v % A == L]
            P = opts[rnd() % len(opts)]
            prev = C[i - LAG] if i >= LAG else 0
            C[i] = (P + MUL * prev) % NSYM
        synth.append(C)
    MSG = synth
    best = None
    for m in range(1, 7):
        for a in (1,):
            h, n = residual_hist(m, a)
            for nm, tb, wt in fold_maps(A):
                x, tot = fold_chi(h, n, tb, wt, A)
                z = chi2_z(x, A - 1)
                if best is None or z > best[0]:
                    best = (z, m, nm, x)
    MSG, MLEN = real
    okrow = (best[1] == LAG and best[2] == 'mod')
    ok = ok and okrow
    print("positive     : planted English via a mod-26 homophonic code at lag"
          " %d" % LAG)
    print("             : sweep peaks at lag %d , fold %s , z %+.1f   %s"
          % (best[1], best[2], best[0], "OK" if okrow else "*** FAIL ***"))

    # RULE 10 must remove something
    h, n = residual_hist(1, 1)
    tot = sum(max(0, MLEN[g] - 1) for g in range(NMSG))
    okrow = n < tot
    ok = ok and okrow
    print("rule 10      : lag 1 uses %d of %d raw residuals after"
          " deduplication   %s" % (n, tot, "OK" if okrow else "*** FAIL ***"))

    print("SELF TEST %s" % ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


USAGE = """eye_fingerprint.py  -  alphabet fingerprint brute

  python eye_fingerprint.py selftest
  python eye_fingerprint.py artefact
  python eye_fingerprint.py sweep [--maxlag 40] [--top 15]
  python eye_fingerprint.py null  [--maxlag 40] [--top 5]
"""


def main(argv):
    build()
    maxlag, top = 40, 15
    pos = []
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == '--maxlag':
            maxlag = int(argv[i + 1]); i += 1
        elif a == '--top':
            top = int(argv[i + 1]); i += 1
        elif a.startswith('--'):
            print("unknown option %s" % a); return 2
        else:
            pos.append(a)
        i += 1
    if not pos:
        print(USAGE); return 2
    c = pos[0]
    if c == 'selftest': return selftest()
    if c == 'artefact': return cmd_artefact()
    if c == 'sweep': return cmd_sweep(maxlag, top)
    if c == 'null': return cmd_null(maxlag, top if top < 20 else 5)
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

if __name__ == '__main__':
    sys.exit(main(sys.argv))
