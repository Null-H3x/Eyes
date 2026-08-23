#!/usr/bin/env python
# ============================================================================
# eye_forge.py  -  THE EXHAUSTIVE GENERATOR SEARCH
#
#   python eye_forge.py selftest
#   python eye_forge.py verify  --threads 32
#   python eye_forge.py grid    --threads 32 --draws 100
#   python eye_forge.py report
#
# THIS ONE IS BUILT TO BE RUN , NOT TO FINISH IN A SANDBOX.
#   Reports 49 to 52 tested hand picked families because that is what fitted a
#   ten minute container.  That biased the whole search towards cheap.  This
#   enumerates the generator space instead : 210 rules by however many draws you
#   ask for , multiprocessing across every core , checkpointed so a kill or a
#   timeout costs only the current chunk.
#
#   210 rules x 100 draws = 21000 simulations at about 0.9 s each
#     one core        about 5 and a quarter hours
#     32 threads      about 10 minutes
#
# WHAT IT SEARCHES , AND WHY THIS SHAPE
#   Report 52 pinned the target to a corner no family had occupied : the corpus
#   reuses a homophone very SOON - 41 percent of reuses inside 4 symbols -
#   while keeping the total repeat rate LOW at 0.157 per symbol.  Cycling rules
#   reuse far too late , 5.6 percent in that band.  Fixed alphabet windows
#   reuse soon enough but repeat far too much overall.
#
#   The corner is an alphabet that is locally stable and changes often.  So the
#   rule is parameterised by the three things that control exactly that :
#
#     W   how many symbols an alphabet survives before it is redrawn
#     B   how fast a letter cycles through its own homophones
#     w   how many preceding plaintext letters steer the choice
#
#   Report 49's smallest window was 15.  The prediction from Report 52 is that
#   the corner sits well below that , which no run so far has looked at.
#
# THE INSTRUMENT IS VALIDATED BEFORE IT IS BELIEVED
#   verify plants a KNOWN grid point , generates a corpus from it , and requires
#   the search to recover that point.  If a rule cannot be found when the answer
#   is known , nothing the grid says about the corpus counts.
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
NS = 83
EFREQ = [8.2, 1.5, 2.8, 4.3, 12.7, 2.2, 2.0, 6.1, 7.0, 0.15, 0.77, 4.0, 2.4,
         6.7, 7.5, 1.9, 0.095, 6.0, 6.3, 9.1, 2.8, 0.98, 2.4, 0.15, 2.0, 0.074]

# the sharing geometry of the 24 real relations , planted into every simulation
GEOM = [(6, 68, 7, 71, 34), (1, 33, 1, 63, 33), (6, 57, 8, 58, 33),
        (7, 34, 8, 33, 33), (7, 68, 8, 66, 33), (2, 39, 2, 74, 32),
        (1, 29, 2, 34, 28), (4, 63, 6, 72, 28), (4, 63, 7, 75, 28),
        (4, 63, 8, 73, 28), (1, 60, 2, 70, 27), (0, 33, 0, 61, 26),
        (0, 53, 2, 65, 25), (1, 32, 2, 72, 25), (1, 62, 2, 37, 25),
        (1, 55, 4, 86, 23), (0, 28, 1, 28, 22), (0, 29, 2, 34, 21),
        (0, 58, 1, 60, 20), (6, 46, 7, 48, 19), (0, 32, 1, 62, 18),
        (0, 60, 1, 32, 18), (0, 32, 2, 72, 18), (0, 60, 2, 37, 18)]
# and the four shared alphabet blocks Report 51 found , which Report 52 showed
# move the relation count by half - included so the grid is not blamed for
# missing them
ANCH = [(0, 29, 1, 29, 4), (0, 37, 1, 37, 13), (6, 25, 8, 25, 3),
        (6, 29, 8, 29, 3), (6, 38, 8, 38, 3)]

WGRID = [0, 4, 5, 6, 7, 8, 10, 12, 15, 20, 25, 30, 40, 60]
BGRID = [0, 1, 2]
HGRID = [0, 1, 2, 3, 4]


def points():
    out = []
    for W in WGRID:
        for B in BGRID:
            for h in HGRID:
                out.append((W, B, h))
    return out


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


