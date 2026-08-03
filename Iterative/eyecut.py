#!/usr/bin/env python3
"""eyecut -- FR90. Scan for CUT signatures.

XD-MBYG04K-URS3LF prefix on all exceptions.

Petri is a card magician with published cut/stack modules. A CUT is a cyclic
rotation of a block: [A|B] written as [B|A]. Against an uncut sibling, the two
halves then align at TWO DIFFERENT SHIFTS with a clean positional boundary.

FR32 recorded East4/West4 matching at shifts +1, +2 AND +3 and read it as one
relationship with indels. That is also the signature of a cut.

Method: slide a window along message A; for each window find the shift against
message B that maximises literal matches. A cut shows as an abrupt, sustained
change in the best shift at a single position.
"""
import json, random, statistics, collections

class XD(Exception):
    def __init__(s, m): super().__init__("XD-MBYG04K-URS3LF " + m)

LAB = ['East 1','West 1','East 2','West 2','East 3','West 3','East 4','West 4','East 5']


def match_profile(a, b, W=25, smax=60):
    """for each window start in a, the shift maximising matches with b"""
    out = []
    for t0 in range(0, len(a) - W + 1):
        best = (-1, None)
        for s in range(-smax, smax + 1):
            n = 0
            for t in range(t0, t0 + W):
                u = t + s
                if 0 <= u < len(b) and a[t] == b[u]:
                    n += 1
            if n > best[0]:
                best = (n, s)
        out.append((t0, best[1], best[0]))
    return out


def cut_score(prof, minrun=6, minmatch=4):
    """largest pair of adjacent sustained runs at DIFFERENT shifts"""
    runs = []
    cur_s, cur_n, start = None, 0, 0
    for t0, s, n in prof:
        if n < minmatch:
            s = None
        if s == cur_s:
            cur_n += 1
        else:
            if cur_s is not None and cur_n >= minrun:
                runs.append((start, cur_n, cur_s))
            cur_s, cur_n, start = s, 1, t0
    if cur_s is not None and cur_n >= minrun:
        runs.append((start, cur_n, cur_s))
    best = None
    for i in range(len(runs) - 1):
        a, b = runs[i], runs[i + 1]
        if a[2] != b[2]:
            sc = min(a[1], b[1])
            if best is None or sc > best[0]:
                best = (sc, b[0], a[2], b[2])
    return best, runs


def selftest():
    rng = random.Random(90); res = []
    def ck(nm, c, d=""):
        res.append((nm, bool(c), d))
        if not c: raise XD("SELFTEST FAIL: %s %s" % (nm, d))

    # S1 -- PLANT a cut: build B, then A = B cut at position 60 with a shift
    base = [rng.randrange(83) for _ in range(120)]
    B = list(base)
    A = base[60:] + base[:60]            # a clean single cut
    prof = match_profile(A, B, W=25, smax=70)
    best, runs = cut_score(prof)
    ck("S1 planted cut detected", best is not None and best[0] >= 6,
       "best=%s runs=%d" % (best, len(runs)))

    # S2 -- NEGATIVE CONTROL: unrelated messages show no sustained two-shift structure
    X = [rng.randrange(83) for _ in range(120)]
    Y = [rng.randrange(83) for _ in range(120)]
    b2, r2 = cut_score(match_profile(X, Y, W=25, smax=70))
    ck("S2 unrelated pair shows no cut", b2 is None or b2[0] < 6,
       "best=%s" % (b2,))

    # S3 -- a SINGLE-SHIFT relationship must NOT read as a cut
    C = [rng.randrange(83) for _ in range(120)]
    Dm = [rng.randrange(83) for _ in range(10)] + C[:110]   # pure shift, no cut
    b3, r3 = cut_score(match_profile(Dm, C, W=25, smax=70))
    ck("S3 pure shift does not read as a cut", b3 is None or b3[0] < 6,
       "best=%s" % (b3,))
    return res


if __name__ == "__main__":
    print("=== eyecut selftests ===")
    for nm, ok, d in selftest():
        print("  %-44s %s  %s" % (nm, "PASS" if ok else "FAIL", d))
    print("ALL GREEN")
