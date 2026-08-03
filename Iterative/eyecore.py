#!/usr/bin/env python3
"""
eyecore -- resolving FR9's fork. Minimal unsatisfiable cores for the
opening/body contradiction, class-level localisation, a reality check on
the implicated classes, and the model test that turns the fork into a
sharp trilemma. Read-only; reuses the FR7 sound rows and FR9's sound
(direct-Gaussian) satisfiability oracle unmodified.

FR9 LEFT A FORK. The literal opening identities (T1 over 1..24, T3 over
1..20 -- absent from the constraint pool because the calibrated anchor
rejects those windows) contradict the certified atlas body classes under
per-message progressive rows. Exactly one of three premises must fail:

  (i)   the literal openings are SHARED PLAINTEXT (an exact Delta=0 pair
        between two messages of one triplet forces their offsets equal,
        because the shared keystream cancels exactly),
  (ii)  the certified atlas classes are SAME-PLAINTEXT,
  (iii) the offset is LINEAR in position (progressive: off_m[t] =
        base_m + drift*t).

THE TESTS.
  C1 minimal ingredient: which single opening pair suffices, and does the
     contradiction need the FR3 cross-triplet bridges?
  C2 minimal unsatisfiable cores by deletion filtering, verified minimal
     (core UNSAT, core minus any one pair SAT).
  C3 class-level localisation: iteratively extract a core, drop one of its
     classes, repeat -- the set of classes that must go to restore
     satisfiability. This prices premise (ii).
  C4 class reality: are the implicated classes real repeats or pattern
     coincidences? Unigram-preserving shuffle null on the isomorph search.
     This prices premise (ii) again, from the other side.
  C5 the model test: rerun the whole contradiction with the ONLY change
     being the keystream reading. Under progressive the within-triplet
     offset difference at shift (p1,p2) is forced to drift*(p2-p1); under
     Gromark/general-K it is a free constant per (triplet, p1, p2), while
     Delta=0 pairs still force offset equality exactly (K cancels). This
     prices premise (iii).

HONESTY NOTE built into the reading of C5: the Gromark rows are strictly
more permissive than the progressive rows, so "Gromark fits" is expected
and is NOT evidence for Gromark. The informative direction is the other
one -- progressive makes a sharp prediction here and it fails.
"""

import json, os, random, sys
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyegauge as EG                      # noqa: E402
import eyestem as ES                       # noqa: E402
import iso_relax as IR                     # noqa: E402
import isomorph as iso                     # noqa: E402
import chain_extract as ce                 # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

TRIPLETS = EG.TRIPLETS
OPENINGS = EG.OPENINGS
BASE, DELTA = N, N + 9

PREREG = {
    "baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
    "null_shuffles": 30,
    "premises": ["(i) openings shared plaintext",
                 "(ii) atlas classes same-plaintext",
                 "(iii) offset linear in position"],
    "permissiveness_note": "Gromark rows are strictly weaker; their fitting is "
                           "expected and is not evidence for Gromark",
}

