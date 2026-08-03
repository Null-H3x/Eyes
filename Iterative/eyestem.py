#!/usr/bin/env python3
"""
eyestem -- the FR6 constructive repair, executed: the atlas fed through
SOUND rows (pattern-letter positions only for isomorph pairs; full spans
only for verified-literal exact pairs; strict-scan pairs keep their own
audited full-span tier). Registered prediction from FR6's exhibit: #M and
#M- become self-consistent under sound rows. The conflict matrix is re-run
under sound rows (the #1 x #F edge autopsy rides on this), cross-validation
against the strict baseline stays armed as a hard rail, and the FR5
registered battery (frozen since FR5) is re-tested under the primary sound
tier.

Row semantics (the new mode): for a non-exact atlas pair with class
pattern P, emit the per-message-progressive row ONLY at offsets i with
P[i] != '.'; for exact pairs and for pairs without a pattern (the strict
scan tier), delegate to the repo's per_msg_prog_rows unchanged. Aligned
equal glyphs at a letter offset of a same-message pair correctly yield a
contradiction row (equal glyphs at different positions are impossible
under the progressive stem reading), matching the repo generator's own
semantics.

Primary-tier rule (pre-committed): sound-atlas UNION strict if the
cross-validation between them is clean; sound-atlas alone otherwise.
"""

import json, os, sys
from collections import Counter
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "eyereach"))
import eyereach as ER                      # noqa: E402  (gated machinery)
import iso_relax as IR                     # noqa: E402
import isomorph as iso                     # noqa: E402
import chain_models as cm                  # noqa: E402
import chain_extract as ce                 # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {
    "prediction_motif_heals": "#M and #M- self-consistent under sound rows",
    "primary_tier_rule": "sound-atlas + strict if cross-validation clean, else sound-atlas",
    "battery": {k: v for k, v in ER.PREREG.items() if k.startswith("H")},
    "baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
}

# ---------------------------------------------------------- atlas w/ patterns
def atlas_pairs_with_patterns(atlas_path, cts, labels):
    a = json.load(open(atlas_path))
    idx = {lab: i for i, lab in enumerate(labels)}
    pairs, pattern_of, by_class = [], {}, {}
    for cls in a["classes"]:
        L, pat = cls["length"], cls["pattern"]
        if len(pat) != L: fail(f"pattern length mismatch in {cls['id']}")
        inst = []
        for it in cls["instances"]:
            mi = idx[it["message"]]
            if list(cts[mi][it["start"]:it["start"] + L]) != list(it["values"]):
                fail(f"atlas values mismatch at {cls['id']} {it['message']}@{it['start']}")
            inst.append((mi, it["start"]))
        cls_pairs = []
        for (m1, p1), (m2, p2) in combinations(inst, 2):
            exact = cts[m1][p1:p1 + L] == cts[m2][p2:p2 + L]
            pr = iso.IsoPair(m1=m1, p1=p1, m2=m2, p2=p2, length=L, exact=exact)
            pairs.append(pr); cls_pairs.append(pr)
            pattern_of[(m1, p1, m2, p2, L)] = pat
        by_class[cls["id"]] = cls_pairs
    return pairs, pattern_of, by_class

def sound_rows_factory(pattern_of):
    def rows(pr, messages, Nn):
        key = (pr.m1, pr.p1, pr.m2, pr.p2, pr.length)
        pat = pattern_of.get(key)
        if pr.exact or pat is None:
            yield from cm.per_msg_prog_rows(pr, messages, Nn)
            return
        bm1, bm2 = Nn + pr.m1, Nn + pr.m2
        rhs = (pr.p2 - pr.p1) % Nn
        for i in range(pr.length):
            if pat[i] == '.': continue
            A = int(messages[pr.m1][pr.p1 + i])
            D = int(messages[pr.m2][pr.p2 + i])
            row = {}
            row[D] = (row.get(D, 0) + 1) % Nn
            row[A] = (row.get(A, 0) + Nn - 1) % Nn
            if pr.m1 != pr.m2:
                row[bm2] = (row.get(bm2, 0) + Nn - 1) % Nn
                row[bm1] = (row.get(bm1, 0) + 1) % Nn
            row = {v: c for v, c in row.items() if c}
            yield row, rhs
    return rows

