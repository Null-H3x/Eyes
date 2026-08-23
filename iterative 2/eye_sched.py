#!/usr/bin/env python
# ============================================================================
# eye_sched.py  -  MEASURING THE REDRAW SCHEDULE INSTEAD OF FITTING IT
#
#   python eye_sched.py selftest
#   python eye_sched.py run --threads 32 --sims 900
#   python eye_sched.py report
#
# THE IDEA
#   Report 58 refuted a redraw on a fixed POSITION schedule and named a redraw
#   on plaintext CONTENT as the successor .  The two make opposite predictions
#   about where relations END .
#
#     position schedule   a relation dies when it meets a boundary that is
#                         misaligned between the two messages , so endpoints
#                         pile up at positions congruent to 0 modulo W
#     content schedule    boundaries align between messages carrying the same
#                         passage , so relations die where the SHARING ends and
#                         endpoints carry no positional regularity at all
#
#   So : is there a W modulo which the 96 relation endpoints concentrate ?
#   That measures the schedule rather than fitting a model to it .
#
# WHY THIS IS BUILT THE WAY IT IS
#   Report 53 measured a search of this project to have no resolving power and
#   withdrew three reports' worth of rankings .  The lesson was that a tool must
#   pass a gate before its verdict counts .  So :
#
#     1 . the statistic is the FAMILY WISE maximum over every candidate W , so
#         testing 57 values of W costs nothing extra and no correction is
#         applied or needed
#     2 . the null is GENERATED , not permuted .  two permutation nulls were
#         built first and both were anti conservative - planted content
#         schedules , which carry no lattice at all , came out at p about 0 . 02 .
#         endpoints cluster sharply where the sharing stops and no smooth null
#         reproduces a sharp edge , so a smooth null calls a sharp edge periodic .
#         the null distribution is therefore drawn from simulated CONTENT
#         schedule corpora carrying the corpus's own sharing geometry and its own
#         message lengths , which makes the size correct by construction
#     3 . the run also simulates the POSITION family at nine values of W , so
#         every verdict is printed beside the measured chance of the tool having
#         seen that W had it been there .  a null result at a W the tool cannot
#         see is not evidence , and the table says which those are
# ============================================================================

