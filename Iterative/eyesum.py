#!/usr/bin/env python3
"""eyesum -- FR70. Does the eye corpus carry constant-sum block structure?

XD-MBYG04K-URS3LF prefix on all exceptions.

MOTIVATION: the Cessation Cipher is a SOLVED puzzle by the same author. Its
solution path is a worked example of his design vocabulary:
  - six symbols transcribed to 0-5 by pixel value
  - six messages merged along shared sections
  - restructured into 27 rows, EACH SUMMING TO ~30
  - the first glyph of the first row replaced with a 3

The eye corpus already matches the first two motifs. The third has never been
tested. Rows hold at most 39 eyes = 13 trigrams, so block size 13 is the
structurally motivated candidate; others are swept for completeness.

A constant-sum design would show ANOMALOUSLY LOW variance in block sums.
"""
import json, random, statistics, math

class XD(Exception):
    def __init__(s, m): super().__init__("XD-MBYG04K-URS3LF " + m)

N = 83


def blocks(msgs, B, drop_partial=True):
    out = []
    for m in msgs:
        for i in range(0, len(m) - (B - 1 if drop_partial else 0), B):
            b = m[i:i + B]
            if len(b) == B or not drop_partial:
                out.append(sum(b))
    return out


def spread(sums):
    """raw dispersion of block sums (non-modular design)"""
    if len(sums) < 2:
        raise XD("too few blocks")
    return statistics.pstdev(sums)


def modconc(sums):
    """concentration of block sums MOD 83 (modular design).
    A constant-sum design puts every block on one residue."""
    if len(sums) < 2:
        raise XD("too few blocks")
    c = {}
    for s in sums:
        r = s % N; c[r] = c.get(r, 0) + 1
    return max(c.values()) / len(sums)


def shuffle_msgs(msgs, rng):
    out = []
    for m in msgs:
        c = list(m); rng.shuffle(c); out.append(c)
    return out


def z_of(obs, draws):
    mu = statistics.mean(draws); sd = statistics.pstdev(draws)
    if sd == 0:
        raise XD("degenerate null")
    return (obs - mu) / sd


# ------------------------------------------------------------------ selftests
def selftest():
    rng = random.Random(70); res = []
    def ck(nm, c, d=""):
        res.append((nm, bool(c), d))
        if not c: raise XD("SELFTEST FAIL: %s %s" % (nm, d))

    lens = [99, 103, 118, 102, 137, 124, 119, 120, 114]

    # S1 -- PLANT: build a corpus whose blocks of 13 sum to a constant
    B = 13; TARGET = 13 * 41
    plant = []
    for L in lens:
        row = []
        for i in range(0, L - B + 1, B):
            blk = [rng.randrange(N) for _ in range(B - 1)]
            blk.append((TARGET - sum(blk)) % N)
            row += blk
        row += [rng.randrange(N) for _ in range(L - len(row))]
        plant.append(row)
    obs = modconc(blocks(plant, B))
    dr = [modconc(blocks(shuffle_msgs(plant, rng), B)) for _ in range(300)]
    z = z_of(obs, dr)
    ck("S1 planted modular constant-sum detected", z > 4.0,
       "concentration %.2f vs null %.2f, z=%+.2f" % (obs, statistics.mean(dr), z))

    # S2 -- NEGATIVE CONTROL: a random corpus must not fire
    rnd = [[rng.randrange(N) for _ in range(L)] for L in lens]
    o2 = modconc(blocks(rnd, B))
    d2 = [modconc(blocks(shuffle_msgs(rnd, rng), B)) for _ in range(300)]
    z2 = z_of(o2, d2)
    ck("S2 random corpus quiet", abs(z2) < 3.0, "z=%+.2f" % z2)

    # S3 -- the null must preserve per-message multisets
    sh = shuffle_msgs(rnd, rng)
    ck("S3 null preserves multiset",
       all(sorted(a) == sorted(b) for a, b in zip(rnd, sh)))

    # S4 -- detector must not fire on the WRONG block size for the plant
    o4 = modconc(blocks(plant, 7))
    d4 = [modconc(blocks(shuffle_msgs(plant, rng), 7)) for _ in range(300)]
    z4 = z_of(o4, d4)
    ck("S4 wrong block size does not fire on the plant", z4 < 4.0,
       "z=%+.2f at B=7 vs %+.2f at B=13" % (z4, z))

    # S5 -- partial-block handling does not manufacture signal
    o5 = spread(blocks(rnd, B, drop_partial=False))
    ck("S5 partial blocks handled", o5 > 0)
    return res


if __name__ == "__main__":
    print("=== eyesum selftests (green before corpus contact) ===")
    for nm, ok, d in selftest():
        print("  %-52s %s  %s" % (nm, "PASS" if ok else "FAIL", d))
    print("ALL GREEN")
