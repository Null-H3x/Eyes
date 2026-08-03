#!/usr/bin/env python3
"""
eyestrict -- reframing a redundancy as a corroboration. Read-only.

FR49's sensitivity map recorded that withdrawing the strict tier costs ZERO
relations, and described those eighteen pairs as "doing no work". That framing
is wrong, and this cycle corrects it.

The strict pairs come from iso_relax's own scan of the corpus. The thirteen
classes were INHERITED from the atlas. They are two different procedures
identifying repeated structure. Asking whether one implies the other is
therefore not a question about redundancy but about agreement.

RESULT. Building with the atlas classes ALONE and then classifying every row
the strict pairs emit: 158 rows, 158 REDUNDANT, zero pivots, zero
contradictions. The atlas implies every constraint the strict tier asserts.
The converse fails -- under a strict-only system 185 atlas rows are still
pivots -- so the atlas is strictly stronger, and the implication runs one way.

WHAT THIS IS AND IS NOT. It is method-level agreement: two procedures reading
the same corpus produce consistent constraints, with no conflict anywhere. It
is NOT data-level independence, since both derive from the same 1,036 glyphs.
The right reading is that the inherited atlas is not an artefact of one
scanning choice -- an independent scan re-finds structure entirely compatible
with it.
"""

import json, os, sys
from collections import Counter

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyeclass2", "eyeaudit2", "eyecirc", "eyerepair2", "eyeaudit",
          "eyeinject", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyeaudit as EA                      # noqa: E402
import eyegauge as EG                      # noqa: E402
import iso_relax as IR                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "strict_rows": 158}

def setup(corpus_path, atlas_path):
    cts, labels, Lx, ctx, pool, _ = EA.load(corpus_path, atlas_path)
    BR = (Lx["East 3"], 101); A1 = (Lx["East 1"], 68)
    def keep(pl):
        return [p for p in pl
                if not any((p.m1, p.p1) == k or (p.m2, p.p2) == k
                           for k in (BR, A1))]
    return cts, labels, Lx, ctx, keep(ctx["apairs"]), keep(ctx["strict"])

def classify_against(cts, ctx, Lx, base_pool, test_pool):
    gf = EA.build(cts, ctx, Lx, base_pool)
    if gf is None: return None, None
    rows = EG.make_rows(ctx, 1, {m: m for m in range(9)})
    tally = Counter(); per = []
    for p in test_pool:
        c = Counter()
        for r, rhs in rows(p, cts, N):
            v = gf.classify(r, rhs); c[v] += 1; tally[v] += 1
        per.append((p, c))
    return tally, per

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: implication in both directions, and a planted conflict")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    cts, labels, Lx, ctx, ap, st = setup(corpus, atlas)

    check("pool splits as expected", len(ap) == 49 and len(st) == 18,
          f"({len(ap)} atlas, {len(st)} strict)")

    t, per = classify_against(cts, ctx, Lx, ap, st)
    check("the atlas implies every strict row",
          t["pivot"] == 0 and t["contradiction"] == 0 and
          t["redundant"] == PREREG["strict_rows"],
          f"({dict(t)})")

    t2, _ = classify_against(cts, ctx, Lx, st, ap)
    check("the converse fails: the atlas is strictly stronger",
          t2 is not None and t2["pivot"] > 0, f"({dict(t2) if t2 else None})")

    # a planted conflicting pair must register as a contradiction
    import isomorph as iso
    bad = [iso.IsoPair(m1=Lx["East 1"], p1=30, m2=Lx["West 2"], p2=60,
                       length=6, exact=False)]
    t3, _ = classify_against(cts, ctx, Lx, ap, bad)
    check("a fabricated pair does NOT come out fully redundant",
          t3["pivot"] + t3["contradiction"] > 0, f"({dict(t3)})")

    c = json.load(open(corpus))
    cc = [list(x) for x in c["ciphertexts"]]
    r = IR.relax(cc, N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard", (r.linked_strict, r.distinct_strict, len(r.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    cts, labels, Lx, ctx, ap, st = setup(corpus_path, atlas_path)
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")
    print(f"\nS1 the two sources")
    print(f"  atlas classes (inherited), repaired : {len(ap)} pairs")
    print(f"  strict tier (iso_relax's own scan)  : {len(st)} pairs")

    print("\nS2 does the atlas imply the strict tier?")
    t, per = classify_against(cts, ctx, Lx, ap, st)
    print(f"  verdicts across all strict rows: {dict(t)}")
    print(f"  {'pair':32s} {'rows':>5s} {'redundant':>10s} {'pivot':>6s} "
          f"{'contra':>7s}")
    for p, c in per:
        print(f"  {labels[p.m1]:8s}@{p.p1:3d} x {labels[p.m2]:8s}@{p.p2:3d} "
              f"{sum(c.values()):5d} {c['redundant']:10d} {c['pivot']:6d} "
              f"{c['contradiction']:7d}")
    print("  -> every constraint the strict tier asserts is independently")
    print("     derivable from the inherited classes")

    print("\nS3 the converse")
    t2, _ = classify_against(cts, ctx, Lx, st, ap)
    print(f"  verdicts across all atlas rows under a strict-only system: "
          f"{dict(t2)}")
    print("  -> the atlas is strictly stronger; the implication runs one way")

    print("\nS4 where the strict pairs live")
    seen = set()
    for p in st:
        seen.add(labels[p.m1]); seen.add(labels[p.m2])
    print(f"  messages involved: {sorted(seen)}")
    print(f"  position range   : "
          f"{min(min(p.p1, p.p2) for p in st)}..{max(max(p.p1, p.p2) for p in st)}")
    print("  they re-find the T1 refrain region — the same passages the #M,")
    print("  #1, #C0 and #C1 classes describe")

    print("\nS5 the correction to FR49")
    print("  FR49 recorded the strict tier as 'doing no work'. That measures")
    print("  its marginal contribution correctly and describes its role wrongly.")
    print("  Two procedures read the same corpus and produced constraints that")
    print("  agree on all 158 rows with zero conflicts. That is method-level")
    print("  CORROBORATION of the inherited atlas, not waste.")
    print("  CAVEAT: both derive from the same 1,036 glyphs, so this is not")
    print("  data-level independence. What it rules out is the atlas being an")
    print("  artefact of one scanning choice.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
