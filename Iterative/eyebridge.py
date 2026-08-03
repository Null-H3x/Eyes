#!/usr/bin/env python3
"""
eyebridge -- position-resolved depth cartography, the pre-registered
full-template mask, and the cross-triplet bridge ledger for the Noita eye
corpus. Read-only; no isomorph is modified, filtered, or weighted.

THREE JOBS.

1. CARTOGRAPHY. The roadmap's depth tree is quantified to branch level;
   this instrument resolves it to positions: for all 36 message pairs, the
   literal-agreement map, the head run (maximal agreement run anchored at
   t=1), and a corpus-wide scan for INTERNAL literal runs (length >= 3,
   not anchored at the head). Null pricing: an internal run of length L
   at a given start has probability ~(1/83)^L if the pair is unrelated
   there; corpus-wide trials ~3600, so E[runs >= 3] ~ 0.006 -- any
   internal run >= 3 is a certified bridge event.

2. FULL-TEMPLATE MASK (pre-registered in FR2 S8). The atlas mask covers
   certified body isomorphs but not the literal opening repeats; FR2's
   masked residuals (d=9 z=2.52; the t=6 trifold at d=4) decoded post-hoc
   as opening leakage. Registered prediction: masking atlas spans PLUS
   opening spans collapses every residual; any lag with full-masked
   z >= 3.0 is the first genuine corpus-wide spectral signal.
   Opening-span rule (fixed before the corpus run): for each message,
   the opening span is [0, e] where e is the largest position such that
   the message's head run (agreement anchored at t=1) with at least one
   other message reaches e.

3. BRIDGE LEDGER. Under the static family c_m[t] = C[(s*p_m[t] + base_m
   + K_g[t]) mod 83] the corpus already contains cross-triplet rigid
   structure:
   (a) literal cross-triplet head runs (shared opening template) certify
       K_gA - K_gB constant on the shared span (bases absorb), merging
       depth stacks across triplets on those positions;
   (b) cross-triplet isomorph classes (#2- spans T2->T3, #M- spans
       T2->T1) certify, at every pattern pair (j,j') of the class,
       equal K-increments across all occurrences -- and under the
       progressive family this forces drift equality across triplets.
   The ledger enumerates these constraints; a plant-validated checker
   verifies the derivation logic against planted general-K corpora,
   including a deliberately broken plant that must be flagged.

Pre-registration: PREREG below, frozen on the plant suite before any new
corpus statistic is computed. The FR2 masking bands are inherited.
"""

import json, math, os, random, sys

ERR = "XD-MBYG04K-URS3LF"
N = 83
NULL_ITERS = 2000
RNG_SEED = 20260723

PREREG = {
    "internal_run_min": 3,        # internal literal run >= 3 -> certified bridge
                                  #   (corpus-wide null E ~ 0.006)
    "head_run_novelty": 3,        # head runs count as template-sharing beyond the
                                  #   universal 2-position header from length 3 up
    "fullmask_collapse_z": 2.0,   # full-masked z < 2.0 -> residual collapsed
    "fullmask_signal_z": 3.0,     # full-masked z >= 3.0 -> corpus-wide signal flag
    "verdict_lags": [3, 4, 7, 9, 13, 17],
}

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

TRIPLETS = {"T1": ["East 1", "West 1", "East 2"],
            "T2": ["West 2", "East 3", "West 3"],
            "T3": ["East 4", "West 4", "East 5"]}

def load_corpus(path):
    c = json.load(open(path))
    return dict(zip(c["message_labels"], c["ciphertexts"]))

def load_atlas(atlas_path, corpus):
    a = json.load(open(atlas_path))
    spans = {lab: set() for lab in corpus}
    classes = []
    for cls in a["classes"]:
        L = cls["length"]
        pat = cls["pattern"]
        pairs = [(i, j) for i in range(L) for j in range(i + 1, L)
                 if pat[i] != '.' and pat[i] == pat[j]]
        inst = []
        for it in cls["instances"]:
            if corpus[it["message"]][it["start"]:it["start"] + L] != it["values"]:
                fail("atlas values do not match corpus")
            spans[it["message"]].update(range(it["start"], it["start"] + L))
            inst.append((it["message"], it["start"]))
        classes.append(dict(id=cls["id"], L=L, pairs=pairs, instances=inst))
    return spans, classes

