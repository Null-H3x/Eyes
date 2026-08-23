#!/usr/bin/env python
# ============================================================================
# eye_choice.py  -  HOW THE CIPHER CHOOSES AMONG HOMOPHONES
#
#   python eye_choice.py version
#   python eye_choice.py selftest
#   python eye_choice.py speed --threads 32 --draws 900
#   python eye_choice.py run   --threads 32 --draws 900
#   python eye_choice.py report
#
# WHAT REPORT 62 LEFT
#   Two observables pulling opposite ways under a bijection :
#
#     the repeat distance curve   demands a LARGE plaintext alphabet , because
#                                 repeated letters make repeated symbols
#     the relation count          demands a SMALL one , because a relation needs
#                                 repeated letters inside its span to match on
#
#   Homophones break the coupling - letter repeats stay common at 1 / PA while
#   symbol repeats fall to 1 / 83 - but only if the CHOICE among homophones is
#   reproducible from the plaintext .  A fresh random choice is not reproducible ,
#   so two messages carrying the same passage produce unrelated repeat patterns
#   and no relation forms .  A strict cycle is reproducible but was refuted at
#   1 in 3646288 because it forces consecutive uses of a letter apart and
#   crushes the first bin from 115 to 15 .
#
#   So the choice rule is the free variable , and this races five of them.
#
# THE PROTOTYPE THAT MOTIVATED IT
#   A choice keyed on the PRECEDING plaintext letter , with no schedule at all ,
#   produced **25 . 7 relations against the corpus's 24** - the first family in
#   this project to reproduce them .  It also drove the 21 to 30 bin to 72 above
#   a flat rate where the corpus sits at 10 above .  Adding a window of 35 put
#   that excess at exactly 10 and dropped the relations to 9 .
#
#   That trade off is the whole search , and neither end of it is the corpus.
#
# WHY IT IS BUILT THE WAY IT IS
#   Rule 9 a   the score is a Gaussian log likelihood carrying its minus log
#              sigma , so a family cannot win by being vague
#   Rule 8 a   each family's own draws are its null , so size is correct by
#              construction
#   Rule 11    the FULL GRID is printed , not a marginal .  Reports 60 and 61
#              quoted a marginal that was gated , passed , and was still wrong ,
#              because the planted corpora came from the same prior the
#              estimator assumed .  no marginal is quoted here at all
#   Rule 12    every command prints its build
#
#   And a gate on mechanism : plant each choice rule and print how often it
#   recovers itself .  A rule the grid cannot recognise cannot be refuted by the
#   corpus failing to look like it.
#
# THE EXPENSIVE PART
#   The relation count needs the relation detector , which costs about 0 . 55 s
#   per corpus against 0 . 004 s for everything else - a hundred times more .
#   That is the whole cost of this tool and it is unavoidable , because the
#   relation count is half the contradiction being tested.
# ============================================================================

import sys, os, math, random, collections, time

VERSION = 'eye_choice build 1 , 21 August 2026'
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

# the 24 relations of Report 59 , as ( a , i , b , j , L ) .  a simulated
# corpus carries the same sharing so the plaintext has the same class structure
GEOM = [(6, 68, 7, 71, 34), (1, 33, 1, 63, 33), (6, 57, 8, 58, 33),
        (7, 34, 8, 33, 33), (7, 68, 8, 66, 33), (2, 39, 2, 74, 32),
        (1, 29, 2, 34, 28), (4, 63, 6, 72, 28), (4, 63, 7, 75, 28),
        (4, 63, 8, 73, 28), (1, 60, 2, 70, 27), (0, 33, 0, 61, 26),
        (0, 53, 2, 65, 25), (1, 32, 2, 72, 25), (1, 62, 2, 37, 25),
        (1, 55, 4, 86, 23), (0, 28, 1, 28, 22), (0, 29, 2, 34, 21),
        (0, 58, 1, 60, 20), (6, 46, 7, 48, 19), (0, 32, 1, 62, 18),
        (0, 60, 1, 32, 18), (0, 32, 2, 72, 18), (0, 60, 2, 37, 18)]