def english(n, r):
    tot = sum(EFREQ)
    cum = []; s = 0.0
    for i in range(26):
        s += EFREQ[i] / tot; cum.append(s)
    out = []
    for _ in range(n):
        x = r.random()
        for i in range(26):
            if x <= cum[i]:
                out.append(i); break
        else:
            out.append(25)
    return out


def quota():
    tot = sum(EFREQ)
    q = [max(1, int(round(NS * f / tot))) for f in EFREQ]
    while sum(q) > NS:
        q[q.index(max(q))] -= 1
    while sum(q) < NS:
        q[EFREQ.index(max(EFREQ[i] / q[i] for i in range(26)))] += 1
    return q


def plaintexts(r):
    pts = [english(LENS[k], r) for k in range(9)]
    for a, i, b, j, L in GEOM + ANCH:
        for t in range(L):
            if i + t < LENS[a] and j + t < LENS[b]:
                pts[b][j + t] = pts[a][i + t]
    return pts


def generate(W, B, hw, seed):
    """
    index into letter c's homophones =
        ( B * occurrences_of_c_so_far  +  hash of the last hw letters
          +  a salt that is redrawn every W symbols )   mod  h_c

    W 0 means the salt never changes , so the alphabet is fixed for the whole
    message.  B 0 means a letter does not advance through its homophones on its
    own.  hw 0 means the preceding text has no say.  Every family Reports 49 to
    52 tested is a corner of this cube.
    """
    r = random.Random(seed)
    q = quota()
    pool = list(range(NS)); r.shuffle(pool)
    H = []; k = 0
    for i in range(26):
        H.append(pool[k:k + q[i]]); k += q[i]
    out = []
    for pt in plaintexts(r):
        occ = [0] * 26
        salt = r.randrange(1 << 20)
        row = []
        for p in range(len(pt)):
            c = pt[p]
            if W and p % W == 0:
                salt = r.randrange(1 << 20)
            acc = B * occ[c] + salt
            for u in range(1, hw + 1):
                acc = acc * 31 + (pt[p - u] if p - u >= 0 else 0) + u
            occ[c] += 1
            v = H[c][acc % len(H[c])]
            if row and v == row[-1]:
                alt = [x for x in H[c] if x != row[-1]]
                if alt:
                    v = alt[acc % len(alt)]
            row.append(v)
        out.append(row)
    return out


BANDS = ((2, 4), (5, 9), (10, 14), (15, 19), (20, 29), (30, 40))
FEAT = ['relations', 'longest', 'repeats per symbol', 'adjacent', 'IC',
        'reuse 2-4', 'reuse 5-9', 'reuse 10-14', 'reuse 15-19', 'reuse 20-29']


def fingerprint(msgs):
    rel = maximal(msgs, 3, 6)
    n = len(rel)
    lg = max([L for k, L, a, i, b, j in rel] or [0])
    tl = sum(L for k, L, a, i, b, j in rel)
    tk = sum(k for k, L, a, i, b, j in rel)
    d = collections.Counter()
    for k, L, a, i, b, j in rel:
        s = msgs[a]
        for t1 in range(L):
            for t2 in range(t1 + 1, L):
                if s[i + t1] == s[i + t2]:
                    d[t2 - t1] += 1
    tot = float(sum(d.values())) or 1.0
    adj = 0
    for s in msgs:
        for p in range(len(s) - 1):
            if s[p] == s[p + 1]:
                adj += 1
    flat = [v for s in msgs for v in s]
    c = collections.Counter(flat)
    N = len(flat)
    ic = sum(v * (v - 1) for v in c.values()) / float(N * (N - 1))
    row = [n, lg, (tk / float(tl) if tl else 0.0), adj, ic]
    for lo, hi in BANDS[:5]:
        row.append(sum(d[x] for x in range(lo, hi + 1)) / tot)
    return row


SCALE = [8.0, 6.0, 0.05, 4.0, 0.0008, 0.09, 0.09, 0.09, 0.09, 0.06]


def _one(args):
    W, B, hw, seed = args
    return fingerprint(generate(W, B, hw, seed))


def run_point(W, B, hw, draws, seed0, pool=None):
    jobs = [(W, B, hw, seed0 + d) for d in range(draws)]
    if pool is None:
        rows = [_one(j) for j in jobs]
    else:
        rows = pool.map(_one, jobs, chunksize=1)
    nf = len(FEAT)
    mu = [sum(r[f] for r in rows) / float(len(rows)) for f in range(nf)]
    sg = [math.sqrt(sum((r[f] - mu[f]) ** 2 for r in rows) / len(rows))
          for f in range(nf)]
    return mu, sg


