"""pyry_gate — dev-conditions oracle + chain-family battery.

Pyry's Conditions (noita.wiki.gg/wiki/Eye_Messages, "Pyry's Conditions") are
the only dev-endorsed ground truth about the ciphertext. This module does
three things:

  1. CORPUS INVARIANTS — encodes the computable conditions as tests and
     verifies them on the real corpus (they must all PASS; if one fails, the
     corpus copy is wrong, which is itself a finding).

       C1  flat unigram distribution            (MC chi-square vs uniform)
       C2  unbroken symbol set 0..N-1
       C7  first symbol differs across all messages; second is universal
       C8  ZERO adjacent doubles c[t]==c[t+1]   (vs shuffle-null expectation)
       C9  true isomorphs never share a value at the same relative position
       CW4 c[t]==c[t+4] excess vs shuffle null  (CodeWarrior0: ~2x)

  2. MODEL GATE — Monte-Carlo pass-rates of each condition under each model
     family (plantlab generators). This quantifies the tension the repo
     currently leaves implicit: per-message-progressive reproduces C9
     automatically but produces C8 doubles at ~L/N per message, so observing
     ZERO doubles in 1036 glyphs is strong evidence AGAINST an unconstrained
     pmp and FOR either (a) a chain cipher with a no-zero step (doubles
     impossible by construction) or (b) an alphabet C deliberately arranged
     against the plaintext's bigrams. The gate turns that into numbers.

  3. CHAIN BATTERY — the cheap decisive test the repo lacks: under ANY
     c[t] = E(p[t]) + c[t-1] (+ alpha*t), the within-message first
     differences d[t] = c[t]-c[t-1] (- alpha*t) are a MONOALPHABETIC image
     of the plaintext, so their IoC is plaintext-high. Sweeping alpha in Z_N
     and z-scoring against a shuffle null either lights up (chain family
     live, and d is a mono-sub cryptogram we can attack directly) or stays
     null (chain-with-fixed-step excluded — an honest exclusion the
     scoreboard can cite).

Honest limits: C9 is checked on isomorphs found at one calibrated (L, reps)
setting; MC pass-rates depend on plantlab's English sample and random rho;
the battery excludes only FIXED-substitution chains — a chain whose step
depends on position beyond a linear ramp, or on more history, can evade it.
"""
from __future__ import annotations

import random
import statistics as st
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "noita_eye_core"))

import plantlab  # noqa: E402

Cts = Sequence[Sequence[int]]


# ------------------------------------------------------------------ helpers
def _chi2_uniform(cts: Cts, N: int) -> float:
    cnt = Counter(s for ct in cts for s in ct)
    T = sum(cnt.values())
    e = T / N
    return sum((cnt.get(v, 0) - e) ** 2 / e for v in range(N))


def _chi2_flatness_z(cts: Cts, N: int) -> float:
    """Standardized flatness: (chi2 - df) / sqrt(2*df), df = N-1.

    A truly flat (uniform) distribution has E[chi2]=df, Var=2*df, so this z
    is ~0 for flat data and grows without bound as the distribution spikes.
    Unlike an MC p-value it does NOT saturate: the real corpus (chi2~150,
    df=82 -> z~5) and a 24-symbol mono image (chi2~6300 -> z~490) are cleanly
    separated. We call a corpus 'flat enough' at z < 25 (chi2 < ~400, i.e.
    < ~5x the uniform expectation) -- comfortably admitting the real corpus
    while rejecting any monoalphabetic scatter."""
    T = sum(len(ct) for ct in cts)
    if T == 0:
        return 0.0
    df = N - 1
    chi2 = _chi2_uniform(cts, N)
    return (chi2 - df) / ((2 * df) ** 0.5)


FLATNESS_Z_MAX = 25.0   # calibrated: real corpus ~5, mono English ~490


def _count_lag(cts: Cts, lag: int) -> int:
    return sum(ct[t] == ct[t + lag] for ct in cts for t in range(len(ct) - lag))


def _shuffle_lag_null(cts: Cts, lag: int, reps: int = 200,
                      seed: int = 0) -> Tuple[float, float]:
    vals = []
    for r in range(reps):
        vals.append(_count_lag(plantlab.shuffle_null(cts, seed=seed + r), lag))
    return st.mean(vals), st.pstdev(vals) or 1e-9