import sys, os, math, random, collections, time

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
PRE = [25, 25, 25, 6, 6, 6, 21, 21, 21]
M = [RAW[n] for n in ORDER]
LENS = [len(m) for m in M]
WMIN, WMAX = 4, 60
GEOM = [(6, 68, 7, 71, 34), (1, 33, 1, 63, 33), (6, 57, 8, 58, 33),
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


def endpoints(msgs, rel=None):
    """
    the four coordinates of every relation , dropped when they sit against a
    message edge - those are forced by the corpus running out , not by a
    redraw , and including them would manufacture structure.
    """
    if rel is None:
        rel = relations(msgs)
    out = []
    for k, L, a, i, b, j in rel:
        for m, p in ((a, i), (a, i + L), (b, j), (b, j + L)):
            if 2 <= p <= len(msgs[m]) - 3:
                out.append((m, p))
    return out


def rayleigh(pts, W):
    """circular concentration of the endpoint positions modulo W"""
    n = len(pts)
    if n < 4:
        return 0.0
    c = 0.0; s = 0.0
    for m, p in pts:
        th = 2.0 * math.pi * (p % W) / W
        c += math.cos(th); s += math.sin(th)
    return (c * c + s * s) / float(n)


def best_W(pts):
    bw, bz = 0, -1.0
    for W in range(WMIN, WMAX + 1):
        z = rayleigh(pts, W)
        if z > bz:
            bz, bw = z, W
    return bw, bz


def shuffled_points(pts, msgs, r):
    """
    the null : each endpoint moved to a uniformly random position in the SAME
    message , keeping the count per message.  That holds the message lengths
    and the endpoint budget fixed and destroys only the schedule.
    """
    out = []
    for m, p in pts:
        out.append((m, r.randrange(2, len(msgs[m]) - 2)))
    return out


# ============================================================================
#  PLANTING - a corpus whose schedule we know
# ============================================================================
VERSION = 'eye_sched build 5 , 21 August 2026 , relative support'
# ----------------------------------------------------------------------------
# rule 12 .  a tool prints which build it is , on every command , before
# anything else .  four builds of this file were sent in one session and an
# output arrived that was missing a whole section , which cost a round trip to
# diagnose because nothing in the output said which build produced it .  a
# number without a build stamp cannot be attributed , and an un attributable
# number is not evidence.
# ----------------------------------------------------------------------------

PA = 40          # plaintext alphabet , the near uniform size report 57 fixed
NSYM = 83


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


def plant_plain(r):
    """
    a plaintext for all nine messages carrying exactly the sharing geometry the
    corpus has .  positions linked by a relation get the same plaintext letter ,
    everything else is free .  adjacent positions are kept unequal because the
    corpus never repeats a symbol adjacently and that is a property of the
    plaintext , not of the schedule.
    """
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
    keys = list(set(cls.values()))
    r.shuffle(keys)
    val = {}
    for k in keys:
        bad = set()
        for q in nb[k]:
            if q in val:
                bad.add(val[q])
        ch = [c for c in range(PA) if c not in bad]
        val[k] = r.choice(ch)
    return [[val[cls[(m, p)]] for p in range(LENS[m])] for m in range(9)]


def encrypt(plain, r, mode, W=0, trig=None, phase=None):
    """
    mode 'pos'      redraw the bijection whenever position == phase modulo W
    mode 'con'      redraw the bijection whenever the plaintext letter is a
                    trigger - boundaries then follow the CONTENT and align
                    automatically between messages carrying the same passage
    mode 'none'     one bijection per message , no schedule at all
    """
    out = []
    for m in range(9):
        pl = plain[m]
        ph = 0 if phase is None else phase[m]
        sig = r.sample(range(NSYM), PA)
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


def trigger_set(target, r):
    """a trigger set sized so the mean content window is about target"""
    k = max(1, int(round(PA / float(target))))
    return set(r.sample(range(PA), k))


def plant(mode, r, W=0, target=30, randphase=False):
    plain = plant_plain(r)
    phase = [r.randrange(W) for _ in range(9)] if (randphase and W) else None
    trig = trigger_set(target, r) if mode == 'con' else None
    return encrypt(plain, r, mode, W=W, trig=trig, phase=phase)


# ============================================================================
#  STATISTICS
# ============================================================================
MAXP = max(LENS) + 4
WS = list(range(WMIN, WMAX + 1))
CT = {}
ST = {}
for _W in WS:
    CT[_W] = [math.cos(2.0 * math.pi * (p % _W) / _W) for p in range(MAXP)]
    ST[_W] = [math.sin(2.0 * math.pi * (p % _W) / _W) for p in range(MAXP)]


def profile(pts):
    """
    three numbers per candidate W .

      glob   pooled first harmonic .  one shared lattice across all nine
             messages , phase included .  expectation 1 under any null that
             randomises position.
      chi    residue counts against flat .  catches a lattice that piles up on
             more than one residue.
      loc    first harmonic computed inside each message and added .  a lattice
             with a DIFFERENT phase per message still shows here .
             expectation = number of messages with enough points.
    """
    per = collections.defaultdict(list)
    for m, p in pts:
        per[m].append(p)
    n = len(pts)
    g = []; c2 = []; lo = []
    for W in WS:
        ct = CT[W]; st = ST[W]
        c = 0.0; s = 0.0
        cnt = [0] * W
        for m, p in pts:
            c += ct[p]; s += st[p]
            cnt[p % W] += 1
        g.append((c * c + s * s) / n)
        e = n / float(W)
        c2.append(sum((k - e) * (k - e) for k in cnt) / e)
        t = 0.0
        for m in per:
            v = per[m]
            if len(v) < 3:
                continue
            cc = 0.0; ss = 0.0
            for p in v:
                cc += ct[p]; ss += st[p]
            t += (cc * cc + ss * ss) / len(v)
        lo.append(t)
    return g, c2, lo


# ---------------------------------------------------------------- the nulls
#
#   the first diagnostic run of this tool detected a planted schedule at every
#   W and then named the wrong W every time - 15 whether 16 , 32 or 48 was
#   planted .  the reason is that the endpoints sit in a band in the middle of
#   the messages , and against a null that spreads points over the whole message
#   ANY clump is significant .  a band and a lattice are the same measurement at
#   the frequency of the band .
#
#   so the null has to keep the coarse shape and destroy only the fine phase ,
#   and the width at which it does that is not something to pick by taste .  the
#   family below is carried through the gate at several widths and the gate
#   reports the size and the power of each ; only a width that holds its size on
#   planted CONTENT schedules is allowed to speak about the corpus.


def null_uniform(pts, r):
    """
    every endpoint to a uniformly random position in the same message .  keeps
    nothing but the count .  known to conflate the band with a lattice - kept
    only as the floor the others are read against.
    """
    return [(m, r.randrange(2, LENS[m] - 2)) for m, p in pts]


def _reflect(q, m):
    lo = 2; hi = LENS[m] - 3
    for _ in range(8):
        if q < lo:
            q = lo + (lo - q)
        elif q > hi:
            q = hi - (q - hi)
        else:
            return q
    return max(lo, min(hi, q))


def make_jitter(h):
    def f(pts, r):
        return [(m, _reflect(p + int(round(r.gauss(0.0, h))), m))
                for m, p in pts]
    f.__name__ = 'jitter %d' % h
    return f


def null_rotate(pts, r):
    """
    each MESSAGE rigidly rotated by its own random offset .  the geometry inside
    a message survives untouched ; only the phase BETWEEN messages is destroyed .
    the strict null for one lattice shared by all nine messages.
    """
    off = [r.randrange(LENS[m] - 4) for m in range(9)]
    out = []
    for m, p in pts:
        span = LENS[m] - 4
        out.append((m, 2 + (p - 2 + off[m]) % span))
    return out


NULLS = [('unif', null_uniform),
         ('jit06', make_jitter(6)),
         ('jit12', make_jitter(12)),
         ('jit20', make_jitter(20)),
         ('jit30', make_jitter(30)),
         ('rot', null_rotate)]
STATS = ['glob', 'chi', 'loc']


# ============================================================================
#  THE NULL IS A FAMILY , NOT A SHUFFLE
#
#   the first two builds of this tool used permutation nulls and both were
#   anti conservative .  planted CONTENT schedules - which carry no lattice at
#   all - came out significant at p about 0 . 02 .  the reason is structural :
#   endpoints under a content schedule cluster sharply where the sharing stops ,
#   and no amount of jittering reproduces a sharp edge , so any smooth null
#   calls a sharp edge periodic .
#
#   so the null distribution is generated , not permuted .  a corpus is
#   simulated under the CONTENT family with the corpus's own sharing geometry
#   and its own message lengths , and the statistic is read off that .  size is
#   then correct by construction : whatever the sharing geometry does to the
#   endpoints , it does to the null too .
#
#   power and resolution come from simulating the POSITION family at each
#   candidate W and asking how often the statistic clears the critical value
#   the content family sets , and where the true W lands in the ordering.
# ============================================================================
GATE_W = [8, 12, 16, 20, 24, 28, 32, 40, 48]
GATE_T = [18, 30, 50]
ALPHA = 0.05
KEYS = ['g', 'c', 'l']


def sim_one(job):
    kind, W, target, rph, seed = job
    r = random.Random(seed)
    msgs = plant(kind, r, W=W, target=target, randphase=rph)
    rel = relations(msgs)
    pts = endpoints(msgs, rel)
    rec = {'kind': kind, 'W': W, 'target': target, 'rph': rph,
           'n': len(pts), 'nrel': len(rel),
           'mlen': (sum(x[1] for x in rel) / float(len(rel))) if rel else 0.0}
    if len(pts) < 8:
        rec['skip'] = 1
        return rec
    rec['skip'] = 0
    pr = profile(pts)
    for k in range(3):
        rec[KEYS[k]] = [round(x, 4) for x in pr[k]]
    return rec


def runjobs(jobs, threads, path, tag):
    """
    the checkpoint is APPENDED , one record per line.

    the first build rewrote the whole result list at every checkpoint , which
    is quadratic .  measured on the 9970 X : 25500 corpora took 489 s against
    the 329 s the workers alone account for , and about 100 s of that gap was
    the parent process re serialising a list that grew to 35 MB , 127 times
    over .  the thread efficiency was never the problem .  one line per record
    makes it linear , and json rather than repr makes reading it back 47 times
    faster - 0 . 24 s against 11 . 3 s on a 10 MB file.
    """
    import json
    done = []
    t0 = time.time()
    fh = open(path, 'w')
    if threads > 1:
        import multiprocessing as mp
        pool = mp.Pool(threads)
        it = pool.imap_unordered(sim_one, jobs, chunksize=8)
    else:
        it = (sim_one(j) for j in jobs)
    for n, rec in enumerate(it, 1):
        done.append(rec)
        fh.write(json.dumps(rec))
        fh.write('\n')
        if n % 200 == 0 or n == len(jobs):
            fh.flush()
            el = time.time() - t0
            sys.stderr.write('  %s %d / %d   %.0f s elapsed , %.0f s left\n'
                             % (tag, n, len(jobs), el,
                                el * (len(jobs) - n) / max(n, 1)))
            sys.stderr.flush()
    if threads > 1:
        pool.close(); pool.join()
    fh.close()
    return done


def loadsims(path):
    """
    reads either format .  a file that starts with a bracket is the old whole
    list checkpoint and is read with eval ; anything else is one json record
    per line .  a half written final line , from a run stopped with control C ,
    is dropped rather than crashing the report.
    """
    import json
    fh = open(path)
    head = fh.read(2)
    fh.close()
    if head.startswith('['):
        sys.stderr.write('  reading the old whole list checkpoint format ,'
                         ' this is slow\n')
        return eval(open(path).read())
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
        sys.stderr.write('  dropped %d incomplete record , the run was'
                         ' interrupted\n' % bad)
    return out


# ---------------------------------------------------------------- the readout
def calibrate(recs, kinds):
    """mean and spread of every statistic at every W over the null families"""
    nW = len(WS)
    mu = [[0.0] * nW for _ in range(3)]
    sd = [[1e-9] * nW for _ in range(3)]
    sel = [r0 for r0 in recs if not r0.get('skip') and r0['kind'] in kinds]
    if not sel:
        return mu, sd, 0
    for k in range(3):
        for w in range(nW):
            v = [r0[KEYS[k]][w] for r0 in sel]
            m0 = sum(v) / len(v)
            var = sum((x - m0) * (x - m0) for x in v) / len(v)
            mu[k][w] = m0
            sd[k][w] = math.sqrt(var) if var > 1e-12 else 1e-9
    return mu, sd, len(sel)


def zvec(vec, mu, sd, k):
    return [(vec[w] - mu[k][w]) / sd[k][w] for w in range(len(WS))]


def Tstat(vec, mu, sd, k):
    z = zvec(vec, mu, sd, k)
    b = max(z)
    return b, WS[z.index(b)], z


def pctile(v, q):
    if not v:
        return 0.0
    w = sorted(v)
    i = int(q * (len(w) - 1))
    return w[i]


# ============================================================================
#  COMMANDS
# ============================================================================
def cmd_selftest():
    bad = 0

    def chk(name, got, exp, tol=0.0):
        ok = (abs(got - exp) <= tol) if isinstance(exp, float) else (got == exp)
        print('  %-46s got %-22s expected %s   %s'
              % (name, repr(got), repr(exp), 'ok' if ok else 'BAD'))
        return 0 if ok else 1

    print('statistic sanity')
    n = 40
    pts = [(0, 10 + 12 * i) for i in range(n)]
    bad += chk('rayleigh , all points same residue mod 12',
               round(rayleigh(pts, 12), 6), float(n), 1e-6)
    pts2 = [(0, p) for p in range(60)]
    bad += chk('rayleigh , one full sweep of residues mod 12',
               round(rayleigh(pts2, 12), 6), 0.0, 1e-6)
    g, c2, lo = profile(pts2)
    bad += chk('chi square , exactly flat residues mod 12',
               round(c2[WS.index(12)], 6), 0.0, 1e-6)
    bad += chk('profile returns one number per candidate W',
               (len(g), len(c2), len(lo)), (len(WS), len(WS), len(WS)))

    print('')
    print('the diagnostic nulls keep what they promise to keep')
    r = random.Random(1)
    P = endpoints(M)
    for nm, fn in NULLS:
        q = fn(P, r)
        bad += chk('%s keeps every point inside its message' % nm,
                   all(2 <= p <= LENS[m] - 3 for m, p in q), True)
        bad += chk('%s keeps the count per message' % nm,
                   sorted(collections.Counter(m for m, p in q).items()),
                   sorted(collections.Counter(m for m, p in P).items()))
    bad += chk('uniform null expectation of glob is one',
               round(sum(profile(null_uniform(P, r))[0][WS.index(20)]
                         for _ in range(400)) / 400.0, 2), 1.0, 0.25)

    print('')
    print('the simulated corpus really carries the sharing geometry')
    r = random.Random(7)
    pl = plant_plain(r)
    bad += chk('every planted relation shares its plaintext',
               all(pl[a][i + t] == pl[b][j + t]
                   for a, i, b, j, L in GEOM for t in range(L)), True)
    bad += chk('no two adjacent plaintext letters equal',
               sum(1 for m in range(9) for p in range(LENS[m] - 1)
                   if pl[m][p] == pl[m][p + 1]), 0)
    bad += chk('planted plaintext uses the whole alphabet',
               len(set(x for row in pl for x in row)), PA)
    bad += chk('planted message lengths match the corpus',
               [len(x) for x in pl], LENS)

    print('')
    print('encryption is a bijection inside a window and redraws at the edge')
    r = random.Random(11)
    ct = encrypt(pl, r, 'pos', W=25)
    ok = True
    for m in range(9):
        for s0 in range(0, LENS[m], 25):
            mp = {}
            for p in range(s0, min(s0 + 25, LENS[m])):
                if pl[m][p] in mp and mp[pl[m][p]] != ct[m][p]:
                    ok = False
                mp[pl[m][p]] = ct[m][p]
            if len(set(mp.values())) != len(mp):
                ok = False
    bad += chk('one letter one symbol inside every window of 25', ok, True)
    ct2 = encrypt(pl, r, 'none')
    ok2 = True
    for m in range(9):
        mp = {}
        for p in range(LENS[m]):
            if pl[m][p] in mp and mp[pl[m][p]] != ct2[m][p]:
                ok2 = False
            mp[pl[m][p]] = ct2[m][p]
    bad += chk('no schedule means one bijection for a whole message', ok2, True)
    bad += chk('ciphertext stays inside the 83 symbols',
               max(max(row) for row in ct) < NSYM and
               min(min(row) for row in ct) >= 0, True)
    r = random.Random(13)
    pl2 = plant_plain(r)
    trig = trigger_set(6, r)
    a, i, b, j, L = GEOM[0]
    cut_a = [t for t in range(1, L) if pl2[a][i + t] in trig]
    cut_b = [t for t in range(1, L) if pl2[b][j + t] in trig]
    bad += chk('a content schedule cuts somewhere in the shared passage',
               len(cut_a) >= 3, True)
    bad += chk('and puts those cuts at the SAME place in both messages',
               cut_a, cut_b)
    ph = [11, 3, 7, 0, 5, 2, 9, 1, 4]
    cp = encrypt(pl2, r, 'pos', W=20, phase=ph)
    off = []
    for m in range(9):
        seen = {}
        brk = 0
        for p in range(LENS[m]):
            if p and (p - ph[m]) % 20 == 0:
                brk = p
            key = (pl2[m][p], brk)
            if key in seen and seen[key] != cp[m][p]:
                off.append(m)
                break
            seen[key] = cp[m][p]
    bad += chk('a per message phase moves the cuts and nothing else', off, [])

    print('')
    print('the corpus itself')
    rel = relations(M)
    bad += chk('relations recovered from the raw corpus', len(rel), 24)
    bad += chk('geometry matches the stored table',
               sorted((a, i, b, j, L) for k, L, a, i, b, j in rel),
               sorted(GEOM))
    bad += chk('endpoints extracted', len(endpoints(M, rel)), 96)

    print('')
    print('the readout is arithmetic , not opinion')
    fake = [{'kind': 'con', 'skip': 0, 'g': [1.0] * len(WS),
             'c': [1.0] * len(WS), 'l': [1.0] * len(WS)},
            {'kind': 'con', 'skip': 0, 'g': [3.0] * len(WS),
             'c': [3.0] * len(WS), 'l': [3.0] * len(WS)}]
    mu, sd, nn = calibrate(fake, ('con',))
    bad += chk('calibration mean of 1 and 3', round(mu[0][0], 6), 2.0, 1e-9)
    bad += chk('calibration spread of 1 and 3', round(sd[0][0], 6), 1.0, 1e-9)
    t, w, z = Tstat([4.0] * len(WS), mu, sd, 0)
    bad += chk('a value two above the mean scores z two', round(t, 6), 2.0, 1e-9)
    bad += chk('the 95th percentile of 0 . . 99', pctile(list(range(100)), 0.95),
               94)

    print('')
    print('SELFTEST %s   %d bad' % ('PASSED' if bad == 0 else 'FAILED', bad))
    return bad


def build_jobs(sims):
    jobs = []
    sd = 100000
    for T in GATE_T:
        for d in range(sims):
            sd += 1
            jobs.append(('con', 0, T, False, sd))
    for d in range(sims):
        sd += 1
        jobs.append(('none', 0, 0, False, sd))
    for W in GATE_W:
        for d in range(max(1, sims // 3)):
            sd += 1
            jobs.append(('pos', W, 0, False, sd))
        for d in range(max(1, sims // 6)):
            sd += 1
            jobs.append(('pos', W, 0, True, sd))
    return jobs


def cmd_run(threads, sims, path):
    jobs = build_jobs(sims)
    print('simulating %d corpora on %d threads' % (len(jobs), threads))
    print('  content family   %d' % sum(1 for j in jobs if j[0] == 'con'))
    print('  no schedule      %d' % sum(1 for j in jobs if j[0] == 'none'))
    print('  position family  %d' % sum(1 for j in jobs if j[0] == 'pos'))
    recs = runjobs(jobs, threads, path, 'sim')
    cmd_report(path)
    return recs


def cmd_report(path):
    recs = loadsims(path)
    mu, sd, nnull = calibrate(recs, ('con', 'none'))
    con = [r0 for r0 in recs if not r0.get('skip') and r0['kind'] in ('con', 'none')]
    pos = [r0 for r0 in recs if not r0.get('skip') and r0['kind'] == 'pos']
    nsk = sum(1 for r0 in recs if r0.get('skip'))

    print('')
    print('=' * 74)
    print('CALIBRATION')
    print('=' * 74)
    print('  simulated corpora            %d' % len(recs))
    print('  too few relations to score   %d' % nsk)
    print('  null family draws used       %d' % nnull)
    print('')
    print('  relations produced , against the %d the corpus has' % len(relations(M)))
    for kind, lab in (('con', 'content schedule'), ('none', 'no schedule')):
        v = [r0['nrel'] for r0 in recs if r0['kind'] == kind]
        u = [r0['mlen'] for r0 in recs if r0['kind'] == kind and r0['nrel']]
        if v:
            print('    %-18s %6.1f relations , mean length %5.1f'
                  % (lab, sum(v) / len(v), sum(u) / max(len(u), 1)))
    agg = {}
    for r0 in pos:
        if r0['rph']:
            continue
        a, b, c = agg.get(r0['W'], (0.0, 0.0, 0))
        agg[r0['W']] = (a + r0['nrel'], b + r0['mlen'], c + 1)
    for W in GATE_W:
        if W in agg:
            a, b, c = agg[W]
            print('    position W %-3d     %6.1f relations , mean length %5.1f'
                  % (W, a / c, b / c))
    print('')
    print('  the same as a demand on the plaintext .  a family that recovers')
    print('  only part of what was planted needs that much MORE sharing to')
    print('  show the %d relations the corpus has.' % len(relations(M)))
    nrel = float(len(relations(M)))
    rows = []
    for kind, W, lab in ([('none', 0, 'no schedule'),
                          ('con', 0, 'content schedule')] +
                         [('pos', W, 'position W %d' % W) for W in GATE_W]):
        v = [r0['nrel'] for r0 in recs
             if r0['kind'] == kind and r0['W'] == W and not r0['rph']]
        if v:
            rows.append((nrel / max(sum(v) / len(v), 0.01), lab,
                         sum(v) / len(v)))
    rows.sort()
    for ratio, lab, got in rows:
        print('    %-22s %5.1f of %2.0f recovered   %5.1f x sharing needed'
              % (lab, got, nrel, ratio))

    print('')
    print('=' * 74)
    print('THE GATE - can this instrument tell the two families apart at all')
    print('=' * 74)
    for k in range(3):
        nullT = [Tstat(r0[KEYS[k]], mu, sd, k)[0] for r0 in con]
        crit = pctile(nullT, 1.0 - ALPHA)
        print('')
        print('  statistic %s   critical value %.2f from %d null draws'
              % (STATS[k], crit, len(nullT)))
        print('  %-8s %-10s %-14s %s' % ('planted', 'detected', 'named W',
                                         'true W median rank of %d' % len(WS)))
        for rph in (False, True):
            if rph:
                print('    with a different window phase in every message')
            for W in GATE_W:
                sel = [r0 for r0 in pos if r0['W'] == W and r0['rph'] == rph]
                if not sel:
                    continue
                hit = 0; named = 0; ranks = []
                for r0 in sel:
                    t, w, z = Tstat(r0[KEYS[k]], mu, sd, k)
                    if t >= crit:
                        hit += 1
                        if abs(w - W) <= 1:
                            named += 1
                    order = sorted(range(len(WS)), key=lambda q: -z[q])
                    ranks.append(order.index(WS.index(W)) + 1 if W in WS else -1)
                ranks.sort()
                print('    W %-4d %5d / %-4d %5.0f %%   %5.0f %%        %6.0f'
                      % (W, hit, len(sel), 100.0 * hit / len(sel),
                         100.0 * named / len(sel), ranks[len(ranks) // 2]))

    print('')
    print('=' * 74)
    print('THE CORPUS')
    print('=' * 74)
    pts = endpoints(M)
    pr = profile(pts)
    print('  %d endpoints from %d relations' % (len(pts), len(relations(M))))
    print('')
    for k in range(3):
        nullT = [Tstat(r0[KEYS[k]], mu, sd, k)[0] for r0 in con]
        crit = pctile(nullT, 1.0 - ALPHA)
        t, w, z = Tstat(pr[k], mu, sd, k)
        ge = sum(1 for x in nullT if x >= t)
        p = (ge + 1.0) / (len(nullT) + 1.0)
        print('  %-6s  score %+6.2f at W %-3d   critical %+5.2f   p %.4f  %s'
              % (STATS[k], t, w, crit, p,
                 'SIGNIFICANT' if p <= ALPHA else 'not significant'))
    print('')
    print('  THE CORPUS READ AS A POSITION IN EACH PLANTED FAMILY')
    print('  the fraction of that family scoring as LOW as the corpus does .')
    print('  a small number means the corpus does not look like that family.')
    print('')
    tobs = Tstat(pr[0], mu, sd, 0)[0]
    print('  %-30s %-10s %-14s %s'
          % ('family', 'p', 'family median', 'draws'))

    def famblock(sel, lab):
        v = [Tstat(r0[KEYS[0]], mu, sd, 0)[0] for r0 in sel if not r0.get('skip')]
        if not v:
            return None
        le = sum(1 for x in v if x <= tobs)
        print('  %-30s %.4f     %+6.2f         %d'
              % (lab, (le + 1.0) / (len(v) + 1.0), pctile(v, 0.5), len(v)))
        return v

    famblock([r0 for r0 in recs if r0['kind'] == 'none'], 'no schedule at all')
    famblock([r0 for r0 in recs if r0['kind'] == 'con'], 'content schedule')
    for rph in (False, True):
        if rph:
            print('  ---- a different window phase in every message ----')
        for W in GATE_W:
            famblock([r0 for r0 in recs if r0['kind'] == 'pos'
                      and r0['W'] == W and r0['rph'] == rph],
                     'position W %d' % W)
    print('')
    print('  RELATIVE SUPPORT , which family the corpus actually looks like')
    print('  ( if this section is missing , you are running an older build )')
    print('  the height of each family at the corpus score , divided by the')
    print('  height of the best supported family .  a tail p answers is the')
    print('  corpus extreme for this family ; this answers which family is')
    print('  likeliest to have produced it , which is the question.')
    print('')
    H = 0.45

    def dens(sel):
        v = [Tstat(r0[KEYS[0]], mu, sd, 0)[0] for r0 in sel
             if not r0.get('skip')]
        if len(v) < 30:
            return None, 0
        acc = 0.0
        for x in v:
            u = (x - tobs) / H
            if u * u < 50.0:
                acc += math.exp(-0.5 * u * u)
        return acc / (len(v) * H * math.sqrt(2.0 * math.pi)), len(v)

    fams = [('no schedule at all',
             [r0 for r0 in recs if r0['kind'] == 'none']),
            ('content schedule',
             [r0 for r0 in recs if r0['kind'] == 'con'])]
    for rph in (False, True):
        for W in GATE_W:
            fams.append(('position W %d%s' % (W, ' , phase per message'
                                              if rph else ''),
                         [r0 for r0 in recs if r0['kind'] == 'pos'
                          and r0['W'] == W and r0['rph'] == rph]))
    got = []
    for lab, sel in fams:
        d, n = dens(sel)
        if d is not None:
            got.append((d, lab, n))
    if got:
        top = max(g0[0] for g0 in got)
        got.sort(reverse=True)
        for d, lab, n in got:
            if top <= 0:
                break
            rr = d / top
            print('    %-38s %s'
                  % (lab, ('1 . 00 , best supported' if rr > 0.999 else
                           ('1 in %.0f' % (1.0 / rr)) if rr > 1e-9 else
                           'below 1 in a billion')))

    pool = [r0 for r0 in recs if r0['kind'] == 'pos' and not r0['rph']
            and r0['W'] in (16, 20, 24, 28, 32)]
    v = [Tstat(r0[KEYS[0]], mu, sd, 0)[0] for r0 in pool if not r0.get('skip')]
    if v:
        le = sum(1 for x in v if x <= tobs)
        print('')
        print('  POOLED shared lattice W 16 to 32 : p %.5f over %d draws'
              % ((le + 1.0) / (len(v) + 1.0), len(v)))
        print('  this is the band the gate above shows the tool can actually')
        print('  see .  outside it a null result is not evidence.')

    k = 0
    t, w, z = Tstat(pr[k], mu, sd, k)
    order = sorted(range(len(WS)), key=lambda q: -z[q])
    print('')
    print('  the ten best supported window widths , pooled first harmonic')
    for q in order[:10]:
        pw = [r0 for r0 in pos if r0['W'] == WS[q] and not r0['rph']]
        det = ''
        if pw:
            nullT = [Tstat(r0[KEYS[0]], mu, sd, 0)[0] for r0 in con]
            crit = pctile(nullT, 1.0 - ALPHA)
            h = sum(1 for r0 in pw
                    if Tstat(r0[KEYS[0]], mu, sd, 0)[0] >= crit)
            det = '   this W is detectable %.0f %% of the time' % (
                100.0 * h / len(pw))
        print('    W %-4d score %+6.2f%s' % (WS[q], z[q], det))


def cmd_speed(threads, sims):
    """
    rule 6 . time the real inner loop on the real machine and extrapolate ,
    rather than quoting a number measured somewhere else.
    """
    print('timing the real simulation loop on this machine')
    print('')
    t0 = time.time()
    for i in range(8):
        sim_one(('con', 0, 30, False, 90000 + i))
    a = (time.time() - t0) / 8.0
    t0 = time.time()
    for i in range(8):
        sim_one(('pos', 24, 0, False, 91000 + i))
    b = (time.time() - t0) / 8.0
    print('  one content family corpus    %.3f s' % a)
    print('  one position family corpus   %.3f s' % b)
    per = (a + b) / 2.0
    eff = 1.0
    if threads > 1:
        import multiprocessing as mp
        probe = [('con', 0, 30, False, 92000 + i) for i in range(threads * 4)]
        pool = mp.Pool(threads)
        t0 = time.time()
        for _ in pool.imap_unordered(sim_one, probe, chunksize=1):
            pass
        wall = time.time() - t0
        pool.close(); pool.join()
        ideal = len(probe) * per / float(threads)
        eff = ideal / wall if wall > 0 else 1.0
        print('')
        print('  %d corpora across %d workers took %.1f s , against %.1f s if'
              % (len(probe), threads, wall, ideal))
        print('  the threads scaled perfectly .  MEASURED EFFICIENCY %.2f .'
              % eff)
        print('  this times the WORKERS only .  it excludes the cost of')
        print('  starting them , which on Windows spawns a fresh interpreter')
        print('  per worker , and the cost of writing the checkpoint.')
        if eff < 0.05:
            eff = 0.05
    print('')
    print('  %-10s %-10s %-14s %s' % ('sims', 'corpora', 'core seconds',
                                      'wall clock at %d threads' % threads))
    for n in (100, 300, 900, 3000, 9000):
        c = len(build_jobs(n))
        tot = c * per
        w = tot / max(threads, 1) / eff
        print('  %-10d %-10d %-14.0f %s'
              % (n, c, tot,
                 ('%.0f s' % w) if w < 120 else ('%.1f min' % (w / 60.0))))
    print('')
    c = len(build_jobs(sims))
    w = c * per / max(threads, 1) / eff
    print('  the run you asked about : --sims %d is %d corpora , about %s'
          % (sims, c, ('%.0f s' % w) if w < 120 else ('%.1f min' % (w / 60.0))))
    print('  null draws %d , smallest reportable p %.5f'
          % (sims * (len(GATE_T) + 1),
             1.0 / (sims * (len(GATE_T) + 1) + 1.0)))


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
    elif cmd in ('run', 'verify', 'scan'):
        cmd_run(opt('--threads', 32), opt('--sims', 3000),
                opt('--out', 'eye_sched_sims.txt', str))
    elif cmd == 'speed':
        cmd_speed(opt('--threads', 32), opt('--sims', 3000))
    elif cmd == 'report':
        cmd_report(opt('--out', 'eye_sched_sims.txt', str))
    else:
        print('commands : version , selftest , speed , run , report')
        print('')
        print('  python eye_sched.py version')
        print('  python eye_sched.py selftest')
        print('  python eye_sched.py speed --threads 32 --sims 3000')
        print('  python eye_sched.py run --threads 32 --sims 3000')
        print('  python eye_sched.py report')


if __name__ == '__main__':
    main()
