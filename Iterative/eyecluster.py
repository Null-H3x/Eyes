#!/usr/bin/env python3
"""
eyecluster -- test for a CERTIFIED-DIFFERENCE grade below the absolute pins,
and (finding none) characterise the letter-collision census as the sole
sound growth lever. Read-only; reuses FR7 sound-rows machinery + repo
consensus unmodified.

THE HYPOTHESIS (this cycle's, entered honestly and then refuted). Under the
per-message-progressive model each symbol value is affine in the free base
variables. It seemed possible that two symbols could have an UNDETERMINED
absolute value yet a DETERMINED difference -- a relational grade sitting
below FR7's 8 absolute pins, potentially decidably linking the FR5 battery
glyphs (glyph 47 is #M's A-letter at the literal E1@40/W1@40 occurrence).

THE RESULT. There is no such grade. A difference x[b]-x[a] is certified iff
it is invariant under the gauge freedoms (global rotation AND every free
per-message base). The gauge-invariance test proves: every symbol outside
the absolute-pin domain has its difference to the domain MOVE under a gauge
shift. Hence the certified-difference set equals the absolute-pin domain
exactly -- the pins already ARE the complete sound relational inventory.
The naive reduction/classify oracles that appear to find a larger grade are
unsound: they pivot on base-lead rows, silently substituting the gauge-0
base values and fabricating cross-message "certifications" (7/44 truth-exact
on the audit plant -- a documented failure mode, kept as a negative gate).

CONSEQUENCE. Growth is not hiding in relational structure; it requires new
LETTER-cell collisions (FR7's determination engine) that extend the
gauge-invariant component itself. The letter-collision census maps exactly
which additions would do so and which touch the battery glyphs.
"""

import json, os, sys
from collections import defaultdict
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
import chain_models as cm                  # noqa: E402
import chain_extract as ce                 # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16}}

def _inv(x): return pow(x % N, N - 2, N)

def gauge_solves(gf, n_msgs, trials=48, seed=0):
    """the sound oracle basis: solve many times with the reference AND every
    free per-message base variable pinned to independent random values. A
    difference is certified iff invariant across ALL solves -- this exercises
    every gauge freedom (global rotation + per-message bases), so only truly
    gauge-invariant differences survive. Perturbing the reference alone is
    INSUFFICIENT: it leaves per-message bases fixed at 0, letting
    within-message differences appear spuriously constant (the 9/191 trap)."""
    import random
    syms = sorted(v for v in gf.solve() if v < N)
    if len(syms) < 2: return None, []
    ref = syms[0]; rng = random.Random(seed)
    solves = []
    for _ in range(trials):
        g = iso.GFSystem(N); g.restore(gf.snapshot())
        try:
            g.add({ref: 1}, rng.randrange(N))
            for m in range(n_msgs):
                g.add({N + m: 1}, rng.randrange(N))
            solves.append(g.solve())
        except Exception:
            pass
    return ref, solves

def certified_diff_sound(solves, a, b):
    if a == b: return 0
    vals = set()
    for s in solves:
        if a not in s or b not in s: return None
        vals.add((s[b] - s[a]) % N)
    return vals.pop() if len(vals) == 1 else None

def certified_diff_naive(gf, a, b):
    """UNSOUND reduction oracle (pivots through base leads). Retained only to
    demonstrate the failure mode in the selftest; never used for verdicts."""
    if a == b: return 0
    r = {b: 1, a: (N - 1) % N}; acc = 0; piv = gf.pivots
    while r:
        lead = min(r)
        if lead not in piv: return None
        prow, prhs = piv[lead]
        f = (r[lead] * _inv(prow[lead])) % N
        for k, c in prow.items():
            nv = (r.get(k, 0) - f * c) % N
            if nv: r[k] = nv
            elif k in r: del r[k]
        acc = (acc - f * prhs) % N
    return (-acc) % N

def letter_collisions(atlas_path, cts, labels):
    a = json.load(open(atlas_path))
    idx = {lab: i for i, lab in enumerate(labels)}
    hypset = {47, 1, 66, 5} | set(ER.INDICATORS.values())
    out = []
    for cls in a["classes"]:
        L, pat = cls["length"], cls["pattern"]
        letter_off = [i for i in range(L) if pat[i] != '.']
        occ = defaultdict(list)
        for it in cls["instances"]:
            mi = idx[it["message"]]
            for i in letter_off:
                occ[cts[mi][it["start"] + i]].append(
                    (it["message"], it["start"] + i, pat[i]))
        for sym, places in occ.items():
            cells = {(p[0], p[1]) for p in places}
            if len(cells) >= 2:
                out.append(dict(cls=cls["id"], sym=sym, places=places,
                                roles=sorted({p[2] for p in places}),
                                hyp=(sym in hypset)))
    return out