BIN = 10
NBIN = 13                      # distances 1 to 130
DMAX = BIN * NBIN


def binof(d):
    if d < 1 or d > DMAX:
        return -1
    return (d - 1) // BIN


# how many within message position pairs land in each bin .  fixed by the
# message lengths alone , so it is the same for the corpus and every simulation
PAIRS = [0] * NBIN
for _n in LENS:
    for _d in range(1, _n):
        _b = binof(_d)
        if _b >= 0:
            PAIRS[_b] += _n - _d


def curve(msgs):
    """same symbol pair counts by distance bin , within messages only"""
    out = [0] * NBIN
    for row in msgs:
        n = len(row)
        for i in range(n):
            ri = row[i]
            top = min(n, i + DMAX + 1)
            for j in range(i + 1, top):
                if ri == row[j]:
                    b = (j - i - 1) // BIN
                    out[b] += 1
    return out


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


def _classes():
    d = DSU()
    for a, i, b, j, L in GEOM:
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
    return cls, nb, list(set(cls.values()))


CLS, NB, KEYS = _classes()


def plant_plain(r, PA):
    """
    a plaintext over PA letters carrying the corpus's sharing geometry , with
    no two adjacent positions equal - the corpus never repeats a symbol
    adjacently and that is a property of the plaintext , not of the schedule.
    """
    keys = list(KEYS)
    r.shuffle(keys)
    val = {}
    for k in keys:
        bad = set()
        for q in NB[k]:
            if q in val:
                bad.add(val[q])
        ch = [c for c in range(PA) if c not in bad]
        val[k] = r.choice(ch)
    return [[val[CLS[(m, p)]] for p in range(LENS[m])] for m in range(9)]




# ---------------------------------------------------------------- the detector
# lifted unchanged from eye_sched.py , which selftests it against the corpus
PRE = [25, 25, 25, 6, 6, 6, 21, 21, 21]

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




# ------------------------------------------------------------- the choice rules
RULES = ['bij', 'cyc', 'rnd', 'ctx1', 'ctx2']
RULENAME = {'bij': 'one symbol per letter', 'cyc': 'cycled in order',
            'rnd': 'chosen at random', 'ctx1': 'keyed on the last letter',
            'ctx2': 'keyed on the last two'}


def homophones(r, PA, rule):
    """
    partition the 83 symbols into PA sets .  under 'bij' a letter owns exactly
    one symbol , which is the classical simple substitution and the control.
    """
    sym = list(range(NSYM))
    r.shuffle(sym)
    if rule == 'bij':
        return [[sym[i]] for i in range(PA)]
    sets = [[] for _ in range(PA)]
    for i, s in enumerate(sym):
        sets[i % PA].append(s)
    return sets


def encrypt(plain, r, PA, rule, sched, W=0, target=30):
    """
    the assignment is redrawn on the schedule ; the CHOICE among a letter's
    symbols follows the rule .  the two are independent and that is the point -
    Report 62 needs a choice that survives a redraw of the assignment.
    """
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
            L = pl[p]
            st = sets[L]
            hh = len(st)
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


def draw(r, PA, rule, sched, W=0, target=30):
    """one random stream for plaintext and key , so the two cannot correlate"""
    return encrypt(plant_plain(r, PA), r, PA, rule, sched, W=W, target=target)


# ------------------------------------------------- regularity , not level
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
    evm /= 9.0
    cov /= 9.0
    if len(gm) > 2:
        mu = sum(gm) / float(len(gm))
        var = sum((x - mu) * (x - mu) for x in gm) / float(len(gm))
        gap = var / (mu * mu) if mu > 0 else 0.0
    else:
        gap = 0.0
    return [even * 1000.0, evm * 1000.0, gap, cov]