# ------------------------------------------------------------------ rows
def rows_factory(ctx, tri, model):
    pattern_of, dot = ctx["pattern_of"], ctx["dot"]
    keys = {}
    def rows(pr, messages, Nn):
        key = (pr.m1, pr.p1, pr.m2, pr.p2, pr.length)
        pat = pattern_of.get(key)
        g1, g2 = tri[pr.m1], tri[pr.m2]
        exact_shift = (g1 == g2 and pr.p1 == pr.p2)   # K cancels exactly
        if model == "progressive" or exact_shift:
            rhs = (pr.p2 - pr.p1) % Nn; dvar = None
        elif model == "gromark":
            dk = (g1, g2, pr.p1, pr.p2)
            if dk not in keys: keys[dk] = DELTA + len(keys)
            dvar = keys[dk]; rhs = 0
        else:
            fail(f"unknown model {model}")
        for i in range(pr.length):
            if pat is not None and not pr.exact and pat[i] == '.': continue
            if pat is None and not pr.exact and \
               ((pr.m1, pr.p1 + i) in dot or (pr.m2, pr.p2 + i) in dot): continue
            A = int(messages[pr.m1][pr.p1 + i]); D = int(messages[pr.m2][pr.p2 + i])
            row = {}
            row[D] = (row.get(D, 0) + 1) % Nn
            row[A] = (row.get(A, 0) + Nn - 1) % Nn
            if pr.m1 != pr.m2:
                row[BASE + pr.m2] = (row.get(BASE + pr.m2, 0) + Nn - 1) % Nn
                row[BASE + pr.m1] = (row.get(BASE + pr.m1, 0) + 1) % Nn
            if dvar is not None:
                row[dvar] = (row.get(dvar, 0) + Nn - 1) % Nn
            row = {v: cc for v, cc in row.items() if cc}
            yield row, rhs
    return rows

def sat(cts, ctx, tri, pool, model="progressive"):
    """FR9's sound oracle: direct Gaussian elimination, order-independent."""
    gf = iso.GFSystem(N)
    rf = rows_factory(ctx, tri, model)
    for pr in pool:
        for row, rhs in rf(pr, cts, N):
            v = gf.classify(row, rhs)
            if v == "contradiction": return False
            if v == "pivot": gf.add(row, rhs)
    return True

# ------------------------------------------------------------------ cores
def minimal_core(cts, ctx, tri, pool, keep, model="progressive"):
    """deletion filtering; result is a genuine MUS w.r.t. single removals."""
    cur = list(pool)
    for p in list(pool):
        trial = [q for q in cur if q is not p]
        if not sat(cts, ctx, tri, trial + keep, model):
            cur = trial
    return cur

def verify_core(cts, ctx, tri, core, keep, model="progressive"):
    if sat(cts, ctx, tri, core + keep, model): return False
    for p in core:
        if not sat(cts, ctx, tri, [q for q in core if q is not p] + keep, model):
            return False
    return True

def class_localisation(cts, ctx, tri, pool, keep, cls_of, max_rounds=8):
    avail = list(pool); dropped = []; rounds = []
    for _ in range(max_rounds):
        if sat(cts, ctx, tri, avail + keep):
            return dropped, rounds, True
        core = minimal_core(cts, ctx, tri, avail, keep)
        cls = sorted({cls_of.get(id(p), "?") for p in core})
        rounds.append((len(core), cls))
        atlas_cls = [x for x in cls if x != "strict"] or cls
        drop = atlas_cls[0]
        dropped.append(drop)
        avail = [p for p in avail if cls_of.get(id(p), "?") != drop]
    return dropped, rounds, sat(cts, ctx, tri, avail + keep)

# ------------------------------------------------------------------ null
def class_reality_null(cts, lengths, shuffles, seed=20260725):
    rng = random.Random(seed)
    out = []
    for Lw, rep in lengths:
        obs = len(iso.find_isomorphs(cts, Lw, rep, different_only=False))
        nulls = []
        for _ in range(shuffles):
            sh = []
            for m in cts:
                s = list(m); rng.shuffle(s); sh.append(s)
            nulls.append(len(iso.find_isomorphs(sh, Lw, rep, different_only=False)))
        mu = sum(nulls) / len(nulls)
        sd = (sum((x - mu) ** 2 for x in nulls) / max(1, len(nulls) - 1)) ** 0.5
        out.append(dict(L=Lw, rep=rep, obs=obs, mu=mu, sd=sd,
                        mx=max(nulls), z=((obs - mu) / sd if sd else None)))
    return out

