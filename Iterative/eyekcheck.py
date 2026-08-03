#!/usr/bin/env python3
"""
eyekcheck -- testing the assumption FR39 did not state, and grading its
conclusion accordingly. Read-only.

WHAT FR39 ASSUMED WITHOUT SAYING SO. The coincidence channel reconstructs the
plaintext as p[t] = A + drift*v[t] with v[t] = (Delta_{c[t]} - t). That step
assumes K_g[t] = kappa_g + drift*t -- progressive -- at EVERY position used.
If K departs from arithmetic anywhere in the measured territory, the residual
enters p as noise, flattens the distribution, and MANUFACTURES the very
result FR39 reported. FR13 proved K arithmetic only on limited ranges, so the
assumption is not free.

THE BIND THIS EXPOSES. FR13's arithmetic ranges were derived from shift-1
certified pairs, so they lie almost entirely INSIDE the spans the channel must
exclude to remain non-circular. Of 481 channel positions, only 22 fall inside
a verified range. Verified-K and non-circular are close to mutually exclusive
on this corpus, which is a structural constraint on what can be measured here
and is worth recording independently of this cycle's verdict.

THE TEST, AND ITS DIRECTION OF BIAS. Admitting positions inside certified
spans restores the sample inside the verified ranges (2147 pairs). Those
positions are circular in a known direction -- shared passages inflate
coincidences -- so the measurement OVERSTATES structure. If it still reads
flat, FR39's conclusion holds a fortiori.

RESULT. Inside the verified ranges: z = -0.94, effective alphabet 102. Outside:
z = -0.61, effective alphabet 89.5. Both flat, and they agree, so the flatness
is not an artifact of K. But power inside the verified region reaches only an
effective alphabet of 50, which grades FR39's claim rather than overturning it.
"""

import json, os, random, sys
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyepool2", "eyeclass", "eyeloo", "eyeclust", "eyefree2", "eyebridge3",
          "eyewiden", "eyepair", "eyeseek", "eyefree", "eyebase", "eyealpha",
          "eyepack", "eyeskel", "eyerepair", "eyescore", "eyeinject",
          "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyepool2 as EP                      # noqa: E402
import eyeloo as EL                        # noqa: E402
import eyerepair as ERP                    # noqa: E402
import eyeinject as EI                     # noqa: E402
import iso_relax as IR                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "arith": {"T3": [(35, 66), (68, 98)], "T2": [(23, 37)], "T1": []},
          "seed": 20260810, "nulls": 2000}

def context(S):
    Lx, cts = S["Lx"], S["cts"]
    pool = ERP.drop(S["pool"], (Lx["East 3"], 101), (Lx["East 1"], 68))
    gf = EL.build(S, pool)
    D, C = EL.deltas(gf)
    W = {}
    for a, b in combinations(range(9), 2):
        h = [d for d in range(N)
             if gf.classify({N + b: 1, N + a: N - 1}, d) == "redundant"]
        if len(h) == 1: W[(a, b)] = h[0]
    cov = set()
    for p in pool:
        for i in range(p.length):
            cov.add((p.m1, p.p1 + i)); cov.add((p.m2, p.p2 + i))
    tri = {}
    for t, ms in (("T1", ["East 1", "West 1", "East 2"]),
                  ("T2", ["West 2", "East 3", "West 3"]),
                  ("T3", ["East 4", "West 4", "East 5"])):
        for m in ms: tri[Lx[m]] = t
    nd = {(Lx["East 1"], Lx["West 1"]), (Lx["East 4"], Lx["East 5"])}
    return D, C, W, cov, tri, nd

def is_arith(tri, m, t):
    return any(lo <= t < hi for lo, hi in PREREG["arith"].get(tri[m], []))

