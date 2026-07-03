"""model_power — how much does the progressive-consistency test actually prove?

The repo's leading model rests substantially on ONE instrument: the
per-message-progressive chain test comes out CONSISTENT on the real corpus. This
module measures that instrument's discrimination power with ground-truth plants
and reports what "consistent" does and does not buy. Purely descriptive: it
counts how each cipher family behaves under the test so the confirmation the
repo already trusts can be read with correct error bars.

============================================================ FINDING 0 (a trap)
ISOMORPH YIELD DOES NOT DISCRIMINATE. It is tempting to argue "autokey/Alberti
destroy isomorphs, and the real corpus has isomorphs, so they're excluded." That
argument is WRONG. The skeleton of a repeated word is a function of the word's
own internal structure (partial sums under chaining, cumulative rotation under
Alberti) and is INVARIANT to the per-instance history offset. So a repeated word
yields the SAME skeleton -- a detectable isomorph -- under autokey and Alberti
just as under a progressive cipher. `skeleton_preservation` shows all families
preserve planted-repeat skeletons at rate ~1.0. Yield tells us a repeat existed,
not which cipher produced it.

===================================================== FINDING 1 (the real one)
The discriminator is CONSTRAINT STRUCTURE, not yield. Given the same isomorph
pairs, each cipher family implies a different linear relation among the q-values:
progressive/beaufort give q[c1]-q[c2] = (base_m1-base_m2)+(p1-p2); autokey gives
a constant per-message-pair offset; periodic gives a period-dependent offset.
The progressive chain test therefore CONTRADICTS the wrong families hard:

    progressive-chain contradictions on clean pairs (mean):
        pmp / pure / beaufort : 0
        periodic              : ~6000
        autokey-1             : ~7500
        Alberti               : ~7400

and the matching autokey-chain accepts autokey/Alberti 8/8. So the real corpus
passing progressive-chain with ZERO contradictions genuinely excludes autokey,
Alberti, and periodic -- a strong, clean result. `discrimination_matrix`
measures it.

===================================================== FINDING 2 (a real limit)
The test confirms an EQUIVALENCE CLASS, not per-msg-progressive specifically.
For a same-plaintext isomorph pair the plaintext value CANCELS between the two
matched positions, so the constraint is blind to HOW plaintext enters. A
Beaufort cipher c[t]=C[(base_m - p[t] + t)] (plaintext SIGN-FLIPPED) yields
constraints identical to pmp and passes 8/8, 0 contradictions -- indistinguish-
able from pmp under this test. Consequence: the ordering attack should target
the whole linear class, and order_anneal should try the beaufort (-p) map as
well as (+p) when reading.

===================================================== FINDING 3 (a method trap)
Consensus PRE-FILTERING makes the test circular. `consensus_alphabet` keeps only
pairs consistent with `per_msg_prog_rows`, so a periodic corpus filtered that way
then "passes" the progressive test -- the contradicting evidence was discarded
first. Discrimination must use RAW or clean pairs. `consensus_circularity` shows
the periodic contradiction count collapsing from thousands (raw) to ~0
(filtered).

HONEST LIMITS: plants use plantlab generators with English-like value
frequencies; "clean pairs" use known planted positions (the uncontaminated upper
bound on discrimination). The real corpus offers only found pairs, so its row is
reported on the axes that don't need ground-truth alignment (yield, and
raw-pair progressive-consistency).
"""
from __future__ import annotations

import random
import statistics as st
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "noita_eye_core"))

import plantlab          # noqa: E402
import isomorph as iso   # noqa: E402
import chain_models as cm    # noqa: E402

REAL_LENGTHS = [99, 103, 118, 102, 137, 124, 119, 120, 114]
REAL_GROUPS = [[0, 1, 2], [6, 7, 8]]
LINEAR_CLASS = ("pmp", "pure", "beaufort")     # pass progressive-chain
REJECTED = ("periodic", "autokey1", "alberti")  # contradict progressive-chain


