#!/usr/bin/env python
# ============================================================================
# eye_share.py  -  HOW MANY MESSAGES CARRY EACH PASSAGE
#
#   python eye_share.py version
#   python eye_share.py selftest
#   python eye_share.py speed --threads 32 --draws 900
#   python eye_share.py run   --threads 32 --draws 900
#   python eye_share.py report
#
# WHAT REPORT 63 LEFT
#   Every one of 121 live families predicted between 4 . 5 and 14 . 6 relations
#   against the corpus's 24 , and the only cell in 360 that reached 24 was dead
#   by three hundred orders of magnitude .  The deficit was universal and it was
#   the whole remaining problem.
#
# THE MISREADING BEING CORRECTED
#   Report 62 called the repeat curve and the relation count coupled - more
#   repeated letters make more repeated symbols .  That is true , but it is a
#   coupling through the ALPHABET .  It is not a coupling through the AMOUNT of
#   sharing , because the repeat curve is a WITHIN message statistic and sharing
#   between two messages adds no repeat inside either of them.
#
#   So more sharing can buy relations for free .  The question is what form it
#   can take , and the corpus answers that itself :
#
#     439 of the 1036 positions already sit inside a known relation , and the
#     rest is fragmented .  Only FOUR TO SIX further disjoint passages fit .
#
#   So more sharing cannot mean more passages .  It can only mean the same
#   passages appearing in MORE MESSAGES , which multiplies relations
#   combinatorially - a passage in four messages yields six pairs from four
#   placements where a passage in two yields one from two.
#
# WHAT THE PROTOTYPE SHOWED
#     extra placements     repeat curve bins 1-5        relations
#            0             102 107 110  94  72             5.5
#            6             113 104 117  86  74            13.6
#           12             110 110 120 106  77            19.9
#           18             118 106 119  94  76            31.8
#        corpus            115 101 104  88  74            24
#
#   The count passes through 24 between twelve and eighteen further placements
#   and the curve barely moves .  And the corpus has room for exactly SIXTEEN .
#   That the amount needed and the amount that fits land in the same range is
#   not something the model was fitted to do.
#
# WHY IT IS BUILT THE WAY IT IS
#   Rule 8 a   each family's own draws are its null
#   Rule 9 a   the score carries its minus log sigma
#   Rule 11    the FULL GRID is printed , never a marginal
#   Rule 12    every command prints its build
#   Rule 14    a grid is audited for cells that collapse onto the same model ,
#              because Report 63's ranked table was led by four rows that were
#              one family printed four times
#
#   And the gate that matters here : plant a KNOWN number of extra placements
#   and print what the readout recovers .  A grid that cannot measure the
#   quantity it was built to measure says nothing about the corpus.
# ============================================================================

import sys, os, math, random, collections, time

VERSION = 'eye_share build 1 , 21 August 2026'
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
M = [RAW[n] for n in ORDER]
LENS = [len(m) for m in M]
NSYM = 83
PRE = [25, 25, 25, 6, 6, 6, 21, 21, 21]

GEOM = [(6, 68, 7, 71, 34), (1, 33, 1, 63, 33), (6, 57, 8, 58, 33),
        (7, 34, 8, 33, 33), (7, 68, 8, 66, 33), (2, 39, 2, 74, 32),
        (1, 29, 2, 34, 28), (4, 63, 6, 72, 28), (4, 63, 7, 75, 28),
        (4, 63, 8, 73, 28), (1, 60, 2, 70, 27), (0, 33, 0, 61, 26),
        (0, 53, 2, 65, 25), (1, 32, 2, 72, 25), (1, 62, 2, 37, 25),
        (1, 55, 4, 86, 23), (0, 28, 1, 28, 22), (0, 29, 2, 34, 21),
        (0, 58, 1, 60, 20), (6, 46, 7, 48, 19), (0, 32, 1, 62, 18),
        (0, 60, 1, 32, 18), (0, 32, 2, 72, 18), (0, 60, 2, 37, 18)]
LSPAN = sorted(x[4] for x in GEOM)

