#!/usr/bin/env python
# ============================================================================
# eye_repeat.py  -  THE REPEAT DISTANCE CURVE , A PHASE FREE OBSERVABLE
#
#   python eye_repeat.py version
#   python eye_repeat.py selftest
#   python eye_repeat.py speed --threads 32 --draws 400
#   python eye_repeat.py run   --threads 32 --draws 400
#   python eye_repeat.py report
#
# WHY THIS OBSERVABLE
#   Report 59 measured the redraw schedule through the ENDS of relations and
#   ran out of resolution : ten families survived inside a factor of two , and
#   every one of them was invisible to absolute position , which was the only
#   thing that instrument could see .  It needed a phase free observable .
#
#   Here is one , and it uses the whole corpus rather than 96 endpoints .
#
#   Take every pair of positions in the same message at distance d , and ask
#   how often the two carry the same symbol .  Under a bijection redrawn every
#   W positions :
#
#     the two positions in the SAME window   same symbol exactly when the
#                                            plaintext letters agree , rate
#                                            1 / PA
#     in DIFFERENT windows                   the two injections are drawn
#                                            independently , rate about 1 / 83
#
#   so the curve is  rate ( d ) = f ( d ) / PA + ( 1 - f ( d ) ) / 83  where
#   f ( d ) is the chance the two positions share a window .  f falls linearly
#   to zero at d = W for a position schedule , falls exponentially for a
#   content schedule , and is flat at one when there is no redraw at all .
#
#   NONE of that depends on where the windows start .  A lattice beginning at
#   offset 7 and one beginning at offset 19 give the same curve .  That is the
#   property Report 59 could not obtain.
#
# WHAT THE CORPUS SAYS BEFORE ANY MODEL IS FITTED
#   699 same symbol pairs out of 59702 within message position pairs , and the
#   rate is FLAT from distance 1 to distance 120 :
#
#     1-20   0.0115     41-60   0.0107     81-100   0.0093
#    21-40   0.0123     61-80   0.0116    101-120   0.0104
#
#   No decay , no cutoff , no scale .  For comparison the same measurement on a
#   simulated corpus with one bijection per message and a 40 letter plaintext
#   runs at 0 . 025 , more than twice as high , which is the flat 1 / PA the
#   model demands.
#
# WHY IT IS BUILT THE WAY IT IS
#   Report 53 withdrew three reports of rankings from a search that turned out
#   to have no resolving power , and Report 54 found a scoring rule that bought
#   vagueness because it divided by each candidate's own spread .  So :
#
#     1 . the score is a Gaussian log likelihood that CARRIES ITS minus log
#         sigma , so a family cannot win by being vague
#     2 . the null for each family is that family's own simulated draws , so
#         size is correct by construction
#     3 . verify plants a corpus from a KNOWN cell of the grid and requires the
#         readout to rank that cell , and prints the rank it actually achieved .
#         a grid that cannot find its own planted cell says nothing about the
#         corpus
#     4 . every command prints its build , per rule 12
# ============================================================================

import sys, os, math, random, collections, time

VERSION = 'eye_repeat build 1 , 21 August 2026'
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


def encrypt(plain, r, PA, mode, W=0, target=30):
    """
    mode 'pos'   redraw every W positions , with a DIFFERENT random phase in
                 every message - the variant Report 59 was blind to , and the
                 one this observable does not care about
    mode 'con'   redraw when the plaintext letter is a trigger
    mode 'none'  one injection for a whole message
    """
    out = []
    trig = None
    if mode == 'con':
        k = max(1, int(round(PA / float(target))))
        trig = set(r.sample(range(PA), k))
    for m in range(9):
        pl = plain[m]
        sig = r.sample(range(NSYM), PA)
        ph = r.randrange(W) if (mode == 'pos' and W) else 0
        row = []
        for p in range(len(pl)):
            if p:
                if mode == 'pos':
                    cut = ((p - ph) % W == 0)
                elif mode == 'con':
                    cut = (pl[p] in trig)
                else:
                    cut = False
                if cut:
                    sig = r.sample(range(NSYM), PA)
            row.append(sig[pl[p]])
        out.append(row)
    return out


