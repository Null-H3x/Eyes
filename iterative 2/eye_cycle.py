#!/usr/bin/env python3
# ============================================================================
# eye_cycle.py   -   structural keystream scorer for the Noita Eye corpus
#                    pure standard library, no pip install, Windows ready
#
# This is a faithful port of eye_cycle.c.  It carries the SAME random number
# generator (xoshiro256++, seeded the same way), so the self test prints the
# same numbers the C build prints.  If they ever disagree, one of the two is
# wrong and neither result should be believed.
#
# WHAT IT DOES
#   Strip a candidate keystream out of the corpus, then score what is left for
#   structure.  Two scorers, neither of which uses letter frequencies, so both
#   survive the Field Report 3 finding that the plaintext layer is flat.
#
#     cycling rotation  (default)  Report 7 hypothesis.  Counts code pairs
#                                  consistent with strict rotation.
#     repeated 3 grams  (--ngram)  Report 15.  Counts 3 grams appearing at two
#                                  or more DISTINCT positions.  Needs only that
#                                  the source repeats content, which nearly
#                                  every real document does.
#
# COMMANDS   (copy paste these)
#
#   python eye_cycle.py selftest
#   python eye_cycle.py speed  addd --ngram --workers 64
#   python eye_cycle.py null   mult 20000 --ngram --workers 64
#   python eye_cycle.py search mult per4  --ngram --workers 64
#
# THE SHIFT QUOTIENT, ON BY DEFAULT
#   Both scorers are blind to adding a constant to the whole keystream, so
#   keystreams come in orbits of 83 (82 in mult) that all score identically and
#   only one member of each needs testing.  Every search here is therefore 83
#   times smaller than the family it covers, which takes per6 from 20 days to
#   under 6 hours.  This is proven, and checked three ways in selftest.  Pass
#   --full to disable it and search the redundant space, for auditing only.
#
#     mode    mult   P = D * K^-1 in Z83 star, keystream in Z82 by discrete log
#             addd   P = ( D - K ) mod 83, additive on the difference stream
#             addb   P = ( C - K ) mod 83, additive on the body, no cumulation
#
#     family  const lin lcg quad cubic per2 per3 per4 per5 per6 per7
#
# ONE DELIBERATE DIFFERENCE FROM THE C BUILD
#   On a tie this file reports the LOWEST index attaining the best score, so
#   two runs of the same search always print the same thing.  The C build
#   reports whichever thread reached a tying score first, which varies run to
#   run.  Scores always agree; a differing index at an equal score is this and
#   nothing else.
#
# ALWAYS run selftest first.  It checks the corpus, then measures each scorer's
# power on synthetic sources and prints the value it got beside the value it
# should have got.  If the arms are not far apart, nothing else in this file
# means anything.
# ============================================================================

import sys, time, math, os

NMSG = 9
NSYM = 83

# ---------------------------------------------------------------- corpus ----
# RAW is embedded at the bottom of this file.  Element 0 of each row is the
# header symbol, which Report 6 proved sits outside the cipher, so it is
# dropped here exactly as the C version drops it.

MSG  = []    # body symbols
MLEN = []
DIF  = []    # difference stream, values 1..82
DLEN = []
ELG  = []    # discrete log base 2 of the difference stream
DLOG = [0] * NSYM
ALOG = [0] * 82
MAXL = 0


def build():
    global MSG, MLEN, DIF, DLEN, ELG, MAXL
    MSG, MLEN, DIF, DLEN, ELG = [], [], [], [], []
    for name in ORDER:
        v = RAW[name]
        body = v[1:]
        MSG.append(body)
        MLEN.append(len(body))
        d = [(body[i + 1] - body[i]) % NSYM for i in range(len(body) - 1)]
        DIF.append(d)
        DLEN.append(len(d))
    MAXL = max(MLEN)
    x = 1
    for e in range(82):
        DLOG[x] = e
        ALOG[e] = x
        x = x * 2 % NSYM
    for m in range(NMSG):
        ELG.append([DLOG[t] for t in DIF[m]])


