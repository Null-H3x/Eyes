#!/usr/bin/env python3
"""
eyeind -- the indicator block, and the first time two structural hypotheses
in this project constrain each other. Read-only.

WHY THIS WAS WORTH LOOKING AT. FR42 recorded the success criterion as
non-computational and the drift as reachable only by external anchors. One
structure had never been exploited: position 0 of each message carries a
distinct glyph, and under the model

    q[ind_m] = base_m + label_m + K_g[0]

so for two messages of one triplet whose indicators sit in a KNOWN component
and whose base difference is forced,

    label_m1 - label_m2 = drift * (Delta_1 - Delta_2 - w)

The label difference is drift times a computable quantity. A hypothesis about
the labels therefore becomes a prediction about the drift.

WHAT THE CORPUS SUPPLIES. Five of the nine indicators sit in the skeleton
(East 1, West 1, East 3, West 3, East 4), but only ONE pair is usable: East 3
and West 3 share component 1 and have a forced base difference. Every other
indicator pair is either outside the skeleton, in a different component, or
cross-triplet with no forced w. That single pair gives

    label(E3) - label(W3) = -drift.

THE CONSEQUENCE. If the nine labels are nine CONSECUTIVE values -- the natural
shape for an ordered set of messages -- every pairwise difference lies in
[-8, +8], so drift must be one of sixteen values. FR5's H1 requires drift 31,
which is not among them. The two hypotheses are INCOMPATIBLE: at most one can
hold. Neither is established, and the narrowing depends entirely on the
consecutive-label assumption, which is a hypothesis about the author's
encoding rather than a measurement. What is new is that the project's
structural hypotheses now constrain each other, which FR34 identified as the
missing ingredient for making the drift testable.
"""

import json, os, random, sys
from collections import Counter
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyenull", "eyedist", "eyevalid", "eyepool2", "eyeclass", "eyeloo",
          "eyeclust", "eyefree2", "eyebridge3", "eyewiden", "eyepair", "eyeseek",
          "eyefree", "eyebase", "eyealpha", "eyepack", "eyeskel", "eyerepair",
          "eyescore", "eyeinject", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyeloo as EL                        # noqa: E402
import eyerepair as ERP                    # noqa: E402
import eyeinject as EI                     # noqa: E402
import iso_relax as IR                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

TRIPLETS = {"T1": ["East 1", "West 1", "East 2"],
            "T2": ["West 2", "East 3", "West 3"],
            "T3": ["East 4", "West 4", "East 5"]}
PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "H1": (47, 1, 4), "label_span": 8}

def setup(S):
    Lx = S["Lx"]
    pool = ERP.drop(S["pool"], (Lx["East 3"], 101), (Lx["East 1"], 68))
    gf = EL.build(S, pool)
    D, C = EL.deltas(gf)
    W = {}
    for a, b in combinations(range(9), 2):
        h = [d for d in range(N)
             if gf.classify({N + b: 1, N + a: N - 1}, d) == "redundant"]
        if len(h) == 1: W[(a, b)] = h[0]; W[(b, a)] = (-h[0]) % N
    return gf, D, C, W

def usable_indicator_pairs(S, D, C, W):
    Lx, cts, labels = S["Lx"], S["cts"], S["labels"]
    tri = {m: t for t, ms in TRIPLETS.items() for m in ms}
    out = []
    for a, b in combinations(labels, 2):
        ga, gb = cts[Lx[a]][0], cts[Lx[b]][0]
        if ga not in C or gb not in C or C[ga] != C[gb]: continue
        ia, ib = Lx[a], Lx[b]
        if (ia, ib) not in W: continue
        out.append((a, b, (D[ga] - D[gb] - W[(ia, ib)]) % N))
    return out

def h1_drift(gf):
    a, b, want = PREREG["H1"]
    h = [d for d in range(N) if gf.classify({b: 1, a: N - 1}, d) == "redundant"]
    if len(h) != 1: return None, None
    return h[0], (want * pow(h[0], N - 2, N)) % N

