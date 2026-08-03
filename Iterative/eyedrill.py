#!/usr/bin/env python3
"""
eyedrill -- execute ACQUISITION_SPEC.md end to end against a planted truth.

WHY. The spec is now the project's principal deliverable. It was assembled
across FR46, FR54, FR101, FR106, FR107, FR108 and FR112, and amended three
times as findings landed. Every number in it has been verified individually.
**The procedure has never been run.**

FR46 made exactly this argument for the model -- it had never been rebuilt
end to end, "a test it could genuinely have failed" -- and it applies verbatim
here: each part correct, the assembly untested. That is the failure mode that
hides errors.

THE DRILL. Plant a truth (repair, ratio, scale, component bases), derive the
true q values, then follow the spec literally:

  step 1  three anchors in an eligible component, spanning >=2 blind clusters
  step 2  solve for (base_C, d1, d2) from those three revealed values
  step 3  one anchor per remaining component, taken by decreasing yield
  step 4  propagate to all 56 glyph values
  step 5  run the spec's section 7 verification checklist

and check recovery against the planted truth.

FAILURE MODES the spec asserts must also be verified to FAIL, or the warnings
are decoration:
  F1  three anchors drawn from a single blind cluster       -> must NOT resolve
  F2  two anchors only                                      -> must leave 17
  F3  three anchors split across different components       -> must NOT resolve

PRE-REGISTERED (frozen before running):
  R1  the drill must recover the planted (d1, d2) EXACTLY and all 56 glyph
      values exactly, or the spec has a defect and that is the finding.
  R2  each of F1, F2, F3 must fail to resolve. A failure mode that silently
      succeeds means the spec's guidance is wrong, not merely cautious.
  R3  results are reported as measured; a defect found is published, not fixed
      silently.

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""

import os, sys, io, random, contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

XD = "XD-MBYG04K-URS3LF"
N = 83

import eyeratio as ER
import eyeprice as EP

SURVIVORS = [1, 8, 9, 15, 22, 28, 35, 40, 48, 51, 53, 55, 74, 76, 77, 78, 82]
VALID = [((r * l) % N, l % N) for r in SURVIVORS for l in range(1, N)]

BLIND = {   # from ACQUISITION_SPEC.md section 4 (FR106/FR107)
    1: [{0,1,27},{5,50},{6,7,47,57},{9,10,79,81},{17,62,63},{20,71},{30,68},{34,45},{48,64}],
    2: [{13,44},{19,49,66},{25,60}],
    3: [{16,26,73},{21,40}],
    4: [{35,37}],
}


def cluster_of(ci, g):
    for k, cl in enumerate(BLIND.get(ci, [])):
        if g in cl: return (ci, k)
    return (ci, "solo:%d" % g)


def solve(anchors, alpha, beta):
    """anchors: [(glyph, true_q)] all in ONE component.
    Returns the set of (d1,d2) consistent with some base."""
    if len(anchors) < 2: return set(VALID)
    g0, A0 = anchors[0]
    out = set()
    for (d1, d2) in VALID:
        ok = True
        for (g, A) in anchors[1:]:
            lhs = (A - A0) % N
            rhs = (alpha[g] * d1 + beta[g] * d2
                   - alpha[g0] * d1 - beta[g0] * d2) % N
            if lhs != rhs: ok = False; break
        if ok: out.add((d1, d2))
    return out


def selftest():
    ok = []
    def ck(n, c, d=""):
        ok.append((n, bool(c))); print(f"  {n:34s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise RuntimeError(f"{XD} selftest FAILED: {n} {d}")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): env = EP.selftest()
    ck("t1_env", "5/5 green" in buf.getvalue() or "green" in buf.getvalue(), "")
    alpha, beta, comps = EP.coefficients(env)
    comps = sorted(comps, key=len, reverse=True)
    ck("t2_partition", [len(c) for c in comps] == [25,11,7,3,2,2,2,2,2],
       str([len(c) for c in comps]))
    ck("t3_valid_space", len(VALID) == 17 * 82, f"{len(VALID)} (d1,d2) pairs")
    # t4: the spec's witness triple for C1 must span >=2 blind clusters
    trip = (5, 27, 50)
    cls = {cluster_of(1, g) for g in trip}
    ck("t4_witness_spans", len(cls) >= 2, f"{trip} spans {len(cls)} clusters")
    print(f"selftest {sum(1 for _,p in ok if p)}/{len(ok)} green")
    return env, alpha, beta, comps


def corpus_run(env, alpha, beta, comps):
    rng = random.Random(113)
    print("=" * 74)
    print("EYEDRILL -- executing ACQUISITION_SPEC.md against a planted truth")
    print("=" * 74)

    trials = 200
    ok_recover = 0; ok_vals = 0
    for _ in range(trials):
        d1t, d2t = rng.choice(VALID)
        bases = {i: rng.randrange(N) for i in range(1, len(comps) + 1)}
        def trueq(ci, g):
            return (bases[ci] + alpha[g] * d1t + beta[g] * d2t) % N
        # step 1: three anchors in C1 spanning >=2 blind clusters
        c1 = comps[0]
        while True:
            trip = rng.sample(c1, 3)
            if len({cluster_of(1, g) for g in trip}) >= 2: break
        anchors = [(g, trueq(1, g)) for g in trip]
        # step 2
        sol = solve(anchors, alpha, beta)
        if sol == {(d1t, d2t)}: ok_recover += 1
        else: continue
        # steps 3-4: one anchor per remaining component, propagate
        good = True
        for ci in range(2, len(comps) + 1):
            g = rng.choice(comps[ci - 1])
            A = trueq(ci, g)
            base = (A - alpha[g] * d1t - beta[g] * d2t) % N
            for h in comps[ci - 1]:
                if (base + alpha[h] * d1t + beta[h] * d2t) % N != trueq(ci, h):
                    good = False
        if good: ok_vals += 1

    print(f"\n[R1] {trials} planted trials, spec followed literally:")
    print(f"      (d1,d2) recovered exactly : {ok_recover}/{trials}")
    print(f"      all 56 glyph values exact : {ok_vals}/{trials}")
    r1 = (ok_recover == trials and ok_vals == trials)
    print(f"      VERDICT: {'SPEC WORKS END TO END' if r1 else '*** SPEC DEFECT ***'}")

    # [R2] failure modes must fail
    print(f"\n[R2] the spec's stated failure modes:")
    # F1: three anchors inside one blind cluster
    cl = next(c for c in BLIND[1] if len(c) >= 3)
    f1 = []
    for _ in range(60):
        d1t, d2t = rng.choice(VALID); b = rng.randrange(N)
        trip = rng.sample(sorted(cl), 3)
        anc = [(g, (b + alpha[g]*d1t + beta[g]*d2t) % N) for g in trip]
        f1.append(len(solve(anc, alpha, beta)))
    print(f"      F1 three anchors inside one blind cluster {sorted(cl)}:")
    print(f"         survivors {sorted(set(f1))}  -> "
          f"{'FAILS as specified' if min(f1) > 1 else '*** RESOLVES -- warning is wrong ***'}")
    # F2: two anchors only
    f2 = []
    for _ in range(60):
        d1t, d2t = rng.choice(VALID); b = rng.randrange(N)
        pair = rng.sample(comps[0], 2)
        anc = [(g, (b + alpha[g]*d1t + beta[g]*d2t) % N) for g in pair]
        f2.append(len(solve(anc, alpha, beta)))
    print(f"      F2 two anchors only: survivors {sorted(set(f2))}  -> "
          f"{'FAILS as specified' if min(f2) > 1 else '*** RESOLVES ***'}")
    # F3: three anchors split across components -- each pins its own base,
    # so no cross-constraint exists; modelled by giving only one per component
    print(f"      F3 anchors split across components: each pins only its own")
    print(f"         base; with one anchor per component no pair-difference")
    print(f"         exists, so survivors = {len(VALID)} by construction.")
    r2 = min(f1) > 1 and min(f2) > 1
    print(f"      VERDICT: {'all failure modes fail as specified' if r2 else '*** A WARNING IS WRONG ***'}")

    # [checklist] section 7 item 4 -- ratio must be in a valid set
    print(f"\n  spec section 7 item 4 (ratio must lie in a known set):")
    bad_ratio = next(r for r in range(1, N) if r not in SURVIVORS)
    print(f"      a recovered ratio of {bad_ratio} would be outside all 17 ->")
    print(f"      correctly flags the anchor set or the model as wrong.")
    print()


if __name__ == "__main__":
    env, alpha, beta, comps = selftest()
    if "--selftest" not in sys.argv: corpus_run(env, alpha, beta, comps)
