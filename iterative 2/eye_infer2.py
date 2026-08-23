#!/usr/bin/env python
# ============================================================================
# eye_infer.py  build 2  -  THE GEOMETRY INVERSE PROBLEM , CEILING REMOVED
#
#   python eye_infer.py version
#   python eye_infer.py selftest
#   python eye_infer.py speed --threads 32 --draws 2000
#   python eye_infer.py run   --threads 32 --draws 2000
#   python eye_infer.py report
#
# WHAT BUILD 1 FOUND , AND WHAT IT GOT WRONG
#   It disfavoured the standing 24 relation geometry - fit p 0 . 041 to 0 . 074 ,
#   chi square 20 . 4 on nine observables , predicting 11 . 2 relations against
#   the corpus's 24 .  That stands.
#
#   Three things it got wrong , all fixed here :
#
#   1 . THE CAP WAS CIRCULAR .  The generator refused to build a plaintext class
#       larger than 8 , a number taken from the corpus's DETECTED geometry .  But
#       the detected geometry is what survives the cipher .  If the true sharing
#       is richer its classes are larger , so a cap taken from the detected
#       geometry forbids the answer being searched for .  The posterior duly
#       piled against that ceiling .  **The cap is now a free dimension , 6 to 24 .**
#
#   2 . THE SUPPORT RANKING WAS INVALID .  The score carries minus log sigma ,
#       which is right between models of the same kind .  The standing 24 plants
#       ONE geometry , so its spread is small ; a generated family plants a
#       different geometry every draw , so its spread carries geometry
#       uncertainty too .  A point hypothesis beats a family that contains it ,
#       every time .  **Support now ranks generated families among themselves
#       only , and the standing 24 is reported beside them , never above them .
#       Goodness of fit leads.**
#
#   3 . MULTIPLICITY DID NOT RESOLVE .  Planted 2 . 2 through 3 . 4 all recovered
#       between 2 . 35 and 2 . 44 , with the true rank no better than chance , and
#       its interaction with passage count carried most of the grid's
#       degeneracy - 1700 cells collapsed to 88 models .  **It is no longer swept .
#       It is drawn afresh every corpus , so its uncertainty is marginalised into
#       each family's spread instead of pretending to be measured.**
#
# THE NINE OBSERVABLES ARE UNCHANGED
#   relations at minrep 3 , 2 and 4 ; messages 3 and 5 at minrep 3 and 2 ; mean
#   and total relation length ; positions covered at minrep 3 and 2 .  All are
#   counts the detector produces directly .  Report 68 measured the whole
#   threshold surface , so these are the corpus in the detector's own terms.
# ============================================================================

import sys, os, math, random, collections, time

VERSION = 'eye_infer build 2 , 22 August 2026'
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
PRE = [25, 25, 25, 6, 6, 6, 21, 21, 21]
NSYM = 83

GEOM24 = [(6, 68, 7, 71, 34), (1, 33, 1, 63, 33), (6, 57, 8, 58, 33),
          (7, 34, 8, 33, 33), (7, 68, 8, 66, 33), (2, 39, 2, 74, 32),
          (1, 29, 2, 34, 28), (4, 63, 6, 72, 28), (4, 63, 7, 75, 28),
          (4, 63, 8, 73, 28), (1, 60, 2, 70, 27), (0, 33, 0, 61, 26),
          (0, 53, 2, 65, 25), (1, 32, 2, 72, 25), (1, 62, 2, 37, 25),
          (1, 55, 4, 86, 23), (0, 28, 1, 28, 22), (0, 29, 2, 34, 21),
          (0, 58, 1, 60, 20), (6, 46, 7, 48, 19), (0, 32, 1, 62, 18),
          (0, 60, 1, 32, 18), (0, 32, 2, 72, 18), (0, 60, 2, 37, 18)]


def prevtab(s):
    last = {}
    pv = [-1] * len(s)
    for p in range(len(s)):
        pv[p] = last.get(s[p], -1)
        last[s[p]] = p
    return pv