BIN = 10
NBIN = 13
DMAX = 130
PAIRS = [0] * NBIN
for _n in LENS:
    for _d in range(1, _n):
        if _d <= DMAX:
            PAIRS[(_d - 1) // BIN] += _n - _d


def curve(msgs):
    out = [0] * NBIN
    for row in msgs:
        n = len(row)
        for i in range(n):
            ri = row[i]
            for j in range(i + 1, min(n, i + DMAX + 1)):
                if ri == row[j]:
                    out[(j - i - 1) // BIN] += 1
    return out


# ---------------------------------------------------------------- the detector
def prevtab(s):
    last = {}
    pv = [-1] * len(s)
    for p in range(len(s)):
        pv[p] = last.get(s[p], -1)
        last[s[p]] = p
    return pv


def maximal(msgs, minrep=3, minlen=6):
    PV = [prevtab(m) for m in msgs]
    out = []
    n = len(msgs)
    for a in range(n):
        La = len(msgs[a]); pa = PV[a]
        for b in range(a, n):
            Lb = len(msgs[b]); pb = PV[b]
            for i in range(La):
                for j in range((i + 1) if a == b else 0, Lb):
                    L = 0; rep = 0
                    while i + L < La and j + L < Lb:
                        qa = pa[i + L]; x = (i + L - qa) if qa >= i else 0
                        qb = pb[j + L]; y = (j + L - qb) if qb >= j else 0
                        if x != y:
                            break
                        if x:
                            rep += 1
                        L += 1
                    if L >= minlen and rep >= minrep:
                        out.append((rep, L, a, i, b, j))
    out.sort(key=lambda t: -t[1])
    keep = []
    for k, L, a, i, b, j in out:
        if any(a == x[2] and b == x[4] and i >= x[3] and i + L <= x[3] + x[1]
               and j - i == x[5] - x[3] for x in keep):
            continue
        keep.append((k, L, a, i, b, j))
    return keep


def relations(msgs):
    best = {}
    for k, L, a, i, b, j in maximal(msgs, 3, 6):
        if a < 9 and b < 9 and i < PRE[a] and j < PRE[b]:
            continue
        key = (a, b, j - i)
        if key not in best or L > best[key][1]:
            best[key] = (k, L, a, i, b, j)
    return sorted(best.values(), key=lambda t: -t[1])


# ------------------------------------------------------------------ planting
class DSU(object):
    def __init__(self):
        self.p = {}

    def find(self, x):
        p = self.p
        r = x
        while p.get(r, r) != r:
            r = p[r]
        while p.get(x, x) != x:
            nxt = p[x]; p[x] = r; x = nxt
        return r

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


def extra_spans(r, n, cover=None):
    """
    n further shared passages the detector may or may not find .

    the first build placed these uniformly at random and it PERCOLATED - union
    find is transitive , so thirty six random spans chained through each other
    and collapsed the corpus into a handful of plaintext classes , driving the
    first repeat bin from 106 to 2909 .  that is not more sharing , it is a
    destroyed plaintext .

    so a placement may not touch a position any other placement already uses .
    every extra class then holds exactly two members , which is the most
    conservative form of more sharing , and it runs out of room honestly when
    the corpus is full.
    """
    used = set(cover) if cover else set()
    out = []
    for _ in range(n):
        placed = False
        for _try in range(300):
            L = r.choice(LSPAN)
            a = r.randrange(9); b = r.randrange(9)
            if LENS[a] <= L + 2 or LENS[b] <= L + 2:
                continue
            i = r.randrange(LENS[a] - L)
            j = r.randrange(LENS[b] - L)
            if a == b and abs(i - j) < L + 2:
                continue
            pa = [(a, i + t) for t in range(L)]
            pb = [(b, j + t) for t in range(L)]
            if any(q in used for q in pa) or any(q in used for q in pb):
                continue
            used.update(pa); used.update(pb)
            out.append((a, i, b, j, L))
            placed = True
            break
        if not placed:
            break
    return out


GEOMCOVER = set()
for _a, _i, _b, _j, _L in GEOM:
    for _t in range(_L):
        GEOMCOVER.add((_a, _i + _t)); GEOMCOVER.add((_b, _j + _t))


def multiplicity(r, n):
    """
    n further PLACEMENTS of passages the corpus already carries , in messages
    that do not yet hold them .

    the corpus has room for only four to six further disjoint passages - 439 of
    its 1036 positions are already inside a known relation and the rest is too
    fragmented .  so more sharing cannot mean more passages .  it can mean the
    same passages appearing in MORE messages , and that multiplies relations
    combinatorially : a passage in four messages yields six pairs from four
    placements , where a passage in two yields one from two.

    a placement goes into a message that does not already carry the passage .
    the first build allowed it to land in the same message and that moved the
    first repeat bin by twenty two percent , because a passage repeated inside
    ONE message does add repeats inside that message .  the corpus already
    carries three such , at lags 28 , 30 and 35 , and they are in GEOM .  this
    parameter is cross message sharing only , which is the thing that is free.
    """
    used = set(GEOMCOVER)
    out = []
    idx = list(range(len(GEOM)))
    r.shuffle(idx)
    for q in idx:
        if len(out) >= n:
            break
        a, i, b, j, L = GEOM[q]
        for _try in range(200):
            c = r.randrange(9)
            if c == a or c == b:
                continue          # a message that does not already carry it
            if LENS[c] <= L + 2:
                continue
            k = r.randrange(LENS[c] - L)
            pc = [(c, k + t) for t in range(L)]
            if any(x in used for x in pc):
                continue
            used.update(pc)
            out.append((a, i, c, k, L))
            break
    return out


def plant_plain(r, PA, extra=0, mult=0):
    d = DSU()
    for a, i, b, j, L in (GEOM + extra_spans(r, extra, GEOMCOVER)
                          + multiplicity(r, mult)):
        for t in range(L):
            d.union((a, i + t), (b, j + t))
    cls = {}
    for m in range(9):
        for p in range(LENS[m]):
            cls[(m, p)] = d.find((m, p))
    nb = collections.defaultdict(set)
    for m in range(9):
        for p in range(LENS[m] - 1):
            x = cls[(m, p)]; y = cls[(m, p + 1)]
            if x != y:
                nb[x].add(y); nb[y].add(x)
    keys = list(set(cls.values()))
    r.shuffle(keys)
    val = {}
    for k in keys:
        bad = set()
        for q in nb[k]:
            if q in val:
                bad.add(val[q])
        ch = [c for c in range(PA) if c not in bad]
        val[k] = r.choice(ch) if ch else r.randrange(PA)
    return [[val[cls[(m, p)]] for p in range(LENS[m])] for m in range(9)]


def homophones(r, PA, rule):
    sym = list(range(NSYM))
    r.shuffle(sym)
    if rule == 'bij':
        return [[sym[i]] for i in range(PA)]
    sets = [[] for _ in range(PA)]
    for i, s in enumerate(sym):
        sets[i % PA].append(s)
    return sets


def encrypt(plain, r, PA, rule, sched, W=0, target=30):
    out = []
    trig = None
    if sched == 'con':
        k = max(1, int(round(PA / float(target))))
        trig = set(r.sample(range(PA), k))
    for m in range(9):
        pl = plain[m]
        row = []
        sets = homophones(r, PA, rule)
        cnt = [0] * PA
        ph = r.randrange(W) if (sched == 'pos' and W) else 0
        for p in range(len(pl)):
            if p:
                if sched == 'pos':
                    cut = ((p - ph) % W == 0)
                elif sched == 'con':
                    cut = (pl[p] in trig)
                else:
                    cut = False
                if cut:
                    sets = homophones(r, PA, rule)
                    cnt = [0] * PA
            L = pl[p]; st = sets[L]; hh = len(st)
            if hh == 1:
                e = 0
            elif rule == 'cyc':
                e = cnt[L] % hh
            elif rule == 'ctx1':
                e = (pl[p - 1] if p else 7) % hh
            elif rule == 'ctx2':
                e = ((pl[p - 1] if p else 7) * 31 +
                     (pl[p - 2] if p > 1 else 3)) % hh
            else:
                e = r.randrange(hh)
            cnt[L] += 1
            row.append(st[e])
        out.append(row)
    return out


def draw(r, PA, rule, sched, W=0, target=30, extra=0, mult=0):
    return encrypt(plant_plain(r, PA, extra, mult), r, PA, rule, sched,
                   W=W, target=target)


# ============================================================================
#  FEATURES
# ============================================================================
COVER_AT = 40


def regular(msgs):
    pooled = collections.Counter()
    evm = 0.0
    cov = 0.0
    gm = []
    for row in msgs:
        n = len(row)
        pooled.update(row)
        c = collections.Counter(row)
        evm += sum(v * v for v in c.values()) / float(n * n)
        cov += len(set(row[:COVER_AT]))
        last = {}
        for p, s in enumerate(row):
            if s in last:
                gm.append(p - last[s])
            last[s] = p
    N = float(sum(pooled.values()))
    even = sum(v * v for v in pooled.values()) / (N * N)
    mu = sum(gm) / float(len(gm))
    var = sum((x - mu) * (x - mu) for x in gm) / float(len(gm))
    return [even * 1000.0, evm / 9.0 * 1000.0, var / (mu * mu), cov / 9.0]


NREG = 4
NDIM = NBIN + NREG + 2


def features(msgs):
    rel = relations(msgs)
    ml = (sum(x[1] for x in rel) / float(len(rel))) if rel else 0.0
    return curve(msgs) + regular(msgs) + [float(len(rel)), ml]


# ============================================================================
#  THE GRID
# ============================================================================
MULT_GRID = [0, 2, 4, 6, 8, 10, 12, 14, 16]
PA_GRID = [16, 20, 24, 28, 34]
RULES = ['ctx1', 'ctx2']
RULENAME = {'ctx1': 'keyed on the last letter', 'ctx2': 'keyed on the last two'}
SCHED = [('con', 30), ('con', 50), ('pos', 28), ('pos', 35)]
HELD = 60
SDFLOOR = 0.5


def cells():
    out = []
    for mult in MULT_GRID:
        for PA in PA_GRID:
            for rule in RULES:
                for sc, x in SCHED:
                    out.append((mult, PA, rule, sc, x))
    return out


def schedname(sc, x):
    return ('window %d' % x) if sc == 'pos' else ('content %d' % x)


def label(c):
    mult, PA, rule, sc, x = c
    return '%2d extra  PA %-3d %-22s %s' % (mult, PA, RULENAME[rule],
                                            schedname(sc, x))


def score(vec, mu, sd):
    t = 0.0
    for k in range(NDIM):
        s = sd[k]
        z = (vec[k] - mu[k]) / s
        t += -0.5 * z * z - math.log(s)
    return t - 0.5 * NDIM * math.log(2.0 * math.pi)


def cell_one(job):
    c, draws, seed = job
    mult, PA, rule, sc, x = c
    r = random.Random(seed)
    W = x if sc == 'pos' else 0
    T = x if sc == 'con' else 30
    vs = []
    for _ in range(draws):
        vs.append(features(draw(r, PA, rule, sc, W=W, target=T, mult=mult)))
    mu = [0.0] * NDIM
    sd = [0.0] * NDIM
    for k in range(NDIM):
        col = [v[k] for v in vs]
        m0 = sum(col) / float(len(col))
        var = sum((y - m0) * (y - m0) for y in col) / float(len(col))
        mu[k] = m0
        sd[k] = max(math.sqrt(var), SDFLOOR)
    obs = features(M)
    lobs = score(obs, mu, sd)
    own = sorted(score(v, mu, sd) for v in vs)
    le = sum(1 for y in own if y <= lobs)
    return {'c': list(c), 'mu': [round(y, 4) for y in mu],
            'sd': [round(y, 4) for y in sd], 'lobs': lobs,
            'p': (le + 1.0) / (len(own) + 1.0),
            'floor': sum(1 for y in sd if y <= SDFLOOR + 1e-9),
            'held': vs[:HELD]}


def runcells(jobs, threads, path):
    import json
    done = []
    t0 = time.time()
    fh = open(path, 'w')
    if threads > 1:
        import multiprocessing as mp
        pool = mp.Pool(threads)
        it = pool.imap_unordered(cell_one, jobs, chunksize=1)
    else:
        it = (cell_one(j) for j in jobs)
    for n, rec in enumerate(it, 1):
        done.append(rec)
        fh.write(json.dumps(rec)); fh.write('\n')
        if n % 5 == 0 or n == len(jobs):
            fh.flush()
            el = time.time() - t0
            sys.stderr.write('  cell %d / %d   %.0f s elapsed , %.0f s left\n'
                             % (n, len(jobs), el,
                                el * (len(jobs) - n) / max(n, 1)))
            sys.stderr.flush()
    if threads > 1:
        pool.close(); pool.join()
    fh.close()
    return done


def loadcells(path):
    import json
    out = []
    bad = 0
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            bad += 1
    if bad:
        sys.stderr.write('  dropped %d incomplete cell\n' % bad)
    return out


# ============================================================================
#  COMMANDS
# ============================================================================
def cmd_selftest():
    bad = 0

    def chk(name, got, exp, tol=0.0):
        ok = (abs(got - exp) <= tol) if isinstance(exp, float) else (got == exp)
        print('  %-56s got %-14s expected %-14s %s'
              % (name, repr(got), repr(exp), 'ok' if ok else 'BAD'))
        return 0 if ok else 1

    print('the detector and the observable still say what they said')
    bad += chk('relations recovered from the raw corpus',
               len(relations(M)), 24)
    bad += chk('the corpus curve', curve(M),
               [115, 101, 104, 88, 74, 64, 47, 45, 26, 18, 10, 7, 0])
    bad += chk('the feature vector width', len(features(M)), NDIM)
    bad += chk('relations and mean length are the last two',
               [round(x, 3) for x in features(M)[-2:]], [24.0, 25.625])

    print('')
    print('THE ROOM THE CORPUS HAS , which is the whole argument')
    bad += chk('positions already inside a known relation', len(GEOMCOVER), 439)
    bad += chk('positions in the corpus', sum(LENS), 1036)
    got = [len(extra_spans(random.Random(700 + t), 100, GEOMCOVER))
           for t in range(6)]
    bad += chk('further DISJOINT passages that fit , asking for 100',
               max(got) <= 8, True)
    print('     ( %s in six tries - the corpus is nearly full )' % got)
    gotm = [len(multiplicity(random.Random(800 + t), 40)) for t in range(6)]
    bad += chk('further PLACEMENTS of existing passages that fit',
               14 <= max(gotm) <= 20, True)
    print('     ( %s in six tries )' % gotm)

    print('')
    print('the extra sharing is what it claims to be')
    r = random.Random(5)
    sp = multiplicity(r, 12)
    bad += chk('twelve placements requested and placed', len(sp), 12)
    bad += chk('each reuses a passage the corpus already carries',
               all(any(a == q[0] and i == q[1] and L == q[4] for q in GEOM)
                   for a, i, c, k, L in sp), True)
    seen = set()
    okd = True
    for a, i, c, k, L in sp:
        for t in range(L):
            if (c, k + t) in seen or (c, k + t) in GEOMCOVER:
                okd = False
            seen.add((c, k + t))
    bad += chk('and lands where nothing else does', okd, True)
    pl = plant_plain(random.Random(9), 20, 0, 12)
    bad += chk('the planted plaintext honours every placement',
               all(pl[a][i + t] == pl[c][k + t]
                   for a, i, c, k, L in multiplicity(random.Random(9), 12)
                   for t in range(L)) if True else True, True)

    print('')
    print('MORE SHARING MUST BUY RELATIONS AND NOT MOVE THE CURVE')
    print('  the mechanism forbids anything else - sharing between two')
    print('  messages adds no repeat inside either of them.')
    lo = hi = 0.0
    c0 = [0.0] * 3
    c1 = [0.0] * 3
    for t in range(4):
        a = draw(random.Random(600 + t), 20, 'ctx1', 'con', target=30, mult=0)
        b = draw(random.Random(600 + t), 20, 'ctx1', 'con', target=30, mult=14)
        lo += len(relations(a)); hi += len(relations(b))
        ca = curve(a); cb = curve(b)
        for k in range(3):
            c0[k] += ca[k]; c1[k] += cb[k]
    bad += chk('fourteen placements raise the relation count',
               hi > lo * 1.7, True)
    print('     ( %.1f relations became %.1f )' % (lo / 4.0, hi / 4.0))
    bad += chk('and leave every early repeat bin alone',
               all(abs(c0[k] - c1[k]) / max(c0[k], 1) < 0.12
                   for k in range(3)), True)
    print('     ( bins 1 to 3 : %s became %s )'
          % ([round(x / 4) for x in c0], [round(x / 4) for x in c1]))
    bad += chk('no placement lands in a message already carrying it',
               all(c not in (a, b0) for a, i, c, k, L in
                   [(q[0], q[1], q[2], q[3], q[4])
                    for q in multiplicity(random.Random(77), 16)]
                   for b0 in [next(z[2] for z in GEOM
                                   if z[0] == a and z[1] == i)]), True)

    print('')
    print('rule 14 - no two cells in this grid are the same model')
    bad += chk('cells', len(cells()),
               len(MULT_GRID) * len(PA_GRID) * len(RULES) * len(SCHED))
    bad += chk('and every one differs in at least one parameter',
               len(set(cells())), len(cells()))

    print('')
    print('the score cannot be won by being vague')
    obs = features(M)
    mu = [float(y) for y in obs]
    bad += chk('a sharp family that fits beats a vague one that fits',
               score(obs, mu, [2.0] * NDIM) > score(obs, mu, [20.0] * NDIM),
               True)
    off = [y + 6 for y in obs]
    bad += chk('a family that misses by 3 sigma loses to one that does not',
               score(obs, mu, [2.0] * NDIM) > score(off, mu, [2.0] * NDIM),
               True)
    bad += chk('a vague family beats a sharp one that is badly wrong',
               score(off, mu, [20.0] * NDIM) > score(off, mu, [2.0] * NDIM),
               True)

    print('')
    print('SELFTEST %s   %d bad' % ('PASSED' if bad == 0 else 'FAILED', bad))
    return bad


def cmd_speed(threads, draws):
    print('timing the real simulation loop on this machine')
    print('')
    t0 = time.time()
    for i in range(6):
        features(draw(random.Random(9000 + i), 20, 'ctx1', 'con',
                      target=30, mult=8))
    per = (time.time() - t0) / 6.0
    print('  one corpus with the relation detector    %.4f s' % per)
    eff = 1.0
    if threads > 1:
        import multiprocessing as mp
        probe = [((8, 20, 'ctx1', 'con', 30), 6, 9500 + i)
                 for i in range(threads)]
        pool = mp.Pool(threads)
        t0 = time.time()
        for _ in pool.imap_unordered(cell_one, probe, chunksize=1):
            pass
        wall = time.time() - t0
        pool.close(); pool.join()
        ideal = len(probe) * 6 * per / float(threads)
        eff = ideal / wall if wall > 0 else 1.0
        print('  %d cells of 6 draws on %d workers took %.1f s against %.1f s'
              % (len(probe), threads, wall, ideal))
        print('  if the threads scaled perfectly .  EFFICIENCY %.2f' % eff)
        if eff < 0.05:
            eff = 0.05
    nc = len(cells())
    print('')
    print('  %-8s %-12s %-14s %s' % ('draws', 'corpora', 'core seconds',
                                     'wall clock at %d threads' % threads))
    for n in (100, 300, 600, 900, 1500):
        tot = nc * n * per
        w = tot / max(threads, 1) / eff
        print('  %-8d %-12d %-14.0f %s'
              % (n, nc * n, tot,
                 ('%.0f s' % w) if w < 120 else ('%.1f min' % (w / 60.0))
                 if w < 7200 else ('%.1f hours' % (w / 3600.0))))
    w = nc * draws * per / max(threads, 1) / eff
    print('')
    print('  --draws %d over %d cells is %d corpora , about %s'
          % (draws, nc, nc * draws,
             ('%.0f s' % w) if w < 120 else ('%.1f min' % (w / 60.0))
             if w < 7200 else ('%.1f hours' % (w / 3600.0))))


def cmd_run(threads, draws, path):
    cs = cells()
    print('simulating %d cells of %d draws , %d corpora , on %d threads'
          % (len(cs), draws, len(cs) * draws, threads))
    jobs = [(c, draws, 21000 + 41 * i) for i, c in enumerate(cs)]
    runcells(jobs, threads, path)
    cmd_report(path)


def cmd_report(path):
    recs = loadcells(path)
    if not recs:
        print('no cells in %s' % path)
        return
    for r0 in recs:
        r0['c'] = tuple(r0['c'])
    obs = features(M)
    best = max(r0['lobs'] for r0 in recs)
    recs.sort(key=lambda r0: -r0['lobs'])
    by = dict((r0['c'], r0) for r0 in recs)

    def sup(r0):
        return math.exp(max(r0['lobs'] - best, -700.0))

    def ss(v):
        if v > 0.999:
            return '1 . 00'
        if v > 1e-12:
            return '1 in %.0f' % (1.0 / v)
        return 'below 1e12'

    print('')
    print('=' * 78)
    print('THE CORPUS AGAINST %d FAMILIES' % len(recs))
    print('=' * 78)
    print('  observed curve   %s   total %d'
          % (' '.join('%3d' % y for y in obs[:NBIN]), sum(obs[:NBIN])))
    print('  relations        %.0f , mean length %.2f' % (obs[-2], obs[-1]))
    print('  sigma floored in %d component of %d'
          % (sum(r0['floor'] for r0 in recs), len(recs) * NDIM))
    print('')
    print('  %-48s %-12s %-8s %s'
          % ('family', 'support', 'fit p', 'relations predicted'))
    print('')
    for r0 in recs[:16]:
        print('  %-48s %-12s %-8.4f %.1f'
              % (label(r0['c']), ss(sup(r0)), r0['p'], r0['mu'][-2]))
    print('  . . .')
    for r0 in recs[-3:]:
        print('  %-48s %-12s %-8.4f %.1f'
              % (label(r0['c']), ss(sup(r0)), r0['p'], r0['mu'][-2]))

    print('')
    print('=' * 78)
    print('THE FULL GRID , PRINTED RATHER THAN MARGINALISED  ( rule 11 )')
    print('=' * 78)
    for rule in RULES:
        for sc, x in SCHED:
            print('')
            print('  %s , %s' % (RULENAME[rule], schedname(sc, x)))
            print('  %-6s %s' % ('PA', ' '.join('%11s' % ('%d extra' % m)
                                                for m in MULT_GRID)))
            for PA in PA_GRID:
                row = []
                for m in MULT_GRID:
                    r0 = by.get((m, PA, rule, sc, x))
                    row.append('%11s' % (ss(sup(r0)).replace(' ', '')
                                         if r0 else '-'))
                print('  %-6d %s' % (PA, ' '.join(row)))

    print('')
    print('=' * 78)
    print('WHAT REJECTS EACH FAMILY , in sigma of its own spread')
    print('=' * 78)
    pick = [0, 1, 2, NBIN, NBIN + 1, NBIN + 2, NBIN + 3, NDIM - 2, NDIM - 1]
    names = ['d1-10', 'd11-20', 'd21-30', 'even', 'evenm', 'gapvar', 'cover',
             'reln', 'rlen']
    print('  %-48s %s' % ('family', ' '.join('%7s' % n for n in names)))
    seen = set()
    for r0 in recs:
        if r0['c'][0] in seen:
            continue
        seen.add(r0['c'][0])
        z = [(obs[k] - r0['mu'][k]) / r0['sd'][k] for k in pick]
        print('  %-48s %s' % (label(r0['c']),
                              ' '.join('%+7.1f' % y for y in z)))
    print('')
    print('  ( the best cell at each number of extra placements )')

    print('')
    print('=' * 78)
    print('THE GATE - plant a KNOWN number of extra placements')
    print('=' * 78)
    print('  the grid was built to measure this quantity .  if it cannot')
    print('  recover a planted value it says nothing about the corpus.')
    print('')
    mus = [(r0['c'], r0['mu'], r0['sd']) for r0 in recs]

    def mmarg(v):
        sc0 = [(score(v, mu, sd), c) for c, mu, sd in mus]
        b = max(x[0] for x in sc0)
        t = {}
        for s0, c0 in sc0:
            t[c0[0]] = t.get(c0[0], 0.0) + math.exp(max(s0 - b, -700.0))
        tt = sum(t.values()) or 1.0
        return dict((k, v0 / tt) for k, v0 in t.items())

    print('  %-10s %-16s %-14s %s'
          % ('planted', 'recovered mean', 'true rank', 'top 3'))
    agg = {}
    for r0 in recs:
        if not r0.get('held'):
            continue
        m0 = r0['c'][0]
        for v in r0['held'][:10]:
            t = mmarg(v)
            pm = sum(k * q for k, q in t.items())
            order = sorted(t, key=lambda k: -t[k])
            a = agg.setdefault(m0, [[], []])
            a[0].append(pm)
            a[1].append(order.index(m0) + 1 if m0 in order else 99)
    for m0 in MULT_GRID:
        if m0 not in agg:
            continue
        pm, rk = agg[m0]
        pm.sort(); rk.sort()
        print('  %-10d %-16.1f %-14d %.0f %%'
              % (m0, pm[len(pm) // 2], rk[len(rk) // 2],
                 100.0 * sum(1 for y in rk if y <= 3) / len(rk)))
    t = mmarg(obs)
    pm = sum(k * q for k, q in t.items())
    print('')
    print('  THE CORPUS recovers %.1f extra placements' % pm)
    for k in sorted(t):
        if t[k] > 0.01:
            print('    %2d extra  %5.1f %%%s'
                  % (k, 100.0 * t[k], '  ' + '#' * int(50 * t[k])))
    print('')
    print('  the corpus has room for about sixteen further placements .  a')
    print('  recovered value near or above that means the model is asking for')
    print('  more sharing than the corpus can physically hold.')

    print('')
    print('=' * 78)
    print('THE GATE ON THE CELL')
    print('=' * 78)
    ranks = []
    for r0 in recs:
        if not r0.get('held'):
            continue
        for v in r0['held'][:10]:
            sc0 = sorted(((score(v, mu, sd), c) for c, mu, sd in mus),
                         reverse=True)
            for q, (s0, c0) in enumerate(sc0):
                if c0 == r0['c']:
                    ranks.append(q + 1)
                    break
    ranks.sort()
    if ranks:
        print('  %d planted corpora against all %d cells' % (len(ranks), len(recs)))
        print('  median rank of the true cell   %d of %d'
              % (ranks[len(ranks) // 2], len(recs)))
        print('  true cell in the top 10        %.1f %%'
              % (100.0 * sum(1 for y in ranks if y <= 10) / len(ranks)))
        print('  true cell ranked first         %.1f %%'
              % (100.0 * sum(1 for y in ranks if y == 1) / len(ranks)))


def main():
    a = sys.argv[1:]
    cmd = a[0] if a else 'selftest'
    print(VERSION)
    print('')

    def opt(name, dflt, cast=int):
        if name in a:
            return cast(a[a.index(name) + 1])
        return dflt

    if cmd == 'version':
        return
    if cmd == 'selftest':
        sys.exit(1 if cmd_selftest() else 0)
    elif cmd == 'speed':
        cmd_speed(opt('--threads', 32), opt('--draws', 900))
    elif cmd in ('run', 'verify', 'scan'):
        cmd_run(opt('--threads', 32), opt('--draws', 900),
                opt('--out', 'eye_share_cells.txt', str))
    elif cmd == 'report':
        cmd_report(opt('--out', 'eye_share_cells.txt', str))
    else:
        print('commands : version , selftest , speed , run , report')
        print('')
        print('  python eye_share.py version')
        print('  python eye_share.py selftest')
        print('  python eye_share.py speed --threads 32 --draws 900')
        print('  python eye_share.py run --threads 32 --draws 900')
        print('  python eye_share.py report')


if __name__ == '__main__':
    main()
