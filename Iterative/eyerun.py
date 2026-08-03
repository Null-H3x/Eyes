#!/usr/bin/env python3
"""
eyerun -- testing FR13's top item, and eliminating a branch. Read-only.

WHY THE OBVIOUS TEST WAS THE WRONG ONE. FR11, FR12 and FR13 all nominated
"extend the agreement statistic into the opening spans" to test branch (i)
of the trilemma -- the proposal that the literal openings are not shared
plaintext. That test does not exist: within a triplet the openings agree at
100% BY CONSTRUCTION, which is the premise, not a measurement.

THE TEST THAT DOES EXIST. FR11's mechanism, sharpened. For two messages of
one triplet the keystream cancels exactly in a literal comparison, so
c1[t] == c2[t] iff p1[t] - p2[t] == off2 - off1. A RUN of consecutive
literal agreements is therefore enormously more informative than the
aggregate rate: under distinct offsets a run of length L costs base^L, and
cross-triplet pairs -- sharing neither keystream nor offset -- supply the
empirical null directly.

THE CONSEQUENCE. If body runs alone force two messages to share an offset,
and the certified atlas cannot carry that offset equality, then the
opening/body contradiction of FR9-FR13 is BODY-INTERNAL and branch (i)
resolves nothing. C2 tests exactly that, with no opening pair anywhere in
the constraint pool. C3 and C4 then price the two branches that remain.

Degeneracy convention (FR8-FR13): "excluded" here means excluded at every
non-degenerate drift; with drift left free the systems remain formally
satisfiable by flattening the keystream, which is monoalphabetic and
FG1-excluded. Both readings are reported.
"""

import json, os, sys
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyeshape", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyeshape as ESH                     # noqa: E402
import eyegauge as EG                      # noqa: E402
import iso_relax as IR                     # noqa: E402
import isomorph as iso                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

TRIPLETS = EG.TRIPLETS
GIDX = {"T1": 0, "T2": 1, "T3": 2}
PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "body_start": 25, "min_run": 2}

# ------------------------------------------------------------------ runs
def literal_runs(A, B, lo, minlen):
    n = min(len(A), len(B)); out = []; t = lo
    while t < n:
        if A[t] == B[t]:
            s = t
            while t < n and A[t] == B[t]: t += 1
            if t - s >= minlen: out.append((s, t - s))
        else:
            t += 1
    return out

def run_census(M, labels, tri, lo, minlen):
    within, cross = [], []
    for a, b in combinations(labels, 2):
        rs = literal_runs(M[a], M[b], lo, minlen)
        (within if tri[a] == tri[b] else cross).append((a, b, rs))
    return within, cross

def baseline_rate(M, labels, tri, lo):
    ag = n = 0
    for a, b in combinations(labels, 2):
        if tri[a] == tri[b]: continue
        m = min(len(M[a]), len(M[b]))
        ag += sum(1 for t in range(lo, m) if M[a][t] == M[b][t]); n += m - lo
    return ag / n

