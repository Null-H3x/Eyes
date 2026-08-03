#!/usr/bin/env python3
"""
eyecho -- decomposition of the lag-d glyph-coincidence spectrum for the
Noita eye corpus: template-anchored vs corpus-wide, position-locked vs
content-driven. Read-only; no isomorph is modified, filtered, or weighted.

THE FRAME. Under the surviving static family (FR1),
c_m[t] = C[(sigma*p_m[t] + base_m + K_g[t]) mod 83], a same-message glyph
coincidence c[t] = c[t+d] holds iff sigma*(p[t]-p[t+d]) == K[t+d]-K[t].
The coincidence rate at lag d is therefore the inner product of the
plaintext lag-d difference distribution and the keystream lag-d increment
distribution. If EITHER is uniform the rate is exactly 1/83. The observed
2.16x excess at d=4 is a JOINT alignment constraint -- it cannot belong to
K alone or plaintext alone.

DISCRIMINATORS.
  S2 template masking: recompute the spectrum with all certified isomorph
     spans removed. Template-anchored excess vanishes; corpus-wide excess
     survives.
  S3 clean co-location: a site is t with c[t]==c[t+4]. If K_g has
     position-locked lag-4 returns (Delta-K4[t]=0 at sites T_K), every
     message in the triplet concentrates sites on T_K, so sites CO-LOCATE
     across messages -- including at positions where the two messages carry
     DIFFERENT glyph values (clean events: c_A[t] != c_B[t], which removes
     the shared-plaintext/template confound without needing base
     knowledge). Content-driven excess (e.g. progressive gauge, where a
     site means the de-drifted stream repeats: u[t]=u[t+d]) has no
     positional anchor and co-locates at chance. Cross-triplet pairs share
     no K and are the built-in negative control.
  S5 multiples: an exactly-period-4 K forces equal excess at d=8,12,...;
     the spectrum decides.

Pre-registration: PREREG below, frozen on the plant suite. Disclosure: the
inside/outside-span site split for d=4 was computed as design input before
this file existed (16 in / 10 out); the masking threshold was set from
plants regardless, and every co-location statistic was corpus-unpeeked
until the selftest went green.
"""

import json, math, os, random, sys

ERR = "XD-MBYG04K-URS3LF"
N = 83
D_MAX = 12                       # spectrum lags analysed in plants/verdicts
D4 = 4
NULL_ITERS = 2000
RNG_SEED = 20260722

PREREG = {
    "spike_z": 3.0,              # z >= 3 vs unigram-permutation null = spike
    "masked_template_z": 2.0,    # masked z(4) <  2.0 -> template-anchored
    "masked_corpuswide_z": 3.0,  # masked z(4) >= 3.0 -> corpus-wide
    "coloc_fire_p": 1e-3,        # within-triplet pooled clean co-location
    "coloc_control_p": 0.01,     # cross-triplet pooled must stay above this
    "period_multiple_z": 2.0,    # z(8) < 2 while z(4) >= 4 -> period-4 K out
}

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

# ---------------------------------------------------------------- corpus
def load_corpus(path):
    c = json.load(open(path))
    return dict(zip(c["message_labels"], c["ciphertexts"]))

TRIPLETS = {"T1": ["East 1", "West 1", "East 2"],
            "T2": ["West 2", "East 3", "West 3"],
            "T3": ["East 4", "West 4", "East 5"]}

def atlas_spans(atlas_path, corpus):
    a = json.load(open(atlas_path))
    spans = {lab: set() for lab in corpus}
    for cls in a["classes"]:
        L = cls["length"]
        for it in cls["instances"]:
            if corpus[it["message"]][it["start"]:it["start"] + L] != it["values"]:
                fail("atlas values do not match corpus")
            spans[it["message"]].update(range(it["start"], it["start"] + L))
    return spans

# ---------------------------------------------------------------- spectrum
def sites(ct, d):
    return [t for t in range(len(ct) - d) if ct[t] == ct[t + d]]

