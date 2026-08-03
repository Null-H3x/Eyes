#!/usr/bin/env python3
"""
eyereveal -- materialise the candidate partial decryptions.

FIRST CYCLE UNDER EYESPIRAL-C. 118 cycles produced structure, exclusions and
tooling, and not one produced an actual candidate decryption. This does.

WHAT IS ACTUALLY DETERMINED. For a determined position,

    p[t] = A_block + v[t],      v[t] = alpha_g*d1 + beta_g*d2 - d_g*t

with v[t] KNOWN once (d1,d2) is chosen and A_block = base_component - b_message.
The 604 alignment cells that span two different blocks link them, and the
linkage leaves ONE connected group of 34 blocks covering 461 positions --
**44.5% of the corpus, determined up to a single additive constant.**

SCALE-INVARIANCE (why there are 17 candidates and not 1,394). Scaling
(d1,d2) -> (lambda*d1, lambda*d2) scales every v by lambda, so

    p[t] = p[t']  <=>  v[t] = v[t']  <=>  lambda*v[t] = lambda*v[t']

The plaintext EQUALITY STRUCTURE is scale-invariant. The 82 scales collapse and
only the 17 ratios give distinct structures.

THE ARTIFACT. For each of the 17 surviving ratios, the 461-position partial
plaintext of the largest connected group, normalised so its free constant is
zero. Rendered as values and as text, so a human or a community hypothesis
about the inner layer can be tested against something concrete.

PRE-REGISTERED (frozen before building):
  R1  the canonical build must reproduce 384/0/56 or the run VOIDS.
  R2  the 17 renderings must be pairwise DISTINCT. If any two coincide the
      scale-invariance argument is wrong and the artifact is withdrawn.
  R3  no claim is made that any rendering is correct. This ships candidates,
      not conclusions.

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""

import os, sys, json, io, contextlib
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
XD = "XD-MBYG04K-URS3LF"
N = 83

import eyeprice as EP
import eyeaudit as AUD

SURVIVORS = [1, 8, 9, 15, 22, 28, 35, 40, 48, 51, 53, 55, 74, 76, 77, 78, 82]
GI = {"East 1": 0, "West 1": 0, "East 2": 0, "West 2": 1, "East 3": 1,
      "West 3": 1, "East 4": 2, "West 4": 2, "East 5": 2}


def setup():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        env = EP.selftest()
    alpha, beta, comps = EP.coefficients(env)
    comps = sorted(comps, key=len, reverse=True)
    compof = {}
    for i, c in enumerate(comps, 1):
        for g in c: compof[g] = i
    cts, labels, Lx, ctx, pool, red = AUD.load(
        os.path.join(HERE, "corpus.json"), os.path.join(HERE, "atlas.json"))
    return alpha, beta, comps, compof, cts, labels, red


def block_groups(cts, labels, red, compof):
    blocks = defaultdict(list)
    for mi in range(len(labels)):
        for t, g in enumerate(cts[mi]):
            if g in compof: blocks[(mi, compof[g])].append(t)
    link = defaultdict(set)
    for pr in red:
        for i in range(pr.length):
            g1 = cts[pr.m1][pr.p1 + i]; g2 = cts[pr.m2][pr.p2 + i]
            if g1 in compof and g2 in compof:
                k1 = (pr.m1, compof[g1]); k2 = (pr.m2, compof[g2])
                if k1 != k2: link[k1].add(k2); link[k2].add(k1)
    seen = set(); groups = []
    for k in blocks:
        if k in seen: continue
        stack = [k]; grp = set()
        while stack:
            x = stack.pop()
            if x in seen: continue
            seen.add(x); grp.add(x); stack.extend(link[x] - seen)
        groups.append(grp)
    groups.sort(key=lambda g: -sum(len(blocks[k]) for k in g))
    return blocks, groups


def decrypt(group, blocks, cts, labels, alpha, beta, compof, d1, d2):
    """v[t] for every position of the group, normalised so the first is 0."""
    out = []
    for (mi, ci) in sorted(group):
        dg = d1 if GI[labels[mi]] == 0 else d2
        for t in sorted(blocks[(mi, ci)]):
            g = cts[mi][t]
            v = (alpha[g] * d1 + beta[g] * d2 - dg * t) % N
            out.append((labels[mi], ci, t, g, v))
    if out:
        base = out[0][4]
        out = [(m, c, t, g, (v - base) % N) for (m, c, t, g, v) in out]
    return out


RAMP = ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")


def render(dec):
    """Canonical: symbols assigned in order of FIRST OCCURRENCE, so the string
    encodes the plaintext EQUALITY STRUCTURE only. Raw values scale with the
    unknown drift scale; the equality structure does not (gate t3)."""
    order = {}
    out = []
    for (_, _, _, _, v) in dec:
        if v not in order: order[v] = len(order)
        out.append(RAMP[order[v] % len(RAMP)])
    return "".join(out)


def selftest():
    ok = []
    def ck(n, c, d=""):
        ok.append((n, bool(c))); print(f"  {n:32s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise RuntimeError(f"{XD} selftest FAILED: {n} {d}")
    alpha, beta, comps, compof, cts, labels, red = setup()
    ck("t1_partition", [len(c) for c in comps] == [25,11,7,3,2,2,2,2,2],
       str([len(c) for c in comps]))
    blocks, groups = block_groups(cts, labels, red, compof)
    big = groups[0]
    npos = sum(len(blocks[k]) for k in big)
    ck("t2_biggest_group", npos == 461, f"{npos} positions, {len(big)} blocks")

    # R2: scale-invariance -- two scales of the SAME ratio must render identically
    a = render(decrypt(big, blocks, cts, labels, alpha, beta, compof, 8, 1))
    b = render(decrypt(big, blocks, cts, labels, alpha, beta, compof, 16, 2))
    ck("t3_scale_invariant", a == b, "ratio 8 at scale 1 and scale 2 agree")

    # different ratios must differ
    c1 = render(decrypt(big, blocks, cts, labels, alpha, beta, compof, 9, 1))
    ck("t4_ratios_differ", a != c1, "ratio 8 vs ratio 9")
    ck("t5_length", len(a) == 461, f"{len(a)} chars")
    print(f"selftest {sum(1 for _,p in ok if p)}/{len(ok)} green")
    return alpha, beta, comps, compof, cts, labels, red, blocks, groups


def build(env):
    alpha, beta, comps, compof, cts, labels, red, blocks, groups = env
    big = groups[0]
    npos = sum(len(blocks[k]) for k in big)
    print("=" * 74)
    print("EYEREVEAL -- candidate partial decryptions")
    print("=" * 74)
    print(f"\n  largest connected block group : {len(big)} blocks, {npos} positions")
    print(f"  corpus coverage               : {100*npos/1036:.1f}%")
    print(f"  free parameters inside it     : ONE additive constant")
    print(f"  candidate readings            : {len(SURVIVORS)} (scale-invariant)\n")

    lines = []
    seen = {}
    for r in SURVIVORS:
        dec = decrypt(big, blocks, cts, labels, alpha, beta, compof, r, 1)
        txt = render(dec)
        if txt in seen:
            raise RuntimeError(f"{XD} R2 VIOLATED: ratio {r} identical to {seen[txt]}")
        seen[txt] = r
        vals = [v for (_,_,_,_,v) in dec]
        from collections import Counter
        cc = Counter(vals)
        rep = sum(n*(n-1)//2 for n in cc.values())
        lines.append((r, txt, len(cc), rep))
        print(f"  ratio {r:2d}: {len(cc):2d} distinct plaintext values, "
              f"{rep:4d} equal-pairs")
    print(f"\n  [R2] all {len(seen)} renderings pairwise distinct: "
          f"{len(seen)==len(SURVIVORS)}")

    # write the artifact
    path = os.path.join(HERE, "CANDIDATE_READINGS.txt")
    with open(path, "w") as f:
        f.write("NOITA EYE MESSAGES -- CANDIDATE PARTIAL DECRYPTIONS\n")
        f.write("=" * 66 + "\n\n")
        f.write(f"{npos} positions ({100*npos/1036:.1f}% of the corpus) across "
                f"{len(big)} linked blocks.\n")
        f.write("Plaintext determined up to ONE additive constant per reading.\n")
        f.write(f"{len(SURVIVORS)} candidates, one per surviving drift ratio.\n")
        f.write("Scale-invariant: the 82 scales give identical equality structure.\n\n")
        f.write("NO CLAIM IS MADE THAT ANY READING IS CORRECT. These are the\n")
        f.write("candidates the model admits; exactly one is right if the model is.\n\n")
        f.write("Encoding: symbols are assigned in order of FIRST OCCURRENCE, so\n")
        f.write("the string encodes the plaintext EQUALITY STRUCTURE and nothing\n")
        f.write("else. Equal characters mean EQUAL PLAINTEXT. Raw values scale with\n")
        f.write("the unknown drift scale; this structure does not.\n\n")
        dec0 = decrypt(big, blocks, cts, labels, alpha, beta, compof, 1, 1)
        f.write("POSITION INDEX (message, component, offset, ciphertext glyph):\n")
        for i, (m, c, t, g, _) in enumerate(dec0):
            if i % 6 == 0: f.write("\n  ")
            f.write(f"{m[:2]}{m[-1]}/C{c}/{t:3d}/g{g:02d}  ")
        f.write("\n\n" + "=" * 66 + "\n\n")
        for r, txt, ndist, rep in lines:
            f.write(f"--- RATIO {r} ---  {ndist} distinct values, {rep} equal-pairs\n")
            for i in range(0, len(txt), 80):
                f.write("  " + txt[i:i+80] + "\n")
            f.write("\n")
    print(f"\n  ARTIFACT WRITTEN: CANDIDATE_READINGS.txt "
          f"({os.path.getsize(path):,} bytes)")
    print()


if __name__ == "__main__":
    env = selftest()
    if "--selftest" not in sys.argv: build(env)
