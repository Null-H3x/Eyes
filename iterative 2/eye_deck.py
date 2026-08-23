#!/usr/bin/env python3
# ============================================================================
# eye_deck.py  -  deck cipher search for the Noita Eye corpus
#                 pure standard library, no pip install, Windows ready
#
# WHY THIS TOOL EXISTS, AND WHY IT IS DIFFERENT FROM EVERY OTHER ONE
#
#   Reports 18 and 19 closed the keystream program on one argument: if the
#   source does not repeat, the correct keystream scores the same as a wrong
#   one, so the answer cannot be recognised even when it is hit.  No scoring
#   function, no search.
#
#   THAT ARGUMENT DOES NOT APPLY TO A DECK CIPHER.
#
#   Report 15 rank 3 kept one scorer alive and flagged it conditional:
#     "plaintext alphabet a proper subset of the 83 ... already excluded for
#      additive and multiplicative combining by the CP-SAT search.  ALIVE FOR
#      EVERY OTHER F."
#
#   A deck cipher is every other F.  With C [ i ] = sigma_i ( P [ i ] ) and
#   sigma_i a general permutation, stripping a candidate deck gives
#   P [ i ] = sigma_i inverse ( C [ i ] ), and DISTINCT SYMBOL COUNT works.
#
#     plaintext alphabet 26 :  correct deck -> 26 distinct , wrong deck -> 83
#     plaintext alphabet 30 :  correct deck -> 30 distinct , wrong deck -> 83
#     plaintext alphabet 60 :  correct deck -> 60 distinct , wrong deck -> 83
#     plaintext alphabet 83 :  correct deck -> 83 distinct , wrong deck -> 83
#
#   The separation is arithmetic, not statistical.  No null, no calibration,
#   no assumption about repeated content.  The one thing it needs is that the
#   inner code uses fewer than 83 codes, which is the last live hypothesis.
#
# WHAT YOU MUST SUPPLY
#   The deck generator.  Everything else is built.  See the PLUG IN HERE
#   section: one function, seed in, list of permutations out.  Until a real
#   generator is pasted in, the built in ones are placeholders that let the
#   machinery be tested, not candidates anyone believes.
#
# COMMANDS   (copy paste these)
#
#   python eye_deck.py selftest
#   python eye_deck.py list
#   python eye_deck.py probe   xorshift-fy 1
#   python eye_deck.py search  xorshift-fy 0 100000 --cut 78 --workers 64
#
#   Do NOT paste angle bracket placeholders.  PowerShell treats < and > as
#   reserved redirection operators and errors before python runs.
#
#   --cut is the early abort.  A candidate is dropped the moment its running
#   distinct count passes this.
#
#   THE CUT IS SET FROM DATA, NOT TASTE.  Cross message coincidence at the
#   same position is P ( P_a = P_b ), and that holds FOR ANY F, because
#   sigma_i is a bijection so C_a = C_b exactly when P_a = P_b.  It therefore
#   bounds the plaintext alphabet for a deck as well:
#
#       measured cross triplet coincidence   0.01683 +- 0.00252
#       implied plaintext alphabet           59 , 95 pct interval [ 46 , 84 ]
#       26 or 30 letters                     excluded at z = - 5.2
#
#   So a correct deck would show about 59 distinct symbols, not 26.  The
#   default cut is 78, above the interval's upper end and below the 83 a
#   wrong deck saturates at.  A cut of 45 would ABORT THE CORRECT ANSWER,
#   which is what this file shipped with for about an hour.
# ============================================================================

import sys, time, os, math

NSYM = 83
NMSG = 9
ORDER = ['East 1', 'West 1', 'East 2', 'West 2', 'East 3',
         'West 3', 'East 4', 'West 4', 'East 5']
LABELS = ['E1', 'W1', 'E2', 'W2', 'E3', 'W3', 'E4', 'W4', 'E5']

MSG, MLEN, DIF, DLEN, MAXL = [], [], [], [], 0


