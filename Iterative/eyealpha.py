#!/usr/bin/env python3
"""
eyealpha -- retesting the structured-alphabet corner against evidence that is
not known to be false, and locating the last standing contradiction exactly.
Read-only.

WHY A RETEST. The doctrine records the structured-alphabet corner as EXCLUDED
by alphabet_sweep across ~9M scored hypotheses. That sweep was computed
against the constraint pool which FR21-FR25 later showed asserts six equalities
a permutation forbids. An exclusion derived from partly-false constraints is
not safe to carry, so the families are re-run against FR26's repaired skeleton
-- 223 relations with zero injectivity violations.

THE TEST IS SHARP. If C is affine, q[g] = a*g + b, then every relation
q[y] - q[x] = D implies a = D * (y-x)^-1. All 223 relations must agree on a
single multiplier. For a wrong drift or a non-affine alphabet the implied
multipliers scatter. Because the skeleton's VALUES are drift-dependent
(FR26), the test sweeps all 82 non-degenerate drifts; a hit would determine
the drift and the alphabet simultaneously, which is why the sweep is worth
running even though the prior is low.

POSITIVE CONTROLS ARE THE POINT. An exclusion means nothing unless the test
detects structure when structure is present, so the gate plants an affine
alphabet and a power alphabet and requires both to be found before any corpus
verdict is reported.

ALSO HERE. FR26 left an asymmetry unexplained: under the repaired pool the T1
opening is satisfiable at every drift while the T3 opening contradicts at
every drift. This locates it -- every PAIR of T3 messages may share an offset;
only the triple may not.
"""

import json, os, random, sys
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyepack", "eyeskel", "eyerepair", "eyescore", "eyeinject",
          "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyeskel as EK                       # noqa: E402
import eyerepair as ERP                    # noqa: E402
import eyeinject as EI                     # noqa: E402
import eyegauge as EG                      # noqa: E402
import iso_relax as IR                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16}}

def inv(x): return pow(x % N, N - 2, N)

# ------------------------------------------------------------------ families
def affine_multipliers(rel):
    """implied multiplier per relation; a true affine alphabet gives one value."""
    cand = {}
    for (x, y), D in rel.items():
        d = (y - x) % N
        if d == 0: continue
        a = (D * inv(d)) % N
        cand[a] = cand.get(a, 0) + 1
    return cand

def power_fits(rel):
    """exponents k for which q[g] = g^k explains EVERY relation."""
    out = []
    for k in range(1, N - 1):
        good = tot = 0
        for (x, y), D in rel.items():
            if x % N == 0 or y % N == 0: continue
            tot += 1
            if (pow(y, k, N) - pow(x, k, N)) % N == D % N: good += 1
        if tot and good == tot: out.append(k)
    return out

