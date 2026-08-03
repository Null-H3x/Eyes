#!/usr/bin/env python3
"""
eyeoffset -- discriminating FR10's surviving premises (i) and (iii) with a
statistic that does not go through constraint satisfiability at all, plus
the certification comparison FR10 nominated. Read-only.

THE MECHANISM. Two messages of one triplet share the keystream K_g. Compare
them literally at the same position:

    c_1[t] = C[(p_1[t] + off_1 + K_g[t]) mod 83]
    c_2[t] = C[(p_2[t] + off_2 + K_g[t]) mod 83]

    c_1[t] == c_2[t]  <=>  p_1[t] - p_2[t] == off_2 - off_1.

K CANCELS EXACTLY. So literal agreement is governed solely by whether the
plaintext difference equals the offset gap -- independent of the keystream
model, the drift, and the alphabet. Two consequences:

  * off_1 == off_2  ->  literal agreement == PLAINTEXT agreement. For a
    near-duplicate pair that is large.
  * off_1 != off_2  ->  agreement requires the plaintext to differ by exactly
    that nonzero constant at each agreeing position. For arbitrary plaintext
    that is chance, whatever the messages share.

Cross-triplet pairs share no keystream and no offset, so they supply an
empirical chance baseline that already absorbs unigram skew.

WHY THIS DISCRIMINATES. FR9 proved (and FR10 confirmed) that under
per-message PROGRESSIVE rows the sound constraint inventory FORBIDS
within-triplet offset equality for E1/E2, W1/E2, E3/W3, E4/W4, E4/E5 and
W4/E5. Every forbidden pair therefore carries a sharp prediction: literal
body agreement at the cross-triplet baseline. Elevated agreement on a
forbidden pair falsifies the forced distinctness -- and hence the reading
that forces it -- without appealing to any of the machinery that produced
the contradiction in the first place.

Openings are excluded from the statistic throughout (they are the disputed
spans); only body positions are counted.
"""

import json, math, os, random, sys
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyecore", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyecore as EC                       # noqa: E402
import eyegauge as EG                      # noqa: E402
import eyereach as ER                      # noqa: E402
import iso_relax as IR                     # noqa: E402
import isomorph as iso                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

TRIPLETS = EG.TRIPLETS
FORBIDDEN = {("East 1", "East 2"), ("West 1", "East 2"), ("East 3", "West 3"),
             ("East 4", "West 4"), ("East 4", "East 5"), ("West 4", "East 5")}

PREREG = {
    "body_start": 25,
    "alpha": 0.01,               # per-pair significance, Bonferroni-corrected
    "baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
    "prediction": "under progressive, FR9-forbidden pairs must sit at the "
                  "cross-triplet baseline",
}

def binom_tail(n, k, p):
    if k <= 0: return 1.0
    return sum(math.comb(n, i) * p**i * (1-p)**(n-i) for i in range(k, n+1))

# ------------------------------------------------------------------ statistic
def agreement_table(M, labels, tri, body_start):
    rows = []
    for a, b in combinations(labels, 2):
        A, B = M[a], M[b]
        n = min(len(A), len(B))
        if n <= body_start: continue
        ag = sum(1 for t in range(body_start, n) if A[t] == B[t])
        rows.append(dict(a=a, b=b, same=(tri[a] == tri[b]), ag=ag,
                         n=n - body_start))
    cross = [r for r in rows if not r["same"]]
    base = sum(r["ag"] for r in cross) / sum(r["n"] for r in cross)
    for r in rows:
        r["rate"] = r["ag"] / r["n"]
        r["x"] = r["rate"] / base
        r["p"] = binom_tail(r["n"], r["ag"], base)
        key = (r["a"], r["b"])
        r["fr9"] = ("FORBIDDEN" if (key in FORBIDDEN or key[::-1] in FORBIDDEN)
                    else ("permitted" if r["same"] else ""))
    return rows, base

