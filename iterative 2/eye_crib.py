#!/usr/bin/env python3
# ============================================================================
# eye_crib.py  -  key free crib engine for the Noita Eye corpus
#                 version 2 , self contained , pure standard library
#
# THE ONE THING THAT MATTERS ABOUT CRIBS HERE , MEASURED
#
#   A crib in ONE message can never be wrong.
#     The alphabet changes at every position , so the same letter at positions
#     p and p + 3 need not give the same ciphertext symbol.  A crib's own
#     internal repeat pattern is therefore unconstrained , which is Report 11's
#     measurement stated the other way round.  A single message crib faces
#     ZERO tests.  It can only propagate.
#
#   A crib covering TWO messages is decided immediately.
#     The only key free fact is cross message agreement at the SAME position ,
#     and there is a lot of it: 3611 discriminating tests across the 36 pairs ,
#     and even the weakest pair gives 74.  A wrong proposal for two messages
#     fails by margins with exponents in the tens.
#
#       pair    tests after divergence   agree   differ   P ( wrong passes )
#       E1/W1            74                20      54        10 ^ - 25
#       E4/E5            93                11      82        10 ^ - 15
#       E4/W4            98                 2      96        10 ^ - 5
#
#   So the useful unit is not a crib.  It is a PAIR of proposals for two
#   messages that overlap after their divergence point.  Guessing a phrase in
#   one message buys you nothing you can check.  Guessing what the SAME passage
#   says in two versions is decisive in milliseconds.
#
# COMMANDS   (copy paste these)
#
#   python eye_crib.py selftest
#   python eye_crib.py power              what a crib is worth , measured
#   python eye_crib.py partition          the key free equality partition
#   python eye_crib.py handles            positions ranked by how much they buy
#   python eye_crib.py template           write a blank crib file to fill in
#   python eye_crib.py check crib.txt     test a proposal
#   python eye_crib.py propagate crib.txt fill in what it forces elsewhere
#
# CRIB FILE FORMAT
#   One line per message.  Blank lines and lines starting with # are ignored.
#
#       E1 THE.SKY.IS.......
#       W1 ...........
#       E4 ?????SKY??
#
#   Label is one of E1 W1 E2 W2 E3 W3 E4 W4 E5.  Text is read one character per
#   cipher symbol starting at position 0.  Dot or question mark means unknown.
#   Characters are compared only for equality , so use any glyphs you like.
# ============================================================================

import sys, math

NSYM = 83
LABELS = ['E1', 'W1', 'E2', 'W2', 'E3', 'W3', 'E4', 'W4', 'E5']
ORDER = ['East 1', 'West 1', 'East 2', 'West 2', 'East 3',
         'West 3', 'East 4', 'West 4', 'East 5']
WILD = '.?_ '

MSG, MLEN, HDR = [], [], []


def build():
    global MSG, MLEN, HDR
    MSG, MLEN, HDR = [], [], []
    for name in ORDER:
        v = RAW[name]
        HDR.append(v[0])          # position 0 , outside the cipher , Report 6
        MSG.append(v[1:])
        MLEN.append(len(v) - 1)


def divergence(a, b):
    n = min(MLEN[a], MLEN[b])
    i = 0
    while i < n and MSG[a][i] == MSG[b][i]:
        i += 1
    return i


def classes_at(i):
    """the key free partition of the messages present at position i"""
    by = {}
    for m in range(9):
        if i < MLEN[m]:
            by.setdefault(MSG[m][i], []).append(m)
    return sorted(by.values(), key=lambda c: (-len(c), c[0]))


# ------------------------------------------------------------------ power ---
def cmd_power():
    print("A proposal for ONE message faces zero tests.  Its internal repeats")
    print("are unconstrained, because position i and position j use different")
    print("alphabets.  It can only propagate, never fail.\n")
    print("  a full plaintext for this message hands you this many further")
    print("  symbols across the other eight, of 1027 total")
    best = None
    for a in range(9):
        got = 0
        for i in range(MLEN[a]):
            for b in range(9):
                if b != a and i < MLEN[b] and MSG[b][i] == MSG[a][i]:
                    got += 1
        if best is None or got > best[1]:
            best = (LABELS[a], got)
        print("    %-3s  %4d" % (LABELS[a], got))
    print("  best single message to guess : %s , %d symbols\n" % best)

    print("A proposal for TWO messages is decided by one binary test per shared")
    print("position after their divergence point.\n")
    print("  pair     common  diverge  tests  agree  differ   P ( wrong passes )")
    rows = []
    for a in range(9):
        for b in range(a + 1, 9):
            n = min(MLEN[a], MLEN[b])
            d = divergence(a, b)
            ag = sum(1 for i in range(d, n) if MSG[a][i] == MSG[b][i])
            di = (n - d) - ag
            k = 0.065                      # letter coincidence, English-like
            lp = ag * math.log(k) + di * math.log(1 - k)
            rows.append((LABELS[a], LABELS[b], n, d, n - d, ag, di, lp))
    for r in sorted(rows, key=lambda x: -x[5])[:6]:
        print("  %s / %s  %5d   %5d   %5d  %5d  %6d   10 ^ %.0f"
              % (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7] / math.log(10)))
    print("  ... 30 more pairs")
    w = min(rows, key=lambda x: x[4])
    print("  weakest pair by test count : %s / %s with %d tests"
          % (w[0], w[1], w[4]))
    print("  total discriminating tests across all 36 pairs : %d"
          % sum(r[4] for r in rows))
    print()
    print("  THE PRACTICAL CONSEQUENCE")
    print("  Guessing a phrase in one message buys nothing you can check.")
    print("  Guessing what the SAME passage says in two versions is decisive.")
    print("  Aim any in game observation at a PAIR inside one triplet:")
    print("    T1  E1 W1 E2      T2  W2 E3 W3      T3  E4 W4 E5")
    return 0


