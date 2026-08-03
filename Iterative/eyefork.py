#!/usr/bin/env python3
"""
eyefork -- the near-duplicate divergence channel, a static-vs-dynamic
discriminator for the Noita eye corpus that never touches an isomorph.

THE CHANNEL. Each triplet contains a near-duplicate pair in body depth
(E1/W1, W2/W3, E4/E5). For an aligned pair sharing effective base+keystream
(proven by agreement >> 1/83), every position-driven term -- base_m, drift*t,
any per-triplet K[t] -- CANCELS in the pairwise comparison. The disagreement
indicator D[t] = [c_A[t] != c_B[t]] is therefore sensitive ONLY to the
plaintext-fed component of the offset, if one exists:

  STATIC (Perfectly Isomorphic: progressive / Gromark / general-K):
      agree(t) <=> p_A[t] == p_B[t].  D = the plaintext edit set. No forced
      structure beyond the edits themselves.

  LAG-k term (pure GAK-lag or XGAK-lag):
      agree(t) <=> sigma*(p_A[t]-p_B[t]) + (p_A[t-k]-p_B[t-k]) == 0 mod N.
      To first order D = P u (P+k): every edit echoes k positions later.
      FALSIFIER: an isolated D-singleton whose t-k and t+k neighbours are
      both in-window and agreeing is (nearly) impossible under lag-k --
      each such singleton costs an exact mod-83 cancellation (~2/83).
      SIGNATURE: echo excess at lag k beyond a run-preserving null.

  SIGMA term (GAK-Sigma / Alberti, or XGAK-Sigma):
      agree(t) <=> sigma*dp[t] + S[t] == 0,  S[t] = sum_{j<t} dp[j] mod N.
      S moves only at edits; agreement can resume ONLY when the running
      difference-sum returns to 0 -- a mod-83 coincidence per opportunity.
      SIGNATURE: block persistence; re-syncs rare.
      LEDGER: R = agreement resumptions after first divergence. Conservative
      null: every disagreement position is an edit giving a fresh 1/83
      return chance  =>  p_Sigma = P(Binom(|D|, 1/83) >= R).
      Loophole (stated, not hidden): value-multiset-balanced edits (anagram
      style rewrites) return S to 0 by construction and evade this test.

DEDUCTION A (atlas channel, reproduced by --atlas). Under ANY pure lag-k
autokey (no position term), two same-plaintext instances WITHIN one message
force glyph-identical ciphertext at every interior position j >= k (state and
plaintext both repeat; beta cancels; holds for any sigma, any C -- the same
bijection lever as the CTAK exclusion). The certified within-message isomorph
pairs show ZERO identities at any position; the longest (L=26) therefore
excludes pure lag-k for all k in [1, 25].

ISOMORPH SAFETY. This instrument only reads. No corpus value is modified,
no isomorph is filtered, weighted, or perturbed.

Pre-registration: see PREREG below -- thresholds fixed before the corpus run.
Selftest gate: --selftest plants all four families at corpus-matched
densities and must pass before any corpus verdict is trusted.
"""

import json, math, os, random, sys
from collections import Counter

ERR = "XD-MBYG04K-URS3LF"
N = 83
LAGS = list(range(1, 11))          # lag hypotheses tested
NULL_ITERS = 2000                  # run-permutation null samples
RNG_SEED = 20260721                # deterministic instrument seed

# ----------------------------------------------------------------------------
# PREREG -- decision thresholds, fixed before the corpus run.
# ----------------------------------------------------------------------------
PREREG = {
    "lag_reject_events": 2,        # v_ev(k) >= 2 accident-events -> lag-k REJECTED
                                   #   (priced on 40-plant sweeps per density:
                                   #    P(v_ev(k_true)>=2) <= 1/40 per pair; family
                                   #    exclusion needs 2 pairs -> ~0.2% false-excl.)
    "lag_pass_events": 1,          # v_ev(k) <= 1 keeps k alive (one priced accident)
    "lag_watch_z": 2.5,            # per-pair: v_ev<=1 AND agreement-echo z >= 2.5
                                   #   -> per-pair watch at that k
    "lag_family_reject_pairs": 2,  # k REJECTED on >= 2 guard-PASS pairs
                                   #   -> lag-k term EXCLUDED (family level)
    "lag_family_watch_pool_z": 2.5,# family SUPPORT(watch): k census-alive on
                                   #   all guard-PASS pairs, >=6 other lags
    "lag_family_full_pool_z": 4.0, #   excluded on >=2 pairs, pooled z >= 2.5;
                                   #   pooled z >= 4.0 upgrades to SUPPORTED
    "sigma_reject_p": 1e-4,        # pooled p_Sigma < 1e-4 -> Sigma/XGAK-Sigma REJECTED
                                   #   (up to the balanced-edit loophole)
    "align_floor": 0.05,           # trailing-window agreement below this triggers the
                                   #   offset sweep. Recovery at a nonzero shift =>
                                   #   indel desync, pair truncated at the break.
                                   #   Flat at ALL shifts => NO indel; the tail is
                                   #   genuine plaintext divergence and the pair
                                   #   remains valid (heads + islands at shift 0
                                   #   prove the frame). [wording corrected after
                                   #   plants: original text conflated the two cases]
    "min_pairs_for_family_call": 2 # a family verdict needs >= 2 independent pairs
}