# --------------------------------------------------------- controlled plants
def planted_corpus(model: str, seed: int, *, N: int = 83, M: int = 9,
                   T: int = 110, wlen: int = 13, positions=(10, 35, 62, 88)):
    """One fixed plaintext word planted at fixed MID-message positions in every
    message; encode under `model`; return (cts, clean_pairs from the KNOWN
    positions). Mid-message (not opening) placement gives each instance a
    different history, which is the honest test bed -- yet note (Finding 0) the
    skeletons still match across models."""
    rng = random.Random(seed)
    word = [rng.randrange(27) for _ in range(wlen)]
    pv = [[rng.randrange(27) for _ in range(T)] for _ in range(M)]
    for m in range(M):
        for p in positions:
            pv[m][p:p + wlen] = word
    C = list(range(N)); random.Random(seed + 1).shuffle(C)
    if model in ("pmp", "pure"):
        bases = ([random.Random(seed + 2 + m).randrange(N) for m in range(M)]
                 if model == "pmp"
                 else [random.Random(seed + 2).randrange(N)] * M)
        cts = [[C[(pv[m][t] + bases[m] + t) % N] for t in range(T)]
               for m in range(M)]
    elif model == "beaufort":
        bases = [random.Random(seed + 2 + m).randrange(N) for m in range(M)]
        cts = [[C[(bases[m] - pv[m][t] + t) % N] for t in range(T)]
               for m in range(M)]
    elif model == "periodic":
        kl = 7
        key = [random.Random(seed + 9 + i).randrange(N) for i in range(kl)]
        ph = [random.Random(seed + 20 + m).randrange(kl) for m in range(M)]
        cts = [[C[(pv[m][t] + key[(t + ph[m]) % kl]) % N] for t in range(T)]
               for m in range(M)]
    elif model == "autokey1":
        cts = []
        for m in range(M):
            prev = random.Random(seed + 2 + m).randrange(N); c = []
            for t in range(T):
                prev = (pv[m][t] + prev) % N; c.append(C[prev])
            cts.append(c)
    elif model == "alberti":
        cts = []
        for m in range(M):
            k = random.Random(seed + 2 + m).randrange(N); c = []
            for t in range(T):
                c.append(C[(pv[m][t] + k) % N]); k = (k + 1 + pv[m][t]) % N
            cts.append(c)
    else:
        raise ValueError(model)
    inst = [(m, p) for m in range(M) for p in positions]
    pairs = [iso.IsoPair(inst[a][0], inst[a][1], inst[b][0], inst[b][1],
                         wlen, False)
             for a in range(len(inst)) for b in range(a + 1, len(inst))]
    return cts, pairs


# ------------------------------------------------- FINDING 0: yield is a trap
def skeleton_preservation(models=("pmp", "beaufort", "autokey1", "alberti"), *,
                          trials: int = 8, seed0: int = 0) -> Dict[str, float]:
    """Fraction of planted-repeat instance-pairs whose skeletons match (i.e.
    would be found as isomorphs). ~1.0 for ALL families -> yield does not
    discriminate."""
    out: Dict[str, float] = {}
    for model in models:
        rates = []
        for s in range(trials):
            cts, pairs = planted_corpus(model, seed0 + s)
            match = sum(iso.skeleton(cts[pr.m1][pr.p1:pr.p1 + pr.length])
                        == iso.skeleton(cts[pr.m2][pr.p2:pr.p2 + pr.length])
                        for pr in pairs)
            rates.append(match / len(pairs))
        out[model] = round(st.mean(rates), 3)
    return out


# -------------------------------------------- FINDING 1 & 2: discrimination
def discrimination_matrix(models=("pmp", "pure", "beaufort", "periodic",
                                  "autokey1", "alberti"), *,
                          trials: int = 8, seed0: int = 0) -> Dict[str, dict]:
    """progressive-chain vs autokey-chain on CLEAN pairs, per model. The
    progressive test accepts the linear class {pmp,pure,beaufort} at 0
    contradictions and rejects {periodic,autokey,alberti} at thousands."""
    out: Dict[str, dict] = {}
    for model in models:
        prog_c = []; prog_k = []; ak_c = []
        for s in range(trials):
            cts, pairs = planted_corpus(model, seed0 + s)
            p = cm.per_message_progressive_chain(cts, pairs, 83)
            a = cm.autokey_chain(cts, pairs, 83, k=1)
            prog_c.append(p.consistent); prog_k.append(p.contradictions)
            ak_c.append(a.consistent)
        out[model] = {
            "progressive_consistent": f"{sum(prog_c)}/{len(prog_c)}",
            "progressive_mean_contradictions": round(st.mean(prog_k), 0),
            "autokey_consistent": f"{sum(ak_c)}/{len(ak_c)}"}
    return out


# ------------------------------------------ FINDING 3: consensus circularity
def consensus_circularity(*, trials: int = 5, L: int = 13, rep: int = 2,
                          seed0: int = 0) -> Dict[str, dict]:
    import chain_extract as ce  # noqa: E402
    out: Dict[str, dict] = {}
    for model in ("pmp", "periodic"):
        raw = []; filt = []
        for s in range(trials):
            pl = plantlab.gen(model, n_msgs=9, lengths=REAL_LENGTHS,
                              groups=REAL_GROUPS, group_share=45, seed=seed0 + s)
            pairs = iso.find_isomorphs(pl.cts, L, rep, different_only=False)
            if len(pairs) < 3:
                continue
            raw.append(cm.per_message_progressive_chain(
                pl.cts, pairs, pl.N).contradictions)
            gf, keep = ce.consensus_alphabet(pl.cts, pairs, pl.N,
                                             cm.per_msg_prog_rows, seed=0)
            kp = [pairs[j] for j in keep] if keep else []
            if len(kp) >= 3:
                filt.append(cm.per_message_progressive_chain(
                    pl.cts, kp, pl.N).contradictions)
        out[model] = {"raw_contradictions": round(st.mean(raw), 0) if raw else None,
                      "filtered_contradictions": round(st.mean(filt), 0)
                      if filt else None}
    return out


