#!/usr/bin/env python3
"""eyegate2.py — GATE 2: order-aware refrain-template admissibility.

WHAT THIS IS
------------
The refrain repeat-template (noita_eye_core/template.py, certified) pins the
22-glyph refrain's relative plaintext to dof=2: beyond the additive gauge and
the free position 7, every pair (i,j) is FORCED to a numeric difference
p[i]-p[j] == g (mod 83).  Gate 2 asks, for a candidate PHRASE and a candidate
ALPHABET ORDER, the question the lag gate could not:

    does there exist ANY embedding v: letters -> Z83 of that cyclic order
    such that the phrase satisfies every forced difference?

CASCADE (each level strictly implies the previous)
  A  same-groups   : phrase[3]==phrase[13], [4]==[5], [10]==[16]
  B  full pattern  : A + all 207 forced-different pairs are different letters
  C  numeric graph : letter-level weighted union-find over
                     v(L[i]) - v(L[j]) == s*g  (s = +-1 sweeps the sigma sign);
                     any letter-pair forced to two deltas -> dead, order-free
  D  embeddability : anchored difference-constraint system (Bellman-Ford,
                     26 nodes): chain P[k+1]-P[k] >= 1 along the order,
                     P[last] <= 82, plus the component equalities from C.
                     Feasible <=> the (phrase, order, s) triple admits a
                     concrete injection.

Levels A-C are order-free; D is where an order earns or loses its keep.
Calibration: C-survivors are tested for D under random orders to give the
candidate order's admission a null.

MODEL SCOPE (honest): inherits the template's model-dependence (per-message-
progressive, drift +1; model_audit flags dof=2 as hypothesis-grade).  sigma is
swept; deck/autokey models are not graded here.

    python3 eyegate2.py --selftest
    python3 eyegate2.py --order BDMAGICKEFHJLNOPQRSTUVWXYZ [--nulls 200]
    python3 eyegate2.py --order ... --phrases myfile.txt
"""
from __future__ import annotations
import sys, os, json, argparse, random, csv
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "noita_eye_core"))
import template as tp                    # certified extractor

N = 83
L = 22
INSTANCES = [(1, 32), (1, 62), (2, 37), (2, 72)]
ERR = "Internal Error Code: XD-GATE2-URS3LF"

# --------------------------------------------------------------------------- #
# template -> forced pair list
# --------------------------------------------------------------------------- #
def load_corpus():
    c = json.load(open(os.path.join(ROOT, "noita_eye_core", "corpus.json")))
    cts = c["ciphertexts"]
    return [cts[l] for l in c["message_labels"]] if isinstance(cts, dict) else list(cts)

def forced_pairs(tmpl):
    """[(i, j, g)] meaning p[i]-p[j] == g (mod N); g==0 from same-groups."""
    out = list(tmpl.diff_pairs)
    for grp in tmpl.same_groups:
        r = grp[0]
        for x in grp[1:]:
            out.append((r, x, 0))
    return out

# --------------------------------------------------------------------------- #
# cascade
# --------------------------------------------------------------------------- #
def gate_A(ph, tmpl):
    return all(len({ph[i] for i in grp}) == 1 for grp in tmpl.same_groups)

def gate_B(ph, tmpl):
    return gate_A(ph, tmpl) and all(ph[i] != ph[j] for i, j, _ in tmpl.diff_pairs)

def gate_C(ph, pairs, s):
    """weighted union-find over letters: v(a)-v(b) == d (mod N).
    returns dict letter -> (root, delta_to_root) or None on contradiction."""
    parent, delta = {}, {}
    def find(x):
        if parent.setdefault(x, x) == x:
            delta.setdefault(x, 0)
            return x, 0
        r, d = find(parent[x])
        parent[x], delta[x] = r, (delta[x] + d) % N
        return r, delta[x]
    for i, j, g in pairs:
        a, b, d = ph[i], ph[j], (s * g) % N     # v(a)-v(b) == d
        ra, da = find(a); rb, db = find(b)
        if ra == rb:
            if (da - db) % N != d:
                return None
        else:
            parent[ra] = rb
            delta[ra] = (d + db - da) % N
    return {x: find(x) for x in parent}