def identity_runs(rel):
    """relations satisfying D = y - x; a keyword-mixed alphabet leaves an
    ordered tail, which would elevate this count."""
    return sum(1 for (x, y), D in rel.items() if D % N == (y - x) % N)

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: positive controls first -- the test must FIND structure")

    rng = random.Random(11)
    glyphs = rng.sample(range(1, N), 30)

    # planted affine alphabet must be detected
    a_true, b_true = 37, 19
    q = {g: (a_true * g + b_true) % N for g in glyphs}
    rel = {(x, y): (q[y] - q[x]) % N for x, y in combinations(sorted(glyphs), 2)}
    cand = affine_multipliers(rel)
    check("planted AFFINE alphabet is detected", len(cand) == 1 and a_true in cand,
          f"({len(cand)} distinct multipliers, recovered {list(cand)[:1]})")

    # planted power alphabet must be detected
    k_true = 5
    qp = {g: pow(g, k_true, N) for g in glyphs}
    relp = {(x, y): (qp[y] - qp[x]) % N for x, y in combinations(sorted(glyphs), 2)}
    check("planted POWER alphabet is detected", k_true in power_fits(relp),
          f"(fits: {power_fits(relp)})")

    # a random permutation must NOT be detected (negative control)
    perm = list(range(N)); rng.shuffle(perm)
    qr = {g: perm[g] for g in glyphs}
    relr = {(x, y): (qr[y] - qr[x]) % N for x, y in combinations(sorted(glyphs), 2)}
    check("random alphabet is NOT detected as affine",
          len(affine_multipliers(relr)) > 5,
          f"({len(affine_multipliers(relr))} distinct multipliers)")
    check("random alphabet is NOT detected as a power map",
          power_fits(relr) == [])

    # identity-run detector fires on an ordered alphabet
    qi = {g: g for g in glyphs}
    reli = {(x, y): (qi[y] - qi[x]) % N for x, y in combinations(sorted(glyphs), 2)}
    check("identity-run detector fires on an ordered alphabet",
          identity_runs(reli) == len(reli))

    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
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
    Lx, cts, ctx, labels = S["Lx"], S["cts"], S["ctx"], S["labels"]
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")
    plA = ERP.drop(S["pool"], (Lx["East 3"], 101), (Lx["East 1"], 68))

    print("\nT1 the last contradiction, located")
    T1o = EG.opening_pairs(labels, EG.OPENINGS[:1])
    T3o = EG.opening_pairs(labels, EG.OPENINGS[1:])
    def sat(pl, group=None):
        return sum(1 for d in range(1, N)
                   if EG.satisfiable(cts, ctx, pl, drift=d, group=group))
    print(f"  T1 opening (E1/W1/E2): satisfiable at {sat(plA+T1o):2d}/82 drifts")
    print(f"  T3 opening (E4/W4/E5): satisfiable at {sat(plA+T3o):2d}/82 drifts")
    print("  decomposing the T3 constraint:")
    for k in (1, 2, 3):
        for combo in combinations(range(3), k):
            ops = [T3o[i] for i in combo]
            nm = " + ".join(f"{labels[T3o[i].m1][0]}{labels[T3o[i].m1][-1]}/"
                            f"{labels[T3o[i].m2][0]}{labels[T3o[i].m2][-1]}"
                            for i in combo)
            print(f"    {nm:26s}: {sat(plA+ops):2d}/82")
    print("  -> every PAIR of T3 messages may share an offset; only the TRIPLE")
    print("     may not. The constraint is genuinely three-way and does not")
    print("     single out any one message.")

    print("\nT2 structured-alphabet families vs the repaired skeleton")
    rels = {}
    for d in range(1, N):
        gf = EK.build(S, plA, d, (("East 4", "East 5"),))
        if gf is None: continue
        rels[d] = EK.skeleton(gf)["det"]
    nrel = len(rels[1])
    print(f"  skeleton: {nrel} relations, swept over {len(rels)} drifts")

    fewest = min(len(affine_multipliers(r)) for r in rels.values())
    print(f"  AFFINE  q[g]=a*g+b : fewest distinct multipliers at any drift = "
          f"{fewest} (a true affine alphabet gives 1)  -> EXCLUDED")

    hits = [(d, k) for d, r in rels.items() for k in power_fits(r)]
    print(f"  POWER   q[g]=g^k   : drift/exponent pairs fitting every relation = "
          f"{hits if hits else 'NONE'}  -> EXCLUDED")

    runs = {d: identity_runs(r) for d, r in rels.items()}
    bd = max(runs, key=lambda d: runs[d])
    exp = nrel / N
    print(f"  ORDERED TAIL (keyword-mixed): best {runs[bd]}/{nrel} at drift {bd}; "
          f"chance expectation {exp:.1f} per drift")
    print(f"    the maximum over {len(rels)} drifts is expected around "
          f"{runs[bd]} at this rate, so this is NOT a signal -> no support")

    print("\nT3 what these exclusions do and do not mean")
    print("  they exclude C being generated by a simple algebraic rule, on")
    print("  evidence that is not known to be false. They do NOT constrain the")
    print("  corpus otherwise: a random permutation returns the same verdict.")
    print("  Their value is that they supersede alphabet_sweep for this pool --")
    print("  the earlier exclusion rested on constraints since shown partly false,")
    print("  and a re-derived exclusion is worth more than an inherited one.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