# ------------------------------------------------------------------- rng ----
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
        s[2] ^= s[0]
        s[3] ^= s[1]
        s[1] ^= s[2]
        s[0] ^= s[3]
        s[2] ^= t
        s[3] = _rotl(s[3], 45)
        return res

    def unif(self):
        return (self.next() >> 11) * (2.0 ** -53)

    def rint(self, n):
        return self.next() % n


# ------------------------------------------------------- cycling scorer -----
def score_stream(stream, length, nsym=NSYM):
    """Count pairs (c,d) such that in every message, between two consecutive
    occurrences of c there is exactly one occurrence of d, and symmetrically.
    Pairs where neither code repeats carry no information and are not counted."""
    pos = [[[] for _ in range(NMSG)] for _ in range(nsym)]
    for m in range(NMSG):
        row = stream[m]
        pm = pos
        for i in range(length[m]):
            pm[row[i]][m].append(i)
    tot = [0] * nsym
    for c in range(nsym):
        t = 0
        for m in range(NMSG):
            t += len(pos[c][m])
        tot[c] = t
    ok = 0
    for c in range(nsym):
        if not tot[c]:
            continue
        for d in range(c + 1, nsym):
            if not tot[d]:
                continue
            good = True
            inf = False
            for m in range(NMSG):
                pc = pos[c][m]
                pd = pos[d][m]
                nc = len(pc)
                nd = len(pd)
                if nc > 1:
                    inf = True
                    if nd == 0:
                        good = False
                        break
                    j = 0
                    for t in range(nc - 1):
                        u = pc[t]
                        v = pc[t + 1]
                        k = 0
                        while j < nd and pd[j] <= u:
                            j += 1
                        while j < nd and pd[j] < v:
                            k += 1
                            j += 1
                        if k != 1:
                            good = False
                            break
                    if not good:
                        break
                if nd > 1:
                    inf = True
                    if nc == 0:
                        good = False
                        break
                    j = 0
                    for t in range(nd - 1):
                        u = pd[t]
                        v = pd[t + 1]
                        k = 0
                        while j < nc and pc[j] <= u:
                            j += 1
                        while j < nc and pc[j] < v:
                            k += 1
                            j += 1
                        if k != 1:
                            good = False
                            break
                    if not good:
                        break
            if good and inf:
                ok += 1
    return ok


# --------------------------------------------------------- ngram scorer -----
def score_ngram(stream, length):
    """Count 3 grams occurring at two or more DISTINCT positions.

    The same position in different messages is the shared prefix, which is
    present whatever the keystream is.  Counting it swamps the real signal:
    Report 15 measured the ciphertext at 109 against a threshold of 115 with
    same position repeats counted, and 0 against 7 with them excluded."""
    first = {}
    counted = set()
    total = 0
    for m in range(NMSG):
        row = stream[m]
        n = length[m] - 2
        for i in range(n):
            k = (row[i] * NSYM + row[i + 1]) * NSYM + row[i + 2]
            fp = first.get(k, -1)
            if fp < 0:
                first[k] = i
            elif fp != i and k not in counted:
                counted.add(k)
                total += 1
    return total


# ------------------------------------------------------------ stripping -----
M_MULT, M_ADDD, M_ADDB = 0, 1, 2
MODNAME = {'mult': M_MULT, 'addd': M_ADDD, 'addb': M_ADDB}


def modulus(mode):
    return 82 if mode == M_MULT else 83


def strip(k, mode):
    """Return the stripped stream and its lengths.

    For the n gram scorer the ALOG lookup in mult mode is a bijection and so
    cannot change any equality, but it is applied anyway so that the two
    scorers see exactly the same stream and the C and Python numbers match."""
    if mode == M_MULT:
        out = [[ALOG[(ELG[m][i] - k[i]) % 82] for i in range(DLEN[m])]
               for m in range(NMSG)]
        return out, DLEN
    if mode == M_ADDD:
        out = [[(DIF[m][i] - k[i]) % NSYM for i in range(DLEN[m])]
               for m in range(NMSG)]
        return out, DLEN
    out = [[(MSG[m][i] - k[i]) % NSYM for i in range(MLEN[m])]
           for m in range(NMSG)]
    return out, MLEN