# ------------------------------------------------------------------ plant
def plant(atlas_path, corpus_path, kind, seed=9, drift=1):
    """Real atlas geometry (FR7 doctrine), synthetic plaintext, offsets equal
    within each triplet so the literal openings are reproduced. kind:
      'progressive' -- K_g(t) = drift*t
      'jumped'      -- K_g(t) = drift*t + jump_g[region(t)], regions chosen so
                       every class span lies inside one region: pairs stay
                       perfect isomorphs but their offset difference is
                       drift*(p2-p1) PLUS a region jump, which progressive rows
                       cannot express and Gromark rows can.
    Returns cts, labels, atlas path, opening specs."""
    import tempfile
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
    for ms, lo, hi in OPENINGS:                     # shared opening plaintext
        blk = [rng.randrange(N) for _ in range(hi - lo + 1)]
        for m in ms: plain[idx[m]][lo:hi + 1] = blk
    bounds = [0, 35, 70, 200]
    jumps = {g: [0] + [rng.randrange(1, N) for _ in range(len(bounds) - 2)]
             for g in TRIPLETS}
    def region(t):
        for r in range(len(bounds) - 1):
            if bounds[r] <= t < bounds[r + 1]: return r
        return len(bounds) - 2
    tri_of = {}
    for g, ms in TRIPLETS.items():
        for m in ms: tri_of[idx[m]] = g
    def K(g, t):
        if kind == "progressive": return (drift * t) % N
        return (drift * t + jumps[g][region(t)]) % N
    off = {}
    for g, ms in TRIPLETS.items():
        b = rng.randrange(N)
        for m in ms: off[idx[m]] = b          # equal within triplet
    cts = [[int(C[(plain[m][t] + off[m] + K(tri_of[m], t)) % N])
            for t in range(lens[m])] for m in range(len(lens))]
    classes = []
    for cls in a["classes"]:
        L = cls["length"]; groups = {}
        for it in cls["instances"]:
            m = idx[it["message"]]; s = it["start"]
            groups.setdefault(tuple(plain[m][s:s + L]), []).append((m, s))
        for gi, members in enumerate(groups.values()):
            if len(members) < 2: continue
            # keep only members that remain perfect isomorphs (same region)
            m0, s0 = members[0]
            pat0 = ES._pattern_of(cts[m0][s0:s0 + L]) if hasattr(ES, "_pattern_of") \
                   else EG._pattern_of(cts[m0][s0:s0 + L])
            # an instance is a perfect isomorph iff its span lies INSIDE one
            # region (so K's difference to any other such span is constant);
            # spans may sit in DIFFERENT regions -- that is what carries the
            # jump the progressive rows cannot express
            good = [(m, s) for m, s in members
                    if (EG._pattern_of(cts[m][s:s + L]) == pat0
                        and region(s) == region(s + L - 1))]
            if len(good) < 2: continue
            classes.append({"id": f"{cls['id']}~{gi}", "length": L, "pattern": pat0,
                            "instances": [{"message": labels[m], "start": s,
                                           "values": cts[m][s:s + L]}
                                          for m, s in good]})
    f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump({"classes": classes}, f); f.close()
    return cts, labels, f.name

