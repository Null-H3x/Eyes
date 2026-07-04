#!/usr/bin/env python3
"""cribfit.py — positioned-crib model battery for the Noita Eye messages.

Takes Kalevala passages whose 9-mer repeat lag matches a message's #M
isomorph-pair lag, aligns them at the exact message coordinates
(#M1 / #M2 sites), and tests the (crib, message) pairing against a battery
of falsifiable key-model families:

  M0  monoalphabetic         c[i] = S(p[i])
      same-letter pairs must be same-symbol. Violation count.

  M1  linear progression     c[i] = S(p[i]) + s*i          (mod 83)
      same-letter pairs pin s = (c[j]-c[i])/(j-i); all pairs must agree.

  M2  stepped key            c[i] = S(p[i]) + g_seg(i)
      g constant on unknown segments. Statistic: minimum number of
      breakpoints needed so no same-letter violating pair lies within a
      segment (greedy interval stabbing), compared against a
      scrambled-crib null (Monte Carlo z-score).

  M3  periodic key, T=2..12  c[i] = S(p[i]) + g(i mod T)
      same-letter pairs at distance = 0 mod T must be same-symbol.

  M4  plaintext autokey      c[i] = S(p[i]) + sum_{k<i}(E(p[k]) + d)
      (Alberti/psum family). Same-letter pairs give linear equations
      over unknowns {E_a} + d in GF(83):
        sum_{k=i..j-1} E(p[k]) + d*(j-i) = c[j]-c[i]
      Gaussian elimination -> rank, consistency, #independent checks,
      p-value 83^-(checks) under uniform null, recovered E if consistent.

  M5  ciphertext autokey     c[i] = E(p[i]) +/- c[i-D],  D in 1..3
      E(p[i]) := c[i] -/+ c[i-D] must be a well-defined function of the
      letter. Violation / support counts per (D, sign).

All tests are embedding-free or solve for the embedding; none assume a
letter ordering. Position indexing matches the canonical trigram CSV.

Usage:
  cribfit.py --selftest
  cribfit.py [--csv PATH] [--corpus PATH] [--pad 10] [--null 200]
             [--out report.txt]
"""
import sys, os, argparse, random
from collections import defaultdict
import numpy as np

ERROR_PREFIX = "Internal Error Code: XD-MBYG04K-URS3LF"
M = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for cand in (HERE, os.path.dirname(HERE)):
    if cand not in sys.path:
        sys.path.insert(0, cand)
from isoscan import load_eye_csv, MASTER_ALPHABET          # noqa: E402
from kalevala_cribscan import build_stream, repeat_hits     # noqa: E402


def _discover(env, names):
    """Ordered discovery: $ENV var, then candidate paths near this file."""
    if os.environ.get(env):
        return os.environ[env]
    for base in (HERE, os.path.dirname(HERE)):
        for n in names:
            p = os.path.join(base, n)
            if os.path.exists(p):
                return p
    return None

# (message-name-in-csv, m1, m2, lag)
ANCHORS = {
    28: ("East 1", 40, 68),
    30: ("West 1", 40, 70),
    35: ("East 2", 45, 80),
}


# --------------------------------------------------------------- crib spans
def crib_positions(m1, lag, pad, msg_len, s, stream, span="full"):
    """Aligned (message_pos, letter) list.

    span='full' : contiguous padded window covering both copies and the
                  intervening text (strongest constraints, strongest
                  assumption: every intervening letter must also match).
    span='pair' : only the two 9-mer copies (weakest assumption: just the
                  isomorph-pair plaintext identity).
    """
    if span == "pair":
        ks = list(range(0, 9)) + list(range(lag, lag + 9))
    else:
        lo = -min(pad, m1, s)
        hi = lag + 9 + min(pad, msg_len - (m1 + lag + 9),
                           stream.size - (s + lag + 9))
        ks = range(lo, hi)
    return [(m1 + k, int(stream[s + k])) for k in ks]


