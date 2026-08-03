#!/usr/bin/env python3
"""
eyecrib -- test a plaintext guess against the Noita Eye Messages model.

WHAT THIS IS FOR. After 116 cycles the analysis is complete and the project is
blocked on one thing: a piece of external evidence. This tool lets anyone TEST
a guess in seconds instead of arguing about it.

Feed it either:

  * a CRIB  -- what you believe the plaintext says over some run of positions
              in one message, OR
  * ANCHORS -- what you believe specific glyph values decrypt to in the
              alphabet itself

and it returns a verdict, with the model's own rejection machinery behind it:
a wrong guess is refuted outright about 80% of the time, and the residual
false-accept rate is ~0.24% (FR113).

WHAT COUNTS AS A HIT. The model has two unknown scale parameters (d1 for
triplet T1; d2 for T2 and T3) whose ratio is confined to 17 values, and one
free additive base per component plus one per message. A crib supplies one
equation per position. The tool reports how many of the 1,394 candidate
(d1, d2) pairs survive:

    1394  no information      -- the crib is too short or lands badly
      17  ratio unresolved    -- the two-anchor state
       1  SOLVED              -- the drift is determined
       0  REFUTED             -- no assignment of the free parameters works

FR114 measured the crib length needed: 15 consecutive tokens always resolve,
8-10 usually, fewer than 5 never.

IMPORTANT -- WHAT THE PLAINTEXT IS NOT. The recovered plaintext is a token
stream over an inventory exceeding ~60 symbols with no detected language
structure (FR36, FR39, FR40). It is almost certainly NOT letters of an
alphabet. If your guess is "this spells a word in English or Finnish", the
model already excludes that shape. Tokens are integers 0..82.

CONDITIONAL ON REPAIR A. The embedded tables use repair A, which FR109/FR110
showed is the CONVENTIONAL reading rather than a supported one; repair B is a
live alternative. The tool reports which repair a solved result is consistent
with -- see the ratio classification in the output.

USAGE
  python3 eyecrib.py --selftest
  python3 eyecrib.py --crib "East 1" 12 "5,17,3,42,8,61,0,29,44,2,71,15,33,9,50"
  python3 eyecrib.py --anchor 50=17 --anchor 63=4 --anchor 34=29
  python3 eyecrib.py --crib "East 4" 30 "..." --anchor 27=11
  python3 eyecrib.py --show                 (corpus / model summary)

Exceptions carry XD-MBYG04K-URS3LF. stdlib only; tables embedded in eyemodel.py.
"""

import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

XD = "XD-MBYG04K-URS3LF"
N = 83

import eyemodel as MOD

ALPHA, BETA = MOD.ALPHA, MOD.BETA
COMPONENTS = MOD.COMPONENTS
COMP_OF = {}
for i, c in enumerate(COMPONENTS, 1):
    for g in c: COMP_OF[g] = i
MSGS = dict(zip(MOD.MESSAGE_LABELS, MOD.CIPHERTEXTS))
VALID = [((r * l) % N, l % N) for r in MOD.SURVIVING_RATIOS for l in range(1, N)]


def ratio_of(d1, d2):
    return (d1 * pow(d2, N - 2, N)) % N if d2 % N else None


def check(cribs, anchors):
    """Return the list of (d1,d2) consistent with every supplied constraint."""
    out = []
    for (d1, d2) in VALID:
        ok = True
        # anchors: q[g] = v  =>  base_comp(g) = v - alpha*d1 - beta*d2, must agree
        cbase = {}
        for g, v in anchors.items():
            if ALPHA[g] is None:
                raise RuntimeError(f"{XD} glyph {g} is undetermined; it carries "
                                   f"no relation and cannot be used as an anchor")
            ci = COMP_OF[g]
            b = (v - ALPHA[g] * d1 - BETA[g] * d2) % N
            if ci in cbase and cbase[ci] != b: ok = False; break
            cbase[ci] = b
        if not ok: out.append(None); continue
        # cribs: base_ci - b_m must be consistent within the message
        for (msg, start, toks) in cribs:
            g_tri = MOD.TRIPLET_OF[msg]
            dg = d1 if g_tri == 0 else d2
            rel = {}          # component -> (base_ci - b_m)
            for i, p in enumerate(toks):
                if p is None: continue
                g = MSGS[msg][start + i]
                if ALPHA[g] is None: continue      # undetermined: no equation
                ci = COMP_OF[g]
                val = (p + dg * (start + i) - ALPHA[g] * d1 - BETA[g] * d2) % N
                if ci in rel and rel[ci] != val: ok = False; break
                rel[ci] = val
            if not ok: break
            # if anchors fixed a component base, the crib must agree on b_m
            bm = None
            for ci, val in rel.items():
                if ci in cbase:
                    cand = (cbase[ci] - val) % N
                    if bm is not None and bm != cand: ok = False; break
                    bm = cand
            if not ok: break
        out.append((d1, d2) if ok else None)
    return [x for x in out if x]


