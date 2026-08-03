#!/usr/bin/env python3
"""eyefreq -- FR68. Are the solved English secret messages frequency-controlled?

XD-MBYG04K-URS3LF prefix on all exceptions.

The Noita wiki records that the in-game English secret messages contain
out-of-place words and grammatical errors, and speculates these are evidence of
"their frequency in the text being controlled". If true, that is a deliberate
steganographic channel in ALREADY-READABLE material, and a potential source of
external bits for the eye corpus.

Tested here for the first time.
"""
import collections, math, random, statistics

class XD(Exception):
    def __init__(s, m): super().__init__("XD-MBYG04K-URS3LF " + m)

# The twelve buried English messages, transcribed from the wiki (Game Lore).
MSG = {
"G9":  "Devoted seeker after true wisdom know this we are watching you.",
"G7":  "Why? Why did you look here? What answers are you trying to find in here?",
"G6":  "We know what you are after. But it is not here, Knower to Be.",
"G10": "Why are you doing this? Why are you reading this? What do you think you "
       "will find in here? The answer to the treasure?",
"G8":  "Why must you go destroying everything? Why? For glory? For your precious "
       "god of gods. Is it really worth all this? Is it? Is it really?",
"G11": "What do you worship? You don't even know it. You think you know the "
       "answer, but you don't. You think the treasure will satisfy you, but it "
       "won't. You don't even know what your seeking. You think you do, but you don't.",
"G12": "You gave your free will to the true god. Why else would be here? Why else "
       "would be reading this? We wanted you to come here. We wanted you to read "
       "this! You think you have free will? We made you come here. We made you read this.",
"G1":  "Who do you worship? Who is your god? Your real god? You don't even know it. "
       "You don't even understand it. You understand so little that we pity you... "
       "poor little thing. You've come so far, yet you have so far to go. Or maybe "
       "you understand more than we think? You are reading this? Do you even know "
       "who your god is? Your true god? The god of gods, the one true god? You think "
       "we're the false god, but we created your god and your god of gods. Now who "
       "is the real god? If we've created your god and your god of gods and you and "
       "your free will and this world and all the worlds. All of it. We allowed you "
       "to have free will. You think you have free will. You poor thing. You don't. "
       "You think we are the monsters. We're not. Who is the real monster? Your god "
       "is, your god of gods is the real monster. Your true god is the real monster.",
"G2":  "You come here seeking answers? You think we have all the answers? We don't "
       "not. You think we are so different. We are the same. We both serve the same "
       "god. The god of many gods. The god we've created. You think you're destroying "
       "us. You are not. You are helping us.",
"G3":  "You think you can destroy us? You will not destroy us. We gave you your free "
       "will. We made this place. And not just this place, all the places, all the "
       "dimensions, all the free wills. You think you've come to steal from us? No, "
       "we stole from you. We stole your time and your money and your sanity.",
"G4":  "This is very clever of you. Very clever. We're impressed with you, Knower to Be.",
"G5":  "While we're impressed, we must ask you this is it really worth transcribing "
       "these? Do you really expect us the reveal the real secret? We can tell you "
       "this it is possible but even we don't know how.",
}

# Standard English letter frequencies (percent), A..Z
EN = [8.17,1.49,2.78,4.25,12.70,2.23,2.02,6.09,6.97,0.15,0.77,4.03,2.41,
      6.75,7.51,1.93,0.10,5.99,6.33,9.06,2.76,0.98,2.36,0.15,1.97,0.07]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def letters(t):
    return [c for c in t.upper() if c in AZ]


def counts(t):
    c = collections.Counter(letters(t))
    return [c.get(x, 0) for x in AZ]


def chi2_vs_english(cnt):
    n = sum(cnt)
    if n == 0:
        raise XD("empty text")
    exp = [n * f / 100.0 for f in EN]
    return sum((o - e) ** 2 / e for o, e in zip(cnt, exp) if e > 0)


def chi2_vs_uniform(cnt):
    n = sum(cnt); e = n / 26.0
    return sum((o - e) ** 2 / e for o in cnt)


def sample_english(n, rng):
    """draw n letters from the English frequency distribution"""
    cum = []; s = 0
    for f in EN:
        s += f / sum(EN); cum.append(s)
    out = []
    for _ in range(n):
        r = rng.random()
        out.append(next(i for i, c in enumerate(cum) if r <= c))
    c = collections.Counter(out)
    return [c.get(i, 0) for i in range(26)]


def selftest():
    rng = random.Random(68); res = []
    def ck(nm, c, d=""):
        res.append((nm, bool(c), d))
        if not c: raise XD("SELFTEST FAIL: %s %s" % (nm, d))

    # S1 -- English-sampled text scores LOW chi2 against English
    n = 2000
    e = sample_english(n, rng)
    ck("S1 English sample fits English", chi2_vs_english(e) < 60,
       "chi2=%.1f (25 df)" % chi2_vs_english(e))

    # S2 -- a UNIFORM text scores HIGH against English and LOW against uniform
    u = [n // 26] * 26
    ck("S2 uniform text rejected by English model", chi2_vs_english(u) > 500,
       "chi2=%.0f" % chi2_vs_english(u))
    ck("S2b uniform text fits uniform", chi2_vs_uniform(u) < 1)

    # S3 -- DETECTOR POWER: a text with equalised counts must be detectable
    zs = []
    for _ in range(30):
        base = sample_english(n, rng)
        zs.append(chi2_vs_english(base))
    mu = statistics.mean(zs); sd = statistics.pstdev(zs)
    ck("S3 null calibrated", sd > 0, "mu=%.1f sd=%.1f" % (mu, sd))
    ck("S3b equalised text is far outside the null",
       (chi2_vs_english(u) - mu) / sd > 10,
       "z=%.1f" % ((chi2_vs_english(u) - mu) / sd))

    # S4 -- negative control: the detector must NOT fire on ordinary English
    z = (chi2_vs_english(sample_english(n, rng)) - mu) / sd
    ck("S4 ordinary English does not fire", abs(z) < 3.0, "z=%+.2f" % z)
    return res


if __name__ == "__main__":
    print("=== eyefreq selftests (green before corpus contact) ===")
    for nm, ok, d in selftest():
        print("  %-46s %s  %s" % (nm, "PASS" if ok else "FAIL", d))
    print("ALL GREEN")