NREG = 4
NDIM = NBIN + NREG + 2          # curve , regularity , relations , mean length


def features(msgs):
    rel = relations(msgs)
    ml = (sum(x[1] for x in rel) / float(len(rel))) if rel else 0.0
    return curve(msgs) + regular(msgs) + [float(len(rel)), ml]


# ============================================================================
#  THE GRID
# ============================================================================
PA_GRID = [12, 16, 20, 24, 28, 34, 45, 60, 83]
SCHED = [('none', 0), ('pos', 20), ('pos', 28), ('pos', 35), ('pos', 45),
         ('pos', 60), ('con', 30), ('con', 50)]
HELD = 60
SDFLOOR = 0.5


def cells():
    out = []
    for PA in PA_GRID:
        for rule in RULES:
            for sc, x in SCHED:
                out.append((PA, rule, sc, x))
    return out


def schedname(sc, x):
    if sc == 'pos':
        return 'window %d' % x
    if sc == 'con':
        return 'content %d' % x
    return 'no redraw'


def label(c):
    PA, rule, sc, x = c
    return 'PA %-3d %-22s %s' % (PA, RULENAME[rule], schedname(sc, x))


def score(vec, mu, sd):
    """rule 9 a - the minus log sigma is what stops vagueness winning"""
    t = 0.0
    for k in range(NDIM):
        s = sd[k]
        z = (vec[k] - mu[k]) / s
        t += -0.5 * z * z - math.log(s)
    return t - 0.5 * NDIM * math.log(2.0 * math.pi)


def cell_one(job):
    c, draws, seed = job
    PA, rule, sc, x = c
    r = random.Random(seed)
    W = x if sc == 'pos' else 0
    T = x if sc == 'con' else 30
    vs = []
    for _ in range(draws):
        vs.append(features(draw(r, PA, rule, sc, W=W, target=T)))
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
        sys.stderr.write('  dropped %d incomplete cell , the run was'
                         ' interrupted\n' % bad)
    return out


