#!/usr/bin/env python3
"""
eyebridge2 -- discriminating FR14's two surviving branches by auditing the
cross-triplet bridges directly. Read-only.

THE SETUP. FR14 showed the opening/body contradiction is body-internal: the
literal body runs between East 4 and East 5 force those two messages to
share an offset, and the certified atlas cannot carry that at any
non-degenerate drift. It also showed that removing either cross-triplet
class -- #2- or #M- -- on its own restores a live system. Branch (ii) of the
trilemma therefore reduces to a concrete question about two objects.

THE RIGHT QUESTION. A cross-triplet class is not one homogeneous claim. Each
is a within-triplet CORE (several instances of a genuinely repeated passage)
plus a single BRIDGING instance in another triplet. Only the bridge asserts
that a passage recurs across triplets, and only the bridge is load-bearing
for the contradiction. So the null to compute is not "could this class arise
by chance" -- FR10 already answered that for long isomorphs generally -- but
"given the core is real, could the bridging window be a chance pattern
match?" That is a far weaker requirement, and it is cheap to price: a class
pattern with k skeleton equal-pairs matches a random window with probability
83^-k, and the search ranged over every window outside the core triplet.

TESTS.
  C1 bridge geometry: core/bridge split and evidence weight (k) per class.
  C2 surgical removal: drop ONLY the bridging instance, keep the core, and
     re-test the body-internal system.
  C3 targeted null: shuffle the bridge message (unigram-preserving) and count
     windows matching the class pattern, with corpus-wide calibration.
  C4 consequence for FR3's cross-triplet drift-equality deduction.
"""

import json, os, random, sys
from collections import Counter
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyerun", "eyeshape", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyeshape as ESH                     # noqa: E402
import eyegauge as EG                      # noqa: E402
import iso_relax as IR                     # noqa: E402
import isomorph as iso                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

TRIPLETS = EG.TRIPLETS
GIDX = {"T1": 0, "T2": 1, "T3": 2}
PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "shuffles": 2000, "seed": 20260726}

# ------------------------------------------------------------------ helpers
def skeleton(cls):
    L, pat = cls["length"], cls["pattern"]
    return L, [(i, j) for i in range(L) for j in range(i + 1, L)
               if pat[i] != '.' and pat[i] == pat[j]]

def matches(seq, L, sk):
    return sum(1 for p in range(len(seq) - L + 1)
               if all(seq[p + i] == seq[p + j] for i, j in sk))

def core_and_bridges(cls, tri):
    cnt = Counter(tri[it["message"]] for it in cls["instances"])
    core = cnt.most_common(1)[0][0]
    bridges = [(it["message"], it["start"]) for it in cls["instances"]
               if tri[it["message"]] != core]
    return core, bridges, dict(cnt)