def gate_D(comp, order):
    """difference-constraint feasibility of an order-preserving embedding.
    comp: letter -> (root, delta) with v(letter)-v(root) == delta (mod N)."""
    pos = {c: k for k, c in enumerate(order)}
    n = len(order)
    if any(x not in pos for x in comp):
        return False
    # edges: x_j - x_i <= w  ==>  (i, j, w)
    edges = [(k + 1, k, -1) for k in range(n - 1)]          # P[k+1]-P[k] >= 1
    edges.append((0, n - 1, 82))                            # P[last]-P[0] <= 82
    by_root = defaultdict(list)
    for x, (r, d) in comp.items():
        by_root[r].append((x, d))
    for r, members in by_root.items():
        x0, d0 = members[0]
        for x, d in members[1:]:
            t = (d - d0) % N                                 # v(x)-v(x0) == t
            if t == 0:
                if x != x0:
                    return False
                continue
            a, b = pos[x0], pos[x]
            D = t if b > a else N - t                        # exact linear gap
            i, j = (a, b) if b > a else (b, a)
            edges.append((i, j, D)); edges.append((j, i, -D))
    dist = [0] * n
    for it in range(n + 1):
        changed = False
        for i, j, w in edges:
            if dist[i] + w < dist[j]:
                dist[j] = dist[i] + w
                changed = True
        if not changed:
            return True
    return False                                             # negative cycle

def run_phrase(ph, tmpl, pairs, order):
    """returns highest level reached: '-', 'A', 'B', 'C+', 'C-', 'D+', 'D-' style dict."""
    res = {"A": gate_A(ph, tmpl), "B": False, "C": [], "D": []}
    if not res["A"]:
        return res
    res["B"] = gate_B(ph, tmpl)
    if not res["B"]:
        return res
    for s in (+1, -1):
        comp = gate_C(ph, pairs, s)
        if comp is not None:
            res["C"].append(s)
            if gate_D(comp, order):
                res["D"].append(s)
    return res

# --------------------------------------------------------------------------- #
# candidates
# --------------------------------------------------------------------------- #
def _clean(s):
    return "".join(ch for ch in s.upper() if "A" <= ch <= "Z")

def windows(s, k=L):
    s = _clean(s)
    return [s[i:i + k] for i in range(len(s) - k + 1)]

EXTRA = [
    "for the seekers of truest of knowledge",
    "the gods are watching you always",
    "we are watching you seeker of truth",
]

def load_candidates(extra_file=None):
    cand = {}
    def add(p, src):
        if len(p) == L and p not in cand:
            cand[p] = src
    pb = os.path.join(ROOT, "lexicon", "phrase_bank.tsv")
    if os.path.exists(pb):
        for row in csv.DictReader(open(pb), delimiter="\t"):
            for w in windows(row["unspaced"]):
                add(w, "phrase_bank")
    sc = os.path.join(ROOT, "lexicon", "sized_candidates.tsv")
    if os.path.exists(sc):
        for row in csv.DictReader(open(sc), delimiter="\t"):
            for w in windows(row["candidate"]):
                add(w, "sized")
    for fn in ("lore_en.txt", "lore_fi.txt"):
        p = os.path.join(ROOT, "lexicon", fn)
        if os.path.exists(p):
            for w in windows(open(p, encoding="utf-8", errors="ignore").read()):
                add(w, fn)
    for s in EXTRA:
        for w in windows(s):
            add(w, "dev-voice")
    if extra_file:
        for line in open(extra_file, encoding="utf-8", errors="ignore"):
            for w in windows(line):
                add(w, "user")
    return cand

# --------------------------------------------------------------------------- #
# selftest
# --------------------------------------------------------------------------- #
def _synth(phrase, order, gaps, sigma=+1, seed=4):
    """4-instance per-message-progressive plant carrying `phrase` at the
    refrain slots, under embedding gaps of `order`."""
    rng = random.Random(seed)
    v, acc = {}, 0
    for c, g in zip(order, gaps):
        v[c] = acc; acc += g
    C = list(range(N)); rng.shuffle(C)
    bases = [rng.randrange(N) for _ in range(9)]
    msgs = [[rng.randrange(N) for _ in range(140)] for _ in range(9)]
    for (m, pos) in INSTANCES:
        for i, ch in enumerate(phrase):
            t = pos + i
            msgs[m][t] = C[(sigma * v[ch] + bases[m] + t) % N]
    return msgs, v

