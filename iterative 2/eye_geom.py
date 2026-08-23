#!/usr/bin/env python
# ============================================================================
# eye_geom.py  -  WHAT THE DETECTOR THRESHOLD DISCARDS , AND WHETHER IT MATTERS
#
#   python eye_geom.py version
#   python eye_geom.py selftest
#   python eye_geom.py speed --threads 32 --draws 5000
#   python eye_geom.py run   --threads 32 --draws 5000
#   python eye_geom.py report
#
# WHY
#   Every report since 33 has used one geometry : 24 relations at minrep 3 and
#   minlen 6 , with relations dropped when both starts lie in a message prefix ,
#   and one relation kept per message pair and shift .  Four choices , none of
#   them ever tested , all of them discarding data.
#
#   Relaxing minrep from 3 to 2 gives **37 relations** , and messages 3 and 5 -
#   which have carried ZERO relations through six reports of geometry - gain
#   four and two .  Report 65 inferred statistically that the corpus must share
#   more than its 24 relations reveal .  The threshold may simply have been
#   hiding it.
#
#   A first pass on 40 replicates put the corpus at 37 against a null mean of
#   6 . 15 , which is suggestive and pinned at the resolution floor of 40 draws.
#   This tool settles it.
#
# WHAT IT MEASURES
#   The full threshold surface - minrep 1 to 5 crossed with minlen 4 to 12 -
#   against THREE nulls , because one null is a claim and three are a test :
#
#     pooled     symbols drawn from the corpus's pooled frequencies
#     permessage symbols drawn from each message's own frequencies
#     shuffle    each message's own symbols , reordered
#
#   The third is the strict one .  It preserves every message's symbol multiset
#   exactly and destroys only the ORDER , so any relation it finds comes from
#   arrangement alone .  A geometry that survives it is real.
#
# WHY IT IS BUILT THE WAY IT IS
#   The extension work in maximal() does not depend on the thresholds , so the
#   whole surface comes from ONE pass per corpus at the loosest setting and is
#   then filtered .  Fifty four threshold cells cost what one costs.
#
#   Rule 8    the null is drawn at the size of the search actually performed
#   Rule 9    the mechanism forbids a relation the null can never produce , and
#             selftest asserts the monotonicity the surface must obey
#   Rule 11   the full surface is printed , never a marginal
#   Rule 12   every command prints its build
# ============================================================================

import sys, os, math, random, collections, time

VERSION = 'eye_geom build 1 , 22 August 2026'
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
MINREP = [1, 2, 3, 4, 5]
MINLEN = [4, 5, 6, 7, 8, 10, 12]


def prevtab(s):
    last = {}
    pv = [-1] * len(s)
    for p in range(len(s)):
        pv[p] = last.get(s[p], -1)
        last[s[p]] = p
    return pv


def extensions(msgs):
    """
    every maximal isomorph extension in the corpus , with no threshold applied .
    the extension work does not depend on minrep or minlen , so one pass here
    serves the whole surface.
    """
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
                    if L >= 4 and rep >= 1:
                        out.append((rep, L, a, i, b, j))
    out.sort(key=lambda t: -t[1])
    return out


def surface(ext, msgs):
    """
    the relation count at every threshold , with the prefix filter and the one
    per pair and shift rule applied exactly as the standing detector applies
    them .  also the count for messages 3 and 5 , which the standing threshold
    leaves empty.
    """
    out = {}
    for mr in MINREP:
        for ml in MINLEN:
            keep = []
            for k, L, a, i, b, j in ext:
                if L < ml or k < mr:
                    continue
                if any(a == x[2] and b == x[4] and i >= x[3]
                       and i + L <= x[3] + x[1] and j - i == x[5] - x[3]
                       for x in keep):
                    continue
                keep.append((k, L, a, i, b, j))
            filt = [x for x in keep
                    if not (x[3] < PRE[x[2]] and x[5] < PRE[x[4]])]
            best = {}
            for k, L, a, i, b, j in filt:
                key = (a, b, j - i)
                if key not in best or L > best[key][1]:
                    best[key] = (k, L, a, i, b, j)
            rel = list(best.values())
            inv = collections.Counter()
            for k, L, a, i, b, j in rel:
                inv[a] += 1; inv[b] += 1
            out[(mr, ml)] = (len(rel), inv[3] + inv[5],
                             sum(x[1] for x in rel))
    return out


def null_pooled(r):
    c = collections.Counter(x for row in M for x in row)
    syms = list(c); wts = [c[s] for s in syms]
    return [r.choices(syms, weights=wts, k=n) for n in LENS]


def null_permessage(r):
    out = []
    for row in M:
        c = collections.Counter(row)
        syms = list(c); wts = [c[s] for s in syms]
        out.append(r.choices(syms, weights=wts, k=len(row)))
    return out


def null_shuffle(r):
    out = []
    for row in M:
        q = list(row); r.shuffle(q); out.append(q)
    return out


NULLS = [('pooled', null_pooled), ('permessage', null_permessage),
         ('shuffle', null_shuffle)]


