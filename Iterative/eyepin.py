#!/usr/bin/env python3
"""
eyepin -- structural cribs as q-relations, tested against the certified pin
component. Read-only; reuses the repo's own iso_relax/consensus machinery
unmodified; no isomorph is filtered or weighted.

THE IDEA. FR4's one-gauge deduction makes the whole corpus a single
monoalphabet in u-space (u = p + t under the progressive reading), so a
structural hypothesis about plaintext tokens becomes an EXACT mod-83
relation between q-values of specific glyphs -- language-free, not gated
by A-vs-B, and falsifiable against the pin component the repo has already
certified. Three hypotheses were formed before the pin table was seen and
are registered here:

  H1 BOUNDARY TOKEN (FR4 S5). If the same token D closes both opening
     frames (T3-frame slot 20 = glyph 47; T1-frame slot 24 = glyph 1),
     then u@24 - u@20 = (D+24)-(D+20):   q[1] - q[47] == 4  (mod 83).
  H3 DOUBLED HEADER. If the universal header (glyph 66 at t=1, glyph 5 at
     t=2) is one token P written twice:   q[5] - q[66] == 1  (mod 83).
  H2 INDICATOR BLOCK (FR4 S5). If the nine position-0 indicators are a
     structured label set of nine consecutive values (any order), the nine
     q-values fit a circular window of width 9 with all values distinct.

TEST MACHINERY. The consensus GF system over the certified tiers (strict
calibrated-anchor isomorphs + within-message exact repeats -- the pin
system, per iso_relax) is solved twice with glyph a pinned to two gauge
values; glyph b's forced difference from a exists iff its solution shifts
by exactly the gauge delta (the same gauge-invariance test iso_relax uses
for pin export, applied pairwise so sub-components disconnected from the
global reference still testify).

VERDICTS (pre-registered): SUPPORTED = forced difference exists and equals
the hypothesized value (coincidence price 1/83 per satisfied equation --
stated, not hidden); VIOLATED = forced difference exists and differs
(exact falsification); UNCHECKABLE = no forced difference (symbols
unlinked at the certified tiers). H2: with k >= 2 determined indicators,
VIOLATED if the forced values cannot sit in any width-9 circular window
with distinct residues; otherwise CONSISTENT with exact coincidence price
computed by enumeration; k < 2 is UNCHECKABLE.

Reproduction guard: the corpus run first re-derives the certified numbers
(strict linked=22, distinct=19, pins=16) and hard-fails on mismatch.
"""

import json, os, sys

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
    "H2_indicator_block": {"glyphs": sorted(INDICATORS.values()),
                            "window": 9},
    "certified_reproduction": {"linked": 22, "distinct": 19, "pins": 16},
    "gauge_delta": 7,
}

# ------------------------------------------------------------- machinery
def build_gf(cts, seed=0, base_len=13):
    """the PIN system of iso_relax: strict calibrated isomorphs + within-
    message exact repeats, cleaned by the repo's consensus."""
    anchor_rep = ce.calibrate_anchor(cts, base_len, seed=seed)
    strict = iso.find_isomorphs(cts, base_len, anchor_rep, different_only=False)
    wm = IR._within_message_pairs(cts, N, max(8, base_len - 3))
    hi_conf = list(strict) + wm
    gf, keep = ce.consensus_alphabet(cts, hi_conf, N, cm.per_msg_prog_rows,
                                     seed=seed)
    clean = [hi_conf[j] for j in keep] if keep else hi_conf
    return gf, clean, strict

def certified_domain(gf, delta=7):
    """iso_relax's soundness domain: symbols that co-shift with the global
    reference under the gauge test (its _determined_pins criterion, WITHOUT
    the injectivity filter). Returns (domain_values, ref). Disconnected
    subcomponents are excluded by construction -- on the audit plant such an
    island is contamination (internally consistent, truth-wrong), which is
    exactly why iso_relax certifies only the reference component."""
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

def forced_diff(gf, a, b, delta=7, _dom_cache={}):
    """forced (q[b]-q[a]) mod N within the CERTIFIED domain, else None."""
    key = id(gf)
    if key not in _dom_cache:
        _dom_cache[key] = certified_domain(gf, delta)
    dom, _ = _dom_cache[key]
    if a == b: return 0
    if a in dom and b in dom:
        return (dom[b] - dom[a]) % N
    return None

def annex_diff(gf, a, b, delta=7):
    """pairwise determination OUTSIDE the certified domain -- reported only
    as a labeled lower-confidence annex, never as a verdict, because the
    audit plant shows disconnected islands can be consensus-surviving
    contamination."""
    if a == b: return 0
    g1 = iso.GFSystem(N); g1.restore(gf.snapshot()); g1.add({a: 1}, 0)
    g2 = iso.GFSystem(N); g2.restore(gf.snapshot()); g2.add({a: 1}, delta)
    s1, s2 = g1.solve(), g2.solve()
    if b in s1 and b in s2 and (s2[b] - s1[b]) % N == delta % N:
        return s1[b] % N
    return None