# -------------------------------------------------------------- partition ---
def cmd_partition():
    print("key free equality partition, one line per position")
    print("a group in brackets shares the same plaintext symbol\n")
    for i in range(max(MLEN)):
        cl = classes_at(i)
        shown = " ".join("[" + " ".join(LABELS[m] for m in c) + "]"
                         for c in cl if len(c) > 1)
        n = sum(1 for m in range(9) if i < MLEN[m])
        print("  %3d  %d present   %s" % (i, n, shown if shown else "all distinct"))
    return 0


def cmd_handles():
    """rank positions by how many symbols one guess there would pin"""
    rows = []
    for i in range(max(MLEN)):
        cl = classes_at(i)
        big = len(cl[0]) if cl else 0
        rows.append((i, big, len(cl)))
    rows.sort(key=lambda r: -r[1])
    print("positions ranked by the size of the largest equal class")
    print("one correct guess at position i pins every message in that class\n")
    print("  position   largest class   distinct classes")
    for i, big, nc in rows[:20]:
        names = " ".join(LABELS[m] for m in classes_at(i)[0])
        print("  %6d %13d %15d    %s" % (i, big, nc, names))
    tot = sum(r[1] for r in rows)
    print("\n  guessing one symbol at EVERY position, always the largest class,")
    print("  pins %d of 1027 body symbols for %d guesses" % (tot, len(rows)))
    return 0


# ------------------------------------------------------------ crib checking --
def read_crib(path):
    crib = {}
    for line in open(path):
        line = line.rstrip('\n')
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2 or parts[0] not in LABELS:
            continue
        crib[LABELS.index(parts[0])] = parts[1]
    return crib


def check(crib, verbose=True):
    """Every pair of asserted letters at the same position is one test:
    the letters must be equal exactly when the ciphertext symbols are."""
    tests = ok = 0
    fails = []
    for a in crib:
        for b in crib:
            if b <= a:
                continue
            ta, tb = crib[a], crib[b]
            n = min(len(ta), len(tb), MLEN[a], MLEN[b])
            for i in range(n):
                ca, cb = ta[i], tb[i]
                if ca in WILD or cb in WILD:
                    continue
                tests += 1
                same_txt = (ca == cb)
                same_cip = (MSG[a][i] == MSG[b][i])
                if same_txt == same_cip:
                    ok += 1
                else:
                    fails.append((i, LABELS[a], ca, LABELS[b], cb, same_cip))
    if verbose:
        print("tests applied  %d" % tests)
        print("consistent     %d" % ok)
        print("contradictions %d" % len(fails))
        for f in fails[:25]:
            print("  position %3d : %s has %r , %s has %r , ciphertext says %s"
                  % (f[0], f[1], f[2], f[3], f[4],
                     "EQUAL" if f[5] else "DIFFERENT"))
        if len(fails) > 25:
            print("  ... %d more" % (len(fails) - 25))
        if tests == 0:
            print("\n  NO TESTS WERE APPLIED.  A proposal covering one message,")
            print("  or covering messages that never overlap, cannot be checked.")
            print("  See the power command.")
        elif not fails:
            print("\n  CONSISTENT.  Run propagate to see what it forces.")
        else:
            print("\n  REFUTED.")
    return tests, ok, fails


def propagate(crib):
    out = [['.'] * MLEN[m] for m in range(9)]
    for m in crib:
        for i, ch in enumerate(crib[m]):
            if i < MLEN[m] and ch not in WILD:
                out[m][i] = ch
    changed = True
    while changed:
        changed = False
        for i in range(max(MLEN)):
            for cl in classes_at(i):
                known = [out[m][i] for m in cl if out[m][i] != '.']
                if not known:
                    continue
                v = known[0]
                for m in cl:
                    if out[m][i] == '.':
                        out[m][i] = v
                        changed = True
    return out


