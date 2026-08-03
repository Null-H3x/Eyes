#!/usr/bin/env python3
"""
eyegauge -- how many gauges does this corpus need? The gauge ladder, the
base-equality matrix, and the opening/body contradiction. Read-only; reuses
the FR7 sound-rows machinery and the repo consensus unmodified.

THE QUESTION. FR7/FR8 certified under PER-MESSAGE rows (one free base
variable per message). FR4 deduced the opposite -- that all nine effective
offsets are equal (the "one gauge" reading), which licenses PURE-progressive
rows with no base freedom at all. Both cannot be right, and the difference is
worth certification: fewer gauges means more determination.

THE TESTS.
  L1 gauge ladder: run the sound pool under 1 gauge (pure), 3 gauges
     (per-triplet) and 9 gauges (per-message); consistency is the diagnostic.
  L2 drift sweep: rhs = drift*(p2-p1) for every drift in 0..82, at each rung.
     Both row generators in the repo hardcode drift=1; a conflict at drift=1
     could be drift misspecification rather than gauge structure, and only a
     sweep can tell them apart. d=0 is DEGENERATE by construction (it asserts
     q[D]==q[A] at every aligned cell, merging symbols; GF carries no
     injectivity so it is always satisfiable) and is excluded by a pin-grade
     guard, never counted as a solution.
  L3 base-equality matrix: for each message pair, merge their base variables
     and re-run the full sound pool. Because consensus drops a pair only on
     contradiction, kept==total holds iff the whole system is satisfiable --
     so a drop under the merge is a genuine UNSATISFIABILITY result, not a
     seed-order artifact (the FR6 greedy-subset trap does not apply to a
     satisfiability verdict, only to which pairs get blamed).
  L4 opening/body test: the literal opening identities (FR3 cartography --
     T1 identical over 1..24, T3 over 1..20) are absent from the constraint
     pool because the calibrated anchor (rep=4) rejects those windows. Under
     the shared-plaintext reading an exact Delta=0 pair forces base equality,
     so adding the openings imposes exactly the merges L3 tests. Whether the
     result is consistent is the sharpest available check on FR4.

INTERPRETATION RULE (pre-committed, then CORRECTED -- see FR9 S1): I registered
that cross-triplet merges would be vacuous because a free base gap absorbs the
per-triplet keystream constant. That is wrong: the row generator carries no
separate kappa, so its base variable IS the effective per-message offset, and
merging two of them asserts equal effective offsets -- a substantive claim in
any triplet pairing. Cross-triplet verdicts are therefore reported as findings
about offsets, while WITHIN-triplet verdicts remain the structurally decisive
ones (there the shared keystream makes the shared-template reading testable).
"""

import json, os, sys
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "eyestem"))
sys.path.insert(0, os.path.join(HERE, "..", "eyereach"))
import eyestem as ES                       # noqa: E402
import eyereach as ER                      # noqa: E402
import iso_relax as IR                     # noqa: E402
import isomorph as iso                     # noqa: E402
import chain_extract as ce                 # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

TRIPLETS = {"T1": ["East 1", "West 1", "East 2"],
            "T2": ["West 2", "East 3", "West 3"],
            "T3": ["East 4", "West 4", "East 5"]}
OPENINGS = [(["East 1", "West 1", "East 2"], 1, 24),
            (["East 4", "West 4", "East 5"], 1, 20)]

PREREG = {
    "baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
    "degenerate_drift": 0,
    "vacuous_RETRACTED": "cross-triplet merges were wrongly pre-registered as vacuous",
    "drifts_reported": [1, 2, 3, 17, 41, 82],
}

# ---------------------------------------------------------------- rows
def build_context(cts, labels, atlas_path):
    apairs, pattern_of, by_class = ES.atlas_pairs_with_patterns(atlas_path, cts, labels)
    a = json.load(open(atlas_path)); idx = {lab: i for i, lab in enumerate(labels)}
    dot = {}; letter = set()
    for cls in a["classes"]:
        Lc, pat = cls["length"], cls["pattern"]
        for it in cls["instances"]:
            mi = idx[it["message"]]
            for i in range(Lc):
                cell = (mi, it["start"] + i)
                (letter.add(cell) if pat[i] != '.' else dot.__setitem__(cell, True))
    for cell in letter: dot.pop(cell, None)
    anchor = ce.calibrate_anchor(cts, 13, seed=0)
    strictp = iso.find_isomorphs(cts, 13, anchor, different_only=False)
    return dict(apairs=apairs, pattern_of=pattern_of, by_class=by_class,
                dot=dot, strict=strictp, anchor=anchor)