def spectrum_z(msgs, d, rng, mask=None, iters=NULL_ITERS):
    """pooled coincidence count at lag d vs per-message unigram-permutation
    null. mask[lab] = set of positions excluded (a comparison (t,t+d) is
    dropped if either endpoint is masked)."""
    def count(streams):
        H = X = 0
        for lab, ct in streams.items():
            mk = mask.get(lab, set()) if mask else set()
            for t in range(len(ct) - d):
                if t in mk or (t + d) in mk: continue
                X += 1; H += (ct[t] == ct[t + d])
        return H, X
    H, X = count(msgs)
    null = []
    for _ in range(iters):
        sh = {}
        for lab, ct in msgs.items():
            s = list(ct); rng.shuffle(s); sh[lab] = s
        null.append(count(sh)[0])
    mu = sum(null) / len(null)
    sd = (sum((x - mu) ** 2 for x in null) / (len(null) - 1)) ** 0.5 or 1e-9
    return dict(hits=H, comps=X, x=(H / X * N if X else 0.0),
                mu=mu, sd=sd, z=(H - mu) / sd)

# ---------------------------------------------------------------- co-location
def clean_colocation(msgs, pairs, d, rng, tmin=8, iters=NULL_ITERS):
    """pooled clean co-location for a list of (labA, labB) pairs.
    site: t in [tmin, minlen-d-1] with c[t]==c[t+d] in that message.
    clean event: t a site in BOTH messages AND c_A[t] != c_B[t].
    null: redraw B's site positions uniformly over the eligible window
    (count preserved), recount clean events against real glyphs."""
    per_pair = []
    pooled_obs = 0
    pooled_null = [0] * iters
    for a, b in pairs:
        A, B = msgs[a], msgs[b]
        lo, hi = tmin, min(len(A), len(B)) - d - 1
        elig = list(range(lo, hi + 1))
        SA = set(t for t in sites(A, d) if lo <= t <= hi)
        SB = set(t for t in sites(B, d) if lo <= t <= hi)
        obs = sum(1 for t in SA & SB if A[t] != B[t])
        pooled_obs += obs
        nb = len(SB)
        for i in range(iters):
            fake = rng.sample(elig, nb) if nb <= len(elig) else elig
            pooled_null[i] += sum(1 for t in fake if t in SA and A[t] != B[t])
        per_pair.append(dict(pair=f"{a} / {b}", nA=len(SA), nB=len(SB), obs=obs))
    ge = sum(1 for v in pooled_null if v >= pooled_obs)
    mu = sum(pooled_null) / iters
    return dict(pairs=per_pair, obs=pooled_obs, null_mu=mu,
                p=(ge + 1) / (iters + 1))

def triplet_pairs(triplets):
    within = []
    for ms in triplets.values():
        for i in range(len(ms)):
            for j in range(i + 1, len(ms)):
                within.append((ms[i], ms[j]))
    labs = [m for ms in triplets.values() for m in ms]
    tri_of = {m: t for t, ms in triplets.items() for m in ms}
    cross = [(labs[i], labs[j]) for i in range(len(labs))
             for j in range(i + 1, len(labs)) if tri_of[labs[i]] != tri_of[labs[j]]]
    return within, cross

# ---------------------------------------------------------------- plants
def weighted_alphabet(rng, coll=0.07, size=20):
    syms = rng.sample(range(N), size)
    w = [1.0 / (i + 1) ** 0.85 for i in range(size)]
    s = sum(w); w = [x / s for x in w]
    c = sum(x * x for x in w)
    scale = (coll / c) ** 0.5
    w = [min(1.0, x * scale) for x in w]
    s = sum(w); w = [x / s for x in w]
    return syms, w

def draw(rng, syms, w):
    r = rng.random(); acc = 0.0
    for s, x in zip(syms, w):
        acc += x
        if r <= acc: return s
    return syms[-1]

