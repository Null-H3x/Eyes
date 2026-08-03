#!/usr/bin/env python3
"""eyeperiod -- FR56. Two surviving explanations for the lag-4 excess.

XD-MBYG04K-URS3LF prefix on all exceptions.

P1  PERIODICITY. If K has period 4, then c[t]=c[t+4] <=> p[t]=p[t+4], i.e. the
    lag-4 excess IS plaintext coincidence ("aligned fraction"). Under a period-p
    keystream each coset t=r mod p is monoalphabetic, so within-coset IoC equals
    the plaintext IoC. Under progressive K it sits at 1/83.
    This matters beyond lag-4: an exact period-4 keystream contradicts the
    progressive premise the entire 384-relation skeleton rests on.

P2  SELF-ISOMORPH RUNS. FR55 tested CHAINS (c[t]=c[t+4]=c[t+8]) and found none,
    but never tested RUNS -- consecutive t both being lag-4 coincidences, which
    is the signature of a passage repeating at internal offset 4.
"""
import json, random, statistics, collections

class XD(Exception):
    def __init__(s, m): super().__init__("XD-MBYG04K-URS3LF " + m)

N = 83


def ioc(seq):
    n = len(seq)
    if n < 2:
        return None
    c = collections.Counter(seq)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1))


def coset_ioc(msgs, p):
    """Pooled within-coset IoC at period p, computed per message then pooled by
    pair counts (never pool across messages -- FR45's lesson)."""
    num = den = 0
    for m in msgs:
        for r in range(p):
            s = m[r::p]
            if len(s) < 2:
                continue
            c = collections.Counter(s)
            num += sum(v * (v - 1) for v in c.values())
            den += len(s) * (len(s) - 1)
    if den == 0:
        raise XD("no coset pairs at period %d" % p)
    return num / den


def lag_hits(msgs, d=4):
    """Return, per message, the sorted list of t with c[t]==c[t+d]."""
    return [[t for t in range(len(m) - d) if m[t] == m[t + d]] for m in msgs]


def run_stats(msgs, d=4):
    """Runs of CONSECUTIVE t that are lag-d coincidences."""
    runs = []
    for hits in lag_hits(msgs, d):
        if not hits:
            continue
        cur = 1
        for a, b in zip(hits, hits[1:]):
            if b == a + 1:
                cur += 1
            else:
                runs.append(cur); cur = 1
        runs.append(cur)
    mx = max(runs) if runs else 0
    n2 = sum(1 for r in runs if r >= 2)
    return mx, n2, runs


def shuffle_msgs(msgs, rng):
    out = []
    for m in msgs:
        c = list(m); rng.shuffle(c); out.append(c)
    return out


def z_of(obs, draws):
    mu = statistics.mean(draws); sd = statistics.pstdev(draws)
    if sd == 0:
        raise XD("degenerate null (zero variance)")
    return (obs - mu) / sd, mu, sd


# --------------------------------------------------------------- selftests
def selftest():
    rng = random.Random(4242)
    out = []

    def ck(name, cond, det=""):
        out.append((name, bool(cond), det))
        if not cond:
            raise XD("SELFTEST FAIL: %s %s" % (name, det))

    lens = [99, 103, 118, 102, 137, 124, 119, 120, 114]

    # ---- S1: PERIOD-4 PLANT must fire the coset test at p=4
    per = []
    K = [rng.randrange(N) for _ in range(4)]
    for L in lens:
        pt = [rng.randrange(40) for _ in range(L)]        # inventory 40
        per.append([(pt[t] + K[t % 4]) % N for t in range(L)])
    c4 = coset_ioc(per, 4)
    ck("S1 period-4 plant elevates coset-4 IoC vs UNIFORM", c4 > 1.8 / N,
       "coset4=%.4f uniform=%.4f" % (c4, 1 / N))

    # ---- S2: the plant must peak AT p=4, not elsewhere
    prof = {p: coset_ioc(per, p) for p in range(2, 13)}
    ck("S2 plant elevated at multiples of 4, not at 3/5",
       prof[4] > 1.5 * max(prof[3], prof[5]),
       "p4=%.4f p3=%.4f p5=%.4f" % (prof[4], prof[3], prof[5]))

    # ---- S3: PROGRESSIVE plant must be QUIET at every period (neg. control)
    prog = []
    for L in lens:
        drift = rng.randrange(1, N); b = rng.randrange(N)
        pt = [rng.randrange(40) for _ in range(L)]
        prog.append([(pt[t] + b + drift * t) % N for t in range(L)])
    pp = {p: coset_ioc(prog, p) for p in range(2, 13)}
    ck("S3 progressive plant quiet at all periods",
       all(v < 1.6 / N for v in pp.values()),
       "max=%.4f vs 1/83=%.4f" % (max(pp.values()), 1 / N))

    # ---- S4: RUN detector fires on a planted self-isomorph at offset 4
    iso = [[rng.randrange(N) for _ in range(L)] for L in lens]
    for m in iso:
        for t in range(30, 40):        # copy a 10-long passage to t+4
            m[t + 4] = m[t]
    mx, n2, _ = run_stats(iso)
    ck("S4 run detector fires on planted offset-4 repeat", mx >= 6,
       "maxrun=%d" % mx)

    # ---- S5: run detector quiet on a clean corpus
    clean = [[rng.randrange(N) for _ in range(L)] for L in lens]
    mxc, n2c, _ = run_stats(clean)
    ck("S5 run detector quiet on clean corpus", mxc <= 2, "maxrun=%d" % mxc)

    # ---- S6: shuffle null preserves per-message multiset
    sh = shuffle_msgs(clean, rng)
    ck("S6 null preserves multiset",
       all(sorted(a) == sorted(b) for a, b in zip(clean, sh)))

    # ---- S7: coset test has POWER at the observed effect size.
    # If the lag-4 excess (rate 0.026) were plaintext coincidence under period-4,
    # coset-4 IoC would be ~0.026. Verify that is separable from 1/83.
    tgt = []
    K = [rng.randrange(N) for _ in range(4)]
    for L in lens:
        pt = [rng.randrange(38) for _ in range(L)]   # 1/38 ~ 0.026
        tgt.append([(pt[t] + K[t % 4]) % N for t in range(L)])
    obs = coset_ioc(tgt, 4)
    dr = [coset_ioc(shuffle_msgs(tgt, rng), 4) for _ in range(300)]
    z, mu, _ = z_of(obs, dr)
    ck("S7 coset test powered at the observed effect size", z > 6.0,
       "z=%+.1f (IoC %.4f)" % (z, obs))

    return out


if __name__ == "__main__":
    print("=== eyeperiod selftests (green before corpus contact) ===")
    for nm, ok, det in selftest():
        print("  %-50s %s  %s" % (nm, "PASS" if ok else "FAIL", det))
    print("ALL GREEN")