def score(t, mu, sg):
    """
    Negative Gaussian log likelihood per axis.  The log sigma term is the part
    that matters : scoring by z alone drops the normalisation and the search
    then prefers whichever rule is VAGUEST , because a wide distribution gives
    a small z for any observation at all.  Measured on the validation run , the
    top twenty ranked rules had a mean spread of 1.272 against 0.677 for the
    bottom twenty - the ranking was buying width , not fit.

    Fixing it is necessary and NOT sufficient : it moved the planted rule from
    rank 146 to 119 of 210.  See cmd_resolution for why.
    """
    tot = 0.0
    z = []
    for f in range(len(FEAT)):
        s = max(sg[f], SCALE[f] * 0.15)
        zz = (t[f] - mu[f]) / s
        z.append(zz)
        tot += 0.5 * zz * zz + math.log(s / SCALE[f])
    return tot / len(FEAT), z


def load_ckpt(path):
    done = {}
    if not os.path.exists(path):
        return done
    for line in open(path):
        p = line.rstrip('\n').split('\t')
        if len(p) < 3 + 2 * len(FEAT):
            continue
        key = (int(p[0]), int(p[1]), int(p[2]))
        vals = [float(x) for x in p[3:]]
        done[key] = (vals[:len(FEAT)], vals[len(FEAT):])
    return done


def cmd_grid(draws, seed, threads, ckpt, target_msgs=None, quiet=False):
    t = fingerprint(target_msgs if target_msgs is not None else M)
    pts = points()
    done = load_ckpt(ckpt)
    todo = [p for p in pts if p not in done]
    if not quiet:
        print("EXHAUSTIVE GENERATOR GRID")
        print("  %d rules , %d draws each , %d simulations"
              % (len(pts), draws, len(pts) * draws))
        print("  %d already in %s , %d to run" % (len(done), ckpt, len(todo)))
        print("  threads %d\n" % threads)
    pool = None
    if threads > 1:
        try:
            import multiprocessing
            pool = multiprocessing.Pool(threads)
        except Exception as e:
            print("  multiprocessing unavailable ( %s ) , running on one core" % e)
    t0 = time.time()
    fh = open(ckpt, 'a')
    for n, (W, B, hw) in enumerate(todo):
        mu, sg = run_point(W, B, hw, draws, seed + 977 * (W + 61 * B + 7 * hw),
                           pool)
        fh.write("\t".join([str(W), str(B), str(hw)] +
                           ["%.6g" % x for x in mu] +
                           ["%.6g" % x for x in sg]) + "\n")
        fh.flush()
        done[(W, B, hw)] = (mu, sg)
        if not quiet:
            m, z = score(t, mu, sg)
            el = time.time() - t0
            eta = el / (n + 1) * (len(todo) - n - 1)
            print("  W %-3d B %d h %d   miss %6.2f   rel %5.1f  reuse2-4 %.3f"
                  "   %d of %d  eta %.0f min"
                  % (W, B, hw, m, mu[0], mu[5], n + 1, len(todo), eta / 60.0))
            sys.stdout.flush()
    fh.close()
    if pool:
        pool.close(); pool.join()
    return done, t


def cmd_report(ckpt):
    t = fingerprint(M)
    done = load_ckpt(ckpt)
    if not done:
        print("nothing in %s yet - run grid first" % ckpt)
        return 2
    rows = []
    for key, (mu, sg) in done.items():
        m, z = score(t, mu, sg)
        rows.append((m, key, mu, sg, z))
    rows.sort()
    print("THE CORPUS")
    for f in range(len(FEAT)):
        print("   %-22s %.4f" % (FEAT[f], t[f]))
    print("\n%d of %d grid points measured\n" % (len(done), len(points())))
    print("  rank   W    B  h    miss    relations  rep/sym  reuse 2-4")
    for n, (m, key, mu, sg, z) in enumerate(rows[:20]):
        print("   %3d   %3d   %d  %d   %6.2f     %6.1f    %.4f    %.4f"
              % (n + 1, key[0], key[1], key[2], m, mu[0], mu[2], mu[5]))
    print("\n  THE WINNER , axis by axis")
    m, key, mu, sg, z = rows[0]
    print("   W %d  B %d  h %d   miss %.2f" % (key[0], key[1], key[2], m))
    for f in range(len(FEAT)):
        print("     %-22s corpus %9.4f   rule %9.4f +- %.4f   z %+6.1f"
              % (FEAT[f], t[f], mu[f], sg[f], z[f]))
    if m < 1.0:
        print("\n  VERDICT : this rule reproduces the corpus on every axis.")
    else:
        worst = max(range(len(FEAT)), key=lambda f: abs(z[f]))
        print("\n  VERDICT : nothing reproduces the corpus.  The nearest misses")
        print("  by %.2f , worst on %s at z %+.1f ." % (m, FEAT[worst], z[worst]))
    return 0


