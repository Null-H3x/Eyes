#!/usr/bin/env python3
"""eyecrib_sweep.py — automated crib -> cascade sweep for the Noita eye corpus.

For every candidate plaintext in the lexicon, at every validated same-plaintext
target, this: (1) places the crib, (2) solves the implied partial alphabet over
GF(83) under the sliding model, (3) CASCADES — uses that partial alphabet to
decrypt the rest of the crib's triplet — and (4) scores the cascade against a
k-gram model of the lore register. Consistency is the gate; cascade is the verdict.

The search is small (thousands of candidates); it is CPU-parallel and finishes in
minutes on many cores. No GPU needed — the limiter is lexicon quality, not compute.

Usage
-----
  python3 eyecrib_sweep.py --selftest
  python3 eyecrib_sweep.py --lexicon lexicon/sized_candidates.tsv --lore lexicon/lore_en.txt \
                           --target all --tier 2 --top 25 --procs 64
  python3 eyecrib_sweep.py --lexicon lexicon/sized_candidates.tsv --lore lexicon/lore_en.txt \
                           --lore lexicon/lore_fi.txt --target refrain --model both
"""
from __future__ import annotations
import sys, os, argparse, math, json
from multiprocessing import Pool
from collections import defaultdict

ERROR_PREFIX = "Internal Error Code: XD-MBYG04K-URS3LF"
N = 83
HERE = os.path.dirname(os.path.abspath(__file__))

# validated same-plaintext targets: instances (msg,start), length, and triplet members
TARGETS = {
 "refrain": dict(L=25, inst=[("West 1",32),("West 1",62),("East 2",37),("East 2",72)],
                 triplet=["East 1","West 1","East 2"]),
 "t3dof1":  dict(L=30, inst=[("East 4",50),("West 4",52),("East 5",51)],
                 triplet=["East 4","West 4","East 5"]),
 "t1open":  dict(L=24, inst=[("East 1",1),("West 1",1),("East 2",1)],
                 triplet=["East 1","West 1","East 2"]),
 "t3open":  dict(L=20, inst=[("East 4",1),("West 4",1),("East 5",1)],
                 triplet=["East 4","West 4","East 5"]),
 "t2pass":  dict(L=23, inst=[("East 3",18),("West 2",12),("West 3",17)],
                 triplet=["West 2","East 3","West 3"]),
}
LEN2TGT = {}
for k,v in TARGETS.items(): LEN2TGT.setdefault(v["L"],[]).append(k)


# ----------------------------------------------------------------- io helpers
def find_corpus(hint=None):
    for c in [hint] + [os.path.join(b,"noita_eye_core","corpus.json") for b in (HERE,os.path.dirname(HERE),os.getcwd())] \
             + [os.path.join(b,"corpus.json") for b in (HERE,os.path.dirname(HERE),os.getcwd())]:
        if c and os.path.isfile(c): return c
    return None

def load_corpus(path):
    d = json.load(open(path)); labels = d["message_labels"]
    ct = {labels[i]: list(c) for i,c in enumerate(d["ciphertexts"])}
    return ct

def build_scorer(lore_paths, k=3):
    alpha = "abcdefghijklmnopqrstuvwxyzåäö"; A = len(alpha); pos = {c:i for i,c in enumerate(alpha)}
    txt = ""
    for p in lore_paths:
        if os.path.isfile(p): txt += open(p,encoding="utf-8",errors="ignore").read().lower()
    seq = [pos[c] for c in txt if c in pos]
    cnt = defaultdict(lambda: 0.1)
    for i in range(len(seq)-k+1):
        cnt[tuple(seq[i:i+k])] += 1
    tot = defaultdict(float)
    for g,c in cnt.items(): tot[g[:-1]] += c
    logp = {g: math.log(c/tot[g[:-1]]) for g,c in cnt.items()}
    floor = math.log(0.1/ (max(tot.values()) if tot else 1))
    return dict(alpha=alpha, A=A, pos=pos, logp=logp, floor=floor, k=k)

def load_lexicon(path, max_tier=3):
    cands = defaultdict(list)  # len -> [(cand, tier, src)]
    with open(path) as f:
        next(f, None)
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 4: continue
            L, tier, cand, src = int(parts[0]), int(parts[1]), parts[2], parts[3]
            if tier <= max_tier: cands[L].append((cand, tier, src))
    return cands


# ----------------------------------------------------------------- GF(83) solve
def gf_solve(rows, nvar):
    """Reduced row-echelon over GF(83). Returns particular solution (free vars=0)
    or None if inconsistent."""
    M = [r[:] for r in rows]; piv = {}; r = 0
    for c in range(nvar):
        p = next((rr for rr in range(r,len(M)) if M[rr][c] % N), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]
        inv = pow(M[r][c], N-2, N); M[r] = [(x*inv) % N for x in M[r]]
        for rr in range(len(M)):
            if rr != r and M[rr][c] % N:
                f = M[rr][c]; M[rr] = [(a-f*b) % N for a,b in zip(M[rr], M[r])]
        piv[c] = r; r += 1
    for row in M:
        if all(x % N == 0 for x in row[:nvar]) and row[nvar] % N: return None
    sol = [0]*nvar
    for c,rr in piv.items(): sol[c] = M[rr][nvar] % N
    return sol

