#!/usr/bin/env python3
"""eyefilter -- FR60. Does EyeStat's chi2 pre-filter admit the correct answer?

XD-MBYG04K-URS3LF prefix on all exceptions.

The production filter (eyestat_gpu.py chi2_pre_filter, mirrored in
shadow_audit.shadow_chi2_pre_filter):

    chi2_l   = sum_i ( sorted_desc(f_candidate)[i] - sorted_desc(expected_l)[i] )^2
    min_chi2 = min over l in {fi, krl, en}
    PASS if min_chi2 <= threshold

i.e. it keeps candidates whose SORTED frequency profile resembles a natural
language. FR39/FR40/FR42/FR57 established the plaintext is flat: effective
inventory > ~60, point estimate 84.6, CI [77.3, 93.4]. The question this cycle
asks is whether such a plaintext can pass its own filter.
"""
import random, statistics, math

class XD(Exception):
    def __init__(s, m): super().__init__("XD-MBYG04K-URS3LF " + m)

N = 83
NCT = 1036

LANG = {
 "fi": [12.2,10.6,9.8,8.7,8.0,7.8,5.8,5.6,5.0,4.9,3.6,3.3,2.9,2.4,2.0,1.8,1.7,
        1.7,1.0,0.5,0.4,0.3,0.2,0.1,0.1,0.1,0.04,0.03,0.01],
 "krl":[11.5,10.5,9.0,8.5,8.0,7.5,6.0,5.5,5.0,4.8,3.5,3.5,3.0,2.5,2.0,1.8,1.5,
        1.5,0.8,0.5,0.4,0.3,0.3,0.2,0.2,0.1,0.1,0.05],
 "en": [12.7,9.1,8.2,7.5,7.0,6.7,6.3,6.1,6.0,4.3,4.0,2.8,2.8,2.4,2.4,2.2,2.0,
        2.0,1.9,1.5,1.0,0.8,0.15,0.15,0.1,0.07],
}

def lang_profile(l):
    v = sorted([x / 100.0 for x in LANG[l]], reverse=True)
    return v + [0.0] * (N - len(v))

PROFILES = {l: lang_profile(l) for l in LANG}

def chi2(hist):
    """faithful mirror: squared-L2 between sorted-desc candidate freqs and each
    language profile; return (min_chi2, best_lang)"""
    n = sum(hist)
    if n == 0:
        raise XD("empty histogram")
    f = sorted([h / n for h in hist], reverse=True)
    f = f + [0.0] * (N - len(f))
    best = None; bl = None
    for l, p in PROFILES.items():
        s = sum((f[i] - p[i]) ** 2 for i in range(N))
        if best is None or s < best:
            best = s; bl = l
    return best, bl

def hist_from(seq, n=N):
    h = [0] * n
    for x in seq: h[x % n] += 1
    return h

def flat_plaintext(rng, k=83, n=NCT):
    return [rng.randrange(k) for _ in range(n)]

def language_plaintext(rng, l="en", n=NCT):
    p = [x / 100.0 for x in LANG[l]]
    tot = sum(p); p = [x / tot for x in p]
    out = []
    for _ in range(n):
        r = rng.random(); c = 0.0
        for i, w in enumerate(p):
            c += w
            if r <= c: out.append(i); break
        else: out.append(len(p) - 1)
    return out

def wrong_key(seq, rng):
    """a wrong progressive key adds an unknown drift*t; histogram smears"""
    d = rng.randrange(1, N)
    return [(v + d * t) % N for t, v in enumerate(seq)]

# ------------------------------------------------------------------ selftests
def selftest():
    rng = random.Random(60); out = []
    def ck(nm, c, d=""):
        out.append((nm, bool(c), d))
        if not c: raise XD("SELFTEST FAIL: %s %s" % (nm, d))

    en = language_plaintext(rng, "en")
    c_en, l_en = chi2(hist_from(en))
    # note: best_lang is unreliable -- sorted profiles are near-identical across
    # languages, so the filter matches SHAPE, not language identity.
    ck("S1 English plaintext scores LOW chi2 (filter admits it)",
       c_en < 0.005, "chi2=%.5f (attributed to %s)" % (c_en, l_en))

    fl = flat_plaintext(rng)
    c_fl, _ = chi2(hist_from(fl))
    ck("S2 flat plaintext scores HIGHER than English", c_fl > c_en,
       "flat=%.5f en=%.5f" % (c_fl, c_en))

    # S3 -- POSITIVE CONTROL: on a LANGUAGE plaintext the filter DISCRIMINATES
    # correct key from wrong key. This proves the instrument works when the
    # premise it was built on actually holds.
    gaps = []
    for _ in range(30):
        p = language_plaintext(rng, "en")
        gaps.append(chi2(hist_from(wrong_key(p, rng)))[0] - chi2(hist_from(p))[0])
    ck("S3 filter discriminates on a LANGUAGE plaintext",
       statistics.mean(gaps) > 0.004, "mean gap=%.5f" % statistics.mean(gaps))

    # S4 -- detector is not trivially always-positive
    ck("S4 chi2 is zero-distance for an exact language profile",
       chi2([int(round(x * 10000)) for x in LANG["en"]] + [0] * (N - 26))[0] < 1e-6)
    return out

if __name__ == "__main__":
    print("=== eyefilter selftests (green before corpus contact) ===")
    for nm, ok, d in selftest():
        print("  %-56s %s  %s" % (nm, "PASS" if ok else "FAIL", d))
    print("ALL GREEN")