def window_consistent(vals, width):
    """can the residue multiset sit in a circular window of the given
    width with all values distinct?"""
    if len(set(vals)) != len(vals): return False
    vs = sorted(set(vals))
    for start in vs:
        if all((v - start) % N < width for v in vs): return True
    return False

def window_price(k, width):
    """exact coincidence probability: k-1 iid uniform residues relative to
    an anchor land so that all k values (anchor at 0) are distinct and fit
    a width-`width` circular window. Enumerated exactly for small k."""
    if k < 2: return 1.0
    from itertools import product
    hits = 0
    for tup in product(range(N), repeat=k - 1):
        if window_consistent([0] + list(tup), width): hits += 1
    return hits / (N ** (k - 1))

# ------------------------------------------------------------- battery
def run_battery(gf):
    out = {}
    for name in ("H1_boundary", "H3_doubled_header"):
        a, b = PREREG[name]["pair"]; want = PREREG[name]["diff"]
        d = forced_diff(gf, a, b, PREREG["gauge_delta"])
        if d is None:
            ad = annex_diff(gf, a, b, PREREG["gauge_delta"])
            out[name] = dict(status="UNCHECKABLE", forced=None, want=want,
                             annex=ad)
        elif d == want % N:
            out[name] = dict(status="SUPPORTED", forced=d, want=want,
                             price=1.0 / N)
        else:
            out[name] = dict(status="VIOLATED", forced=d, want=want)
    glyphs = PREREG["H2_indicator_block"]["glyphs"]
    width = PREREG["H2_indicator_block"]["window"]
    rel = None
    for anchor in glyphs:
        vals = {}
        for g in glyphs:
            d = forced_diff(gf, anchor, g, PREREG["gauge_delta"])
            if d is not None: vals[g] = d
        if len(vals) >= 2: rel = (anchor, vals); break
    if rel is None:
        out["H2_indicator_block"] = dict(status="UNCHECKABLE", determined=0)
    else:
        anchor, vals = rel
        ok = window_consistent(list(vals.values()), width)
        out["H2_indicator_block"] = dict(
            status=("CONSISTENT" if ok else "VIOLATED"),
            determined=len(vals), anchor=anchor, values=vals,
            price=(window_price(len(vals), width) if ok else None))
    return out

# ------------------------------------------------------------- selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond

    print("selftest: forced-diff exactness, verdict labels, window logic")
    cts, q_truth, bases = IR._overdetermined_plant(seed=3)
    # SOUND configuration: the audited plant invocation (base_len=10, the
    # calibration matched to the planted word)
    gf, clean, strict = build_gf(cts, seed=0, base_len=10)
    sol = gf.solve()
    comp = sorted(v for v in sol if v < N)
    check("plant component nonempty", len(comp) >= 5, f"({len(comp)} symbols)")

    # certified domain: exact vs ground truth
    import itertools
    dom, ref = certified_domain(gf)
    check("certified domain nonempty", len(dom) >= 2, f"({len(dom)} symbols, ref={ref})")
    tested = exact = 0
    for a, b in itertools.combinations(sorted(dom)[:8], 2):
        d = forced_diff(gf, a, b)
        tested += 1
        exact += (d == (q_truth[b] - q_truth[a]) % N)
    check("certified diffs exact vs ground truth", tested >= 1 and exact == tested,
          f"({exact}/{tested})")

    # the contaminated island (annex-determined, truth-wrong) is EXCLUDED
    island = []
    for a, b in itertools.combinations([s for s in comp if s not in dom][:10], 2):
        ad = annex_diff(gf, a, b)
        if ad is not None and ad != (q_truth[b] - q_truth[a]) % N:
            island.append((a, b, ad))
    check("contaminated island exists in annex and is excluded from certified",
          len(island) >= 1 and all(a not in dom and b not in dom for a, b, _ in island),
          f"({len(island)} truth-wrong annex pairs, all outside certified domain)")

    # NEGATIVE EXHIBIT: miscalibrated tier (base_len=13 on this plant)
    # contaminates even the reference component -- calibration, not the
    # domain filter, is the first line of soundness; the corpus run's
    # reproduction guard pins the certified corpus calibration
    gf_bad, _, _ = build_gf(cts, seed=0, base_len=13)
    dom_bad, ref_bad = certified_domain(gf_bad)
    wrong = 0
    for a, b in itertools.combinations(sorted(dom_bad), 2):
        d = (dom_bad[b] - dom_bad[a]) % N
        if d != (q_truth[b] - q_truth[a]) % N: wrong += 1
    check("miscalibrated tier demonstrably unsound (negative exhibit)",
          len(dom_bad) >= 2 and wrong >= 1,
          f"({wrong} truth-wrong certified pairs at base_len=13)")

    # None for pairs crossing out of everything
    linked = set(comp)
    outside = [s for s in range(N) if s not in linked][:3]
    nones = sum(1 for o in outside if forced_diff(gf, ref, o) is None)
    check("unlinked pairs return None", nones == len(outside),
          f"({nones}/{len(outside)})")

    # verdict labels via a temporary battery aimed at plant truth
    ds = sorted(dom)
    a, b = ds[0], ds[1]
    truth = (q_truth[b] - q_truth[a]) % N
    saved = dict(PREREG["H1_boundary"])
    PREREG["H1_boundary"] = {"pair": [a, b], "diff": truth}
    r = run_battery(gf)["H1_boundary"]
    good_sup = r["status"] == "SUPPORTED"
    PREREG["H1_boundary"] = {"pair": [a, b], "diff": (truth + 1) % N}
    r = run_battery(gf)["H1_boundary"]
    good_vio = r["status"] == "VIOLATED"
    PREREG["H1_boundary"] = saved
    check("SUPPORTED / VIOLATED labels correct", good_sup and good_vio)

    # window logic unit tests
    check("window: {0,3,8} fits", window_consistent([0, 3, 8], 9))
    check("window: {0,3,9} rejected", not window_consistent([0, 3, 9], 9))
    check("window: wraparound {80,1,3} fits", window_consistent([80, 1, 3], 9))
    check("window: duplicate rejected", not window_consistent([0, 4, 4], 9))
    p2 = window_price(2, 9)
    check("window price k=2 exact", abs(p2 - 16 / 83) < 1e-12, f"({p2:.4f})")

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")
    return ok