def draw(r, PA, mode, W=0, target=30):
    return encrypt(plant_plain(r, PA), r, PA, mode, W=W, target=target)


# ============================================================================
#  THE GRID
# ============================================================================
PA_GRID = [30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 83]
W_GRID = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 60]
T_GRID = [5, 8, 12, 20, 30, 50]
HELD = 100          # draws per cell kept back to test the grid on itself
SDFLOOR = 0.5


def cells():
    out = []
    for PA in PA_GRID:
        for W in W_GRID:
            out.append(('pos', PA, W))
        for T in T_GRID:
            out.append(('con', PA, T))
        out.append(('none', PA, 0))
    return out


def label(c):
    mode, PA, x = c
    if mode == 'pos':
        return 'PA %-3d  window %-3d' % (PA, x)
    if mode == 'con':
        return 'PA %-3d  content %-3d' % (PA, x)
    return 'PA %-3d  no redraw ' % PA


def score(vec, mu, sd):
    """
    Gaussian log likelihood of a count vector under a family .

    the minus log sigma is not decoration .  Report 54 found a scoring rule
    that divided by each candidate's own spread and therefore paid candidates
    to be vague - the top twenty were 1 . 9 times wider than the bottom twenty
    and the planted rule sat at 146 of 210 .  carrying minus log sigma is what
    stops a family winning by predicting everything.
    """
    t = 0.0
    for k in range(NBIN):
        s = sd[k]
        z = (vec[k] - mu[k]) / s
        t += -0.5 * z * z - math.log(s)
    return t - 0.5 * NBIN * math.log(2.0 * math.pi)


OBS = None


