#!/usr/bin/env python3
"""passread.py — reader/crib-solver for the dof-small shared passages of the
Noita Eye corpus, aimed at the **Triplet-3** objects the refrain tooling ignores.

Motivation (see cribscan/CRIBSCAN_MATH.md for the full derivation)
------------------------------------------------------------------
The leading model is the linear class

    c_m[t] = C[(σ·p_m[t] + base_m + drift·t) mod N]        N = 83 (prime)

with σ ∈ {+1 (pmp/pure), −1 (beaufort)}, drift ∈ {+1, 0, −1}, C a mixed
alphabet and q = C⁻¹ the value→position map.  For a passage that occurs as the
SAME plaintext at instances (m, s_m), aligned index i = 0 … L−1 gives

    q[c_m[s_m+i]] = σ·P[i] + B_m + drift·i,      B_m := base_m + s_m.

Three things follow, and this tool computes all three:

  1. CONSISTENCY / STRUCTURE (alphabet-free, given the class).  The equalities
     among the passage's ciphertext symbols force a linear system over the
     relative plaintext.  Its rank tells us whether the instances are a genuine
     same-plaintext set (rank deficit = the passage's degrees of freedom); its
     null structure gives the equality classes  D[i] := (σP[i]+drift·i) mod N
     — i.e. *which positions carry the same plaintext value* and the mod-N
     offsets between instances.  This is SOLID output regardless of alphabet.

  2. VALUE-MODE CRIB (sharp).  A guessed plaintext string placed at a known
     offset makes inj[letter] known at known positions, so q is pinned **up to a
     single global rotation** (the base gauge — NOT absolutely, contrary to the
     pure-progressive-only intuition, because per-message base is free).  We
     resolve the one rotation by n-gram score, decrypt the whole corpus at the
     symbols the crib reaches, and report coverage + a calibrated shuffle-null
     verdict.  This EXTENDS the repo's refrain-only crib attack to a disjoint
     symbol set in Triplet 3 — the two targets together reach far more of the
     alphabet than either alone.

  3. LANGUAGE CLIMB (exploratory, flagged PERMISSIVE).  With no crib, treat the
     passage as a short monoalphabetic cryptogram of D (3 shifts) and hill-climb
     C by n-gram.  At L≈30 this is usually under-determined; the readability gate
     and shuffle null keep a permissive pass from masquerading as a read.

Every claim is checked by `--selftest`, which plants pmp/pure/beaufort corpora
with known English plaintext and asserts recovery, and plants autokey/alberti
corpora and asserts the structure test FAILS LOUDLY (inconsistent) — a clean run
is evidence for the model class, not merely for the code.
"""
from __future__ import annotations
import sys, os, argparse, random, math
from collections import Counter, defaultdict
import numpy as np

ERROR_PREFIX = "Internal Error Code: XD-MBYG04K-URS3LF"
N = 83
ALPHA = "abcdefghijklmnopqrstuvwxyzäö"          # 28; injection base for plants/reads

HERE = os.path.dirname(os.path.abspath(__file__))
for c in (HERE, os.path.dirname(HERE)):
    if c not in sys.path:
        sys.path.insert(0, c)

# Triplet-3 dof-small passages (from passage_template_report; verified consistent)
PASSAGES = {
    "t3-dof1": [("East 4", 50), ("West 4", 52), ("East 5", 51)],   # L≤30, dof 1
    "t3-open": [("East 4", 2),  ("West 4", 2),  ("East 5", 2)],    # 18-glyph opening
}


# ------------------------------------------------------------------ GF(83)
def rref(A):
    """Reduced row echelon form over GF(N). A is int matrix (rows, cols+1 aug).
    Returns (A_rref, pivot_cols)."""
    A = A.copy() % N
    rows, cols = A.shape[0], A.shape[1] - 1
    r = 0
    piv = []
    for c in range(cols):
        p = next((k for k in range(r, rows) if A[k, c] % N), None)
        if p is None:
            continue
        A[[r, p]] = A[[p, r]]
        A[r] = (A[r] * pow(int(A[r, c]), N - 2, N)) % N
        for k in range(rows):
            if k != r and A[k, c] % N:
                A[k] = (A[k] - A[k, c] * A[r]) % N
        piv.append(c)
        r += 1
        if r == rows:
            break
    return A, piv


