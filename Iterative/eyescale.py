#!/usr/bin/env python3
"""
eyescale -- how many independent SCALES must the anchor programme buy?

FR54 priced acquisition under a single global drift: two anchors in component 1
fix base and drift together and deliver 25 glyphs / 31.2% of the corpus, then
one anchor per remaining component reaches 56 glyphs / 74.1%. Its central claim
was that the SECOND anchor supplies a pair-difference, bijective in the drift,
and therefore pins the drift for the ENTIRE system at once.

FR102 showed drift equality is unsupported: repair A severed #M-'s bridge, the
only alignment linking T1 to anything. FR103 showed skeleton consistency does
not rescue it -- 77 of 82 ratios survive consistency and injectivity. So the
model is a two-parameter family and FR54's central claim is conditional on an
equality that no longer holds.

CHALLENGE I sharpened the question. Component structure and the Delta RATIOS
come from drift-free relations (q[a]-q[b] = q[c]-q[e]); the drift enters only
as SCALE. So the question is not "how many drifts" but HOW MANY INDEPENDENT
SCALES acquisition must buy -- measurable directly, and what FR54 priced
without knowing it.

METHOD. The alignment system over GF(83), unknowns

    q[0..82]  alphabet values        83
    b_m       per-message offsets     9
    d1        drift of T1             1
    d2        drift of T2 and T3      1
                                     ---
                                      94

An ANCHOR is an external pin q[g] = v, contributing the row e_g. A value q[s]
is DETERMINED exactly when e_s lies in the row space of (system + anchors) --
the pinned values do not matter, only the rank, so yield is computable without
knowing what any anchor says.

Two configurations on identical machinery:
    ONE-DRIFT : plus the row (d1 - d2) = 0      [FR54's premise]
    TWO-DRIFT : without it                       [FR102/FR103 reality]

POOL. FR103's corrected pool: all certified instance pairs EXCEPT class #M-,
whose pairwise same-passage assertion contradicts the skeleton at every drift
(CORRECTIONS.md E5). 39 alignments, lettered cells only.

PRE-REGISTERED (frozen before corpus contact):
  R1  a claim that two drifts cost MORE anchors requires the two-drift greedy
      to need strictly more anchors than one-drift for the same glyph count.
  R2  the one-drift configuration must reproduce FR54's headline (2 anchors ->
      25 glyphs, component 1) or the instrument is wrong and the run is void.
  R3  the ordering is reported as GREEDY, never as proven optimal.

stdlib only. Exceptions carry XD-MBYG04K-URS3LF.
"""

import json, os, re, sys
from itertools import combinations

XD = "XD-MBYG04K-URS3LF"
N = 83
HERE = os.path.dirname(os.path.abspath(__file__))

TRIPLET = {"East 1": 0, "West 1": 0, "East 2": 0,
           "West 2": 1, "East 3": 1, "West 3": 1,
           "East 4": 2, "West 4": 2, "East 5": 2}
DISCARDED = {("#M-", "East 3", 101), ("#M", "East 1", 68)}
EXCLUDE_CLASSES = {"#M-"}

def inv(a):
    a %= N
    if a == 0: raise RuntimeError(f"{XD} inverse of zero")
    return pow(a, N - 2, N)

class Echelon:
    __slots__ = ("piv",)
    def __init__(self, other=None):
        self.piv = {c: r[:] for c, r in other.piv.items()} if other else {}
    def reduce(self, v):
        v = list(v)
        for c, row in self.piv.items():
            if v[c] % N:
                f = v[c]
                v = [(x - f * y) % N for x, y in zip(v, row)]
        return v
    def add(self, v):
        r = self.reduce(v)
        p = next((i for i, x in enumerate(r) if x % N), None)
        if p is None: return False
        iv = inv(r[p]); r = [(x * iv) % N for x in r]
        for c in list(self.piv):
            row = self.piv[c]
            if row[p] % N:
                f = row[p]
                self.piv[c] = [(x - f * y) % N for x, y in zip(row, r)]
        self.piv[p] = r
        return True
    def spans(self, v):
        return not any(x % N for x in self.reduce(v))
    def rank(self): return len(self.piv)

def load_corpus(p=None):
    d = json.load(open(p or os.path.join(HERE, "corpus.json")))
    return dict(zip(d["message_labels"], d["ciphertexts"]))

def load_atlas(p=None):
    return json.load(open(p or os.path.join(HERE, "atlas.json")))["classes"]

def load_components():
    src = open(os.path.join(HERE, "eyerunner.py")).read()
    out = []
    for n in ["C1", "C2", "C3", "C4"]:
        m = re.search(rf"^{n} = (\{{[^}}]+\}})", src, re.M | re.S)
        out.append(eval(m.group(1)))
    return out

def alignments(classes):
    out = []
    for cls in classes:
        if cls["id"] in EXCLUDE_CLASSES: continue
        offs = [i for i, ch in enumerate(cls["pattern"]) if ch != "."]
        ins = [(it["message"], it["start"]) for it in cls["instances"]
               if (cls["id"], it["message"], it["start"]) not in DISCARDED]
        for (m1, s1), (m2, s2) in combinations(ins, 2):
            if len(offs) >= 2: out.append((m1, s1, m2, s2, offs))
    return out