# ---------------------------------------------------------- selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: sound-rows mode, interior-variation plant, guards")

    # 1. all-letter patterns == per_msg rows (path equivalence on audited plant)
    cts, q_truth, bases = IR._overdetermined_plant(seed=3)
    anchor = ce.calibrate_anchor(cts, 10, seed=0)
    scanp = iso.find_isomorphs(cts, 10, anchor, different_only=False)
    pat_all = {(p.m1, p.p1, p.m2, p.p2, p.length): "X" * p.length for p in scanp}
    gfA, kA = ce.consensus_alphabet(cts, scanp, N, sound_rows_factory(pat_all), seed=0)
    gfB, kB = ce.consensus_alphabet(cts, scanp, N, cm.per_msg_prog_rows, seed=0)
    dA, _ = ER.certified_domain(gfA); dB, _ = ER.certified_domain(gfB)
    check("all-letter sound rows == per_msg rows", dA == dB and len(dA) >= 2,
          f"(|dom|={len(dA)})")

    # 2. interior-variation plant: fixed skeleton, varied dots
    import numpy as np
    rng = np.random.default_rng(7)
    C = list(rng.permutation(N)); qt = [0] * N
    for pos, s in enumerate(C): qt[s] = pos
    T = 80; base = 5
    plain = [[int(x) for x in rng.integers(0, N, T)] for _ in range(2)]
    pat = "AB.CB.A."                                  # letters 0,1,3,4,6
    stem = {0: 11, 1: 30, 3: 52, 4: None, 6: None}    # B repeats, A repeats via u
    # choose letter tokens s.t. u-repeats hold: A@0/A@6 -> p6 = p0 - 6;
    # B@1/B@4 -> p4 = p1 - 3
    stem[6] = (stem[0] - 6) % N; stem[4] = (stem[1] - 3) % N
    spots = [(0, 10), (0, 40), (1, 25)]
    for (m, p0) in spots:
        for i in range(8):
            plain[m][p0 + i] = stem[i] if i in stem else int(rng.integers(0, N))
    cts2 = [[int(C[(plain[m][t] + base + t) % N]) for t in range(T)] for m in range(2)]
    prs, pod = [], {}
    for (a1, b1), (a2, b2) in combinations(spots, 2):
        pr = iso.IsoPair(m1=a1, p1=b1, m2=a2, p2=b2, length=8,
                         exact=cts2[a1][b1:b1+8] == cts2[a2][b2:b2+8])
        prs.append(pr); pod[(a1, b1, a2, b2, 8)] = pat
    gfS, kS = ce.consensus_alphabet(cts2, prs, N, sound_rows_factory(pod), seed=0)
    keptS = len(kS) if kS else len(prs)
    check("benign interior variation: sound rows keep all", keptS == 3,
          f"(sound {keptS}/3)")

    # 2b. the FR6 exhibit itself as the known-contradictory configuration
    # (GF systems carry no injectivity, so synthetic contradictions collapse
    # into value-coincidences; the corpus's certified four-cycle is the
    # specification): full-span must drop, sound rows must keep all six
    W = {"E1a": [47,44,48,42,19,48,13,47,19], "E1b": [71,11,74,56,4,74,19,71,4],
         "W1a": [47,44,48,42,19,48,13,47,19], "W1b": [68,46,17,36,13,17,21,68,13]}
    ctsX = [[81]*90, [82]*90]
    ctsX[0][40:49] = W["E1a"]; ctsX[0][68:77] = W["E1b"]
    ctsX[1][40:49] = W["W1a"]; ctsX[1][70:79] = W["W1b"]
    spotsX = [(0,40),(0,68),(1,40),(1,70)]
    patM = "A.B.CB.AC"
    prsX, podX = [], {}
    for (a1,b1),(a2,b2) in combinations(spotsX, 2):
        pr = iso.IsoPair(m1=a1,p1=b1,m2=a2,p2=b2,length=9,
                         exact=ctsX[a1][b1:b1+9]==ctsX[a2][b2:b2+9])
        prsX.append(pr); podX[(a1,b1,a2,b2,9)] = patM
    gfXf, kXf = ce.consensus_alphabet(ctsX, prsX, N, cm.per_msg_prog_rows, seed=0)
    keptXf = len(kXf) if kXf else len(prsX)
    gfXs, kXs = ce.consensus_alphabet(ctsX, prsX, N, sound_rows_factory(podX), seed=0)
    keptXs = len(kXs) if kXs else len(prsX)
    check("FR6 exhibit: full-span drops, sound rows keep all six",
          keptXf < 6 and keptXs == 6, f"(full {keptXf}/6, sound {keptXs}/6)")

    dS, _ = ER.certified_domain(gfS)
    exact = all((dS[b] - dS[a]) % N == (qt[b] - qt[a]) % N
                for a, b in combinations(sorted(dS), 2))
    check("sound-rows certified diffs exact vs truth", exact, f"(|dom|={len(dS)})")

    # 3. exact-pair handling: literal repeat across messages at aligned pos
    cts3 = [list(x) for x in cts2]
    cts3[1][10:18] = cts3[0][10:18]
    pr = iso.IsoPair(m1=0, p1=10, m2=1, p2=10, length=8, exact=True)
    gfE, kE = ce.consensus_alphabet(cts3, [pr], N, sound_rows_factory({}), seed=0)
    check("exact pair takes full-span path, consistent",
          (len(kE) if kE else 1) == 1)

    # 4. battery labels via ER machinery on the sound domain
    if len(dS) >= 2:
        ds = sorted(dS); a, b = ds[0], ds[1]
        truth = (dS[b] - dS[a]) % N
        png, _ = ER.pin_grade(dS)
        saved = dict(ER.PREREG["H1_boundary"])
        ER.PREREG["H1_boundary"] = {"pair": [a, b], "diff": truth}
        r1 = ER.run_battery(dS, png)["H1_boundary"]["status"]
        ER.PREREG["H1_boundary"] = {"pair": [a, b], "diff": (truth + 1) % N}
        r2 = ER.run_battery(dS, png)["H1_boundary"]["status"]
        ER.PREREG["H1_boundary"] = saved
        check("battery labels under sound domain", r1 == "SUPPORTED" and r2 == "VIOLATED")
    else:
        check("battery labels under sound domain", False, "(domain too small)")

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ---------------------------------------------------------- corpus
def corpus_run(corpus_path, atlas_path):
    c = json.load(open(corpus_path))
    cts = [list(x) for x in c["ciphertexts"]]
    labels = c["message_labels"]
    print("\npre-registered:", json.dumps(PREREG["prediction_motif_heals"]))

    r = IR.relax(cts, N, seed=0)
    bg = PREREG["baseline_guard"]
    if (r.linked_strict, r.distinct_strict, len(r.pins)) != \
       (bg["linked"], bg["distinct"], bg["pins"]):
        fail("baseline reproduction mismatch")
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    apairs, pattern_of, by_class = atlas_pairs_with_patterns(atlas_path, cts, labels)
    srows = sound_rows_factory(pattern_of)

    print("\nC1 isolated per-class consensus under SOUND rows:")
    heal = True
    for cid, prs in by_class.items():
        gf, keep = ce.consensus_alphabet(cts, prs, N, srows, seed=0)
        k = len(keep) if keep else len(prs)
        tag = "SELF-CONSISTENT" if k == len(prs) else "INTERNAL CONFLICT"
        if k != len(prs) and cid in ("#M", "#M-"): heal = False
        print(f"  {cid:5s} {k}/{len(prs)}  {tag}")
    print(f"  registered prediction (#M/#M- heal): "
          f"{'CONFIRMED' if heal else 'REFUTED'}")

    print("\nC2 pairwise class-union matrix under SOUND rows (X = conflict):")
    cids = list(by_class); edges = []
    print("      " + " ".join(f"{x:>4s}" for x in cids))
    for c1 in cids:
        row = []
        for c2 in cids:
            if c1 == c2: row.append("  . "); continue
            prs = by_class[c1] + by_class[c2]
            gf, keep = ce.consensus_alphabet(cts, prs, N, srows, seed=0)
            k = len(keep) if keep else len(prs)
            bad = k < len(prs)
            if bad and (c2, c1) not in edges: edges.append((c1, c2))
            row.append("  X " if bad else "  o ")
        print(f"{c1:5s} " + " ".join(row))
    print(f"  remaining conflict edges: {len(edges)}: {edges}")

    print("\nC3 global sound-atlas consensus:")
    gfA, keepA = ce.consensus_alphabet(cts, apairs, N, srows, seed=0)
    kA = len(keepA) if keepA else len(apairs)
    print(f"  kept {kA}/{len(apairs)}")
    domA, refA = ER.certified_domain(gfA)
    pngA, taintA = ER.pin_grade(domA)
    print(f"  certified={len(domA)} pin-grade={len(pngA)} tainted={taintA}")

    anchor = ce.calibrate_anchor(cts, 13, seed=0)
    strictp = iso.find_isomorphs(cts, 13, anchor, different_only=False)
    gfS, _ = ce.consensus_alphabet(cts, strictp, N, cm.per_msg_prog_rows, seed=0)
    domS, _ = ER.certified_domain(gfS)
    shared, bad = ER.cross_validate(domS, domA)
    print(f"\nC4 cross-validation sound-atlas vs strict: shared={len(shared)} "
          f"disagreements={len(bad)}")

    if not bad:
        pool = apairs + strictp
        gfP, keepP = ce.consensus_alphabet(cts, pool, N, srows, seed=0)
        kP = len(keepP) if keepP else len(pool)
        domP, _ = ER.certified_domain(gfP)
        pngP, taintP = ER.pin_grade(domP)
        print(f"\nC5 PRIMARY tier (sound-atlas + strict): kept {kP}/{len(pool)} "
              f"certified={len(domP)} pin-grade={len(pngP)}")
    else:
        print("\nC5 PRIMARY tier = sound-atlas alone (per rule; disagreements listed):")
        for a, b in bad[:10]: print(f"    disagree: ({a},{b})")
        domP, pngP = domA, pngA

    print("\nC6 REGISTERED BATTERY under PRIMARY tier:")
    hyp = sorted({47, 1, 66, 5} | set(ER.INDICATORS.values()))
    for g in hyp:
        st = ("pin-grade" if g in pngP else
              "certified-tainted" if g in domP else "unlinked")
        print(f"  glyph {g:2d}: {st}")
    for name, res in ER.run_battery(domP, pngP).items():
        print(f"  {name}: {res}")

    Mm = dict(zip(labels, c["ciphertexts"]))
    print("\nC7 pin-grade template skeleton under PRIMARY tier:")
    for frame, tmpl in (("A", {t: Mm["East 4"][t] for t in range(3, 21)}),
                        ("B", {t: Mm["East 1"][t] for t in range(3, 25)})):
        for t, g in sorted(tmpl.items()):
            if g in pngP:
                print(f"  frame {frame} t={t:2d} glyph {g:2d} q={pngP[g]:2d} "
                      f"p_gauge={(pngP[g] - t) % N:2d}")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
