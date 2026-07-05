#!/usr/bin/env python3
"""dedrift_probe.py — fingerprint the Eye plaintext's statistical *type* through
the de-drift channel, WITHOUT recovering the full alphabet.

The idea (see cipher_data/cipher_family_field_guide_2.md)
---------------------------------------------------------
The surviving model is the linear class c_m[t] = C[(σ·p_m[t] + base_m + drift·t)
mod N].  The drift carries no key entropy, so define

    d[t] := q[c_m[t]] − drift·t  =  σ·p_m[t] + base_m           (q = C⁻¹)

and the position term cancels: d is a MONOALPHABETIC image of the plaintext, per
message (base_m is just an additive shift).  We do not have full q — but we have
16 gauge-invariant pins (verified: the two West-1 refrain instances de-drift to
identical values, 9/9), and a pin is a *value* that applies corpus-wide because C
is global.  So at every position carrying a pinned symbol we can read d[t], i.e.
the plaintext value up to (σ, base_m, one global rotation).

Every gauge nuisance — σ, base_m, the rotation — is an additive/negation
transform, and collision-based statistics (IoC = Σpᵢ², triple-rate = Σpᵢ³) are
invariant to all of them.  So the de-drift channel measures the plaintext's
frequency *shape* directly, bypassing the alphabet-ordering wall that blocks
everything else.  Natural language has IoC ≈ 0.066–0.073; this probe asks what
the Eye plaintext's IoC actually is and which source type it matches.

What it does
------------
1. Pull pins from iso_relax on the refrain component (or take injected pins).
2. Auto-detect the drift sign by refrain self-consistency, then de-drift every
   pinned position into per-message value lists.
3. Estimate IoC (within-message-pooled, base-invariant, unbiased) and the
   triple-collision rate, with a bootstrap CI.
4. Monte-Carlo a null for each candidate plaintext model (natural Finnish /
   English, uniform-K, base64, hex, Finnish bigrams/syllables, flattened
   language) at the OBSERVED per-message sample sizes, and rank models by how
   well their null brackets the observed statistic.

`--selftest` plants corpora whose plaintext is drawn from a KNOWN type
(correlated real Finnish, uniform-53, base64) and asserts (a) the de-drift
estimator recovers the planted IoC — i.e. the pinned-position sample is
representative — and (b) the fingerprint ranks the planted type first and
rejects the wrong ones.  A green run means the instrument can tell plaintext
types apart, which is the whole point.
"""
from __future__ import annotations
import sys, os, argparse, random, math
from collections import Counter
import numpy as np

ERROR_PREFIX = "Internal Error Code: XD-MBYG04K-URS3LF"
N = 83
HERE = os.path.dirname(os.path.abspath(__file__))
for c in (HERE, os.path.dirname(HERE),
          os.path.join(os.path.dirname(HERE), "noita_eye_core"),
          os.path.join(os.path.dirname(HERE), "eyeforward")):
    if os.path.isdir(c) and c not in sys.path:
        sys.path.insert(0, c)

REFRAIN = [("West 1", 32), ("West 1", 62), ("East 2", 37), ("East 2", 72)]  # L=25
# The refrain is ONE plaintext repeated 4x; counting all instances oversamples its
# letters and inflates IoC. Keep the first instance (West 1@32); exclude the rest so
# each unique plaintext position is counted once.
EXCLUDE_DUP = [("West 1", 62, 25), ("East 2", 37, 25), ("East 2", 72, 25)]


# ----------------------------------------------------------- statistics
def ioc_within(values_by_msg):
    """Within-message-pooled unbiased IoC: Σ_m Σ_v n(n-1) / Σ_m N(N-1).
    Base-invariant (only within-message pairs) and pools all data."""
    num = den = 0
    for vals in values_by_msg:
        c = Counter(vals); Nm = len(vals)
        num += sum(v * (v - 1) for v in c.values())
        den += Nm * (Nm - 1)
    return num / den if den else float("nan")