def solve_crib(inst_ct, inst_starts, crib, drift, sign):
    """inst_ct: aligned ciphertext windows; inst_starts: absolute start of each.
    Returns (qmap, emap, bases) or None. bases are TRUE message bases."""
    L = len(crib)
    syms = []; sidx = {}
    for ct in inst_ct:
        for i in range(L):
            c = ct[i]
            if c not in sidx: sidx[c] = len(syms); syms.append(c)
    lets = sorted(set(crib)); lidx = {l:i for i,l in enumerate(lets)}
    ninst = len(inst_ct)
    nq, ne = len(syms), len(lets); nvar = nq + ne + ninst
    rows = []
    for m,ct in enumerate(inst_ct):
        s = inst_starts[m]
        for i in range(L):
            c = ct[i]; l = crib[i]; row = [0]*(nvar+1)
            row[sidx[c]] = 1                       # q[c]
            row[nq+lidx[l]] = (N - (sign % N)) % N # - sign*e[l]  (e := sign*E)
            row[nq+ne+m] = N-1                     # - base_m
            row[nvar] = (drift*(s+i)) % N          # = drift*(absolute position)
            rows.append(row)
    sol = gf_solve(rows, nvar)
    if sol is None: return None
    qmap = {syms[i]: sol[i] for i in range(nq)}
    emap = {lets[i]: sol[nq+i] for i in range(ne)}
    bases = [sol[nq+ne+m] for m in range(ninst)]
    return qmap, emap, bases


# ----------------------------------------------------------------- cascade + score
def cascade_score(qmap, emap, base, triplet_ct, drift, starts, SC):
    """Decrypt the triplet's messages using the partial alphabet; score covered
    letters with the k-gram model. Returns (avg_logprob, coverage_fraction)."""
    inv_e = {}
    for l,e in emap.items(): inv_e.setdefault(e % N, l)  # e-code -> letter
    seq = []; covered = 0; total = 0
    logp, floor, k = SC["logp"], SC["floor"], SC["k"]; posmap = SC["pos"]
    for m, ct in triplet_ct:
        s0 = starts.get(m, 0)
        run = []
        for t,c in enumerate(ct):
            total += 1
            if c in qmap:
                ecode = (qmap[c] - base - drift*(t)) % N
                if ecode in inv_e:
                    run.append(posmap[inv_e[ecode]]); covered += 1; continue
            if len(run) >= k: seq.append(run)
            run = []
        if len(run) >= k: seq.append(run)
    # score contiguous decrypted runs
    tot = 0.0; n = 0
    for run in seq:
        for i in range(len(run)-k+1):
            g = tuple(run[i:i+k]); tot += logp.get(g, floor); n += 1
    avg = tot/n if n else floor
    cov = covered/total if total else 0
    return avg, cov


def score_candidate(args):
    cand, target, corpus_ct, drift_signs, SC = args
    t = TARGETS[target]; L = t["L"]
    inst_ct = [corpus_ct[m][s:s+L] for (m,s) in t["inst"]]
    inst_starts = [s for (m,s) in t["inst"]]
    triplet_ct = [(m, corpus_ct[m]) for m in t["triplet"]]
    best = None
    for drift, sign in drift_signs:
        r = solve_crib(inst_ct, inst_starts, cand, drift, sign)
        if r is None: continue
        qmap, emap, bases = r
        base = bases[0]  # within-triplet bases equal -> true message base
        avg, cov = cascade_score(qmap, emap, base, triplet_ct, drift, {}, SC)
        combined = avg + math.log(max(cov, 1e-3))  # reward both coherence and coverage
        if best is None or combined > best[0]:
            best = (combined, avg, cov, drift, sign)
    if best is None: return None
    return (best[0], best[1], best[2], best[3], best[4], cand, target)


