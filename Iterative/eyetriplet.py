#!/usr/bin/env python3
"""eyetriplet -- FR75. Is every triplet actually in depth?

XD-MBYG04K-URS3LF prefix on all exceptions.

FR65 verified the per-triplet keystream premise POOLED across all three triplets
(within z=+12.47, cross z=+1.26). It was never decomposed. T2 has behaved oddly
twice: W2 is uncoupled (FR35, FR73, FR74) and E3/W3 is the weakest pair in the
corpus. If T2 is not in depth, the model for a third of the corpus is wrong.
"""
import json, random, statistics, itertools

class XD(Exception):
    def __init__(s, m): super().__init__("XD-MBYG04K-URS3LF " + m)

N = 83
LAB = ['East 1','West 1','East 2','West 2','East 3','West 3','East 4','West 4','East 5']
TRIP = {'East 1':1,'West 1':1,'East 2':1,
        'West 2':2,'East 3':2,'West 3':2,
        'East 4':3,'West 4':3,'East 5':3}


def agree(a, b, lo=0):
    n = min(len(a), len(b))
    if n <= lo:
        raise XD("no overlap")
    h = sum(1 for t in range(lo, n) if a[t] == b[t])
    return h, n - lo


def triplet_stat(msgs, idx, members, lo=0):
    h = t = 0
    for x, y in itertools.combinations(members, 2):
        a, b = agree(msgs[idx[x]], msgs[idx[y]], lo)
        h += a; t += b
    return h, t


def shuffle_msgs(msgs, rng):
    out = []
    for m in msgs:
        c = list(m); rng.shuffle(c); out.append(c)
    return out


def z_of(obs, draws):
    mu = statistics.mean(draws); sd = statistics.pstdev(draws)
    if sd == 0:
        raise XD("degenerate null")
    return (obs - mu) / sd, mu


def selftest():
    rng = random.Random(75); res = []
    def ck(nm, c, d=""):
        res.append((nm, bool(c), d))
        if not c: raise XD("SELFTEST FAIL: %s %s" % (nm, d))

    lens = [99, 103, 118, 102, 137, 124, 119, 120, 114]
    idx = {l: i for i, l in enumerate(LAB)}

    # S1 -- PLANT: a triplet genuinely in depth (shared plaintext under one key)
    key = [rng.randrange(N) for _ in range(200)]
    base_pt = [rng.randrange(N) for _ in range(200)]
    depth = []
    for i, L in enumerate(lens):
        if i < 3:                       # first triplet shares 50% of plaintext
            pt = [base_pt[t] if rng.random() < 0.5 else rng.randrange(N)
                  for t in range(L)]
            depth.append([(pt[t] + key[t]) % N for t in range(L)])
        else:
            depth.append([rng.randrange(N) for _ in range(L)])
    sh = [shuffle_msgs(depth, rng) for _ in range(300)]
    h, t = triplet_stat(depth, idx, ['East 1', 'West 1', 'East 2'])
    dr = [triplet_stat(s, idx, ['East 1', 'West 1', 'East 2'])[0] for s in sh]
    z, mu = z_of(h, dr)
    ck("S1 planted depth detected", z > 6.0, "z=%+.2f" % z)

    # S2 -- NEGATIVE CONTROL: a non-depth triplet in the same corpus is quiet
    h2, t2 = triplet_stat(depth, idx, ['West 2', 'East 3', 'West 3'])
    dr2 = [triplet_stat(s, idx, ['West 2', 'East 3', 'West 3'])[0] for s in sh]
    z2, _ = z_of(h2, dr2)
    ck("S2 non-depth triplet quiet", abs(z2) < 3.0, "z=%+.2f" % z2)

    # S3 -- the instrument separates them within one corpus
    ck("S3 separation demonstrated", z - z2 > 6.0, "gap=%.1f sigma" % (z - z2))
    return res


if __name__ == "__main__":
    print("=== eyetriplet selftests ===")
    for nm, ok, d in selftest():
        print("  %-42s %s  %s" % (nm, "PASS" if ok else "FAIL", d))
    print("ALL GREEN")