# ============================================================================
#  COMMANDS
# ============================================================================
def cmd_selftest():
    bad = 0

    def chk(name, got, exp, tol=0.0):
        ok = (abs(got - exp) <= tol) if isinstance(exp, float) else (got == exp)
        print('  %-54s got %-16s expected %-16s %s'
              % (name, repr(got), repr(exp), 'ok' if ok else 'BAD'))
        return 0 if ok else 1

    print('the detector , lifted from eye_sched , still says what it said')
    rel = relations(M)
    bad += chk('relations recovered from the raw corpus', len(rel), 24)
    bad += chk('geometry matches the stored table',
               sorted((a, i, b, j, L) for k, L, a, i, b, j in rel),
               sorted(GEOM))
    bad += chk('mean relation length', round(
        sum(x[1] for x in rel) / 24.0, 3), 25.625, 1e-9)

    print('')
    print('the observable counts what it says it counts')
    bad += chk('every pair matches when every symbol is the same',
               curve([[7] * n for n in LENS]), PAIRS)
    bad += chk('the corpus curve', curve(M),
               [115, 101, 104, 88, 74, 64, 47, 45, 26, 18, 10, 7, 0])
    bad += chk('the feature vector width', len(features(M)), NDIM)
    bad += chk('and its last two entries are the relation count and length',
               [round(x, 3) for x in features(M)[-2:]], [24.0, 25.625])

    print('')
    print('the homophone sets are a partition , and bij is a bijection')
    for rule in RULES:
        hs = homophones(random.Random(3), 20, rule)
        if rule == 'bij':
            bad += chk('bij gives one symbol per letter',
                       sorted(len(x) for x in hs), [1] * 20)
        else:
            bad += chk('%s partitions all 83 symbols' % rule,
                       sorted(x for s0 in hs for x in s0), list(range(NSYM)))

    print('')
    print('THE MECHANISM THIS TOOL RESTS ON')
    print('  a choice keyed on the plaintext must give the SAME symbols in two')
    print('  copies of the same passage .  a random choice must not.')
    pl = plant_plain(random.Random(21), 20)
    a, i, b, j, L = 0, 33, 0, 61, 26          # the lag 28 self passage
    bad += chk('the test passage really is shared plaintext',
               pl[a][i:i + L] == pl[b][j:j + L], True)
    for rule, want in (('ctx1', True), ('ctx2', True), ('rnd', False)):
        ct = encrypt(pl, random.Random(21), 20, rule, 'none')
        same = sum(1 for t in range(1, L)
                   if ct[a][i + t] == ct[b][j + t])
        bad += chk('%s reproduces the passage , %d of %d positions'
                   % (rule, same, L - 1), same >= L - 3 if want else same < 8,
                   True)
    ct = encrypt(pl, random.Random(21), 20, 'cyc', 'none')
    use = collections.Counter()
    for p in range(LENS[0]):
        if pl[0][p] == pl[0][33]:
            use[ct[0][p]] += 1
    bad += chk('cycling still balances its homophones',
               (max(use.values()) - min(use.values())) <= 1 if len(use) > 1
               else True, True)
    bad += chk('and cycling still crushes the shortest repeats',
               curve(encrypt(pl, random.Random(5), 20, 'cyc', 'none'))[0] <
               curve(encrypt(pl, random.Random(5), 20, 'rnd', 'none'))[0] / 2,
               True)

    print('')
    print('a redraw really breaks the passage echo')
    ce = encrypt(pl, random.Random(31), 20, 'ctx1', 'none')
    cw = encrypt(pl, random.Random(31), 20, 'ctx1', 'pos', W=8)
    e0 = sum(1 for t in range(L) if ce[0][33 + t] == ce[0][61 + t])
    e1 = sum(1 for t in range(L) if cw[0][33 + t] == cw[0][61 + t])
    bad += chk('no schedule echoes the passage , a window of 8 does not',
               e0 > 3 * max(e1, 1), True)

    print('')
    print('the score cannot be won by being vague - the Report 54 regression')
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
    bad += chk('cells', len(cells()),
               len(PA_GRID) * len(RULES) * len(SCHED))

    print('')
    print('SELFTEST %s   %d bad' % ('PASSED' if bad == 0 else 'FAILED', bad))
    return bad


def cmd_speed(threads, draws):
    print('timing the real simulation loop on this machine')
    print('')
    t0 = time.time()
    for i in range(6):
        features(draw(random.Random(9000 + i), 20, 'ctx1', 'pos', W=35))
    per = (time.time() - t0) / 6.0
    t0 = time.time()
    for i in range(6):
        curve(draw(random.Random(9100 + i), 20, 'ctx1', 'pos', W=35))
    cheap = (time.time() - t0) / 6.0
    print('  one corpus WITH the relation detector    %.4f s' % per)
    print('  the same corpus without it               %.4f s' % cheap)
    print('  the detector is %.0f times the rest of the work'
          % (per / max(cheap, 1e-9)))
    eff = 1.0
    if threads > 1:
        import multiprocessing as mp
        probe = [((20, 'ctx1', 'pos', 35), 6, 9500 + i) for i in range(threads)]
        pool = mp.Pool(threads)
        t0 = time.time()
        for _ in pool.imap_unordered(cell_one, probe, chunksize=1):
            pass
        wall = time.time() - t0
        pool.close(); pool.join()
        ideal = len(probe) * 6 * per / float(threads)
        eff = ideal / wall if wall > 0 else 1.0
        print('')
        print('  %d cells of 6 draws across %d workers took %.1f s against'
              % (len(probe), threads, wall))
        print('  %.1f s if the threads scaled perfectly .  EFFICIENCY %.2f .'
              % (ideal, eff))
        print('  this times the workers only .  it excludes starting them.')
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
                 ('%.0f s' % w) if w < 120 else
                 ('%.1f min' % (w / 60.0)) if w < 7200 else
                 ('%.1f hours' % (w / 3600.0))))
    w = nc * draws * per / max(threads, 1) / eff
    print('')
    print('  the run you asked about : --draws %d over %d cells is %d corpora'
          % (draws, nc, nc * draws))
    print('  about %s'
          % (('%.0f s' % w) if w < 120 else ('%.1f min' % (w / 60.0))
             if w < 7200 else ('%.1f hours' % (w / 3600.0))))


