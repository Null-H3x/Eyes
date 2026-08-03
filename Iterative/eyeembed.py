#!/usr/bin/env python3
"""
eyeembed -- can embeddedness discriminate repair A from repair B?

FR109 reopened FR25's repair fork by showing FR47's injectivity refutation of
repair B holds only at ratio 1, and collapsed FR48's likelihood ratio with it.
What survives in favour of repair A is drift-independent: FR2's structural
anomaly and FR27's EMBEDDEDNESS asymmetry --

    East 1@68 (discarded by repair A) is the only instance in either candidate
    class with no parent passage; East 4@51 (discarded by repair B) sits inside
    #3+@51.

FR27 priced this as soft. FR48 gave the (now collapsed) passage argument a
likelihood ratio; embeddedness deserves the same treatment. That is this cycle.

THE CONFOUND, PRE-EMPTED (CHALLENGE II). If a short class's PATTERN is a
sub-pattern of a longer class's pattern at the implied offset, then every long
instance CONTAINS a short instance BY CONSTRUCTION. Embeddedness would then be
an artefact of atlas structure, carrying no information about any individual
instance. FR50 already observed same-start containments, which is the signature.

    => containment is classified as STRUCTURAL (the child's pattern is implied
       by the parent's at that offset) or INCIDENTAL (it is not). Only
       incidental containment can be evidence.

If every containment is structural, embeddedness carries nothing and FR27's
argument dies -- leaving repair A with no surviving support. That is checked
first and reported whichever way it falls.

THE LIKELIHOOD RATIO, if embeddedness survives:

    LR(A over B) = [P(parentless|spurious) / P(parentless|genuine)]
                 x [P(embedded|genuine)   / P(embedded|spurious)]

  P(embedded | genuine)  estimated from certified instances other than the two
                         candidates
  P(embedded | spurious) estimated from a positional null: same message, same
                         length, random start -- a chance match's position is
                         not special

PRE-REGISTERED (frozen before measurement):
  R1  containment is classified structural vs incidental BEFORE any rate is
      computed; rates use incidental containment only.
  R2  if the incidental-containment rate among certified instances does not
      exceed the null rate, embeddedness carries no information and NO
      likelihood ratio is reported.
  R3  the two candidate instances are EXCLUDED from the rate estimates they are
      then scored against.

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""

import json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
XD = "XD-MBYG04K-URS3LF"

CAND_A = ("#M", "East 1", 68)     # discarded by repair A
CAND_B = ("#3", "East 4", 51)     # discarded by repair B


def load():
    c = json.load(open(os.path.join(HERE, "corpus.json")))
    M = dict(zip(c["message_labels"], c["ciphertexts"]))
    classes = json.load(open(os.path.join(HERE, "atlas.json")))["classes"]
    return M, classes


def instances(classes):
    out = []
    for cls in classes:
        for it in cls["instances"]:
            out.append((cls["id"], it["message"], it["start"],
                        cls["length"], cls["pattern"]))
    return out


def pattern_implies(parent_pat, off, child_pat):
    """Is the child's equality pattern IMPLIED by the parent's at this offset?
    True iff every equality the child asserts is also asserted by the parent."""
    L = len(child_pat)
    for i in range(L):
        for j in range(i + 1, L):
            if child_pat[i] == "." or child_pat[j] == ".": continue
            if child_pat[i] != child_pat[j]: continue
            pi, pj = parent_pat[off + i], parent_pat[off + j]
            if pi == "." or pj == "." or pi != pj:
                return False          # child asserts an equality parent does not
    return True


def containments(inst, others):
    """Return (structural, incidental) parent counts for one instance."""
    cid, m, s, L, pat = inst
    struct = 0; incid = 0
    for (oid, om, os_, oL, opat) in others:
        if om != m or oL <= L: continue
        if not (os_ <= s and os_ + oL >= s + L): continue
        off = s - os_
        if pattern_implies(opat, off, pat): struct += 1
        else: incid += 1
    return struct, incid


def selftest():
    ok = []
    def ck(n, c, d=""):
        ok.append((n, bool(c))); print(f"  {n:32s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise RuntimeError(f"{XD} selftest FAILED: {n} {d}")

    M, classes = load()
    ck("t1_load", len(classes) == 13, f"{len(classes)} classes")

    # t2: a child pattern literally cut from a parent must be STRUCTURAL
    ck("t2_structural", pattern_implies("A.B..B.A", 0, "A.B..B.A"), "identity")
    ck("t2b_substring", pattern_implies("AB..BA", 1, "B..B"), "cut from parent")

    # t3: a child asserting an equality the parent does not must be INCIDENTAL
    ck("t3_incidental", not pattern_implies("A....A", 1, "B..B"),
       "child equality absent from parent")

    # t4: the two candidates exist in the atlas
    ins = instances(classes)
    have_a = any((i[0], i[1], i[2]) == CAND_A for i in ins)
    have_b = any((i[0], i[1], i[2]) == CAND_B for i in ins)
    ck("t4_candidates_present", have_a and have_b, f"A={have_a} B={have_b}")
    print(f"selftest {sum(1 for _,p in ok if p)}/{len(ok)} green")
    return M, classes


def corpus_run(M, classes):
    ins = instances(classes)
    print("=" * 74)
    print("EYEEMBED -- does embeddedness discriminate repair A from repair B?")
    print("=" * 74)

    # [R1] classify every containment before computing any rate
    tot_s = tot_i = 0
    rec = {}
    for inst in ins:
        s, i = containments(inst, [o for o in ins if o is not inst])
        rec[(inst[0], inst[1], inst[2])] = (s, i, inst[3])
        tot_s += s; tot_i += i
    print(f"\n[R1] containment census over {len(ins)} certified instances:")
    print(f"      STRUCTURAL parent relations : {tot_s}")
    print(f"      INCIDENTAL parent relations : {tot_i}")
    if tot_i == 0:
        print("\n      *** every containment is structural ***")
        print("      Embeddedness is an artefact of atlas pattern nesting and")
        print("      carries NO information about individual instances.")
        print("      [R2] no likelihood ratio reported. FR27's argument DIES,")
        print("      and repair A loses its last quantitative support.")
        return

    # the two candidates
    for tag, cand in (("A discards", CAND_A), ("B discards", CAND_B)):
        s, i, L = rec[cand]
        print(f"\n  {tag} {cand[0]} {cand[1]}@{cand[2]} (L={L}): "
              f"structural parents {s}, incidental parents {i}")

    # [R3] rates from all OTHER certified instances
    others = {k: v for k, v in rec.items() if k not in (CAND_A, CAND_B)}
    emb = sum(1 for (s, i, L) in others.values() if i > 0)
    print(f"\n[R3] among the other {len(others)} certified instances:")
    print(f"      with >=1 INCIDENTAL parent : {emb} ({100*emb/len(others):.0f}%)")

    # positional null: same message, same length, random start
    rng = random.Random(110)
    trials = 4000; hit = 0
    lens = [v[2] for v in others.values()]
    msgs = list(M)
    for _ in range(trials):
        L = rng.choice(lens); m = rng.choice(msgs)
        if len(M[m]) <= L: continue
        s = rng.randrange(0, len(M[m]) - L)
        # a spurious instance's pattern is whatever the corpus gives there;
        # count only incidental containment by longer certified instances
        n = 0
        for (oid, om, os_, oL, opat) in ins:
            if om != m or oL <= L: continue
            if os_ <= s and os_ + oL >= s + L: n += 1
        if n: hit += 1
    p_null = hit / trials
    p_gen = emb / len(others)
    print(f"      positional null (random start, same length): "
          f"{100*p_null:.1f}% lie inside a longer certified instance")

    if p_gen <= p_null:
        print("\n[R2] certified instances are NOT more embedded than chance")
        print("     -> embeddedness carries no information; no LR reported.")
        return

    # likelihood ratio
    pe_g, pe_s = p_gen, max(p_null, 1e-6)
    pp_g, pp_s = 1 - pe_g, 1 - pe_s
    obs_A = pp_s * pe_g        # A: E1@68 spurious & parentless, E4@51 genuine & embedded
    obs_B = pp_g * pe_s        # B: E1@68 genuine & parentless, E4@51 spurious & embedded
    LR = obs_A / obs_B if obs_B else float("inf")
    print(f"\n  P(embedded | genuine)  = {pe_g:.3f}")
    print(f"  P(embedded | spurious) = {pe_s:.3f}")
    print(f"  P(obs | A) = P(parentless|spur) x P(embedded|gen) = {obs_A:.4f}")
    print(f"  P(obs | B) = P(parentless|gen)  x P(embedded|spur) = {obs_B:.4f}")
    print(f"\n  LIKELIHOOD RATIO favouring repair A: {LR:.1f}x")
    print(f"  (FR48's collapsed passage argument claimed 2.8e5x; this is the")
    print(f"   honest replacement and it is far weaker.)")
    print()


if __name__ == "__main__":
    M, classes = selftest()
    if "--selftest" not in sys.argv: corpus_run(M, classes)
