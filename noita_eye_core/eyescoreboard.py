"""Cipher candidate scoreboard — rank interrelated-alphabet models on the eye corpus.

Runs a battery of calibrated tests per candidate cipher model and assigns a
verdict + numeric score so we can EXCLUDE permissive fits, compare survivors,
and record whether the block-difference / depth premise still holds.

Tests per GF model (on real corpus + planted controls):
  1. Plant discrimination — consistent on OWN plant, contradicts wrong plants
  2. Clean extraction — chain_extract with model rows_fn (clean vs flagged)
  3. Refrain extent — model_audit consistent_extent @ 4× refrain (if applicable)
  4. Structural premise gates — isomorphs, keystream scope, resync (global)

Verdict tiers (higher score = better rank):
  EXCLUDED   — ruled out by structure or proven moot
  PERMISSIVE — fits everything (free-δ / autokey-1 family)
  INCONCLUSIVE — real-corpus signal indistinguishable from null
  SUGGESTIVE — beats null modestly; not a unique discriminator
  SUPPORTED  — passes plant discrimination + selective on real corpus
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import chain_extract as ce
import chain_models as cm
import depthmap as dm
import isomorph as iso
import keystream_scope as ks
import model_audit as ma
import refrain as rf
import resync


RowsFn = Callable


@dataclass
class CandidateRow:
    model_id: str
    name: str
    family: str
    searchable: bool
    keyspace_note: str
    # plant discrimination (clean pairs on planted corpora)
    own_plant_ok: Optional[bool] = None
    rejects_autokey_plant: Optional[bool] = None
    rejects_two_alphabet_plant: Optional[bool] = None
    plant_contradiction_rate: Optional[float] = None
    # real corpus extraction (L=13, broad mr=3)
    clean_windows: Optional[int] = None
    flagged: Optional[int] = None
    recovery_ratio: Optional[float] = None
    distinct_positions: Optional[int] = None
    # refrain 4-window audit (per-message progressive GF only when applicable)
    refrain_extent: Optional[int] = None
    refrain_pure_extent: Optional[int] = None
    refrain_null_p: Optional[float] = None
    refrain_null_z: Optional[float] = None
    # composite
    score: int = 0
    rank: int = 0
    verdict: str = "INCONCLUSIVE"
    notes: List[str] = field(default_factory=list)


@dataclass
class PremiseReport:
    """Model-independent checks: is ciphertext-plaintext block-difference still tenable?"""
    isomorph_z: float
    isomorph_observed: int
    keystream_body_verdict: str
    keystream_within_z: float
    keystream_cross_z: float
    exploitable_depth: int
    e1_w1_resync: int
    body_proven_pairs: int
    premise_ok: bool
    premise_notes: List[str] = field(default_factory=list)


@dataclass
class Scoreboard:
    candidates: List[CandidateRow]
    premise: PremiseReport
    ranked_ids: List[str]
    reproduce: str = "python3 eyewitness/eyescoreboard.py"


def _chain_from_rows(name: str, rows_fn: RowsFn, messages, pairs, N) -> cm.ChainStat:
    """Generic GF chain stat for any rows_fn (mirrors per_message_progressive_chain)."""
    gf = iso.GFSystem(N)
    parent = list(range(N))

    def union(a, b):
        ra, rb = a, b
        while parent[ra] != ra:
            ra = parent[ra]
        while parent[rb] != rb:
            rb = parent[rb]
        parent[ra] = rb

    constraints = contradictions = redundant = 0
    touched: set = set()
    for pr in pairs:
        for i, (row, rhs) in enumerate(rows_fn(pr, messages, N)):
            if i >= pr.length:
                break
            A = int(messages[pr.m1][pr.p1 + i])
            D = int(messages[pr.m2][pr.p2 + i])
            constraints += 1
            res = gf.add(row, rhs)
            if res == "contradiction":
                contradictions += 1
            elif res == "redundant":
                redundant += 1
            touched.add(A)
            touched.add(D)
            union(A, D)
    linked = 0
    if touched:
        comps: Dict[int, int] = {}
        for s in touched:
            r = s
            while parent[r] != r:
                r = parent[r]
            comps[r] = comps.get(r, 0) + 1
        linked = max(comps.values()) if comps else 0
    return cm.ChainStat(name, constraints, contradictions, redundant,
                        len(gf.pivots), linked, contradictions == 0)


def _plant_pure_progressive(N, rng, M=6, T=80, C=None):
    """Ground-truth plant for pure-progressive (single global slide, base=0)."""
    if C is None:
        C = list(rng.permutation(N))
    W = cm._word_sliding(rng, N)
    msgs = []
    for _ in range(M):
        P = list(rng.integers(0, N, size=T))
        for p in cm._WORD_POS:
            P[p:p + cm._WLEN] = W
        msgs.append([C[(P[t] + t) % N] for t in range(T)])
    return msgs


def _plant_discrimination(rows_fn: RowsFn, N: int, seed: int = 1,
                          *, own_plant=None) -> Tuple[Optional[bool], Optional[bool],
                                                       Optional[bool], float]:
    import numpy as np
    rng = np.random.default_rng(seed)
    M = 6
    if own_plant is None:
        mp = cm.plant_per_msg_progressive(N, rng, M=M)[0]
    else:
        mp = own_plant(N, rng, M=M)
    ak = cm.plant_autokey(N, rng, M=M)
    ta = cm.plant_two_alphabet(N, rng, M=M)
    pairs = cm.clean_pairs(M)
    own_stat = _chain_from_rows("test", rows_fn, mp, pairs, N)
    ak_stat = _chain_from_rows("test", rows_fn, ak, pairs, N)
    ta_stat = _chain_from_rows("test", rows_fn, ta, pairs, N)
    rate = (own_stat.contradictions / own_stat.constraints
            if own_stat.constraints else 0.0)
    return (own_stat.consistent,
            not ak_stat.consistent,
            not ta_stat.consistent,
            rate)


def _score_row(row: CandidateRow) -> None:
    if row.verdict == "EXCLUDED":
        row.score = -1000
        return
    s = 0
    notes: List[str] = []

    if row.own_plant_ok:
        s += 25
    elif row.own_plant_ok is False:
        s -= 40
        notes.append("contradicts own plant")

    if row.rejects_autokey_plant and row.rejects_two_alphabet_plant:
        s += 20
    elif row.rejects_autokey_plant is False or row.rejects_two_alphabet_plant is False:
        s -= 35
        notes.append("permissive on control plants")

    if row.plant_contradiction_rate is not None and row.plant_contradiction_rate == 0:
        s += 5

    if row.clean_windows is not None:
        total = row.clean_windows + (row.flagged or 0)
        if total > 0:
            frac = row.clean_windows / total
            if frac >= 0.15:
                s += 15
            elif frac >= 0.05:
                s += 5
            notes.append(f"clean fraction {frac:.0%}")

    if row.recovery_ratio is not None:
        if row.recovery_ratio >= 0.85:
            s += 10
        elif row.recovery_ratio >= 0.5:
            s += 3

    if row.refrain_extent is not None:
        if row.refrain_extent >= 22:
            s += 15
        elif row.refrain_extent >= 18:
            s += 8
        if row.refrain_null_p is not None:
            if row.refrain_null_p < 0.01:
                s += 15
            elif row.refrain_null_p < 0.05:
                s += 8
            else:
                notes.append(f"refrain null p={row.refrain_null_p:.3f}")

    if row.refrain_pure_extent is not None and row.refrain_extent is not None:
        if row.refrain_pure_extent >= row.refrain_extent - 1:
            notes.append("pure-progressive nearly as deep")

    row.notes.extend(notes)

    if row.rejects_autokey_plant is False:
        row.verdict = "PERMISSIVE"
        row.score = min(s, 10)
    elif row.own_plant_ok is False:
        row.verdict = "INCONCLUSIVE"
        row.score = s
    elif s >= 70 and row.rejects_autokey_plant and row.rejects_two_alphabet_plant:
        row.verdict = "SUPPORTED"
        row.score = s
    elif s >= 45:
        row.verdict = "SUGGESTIVE"
        row.score = s
    else:
        row.verdict = "INCONCLUSIVE"
        row.score = s


def _premise_report(messages, N: int) -> PremiseReport:
    sig = iso.significance(messages, 12, 3, n_null=120, seed=0)
    scope = ks.scope_report(messages, N, body_start=25)
    dm_map = dm.build(messages, N)
    rs = resync.count_resync(messages[0], messages[1])
    body_proven = sum(1 for ev in dm_map.pairs if ev.body_proven)
    notes: List[str] = []
    ok = True
    if sig["z"] < 5:
        ok = False
        notes.append("isomorph abundance weak")
    if scope.cross_sig.z > 2 and scope.within_sig.z > 5:
        notes.append("cross-triplet diff elevated (check confound)")
    if scope.within_sig.z < 3:
        ok = False
        notes.append("within-triplet depth weak")
    if dm_map.exploitable_total < 20:
        ok = False
        notes.append("exploitable depth low")
    if rs < 2:
        notes.append("few re-sync events")
    return PremiseReport(
        isomorph_z=float(sig["z"]),
        isomorph_observed=int(sig["observed"]),
        keystream_body_verdict=scope.verdict,
        keystream_within_z=float(scope.within_sig.z),
        keystream_cross_z=float(scope.cross_sig.z),
        exploitable_depth=int(dm_map.exploitable_total),
        e1_w1_resync=int(rs),
        body_proven_pairs=int(body_proven),
        premise_ok=ok,
        premise_notes=notes,
    )


def _run_gf_model(model_id: str, name: str, family: str, rows_fn: RowsFn,
                  messages, N: int, *, searchable: bool, keyspace: str,
                  refrain_audit: bool = True,
                  own_plant=None) -> CandidateRow:
    row = CandidateRow(model_id, name, family, searchable, keyspace)
    own, rej_a, rej_t, rate = _plant_discrimination(rows_fn, N, own_plant=own_plant)
    row.own_plant_ok = own
    row.rejects_autokey_plant = rej_a
    row.rejects_two_alphabet_plant = rej_t
    row.plant_contradiction_rate = round(rate, 4)

    ext = ce.extract(messages, base_len=13, broad_repeats=3, rows_fn=rows_fn, N=N)
    row.clean_windows = ext.n_clean_windows
    row.flagged = ext.n_flagged
    row.recovery_ratio = round(ext.recovery_ratio, 3)
    row.distinct_positions = ext.positions_distinct

    if refrain_audit:
        region = rf.DEFAULT_INSTANCES
        audit = ma.audit(messages, region, N, n_null=400, seed=0)
        row.refrain_extent = audit.refrain_permsg if model_id == "per-msg-progressive" else None
        if model_id in ("per-msg-progressive", "pure-progressive"):
            row.refrain_extent = ma.consistent_extent(
                messages, region, N, per_message=(model_id == "per-msg-progressive"))
            row.refrain_pure_extent = ma.consistent_extent(
                messages, region, N, per_message=False)
            row.refrain_null_p = round(audit.p_value, 4)
            row.refrain_null_z = round(audit.z, 2)

    _score_row(row)
    return row


def _static_row(model_id: str, name: str, family: str, verdict: str,
                keyspace: str, notes: List[str]) -> CandidateRow:
    row = CandidateRow(model_id, name, family, False, keyspace,
                       verdict=verdict, notes=list(notes))
    row.score = -1000 if verdict == "EXCLUDED" else -500
    return row


def build_scoreboard(messages, N: Optional[int] = None, *,
                     n_null: int = 400) -> Scoreboard:
    if N is None:
        N = max(int(max(m)) for m in messages) + 1

    premise = _premise_report(messages, N)

    candidates: List[CandidateRow] = []

    # --- GF interrelated models (live tests) ---
    candidates.append(_run_gf_model(
        "per-msg-progressive",
        "Per-message progressive + per-triplet K",
        "c[m][t]=C[(p+base_m+K_g[t])]",
        cm.per_msg_prog_rows, messages, N,
        searchable=True, keyspace="~83^6 bases (clustered)",
        refrain_audit=True,
    ))
    candidates.append(_run_gf_model(
        "pure-progressive",
        "Pure progressive (no per-message base)",
        "c[t]=C[(p+t)] global slide",
        cm.pure_prog_rows, messages, N,
        searchable=False, keyspace="header-forced subcase",
        refrain_audit=True,
        own_plant=_plant_pure_progressive,
    ))
    candidates.append(_run_gf_model(
        "free-delta",
        "Free-δ / autokey-1 interrelation",
        "x[D]-x[A]-x[D0]+x[A0]=0 per pair",
        ce.free_delta_rows, messages, N,
        searchable=False, keyspace="per-pair δ absorbs all",
        refrain_audit=False,
    ))

    # autokey-1 chain (equivalent to free-δ; recorded separately for clarity)
    ak_row = CandidateRow(
        "autokey-1", "Ciphertext autokey lag-1 (chaining)", "c[t]=p[t]+c[t-1]",
        False, "per-pair δ; ≡ free-δ",
    )
    own, rej_a, rej_t, rate = _plant_discrimination(
        lambda pr, msgs, n: list(ce.free_delta_rows(pr, msgs, n)), N,
        own_plant=cm.plant_autokey,
    )
    ak_row.own_plant_ok = own
    ak_row.rejects_autokey_plant = rej_a
    ak_row.rejects_two_alphabet_plant = rej_t
    ak_row.plant_contradiction_rate = round(rate, 4)
    ext = ce.extract(messages, rows_fn=ce.free_delta_rows, N=N)
    ak_row.clean_windows = ext.n_clean_windows
    ak_row.flagged = ext.n_flagged
    ak_row.recovery_ratio = round(ext.recovery_ratio, 3)
    ak_row.notes.append("equivalent to free-δ on plants (chain_models proof)")
    _score_row(ak_row)
    candidates.append(ak_row)

    # --- Excluded / moot families (ledger reference rows) ---
    candidates.extend([
        _static_row("monoalphabetic", "Monoalphabetic substitution", "c=C[p]",
                    "EXCLUDED", "83!", ["flat unigram; classify excluded"]),
        _static_row("otp-unrelated", "OTP / unrelated alphabet columns", "independent decks",
                    "EXCLUDED", "83^L", ["isomorphs forbid unrelated alphabets"]),
        _static_row("aes-salakieli", "AES-128-CTR (salakieli)", "N=256 block",
                    "EXCLUDED", "—", ["N=83; decrypts to noise"]),
        _static_row("transposition", "Transposition / periodic block", "permute positions",
                    "EXCLUDED", "—", ["repeat_census excluded"]),
        _static_row("prng-seed", "PRNG seed × GAK", "small integer seed",
                    "EXCLUDED", "~3.4e11", ["moot: offline author; provenance"]),
        _static_row("ct-autokey-global", "Global ciphertext-autokey body", "keystream=c[t-1]",
                    "EXCLUDED", "—", [f"E1/W1 re-sync={premise.e1_w1_resync} excludes CT-autokey"]),
        _static_row("general-K", "General aperiodic K per triplet", "K_g[t] arbitrary",
                    "EXCLUDED", "83^300", ["fits but not searchable"]),
    ])

    # Rank: score descending; EXCLUDED last
    ranked = sorted(candidates, key=lambda r: (r.score, r.model_id), reverse=True)
    for i, row in enumerate(ranked, 1):
        row.rank = i
    ranked_ids = [r.model_id for r in ranked]

    return Scoreboard(ranked, premise, ranked_ids)


def render_markdown(sb: Scoreboard) -> str:
    L: List[str] = [
        "# EyeScoreboard — cipher candidate ranking",
        "",
        f"*Reproduce: `{sb.reproduce}`. Gate: `python3 noita_eye_core/selftest.py`.*",
        "",
        "## Premise check (block-difference / depth model-independent)",
        "",
        f"- Isomorph abundance (L=12): **{sb.premise.isomorph_observed}** windows, "
        f"**z={sb.premise.isomorph_z:.1f}**",
        f"- Keystream scope (body): **{sb.premise.keystream_body_verdict}** "
        f"(within z={sb.premise.keystream_within_z:.1f}, cross z="
        f"{sb.premise.keystream_cross_z:.1f})",
        f"- Exploitable 2-deep positions: **{sb.premise.exploitable_depth}**",
        f"- E1/W1 re-sync events: **{sb.premise.e1_w1_resync}**",
        f"- Body-proven depth pairs: **{sb.premise.body_proven_pairs}**",
        f"- **Premise tenable:** {'YES' if sb.premise.premise_ok else 'WEAK / review notes'}",
        "",
    ]
    if sb.premise.premise_notes:
        for n in sb.premise.premise_notes:
            L.append(f"  - {n}")
        L.append("")

    L.extend([
        "## Candidate ranking (higher score = better fit; not proof of author cipher)",
        "",
        "| rank | id | verdict | score | clean | flagged | recovery | refrain L | null p |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|",
    ])
    for r in sb.candidates:
        ref = str(r.refrain_extent) if r.refrain_extent is not None else "—"
        np_ = f"{r.refrain_null_p:.3f}" if r.refrain_null_p is not None else "—"
        cw = r.clean_windows if r.clean_windows is not None else "—"
        fl = r.flagged if r.flagged is not None else "—"
        rr = f"{r.recovery_ratio:.2f}" if r.recovery_ratio is not None else "—"
        L.append(f"| {r.rank} | {r.model_id} | {r.verdict} | {r.score} | "
                 f"{cw} | {fl} | {rr} | {ref} | {np_} |")

    L.extend(["", "## Detail", ""])
    for r in sb.candidates:
        L.append(f"### {r.rank}. `{r.model_id}` — {r.name}")
        L.append(f"- **Verdict:** {r.verdict} (score **{r.score}**)")
        L.append(f"- **Family:** `{r.family}`")
        L.append(f"- **Keyspace:** {r.keyspace_note}; searchable={r.searchable}")
        if r.own_plant_ok is not None:
            L.append(f"- **Plant discrim:** own={r.own_plant_ok}, "
                     f"reject-autokey={r.rejects_autokey_plant}, "
                     f"reject-two-alphabet={r.rejects_two_alphabet_plant}")
        if r.notes:
            L.append(f"- **Notes:** {'; '.join(r.notes)}")
        L.append("")

    L.extend([
        "## Read",
        "- **Premise OK** means model-independent structure (isomorphs, triplet depth, "
        "re-sync) still supports ciphertext-plaintext *difference* attacks — not that any "
        "one cipher formula is confirmed.",
        "- **SUPPORTED / SUGGESTIVE** means the model passes planted controls and beats "
        "permissive alternatives — still not unique on the real corpus (see model_audit).",
        "- **PERMISSIVE** models (free-δ, autokey-1) fit even wrong plants — do not use "
        "for contamination filtering.",
        "- **EXCLUDED** rows are kept as regression gates; they should never rank above "
        "live GF models.",
        "",
    ])
    return "\n".join(L)


def selftest() -> List[Tuple[str, bool]]:
    import numpy as np
    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(0)
    C = list(rng.permutation(N))
    T = 100
    msgs = [[C[(int(rng.integers(0, N)) + t) % N] for t in range(T)] for _ in range(3)]

    sb = build_scoreboard(msgs, N, n_null=50)
    out.append(("build_scoreboard returns candidates", len(sb.candidates) >= 8))
    out.append(("premise block present", sb.premise is not None))

    ids = {r.model_id for r in sb.candidates}
    out.append(("includes per-msg-progressive", "per-msg-progressive" in ids))
    out.append(("includes free-delta", "free-delta" in ids))
    out.append(("includes excluded mono", "monoalphabetic" in ids))

    per_msg = next(r for r in sb.candidates if r.model_id == "per-msg-progressive")
    free = next(r for r in sb.candidates if r.model_id == "free-delta")
    mono = next(r for r in sb.candidates if r.model_id == "monoalphabetic")

    out.append(("monoalphabetic is EXCLUDED", mono.verdict == "EXCLUDED"))
    out.append(("free-delta is PERMISSIVE or low score",
                free.verdict == "PERMISSIVE" or free.score < per_msg.score))
    out.append(("EXCLUDED scores below live models",
                mono.score < per_msg.score))

    # Real corpus smoke (optional if corpus present)
    try:
        import corpus as corpus_mod
        c = corpus_mod.load()
        M = [list(x) for x in c.ciphertexts]
        sb_real = build_scoreboard(M, c.N, n_null=80)
        pm = next(r for r in sb_real.candidates if r.model_id == "per-msg-progressive")
        out.append(("real corpus: per-msg plant discrim ok",
                    pm.rejects_autokey_plant is True))
        out.append(("real corpus: premise isomorph z>5",
                    sb_real.premise.isomorph_z > 5))
        out.append(("render_markdown non-empty", len(render_markdown(sb_real)) > 500))
    except Exception:
        out.append(("real corpus smoke", False))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} eyescoreboard checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
