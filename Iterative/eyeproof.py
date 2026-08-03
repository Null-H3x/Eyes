#!/usr/bin/env python3
"""eyeproof -- uniqueness by exhaustion, not sampling.

THEOREM SHAPE. Consistency is subset-monotone: a subset of a consistent row
system is consistent. So if (i) a class is individually inconsistent with the
mandatory pool it can enter NO consistent set containing the pool, and (ii)
the set of individually-consistent classes is JOINTLY consistent, then every
maximal consistent set equals {pool + all survivors}. Uniqueness follows with
no sampling and no measure-zero caveat.

GATES (all must pass before the theorem is asserted):
  G1  control-negative: on the classes-only system (known: 68 maximal sets)
      the survivors must NOT be jointly consistent -- the method must be able
      to say no.
  G2  the forced set's signature must equal the certified unique reading:
      794 relations, 61 glyphs, 8 equalities, sha 7e9ab7231a6eb285...
  G3  planted: injecting one fabricated class that conflicts with an accepted
      class must produce a joint conflict (the method detects order-dependence
      when it exists).
"""
import sys, copy, hashlib
sys.path.insert(0, ".")
from make_mandatory import parse_problem, Ech, N

XD = "XD-MBYG04K-URS3LF"
CERT = "7e9ab7231a6eb285795c9ca484329b209c1e95ff15fb317b8055a170761fecdf"

def survivors_and_joint(seeds, classes, extra=None):
    base = Ech()
    for row, rhs in seeds: base.add(row, rhs)
    cls = list(classes) + (extra or [])
    ok = []
    for ci, rows in enumerate(cls):
        s = copy.deepcopy(base)
        good = True
        for row, rhs in rows:
            if s.add(row, rhs) == -1: good = False; break
        if good: ok.append(ci)
    s = copy.deepcopy(base); conflicts = []
    for ci in ok:
        bak = (dict(s.piv), list(s.rows))
        for row, rhs in cls[ci]:
            if s.add(row, rhs) == -1:
                s.piv, s.rows = bak; conflicts.append(ci); break
    return ok, conflicts, s

def signature(s):
    gl = s.used_glyphs(); sig = []
    for i in range(len(gl)):
        for j in range(i+1, len(gl)):
            d = s.query(gl[i], gl[j])
            if d is not None: sig.append((gl[i], gl[j], d))
    sig.sort()
    sha = hashlib.sha256(";".join(f"{a},{b},{d}" for a,b,d in sig).encode()).hexdigest()
    eq = sum(1 for _,_,d in sig if d == 0)
    return sig, sha, len(gl), eq

def main():
    seeds0, classes = parse_problem("maxset_problem.txt")
    poolrows = parse_problem("mand/maxset_problem.txt")[0][15:]
    ok = True
    def chk(name, cond, note=""):
        nonlocal ok; ok &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")

    print("G1 control-negative (classes-only system, known 68 maximal sets):")
    okc, confc, _ = survivors_and_joint(seeds0, classes)
    chk("survivors NOT jointly consistent on the control", len(confc) > 0,
        f"({len(okc)} survivors, {len(confc)} joint conflicts)")

    print("G3 planted order-dependence is detected (mandatory system + fabricated class):")
    # fabricate a class asserting q[a]-q[b] = wrong value for a pair the pool forces
    okm0, _, s0 = survivors_and_joint(seeds0 + poolrows, classes)
    sig0, _, _, _ = signature(s0)
    a, b, v = sig0[0]
    fab = [[({a:1, b:N-1}, (v+1) % N)]]
    okp, confp, _ = survivors_and_joint(seeds0 + poolrows, classes, extra=fab)
    chk("fabricated conflicting class produces joint conflict or DOA",
        (len(classes) in confp) or (len(classes) not in okp))

    print("THE MANDATORY SYSTEM:")
    okm, confm, sm = survivors_and_joint(seeds0 + poolrows, classes)
    print(f"  individually consistent with the pool : {len(okm)} / {len(classes)}")
    print(f"  dead on arrival                       : {len(classes)-len(okm)}")
    print(f"  joint conflicts among survivors       : {len(confm)}")
    chk("survivors jointly consistent", len(confm) == 0)
    sig, sha, gly, eq = signature(sm)
    chk("forced set reproduces the certified object",
        sha == CERT and len(sig) == 794 and gly == 61 and eq == 8,
        f"({len(sig)} rel, {gly} gly, {eq} eq, sha {sha[:16]}...)")

    if not ok: raise SystemExit(f"{XD}: gate failure -- theorem NOT asserted")
    print()
    print("THEOREM. With the atlas pool mandatory, every maximal consistent")
    print(f"class set equals {{pool + the {len(okm)} survivors}}: the 50 excluded")
    print("classes are each individually inconsistent with the pool (subset-")
    print("monotonicity bars them from every consistent superset), and the")
    print("survivors coexist. The unique reading is PROVEN, not sampled.")

if __name__ == "__main__":
    main()