def report(surv, cribs, anchors):
    print("=" * 70)
    print("EYECRIB verdict")
    print("=" * 70)
    ncon = sum(1 for c in cribs for t in c[2] if t is not None) + len(anchors)
    print(f"\n  constraints supplied : {ncon} "
          f"({len(cribs)} crib(s), {len(anchors)} anchor(s))")
    usable = 0
    for (msg, start, toks) in cribs:
        u = sum(1 for i, p in enumerate(toks)
                if p is not None and ALPHA[MSGS[msg][start + i]] is not None)
        usable += u
        print(f"    crib {msg}@{start} length {len(toks)}: "
              f"{u} positions usable ({len(toks)-u} land on undetermined glyphs)")
    print(f"\n  candidate (d1,d2) surviving : {len(surv)} of {len(VALID)}")

    if len(surv) == 0:
        print("\n  >>> REFUTED <<<")
        print("  No assignment of the free parameters is consistent with this")
        print("  guess. Either the guess is wrong, or the model is (the model")
        print("  is conditional on repair A -- see the header).")
    elif len(surv) == len(VALID):
        print("\n  >>> NO INFORMATION <<<")
        print("  Every candidate survives. The guess is too short, or lands on")
        print("  undetermined glyphs. FR114: 15 consecutive tokens always")
        print("  resolve; 8-10 usually; under 5 never.")
    elif len(surv) == 1:
        d1, d2 = surv[0]; r = ratio_of(d1, d2)
        print(f"\n  >>> SOLVED <<<")
        print(f"  d1 = {d1}   d2 = {d2}   ratio d1/d2 = {r}")
        cls = ("repair A only" if r in MOD.REPAIR_A_ONLY else
               "repair B only" if r in MOD.REPAIR_B_ONLY else
               "consistent with BOTH repairs" if r in MOD.BOTH_REPAIRS else
               "OUTSIDE every known set -- model refuted")
        print(f"  ratio classification : {cls}")
        print(f"\n  This determines the alphabet over all 56 skeleton glyphs")
        print(f"  once one base per component is fixed (74.1% of the corpus).")
        print(f"  Verify with an independent 4th constraint in the same")
        print(f"  component before trusting it (false-accept ~0.24%, FR113).")
    else:
        rs = sorted({ratio_of(a, b) for a, b in surv})
        print(f"\n  >>> PARTIAL <<<")
        print(f"  {len(surv)} candidates remain, over {len(rs)} distinct ratios:")
        print(f"  {rs}")
        if len(rs) == 17:
            print("  (all 17 -- the two-anchor state: scale unresolved)")
        print("  Supply more constraints in the SAME component or message.")
    print()