def triple_within(values_by_msg):
    """Within-message triple-collision rate Σ Σ n(n-1)(n-2) / Σ N(N-1)(N-2).
    Separates flat vs peaked distributions at equal IoC."""
    num = den = 0
    for vals in values_by_msg:
        c = Counter(vals); Nm = len(vals)
        num += sum(v * (v - 1) * (v - 2) for v in c.values())
        den += Nm * (Nm - 1) * (Nm - 2)
    return num / den if den else float("nan")


def jackknife_ci(values_by_msg, stat, z=1.645):
    """Leave-one-message-out jackknife CI. Unlike bootstrap-with-replacement, this
    introduces no spurious collisions, so it is valid for collision statistics."""
    full = stat(values_by_msg)
    nz = [v for v in values_by_msg if len(v) > 1]
    loo = []
    for i in range(len(nz)):
        e = stat([v for j, v in enumerate(nz) if j != i])
        if not math.isnan(e):
            loo.append(e)
    n = len(loo)
    if n < 2:
        return (full, full)
    mean = sum(loo) / n
    var = (n - 1) / n * sum((x - mean) ** 2 for x in loo)
    se = math.sqrt(var)
    return (full - z * se, full + z * se)


# ------------------------------------------------------- candidate models
def _freqs_from_text(path, alpha):
    pos = {ch: i for i, ch in enumerate(alpha)}
    c = Counter()
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            for chunk in iter(lambda: f.read(1 << 20), ""):
                for ch in chunk.lower():
                    if ch in pos:
                        c[ch] += 1
    except FileNotFoundError:
        return None
    tot = sum(c.values())
    return np.array([c[ch] / tot for ch in alpha]) if tot else None


def _bigram_freqs(path, alpha, top=None):
    pos = set(alpha); c = Counter(); prev = None
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            for chunk in iter(lambda: f.read(1 << 20), ""):
                for ch in chunk.lower():
                    if ch not in pos:
                        prev = None; continue
                    if prev is not None:
                        c[prev + ch] += 1
                    prev = ch
    except FileNotFoundError:
        return None
    items = c.most_common(top) if top else c.items()
    tot = sum(v for _, v in items)
    return np.array([v / tot for _, v in items]) if tot else None


def _syllable_freqs(path, alpha):
    """Crude CV(C) syllabification of Finnish: split on vowel groups. Approximates
    a syllabary inventory (coarser than bigrams, finer than letters)."""
    vowels = set("aeiouyäö"); pos = set(alpha)
    c = Counter()
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            text = f.read(4 << 20).lower()
    except FileNotFoundError:
        return None
    for word in text.split():
        w = [ch for ch in word if ch in pos]
        if not w:
            continue
        syl = ""; seen_v = False
        for ch in w:
            isv = ch in vowels
            if isv and seen_v and syl:
                c[syl] += 1; syl = ch; seen_v = True
            else:
                syl += ch; seen_v = seen_v or isv
        if syl:
            c[syl] += 1
    tot = sum(c.values())
    return np.array([v / tot for v in c.values()]) if tot else None


def candidate_models(corpdir):
    fi = os.path.join(corpdir, "kalevala_finnish_clean.txt")
    en = os.path.join(corpdir, "english_big.txt")
    M = {}
    def uni(k): return np.full(k, 1 / k)
    for k in (16, 26, 29, 40, 53, 64, 83):
        M[f"uniform-{k}"] = uni(k)
    M["hex (uniform-16)"] = uni(16)
    M["base64 (uniform-64)"] = uni(64)
    ff = _freqs_from_text(fi, "abcdefghijklmnopqrstuvwxyzäö")
    ef = _freqs_from_text(en, "abcdefghijklmnopqrstuvwxyz")
    if ff is not None:
        M["natural-finnish"] = ff
        M["finnish-flattened^0.5"] = (lambda p: p / p.sum())(ff ** 0.5)
    if ef is not None:
        M["natural-english"] = ef
    bg = _bigram_freqs(fi, "abcdefghijklmnopqrstuvwxyzäö", top=120)
    if bg is not None:
        M["finnish-bigram(top120)"] = bg / bg.sum()
    sy = _syllable_freqs(fi, "abcdefghijklmnopqrstuvwxyzäö")
    if sy is not None:
        M["finnish-syllable"] = sy
    return M