def fail(msg):
    raise RuntimeError(f"{ERR}: {msg}")

# ----------------------------------------------------------------------------
# corpus access
# ----------------------------------------------------------------------------
def load_corpus(path):
    c = json.load(open(path))
    M = dict(zip(c["message_labels"], c["ciphertexts"]))
    if len(M) != 9: fail("corpus does not contain 9 messages")
    return M

NEAR_DUPS = [("East 1", "West 1"), ("West 2", "West 3"), ("East 4", "East 5")]

def disagreement(A, B, start=1):
    """D[t] over the aligned overlap, skipping position 0 (per-message
    indicator, disagrees by construction -- an artifact, not an edit)."""
    L = min(len(A), len(B))
    return [1 if A[t] != B[t] else 0 for t in range(start, L)]

# ----------------------------------------------------------------------------
# statistics on a 0/1 disagreement sequence
# ----------------------------------------------------------------------------
def runs_of(D):
    out = []
    i = 0
    while i < len(D):
        j = i
        while j < len(D) and D[j] == D[i]: j += 1
        out.append((D[i], j - i))
        i = j
    return out

def resync_ledger(D):
    """R = number of maximal agreement runs occurring AFTER the first
    disagreement (each is a re-sync). B = number of disagreement runs.
    p_Sigma = P(Binom(|D|,1/83) >= R), the conservative Sigma-family null."""
    rr = runs_of(D)
    first_dis = next((i for i, (v, _) in enumerate(rr) if v == 1), None)
    if first_dis is None:
        return dict(R=0, B=0, nD=0, p_sigma=1.0)
    R = sum(1 for v, _ in rr[first_dis + 1:] if v == 0)
    B = sum(1 for v, _ in rr if v == 1)
    nD = sum(D)
    p = binom_sf(nD, 1.0 / N, R)
    return dict(R=R, B=B, nD=nD, p_sigma=p)

def binom_sf(n, p, r):
    """P(X >= r), X ~ Binom(n, p). Exact, small n."""
    if r <= 0: return 1.0
    s = 0.0
    for k in range(r, n + 1):
        s += math.comb(n, k) * (p ** k) * ((1 - p) ** (n - k))
    return min(1.0, s)

def flanked_violations(D, k):
    """raw v(k): positions with D[t]=1 and agreement at BOTH t-k and t+k
    (in-window). Under a lag-k term each requires an exact mod-N
    cancellation (a fresh edit at t+k cancelling the echo, ~1/83 per
    doubly-edited spacing-k pair). Verified on 200 plants: rate matches
    (edit pairs at spacing k)/83, and ONE cancellation spawns violations at
    both t and t+2k."""
    n = len(D); out = []
    for t in range(n):
        if not D[t]: continue
        if t - k < 0 or t + k >= n: continue
        if D[t - k] or D[t + k]: continue
        out.append(t)
    return out

def violation_events(D, k):
    """v_ev(k): flanked violations clustered so that members 2k apart count
    as ONE accident (a single cancelling edit-pair produces both). Under
    lag-k truth E[v_ev] ~ 0.1 at corpus sizes; >= 3 events is priced at
    < ~1e-3 and REJECTS lag-k. Under static, flanked patterns are generic
    and v_ev is large except at extreme density."""
    ts = flanked_violations(D, k)
    ev = 0; used = set()
    for t in ts:
        if t in used: continue
        used.add(t)
        u = t + 2 * k
        while u in ts and u not in used:
            used.add(u); u += 2 * k
        ev += 1
    return ev