def one(job):
    kind, seed = job
    r = random.Random(seed)
    msgs = dict(NULLS)[kind](r)
    return kind, surface(extensions(msgs), msgs)


def cmd_selftest():
    bad = 0

    def chk(name, got, exp):
        ok = got == exp
        print('  %-56s got %-14s expected %-14s %s'
              % (name, repr(got), repr(exp), 'ok' if ok else 'BAD'))
        return 0 if ok else 1

    ext = extensions(M)
    s = surface(ext, M)
    print('the standing geometry is reproduced exactly')
    bad += chk('minrep 3 minlen 6 gives the 24 relations of Report 33',
               s[(3, 6)][0], 24)
    bad += chk('and messages 3 and 5 appear in none of them', s[(3, 6)][1], 0)
    bad += chk('total relation length', s[(3, 6)][2], 615)
    print('')
    print('what the threshold discards')
    bad += chk('minrep 2 minlen 6 gives 37', s[(2, 6)][0], 37)
    bad += chk('and messages 3 and 5 appear 6 times', s[(2, 6)][1], 6)
    print('')
    print('the mechanism forbids these , so they are asserted')
    ok = True
    for ml in MINLEN:
        for a, b in zip(MINREP, MINREP[1:]):
            if s[(a, ml)][0] < s[(b, ml)][0]:
                ok = False
    bad += chk('the count never rises as minrep rises', ok, True)
    ok2 = True
    for mr in MINREP:
        for a, b in zip(MINLEN, MINLEN[1:]):
            if s[(mr, a)][0] < s[(mr, b)][0]:
                ok2 = False
    bad += chk('the count never rises as minlen rises', ok2, True)
    bad += chk('every extension is at least 4 long',
               min(x[1] for x in ext) >= 4, True)
    print('')
    print('the three nulls keep what they promise to keep')
    r = random.Random(2)
    a = null_shuffle(r)
    bad += chk('the shuffle null keeps every message symbol multiset',
               all(sorted(a[m]) == sorted(M[m]) for m in range(9)), True)
    bad += chk('and does not keep the order',
               sum(1 for m in range(9) for p in range(LENS[m])
                   if a[m][p] == M[m][p]) < 40, True)
    b = null_permessage(r)
    bad += chk('the per message null keeps every message length',
               [len(x) for x in b], LENS)
    c = null_pooled(r)
    bad += chk('the pooled null keeps the corpus length',
               sum(len(x) for x in c), sum(LENS))
    print('')
    print('a null corpus must produce almost nothing at the standing threshold')
    v = []
    for t in range(12):
        q = null_shuffle(random.Random(300 + t))
        v.append(surface(extensions(q), q)[(3, 6)][0])
    print('     ( shuffle null at minrep 3 minlen 6 : %s )' % v)
    bad += chk('twelve shuffled corpora stay far below the corpus 24',
               max(v) < 12, True)
    print('')
    print('SELFTEST %s   %d bad' % ('PASSED' if bad == 0 else 'FAILED', bad))
    return bad


def cmd_speed(threads, draws):
    t0 = time.time()
    for i in range(4):
        q = null_shuffle(random.Random(900 + i))
        surface(extensions(q), q)
    per = (time.time() - t0) / 4.0
    print('  one null corpus , all %d threshold cells   %.3f s'
          % (len(MINREP) * len(MINLEN), per))
    eff = 1.0
    if threads > 1:
        import multiprocessing as mp
        pool = mp.Pool(threads)
        probe = [('shuffle', 950 + i) for i in range(threads * 2)]
        t0 = time.time()
        for _ in pool.imap_unordered(one, probe, chunksize=1):
            pass
        wall = time.time() - t0
        pool.close(); pool.join()
        ideal = len(probe) * per / float(threads)
        eff = ideal / wall if wall > 0 else 1.0
        print('  %d corpora on %d workers took %.1f s against %.1f s ideal ,'
              % (len(probe), threads, wall, ideal))
        print('  EFFICIENCY %.2f' % eff)
        if eff < 0.05:
            eff = 0.05
    print('')
    print('  %-8s %-12s %s' % ('draws', 'corpora', 'wall clock'))
    for n in (500, 2000, 5000, 20000):
        tot = n * len(NULLS) * per
        w = tot / max(threads, 1) / eff
        print('  %-8d %-12d %s'
              % (n, n * len(NULLS),
                 ('%.0f s' % w) if w < 120 else ('%.1f min' % (w / 60.0))
                 if w < 7200 else ('%.1f hours' % (w / 3600.0))))
    w = draws * len(NULLS) * per / max(threads, 1) / eff
    print('')
    print('  --draws %d is %d null corpora , about %s , smallest p %.6f'
          % (draws, draws * len(NULLS),
             ('%.1f min' % (w / 60.0)) if w < 7200 else
             ('%.1f hours' % (w / 3600.0)), 1.0 / (draws + 1.0)))