def letter_pairs(span):
    """All same-letter position pairs (i<j) with message positions."""
    by = defaultdict(list)
    for pos, a in span:
        by[a].append(pos)
    pairs = []
    for a, ps in by.items():
        for x in range(len(ps)):
            for y in range(x + 1, len(ps)):
                pairs.append((ps[x], ps[y], a))
    return pairs, by


# ------------------------------------------------------------------- models
def m0_mono(c, pairs):
    bad = sum(1 for i, j, _ in pairs if c[i] != c[j])
    return bad, len(pairs)


def m1_linear(c, pairs):
    inv = [0] + [pow(x, M - 2, M) for x in range(1, M)]
    slopes = defaultdict(int)
    for i, j, _ in pairs:
        d = (j - i) % M
        if d:
            slopes[((c[j] - c[i]) * inv[d]) % M] += 1
    if not slopes:
        return None, 0, 0
    s, votes = max(slopes.items(), key=lambda kv: kv[1])
    return s, votes, len(pairs)


def m2_stepped(c, pairs):
    """Minimum breakpoints stabbing all violating pairs; support count."""
    viol = sorted(((i, j) for i, j, _ in pairs if c[i] != c[j]),
                  key=lambda ij: ij[1])
    breaks, last = 0, -10**9
    for i, j in viol:                       # break slot in (i, j]
        if last <= i:
            last = j
            breaks += 1
    support = sum(1 for i, j, _ in pairs if c[i] == c[j])
    return breaks, len(viol), support


def m2_null(c, span, n_iter, rng):
    """Scrambled-crib null distribution of min-breaks."""
    positions = [p for p, _ in span]
    letters = [a for _, a in span]
    stats = []
    for _ in range(n_iter):
        rng.shuffle(letters)
        pairs, _ = letter_pairs(list(zip(positions, letters)))
        b, _, _ = m2_stepped(c, pairs)
        stats.append(b)
    return float(np.mean(stats)), float(np.std(stats) or 1.0)


def m3_periodic(c, pairs, Ts=range(2, 13)):
    out = []
    for T in Ts:
        v = s = 0
        for i, j, _ in pairs:
            if (j - i) % T == 0:
                if c[i] == c[j]:
                    s += 1
                else:
                    v += 1
        out.append((T, v, s))
    return out


def m4_psum(c, span, pairs):
    """GF(83) linear system over {E_a} + d from same-letter pairs."""
    span_map = dict(span)                      # pos -> letter
    letters = sorted({a for _, a in span})
    col = {a: k for k, a in enumerate(letters)}
    ncols = len(letters) + 1                   # +1 for d
    rows = []
    for i, j, _ in pairs:
        if any(p not in span_map for p in range(i, j)):
            continue                           # need contiguous coverage
        vec = [0] * (ncols + 1)
        for p in range(i, j):
            vec[col[span_map[p]]] = (vec[col[span_map[p]]] + 1) % M
        vec[len(letters)] = (j - i) % M        # d coefficient
        vec[ncols] = (c[j] - c[i]) % M         # rhs
        rows.append(vec)
    if not rows:
        return dict(eqs=0, rank=0, checks=0, consistent=True, E=None)
    A = np.array(rows, dtype=np.int64) % M
    rank, bad = 0, 0
    r = 0
    for col_i in range(ncols):
        piv = None
        for rr in range(r, len(A)):
            if A[rr, col_i] % M:
                piv = rr
                break
        if piv is None:
            continue
        A[[r, piv]] = A[[piv, r]]
        inv = pow(int(A[r, col_i]), M - 2, M)
        A[r] = (A[r] * inv) % M
        for rr in range(len(A)):
            if rr != r and A[rr, col_i] % M:
                A[rr] = (A[rr] - A[rr, col_i] * A[r]) % M
        r += 1
    rank = r
    for rr in range(rank, len(A)):
        if A[rr, ncols] % M:                   # 0 = nonzero -> inconsistent
            bad += 1
    checks = len(A) - rank
    E = None
    if bad == 0 and rank:
        sol = [0] * ncols
        for rr in range(rank):
            lead = next((cc for cc in range(ncols) if A[rr, cc] % M), None)
            if lead is not None:
                sol[lead] = int(A[rr, ncols]) % M
        E = {MASTER_ALPHABET[a]: sol[col[a]] for a in letters}
        E["<d>"] = sol[len(letters)]
    return dict(eqs=len(rows), rank=rank, checks=checks,
                consistent=(bad == 0), n_bad=bad, E=E)


