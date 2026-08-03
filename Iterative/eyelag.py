#!/usr/bin/env python3
"""eyelag -- FR55. Decompose the lag-4 coincidence excess.

XD-MBYG04K-URS3LF prefix on all exceptions.

Two channels, both drift-free on the skeleton:
  CT channel: c[t] == c[t+d]                      <=>  Delta(g2)-Delta(g1) == 0
  PT channel: p[t] == p[t+d] (plaintext repeat)   <=>  Delta(g2)-Delta(g1) == d

Null (FR42 geometry-preserving): permute which glyph occupies each position
WITHIN each (message, component) block. Preserves block membership, positions
and the Delta multiset exactly; randomises only the plaintext.
"""
import json, random, statistics, math, sys

class XD(Exception):
    def __init__(s, m): super().__init__("XD-MBYG04K-URS3LF " + m)

DATA_PATH = "corpus.json"

C1 = {0:0,1:3,5:7,6:34,7:36,9:58,10:55,17:29,20:39,27:1,30:66,34:61,41:69,
      45:60,47:35,48:82,50:8,57:33,62:28,63:31,64:81,68:65,71:38,79:57,81:54}
C2 = {13:0,19:53,23:4,25:82,44:1,46:31,49:52,60:81,66:55,72:35,78:25}
C3 = {16:0,21:58,26:1,40:57,42:35,67:31,73:2}
C4 = {4:0,35:55,37:57}
COMPS = [C1, C2, C3, C4]
DELTA = {}
COMPOF = {}
for i, C in enumerate(COMPS):
    for g, dv in C.items():
        DELTA[g] = dv; COMPOF[g] = i

N = 83


# ---------------------------------------------------------------- channels
def channel_counts(msgs, d, comp_of, delta, lo=0):
    """Return (ct_hits, pt_hits, usable_pairs) at distance d.
    Only pairs whose two glyphs share a component are usable."""
    ct = pt = tot = 0
    for m in msgs:
        for t in range(lo, len(m) - d):
            a, b = m[t], m[t + d]
            if a not in comp_of or b not in comp_of:
                continue
            if comp_of[a] != comp_of[b]:
                continue
            tot += 1
            diff = (delta[b] - delta[a]) % N
            if diff == 0:
                ct += 1
            if diff == d % N:
                pt += 1
    return ct, pt, tot


def raw_coincidence(msgs, d, lo=0):
    """Plain ciphertext coincidence count at lag d, all positions."""
    h = n = 0
    for m in msgs:
        for t in range(lo, len(m) - d):
            n += 1
            if m[t] == m[t + d]:
                h += 1
    return h, n


# ------------------------------------------------------------------ nulls
def null_within_block(msgs, comp_of, rng):
    """FR42 geometry-preserving: permute glyphs within each (message,component)
    block. Positions not in any component are left untouched."""
    out = []
    for m in msgs:
        m = list(m)
        buckets = {}
        for t, g in enumerate(m):
            if g in comp_of:
                buckets.setdefault(comp_of[g], []).append(t)
        for c, idxs in buckets.items():
            gl = [m[t] for t in idxs]
            rng.shuffle(gl)
            for t, g in zip(idxs, gl):
                m[t] = g
        out.append(m)
    return out


def null_within_message(msgs, rng):
    """Unigram-preserving shuffle inside each message. Used for the raw
    ciphertext channel only."""
    out = []
    for m in msgs:
        m = list(m); rng.shuffle(m); out.append(m)
    return out


def z_of(obs, draws):
    mu = statistics.mean(draws)
    sd = statistics.pstdev(draws)
    if sd == 0:
        raise XD("null has zero variance; statistic is degenerate")
    return (obs - mu) / sd, mu, sd


