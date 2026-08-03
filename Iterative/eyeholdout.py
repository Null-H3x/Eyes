#!/usr/bin/env python3
"""
eyeholdout -- can out-of-sample prediction adjudicate the repair fork?

FR109 reopened FR25's fork; FR110 killed its last support. Repair A is now
conventional rather than preferred. The only internal route left is the FR37 /
FR38 methodology, which has never been applied to the alternative reading.

CHALLENGE I rejects the naive form. Running leave-one-pair-out on repair B and
comparing rates to repair A's 59/59 is weak: both repairs were SELECTED for
injectivity-cleanness, so both models are coherent by construction and both may
score near 100%. A test both readings pass discriminates nothing.

THE SHARP FORM. The DISCARDED INSTANCE is itself held-out evidence.

    repair A asserts East 1@68 spurious and builds without it. If A's model
    nevertheless PREDICTS East 1@68's cells, that instance behaves like genuine
    shared plaintext and A discarded something real -- evidence against A.

    repair B asserts East 4@51 spurious. Same logic, mirrored.

A spurious instance is a chance pattern match, so its cells carry arbitrary
glyph pairs and a model built without it should not predict them beyond chance.
A genuine instance encodes real shared plaintext and should be predicted.

BUILT-IN NEGATIVE CONTROL. East 3@101 is discarded by BOTH repairs and was
priced at coincidence grade by FR15 (p ~ 0.10). A sound method should fail to
predict it under both models -- a control drawn from the corpus rather than
planted.

PREDICTION, per FR37: a held-out pair is PREDICTED if every cell whose two
glyphs are both determined by the rebuilt model agrees on a single value of
q[b] - q[a]. Cells the model cannot reach are not testable and are excluded.

PRE-REGISTERED (frozen before measurement):
  R1  comparison is run at the SHARED clean ratios {8, 9, 22, 40} so that both
      repairs are evaluated where both are injectivity-clean.
  R2  East 3@101 must NOT be predicted under either model. If it is, the method
      cannot distinguish genuine from spurious and NO verdict is drawn.
  R3  a verdict is claimed only if the two candidates behave DIFFERENTLY. If
      both are predicted, or neither is, the fork is closed to internal
      analysis and that is the finding.

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""

import json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

XD = "XD-MBYG04K-URS3LF"
N = 83

import eyegauge as EG
import isomorph as iso
import eyeratio as ER
import eyerefork as RF

SHARED = [8, 9, 22, 40]
CANDIDATES = {
    "East 1@68  (repair A calls spurious)": ("East 1", 68),
    "East 4@51  (repair B calls spurious)": ("East 4", 51),
    "East 3@101 (BOTH call spurious)":      ("East 3", 101),
}


def build_model(cts, ctx, Lx, red, gmap, d1, d2):
    return ER.build_two(cts, ctx, Lx, red, d1, d2, gmap)


def determined_diff(gf, a, b):
    """Value of q[b]-q[a] if the model determines it, else None."""
    if a == b: return None
    hits = [d for d in range(N)
            if gf.classify({b: 1, a: N - 1}, d) == "redundant"]
    return hits[0] if len(hits) == 1 else None


def predict_pair(gf, cts, pr, ctx):
    """FR37 prediction: do all determined cells of this pair agree on one w?
    Returns (testable_cells, agree) with agree None if untestable."""
    pattern_of, dot = ctx["pattern_of"], ctx["dot"]
    key = (pr.m1, pr.p1, pr.m2, pr.p2, pr.length)
    pat = pattern_of.get(key)
    vals = []
    for i in range(pr.length):
        if pat is not None and not pr.exact and pat[i] == '.': continue
        if pat is None and not pr.exact and \
           ((pr.m1, pr.p1 + i) in dot or (pr.m2, pr.p2 + i) in dot): continue
        a = int(cts[pr.m1][pr.p1 + i]); b = int(cts[pr.m2][pr.p2 + i])
        v = determined_diff(gf, a, b)
        if v is not None: vals.append(v)
    # A single determined cell agrees with itself trivially, which makes the
    # test powerless (measured: 52% of random pairs "predicted"). FR37's 1.2%
    # chance rate implies at least two determined cells were required. Pairs
    # with fewer than two are UNTESTABLE, not predicted.
    if len(vals) < 2: return len(vals), None
    return len(vals), len(set(vals)) == 1


def pairs_touching(pool, Lx, msg, pos):
    k = (Lx[msg], pos)
    return [p for p in pool if (p.m1, p.p1) == k or (p.m2, p.p2) == k]


def selftest():
    ok = []
    def ck(n, c, d=""):
        ok.append((n, bool(c))); print(f"  {n:34s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise RuntimeError(f"{XD} selftest FAILED: {n} {d}")

    cts, labels, Lx, ctx, pool = RF.load_pool()
    gmap = ER.group_map(labels)
    ck("t1_pool", len(pool) == 83, f"{len(pool)} sound pairs")

    redA = RF.repaired(pool, Lx, RF.REPAIRS["A"])
    gfA = build_model(cts, ctx, Lx, redA, gmap, 1, 1)
    ck("t2_modelA", gfA is not None, "repair A builds at ratio 1")

    # t3: the model must predict a pair it was BUILT from (sanity, not evidence)
    inpool = redA[0]
    n, agree = predict_pair(gfA, cts, inpool, ctx)
    ck("t3_insample", agree is True and n > 0,
       f"in-sample pair: {n} cells, agree={agree}")

    # t4: a fabricated pair over random positions should NOT be predicted
    rng = random.Random(111)
    class Fake:
        pass
    bad = 0; tested = 0
    for _ in range(40):
        f = Fake()
        f.m1 = rng.randrange(9); f.m2 = rng.randrange(9)
        L = 9
        if len(cts[f.m1]) <= L + 2 or len(cts[f.m2]) <= L + 2: continue
        f.p1 = rng.randrange(len(cts[f.m1]) - L)
        f.p2 = rng.randrange(len(cts[f.m2]) - L)
        f.length = L; f.exact = True
        n, agree = predict_pair(gfA, cts, f, ctx)
        if agree is not None:
            tested += 1
            if agree: bad += 1
    rate = bad / tested if tested else 0
    ck("t4_chance_low", rate < 0.25,
       f"random pairs predicted {bad}/{tested} (>=2 determined cells required)")

    # t5: candidate pairs exist in the full pool
    for lbl, (m, p) in CANDIDATES.items():
        ck(f"t5_{m}@{p}", len(pairs_touching(pool, Lx, m, p)) > 0,
           f"{len(pairs_touching(pool, Lx, m, p))} pool pairs")
    print(f"selftest {sum(1 for _,p in ok if p)}/{len(ok)} green")
    return cts, labels, Lx, ctx, pool, gmap, rate


def corpus_run(env):
    cts, labels, Lx, ctx, pool, gmap, chance = env
    print("=" * 74)
    print("EYEHOLDOUT -- predicting each discarded instance from the model")
    print("              built without it")
    print("=" * 74)
    print(f"\n  chance rate on random pairs (from gate): {100*chance:.0f}%")
    print(f"  [R1] evaluated at the shared clean ratios {SHARED}\n")

    results = {}
    for repair in ("A", "B"):
        red = RF.repaired(pool, Lx, RF.REPAIRS[repair])
        for lbl, (m, p) in CANDIDATES.items():
            held = pairs_touching(pool, Lx, m, p)
            # only meaningful if this repair actually excluded them
            excluded = all(h not in red for h in held)
            if not excluded: continue
            per_ratio = []
            for r in SHARED:
                gf = build_model(cts, ctx, Lx, red, gmap, r, 1)
                if gf is None: per_ratio.append(None); continue
                tot = 0; agree_all = True; any_test = False
                for h in held:
                    n, ag = predict_pair(gf, cts, h, ctx)
                    if ag is None: continue
                    any_test = True; tot += n
                    if not ag: agree_all = False
                per_ratio.append((tot, agree_all) if any_test else None)
            results[(repair, lbl)] = per_ratio
            summary = ["untestable" if x is None
                       else ("PREDICTED" if x[1] else "not predicted")
                       for x in per_ratio]
            cells = [0 if x is None else x[0] for x in per_ratio]
            print(f"  model {repair} | held out {lbl}")
            print(f"      {len(held)} pool pairs, testable cells per ratio {cells}")
            print(f"      verdict per ratio {SHARED}: {summary}\n")

    # [R2] control
    ctrl = [results.get((r, "East 3@101 (BOTH call spurious)")) for r in ("A", "B")]
    ctrl_pred = any(x is not None and x[1] for c in ctrl if c for x in c if x)
    print(f"[R2] control East 3@101 predicted under either model: {ctrl_pred}")
    if ctrl_pred:
        print("     the method cannot separate genuine from spurious -> NO verdict")
        return

    a_key = ("A", "East 1@68  (repair A calls spurious)")
    b_key = ("B", "East 4@51  (repair B calls spurious)")
    a_res = [x for x in (results.get(a_key) or []) if x]
    b_res = [x for x in (results.get(b_key) or []) if x]
    a_pred = bool(a_res) and all(x[1] for x in a_res)
    b_pred = bool(b_res) and all(x[1] for x in b_res)
    print(f"\n[R3] East 1@68 predicted by model A : {a_pred}"
          f"{'  (testable)' if a_res else '  (UNTESTABLE)'}")
    print(f"     East 4@51 predicted by model B : {b_pred}"
          f"{'  (testable)' if b_res else '  (UNTESTABLE)'}")
    if a_pred == b_pred:
        print("\n     THE CANDIDATES BEHAVE IDENTICALLY -> no verdict.")
        print("     The repair fork is CLOSED TO INTERNAL ANALYSIS; only")
        print("     acquisition can settle it.")
    elif a_pred and not b_pred:
        print("\n     East 1@68 behaves GENUINE, East 4@51 behaves SPURIOUS")
        print("     -> evidence FAVOURS REPAIR B.")
    else:
        print("\n     East 4@51 behaves GENUINE, East 1@68 behaves SPURIOUS")
        print("     -> evidence FAVOURS REPAIR A.")
    print()


if __name__ == "__main__":
    env = selftest()
    if "--selftest" not in sys.argv: corpus_run(env)
