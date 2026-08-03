#!/usr/bin/env python3
"""
eyereach -- atlas-fed evidence expansion for the certified pin component,
with cross-validation, pin-grade filtering, and the FR5 registered battery
re-tested under the expanded tier. Read-only; the repo's consensus and
gauge machinery are reused unmodified; atlas values are re-verified against
the corpus before any constraint is built.

WHY THIS IS SOUND NEW EVIDENCE. iso_relax's strict tier scans at
base_len=13, so the community-certified atlas classes of length 8-12
(#M L=9 with 6 instances, #M- L=8 with 7, #3 L=12 with 3) never feed the
consensus at all -- despite being the most replicated structures in the
corpus. This module builds IsoPair constraints directly from the curated
atlas (all 13 classes, every instance pair), pushes them through the SAME
consensus gate, certified-domain test, and collision filter as FR5, and
cross-validates: symbols determined by BOTH the strict scan and the atlas
feed must agree on every pairwise difference, or the run aborts loudly.

TIERS (pre-committed before any corpus result was seen):
  S    strict scan + per-message rows      -- the FR5 baseline (guard: 22/19/16)
  A    atlas pairs + per-message rows
  A+S  combined     + per-message rows     -- PRIMARY tier for the battery
  P    combined     + pure-progressive rows -- one-gauge tier (FR4-conditional;
       the repo's own pure_prog_rows docstring notes the literal universal
       header forces this mode), reported separately and labeled conditional.

The FR5 battery (H1 boundary q[1]-q[47]=4; H3 doubled header q[5]-q[66]=1;
H2 indicator width-9 window) carries over with identical verdict rules; the
only new pre-commitment is the tier choice above.
"""

import json, os, sys
from collections import Counter
from itertools import combinations, product

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
EYEFORWARD = os.environ.get("EYEFORWARD_DIR",
    os.path.join(HERE, "..", "Eyes-main", "eyeforward"))
sys.path.insert(0, EYEFORWARD)

import iso_relax as IR          # noqa: E402
import isomorph as iso          # noqa: E402
import chain_models as cm       # noqa: E402
import chain_extract as ce      # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

INDICATORS = {"East 1": 50, "West 1": 80, "East 2": 36, "West 2": 76,
              "East 3": 63, "West 3": 34, "East 4": 27, "West 4": 77,
              "East 5": 33}

PREREG = {
    "H1_boundary": {"pair": [47, 1], "diff": 4},
    "H3_doubled_header": {"pair": [66, 5], "diff": 1},
    "H2_indicator_block": {"glyphs": sorted(INDICATORS.values()), "window": 9},
    "primary_tier": "A+S (per-message rows)",
    "baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
    "gauge_delta": 7,
}

# ------------------------------------------------------------- atlas pairs
def atlas_pairs(atlas_path, cts, labels):
    """IsoPair list from every instance pair of every atlas class, values
    verified against the corpus; hard-fail on any mismatch."""
    a = json.load(open(atlas_path))
    idx = {lab: i for i, lab in enumerate(labels)}
    pairs, classes = [], []
    for cls in a["classes"]:
        L = cls["length"]
        inst = []
        for it in cls["instances"]:
            mi = idx[it["message"]]
            if list(cts[mi][it["start"]:it["start"] + L]) != list(it["values"]):
                fail(f"atlas values mismatch corpus at {cls['id']} "
                     f"{it['message']}@{it['start']}")
            inst.append((mi, it["start"]))
        for (m1, p1), (m2, p2) in combinations(inst, 2):
            exact = cts[m1][p1:p1 + L] == cts[m2][p2:p2 + L]
            pairs.append(iso.IsoPair(m1=m1, p1=p1, m2=m2, p2=p2,
                                     length=L, exact=exact))
        classes.append((cls["id"], L, len(inst)))
    return pairs, classes

# ------------------------------------------------------------- tiers
def consensus(cts, pairs, rows_fn, seed=0):
    gf, keep = ce.consensus_alphabet(cts, pairs, N, rows_fn, seed=seed)
    return gf, (len(keep) if keep else len(pairs)), len(pairs)

def certified_domain(gf, delta=7):
    base = gf.solve()
    sym = sorted(v for v in base if v < N)
    if len(sym) < 2: return {}, None
    ref = sym[0]
    g1 = iso.GFSystem(N); g1.restore(gf.snapshot()); g1.add({ref: 1}, 0)
    g2 = iso.GFSystem(N); g2.restore(gf.snapshot()); g2.add({ref: 1}, delta)
    s1, s2 = g1.solve(), g2.solve()
    dom = {x: s1[x] % N for x in sym
           if x in s1 and x in s2 and (s2[x] - s1[x]) % N == delta % N}
    return dom, ref

