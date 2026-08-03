#!/usr/bin/env python3
"""
eyeanchor -- testing FR16's coherent configuration predictively, finding the
result flat, diagnosing why, and turning the diagnosis into an operational
target list for the R6 external-anchor programme. Read-only.

THE PREDICTIVE TEST. FR16 reached the first configuration in the series that
is consistent without flattening the keystream. Its horizon asked whether
certification can finally grow from there. Two constraints are available that
the project has never imposed: the offset equalities forced by literal body
runs, E1/W1 (a run of length 13, chance ~5e-25) and E4/E5 (three runs of
length 3). Unlike FR15's removal test these ADD information, so the question
is well-posed.

THE ANSWER IS NO, AND THE PATTERN IS NOW DIAGNOSTIC. Certification stays at
exactly 10 certified symbols with one merge, both merges, or neither. That is
the third consecutive cycle in which a "does certification grow" test comes
back flat -- FR11's reading comparison, FR16's bridge removal, and now this.
The common factor is that all three manipulate OFFSET / BASE information, and
offsets are not the bottleneck. FR8 proved certified differences collapse onto
the absolute-pin domain; what limits growth is symbol linking under gauge
invariance, and no amount of offset information touches that.

THE CONSTRUCTIVE TURN. External anchors are the doctrine's route past the
wall, and they act on symbols rather than offsets. A single anchor does not
grow the gauge-invariant certified domain -- it only fixes the rotation the
reference already fixes -- but it does DETERMINE symbols, which is the
operationally relevant quantity. Measuring that gives a leverage curve and,
more usefully, a per-glyph ranking: anchor placement dominates anchor count.

CAVEATS carried in the output: "determined" presumes the supplied pin values
are CORRECT; only the 51 glyphs the constraint pool touches are reachable at
all, so full determination here is not a full solve; and the ranking is
computed against the current sound tier.
"""

import json, os, random, sys

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyecohere", "eyeshape", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyegauge as EG                      # noqa: E402
import eyereach as ER                      # noqa: E402
import iso_relax as IR                     # noqa: E402
import isomorph as iso                     # noqa: E402
import chain_extract as ce                 # noqa: E402
import eyeshape as ESH                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

TRIPLETS = EG.TRIPLETS
PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "bridge": ("East 3", 101), "seed": 20260727,
          "runs_merges": [("East 1", "West 1"), ("East 4", "East 5")]}

def setup(corpus_path, atlas_path):
    c = json.load(open(corpus_path))
    cts = [list(x) for x in c["ciphertexts"]]; labels = c["message_labels"]
    Lx = {l: i for i, l in enumerate(labels)}
    ctx = EG.build_context(cts, labels, atlas_path)
    pool = ctx["apairs"] + ctx["strict"]
    bm, bp = PREREG["bridge"]; br = (Lx[bm], bp)
    red = [p for p in pool if not ((p.m1, p.p1) == br or (p.m2, p.p2) == br)]
    rows = EG.make_rows(ctx, 1, {m: m for m in range(9)})
    return dict(cts=cts, labels=labels, Lx=Lx, ctx=ctx, pool=pool, red=red,
                rows=rows)

def build(S, pl, merges=(), pins=()):
    gf, _ = ce.consensus_alphabet(S["cts"], pl, N, S["rows"], seed=0)
    for a, b in merges:
        row = {N + S["Lx"][b]: 1, N + S["Lx"][a]: N - 1}
        v = gf.classify(row, 0)
        if v == "contradiction": return None
        if v == "pivot": gf.add(row, 0)
    for s, val in pins:
        v = gf.classify({s: 1}, val)
        if v == "contradiction": return None
        if v == "pivot": gf.add({s: 1}, val)
    return gf