# ------------------------------------------------------------- cartography
def agree_map(A, B):
    n = min(len(A), len(B))
    return [1 if A[t] == B[t] else 0 for t in range(n)]

def head_run(A, B):
    """maximal run of agreement anchored at t=1 (position 0 is the
    per-message indicator and is excluded by construction)."""
    n = min(len(A), len(B)); e = 0
    for t in range(1, n):
        if A[t] == B[t]: e = t
        else: break
    return e                                   # last agreeing position; 0 = none

def internal_runs(A, B, minlen):
    """literal agreement runs of length >= minlen NOT anchored at the
    head run (start > head_run end + 1)."""
    n = min(len(A), len(B)); e = head_run(A, B)
    out = []; t = e + 2                        # first start strictly past head run
    while t < n:
        if A[t] == B[t]:
            s = t
            while t < n and A[t] == B[t]: t += 1
            if t - s >= minlen: out.append((s, t - s))
        else:
            t += 1
    return out

def opening_spans(msgs):
    """rule fixed in module docstring: per-message mask [0, e_max]."""
    labs = list(msgs)
    ends = {lab: 0 for lab in labs}
    for i in range(len(labs)):
        for j in range(i + 1, len(labs)):
            e = head_run(msgs[labs[i]], msgs[labs[j]])
            ends[labs[i]] = max(ends[labs[i]], e)
            ends[labs[j]] = max(ends[labs[j]], e)
    return {lab: set(range(0, ends[lab] + 1)) for lab in labs}, ends

# ------------------------------------------------------------- spectrum
def sites(ct, d):
    return [t for t in range(len(ct) - d) if ct[t] == ct[t + d]]

def spectrum_z(msgs, d, rng, mask=None, iters=NULL_ITERS):
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

# ------------------------------------------------------------- bridge ledger
def tri_of(lab, triplets):
    for t, ms in triplets.items():
        if lab in ms: return t
    fail(f"unknown message {lab}")

def bridge_ledger(classes, triplets):
    """enumerate cross-triplet isomorph bridges: for each class whose
    instances span >= 2 triplets, every pattern pair (j,j') yields the
    constraint K_{g(A)}[aA+j'] - K_{g(A)}[aA+j] == K_{g(B)}[aB+j'] -
    K_{g(B)}[aB+j] for every instance pair (A,B). Returns the constraint
    inventory grouped by class."""
    out = []
    for cls in classes:
        tris = {tri_of(m, triplets) for m, _ in cls["instances"]}
        if len(tris) < 2: continue
        cons = []
        for pi in range(len(cls["instances"])):
            for pj in range(pi + 1, len(cls["instances"])):
                (mA, aA), (mB, aB) = cls["instances"][pi], cls["instances"][pj]
                gA, gB = tri_of(mA, triplets), tri_of(mB, triplets)
                if gA == gB: continue
                for (j, jp) in cls["pairs"]:
                    cons.append(dict(gA=gA, tA=(aA + j, aA + jp),
                                     gB=gB, tB=(aB + j, aB + jp)))
        out.append(dict(id=cls["id"], triplets=sorted(tris),
                        n_pattern_pairs=len(cls["pairs"]), constraints=cons))
    return out

def check_ledger_against_K(ledger, K):
    """plant checker: K maps triplet name -> keystream list. Verifies every
    enumerated increment-equality constraint numerically; returns list of
    violations."""
    bad = []
    for cls in ledger:
        for c in cls["constraints"]:
            dA = (K[c["gA"]][c["tA"][1]] - K[c["gA"]][c["tA"][0]]) % N
            dB = (K[c["gB"]][c["tB"][1]] - K[c["gB"]][c["tB"][0]]) % N
            if dA != dB: bad.append((cls["id"], c))
    return bad