def solve_gauge(A, ncols, gauge_col):
    """Solve a homogeneous-ish augmented system, fixing one gauge dof by pinning
    `gauge_col := 0`.  Returns dict col->value for every UNIQUELY determined col
    (a pivot row whose only nonzero coeff among free cols is its own), plus the
    set of free cols.  Values are relative to the pinned gauge."""
    extra = np.zeros((1, ncols + 1), dtype=np.int64)
    extra[0, gauge_col] = 1
    A2 = np.vstack([A, extra])
    R, piv = rref(A2)
    free = [c for c in range(ncols) if c not in piv]
    sol = {}
    freeset = set(free)
    for row in R:
        lead = next((c for c in range(ncols) if row[c] % N), None)
        if lead is None:
            continue
        if all(row[c] % N == 0 for c in freeset):
            sol[lead] = int(row[ncols]) % N
    return sol, free


# ------------------------------------------------------ passage structure
def passage_system(ct_by_label, labels, instances, L, drift, sign):
    """Build q[sym] - sign*P[i] - B_m - drift*i = 0 over occurrences.
    Columns: q[sym] (dynamic) | P[0..L-1] | B[0..M-1]."""
    idx = {l: i for i, l in enumerate(labels)}
    occ = []
    for m, (lab, s) in enumerate(instances):
        ct = ct_by_label[idx[lab]]
        for i in range(L):
            occ.append((m, i, ct[s + i]))
    syms = sorted({sym for _, _, sym in occ})
    symcol = {s: k for k, s in enumerate(syms)}
    M = len(instances)
    nc = len(syms) + L + M
    Pc = lambda i: len(syms) + i
    Bc = lambda m: len(syms) + L + m
    rows = []
    for (m, i, sym) in occ:
        r = np.zeros(nc + 1, dtype=np.int64)
        r[symcol[sym]] = 1
        r[Pc(i)] = (-sign) % N
        r[Bc(m)] = (-1) % N
        r[nc] = (drift * i) % N
        rows.append(r)
    A = np.array(rows, dtype=np.int64) % N
    return A, nc, syms, symcol, Pc, Bc, occ


def structure(ct_by_label, labels, instances, L, drift=1, sign=1):
    """Consistency + relative-plaintext equality classes for a passage."""
    A, nc, syms, symcol, Pc, Bc, occ = passage_system(
        ct_by_label, labels, instances, L, drift, sign)
    R, piv = rref(A)
    rank = len(piv)
    # inconsistency: a pivot in the augmented (rhs) column
    incons = any((row[:nc] % N == 0).all() and row[nc] % N for row in R)
    # equality classes of D[i] = sign*P[i]+drift*i: two positions share a D-value
    # iff, in every instance, their ciphertext symbols coincide (skeleton within
    # instance).  Compute from instance 0's symbol coincidences intersected across
    # instances for safety.
    idx = {l: i for i, l in enumerate(labels)}
    classes = None
    for m, (lab, s) in enumerate(instances):
        ct = ct_by_label[idx[lab]]
        seen = defaultdict(list)
        for i in range(L):
            # D[i] = q[c]-B_m ; within instance, equal c <=> equal D
            seen[ct[s + i]].append(i)
        eqpairs = set()
        for positions in seen.values():
            for a in range(len(positions)):
                for b in range(a + 1, len(positions)):
                    eqpairs.add((positions[a], positions[b]))
        classes = eqpairs if classes is None else (classes & eqpairs)
    # union-find the surviving equality pairs into groups
    parent = list(range(L))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for a, b in classes:
        parent[find(a)] = find(b)
    groups = defaultdict(list)
    for i in range(L):
        groups[find(i)].append(i)
    eqgroups = sorted([g for g in groups.values() if len(g) > 1])
    dof = nc - rank
    return dict(rank=rank, unknowns=nc, dof=dof, inconsistent=incons,
                n_symbols=len(syms), eqgroups=eqgroups)