def selftest():
    ok = fail = 0
    def chk(name, cond):
        nonlocal ok, fail
        print(f"  [{'OK ' if cond else 'FAIL'}] {name}")
        ok, fail = ok + cond, fail + (not cond)

    # unit: gate_D window logic on the plain alphabet
    az = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chk("unit: adjacent letters at gap 1 feasible",
        gate_D({"A": ("A", 0), "B": ("A", 1)}, az))
    chk("unit: adjacent letters at gap 82 infeasible (window math)",
        not gate_D({"A": ("A", 0), "B": ("A", 82)}, az))
    chk("unit: wrap-direction gap handled (B->A == 83-1)",
        gate_D({"B": ("B", 0), "A": ("B", 82)}, az))

    # plant: known order + irregular embedding + phrase with the right skeleton
    order = "BDMAGICKEFHJLNOPQRSTUVWXYZ"
    rng = random.Random(11)
    gaps = [1] * 26
    for _ in range(N - 26):
        gaps[rng.randrange(26)] += 1
    # build a phrase that satisfies the refrain skeleton by construction:
    # positions: 3==13, 4==5, 10==16, all diff pairs distinct letters
    base = "ABCDEFGHIJKLMNOPQRSTUV"
    ph = list(base)
    ph[13] = ph[3]; ph[5] = ph[4]; ph[16] = ph[10]
    phrase = "".join(ph)
    msgs, v = _synth(phrase, order, gaps, sigma=+1)
    t = tp.extract(msgs, INSTANCES, L, N)
    chk("plant: synthetic template consistent", t.consistent)
    pairs = forced_pairs(t)
    res = run_phrase(phrase, t, pairs, order)
    chk("plant: true phrase passes A/B on its own template", res["B"])
    chk("plant: true phrase numeric-consistent at sigma=+1", +1 in res["C"])
    chk("plant: true (phrase, order) embeddable", +1 in res["D"])
    # wrong phrase: violate a relation the synthetic template actually forces
    bad = list(phrase)
    if t.same_groups:
        g0 = t.same_groups[0]
        bad[g0[1]] = "Z" if phrase[g0[1]] != "Z" else "Y"
    else:
        i0, j0, _ = t.diff_pairs[0]
        bad[j0] = bad[i0]
    chk("plant: corrupted phrase rejected", not run_phrase("".join(bad), t, pairs, order)["B"])
    # adversarial order: swap two letters inside a forced arc -> should reject
    rej = 0; tries = 40
    letters = sorted(set(phrase))
    rng2 = random.Random(7)
    for _ in range(tries):
        ro = list(order); rng2.shuffle(ro)
        if not run_phrase(phrase, t, pairs, "".join(ro))["D"]:
            rej += 1
    chk(f"plant: random orders rejected for the true phrase ({rej}/{tries} rejected)",
        rej > 0)

    # real corpus: certified facts reproduce
    real = tp.extract(load_corpus(), INSTANCES, L, N)
    chk("real: dof=2, free=[7]", real.dof == 2 and real.free_positions == [7])
    chk("real: same-groups {3,13}{4,5}{10,16}",
        sorted(map(sorted, real.same_groups)) == [[3, 13], [4, 5], [10, 16]])
    chk("real: 207 forced-different pairs", len(real.diff_pairs) == 207)

    print(f"  selftest: {ok} passed, {fail} failed")
    return fail == 0

# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--order", type=str)
    ap.add_argument("--phrases", type=str, default=None)
    ap.add_argument("--nulls", type=int, default=200)
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if not a.order:
        print(f"{ERR}: --order required"); sys.exit(2)
    order = a.order.upper()

    tmpl = tp.extract(load_corpus(), INSTANCES, L, N)
    pairs = forced_pairs(tmpl)
    cand = load_candidates(a.phrases)
    print(f"[eyegate2] order={order}  candidates={len(cand)}  "
          f"(dof={tmpl.dof}, forced pairs={len(pairs)})")

    nA = nB = 0; C_surv = []; D_surv = []
    for ph, src in cand.items():
        r = run_phrase(ph, tmpl, pairs, order)
        nA += r["A"]; nB += r["B"]
        if r["C"]:
            C_surv.append((ph, src, r["C"]))
        if r["D"]:
            D_surv.append((ph, src, r["D"]))
    print(f"  funnel: {len(cand)} -> A(same-groups) {nA} -> B(full pattern) {nB}"
          f" -> C(numeric) {len(C_surv)} -> D(embeddable, this order) {len(D_surv)}")
    for ph, src, ss in C_surv[:20]:
        tag = "D!" if any(ph == p for p, _, _ in D_surv) else "C "
        print(f"    [{tag}] {ph}  ({src}, sigma*={ss})")
    if C_surv and a.nulls:
        rng = random.Random(3)
        letters = sorted(set(order))
        base_rate = []
        for k in range(a.nulls):
            ro = list(letters); rng.shuffle(ro); ro = "".join(ro)
            hits = sum(1 for ph, src, ss in C_surv
                       if run_phrase(ph, tmpl, pairs, ro)["D"])
            base_rate.append(hits)
        mu = sum(base_rate) / len(base_rate)
        print(f"  null: mean D-admissions over {a.nulls} random orders = {mu:.2f}"
              f"   candidate order admits = {len(D_surv)}")

if __name__ == "__main__":
    main()
