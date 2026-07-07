#!/usr/bin/env python3
"""order_gate.py — Priority-1 two-crib **order-overlap gate** for the Noita eyes.

WHAT THIS IS
------------
The alphabet *links but does not order* (`iso_relax` exports ~16 sound pins;
`support_min` needs ~22 to converge, 100% by ~40).  Two overlapping crib targets
exist, and each — placed under the live linear class — pins the value->position
map `q = C^{-1}` for the symbols it reaches, **up to one global rotation**
(per-message base is free; see cribscan/passread.py and noita_eye_core/refrain.py):

    c_m[t] = C[(sigma*p_m[t] + base_m + drift*t) mod N],   N = 83, sigma in {+1,-1},
    drift in {+1,0,-1};   q[c_m[t]] = sigma*p_m[t] + base_m + drift*t.

  * T1  — the 4x refrain     (West1@32/@62, East2@37/@72), L=22
  * T3  — the Triplet-3 dof-1 passage (East4@50, West4@52, East5@51), L=30

On THIS corpus the two targets share **31 distinct cipher symbols** and their
union covers **69 of 83 (83.1%)** — computable from the ciphertext alone
(`--real`).  A correct (T1-phrase, T3-phrase) pair therefore imposes **31 hard
equality checks** and, if it passes, welds to a 69-symbol map — past
`support_min`'s floor.

THE GATE
--------
Place a crib on each target under ONE joint hypothesis (T1 phrase, T3 phrase,
plaintext-alphabet ordering `inj`, sigma, drift).  Each yields a partial map
`q_A[sym]`, `q_B[sym]`, each in its own base-0 gauge, i.e. each equals the true
`q[sym]` plus a per-map constant.  Hence on the overlap:

    q_A[sym] - q_B[sym]  ==  (const_A - const_B)  ==  a SINGLE delta, for all sym.

**Gate = that delta set is a singleton.**  A wrong pair scatters the deltas and is
rejected; a correct pair passes, and the common delta welds B into A's gauge,
producing one map over the union of reached symbols (still up to one global
rotation, resolved downstream by IoC — which is invariant to the base AND the
rotation, so no gauge resolution is needed for the success signal).

Because per-target value-mode placement is already sharp (a wrong phrase whose
repeat structure violates the ciphertext's keystream collisions self-contradicts),
the gate's role is threefold: (1) confirm a JOINT hypothesis across two committed
targets, (2) weld two partial maps into one, (3) resolve the single-target rotation
freedom.  See `selftest()` for the calibrated evidence (correct -> weld -> read;
wrong -> reject; 0 false positives over thousands of random candidates).

ATLAS SEED (optional coverage extension)
----------------------------------------
`isomorph_atlas.json` (13 verified, ranked classes) supplies more same-plaintext
alignments.  Within a class, two instances A,B satisfy
`q[symA_i] - q[symB_i] = const` for all aligned i.  Once the cribs pin one aligned
pair, that constant is solved and propagates to pin the partner symbols at every
other aligned index — pushing reachable coverage from 69 toward 82/83 (98.8%).
Restricted to Tier A/B and gated on cross-index consistency (contamination guard).

GUARDRAIL (honoring the repo's own retraction)
----------------------------------------------
This tool reports *linkage/coverage* and a *readability z*.  It does NOT mint
"certified ordered pins" — those come only from `eyeforward/iso_relax`.  A gate
pass with a high corpus IoC z is a strong candidate to hand to `iso_relax`, not a
final claim.

    python order_gate.py --selftest      # plant-backed validation (no corpus needed)
    python order_gate.py --real          # real-corpus overlap/coverage report
    python order_gate.py --demo          # run the gate over tiny candidate lists
"""
from __future__ import annotations
import sys, os, json, argparse, random, math
from collections import defaultdict

ERROR_PREFIX = "Internal Error Code: order-gate"
N = 83
ALPHA = "abcdefghijklmnopqrstuvwxyzäö"          # 28-symbol injection base

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for c in (HERE, ROOT, os.path.join(ROOT, "noita_eye_core")):
    if c not in sys.path:
        sys.path.insert(0, c)