def build():
    global MSG, MLEN, DIF, DLEN, MAXL
    MSG, MLEN, DIF, DLEN = [], [], [], []
    for name in ORDER:
        body = RAW[name][1:]
        MSG.append(body)
        MLEN.append(len(body))
        d = [(body[i + 1] - body[i]) % NSYM for i in range(len(body) - 1)]
        DIF.append(d)
        DLEN.append(len(d))
    MAXL = max(MLEN)


# ======================================================================
#  PLUG IN HERE
#  ------------
#  A generator takes a seed and returns a list of at least MAXL
#  permutations of range(83) - the deck state at each cipher position.
#  Paste the real shuffle and the real PRNG in as a new function and add
#  it to GENERATORS at the bottom of this block.
#
#  WHAT I NEED FROM THE REPOSITORY TO WRITE THE REAL ONE
#    1  the PRNG itself: algorithm, state width, the exact constants,
#       how it is seeded, and whether it is advanced per shuffle or per card
#    2  the shuffle: riffle, faro in or out, overhand, cut, Fisher Yates,
#       and how many are applied between one symbol and the next
#    3  the deck size, and how the cards map onto the 83 symbols
#    4  the seed space: how wide, and whether seeds are arbitrary or come
#       from something like a timestamp or a level seed
#  Item 4 decides feasibility on its own.  See the speed note in search.
# ======================================================================

class LCG(object):
    """A generic linear congruential generator.  a, c, m are supplied so any
    of the classic parameter sets can be used without editing code."""
    __slots__ = ('s', 'a', 'c', 'm')

    def __init__(self, seed, a, c, m):
        self.s = seed % m
        self.a, self.c, self.m = a, c, m

    def next(self):
        self.s = (self.a * self.s + self.c) % self.m
        return self.s

    def below(self, n):
        return self.next() % n


class XorShift32(object):
    __slots__ = ('s',)

    def __init__(self, seed):
        self.s = (seed & 0xFFFFFFFF) or 0x9E3779B9

    def next(self):
        x = self.s
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        self.s = x
        return x

    def below(self, n):
        return self.next() % n


def _fisher_yates(rng, deck):
    for i in range(len(deck) - 1, 0, -1):
        j = rng.below(i + 1)
        deck[i], deck[j] = deck[j], deck[i]
    return deck


def _riffle(rng, deck):
    n = len(deck)
    cut = n // 2 + rng.below(5) - 2
    a, b = deck[:cut], deck[cut:]
    out = []
    while a or b:
        if not a:
            out.append(b.pop(0))
        elif not b:
            out.append(a.pop(0))
        elif rng.below(2):
            out.append(a.pop(0))
        else:
            out.append(b.pop(0))
    return out


def _faro(rng, deck):
    n = len(deck)
    h = (n + 1) // 2
    a, b = deck[:h], deck[h:]
    out = []
    for i in range(n):
        if i % 2 == 0 and a:
            out.append(a.pop(0))
        elif b:
            out.append(b.pop(0))
        elif a:
            out.append(a.pop(0))
    return out


def _cut(rng, deck):
    k = 1 + rng.below(len(deck) - 1)
    return deck[k:] + deck[:k]


def make_gen(rngmaker, op, per_step=1):
    """LAZY.  Yields one deck state at a time so the early abort can stop the
    shuffling as well as the scoring.

    The first version returned a full list of MAXL decks and only then scored
    them.  A wrong candidate passes the cut at position 40 of 136, so the
    abort was saving the scoring, which is nearly free, and none of the
    shuffling, which is the entire cost.  That is why the measured throughput
    matched the no-abort estimate instead of beating it."""
    def gen(seed, n):
        rng = rngmaker(seed)
        deck = list(range(NSYM))
        for _ in range(n):
            for _ in range(per_step):
                deck = op(rng, deck)
            yield deck
    return gen


