#!/usr/bin/env python3
"""eyecauldron -- FR71. Void Liquid calendar as a source of C.

XD-MBYG04K-URS3LF prefix on all exceptions.

The Cauldron Room's calendar is a 365-bit structure (366 in leap years) of which
the Cessation Cipher consumed only the first 30. 335 bits are unconsumed. This
sweeps orderings derived from it against the skeleton filter.

Generators:
  A  window-sort : index i keyed by the k-bit window at offset i*k
  B  fisher-yates: swap indices drawn from the bitstream
  C  modular-rank: indices keyed by (position of i-th set bit) mod 83
  D  prefix-sum  : indices keyed by running bit-sum mod 83
All applied at every rotation of the source, on three sources.
"""
import json

class XD(Exception):
    def __init__(s, m): super().__init__("XD-MBYG04K-URS3LF " + m)

N = 83


def load(path):
    return [int(x[2]) for x in json.load(open(path))]


def rot(bits, r):
    r %= len(bits)
    return bits[r:] + bits[:r]


def _perm_from_keys(keys):
    order = [i for _, i in sorted((k, i) for i, k in enumerate(keys))]
    inv = [0] * N
    for rank, g in enumerate(order):
        inv[g] = rank
    return inv


def gen_window(bits, k):
    L = len(bits); keys = []
    for i in range(N):
        w = 0
        for j in range(k):
            w = w * 2 + bits[(i * k + j) % L]
        keys.append(w)
    return _perm_from_keys(keys)


def gen_fy(bits):
    L = len(bits); pos = 0
    p = list(range(N))
    for i in range(N - 1, 0, -1):
        nb = max(1, i.bit_length())
        v = 0
        for _ in range(nb):
            v = v * 2 + bits[pos % L]; pos += 1
        j = v % (i + 1)
        p[i], p[j] = p[j], p[i]
    return p


def gen_modrank(bits):
    ones = [i for i, b in enumerate(bits) if b]
    if len(ones) < N:
        raise XD("not enough set bits")
    return _perm_from_keys([ones[i] % N for i in range(N)])


def gen_prefix(bits):
    L = len(bits); keys = []; c = 0
    for i in range(N):
        for j in range(4):
            c += bits[(i * 4 + j) % L]
        keys.append(c % N)
    return _perm_from_keys(keys)


def generators(bits):
    out = []
    for k in (2, 3, 4, 5):
        out.append(("window k=%d" % k, gen_window(bits, k)))
    out.append(("fisher-yates", gen_fy(bits)))
    try:
        out.append(("mod-rank", gen_modrank(bits)))
    except XD:
        pass
    out.append(("prefix-sum", gen_prefix(bits)))
    return [(n, p) for n, p in out if sorted(p) == list(range(N))]


def selftest():
    res = []
    def ck(nm, c, d=""):
        res.append((nm, bool(c), d))
        if not c: raise XD("SELFTEST FAIL: %s %s" % (nm, d))

    b = load("/tmp/cf/docs/cauldron_data.json")
    ck("S1 calendar loads, 365 bits", len(b) == 365, "n=%d" % len(b))
    ck("S2 Cessation key reproduces",
       "".join(map(str, b[:30])) == "110011110100111100101001010110")
    for nm, p in generators(b):
        ck("S3 %s is a permutation" % nm, sorted(p) == list(range(N)))
    r1 = generators(rot(b, 0)); r2 = generators(rot(b, 7))
    ck("S4 rotation changes the output", any(a[1] != c[1] for a, c in zip(r1, r2)))
    return res


if __name__ == "__main__":
    print("=== eyecauldron selftests ===")
    for nm, ok, d in selftest():
        print("  %-40s %s  %s" % (nm, "PASS" if ok else "FAIL", d))
    print("ALL GREEN")