import numpy as np
from passread import rref, solve_gauge          # reuse the exact linear-algebra conventions

# --------------------------------------------------------------------------- #
# Target registry (message label, start).  Extents are the repo's certified ones.
# --------------------------------------------------------------------------- #
LABELS = ["East 1", "West 1", "East 2", "West 2", "East 3",
          "West 3", "East 4", "West 4", "East 5"]
REFRAIN_INST = [("West 1", 32), ("West 1", 62), ("East 2", 37), ("East 2", 72)]
REFRAIN_L = 22
T3_INST = [("East 4", 50), ("West 4", 52), ("East 5", 51)]
T3_L = 30
T3_OPEN_INST = [("East 4", 2), ("West 4", 2), ("East 5", 2)]
T3_OPEN_L = 18


# --------------------------------------------------------------------------- #
# Core: place a crib, return the glyph->position map (mirrors passread.place_crib
# but EXPOSES qrel, which the gate needs).
# --------------------------------------------------------------------------- #
def crib_map(ct_by_label, labels, instances, plain, offset, drift, sign, inj):
    """Return (qrel: {cipher_sym -> q value in base-0 gauge}, contradiction: bool,
    bases: {m -> B_m}).  qrel is pinned relative to instance-0's base (== 0)."""
    idx = {l: i for i, l in enumerate(labels)}
    occ = []
    for m, (lab, s) in enumerate(instances):
        row = ct_by_label[idx[lab]]
        for j, ch in enumerate(plain):
            if ch not in inj:
                continue
            t = s + offset + j
            if 0 <= t < len(row):
                occ.append((m, t, inj[ch]))
    if not occ:
        return {}, False, {}
    syms = sorted({ct_by_label[idx[instances[m][0]]][t] for (m, t, _) in occ})
    symcol = {sy: k for k, sy in enumerate(syms)}
    M = len(instances)
    nc = len(syms) + M
    Bc = lambda m: len(syms) + m
    rows = []
    for (m, t, val) in occ:
        r = np.zeros(nc + 1, dtype=np.int64)
        sym = ct_by_label[idx[instances[m][0]]][t]
        r[symcol[sym]] = 1
        r[Bc(m)] = (-1) % N
        r[nc] = (sign * val + drift * t) % N
        rows.append(r)
    A = np.array(rows, dtype=np.int64) % N
    Rc, _ = rref(A)
    contradiction = any((row[:nc] % N == 0).all() and row[nc] % N for row in Rc)
    sol, _ = solve_gauge(A, nc, Bc(0))
    qrel = {syms[c]: v for c, v in sol.items() if c < len(syms)}
    bases = {m: sol.get(Bc(m), 0) for m in range(M)}
    return qrel, contradiction, bases


# --------------------------------------------------------------------------- #
# The gate + weld
# --------------------------------------------------------------------------- #
def overlap_gate(qA, qB):
    """Cross-target overlap-consistency gate.  Returns a dict with pass/delta/
    overlap/n_deltas.  PASS iff every shared symbol yields the same delta."""
    overlap = set(qA) & set(qB)
    deltas = {(qA[s] - qB[s]) % N for s in overlap}
    return {
        "pass": (len(overlap) > 0 and len(deltas) == 1),
        "delta": (next(iter(deltas)) if len(deltas) == 1 else None),
        "overlap": len(overlap),
        "n_deltas": len(deltas),
    }


def weld(qA, qB, delta):
    """Merge B (shifted by +delta) into A's gauge.  None on any residual clash."""
    merged = dict(qA)
    for s, v in qB.items():
        vv = (v + delta) % N
        if s in merged and merged[s] != vv:
            return None
        merged[s] = vv
    return merged


# --------------------------------------------------------------------------- #
# Corpus-wide success signal: per-message IoC of the pinned positions vs a
# shuffle null.  Invariant to per-message base AND to the global rotation
# (both are constant shifts); drift is known and subtracted explicitly.
# --------------------------------------------------------------------------- #
def _ioc(vals):
    if len(vals) < 2:
        return 0.0
    cnt = defaultdict(int)
    for v in vals:
        cnt[v] += 1
    L = len(vals)
    return sum(c * (c - 1) for c in cnt.values()) / (L * (L - 1))


