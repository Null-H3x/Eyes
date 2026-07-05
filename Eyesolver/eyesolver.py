#!/usr/bin/env python3
"""eyesolver.py — a purpose-built classical-cipher solver for the Noita Eye
corpus (N=83, scattered embedding), covering BOTH competing cipher models with
one engine: the repo's STATIC reading (Quagmire-IV with a progressive/Trithemius
key — the "AZDecrypt against the corpus" case) and the community's DYNAMIC reading
(plaintext-autokey Alberti).

Off-the-shelf AZDecrypt / stblake-polyalphabetic are hardcoded for 26-letter
alphabets and standard key structures, so they cannot ingest N=83-with-unknown-
embedding directly. This reimplements the same algorithm class (shotgun hill
climb + simulated annealing + strong n-gram objective + crib anchoring) for our
exact structure, seeded by the 16 gauge-invariant pins.

WHAT THE SELFTEST ESTABLISHED (see README):
Both engines are SOUND — they recover planted language plaintext when seeded near
the solution. But the double-mixed search only becomes navigable at ~60 of 83
correct q-values; from the 16 pins we actually have, NEITHER model converges,
with the strongest 3-gram objective, and cribs help only marginally (static) or
hurt via state-propagation (autokey). This is the Quagmire-IV / double-mixed
hardness, quantified on our structure. The tool is therefore validated and ready,
and doubles as an independent confirmation of the pin-count wall: run it on the
real corpus and it will not read — the same wall, reached from the solver side.

Models
------
static : c_m[t] = C[(sign*E[L[t]] + base_tri + drift*t) mod N]
         decrypt L[t] = M[(q[c]-drift*t-base) mod N]      (vectorized)
autokey: c[t]   = C[(E[L[t]] + S(t)) mod N],  S(t)=init+sum_{k<t} E[L[k]]
         decrypt sequentially, accumulating the recovered code           (state)

Key = (q: 83-perm seeded by pins) + (M: 83->alphabet read map) + params
(3 bases for static / init for autokey). Search: parallel shotgun restarts, SA.

Usage
-----
  python3 eyesolver.py --selftest
  python3 eyesolver.py --model static  --lang finnish --restarts 64
  python3 eyesolver.py --model autokey --lang karelian --crib-file crib.tsv
Languages: english | finnish | karelian (LMs built from ../corpora).
Run the heavy search on many cores: --restarts scales across CPUs.
"""
from __future__ import annotations
import sys, os, argparse, random, math, json
from multiprocessing import Pool
import numpy as np

ERROR_PREFIX = "Internal Error Code: XD-MBYG04K-URS3LF"
N = 83
HERE = os.path.dirname(os.path.abspath(__file__))
for c in (HERE, os.path.dirname(HERE),
          os.path.join(os.path.dirname(HERE), "noita_eye_core"),
          os.path.join(os.path.dirname(HERE), "eyeforward")):
    if os.path.isdir(c) and c not in sys.path:
        sys.path.insert(0, c)

ALPHABETS = {
    "english":  "abcdefghijklmnopqrstuvwxyz ",
    "finnish":  "abcdefghijklmnopqrstuvwxyzäö ",
    "karelian": "abcčdefghijklmnoprsštuvyzžäö ",
}
TRIPLET = {0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1, 6: 2, 7: 2, 8: 2}  # msg idx -> triplet

# The 16 gauge-invariant pins (symbol -> position in C), from iso_relax on the
# refrain component E1/W1/E2. Hardcoded so the real-corpus run needs no external
# dependency; override with --pins-file or recompute via iso_relax if available.
KNOWN_PINS = {5: 35, 13: 13, 17: 15, 18: 28, 19: 66, 21: 43, 23: 23, 31: 76,
              44: 8, 46: 38, 48: 68, 49: 71, 57: 25, 59: 78, 64: 73, 65: 53}

CORPUS_FILES = {"english": "english_big.txt", "finnish": "kalevala_finnish_clean.txt"}