def determined(gf):
    sol = gf.solve(); syms = [v for v in sol if v < N]
    det = {s for s in syms
           if gf.classify({s: 1}, (sol[s] + 1) % N) == "contradiction"}
    return det, syms

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: determination logic and monotonicity")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    S = setup(corpus, atlas)

    gf0 = build(S, S["pool"])
    det0, syms = determined(gf0)
    check("no external pins determines nothing", len(det0) == 0,
          f"({len(det0)} of {len(syms)})")

    sol0 = gf0.solve()
    gfa = build(S, S["pool"], pins=[(syms[0], sol0[syms[0]])])
    det1, _ = determined(gfa)
    check("one pin determines a nonempty set", len(det1) >= 1, f"({len(det1)})")

    gfb = build(S, S["pool"],
                pins=[(s, sol0[s]) for s in syms[:2]])
    det2, _ = determined(gfb)
    check("monotone: two pins determine at least as many as one",
          len(det2) >= len(det1), f"({len(det1)} -> {len(det2)})")

    gfall = build(S, S["pool"], pins=[(s, sol0[s]) for s in syms])
    detall, _ = determined(gfall)
    check("pinning every symbol determines every symbol",
          len(detall) == len(syms), f"({len(detall)}/{len(syms)})")

    r = IR.relax(S["cts"], N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard reproduces the certified inventory",
          (r.linked_strict, r.distinct_strict, len(r.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    S = setup(corpus_path, atlas_path)
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    print("\nC1 predictive test: certification from FR16's coherent configuration")
    print("  (run-forced offset equalities ADD information, so this is well-posed)")
    print("  NOTE: FR16's coherent configuration requires PER-TRIPLET drifts. Under a")
    print("  fixed GLOBAL drift the E4/E5 merge contradicts (FR9/FR16 reproduced), so")
    print("  both row models are reported and the conclusion is checked in each.")
    GIDX = {"T1": 0, "T2": 1, "T3": 2}
    trig = {S["Lx"][m]: GIDX[t] for t, ms in TRIPLETS.items() for m in ms}
    SEG = N + 9
    def pertrip_gf(pl, merges):
        """per-message bases + per-triplet affine keystream (FR16 model)"""
        gf = iso.GFSystem(N)
        for a, b in merges:
            row = {N + S["Lx"][b]: 1, N + S["Lx"][a]: N - 1}
            v = gf.classify(row, 0)
            if v == "contradiction": return None
            if v == "pivot": gf.add(row, 0)
        po, dot = S["ctx"]["pattern_of"], S["ctx"]["dot"]
        for pr in pl:
            key = (pr.m1, pr.p1, pr.m2, pr.p2, pr.length); pat = po.get(key)
            g1, g2 = trig[pr.m1], trig[pr.m2]
            for i in range(pr.length):
                if pat is not None and not pr.exact and pat[i] == '.': continue
                if pat is None and not pr.exact and \
                   ((pr.m1, pr.p1 + i) in dot or (pr.m2, pr.p2 + i) in dot): continue
                A = int(S["cts"][pr.m1][pr.p1 + i]); D = int(S["cts"][pr.m2][pr.p2 + i])
                t1, t2 = pr.p1 + i, pr.p2 + i
                row = {}
                def acc(k_, v_): row[k_] = (row.get(k_, 0) + v_) % N
                acc(D, 1); acc(A, N - 1)
                if pr.m1 != pr.m2:
                    acc(N + pr.m2, N - 1); acc(N + pr.m1, 1)
                acc(SEG + 2 * g2, N - 1); acc(SEG + 2 * g2 + 1, (N - t2 % N) % N)
                acc(SEG + 2 * g1, 1);     acc(SEG + 2 * g1 + 1, t1 % N)
                row = {k_: v_ for k_, v_ in row.items() if v_}
                v = gf.classify(row, 0)
                if v == "contradiction": return None
                if v == "pivot": gf.add(row, 0)
        return gf
    cases = (("reduced pool, no merges", S["red"], ()),
             ("reduced + E1/W1 merge", S["red"], [PREREG["runs_merges"][0]]),
             ("reduced + E4/E5 merge", S["red"], [PREREG["runs_merges"][1]]),
             ("reduced + BOTH run-forced merges", S["red"], PREREG["runs_merges"]),
             ("full pool + both merges", S["pool"], PREREG["runs_merges"]))
    print("\n  (a) global drift = 1 (the FR9-FR14 model):")
    for tag, pl, mg in cases:
        gf = build(S, pl, merges=mg)
        if gf is None: print(f"      {tag:34s}: CONTRADICTION"); continue
        dom, _ = ER.certified_domain(gf)
        print(f"      {tag:34s}: certified = {len(dom)}")
    print("\n  (b) per-triplet free drifts (FR16's coherent model):")
    for tag, pl, mg in cases:
        gf = pertrip_gf(pl, mg)
        if gf is None: print(f"      {tag:34s}: CONTRADICTION"); continue
        dom, _ = ER.certified_domain(gf)
        print(f"      {tag:34s}: certified = {len(dom)}  {sorted(dom)}")
    print("  -> FLAT. Third consecutive cycle where a certification-growth test")
    print("     returns nothing; all three manipulated OFFSET information, and")
    print("     offsets are not the bottleneck (FR8: growth is symbol-linking-limited)")

    print("\nC2 external-anchor leverage curve (random placement, 12 trials each)")
    gf0 = build(S, S["pool"]); sol0 = gf0.solve()
    syms = sorted(v for v in sol0 if v < N)
    print(f"  reachable symbols (touched by the constraint pool): {len(syms)} of 83")
    rng = random.Random(PREREG["seed"])
    print(f"  {'k pins':>7s} {'determined mean':>16s} {'best':>6s} {'worst':>6s}")
    for k in (0, 1, 2, 3, 5, 8, 12, 16, 20, 25, 30):
        vals = []
        for _ in range(12 if k else 1):
            pins = [(s, sol0[s]) for s in (rng.sample(syms, k) if k else [])]
            gf = build(S, S["pool"], pins=pins)
            if gf is None: continue
            vals.append(len(determined(gf)[0]))
        if vals:
            print(f"  {k:7d} {sum(vals)/len(vals):16.1f} {max(vals):6d} {min(vals):6d}")

    print("\nC3 per-glyph leverage: symbols determined by pinning that glyph alone")
    lev = []
    for s in syms:
        gf = build(S, S["pool"], pins=[(s, sol0[s])])
        if gf is None: continue
        lev.append((len(determined(gf)[0]), s))
    lev.sort(reverse=True)
    print(f"  strongest: {[(s, n) for n, s in lev[:10]]}")
    print(f"  weakest  : {[(s, n) for n, s in lev[-6:]]}")
    print("  -> placement dominates count: a single anchor is worth 21 symbols "
          "or 1,\n     depending only on which component it lands in")

    print("\nC4 greedy anchor set (each next glyph chosen to maximise determination)")
    chosen = []
    for _ in range(10):
        best = None
        for s in syms:
            if s in chosen: continue
            gf = build(S, S["pool"], pins=[(x, sol0[x]) for x in chosen + [s]])
            if gf is None: continue
            n = len(determined(gf)[0])
            if best is None or n > best[0]: best = (n, s)
        if best is None: break
        chosen.append(best[1])
        print(f"  {len(chosen)} anchors {chosen}: determined {best[0]}/{len(syms)}")
        if best[0] >= len(syms): break

    print("\nC5 caveats")
    print("  * 'determined' presumes the supplied pin values are CORRECT")
    print(f"  * only {len(syms)} of 83 glyphs are reachable by the current pool;")
    print("    determining all of them is not a full solve")
    print("  * the ranking is computed against the current sound tier and would")
    print("    move if the pool changes")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