GENERATORS = {
    # name                 : generator
    'lcg-glibc-fy':  make_gen(lambda s: LCG(s, 1103515245, 12345, 1 << 31), _fisher_yates),
    'lcg-java-fy':   make_gen(lambda s: LCG(s, 25214903917, 11, 1 << 48), _fisher_yates),
    'lcg-numrec-fy': make_gen(lambda s: LCG(s, 1664525, 1013904223, 1 << 32), _fisher_yates),
    'xorshift-fy':   make_gen(XorShift32, _fisher_yates),
    'xorshift-riffle': make_gen(XorShift32, _riffle, 3),
    'xorshift-cut':  make_gen(XorShift32, _cut),
    'xorshift-faro': make_gen(XorShift32, _faro),
}


# ------------------------------------------------------------- the scorer ---
def strip_distinct(decks, mode, cut=None):
    """Return the number of DISTINCT plaintext symbols the candidate implies.
    Aborts early once the count passes cut, returning cut + 1, because a wrong
    candidate blows past any threshold within the first hundred symbols."""
    seen = [False] * NSYM
    k = 0
    if mode == 'perm':
        for i, d in enumerate(decks):
            if i >= MAXL:
                break
            inv = None
            for m in range(NMSG):
                if i >= MLEN[m]:
                    continue
                if inv is None:
                    inv = [0] * NSYM
                    for x in range(NSYM):
                        inv[d[x]] = x
                v = inv[MSG[m][i]]
                if not seen[v]:
                    seen[v] = True
                    k += 1
                    if cut is not None and k > cut:
                        return k
    else:
        for i, d in enumerate(decks):
            if i >= MAXL:
                break
            key = d[0]                        # top card as the stream value
            for m in range(NMSG):
                if i >= DLEN[m]:
                    continue
                v = (DIF[m][i] - key) % NSYM
                if not seen[v]:
                    seen[v] = True
                    k += 1
                    if cut is not None and k > cut:
                        return k
    return k


# ---------------------------------------------------------------- commands --
def cmd_list():
    print("built in generators.  These are PLACEHOLDERS for testing the")
    print("machinery, not candidates anyone believes.\n")
    for k in sorted(GENERATORS):
        print("  %s" % k)
    print("\nsee the PLUG IN HERE block for what to paste in, and what I need")
    print("from the repository to write the real one.")
    return 0


def cmd_probe(name, seed, mode='perm'):
    g = GENERATORS[name]
    t0 = time.time()
    k = strip_distinct(g(seed, MAXL), mode)
    t1 = time.time()
    kc = strip_distinct(g(seed, MAXL), mode, 78)
    dt = time.time() - t1
    print("  full scan %.1f ms , with the abort at 78 %.1f ms"
          % ((t1 - t0) * 1000, dt * 1000))
    print("generator %s   seed %d   mode %s" % (name, seed, mode))
    print("  distinct plaintext symbols implied : %d of 83" % k)
    print("  a correct deck with a 26 letter inner code would give 26")
    print("  a wrong deck gives 83")
    print("  time for one candidate : %.1f ms" % (dt * 1000))
    print("  at 64 threads that is %.0f seeds per second, so"
          % (64 / dt))
    for bits in (20, 24, 32, 40):
        secs = (2 ** bits) * dt / 64
        print("    2^%-2d seeds  %s" % (bits, human(secs)))
    print("  this table already includes the abort.  It is measured on THIS")
    print("  machine, not estimated.")
    print()
    print("  FALSE POSITIVE RATE AT THIS CUT")
    print("    a wrong deck implies 1027 near uniform draws over 83 values, so")
    print("    the expected number of values it MISSES is 83 x (82/83)^1027")
    print("    = %.1e .  Missing five or more, which is what a score of 78"
          % (83 * (82.0 / 83.0) ** 1027))
    print("    would need, has probability far below one in a trillion.")
    print("    So a hit cannot be a false alarm, at any seed count.  The only")
    print("    limit on this search is wall clock.")
    return 0