def plant_ctx(cts, labels, apath):
    apairs, pattern_of, by_class = ES.atlas_pairs_with_patterns(apath, cts, labels)
    return dict(apairs=apairs, pattern_of=pattern_of, by_class=by_class,
                dot={}, strict=[], anchor=None)

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: core minimality, model discrimination, null machinery")

    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    c = json.load(open(corpus)); labels = c["message_labels"]
    Lx = {lab: i for i, lab in enumerate(labels)}
    tri = {}
    for g, ms in TRIPLETS.items():
        for m in ms: tri[Lx[m]] = g

    # (1) progressive plant: openings must be CONSISTENT under progressive
    ctsP, labP, apP = plant(atlas, corpus, "progressive")
    ctxP = plant_ctx(ctsP, labP, apP)
    opsP = EG.opening_pairs(labP, OPENINGS)
    EG.verify_literal(ctsP, labP, OPENINGS)
    sP = sat(ctsP, ctxP, tri, ctxP["apairs"] + opsP, "progressive")
    check("progressive plant: openings consistent under progressive rows", sP,
          f"(pairs={len(ctxP['apairs'])})")

    # (2) MODEL DISCRIMINATOR on a CERTIFIED CORPUS EXHIBIT.
    #     FR7 doctrine: synthetic plaintext lacks the cross-context collisions
    #     that generate contradiction cycles, so the right specification is a
    #     corpus exhibit whose status is already certified. This is the FR10
    #     T3 minimal core (verified minimal below); it must be UNSAT under
    #     progressive and SAT under Gromark -- the whole cycle's claim.
    ctsR = [list(x) for x in c["ciphertexts"]]
    ctxR = EG.build_context(ctsR, labels, atlas)
    poolR = ctxR["apairs"] + ctxR["strict"]
    want = [("East 1", 40, "East 3", 101, 8), ("East 1", 68, "East 3", 101, 8),
            ("East 4", 51, "East 5", 52, 12), ("West 4", 53, "East 5", 52, 12),
            ("West 1", 40, "East 2", 80, 13), ("West 1", 70, "East 2", 80, 13)]
    exhibit = []
    for m1, p1, m2, p2, L in want:
        hit = [p for p in poolR if p.m1 == Lx[m1] and p.p1 == p1
               and p.m2 == Lx[m2] and p.p2 == p2 and p.length == L]
        if not hit: fail(f"exhibit pair missing from pool: {m1}@{p1} x {m2}@{p2}")
        exhibit.append(hit[0])
    opR = [iso.IsoPair(m1=Lx["East 4"], p1=1, m2=Lx["West 4"], p2=1,
                       length=20, exact=True)]
    EG.verify_literal(ctsR, labels, OPENINGS)
    ep = sat(ctsR, ctxR, tri, exhibit + opR, "progressive")
    eg = sat(ctsR, ctxR, tri, exhibit + opR, "gromark")
    check("certified exhibit: UNSAT under progressive, SAT under Gromark "
          "(the model discriminator)", (not ep) and eg,
          f"(prog={ep}, gromark={eg})")

    # (3) that exhibit is a genuine minimal core
    check("certified exhibit is a genuinely minimal core",
          verify_core(ctsR, ctxR, tri, exhibit, opR), f"(|core|={len(exhibit)})")

    # (4) no core exists when the system is satisfiable
    check("satisfiable system yields no contradiction",
          sat(ctsP, ctxP, tri, ctxP["apairs"] + opsP, "progressive"))

    # (5) null machinery: shuffled corpora destroy long isomorphs
    cts = [list(x) for x in c["ciphertexts"]]
    res = class_reality_null(cts, [(12, 3)], shuffles=6)
    r = res[0]
    check("null machinery: long isomorphs vanish under shuffling",
          r["obs"] > 0 and r["mx"] == 0, f"(obs={r['obs']}, null max={r['mx']})")

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    c = json.load(open(corpus_path))
    cts = [list(x) for x in c["ciphertexts"]]; labels = c["message_labels"]
    Lx = {lab: i for i, lab in enumerate(labels)}
    r = IR.relax(cts, N, seed=0); bg = PREREG["baseline_guard"]
    if (r.linked_strict, r.distinct_strict, len(r.pins)) != \
       (bg["linked"], bg["distinct"], bg["pins"]):
        fail("baseline reproduction mismatch")
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    ctx = EG.build_context(cts, labels, atlas_path)
    pool = ctx["apairs"] + ctx["strict"]
    tri = {}
    for g, ms in TRIPLETS.items():
        for m in ms: tri[Lx[m]] = g
    cls_of = {}
    for cid, prs in ctx["by_class"].items():
        for p in prs: cls_of[id(p)] = cid
    for p in ctx["strict"]: cls_of[id(p)] = "strict"
    EG.verify_literal(cts, labels, OPENINGS)
    T1o = EG.opening_pairs(labels, OPENINGS[:1])
    T3o = EG.opening_pairs(labels, OPENINGS[1:])

    print("\nC1 minimal ingredient: which single opening pair contradicts?")
    for tag, ops in (("T1", T1o), ("T3", T3o)):
        for o in ops:
            s = sat(cts, ctx, tri, pool + [o])
            print(f"  {tag}: {labels[o.m1]:8s}/{labels[o.m2]:8s} -> "
                  f"{'satisfiable' if s else 'CONTRADICTION'}")
    wt = [p for p in pool if tri[p.m1] == tri[p.m2]]
    print(f"  within-triplet pool only + T3 opening: "
          f"{'satisfiable' if sat(cts, ctx, tri, wt + T3o) else 'CONTRADICTION'}"
          f"   -> cross-triplet bridges are NOT required")

    print("\nC2 minimal unsatisfiable cores (verified minimal):")
    for tag, op in (("T3 opening E4/W4",
                     iso.IsoPair(m1=Lx["East 4"], p1=1, m2=Lx["West 4"], p2=1,
                                 length=20, exact=True)),
                    ("T1 opening E1/E2",
                     iso.IsoPair(m1=Lx["East 1"], p1=1, m2=Lx["East 2"], p2=1,
                                 length=24, exact=True))):
        core = minimal_core(cts, ctx, tri, pool, [op])
        good = verify_core(cts, ctx, tri, core, [op])
        print(f"  {tag}: |core| = {len(core)} + 1 opening pair  (minimal={good})")
        for p in core:
            print(f"    [{cls_of.get(id(p), '?'):6s}] {labels[p.m1]:8s}@{p.p1:3d} x "
                  f"{labels[p.m2]:8s}@{p.p2:3d} L={p.length}")

    print("\nC3 class localisation (which classes must go to restore satisfiability):")
    for tag, ops in (("T3 opening", T3o), ("T1 opening", T1o)):
        dropped, rounds, done = class_localisation(cts, ctx, tri, pool, ops, cls_of)
        for i, (sz, cls) in enumerate(rounds):
            print(f"    {tag} round {i}: |core|={sz} classes={cls}")
        print(f"    {tag}: satisfiable after dropping {dropped} "
              f"({'resolved' if done else 'NOT resolved within budget'})")
        print(f"    [note] this is a GREEDY path: {len(dropped)} classes is an "
              f"UPPER bound on the minimum hitting set, not a minimum "
              f"(FR6 greedy-subset lesson applies to hitting sets too)")

    print("\nC4 class reality (unigram-preserving shuffle null):")
    for res in class_reality_null(cts, [(12, 3), (15, 3), (8, 2)],
                                  PREREG["null_shuffles"]):
        print(f"    L={res['L']:2d} min_repeats={res['rep']}: observed {res['obs']:3d}, "
              f"null mean {res['mu']:.1f} (max {res['mx']}), "
              f"z={'inf' if res['z'] is None else f'{res[chr(122)]:.1f}'}")

    print("\nC5 the model test (only the keystream reading changes):")
    for model in ("progressive", "gromark"):
        line = []
        for tag, extra in (("alone", []), ("+T1", T1o), ("+T3", T3o),
                           ("+both", T1o + T3o)):
            line.append(f"{tag}={'SAT' if sat(cts, ctx, tri, pool + extra, model) else 'CONTRA'}")
        print(f"    {model:12s}: " + "  ".join(line))
    print("    within-triplet base merges under Gromark:")
    for a, b in (("East 4", "West 4"), ("East 1", "East 2"), ("East 3", "West 3")):
        pr = iso.IsoPair(m1=Lx[a], p1=1, m2=Lx[b], p2=1, length=2, exact=True)
        print(f"      {a:8s}/{b:8s}: "
              f"{'permitted' if sat(cts, ctx, tri, pool + [pr], 'gromark') else 'FORBIDDEN'}")
    print(f"    [note] {PREREG['permissiveness_note']}")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