def strip_and_score(k, mode, scorer):
    st, ln = strip(k, mode)
    return score_ngram(st, ln) if scorer else score_stream(st, ln)


# -------------------------------------------------- synthetic generators ----
FRQ = [12.7, 9.1, 8.2, 7.5, 7.0, 6.7, 6.3, 6.1, 6.0, 4.3, 4.0, 2.8, 2.8,
       2.4, 2.4, 2.2, 2.0, 2.0, 1.9, 1.5, 1.0, 0.8, 0.15, 0.15, 0.10, 0.07]


def gen_cycling(r):
    s = sum(FRQ)
    sz = []
    tot = 0
    for i in range(26):
        v = int(NSYM * FRQ[i] / s + 0.5)
        if v < 1:
            v = 1
        sz.append(v)
        tot += v
    i = 25
    while tot > NSYM:
        if sz[i] > 1:
            sz[i] -= 1
            tot -= 1
        i = (i + 25) % 26
    while tot < NSYM:
        sz[0] += 1
        tot += 1
    codes = list(range(NSYM))
    for i in range(NSYM - 1, 0, -1):
        j = r.rint(i + 1)
        codes[i], codes[j] = codes[j], codes[i]
    start = []
    at = 0
    for i in range(26):
        start.append(at)
        at += sz[i]
    out = []
    for m in range(NMSG):
        ctr = [r.rint(sz[i]) for i in range(26)]
        row = []
        for _ in range(DLEN[m]):
            u = r.unif() * s
            acc = 0.0
            L = 25
            for j in range(26):
                acc += FRQ[j]
                if u <= acc:
                    L = j
                    break
            row.append(codes[start[L] + (ctr[L] % sz[L])])
            ctr[L] += 1
        out.append(row)
    return out


def gen_wordy(r, homophonic):
    """A source with REPEATED CONTENT.  gen_cycling draws letters
    independently, so it has no repeated words and the n gram scorer correctly
    reads near zero on it, which makes it useless as a power check for THAT
    scorer.  This one emits a small vocabulary of repeated tokens, which is
    what any real document does."""
    nvoc, vlen = 60, 5
    codes = list(range(NSYM))
    for i in range(NSYM - 1, 0, -1):
        j = r.rint(i + 1)
        codes[i], codes[j] = codes[j], codes[i]
    alpha = 30 if homophonic else 27
    voc = [[r.rint(alpha) for _ in range(vlen)] for _ in range(nvoc)]
    out = []
    for m in range(NMSG):
        ctr = [0] * 64
        row = []
        i = 0
        n = DLEN[m]
        while i < n:
            w = r.rint(nvoc)
            c = 0
            while c < vlen and i < n:
                L = voc[w][c]
                if homophonic:
                    h = 2 + (L % 2)
                    row.append(codes[(L * 3 + (ctr[L] % h)) % NSYM])
                    ctr[L] += 1
                else:
                    row.append(codes[L])
                c += 1
                i += 1
        out.append(row)
    return out


def gen_random(r):
    return [[r.rint(NSYM) for _ in range(DLEN[m])] for m in range(NMSG)]