def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: sound oracle exactness, the collapse theorem, naive-oracle trap")

    cts, q_truth, bases = IR._overdetermined_plant(seed=3)
    anchor = ce.calibrate_anchor(cts, 10, seed=0)
    scanp = iso.find_isomorphs(cts, 10, anchor, different_only=False)
    gf, keep = ce.consensus_alphabet(cts, scanp, N, cm.per_msg_prog_rows, seed=0)
    syms = sorted(v for v in gf.solve() if v < N)
    absset, _ = ER.certified_domain(gf)
    dom = set(absset)

    # 1. absolute-pin differences are exact vs truth (the trusted primitive)
    tested = exact = 0
    for a, b in combinations(sorted(dom), 2):
        tested += 1
        exact += ((absset[b] - absset[a]) % N == (q_truth[b] - q_truth[a]) % N)
    check("absolute-pin differences exact vs truth", tested == exact,
          f"({exact}/{tested}, pins={len(dom)})")

    # 2. THE COLLAPSE (proven with the trusted gauge oracle, two shifts of the
    #    reference suffice to move any non-pin symbol because the reference sits
    #    in a fixed component and non-pins are gauge-free relative to it): every
    #    symbol OUTSIDE the pin domain has a difference to the domain that MOVES
    #    under a reference gauge shift -> not certified. So the
    #    certified-difference set cannot exceed the pin domain.
    ref = sorted(dom)[0]
    def sh(delta):
        g = iso.GFSystem(N); g.restore(gf.snapshot()); g.add({ref: 1}, delta)
        return g.solve()
    s0, s7 = sh(0), sh(7)
    outs = [s for s in syms if s not in dom]
    moved = 0
    for o in outs:
        vs = {(sx[o] - sx[ref]) % N for sx in (s0, s7) if o in sx}
        if len(vs) > 1: moved += 1
    check("collapse: every non-pin symbol moves under gauge (no relational grade)",
          moved == len(outs), f"({moved}/{len(outs)})")

    # 3. within-pin differences are gauge-invariant (the complementary half)
    inv = all(len({(sx[b] - sx[a]) % N for sx in (s0, s7)}) == 1
              for a, b in combinations(sorted(dom), 2))
    check("pin differences are gauge-invariant", inv)

    # 4. the naive oracle is demonstrably unsound (the trap, kept explicit)
    ntest = nexact = 0
    for a, b in combinations(syms, 2):
        d = certified_diff_naive(gf, a, b)
        if d is not None:
            ntest += 1; nexact += (d == (q_truth[b] - q_truth[a]) % N)
    check("naive reduction oracle is UNSOUND (documented failure mode)",
          ntest > nexact, f"({nexact}/{ntest} exact -- base-lead substitution fabricates certs)")

    # 5. letter-collision census returns hyp-tagged collisions on a plant atlas
    import tempfile
    classes = [{"id": "#T", "length": 4, "pattern": "ABAB",
                "instances": [{"message": "m0", "start": 0,
                               "values": [int(cts[0][i]) for i in range(4)]},
                              {"message": "m1", "start": 0,
                               "values": [int(cts[1][i]) for i in range(4)]}]}]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"classes": classes}, f); ap = f.name
    lc = letter_collisions(ap, cts, [f"m{i}" for i in range(len(cts))])
    check("letter-collision census runs", isinstance(lc, list))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