def extensions(msgs):
    PV = [prevtab(m) for m in msgs]
    out = []
    for a in range(9):
        La = len(msgs[a]); pa = PV[a]
        for b in range(a, 9):
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
                    if L >= 6 and rep >= 2:
                        out.append((rep, L, a, i, b, j))
    out.sort(key=lambda t: -t[1])
    return out


def dedup(ext):
    """
    containment applies only inside one message pair and shift , so group first .
    done once at the loosest threshold and filtered by repeat count , which is
    exact : a longer relation containing a shorter one at the same shift has at
    least as many repeats , because a window starting earlier can only add prior
    occurrences.
    """
    grp = collections.defaultdict(list)
    for k, L, a, i, b, j in ext:
        grp[(a, b, j - i)].append((k, L, a, i, b, j))
    out = []
    for key in grp:
        keep = []
        for k, L, a, i, b, j in sorted(grp[key], key=lambda t: -t[1]):
            if any(i >= x[3] and i + L <= x[3] + x[1] for x in keep):
                continue
            keep.append((k, L, a, i, b, j))
        out.extend(keep)
    return out


def at(ded, mr):
    filt = [x for x in ded
            if x[0] >= mr and not (x[3] < PRE[x[2]] and x[5] < PRE[x[4]])]
    best = {}
    for k, L, a, i, b, j in filt:
        key = (a, b, j - i)
        if key not in best or L > best[key][1]:
            best[key] = (k, L, a, i, b, j)
    return list(best.values())


NOBS = 9
TARGET = [24.0, 37.0, 12.0, 0.0, 6.0, 25.625, 615.0, 439.0, 596.0]
OBSNAME = ['rel mr3', 'rel mr2', 'rel mr4', 'm35 mr3', 'm35 mr2',
           'mean len', 'total len', 'cover mr3', 'cover mr2']


def observe(msgs):
    ded = dedup(extensions(msgs))
    r3 = at(ded, 3); r2 = at(ded, 2); r4 = at(ded, 4)

    def m35(rel):
        c = 0
        for k, L, a, i, b, j in rel:
            if a in (3, 5):
                c += 1
            if b in (3, 5):
                c += 1
        return c

    def cov(rel):
        s = set()
        for k, L, a, i, b, j in rel:
            for t in range(L):
                s.add((a, i + t)); s.add((b, j + t))
        return len(s)

    ml = (sum(x[1] for x in r3) / float(len(r3))) if r3 else 0.0
    return [float(len(r3)), float(len(r2)), float(len(r4)),
            float(m35(r3)), float(m35(r2)), ml,
            float(sum(x[1] for x in r3)), float(cov(r3)), float(cov(r2))]


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


TRIES = 40      # build 1 used 3 and mistook its own retry budget for a
                # property of the corpus - asking for 60 passages placed 15 at
                # 3 tries and 23 at 60 .  the saturation it reported , and the
                # ceiling Report 69 found the posterior piling against , were
                # partly this.