# ------------------------------------------------------------- selftest -----
def selftest():
    print("corpus       : body lengths " + " ".join(str(x) for x in MLEN))
    print("             : expected     98 102 117 101 136 123 118 119 113")
    bad = sum(1 for m in range(NMSG) for x in DIF[m] if x == 0)
    print("no doubles   : %d zero steps in the difference stream, expected 0" % bad)
    print("unstripped   : difference stream scores %d, expected 0" % score_stream(DIF, DLEN))

    r2 = Rng(99)
    a = score_ngram(gen_wordy(r2, 0), DLEN)
    b = score_ngram(gen_wordy(r2, 1), DLEN)
    c = score_ngram(gen_cycling(r2), DLEN)
    d = score_ngram(gen_random(r2), DLEN)
    e = score_ngram(DIF, DLEN)
    print("ngram scorer : repeating source, plain substitution   %-4d expected 174" % a)
    print("             : repeating source, homophonic           %-4d expected 61" % b)
    print("             : independent letters, no repeated words %-4d expected 3" % c)
    print("             : flat random                            %-4d expected 0" % d)
    print("             : the real ciphertext, keystream on      %-4d expected 2" % e)

    r = Rng(4242)
    sc = sc2 = sr = sr2 = 0.0
    mnc, mxr = 1 << 30, 0
    for _ in range(20):
        x = score_stream(gen_cycling(r), DLEN)
        sc += x
        sc2 += float(x) * x
        mnc = min(mnc, x)
        y = score_stream(gen_random(r), DLEN)
        sr += y
        sr2 += float(y) * y
        mxr = max(mxr, y)
    mc, mr = sc / 20, sr / 20
    vc, vr = sc2 / 20 - mc * mc, sr2 / 20 - mr * mr
    vc = vc if vc > 0 else 0.0
    vr = vr if vr > 0 else 0.0
    sep = (mc - mr) / math.sqrt((vc + vr) / 2)
    print("power test   : cycling arm mean %.1f sd %.1f min %d   expected 321.2 38.7 250"
          % (mc, math.sqrt(vc), mnc))
    print("             : random  arm mean %.1f sd %.1f max %d     expected 1.6 1.6 6"
          % (mr, math.sqrt(vr), mxr))
    print("             : separation %.1f sd, expected 11.7" % sep)

    # ---- the shift quotient, checked in three ways rather than asserted -----
    qok = True
    rq = Rng(7)

    # 1  the scorers really are blind to a global shift.  Every one of the mod
    #    shifts of a random keystream must give ONE score, not a spread.
    for mode, mname in ((M_MULT, 'mult'), (M_ADDD, 'addd'), (M_ADDB, 'addb')):
        mod = modulus(mode)
        spread = set()
        for _ in range(2):
            k = [rq.rint(mod) for _ in range(MAXL)]
            for sc in (0, 1):                      # the two scorers, separately
                vals = set()
                for c in range(mod):
                    kk = [(x + c) % mod for x in k]
                    vals.add(strip_and_score(kk, mode, sc))
                spread.add(len(vals))
        good = spread == {1}
        qok = qok and good
        print("quotient     : %s, %d shifts of a random keystream give %s distinct"
              " score%s, expected 1   %s"
              % (mname, mod, sorted(spread), "" if spread == {1} else "s",
                 "OK" if good else "*** FAIL ***"))

    # 2  every family is CLOSED under the shift, and the slot held at zero is
    #    the right one.  lcg is the trap: k [ i ] + c is an lcg with the same
    #    multiplier a, seed k0 + c and increment b + c ( 1 - a ), so the shift
    #    lives in p [ 2 ] and fixing p [ 0 ] searches the wrong set.
    mod = 83
    for fam in ['const', 'lin', 'lcg', 'quad', 'cubic', 'per2', 'per5']:
        deg = family_degree(fam)
        bad2 = 0
        for _ in range(20):
            p = [rq.rint(mod) for _ in range(deg)]
            c = rq.rint(mod)
            # how a global shift of the keystream moves the PARAMETERS is
            # family specific, and this is where the second trap sits.  For a
            # polynomial it moves the constant term alone.  For a periodic
            # keystream it moves EVERY coefficient, because every coefficient
            # is a keystream value.  Shifting only p [ 0 ] of a per2 does not
            # shift the keystream at all, it changes one phase.
            if fam == 'lcg':
                p2 = [p[0], (p[1] + c * (1 - p[0])) % mod, (p[2] + c) % mod]
            elif fam.startswith('per'):
                p2 = [(x + c) % mod for x in p]
            else:
                p2 = list(p)
                p2[0] = (p2[0] + c) % mod
            k1 = keystream(p, fam, deg, mod, MAXL)
            k2 = keystream(p2, fam, deg, mod, MAXL)
            if any((a2 - a1) % mod != c for a1, a2 in zip(k1, k2)):
                bad2 += 1
        good = bad2 == 0
        qok = qok and good
        print("             : %-5s shift stays in the family, %d of 20 failures,"
              " expected 0, quotient holds p [ %d ] at 0   %s"
              % (fam, bad2, fixslot(fam), "OK" if good else "*** FAIL ***"))

    # 3  end to end, exhaustively, on the one family small enough to do both
    #    arms inside a selftest.  lcg was checked the same way out of band:
    #    addd lcg full 571 787 -> 7, quotient on p [ 2 ] 6889 -> 7, and quotient
    #    on p [ 0 ] 6889 -> 2, which is how the trap was found.
    mode, mod, fam, deg = M_ADDD, 83, 'per2', 2
    bf = max(strip_and_score(keystream(expand(i, fam, deg, mod, False), fam, deg,
             mod, MAXL), mode, 1) for i in range(mod ** deg))
    bq = max(strip_and_score(keystream(expand(i, fam, deg, mod, True), fam, deg,
             mod, MAXL), mode, 1) for i in range(mod))
    good = bf == bq
    qok = qok and good
    print("             : addd per2 exhaustive, full %d -> %d, quotient %d -> %d   %s"
          % (mod ** deg, bf, mod, bq, "MATCH" if good else "*** MISMATCH ***"))

    ok = (bad == 0 and a == 174 and b == 61 and d == 0
          and mc > 120 and mr < 20 and sep > 5 and qok)
    print("SELF TEST %s" % ("PASSED" if ok else "FAILED"))
    if not ok:
        print("  the numbers above disagree with the C build.  Do not trust any")
        print("  search result from this file until that is explained.")
    return 0 if ok else 1