def cmd_propagate(crib):
    tests, ok, fails = check(crib, verbose=False)
    if fails:
        print("proposal is REFUTED, %d contradictions.  Not propagating." % len(fails))
        return 1
    out = propagate(crib)
    given = sum(1 for m in crib for c in crib[m] if c not in WILD)
    filled = sum(1 for m in range(9) for c in out[m] if c != '.')
    print("given %d symbols, %d tests passed" % (given, tests))
    print("propagates to %d of 1027 body symbols\n" % filled)
    for m in range(9):
        print("  %-3s %s" % (LABELS[m], "".join(out[m])))
    return 0


def cmd_template():
    with open('crib.txt', 'w') as f:
        f.write("# one line per message, dot means unknown\n")
        f.write("# aim at a PAIR inside one triplet - see the power command\n")
        f.write("#   T1  E1 W1 E2      T2  W2 E3 W3      T3  E4 W4 E5\n")
        for m in range(9):
            f.write("%s %s\n" % (LABELS[m], "." * MLEN[m]))
    print("wrote crib.txt , 9 lines , lengths " + " ".join(str(x) for x in MLEN))
    print("edit it and run:  python eye_crib.py check crib.txt")
    return 0


# --------------------------------------------------------------- selftest ---
def selftest():
    ok = True
    print("corpus       : body lengths " + " ".join(str(x) for x in MLEN))
    print("             : expected     98 102 117 101 136 123 118 119 113")
    ok = ok and MLEN == [98, 102, 117, 101, 136, 123, 118, 119, 113]
    print("headers      : " + " ".join(str(x) for x in HDR))
    print("             : expected 50 80 36 76 63 34 27 77 33")
    ok = ok and HDR == [50, 80, 36, 76, 63, 34, 27, 77, 33]

    d = [divergence(0, 1), divergence(3, 4), divergence(6, 7)]
    print("divergence   : E1/W1 %d , W2/E3 %d , E4/W4 %d" % tuple(d))
    print("             : expected 24 , 5 , 20   the triplet openings")
    print("             : these are BODY coordinates.  Earlier reports quote")
    print("             : them one higher because they counted the header.")
    ok = ok and d == [24, 5, 20]

    # a TRUE crib must pass: read the real symbols off as letters
    true0 = "".join(chr(65 + MSG[0][i] % 26) for i in range(MLEN[0]))
    print("true crib    : a proposal built FROM the ciphertext must be consistent")
    # build it for two messages using a common symbol -> letter map
    mp = {}
    def lt(v):
        if v not in mp:
            mp[v] = chr(33 + len(mp))
        return mp[v]
    c = {0: "".join(lt(MSG[0][i]) for i in range(MLEN[0])),
         1: "".join(lt(MSG[1][i]) for i in range(MLEN[1]))}
    t, o, f = check(c, verbose=False)
    print("             : %d tests, %d passed, %d contradictions, expected 0"
          % (t, o, len(f)))
    ok = ok and t > 0 and not f

    # and a deliberately BROKEN one must fail
    bad = dict(c)
    lst = list(bad[1])
    j = divergence(0, 1)
    lst[j] = bad[0][j]                     # force agreement where there is none
    bad[1] = "".join(lst)
    t2, o2, f2 = check(bad, verbose=False)
    print("broken crib  : one symbol flipped at the divergence point")
    print("             : %d contradictions, expected at least 1" % len(f2))
    ok = ok and len(f2) >= 1

    # a single message proposal must face ZERO tests
    t3, _, _ = check({0: c[0]}, verbose=False)
    print("single msg   : %d tests applied, expected 0   (this is the point)" % t3)
    ok = ok and t3 == 0

    print("SELF TEST %s" % ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


USAGE = """eye_crib.py  -  key free crib engine, self contained

  python eye_crib.py selftest
  python eye_crib.py power
  python eye_crib.py partition
  python eye_crib.py handles
  python eye_crib.py template
  python eye_crib.py check crib.txt
  python eye_crib.py propagate crib.txt
"""


def main(argv):
    build()
    if len(argv) < 2:
        print(USAGE); return 2
    cmd = argv[1]
    if cmd == 'selftest':
        return selftest()
    if cmd == 'power':
        return cmd_power()
    if cmd == 'partition':
        return cmd_partition()
    if cmd == 'handles':
        return cmd_handles()
    if cmd == 'template':
        return cmd_template()
    if cmd in ('check', 'propagate'):
        if len(argv) < 3:
            print("give a crib file, or run:  python eye_crib.py template")
            return 2
        crib = read_crib(argv[2])
        if not crib:
            print("no usable lines in %s" % argv[2]); return 2
        if cmd == 'check':
            check(crib); return 0
        return cmd_propagate(crib)
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