def make_geometry(r, npass, cap, lmean):
    """
    npass shared passages , each carried by k messages .  k is drawn afresh here
    rather than swept , because build 1 measured it to be unidentifiable and its
    interaction with npass carried most of that grid's degeneracy.

    cap is the largest plaintext class allowed .  build 1 fixed it at 8 , taken
    from the corpus's DETECTED geometry , which is circular - the detected
    geometry is what survives the cipher , so a search for richer sharing was
    forbidden from finding it .  it is a free dimension now.
    """
    d = DSU()
    csize = {}
    placed = []
    for _ in range(npass * TRIES):
        if len(placed) >= npass:
            break
        L = max(8, min(40, int(round(r.gauss(lmean, lmean * 0.28)))))
        mult = 2.2 + r.random() * 1.2
        u = r.random()
        k = (3 if u < (4.0 - mult) else 4) if mult >= 3.0 else \
            (2 if u < (3.0 - mult) else 3)
        cand = [m for m in range(9) if LENS[m] > L + 2]
        if len(cand) < k:
            continue
        msgs = r.sample(cand, k)
        spots = [(m, r.randrange(LENS[m] - L)) for m in msgs]
        # a per offset projection is not enough - two offsets of one passage can
        # touch the SAME existing class , and each projection then sees only its
        # own share of the growth .  so apply the passage , recompute every class
        # size , and roll back if the cap is broken .  the state is a thousand
        # entries , so a snapshot per passage costs nothing and is exact.
        snapP = dict(d.p)
        snapC = dict(csize)
        a0, p0 = spots[0]
        for t in range(L):
            for m, p in spots[1:]:
                ra = d.find((a0, p0 + t)); rb = d.find((m, p + t))
                if ra == rb:
                    continue
                tot = csize.get(ra, 1) + csize.get(rb, 1)
                d.union((a0, p0 + t), (m, p + t))
                csize[d.find((a0, p0 + t))] = tot
        sz = collections.Counter()
        for mm in range(9):
            for pp in range(LENS[mm]):
                sz[d.find((mm, pp))] += 1
        if sz and max(sz.values()) > cap:
            d.p = snapP
            csize.clear(); csize.update(snapC)
            continue
        placed.append((spots, L))
    return d, placed


def plant_plain(r, PA, d):
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


def encrypt(pl, r, PA, mode, W):
    out = []
    base = NSYM // PA
    ex = NSYM - base * PA
    trig = None
    if mode == 'con':
        trig = set(r.sample(range(PA), max(1, int(round(PA / float(W))))))
    for m in range(9):
        def fresh():
            sym = list(range(NSYM)); r.shuffle(sym)
            s = []; z = 0
            for k in range(PA):
                n = base + (1 if k < ex else 0)
                s.append(sym[z:z + n]); z += n
            return s
        sets = fresh()
        ph = r.randrange(W) if mode == 'pos' else 0
        row = []
        for p in range(LENS[m]):
            if p:
                cut = ((p - ph) % W == 0) if mode == 'pos' else (pl[m][p] in trig)
                if cut:
                    sets = fresh()
            L = pl[m][p]; st = sets[L]
            row.append(st[(pl[m][p - 1] if p else 7) % len(st)])
        out.append(row)
    return out


def draw(r, npass, cap, lmean, PA, mode, W):
    d, placed = make_geometry(r, npass, cap, lmean)
    return encrypt(plant_plain(r, PA, d), r, PA, mode, W), len(placed)


def draw_known(r, PA, mode, W):
    d = DSU()
    for a, i, b, j, L in GEOM24:
        for t in range(L):
            d.union((a, i + t), (b, j + t))
    return encrypt(plant_plain(r, PA, d), r, PA, mode, W), 24


# ============================================================================
#  THE GRID
# ============================================================================
NPASS = [8, 12, 16, 20, 26, 34]
CAP = [6, 8, 12, 16, 24]
LMEAN = 26
PA_GRID = [16, 20, 24, 28, 34]
SCHED = [('pos', 28), ('pos', 35), ('con', 30), ('con', 50)]
HELD = 50
SDFLOOR = 0.30


def cells():
    out = []
    for PA in PA_GRID:
        for mode, W in SCHED:
            out.append((0, 0, PA, mode, W))
            for n in NPASS:
                for c in CAP:
                    out.append((n, c, PA, mode, W))
    return out


def label(c):
    n, cap, PA, mode, W = c
    if n == 0:
        return 'the standing 24          PA %-3d %s %d' % (PA, mode, W)
    return '%2d passages , cap %-3d     PA %-3d %s %d' % (n, cap, PA, mode, W)


def score(vec, mu, sd):
    t = 0.0
    for k in range(NOBS):
        z = (vec[k] - mu[k]) / sd[k]
        t += -0.5 * z * z - math.log(sd[k])
    return t - 0.5 * NOBS * math.log(2.0 * math.pi)


