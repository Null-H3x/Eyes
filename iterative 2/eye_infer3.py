#!/usr/bin/env python
import sys, os, math, random, collections, time
VERSION = "eye_infer build 3 , 22 August 2026"
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
GRP = {0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1, 6: 2, 7: 2, 8: 2}
NSYM = 83
TRIES = 40

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


NOBS = 11
TARGET = [24.0, 37.0, 12.0, 0.0, 6.0, 25.625, 615.0, 439.0, 596.0,
          0.8333, 0.6216]
OBSNAME = ['rel mr3', 'rel mr2', 'rel mr4', 'm35 mr3', 'm35 mr2',
           'mean len', 'total len', 'cover mr3', 'cover mr2',
           'within3', 'within2']


def wfrac(rel):
    """
    the fraction of relations joining two messages of the same prefix triplet .
    the corpus runs 0 . 83 at minrep 3 and 0 . 62 at minrep 2 , against 0 . 25
    from placing passages uniformly over nine messages .  build 2 placed them
    uniformly and overshot messages 3 and 5 by two to four times ; this is that
    error made into a measured observable rather than an inferred one.
    """
    if not rel:
        return 0.0
    return sum(1 for k, L, a, i, b, j in rel
               if GRP[a] == GRP[b]) / float(len(rel))


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
            float(sum(x[1] for x in r3)), float(cov(r3)), float(cov(r2)),
            wfrac(r3), wfrac(r2)]


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


def make_geometry(r, npass, cap, lmean, within, alpha):
    """
    within is the chance a passage is placed inside ONE prefix triplet .  build 2
    had no such parameter and placed uniformly , which puts 0 . 25 of its pairs
    inside a triplet by chance where the corpus runs 0 . 62 to 0 . 83.

    the cap is enforced by snapshot and rollback rather than a per offset
    projection , because two offsets of one passage can touch the same existing
    class and each projection then sees only its own share of the growth.
    """
    # the three triplets do not share equally - the corpus's middle triplet
    # carries almost none at minrep 3 - so the group weights are drawn from a
    # Dirichlet with concentration alpha rather than fixed .  large alpha is
    # uniform , small alpha concentrates on a random subset .  which groups are
    # heavy is left to the draw rather than fitted , because fitting it would
    # be assuming the answer.
    gw = [r.gammavariate(alpha, 1.0) + 1e-9 for _ in range(3)]
    gt = sum(gw)
    gw = [x / gt for x in gw]
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
        if len(cand) < 2:
            continue
        if r.random() < within:
            u2 = r.random(); g = 0; acc = 0.0
            for gg in range(3):
                acc += gw[gg]
                if u2 <= acc:
                    g = gg; break
            pool = [m for m in cand if GRP[m] == g]
            if len(pool) < 2:
                pool = cand
        else:
            pool = cand
        k = min(k, len(pool))
        msgs = r.sample(pool, k)
        spots = [(m, r.randrange(LENS[m] - L)) for m in msgs]
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


def draw(r, npass, cap, lmean, PA, mode, W, within, alpha):
    d, placed = make_geometry(r, npass, cap, lmean, within, alpha)
    return encrypt(plant_plain(r, PA, d), r, PA, mode, W), len(placed)


def draw_known(r, PA, mode, W):
    d = DSU()
    for a, i, b, j, L in GEOM24:
        for t in range(L):
            d.union((a, i + t), (b, j + t))
    return encrypt(plant_plain(r, PA, d), r, PA, mode, W), 24


NPASS = [12, 16, 20, 26]
CAP = [8, 12, 16]
WITHIN = [0.5, 0.7, 0.85, 1.0]
ALPHA = [3.0, 1.0, 0.3, 0.1]
LMEAN = 26
PA_GRID = [28, 34]
SCHED = [('con', 30), ('con', 50)]
HELD = 40
SDFLOOR = 0.02


def cells():
    out = []
    for PA in PA_GRID:
        for mode, W in SCHED:
            out.append((0, 0, 0.0, 0.0, PA, mode, W))
            for n in NPASS:
                for c in CAP:
                    for wi in WITHIN:
                        for al in ALPHA:
                            out.append((n, c, wi, al, PA, mode, W))
    return out