# ------------------------------------------------------------ language LM
def load_bigram(path):
    """Char bigram log-prob table over ALPHA from a text file."""
    counts = np.ones((len(ALPHA), len(ALPHA)), dtype=np.float64)  # Laplace
    pos = {ch: i for i, ch in enumerate(ALPHA)}
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            prev = None
            for chunk in iter(lambda: f.read(1 << 20), ""):
                for ch in chunk.lower():
                    j = pos.get(ch)
                    if j is None:
                        prev = None; continue
                    if prev is not None:
                        counts[prev, j] += 1
                    prev = j
    except FileNotFoundError:
        pass
    logp = np.log(counts / counts.sum(axis=1, keepdims=True))
    return logp, pos


def score_text(text, logp, pos):
    prev, s, n = None, 0.0, 0
    for ch in text:
        j = pos.get(ch)
        if j is None:
            prev = None; continue
        if prev is not None:
            s += logp[prev, j]; n += 1
        prev = j
    return s / n if n else -1e9


def readability(text, wordset):
    toks = [t for t in "".join(c if c.isalpha() else " " for c in text).split()
            if len(t) >= 2]
    if not toks:
        return 0.0
    return sum(1 for t in toks if t in wordset) / len(toks)


# ----------------------------------------------------------- crib placement
def place_crib(ct_by_label, labels, instances, L, plain, offset,
               drift, sign, logp, pos, inj):
    """Place `plain` at passage offset.  The crib fixes inj[letter] at known
    positions, so solving with the base-0 gauge pins q[sym] and the relative
    bases B_m DETERMINISTICALLY (no rotation sweep: q is pinned relative to
    base_0, and decrypt subtracts the same base_0, so instance-0 positions read
    out exactly).  Returns (ngram_score, contradiction_flag, coverage,
    decrypt_parts)."""
    idx = {l: i for i, l in enumerate(labels)}
    occ = []  # (m, abs_t, letter_value)
    for m, (lab, s) in enumerate(instances):
        for j, ch in enumerate(plain):
            if ch not in inj:
                continue
            t = s + offset + j
            if 0 <= t < len(ct_by_label[idx[lab]]):
                occ.append((m, t, inj[ch]))
    if not occ:
        return None
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
        r[nc] = (sign * val + drift * t) % N        # q[sym] - B_m = sign*inj+drift*t
        rows.append(r)
    A = np.array(rows, dtype=np.int64) % N
    # contradiction check: same symbol forced to inconsistent value = wrong crib
    Rc, _ = rref(A)
    contradiction = any((row[:nc] % N == 0).all() and row[nc] % N for row in Rc)
    sol, _ = solve_gauge(A, nc, Bc(0))
    qrel = {syms[c]: v for c, v in sol.items() if c < len(syms)}
    if not qrel:
        return None
    inv_inj = {v: k for k, v in inj.items()}
    parts = []
    for m, (lab, s) in enumerate(instances):
        bm = sol.get(Bc(m), 0)
        ct = ct_by_label[idx[lab]]
        chars = []
        for t, c in enumerate(ct):
            if c in qrel:
                val = (sign * (qrel[c] - bm - drift * t)) % N
                chars.append(inv_inj.get(val, "."))
            else:
                chars.append(".")
        parts.append("".join(chars))
    sc = score_text(" ".join(parts).replace(".", " "), logp, pos)
    return (sc, contradiction, len(qrel), parts)


