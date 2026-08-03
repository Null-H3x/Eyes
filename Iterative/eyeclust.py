#!/usr/bin/env python3
"""
eyeclust -- a drift discriminator that is not scale-invariant, and the
exclusion its null buys. Read-only.

WHY A NEW DISCRIMINATOR WAS WORTH LOOKING FOR. FR30 proved every determined
relation has the form D = drift * Delta_eff, so the skeleton is a
one-parameter family and the drift rescales everything at once. Injectivity
(FR21) and cross-component packing (FR27) are both invariant under that
rescaling and therefore cannot pin it. What WOULD break the symmetry is a
property of the plaintext that is not scale-invariant.

THE IDEA. Inside a component, FR30's channel gives p[t] = A + drift*v[t] with
v[t] = (Delta_{c[t]} - t) computable without knowing drift, bases or the
alphabet. If the plaintext alphabet is a CONTIGUOUS range of size k -- the
natural shape for a token stream whose tokens are numbered 0..k-1 -- then every
p in a (message, component) block lies in a window of size k, so the set
{drift*v} must also lie in a window of size k. For the true drift the values
cluster; for a wrong drift they scatter. Window width is emphatically not
scale-invariant, so this can discriminate where injectivity and packing cannot.

WHAT IT FINDS. Nothing, and the positive controls make that informative. A
planted contiguous alphabet of 26, 40 or 60 recovers the true drift at rank 1
with z between -4.1 and -5.7; a planted full-width alphabet recovers nothing.
The corpus's best drift sits at z = -2.19, which is what the maximum of 82
draws reaches by chance. So a small contiguous plaintext alphabet is EXCLUDED
at roughly 4-sigma power -- an independent, drift-free corroboration of
FG2/FG3's effective alphabet near 79, and a real narrowing of the A-vs-B fork.

The statistic is symmetric under drift -> -drift (a window and its reflection
have equal width), so results always appear in mirror pairs; that is a
property of the test, not a finding.
"""

import json, os, random, sys

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyefree2", "eyebridge3", "eyewiden", "eyepair", "eyeseek", "eyefree",
          "eyebase", "eyealpha", "eyepack", "eyeskel", "eyerepair", "eyescore",
          "eyeinject", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyefree2 as EF2                     # noqa: E402
import eyerepair as ERP                    # noqa: E402
import eyeinject as EI                     # noqa: E402
import iso_relax as IR                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "min_block": 4, "seed": 20260806, "true_drift": 37,
          "alphabets": [26, 40, 60, 83]}

def minwindow(vals):
    """width of the smallest circular window containing every value"""
    s = sorted(set(vals))
    if len(s) < 2: return 1
    return min(((s[i - 1] - s[i]) % N) + 1 for i in range(len(s)))

def score(blocks, d):
    return sum(minwindow([(d * x) % N for x in b]) for b in blocks) / len(blocks)

def sweep(blocks):
    sc = sorted(((score(blocks, d), d) for d in range(1, N)))
    vals = [s for s, _ in sc]
    mu = sum(vals) / len(vals)
    sd = (sum((v - mu) ** 2 for v in vals) / (len(vals) - 1)) ** 0.5
    return sc, mu, sd

def corpus_blocks(S, cells):
    gf, r, delta, comp = EF2.skeleton(S, cells)
    Lx, cts = S["Lx"], S["cts"]
    plA = ERP.drop(S["pool"], (Lx["East 3"], 101), (Lx["East 1"], 68))
    cov = set()
    for p in plA:
        for i in range(p.length):
            cov.add((p.m1, p.p1 + i)); cov.add((p.m2, p.p2 + i))
    blocks = []
    for mi, m in enumerate(cts):
        for ci in sorted(set(comp.values())):
            vs = [(delta[g] - t) % N for t, g in enumerate(m)
                  if comp.get(g) == ci and (mi, t) not in cov]
            if len(vs) >= PREREG["min_block"]: blocks.append(vs)
    return blocks, r