def per_message_ioc(messages, qmap, drift, sign, min_dec=8):
    vals_per_msg = []
    for m in messages:
        d = [(sign * (qmap[int(c)] - drift * t)) % N
             for t, c in enumerate(m) if int(c) in qmap]
        if len(d) >= min_dec:
            vals_per_msg.append(_ioc(d))
    return sum(vals_per_msg) / len(vals_per_msg) if vals_per_msg else 0.0


def corpus_ioc_z(messages, qmap, drift, sign, n_null=300, seed=0):
    obs = per_message_ioc(messages, qmap, drift, sign)
    rng = np.random.default_rng(seed)
    syms = sorted(qmap)
    vals = [qmap[s] for s in syms]
    nulls = []
    for _ in range(n_null):
        perm = list(vals)
        rng.shuffle(perm)
        shuffled = {s: perm[i] for i, s in enumerate(syms)}
        nulls.append(per_message_ioc(messages, shuffled, drift, sign))
    nm = float(np.mean(nulls)) if nulls else 0.0
    nsd = float(np.std(nulls)) if nulls else 1e-9
    return {"ioc": obs, "null_mean": nm, "null_sd": nsd, "z": (obs - nm) / (nsd + 1e-9)}


# --------------------------------------------------------------------------- #
# Atlas seed: extend a welded map via same-plaintext class alignments.
# --------------------------------------------------------------------------- #
def _atlas_instances(atlas, tiers=("A", "B")):
    """Yield per-class lists of instance value-sequences, restricted to tiers."""
    for cl in atlas["classes"]:
        if cl.get("tier") in tiers:
            yield cl["id"], [inst["values"] for inst in cl["instances"]]


def extend_with_atlas(merged, atlas, tiers=("A", "B"), require_consistent=True):
    """Propagate q from a welded crib map across atlas same-plaintext alignments.

    For instances A,B of a class, q[symA_i]-q[symB_i] is a constant d over aligned
    i.  Solve d from any aligned index with BOTH sides pinned, then pin partners at
    all other indices.  Iterate to a fixed point.  Returns (extended_map, report)."""
    ext = dict(merged)
    added_total = 0
    skipped = 0
    changed = True
    while changed:
        changed = False
        for cid, insts in _atlas_instances(atlas, tiers):
            for a in range(len(insts)):
                for b in range(len(insts)):
                    if a == b:
                        continue
                    va, vb = insts[a], insts[b]
                    L = min(len(va), len(vb))
                    # measure d from indices where both pinned
                    measured = {(ext[va[i]] - ext[vb[i]]) % N
                                for i in range(L) if va[i] in ext and vb[i] in ext}
                    if len(measured) == 0:
                        continue
                    if require_consistent and len(measured) > 1:
                        skipped += 1          # misalignment guard: inconsistent d
                        continue
                    d = next(iter(measured))
                    for i in range(L):
                        if va[i] in ext and vb[i] not in ext:
                            ext[vb[i]] = (ext[va[i]] - d) % N
                            added_total += 1
                            changed = True
    return ext, {"added": added_total, "pairs_skipped_inconsistent": skipped,
                 "coverage": len(ext)}