def depth_pair_count(msgs, components, span_of):
    """P1 metric: number of unordered same-position message pairs (m,m',t)
    lying in one K-component under a common gauge, restricted to the
    positions where the component's gauge link is certified (span_of).
    components: list of sets of labels; span_of: dict component-index ->
    set of positions certified (None = all shared positions)."""
    total = 0
    for ci, comp in enumerate(components):
        comp = sorted(comp)
        for i in range(len(comp)):
            for j in range(i + 1, len(comp)):
                A, B = msgs[comp[i]], msgs[comp[j]]
                n = min(len(A), len(B))
                allowed = span_of.get(ci)
                for t in range(1, n):
                    if allowed is None or t in allowed:
                        total += 1
    return total

# ------------------------------------------------------------- plants
def plant_cart(rng):
    """9 messages with engineered head structure and one internal run:
    all share positions 1-2; six share 3-5; four share 6-7; two share a
    body run of length 4 at t=50. Everything else independent uniform."""
    L = 100
    msgs = {f"m{i}": [rng.randrange(N) for _ in range(L)] for i in range(1, 10)}
    hdr = [rng.randrange(N) for _ in range(2)]
    mid = [rng.randrange(N) for _ in range(3)]
    sub = [rng.randrange(N) for _ in range(2)]
    body = [rng.randrange(N) for _ in range(4)]
    for i in range(1, 10):
        msgs[f"m{i}"][1:3] = hdr
    for i in range(4, 10):
        msgs[f"m{i}"][3:6] = mid
    for i in range(6, 10):
        msgs[f"m{i}"][6:8] = sub
    for i in (4, 7):
        msgs[f"m{i}"][50:54] = body
    # guard: break any accidental extensions
    for i in range(1, 10):
        for i2 in range(i + 1, 10):
            A, B = msgs[f"m{i}"], msgs[f"m{i2}"]
            for t in (8, 54):
                if A[t] == B[t]: B[t] = (B[t] + 1 + rng.randrange(N - 1)) % N
    return msgs

def plant_fullmask(rng):
    """progressive corpus where the ONLY d-structure is a shared opening
    template with an internal d=9 link and a repeated body passage with a
    d=4 link; atlas-mask alone leaves the opening residual, full mask
    collapses it."""
    L = 110; sigma = 1
    trips = {"T1": ["m1", "m2", "m3"], "T2": ["m4", "m5", "m6"],
             "T3": ["m7", "m8", "m9"]}
    syms = rng.sample(range(N), 20)
    def clean_opening():
        # only structure: two planted d=9 links; rejection-sample away any
        # accidental progressive-coincidence link at d in {3,4,7,9}
        while True:
            op = [rng.choice(syms) for _ in range(16)]
            op[13] = (op[4] - 9 * sigma) % N
            op[15] = (op[6] - 9 * sigma) % N
            op[11] = (op[2] - 9 * sigma) % N
            acc = 0
            for d in (3, 4, 7, 9):
                for j in range(16 - d):
                    if (op[j] - op[j + d]) % N == (d * sigma) % N:
                        acc += 1
            if acc == 3:                       # exactly the three planted d=9
                return op
    opening = clean_opening()
    passage = [rng.choice(syms) for _ in range(18)]
    passage[7] = (passage[3] - 4 * sigma) % N           # d=4 link at rel 3
    msgs = {}; atlas_mask = {}; open_truth = {}
    for tname, ms in trips.items():
        K = [t % N for t in range(L)]
        for lab in ms:
            base = rng.randrange(N)
            p = [rng.choice(syms) for _ in range(L)]
            p[1:17] = opening
            s0 = 40 + rng.randrange(3)                  # jittered occurrence
            p[s0:s0 + 18] = passage
            s1 = 75 + rng.randrange(3)
            p[s1:s1 + 18] = passage
            C = list(range(N)); rng.shuffle(C)
            msgs[lab] = [C[(sigma * p[t] + base + K[t]) % N] for t in range(L)]
            atlas_mask[lab] = set(range(s0, s0 + 18)) | set(range(s1, s1 + 18))
            open_truth[lab] = set(range(0, 17))
    return msgs, trips, atlas_mask, open_truth