def cmd_resolution(ckpt, truth=(8, 1, 2)):
    """
    THE QUESTION THAT DECIDES WHETHER ANY OF THIS MEANS ANYTHING.
    Score every grid point against a corpus generated by a KNOWN point , and
    ask whether the score tracks how far that point is from the truth.  A
    working instrument gives a strongly positive correlation.
    """
    done = load_ckpt(ckpt)
    if not done:
        print("run verify first"); return 2
    t = fingerprint(generate(truth[0], truth[1], truth[2], 987654321))
    WI = dict((w, i) for i, w in enumerate(WGRID))
    rows = []
    for k, (mu, sg) in done.items():
        d = abs(WI[k[0]] - WI[truth[0]]) + abs(k[1] - truth[1]) + abs(k[2] - truth[2])
        m, z = score(t, mu, sg)
        rows.append((m, d, k))
    n = len(rows)
    mm = [x[0] for x in rows]; dd = [x[1] for x in rows]
    mub = sum(mm) / n; mud = sum(dd) / n
    sm = math.sqrt(sum((x - mub) ** 2 for x in mm) / n)
    sd = math.sqrt(sum((x - mud) ** 2 for x in dd) / n)
    cor = sum((mm[i] - mub) * (dd[i] - mud) for i in range(n)) / n / (sm * sd)
    rows.sort()
    rank = [x[2] for x in rows].index(truth) + 1
    print("RESOLUTION OF THE INSTRUMENT\n")
    print("  planted rule W %d B %d h %d" % truth)
    print("  its rank among %d grid points          : %d" % (n, rank))
    print("  correlation of score with true distance : %+.3f" % cor)
    print("  a working instrument would be strongly positive\n")
    if cor < 0.25 or rank > 10:
        print("  THE INSTRUMENT HAS NO RESOLUTION.  It cannot find a rule it")
        print("  generated itself , so it cannot identify the corpus's rule")
        print("  either , and any RANKING it produces is noise.")
        print("\n  What survives : a family that produces a value near ZERO on")
        print("  an axis where the corpus is far from zero cannot have made the")
        print("  corpus , whatever the ranking says.  Binary refutations of that")
        print("  kind hold.  Orderings among plausible rules do not.")
    else:
        print("  The instrument resolves.  Rankings can be read.")
    return 0


def cmd_verify(draws, seed, threads):
    """
    plant a KNOWN grid point , build a corpus from it , and require the search
    to name it.  A grid that cannot find a rule when the answer is known says
    nothing about the corpus.
    """
    truth = (8, 1, 2)
    print("VALIDATION  -  planting W %d  B %d  h %d\n" % truth)
    planted = generate(truth[0], truth[1], truth[2], 987654321)
    done, t = cmd_grid(draws, seed, threads, '_verify_ckpt.tsv',
                       target_msgs=planted, quiet=True)
    rows = []
    for key, (mu, sg) in done.items():
        m, z = score(t, mu, sg)
        rows.append((m, key))
    rows.sort()
    print("  best five grid points for the planted corpus")
    for m, key in rows[:5]:
        tag = "   <- the planted rule" if key == truth else ""
        print("    W %-3d B %d h %d   miss %.2f%s" % (key[0], key[1], key[2], m, tag))
    rank = [k for m, k in rows].index(truth) + 1
    print("\n  the planted rule ranks %d of %d" % (rank, len(rows)))
    if rank <= 5:
        print("  VALIDATED : the grid recovers a known generator.")
    else:
        print("  NOT VALIDATED : the grid cannot find a rule it made itself.")
        print("  Raising --draws will NOT fix it - run  resolution  to see why.")
        print("  The observation is a SINGLE corpus , so even the true rule sits")
        print("  about one sigma from its own mean on every axis , and every")
        print("  rule whose mean lies within a sigma is indistinguishable.")
    return 0 if rank <= 5 else 1