def pin_grade(dom):
    cnt = Counter(dom.values())
    return {g: v for g, v in dom.items() if cnt[v] == 1}, \
           sorted(g for g in dom if cnt[dom[g]] > 1)

def cross_validate(domA, domB):
    """symbols in both domains must agree on every pairwise difference."""
    shared = sorted(set(domA) & set(domB))
    bad = []
    for a, b in combinations(shared, 2):
        if (domA[b] - domA[a]) % N != (domB[b] - domB[a]) % N:
            bad.append((a, b))
    return shared, bad

# ------------------------------------------------------------- battery
def window_consistent(vals, width):
    if len(set(vals)) != len(vals): return False
    vs = sorted(set(vals))
    return any(all((v - s) % N < width for v in vs) for s in vs)

def window_price(k, width):
    if k < 2: return 1.0
    hits = 0
    for tup in product(range(N), repeat=k - 1):
        if window_consistent([0] + list(tup), width): hits += 1
    return hits / (N ** (k - 1))

def run_battery(dom, png):
    """battery against a certified domain; pin-grade set used for taint
    labeling. Verdict rules identical to FR5."""
    out = {}
    for name in ("H1_boundary", "H3_doubled_header"):
        a, b = PREREG[name]["pair"]; want = PREREG[name]["diff"]
        if a in dom and b in dom:
            d = (dom[b] - dom[a]) % N
            taint = [g for g in (a, b) if g not in png]
            status = "SUPPORTED" if d == want % N else "VIOLATED"
            out[name] = dict(status=status, forced=d, want=want,
                             taint=taint, price=(1.0 / N if not taint else None))
        else:
            out[name] = dict(status="UNCHECKABLE",
                             missing=[g for g in (a, b) if g not in dom])
    glyphs = PREREG["H2_indicator_block"]["glyphs"]
    width = PREREG["H2_indicator_block"]["window"]
    linked = {g: dom[g] for g in glyphs if g in dom}
    if len(linked) < 2:
        out["H2_indicator_block"] = dict(status="UNCHECKABLE",
                                         determined=len(linked))
    else:
        ok = window_consistent(list(linked.values()), width)
        taint = [g for g in linked if g not in png]
        out["H2_indicator_block"] = dict(
            status=("CONSISTENT" if ok else "VIOLATED"),
            determined=len(linked), values=linked, taint=taint,
            price=(window_price(len(linked), width) if ok else None))
    return out

# ------------------------------------------------------------- plants
def plant_with_atlas(rng_seed=11, short_extra=True):
    """progressive plant mirroring the REAL atlas geometry: a long class
    (L=14, four u-repeats, reachable by the sound strict scan) and a short
    class (L=9) that is the long passage's plaintext sub-window [3..12) --
    three EMBEDDED instances sharing cells with the long spans (the #M-in-#1
    nesting) plus one STANDALONE instance in a fourth message (the solo
    occurrence), whose ciphertext symbols are new: the reach only the atlas
    feed can certify. Returns cts, q_truth, synthetic atlas, standalone
    symbol list."""
    import numpy as np
    rng = np.random.default_rng(rng_seed)
    C = list(rng.permutation(N)); q = [0] * N
    for pos, s in enumerate(C): q[s] = pos
    T, n_msgs, base = 100, 4, 20
    plain = [[int(x) for x in rng.integers(0, N, T)] for _ in range(n_msgs)]
    longp = [int(x) for x in rng.integers(0, N, 14)]
    # four u-repeats, three landing inside the sub-window [3..12)
    longp[8] = (longp[4] + 4 - 8) % N
    longp[11] = (longp[5] + 5 - 11) % N
    longp[10] = (longp[3] + 3 - 10) % N
    longp[13] = (longp[0] + 0 - 13) % N
    # cross-context collisions (the determination engine): same symbol at
    # different offsets across instances cancels pair constants
    longp[12] = (longp[2] + 10) % N   # u(m0,22)=u(m1,32): m0-off12 == m1-off2
    longp[1] = (longp[8] + 34) % N    # u(m0,11)=u(m3,45): m0-off1 == standalone-off5
    longp[6] = (longp[3] + 22) % N    # u(m1,36)=u(m2,58): m1-off6 == m2-off3
    subp = longp[3:12]
    long_spots = [(0, 10), (1, 30), (2, 55)]
    for m, p0 in long_spots: plain[m][p0:p0 + 14] = longp
    if short_extra:
        plain[3][40:49] = subp                      # standalone occurrence
    cts = [[int(C[(plain[m][t] + base + t) % N]) for t in range(T)]
           for m in range(n_msgs)]
    classes = [{"id": "#L", "length": 14, "pattern": "?" * 14,
                "instances": [{"message": f"m{m}", "start": p0,
                               "values": cts[m][p0:p0 + 14]}
                              for m, p0 in long_spots]}]
    if short_extra:
        short_spots = [(m, p0 + 3) for m, p0 in long_spots] + [(3, 40)]
        classes.append({"id": "#S", "length": 9, "pattern": "?" * 9,
                        "instances": [{"message": f"m{m}", "start": p0,
                                       "values": cts[m][p0:p0 + 9]}
                                      for m, p0 in short_spots]})
    short_syms = sorted({cts[3][40 + i] for i in range(9)}) if short_extra else []
    return cts, q, classes, short_syms