# -------------------------------------------------------------- selftests
def selftest():
    rng = random.Random(12345)
    results = []

    def ck(name, cond, detail=""):
        results.append((name, bool(cond), detail))
        if not cond:
            raise XD("SELFTEST FAIL: %s %s" % (name, detail))

    # ---- S1: geometry-preserving null preserves the Delta multiset exactly
    msgs = [[rng.choice(list(DELTA)) for _ in range(120)] for _ in range(9)]
    prof0 = sorted(DELTA[g] for m in msgs for g in m)
    sh = null_within_block(msgs, COMPOF, rng)
    prof1 = sorted(DELTA[g] for m in sh for g in m)
    ck("S1 delta-multiset preserved", prof0 == prof1,
       "drift=%d" % sum(1 for a, b in zip(prof0, prof1) if a != b))

    # ---- S2: null preserves component membership per position
    ok = all(COMPOF[a] == COMPOF[b]
             for m0, m1 in zip(msgs, sh) for a, b in zip(m0, m1))
    ck("S2 component membership preserved", ok)

    # ---- S3: within-message shuffle preserves per-message multiset
    sh2 = null_within_message(msgs, rng)
    ck("S3 unigram shuffle preserves multiset",
       all(sorted(a) == sorted(b) for a, b in zip(msgs, sh2)))

    # ---- S4: CT channel detects a PLANTED ciphertext-repeat excess at d=4
    pl = [list(m) for m in msgs]
    for m in pl:
        for t in range(0, len(m) - 4, 9):      # plant repeats at lag 4
            m[t + 4] = m[t]
    obs, _, _ = channel_counts(pl, 4, COMPOF, DELTA)
    dr = [channel_counts(null_within_block(pl, COMPOF, rng), 4, COMPOF, DELTA)[0]
          for _ in range(200)]
    zc, _, _ = z_of(obs, dr)
    ck("S4 CT channel detects planted CT excess", zc > 4.0, "z=%+.2f" % zc)

    # ---- S5: PT channel detects a PLANTED plaintext-repeat excess at d=4
    # plaintext repeat  <=>  Delta(g2)-Delta(g1) == 4
    bydelta = {}
    for g, dv in DELTA.items():
        bydelta.setdefault((COMPOF[g], dv), g)
    pl2 = [list(m) for m in msgs]
    planted = 0
    for m in pl2:
        for t in range(0, len(m) - 4, 9):
            a = m[t]
            tgt = bydelta.get((COMPOF[a], (DELTA[a] + 4) % N))
            if tgt is not None:
                m[t + 4] = tgt; planted += 1
    ck("S5a planting produced targets", planted > 30, "planted=%d" % planted)
    obs, _, _ = channel_counts(pl2, 4, COMPOF, DELTA)
    obs = channel_counts(pl2, 4, COMPOF, DELTA)[1]
    dr = [channel_counts(null_within_block(pl2, COMPOF, rng), 4, COMPOF, DELTA)[1]
          for _ in range(200)]
    zp, _, _ = z_of(obs, dr)
    ck("S5 PT channel detects planted PT excess", zp > 4.0, "z=%+.2f" % zp)

    # ---- S6: SEPARATION -- a planted CT excess must NOT fire the PT channel
    obs = channel_counts(pl, 4, COMPOF, DELTA)[1]
    dr = [channel_counts(null_within_block(pl, COMPOF, rng), 4, COMPOF, DELTA)[1]
          for _ in range(200)]
    zsep, _, _ = z_of(obs, dr)
    ck("S6 channels separate (CT plant quiet in PT)", abs(zsep) < 3.0,
       "z=%+.2f" % zsep)

    # ---- S7: NEGATIVE CONTROL -- clean random corpus fires neither channel
    clean = [[rng.choice(list(DELTA)) for _ in range(120)] for _ in range(9)]
    for lbl, idx in (("CT", 0), ("PT", 1)):
        obs = channel_counts(clean, 4, COMPOF, DELTA)[idx]
        dr = [channel_counts(null_within_block(clean, COMPOF, rng), 4,
                             COMPOF, DELTA)[idx] for _ in range(200)]
        zz, _, _ = z_of(obs, dr)
        ck("S7 %s quiet on clean corpus" % lbl, abs(zz) < 3.0, "z=%+.2f" % zz)

    return results


if __name__ == "__main__":
    print("=== eyelag selftests (must be green before corpus contact) ===")
    for nm, ok, det in selftest():
        print("  %-46s %s  %s" % (nm, "PASS" if ok else "FAIL", det))
    print("ALL GREEN")