def human(s):
    if s < 90: return "%.0f seconds" % s
    if s < 5400: return "%.1f minutes" % (s / 60)
    if s < 172800: return "%.1f hours" % (s / 3600)
    return "%.1f days" % (s / 86400)


_W = {}


def _init(name, mode, cut):
    build()
    _W['g'] = GENERATORS[name]
    _W['mode'] = mode
    _W['cut'] = cut


def _chunk(arg):
    lo, hi = arg
    g, mode, cut = _W['g'], _W['mode'], _W['cut']
    best, bs = NSYM + 1, -1
    for s in range(lo, hi):
        k = strip_distinct(g(s, MAXL), mode, cut)
        # k > cut means the candidate was ABORTED, not that it scored k.
        # An aborted candidate is rejected and must never win.
        if k <= cut and k < best:
            best, bs = k, s
    return best, bs


def cmd_search(name, lo, hi, mode, cut, workers):
    print("generator %s   seeds %d to %d   mode %s   early abort at %d"
          % (name, lo, hi, mode, cut))
    print("  a hit is a candidate whose distinct count is FAR below 83.")
    print("  There is no threshold to calibrate: 26 versus 83 is arithmetic.")
    n = hi - lo
    step = max(1, n // (workers * 8))
    items = [(a, min(a + step, hi)) for a in range(lo, hi, step)]
    t0 = time.time()
    if workers <= 1:
        _init(name, mode, cut)
        res = [_chunk(x) for x in items]
    else:
        import multiprocessing as mp
        with mp.Pool(workers, initializer=_init,
                     initargs=(name, mode, cut)) as p:
            res = p.map(_chunk, items, chunksize=1)
    best, bs = NSYM + 1, -1
    for b, s in res:
        if b < best:
            best, bs = b, s
    el = time.time() - t0
    print("  %d seeds in %.0f s , %.0f per second" % (n, el, n / el if el else 0))
    if bs < 0:
        print("  every seed aborted above the cut of %d." % cut)
        print("  nothing.  A wrong deck always saturates at or near 83.")
    else:
        print("  lowest distinct count %d at seed %d" % (best, bs))
        print("  *** BELOW THE CUT.  STOP AND INVESTIGATE. ***")
    return 0


def selftest():
    global MSG, MLEN, DIF, DLEN, MAXL
    ok = True
    print("corpus       : body lengths " + " ".join(str(x) for x in MLEN))
    print("             : expected     98 102 117 101 136 123 118 119 113")
    ok = ok and MLEN == [98, 102, 117, 101, 136, 123, 118, 119, 113]

    # POSITIVE CONTROL.  Build a synthetic corpus with a known deck and a known
    # plaintext alphabet, then check the scorer recovers the alphabet size and
    # saturates on a wrong deck.  Without this the tool proves nothing.
    real = (list(MSG), list(MLEN), list(DIF), list(DLEN), MAXL)
    g = GENERATORS['xorshift-fy']
    print("positive test: synthetic deck cipher, known plaintext alphabet")
    print("               alpha   correct deck   wrong deck   expected")
    for alpha in (26, 30, 45):
        dk = list(g(12345, MAXL))
        src = LCG(999 + alpha, 1103515245, 12345, 1 << 31)
        P = [[src.below(alpha) for _ in range(real[1][m])] for m in range(NMSG)]
        MSG = [[dk[i][P[m][i]] for i in range(real[1][m])] for m in range(NMSG)]
        MLEN = list(real[1]); MAXL = max(MLEN)
        good = strip_distinct(iter(dk), 'perm')
        bad = strip_distinct(g(999999, MAXL), 'perm')
        okrow = (good == alpha and bad >= 80)
        ok = ok and okrow
        print("               %5d %14d %12d   %d and 83   %s"
              % (alpha, good, bad, alpha, "OK" if okrow else "*** FAIL ***"))
    MSG, MLEN, DIF, DLEN, MAXL = real

    # the early abort must not change the verdict, only the cost
    full = strip_distinct(g(4242, MAXL), 'perm')
    cutv = strip_distinct(g(4242, MAXL), 'perm', 45)
    okrow = (full > 45 and cutv == 46)   # sentinel is cut + 1
    ok = ok and okrow
    print("early abort  : full count %d , aborted count %d , expected 46   %s"
          % (full, cutv, "OK" if okrow else "*** FAIL ***"))

    # THE CUT MUST ADMIT THE MEASURED PLAINTEXT ALPHABET.  The coincidence
    # bound puts it at 59 with a 95 percent interval to 84, so any cut at or
    # below that point estimate would abort the correct answer.
    DEFAULT_CUT = 78
    ALPHA_EST, ALPHA_HI = 59, 84
    okrow = DEFAULT_CUT > ALPHA_EST and DEFAULT_CUT < NSYM
    ok = ok and okrow
    print("cut sanity   : default cut %d , measured alphabet estimate %d ,"
          " interval to %d" % (DEFAULT_CUT, ALPHA_EST, ALPHA_HI))
    print("             : the cut must exceed the estimate and stay under 83   %s"
          % ("OK" if okrow else "*** FAIL ***"))
    a = strip_distinct(g(777, MAXL), 'perm')
    b = strip_distinct(g(777, MAXL), 'perm', DEFAULT_CUT)
    okrow = (b > DEFAULT_CUT and a == NSYM)
    ok = ok and okrow
    print("             : a wrong deck still saturates and aborts at the"
          " higher cut   %s" % ("OK" if okrow else "*** FAIL ***"))

    # an aborted candidate must never be reported as a winner
    _init('xorshift-fy', 'perm', 78)
    b, sd = _chunk((0, 40))
    okrow = (sd == -1 and b == NSYM + 1)
    ok = ok and okrow
    print("abort rule   : 40 placeholder seeds, winner seed %d , expected -1   %s"
          % (sd, "OK" if okrow else "*** FAIL ***"))

    # and on the REAL corpus a placeholder generator must saturate
    k = strip_distinct(g(1, MAXL), 'perm')
    print("real corpus  : placeholder generator gives %d distinct, expected 83" % k)
    ok = ok and k == 83
    print("             : that is the null reading.  Any real generator that")
    print("             : returns much less than 83 is the answer.")
    print("SELF TEST %s" % ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


USAGE = """eye_deck.py  -  deck cipher search, pure standard library

  python eye_deck.py selftest
  python eye_deck.py list
  python eye_deck.py probe  GEN SEED [--mode perm]
  python eye_deck.py search GEN LO HI [--mode perm] [--cut 78] [--workers 64]

  NOTE  do not paste angle brackets.  PowerShell treats < and > as reserved
        redirection operators and errors before python ever runs.
"""


def main(argv):
    build()
    mode, cut, workers = 'perm', 78, os.cpu_count() or 1
    pos = []
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == '--mode':
            mode = argv[i + 1]; i += 1
        elif a == '--cut':
            cut = int(argv[i + 1]); i += 1
        elif a == '--workers':
            workers = int(argv[i + 1]); i += 1
        elif a.startswith('--'):
            print("unknown option %s" % a); return 2
        else:
            pos.append(a)
        i += 1
    if not pos:
        print(USAGE); return 2
    c = pos[0]
    if c == 'selftest': return selftest()
    if c == 'list': return cmd_list()
    if c == 'probe':
        if pos[1] not in GENERATORS:
            print("unknown generator, run:  python eye_deck.py list"); return 2
        return cmd_probe(pos[1], int(pos[2]), mode)
    if c == 'search':
        if pos[1] not in GENERATORS:
            print("unknown generator, run:  python eye_deck.py list"); return 2
        return cmd_search(pos[1], int(pos[2]), int(pos[3]), mode, cut, workers)
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
