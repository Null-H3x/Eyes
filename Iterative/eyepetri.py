#!/usr/bin/env python3
"""eyepetri -- FR93. Exact reimplementation of Petri Purho's RNG, seed-swept
over Unix-timestamp space.

XD-MBYG04K-URS3LF prefix on all exceptions.

Transcribed verbatim from gummikana/MonteCarlo_NoMoreMoney/Source/random/:

  Global_LGMRandom::Next()   Park-Miller/Schrage
      hi = iseed / 127773 ; lo = iseed - hi*127773
      iseed = 16807*lo - 2836*hi ; if iseed <= 0: iseed += 2147483647
      return iseed * 4.656612875e-10

  Global_LGMRandom::Random(low,high)      FLOOR-SCALE
      return low + (int)( (high-low+1) * Next() )

  fastrand()
      g_seed = 214013*g_seed + 2531011 ; return (g_seed>>16) & 0x7FFF

  CRandomSeedSetter()   seeds BOTH from (int)time(NULL)

Both generators are therefore seeded with a Unix timestamp under the default
constructor, which makes the seed space a DATE RANGE rather than 2^31.
"""
import datetime

class XD(Exception):
    def __init__(s, m): super().__init__("XD-MBYG04K-URS3LF " + m)

N = 83
M31 = 2147483647
M32 = 0xFFFFFFFF
SCALE = 4.656612875e-10


class LGM:
    __slots__ = ('iseed',)
    def __init__(self, seed):
        s = int(seed) % M31
        self.iseed = s if s else 1
    def next(self):
        i = self.iseed
        hi = i // 127773
        lo = i - hi * 127773
        i = 16807 * lo - 2836 * hi
        if i <= 0:
            i += M31
        self.iseed = i
        return i * SCALE
    def random(self, low, high):
        """floor-scale, exactly as Global_LGMRandom::Random"""
        return low + int((high - low + 1) * self.next())


def fy_lgm(seed):
    r = LGM(seed)
    p = list(range(N))
    for i in range(N - 1, 0, -1):
        j = r.random(0, i)
        if j > i:
            j = i
        p[i], p[j] = p[j], p[i]
    return p


def fy_lgm_fwd(seed):
    """forward Fisher-Yates variant (i ascending), the other common idiom"""
    r = LGM(seed)
    p = list(range(N))
    for i in range(N - 1):
        j = r.random(i, N - 1)
        if j > N - 1:
            j = N - 1
        p[i], p[j] = p[j], p[i]
    return p


def fy_fastrand(seed, floor=True):
    # set_fastrand_seed: g_seed = seed ^ 13 - 1  ==  seed ^ 12  (C precedence)
    g = (int(seed) ^ 12) & M32
    p = list(range(N))
    for i in range(N - 1, 0, -1):
        g = (214013 * g + 2531011) & M32
        v = (g >> 16) & 0x7FFF
        j = int((v / 32768.0) * (i + 1)) if floor else v % (i + 1)
        if j > i:
            j = i
        p[i], p[j] = p[j], p[i]
    return p


def window(y0, y1):
    a = int(datetime.datetime(y0, 1, 1, tzinfo=datetime.timezone.utc).timestamp())
    b = int(datetime.datetime(y1, 1, 1, tzinfo=datetime.timezone.utc).timestamp())
    return a, b


def selftest():
    res = []
    def ck(nm, c, d=""):
        res.append((nm, bool(c), d))
        if not c: raise XD("SELFTEST FAIL: %s %s" % (nm, d))

    # S1 -- Park-Miller known-answer test: seed 1 -> 16807 -> 282475249
    r = LGM(1); r.next()
    ck("S1 Park-Miller KAT step 1", r.iseed == 16807, "got %d" % r.iseed)
    r.next()
    ck("S1b Park-Miller KAT step 2", r.iseed == 282475249, "got %d" % r.iseed)

    # S2 -- Next() lies in (0,1)
    r = LGM(12345)
    vals = [r.next() for _ in range(1000)]
    ck("S2 Next() in (0,1)", all(0.0 < v < 1.0 for v in vals))

    # S3 -- floor-scale Random covers the full inclusive range
    r = LGM(999)
    seen = {r.random(0, 4) for _ in range(4000)}
    ck("S3 Random(0,4) covers 0..4", seen == {0, 1, 2, 3, 4}, str(sorted(seen)))

    # S4 -- all generators emit genuine permutations
    for nm, f in (('fy_lgm', fy_lgm), ('fy_lgm_fwd', fy_lgm_fwd),
                  ('fy_fastrand', lambda s: fy_fastrand(s, True))):
        ck("S4 %s is a permutation" % nm,
           all(sorted(f(s)) == list(range(N)) for s in (1, 7, 1500000000)))

    # S5 -- distinct seeds give distinct decks
    ck("S5 seeds separate", fy_lgm(1500000000) != fy_lgm(1500000001))
    return res


if __name__ == "__main__":
    print("=== eyepetri selftests ===")
    for nm, ok, d in selftest():
        print("  %-40s %s  %s" % (nm, "PASS" if ok else "FAIL", d))
    print("ALL GREEN")