def plant_corpus(rng, kind, L=110, sigma=1):
    """3 triplets x 3 messages under the static model with engineered
    structure. Returns (msgs, triplets, mask_spans)."""
    msgs = {}; spans = {}
    trips = {"T1": ["m1", "m2", "m3"], "T2": ["m4", "m5", "m6"],
             "T3": ["m7", "m8", "m9"]}
    for tname, ms in trips.items():
        # per-triplet keystream
        if kind in ("null", "template", "prog_delta"):
            pass
        if kind in ("null", "template", "prog_delta"):
            if kind == "null":
                K = [rng.randrange(N) for _ in range(L)]
            else:
                K = [(1 * t) % N for t in range(L)]          # progressive
        elif kind in ("k_return", "k_return_strong"):
            pr = 0.28 if kind == "k_return" else 0.15
            K = []
            for t in range(L):
                if t >= 4 and rng.random() < pr: K.append(K[t - 4])
                else: K.append(rng.randrange(N))
        elif kind == "k_period4":
            blk = [rng.randrange(N) for _ in range(4)]
            K = [blk[t % 4] for t in range(L)]
        else:
            fail(f"unknown plant kind {kind}")
        syms, w = weighted_alphabet(rng, coll=(0.15 if kind == "k_return_strong" else 0.07))
        passage = None
        if kind == "template":
            passage = [draw(rng, syms, w) for _ in range(20)]
            for j in (3, 9):                                  # internal d=4 links
                passage[j + 4] = (passage[j] - 4 * sigma) % N
        for lab in ms:
            base = rng.randrange(N)
            p = [draw(rng, syms, w) for _ in range(L)]
            if kind == "prog_delta":
                for t in range(L - 4):
                    if rng.random() < 0.03:
                        p[t + 4] = (p[t] - 4 * sigma) % N      # Delta-p4 = -4s
            mspan = set()
            if kind == "template":
                for s0 in (15, 60):
                    p[s0:s0 + 20] = passage
                    mspan.update(range(s0, s0 + 20))
            C = list(range(N)); rng.shuffle(C)
            msgs[lab] = [C[(sigma * p[t] + base + K[t]) % N] for t in range(L)]
            spans[lab] = mspan
    return msgs, trips, spans