# ------------------------------------------------------------- corpus
def corpus_run(corpus_path):
    c = json.load(open(corpus_path))
    cts = [list(x) for x in c["ciphertexts"]]
    print("\npre-registered battery:", json.dumps(
        {k: v for k, v in PREREG.items() if k.startswith("H")}))

    # reproduction guard
    r = IR.relax(cts, N, seed=0)
    want = PREREG["certified_reproduction"]
    if (r.linked_strict, r.distinct_strict, len(r.pins)) != \
       (want["linked"], want["distinct"], want["pins"]):
        fail(f"certified reproduction mismatch: got "
             f"{(r.linked_strict, r.distinct_strict, len(r.pins))}")
    print(f"reproduction guard: linked={r.linked_strict} "
          f"distinct={r.distinct_strict} pins={len(r.pins)}  [MATCHES CERTIFIED]")

    gf, clean, strict = build_gf(cts, seed=0)
    sol = gf.solve()
    comp = sorted(v for v in sol if v < N)
    print(f"pin-system component: {len(comp)} symbols in consensus solution")

    print("\nhypothesis glyph status:")
    hyp_glyphs = sorted({47, 1, 66, 5} | set(INDICATORS.values()))
    for g in hyp_glyphs:
        print(f"  glyph {g:2d}: {'in consensus solution' if g in sol else 'outside pin system'}")

    print("\nregistered battery results:")
    out = run_battery(gf)
    for name, res in out.items():
        print(f"  {name}: {res}")

    # pin-grade template skeleton (the constructive artifact)
    from collections import Counter
    dom, ref = certified_domain(gf)
    cnt = Counter(dom.values())
    png = {g: v for g, v in dom.items() if cnt[v] == 1}
    tainted = sorted(g for g in dom if cnt[dom[g]] > 1)
    print(f"\npin-grade symbols ({len(png)}), collision-tainted excluded {tainted}")
    labels = c["message_labels"]
    Mm = dict(zip(labels, c["ciphertexts"]))
    tmplA = {t: Mm["East 4"][t] for t in range(3, 21)}
    tmplB = {t: Mm["East 1"][t] for t in range(3, 25)}
    print("pin-grade template skeleton (frame, t, glyph, q_ref, p_gauge=q-t):")
    for frame, tmpl in (("A", tmplA), ("B", tmplB)):
        for t, g in sorted(tmpl.items()):
            if g in png:
                print(f"  frame {frame} t={t:2d} glyph {g:2d} q={png[g]:2d} "
                      f"p_gauge={(png[g]-t)%N:2d}")

    print("\npost-hoc descriptive (not a registered test): pins place "
          "q[49]-q[48] = "
          f"{(r.pins[49]-r.pins[48]) % N if 48 in r.pins and 49 in r.pins else 'n/a'}"
          " -- the two opening frames' first tokens differ by that amount "
          "in plaintext value under the one gauge.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus)
