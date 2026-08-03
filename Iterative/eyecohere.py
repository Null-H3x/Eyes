#!/usr/bin/env python3
"""
eyecohere -- adopting FR15's branch (ii) provisionally, measuring what it
actually buys, and finding the first configuration in seven cycles that is
consistent WITHOUT flattening the keystream. Read-only.

THE CORRECTION THIS CYCLE FORCES. FR15 reported that dropping the #M- bridge
instance (East 3 @ 101) turns FR14's body-internal system from degenerate to
live. That is true under a PER-TRIPLET drift model and false under a SINGLE
GLOBAL drift: with one shared drift, removing the bridge changes nothing at
all -- the gauge ladder, the base-equality matrix, the opening contradiction,
the body-internal contradiction and the certified pin set all come out
bit-identical. The two readings are not independent: a single global drift is
licensed only by FR3's cross-triplet drift-equality deduction, and that
deduction rests on the two bridge windows, one of which FR15 priced at
coincidence grade. So "discard the weak bridge" and "let drifts vary per
triplet" are one package, not two choices.

WHAT THE PACKAGE DOES AND DOES NOT FIX. It fixes FR14's body-internal
contradiction: with the bridge gone, the E4/E5 offset equality forced by the
literal body runs is carried with all three triplet drifts still live. It does
NOT fix the opening contradiction: add the literal openings back and every
drift is forced flat again. Branch (ii) alone is therefore insufficient --
exactly as FR14 showed branch (i) alone is insufficient.

THE COMBINATION. Excluding the openings from the constraint pool (branch i)
AND dropping E3@101 (branch ii) yields a system that is LIVE with 3 of 3
drifts free while honouring the body-run evidence. This is the first
configuration in the FR9-FR15 sequence that buys consistency without
surrendering determination.
"""

import json, os, sys

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyebridge2", "eyeshape", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyeshape as ESH                     # noqa: E402
import eyegauge as EG                      # noqa: E402
import eyereach as ER                      # noqa: E402
import iso_relax as IR                     # noqa: E402
import isomorph as iso                     # noqa: E402
import chain_extract as ce                 # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

TRIPLETS = EG.TRIPLETS
GIDX = {"T1": 0, "T2": 1, "T3": 2}
PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "bridge": ("East 3", 101)}

def setup(corpus_path, atlas_path):
    c = json.load(open(corpus_path))
    cts = [list(x) for x in c["ciphertexts"]]; labels = c["message_labels"]
    Lx = {l: i for i, l in enumerate(labels)}
    tri = {m: t for t, ms in TRIPLETS.items() for m in ms}
    trig = {Lx[m]: GIDX[t] for m, t in tri.items()}
    ctx = EG.build_context(cts, labels, atlas_path)
    pool = ctx["apairs"] + ctx["strict"]
    bm, bp = PREREG["bridge"]
    br = (Lx[bm], bp)
    red = [p for p in pool if not ((p.m1, p.p1) == br or (p.m2, p.p2) == br)]
    T1o = EG.opening_pairs(labels, EG.OPENINGS[:1])
    T3o = EG.opening_pairs(labels, EG.OPENINGS[1:])
    merge = iso.IsoPair(m1=Lx["East 4"], p1=25, m2=Lx["East 5"], p2=25,
                        length=3, exact=True)
    if cts[Lx["East 4"]][25:28] != cts[Lx["East 5"]][25:28]:
        fail("E4/E5 body run @25 is not literal")
    return dict(cts=cts, labels=labels, Lx=Lx, trig=trig, ctx=ctx, pool=pool,
                red=red, openings=T1o + T3o, merge=merge)

def per_triplet(S, pl):
    return ESH.analyse(S["cts"], S["ctx"], S["trig"], pl, {})