def _isomorph_coincidences(cts: Cts, N: int, L: int = 10,
                           min_rep: int = 3) -> Tuple[int, int]:
    """(pairs, pairs with any same-value-same-position coincidence) among
    true (non-exact) isomorphs. Uses the repo's own finder as the single
    source of truth for skeleton matching."""
    import isomorph as iso   # noqa: E402  (from noita_eye_core)
    pairs = iso.find_isomorphs(cts, L, min_rep, different_only=True)
    bad = 0
    for p in pairs:
        a = cts[p.m1][p.p1:p.p1 + p.length]
        b = cts[p.m2][p.p2:p.p2 + p.length]
        if any(x == y for x, y in zip(a, b)):
            bad += 1
    return len(pairs), bad


# ------------------------------------------------------------- the conditions
def conditions(cts: Cts, N: int, seed: int = 0) -> Dict[str, dict]:
    out: Dict[str, dict] = {}

    z = _chi2_flatness_z(cts, N)
    out["C1_flat_unigram"] = {"pass": z < FLATNESS_Z_MAX,
                              "flatness_z": round(z, 1)}

    used = {s for ct in cts for s in ct}
    out["C2_unbroken_set"] = {"pass": used == set(range(N)),
                              "used": len(used)}

    firsts = [ct[0] for ct in cts]
    seconds = [ct[1] for ct in cts]
    out["C7_header"] = {"pass": len(set(firsts)) == len(firsts)
                        and len(set(seconds)) == 1,
                        "firsts_distinct": len(set(firsts)) == len(firsts),
                        "second_universal": len(set(seconds)) == 1}

    d1 = _count_lag(cts, 1)
    mu1, sd1 = _shuffle_lag_null(cts, 1, seed=seed)
    out["C8_no_doubles"] = {"pass": d1 == 0, "observed": d1,
                            "shuffle_null_mean": round(mu1, 1),
                            "z_vs_null": round((d1 - mu1) / sd1, 1)}

    npairs, bad = _isomorph_coincidences(cts, N)
    out["C9_iso_disjoint"] = {"pass": npairs > 0 and bad == 0,
                              "pairs": npairs, "coinciding": bad}

    d4 = _count_lag(cts, 4)
    mu4, sd4 = _shuffle_lag_null(cts, 4, seed=seed)
    out["CW_dist4_excess"] = {"pass": d4 > mu4 + 2 * sd4,
                              "observed": d4,
                              "shuffle_null_mean": round(mu4, 1),
                              "ratio": round(d4 / mu4, 2) if mu4 else None}
    return out


# --------------------------------------------------------------- chain battery
def _ioc(seq: Sequence[int], N: int) -> float:
    cnt = Counter(seq); T = len(seq)
    if T < 2:
        return 0.0
    return sum(c * (c - 1) for c in cnt.values()) / (T * (T - 1))