def selftest():
    ok = True
    t = fingerprint(M)
    okrow = t[0] == 38 and t[1] == 34 and t[3] == 0
    ok = ok and okrow
    print("corpus       : %d relations , longest %d , %d adjacent , expected"
          % (t[0], t[1], t[3]))
    print("             : 38 34 0   %s" % ("OK" if okrow else "*** FAIL ***"))
    okrow = abs(t[2] - 0.157) < 0.01 and abs(t[5] - 0.41) < 0.06
    ok = ok and okrow
    print("             : repeats per symbol %.4f , reuse in 2 to 4 %.3f ,"
          % (t[2], t[5]))
    print("             : expected 0.157 and 0.41   %s"
          % ("OK" if okrow else "*** FAIL ***"))

    okrow = len(points()) == len(WGRID) * len(BGRID) * len(HGRID)
    ok = ok and okrow
    print("grid         : %d rules over W %d , B %d , h %d   %s"
          % (len(points()), len(WGRID), len(BGRID), len(HGRID),
             "OK" if okrow else "*** FAIL ***"))

    # the old families must be corners of the cube
    a = fingerprint(generate(0, 1, 0, 11))
    b = fingerprint(generate(0, 0, 3, 11))
    c = fingerprint(generate(15, 0, 0, 11))
    print("corners      : W0 B1 h0 is the pure cycle , %d relations" % a[0])
    print("             : W0 B0 h3 is the pure history , %d relations" % b[0])
    print("             : W15 B0 h0 is the fixed window , %d relations" % c[0])
    okrow = c[2] > t[2] and a[5] < t[5]
    ok = ok and okrow
    print("             : the window corner over repeats , %.3f against %.3f ,"
          % (c[2], t[2]))
    print("             : and the cycle corner reuses too late , %.3f against"
          % a[5])
    print("             : %.3f - the two failures Report 52 found   %s"
          % (t[5], "OK" if okrow else "*** FAIL ***"))

    r1 = fingerprint(generate(8, 1, 2, 555))
    r2 = fingerprint(generate(8, 1, 2, 555))
    okrow = r1 == r2
    ok = ok and okrow
    print("determinism  : the same seed gives the same corpus   %s"
          % ("OK" if okrow else "*** FAIL ***"))
    print("SELF TEST %s" % ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


USAGE = """eye_forge.py  -  the exhaustive generator search

  python eye_forge.py selftest
  python eye_forge.py verify --threads 32 --draws 40
  python eye_forge.py grid   --threads 32 --draws 100
  python eye_forge.py report
  python eye_forge.py resolution      does the instrument resolve at all

  --threads  worker processes , default 1 .  Use as many cores as you have .
  --draws    simulations per rule , default 100
  --ckpt     checkpoint file , default eye_forge_ckpt.tsv

  The grid writes every finished rule to the checkpoint immediately , so a
  kill , a timeout or a reboot costs only the rule in flight .  Re run the same
  command and it picks up where it stopped .  report reads the checkpoint and
  can be run while the grid is still going .

  210 rules x 100 draws is about 5 and a quarter hours on one core and about
  10 minutes on 32 threads .
"""


def main(argv):
    draws, seed, threads = 100, 20260820, 1
    ckpt = 'eye_forge_ckpt.tsv'
    pos = []
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == '--draws':
            draws = int(argv[i + 1]); i += 1
        elif a == '--seed':
            seed = int(argv[i + 1]); i += 1
        elif a == '--threads':
            threads = int(argv[i + 1]); i += 1
        elif a == '--ckpt':
            ckpt = argv[i + 1]; i += 1
        elif a.startswith('--'):
            print("unknown option %s" % a); return 2
        else:
            pos.append(a)
        i += 1
    argv = [argv[0]] + pos
    if len(argv) < 2:
        print(USAGE); return 2
    c = argv[1]
    if c == 'selftest':
        return selftest()
    if c == 'verify':
        return cmd_verify(draws, seed, threads)
    if c == 'grid':
        cmd_grid(draws, seed, threads, ckpt)
        return cmd_report(ckpt)
    if c == 'report':
        return cmd_report(ckpt)
    if c == 'resolution':
        return cmd_resolution('_verify_ckpt.tsv')
    print(USAGE)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