def chisq(vec, mu, sd):
    return sum(((vec[k] - mu[k]) / sd[k]) ** 2 for k in range(NOBS))


def cell_one(job):
    c, draws, seed = job
    n, cap, PA, mode, W = c
    r = random.Random(seed)
    vs = []
    pl = 0
    for _ in range(draws):
        if n == 0:
            msgs, k = draw_known(r, PA, mode, W)
        else:
            msgs, k = draw(r, n, cap, LMEAN, PA, mode, W)
        pl += k
        vs.append(observe(msgs))
    mu = [0.0] * NOBS
    sd = [0.0] * NOBS
    for k in range(NOBS):
        col = [v[k] for v in vs]
        m0 = sum(col) / float(len(col))
        var = sum((y - m0) * (y - m0) for y in col) / float(len(col))
        mu[k] = m0
        sd[k] = max(math.sqrt(var), SDFLOOR)
    lobs = score(TARGET, mu, sd)
    own = sorted(score(v, mu, sd) for v in vs)
    le = sum(1 for y in own if y <= lobs)
    return {'c': list(c), 'mu': [round(y, 4) for y in mu],
            'sd': [round(y, 4) for y in sd], 'lobs': lobs,
            'chi': chisq(TARGET, mu, sd),
            'placed': pl / float(draws),
            'p': (le + 1.0) / (len(own) + 1.0),
            'floor': sum(1 for y in sd if y <= SDFLOOR + 1e-9),
            'held': vs[:HELD]}


def runcells(jobs, threads, path):
    import json
    t0 = time.time()
    fh = open(path, 'w')
    if threads > 1:
        import multiprocessing as mp
        pool = mp.Pool(threads)
        it = pool.imap_unordered(cell_one, jobs, chunksize=1)
    else:
        it = (cell_one(j) for j in jobs)
    for n, rec in enumerate(it, 1):
        fh.write(json.dumps(rec)); fh.write('\n')
        if n % 20 == 0 or n == len(jobs):
            fh.flush()
            el = time.time() - t0
            sys.stderr.write('  cell %d / %d   %.0f s elapsed , %.0f s left\n'
                             % (n, len(jobs), el,
                                el * (len(jobs) - n) / max(n, 1)))
            sys.stderr.flush()
    if threads > 1:
        pool.close(); pool.join()
    fh.close()