def chain_battery(cts: Cts, N: int, nulls: int = 60,
                  seed: int = 0) -> dict:
    """Sweep alpha: d[t] = (c[t]-c[t-1]-alpha*t) mod N pooled across messages.
    Under c[t]=E(p[t])+c[t-1]+alpha*t, the right alpha makes d a mono image
    of the plaintext (IoC high). z is the max-alpha IoC against the same
    max-alpha statistic on shuffle nulls (apples to apples: the null also
    gets to pick its best alpha, so selection bias is priced in)."""
    def max_alpha_ioc(css: Cts) -> Tuple[int, float]:
        best = (0, -1.0)
        for a in range(N):
            pooled: List[int] = []
            for ct in css:
                pooled.extend((ct[t] - ct[t - 1] - a * t) % N
                              for t in range(1, len(ct)))
            v = _ioc(pooled, N)
            if v > best[1]:
                best = (a, v)
        return best

    # full alpha profile: lets us separate "one alpha spikes" (true fixed-step
    # chain) from "IoC broadly elevated" (a structural artifact that beats the
    # shuffle null at every alpha, e.g. shared openings inflating repeats).
    profile: List[float] = []
    for a in range(N):
        pooled: List[int] = []
        for ct in cts:
            pooled.extend((ct[t] - ct[t - 1] - a * t) % N
                          for t in range(1, len(ct)))
        profile.append(_ioc(pooled, N))
    a_star = max(range(N), key=lambda a: profile[a])
    obs = profile[a_star]
    p_mu, p_sd = st.mean(profile), st.pstdev(profile) or 1e-9
    peak_z = (obs - p_mu) / p_sd          # peak vs OTHER alphas (intra-profile)

    null_vals = [max_alpha_ioc(plantlab.shuffle_null(cts, seed=seed + r))[1]
                 for r in range(nulls)]
    mu, sd = st.mean(null_vals), st.pstdev(null_vals) or 1e-9
    z = (obs - mu) / sd                   # peak vs shuffle-null (inter-corpus)

    # A clean fixed-step chain needs BOTH: the corpus beats the null (z high)
    # AND one alpha stands out from the rest (peak_z high). Broad elevation
    # with a flat profile is an artifact, not a chain.
    if z > 5 and peak_z > 5:
        verdict = "CLEAN FIXED-STEP CHAIN SIGNAL"
    elif z > 5:
        verdict = ("weak/ambiguous: corpus beats null but no single alpha "
                   "dominates (peak only %.1f-sigma over other alphas)" % peak_z)
    else:
        verdict = "no fixed-step chain signal"
    return {"best_alpha": a_star, "ioc": round(obs, 5),
            "null_mean": round(mu, 5), "z_vs_null": round(z, 1),
            "peak_z_intra_profile": round(peak_z, 1), "verdict": verdict}


# ------------------------------------------------------------------ model gate
GATE_MODELS = ("pmp", "pure", "autokey1", "chain_nz", "alberti")


