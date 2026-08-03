#!/usr/bin/env python3
"""
eyemerge -- merge-admissibility sweep for the alphabet-size question [56, 83],
plus the audit of V4's stated mechanism. Read-only; no isomorph modified.

THE QUESTION. 56 glyphs are proven pairwise-distinct symbols (within-component
distinct Delta). The residual [56, 83] window turns on whether any of the 27
undetermined glyphs is a VARIANT of another glyph (mis-segmentation /
homoglyph). Tech-ref section 4.2 proposes testing each of the 1,512
determined-merges "by rebuilding the skeleton and recording added relations
versus contradictions." CHALLENGE I (FR97 section 1) shows that mechanism is
near-vacuous: undetermined glyphs occupy no cell of any w-anchored pair, so a
skeleton rebuild under any merge adds zero relations and contradicts nothing.
What survives are three screens that do not route through the rebuild:

  S1  ADJACENCY (primary). The corpus has 0 same-value doubles in 1,027
      adjacent slots (~12.4 expected; chance ~4e-6). Under the surviving
      model a symbol double at t requires the plaintext step -drift, so the
      exact zero reads as mechanism: the plaintext never steps by -drift.
      A merged pair (g,h) adjacent anywhere would BE a symbol double.
      => g,h adjacent => merge excluded. Conditional on the mechanism
      reading; the variant-masking conspiracy is priced in FR97.

  S3  SAME-INSTANCE EXACTNESS. Within one certified pool instance, two cells
      carrying different pattern letters are symbol-distinct: merging their
      values would coarsen that instance's equality signature while sibling
      instances keep the cells unequal, breaking the certified perfect-
      isomorph reading. => for every pool instance, every differently-
      lettered cell pair's value pair is merge-excluded. Conditional on the
      class being genuine. Dot cells carry no assertion and are never used.

  S2  INDICATOR DISTINCTNESS (secondary; weakest conditionality; NEVER used
      for floor claims). The nine position-0 glyphs read as per-message
      labels. Merging two collapses two labels. Flagged, not floor-bearing.

CENSUS (the V4 audit). Undetermined-glyph occurrences at lettered cells,
split pool / discarded (repair A) / dot, with the pool hits localized to
w-free contexts (cross-triplet bridge instances; West 2 instances).

NULL CALIBRATION. Within-message shuffles preserving per-message multisets:
distribution of S1 exclusion counts over the 1,863 candidate merges, and
per-pair survival probability (the power map: a survivor whose null survival
probability is high survives by weakness, not by evidence).

FLOOR. Conditional minimum alphabet size = 56 + (minimum number of
undetermined-only classes) under the S1+S3 compatibility graph, exact by
branch-and-bound over the 27 undetermined glyphs. Determined glyphs are
pairwise incompatible by proof; a class holds at most one.

PRE-REGISTERED (frozen before corpus contact):
  R1  a floor raise is claimed only from S1+S3, and only for a glyph with
      ZERO surviving partners among all 82 others.
  R2  corpus-derived-ordering curiosity (VectorAddUnique idiom): candidates
      pass only on skeleton_ok (selectivity ~1e-78). Expected passes: 0.
  R3  "evidence FOR mergeability" claimed only if the observed S1 exclusion
      count falls below the null 5th percentile. Otherwise the verdict is
      power-limited, stated as such.

All exceptions carry the prefix XD-MBYG04K-URS3LF. stdlib only.
"""

import json, os, random, re, sys
from collections import Counter

XD = "XD-MBYG04K-URS3LF"
N = 83
HERE = os.path.dirname(os.path.abspath(__file__))

UNDET = frozenset({2,11,43,29,8,15,70,22,31,3,24,51,61,65,77,36,69,33,56,58,
                   76,28,38,82,12,53,52})
DET = frozenset(range(N)) - UNDET
DISCARDED = {("#M-", "East 3", 101), ("#M", "East 1", 68)}   # repair A
INDIC_DOCTRINE = {"East 1": 50, "West 1": 80, "East 3": 63,
                  "West 3": 34, "East 4": 27}                 # FR43

# ---------------------------------------------------------------- loading