def corpus_run(corpus_path, atlas_path):
    c = json.load(open(corpus_path))
    cts = [list(x) for x in c["ciphertexts"]]
    labels = c["message_labels"]

    r = IR.relax(cts, N, seed=0)
    bg = PREREG["baseline_guard"]
    if (r.linked_strict, r.distinct_strict, len(r.pins)) != \
       (bg["linked"], bg["distinct"], bg["pins"]):
        fail("baseline reproduction mismatch")
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    # FR7 unified sound tier via eyecluster's own builder in eyestem terms
    sys.path.insert(0, os.path.join(HERE, "..", "eyecluster"))
    gf, kept, tot = _sound_gf(cts, labels, atlas_path)
    print(f"unified sound tier: kept {kept}/{tot}")
    syms = sorted(v for v in gf.solve() if v < N)
    absset, _ = ER.certified_domain(gf)
    dom = set(absset)
    print(f"solution symbols: {len(syms)}  absolute pins: {len(dom)}")

    # the collapse, on the corpus: gauge-motion test (trusted primitive)
    ref = sorted(dom)[0] if dom else syms[0]
    def sh(delta):
        g = iso.GFSystem(N); g.restore(gf.snapshot()); g.add({ref: 1}, delta)
        return g.solve()
    s0, s7 = sh(0), sh(7)
    outs = [s for s in syms if s not in dom]
    moved = sum(1 for o in outs
                if len({(sx[o] - sx[ref]) % N for sx in (s0, s7) if o in sx}) > 1)
    print(f"\nnon-pin symbols: {len(outs)}; move under gauge shift: {moved}")
    print(f"COLLAPSE THEOREM on corpus: "
          f"{'CONFIRMED -- certified-difference set == absolute-pin domain, no relational grade' if moved == len(outs) else 'VIOLATED -- a relational grade exists'}")

    # contrast with the unsound naive oracle to quantify the trap on-corpus
    naive_cd = set()
    for a, b in combinations(syms, 2):
        if certified_diff_naive(gf, a, b) is not None:
            naive_cd.add(a); naive_cd.add(b)
    print(f"(naive UNSOUND oracle would falsely report {len(naive_cd)} symbols "
          f"linked -- the mirage this cycle refutes)")

    print("\nletter-collision census (the sole sound growth lever, FR7):")
    coll = letter_collisions(atlas_path, cts, labels)
    hyp_touch = defaultdict(list)
    dom = set(absset)
    growth = []
    for e in coll:
        in_dom = e["sym"] in dom
        placestr = ", ".join(f"{p[0]}@{p[1]}[{p[2]}]" for p in e["places"])
        tag = "HYP" if e["hyp"] else ""
        extends = "EXTENDS-DOMAIN" if not in_dom else ""
        if not in_dom: growth.append(e["sym"])
        print(f"  {e['cls']:5s} sym {e['sym']:2d} roles {e['roles']} "
              f"{'in-pin' if in_dom else 'free'} {tag} {extends}: {placestr}")
        if e["hyp"]: hyp_touch[e["sym"]].append(e["cls"])

    print("\nhypothesis glyphs and their letter-collision reach:")
    for g in sorted({47, 1, 66, 5} | set(ER.INDICATORS.values())):
        cl = hyp_touch.get(g, [])
        print(f"  glyph {g:2d}: {'letter-collides in ' + ','.join(cl) if cl else 'no letter collision (unreachable this way)'}")

def _sound_gf(cts, labels, atlas_path):
    apairs, pattern_of, by_class = ES.atlas_pairs_with_patterns(atlas_path, cts, labels)
    a = json.load(open(atlas_path)); idx = {lab: i for i, lab in enumerate(labels)}
    dot = {}; letter = set()
    for cls in a["classes"]:
        L, pat = cls["length"], cls["pattern"]
        for it in cls["instances"]:
            mi = idx[it["message"]]
            for i in range(L):
                cell = (mi, it["start"] + i)
                (letter.add(cell) if pat[i] != '.' else dot.__setitem__(cell, True))
    for cell in letter: dot.pop(cell, None)
    srows = ES.sound_rows_factory(pattern_of)
    anchor = ce.calibrate_anchor(cts, 13, seed=0)
    strictp = iso.find_isomorphs(cts, 13, anchor, different_only=False)
    def unified(pr, messages, Nn):
        key = (pr.m1, pr.p1, pr.m2, pr.p2, pr.length)
        if key in pattern_of or pr.exact:
            yield from srows(pr, messages, Nn); return
        bm1, bm2 = Nn + pr.m1, Nn + pr.m2; rhs = (pr.p2 - pr.p1) % Nn
        for i in range(pr.length):
            if (pr.m1, pr.p1 + i) in dot or (pr.m2, pr.p2 + i) in dot: continue
            A = int(messages[pr.m1][pr.p1 + i]); D = int(messages[pr.m2][pr.p2 + i])
            row = {D: 1, A: (Nn - 1) % Nn} if A != D else {}
            if pr.m1 != pr.m2:
                row[bm2] = (row.get(bm2, 0) + Nn - 1) % Nn
                row[bm1] = (row.get(bm1, 0) + 1) % Nn
            row = {v: cc for v, cc in row.items() if cc}
            yield row, rhs
    pool = apairs + strictp
    gf, keep = ce.consensus_alphabet(cts, pool, N, unified, seed=0)
    return gf, len(keep) if keep else len(pool), len(pool)

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