# ----------------------------------------------------------------- selftest
def selftest():
    import random
    print("selftest: planting a known lore crib into a synthetic triplet ...")
    rng = random.Random(7)
    alpha = "abcdefghijklmnopqrstuvwxyzåäö "
    C = list(range(N)); rng.shuffle(C)                 # secret mixed alphabet
    E = {a: rng.randrange(N) for a in alpha}           # secret embedding (distinct enough)
    vals = rng.sample(range(N), len(alpha)); E = {a:vals[i] for i,a in enumerate(alpha)}
    drift, sign, base = 1, 1, 40
    pt = "youthinkyouknowtheanswerbutyoudontknowanything the treasure will not satisfy you"
    pt = pt.lower()
    def enc(p, s0):
        return [C[(sign*E[ch] + base + drift*(s0+t)) % N] for t,ch in enumerate(p)]
    # three instances of a shared 25-char passage at different offsets in three messages
    passage = pt[:25]
    m1 = enc("xxxxx"+passage+pt[25:60], 0)
    m2 = enc("xx"+passage+pt[25:70], 0)
    m3 = enc(passage+pt[25:55], 0)
    corpus = {"West 1": m1, "East 2": m2, "East 1": m3}
    TARGETS["_t"] = dict(L=25, inst=[("West 1",5),("East 2",2),("East 1",0)],
                         triplet=["East 1","West 1","East 2"])
    SC = build_scorer([], k=3)
    # inject a lore model so scoring means something
    lore = "youthinkyouknowtheanswerbutyoudont the treasure will not satisfy you we are watching"
    seq = [SC["pos"][c] for c in lore if c in SC["pos"]]
    from collections import defaultdict as dd
    cnt = dd(lambda:0.1)
    for i in range(len(seq)-2): cnt[tuple(seq[i:i+3])] += 1
    tot = dd(float)
    for g,c in cnt.items(): tot[g[:-1]] += c
    SC["logp"] = {g: math.log(c/tot[g[:-1]]) for g,c in cnt.items()}
    correct = "youthinkyouknowtheanswer"[:25].ljust(25,"x")[:25]
    correct = passage  # the true 25-char plaintext
    decoys = ["wewantedyoutocomeherenowx","thegodofgodstheonetrueone","provethineknowledgeandsee",
              "devotedseekeraftertruewis","xqzjkvbwmplnrtsdghfaeioucy"]
    results = []
    for cand in [correct]+decoys:
        r = score_candidate((cand[:25], "_t", corpus, [(1,1),(1,-1),(-1,1),(-1,-1)], SC))
        results.append((r[0] if r else -99, cand, bool(r)))
    results.sort(reverse=True)
    print("  ranked (combined score):")
    for sc,cand,ok in results:
        tag = "  <-- planted truth" if cand==correct else ""
        print(f"    {sc:+7.3f}  {cand}{tag}")
    top = results[0][1]
    ok = (top == correct)
    del TARGETS["_t"]
    print("selftest:", "PASS — correct crib ranks #1" if ok else "FAIL — plant not recovered")
    return 0 if ok else 1


# ----------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--corpus", default=None)
    ap.add_argument("--lexicon", default=None)
    ap.add_argument("--lore", action="append", default=[])
    ap.add_argument("--target", default="all", help="refrain|t3dof1|t1open|t3open|t2pass|all")
    ap.add_argument("--tier", type=int, default=2, help="max candidate tier to test (1-3)")
    ap.add_argument("--model", choices=["static","both"], default="static")
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--procs", type=int, default=None)
    a = ap.parse_args()
    if a.selftest: sys.exit(selftest())

    cpath = find_corpus(a.corpus)
    if not cpath: sys.exit(f"{ERROR_PREFIX}\ncorpus.json not found; pass --corpus")
    corpus = load_corpus(cpath)
    if not a.lexicon or not os.path.isfile(a.lexicon):
        sys.exit(f"{ERROR_PREFIX}\nlexicon not found; pass --lexicon lexicon/sized_candidates.tsv")
    lore = a.lore or [os.path.join(os.path.dirname(a.lexicon),"lore_en.txt")]
    SC = build_scorer(lore, k=3)
    lex = load_lexicon(a.lexicon, a.tier)
    tgts = list(TARGETS) if a.target=="all" else [a.target]
    drift_signs = [(1,1),(1,-1),(-1,1),(-1,-1)]  # language-viable gauges

    jobs = []
    for tg in tgts:
        L = TARGETS[tg]["L"]
        for cand,tier,src in lex.get(L,[]):
            jobs.append((cand, tg, corpus, drift_signs, SC))
    print(f"corpus={cpath}  lore={lore}  tiers<= {a.tier}")
    print(f"targets={tgts}  candidates={len(jobs)}  gauges={len(drift_signs)}")
    if not jobs: sys.exit("no candidates at these target lengths / tiers")
    with Pool(a.procs) as p:
        res = [r for r in p.map(score_candidate, jobs) if r]
    res.sort(reverse=True)
    print(f"\n=== top {a.top} by cascade score (score = k-gram/char + log coverage) ===")
    print(f"{'score':>8} {'kgram':>7} {'cov':>5}  {'drift':>5} {'target':8} candidate")
    for combined,avg,cov,drift,sign,cand,tg in res[:a.top]:
        print(f"{combined:>8.3f} {avg:>7.3f} {cov:>5.0%}  {drift:>+5} {tg:8} {cand}")
    print("\nHigh score + high coverage on a discriminating target = a candidate to inspect by eye.")
    print("Nothing here proves a read; it ranks which guesses cascade least-badly. Verify the top few.")


if __name__ == "__main__":
    main()