def load_corpus(path=None):
    p = path or os.path.join(HERE, "corpus.json")
    d = json.load(open(p))
    M = dict(zip(d["message_labels"], d["ciphertexts"]))
    if sum(len(v) for v in M.values()) != 1036:
        raise RuntimeError(f"{XD} corpus length != 1036")
    return d["message_labels"], M

def load_atlas(path=None):
    p = path or os.path.join(HERE, "atlas.json")
    return json.load(open(p))["classes"]

def load_runner():
    """Import eyerunner for skeleton_ok / drift_of / canary machinery."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "eyerunner", os.path.join(HERE, "eyerunner.py"))
    er = importlib.util.module_from_spec(spec)
    argv, sys.argv = sys.argv, ["eyerunner.py"]
    try:
        spec.loader.exec_module(er)
    except SystemExit:
        pass
    finally:
        sys.argv = argv
    return er

# ---------------------------------------------------------------- screens

def adjacency_counts(M):
    """Unordered value-pair -> number of adjacent occurrences, per message
    stream. Also returns (slots, same-value doubles)."""
    adj = Counter(); slots = 0; doubles = 0
    for ct in M.values():
        for t in range(len(ct) - 1):
            x, y = ct[t], ct[t + 1]; slots += 1
            if x == y: doubles += 1
            adj[(min(x, y), max(x, y))] += 1
    return adj, slots, doubles

def s3_pairs(classes, M, include_discarded=False):
    """Value pairs excluded by same-instance exactness: differently-lettered
    cells of one pool instance."""
    out = Counter()
    for cls in classes:
        pat = cls["pattern"]; L = cls["length"]
        lettered = [i for i, ch in enumerate(pat) if ch != "."]
        for it in cls["instances"]:
            key = (cls["id"], it["message"], it["start"])
            if not include_discarded and key in DISCARDED:
                continue
            vals = M[it["message"]][it["start"]:it["start"] + L]
            for a in range(len(lettered)):
                for b in range(a + 1, len(lettered)):
                    i, j = lettered[a], lettered[b]
                    if pat[i] == pat[j]:
                        if vals[i] != vals[j]:
                            raise RuntimeError(
                                f"{XD} atlas same-letter violated: {key} "
                                f"cells {i},{j} letter {pat[i]} carry "
                                f"{vals[i]} != {vals[j]}")
                    else:
                        va, vb = vals[i], vals[j]
                        if va == vb:
                            raise RuntimeError(
                                f"{XD} atlas exactness violated: {key} "
                                f"cells {i},{j} letters {pat[i]}{pat[j]} "
                                f"share value {va}")
                        out[(min(va, vb), max(va, vb))] += 1
    return out

def census(classes, M):
    """Undetermined occurrences at lettered cells: pool vs discarded vs dot."""
    c = {g: {"lettered": 0, "lettered_disc": 0, "dot": 0} for g in UNDET}
    locs = []
    for cls in classes:
        pat = cls["pattern"]; L = cls["length"]
        for it in cls["instances"]:
            key = (cls["id"], it["message"], it["start"])
            disc = key in DISCARDED
            vals = M[it["message"]][it["start"]:it["start"] + L]
            for i, ch in enumerate(pat):
                g = vals[i]
                if g not in UNDET: continue
                if ch == ".":
                    c[g]["dot"] += 1
                elif disc:
                    c[g]["lettered_disc"] += 1
                else:
                    c[g]["lettered"] += 1
                    locs.append((g, cls["id"], it["message"], it["start"], i, ch))
    return c, locs

# ---------------------------------------------------------------- null

def shuffle_within(M, rng):
    return {lab: rng.sample(ct, len(ct)) for lab, ct in M.items()}

def s1_excluded_set(adj, cand):
    return {p for p in cand if adj.get(p, 0) > 0}

def candidate_pairs():
    cand = set()
    for u in UNDET:
        for d in DET:
            cand.add((min(u, d), max(u, d)))
    us = sorted(UNDET)
    for i in range(len(us)):
        for j in range(i + 1, len(us)):
            cand.add((us[i], us[j]))
    return cand

# ---------------------------------------------------------------- floor

def min_extra_classes(undet, compat, limit=200000):
    """Exact minimum number of undetermined-only classes, by DFS with
    memo-free branch and bound. Each undetermined glyph is either attached
    to a determined glyph's class (at most one per determined glyph is NOT
    required -- several u's may share one determined class if pairwise
    compatible and each compatible with that determined glyph) or grouped
    into undetermined-only cliques. Returns (min_extra, nodes_visited)."""
    us = sorted(undet)
    best = [len(us) + 1]; visited = [0]

    def ok_group(group, x):
        return all(compat(x, y) for y in group)

    def dfs(idx, det_groups, u_groups):
        visited[0] += 1
        if visited[0] > limit:
            raise RuntimeError(f"{XD} floor search exceeded node limit")
        if len(u_groups) >= best[0]:
            return
        if idx == len(us):
            best[0] = min(best[0], len(u_groups))
            return
        x = us[idx]
        # attach to an existing determined-anchored group
        for g in det_groups:
            if compat(x, g[0]) and ok_group(g[1], x):
                g[1].append(x); dfs(idx + 1, det_groups, u_groups); g[1].pop()
        # open a new determined-anchored group
        for d in sorted(DET):
            if compat(x, d):
                det_groups.append((d, [x]))
                dfs(idx + 1, det_groups, u_groups)
                det_groups.pop()
                break   # symmetric: first workable anchor suffices to witness 0-cost
        # join an undetermined-only group
        for g in u_groups:
            if ok_group(g, x):
                g.append(x); dfs(idx + 1, det_groups, u_groups); g.pop()
        # open a new undetermined-only group
        u_groups.append([x]); dfs(idx + 1, det_groups, u_groups); u_groups.pop()

    dfs(0, [], [])
    return best[0], visited[0]

# ---------------------------------------------------------------- selftest

def selftest():
    checks = []
    def ck(name, cond, detail=""):
        checks.append((name, bool(cond), detail))
        if not cond:
            raise RuntimeError(f"{XD} selftest FAILED: {name} {detail}")

    labels, M = load_corpus()
    classes = load_atlas()

    # T1 corpus integrity
    adj, slots, doubles = adjacency_counts(M)
    vals = set(v for ct in M.values() for v in ct)
    ck("t1_corpus", len(labels) == 9 and slots == 1027 and doubles == 0
       and vals == set(range(N)), f"slots={slots} doubles={doubles}")

    # T2/T3 S1 plants
    plant = {"A": [5, 7, 5, 7], "B": [9, 3, 9, 3]}
    padj, _, _ = adjacency_counts(plant)
    ck("t2_s1_fires", (5, 7) in s1_excluded_set(padj, {(5, 7)}), "")
    ck("t3_s1_survives", (5, 9) not in s1_excluded_set(padj, {(5, 9)}),
       "5,9 never adjacent in plant")

    # T4 census machinery on a planted class
    pm = {"X": [2, 11, 2, 11, 40]}
    pcls = [{"id": "#P", "pattern": "A.A.B", "length": 5,
             "instances": [{"message": "X", "start": 0}]}]
    cc, locs = census(pcls, pm)
    ck("t4_census", cc[2]["lettered"] == 2 and cc[11]["dot"] == 2
       and len(locs) == 2, f"{cc[2]} {cc[11]}")

    # T5 S3 machinery: diff-letter pair excluded, same-letter/dot not
    p3 = s3_pairs(pcls, pm)
    ck("t5_s3", (2, 40) in p3 and p3[(2, 40)] == 2 and (2, 2) not in p3
       and (2, 11) not in p3 and (11, 40) not in p3, str(dict(p3)))

    # both exactness guards fire on bad plants
    bad = [{"id": "#B", "pattern": "AB", "length": 2,
            "instances": [{"message": "X", "start": 1}]}]
    badm = {"X": [0, 6, 6]}                                  # A=B equal: BAD
    try:
        s3_pairs(bad, badm); ck("t5b_guard_diff", False, "guard silent")
    except RuntimeError:
        ck("t5b_guard_diff", True, "fires on planted A=B equality")
    bad2 = [{"id": "#B2", "pattern": "AA", "length": 2,
             "instances": [{"message": "X", "start": 1}]}]
    badm2 = {"X": [0, 6, 7]}                                 # A cells differ: BAD
    try:
        s3_pairs(bad2, badm2); ck("t5c_guard_same", False, "guard silent")
    except RuntimeError:
        ck("t5c_guard_same", True, "fires on planted same-letter mismatch")

    # T6 null shuffle: multisets preserved, seeded determinism
    r1, r2 = random.Random(97), random.Random(97)
    sA, sB = shuffle_within(M, r1), shuffle_within(M, r2)
    ck("t6_null", all(Counter(sA[l]) == Counter(M[l]) for l in labels)
       and sA == sB, "")

    # T7 indicators match doctrine
    ind = {lab: M[lab][0] for lab in labels}
    ck("t7_indicators", all(ind[k] == v for k, v in INDIC_DOCTRINE.items()),
       str(ind))

    # T8 floor solver plants
    allc = lambda a, b: True
    e0, _ = min_extra_classes({1, 2, 3}, allc)
    ck("t8a_floor_allcompat", e0 == 0, f"extra={e0}")
    iso = lambda a, b: False
    e1, _ = min_extra_classes({1, 2}, iso)
    ck("t8b_floor_isolated", e1 == 2, f"extra={e1}")
    # two u's sharing nothing with det (iso to det), compatible together
    semi = lambda a, b: (a in {12, 53} and b in {12, 53})
    e2, _ = min_extra_classes({12, 53}, semi)
    ck("t8c_floor_pairup", e2 == 1, f"extra={e2}")

    # T9 skeleton_ok via eyerunner: canary passes, transposition fails
    er = load_runner()
    can = er.build_canaries(1, random.Random(5))[0]
    ck("t9a_skel_canary", er.skeleton_ok(can), "")
    bad = list(can); bad[0], bad[1] = bad[1], bad[0]
    ck("t9b_skel_reject", not er.skeleton_ok(bad), "")

    for n, p, d in checks:
        print(f"  {n:24s} {'PASS' if p else 'FAIL'} {d}")
    print(f"selftest {sum(1 for _,p,_ in checks if p)}/{len(checks)} green")
    return True

# ---------------------------------------------------------------- corpus run

def corpus_run(draws=2000, seed=20260726):
    labels, M = load_corpus()
    classes = load_atlas()
    er = load_runner()
    rng = random.Random(seed)

    print("=" * 72)
    print("EYEMERGE corpus run -- pre-registered R1/R2/R3 in module docstring")
    print("=" * 72)

    # ---- census (the V4 audit)
    cc, locs = census(classes, M)
    tot_let = sum(v["lettered"] for v in cc.values())
    tot_disc = sum(v["lettered_disc"] for v in cc.values())
    tot_dot = sum(v["dot"] for v in cc.values())
    print(f"\n[CENSUS] undetermined at lettered cells: pool={tot_let} "
          f"discarded={tot_disc} dots={tot_dot}")
    for g, cid, lab, s, off, ch in locs:
        print(f"  pool hit: glyph {g} in {cid} {lab}@{s} offset {off} "
              f"letter {ch}")

    # ---- screens
    cand = candidate_pairs()
    adj, slots, doubles = adjacency_counts(M)
    s1 = s1_excluded_set(adj, cand)
    s3all = s3_pairs(classes, M)
    s3 = {p for p in s3all if p in cand}
    s3_detdet = {p for p in s3all if p[0] in DET and p[1] in DET}
    indic = {M[lab][0] for lab in labels}
    s2 = {p for p in cand if p[0] in indic and p[1] in indic}

    du = sorted(p for p in cand if (p[0] in DET) != (p[1] in DET))
    uu = sorted(p for p in cand if p[0] in UNDET and p[1] in UNDET)
    print(f"\n[SCREENS] candidates: {len(cand)} "
          f"(det x undet {len(du)}, undet x undet {len(uu)})")
    print(f"  S1 adjacency excluded : {len(s1):4d} "
          f"({sum(1 for p in s1 if p in set(du))} du, "
          f"{sum(1 for p in s1 if p in set(uu))} uu)")
    print(f"  S3 exactness excluded : {len(s3):4d}  "
          f"pairs: {sorted(s3)}")
    print(f"  S3 det-det (consistency, already proven distinct): "
          f"{len(s3_detdet)}")
    print(f"  S2 indicator flagged  : {len(s2):4d}  (not floor-bearing)")
    hard = s1 | s3
    print(f"  S1 u S3 (floor-bearing): {len(hard)}  "
          f"union with S2: {len(hard | s2)}")

    # ---- per-glyph survivor profile
    print(f"\n[PROFILE] per undetermined glyph: surviving determined "
          f"partners of 56 (S1+S3)")
    freq = Counter(v for ct in M.values() for v in ct)
    iso_glyphs = []
    for u in sorted(UNDET):
        sd = sum(1 for d in DET if (min(u, d), max(u, d)) not in hard)
        su = sum(1 for w in UNDET if w != u
                 and (min(u, w), max(u, w)) not in hard)
        if sd + su == 0: iso_glyphs.append(u)
        print(f"  glyph {u:2d} (freq {freq[u]:2d}): det-survivors {sd:2d}  "
              f"undet-survivors {su:2d}")

    # ---- floor (R1)
    compat = lambda a, b: (min(a, b), max(a, b)) not in hard
    extra, nodes = min_extra_classes(UNDET, compat)
    print(f"\n[FLOOR] R1: fully-isolated glyphs (0 survivors of 82): "
          f"{iso_glyphs or 'none'}")
    print(f"  exact min undetermined-only classes: {extra} "
          f"(search nodes {nodes})")
    print(f"  conditional minimum alphabet size: {56 + extra}")

    # ---- null calibration (R3)
    obs = len(s1)
    null_counts = []
    for _ in range(draws):
        sm = shuffle_within(M, rng)
        nadj, _, _ = adjacency_counts(sm)
        null_counts.append(len(s1_excluded_set(nadj, cand)))
    null_counts.sort()
    mu = sum(null_counts) / draws
    sd = (sum((x - mu) ** 2 for x in null_counts) / (draws - 1)) ** 0.5
    p05 = null_counts[int(0.05 * draws)]
    z = (obs - mu) / sd if sd else float("nan")
    print(f"\n[NULL] S1 exclusions: observed {obs}  null mu={mu:.1f} "
          f"sd={sd:.2f}  5th pct={p05}  z={z:+.2f}  draws={draws}")
    print(f"  R3 verdict: "
          f"{'BELOW 5th pct -- evidence for mergeability' if obs < p05 else 'within null -- power-limited, no evidence either way'}")

    # per-pair survival probability (power map) on a subsample of draws
    surv = Counter()
    sub = min(500, draws)
    rng2 = random.Random(seed + 1)
    for _ in range(sub):
        sm = shuffle_within(M, rng2)
        nadj, _, _ = adjacency_counts(sm)
        for p in cand:
            if nadj.get(p, 0) == 0:
                surv[p] += 1
    surv_p = {p: surv[p] / sub for p in cand}
    survivors = [p for p in cand if p not in hard]
    informative = [p for p in survivors if surv_p[p] < 0.5]
    print(f"  survivors {len(survivors)}; with null-survival p<0.5 "
          f"(informative): {len(informative)}")
    exp_surv = sum(surv_p[p] for p in cand)
    print(f"  expected survivors if NO merge is real: {exp_surv:.1f} "
          f"(observed {len(survivors)})")

    # ---- corpus-derived orderings (R2 curiosity; VectorAddUnique idiom)
    stream = []
    for lab in labels: stream.extend(M[lab])
    firsts = list(dict.fromkeys(stream))
    lasts = list(dict.fromkeys(reversed(stream)))
    byfreq = [g for g, _ in freq.most_common()]
    inv = lambda p: [p.index(i) for i in range(N)]
    cands = {"first_occurrence": firsts, "first_occ_rev": firsts[::-1],
             "first_occ_inv": inv(firsts), "last_occurrence": lasts,
             "freq_desc": byfreq, "freq_asc": byfreq[::-1],
             "freq_inv": inv(byfreq)}
    hits = {k: er.skeleton_ok(v) for k, v in cands.items()}
    print(f"\n[R2] corpus-derived orderings through skeleton_ok "
          f"(~1e-78): {sum(hits.values())}/{len(hits)} pass "
          f"{'-- ' + str([k for k,v in hits.items() if v]) if any(hits.values()) else '(expected 0)'}")

    return dict(census=(tot_let, tot_disc, tot_dot), s1=len(s1),
                s3=sorted(s3), s2=len(s2), floor=56 + extra,
                iso=iso_glyphs, z=z, survivors=len(survivors),
                expected_survivors=exp_surv)

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        selftest()
        corpus_run()