# ---------------------------------------------------------------- selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    def fresh(tag): return random.Random(f"{RNG_SEED}:{tag}")

    print("selftest: planted spectra and co-location at corpus-matched shapes")

    # P1 null: no spike, no co-location
    msgs, trips, spans = plant_corpus(fresh("p1"), "null")
    sp = {d: spectrum_z(msgs, d, fresh(f"p1s{d}"), iters=400) for d in range(1, D_MAX + 1)}
    spikes = [d for d in sp if sp[d]["z"] >= PREREG["spike_z"]]
    check("null: no spectrum spikes", len(spikes) == 0, f"{spikes}")
    w, x = triplet_pairs(trips)
    cw = clean_colocation(msgs, w, D4, fresh("p1c"), iters=400)
    check("null: within-triplet co-location quiet", cw["p"] > 0.05,
          f"(obs={cw['obs']}, p={cw['p']:.3f})")

    # P2 K-return: spike at 4, survives masking-of-random-spans, co-location
    # fires within-triplet, cross-triplet control quiet
    msgs, trips, spans = plant_corpus(fresh("p2"), "k_return")
    s4 = spectrum_z(msgs, D4, fresh("p2s"), iters=400)
    check("k_return: spike at d=4", s4["z"] >= PREREG["spike_z"], f"(x={s4['x']:.2f}, z={s4['z']:.1f})")
    fake_mask = {lab: set(range(30, 70)) for lab in msgs}
    s4m = spectrum_z(msgs, D4, fresh("p2sm"), mask=fake_mask, iters=400)
    check("k_return: survives span masking (corpus-wide)",
          s4m["z"] >= PREREG["masked_corpuswide_z"], f"(masked z={s4m['z']:.1f})")
    # mechanism check on a strong plant (site supply boosted); power at
    # corpus-like counts is MEASURED and reported, not asserted
    msgs2, trips2, _ = plant_corpus(fresh("p2b"), "k_return_strong")
    w2, x2 = triplet_pairs(trips2)
    cw2 = clean_colocation(msgs2, w2, D4, fresh("p2bc"), iters=800)
    cx2 = clean_colocation(msgs2, x2, D4, fresh("p2bx"), iters=800)
    check("k_return_strong: within-triplet clean co-location fires (p<0.01)",
          cw2["p"] < 0.01,
          f"(obs={cw2['obs']} vs mu={cw2['null_mu']:.2f}, p={cw2['p']:.4f})")
    check("k_return_strong: cross-triplet control quiet",
          cx2["p"] > PREREG["coloc_control_p"],
          f"(obs={cx2['obs']} vs mu={cx2['null_mu']:.2f}, p={cx2['p']:.3f})")
    fires = 0; obs_sum = 0.0; mu_sum = 0.0
    for i in range(8):
        m3, t3, _ = plant_corpus(fresh(f"pw{i}"), "k_return")
        w3, _ = triplet_pairs(t3)
        c3 = clean_colocation(m3, w3, D4, fresh(f"pwc{i}"), iters=200)
        fires += (c3["p"] < PREREG["coloc_fire_p"])
        obs_sum += c3["obs"]; mu_sum += c3["null_mu"]
    print(f"  [note] co-location power, diffuse anchors (q=0.28, coll=0.07, corpus-like "
          f"site counts): fired {fires}/8; mean obs={obs_sum/8:.1f} vs null {mu_sum/8:.1f}")
    print(f"  [note] the test detects SHARP anchoring (few positions, high contrast) and "
          f"misses DIFFUSE anchoring at corpus site counts; a quiet corpus result is weak "
          f"evidence against diffuse structure, per prereg wording")

    # P3 progressive content structure: spike fires, co-location does NOT
    msgs, trips, spans = plant_corpus(fresh("p3"), "prog_delta")
    s4 = spectrum_z(msgs, D4, fresh("p3s"), iters=400)
    check("prog_delta: spike at d=4", s4["z"] >= PREREG["spike_z"], f"(x={s4['x']:.2f}, z={s4['z']:.1f})")
    w, x = triplet_pairs(trips)
    cw = clean_colocation(msgs, w, D4, fresh("p3c"), iters=400)
    check("prog_delta: co-location stays quiet (discriminator)",
          cw["p"] > 0.05, f"(obs={cw['obs']}, p={cw['p']:.3f})")

    # P4 template: spike fires unmasked, dies under true-span masking
    msgs, trips, spans = plant_corpus(fresh("p4"), "template")
    s4 = spectrum_z(msgs, D4, fresh("p4s"), iters=400)
    check("template: spike at d=4 unmasked", s4["z"] >= PREREG["spike_z"],
          f"(x={s4['x']:.2f}, z={s4['z']:.1f})")
    s4m = spectrum_z(msgs, D4, fresh("p4sm"), mask=spans, iters=400)
    check("template: masked spectrum flat", s4m["z"] < PREREG["masked_template_z"],
          f"(masked z={s4m['z']:.1f})")

    # P5 exact period-4 K: multiples signature
    msgs, trips, spans = plant_corpus(fresh("p5"), "k_period4")
    s4 = spectrum_z(msgs, D4, fresh("p5s"), iters=400)
    s8 = spectrum_z(msgs, 8, fresh("p5s8"), iters=400)
    check("k_period4: spikes at 4 AND 8", s4["z"] >= 3 and s8["z"] >= 3,
          f"(z4={s4['z']:.1f}, z8={s8['z']:.1f})")

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")
    return ok