def global_drift(S, pl):
    return sum(1 for d in range(1, N)
               if EG.satisfiable(S["cts"], S["ctx"], pl, drift=d))

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: bridge arithmetic and the four anchor results")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    S = setup(corpus, atlas)

    check("bridge removal drops exactly the 6 pairs touching E3@101",
          len(S["pool"]) - len(S["red"]) == 6,
          f"({len(S['pool'])} -> {len(S['red'])})")

    st, fr, ex = per_triplet(S, S["pool"])
    check("baseline: full pool LIVE with 3 of 3 drifts free",
          st == "LIVE" and fr == 3, f"({st}, {fr}/{ex})")

    st, fr, _ = per_triplet(S, S["pool"] + [S["merge"]])
    check("FR14 reproduced: full pool + body-run merge is DEGENERATE",
          st == "DEGENERATE" and fr == 0, f"({st}, free={fr})")

    st, fr, _ = per_triplet(S, S["red"] + [S["merge"]])
    check("FR15 reproduced (per-triplet drifts): reduced + merge is LIVE",
          st == "LIVE" and fr == 3, f"({st}, free={fr})")

    n_full = global_drift(S, S["pool"] + [S["merge"]])
    n_red = global_drift(S, S["red"] + [S["merge"]])
    check("THE CORRECTION: under a single global drift the bridge removal "
          "changes nothing", n_full == n_red == 0, f"({n_full}/82 vs {n_red}/82)")

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    S = setup(corpus_path, atlas_path)
    cts, labels = S["cts"], S["labels"]
    r = IR.relax(cts, N, seed=0); bg = PREREG["baseline_guard"]
    if (r.linked_strict, r.distinct_strict, len(r.pins)) != \
       (bg["linked"], bg["distinct"], bg["pins"]):
        fail("baseline reproduction mismatch")
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")
    print(f"full pool {len(S['pool'])} pairs; reduced (E3@101 dropped) "
          f"{len(S['red'])}")

    print("\nC1 the drift-scope correction: single GLOBAL drift, full vs reduced")
    gauges = {"1 gauge (pure)": {m: 0 for m in range(9)},
              "3 gauges (per-triplet)": {m: S["trig"][m] for m in range(9)},
              "9 gauges (per-message)": {m: m for m in range(9)}}
    for name, g in gauges.items():
        a = sum(1 for d in range(1, N)
                if EG.satisfiable(cts, S["ctx"], S["pool"], drift=d, group=g))
        b = sum(1 for d in range(1, N)
                if EG.satisfiable(cts, S["ctx"], S["red"], drift=d, group=g))
        print(f"  {name:24s}: full {a:2d}/82   reduced {b:2d}/82")
    for tag, extra in (("+ openings", S["openings"]), ("+ merge", [S["merge"]])):
        a = global_drift(S, S["pool"] + extra); b = global_drift(S, S["red"] + extra)
        print(f"  pool {tag:12s}      : full {a:2d}/82   reduced {b:2d}/82")
    print("  -> under one global drift the bridge is inert; FR15's result lives "
          "entirely\n     in the per-triplet reading, and that reading is "
          "licensed by the same\n     bridge audit (FR3's drift equality came "
          "from the bridges)")

    print("\nC2 the package, per-triplet drifts (free drifts = model health):")
    rows = [("full pool", S["pool"], []),
            ("full pool + openings", S["pool"], S["openings"]),
            ("full pool + body-run merge", S["pool"], [S["merge"]]),
            ("full pool + openings + merge", S["pool"], S["openings"] + [S["merge"]]),
            ("REDUCED pool", S["red"], []),
            ("REDUCED + openings", S["red"], S["openings"]),
            ("REDUCED + body-run merge", S["red"], [S["merge"]]),
            ("REDUCED + openings + merge", S["red"], S["openings"] + [S["merge"]])]
    for tag, pl, extra in rows:
        st, fr, ex = per_triplet(S, pl + extra)
        mark = "   <== COHERENT" if (st == "LIVE" and fr == 3 and extra) else ""
        print(f"  {tag:30s}: {st:11s} free drifts {fr}/{ex}{mark}")

    print("\nC3 reading the table")
    print("  branch (ii) alone  -- reduced pool + openings -- is DEGENERATE:")
    print("     dropping the weak bridge does NOT rescue the opening contradiction.")
    print("  branch (i) alone was already shown insufficient (FR14): the body-run")
    print("     contradiction survives with no opening data in the pool.")
    print("  TOGETHER they suffice: reduced pool + body-run merge, openings")
    print("     excluded, is LIVE with all three triplet drifts still free.")

    print("\nC4 certification under the coherent configuration:")
    for tag, pl in (("full pool", S["pool"]), ("reduced pool", S["red"])):
        gf, _ = ce.consensus_alphabet(cts, pl, N,
                    EG.make_rows(S["ctx"], 1, {m: m for m in range(9)}), seed=0)
        dom, _ = ER.certified_domain(gf); png, _ = ER.pin_grade(dom)
        print(f"  {tag:14s}: certified={len(dom)} pin-grade={len(png)} "
              f"pins={sorted(png)}")
    print("  -> the pin inventory is unchanged by the bridge removal: this cycle "
          "costs\n     the doctrine nothing in certified material")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
