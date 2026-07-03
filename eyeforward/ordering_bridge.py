#!/usr/bin/env python3
"""ordering_bridge -- same-day verdicts for alphabet-ordering hypotheses.

THE IDEA
========
Two workstreams now attack the same unknown from opposite sides.  The anchor
graph (iso_relax -> support_min) LINKS symbols but cannot ORDER them past a
0.012 ordering ratio; the deck-sweep / primer-cut work generates candidate
ORDERINGS but has no reader to tell a live one from a dud.  This module is
the bridge: feed it any ordering hypothesis -- full or partial, with or
without letter assignments -- and it returns a scored verdict the same day,
instead of a bespoke manual investigation per idea.

WHAT IT SWEEPS, AND WHY
=======================
model_power established that the corpus evidence pins down only the LINEAR
CLASS {pmp, pure, beaufort}: the chain test cannot see the plaintext SIGN
(same-plaintext pairs cancel it) and, at real sparsity, cannot see the time
DRIFT either ('pure' plants pass 6/6).  A hypothesis tester that assumes
sign=+ and drift=+1 would therefore silently fail on 5 of the 6 live model
variants.  So every read here sweeps:

    drift in {+1, 0, -1}   residue r[t] = q[c[t]] - drift*t
    sign  in {+, -}        plaintext p = +(r - base)  or  -(r - base)

The LEARNED read (order_anneal's climb) absorbs sign automatically -- a
sign flip only relabels the canonical residues, and the climb learns
arbitrary relabelings (locked in by order_anneal selftest check 6) -- so it
sweeps drift only.  The DIRECT read, available when the hypothesis includes
letter assignments, maps residues through the CLAIMED letters, where sign
genuinely matters; it sweeps drift x sign x global base offset.

HONEST LIMITS
=============
* Completion of PARTIAL hypotheses reuses support_min's anneal, which
  minimizes the drifted-residue support.  At drift=0 that objective is
  q-INVARIANT (distinct q[c[t]] == distinct c[t] for any permutation), so
  completion under drift=0 is refused with an explanation rather than
  returning noise.  Full-q scoring at drift=0 is fine (reads still work).
* drift=-1 completion reuses anneal unchanged via per-message REVERSAL:
  distinct(q[c[t]]+t) == distinct(q[c'[s]]-s) up to a per-message constant
  when c' is c reversed.  Reads do NOT use reversal (shared openings would
  move to the tail, blinding align_bases_by_prefix); they use the drift
  kwarg on reduce_to_residues directly.
* The support gap at 16 pins was ~+0.5 on the real corpus -- NOT decisive
  (the objective compresses any corpus somewhat at n=115, N=83).  verdicts
  therefore never PASS on support alone; a PASS requires a read.
* Direct-read relative bases come from shared openings (Pyry #3).  A
  hypothesis corpus without shared openings would need _fit_bases instead;
  the real corpus has them, so this bridge assumes them.

VERDICTS
========
PASS          a read (learned or direct) clears READ_Z with real words
SUPPORT_ONLY  support collapses far below the shuffle control, but no read
FAIL          neither
"""

from __future__ import annotations

import argparse
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, Union