def cmd_run(threads, draws, path):
    cs = cells()
    print('simulating %d cells of %d draws , %d corpora , on %d threads'
          % (len(cs), draws, len(cs) * draws, threads))
    print('the relation detector runs on every one , which is the whole cost')
    jobs = [(c, draws, 11000 + 37 * i) for i, c in enumerate(cs)]
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

    def supstr(v):
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
    print('  regularity       even %.2f  evenm %.2f  gapvar %.4f  cover %.1f'
          % tuple(obs[NBIN:NBIN + 4]))
    print('  relations        %.0f , mean length %.2f' % (obs[-2], obs[-1]))
    print('  sigma floored in %d component of %d'
          % (sum(r0['floor'] for r0 in recs), len(recs) * NDIM))
    print('')
    print('  %-42s %-12s %-8s %s'
          % ('family', 'support', 'fit p', 'relations predicted'))
    print('')
    for r0 in recs[:18]:
        print('  %-42s %-12s %-8.4f %.1f'
              % (label(r0['c']), supstr(sup(r0)), r0['p'], r0['mu'][-2]))
    print('  . . .')
    for r0 in recs[-3:]:
        print('  %-42s %-12s %-8.4f %.1f'
              % (label(r0['c']), supstr(sup(r0)), r0['p'], r0['mu'][-2]))

    print('')
    print('  best cell of each choice rule')
    for rule in RULES:
        sel = [r0 for r0 in recs if r0['c'][1] == rule]
        if sel:
            print('    %-24s %-42s %-12s p %.4f'
                  % (RULENAME[rule], label(sel[0]['c']), supstr(sup(sel[0])),
                     sel[0]['p']))
    print('')
    print('  best cell of each schedule')
    for sc, x in SCHED:
        sel = [r0 for r0 in recs if r0['c'][2] == sc and r0['c'][3] == x]
        if sel:
            print('    %-24s %-42s %-12s p %.4f'
                  % (schedname(sc, x), label(sel[0]['c']), supstr(sup(sel[0])),
                     sel[0]['p']))

    print('')
    print('=' * 78)
    print('THE FULL GRID , PRINTED RATHER THAN MARGINALISED')
    print('=' * 78)
    print('  rule 11 .  Reports 60 and 61 quoted a marginal that was gated ,')
    print('  passed , and was still wrong , because the planted corpora came')
    print('  from the same prior the estimator assumed .  no marginal is')
    print('  quoted anywhere in this report .  this is the whole grid.')
    for rule in RULES:
        print('')
        print('  %s' % RULENAME[rule].upper())
        print('  %-5s %s' % ('PA', ' '.join('%11s' % schedname(sc, x)
                                            for sc, x in SCHED)))
        for PA in PA_GRID:
            row = []
            for sc, x in SCHED:
                r0 = by.get((PA, rule, sc, x))
                row.append('%11s' % (supstr(sup(r0)).replace(' ', '')
                                     if r0 else '-'))
            print('  %-5d %s' % (PA, ' '.join(row)))

    print('')
    print('=' * 78)
    print('WHAT REJECTS EACH FAMILY , in sigma of that family own spread')
    print('=' * 78)
    pick = [0, 1, 2, 3, NBIN, NBIN + 1, NBIN + 2, NBIN + 3, NDIM - 2, NDIM - 1]
    names = ['d1-10', 'd11-20', 'd21-30', 'd31-40', 'even', 'evenm',
             'gapvar', 'cover', 'reln', 'rlen']
    print('  %-42s %s' % ('family', ' '.join('%7s' % n for n in names)))
    seen = set()
    for r0 in recs:
        if r0['c'][1] in seen:
            continue
        seen.add(r0['c'][1])
        z = [(obs[k] - r0['mu'][k]) / r0['sd'][k] for k in pick]
        print('  %-42s %s' % (label(r0['c']),
                              ' '.join('%+7.1f' % y for y in z)))
    print('')
    print('  ( the best cell of each rule , so each line is that rule at its')
    print('  most favourable setting .  reln is the relation count , which is')
    print('  half the contradiction Report 62 opened )')

    print('')
    print('=' * 78)
    print('THE GATE ON THE CHOICE RULE')
    print('=' * 78)
    print('  a rule can only be refuted if the grid recognises it when it IS')
    print('  the truth .  plant each , see which wins.')
    print('')
    mus = [(r0['c'], r0['mu'], r0['sd']) for r0 in recs]
    NC = {}
    for c in cells():
        NC[c[1]] = NC.get(c[1], 0) + 1

    def rmarg(v):
        sc = [(score(v, mu, sd), c) for c, mu, sd in mus]
        b = max(x[0] for x in sc)
        t = {}
        for s0, c0 in sc:
            t[c0[1]] = t.get(c0[1], 0.0) + math.exp(max(s0 - b, -700.0))
        tt = sum(t.values()) or 1.0
        return dict((k, v0 / tt) for k, v0 in t.items())

    agg = {}
    for r0 in recs:
        if not r0.get('held'):
            continue
        tm = r0['c'][1]
        for v in r0['held'][:10]:
            mm = rmarg(v)
            a = agg.setdefault(tm, {})
            for k in RULES:
                a[k] = a.get(k, 0.0) + mm.get(k, 0.0)
    print('  %-24s %s' % ('planted', ' '.join('%9s' % k for k in RULES)))
    for k in RULES:
        if k not in agg:
            continue
        n = sum(agg[k].values()) or 1.0
        print('  %-24s %s' % (RULENAME[k],
                              ' '.join('%8.1f %%' % (100.0 * agg[k][q] / n)
                                       for q in RULES)))
    mm = rmarg(obs)
    print('  %-24s %s' % ('THE CORPUS',
                          ' '.join('%8.1f %%' % (100.0 * mm.get(k, 0.0))
                                   for k in RULES)))
    print('')
    print('  every rule has %d cells , so this row is NOT biased by cell'
          % NC.get(RULES[0], 0))
    print('  count the way the mechanism marginal of Report 61 was .  read the')
    print('  diagonal first : a rule below about 40 percent on its own diagonal')
    print('  cannot be refuted by the corpus failing to look like it.')

    print('')
    print('=' * 78)
    print('THE GATE ON THE CELL')
    print('=' * 78)
    ranks = []
    for r0 in recs:
        if not r0.get('held'):
            continue
        for v in r0['held'][:10]:
            sc = sorted(((score(v, mu, sd), c) for c, mu, sd in mus),
                        reverse=True)
            for q, (s0, c0) in enumerate(sc):
                if c0 == r0['c']:
                    ranks.append(q + 1)
                    break
    ranks.sort()
    if ranks:
        print('  %d planted corpora scored against all %d cells'
              % (len(ranks), len(recs)))
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
                opt('--out', 'eye_choice_cells.txt', str))
    elif cmd == 'report':
        cmd_report(opt('--out', 'eye_choice_cells.txt', str))
    else:
        print('commands : version , selftest , speed , run , report')
        print('')
        print('  python eye_choice.py version')
        print('  python eye_choice.py selftest')
        print('  python eye_choice.py speed --threads 32 --draws 900')
        print('  python eye_choice.py run --threads 32 --draws 900')
        print('  python eye_choice.py report')


if __name__ == '__main__':
    main()