def consecutive_label_drifts(k, span):
    """drifts d for which drift*k lies within +-span of zero (mod 83)"""
    out = []
    for d in range(1, N):
        v = (d * k) % N
        if v <= span or v >= N - span: out.append(d)
    return out

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: indicator algebra on a plant, membership, narrowing logic")

    # the algebra, on synthetic data where labels and drift are known
    rng = random.Random(6)
    C0 = list(range(N)); rng.shuffle(C0)
    q = [0] * N
    for i, s in enumerate(C0): q[s] = i
    drift, b1, b2, kap = 23, 9, 44, 5
    lab1, lab2 = 3, 5
    ind1 = C0[(lab1 + b1 + kap) % N]
    ind2 = C0[(lab2 + b2 + kap) % N]
    dinv = pow(drift, N - 2, N)
    Dl = {g: (q[g] * dinv) % N for g in range(N)}
    w = ((b2 - b1) * dinv) % N          # base[m2]-base[m1] = drift*w
    k = (Dl[ind1] - Dl[ind2] + w) % N
    check("indicator algebra recovers the label difference",
          (drift * k) % N == (lab1 - lab2) % N,
          f"(drift*k = {(drift*k)%N}, true diff = {(lab1-lab2)%N})")

    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    S = EI.setup(corpus, atlas)
    gf, D, C, W = setup(S)

    inds = [S["cts"][S["Lx"][m]][0] for m in S["labels"]]
    check("the nine indicators are distinct", len(set(inds)) == 9)

    up = usable_indicator_pairs(S, D, C, W)
    check("exactly one indicator pair is usable", len(up) == 1, f"({up})")

    coef, d1 = h1_drift(gf)
    check("H1 is expressible and selects one drift",
          coef is not None and d1 is not None, f"(coefficient {coef}, drift {d1})")

    allowed = consecutive_label_drifts(up[0][2], PREREG["label_span"])
    check("the consecutive-label hypothesis narrows the drift",
          0 < len(allowed) < N // 3, f"({len(allowed)} of 82)")
    check("and it excludes H1's drift (the hypotheses conflict)",
          d1 not in allowed, f"(H1 drift {d1})")

    c = json.load(open(corpus))
    cts = [list(x) for x in c["ciphertexts"]]
    r = IR.relax(cts, N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard", (r.linked_strict, r.distinct_strict, len(r.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    S = EI.setup(corpus_path, atlas_path)
    Lx, cts, labels = S["Lx"], S["cts"], S["labels"]
    gf, D, C, W = setup(S)
    tri = {m: t for t, ms in TRIPLETS.items() for m in ms}
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    print("\nI1 the indicator block against the 56-glyph skeleton")
    print(f"  {'message':9s} {'triplet':8s} {'glyph':>5s} {'component':>10s} "
          f"{'Delta':>6s}")
    for m in labels:
        g = cts[Lx[m]][0]
        print(f"  {m:9s} {tri[m]:8s} {g:5d} "
              f"{('C'+str(C[g]+1)) if g in C else '-':>10s} "
              f"{str(D[g]) if g in D else '-':>6s}")
    inC = [m for m in labels if cts[Lx[m]][0] in C]
    print(f"  indicators inside the skeleton: {len(inC)} -> {inC}")

    print("\nI2 usable pairs")
    up = usable_indicator_pairs(S, D, C, W)
    for a, b, k in up:
        print(f"  {a}/{b}: label difference = drift * {k}"
              f"  (= -drift)" if k == N - 1 else "")
    print(f"  only {len(up)} of 36 indicator pairs is usable: the rest are")
    print( "  outside the skeleton, in different components, or cross-triplet")
    print( "  with no forced base difference")

    print("\nI3 the two hypotheses")
    coef, d1 = h1_drift(gf)
    print(f"  H1 (FR5 boundary token): q[1]-q[47] = {coef}*drift, so drift = {d1}")
    k = up[0][2]
    allowed = consecutive_label_drifts(k, PREREG["label_span"])
    print(f"  H4 (indicator labels consecutive): |drift*{k}| <= "
          f"{PREREG['label_span']} gives drift in")
    print(f"     {allowed}")
    print(f"     {len(allowed)} of 82 values, a {82/len(allowed):.1f}x narrowing")
    print(f"\n  H1's drift {d1} is "
          f"{'in' if d1 in allowed else 'NOT in'} H4's admissible set")
    print(f"  -> the two hypotheses are "
          f"{'compatible' if d1 in allowed else 'INCOMPATIBLE: at most one holds'}")

    print("\nI4 how much this is worth")
    print("  NEITHER hypothesis is established. H1 has been unfalsifiable since")
    print("  FR33 because its coefficient is invertible; H4's narrowing rests")
    print("  entirely on the labels being consecutive, which is a guess about")
    print("  the author's encoding rather than a measurement.")
    print("  What IS new is that they now constrain each other. FR34 identified")
    print("  a second independent drift prediction as the missing ingredient")
    print("  for making the drift testable from inside the corpus; this is one,")
    print("  and it disagrees with the first. At most one of the two structural")
    print("  readings the project carries can be correct.")
    print("\n  If the labels are merely DISTINCT rather than consecutive, H4")
    print("  says nothing and the conflict evaporates. That is the assumption")
    print("  to attack next.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