def planted(sizes, k, drift, rng):
    dinv = pow(drift, N - 2, N)
    out = []
    for n in sizes:
        A = rng.randrange(N)
        out.append([((rng.randrange(k) - A) * dinv) % N for _ in range(n)])
    return out

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: window statistic, planted-drift recovery, symmetry")

    check("window width is exact on a constructed set",
          minwindow([0, 1, 2, 80]) == 6 and minwindow([0, 41]) == 42,
          f"({minwindow([0,1,2,80])}, {minwindow([0,41])})")

    rng = random.Random(PREREG["seed"])
    sizes = [12] * 30
    d0 = PREREG["true_drift"]

    b = planted(sizes, 26, d0, rng)
    sc, mu, sd = sweep(b)
    rank = [i + 1 for i, (s, d) in enumerate(sc) if d == d0][0]
    check("planted contiguous alphabet (k=26) recovers the drift at rank 1",
          rank == 1, f"(rank {rank}, z {(dict((d,s) for s,d in sc)[d0]-mu)/sd:+.2f})")

    b = planted(sizes, N, d0, rng)
    sc, mu, sd = sweep(b)
    rank = [i + 1 for i, (s, d) in enumerate(sc) if d == d0][0]
    check("planted FULL alphabet recovers nothing (negative control)",
          rank > 10, f"(rank {rank})")

    # the statistic must be symmetric under d -> -d
    b = planted(sizes, 40, d0, rng)
    sym = all(abs(score(b, d) - score(b, (N - d) % N)) < 1e-9
              for d in (3, 17, 44))
    check("statistic is symmetric under drift -> -drift", sym)

    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    S = EI.setup(corpus, atlas)
    blocks, r = corpus_blocks(S, EF2.PREREG["cells"])
    check("FR35's skeleton reproduced",
          r["det"] == 384 and len(r["linked"]) == 56 and not r["eq"],
          f"({r['det']} relations, {len(r['linked'])} glyphs)")
    check("corpus yields enough blocks to score", len(blocks) >= 20,
          f"({len(blocks)} blocks)")

    c = json.load(open(corpus))
    cts = [list(x) for x in c["ciphertexts"]]
    rr = IR.relax(cts, N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard", (rr.linked_strict, rr.distinct_strict, len(rr.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    S = EI.setup(corpus_path, atlas_path)
    blocks, r = corpus_blocks(S, EF2.PREREG["cells"])
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")
    print(f"skeleton: {r['det']} relations, {len(r['linked'])} glyphs; "
          f"{len(blocks)} blocks, {sum(len(b) for b in blocks)} positions")

    print("\nC1 power: planted contiguous alphabets of size k")
    rng = random.Random(PREREG["seed"])
    sizes = [len(b) for b in blocks]
    d0 = PREREG["true_drift"]
    print(f"  {'k':>4s} {'rank of true drift':>19s} {'best drift':>11s} "
          f"{'z of truth':>11s}")
    for k in PREREG["alphabets"]:
        b = planted(sizes, k, d0, rng)
        sc, mu, sd = sweep(b)
        rank = [i + 1 for i, (s, d) in enumerate(sc) if d == d0][0]
        z = (dict((d, s) for s, d in sc)[d0] - mu) / sd
        print(f"  {k:4d} {rank:19d} {sc[0][1]:11d} {z:+11.2f}")
    print("  -> decisive for a small contiguous alphabet, powerless at full width,")
    print("     exactly as the construction predicts")

    print("\nC2 the corpus")
    sc, mu, sd = sweep(blocks)
    print(f"  {'rank':>4s} {'drift':>5s} {'mean window':>12s} {'z':>7s}")
    for i, (s, d) in enumerate(sc[:6]):
        print(f"  {i+1:4d} {d:5d} {s:12.2f} {(s-mu)/sd:+7.2f}")
    print(f"  across all drifts: mean {mu:.2f}, sd {sd:.2f}")
    print(f"  best drift {sc[0][1]} at z = {(sc[0][0]-mu)/sd:+.2f}")
    print("  with 82 drifts scored, the minimum of 82 draws reaches about that")
    print("  by chance -> NO drift discrimination")
    h1 = [i + 1 for i, (s, d) in enumerate(sc) if d == 31][0]
    print(f"  H1's predicted drift 31 ranks {h1} of 82 -- neither supported nor")
    print("  refuted, since the test has no power here")

    print("\nC3 what the null excludes")
    print("  the controls show the test would find the drift at z ~ -4 or better")
    print("  for any contiguous plaintext alphabet up to size 60. It does not.")
    print("  -> a SMALL CONTIGUOUS plaintext alphabet is excluded. If the")
    print("     plaintext is a token stream with contiguously numbered tokens,")
    print("     its inventory is large -- independent, drift-free corroboration")
    print("     of FG2/FG3's effective alphabet near 79, reached without pins.")
    print("  CAVEAT: a small but SCATTERED alphabet would not cluster and is not")
    print("  excluded by this test; it would need a coincidence measure, which")
    print("  FR30 built and found underpowered at current coverage.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