def cell_one(job):
    c, draws, seed = job
    mode, PA, x = c
    r = random.Random(seed)
    W = x if mode == 'pos' else 0
    T = x if mode == 'con' else 30
    vs = []
    for _ in range(draws):
        vs.append(curve(draw(r, PA, mode, W=W, target=T)))
    mu = [0.0] * NBIN
    sd = [0.0] * NBIN
    for k in range(NBIN):
        col = [v[k] for v in vs]
        m0 = sum(col) / float(len(col))
        var = sum((y - m0) * (y - m0) for y in col) / float(len(col))
        mu[k] = m0
        sd[k] = max(math.sqrt(var), SDFLOOR)
    obs = curve(M)
    lobs = score(obs, mu, sd)
    own = [score(v, mu, sd) for v in vs]
    le = sum(1 for y in own if y <= lobs)
    own.sort()
    return {'c': list(c), 'mu': [round(y, 4) for y in mu],
            'sd': [round(y, 4) for y in sd],
            'lobs': lobs, 'p': (le + 1.0) / (len(own) + 1.0),
            'lmed': own[len(own) // 2],
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
        if n % 10 == 0 or n == len(jobs):
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
        print('  %-52s got %-18s expected %-18s %s'
              % (name, repr(got), repr(exp), 'ok' if ok else 'BAD'))
        return 0 if ok else 1

    print('the observable counts what it says it counts')
    flat = [[7] * n for n in LENS]
    bad += chk('every pair matches when every symbol is the same',
               curve(flat), PAIRS)
    allsep = [list(range(n)) for n in LENS]
    bad += chk('no pair matches when no symbol repeats',
               sum(curve(allsep)), 0)
    ind = 0
    for n in LENS:
        for d in range(1, min(n, DMAX + 1)):
            ind += n - d
    bad += chk('the pair count agrees with an independent count',
               sum(PAIRS), ind)
    bad += chk('the corpus curve', curve(M),
               [115, 101, 104, 88, 74, 64, 47, 45, 26, 18, 10, 7, 0])
    bad += chk('the corpus total', sum(curve(M)), 699)

    print('')
    print('the mechanism forbids these , so they are asserted')
    r = random.Random(5)
    for PA in (40, 80):
        acc = 0; tot = 0
        for t in range(12):
            v = curve(draw(random.Random(100 + t), PA, 'none'))
            acc += sum(v); tot += sum(PAIRS)
        bad += chk('no redraw at PA %d gives a rate of one in %d' % (PA, PA),
                   round(tot / float(acc), 1), float(PA), PA * 0.14)
    acc = 0; tot = 0
    for t in range(12):
        v = curve(draw(random.Random(200 + t), 40, 'pos', W=2))
        acc += sum(v); tot += sum(PAIRS)
    bad += chk('a window of 2 gives the chance rate one in 83',
               round(tot / float(acc), 1), 83.0, 12.0)

    def shortrate(PA, W, n=10):
        a = 0
        for t in range(n):
            a += curve(draw(random.Random(300 + t), PA, 'pos', W=W))[0]
        return a / float(n * PAIRS[0])
    v40 = shortrate(40, 20); v83 = shortrate(83, 20)
    bad += chk('a bigger plaintext alphabet repeats less at short range',
               v40 > v83, True)
    w6 = shortrate(55, 6); w30 = shortrate(55, 30)
    bad += chk('a wider window repeats more at short range', w30 > w6, True)

    print('')
    print('encryption is a bijection inside a window')
    pl = plant_plain(random.Random(9), 50)
    ct = encrypt(pl, random.Random(9), 50, 'pos', W=16)
    okb = True
    for m in range(9):
        seen = {}
        brk = 0
        for p in range(LENS[m]):
            if p and (p - 0) % 16 == 0:
                pass
        # a per message phase is drawn inside encrypt , so recover it from the
        # ciphertext by testing every offset and requiring one to be consistent
        good = False
        for ph in range(16):
            mp = {}; ok2 = True; brk = 0
            for p in range(LENS[m]):
                if p and (p - ph) % 16 == 0:
                    brk = p
                key = (pl[m][p], brk)
                if key in mp and mp[key] != ct[m][p]:
                    ok2 = False; break
                mp[key] = ct[m][p]
            if ok2:
                good = True; break
        if not good:
            okb = False
    bad += chk('one letter one symbol inside every window , at some phase',
               okb, True)
    bad += chk('every planted relation shares its plaintext',
               all(pl[a][i + t] == pl[b][j + t]
                   for a, i, b, j, L in GEOM for t in range(L)), True)
    bad += chk('no two adjacent plaintext letters equal',
               sum(1 for m in range(9) for p in range(LENS[m] - 1)
                   if pl[m][p] == pl[m][p + 1]), 0)
    bad += chk('ciphertext stays inside the 83 symbols',
               max(max(x) for x in ct) < NSYM and
               min(min(x) for x in ct) >= 0, True)

    print('')
    print('the score cannot be won by being vague - the Report 54 regression')
    obs = curve(M)
    mu = [float(y) for y in obs]
    sharp = score(obs, mu, [2.0] * NBIN)
    vague = score(obs, mu, [20.0] * NBIN)
    bad += chk('a sharp family that fits beats a vague one that fits',
               sharp > vague, True)
    off = [y + 6 for y in obs]
    bad += chk('a family that misses by 3 sigma loses to one that does not',
               score(obs, mu, [2.0] * NBIN) > score(off, mu, [2.0] * NBIN),
               True)
    bad += chk('a vague family beats a sharp one that is badly wrong',
               score(off, mu, [20.0] * NBIN) > score(off, mu, [2.0] * NBIN),
               True)

    print('')
    print('the grid is the size it claims')
    bad += chk('cells', len(cells()),
               len(PA_GRID) * (len(W_GRID) + len(T_GRID) + 1))

    print('')
    print('SELFTEST %s   %d bad' % ('PASSED' if bad == 0 else 'FAILED', bad))
    return bad


def cmd_speed(threads, draws):
    print('timing the real simulation loop on this machine')
    print('')
    t0 = time.time()
    for i in range(40):
        curve(draw(random.Random(9000 + i), 55, 'pos', W=10))
    per = (time.time() - t0) / 40.0
    print('  one simulated corpus         %.4f s' % per)
    eff = 1.0
    if threads > 1:
        import multiprocessing as mp
        probe = [(('pos', 55, 10), 40, 9500 + i) for i in range(threads)]
        pool = mp.Pool(threads)
        t0 = time.time()
        for _ in pool.imap_unordered(cell_one, probe, chunksize=1):
            pass
        wall = time.time() - t0
        pool.close(); pool.join()
        ideal = len(probe) * 40 * per / float(threads)
        eff = ideal / wall if wall > 0 else 1.0
        print('  %d cells of 40 draws across %d workers took %.1f s , against'
              % (len(probe), threads, wall))
        print('  %.1f s if the threads scaled perfectly .  EFFICIENCY %.2f .'
              % (ideal, eff))
        print('  this times the workers only .  it excludes starting them ,')
        print('  which on Windows spawns a fresh interpreter per worker.')
        if eff < 0.05:
            eff = 0.05
    nc = len(cells())
    print('')
    print('  %-10s %-12s %-14s %s' % ('draws', 'corpora', 'core seconds',
                                      'wall clock at %d threads' % threads))
    for n in (200, 500, 1000, 2000, 5000):
        tot = nc * n * per
        w = tot / max(threads, 1) / eff
        print('  %-10d %-12d %-14.0f %s'
              % (n, nc * n, tot,
                 ('%.0f s' % w) if w < 120 else ('%.1f min' % (w / 60.0))))
    w = nc * draws * per / max(threads, 1) / eff
    print('')
    print('  the run you asked about : --draws %d over %d cells is %d corpora'
          % (draws, nc, nc * draws))
    print('  about %s , and the grid then tests itself on %d planted corpora'
          % (('%.0f s' % w) if w < 120 else ('%.1f min' % (w / 60.0)),
             nc * HELD))


def cmd_run(threads, draws, path):
    cs = cells()
    print('simulating %d cells of %d draws , %d corpora , on %d threads'
          % (len(cs), draws, len(cs) * draws, threads))
    jobs = [(c, draws, 7000 + 31 * i) for i, c in enumerate(cs)]
    runcells(jobs, threads, path)
    cmd_report(path)


def cmd_report(path):
    recs = loadcells(path)
    if not recs:
        print('no cells in %s' % path)
        return
    obs = curve(M)
    for r0 in recs:
        r0['c'] = tuple(r0['c'])
    best = max(r0['lobs'] for r0 in recs)
    recs.sort(key=lambda r0: -r0['lobs'])
    nfloor = sum(r0['floor'] for r0 in recs)

    print('')
    print('=' * 74)
    print('THE CORPUS AGAINST %d FAMILIES' % len(recs))
    print('=' * 74)
    print('  observed curve   %s   total %d'
          % (' '.join('%3d' % y for y in obs), sum(obs)))
    print('  pairs per bin    %s' % ' '.join('%3d' % (y // 100) for y in PAIRS)
          + '   ( hundreds )')
    print('  bins are distances 1-10 , 11-20 , . . . , 121-130')
    print('')
    print('  sigma floored in %d bin of %d , floor %.1f'
          % (nfloor, len(recs) * NBIN, SDFLOOR))
    print('')
    print('  %-24s %-12s %-10s %s'
          % ('family', 'support', 'fit p', 'predicted curve'))
    print('')
    for r0 in recs[:14]:
        rr = math.exp(max(r0['lobs'] - best, -700.0))
        print('  %-24s %-12s %-10.4f %s'
              % (label(r0['c']),
                 '1 . 00' if rr > 0.999 else
                 ('1 in %.0f' % (1.0 / rr)) if rr > 1e-12 else 'below 1e12',
                 r0['p'],
                 ' '.join('%3.0f' % y for y in r0['mu'])))
    print('  . . .')
    for r0 in recs[-3:]:
        rr = math.exp(max(r0['lobs'] - best, -700.0))
        print('  %-24s %-12s %-10.4f %s'
              % (label(r0['c']),
                 ('1 in %.0f' % (1.0 / rr)) if rr > 1e-12 else 'below 1 in 1e12',
                 r0['p'],
                 ' '.join('%3.0f' % y for y in r0['mu'])))

    print('')
    print('  best supported family of each kind')
    for mode, lab in (('pos', 'position schedule'),
                      ('con', 'content schedule'),
                      ('none', 'no redraw at all')):
        sel = [r0 for r0 in recs if r0['c'][0] == mode]
        if sel:
            b = sel[0]
            rr = math.exp(max(b['lobs'] - best, -700.0))
            print('    %-20s %-24s support %-12s fit p %.4f'
                  % (lab, label(b['c']),
                     '1 . 00' if rr > 0.999 else
                     ('1 in %.0f' % (1.0 / rr)) if rr > 1e-12 else 'below 1e12',
                     b['p']))

    print('')
    print('  every family whose own draws make the corpus plausible , p above')
    print('  0 . 05 , and which is within a factor of 100 of the best')
    live = [r0 for r0 in recs
            if r0['p'] > 0.05 and math.exp(max(r0['lobs'] - best, -700.0)) > 0.01]
    if not live:
        print('    NONE .  no family in the grid both fits and is plausible.')
    for r0 in live[:24]:
        rr = math.exp(max(r0['lobs'] - best, -700.0))
        print('    %-24s support %-12s fit p %.4f'
              % (label(r0['c']),
                 '1 . 00' if rr > 0.999 else '1 in %.0f' % (1.0 / rr), r0['p']))
    if len(live) > 24:
        print('    and %d more' % (len(live) - 24))

    print('')
    print('=' * 74)
    print('THE GATE - can the grid find a cell it planted itself')
    print('=' * 74)
    mus = [(r0['c'], r0['mu'], r0['sd']) for r0 in recs]
    ranks = {}
    for r0 in recs:
        if not r0.get('held'):
            continue
        rk = []
        for v in r0['held']:
            sc = [(score(v, mu, sd), c) for c, mu, sd in mus]
            sc.sort(reverse=True)
            for q, (s0, c0) in enumerate(sc):
                if c0 == r0['c']:
                    rk.append(q + 1)
                    break
        rk.sort()
        ranks[r0['c']] = rk
    allr = []
    for v in ranks.values():
        allr.extend(v)
    allr.sort()
    if allr:
        print('  %d planted corpora scored against all %d cells'
              % (len(allr), len(recs)))
        print('  median rank of the true cell   %d of %d'
              % (allr[len(allr) // 2], len(recs)))
        print('  true cell in the top 10        %.1f %%'
              % (100.0 * sum(1 for y in allr if y <= 10) / len(allr)))
        print('  true cell ranked first         %.1f %%'
              % (100.0 * sum(1 for y in allr if y == 1) / len(allr)))
        print('')
        print('  a grid that cannot find its own planted cell says nothing')
        print('  about the corpus .  median rank by kind :')
        for mode, lab in (('pos', 'position schedule'),
                          ('con', 'content schedule'),
                          ('none', 'no redraw at all')):
            v = []
            for c, rk in ranks.items():
                if c[0] == mode:
                    v.extend(rk)
            v.sort()
            if v:
                print('    %-20s median %-5d top ten %.0f %%'
                      % (lab, v[len(v) // 2],
                         100.0 * sum(1 for y in v if y <= 10) / len(v)))
        print('')
        print('  which parameter the grid can actually pin down , read off')
        print('  the same planted corpora')
        conf = {}
        for r0 in recs:
            if r0['c'][0] != 'pos' or not r0.get('held'):
                continue
            for v in r0['held'][:20]:
                sc = max(((score(v, mu, sd), c) for c, mu, sd in mus))
                got = sc[1]
                a, b = conf.get(r0['c'], (0, 0))
                conf[r0['c']] = (a + (1 if got[1] == r0['c'][1] else 0),
                                 b + (1 if (got[0] == 'pos' and
                                            got[2] == r0['c'][2]) else 0))
        na = sum(x[0] for x in conf.values())
        nw = sum(x[1] for x in conf.values())
        nt = 20 * len(conf)
        print('    plaintext alphabet recovered exactly   %.0f %%'
              % (100.0 * na / max(nt, 1)))
        print('    window width recovered exactly         %.0f %%'
              % (100.0 * nw / max(nt, 1)))
    cmd_marginal(recs)


def wmarg(vec, mus, best=None):
    """support weighted marginal over window width , position families only"""
    sc = [(score(vec, mu, sd), c) for c, mu, sd in mus]
    b = max(x[0] for x in sc)
    tot = {}
    for s0, c0 in sc:
        if c0[0] != 'pos':
            continue
        tot[c0[2]] = tot.get(c0[2], 0.0) + math.exp(max(s0 - b, -700.0))
    t = sum(tot.values()) or 1.0
    for k in tot:
        tot[k] /= t
    return tot


def pmean(t):
    return sum(k * v for k, v in t.items())


def cmd_marginal(recs):
    """
    the grid cannot name a cell - the gate says the true cell lands at median
    rank 15 of 220 and the exact window is recovered 28 percent of the time .
    what it CAN do is place the window on a scale , and that claim gets its own
    gate : plant a known W , read the marginal back , and print the answer the
    corpus gives beside the answers the planted corpora gave.
    """
    mus = [(r0['c'], r0['mu'], r0['sd']) for r0 in recs]
    obs = curve(M)
    ct = wmarg(obs, mus)
    print('')
    print('=' * 74)
    print('THE WINDOW , ON A GATED SCALE')
    print('=' * 74)
    print('  the corpus , support weighted over every position family')
    print('')
    for k in sorted(ct):
        if ct[k] > 0.002:
            print('    W %-4d %5.1f %%%s' % (k, 100.0 * ct[k],
                                             '  ' + '#' * int(60 * ct[k])))
    print('')
    print('    posterior mean window   %.1f' % pmean(ct))
    print('')
    print('  the same readout on corpora with a KNOWN window , so the number')
    print('  above can be read against something .  the estimator floors near')
    print('  9 because the grid cannot see below its own resolution , which is')
    print('  why a raw posterior mean is not quoted as the answer.')
    print('')
    print('    %-10s %-18s %s' % ('planted W', 'posterior mean', 'true W rank'))
    agg = {}
    for r0 in recs:
        if r0['c'][0] != 'pos' or not r0.get('held'):
            continue
        W = r0['c'][2]
        for v in r0['held'][:16]:
            t = wmarg(v, mus)
            order = sorted(t, key=lambda k: -t[k])
            a = agg.setdefault(W, [[], []])
            a[0].append(pmean(t))
            a[1].append(order.index(W) + 1 if W in order else 99)
    for W in sorted(agg):
        pm, rk = agg[W]
        pm.sort(); rk.sort()
        print('    %-10d %-18.1f %d' % (W, pm[len(pm) // 2], rk[len(rk) // 2]))
    lo = []
    hi = []
    for W in agg:
        if W <= 8:
            lo.extend(agg[W][0])
        if W >= 20:
            hi.extend(agg[W][0])
    lo.sort(); hi.sort()
    if lo and hi:
        print('')
        print('    planted W 8 or less   posterior mean median %.1f'
              % lo[len(lo) // 2])
        print('    planted W 20 or more  posterior mean median %.1f'
              % hi[len(hi) // 2])
        c = pmean(ct)
        print('')
        if c <= lo[len(lo) // 2] + 0.5:
            print('    THE CORPUS AT %.1f SITS AT OR BELOW THE SMALL W'
                  ' CALIBRATION POINT .' % c)
            print('    the window is at the bottom of the grid , not in the'
                  ' middle of it.')
        elif c >= hi[len(hi) // 2] - 0.5:
            print('    the corpus at %.1f sits at the large W calibration'
                  ' point.' % c)
        else:
            print('    the corpus at %.1f sits between the two calibration'
                  ' points and this readout does not separate them.' % c)


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
        cmd_speed(opt('--threads', 32), opt('--draws', 2000))
    elif cmd in ('run', 'verify', 'scan'):
        cmd_run(opt('--threads', 32), opt('--draws', 2000),
                opt('--out', 'eye_repeat_cells.txt', str))
    elif cmd == 'report':
        cmd_report(opt('--out', 'eye_repeat_cells.txt', str))
    else:
        print('commands : version , selftest , speed , run , report')
        print('')
        print('  python eye_repeat.py version')
        print('  python eye_repeat.py selftest')
        print('  python eye_repeat.py speed --threads 32 --draws 2000')
        print('  python eye_repeat.py run --threads 32 --draws 2000')
        print('  python eye_repeat.py report')


if __name__ == '__main__':
    main()