HERE = Path(__file__).resolve().parent
for p in (HERE, HERE.parent / "noita_eye_core"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import plantlab                                            # noqa: E402
import support_min                                         # noqa: E402
import order_anneal                                        # noqa: E402

Cts = Sequence[Sequence[int]]

READ_Z = 6.0          # order_anneal precedent for "beats its own null"
SUPPORT_Z = -4.0      # permutation-null z for SUPPORT_ONLY (true q ~ -15)
READ_TOKENS = 0.25    # min fraction of decoded tokens that are real words
COMPLETE_GAP = 5.0    # anneal gap vs control for partial SUPPORT_ONLY
                      # (16 real pins gave ~+0.5-1.6: below; 40 true plant
                      #  pins gave +31.6: far above)
DRIFTS = (1, 0, -1)
SIGNS = (1, -1)


# --------------------------------------------------------------------------
# hypothesis normalization
# --------------------------------------------------------------------------
@dataclass
class Hypothesis:
    """A normalized ordering hypothesis.

    pins    : value -> position (always populated; full when complete)
    q       : full value -> position array, or None if partial
    letters : value -> claimed plaintext char (optional; enables direct read)
    """
    N: int
    pins: Dict[int, int]
    q: Optional[List[int]] = None
    letters: Optional[Dict[int, str]] = None
    label: str = "hypothesis"


def normalize(N: int, *,
              q: Optional[Sequence[int]] = None,
              C: Optional[Sequence[int]] = None,
              ordering: Optional[Sequence[int]] = None,
              pins: Optional[Dict[int, int]] = None,
              letters: Optional[Union[str, Dict[int, str]]] = None,
              label: str = "hypothesis") -> Hypothesis:
    """Accept any of the four hypothesis forms and normalize.

    q        full value->position permutation
    C        full position->value permutation (q is inverted from it)
    ordering possibly-PARTIAL sequence of values in position order
             (a primer-cut prefix: ordering[i] = value at position i)
    pins     explicit partial {value: position}
    letters  claimed plaintext chars: dict value->char, or a string aligned
             to POSITIONS (letters[i] = char at alphabet position i, which
             is converted through the ordering/q to value->char)
    """
    forms = [f for f in (q, C, ordering, pins) if f is not None]
    if len(forms) != 1:
        raise ValueError("give exactly one of q / C / ordering / pins")

    if C is not None:
        if sorted(C) != list(range(N)):
            raise ValueError("C must be a permutation of 0..N-1")
        q = [0] * N
        for pos, val in enumerate(C):
            q[val] = pos
    if q is not None:
        if sorted(q) != list(range(N)):
            raise ValueError("q must be a permutation of 0..N-1")
        pin_map = {v: q[v] for v in range(N)}
        full_q: Optional[List[int]] = list(q)
    elif ordering is not None:
        vals = list(ordering)
        if len(set(vals)) != len(vals):
            raise ValueError("ordering repeats a value")
        if any(not (0 <= v < N) for v in vals):
            raise ValueError("ordering value out of range")
        pin_map = {v: i for i, v in enumerate(vals)}
        full_q = None
        if len(vals) == N:
            full_q = [0] * N
            for i, v in enumerate(vals):
                full_q[v] = i
    else:
        pin_map = dict(pins)                                # type: ignore
        if len(set(pin_map.values())) != len(pin_map):
            raise ValueError("pins map two values to one position")
        full_q = None
        if len(pin_map) == N:
            full_q = [0] * N
            for v, pos in pin_map.items():
                full_q[v] = pos

    lmap: Optional[Dict[int, str]] = None
    if letters is not None:
        if isinstance(letters, dict):
            lmap = dict(letters)
        else:
            # a string over POSITIONS: route through the ordering to values.
            lmap = {}
            for v, pos in pin_map.items():
                if pos < len(letters):
                    lmap[v] = letters[pos]
    return Hypothesis(N=N, pins=pin_map, q=full_q, letters=lmap, label=label)


# --------------------------------------------------------------------------
# drift-generalized support (bit-compatible with support_min at drift=+1)
# --------------------------------------------------------------------------
def gsupport(q: Sequence[int], cts: Cts, N: int, drift: int = 1) -> float:
    tot = 0
    for ct in cts:
        tot += len({(q[c] - drift * t) % N for t, c in enumerate(ct)})
    return tot / len(cts)


def _reverse(cts: Cts) -> List[List[int]]:
    return [list(ct)[::-1] for ct in cts]


def complete(cts: Cts, N: int, pins: Dict[int, int], *, drift: int = 1,
             restarts: int = 6, iters: int = 6000, seed: int = 0
             ) -> Tuple[List[int], float]:
    """Complete a partial hypothesis by support-anneal at the given drift.

    drift=-1 rides on support_min unchanged via per-message reversal (a
    per-message constant offsets the residues, which distinct-counting
    ignores).  drift=0 is refused: the objective is then q-invariant.
    """
    if drift == 0:
        raise ValueError(
            "completion at drift=0 is meaningless: support of q[c[t]] is "
            "permutation-invariant, so the anneal would return noise")
    work = cts if drift == 1 else _reverse(cts)
    q_hat, sup, _ = support_min.anneal(work, N, pins=pins, restarts=restarts,
                                       iters=iters, seed=seed)
    return list(q_hat), float(sup)


# --------------------------------------------------------------------------
# reads
# --------------------------------------------------------------------------
def lexicon_bank() -> Dict[str, set]:
    """Token lexicons mirroring order_anneal.language_bank's sources.

    Needed because a climb's z (score vs its own random-O null) measures
    'found SOME structure', not 'text is readable'.  On the real corpus a
    drift-0 style raw climb hit z=37.9 in 'karelian' while decoding to
    letter soup -- the exact Finnish/Karelian mirage EyeStat's winners kept
    producing.  Verdicts therefore additionally require that a decent
    fraction of decoded tokens are real words of the winning language."""
    lex = {"english": {w for w in plantlab.SAMPLE_TEXT.lower().split()
                       if len(w) >= 3}}
    est = HERE.parent / "eyestat"
    for name, fn in (("finnish", "extra_words_fi.txt"),
                     ("karelian", "extra_words_krl.txt")):
        p = est / fn
        if p.exists():
            lex[name] = {w for w in p.read_text(
                encoding="utf-8", errors="ignore").lower().split()
                if len(w) >= 3}
    return lex


def readability(texts: Sequence[str], language: str,
                lex: Optional[Dict[str, set]] = None) -> float:
    """Fraction of length>=3 decoded tokens found in the language lexicon."""
    lex = lex or lexicon_bank()
    words = lex.get(language)
    if not words:
        return 0.0
    toks = [t for s in texts for t in s.lower().split() if len(t) >= 3]
    if not toks:
        return 0.0
    return sum(t in words for t in toks) / len(toks)


def _word_hits(texts: Sequence[str],
               words: Sequence[str] = ("the", "and", "work", "sun",
                                       "mountain", "miner", "before")) -> int:
    joined = " ".join(texts).lower()
    return sum(joined.count(w) for w in words)


def direct_read(cts: Cts, q: Sequence[int], N: int,
                letters: Dict[int, str], bank=None) -> dict:
    """Fixed-letter read: sweep drift x sign x global base offset.

    The hypothesis CLAIMS which letter sits at each alphabet value, so no
    substitution is learned -- the sweep alone decides.  This is where the
    Beaufort sign blindness would bite a naive reader, and where this
    module makes it a swept parameter instead.
    """
    bank = bank or order_anneal.language_bank()
    best = None
    for drift in DRIFTS:
        res = order_anneal.reduce_to_residues(cts, q, N, drift=drift)
        rel = order_anneal.align_bases_by_prefix(res, N)
        for sign in SIGNS:
            for lang, model in bank.items():
                for g in range(N):
                    texts = ["".join(
                        letters.get((sign * (r - rel[m] - g)) % N, " ")
                        for r in row) for m, row in enumerate(res)]
                    sc = sum(model.score(s) for s in texts) / len(texts)
                    if best is None or sc > best["score"]:
                        best = {"score": sc, "drift": drift, "sign": sign,
                                "g": g, "language": lang, "plaintext": texts}
    # z against a shuffled-letters null of the SAME winning geometry.
    rng = random.Random(0)
    res = order_anneal.reduce_to_residues(cts, q, N, drift=best["drift"])
    rel = order_anneal.align_bases_by_prefix(res, N)
    model = (bank[best["language"]])
    nulls = []
    vals = list(letters.keys())
    for _ in range(24):
        perm = vals[:]
        rng.shuffle(perm)
        lm = {v: letters[p] for v, p in zip(vals, perm)}
        texts = ["".join(
            lm.get((best["sign"] * (r - rel[m] - best["g"])) % N, " ")
            for r in row) for m, row in enumerate(res)]
        nulls.append(sum(model.score(s) for s in texts) / len(texts))
    mu = sum(nulls) / len(nulls)
    sd = (sum((x - mu) ** 2 for x in nulls) / len(nulls)) ** 0.5 or 1e-9
    best["z"] = round((best["score"] - mu) / sd, 1)
    best["hits"] = _word_hits(best["plaintext"])
    return best


def learned_read(cts: Cts, q: Sequence[int], N: int, *, bank=None,
                 drifts: Sequence[int] = (1, -1), restarts: int = 4,
                 iters: int = 8000, seed: int = 0) -> dict:
    """order_anneal climb per drift in {+1,-1}; sign is absorbed by the map.

    drift=0 is REFUSED for the same reason completion refuses it, one level
    up: at drift=0 the residues are a bare relabeling of the ciphertext,
    and the learned substitution absorbs relabelings -- so the climb's
    outcome is IDENTICAL for every hypothesis q.  It degenerates into a raw
    mono-sub attack on the corpus and says nothing about the ordering under
    test (the real corpus scored z=37.9 'karelian' letter soup this way).
    A drift=0 model remains testable via direct_read, where letters are
    claimed, not learned."""
    if 0 in drifts:
        raise ValueError("learned read at drift=0 is hypothesis-invariant: "
                         "the climb absorbs relabelings, so every q scores "
                         "identically; use direct_read for drift=0 models")
    best = None
    for drift in drifts:
        rep = order_anneal.solve(cts, q, N, bank=bank, restarts=restarts,
                                 iters=iters, seed=seed, drift=drift)
        rep = dict(rep)
        rep["drift"] = drift
        rep["hits"] = _word_hits(rep["plaintext"])
        if best is None or rep["z"] > best["z"]:
            best = rep
    return best


# --------------------------------------------------------------------------
# the scorecard
# --------------------------------------------------------------------------
def scorecard(cts: Cts, N: int, hyp: Hypothesis, *, bank=None,
              read_restarts: int = 4, read_iters: int = 8000,
              complete_restarts: int = 6, complete_iters: int = 6000,
              seed: int = 0) -> dict:
    """Full verdict for one hypothesis against one corpus."""
    card: dict = {"label": hyp.label, "n_pins": len(hyp.pins),
                  "partial": hyp.q is None}
    shuffled = plantlab.shuffle_null(cts, seed=seed)

    q = hyp.q
    if q is None:
        if len(hyp.pins) < 20:
            card["warning"] = (f"only {len(hyp.pins)} pins; support_min "
                               "recovery is unreliable below ~20-30")
        comp = {}
        for drift in (1, -1):
            q_d, sup_real = complete(cts, N, hyp.pins, drift=drift,
                                     restarts=complete_restarts,
                                     iters=complete_iters, seed=seed)
            _, sup_ctrl = complete(shuffled, N, hyp.pins, drift=drift,
                                   restarts=complete_restarts,
                                   iters=complete_iters, seed=seed)
            comp[drift] = {"q": q_d, "support": sup_real,
                           "control": sup_ctrl,
                           "gap": round(sup_ctrl - sup_real, 2)}
        best_drift = max(comp, key=lambda d: comp[d]["gap"])
        card["completion"] = {d: {k: v for k, v in comp[d].items()
                                  if k != "q"} for d in comp}
        card["completion_drift"] = best_drift
        q = comp[best_drift]["q"]

    # support panel for the (given or completed) full q.
    #
    # TWO nulls, deliberately:
    # * random-PERMUTATION null (same corpus, random q): "is THIS q special?"
    #   -- this is the verdict-bearing statistic.  A shuffled-CORPUS control
    # * shuffle-corpus gap: kept as a diagnostic only.  Real corpora carry
    #   intrinsic compressibility (repeated plaintext survives any q), so a
    #   WRONG q still shows a small positive shuffle gap; the selftest's
    #   wrong-q check exists to keep this trap from re-entering the verdict.
    rngq = random.Random(seed + 101)
    sup = {}
    for drift in (1, -1):
        real = gsupport(q, cts, N, drift)
        ctrl = gsupport(q, shuffled, N, drift)
        nulls = []
        for _ in range(24):
            qr = list(range(N))
            rngq.shuffle(qr)
            nulls.append(gsupport(qr, cts, N, drift))
        mu = sum(nulls) / len(nulls)
        sd = (sum((x - mu) ** 2 for x in nulls) / len(nulls)) ** 0.5 or 1e-9
        sup[drift] = {"real": round(real, 2), "control": round(ctrl, 2),
                      "gap": round(ctrl - real, 2),
                      "z_vs_random_q": round((real - mu) / sd, 1)}
    card["support"] = sup

    lex = lexicon_bank()
    lr = learned_read(cts, q, N, bank=bank, restarts=read_restarts,
                      iters=read_iters, seed=seed)
    lr["readability"] = round(readability(lr["plaintext"],
                                          lr["language"], lex), 2)
    card["learned"] = {k: lr[k] for k in
                       ("language", "z", "drift", "hits", "readability")}
    card["learned"]["snippet"] = lr["plaintext"][0][:70]
    reads = [("learned", lr["z"], lr["readability"])]

    if hyp.letters:
        dr = direct_read(cts, q, N, hyp.letters, bank=bank)
        dr["readability"] = round(readability(dr["plaintext"],
                                              dr["language"], lex), 2)
        card["direct"] = {k: dr[k] for k in
                          ("language", "z", "drift", "sign", "g", "hits",
                           "readability")}
        card["direct"]["snippet"] = dr["plaintext"][0][:70]
        reads.append(("direct", dr["z"], dr["readability"]))

    # best_z reports the strongest raw read; the PASS verdict additionally
    # requires readability, so a structural-z mirage never PASSes.
    best_reader, best_z, _ = max(reads, key=lambda r: r[1])
    passing = [r for r in reads
               if r[1] >= READ_Z and r[2] >= READ_TOKENS]

    # Verdict.  For a FULL hypothesis the permutation-null z is the honest
    # support statistic.  For a COMPLETED partial it is CIRCULAR -- the
    # anneal minimized exactly the quantity being z-scored -- so the
    # verdict-bearing statistic is instead the completion GAP against the
    # shuffled control annealed with identical effort (the overfit control
    # that first showed 16 pins were not enough).
    if card["partial"]:
        for s in sup.values():
            s["circular"] = True     # fitted q: do not read z as evidence
        sup_ok = (card["completion"][card["completion_drift"]]["gap"]
                  >= COMPLETE_GAP)
    else:
        sup_ok = min(s["z_vs_random_q"] for s in sup.values()) <= SUPPORT_Z
    if passing:
        best_reader, best_z, _ = max(passing, key=lambda r: r[1])
        card["verdict"] = "PASS"
    elif sup_ok:
        card["verdict"] = "SUPPORT_ONLY"
    else:
        card["verdict"] = "FAIL"
    card["best_reader"] = best_reader
    card["best_z"] = best_z
    card["q"] = q
    return card


# --------------------------------------------------------------------------
# selftest -- the paranoia audit
# --------------------------------------------------------------------------
def _reverse_drift_plant(seed: int = 5) -> "plantlab.Plant":
    """A drift=-1 plant built from pmp ground truth: c = C[p + base - t]."""
    pl = plantlab.gen("pmp", seed=seed, shared_prefix=20)
    C = [0] * pl.N
    for v, pos in enumerate(pl.q):
        C[pos] = v
    cts = [[C[(pl.pvals[m][t] + pl.bases[m] - t) % pl.N]
            for t in range(len(pl.pvals[m]))] for m in range(len(pl.pvals))]
    pl.cts = cts
    pl.model = "pmp_rev"
    return pl


def _true_letters(pl) -> Dict[int, str]:
    return {v: ch for ch, v in pl.rho.items()}


def selftest() -> List[Tuple[str, bool]]:
    checks: List[Tuple[str, bool]] = []
    N = 83
    bank = {"english": order_anneal.CharNgram.train(plantlab.SAMPLE_TEXT,
                                                    plantlab.ALPHABET)}
    pl = plantlab.gen("pmp", seed=3, shared_prefix=20)
    C_true = [0] * N
    for v, pos in enumerate(pl.q):
        C_true[pos] = v

    # (1-3) normalization KATs across all input forms.
    h_q = normalize(N, q=pl.q)
    h_C = normalize(N, C=C_true)
    checks.append(("normalize: q and C forms agree", h_q.q == h_C.q == list(pl.q)))
    part = C_true[:30]
    h_o = normalize(N, ordering=part)
    ok = (h_o.q is None and len(h_o.pins) == 30
          and all(h_o.pins[v] == i for i, v in enumerate(part)))
    checks.append(("normalize: partial ordering -> pins", ok))
    try:
        normalize(N, ordering=[1, 2, 1])
        checks.append(("normalize: rejects duplicate values", False))
    except ValueError:
        checks.append(("normalize: rejects duplicate values", True))

    # (4) gsupport is bit-compatible with support_min at drift=+1.
    a = gsupport(pl.q, pl.cts, N, 1)
    b = support_min.support(pl.q, pl.cts, N)
    checks.append(("gsupport(drift=1) == support_min.support", a == b))

    # (5) full true q: support panel shows a decisive real-vs-control gap.
    sc = scorecard(pl.cts, N, h_q, bank=bank, seed=1,
                   read_restarts=10, read_iters=18000)
    gap = sc["support"][1]["gap"]
    zq = sc["support"][1]["z_vs_random_q"]
    checks.append((f"true q: support decisive (gap={gap}, z={zq})",
                   gap > 10 and zq < -8))

    # (6) full true q: verdict PASS via the learned read.
    checks.append((f"true q: verdict PASS (z={sc['best_z']}, "
                   f"readability={sc['learned']['readability']})",
                   sc["verdict"] == "PASS" and sc["learned"]["drift"] == 1))

    # (7) direct read picks sign=+ on a pmp plant with true letters.
    dr = direct_read(pl.cts, pl.q, N, _true_letters(pl), bank=bank)
    checks.append((f"direct read: pmp -> sign=+ (z={dr['z']}, "
                   f"hits={dr['hits']})",
                   dr["sign"] == 1 and dr["drift"] == 1
                   and dr["z"] > READ_Z and dr["hits"] >= 20))

    # (8) direct read picks sign=- on a beaufort plant: the exact blind
    #     spot model_power flagged, now a swept parameter.
    plb = plantlab.gen("beaufort", seed=7, shared_prefix=20)
    drb = direct_read(plb.cts, plb.q, N, _true_letters(plb), bank=bank)
    checks.append((f"direct read: beaufort -> sign=- (z={drb['z']}, "
                   f"hits={drb['hits']})",
                   drb["sign"] == -1 and drb["drift"] == 1
                   and drb["z"] > READ_Z and drb["hits"] >= 20))

    # (9) drift sweep: a reverse-drift plant is read at drift=-1.
    plr = _reverse_drift_plant(seed=5)
    drr = direct_read(plr.cts, plr.q, N, _true_letters(plr), bank=bank)
    checks.append((f"direct read: reverse plant -> drift=-1 (z={drr['z']})",
                   drr["drift"] == -1 and drr["sign"] == 1
                   and drr["z"] > READ_Z))

    # (10) a WRONG full ordering fails: no support gap, no read.
    rng = random.Random(13)
    q_bad = list(range(N))
    rng.shuffle(q_bad)
    scb = scorecard(pl.cts, N, normalize(N, q=q_bad, label="wrong"),
                    bank=bank, read_restarts=2, read_iters=3000, seed=1)
    zqb = min(s["z_vs_random_q"] for s in scb["support"].values())
    checks.append((f"wrong q: verdict FAIL (read z={scb['best_z']}, "
                   f"support z={zqb})", scb["verdict"] == "FAIL"))

    # (11) partial hypothesis: 40 true pins complete to a high-recovery q
    #      and a positive anneal gap vs the shuffled control.
    pins40 = {v: pl.q[v] for v in range(N) if pl.q[v] < 40}
    scp = scorecard(pl.cts, N, normalize(N, pins=pins40, label="40 pins"),
                    bank=bank, complete_restarts=8, complete_iters=8000,
                    read_restarts=2, read_iters=3000, seed=2)
    rec = support_min.recovery(scp["q"], pl.q, N, pl.cts)["accuracy"]
    cgap = scp["completion"][scp["completion_drift"]]["gap"]
    circ = all(v.get("circular") for v in scp["support"].values())
    checks.append((f"40 true pins: recovery={rec:.2f}, gap={cgap}, "
                   f"verdict={scp['verdict']} (fitted support flagged "
                   f"circular)", rec >= 0.9 and cgap > COMPLETE_GAP
                   and circ and scp["verdict"] in ("PASS", "SUPPORT_ONLY")))

    # (12) drift=0 completion is refused with an explanation.
    try:
        complete(pl.cts, N, pins40, drift=0)
        checks.append(("drift=0 completion refused", False))
    except ValueError:
        checks.append(("drift=0 completion refused", True))

    # (13) drift=0 learned read refused (hypothesis-invariance trap,
    #      caught live on the real corpus: z=37.9 karelian letter soup).
    try:
        learned_read(pl.cts, pl.q, N, bank=bank, drifts=(1, 0))
        checks.append(("drift=0 learned read refused", False))
    except ValueError:
        checks.append(("drift=0 learned read refused", True))

    # (14) readability gate: real sample text scores high, alphabet soup
    #      scores zero -- the gate that keeps a z-only mirage from PASSing.
    hi = readability([plantlab.SAMPLE_TEXT], "english")
    lo = readability(["qzx vkq jjw ppk zzt"], "english")
    checks.append((f"readability gate separates (hi={hi:.2f}, lo={lo:.2f})",
                   hi > 0.8 and lo == 0.0))

    # (15) determinism: identical inputs, identical verdict cards.
    s1 = scorecard(pl.cts, N, h_q, bank=bank, seed=4,
                   read_restarts=2, read_iters=2000)
    s2 = scorecard(pl.cts, N, h_q, bank=bank, seed=4,
                   read_restarts=2, read_iters=2000)
    checks.append(("scorecard deterministic", s1 == s2))
    return checks


def _run_selftest() -> int:
    ok = True
    for name, passed in selftest():
        print(f"[{'OK  ' if passed else 'FAIL'}] {name}")
        ok &= passed
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _run_selftest()
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