# ------------------------------------------------------------- language model
def build_lm(lang, corpdir, k=3, cap=4_000_000):
    alpha = ALPHABETS[lang]; A = len(alpha); posmap = {c: i for i, c in enumerate(alpha)}
    if lang == "karelian":
        import glob, re
        xmls = glob.glob(os.path.join(corpdir, "corpus-olo", "converted", "**", "*.xml"),
                         recursive=True)
        if not xmls:
            raise RuntimeError(
                f"{ERROR_PREFIX}\nKarelian corpus not found under {corpdir}/corpus-olo/.\n"
                f"Pass --corpora <dir> pointing at the folder that contains 'corpus-olo/'.")
        raw = ""
        for x in xmls[:3]:
            raw += re.sub(r"<[^>]+>", " ", open(x, encoding="utf-8", errors="ignore").read(cap))
        text = raw.lower()
    else:
        fp = os.path.join(corpdir, CORPUS_FILES[lang])
        if not os.path.isfile(fp):
            raise RuntimeError(
                f"{ERROR_PREFIX}\nlanguage corpus not found: {fp}\n"
                f"Looked in corpora dir: {corpdir}\n"
                f"Fix: put '{CORPUS_FILES[lang]}' there, or pass "
                f"--corpora <dir-containing-the-.txt-corpora>.")
        text = open(fp, encoding="utf-8", errors="ignore").read(cap).lower()
    seq = np.array([posmap[c] for c in text if c in posmap], dtype=np.int64)
    if len(seq) < 10000:
        raise RuntimeError(f"{ERROR_PREFIX}\ntoo little {lang} text ({len(seq)})")
    if k == 3:
        idx = seq[:-2] * A * A + seq[1:-1] * A + seq[2:]
        cnt = np.bincount(idx, minlength=A ** 3).astype(np.float64) + 0.05
        cnt = cnt.reshape(A * A, A); cnt /= cnt.sum(1, keepdims=True)
        logp = np.log(cnt).ravel()
    else:  # k==4
        idx = ((seq[:-3] * A + seq[1:-2]) * A + seq[2:-1]) * A + seq[3:]
        cnt = np.bincount(idx, minlength=A ** 4).astype(np.float64) + 0.02
        cnt = cnt.reshape(A ** 3, A); cnt /= cnt.sum(1, keepdims=True)
        logp = np.log(cnt).ravel()
    uni = np.bincount(seq, minlength=A).astype(float); uni /= uni.sum()
    ref = _score(seq[:5000], logp, A, k)
    return dict(alpha=alpha, A=A, k=k, logp=logp, uni=uni, ref=ref, posmap=posmap)


def _score(L, logp, A, k):
    if k == 3:
        return logp[L[:-2] * A * A + L[1:-1] * A + L[2:]].sum() / max(1, len(L) - 2)
    return logp[((L[:-3] * A + L[1:-2]) * A + L[2:-1]) * A + L[3:]].sum() / max(1, len(L) - 3)


# ----------------------------------------------------------------- decrypt
def decrypt_static(q, M, ct, tri, drift, bases):
    t = np.arange(len(ct))
    base = bases[tri]
    return M[(q[ct] - drift * t - base) % N]


def decrypt_autokey(q, M, ct, init, bounds=None):
    """Sequential autokey decrypt. State resets to `init` at each message start
    (bounds = sorted message-start offsets); a single message uses bounds=[0]."""
    L = np.empty(len(ct), np.int64)
    qc = q[ct]
    bset = set(bounds) if bounds is not None else {0}
    S = init
    for t in range(len(ct)):
        if t in bset:
            S = init
        e = (qc[t] - S) % N; L[t] = M[e]; S = (S + e) % N
    return L