# ---------------------------------------------------------------- speed -----
FAMDEG = {'const': 1, 'lin': 2, 'lcg': 3, 'quad': 3, 'cubic': 4}


def family_degree(fam):
    if fam.startswith('per'):
        return int(fam[3:])
    if fam not in FAMDEG:
        raise SystemExit("unknown family %s" % fam)
    return FAMDEG[fam]


# --------------------------------------------------- the shift quotient -----
# Both scorers are invariant under adding a constant to the WHOLE keystream.
#
#   addd, addb   stripping gives ( X - k - c ), a uniform shift of every symbol,
#                which is a bijection on the 83 symbols and so preserves every
#                equality the scorers look at
#   mult         stripping gives ALOG [ ( e - k - c ) mod 82 ], which is the old
#                stream multiplied by 2 to the minus c, again a bijection
#
# So keystreams come in orbits of size 83 (82 in mult) that all score
# identically, and only one member of each orbit needs testing.  Every family
# here is closed under the shift, so the orbit can be pinned by fixing one
# parameter to zero:
#
#   const lin quad cubic per2..per6   the constant term, p [ 0 ]
#   lcg                               the SEED k0, which is p [ 2 ], NOT p [ 0 ]
#
# The lcg case is the one that bites.  k' [ i ] = k [ i ] + c is again an lcg
# with the same multiplier a, seed k0 + c and increment b + c ( 1 - a ), so the
# shift moves p [ 1 ] and p [ 2 ] together and fixing p [ 0 ] instead of p [ 2 ]
# silently searches the wrong set.  Verified: on addd per3 the quotient found
# the same best score of 7 from 6889 candidates that the full 571 787 found,
# and fixing p [ 0 ] on lcg returned 2 where the truth is 7.

FIXSLOT = {'lcg': 2}


def fixslot(fam):
    return FIXSLOT.get(fam, 0)


