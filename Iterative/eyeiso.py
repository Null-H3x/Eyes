#!/usr/bin/env python3
"""eyeiso -- FR77. Is isomorph abundance carried by non-literal matches?

XD-MBYG04K-URS3LF prefix on all exceptions.

Doctrine treats long-isomorph abundance as the one non-vacuous discriminator:
ciphertext-value feedback crushes long isomorphs, the corpus does not.

But a LITERAL match (identical glyph sequences) survives feedback ciphers
perfectly well -- identical plaintext under an identical key gives identical
ciphertext. Only NON-LITERAL isomorphs (same repeat pattern, different glyphs)
discriminate. And the corpus contains two near-duplicate message pairs that
generate literal matches in abundance.

This decomposes the abundance figure accordingly.
"""
import json, random, collections, itertools, statistics

class XD(Exception):
    def __init__(s, m): super().__init__("XD-MBYG04K-URS3LF " + m)

LAB = ['East 1','West 1','East 2','West 2','East 3','West 3','East 4','West 4','East 5']


def pattern(win):
    """canonical repeat pattern: first-occurrence encoding. ABCA -> (0,1,2,0)"""
    seen = {}; out = []
    for x in win:
        if x not in seen:
            seen[x] = len(seen)
        out.append(seen[x])
    return tuple(out)


def windows(msgs, L, min_rep=2):
    """min_rep: minimum number of repeated positions required.
    Windows of all-distinct glyphs share the trivial pattern (0,1,..,L-1) and
    match everything; they carry no information and are excluded."""
    for mi, m in enumerate(msgs):
        for i in range(len(m) - L + 1):
            w = m[i:i + L]
            if L - len(set(w)) < min_rep:
                continue
            yield mi, i, tuple(w), pattern(w)


def isomorph_pairs(msgs, L, cross_message_only=True, min_rep=2):
    """returns (literal, nonliteral) pair counts and a per-message-pair tally"""
    buckets = collections.defaultdict(list)
    for mi, i, w, p in windows(msgs, L, min_rep):
        buckets[p].append((mi, i, w))
    lit = non = 0
    tally = collections.Counter()
    for p, items in buckets.items():
        if len(items) < 2:
            continue
        for (a, ia, wa), (b, ib, wb) in itertools.combinations(items, 2):
            if cross_message_only and a == b:
                continue
            if wa == wb:
                lit += 1
            else:
                non += 1
                tally[(min(a, b), max(a, b))] += 1
    return lit, non, tally


def shuffle_msgs(msgs, rng):
    out = []
    for m in msgs:
        c = list(m); rng.shuffle(c); out.append(c)
    return out


def selftest():
    rng = random.Random(77); res = []
    def ck(nm, c, d=""):
        res.append((nm, bool(c), d))
        if not c: raise XD("SELFTEST FAIL: %s %s" % (nm, d))

    ck("S1 pattern canonicalises", pattern([5, 9, 2, 5]) == (0, 1, 2, 0))
    ck("S1b distinct glyphs, same pattern",
       pattern([5, 9, 2, 5]) == pattern([7, 1, 3, 7]))
    ck("S1c different pattern distinguished",
       pattern([5, 9, 2, 5]) != pattern([5, 9, 2, 9]))

    lens = [60] * 4
    gl = list(range(83))

    # S2 -- PLANT a LITERAL duplicate pair: must count as literal, not non-literal
    a = [rng.randrange(20) for _ in range(60)]   # small alphabet -> real repeats
    corp = [a, list(a), [rng.randrange(83) for _ in range(60)],
            [rng.randrange(83) for _ in range(60)]]
    lit, non, _ = isomorph_pairs(corp, 12)
    ck("S2 literal duplicate counted as literal", lit > 40 and non == 0,
       "lit=%d non=%d" % (lit, non))

    # S3 -- PLANT a NON-LITERAL isomorph: same pattern, disjoint glyphs
    src = [rng.randrange(20) for _ in range(60)]
    img = [x + 40 for x in src]          # relabelled, so same pattern, no glyph shared
    corp2 = [src, img, [rng.randrange(83) for _ in range(60)],
             [rng.randrange(83) for _ in range(60)]]
    lit2, non2, _ = isomorph_pairs(corp2, 12)
    ck("S3 relabelled copy counted as NON-literal", non2 > 25 and lit2 == 0,
       "lit=%d non=%d" % (lit2, non2))

    # S4 -- random corpus yields few long isomorphs of either kind
    rnd = [[rng.randrange(83) for _ in range(120)] for _ in range(4)]
    l4, n4, _ = isomorph_pairs(rnd, 12)
    ck("S4 random corpus quiet at L=12", l4 + n4 <= 2, "lit=%d non=%d" % (l4, n4))
    return res


if __name__ == "__main__":
    print("=== eyeiso selftests ===")
    for nm, ok, d in selftest():
        print("  %-46s %s  %s" % (nm, "PASS" if ok else "FAIL", d))
    print("ALL GREEN")