# --------------------------------------------------------------------------- #
# Driver: run the gate over candidate phrase lists for the two targets.
# --------------------------------------------------------------------------- #
def run_gate(messages, labels, t1_phrases, t3_phrases, inj, sign, drift,
             atlas=None, n_null=300, min_overlap=8, verbose=False):
    ct_by_label = [list(m) for m in messages]
    results = []
    # pre-place each target's candidates once (single-target consistency filter)
    t1_maps = {}
    for p in t1_phrases:
        q, contra, _ = crib_map(ct_by_label, labels, REFRAIN_INST, p, 0, drift, sign, inj)
        if q and not contra:
            t1_maps[p] = q
    t3_maps = {}
    for p in t3_phrases:
        q, contra, _ = crib_map(ct_by_label, labels, T3_INST, p, 0, drift, sign, inj)
        if q and not contra:
            t3_maps[p] = q
    for p1, qA in t1_maps.items():
        for p3, qB in t3_maps.items():
            g = overlap_gate(qA, qB)
            if not g["pass"] or g["overlap"] < min_overlap:
                continue
            merged = weld(qA, qB, g["delta"])
            if merged is None:
                continue
            cov = len(merged)
            if atlas is not None:
                merged, arep = extend_with_atlas(merged, atlas)
                cov = arep["coverage"]
            z = corpus_ioc_z(messages, merged, drift, sign, n_null=n_null)
            results.append({"t1": p1, "t3": p3, "overlap": g["overlap"],
                            "coverage": cov, "ioc": z["ioc"], "z": z["z"]})
    results.sort(key=lambda r: -r["z"])
    return results


# --------------------------------------------------------------------------- #
# Plant lab (ground truth) + selftest
# --------------------------------------------------------------------------- #
def make_joint_plant(seed, sign=1, drift=1, pure=False, mlen=125, extra_class=True):
    """Plant a 9-message corpus that contains BOTH the T1 refrain and the T3 dof-1
    passage as shared plaintext (so their reached symbols overlap), plus one extra
    shared segment usable as a synthetic atlas class."""
    rng = random.Random(seed)
    C = list(range(N)); rng.shuffle(C)
    inj = {ch: i for i, ch in enumerate(ALPHA)}
    inv = {v: k for k, v in inj.items()}
    base = {lab: (0 if pure else rng.randrange(N)) for lab in LABELS}
    P = {lab: [rng.randrange(len(ALPHA)) for _ in range(mlen)] for lab in LABELS}
    ref_pt = [rng.randrange(len(ALPHA)) for _ in range(REFRAIN_L)]
    t3_pt = [rng.randrange(len(ALPHA)) for _ in range(T3_L)]
    for lab, s in REFRAIN_INST:
        P[lab][s:s + REFRAIN_L] = ref_pt
    for lab, s in T3_INST:
        P[lab][s:s + T3_L] = t3_pt
    # synthetic atlas class: a 16-long shared segment across 3 other placements,
    # positioned so one instance overlaps already-reachable symbols.
    atlas_obj = None
    if extra_class:
        seg = [rng.randrange(len(ALPHA)) for _ in range(16)]
        seg_inst = [("East 1", 40), ("West 3", 20), ("East 3", 60)]
        for lab, s in seg_inst:
            P[lab][s:s + 16] = seg
    ct = {lab: [C[(sign * P[lab][t] + base[lab] + drift * t) % N] for t in range(mlen)]
          for lab in LABELS}
    messages = [ct[l] for l in LABELS]
    if extra_class:
        insts = []
        for lab, s in seg_inst:
            insts.append({"values": [ct[lab][s + i] for i in range(16)]})
        atlas_obj = {"classes": [{"id": "#SYN", "tier": "A", "instances": insts}]}
    ref_str = "".join(inv[v] for v in ref_pt)
    t3_str = "".join(inv[v] for v in t3_pt)
    truth = {"C": C, "base": base, "P": P}
    return messages, inj, ref_str, t3_str, atlas_obj, truth


def _read_accuracy(messages, qmap, truth, sign, drift):
    """Fraction of pinned positions decrypted to the correct plant plaintext,
    after resolving the single global rotation against ground truth."""
    q_true = {c: i for i, c in enumerate(truth["C"])}
    rots = {(qmap[s] - q_true[s]) % N for s in qmap if s in q_true}
    rot_ok = (len(rots) == 1)
    rot = next(iter(rots)) if rots else 0
    correct = tot = 0
    for li, lab in enumerate(LABELS):
        for t, c in enumerate(messages[li]):
            if c in qmap:
                p = (sign * ((qmap[c] - rot) - truth["base"][lab] - drift * t)) % N
                tot += 1
                correct += (p == truth["P"][lab][t])
    return rot_ok, (correct / tot if tot else 0.0), tot