def loadcells(path):
    import json
    out = []
    for line in open(path):
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def cmd_selftest():
    bad = 0

    def chk(name, got, exp):
        ok = got == exp
        print('  %-58s got %-12s expected %-12s %s'
              % (name, repr(got), repr(exp), 'ok' if ok else 'BAD'))
        return 0 if ok else 1

    print('the nine observables are the corpus , exactly')
    v = observe(M)
    bad += chk('all nine', [round(x, 3) for x in v],
               [round(x, 3) for x in TARGET])

    print('')
    print('THE BUILD 1 ERROR THIS BUILD EXISTS TO FIX')
    global TRIES
    keep = TRIES
    row = []
    for T in (3, 40):
        TRIES = T
        row.append(sum(len(make_geometry(random.Random(600 + t), 44, 12, 26)[1])
                       for t in range(5)) / 5.0)
    TRIES = keep
    print('     ( asking for 44 passages : %.1f placed at 3 tries , %.1f at 40 )'
          % (row[0], row[1]))
    bad += chk('the retry budget , not the corpus , set build 1 saturation',
               row[1] > row[0] * 1.3, True)

    print('')
    print('the generator does what it says')
    d, placed = make_geometry(random.Random(4), 16, 12, 26)
    bad += chk('sixteen requested , most placed', len(placed) >= 14, True)
    ok = True
    for spots, L in placed:
        a0, p0 = spots[0]
        for m, p in spots[1:]:
            for t in range(L):
                if d.find((a0, p0 + t)) != d.find((m, p + t)):
                    ok = False
    bad += chk('every placement of a passage is in one class', ok, True)
    for cap in CAP:
        d2, _ = make_geometry(random.Random(9), 30, cap, 26)
        size = collections.Counter()
        for m in range(9):
            for p in range(LENS[m]):
                size[d2.find((m, p))] += 1
        bad += chk('cap %d is honoured' % cap, max(size.values()) <= cap, True)

    print('')
    print('the mechanism forbids these , so they are asserted')
    lo = sum(observe(draw(random.Random(80 + t), 8, 12, 26, 20, 'pos', 35)[0])[0]
             for t in range(4)) / 4.0
    hi = sum(observe(draw(random.Random(80 + t), 34, 12, 26, 20, 'pos', 35)[0])[0]
             for t in range(4)) / 4.0
    bad += chk('more passages give more relations', hi > lo * 1.5, True)
    print('     ( 8 passages gave %.1f , 34 gave %.1f , the corpus has 24 )'
          % (lo, hi))
    a = sum(observe(draw(random.Random(70 + t), 20, 6, 26, 20, 'pos', 35)[0])[7]
            for t in range(4)) / 4.0
    b = sum(observe(draw(random.Random(70 + t), 20, 24, 26, 20, 'pos', 35)[0])[7]
            for t in range(4)) / 4.0
    print('     ( coverage at cap 6 %.0f , at cap 24 %.0f , the corpus 439 )'
          % (a, b))

    print('')
    print('the standing geometry still misses , as build 1 found')
    m3 = sum(observe(draw_known(random.Random(70 + t), 28, 'con', 30)[0])[0]
             for t in range(5)) / 5.0
    print('     ( the standing 24 yields %.1f relations , the corpus 24 )' % m3)
    bad += chk('it still misses by more than double', m3 < 12.0, True)

    print('')
    print('the score is only used where it is valid')
    mu = [float(y) for y in TARGET]
    bad += chk('a family that misses loses to one that does not',
               score(TARGET, mu, [1.0] * NOBS) > score([y + 3 for y in TARGET],
                                                       mu, [1.0] * NOBS), True)
    bad += chk('chi square of a perfect fit is zero',
               round(chisq(TARGET, mu, [1.0] * NOBS), 6), 0.0)
    bad += chk('and of a three sigma miss on all nine is 81',
               round(chisq([y + 3 for y in TARGET], mu, [1.0] * NOBS), 6), 81.0)

    print('')
    bad += chk('cells', len(cells()),
               len(PA_GRID) * len(SCHED) * (1 + len(NPASS) * len(CAP)))

    print('')
    print('SELFTEST %s   %d bad' % ('PASSED' if bad == 0 else 'FAILED', bad))
    return bad


def cmd_speed(threads, draws):
    t0 = time.time()
    for i in range(8):
        observe(draw(random.Random(900 + i), 20, 12, 26, 24, 'con', 30)[0])
    per = (time.time() - t0) / 8.0
    print('  one simulated corpus , all nine observables   %.3f s' % per)
    eff = 1.0
    if threads > 1:
        import multiprocessing as mp
        pool = mp.Pool(threads)
        probe = [((20, 12, 24, 'con', 30), 8, 950 + i) for i in range(threads)]
        t0 = time.time()
        for _ in pool.imap_unordered(cell_one, probe, chunksize=1):
            pass
        wall = time.time() - t0
        pool.close(); pool.join()
        ideal = len(probe) * 8 * per / float(threads)
        eff = ideal / wall if wall > 0 else 1.0
        print('  EFFICIENCY %.2f' % eff)
        if eff < 0.05:
            eff = 0.05
    nc = len(cells())
    print('')
    print('  %-8s %-12s %s' % ('draws', 'corpora', 'wall clock at %d threads'
                               % threads))
    for n in (500, 1000, 2000, 4000):
        w = nc * n * per / max(threads, 1) / eff
        print('  %-8d %-12d %s'
              % (n, nc * n, ('%.1f min' % (w / 60.0)) if w < 7200
                 else ('%.1f hours' % (w / 3600.0))))
    w = nc * draws * per / max(threads, 1) / eff
    print('')
    print('  --draws %d over %d cells is %d corpora , about %s'
          % (draws, nc, nc * draws,
             ('%.1f min' % (w / 60.0)) if w < 7200
             else ('%.1f hours' % (w / 3600.0))))