def label(c):
    n, cap, wi, al, PA, mode, W = c
    if n == 0:
        return 'the standing 24                    PA %-3d %s %d' % (PA, mode, W)
    return '%2d pass cap %-3d within %.2f alpha %.1f PA %-3d %s %d' % (
        n, cap, wi, al, PA, mode, W)


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
    n, cap, wi, al, PA, mode, W = c
    r = random.Random(seed)
    vs = []
    pl = 0
    for _ in range(draws):
        if n == 0:
            msgs, k = draw_known(r, PA, mode, W)
        else:
            msgs, k = draw(r, n, cap, LMEAN, PA, mode, W, wi, al)
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
    return {'c': list(c), 'mu': [round(y, 4) for y in mu],
            'sd': [round(y, 4) for y in sd],
            'lobs': score(TARGET, mu, sd), 'chi': chisq(TARGET, mu, sd),
            'placed': pl / float(draws),
            'p': (sum(1 for v in vs if score(v, mu, sd) <=
                      score(TARGET, mu, sd)) + 1.0) / (len(vs) + 1.0),
            'held': vs[:HELD]}


def cmd_selftest():
    bad = 0

    def chk(name, got, exp):
        ok = got == exp
        print('  %-56s got %-13s expected %-13s %s'
              % (name, repr(got), repr(exp), 'ok' if ok else 'BAD'))
        return 0 if ok else 1

    print('the eleven observables are the corpus , exactly')
    v = observe(M)
    bad += chk('all eleven', [round(x, 3) for x in v],
               [round(x, 3) for x in TARGET])
    print('     ( within a triplet : 0 . 833 at minrep 3 , 0 . 622 at minrep 2 ,')
    print('     against 0 . 25 from placing passages uniformly )')

    print('')
    print('THE TWO NEW PARAMETERS MOVE WHAT THEY SHOULD')
    lo = sum(observe(draw(random.Random(60 + t), 16, 12, 26, 28, 'con', 30,
                          0.25, 3.0)[0])[9] for t in range(5)) / 5.0
    hi = sum(observe(draw(random.Random(60 + t), 16, 12, 26, 28, 'con', 30,
                          1.0, 3.0)[0])[9] for t in range(5)) / 5.0
    bad += chk('within raises the within triplet fraction', hi > lo + 0.25, True)
    print('     ( within 0 . 25 gave %.2f , within 1 . 00 gave %.2f , corpus 0 . 83 )'
          % (lo, hi))
    a = sum(observe(draw(random.Random(70 + t), 16, 12, 26, 28, 'con', 30,
                         0.85, 3.0)[0])[4] for t in range(5)) / 5.0
    b = sum(observe(draw(random.Random(70 + t), 16, 12, 26, 28, 'con', 30,
                         0.85, 0.1)[0])[4] for t in range(5)) / 5.0
    bad += chk('a low alpha concentrates and cuts messages 3 and 5', b < a, True)
    print('     ( alpha 3 . 0 gave %.1f , alpha 0 . 1 gave %.1f , corpus 6 )'
          % (a, b))

    print('')
    print('the standing geometry still misses')
    m3 = sum(observe(draw_known(random.Random(70 + t), 28, 'con', 30)[0])[0]
             for t in range(5)) / 5.0
    print('     ( the standing 24 yields %.1f relations , the corpus 24 )' % m3)
    bad += chk('it still misses by more than double', m3 < 12.0, True)

    print('')
    print('the cap is honoured and the generator is sane')
    for cap in CAP:
        d2, _ = make_geometry(random.Random(9), 26, cap, 26, 0.7, 1.0)
        size = collections.Counter()
        for m in range(9):
            for p in range(LENS[m]):
                size[d2.find((m, p))] += 1
        bad += chk('cap %d is honoured' % cap, max(size.values()) <= cap, True)

    print('')
    print('the score is used where it is valid , and both ways are shown')
    mu = [float(y) for y in TARGET]
    bad += chk('a family that misses loses to one that does not',
               score(TARGET, mu, [1.0] * NOBS) >
               score([y + 3 for y in TARGET], mu, [1.0] * NOBS), True)
    bad += chk('support charges for a wide spread , chi square does not',
               score(TARGET, mu, [1.0] * NOBS) > score(TARGET, mu,
                                                       [9.0] * NOBS) and
               chisq(TARGET, mu, [1.0] * NOBS) == chisq(TARGET, mu,
                                                        [9.0] * NOBS), True)
    print('     ( which is why support ranks the families and chi square is')
    print('     printed beside it , and neither is quoted alone )')

    print('')
    bad += chk('cells', len(cells()), len(PA_GRID) * len(SCHED) *
               (1 + len(NPASS) * len(CAP) * len(WITHIN) * len(ALPHA)))
    print('')
    print('SELFTEST %s   %d bad' % ('PASSED' if bad == 0 else 'FAILED', bad))
    return bad


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