def model_ioc(p):       # theoretical IoC of a distribution
    return float((p * p).sum())


def mc_null(p_model, sizes, stat, trials=1500, seed=1):
    """Monte-Carlo the statistic under a plaintext model at the observed
    per-message sample sizes (iid draws from the model marginal + a random base,
    which the statistic ignores)."""
    rng = np.random.default_rng(seed)
    K = len(p_model)
    out = []
    for _ in range(trials):
        vbm = [list(rng.choice(K, size=n, p=p_model)) for n in sizes]
        e = stat(vbm)
        if not math.isnan(e):
            out.append(e)
    return np.array(out)


# ------------------------------------------------------------- de-drift
def detect_drift_and_dedrift(cts_by_label, labels, pins):
    """Pick drift sign by refrain self-consistency; return per-message de-drifted
    value lists and the chosen drift."""
    idx = {l: i for i, l in enumerate(labels)}

    def consistency(drift):
        W1 = cts_by_label[idx["West 1"]]; ok = tot = 0
        for i in range(25):
            ca, cb = W1[32 + i], W1[62 + i]
            if ca in pins and cb in pins:
                da = (pins[ca] - drift * (32 + i)) % N
                db = (pins[cb] - drift * (62 + i)) % N
                tot += 1; ok += (da == db)
        return ok, tot

    best = None
    for drift in (1, -1):
        ok, tot = consistency(drift)
        if best is None or ok > best[1]:
            best = (drift, ok, tot)
    drift = best[0]
    excl = {(lab, s + i) for (lab, s, L) in EXCLUDE_DUP for i in range(L)}
    vbm = []
    for lab in labels:
        ct = cts_by_label[idx[lab]]
        vbm.append([(pins[c] - drift * t) % N for t, c in enumerate(ct)
                    if c in pins and (lab, t) not in excl])
    return vbm, drift, best[1], best[2]


def get_refrain_pins(cts_by_label, labels):
    import iso_relax
    idx = {l: i for i, l in enumerate(labels)}
    r = iso_relax.relax([cts_by_label[idx[l]] for l in ["East 1", "West 1", "East 2"]], N)
    return dict(r.pins)


# --------------------------------------------------------------- report
def fingerprint(vbm, corpdir, label=""):
    sizes = [len(v) for v in vbm]
    obs_ioc = ioc_within(vbm)
    obs_tri = triple_within(vbm)
    ci = jackknife_ci(vbm, ioc_within)
    n = sum(sizes)
    print(f"\n=== de-drift fingerprint {label} ===")
    print(f"samples: {n} positions across {len([s for s in sizes if s])} messages "
          f"(per-msg {sizes})")
    print(f"observed IoC (within-message) = {obs_ioc:.4f}   90% CI [{ci[0]:.4f}, {ci[1]:.4f}]")
    if obs_ioc > 0:
        eff = 1 / obs_ioc
        print(f"effective alphabet size 1/IoC ≈ {eff:.0f}   "
              f"(CI [{1/ci[1]:.0f}, {1/ci[0]:.0f}])")
    print(f"observed triple-rate = {obs_tri:.5f}")

    models = candidate_models(corpdir)
    rows = []
    for name, p in models.items():
        null = mc_null(p, sizes, ioc_within)
        if len(null) == 0:
            continue
        pct = 100 * (null < obs_ioc).mean()          # percentile of observed in null
        # two-sided consistency: is observed within the model's central 90%?
        lo, hi = np.percentile(null, [5, 95])
        consistent = lo <= obs_ioc <= hi
        rows.append((abs(model_ioc(p) - obs_ioc), name, model_ioc(p),
                     null.mean(), (lo, hi), consistent, pct))
    rows.sort()
    print(f"\n{'model':24s} {'IoC(model)':>10} {'MC mean':>8} {'MC 90% band':>18} {'obs in band?':>12}")
    for _, name, mi, mm, (lo, hi), cons, pct in rows:
        band = f"[{lo:.4f},{hi:.4f}]"
        print(f"{name:24s} {mi:>10.4f} {mm:>8.4f} {band:>18} {'YES' if cons else 'no':>12}")
    top = [r for r in rows if r[5]]
    print("\nconsistent with observed (obs inside MC 90% band):",
          ", ".join(r[1] for r in top) if top else "(none — observed between grid points)")
    print("rejected (natural language, etc.):",
          ", ".join(r[1] for r in rows if not r[5] and
                    ("natural" in r[1] or r[1] in ("hex (uniform-16)",))))
    return obs_ioc, ci, rows