def plant_bridge(rng, broken=False):
    """general-K corpus with a planted cross-triplet repeated passage:
    the same plaintext passage appears in T2 (one message) and T3 (two
    messages). K_2 and K_3 are arbitrary EXCEPT constructed so the
    passage occurrences produce skeleton-identical ciphertext (the
    increment-equality constraints hold by construction). If broken=True,
    one constrained K_3 increment is perturbed after construction, which
    must surface as a checker violation."""
    L = 120; sigma = 1
    trips = {"T2": ["mA"], "T3": ["mB", "mC"]}
    Lp = 12
    passage = rng.sample(range(N), Lp)                  # distinct plaintext values
    # pattern pairs to plant: (0,7),(2,5),(4,8) -- the motif geometry
    ppairs = [(0, 7), (2, 5), (4, 8)]
    K2 = [rng.randrange(N) for _ in range(L)]
    K3 = [rng.randrange(N) for _ in range(L)]
    a2, a3b, a3c = 30, 44, 71
    # force the increment equalities at pattern pairs across all occurrences,
    # and force the plaintext差 at those pairs to equal the K-increment so the
    # skeleton letter actually repeats (q equality at pattern pairs)
    for (j, jp) in ppairs:
        inc = (sigma * (passage[j] - passage[jp])) % N
        K2[a2 + jp] = (K2[a2 + j] + inc) % N
        K3[a3b + jp] = (K3[a3b + j] + inc) % N
        K3[a3c + jp] = (K3[a3c + j] + inc) % N
    if broken:
        K3[a3c + ppairs[0][1]] = (K3[a3c + ppairs[0][1]] + 1) % N
    Ks = {"T2": K2, "T3": K3}
    msgs = {}
    starts = {"mA": ("T2", a2), "mB": ("T3", a3b), "mC": ("T3", a3c)}
    for lab in ("mA", "mB", "mC"):
        g, s0 = starts[lab]
        base = rng.randrange(N)
        p = [rng.randrange(N) for _ in range(L)]
        p[s0:s0 + Lp] = passage
        C = list(range(N)); rng.shuffle(C)
        msgs[lab] = [C[(sigma * p[t] + base + Ks[g][t]) % N] for t in range(L)]
    classes = [dict(id="#X", L=Lp, pairs=ppairs,
                    instances=[("mA", a2), ("mB", a3b), ("mC", a3c)])]
    return msgs, trips, classes, Ks