# ------------------------------------------------------------- one restart
def _restart(args):
    (model, ct, tri_ranges, pins, cribpos, cribval, lm_pack, iters, seed, drift) = args
    alpha, A, k, logp, uni = lm_pack
    rng = random.Random(seed)
    fixed = set(pins); free_syms = [s for s in range(N) if s not in fixed]
    used = set(pins.values()); free_codes = [c for c in range(N) if c not in used]
    q = np.zeros(N, np.int64)
    for s, c in pins.items(): q[s] = c
    fc = free_codes[:]; rng.shuffle(fc)
    for s, c in zip(free_syms, fc): q[s] = c
    # init M by frequency matching on the (message-0-triplet) de-drift
    if model == "static":
        D = (q[ct] - np.arange(len(ct))) % N
    else:
        D = q[ct]
    order_c = np.argsort(-np.bincount(D, minlength=N).astype(float))
    order_l = np.argsort(-uni)
    M = np.zeros(N, np.int64)
    for i, c in enumerate(order_c): M[c] = order_l[i % A]
    init = rng.randrange(N); bases = [0, rng.randrange(N), rng.randrange(N)]
    msg_bounds = [lo for (lo, hi, tr) in tri_ranges]

    def dec(q, M, init, bases):
        if model == "static":
            out = np.empty(len(ct), np.int64)
            for (lo, hi, tr) in tri_ranges:
                out[lo:hi] = decrypt_static(q, M, ct[lo:hi], tr, drift, bases)
            return out
        return decrypt_autokey(q, M, ct, init, bounds=msg_bounds)

    def sc(q, M, init, bases):
        L = dec(q, M, init, bases); s = _score(L, logp, A, k)
        if cribpos.size:
            s += 3.0 * (L[cribpos] == cribval).mean()
        return s

    n_tri = len({tr for _, _, tr in tri_ranges})
    q_frac, m_frac = (0.45, 1.0) if (model == "static" and n_tri == 1) else (0.40, 0.85)
    cur = sc(q, M, init, bases); best = cur
    bq, bM, binit, bbases = q.copy(), M.copy(), init, bases[:]
    T0, T1 = 0.6, 0.02
    for it in range(iters):
        T = T0 * (T1 / T0) ** (it / iters); r = rng.random()
        if r < q_frac and len(free_syms) >= 2:
            a, b = rng.sample(free_syms, 2); q[a], q[b] = q[b], q[a]
            nw = sc(q, M, init, bases)
            if nw >= cur or rng.random() < math.exp((nw - cur) / T): cur = nw
            else: q[a], q[b] = q[b], q[a]
        elif r < m_frac:
            c = rng.randrange(N); o = M[c]; M[c] = rng.randrange(A)
            nw = sc(q, M, init, bases)
            if nw >= cur or rng.random() < math.exp((nw - cur) / T): cur = nw
            else: M[c] = o
        else:
            if model == "autokey":
                o = init; init = rng.randrange(N); nw = sc(q, M, init, bases)
                if nw >= cur or rng.random() < math.exp((nw - cur) / T): cur = nw
                else: init = o
            else:
                j = rng.choice([1, 2]); o = bases[j]; bases[j] = rng.randrange(N)
                nw = sc(q, M, init, bases)
                if nw >= cur or rng.random() < math.exp((nw - cur) / T): cur = nw
                else: bases[j] = o
        if cur > best:
            best = cur; bq, bM, binit, bbases = q.copy(), M.copy(), init, bases[:]
    return (best, bq, bM, binit, bbases)


# --------------------------------------------------------------- driver
def solve(model, ct, tri_ranges, pins, crib, lm, restarts=8, iters=200000,
          drift=1, procs=None):
    cribpos = np.array(list(crib.keys()), dtype=int) if crib else np.array([], int)
    cribval = np.array([crib[p] for p in crib], dtype=int) if crib else np.array([], int)
    lm_pack = (lm["alpha"], lm["A"], lm["k"], lm["logp"], lm["uni"])
    jobs = [(model, ct, tri_ranges, pins, cribpos, cribval, lm_pack, iters, s, drift)
            for s in range(restarts)]
    if procs == 1 or restarts == 1:
        res = [_restart(j) for j in jobs]
    else:
        with Pool(procs) as p:
            res = p.map(_restart, jobs)
    return max(res, key=lambda r: r[0])