def m5_ct_autokey(c, span, Ds=(1, 2, 3)):
    span_map = dict(span)
    out = []
    for D in Ds:
        for sign, label in ((1, f"c[i]-c[i-{D}]"), (-1, f"c[i-{D}]-c[i]")):
            table, v, s = {}, 0, 0
            for pos, a in span:
                if pos - D not in span_map:
                    continue
                val = (sign * (c[pos] - c[pos - D])) % M
                if a in table:
                    if table[a] == val:
                        s += 1
                    else:
                        v += 1
                else:
                    table[a] = val
            out.append((label, v, s))
    return out


# ----------------------------------------------------------------- selftest
def selftest():
    rng = random.Random(7)
    nletters = 20
    L, lag, m1 = 110, 30, 40
    p = [rng.randrange(nletters) for _ in range(L)]
    p[m1 + lag:m1 + lag + 9] = p[m1:m1 + 9]           # forced 9-mer repeat
    S = list(range(M)); rng.shuffle(S)

    def enc(gfun):
        return [(S[p[i]] + gfun(i)) % M for i in range(L)]

    segb = sorted(rng.sample(range(10, L - 10), 4))
    segv = [rng.randrange(M) for _ in range(5)]
    def g_step(i):
        return segv[sum(1 for b in segb if i >= b)]
    E = [rng.randrange(M) for _ in range(nletters)]
    d = 5
    pre = [0] * (L + 1)
    for i in range(L):
        pre[i + 1] = (pre[i] + E[p[i]] + d) % M
    ciphers = {
        "M0": enc(lambda i: 0),
        "M1": enc(lambda i: (7 * i) % M),
        "M2": enc(g_step),
        "M3": enc(lambda i: (i % 7) * 11 % M),
        "M4": [(S[p[i]] + pre[i]) % M for i in range(L)],
    }
    c5 = [0] * L
    for i in range(L):
        c5[i] = (E[p[i]] + (c5[i - 1] if i else 17)) % M
    ciphers["M5"] = c5

    span = [(m1 - 10 + k, p[m1 - 10 + k]) for k in range(10 + lag + 9 + 10)]
    pairs, _ = letter_pairs(span)
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(f"  {name:34s} {'PASS' if cond else 'FAIL'}")
        ok &= cond

    chk("M0 detects mono (0 violations)", m0_mono(ciphers["M0"], pairs)[0] == 0)
    chk("M0 rejects stepped", m0_mono(ciphers["M2"], pairs)[0] > 0)
    s, votes, tot = m1_linear(ciphers["M1"], pairs)
    chk("M1 recovers slope 7 unanimously", s == 7 and votes == tot)
    b_true, _, _ = m2_stepped(ciphers["M2"], pairs)
    chk("M2 min-breaks <= true segments-1", b_true <= 4)
    per = dict((T, (v, sup)) for T, v, sup in m3_periodic(ciphers["M3"], pairs))
    chk("M3 T=7 clean, T=5 dirty", per[7][0] == 0 and per[5][0] > 0)
    r4 = m4_psum(ciphers["M4"], span, pairs)
    chk(f"M4 consistent ({r4['checks']} checks)",
        r4["consistent"] and r4["checks"] >= 3)
    r4x = m4_psum(ciphers["M2"], span, pairs)
    chk("M4 rejects stepped cipher", not r4x["consistent"])
    m5r = dict((lab, (v, sup)) for lab, v, sup in m5_ct_autokey(ciphers["M5"], span))
    chk("M5 D=1 clean with support",
        m5r["c[i]-c[i-1]"][0] == 0 and m5r["c[i]-c[i-1]"][1] > 0)
    # scrambled crib must break M4 consistency (with high probability)
    letters = [a for _, a in span]; rng.shuffle(letters)
    spanx = list(zip([q for q, _ in span], letters))
    px, _ = letter_pairs(spanx)
    r4s = m4_psum(ciphers["M4"], spanx, px)
    chk("M4 rejects scrambled crib", not r4s["consistent"])
    print("selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# --------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=_discover("EYES_CSV", (
        "noita_eye_data_trigrams.csv",
        "data/noita_eye_data_trigrams.csv",
        "NoitaCryptographyResearch/eye/reference/noita_eye_data_trigrams.csv")))
    ap.add_argument("--corpus", default=_discover("EYES_CORPUS", (
        "kalevala_finnish_clean.txt",
        "corpora/kalevala_finnish_clean.txt",
        "data/kalevala_finnish.txt")))
    ap.add_argument("--span", choices=("full", "pair"), default="full")
    ap.add_argument("--pad", type=int, default=10)
    ap.add_argument("--null", type=int, default=200)
    ap.add_argument("--out", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())

    if not a.csv or not a.corpus:
        sys.exit(f"{ERROR_PREFIX}\ncould not discover "
                 f"{'CSV' if not a.csv else 'corpus'} — set $EYES_CSV / "
                 f"$EYES_CORPUS or pass --csv / --corpus")
    try:
        msgs = load_eye_csv(a.csv)
        with open(a.corpus, encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        sys.exit(f"{ERROR_PREFIX}\n{e}")

    stream, srcpos, text_n = build_stream(text)
    rng = random.Random(42)
    lines = []
    emit = lines.append

    for lag, (mname, m1, m2) in ANCHORS.items():
        c = list(msgs[mname])
        for s in repeat_hits(stream, 9, lag):
            nine = "".join(MASTER_ALPHABET[stream[s + k]] for k in range(9))
            span = crib_positions(m1, lag, a.pad, len(c), s, stream, a.span)
            pairs, _ = letter_pairs(span)
            emit(f"\n=== {mname} lag {lag}  crib '{nine}' @corpus {s}  "
                 f"span {span[0][0]}..{span[-1][0]} "
                 f"({len(span)} pos, {len(pairs)} same-letter pairs) ===")
            v0, t0 = m0_mono(c, pairs)
            emit(f"  M0 mono:      {v0}/{t0} violations")
            s1, votes, tot = m1_linear(c, pairs)
            emit(f"  M1 linear:    best slope {s1} agrees {votes}/{tot}")
            b, nv, sup = m2_stepped(c, pairs)
            mu, sd = m2_null(c, span, a.null, rng)
            z = (b - mu) / sd
            emit(f"  M2 stepped:   min-breaks {b} (null {mu:.1f}±{sd:.1f}, "
                 f"z={z:+.2f}), support {sup}")
            best = sorted(m3_periodic(c, pairs), key=lambda t: (t[1], -t[2]))[:2]
            emit(f"  M3 periodic:  best {[f'T={T} v={v} s={s_}' for T, v, s_ in best]}")
            r4 = m4_psum(c, span, pairs)
            tag = ("CONSISTENT p≈83^-%d" % r4["checks"]) if r4["consistent"] \
                else f"inconsistent ({r4['n_bad']} bad rows)"
            emit(f"  M4 psum:      eqs {r4['eqs']} rank {r4['rank']} "
                 f"checks {r4['checks']} -> {tag}")
            if r4["consistent"] and r4["checks"] >= 3 and r4["E"]:
                emit(f"     recovered E: {r4['E']}")
            worst = sorted(m5_ct_autokey(c, span), key=lambda t: t[1])[:2]
            emit(f"  M5 ct-autokey: best {[f'{l} v={v} s={s_}' for l, v, s_ in worst]}")

    report = "\n".join(lines)
    print(report)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(report + "\n")


if __name__ == "__main__":
    main()