def make_rows(ctx, drift=1, group=None, n_msgs=9):
    pattern_of, dot = ctx["pattern_of"], ctx["dot"]
    if group is None: group = {m: m for m in range(n_msgs)}
    def rows(pr, messages, Nn):
        key = (pr.m1, pr.p1, pr.m2, pr.p2, pr.length)
        pat = pattern_of.get(key)
        rhs = (drift * (pr.p2 - pr.p1)) % Nn
        g1, g2 = group.get(pr.m1), group.get(pr.m2)
        for i in range(pr.length):
            if pat is not None and not pr.exact and pat[i] == '.': continue
            if pat is None and not pr.exact and \
               ((pr.m1, pr.p1 + i) in dot or (pr.m2, pr.p2 + i) in dot): continue
            A = int(messages[pr.m1][pr.p1 + i]); D = int(messages[pr.m2][pr.p2 + i])
            row = {}
            row[D] = (row.get(D, 0) + 1) % Nn
            row[A] = (row.get(A, 0) + Nn - 1) % Nn
            if g1 is not None and g2 is not None and g1 != g2:
                row[Nn + g2] = (row.get(Nn + g2, 0) + Nn - 1) % Nn
                row[Nn + g1] = (row.get(Nn + g1, 0) + 1) % Nn
            row = {v: cc for v, cc in row.items() if cc}
            yield row, rhs
    return rows

def run(cts, ctx, pool, drift=1, group=None, n_msgs=9):
    gf, k = ce.consensus_alphabet(cts, pool, N, make_rows(ctx, drift, group, n_msgs), seed=0)
    kept = len(k) if k else len(pool)
    return kept, len(pool), gf

def satisfiable(cts, ctx, pool, drift=1, group=None, n_msgs=9):
    """SOUND satisfiability: direct Gaussian elimination over all rows.
    Order-independent and exact.

    NOT to be confused with consensus_alphabet's kept-count. That routine is a
    heuristic (restarts + greedy purify-to-fixed-point, keeping the basin that
    "explains" the most pairs); it can drop pairs that are merely unexplained
    by the chosen basin, so kept < total does NOT imply unsatisfiability. This
    cycle initially made that inference and it is wrong -- see the selftest's
    negative gate, which asserts the two disagree on a known-satisfiable
    system."""
    gf = iso.GFSystem(N)
    rows_fn = make_rows(ctx, drift, group, n_msgs)
    for pr in pool:
        for row, rhs in rows_fn(pr, cts, N):
            verdict = gf.classify(row, rhs)
            if verdict == "contradiction":
                return False
            if verdict == "pivot":
                gf.add(row, rhs)
    return True

def degenerate(gf):
    """d=0-style collapse: everything merged onto one value -> no pin grade."""
    dom, _ = ER.certified_domain(gf)
    png, _ = ER.pin_grade(dom)
    return len(png) == 0

def opening_pairs(labels, specs):
    Lx = {lab: i for i, lab in enumerate(labels)}
    out = []
    for ms, lo, hi in specs:
        for m1, m2 in combinations(ms, 2):
            out.append(iso.IsoPair(m1=Lx[m1], p1=lo, m2=Lx[m2], p2=lo,
                                   length=hi - lo + 1, exact=True))
    return out

def verify_literal(cts, labels, specs):
    Lx = {lab: i for i, lab in enumerate(labels)}
    for ms, lo, hi in specs:
        ref = cts[Lx[ms[0]]][lo:hi + 1]
        for m in ms[1:]:
            if cts[Lx[m]][lo:hi + 1] != ref:
                fail(f"claimed literal opening {ms} {lo}..{hi} is not literal")
    return True

# ---------------------------------------------------------------- plant
def _pattern_of(vals):
    pat = []; seen = {}; nxt = ord('A')
    for v in vals:
        if vals.count(v) > 1:
            if v not in seen: seen[v] = chr(nxt); nxt += 1
            pat.append(seen[v])
        else: pat.append('.')
    return "".join(pat)