# --------------------------------------------------------------- plant lab
def _plant(model_kind, corpdir, seed=0, msg_lens=None):
    """Plant a pmp corpus. model_kind: 'finnish-real' (correlated text),
    'uniform-53', 'base64'. Returns (labels, cts, true_pins)."""
    rng = random.Random(seed)
    C = list(range(N)); rng.shuffle(C)
    q = [0] * N
    for posn, val in enumerate(C):
        q[val] = posn
    labels = ["East 1", "West 1", "East 2", "West 2", "East 3",
              "West 3", "East 4", "West 4", "East 5"]
    lens = msg_lens or {l: L for l, L in zip(labels,
                        [99, 103, 118, 102, 137, 124, 119, 120, 114])}
    bases = {l: rng.randrange(N) for l in labels}

    if model_kind == "finnish-real":
        alpha = "abcdefghijklmnopqrstuvwxyzäö"; pos = {ch: i for i, ch in enumerate(alpha)}
        txt = open(os.path.join(corpdir, "kalevala_finnish_clean.txt"),
                   encoding="utf-8", errors="ignore").read().lower()
        stream = [pos[ch] for ch in txt if ch in pos]
        def draw(nn, off): return stream[off:off + nn]
        seq_mode = True
    else:
        K = 53 if model_kind == "uniform-53" else 64
        def draw(nn, off): return [rng.randrange(K) for _ in range(nn)]
        seq_mode = False

    pv = {}; off = 100
    # shared refrain (drawn from same model) so structure exists, though we use true pins
    refr = draw(25, 0)
    for lab in labels:
        L = lens[lab]
        body = draw(L, off); off += L + 7
        pv[lab] = list(body)
    for lab, s in REFRAIN:
        pv[lab][s:s + 25] = list(refr)

    cts = []
    for lab in labels:
        ct = [C[(pv[lab][t] + bases[lab] + t) % N] for t in range(len(pv[lab]))]
        cts.append(ct)
    # true pins: mimic real coverage — expose 16 symbols, but GUARANTEE a few land
    # on aligned West-1 refrain positions so the drift self-consistency path has data
    W1 = cts[labels.index("West 1")]
    forced = set()
    for i in range(0, 25, 6):
        forced.add(W1[32 + i]); forced.add(W1[62 + i])
    pool = [s for s in range(N) if s not in forced]
    exposed = forced | set(rng.sample(pool, max(0, 16 - len(forced))))
    true_pins = {s: q[s] for s in exposed}
    return labels, cts, true_pins