def selftest():
    out = []
    def check(name, cond):
        out.append((name, bool(cond)))

    messages, inj, ref_str, t3_str, atlas_obj, truth = make_joint_plant(7)
    inv = {v: k for k, v in inj.items()}
    ct_by_label = [list(m) for m in messages]

    # 1) correct pair: no contradiction, gate passes, welds, reads 100%, z high
    qA, cA, _ = crib_map(ct_by_label, LABELS, REFRAIN_INST, ref_str, 0, 1, 1, inj)
    qB, cB, _ = crib_map(ct_by_label, LABELS, T3_INST, t3_str, 0, 1, 1, inj)
    check("correct T1 consistent", qA and not cA)
    check("correct T3 consistent", qB and not cB)
    g = overlap_gate(qA, qB)
    check("gate passes on correct pair", g["pass"])
    check("overlap >= 20 hard checks", g["overlap"] >= 20)
    merged = weld(qA, qB, g["delta"])
    check("weld succeeds", merged is not None)
    check("welded coverage >= 60 symbols", merged and len(merged) >= 60)
    rot_ok, acc, tot = _read_accuracy(messages, merged, truth, 1, 1)
    check("single global rotation", rot_ok)
    check("corpus read accuracy == 1.0", acc == 1.0)
    z = corpus_ioc_z(messages, merged, 1, 1, n_null=200)
    check("corpus IoC z > 8 on correct", z["z"] > 8)

    # 2) self-inconsistent guess is killed before the gate
    rr = random.Random(1)
    scr = "".join(inv[rr.randrange(len(ALPHA))] for _ in range(REFRAIN_L))
    _, cbad, _ = crib_map(ct_by_label, LABELS, REFRAIN_INST, scr, 0, 1, 1, inj)
    check("scrambled refrain contradicts", cbad)

    # 3) statistical: wrong T3 candidates NEVER survive the cross-gate vs correct T1
    rng = random.Random(99)
    survived = tested = 0
    for _ in range(2000):
        cand = "".join(inv[rng.randrange(len(ALPHA))] for _ in range(T3_L))
        qc, cc, _ = crib_map(ct_by_label, LABELS, T3_INST, cand, 0, 1, 1, inj)
        if not qc or cc:
            continue
        tested += 1
        gg = overlap_gate(qA, qc)
        if gg["pass"] and gg["overlap"] >= 8:
            survived += 1
    check("zero false positives over random T3 candidates", survived == 0)

    # 4) isomorph-preserving relabel (passes pattern-mode) is rejected
    perm = list(range(len(ALPHA)))
    rng.shuffle(perm)
    while all((perm[i] - perm[0]) % len(ALPHA) == i % len(ALPHA) for i in range(len(ALPHA))):
        rng.shuffle(perm)
    iso_wrong = "".join(inv[perm[inj[ch]]] for ch in t3_str)
    qiw, ciw, _ = crib_map(ct_by_label, LABELS, T3_INST, iso_wrong, 0, 1, 1, inj)
    rejected = ciw or (not overlap_gate(qA, qiw)["pass"])
    check("isomorph-preserving wrong T3 rejected", rejected)

    # 5) atlas seed extends coverage on the plant
    if atlas_obj is not None:
        base_cov = len(merged)
        ext, arep = extend_with_atlas(merged, atlas_obj)
        check("atlas seed adds coverage", arep["coverage"] > base_cov)
        # extended pins must still be correct
        rot_ok2, acc2, tot2 = _read_accuracy(messages, ext, truth, 1, 1)
        check("atlas-extended pins still read 100%", acc2 == 1.0)

    # 6) real-corpus overlap/coverage sanity (if corpus present)
    cp = os.path.join(ROOT, "noita_eye_core", "corpus.json")
    if os.path.exists(cp):
        cj = json.load(open(cp))
        rl = cj["message_labels"]; rm = [list(m) for m in cj["ciphertexts"]]
        ridx = {l: i for i, l in enumerate(rl)}
        def reach(instances, L):
            S = set()
            for lab, s in instances:
                row = rm[ridx[lab]]
                for t in range(s, min(s + L, len(row))):
                    S.add(row[t])
            return S
        R1 = reach(REFRAIN_INST, REFRAIN_L); R3 = reach(T3_INST, T3_L)
        check("real T1 reaches 52 symbols", len(R1) == 52)
        check("real T3 reaches 48 symbols", len(R3) == 48)
        check("real overlap == 31 hard checks", len(R1 & R3) == 31)
        check("real union covers >= 83%", len(R1 | R3) / N >= 0.83)
    return out