def echo_count(D, k):
    return sum(1 for t in range(len(D) - k) if D[t] and D[t + k])

def agreement_echo(D, k):
    """Y(k): co-agreement at lag k. Under a lag-k term, agree(t) requires
    edit-free at {t, t-k}, so P(A[t] & A[t+k]) = (1-p)^3 vs (1-p)^4 generic:
    a forced autocorrelation spike at exactly k, at any density."""
    return sum(1 for t in range(len(D) - k) if (not D[t]) and (not D[t + k]))

def run_permutation_null(D, lags, iters, rng):
    """Preserve the multisets of agreement-run and disagreement-run lengths
    (and alternation); randomize their order. Absorbs clumping; leaves only
    lag-specific structure as excess."""
    rr = runs_of(D)
    dis = [l for v, l in rr if v == 1]
    agr = [l for v, l in rr if v == 0]
    starts_with = rr[0][0] if rr else 0
    stats = {k: [] for k in lags}
    singl = {k: [] for k in lags}
    for _ in range(iters):
        rng.shuffle(dis); rng.shuffle(agr)
        seq = []
        a, b = (dis, agr) if starts_with == 1 else (agr, dis)
        va, vb = (1, 0) if starts_with == 1 else (0, 1)
        i = j = 0
        turn = 0
        while i < len(a) or j < len(b):
            if turn == 0 and i < len(a):
                seq.extend([va] * a[i]); i += 1
            elif turn == 1 and j < len(b):
                seq.extend([vb] * b[j]); j += 1
            turn ^= 1
        for k in lags:
            stats[k].append(agreement_echo(seq, k))
            singl[k].append(violation_events(seq, k))
    out = {}
    for k in lags:
        xs = stats[k]
        mu = sum(xs) / len(xs)
        sd = (sum((x - mu) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5 or 1e-9
        p_v0 = sum(1 for s in singl[k] if s == 0) / len(singl[k])
        out[k] = dict(mu=mu, sd=sd, p_v0_null=p_v0)
    return out

def trailing_agreement(D, w=20):
    if len(D) < w: w = max(4, len(D) // 2)
    tail = D[-w:]
    return 1.0 - sum(tail) / len(tail)

def offset_sweep(A, B, shifts=range(-5, 6), start=1):
    """agreement rate at shifted alignments -- indel detector."""
    out = {}
    for s in shifts:
        n = 0; ag = 0
        for t in range(start, min(len(A), len(B))):
            u = t + s
            if 0 <= u < len(B):
                n += 1; ag += (A[t] == B[u])
        out[s] = ag / n if n else 0.0
    return out

# ----------------------------------------------------------------------------
# pair analysis
# ----------------------------------------------------------------------------
def analyse_pair(A, B, rng, label="pair"):
    D = disagreement(A, B, start=1)
    nD = sum(D); n = len(D)
    led = resync_ledger(D)
    null = run_permutation_null(D, LAGS, NULL_ITERS, rng)
    lag_rows = {}
    for k in LAGS:
        X = agreement_echo(D, k); v = violation_events(D, k)
        z = (X - null[k]["mu"]) / null[k]["sd"]
        verdict = "REJECTED" if v >= PREREG["lag_reject_events"] else (
                  "watch" if (v <= PREREG["lag_pass_events"]
                              and z >= PREREG["lag_watch_z"])
                  else "inconclusive")
        lag_rows[k] = dict(echo=X, z=z, v=v, p_v0_null=null[k]["p_v0_null"],
                           verdict=verdict)
    guard_tail = trailing_agreement(D)
    guard = "PASS" if guard_tail >= PREREG["align_floor"] else "CHECK-SHIFTS"
    return dict(label=label, n=n, nD=nD, agree=1 - nD / n, ledger=led,
                lags=lag_rows, guard=guard, guard_tail=guard_tail)

# ----------------------------------------------------------------------------
# plant generators -- all families over Z_N, corpus-matched shapes.
# plaintext: ~20-symbol alphabet embedded by random injection into Z_N;
# shared prefix models the depth openings; edits scattered or clustered.
# ----------------------------------------------------------------------------
def make_plain_pair(rng, L, prefix, dens, clustered):
    alpha = rng.sample(range(N), 20)
    pA = [rng.choice(alpha) for _ in range(L)]
    pB = list(pA)
    t = prefix
    if clustered:
        while t < L:
            if rng.random() < dens / 3.0:            # start an edit block
                blk = 1 + int(rng.expovariate(1 / 3.0))
                for u in range(t, min(L, t + blk)):
                    pB[u] = rng.choice([a for a in alpha if a != pA[u]])
                t += blk
            else:
                t += 1
    else:
        for u in range(prefix, L):
            if rng.random() < dens:
                pB[u] = rng.choice([a for a in alpha if a != pA[u]])
    return pA, pB

def encrypt(p, fam, C, base, drift, k, sigma=1):
    c = []; S = 0
    for t, x in enumerate(p):
        if fam == "static":
            off = base + drift * t
        elif fam == "lag":
            off = base + (p[t - k] if t >= k else 7)          # primer
        elif fam == "xgak_lag":
            off = base + drift * t + (p[t - k] if t >= k else 7)
        elif fam == "sigma":
            off = base + S
        elif fam == "xgak_sigma":
            off = base + drift * t + S
        else:
            fail(f"unknown family {fam}")
        c.append(C[(sigma * x + off) % N])
        S = (S + x) % N
    return c

def plant_pair(rng, fam, L=100, prefix=24, dens=0.35, clustered=False, k=4):
    pA, pB = make_plain_pair(rng, L, prefix, dens, clustered)
    C = list(range(N)); rng.shuffle(C)
    base = rng.randrange(N); drift = 1
    A = encrypt(pA, fam, C, base, drift, k)
    B = encrypt(pB, fam, C, base, drift, k)
    return A, B

# ----------------------------------------------------------------------------
# selftest -- planted ground truth; must go green before corpus is trusted.
# ----------------------------------------------------------------------------
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    def fresh(tag):
        return random.Random(f"{RNG_SEED}:{tag}")

    print("selftest: planted families at corpus-matched densities")
    # 1. static, scattered: Sigma rejected; lag falsifier census live
    rng = fresh("static35")
    A, B = plant_pair(rng, "static", dens=0.35)
    r = analyse_pair(A, B, fresh("static35n"), "static-plant")
    check("static: Sigma rejected", r["ledger"]["p_sigma"] < PREREG["sigma_reject_p"],
          f"(R={r['ledger']['R']}, p={r['ledger']['p_sigma']:.2e})")
    rej = [k for k in LAGS if r["lags"][k]["verdict"] == "REJECTED"]
    check("static: census rejects most lags", len(rej) >= 8, f"({len(rej)}/10 rejected)")
    watch = [k for k in LAGS if r["lags"][k]["verdict"] == "watch"]
    check("static: no spurious lag watch", len(watch) == 0, f"{watch}")

    # 2. lag-4 pure: true k survives census (<=1 event), others rejected,
    #    agreement-echo confirms, k recovered
    rng = fresh("lag4")
    A, B = plant_pair(rng, "lag", dens=0.35, k=4)
    r = analyse_pair(A, B, fresh("lag4n"), "lag4-plant")
    check("lag4: v_ev(4) <= 1", r["lags"][4]["v"] <= PREREG["lag_pass_events"],
          f"(v_ev={r['lags'][4]['v']})")
    others = [k for k in LAGS if k != 4 and r["lags"][k]["verdict"] == "REJECTED"]
    check("lag4: census rejects most other lags", len(others) >= 6,
          f"({len(others)}/9 rejected)")
    check("lag4: agreement-echo z(4) >= watch", r["lags"][4]["z"] >= PREREG["lag_watch_z"],
          f"(z={r['lags'][4]['z']:.1f})")
    alive = [k for k in LAGS if r["lags"][k]["v"] <= PREREG["lag_pass_events"]]
    best = max(alive, key=lambda k: r["lags"][k]["z"]) if alive else None
    check("lag4: k recovered (alive & max z)", best == 4, f"(best={best})")

    # 3. xgak_lag-4: pair channel blind to drift -- same signature
    rng = fresh("xg4")
    A, B = plant_pair(rng, "xgak_lag", dens=0.35, k=4)
    r = analyse_pair(A, B, fresh("xg4n"), "xgak-lag4-plant")
    check("xgak-lag4: v_ev(4)<=1 and z(4)>=watch",
          r["lags"][4]["v"] <= 1 and r["lags"][4]["z"] >= PREREG["lag_watch_z"],
          f"(v_ev={r['lags'][4]['v']}, z={r['lags'][4]['z']:.1f})")

    # 4. pooled lag support across three pair-plants (family-level rule)
    zs = []
    okpool = True
    for i, dd in enumerate((0.35, 0.45, 0.55)):
        rng = fresh(f"pool{i}")
        A, B = plant_pair(rng, "lag", dens=dd, k=4)
        rr = analyse_pair(A, B, fresh(f"pool{i}n"), "pool")
        zs.append(rr["lags"][4]["z"])
        okpool = okpool and (rr["lags"][4]["v"] <= PREREG["lag_pass_events"])
    zpool = sum(zs) / math.sqrt(len(zs))
    check("lag4: pooled z across 3 plants >= family watch bar",
          okpool and zpool >= PREREG["lag_family_watch_pool_z"],
          f"(zs={['%.1f'%z for z in zs]}, zpool={zpool:.1f})")

    # 5. sigma: persistence; not rejected by its own ledger
    rng = fresh("sig")
    A, B = plant_pair(rng, "sigma", dens=0.35)
    r = analyse_pair(A, B, fresh("sign"), "sigma-plant")
    check("sigma: not rejected by its own ledger",
          r["ledger"]["p_sigma"] > PREREG["sigma_reject_p"],
          f"(R={r['ledger']['R']}, p={r['ledger']['p_sigma']:.2e})")
    rr = runs_of(disagreement(A, B, 1))
    meandis = sum(l for v, l in rr if v == 1) / max(1, sum(1 for v, _ in rr if v == 1))
    check("sigma: persistent divergence blocks", meandis >= 8.0,
          f"(mean dis-run {meandis:.1f})")
    rng = fresh("xsig")
    A, B = plant_pair(rng, "xgak_sigma", dens=0.35)
    r = analyse_pair(A, B, fresh("xsign"), "xgak-sigma-plant")
    check("xgak-sigma: not rejected", r["ledger"]["p_sigma"] > PREREG["sigma_reject_p"],
          f"(R={r['ledger']['R']})")

    # 6. clustered static: no spurious lag watch; Sigma still rejected
    rng = fresh("clu")
    A, B = plant_pair(rng, "static", dens=0.5, clustered=True)
    r = analyse_pair(A, B, fresh("clun"), "static-clustered")
    watch = [k for k in LAGS if r["lags"][k]["verdict"] == "watch"]
    check("static-clustered: no spurious lag watch", len(watch) == 0, f"{watch}")
    check("static-clustered: Sigma rejected",
          r["ledger"]["p_sigma"] < PREREG["sigma_reject_p"],
          f"(p={r['ledger']['p_sigma']:.2e})")

    # 7. dense regime (W2/W3-like): single-pair power limited by design;
    #    direction must hold; pooled static across corpus densities carries
    rng = fresh("dense")
    A, B = plant_pair(rng, "static", dens=0.92)
    r = analyse_pair(A, B, fresh("densen"), "static-dense")
    check("dense: Sigma direction correct (p < 0.2)",
          r["ledger"]["p_sigma"] < 0.2,
          f"(R={r['ledger']['R']}, p={r['ledger']['p_sigma']:.2e}; single-pair power limited, pooled carries)")
    pooled_nD = pooled_R = 0
    for i, dd in enumerate((0.55, 0.73, 0.92)):
        rng = fresh(f"sp{i}")
        A, B = plant_pair(rng, "static", dens=dd)
        rr2 = analyse_pair(A, B, fresh(f"sp{i}n"), "pool")
        pooled_nD += rr2["ledger"]["nD"]; pooled_R += rr2["ledger"]["R"]
    pp = binom_sf(pooled_nD, 1.0 / N, pooled_R)
    check("static pooled (3 corpus densities): Sigma rejected",
          pp < PREREG["sigma_reject_p"], f"(R={pooled_R}, p={pp:.2e})")

    # 8. power replicates at dens 0.55: census discrimination is the primary
    # lag statistic (echo z is confirmatory only; per-pair z power at this
    # density is ~0.2 and is reported, not gated)
    hits = 0; zhits = 0
    for i in range(10):
        rng = fresh(f"pw{i}")
        A, B = plant_pair(rng, "lag", dens=0.55, k=4)
        r = analyse_pair(A, B, fresh(f"pw{i}n"), "p")
        others = sum(1 for k in LAGS if k != 4 and r["lags"][k]["verdict"] == "REJECTED")
        if r["lags"][4]["v"] <= PREREG["lag_pass_events"] and others >= 6:
            hits += 1
        if r["lags"][4]["z"] >= PREREG["lag_watch_z"]:
            zhits += 1
    check("lag4 census power at dens 0.55 >= 7/10", hits >= 7,
          f"({hits}/10 census; echo-z watch fired {zhits}/10, informational)")
    clean = 0
    for i in range(10):
        rng = fresh(f"st{i}")
        A, B = plant_pair(rng, "static", dens=0.55)
        r = analyse_pair(A, B, fresh(f"st{i}n"), "p")
        if not any(r["lags"][k]["verdict"] == "watch" for k in LAGS):
            clean += 1
    check("static at 0.55: no false lag watch in >=9/10", clean >= 9, f"({clean}/10)")

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")
    return ok

# ----------------------------------------------------------------------------
# Deduction A -- atlas forced-identity check (pure lag-k exclusion)
# ----------------------------------------------------------------------------
def atlas_check(atlas_path, corpus_path):
    a = json.load(open(atlas_path)); M = load_corpus(corpus_path)
    kill = 0; rows = []
    for cls in a["classes"]:
        L = cls["length"]; bym = {}
        for it in cls["instances"]:
            if M[it["message"]][it["start"]:it["start"] + L] != it["values"]:
                fail("atlas values do not match corpus")
            bym.setdefault(it["message"], []).append(it)
        for msg, lst in bym.items():
            for i in range(len(lst)):
                for j in range(i + 1, len(lst)):
                    A = lst[i]["values"]; B = lst[j]["values"]
                    ident = sum(1 for t in range(L) if A[t] == B[t])
                    viol = max((t for t in range(L) if A[t] != B[t]), default=-1)
                    rows.append((cls["id"], msg, lst[i]["start"], lst[j]["start"],
                                 L, ident, viol))
                    kill = max(kill, viol)
    return kill, rows

# ----------------------------------------------------------------------------
# corpus run
# ----------------------------------------------------------------------------
def corpus_run(corpus_path):
    rng = random.Random(RNG_SEED + 1)
    M = load_corpus(corpus_path)
    print("\npre-registered thresholds:", json.dumps(PREREG))
    results = []
    for a, b in NEAR_DUPS:
        A, B = M[a], M[b]
        r = analyse_pair(A, B, rng, f"{a} / {b}")
        results.append(r)
        led = r["ledger"]
        print(f"\n=== {r['label']} ===  overlap n={r['n']}  agree={r['agree']:.3f}"
              f"  guard={r['guard']} (tail agree {r['guard_tail']:.2f})")
        print(f"  Sigma ledger: R={led['R']} re-syncs, B={led['B']} dis-runs, "
              f"|D|={led['nD']}, p_Sigma={led['p_sigma']:.3e}"
              f"  -> {'REJECTED' if led['p_sigma'] < PREREG['sigma_reject_p'] else 'not rejected'}")
        print(f"  {'k':>2s} {'echo':>5s} {'z':>7s} {'v(k)':>5s} {'P(v0|null)':>10s}  verdict")
        for k in LAGS:
            row = r["lags"][k]
            print(f"  {k:2d} {row['echo']:5d} {row['z']:7.2f} {row['v']:5d} "
                  f"{row['p_v0_null']:10.3f}  {row['verdict']}")
        if r["guard"] != "PASS":
            sw = offset_sweep(M[a], M[b])
            print("  offset sweep (indel probe):",
                  {s: round(v, 3) for s, v in sw.items()})
    # pooled Sigma
    pooled_nD = sum(r["ledger"]["nD"] for r in results)
    pooled_R = sum(r["ledger"]["R"] for r in results)
    pooled_p = binom_sf(pooled_nD, 1.0 / N, pooled_R)
    print(f"\npooled Sigma ledger: R={pooled_R}, |D|={pooled_nD}, "
          f"p_Sigma={pooled_p:.3e} -> "
          f"{'REJECTED (up to balanced-edit loophole)' if pooled_p < PREREG['sigma_reject_p'] else 'not rejected'}")
    return results, pooled_p

# ----------------------------------------------------------------------------
if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(here, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(here, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    if "--atlas" in sys.argv:
        kill, rows = atlas_check(atlas, corpus)
        for r in rows:
            print(f"  {r[0]:5s} {r[1]:8s} @{r[2]}vs@{r[3]}  L={r[4]}  "
                  f"identities={r[5]}  last-violating j={r[6]}")
        print(f"pure lag-k GAK excluded for all k in [1, {kill}]")
        sys.exit(0)
    selftest()                      # gate: never run corpus on a red harness
    corpus_run(corpus)