# --------------------------------------------------------------- selftest
def selftest(corpdir):
    ok = True
    def chk(name, cond):
        nonlocal ok; print(f"  {name:52s} {'PASS' if cond else 'FAIL'}"); ok &= cond
    lm = build_lm("english", corpdir, k=3)
    A = lm["A"]; posmap = lm["posmap"]
    txt = open(os.path.join(corpdir, "english_big.txt"), encoding="utf-8",
               errors="ignore").read(1_500_000).lower()
    pt = np.array([posmap[c] for c in txt[50000:50400] if c in posmap][:300])
    rng = random.Random(7)
    E = list(range(A)); rng.shuffle(E)
    C = list(range(N)); rng.shuffle(C); q = np.zeros(N, np.int64)
    for p, v in enumerate(C): q[v] = p

    # STATIC engine: seed near solution (62 pins) -> must recover
    ct = np.array([C[(E[pt[t]] + t) % N] for t in range(len(pt))])
    tri_ranges = [(0, len(ct), 0)]
    sp = {s: int(q[s]) for s in random.Random(3).sample(range(N), 70)}
    r = solve("static", ct, tri_ranges, sp, {}, lm, restarts=4, iters=300000, procs=4)
    dec = np.empty(len(ct), np.int64)
    dec[:] = decrypt_static(r[1], r[2], ct, 0, 1, r[4])
    acc = (dec == pt).mean()
    chk(f"static engine converges from 70-pin seed (acc={acc:.0%}, vs 9% floor)", acc > 0.5)

    # AUTOKEY engine: seed high (76) — autokey propagates errors, so validate the
    # machinery near-complete; a short instance keeps the sequential decrypt fast.
    pt2 = pt[:150]
    ct2 = np.empty(len(pt2), np.int64); S = 5
    for t in range(len(pt2)):
        e = E[pt2[t]]; ct2[t] = C[(e + S) % N]; S = (S + e) % N
    sp2 = {s: int(q[s]) for s in random.Random(4).sample(range(N), 76)}
    r2 = solve("autokey", ct2, [(0, len(ct2), 0)], sp2, {}, lm,
               restarts=4, iters=70000, procs=4)
    dec2 = decrypt_autokey(r2[1], r2[2], ct2, r2[3])
    acc2 = (dec2 == pt2).mean()
    chk(f"autokey engine recovers 76-pin-seeded plant (acc={acc2:.0%})", acc2 > 0.4)

    # the WALL: static from 16 pins must NOT converge (documents the finding)
    sp16 = {s: int(q[s]) for s in random.Random(5).sample(range(N), 16)}
    r3 = solve("static", ct, tri_ranges, sp16, {}, lm, restarts=4, iters=120000, procs=4)
    dec3 = decrypt_static(r3[1], r3[2], ct, 0, 1, r3[4])
    acc3 = (dec3 == pt).mean()
    chk(f"16-pin static stays UNSOLVED (acc={acc3:.0%}, expected <30%)", acc3 < 0.3)

    print("selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# ------------------------------------------------------------------- main
def find_corpora(hint=None):
    """Locate the corpora directory. Tries the hint, then a set of common
    locations relative to the script and CWD, then walks up looking for a folder
    that actually contains english_big.txt."""
    cands = []
    if hint:
        cands.append(hint)
    for base in (HERE, os.path.dirname(HERE), os.path.dirname(os.path.dirname(HERE)),
                 os.getcwd()):
        cands.append(os.path.join(base, "corpora"))
        cands.append(base)  # in case files sit directly there
    # walk up from HERE
    d = HERE
    for _ in range(6):
        cands.append(os.path.join(d, "corpora"))
        d = os.path.dirname(d)
    seen = set()
    for c in cands:
        c = os.path.abspath(c)
        if c in seen or not os.path.isdir(c):
            continue
        seen.add(c)
        if (os.path.isfile(os.path.join(c, "english_big.txt")) or
                os.path.isdir(os.path.join(c, "corpus-olo"))):
            return c
    return hint or os.path.join(os.path.dirname(HERE), "corpora")


def find_corpus_json(hint=None):
    cands = [hint] if hint else []
    for base in (HERE, os.path.dirname(HERE), os.getcwd()):
        cands += [os.path.join(base, "noita_eye_core", "corpus.json"),
                  os.path.join(base, "corpus.json")]
    for c in cands:
        if c and os.path.isfile(c):
            return c
    return None


def load_pins(pins_file=None, cts=None, labels=None):
    """Pins from (1) --pins-file 'symbol<TAB>position' lines, else (2) iso_relax
    if importable, else (3) the hardcoded KNOWN_PINS. Never hard-fails."""
    if pins_file:
        pins = {}
        with open(pins_file) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                s, p = line.replace("\t", " ").split()[:2]
                pins[int(s)] = int(p)
        return pins, f"file:{pins_file}"
    if cts is not None:
        try:
            import iso_relax
            idx = {l: i for i, l in enumerate(labels)}
            r = iso_relax.relax([cts[idx[l]] for l in ["East 1", "West 1", "East 2"]], N)
            if r.pins:
                return dict(r.pins), "iso_relax"
        except Exception:
            pass
    return dict(KNOWN_PINS), "hardcoded KNOWN_PINS"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--model", choices=["static", "autokey"], default="static")
    ap.add_argument("--lang", choices=list(ALPHABETS), default="finnish")
    ap.add_argument("--corpus", default=None)
    ap.add_argument("--corpora", default=None)
    ap.add_argument("--restarts", type=int, default=8)
    ap.add_argument("--iters", type=int, default=200000)
    ap.add_argument("--k", type=int, default=3, choices=[3, 4])
    ap.add_argument("--procs", type=int, default=None)
    ap.add_argument("--crib-file", default=None, help="TSV: position<TAB>letter per line")
    ap.add_argument("--pins-file", default=None, help="TSV: symbol<TAB>position per line")
    a = ap.parse_args()
    corpdir = find_corpora(a.corpora)
    if a.selftest:
        sys.exit(selftest(corpdir))

    path = find_corpus_json(a.corpus)
    if not path:
        sys.exit(f"{ERROR_PREFIX}\ncorpus.json not found. Pass --corpus "
                 f"<path-to-noita_eye_core/corpus.json>.")
    d = json.load(open(path)); labels = d["message_labels"]
    cts = [list(c) for c in d["ciphertexts"]]
    flat = []; tri_ranges = []; off = 0
    for m, ct in enumerate(cts):
        tri_ranges.append((off, off + len(ct), TRIPLET[m])); flat += ct; off += len(ct)
    flat = np.array(flat)

    pins, pin_src = load_pins(a.pins_file, cts, labels)
    crib = {}
    if a.crib_file:
        for ln, line in enumerate(open(a.crib_file), 1):
            line = line.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                print(f"  (crib line {ln} skipped: expected 'pos<TAB>letter')"); continue
            ch = parts[1].strip().lower()
            if ch not in ALPHABETS[a.lang]:
                print(f"  (crib line {ln} skipped: '{ch}' not in {a.lang} alphabet)"); continue
            try:
                crib[int(parts[0])] = ALPHABETS[a.lang].index(ch)
            except ValueError:
                print(f"  (crib line {ln} skipped: bad position '{parts[0]}')")

    try:
        lm = build_lm(a.lang, corpdir, k=a.k)
    except RuntimeError as e:
        sys.exit(str(e))
    print(f"model={a.model} lang={a.lang} pins={len(pins)} ({pin_src}) "
          f"crib={len(crib)} restarts={a.restarts} iters={a.iters} corpus={path}")
    print(f"language reference score = {lm['ref']:.3f} (a real read lands near this)")
    r = solve(a.model, flat, tri_ranges, pins, crib, lm,
              restarts=a.restarts, iters=a.iters, procs=a.procs)
    best, bq, bM, binit, bbases = r
    if a.model == "static":
        out = np.empty(len(flat), np.int64)
        for lo, hi, tr in tri_ranges:
            out[lo:hi] = decrypt_static(bq, bM, flat[lo:hi], tr, 1, bbases)
    else:
        out = decrypt_autokey(bq, bM, flat, binit, bounds=[lo for lo, hi, tr in tri_ranges])
    inv = {i: c for c, i in lm["posmap"].items()}
    print(f"\nbest score = {best:.3f}  (ref {lm['ref']:.3f})")
    print("best decrypt (first message):")
    print("".join(inv[x] for x in out[:tri_ranges[0][1]]))
    read = best > lm["ref"] - 0.30   # within 0.30 nats/char of real language
    print(f"\nverdict: {'CANDIDATE READ — inspect by eye + crib/overlap gates' if read else 'no read (expected from 16 pins; see README on the wall)'}")


if __name__ == "__main__":
    main()