def class_pairs(cls, Lx, cts, drop=None):
    L = cls["length"]
    inst = [(Lx[it["message"]], it["start"]) for it in cls["instances"]
            if drop is None or (it["message"], it["start"]) != drop]
    out = []
    for (m1, p1), (m2, p2) in combinations(inst, 2):
        out.append(iso.IsoPair(m1=m1, p1=p1, m2=m2, p2=p2, length=L,
                               exact=cts[m1][p1:p1 + L] == cts[m2][p2:p2 + L]))
    return out

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: pattern matching, null calibration, surgical removal")

    # pattern matcher exactness
    seq = [1, 5, 2, 9, 5, 7, 1, 3]
    check("matcher finds a planted skeleton",
          matches(seq, 7, [(0, 6), (1, 4)]) == 1)
    check("matcher rejects a skeleton that does not hold",
          matches(seq, 7, [(0, 1)]) == 0)

    # null calibration: weak skeletons match often, strong ones essentially never
    rng = random.Random(1)
    s = [rng.randrange(N) for _ in range(140)]
    weak = matches(s, 8, [(0, 7)])
    strong = matches(s, 25, [(0, 4), (10, 16), (20, 24), (2, 8), (5, 15)])
    check("null calibration: 1-pair skeleton matches often, 5-pair almost never",
          weak >= 1 and strong == 0, f"(weak={weak}, strong={strong})")

    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    c = json.load(open(corpus)); labels = c["message_labels"]
    cts = [list(x) for x in c["ciphertexts"]]
    Lx = {lab: i for i, lab in enumerate(labels)}
    a = json.load(open(atlas))

    # surgical removal removes exactly the bridge's pairs
    cls = next(x for x in a["classes"] if x["id"] == "#M-")
    full = class_pairs(cls, Lx, cts)
    trimmed = class_pairs(cls, Lx, cts, drop=("East 3", 101))
    n = len(cls["instances"])
    check("dropping one instance removes exactly (n-1) pairs",
          len(full) - len(trimmed) == n - 1, f"({len(full)} -> {len(trimmed)})")

    # corpus control: reproduce FR14's degenerate body-internal system
    trig = {Lx[m]: GIDX[t] for t, ms in TRIPLETS.items() for m in ms}
    ctx = EG.build_context(cts, labels, atlas)
    pool = ctx["apairs"] + ctx["strict"]
    merge = iso.IsoPair(m1=Lx["East 4"], p1=25, m2=Lx["East 5"], p2=25,
                        length=3, exact=True)
    if cts[Lx["East 4"]][25:28] != cts[Lx["East 5"]][25:28]:
        fail("E4/E5 body run @25 is not literal")
    st = ESH.analyse(cts, ctx, trig, pool + [merge], {})[0]
    check("corpus control: body-internal system is DEGENERATE (FR14)",
          st == "DEGENERATE", f"({st})")

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    c = json.load(open(corpus_path))
    cts = [list(x) for x in c["ciphertexts"]]; labels = c["message_labels"]
    M = dict(zip(labels, c["ciphertexts"])); Lx = {l: i for i, l in enumerate(labels)}
    tri = {m: t for t, ms in TRIPLETS.items() for m in ms}
    trig = {Lx[m]: GIDX[t] for m, t in tri.items()}
    a = json.load(open(atlas_path))

    r = IR.relax(cts, N, seed=0); bg = PREREG["baseline_guard"]
    if (r.linked_strict, r.distinct_strict, len(r.pins)) != \
       (bg["linked"], bg["distinct"], bg["pins"]):
        fail("baseline reproduction mismatch")
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    ctx = EG.build_context(cts, labels, atlas_path)
    pool = ctx["apairs"] + ctx["strict"]
    merge = iso.IsoPair(m1=Lx["East 4"], p1=25, m2=Lx["East 5"], p2=25,
                        length=3, exact=True)
    def live(pl): return ESH.analyse(cts, ctx, trig, pl, {})[0]

    xclasses = [cl for cl in a["classes"]
                if len({tri[it["message"]] for it in cl["instances"]}) > 1]
    print(f"\nC1 cross-triplet bridge geometry ({len(xclasses)} classes):")
    info = {}
    for cl in xclasses:
        L, sk = skeleton(cl)
        core, bridges, cnt = core_and_bridges(cl, tri)
        others = [m for m in labels if tri[m] != core]
        wins = sum(max(0, len(M[m]) - L + 1) for m in others)
        exp = wins * (83.0 ** -len(sk))
        info[cl["id"]] = dict(L=L, sk=sk, core=core, bridges=bridges, exp=exp)
        print(f"  {cl['id']:4s} L={L:3d} pattern={cl['pattern']}")
        print(f"       skeleton equal-pairs k={len(sk)}  chance/window=83^-{len(sk)}"
              f"={83.0**-len(sk):.2e}")
        print(f"       instances {cnt}, core={core}, bridge(s)={bridges}")
        print(f"       windows searched outside core={wins}; "
              f"EXPECTED chance matches={exp:.3f}")

    print("\nC2 surgical removal: drop ONLY the bridging instance")
    print(f"  full pool + E4/E5 merge: {live(pool + [merge])}")
    for cl in xclasses:
        cid = cl["id"]; br = info[cid]["bridges"][0]
        rest = [p for p in pool if p not in ctx["by_class"][cid]]
        trimmed = class_pairs(cl, Lx, cts, drop=br)
        print(f"  {cid:4s} bridge {br} removed (core kept): "
              f"{live(rest + trimmed + [merge])}")
        print(f"  {cid:4s} whole class removed            : {live(rest + [merge])}")

    print(f"\nC3 targeted null: is each bridge a chance pattern match?")
    rng = random.Random(PREREG["seed"])
    for cl in xclasses:
        cid = cl["id"]; L, sk = skeleton(cl)
        bmsg = info[cid]["bridges"][0][0]
        obs = matches(M[bmsg], L, sk)
        nulls = []
        for _ in range(PREREG["shuffles"]):
            s = list(M[bmsg]); rng.shuffle(s)
            nulls.append(matches(s, L, sk))
        ge = sum(1 for x in nulls if x >= obs)
        p1 = (ge + 1) / (PREREG["shuffles"] + 1)
        ncand = len([m for m in labels if tri[m] != info[cid]["core"]])
        print(f"  {cid:4s} bridge in {bmsg}: matching windows={obs}, "
              f"null mean={sum(nulls)/len(nulls):.3f}, p={p1:.4f}, "
              f"corrected for {ncand} candidate messages ~ {min(1.0, p1*ncand):.3f}")
        per = {m: matches(M[m], L, sk) for m in labels}
        print(f"       corpus-wide matches per message: {per}")

    print("\nC4 consequence for FR3's cross-triplet drift-equality deduction:")
    print("  FR3 derived drift(T1)=drift(T2) from #M- and drift(T2)=drift(T3) "
          "from #2-.")
    print("  Discarding a bridge removes exactly the link it supplied; the "
          "surviving\n  bridge keeps its own link. The two deductions stand or "
          "fall separately.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