def plant_from_geometry(atlas_path, corpus_path, offsets, drift=1, seed=5):
    """FR7 doctrine: certified corpus geometry is the right plant spec. Takes
    the REAL atlas instance geometry (which is what generates cross-context
    collision cycles -- nested and overlapping classes), regenerates synthetic
    plaintext with shared blocks per class, and re-encrypts under KNOWN
    per-message offsets. Classes are rebuilt from whatever plaintext identity
    actually survives the overlap writes, so the plant is self-consistent by
    construction. Returns cts, labels, atlas path."""
    import random, tempfile
    rng = random.Random(seed)
    c = json.load(open(corpus_path)); labels = c["message_labels"]
    lens = [len(x) for x in c["ciphertexts"]]
    a = json.load(open(atlas_path)); idx = {lab: i for i, lab in enumerate(labels)}
    C = list(range(N)); rng.shuffle(C)
    plain = [[rng.randrange(N) for _ in range(lens[m])] for m in range(len(lens))]
    for cls in a["classes"]:
        L = cls["length"]; block = [rng.randrange(N) for _ in range(L)]
        for it in cls["instances"]:
            m = idx[it["message"]]; s = it["start"]
            plain[m][s:s + L] = block
    cts = [[int(C[(plain[m][t] + offsets[m] + drift * t) % N]) for t in range(lens[m])]
           for m in range(len(lens))]
    classes = []
    for cls in a["classes"]:
        L = cls["length"]
        groups = {}
        for it in cls["instances"]:
            m = idx[it["message"]]; s = it["start"]
            groups.setdefault(tuple(plain[m][s:s + L]), []).append((m, s))
        for gi, members in enumerate(groups.values()):
            if len(members) < 2: continue
            m0, s0 = members[0]
            classes.append({"id": f"{cls['id']}~{gi}", "length": L,
                            "pattern": _pattern_of(cts[m0][s0:s0 + L]),
                            "instances": [{"message": labels[m], "start": s,
                                           "values": cts[m][s:s + L]}
                                          for m, s in members]})
    f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump({"classes": classes}, f); f.close()
    return cts, labels, f.name

def plant_ctx(cts, labels, apath):
    apairs, pattern_of, by_class = ES.atlas_pairs_with_patterns(apath, cts, labels)
    return dict(apairs=apairs, pattern_of=pattern_of, by_class=by_class,
                dot={}, strict=[], anchor=None)