def build_rows(al, M, idx, one_drift):
    nb = len(idx); DD = N + nb; ncols = N + nb + 2
    rows = []
    for (m1, s1, m2, s2, offs) in al:
        g1, g2 = TRIPLET[m1], TRIPLET[m2]
        i1, i2 = DD + (0 if g1 == 0 else 1), DD + (0 if g2 == 0 else 1)
        for i in offs:
            a, b = M[m1][s1 + i], M[m2][s2 + i]
            r = [0] * ncols
            r[a] = (r[a] + 1) % N; r[b] = (r[b] - 1) % N
            r[N + idx[m1]] = (r[N + idx[m1]] - 1) % N
            r[N + idx[m2]] = (r[N + idx[m2]] + 1) % N
            r[i1] = (r[i1] - (s1 + i)) % N
            r[i2] = (r[i2] + (s2 + i)) % N
            if any(r): rows.append(r)
    if one_drift:
        r = [0] * ncols; r[DD] = 1; r[DD + 1] = N - 1
        rows.append(r)
    return rows, ncols

def determined(ech, ncols, glyphs):
    out = []
    for s in glyphs:
        v = [0] * ncols; v[s] = 1
        if ech.spans(v): out.append(s)
    return out

def greedy(rows, ncols, glyphs, cnt, max_anchors=14):
    base = Echelon()
    for r in rows: base.add(r)
    ech = Echelon(base); chosen = []
    det = set(determined(ech, ncols, glyphs))
    hist = [(0, None, len(det), sum(cnt[g] for g in det))]
    for _ in range(max_anchors):
        best = None
        for g in glyphs:
            if g in det: continue
            tr = Echelon(ech)
            v = [0] * ncols; v[g] = 1
            tr.add(v)
            nd = set(determined(tr, ncols, glyphs))
            gain = len(nd) - len(det)
            if best is None or gain > best[0]: best = (gain, g, nd)
        if best is None: break
        _, g, nd = best
        v = [0] * ncols; v[g] = 1
        ech.add(v); chosen.append(g); det = nd
        hist.append((len(chosen), g, len(det), sum(cnt[x] for x in det)))
        if len(det) == len(glyphs): break
    return chosen, hist

def selftest():
    ok = []
    def ck(n, c, d=""):
        ok.append((n, bool(c))); print(f"  {n:32s} {'PASS' if c else 'FAIL'} {d}")
        if not c: raise RuntimeError(f"{XD} selftest FAILED: {n} {d}")
    ck("t1_inv", all((x * inv(x)) % N == 1 for x in range(1, N)), "")
    e = Echelon(); e.add([1, 2, 3]); e.add([2, 4, 6])
    ck("t2_echelon_rank", e.rank() == 1, "dependent row rejected")
    ck("t3_spans", e.spans([2, 4, 6]) and not e.spans([0, 1, 0]), "")
    e.add([0, 1, 1]); ck("t4_rank2", e.rank() == 2, "")
    ech = Echelon(); ech.add([1, N - 1, 0]); ech.add([1, 0, 0])
    ck("t5_propagation", ech.spans([0, 1, 0]),
       "anchoring q0 determines q1 via the relation")
    ech2 = Echelon(); ech2.add([1, N - 1, 0])
    ck("t5b_no_free_lunch", not ech2.spans([1, 0, 0]),
       "relation alone determines nothing absolutely")
    M = load_corpus(); al = alignments(load_atlas())
    ck("t6_pool", len(al) == 39, f"{len(al)} alignments, #M- excluded")
    print(f"selftest {sum(1 for _,p in ok if p)}/{len(ok)} green")

def corpus_run():
    M = load_corpus(); classes = load_atlas(); comps = load_components()
    idx = {m: i for i, m in enumerate(sorted(M))}
    al = alignments(classes)
    glyphs = sorted(set().union(*[set(c) for c in comps]))
    cnt = {g: sum(1 for ct in M.values() for v in ct if v == g) for g in glyphs}
    comp_of = {}
    for ci, c in enumerate(comps, 1):
        for g in c: comp_of[g] = ci
    print("=" * 74)
    print("EYESCALE -- anchor yield: one drift (FR54) vs two (FR102/FR103)")
    print("=" * 74)
    print(f"pool {len(al)} alignments (#M- excluded, E5); "
          f"skeleton glyphs {len(glyphs)}")
    res = {}
    for label, one in (("ONE-DRIFT (FR54 premise)", True),
                       ("TWO-DRIFT (FR102/FR103)", False)):
        rows, ncols = build_rows(al, M, idx, one)
        chosen, hist = greedy(rows, ncols, glyphs, cnt)
        res[label] = hist
        print(f"\n--- {label} ---")
        print(f"  {'anchors':>7} {'glyph':>9} {'glyphs':>7} "
              f"{'positions':>10} {'corpus':>8}")
        for k, g, nd, npos in hist:
            gs = "-" if g is None else f"{g}(c{comp_of.get(g,'?')})"
            print(f"  {k:>7} {gs:>9} {nd:>7} {npos:>10} "
                  f"{100*npos/1036:>7.1f}%")
    print("\n=== comparison ===")
    h1, h2 = res["ONE-DRIFT (FR54 premise)"], res["TWO-DRIFT (FR102/FR103)"]
    def first_at(h, n):
        for k, g, nd, npos in h:
            if nd >= n: return k
        return None
    for t in (25, 36, 43, 46):
        a1, a2 = first_at(h1, t), first_at(h2, t)
        if a1 is None and a2 is None: continue
        d = "" if (a1 is None or a2 is None) else f"   (+{a2-a1} anchors)"
        print(f"  reach {t:>2} glyphs : one-drift {a1}, two-drift {a2}{d}")
    r2 = h1[2][2] if len(h1) > 2 else None
    print(f"\n  R2 -- one-drift at 2 anchors determines {r2} glyphs "
          f"(FR54 headline 25)")

if __name__ == "__main__":
    selftest()
    if "--selftest" not in sys.argv: corpus_run()