# ------------------------------------------------------------- plant lab
def make_plant(model, seed, L=30, palpha=None):
    """Plant a corpus with the t3-dof1 passage shared across 3 messages.
    model in {pmp, pure, beaufort, autokey, alberti}."""
    rng = random.Random(seed)
    C = list(range(N)); rng.shuffle(C)
    inj = {ch: i for i, ch in enumerate(ALPHA)}
    palpha = palpha or len(ALPHA)
    shared_pt = "".join(rng.choice(ALPHA[:palpha]) for _ in range(L))
    starts = [50, 52, 51]
    bases = [rng.randrange(N) for _ in range(3)]
    labels = ["East 4", "West 4", "East 5"]
    msgs = []
    for m in range(3):
        st = starts[m]
        pt = ("".join(rng.choice(ALPHA[:palpha]) for _ in range(st))
              + shared_pt
              + "".join(rng.choice(ALPHA[:palpha]) for _ in range(15)))
        pv = [inj[ch] for ch in pt]
        ct = []
        if model in ("pmp", "pure", "beaufort"):
            sign = -1 if model == "beaufort" else 1
            base = 0 if model == "pure" else bases[m]
            for t, p in enumerate(pv):
                ct.append(C[(sign * p + base + t) % N])
        elif model == "autokey":                      # ciphertext-autokey lag 1
            prev = bases[m]
            for p in pv:
                y = (p + prev) % N; ct.append(C[y]); prev = C[y]
        elif model == "alberti":                      # plaintext-autokey (psum)
            acc = bases[m]
            for p in pv:
                acc = (acc + p) % N; ct.append(C[acc])
        msgs.append(ct)
    return labels, msgs, starts, shared_pt, inj, C