def cmd_run(threads, draws, path):
    cs = cells()
    print('simulating %d cells of %d draws , %d corpora , on %d threads'
          % (len(cs), draws, len(cs) * draws, threads))
    jobs = [(c, draws, 51000 + 71 * i) for i, c in enumerate(cs)]
    runcells(jobs, threads, path)
    cmd_report(path)


def cmd_report(path):
    recs = loadcells(path)
    if not recs:
        print('no cells in %s' % path)
        return
    for r0 in recs:
        r0['c'] = tuple(r0['c'])
    fam = [r0 for r0 in recs if r0['c'][0] != 0]
    ref = [r0 for r0 in recs if r0['c'][0] == 0]
    fam.sort(key=lambda r0: r0['chi'])
    ref.sort(key=lambda r0: r0['chi'])
    by = dict((r0['c'], r0) for r0 in recs)

    print('')
    print('=' * 78)
    print('RULE 14 - HOW MANY CELLS ARE THE SAME MODEL')
    print('=' * 78)
    seen = set(); groups = []
    for i, a in enumerate(recs):
        if a['c'] in seen:
            continue
        grp = [a['c']]; seen.add(a['c'])
        for b in recs[i + 1:]:
            if b['c'] in seen:
                continue
            if all(abs(a['mu'][k] - b['mu'][k]) <
                   0.2 * max(a['sd'][k], b['sd'][k]) for k in range(NOBS)):
                grp.append(b['c']); seen.add(b['c'])
        groups.append(grp)
    groups.sort(key=len, reverse=True)
    print('  %d cells collapse into %d distinguishable models , largest group %d'
          % (len(recs), len(groups), len(groups[0])))

    print('')
    print('=' * 78)
    print('GOODNESS OF FIT  -  nine observables , a typical draw scores 9')
    print('=' * 78)
    print('  build 1 ranked by support and put the standing geometry first while')
    print('  it fitted worst .  support charges a family for carrying geometry')
    print('  uncertainty that a point hypothesis does not carry , so it is not')
    print('  used across those two kinds here .  chi square leads.')
    print('')
    print('  %-42s %-8s %-8s %-8s %s'
          % ('geometry', 'chi2', 'fit p', 'placed', 'rel mr3 / mr2 / m35'))
    print('')
    for r0 in fam[:20]:
        print('  %-42s %-8.1f %-8.4f %-8.1f %.1f / %.1f / %.1f'
              % (label(r0['c']), r0['chi'], r0['p'], r0['placed'],
                 r0['mu'][0], r0['mu'][1], r0['mu'][4]))
    print('  . . .')
    for r0 in fam[-2:]:
        print('  %-42s %-8.1f %-8.4f %-8.1f %.1f / %.1f / %.1f'
              % (label(r0['c']), r0['chi'], r0['p'], r0['placed'],
                 r0['mu'][0], r0['mu'][1], r0['mu'][4]))
    print('')
    print('  THE STANDING 24 , REPORTED BESIDE THEM RATHER THAN ABOVE THEM')
    for r0 in ref[:5]:
        print('  %-42s %-8.1f %-8.4f %-8.1f %.1f / %.1f / %.1f'
              % (label(r0['c']), r0['chi'], r0['p'], r0['placed'],
                 r0['mu'][0], r0['mu'][1], r0['mu'][4]))
    print('    best standing chi square %.1f , best generated %.1f'
          % (ref[0]['chi'], fam[0]['chi']))

    print('')
    print('=' * 78)
    print('THE FULL GRID  ( rule 11 )  -  chi square , best over alphabet')
    print('=' * 78)
    for mode, W in SCHED:
        print('')
        print('  %s %d' % (mode, W))
        print('  %-10s %s' % ('passages', ' '.join('%9s' % ('cap %d' % c)
                                                   for c in CAP)))
        for n in NPASS:
            row = []
            for c in CAP:
                v = min(by[(n, c, PA, mode, W)]['chi'] for PA in PA_GRID)
                row.append('%9.1f' % v)
            print('  %-10d %s' % (n, ' '.join(row)))

    print('')
    print('=' * 78)
    print('WHAT REJECTS EACH GEOMETRY , in sigma')
    print('=' * 78)
    print('  %-34s %s' % ('geometry', ' '.join('%9s' % n for n in OBSNAME)))
    shown = set()
    for r0 in fam + ref:
        k = r0['c'][0]
        if k in shown:
            continue
        shown.add(k)
        z = [(TARGET[q] - r0['mu'][q]) / r0['sd'][q] for q in range(NOBS)]
        print('  %-34s %s' % (label(r0['c'])[:34],
                              ' '.join('%+9.1f' % y for y in z)))

    print('')
    print('=' * 78)
    print('THE GATE - plant a KNOWN geometry , see what comes back')
    print('=' * 78)
    mus = [(r0['c'], r0['mu'], r0['sd']) for r0 in fam]

    def marg(v, idx, levels):
        sc = [(score(v, mu, sd), c) for c, mu, sd in mus]
        b = max(x[0] for x in sc)
        t = dict((l, 0.0) for l in levels)
        for s0, c0 in sc:
            t[c0[idx]] = t.get(c0[idx], 0.0) + math.exp(max(s0 - b, -700.0))
        tt = sum(t.values()) or 1.0
        return dict((k, x / tt) for k, x in t.items())

    for idx, levels, nm in ((0, NPASS, 'passages'), (1, CAP, 'class cap')):
        print('')
        print('  %-14s %-16s %s' % ('planted ' + nm, 'recovered mean', 'rank'))
        agg = {}
        for r0 in fam:
            if not r0.get('held'):
                continue
            key = r0['c'][idx]
            for v in r0['held'][:8]:
                t = marg(v, idx, levels)
                pm = sum(k * q for k, q in t.items())
                order = sorted(t, key=lambda k: -t[k])
                a = agg.setdefault(key, [[], []])
                a[0].append(pm); a[1].append(order.index(key) + 1)
        for lv in levels:
            if lv not in agg:
                continue
            pm, rk = agg[lv]
            pm.sort(); rk.sort()
            print('  %-14s %-16.2f %d of %d'
                  % (lv, pm[len(pm) // 2], rk[len(rk) // 2], len(levels)))
        t = marg(TARGET, idx, levels)
        print('  %-14s %-16.2f' % ('THE CORPUS',
                                   sum(k * q for k, q in t.items())))
        for k in sorted(t):
            if t[k] > 0.02:
                print('      %-6s %5.1f %%%s' % (k, 100.0 * t[k],
                                                 '  ' + '#' * int(40 * t[k])))
        print('  ( if the corpus sits above the highest planted calibration')
        print('  point , the grid still stops before the answer does )')


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
                opt('--out', 'eye_infer2_cells.txt', str))
    elif cmd == 'report':
        cmd_report(opt('--out', 'eye_infer2_cells.txt', str))
    else:
        print('commands : version , selftest , speed , run , report')
        print('')
        print('  python eye_infer2.py version')
        print('  python eye_infer2.py selftest')
        print('  python eye_infer2.py speed --threads 32 --draws 2000')
        print('  python eye_infer2.py run --threads 32 --draws 2000')
        print('  python eye_infer2.py report')


if __name__ == '__main__':
    main()