def cmd_run(threads, draws, path):
    import json
    jobs = []
    sd = 40000
    for kind, fn in NULLS:
        for d in range(draws):
            sd += 1
            jobs.append((kind, sd))
    print('%d null corpora across %d nulls on %d threads'
          % (len(jobs), len(NULLS), threads))
    fh = open(path, 'w')
    t0 = time.time()
    if threads > 1:
        import multiprocessing as mp
        pool = mp.Pool(threads)
        it = pool.imap_unordered(one, jobs, chunksize=4)
    else:
        it = (one(j) for j in jobs)
    for n, (kind, s) in enumerate(it, 1):
        fh.write(json.dumps([kind, dict(('%d,%d' % k, v)
                                        for k, v in s.items())]))
        fh.write('\n')
        if n % 200 == 0 or n == len(jobs):
            fh.flush()
            el = time.time() - t0
            sys.stderr.write('  %d / %d   %.0f s elapsed , %.0f s left\n'
                             % (n, len(jobs), el,
                                el * (len(jobs) - n) / max(n, 1)))
            sys.stderr.flush()
    if threads > 1:
        pool.close(); pool.join()
    fh.close()
    cmd_report(path)


def cmd_report(path):
    import json
    data = collections.defaultdict(lambda: collections.defaultdict(list))
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        try:
            kind, s = json.loads(line)
        except ValueError:
            continue
        for k, v in s.items():
            mr, ml = k.split(',')
            data[kind][(int(mr), int(ml))].append(v[0])
    if not data:
        print('no draws in %s' % path)
        return
    obs = surface(extensions(M), M)
    n = len(list(data.values())[0][(3, 6)])
    print('')
    print('=' * 78)
    print('THE THRESHOLD SURFACE , %d draws per null' % n)
    print('=' * 78)
    print('  the corpus relation count at every threshold , and beneath it the')
    print('  count on the strict null - each message own symbols , reordered')
    print('')
    for tag, lab in (('obs', 'THE CORPUS'), ('shuffle', 'shuffle null mean'),
                     ('p', 'p value against shuffle')):
        print('  %-24s %s' % (lab, ' '.join('%7s' % ('len %d' % ml)
                                            for ml in MINLEN)))
        for mr in MINREP:
            row = []
            for ml in MINLEN:
                o = obs[(mr, ml)][0]
                v = data['shuffle'][(mr, ml)]
                if tag == 'obs':
                    row.append('%7d' % o)
                elif tag == 'shuffle':
                    row.append('%7.2f' % (sum(v) / float(len(v))))
                else:
                    ge = sum(1 for x in v if x >= o)
                    row.append('%7.5f' % ((ge + 1.0) / (len(v) + 1.0)))
            print('    minrep %-15d %s' % (mr, ' '.join(row)))
        print('')
    print('  the three nulls at the two thresholds that matter')
    print('')
    print('  %-14s %-10s %-12s %-10s %s'
          % ('threshold', 'corpus', 'null', 'null mean', 'p'))
    for mr, ml in ((3, 6), (2, 6), (2, 4), (1, 6)):
        o = obs[(mr, ml)][0]
        for kind, fn in NULLS:
            v = data[kind][(mr, ml)]
            if not v:
                continue
            ge = sum(1 for x in v if x >= o)
            print('  %-14s %-10d %-12s %-10.2f %.5f'
                  % ('%d / %d' % (mr, ml) if kind == NULLS[0][0] else '',
                     o if kind == NULLS[0][0] else o, kind,
                     sum(v) / float(len(v)), (ge + 1.0) / (len(v) + 1.0)))
        print('')
    print('  THE RELATIONS THE STANDING THRESHOLD DISCARDS')
    o3 = obs[(3, 6)][0]; o2 = obs[(2, 6)][0]
    v3 = data['shuffle'][(3, 6)]; v2 = data['shuffle'][(2, 6)]
    gains = [b - a for a, b in zip(v3, v2)]
    gains.sort()
    ge = sum(1 for x in gains if x >= o2 - o3)
    print('    the corpus gains %d relations from minrep 3 to 2' % (o2 - o3))
    print('    the shuffle null gains %.2f on average , 95th percentile %d'
          % (sum(gains) / float(len(gains)), gains[int(0.95 * len(gains))]))
    print('    p = %.5f , so about %.1f of the %d are real'
          % ((ge + 1.0) / (len(gains) + 1.0),
             (o2 - o3) - sum(gains) / float(len(gains)), o2 - o3))
    print('')
    print('    messages 3 and 5 appear in %d relations at minrep 2 and %d at 3'
          % (obs[(2, 6)][1], obs[(3, 6)][1]))


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
        cmd_speed(opt('--threads', 32), opt('--draws', 5000))
    elif cmd in ('run', 'verify', 'scan'):
        cmd_run(opt('--threads', 32), opt('--draws', 5000),
                opt('--out', 'eye_geom_null.txt', str))
    elif cmd == 'report':
        cmd_report(opt('--out', 'eye_geom_null.txt', str))
    else:
        print('commands : version , selftest , speed , run , report')
        print('')
        print('  python eye_geom.py version')
        print('  python eye_geom.py selftest')
        print('  python eye_geom.py speed --threads 32 --draws 5000')
        print('  python eye_geom.py run --threads 32 --draws 5000')
        print('  python eye_geom.py report')


if __name__ == '__main__':
    main()