def verdict(rows, base, alpha, n_within):
    bonf = alpha / max(1, n_within)
    out = []
    for r in rows:
        if not r["same"]: continue
        sig = r["p"] < bonf
        out.append(dict(pair=f"{r['a']}/{r['b']}", fr9=r["fr9"], ag=r["ag"],
                        n=r["n"], x=r["x"], p=r["p"], sig=sig,
                        conflict=(sig and r["fr9"] == "FORBIDDEN")))
    return out, bonf

# ------------------------------------------------------------------ plants
def plant_pair(shared_offset, seed=3, T=140, share_frac=0.30, body_start=25):
    """two messages of one triplet: same keystream, shared plaintext on a
    fraction of body positions, offsets equal or not. Returns the pair and a
    third message from a different triplet (independent keystream) as the
    baseline partner."""
    rng = random.Random(seed)
    C = list(range(N)); rng.shuffle(C)
    K = [rng.randrange(N) for _ in range(T)]
    K2 = [rng.randrange(N) for _ in range(T)]
    off1 = 17; off2 = 17 if shared_offset else 44
    p1 = [rng.randrange(N) for _ in range(T)]
    p2 = [rng.randrange(N) for _ in range(T)]
    for t in range(body_start, T):
        if rng.random() < share_frac: p2[t] = p1[t]
    p3 = [rng.randrange(N) for _ in range(T)]
    enc = lambda p, off, KK: [C[(p[t] + off + KK[t]) % N] for t in range(T)]
    return enc(p1, off1, K), enc(p2, off2, K), enc(p3, 61, K2)