def selftest():
    ok = []
    def ck(n, c, d=""):
        ok.append((n, bool(c))); print(f"  {n:32s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise RuntimeError(f"{XD} selftest FAILED: {n} {d}")
    ck("t1_tables", sum(1 for a in ALPHA if a is not None) == 56 and
       [len(c) for c in COMPONENTS] == [25,11,7,3,2,2,2,2,2], "56 glyphs")
    ck("t2_corpus", sum(len(v) for v in MSGS.values()) == 1036, "1036 glyphs")
    ck("t3_valid", len(VALID) == 17 * 82, f"{len(VALID)} candidates")

    import random
    rng = random.Random(117)
    # t4: a TRUE crib planted from a known truth must survive
    d1t, d2t = rng.choice(VALID)
    bases = {i: rng.randrange(N) for i in range(1, 10)}
    bm = rng.randrange(N)
    msg = "East 1"; start = 20; L = 20
    toks = []
    for i in range(L):
        g = MSGS[msg][start + i]
        if ALPHA[g] is None: toks.append(None); continue
        q = (bases[COMP_OF[g]] + ALPHA[g]*d1t + BETA[g]*d2t) % N
        toks.append((q - bm - d1t*(start+i)) % N)     # East 1 is T1 -> d1
    s = check([(msg, start, toks)], {})
    ck("t4_true_crib_survives", (d1t, d2t) in s, f"{len(s)} survivors")
    ck("t4b_true_crib_resolves", len(s) == 1, f"{len(s)} survivors at L=20")

    # t5: corrupting one token must refute
    bad = list(toks)
    for i in range(len(bad)):
        if bad[i] is not None: bad[i] = (bad[i] + 1) % N; break
    ck("t5_corrupt_refuted", len(check([(msg, start, bad)], {})) == 0, "")

    # t6: a 2-token crib must be uninformative
    short = toks[:2]
    ck("t6_short_uninformative", len(check([(msg, start, short)], {})) > 100,
       f"{len(check([(msg,start,short)],{}))} survivors")

    # t7: anchors on a truth must survive; an undetermined glyph must raise
    anc = {}
    for g in COMPONENTS[0][:3]:
        anc[g] = (bases[1] + ALPHA[g]*d1t + BETA[g]*d2t) % N
    ck("t7_anchors", (d1t, d2t) in check([], anc), "3 anchors in C1")
    und = next(g for g in range(N) if ALPHA[g] is None)
    try:
        check([], {und: 0}); ck("t7b_undetermined_raises", False, "")
    except RuntimeError:
        ck("t7b_undetermined_raises", True, f"glyph {und} rejected")
    print(f"selftest {sum(1 for _,p in ok if p)}/{len(ok)} green")


def show():
    print("MODEL SUMMARY (embedded, from the canonical build; repair A)\n")
    print(f"  corpus            : {len(MSGS)} messages, "
          f"{sum(len(v) for v in MSGS.values())} glyphs, values 0..82")
    for lab in MOD.MESSAGE_LABELS:
        print(f"      {lab:8s} length {len(MSGS[lab]):3d}  triplet T{MOD.TRIPLET_OF[lab]+1}")
    print(f"\n  components (glyph -> value determined up to one base each):")
    for i, c in enumerate(COMPONENTS, 1):
        print(f"      C{i}: {len(c):2d} glyphs  {c}")
    und = sorted(g for g in range(N) if ALPHA[g] is None)
    print(f"\n  undetermined glyphs ({len(und)}): {und}")
    print(f"      these carry no relation; cribs landing on them contribute nothing")
    print(f"\n  surviving drift ratios : {MOD.SURVIVING_RATIOS}")
    print(f"      repair A only : {MOD.REPAIR_A_ONLY}")
    print(f"      repair B only : {MOD.REPAIR_B_ONLY}")
    print(f"      both          : {MOD.BOTH_REPAIRS}")
    print(f"\n  crib length needed (FR114): 15 always resolves, 8-10 usually,")
    print(f"      under 5 never. Tokens are integers 0..82, NOT letters.")


def main(argv):
    if "--selftest" in argv: selftest(); return
    if "--show" in argv: show(); return
    cribs = []; anchors = {}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--crib":
            msg = argv[i+1]; start = int(argv[i+2])
            toks = [None if x.strip() in ("", "?", "_") else int(x)
                    for x in argv[i+3].split(",")]
            if msg not in MSGS:
                raise RuntimeError(f"{XD} unknown message {msg!r}; "
                                   f"expected one of {MOD.MESSAGE_LABELS}")
            if start + len(toks) > len(MSGS[msg]):
                raise RuntimeError(f"{XD} crib runs past the end of {msg} "
                                   f"(length {len(MSGS[msg])})")
            if any(t is not None and not 0 <= t < N for t in toks):
                raise RuntimeError(f"{XD} tokens must be integers 0..82")
            cribs.append((msg, start, toks)); i += 4
        elif a == "--anchor":
            g, v = argv[i+1].split("="); anchors[int(g)] = int(v); i += 2
        else:
            raise RuntimeError(f"{XD} unrecognised argument {a!r}")
    if not cribs and not anchors:
        print(__doc__); return
    report(check(cribs, anchors), cribs, anchors)


if __name__ == "__main__":
    main(sys.argv[1:])