# ------------------------------------------------------------- selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    def fresh(tag): return random.Random(f"{RNG_SEED}:{tag}")

    print("selftest: cartography, masks, and bridge derivation on plants")

    # 1. cartography exactness
    msgs = plant_cart(fresh("c1"))
    e12 = head_run(msgs["m1"], msgs["m2"])
    e45 = head_run(msgs["m4"], msgs["m5"])
    e67 = head_run(msgs["m6"], msgs["m7"])
    check("cart: head runs resolve the tree", (e12, e45, e67) == (2, 5, 7),
          f"(got {(e12, e45, e67)})")
    ir = internal_runs(msgs["m4"], msgs["m7"], PREREG["internal_run_min"])
    check("cart: planted internal run found", ir == [(50, 4)], f"(got {ir})")
    others = sum(len(internal_runs(msgs[a], msgs[b], PREREG["internal_run_min"]))
                 for a in msgs for b in msgs if a < b and {a, b} != {"m4", "m7"})
    check("cart: no false internal runs", others == 0, f"({others})")
    ospans, ends = opening_spans(msgs)
    check("cart: opening rule per message", ends["m1"] == 2 and ends["m4"] == 5
          and ends["m6"] == 7 and ends["m9"] == 7, f"(ends={ends})")

    # 2. null cartography: random messages -> no internal runs, head runs < 3
    rmsgs = {}
    for i in range(9):
        rr = fresh(f"n{i}")
        rmsgs[f"r{i}"] = [rr.randrange(N) for _ in range(110)]
    nruns = sum(len(internal_runs(rmsgs[a], rmsgs[b], 3))
                for a in rmsgs for b in rmsgs if a < b)
    nheads = max(head_run(rmsgs[a], rmsgs[b]) for a in rmsgs for b in rmsgs if a < b)
    check("null: no internal runs, no head templates", nruns == 0 and nheads < 3,
          f"(runs={nruns}, max head={nheads})")

    # 3. full-template mask: atlas-only leaves the opening residual, full
    #    mask collapses it; the body-passage d=4 dies under atlas mask alone
    msgs, trips, amask, otruth = plant_fullmask(fresh("f1"))
    s9_raw = spectrum_z(msgs, 9, fresh("f2"), iters=400)
    s9_atlas = spectrum_z(msgs, 9, fresh("f3"), mask=amask, iters=400)
    fullmask = {lab: amask[lab] | otruth[lab] for lab in msgs}
    s9_full = spectrum_z(msgs, 9, fresh("f4"), mask=fullmask, iters=400)
    check("fullmask: opening d=9 visible raw", s9_raw["z"] >= 3.0,
          f"(z={s9_raw['z']:.1f})")
    check("fullmask: atlas mask alone leaves d=9", s9_atlas["z"] >= 3.0,
          f"(z={s9_atlas['z']:.1f})")
    check("fullmask: full mask collapses d=9", s9_full["z"] < PREREG["fullmask_collapse_z"],
          f"(z={s9_full['z']:.1f})")
    s4_atlas = spectrum_z(msgs, 4, fresh("f5"), mask=amask, iters=400)
    check("fullmask: body-template d=4 dies under atlas mask", s4_atlas["z"] < 2.0,
          f"(z={s4_atlas['z']:.1f})")

    # 4. bridge derivation: constraints enumerated and verified on true K;
    #    broken plant flagged
    msgs, trips, classes, Ks = plant_bridge(fresh("b1"))
    led = bridge_ledger(classes, trips)
    ncons = sum(len(c["constraints"]) for c in led)
    check("bridge: cross-triplet constraints enumerated", ncons == 6,
          f"(got {ncons}; 3 pattern pairs x 2 cross-instance pairs)")
    bad = check_ledger_against_K(led, Ks)
    check("bridge: derivation holds on true K", len(bad) == 0, f"({len(bad)} violations)")
    msgs2, trips2, classes2, Ks2 = plant_bridge(fresh("b1"), broken=True)
    bad2 = check_ledger_against_K(bridge_ledger(classes2, trips2), Ks2)
    check("bridge: broken plant flagged", len(bad2) >= 1, f"({len(bad2)} violations)")

    # 5. depth-pair metric: merge arithmetic on a known construction
    comp_split = [{"mA"}, {"mB", "mC"}]
    comp_merged = [{"mA", "mB", "mC"}]
    span = set(range(1, 8))
    before = depth_pair_count(msgs, comp_split, {0: None, 1: span})
    after = depth_pair_count(msgs, comp_merged, {0: span})
    check("bridge: merged depth pairs = 3x span size", after == 3 * len(span)
          and before == len(span), f"(before={before}, after={after})")

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")
    return ok