def expand(idx, fam, deg, mod, quot):
    """index -> parameter vector.  With the quotient on, one slot is held at
    zero and the index runs over the remaining deg - 1 coefficients."""
    if not quot:
        p = []
        q = idx
        for _ in range(deg):
            p.append(q % mod)
            q //= mod
        return p
    fs = fixslot(fam)
    p = [0] * deg
    q = idx
    for i in range(deg):
        if i == fs:
            continue
        p[i] = q % mod
        q //= mod
    return p


def space(fam, deg, mod, quot):
    return mod ** (deg - 1) if quot else mod ** deg


def keystream(p, fam, deg, mod, n):
    if fam.startswith('per'):
        per = deg
        return [p[i % per] for i in range(n)]
    if fam == 'lcg':
        k = [p[2]]
        for i in range(1, n):
            k.append((p[0] * k[i - 1] + p[1]) % mod)
        return k
    k = []
    for i in range(n):
        v = p[0]
        ip = 1
        for dd in range(1, deg):
            ip = ip * i % mod
            v = (v + p[dd] * ip) % mod
        k.append(v)
    return k


def speed(mode, scorer, workers):
    r = Rng(1)
    mod = modulus(mode)
    n = MAXL
    t0 = time.time()
    N = 300
    for _ in range(N):
        k = [r.rint(mod) for _ in range(n)]
        strip_and_score(k, mode, scorer)
    dt = (time.time() - t0) / N
    print("throughput   : %.0f microseconds per candidate on one core" % (dt * 1e6))
    print("             : %.0f candidates per second at %d workers" % (workers / dt, workers))
    print()
    print("  family     full space        after quotient    wall clock at %d workers"
          % workers)
    for fam in ['const', 'lin', 'lcg', 'quad', 'cubic',
                'per2', 'per3', 'per4', 'per5', 'per6', 'per7']:
        deg = family_degree(fam)
        tot = space(fam, deg, mod, True)
        secs = tot * dt / workers
        print("  %-9s  %-17d %-17d %s" % (fam, mod ** deg, tot, human(secs)))
    print()
    print("  the quotient column is what actually runs.  Anything over about a")
    print("  day there is where a GPU or a different algorithm earns its keep.")
    return 0


def human(s):
    if s < 90:
        return "%.0f seconds" % s
    if s < 5400:
        return "%.1f minutes" % (s / 60)
    if s < 172800:
        return "%.1f hours" % (s / 3600)
    return "%.1f days" % (s / 86400)


# ----------------------------------------------------------- null / search --
_W = {}


def _init(mode, scorer):
    _W['mode'] = mode
    _W['scorer'] = scorer
    build()


def _null_chunk(arg):
    seed, count = arg
    mode, scorer = _W['mode'], _W['scorer']
    mod = modulus(mode)
    r = Rng(seed)
    best = 0
    hist = [0] * 64
    n = MAXL
    for _ in range(count):
        k = [r.rint(mod) for _ in range(n)]
        s = strip_and_score(k, mode, scorer)
        if s > best:
            best = s
        if s < 64:
            hist[s] += 1
    return best, hist


def _search_chunk(arg):
    lo, hi, fam, deg, quot = arg
    mode, scorer = _W['mode'], _W['scorer']
    mod = modulus(mode)
    n = MAXL
    best, bestidx = -1, -1
    for idx in range(lo, hi):
        p = expand(idx, fam, deg, mod, quot)
        k = keystream(p, fam, deg, mod, n)
        s = strip_and_score(k, mode, scorer)
        if s > best:
            best, bestidx = s, idx
    return best, bestidx


def parmap(fn, items, workers, mode, scorer):
    if workers <= 1 or len(items) == 1:
        _init(mode, scorer)
        return [fn(x) for x in items]
    import multiprocessing as mp
    with mp.Pool(workers, initializer=_init, initargs=(mode, scorer)) as pool:
        return pool.map(fn, items, chunksize=1)