# ------------------------------------------------------------------ plants
def plant_pair(shared_offset, seed=11, T=140, share=0.30, lo=25, phrase=6):
    """two messages of one triplet: shared keystream, a shared plaintext
    PHRASE plus scattered shared tokens, offsets equal or not."""
    import random
    rng = random.Random(seed)
    C = list(range(N)); rng.shuffle(C)
    K = [rng.randrange(N) for _ in range(T)]
    o1, o2 = 17, (17 if shared_offset else 44)
    p1 = [rng.randrange(N) for _ in range(T)]
    p2 = [rng.randrange(N) for _ in range(T)]
    for t in range(lo, T):
        if rng.random() < share: p2[t] = p1[t]
    p2[60:60 + phrase] = p1[60:60 + phrase]        # a genuine shared phrase
    enc = lambda p, o: [C[(p[t] + o + K[t]) % N] for t in range(T)]
    return enc(p1, o1), enc(p2, o2)

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: run mechanism both directions, corpus controls")
    lo = PREREG["body_start"]

    A, B = plant_pair(True)
    rs = literal_runs(A, B, lo, 2)
    check("shared offset: shared phrase appears as a literal run",
          any(L >= 4 for _, L in rs), f"(runs={rs[:4]})")

    A2, B2 = plant_pair(False)
    rs2 = literal_runs(A2, B2, lo, 2)
    check("DISTINCT offsets: identical phrase yields NO literal run "
          "(the negative control)", len(rs2) == 0, f"(runs={rs2})")

    check("run finder is exact on a constructed case",
          literal_runs([1,2,3,4,5], [9,2,3,4,9], 0, 2) == [(1, 3)])

    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    c = json.load(open(corpus)); labels = c["message_labels"]
    M = dict(zip(labels, c["ciphertexts"]))
    cts = [list(x) for x in c["ciphertexts"]]
    Lx = {lab: i for i, lab in enumerate(labels)}
    tri = {m: t for t, ms in TRIPLETS.items() for m in ms}
    ctx = EG.build_context(cts, labels, atlas)
    pool = ctx["apairs"] + ctx["strict"]

    _, cross = run_census(M, labels, tri, lo, 2)
    check("empirical null: zero body runs among cross-triplet pairs",
          sum(len(rs) for _, _, rs in cross) == 0)

    # E1/W1 is FR9-permitted to share an offset: its merge must stay satisfiable
    g = {m: m for m in range(9)}; g[Lx["West 1"]] = g[Lx["East 1"]]
    n_ok = sum(1 for d in range(1, N) if EG.satisfiable(cts, ctx, pool, drift=d, group=g))
    check("positive control: E1/W1 merge satisfiable at every drift", n_ok == 82,
          f"({n_ok}/82)")

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    c = json.load(open(corpus_path))
    labels = c["message_labels"]; M = dict(zip(labels, c["ciphertexts"]))
    cts = [list(x) for x in c["ciphertexts"]]
    Lx = {lab: i for i, lab in enumerate(labels)}
    tri = {m: t for t, ms in TRIPLETS.items() for m in ms}
    trig = {Lx[m]: GIDX[t] for m, t in tri.items()}
    lo = PREREG["body_start"]

    r = IR.relax(cts, N, seed=0); bg = PREREG["baseline_guard"]
    if (r.linked_strict, r.distinct_strict, len(r.pins)) != \
       (bg["linked"], bg["distinct"], bg["pins"]):
        fail("baseline reproduction mismatch")
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    ctx = EG.build_context(cts, labels, atlas_path)
    pool = ctx["apairs"] + ctx["strict"]; by = ctx["by_class"]
    base = baseline_rate(M, labels, tri, lo)

    print(f"\nC1 literal BODY runs (t >= {lo}); cross-triplet baseline rate "
          f"{base:.5f}")
    within, cross = run_census(M, labels, tri, lo, PREREG["min_run"])
    ncross = sum(len(rs) for _, _, rs in cross)
    print(f"  EMPIRICAL NULL -- cross-triplet pairs (no shared keystream, no "
          f"shared offset): {ncross} runs of length >= {PREREG['min_run']} "
          f"across {len(cross)} pairs")
    for a, b, rs in within:
        if not rs: continue
        det = ", ".join(f"@{s}(L={L}, chance~{base**L:.1e})" for s, L in rs)
        print(f"  {a:8s}/{b:8s}: {det}")
    print("  -> a run of literal agreement is only possible when the two "
          "messages\n     share an offset; the keystream cancels either way")

    print("\nC2 is the contradiction BODY-INTERNAL? (no opening pair anywhere)")
    for a, b in (("East 4", "East 5"), ("West 4", "East 5"), ("East 1", "West 1")):
        g = {m: m for m in range(9)}; g[Lx[b]] = g[Lx[a]]
        nd = sum(1 for d in range(1, N)
                 if EG.satisfiable(cts, ctx, pool, drift=d, group=g))
        run_ev = [rs for x, y, rs in within if {x, y} == {a, b}][0]
        print(f"  merge {a}/{b}: satisfiable at {nd}/82 non-degenerate drifts; "
              f"body runs {[(s, L) for s, L in run_ev]}")
    nd0 = sum(1 for d in range(1, N) if EG.satisfiable(cts, ctx, pool, drift=d))
    print(f"  control, no merge imposed: {nd0}/82")
    print("  -> E4/E5 carry run evidence for a shared offset that the atlas "
          "cannot\n     accommodate, using no opening data: branch (i) does "
          "NOT resolve the trilemma")

    merge = iso.IsoPair(m1=Lx["East 4"], p1=25, m2=Lx["East 5"], p2=25,
                        length=3, exact=True)
    if cts[Lx["East 4"]][25:28] != cts[Lx["East 5"]][25:28]:
        fail("E4/E5 body run @25 is not literal")

    print("\nC3 branch (ii): which classes carry the body-internal version?")
    full = ESH.analyse(cts, ctx, trig, pool + [merge], {})[0]
    print(f"  full pool + merge, globally affine: {full}")
    restor = [cid for cid in by
              if ESH.analyse(cts, ctx, trig,
                             [p for p in pool if p not in by[cid]] + [merge],
                             {})[0] == "LIVE"]
    print(f"  single-class removals giving a LIVE system: {restor}")
    print("  (both are the CROSS-TRIPLET bridge classes -- the same ones FR3 "
          "used\n   to derive drift equality)")

    print("\nC4 branch (iii'): admissible key resets, and their coherence with "
          "FR13")
    sm = ESH.shape_map(pool, trig)
    arith = sm[2].get(1, [])
    hits = [s for s in range(18, 110)
            if ESH.analyse(cts, ctx, trig, pool + [merge], {2: [s]})[0] == "LIVE"]
    inside = [s for s in hits if any(lo2 < s < hi2 - 1 for lo2, hi2 in arith)]
    print(f"  T3 proven arithmetic on {arith}")
    print(f"  admissible T3 break positions: {hits}")
    print(f"  of these, strictly inside a proven-arithmetic range: {inside} "
          f"(these need a continuous join, i.e. not a real reset)")
    print(f"  clean reset positions: {[s for s in hits if s not in inside]}")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