def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: agreement mechanism, both directions")
    bs = PREREG["body_start"]

    # shared offsets -> agreement tracks plaintext sharing
    A, B, Cc = plant_pair(True)
    n = len(A) - bs
    ag = sum(1 for t in range(bs, len(A)) if A[t] == B[t])
    agx = sum(1 for t in range(bs, len(A)) if A[t] == Cc[t])
    check("shared offset: agreement tracks shared plaintext",
          ag / n > 0.20, f"(rate={ag/n:.3f}, expected ~0.30)")
    check("shared offset: cross-keystream partner stays at chance",
          agx / n < 0.05, f"(rate={agx/n:.3f})")

    # distinct offsets -> shared plaintext yields NO literal agreement
    A2, B2, C2 = plant_pair(False)
    ag2 = sum(1 for t in range(bs, len(A2)) if A2[t] == B2[t])
    check("DISTINCT offsets: identical plaintext gives chance agreement "
          "(the negative control)", ag2 / n < 0.05,
          f"(rate={ag2/n:.3f}, same 30% shared plaintext)")

    # the statistic separates the two cases decisively
    check("statistic separates shared from distinct offsets",
          (ag / n) > 5 * (ag2 / n + 1e-9), f"({ag/n:.3f} vs {ag2/n:.3f})")

    # binomial tail sanity
    check("binomial tail sane", abs(binom_tail(10, 10, 0.5) - 1/1024) < 1e-12
          and binom_tail(10, 0, 0.5) == 1.0)

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    c = json.load(open(corpus_path))
    labels = c["message_labels"]; M = dict(zip(labels, c["ciphertexts"]))
    cts = [list(x) for x in c["ciphertexts"]]
    Lx = {lab: i for i, lab in enumerate(labels)}
    tri = {m: t for t, ms in TRIPLETS.items() for m in ms}

    r = IR.relax(cts, N, seed=0); bg = PREREG["baseline_guard"]
    if (r.linked_strict, r.distinct_strict, len(r.pins)) != \
       (bg["linked"], bg["distinct"], bg["pins"]):
        fail("baseline reproduction mismatch")
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")
    print(f"\npre-registered prediction: {PREREG['prediction']}")

    rows, base = agreement_table(M, labels, tri, PREREG["body_start"])
    cross = [x for x in rows if not x["same"]]
    print(f"\nS1 cross-triplet baseline (no shared keystream, no shared offset): "
          f"{sum(x['ag'] for x in cross)}/{sum(x['n'] for x in cross)} = "
          f"{base:.5f}  (x{base*N:.2f} of 1/83)")

    res, bonf = verdict(rows, base, PREREG["alpha"], 9)
    print(f"\nS2 within-triplet body agreement (Bonferroni alpha = {bonf:.2e}):")
    print(f"  {'pair':20s} {'FR9':>10s} {'agree':>6s} {'n':>4s} {'xbase':>6s} "
          f"{'p':>10s}  verdict")
    for v in sorted(res, key=lambda z: -z["x"]):
        tag = ("CONFLICTS WITH PROGRESSIVE" if v["conflict"]
               else ("elevated (consistent)" if v["sig"] else "at baseline"))
        print(f"  {v['pair']:20s} {v['fr9']:>10s} {v['ag']:6d} {v['n']:4d} "
              f"{v['x']:6.2f} {v['p']:10.2e}  {tag}")

    conf = [v for v in res if v["conflict"]]
    print(f"\n  pairs elevated DESPITE being forbidden under progressive: "
          f"{len(conf)} -> {[v['pair'] for v in conf]}")

    print("\nS3 what distinct offsets would require of the plaintext:")
    for v in sorted(conf, key=lambda z: -z["x"]):
        a, b = v["pair"].split("/")
        print(f"  {v['pair']}: {v['ag']} body positions agree literally. Under "
              f"forced-distinct offsets each would need p[{a[0]}{a[-1]}] - "
              f"p[{b[0]}{b[-1]}] to equal the same nonzero constant; expected "
              f"at baseline {v['n']*base:.1f}.")

    print("\nS4 certification under the two surviving readings:")
    ctx = EG.build_context(cts, labels, atlas_path)
    pool = ctx["apairs"] + ctx["strict"]
    trii = {Lx[m]: t for m, t in tri.items()}
    T1o = EG.opening_pairs(labels, EG.OPENINGS[:1])
    T3o = EG.opening_pairs(labels, EG.OPENINGS[1:])
    def certify(pool_, model):
        if not EC.sat(cts, ctx, trii, pool_, model): return None
        gf = iso.GFSystem(N)
        rf = EC.rows_factory(ctx, trii, model)
        for pr in pool_:
            for row, rhs in rf(pr, cts, N):
                if gf.classify(row, rhs) == "pivot": gf.add(row, rhs)
        dom, _ = ER.certified_domain(gf)
        png, taint = ER.pin_grade(dom)
        sol = gf.solve(); syms = [v for v in sol if v < N]
        distinct = len({sol[v] for v in syms})
        return dom, png, taint, len(syms), distinct
    settings = [("(i)  progressive, openings excluded", pool, "progressive"),
                ("(iii) Gromark, openings included", pool + T1o + T3o, "gromark"),
                ("control: Gromark, openings excluded", pool, "gromark")]
    doms = {}
    for name, pl, model in settings:
        out = certify(pl, model)
        if out is None:
            print(f"  {name:38s}: UNSATISFIABLE"); continue
        dom, png, taint, nsym, distinct = out
        doms[name] = dom
        degen = " <-- DEGENERATE: all symbols merged" if distinct <= 1 else ""
        print(f"  {name:38s}: certified={len(dom):3d} pin-grade={len(png):3d} "
              f"solution symbols={nsym} distinct values={distinct}{degen}")
    keys = list(doms)
    print("  [note] a reading whose solution collapses to one value certifies "
          "nothing usable: it fits by absorbing, not by determining")
    if len(keys) >= 2:
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                shared, bad = ER.cross_validate(doms[keys[i]], doms[keys[j]])
                print(f"  cross-validate [{keys[i][:12]}] vs [{keys[j][:12]}]: "
                      f"shared={len(shared)} disagreements={len(bad)}")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