# --------------------------------------------------------------------------- #
def _demo():
    """Tiny end-to-end demo on a plant: feed candidate lists incl. the truth."""
    messages, inj, ref_str, t3_str, atlas_obj, _ = make_joint_plant(7)
    inv = {v: k for k, v in inj.items()}
    rng = random.Random(3)
    def rand_phrase(L):
        return "".join(inv[rng.randrange(len(ALPHA))] for _ in range(L))
    t1_cands = [ref_str] + [rand_phrase(REFRAIN_L) for _ in range(6)]
    t3_cands = [t3_str] + [rand_phrase(T3_L) for _ in range(6)]
    res = run_gate(messages, LABELS, t1_cands, t3_cands, inj, 1, 1,
                   atlas=atlas_obj, n_null=200)
    print(f"candidates in: T1={len(t1_cands)} T3={len(t3_cands)}  "
          f"(1 correct each + noise)")
    print(f"pairs surviving gate+weld: {len(res)}")
    for r in res[:5]:
        tag = "  <-- planted truth" if (r["t1"] == ref_str and r["t3"] == t3_str) else ""
        print(f"  overlap={r['overlap']:>2} coverage={r['coverage']:>2} "
              f"IoC={r['ioc']:.4f} z={r['z']:>6.1f}{tag}")


def _real_report():
    cp = os.path.join(ROOT, "noita_eye_core", "corpus.json")
    cj = json.load(open(cp))
    rl = cj["message_labels"]; rm = [list(m) for m in cj["ciphertexts"]]
    ridx = {l: i for i, l in enumerate(rl)}
    def reach(instances, L):
        S = set()
        for lab, s in instances:
            row = rm[ridx[lab]]
            for t in range(s, min(s + L, len(row))):
                S.add(row[t])
        return S
    R1 = reach(REFRAIN_INST, REFRAIN_L)
    R3 = reach(T3_INST, T3_L)
    RO = reach(T3_OPEN_INST, T3_OPEN_L)
    print("Real-corpus reachability (ciphertext-only, no phrase needed):")
    print(f"  T1 refrain : {len(R1)} symbols")
    print(f"  T3 dof-1   : {len(R3)} symbols")
    print(f"  overlap (hard checks) : {len(R1 & R3)}")
    print(f"  union T1+T3           : {len(R1 | R3)} = {100*len(R1|R3)/N:.1f}%")
    print(f"  union +T3open         : {len(R1 | R3 | RO)} = {100*len(R1|R3|RO)/N:.1f}%")
    ap = os.path.join(ROOT, "isomorph_atlas.json")
    if os.path.exists(ap):
        atlas = json.load(open(ap))
        Aall = set()
        for cl in atlas["classes"]:
            for inst in cl["instances"]:
                Aall.update(inst["values"])
        print(f"  +atlas grand union    : {len(R1 | R3 | RO | Aall)} = "
              f"{100*len(R1|R3|RO|Aall)/N:.1f}%")


def main():
    ap = argparse.ArgumentParser(description="Priority-1 two-crib order-overlap gate")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--real", action="store_true")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        rows = selftest()
        w = max(len(n) for n, _ in rows)
        allok = True
        for n, ok in rows:
            print(f"  [{'PASS' if ok else 'FAIL'}] {n:<{w}}")
            allok &= ok
        print(f"\n{'ALL PASS' if allok else 'FAILURES PRESENT'}  ({sum(o for _,o in rows)}/{len(rows)})")
        sys.exit(0 if allok else 1)
    elif a.real:
        _real_report()
    elif a.demo:
        _demo()
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