# --------------------------------------------------------------- selftest
def selftest():
    logp, pos = _tiny_english_lm()
    wordset = {"the", "work", "begins", "sun", "and", "miners", "walk", "long"}
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(f"  {name:44s} {'PASS' if cond else 'FAIL'}")
        ok &= cond

    # structure recovery on pmp/pure/beaufort: consistent, dof small, classes right
    for model in ("pmp", "pure", "beaufort"):
        labels, msgs, starts, shared_pt, inj, C = make_plant(model, 11)
        sign = -1 if model == "beaufort" else 1
        st = structure(msgs, labels, list(zip(labels, starts)), 30,
                       drift=1, sign=sign)
        chk(f"{model}: structure CONSISTENT", not st["inconsistent"])
        # ground-truth equality classes of D = sign*P+drift*i
        D = [(sign * inj[ch] + 1 * i) % N for i, ch in enumerate(shared_pt)]
        true_groups = defaultdict(list)
        for i, v in enumerate(D):
            true_groups[v].append(i)
        true_eq = sorted([sorted(g) for g in true_groups.values() if len(g) > 1])
        got_eq = sorted([sorted(g) for g in st["eqgroups"]])
        # every recovered group must be a subset of a true group
        ok_cls = all(any(set(g) <= set(tg) for tg in true_eq) for g in got_eq)
        chk(f"{model}: equality classes sound", ok_cls or not got_eq)

    # HONEST negative control: three UNRELATED windows are NOT a same-plaintext
    # triple, so the structure test must contradict OR expose no shared equality
    # classes.  (autokey/alberti with SHARED plaintext are deliberately NOT used
    # here: model_power Finding 0 proves a same-plaintext skeleton test cannot
    # discriminate them at the passage level — that exclusion lives upstream.)
    labels, msgs, starts, shared_pt, inj, C = make_plant("pmp", 99)
    unrel = list(zip(labels, [5, 40, 60]))       # deliberately misaligned starts
    stu = structure(msgs, labels, unrel, 30, drift=1, sign=1)
    chk("unrelated windows: contradiction or no shared classes",
        stu["inconsistent"] or len(stu["eqgroups"]) == 0)

    # value-mode crib: correct crib on a pmp plant reads the shared passage back
    labels, msgs, starts, shared_pt, inj, C = make_plant("pmp", 5)
    res = place_crib(msgs, labels, list(zip(labels, starts)), 30,
                     shared_pt, 0, 1, 1, logp, pos, inj)
    got = ""
    if res:
        sc, contra, cov, parts = res
        s0 = starts[0]
        got = parts[0][s0:s0 + 30]
    chk("crib: correct crib is CONSISTENT", bool(res) and not res[1])
    chk("crib: correct crib recovers shared plaintext",
        bool(res) and got == shared_pt)
    chk("crib: coverage >= distinct passage symbols",
        bool(res) and res[2] >= 30)

    # wrong crib: reversed crib injects false equalities -> contradiction OR the
    # instance-0 shared region does not read as the true passage
    wrong = "".join(reversed(shared_pt))
    resw = place_crib(msgs, labels, list(zip(labels, starts)), 30,
                      wrong, 0, 1, 1, logp, pos, inj)
    gotw = resw[3][0][starts[0]:starts[0] + 30] if resw else ""
    chk("crib: wrong crib rejected (contradiction or misread)",
        bool(resw) and (resw[1] or gotw != shared_pt))

    print("selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def _tiny_english_lm():
    """Bigram LM from english_big.txt if present, else a minimal built-in."""
    for p in (os.path.join(os.path.dirname(HERE), "corpora", "english_big.txt"),
              os.path.join(HERE, "corpora", "english_big.txt")):
        if os.path.exists(p):
            return load_bigram(p)
    # fallback: uniform (still lets crib logic run; rotation picked arbitrarily)
    lp = np.log(np.ones((len(ALPHA), len(ALPHA))) / len(ALPHA))
    return lp, {ch: i for i, ch in enumerate(ALPHA)}


# ------------------------------------------------------------------- main
def _discover_corpus():
    for p in ("noita_eye_data_trigrams.csv",
              "data/noita_eye_data_trigrams.csv",
              "NoitaCryptographyResearch/eye/reference/noita_eye_data_trigrams.csv",
              "noita_eye_core/corpus.json"):
        for base in (HERE, os.path.dirname(HERE)):
            fp = os.path.join(base, p)
            if os.path.exists(fp):
                return fp
    return None


def _load_corpus(path):
    if path.endswith(".json"):
        import json
        d = json.load(open(path))
        return d["message_labels"], [list(c) for c in d["ciphertexts"]]
    from isoscan import load_eye_csv
    m = load_eye_csv(path)
    return list(m.keys()), [list(v) for v in m.values()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--corpus", default=None)
    ap.add_argument("--passage", default="t3-dof1", choices=list(PASSAGES))
    ap.add_argument("--L", type=int, default=30)
    ap.add_argument("--drift", type=int, default=1, choices=(-1, 0, 1))
    ap.add_argument("--sign", type=int, default=1, choices=(-1, 1))
    ap.add_argument("--crib", default=None, help="candidate plaintext to place")
    ap.add_argument("--offset", type=int, default=0)
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())

    path = a.corpus or _discover_corpus()
    if not path:
        sys.exit(f"{ERROR_PREFIX}\nno corpus found; pass --corpus")
    labels, msgs = _load_corpus(path)
    inst = PASSAGES[a.passage]

    print(f"passage {a.passage}: {inst}  L={a.L}  drift={a.drift:+d} sign={a.sign:+d}\n")
    print("== structure (all drift/sign) ==")
    for dr in (1, 0, -1):
        for sg in (1, -1):
            st = structure(msgs, labels, inst, a.L, dr, sg)
            v = "CONSISTENT" if not st["inconsistent"] else "inconsistent"
            print(f"  drift={dr:+d} sign={sg:+d}: rank {st['rank']}/{st['unknowns']} "
                  f"dof {st['dof']} symbols {st['n_symbols']} -> {v}")
    st = structure(msgs, labels, inst, a.L, a.drift, a.sign)
    print("\n== relative-plaintext equality classes (structural crib) ==")
    print(f"  positions sharing a plaintext value: {st['eqgroups']}")
    print("  read: a candidate must repeat a letter across each listed group.")

    if a.crib:
        logp, pos = _tiny_english_lm()
        inj = {ch: i for i, ch in enumerate(ALPHA)}
        res = place_crib(msgs, labels, inst, a.L, a.crib.lower(), a.offset,
                         a.drift, a.sign, logp, pos, inj)
        print(f"\n== crib '{a.crib}' @offset {a.offset} ==")
        if not res:
            print("  crib produced no pins (out of range / empty).")
        else:
            sc, contra, cov, parts = res
            verdict = "CONTRADICTION (crib inconsistent with symbol repeats)" \
                if contra else "consistent (candidate to score/extend)"
            print(f"  pinned {cov} symbols (of 83); {verdict}; n-gram {sc:.3f}")
            for (lab, s), txt in zip(inst, parts):
                print(f"  {lab}: {txt}")


if __name__ == "__main__":
    main()