# ------------------------------------------------------- real corpus report
def real_corpus_report() -> dict:
    import corpus as corpus_mod  # noqa: E402
    c = corpus_mod.load()
    cts = [list(x) for x in c.ciphertexts]
    ys = {f"L{L}_rep{rep}": len(iso.find_isomorphs(cts, L, rep,
                                                   different_only=False))
          for (L, rep) in ((10, 3), (13, 2), (13, 4))}
    pairs = iso.find_isomorphs(cts, 13, 4, different_only=False)
    stat = cm.per_message_progressive_chain(cts, pairs, c.N)
    return {"isomorph_yield": ys,
            "progressive_chain": {"pairs": len(pairs),
                                  "consistent": stat.consistent,
                                  "contradictions": stat.contradictions,
                                  "symbols_linked": stat.symbols_linked}}


# --------------------------------------------------------------------- selftest
def selftest() -> List[Tuple[str, bool]]:
    checks: List[Tuple[str, bool]] = []

    # FINDING 0: yield is NOT a discriminator (all families preserve skeletons).
    sk = skeleton_preservation(trials=6)
    checks.append((f"yield trap: all families preserve skeletons "
                   f"(min {min(sk.values()):.2f})",
                   all(v > 0.95 for v in sk.values())))
    checks.append(("yield trap: autokey preserves like pmp",
                   abs(sk["autokey1"] - sk["pmp"]) < 0.05))

    # FINDING 1: progressive-chain rejects the wrong families, accepts linear.
    dm = discrimination_matrix(trials=6)
    for m in LINEAR_CLASS:
        checks.append((f"{m}: progressive-consistent, 0 contra "
                       f"({dm[m]['progressive_consistent']})",
                       dm[m]["progressive_mean_contradictions"] == 0))
    for m in REJECTED:
        checks.append((f"{m}: progressive REJECTS "
                       f"({dm[m]['progressive_mean_contradictions']:.0f} contra)",
                       dm[m]["progressive_mean_contradictions"] > 100))
    # autokey/alberti accepted by the MATCHING test (sanity: they're real ciphers)
    checks.append(("autokey accepted by autokey-chain",
                   dm["autokey1"]["autokey_consistent"].startswith(
                       str(6))))

    # FINDING 2: beaufort indistinguishable from pmp (equivalence class).
    checks.append(("equivalence: beaufort ≡ pmp under the test",
                   dm["beaufort"]["progressive_consistent"]
                   == dm["pmp"]["progressive_consistent"]
                   and dm["beaufort"]["progressive_mean_contradictions"] == 0))

    # FINDING 3: consensus filtering hides the periodic contradiction.
    cc = consensus_circularity(trials=4)
    per = cc.get("periodic", {})
    checks.append(("consensus filter hides periodic contradiction",
                   per.get("raw_contradictions") is not None
                   and per.get("filtered_contradictions") is not None
                   and per["raw_contradictions"]
                   > 5 * max(per["filtered_contradictions"], 0.1)))

    # REAL CORPUS: abundant isomorphs AND progressive-consistent (0 contra) ->
    # in the linear class, autokey/alberti/periodic excluded.
    r = real_corpus_report()
    checks.append(("real corpus has abundant isomorphs",
                   r["isomorph_yield"]["L13_rep2"] > 20))
    checks.append(("real corpus progressive-consistent (raw rep4, 0 contra)",
                   r["progressive_chain"]["consistent"]
                   and r["progressive_chain"]["contradictions"] == 0))

    # determinism
    checks.append(("discrimination deterministic",
                   discrimination_matrix(trials=3)["pmp"]
                   == discrimination_matrix(trials=3)["pmp"]))
    return checks


def main() -> int:
    if "--selftest" in sys.argv:
        results = selftest()
        for name, ok in results:
            print(f"[{'OK  ' if ok else 'FAIL'}] {name}")
        return 0 if all(ok for _, ok in results) else 1

    print("== FINDING 0: isomorph yield is NOT a discriminator ==")
    print("  planted-repeat skeleton-match rate (want: ~1.0 for ALL):")
    for m, v in skeleton_preservation().items():
        print(f"    {m:10s} {v}")
    print("\n== FINDING 1+2: constraint-structure discrimination (clean pairs) ==")
    for m, r in discrimination_matrix().items():
        tag = "LINEAR " if m in LINEAR_CLASS else "reject "
        print(f"  [{tag}] {m:10s} {r}")
    print("  -> {pmp,pure,beaufort} one equivalence class; periodic/autokey/"
          "alberti rejected")
    print("\n== FINDING 3: consensus-filter circularity ==")
    for m, r in consensus_circularity().items():
        print(f"  {m:10s} {r}")
    print("\n== REAL CORPUS ==")
    r = real_corpus_report()
    print(f"  isomorph yield : {r['isomorph_yield']}")
    print(f"  progressive    : {r['progressive_chain']}")
    print("\n  Reading: abundant isomorphs + progressive-consistent (0 contra)"
          " place the real corpus in the {pmp,pure,beaufort} linear class;"
          " autokey/Alberti/periodic are excluded by the ZERO contradictions"
          " (they would each produce thousands). The test does NOT single out"
          " pmp -- order_anneal should also try the beaufort (-p) map.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