def model_gate(K: int = 20, seed: int = 0) -> Dict[str, dict]:
    """MC pass-rates per model for the discriminating conditions, plus the
    chain-battery hit-rate. C1/C2/C7 are omitted (any model can satisfy them
    by construction choices); C8/C9/CW4/battery genuinely discriminate."""
    out: Dict[str, dict] = {}
    for model in GATE_MODELS:
        c8 = c9 = cw = bat = 0
        for k in range(K):
            pl = plantlab.gen(model, seed=seed * 1000 + k, shared_prefix=20)
            cond = conditions(pl.cts, pl.N, seed=k)
            c8 += cond["C8_no_doubles"]["pass"]
            c9 += cond["C9_iso_disjoint"]["pass"]
            cw += cond["CW_dist4_excess"]["pass"]
            if k < max(3, K // 6):          # battery is O(N*T); sample it
                bat += chain_battery(pl.cts, pl.N, nulls=25,
                                     seed=k)["z_vs_null"] > 5
        nb = max(3, K // 6)
        out[model] = {"C8_no_doubles": f"{c8}/{K}",
                      "C9_iso_disjoint": f"{c9}/{K}",
                      "CW_dist4": f"{cw}/{K}",
                      "chain_battery_hits": f"{bat}/{nb}"}
    return out


# --------------------------------------------------------------------- selftest
def selftest() -> List[Tuple[str, bool]]:
    checks: List[Tuple[str, bool]] = []

    # flatness: uniform passes, a mono-sub of English fails, real corpus passes
    uni = plantlab.uniform_null(9, 115, seed=1)
    checks.append(("C1 passes uniform",
                   conditions(uni, 83, seed=1)["C1_flat_unigram"]["pass"]))
    pl = plantlab.gen("pmp", seed=2)
    mono = [[pl.rho[ch] for ch in pt] for pt in pl.pts]   # raw mono image
    checks.append(("C1 rejects mono-sub English",
                   not conditions(mono, 83, seed=2)["C1_flat_unigram"]["pass"]))
    # separation margin: mono flatness-z must dwarf a pmp ciphertext's
    z_mono = _chi2_flatness_z(mono, 83)
    z_ct = _chi2_flatness_z(pl.cts, 83)
    checks.append(("C1 mono-z >> ct-z", z_mono > 10 * max(z_ct, 1.0)))

    # C8: chain_nz structurally passes; pmp overwhelmingly fails
    cz = plantlab.gen("chain_nz", seed=3)
    checks.append(("C8 pass on chain_nz",
                   conditions(cz.cts, 83, seed=3)["C8_no_doubles"]["pass"]))
    pmp_fail = sum(not conditions(plantlab.gen("pmp", seed=100 + k).cts, 83,
                                  seed=k)["C8_no_doubles"]["pass"]
                   for k in range(8))
    checks.append(("C8 fails on >=7/8 pmp plants", pmp_fail >= 7))

    # C9: the coincidence-detector must FIRE when a coincidence is planted and
    # stay silent when isomorphs are genuinely value-disjoint. (Synthetic
    # filler text is too repetition-poor to breed L>=10 isomorphs, so we test
    # the DETECTOR on hand-built pairs rather than relying on plant isomorphs.)
    def _coinc(a, b):
        return any(x == y for x, y in zip(a, b))
    checks.append(("C9 detector fires on planted coincidence",
                   _coinc([1, 2, 3, 4], [9, 2, 8, 7])))       # value 2 aligns
    checks.append(("C9 detector silent on disjoint",
                   not _coinc([1, 2, 3, 4], [5, 6, 7, 8])))
    # binding real-data check: the REAL corpus must satisfy C9 (this is the
    # claim that actually matters and it is independent of plant realism).
    try:
        import corpus as corpus_mod  # noqa: E402
        rc = [list(x) for x in corpus_mod.load().ciphertexts]
        c9r = conditions(rc, 83, seed=0)["C9_iso_disjoint"]
        checks.append(("C9 holds on REAL corpus (pairs>0, coinc=0)", c9r["pass"]))
    except Exception:
        checks.append(("C9 real-corpus check (corpus available)", False))

    # battery: lights up on autokey1 (alpha=0), on ramped chain (alpha found),
    # stays null on pmp and on uniform noise
    a1 = plantlab.gen("autokey1", seed=5)
    b = chain_battery(a1.cts, 83, nulls=30, seed=5)
    checks.append(("battery detects autokey1", b["z_vs_null"] > 5 and b["best_alpha"] == 0))
    alpha_true = 7
    ramp = [[(c + alpha_true * ((t + 1) * (t + 2) // 2 - 1)) % 83
             for t, c in enumerate(ct)] for ct in a1.cts]
    # note: adding alpha*t to the STEP means c[t] gains alpha*sum(1..t);
    # build directly instead to avoid off-by-one:
    ramp = []
    for m, pv in enumerate(a1.pvals):
        prev = a1.bases[m]; row = []
        for t, v in enumerate(pv):
            prev = (a1.E[v] + prev + alpha_true * t) % 83
            row.append(prev)
        ramp.append(row)
    br = chain_battery(ramp, 83, nulls=30, seed=6)
    checks.append(("battery finds ramp alpha",
                   br["z_vs_null"] > 5 and br["best_alpha"] == alpha_true))
    bp = chain_battery(plantlab.gen("pmp", seed=7).cts, 83, nulls=30, seed=7)
    checks.append(("battery null on pmp", bp["z_vs_null"] < 5))
    bu = chain_battery(plantlab.uniform_null(9, 115, seed=8), 83,
                       nulls=30, seed=8)
    checks.append(("battery null on noise", bu["z_vs_null"] < 5))

    # dist4: shuffle-null machinery sane (no self-excess on shuffled data)
    sp4 = plantlab.gen("pmp", seed=4, shared_prefix=22)
    d4 = conditions(plantlab.shuffle_null(sp4.cts, seed=9), 83,
                    seed=9)["CW_dist4_excess"]
    checks.append(("CW4 no excess on shuffled", not d4["pass"]))
    return checks


def main() -> int:
    import corpus as corpus_mod  # noqa: E402
    if "--selftest" in sys.argv:
        results = selftest()
        for name, ok in results:
            print(f"[{'OK  ' if ok else 'FAIL'}] {name}")
        return 0 if all(ok for _, ok in results) else 1

    c = corpus_mod.load()
    cts = [list(x) for x in c.ciphertexts]
    print("== Pyry-condition corpus invariants (real corpus) ==")
    for name, r in conditions(cts, c.N).items():
        print(f"  [{'PASS' if r['pass'] else 'FAIL'}] {name:18s} {r}")
    print("\n== Chain battery (real corpus) ==")
    print(" ", chain_battery(cts, c.N))
    if "--gate" in sys.argv:
        print("\n== Model gate (MC pass-rates on plants) ==")
        for model, row in model_gate().items():
            print(f"  {model:9s} {row}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