def collect_null(mode, scorer, workers, nkeys, seed):
    per = max(1, nkeys // (workers * 4))
    items = []
    left = nkeys
    i = 0
    while left > 0:
        c = min(per, left)
        items.append((seed * 7919 + i, c))
        left -= c
        i += 1
    res = parmap(_null_chunk, items, workers, mode, scorer)
    best = max(x[0] for x in res)
    hist = [0] * 64
    for _, h in res:
        for j in range(64):
            hist[j] += h[j]
    return best, hist, sum(hist)


# --------------------------------------------------- the size matched null --
# THE MISTAKE THIS REPLACES
#   Version 1 printed "best of 200 000 random keystreams is 6 to 7" beside the
#   result of a search over 47 458 321 candidates.  Those are not comparable.
#   The maximum of 47 million draws is far above the maximum of 200 thousand,
#   so a search can print 9 against that 7 and be pure noise.  It did.
#
#   This is the Report 14 failure mode again, in my own tool: a real number
#   compared against a null of the wrong size.  The threshold must be the
#   expected maximum over a set the SIZE OF THE SEARCH, not over the sample
#   that was convenient to draw.

def tail_model(hist, N):
    """Return p_ge(s), measured where there is data and extrapolated above it
    with a geometric tail fitted to the last bins that have enough counts."""
    surv = [sum(hist[s:]) for s in range(64)]
    direct = [s for s in range(64) if surv[s] >= 20]
    smax = max(direct) if direct else 0
    fit = [s for s in direct if s >= max(1, smax - 4)]
    if len(fit) >= 2:
        n = len(fit)
        sx = sum(fit)
        sy = sum(math.log(surv[s] / float(N)) for s in fit)
        sxx = sum(s * s for s in fit)
        sxy = sum(s * math.log(surv[s] / float(N)) for s in fit)
        b = (n * sxy - sx * sy) / (n * sxx - sx * sx)
        a = (sy - b * sx) / n
    else:
        a, b = 0.0, -2.0

    def p_ge(s):
        if s <= smax:
            return surv[s] / float(N)
        return math.exp(a + b * s)
    return p_ge, smax, math.exp(-b)


def threshold_for(p_ge, space, alpha=0.05):
    """smallest score whose expected count in `space` draws is at or below alpha"""
    for s in range(1, 400):
        if p_ge(s) * space <= alpha:
            return s
    return 400


def report_calibration(p_ge, smax, ratio, space, best, label):
    print("  null calibration, %s" % label)
    print("    measured directly up to score %d, geometric tail above it,"
          " decay %.1fx per point" % (smax, ratio))
    print("    score   expected count among %d candidates" % space)
    lo = max(1, best - 3)
    for s in range(lo, best + 4):
        e = p_ge(s) * space
        mark = "   <-- observed best" if s == best else ""
        print("      %3d   %-16s%s"
              % (s, ("%.3g" % e) if e >= 0.001 else "%.1e" % e, mark))
    thr = threshold_for(p_ge, space)
    exp_at_best = p_ge(best) * space
    print("    a search this size needs to BEAT %d for an expected count under 0.05" % (thr - 1))
    print("    the observed %d has expected count %.4g  ->  %s"
          % (best, exp_at_best,
             "NOISE" if exp_at_best > 0.05 else "WORTH A LOOK"))
    return thr


def run_null(mode, nkeys, seed, scorer, workers, space=None):
    t0 = time.time()
    best, hist, N = collect_null(mode, scorer, workers, nkeys, seed)
    p_ge, smax, ratio = tail_model(hist, N)
    run = 0
    p999 = 0
    for j in range(64):
        run += hist[j]
        if run < 0.999 * N:
            p999 = j
    print("null : %d random keys, max score %d, 99.9 percentile %d   [%.0f s]"
          % (N, best, p999, time.time() - t0))
    print("  survival function")
    for s in range(1, 64):
        if sum(hist[s:]) == 0:
            break
        print("    P( score >= %2d ) = %-10d / %d = %.3e"
              % (s, sum(hist[s:]), N, sum(hist[s:]) / float(N)))
    print("  geometric tail above score %d, decay %.1fx per point" % (smax, ratio))
    for sp, nm in ((571787, 'a 571 787 search'), (47458321, 'a 47 458 321 search'),
                   (3939040643, 'a 3 939 040 643 search')):
        print("    %-24s expect to BEAT %d" % (nm, threshold_for(p_ge, sp) - 1))
    return 0


def run_search(mode, fam, scorer, workers, quot=True):
    deg = family_degree(fam)
    mod = modulus(mode)
    total = space(fam, deg, mod, quot)
    full = mod ** deg
    print("family %s, %s scorer" % (fam, "ngram" if scorer else "cycling"))
    if quot:
        print("  %d candidates after the shift quotient, from %d   (%dx saved,"
              " p [ %d ] held at 0)" % (total, full, mod, fixslot(fam)))
    else:
        print("  %d candidates, quotient DISABLED" % total)
    nchunk = workers * 8 if total > workers * 8 else 1
    step = (total + nchunk - 1) // nchunk
    items = []
    lo = 0
    while lo < total:
        items.append((lo, min(lo + step, total), fam, deg, quot))
        lo += step
    t0 = time.time()
    res = parmap(_search_chunk, items, workers, mode, scorer)
    best, bestidx = -1, -1
    for b, bi in res:
        if b > best:
            best, bestidx = b, bi
    p = expand(bestidx, fam, deg, mod, quot)
    el = time.time() - t0
    print("family %s : best score %d   [%.0f s]" % (fam, best, el))
    print("  parameters %s   (index %d)" % (p, bestidx))
    print("  the whole orbit p + c scores the same, so this stands for %d keystreams" % mod)

    # size matched null, drawn now rather than quoted from a smaller run.
    # 400 000 keys costs a couple of seconds against searches that cost minutes.
    nk = 400000
    print("  drawing a size matched null, %d random keystreams ..." % nk)
    _, hist, N = collect_null(mode, scorer, workers, nk, 20250817)
    p_ge, smax, ratio = tail_model(hist, N)
    report_calibration(p_ge, smax, ratio, total, best,
                       "%d random keystreams, same mode and scorer" % N)
    print("  for scale, a real keystream on a repeating source scores 138 to 750")
    return 0


# ----------------------------------------------------------------- main -----
USAGE = """eye_cycle.py  -  structural keystream scorer, pure standard library

  python eye_cycle.py selftest
  python eye_cycle.py speed [--ngram] [--workers N]
  python eye_cycle.py null   <mode> <nkeys> [seed] [--ngram] [--workers N]
  python eye_cycle.py search <mode> <family> [--ngram] [--workers N]

  mode     mult  addd  addb
  family   const lin lcg quad cubic per2 per3 per4 per5 per6
  --ngram  use the repeated 3 gram scorer instead of the cycling scorer
  --full   disable the shift quotient and search all mod^deg keystreams.
           Only for auditing.  The quotient is proven and checked in selftest.
"""


def main(argv):
    build()
    if len(argv) < 2:
        print(USAGE)
        return 2
    # argument parsing, done by walking the list so that a positional value
    # that happens to equal the worker count is not eaten by mistake
    scorer = 0
    quot = True
    workers = os.cpu_count() or 1
    pos = []
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == '--ngram':
            scorer = 1
        elif a == '--full':
            quot = False
        elif a == '--workers':
            workers = int(argv[i + 1])
            i += 1
        elif a.startswith('--'):
            print("unknown option %s" % a)
            return 2
        else:
            pos.append(a)
        i += 1
    if not pos:
        print(USAGE)
        return 2
    cmd = pos[0]

    if cmd == 'selftest':
        return selftest()
    if cmd == 'speed':
        mode = MODNAME.get(pos[1], M_MULT) if len(pos) > 1 else M_MULT
        return speed(mode, scorer, workers)
    if cmd == 'null':
        mode = MODNAME[pos[1]]
        nkeys = int(pos[2])
        seed = int(pos[3]) if len(pos) > 3 else 12345
        return run_null(mode, nkeys, seed, scorer, workers)
    if cmd == 'search':
        mode = MODNAME[pos[1]]
        return run_search(mode, pos[2], scorer, workers, quot)
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