# ---------------------------------------------------------------- corpus run
def corpus_run(corpus_path, atlas_path):
    M = load_corpus(corpus_path)
    spans = atlas_spans(atlas_path, M)
    rng = random.Random(RNG_SEED + 1)
    print("\npre-registered thresholds:", json.dumps(PREREG))

    print("\nS1 spectrum (pooled, unigram-permutation z):")
    print(f"  {'d':>3s} {'hits':>5s} {'x':>6s} {'z':>7s}")
    table = {}
    for d in range(1, 25):
        r = spectrum_z(M, d, rng, iters=NULL_ITERS if d <= D_MAX else 400)
        table[d] = r
        print(f"  {d:3d} {r['hits']:5d} {r['x']:6.2f} {r['z']:7.2f}")

    print("\nS5 multiples: z(4)=%.2f z(8)=%.2f z(12)=%.2f -> %s" % (
        table[4]["z"], table[8]["z"], table[12]["z"],
        "exact period-4 K EXCLUDED" if (table[8]["z"] < PREREG["period_multiple_z"]
                                        and table[4]["z"] >= 4) else "inconclusive"))

    print("\nS2 template masking (atlas spans removed):")
    for d in (3, 4, 7, 9, 13, 17):
        r = spectrum_z(M, d, rng, mask=spans, iters=NULL_ITERS)
        tag = ""
        if d == D4:
            if r["z"] < PREREG["masked_template_z"]: tag = "-> TEMPLATE-ANCHORED"
            elif r["z"] >= PREREG["masked_corpuswide_z"]: tag = "-> CORPUS-WIDE"
            else: tag = "-> inconclusive band"
        print(f"  masked d={d:2d}: hits={r['hits']:3d} comps={r['comps']:4d} "
              f"x={r['x']:5.2f} z={r['z']:6.2f} {tag}")

    print("\nS3 clean co-location at d=4 (t>=8, glyphs differ):")
    w, x = triplet_pairs(TRIPLETS)
    cw = clean_colocation(M, w, D4, rng)
    cx = clean_colocation(M, x, D4, rng)
    for pp in cw["pairs"]:
        print(f"  within  {pp['pair']:22s} sites A={pp['nA']} B={pp['nB']} clean-coloc={pp['obs']}")
    print(f"  within-triplet pooled: obs={cw['obs']} null_mu={cw['null_mu']:.2f} p={cw['p']:.4f}")
    print(f"  cross-triplet pooled:  obs={cx['obs']} null_mu={cx['null_mu']:.2f} p={cx['p']:.4f}")
    if cw["p"] < PREREG["coloc_fire_p"] and cx["p"] > PREREG["coloc_control_p"]:
        print("  -> POSITION-LOCKED (K-anchored) structure detected")
    elif cw["p"] > 0.05:
        print("  -> no position-locking DETECTED (power-limited at corpus site "
              "counts; see selftest power note -- not proof of absence)")
    else:
        print("  -> gray zone per prereg")

    print("\nS4 near-dup detail (confounded = all four glyphs equal):")
    for a, b in [("East 1", "West 1"), ("West 2", "West 3"), ("East 4", "East 5")]:
        A, B = M[a], M[b]
        lo, hi = 8, min(len(A), len(B)) - D4 - 1
        SA = set(t for t in sites(A, D4) if lo <= t <= hi)
        SB = set(t for t in sites(B, D4) if lo <= t <= hi)
        both = sorted(SA & SB)
        conf = [t for t in both if A[t] == B[t]]
        clean = [t for t in both if A[t] != B[t]]
        print(f"  {a}/{b}: co-sites={both} confounded={conf} clean={clean}")

    print("\nsite census (message, t, inside-atlas-span):")
    for lab, ct in M.items():
        ss = sites(ct, D4)
        mk = spans[lab]
        anno = [f"{t}{'*' if (t in mk and t+4 in mk) else ''}" for t in ss]
        print(f"  {lab:8s} d4-sites: {anno}")

# ---------------------------------------------------------------- main
if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(here, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(here, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