def cmd_speed(threads, draws):
    t0 = time.time()
    for i in range(8):
        observe(draw(random.Random(900 + i), 16, 12, 26, 28, 'con', 30,
                     0.85, 0.3)[0])
    per = (time.time() - t0) / 8.0
    print('  one simulated corpus , eleven observables   %.3f s' % per)
    eff = 1.0
    if threads > 1:
        import multiprocessing as mp
        pool = mp.Pool(threads)
        probe = [((16, 12, 0.85, 0.3, 28, 'con', 30), 8, 950 + i)
                 for i in range(threads)]
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
    for n in (500, 1000, 2000, 4000):
        w = nc * n * per / max(threads, 1) / eff
        print('  draws %-6d %-10d corpora   %s'
              % (n, nc * n, ('%.1f min' % (w / 60.0)) if w < 7200
                 else ('%.1f hours' % (w / 3600.0))))
    w = nc * draws * per / max(threads, 1) / eff
    print('')
    print('  --draws %d over %d cells is %d corpora , about %s'
          % (draws, nc, nc * draws, ('%.1f min' % (w / 60.0)) if w < 7200
             else ('%.1f hours' % (w / 3600.0))))


def cmd_run(threads, draws, path):
    cs = cells()
    print('simulating %d cells of %d draws , %d corpora , on %d threads'
          % (len(cs), draws, len(cs) * draws, threads))
    runcells([(c, draws, 61000 + 83 * i) for i, c in enumerate(cs)],
             threads, path)
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
    b = max(r0['lobs'] for r0 in fam)
    fam.sort(key=lambda r0: -r0['lobs'])
    ref.sort(key=lambda r0: r0['chi'])
    by = dict((r0['c'], r0) for r0 in recs)

    def sup(r0):
        return math.exp(max(r0['lobs'] - b, -700.0))

    def ss(v):
        return '1 . 00' if v > 0.5 else ('1 in %.0f' % (1.0 / v)
                                         if v > 1e-12 else 'below 1e12')

    print('')
    print('=' * 78)
    print('RULE 14')
    print('=' * 78)
    seen = set(); groups = []
    for i, a in enumerate(recs):
        if a['c'] in seen:
            continue
        grp = [a['c']]; seen.add(a['c'])
        for c in recs[i + 1:]:
            if c['c'] in seen:
                continue
            if all(abs(a['mu'][k] - c['mu'][k]) <
                   0.2 * max(a['sd'][k], c['sd'][k]) for k in range(NOBS)):
                grp.append(c['c']); seen.add(c['c'])
        groups.append(grp)
    groups.sort(key=len, reverse=True)
    print('  %d cells , %d distinguishable models , largest group %d'
          % (len(recs), len(groups), len(groups[0])))

    print('')
    print('=' * 78)
    print('RANKED BY SUPPORT AMONG THE GENERATED FAMILIES')
    print('=' * 78)
    print('  support charges for a wide spread and chi square does not , so')
    print('  support ranks and chi square is printed beside it .  the standing')
    print('  24 is a point hypothesis and is judged only by its own fit p.')
    print('')
    print('  %-52s %-11s %-6s %-6s %s'
          % ('geometry', 'support', 'chi2', 'fit p', 'rel3 / m35 / within3'))
    print('')
    for r0 in fam[:22]:
        print('  %-52s %-11s %-6.1f %-6.3f %.1f / %.1f / %.2f'
              % (label(r0['c']), ss(sup(r0)), r0['chi'], r0['p'],
                 r0['mu'][0], r0['mu'][4], r0['mu'][9]))
    print('  . . .')
    for r0 in fam[-2:]:
        print('  %-52s %-11s %-6.1f %-6.3f %.1f / %.1f / %.2f'
              % (label(r0['c']), ss(sup(r0)), r0['chi'], r0['p'],
                 r0['mu'][0], r0['mu'][4], r0['mu'][9]))
    print('')
    print('  THE STANDING 24 , BY ITS OWN FIT P ONLY')
    for r0 in ref:
        print('  %-52s %-11s %-6.1f %-6.3f %.1f / %.1f / %.2f'
              % (label(r0['c']), '-', r0['chi'], r0['p'],
                 r0['mu'][0], r0['mu'][4], r0['mu'][9]))

    print('')
    print('=' * 78)
    print('THE FULL GRID  ( rule 11 )  -  support , best over cap and alphabet')
    print('=' * 78)
    for mode, W in SCHED:
        for al in ALPHA:
            print('')
            print('  %s %d , alpha %.1f' % (mode, W, al))
            print('  %-10s %s' % ('passages', ' '.join('%12s' % ('within %.2f'
                                                                 % w)
                                                       for w in WITHIN)))
            for n in NPASS:
                row = []
                for wi in WITHIN:
                    v = max(sup(by[(n, c, wi, al, PA, mode, W)])
                            for c in CAP for PA in PA_GRID)
                    row.append('%12s' % ss(v).replace(' ', ''))
                print('  %-10d %s' % (n, ' '.join(row)))

    print('')
    print('=' * 78)
    print('WHAT REJECTS EACH , in sigma')
    print('=' * 78)
    print('  %-30s %s' % ('geometry', ' '.join('%9s' % n for n in OBSNAME)))
    for r0 in fam[:6] + ref[:1]:
        z = [(TARGET[q] - r0['mu'][q]) / r0['sd'][q] for q in range(NOBS)]
        print('  %-30s %s' % (label(r0['c'])[:30],
                              ' '.join('%+9.1f' % y for y in z)))

    print('')
    print('=' * 78)
    print('THE GATE')
    print('=' * 78)
    mus = [(r0['c'], r0['mu'], r0['sd']) for r0 in fam]

    def marg(v, idx, levels):
        sc = [(score(v, mu, sd), c) for c, mu, sd in mus]
        bb = max(x[0] for x in sc)
        t = dict((l, 0.0) for l in levels)
        for s0, c0 in sc:
            t[c0[idx]] = t.get(c0[idx], 0.0) + math.exp(max(s0 - bb, -700.0))
        tt = sum(t.values()) or 1.0
        return dict((k, x / tt) for k, x in t.items())

    for idx, levels, nm in ((0, NPASS, 'passages'), (1, CAP, 'class cap'),
                            (2, WITHIN, 'within'), (3, ALPHA, 'alpha')):
        print('')
        print('  %-16s %-16s %s' % ('planted ' + nm, 'recovered', 'rank'))
        agg = {}
        for r0 in fam:
            if not r0.get('held'):
                continue
            key = r0['c'][idx]
            for v in r0['held'][:6]:
                t = marg(v, idx, levels)
                order = sorted(t, key=lambda k: -t[k])
                a = agg.setdefault(key, [[], []])
                a[0].append(sum(k * q for k, q in t.items()))
                a[1].append(order.index(key) + 1)
        for lv in levels:
            if lv not in agg:
                continue
            pm, rk = agg[lv]
            pm.sort(); rk.sort()
            print('  %-16s %-16.3f %d of %d'
                  % (lv, pm[len(pm) // 2], rk[len(rk) // 2], len(levels)))
        t = marg(TARGET, idx, levels)
        print('  %-16s %-16.3f' % ('THE CORPUS',
                                   sum(k * q for k, q in t.items())))
        for k in sorted(t):
            if t[k] > 0.02:
                print('      %-6s %5.1f %%%s' % (k, 100.0 * t[k],
                                                 '  ' + '#' * int(35 * t[k])))


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
                opt('--out', 'eye_infer3_cells.txt', str))
    elif cmd == 'report':
        cmd_report(opt('--out', 'eye_infer3_cells.txt', str))
    else:
        print('commands : version , selftest , speed , run , report')
        print('')
        print('  python eye_infer3.py version')
        print('  python eye_infer3.py selftest')
        print('  python eye_infer3.py speed --threads 32 --draws 2000')
        print('  python eye_infer3.py run --threads 32 --draws 2000')
        print('  python eye_infer3.py report')


if __name__ == '__main__':
    main()