def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond

    print("selftest: atlas-path equivalence, guards, cross-validation, battery")
    import json as _json, tempfile
    from itertools import combinations as _comb

    # the repo's audited overdetermined plant + its audited sound scan config
    cts, q_truth, bases = IR._overdetermined_plant(seed=3)
    labels = [f"m{i}" for i in range(len(cts))]
    anchor = ce.calibrate_anchor(cts, 10, seed=0)
    scanp = iso.find_isomorphs(cts, 10, anchor, different_only=False)
    check("scan finds pairs on audit plant", len(scanp) >= 2, f"({len(scanp)})")

    # wrap scan pairs as 2-instance atlas classes; my path must reproduce
    # the direct-feed result exactly (equivalence), and be exact vs truth
    classes = []
    for k, pr in enumerate(scanp):
        classes.append({"id": f"#{k}", "length": pr.length, "pattern": "?" * pr.length,
                        "instances": [
                            {"message": labels[pr.m1], "start": pr.p1,
                             "values": [int(x) for x in cts[pr.m1][pr.p1:pr.p1 + pr.length]]},
                            {"message": labels[pr.m2], "start": pr.p2,
                             "values": [int(x) for x in cts[pr.m2][pr.p2:pr.p2 + pr.length]]}]})
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        _json.dump({"classes": classes}, f); apath = f.name
    apairs, _cl = atlas_pairs(apath, cts, labels)
    gfA, keptA, totA = consensus(cts, apairs, cm.per_msg_prog_rows)
    gfD, keptD, totD = consensus(cts, scanp, cm.per_msg_prog_rows)
    domA, refA = certified_domain(gfA)
    domD, refD = certified_domain(gfD)
    check("atlas path == direct feed (equivalence)", domA == domD,
          f"(|A|={len(domA)}, |D|={len(domD)})")
    exact = all((domA[b] - domA[a]) % N == (q_truth[b] - q_truth[a]) % N
                for a, b in _comb(sorted(domA), 2))
    check("atlas-fed certified diffs exact vs truth", len(domA) >= 2 and exact,
          f"({len(domA)} symbols)")

    # monotone reach: feeding a strict subset of classes certifies no more
    sub_classes = classes[:max(1, len(classes) // 2)]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        _json.dump({"classes": sub_classes}, f); spath = f.name
    spairs, _ = atlas_pairs(spath, cts, labels)
    gfSub, _, _ = consensus(cts, spairs, cm.per_msg_prog_rows)
    domSub, _ = certified_domain(gfSub)
    check("subset feed certifies a subset (monotone reach logic)",
          set(domSub) <= set(domA), f"(sub={len(domSub)} of {len(domA)})")

    # cross-validation on overlapping sound tiers
    shared, bad = cross_validate(domSub, domA)
    check("cross-validation agrees on overlap", len(bad) == 0,
          f"(shared={len(shared)})")

    # corrupted atlas values hard-fail
    classes2 = _json.loads(_json.dumps(classes))
    classes2[0]["instances"][0]["values"][0] = \
        (classes2[0]["instances"][0]["values"][0] + 1) % N
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        _json.dump({"classes": classes2}, f); bpath = f.name
    try:
        atlas_pairs(bpath, cts, labels); guard = False
    except RuntimeError as e:
        guard = str(e).startswith(ERR)
    check("corrupted atlas values hard-fail with prefix", guard)

    # pure rows on the pure-progressive plant: no smaller, still exact
    gfP, _, _ = consensus(cts, apairs, cm.pure_prog_rows)
    domP, _ = certified_domain(gfP)
    exactP = all((domP[b] - domP[a]) % N == (q_truth[b] - q_truth[a]) % N
                 for a, b in _comb(sorted(domP), 2))
    check("pure-rows tier exact and no smaller", exactP and len(domP) >= len(domA),
          f"(P={len(domP)}, A={len(domA)})")

    # battery labels
    ds = sorted(domA); a, b = ds[0], ds[1]
    truth = (domA[b] - domA[a]) % N
    png, _t = pin_grade(domA)
    saved = dict(PREREG["H1_boundary"])
    PREREG["H1_boundary"] = {"pair": [a, b], "diff": truth}
    r1 = run_battery(domA, png)["H1_boundary"]["status"]
    PREREG["H1_boundary"] = {"pair": [a, b], "diff": (truth + 1) % N}
    r2 = run_battery(domA, png)["H1_boundary"]["status"]
    PREREG["H1_boundary"] = saved
    check("battery SUPPORTED/VIOLATED labels", r1 == "SUPPORTED" and r2 == "VIOLATED")

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")
    return ok

# ------------------------------------------------------------- corpus
def corpus_run(corpus_path, atlas_path):
    c = json.load(open(corpus_path))
    cts = [list(x) for x in c["ciphertexts"]]
    labels = c["message_labels"]
    print("\npre-registered:", json.dumps({k: v for k, v in PREREG.items()
                                           if k.startswith(("H", "primary"))}))

    # baseline guard
    r = IR.relax(cts, N, seed=0)
    bg = PREREG["baseline_guard"]
    if (r.linked_strict, r.distinct_strict, len(r.pins)) != \
       (bg["linked"], bg["distinct"], bg["pins"]):
        fail("baseline reproduction mismatch")
    print(f"baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    anchor = ce.calibrate_anchor(cts, 13, seed=0)
    strictp = iso.find_isomorphs(cts, 13, anchor, different_only=False)
    apairs, aclasses = atlas_pairs(atlas_path, cts, labels)
    print(f"atlas feed: {len(apairs)} instance pairs from "
          f"{len(aclasses)} classes: {aclasses}")

    tiers = {}
    for name, pairs, rows in (
        ("S", strictp, cm.per_msg_prog_rows),
        ("A", apairs, cm.per_msg_prog_rows),
        ("A+S", apairs + strictp, cm.per_msg_prog_rows),
        ("P", apairs + strictp, cm.pure_prog_rows)):
        gf, kept, tot = consensus(cts, pairs, rows)
        dom, ref = certified_domain(gf)
        png, taint = pin_grade(dom)
        tiers[name] = dict(dom=dom, png=png, taint=taint, kept=kept, tot=tot)
        print(f"tier {name:3s}: pairs kept {kept}/{tot}  certified={len(dom)} "
              f"pin-grade={len(png)} tainted={taint}")

    shared, bad = cross_validate(tiers["S"]["dom"], tiers["A"]["dom"])
    print(f"\ncross-validation S vs A: {len(shared)} shared symbols, "
          f"{len(bad)} disagreements")
    if bad: fail(f"strict/atlas cross-validation disagreements: {bad}")

    prim = tiers["A+S"]
    print(f"\nhypothesis glyph status under PRIMARY tier (A+S):")
    hyp = sorted({47, 1, 66, 5} | set(INDICATORS.values()))
    for g in hyp:
        st = ("pin-grade" if g in prim["png"] else
              "certified-tainted" if g in prim["dom"] else "unlinked")
        print(f"  glyph {g:2d}: {st}")

    print(f"\nREGISTERED BATTERY under PRIMARY tier (A+S):")
    for name, res in run_battery(prim["dom"], prim["png"]).items():
        print(f"  {name}: {res}")

    print(f"\nbattery under one-gauge tier P (FR4-conditional, labeled):")
    for name, res in run_battery(tiers["P"]["dom"], tiers["P"]["png"]).items():
        print(f"  {name}: {res}")

    # extended pin-grade template skeleton under the primary tier
    Mm = dict(zip(labels, c["ciphertexts"]))
    tmplA = {t: Mm["East 4"][t] for t in range(3, 21)}
    tmplB = {t: Mm["East 1"][t] for t in range(3, 25)}
    print("\npin-grade template skeleton under PRIMARY tier:")
    for frame, tmpl in (("A", tmplA), ("B", tmplB)):
        for t, g in sorted(tmpl.items()):
            if g in prim["png"]:
                print(f"  frame {frame} t={t:2d} glyph {g:2d} q={prim['png'][g]:2d} "
                      f"p_gauge={(prim['png'][g] - t) % N:2d}")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