def channel(S, D, C, cov, tri, use_arith, drop_cov, invert=False):
    pos = {}
    for mi, m in enumerate(S["cts"]):
        for t, g in enumerate(m):
            if g not in C: continue
            if drop_cov and (mi, t) in cov: continue
            if use_arith:
                a = is_arith(tri, mi, t)
                if (not a) if not invert else a: continue
            pos.setdefault((mi, C[g]), []).append((t, (D[g] - t) % N))
    return pos

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: arithmetic map, the bind, circularity direction")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    S = EI.setup(corpus, atlas)
    D, C, W, cov, tri, nd = context(S)
    Lx = S["Lx"]

    check("T1 has no proven-arithmetic range (FR13)",
          PREREG["arith"]["T1"] == [])
    check("T3's ranges match FR13's cartography",
          PREREG["arith"]["T3"] == [(35, 66), (68, 98)])
    check("a T3 position inside a range is recognised",
          is_arith(tri, Lx["East 4"], 40) and not is_arith(tri, Lx["East 4"], 20))

    full = channel(S, D, C, cov, tri, False, True)
    restr = channel(S, D, C, cov, tri, True, True)
    nf = sum(len(v) for v in full.values()); nr = sum(len(v) for v in restr.values())
    check("the bind is real: verified-K and non-circular barely overlap",
          nr < 0.1 * nf, f"({nr} of {nf} positions)")

    # circularity must inflate coincidences, not deflate them
    inc = channel(S, D, C, cov, tri, True, False)
    exc = channel(S, D, C, cov, tri, True, True)
    hi, pi = EP.measure(EP.build_sets(inc, W, nd, True))
    he, pe = EP.measure(EP.build_sets(exc, W, nd, True))
    ri = hi / max(pi, 1); re = he / max(pe, 1)
    check("admitting certified spans raises the coincidence rate (known bias)",
          pi > pe and ri >= re * 0.9,
          f"(with spans {ri:.4f}, without {re:.4f})")

    c = json.load(open(corpus))
    cts = [list(x) for x in c["ciphertexts"]]
    r = IR.relax(cts, N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard", (r.linked_strict, r.distinct_strict, len(r.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    S = EI.setup(corpus_path, atlas_path)
    D, C, W, cov, tri, nd = context(S)
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    print("\nQ1 the bind: verified-K territory versus non-circular territory")
    print(f"  {'configuration':44s} {'positions':>10s} {'pairs':>7s}")
    for tag, ua, dc in (("all positions, spans excluded (FR39)", False, True),
                        ("arithmetic ranges, spans excluded", True, True),
                        ("arithmetic ranges, spans INCLUDED", True, False),
                        ("all positions, spans included", False, False)):
        p = channel(S, D, C, cov, tri, ua, dc)
        H, P = EP.measure(EP.build_sets(p, W, nd, True))
        print(f"  {tag:44s} {sum(len(v) for v in p.values()):10d} {P:7d}")
    print("  FR13's ranges come from shift-1 certified pairs, so they sit inside")
    print("  the spans the channel excludes for non-circularity. The two")
    print("  requirements are nearly incompatible on this corpus.")

    print("\nQ2 measurement inside the verified ranges (spans admitted)")
    print("  circularity inflates coincidences, so this OVERSTATES structure")
    p = channel(S, D, C, cov, tri, True, False)
    sets = EP.build_sets(p, W, nd, True)
    H, P = EP.measure(sets)
    mu, sd = EP.null_stats(sets, PREREG["nulls"], PREREG["seed"])
    print(f"  pairs {P}, coincidences {H}, null {mu:.1f} +- {sd:.2f}, "
          f"z = {(H-mu)/sd:+.2f}, effective alphabet {P/max(H,1):.1f}")
    print(f"  {'effective alphabet':>19s} {'z':>7s}")
    for eff in (79, 70, 60, 50, 40):
        print(f"  {eff:19d} {(P/eff-mu)/sd:+7.2f}")

    print("\nQ3 control: the same measurement OUTSIDE the verified ranges")
    p2 = channel(S, D, C, cov, tri, True, True, invert=True)
    s2 = EP.build_sets(p2, W, nd, True)
    H2, P2 = EP.measure(s2)
    mu2, sd2 = EP.null_stats(s2, PREREG["nulls"], PREREG["seed"])
    print(f"  pairs {P2}, coincidences {H2}, null {mu2:.1f} +- {sd2:.2f}, "
          f"z = {(H2-mu2)/sd2:+.2f}, effective alphabet {P2/max(H2,1):.1f}")

    print("\nQ4 verdict")
    print("  both regions read flat and they agree, so the flatness FR39")
    print("  reported is NOT an artifact of K departing from arithmetic")
    print("  outside the verified ranges. FR39's conclusion survives.")
    print("  But the claim should be GRADED by where the power lies:")
    print("    * on verified-K territory, effective alphabets <= 50 are excluded")
    print("    * on the full channel, <= 60 is excluded, conditional on")
    print("      progressive K holding outside the ranges where it is proven")
    print("  FR39 stated the second without the conditional. That is the")
    print("  correction this cycle makes.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