# --------------------------------------------------------------- selftest
def selftest(corpdir):
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(f"  {name:54s} {'PASS' if cond else 'FAIL'}")
        ok &= cond

    # representativeness + recovery: plant three known types, de-drift with true
    # pins, check recovered IoC matches the planted type's IoC.
    finnish_ioc = model_ioc(_freqs_from_text(
        os.path.join(corpdir, "kalevala_finnish_clean.txt"),
        "abcdefghijklmnopqrstuvwxyzäö"))
    targets = [("finnish-real", finnish_ioc, 0.015),
               ("uniform-53", 1 / 53, 0.006),
               ("base64", 1 / 64, 0.006)]
    recovered = {}
    for kind, want, tol in targets:
        labels, cts, pins = _plant(kind, corpdir, seed=hash(kind) % 1000)
        vbm, drift, okc, totc = detect_drift_and_dedrift(cts, labels, pins)
        got = ioc_within(vbm)
        recovered[kind] = got
        chk(f"{kind}: drift self-consistent ({okc}/{totc})", okc == totc and totc > 0)
        chk(f"{kind}: de-drift IoC recovers planted ({got:.4f}~{want:.4f})",
            abs(got - want) < tol)

    # discrimination: recovered IoCs must be well-separated and ordered
    chk("recovered IoCs ordered finnish > uniform53 > base64",
        recovered["finnish-real"] > recovered["uniform-53"] > recovered["base64"])

    # identification: for a finnish plant, natural language must be IN-band and
    # uniform-83 OUT; for a base64 plant, the reverse.
    for kind, must_in, must_out in [
            ("finnish-real", "natural-finnish", "uniform-83"),
            ("base64", "base64 (uniform-64)", "natural-finnish")]:
        labels, cts, pins = _plant(kind, corpdir, seed=7)
        vbm, *_ = detect_drift_and_dedrift(cts, labels, pins)
        sizes = [len(v) for v in vbm]; obs = ioc_within(vbm)
        models = candidate_models(corpdir)
        def inband(mn):
            null = mc_null(models[mn], sizes, ioc_within, trials=1200)
            lo, hi = np.percentile(null, [5, 95]); return lo <= obs <= hi
        chk(f"{kind}: '{must_in}' consistent", inband(must_in))
        chk(f"{kind}: '{must_out}' rejected", not inband(must_out))

    print("selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# ------------------------------------------------------------------- main
def _discover():
    for p in ("noita_eye_core/corpus.json", "corpus.json",
              "NoitaCryptographyResearch/eye/reference/noita_eye_data_trigrams.csv"):
        for base in (HERE, os.path.dirname(HERE)):
            fp = os.path.join(base, p)
            if os.path.exists(fp):
                return fp
    return None


def _load(path):
    if path.endswith(".json"):
        import json
        d = json.load(open(path)); return d["message_labels"], [list(c) for c in d["ciphertexts"]]
    from isoscan import load_eye_csv
    m = load_eye_csv(path); return list(m.keys()), [list(v) for v in m.values()]


def _corpdir():
    for c in (os.path.join(os.path.dirname(HERE), "corpora"),
              os.path.join(HERE, "corpora")):
        if os.path.isdir(c):
            return c
    return "."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--corpus", default=None)
    ap.add_argument("--corpora", default=None, help="dir with reference language texts")
    a = ap.parse_args()
    corpdir = a.corpora or _corpdir()
    if a.selftest:
        sys.exit(selftest(corpdir))

    path = a.corpus or _discover()
    if not path:
        sys.exit(f"{ERROR_PREFIX}\nno corpus found; pass --corpus")
    labels, cts = _load(path)
    try:
        pins = get_refrain_pins(cts, labels)
    except Exception as e:
        sys.exit(f"{ERROR_PREFIX}\ncould not obtain pins (need iso_relax on path): {e}")
    vbm, drift, okc, totc = detect_drift_and_dedrift(cts, labels, pins)
    print(f"pins: {len(pins)}   drift gauge: {drift:+d} "
          f"(refrain self-consistency {okc}/{totc})")
    fingerprint(vbm, corpdir, label="(real corpus)")


if __name__ == "__main__":
    main()