# ------------------------------------------------------------- corpus run
def corpus_run(corpus_path, atlas_path):
    M = load_corpus(corpus_path)
    aspans, classes = load_atlas(atlas_path, M)
    rng = random.Random(RNG_SEED + 1)
    labs = list(M)
    print("\npre-registered thresholds:", json.dumps(PREREG))

    print("\n=== C1 cartography: head runs (last agreeing position; 0=none) ===")
    hr = {}
    for i in range(len(labs)):
        for j in range(i + 1, len(labs)):
            a, b = labs[i], labs[j]
            hr[(a, b)] = head_run(M[a], M[b])
    def tri(lab): return tri_of(lab, TRIPLETS)
    print("  within-triplet:")
    for (a, b), e in sorted(hr.items(), key=lambda kv: -kv[1]):
        if tri(a) == tri(b):
            print(f"    {a:8s}/{b:8s} head run 1..{e}" if e else
                  f"    {a:8s}/{b:8s} none")
    print("  cross-triplet (>2 = template beyond universal header):")
    for (a, b), e in sorted(hr.items(), key=lambda kv: -kv[1]):
        if tri(a) != tri(b) and e >= PREREG["head_run_novelty"]:
            print(f"    {a:8s}/{b:8s} head run 1..{e}   [{tri(a)}<->{tri(b)}]")
    xmax = max(e for (a, b), e in hr.items() if tri(a) != tri(b))
    print(f"  deepest cross-triplet head run: {xmax}")

    print("\n=== C2 internal literal runs >= "
          f"{PREREG['internal_run_min']} (certified bridge events) ===")
    found = 0
    for i in range(len(labs)):
        for j in range(i + 1, len(labs)):
            a, b = labs[i], labs[j]
            for (s, l) in internal_runs(M[a], M[b], PREREG["internal_run_min"]):
                found += 1
                print(f"    {a:8s}/{b:8s} run @{s} length {l}  "
                      f"[{tri(a)}{'=' if tri(a)==tri(b) else '<->'}{tri(b)}]")
    if not found: print("    none")

    print("\n=== C3 opening spans (mask rule) ===")
    ospans, ends = opening_spans(M)
    for lab in labs:
        print(f"    {lab:8s} opening [0..{ends[lab]}]")

    print("\n=== C4 full-template mask spectrum (atlas + opening spans) ===")
    fullmask = {lab: aspans[lab] | ospans[lab] for lab in labs}
    flagged = []
    for d in PREREG["verdict_lags"]:
        r = spectrum_z(M, d, rng, mask=fullmask, iters=NULL_ITERS)
        tag = ""
        if r["z"] >= PREREG["fullmask_signal_z"]:
            tag = "-> CORPUS-WIDE SIGNAL FLAG"; flagged.append(d)
        elif r["z"] < PREREG["fullmask_collapse_z"]:
            tag = "-> collapsed"
        else:
            tag = "-> inconclusive band"
        print(f"    full-masked d={d:2d}: hits={r['hits']:3d} comps={r['comps']:4d} "
              f"x={r['x']:5.2f} z={r['z']:6.2f} {tag}")
    print("    full-mask sweep d=1..24 (400-iter nulls), |z|>=2 only:")
    for d in range(1, 25):
        if d in PREREG["verdict_lags"]: continue
        r = spectrum_z(M, d, rng, mask=fullmask, iters=400)
        if abs(r["z"]) >= 2.0:
            print(f"      d={d:2d}: x={r['x']:5.2f} z={r['z']:6.2f}")

    print("\n=== C5 bridge ledger: cross-triplet isomorph constraints ===")
    led = bridge_ledger(classes, TRIPLETS)
    for cls in led:
        print(f"    {cls['id']:5s} spans {'+'.join(cls['triplets'])}: "
              f"{cls['n_pattern_pairs']} pattern pairs -> "
              f"{len(cls['constraints'])} cross-triplet increment equalities")
    print("    (under the progressive family each equality forces "
          "drift_gA = drift_gB; under general-K each is one rigid link)")

    print("\n=== C6 depth-stack merge (P1 metric) ===")
    xspan = set(range(1, xmax + 1))
    comps_before = [set(ms) for ms in TRIPLETS.values()]
    before = depth_pair_count(M, comps_before, {i: None for i in range(3)})
    merged = [set(TRIPLETS["T2"]) | set(TRIPLETS["T3"])]
    add = depth_pair_count(M, merged, {0: xspan}) - \
          depth_pair_count(M, [set(TRIPLETS["T2"])], {0: xspan}) - \
          depth_pair_count(M, [set(TRIPLETS["T3"])], {0: xspan})
    print(f"    within-triplet depth pairs (all shared positions): {before}")
    print(f"    cross-triplet depth pairs gained on certified span [1..{xmax}]: {add}")
    print(f"    (gauge: K_T2 - K_T3 constant on the span, bases absorbed; "
          f"conditional on shared opening template)")

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