# ---------------------------------------------------------------- selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: gauge ladder sensitivity, matrix soundness, degeneracy guard")

    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))

    # (1) equal-offset plant: one gauge must be CONSISTENT -- the test must
    #     never fabricate a prohibition
    offE = [11] * 9
    ctsE, labE, apE = plant_from_geometry(atlas, corpus, offE)
    ctxE = plant_ctx(ctsE, labE, apE); poolE = ctxE["apairs"]
    sE1 = satisfiable(ctsE, ctxE, poolE, group={m: 0 for m in range(9)})
    sE9 = satisfiable(ctsE, ctxE, poolE, group={m: m for m in range(9)})
    check("equal-offset plant: one gauge consistent (no false prohibition)",
          sE1 and sE9, f"(pairs={len(poolE)}, one={sE1}, per={sE9})")

    # (2) distinct-offset plant: one gauge must be INCONSISTENT
    offD = [3, 3, 40, 17, 62, 9, 71, 28, 55]
    ctsD, labD, apD = plant_from_geometry(atlas, corpus, offD)
    ctxD = plant_ctx(ctsD, labD, apD); poolD = ctxD["apairs"]
    sD1 = satisfiable(ctsD, ctxD, poolD, group={m: 0 for m in range(9)})
    sD9 = satisfiable(ctsD, ctxD, poolD, group={m: m for m in range(9)})
    check("distinct-offset plant: one gauge inconsistent, per-message consistent",
          (not sD1) and sD9, f"(one={sD1}, per={sD9})")

    # (3) matrix soundness on the distinct-offset plant
    verdict = {}
    for i, j in combinations(range(9), 2):
        g = {m: m for m in range(9)}; g[j] = g[i]
        verdict[(i, j)] = satisfiable(ctsD, ctxD, poolD, group=g)
    truly_equal = {(i, j) for i, j in combinations(range(9), 2) if offD[i] == offD[j]}
    permitted = {p for p, v in verdict.items() if v}
    forbidden = {p for p, v in verdict.items() if not v}
    check("matrix: truly-equal pairs never forbidden", truly_equal <= permitted,
          f"(equal={sorted(truly_equal)})")
    # pairwise detection power depends on how tightly two messages are
    # coupled by shared classes; it is MEASURED here, not asserted (the
    # global one-gauge check above is the guaranteed sensitivity test)
    print(f"  [note] pairwise merge detection power on this plant: "
          f"{len(forbidden)}/{len(verdict)} truly-distinct merges detected; "
          f"pairwise power is coupling-dependent, so a corpus 'permitted' "
          f"verdict is weak evidence while a 'forbidden' verdict is exact")

    # (3b) NEGATIVE GATE: the consensus heuristic disagrees with the sound
    #      oracle on a known-satisfiable system -- the inference this cycle
    #      initially made (kept<total => unsatisfiable) is invalid
    keptE, totE, _ = run(ctsE, ctxE, poolE, group={m: m for m in range(9)})
    check("consensus kept-count is NOT a satisfiability oracle (negative gate)",
          sE9 and keptE < totE,
          f"(sound=SAT but heuristic kept {keptE}/{totE})")

    # (3c) oracle unit tests: exact contradiction detection
    class _C: pass
    gfu = iso.GFSystem(N)
    gfu.add({0: 1, 1: (N - 1)}, 1)
    check("oracle detects a direct contradiction",
          gfu.classify({0: 1, 1: (N - 1)}, 2) == "contradiction")
    check("oracle accepts a consistent restatement",
          gfu.classify({0: 1, 1: (N - 1)}, 1) == "redundant")

    # (4) degeneracy guard, via the sound path
    g0 = {m: 0 for m in range(9)}
    sat0 = satisfiable(ctsD, ctxD, poolD, drift=0, group=g0)
    gf0 = iso.GFSystem(N)
    for pr in poolD:
        for row, rhs in make_rows(ctxD, 0, g0, 9)(pr, ctsD, N):
            if gf0.classify(row, rhs) == "pivot": gf0.add(row, rhs)
    check("d=0 satisfiable but DEGENERATE (no pin grade)",
          sat0 and degenerate(gf0), f"(sat={sat0})")

    # (5) an exact Delta=0 pair acts exactly as a base merge
    pr = iso.IsoPair(m1=0, p1=30, m2=1, p2=30, length=8, exact=True)
    ctsX = [list(x) for x in ctsD]; ctsX[1][30:38] = ctsX[0][30:38]
    sX = satisfiable(ctsX, ctxD, poolD + [pr], group={m: m for m in range(9)})
    g01 = {m: m for m in range(9)}; g01[1] = g01[0]
    sM = satisfiable(ctsX, ctxD, poolD, group=g01)
    check("exact Delta=0 pair behaves as a base merge", sX == sM,
          f"(with-pair={sX}, merged={sM})")

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ---------------------------------------------------------------- corpus
def corpus_run(corpus_path, atlas_path):
    c = json.load(open(corpus_path))
    cts = [list(x) for x in c["ciphertexts"]]; labels = c["message_labels"]
    Lx = {lab: i for i, lab in enumerate(labels)}

    r = IR.relax(cts, N, seed=0)
    bg = PREREG["baseline_guard"]
    if (r.linked_strict, r.distinct_strict, len(r.pins)) != \
       (bg["linked"], bg["distinct"], bg["pins"]):
        fail("baseline reproduction mismatch")
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    ctx = build_context(cts, labels, atlas_path)
    pool = ctx["apairs"] + ctx["strict"]
    print(f"sound pool: {len(ctx['apairs'])} atlas + {len(ctx['strict'])} strict "
          f"= {len(pool)} pairs (anchor rep={ctx['anchor']})")
    op = sorted({(p.m1, p.p1, p.m2, p.p2) for p in ctx["strict"]
                 if p.p1 < 25 and p.p2 < 25})
    print(f"strict pairs inside the opening region: {len(op)}  "
          f"-> the literal openings are ABSENT from the pool")

    tri = {}
    for t, ms in TRIPLETS.items():
        for m in ms: tri[Lx[m]] = t
    gauges = {"1 gauge (pure / FR4 one-gauge)": {m: 0 for m in range(9)},
              "3 gauges (per-triplet)": {m: {"T1": 0, "T2": 1, "T3": 2}[tri[m]]
                                         for m in range(9)},
              "9 gauges (per-message)": {m: m for m in range(9)}}

    print("\nL1/L2 gauge ladder, SOUND oracle (d=0 excluded as degenerate):")
    for name, g in gauges.items():
        sat_ds = [d for d in range(1, N) if satisfiable(cts, ctx, pool, drift=d, group=g)]
        gfd = iso.GFSystem(N)
        for pr in pool:
            for row, rhs in make_rows(ctx, 1, g)(pr, cts, N):
                if gfd.classify(row, rhs) == "pivot": gfd.add(row, rhs)
        dom, _ = ER.certified_domain(gfd); png, _ = ER.pin_grade(dom)
        tail = (f"certified={len(dom)} pin={len(png)}" if 1 in sat_ds
                else "(certification meaningless: system unsatisfiable)")
        print(f"  {name:34s}: satisfiable at d=1? "
              f"{'YES' if 1 in sat_ds else 'NO':3s}   "
              f"non-degenerate drifts satisfiable: {len(sat_ds)}/82   {tail}")

    print("\nL3 base-equality matrix (may messages i,j share a base?):")
    hdr = "      " + " ".join(f"{labels[j][0]}{labels[j][-1]}" for j in range(9))
    print(hdr)
    forbidden = []
    for i in range(9):
        row = []
        for j in range(9):
            if i == j: row.append(" . "); continue
            g = {m: m for m in range(9)}; g[j] = g[i]
            okp = satisfiable(cts, ctx, pool, group=g)
            if not okp and i < j: forbidden.append((labels[i], labels[j]))
            row.append(" o " if okp else " X ")
        print(f"{labels[i]:8s} " + " ".join(row))
    within = [(a, b) for a, b in forbidden if tri[Lx[a]] == tri[Lx[b]]]
    cross = [(a, b) for a, b in forbidden if tri[Lx[a]] != tri[Lx[b]]]
    print(f"\n  forbidden within-triplet ({len(within)}): {within}")
    print(f"  forbidden cross-triplet  ({len(cross)}): {cross}"
          f"   [pre-registered as vacuous; that registration is RETRACTED -- see FR9 S1]")

    print("\n  drift-robustness of the within-triplet prohibitions:")
    print("    pair                 " + " ".join(f"d={d}" for d in PREREG["drifts_reported"]))
    for a, b in within + [("East 1", "West 1")]:
        outs = []
        for d in PREREG["drifts_reported"]:
            g = {m: m for m in range(9)}; g[Lx[b]] = g[Lx[a]]
            outs.append("FORB" if not satisfiable(cts, ctx, pool, drift=d, group=g)
                        else " OK ")
        print(f"    {a:8s}/{b:8s}  " + "  ".join(outs))

    print("\nL4 opening/body test (FR3 literal identities added to the pool):")
    verify_literal(cts, labels, OPENINGS)
    print("  literal opening identities verified against the corpus")
    T1o = opening_pairs(labels, OPENINGS[:1])
    T3o = opening_pairs(labels, OPENINGS[1:])
    for tag, extra in (("nothing", []), ("T1 openings", T1o),
                       ("T3 openings", T3o), ("both openings", T1o + T3o)):
        s = satisfiable(cts, ctx, pool + extra)
        print(f"  pool + {tag:14s}: {'SATISFIABLE' if s else 'CONTRADICTION'}")
    print(f"  openings alone: "
          f"{'satisfiable' if satisfiable(cts, ctx, T1o + T3o) else 'CONTRADICTION'}")
    print(f"  strict tier + openings: "
          f"{'satisfiable' if satisfiable(cts, ctx, ctx['strict'] + T1o + T3o) else 'CONTRADICTION'}")

    print("\n  minimal exhibits (smallest class sets that contradict an opening):")
    cids = list(ctx["by_class"])
    for tag, ops in (("T3 opening", T3o), ("T1 opening", T1o)):
        singles = [cid for cid in cids
                   if not satisfiable(cts, ctx, ctx["by_class"][cid] + ops)]
        if singles:
            print(f"    {tag}: single class {singles}")
            continue
        found = None
        for c1, c2 in combinations(cids, 2):
            if not satisfiable(cts, ctx,
                               ctx["by_class"][c1] + ctx["by_class"][c2] + ops):
                found = (c1, c2); break
        print(f"    {tag}: minimal class pair {found if found else '>2 classes required'}")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
