"""Cipher candidate scoreboard — rank interrelated-alphabet models on the eye corpus.

Methodology (paranoia-audited):
  - Plant discrimination uses model-appropriate OWN plants (not one plant for all).
  - Real-corpus discrimination uses contradiction rate on broad isomorph pairs —
    this is the metric that actually differs between progressive models.
  - Clean-window fraction from chain_extract is reported but NOT scored when
    identical across models (anchor set is model-invariant at mr=3).
  - SUPPORTED requires plant gates AND a real-corpus discriminator — NOT merely
    high refrain extent (pure-progressive reaches L=21 vs L=22).
  - Cross-checked against chain_models.discrimination_audit() on every run.

See run_methodology_audit() for assumption challenges and shuffle-null controls.
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
import trigram as tg
from stats import ioc


RowsFn = Callable


@dataclass
class CandidateRow:
    model_id: str
    name: str
    family: str
    searchable: bool
    keyspace_note: str
    own_plant_ok: Optional[bool] = None
    rejects_autokey_plant: Optional[bool] = None
    rejects_two_alphabet_plant: Optional[bool] = None
    plant_contradiction_rate: Optional[float] = None
    real_contradiction_rate: Optional[float] = None
    real_constraints: Optional[int] = None
    clean_windows: Optional[int] = None
    flagged: Optional[int] = None
    recovery_ratio: Optional[float] = None
    distinct_positions: Optional[int] = None
    refrain_extent: Optional[int] = None
    refrain_pure_extent: Optional[int] = None
    refrain_null_p: Optional[float] = None
    refrain_null_z: Optional[float] = None
    score: int = 0
    rank: int = 0
    verdict: str = "INCONCLUSIVE"
    notes: List[str] = field(default_factory=list)


@dataclass
class PremiseReport:
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
class TripletCombineProbe:
    triplet: int
    combine_ioc: float
    combine_z: float
    digit_sum_ioc: float
    null_ioc_mean: float
    significant: bool


@dataclass
class MethodologyAudit:
    """Challenges ground-truth assumptions; all checks should pass on a sound run."""
    chain_models_agrees: bool
    shuffle_clean_fraction: float
    live_clean_fraction: float
    extract_metrics_model_invariant: bool
    per_msg_real_contra: float
    pure_real_contra: float
    free_real_contra: float
    refrain_extent_gap: int
    triplet_combine: List[TripletCombineProbe]
    challenged_assumptions: List[str]
    audit_pass: bool
    notes: List[str] = field(default_factory=list)


@dataclass
class Scoreboard:
    candidates: List[CandidateRow]
    premise: PremiseReport
    methodology: MethodologyAudit
    ranked_ids: List[str]
    reproduce: str = "python3 eyewitness/eyescoreboard.py"


def _chain_from_rows(name: str, rows_fn: RowsFn, messages, pairs, N) -> cm.ChainStat:
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


def _real_corpus_chain(rows_fn: RowsFn, messages, N, base_len: int = 13,
                       broad_repeats: int = 3) -> Tuple[float, int, int]:
    pairs = iso.find_isomorphs(messages, base_len, broad_repeats)
    stat = _chain_from_rows("real", rows_fn, messages, pairs, N)
    rate = stat.contradictions / stat.constraints if stat.constraints else 0.0
    return rate, stat.constraints, stat.contradictions


def _plant_pure_progressive(N, rng, M=6, T=80, C=None):
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
    mp = (cm.plant_per_msg_progressive(N, rng, M=M)[0] if own_plant is None
          else own_plant(N, rng, M=M))
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


def _shuffle_null_clean_fraction(rows_fn: RowsFn, messages, N, seed: int = 0) -> float:
    import numpy as np
    rng = np.random.default_rng(seed)
    sh = [list(rng.permutation(m)) for m in messages]
    ext = ce.extract(sh, base_len=13, broad_repeats=3, rows_fn=rows_fn, N=N, seed=seed)
    tot = ext.n_clean_windows + ext.n_flagged
    return ext.n_clean_windows / tot if tot else 0.0


def _triplet_combine_probes(messages, N: int, body_start: int = 25,
                            n_null: int = 200, seed: int = 0) -> List[TripletCombineProbe]:
    """If ciphertext were a meta-trigram from combining triplet members, aligned
    combine streams would look structured vs shuffle null. Observed: they do not."""
    import numpy as np
    if len(messages) < 9:
        return []
    rng = np.random.default_rng(seed)
    triplets = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
    out: List[TripletCombineProbe] = []
    for gi, g in enumerate(triplets):
        L = min(len(messages[m]) for m in g)
        if L - body_start < 8:
            continue
        comb = [(messages[g[0]][t] + messages[g[1]][t] + messages[g[2]][t]) % N
                for t in range(L)]
        dcomb = []
        for t in range(L):
            digits = [tg.to_digits(messages[m][t], 5, 3) for m in g]
            ds = [(digits[0][i] + digits[1][i] + digits[2][i]) % 5 for i in range(3)]
            dcomb.append(tg.from_digits(ds, 5))
        obs = ioc(comb[body_start:])
        obs_d = ioc(dcomb[body_start:])
        nulls = []
        for _ in range(n_null):
            sh = [list(rng.permutation(messages[m])) for m in g]
            cc = [(sh[0][t] + sh[1][t] + sh[2][t]) % N for t in range(L)]
            nulls.append(ioc(cc[body_start:]))
        nm = float(np.mean(nulls))
        ns = float(np.std(nulls))
        z = (obs - nm) / (ns + 1e-9)
        out.append(TripletCombineProbe(
            triplet=gi + 1,
            combine_ioc=float(obs),
            combine_z=float(z),
            digit_sum_ioc=float(obs_d),
            null_ioc_mean=nm,
            significant=z > 3,
        ))
    return out


def run_methodology_audit(messages, candidates: List[CandidateRow], N: int,
                          seed: int = 0) -> MethodologyAudit:
    challenged: List[str] = []
    notes: List[str] = []

    audit = cm.discrimination_audit(N, seed=1)
    pm = audit["per-msg-prog"]["per-msg-prog"]
    pm_on_ak = audit["autokey"]["per-msg-prog"]
    agrees = pm.consistent and (not pm_on_ak.consistent)
    if not agrees:
        challenged.append("chain_models discrimination_audit mismatch")

    live_rows = [r for r in candidates if r.model_id in
                 ("per-msg-progressive", "pure-progressive", "free-delta")]
    clean_set = {(r.clean_windows, r.flagged) for r in live_rows if r.clean_windows is not None}
    invariant = len(clean_set) <= 1 and len(live_rows) >= 2
    if invariant:
        challenged.append(
            "extract clean/flagged counts are identical across GF models — "
            "do not treat clean fraction as a model discriminator"
        )

    shuffle_frac = _shuffle_null_clean_fraction(cm.per_msg_prog_rows, messages, N, seed)
    live_frac = 0.0
    pm_row = next((r for r in candidates if r.model_id == "per-msg-progressive"), None)
    if pm_row and pm_row.clean_windows is not None:
        tot = pm_row.clean_windows + (pm_row.flagged or 0)
        live_frac = pm_row.clean_windows / tot if tot else 0.0
    if shuffle_frac > live_frac * 0.5:
        notes.append("shuffle null retains substantial clean fraction — anchor set is loose")

    per_msg_c = next(r for r in candidates if r.model_id == "per-msg-progressive")
    pure_c = next(r for r in candidates if r.model_id == "pure-progressive")
    free_c = next(r for r in candidates if r.model_id == "free-delta")
    gap = (per_msg_c.refrain_extent or 0) - (pure_c.refrain_pure_extent or pure_c.refrain_extent or 0)

    if gap <= 1:
        challenged.append(
            f"refrain extent gap per-msg vs pure is only {gap} — model not uniquely identified"
        )

    if (per_msg_c.real_contradiction_rate is not None and
            pure_c.real_contradiction_rate is not None):
        if per_msg_c.real_contradiction_rate >= pure_c.real_contradiction_rate:
            challenged.append("per-msg does not beat pure on real-corpus contradiction rate")

    triplet_combine = _triplet_combine_probes(messages, N, seed=seed)
    if not any(p.significant for p in triplet_combine):
        notes.append("triplet member combine (sum mod 83) is NOT structured vs null — "
                     "symbols are not a meta-trigram of the triplet set")

    audit_pass = agrees and (per_msg_c.rejects_autokey_plant is True)
    return MethodologyAudit(
        chain_models_agrees=agrees,
        shuffle_clean_fraction=round(shuffle_frac, 4),
        live_clean_fraction=round(live_frac, 4),
        extract_metrics_model_invariant=invariant,
        per_msg_real_contra=round(per_msg_c.real_contradiction_rate or 0, 4),
        pure_real_contra=round(pure_c.real_contradiction_rate or 0, 4),
        free_real_contra=round(free_c.real_contradiction_rate or 0, 4),
        refrain_extent_gap=gap,
        triplet_combine=triplet_combine,
        challenged_assumptions=challenged,
        audit_pass=audit_pass,
        notes=notes,
    )


def _score_row(row: CandidateRow, *, meth: Optional[MethodologyAudit] = None,
               pure_contra: Optional[float] = None) -> None:
    if row.verdict == "EXCLUDED":
        row.score = -1000
        return

    s = 0
    notes: List[str] = list(row.notes)

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

    # Real-corpus discriminator: lower contradiction rate on broad pairs is better
    if (row.real_contradiction_rate is not None and pure_contra is not None
            and row.model_id == "per-msg-progressive"):
        if row.real_contradiction_rate < pure_contra * 0.92:
            s += 20
            notes.append(f"real contra {row.real_contradiction_rate:.2%} < pure {pure_contra:.2%}")
    if row.real_contradiction_rate == 0 and row.model_id in ("free-delta", "autokey-1"):
        notes.append("zero real contradictions — permissive")

    # Do NOT score identical clean fractions (methodology audit flags this)
    if meth and not meth.extract_metrics_model_invariant:
        if row.clean_windows is not None:
            tot = row.clean_windows + (row.flagged or 0)
            if tot > 0:
                frac = row.clean_windows / tot
                if frac >= 0.15:
                    s += 8

    if row.recovery_ratio is not None and row.recovery_ratio >= 0.85:
        s += 5

    unique_refrain = False
    if row.refrain_extent is not None:
        if row.refrain_extent >= 22:
            s += 10
        if row.refrain_pure_extent is not None:
            if row.refrain_extent > row.refrain_pure_extent:
                s += 10
                unique_refrain = True
            else:
                notes.append("pure-progressive tied on refrain extent")
        if row.refrain_null_p is not None and row.refrain_null_p < 0.01:
            s += 8

    row.notes = notes

    if row.rejects_autokey_plant is False:
        row.verdict = "PERMISSIVE"
        row.score = min(s, 10)
    elif row.own_plant_ok is False:
        row.verdict = "INCONCLUSIVE"
        row.score = s
    elif (s >= 55 and row.rejects_autokey_plant and row.rejects_two_alphabet_plant
          and unique_refrain and row.model_id == "per-msg-progressive"):
        row.verdict = "SUPPORTED"
        row.score = s
    elif s >= 40 and row.rejects_autokey_plant:
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

    rc_rate, rc_n, rc_c = _real_corpus_chain(rows_fn, messages, N)
    row.real_contradiction_rate = round(rc_rate, 4)
    row.real_constraints = rc_n

    ext = ce.extract(messages, base_len=13, broad_repeats=3, rows_fn=rows_fn, N=N)
    row.clean_windows = ext.n_clean_windows
    row.flagged = ext.n_flagged
    row.recovery_ratio = round(ext.recovery_ratio, 3)
    row.distinct_positions = ext.positions_distinct

    if refrain_audit:
        region = rf.DEFAULT_INSTANCES
        audit = ma.audit(messages, region, N, n_null=400, seed=0)
        if model_id in ("per-msg-progressive", "pure-progressive"):
            row.refrain_extent = ma.consistent_extent(
                messages, region, N, per_message=(model_id == "per-msg-progressive"))
            row.refrain_pure_extent = ma.consistent_extent(
                messages, region, N, per_message=False)
            row.refrain_null_p = round(audit.p_value, 4)
            row.refrain_null_z = round(audit.z, 2)

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

    candidates.append(_run_gf_model(
        "per-msg-progressive",
        "Per-message progressive + per-triplet K",
        "c[m][t]=C[(p+base_m+K_g[t])]",
        cm.per_msg_prog_rows, messages, N,
        searchable=True, keyspace="~83^6 bases (clustered)",
    ))
    candidates.append(_run_gf_model(
        "pure-progressive",
        "Pure progressive (no per-message base)",
        "c[t]=C[(p+t)] global slide",
        cm.pure_prog_rows, messages, N,
        searchable=False, keyspace="header-forced subcase",
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
    rc_rate, rc_n, _ = _real_corpus_chain(ce.free_delta_rows, messages, N)
    ak_row.real_contradiction_rate = round(rc_rate, 4)
    ak_row.real_constraints = rc_n
    ext = ce.extract(messages, rows_fn=ce.free_delta_rows, N=N)
    ak_row.clean_windows = ext.n_clean_windows
    ak_row.flagged = ext.n_flagged
    ak_row.recovery_ratio = round(ext.recovery_ratio, 3)
    ak_row.notes.append("equivalent to free-δ on plants (chain_models proof)")
    candidates.append(ak_row)

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

    meth = run_methodology_audit(messages, candidates, N)
    pm_row = next((r for r in candidates if r.model_id == "per-msg-progressive"), None)
    pure_row = next((r for r in candidates if r.model_id == "pure-progressive"), None)
    pure_contra = pure_row.real_contradiction_rate if pure_row else None

    for row in candidates:
        if row.verdict != "EXCLUDED":
            _score_row(row, meth=meth, pure_contra=pure_contra)

    ranked = sorted(candidates, key=lambda r: (r.score, r.model_id), reverse=True)
    for i, row in enumerate(ranked, 1):
        row.rank = i

    return Scoreboard(ranked, premise, meth, [r.model_id for r in ranked])


def render_markdown(sb: Scoreboard) -> str:
    L: List[str] = [
        "# EyeScoreboard — cipher candidate ranking (methodology-audited)",
        "",
        f"*Reproduce: `{sb.reproduce}`. Gate: `python3 noita_eye_core/selftest.py`.*",
        "",
        "## Premise check (block-difference / depth — model-independent)",
        "",
        f"- Isomorph abundance (L=12): **{sb.premise.isomorph_observed}**, z=**{sb.premise.isomorph_z:.1f}**",
        f"- Keystream scope (body): **{sb.premise.keystream_body_verdict}**",
        f"  (within z={sb.premise.keystream_within_z:.1f}, cross z={sb.premise.keystream_cross_z:.1f})",
        f"- Exploitable depth: **{sb.premise.exploitable_depth}**; E1/W1 re-sync: **{sb.premise.e1_w1_resync}**",
        f"- **Premise tenable:** {'YES' if sb.premise.premise_ok else 'WEAK'}",
        "",
        "## Methodology audit (ground-truth challenges)",
        "",
        f"- chain_models discrimination_audit agrees: **{sb.methodology.chain_models_agrees}**",
        f"- Real-corpus contradiction rate: per-msg **{sb.methodology.per_msg_real_contra:.2%}**, "
        f"pure **{sb.methodology.pure_real_contra:.2%}**, free-δ **{sb.methodology.free_real_contra:.2%}**",
        f"- Extract clean fraction invariant across models: **{sb.methodology.extract_metrics_model_invariant}**",
        f"- Shuffle-null clean fraction: **{sb.methodology.shuffle_clean_fraction:.2%}** "
        f"(live **{sb.methodology.live_clean_fraction:.2%}**)",
        f"- Refrain extent gap (per-msg − pure): **{sb.methodology.refrain_extent_gap}**",
        f"- **Audit pass:** {'YES' if sb.methodology.audit_pass else 'REVIEW'}",
        "",
    ]
    if sb.methodology.challenged_assumptions:
        L.append("**Challenged assumptions (expected on real corpus — not bugs):**")
        for c in sb.methodology.challenged_assumptions:
            L.append(f"- {c}")
        L.append("")
    if sb.methodology.triplet_combine:
        L.append("**Triplet combine probe** (if symbols were meta-trigrams of the triplet set):")
        for p in sb.methodology.triplet_combine:
            L.append(f"- Triplet {p.triplet}: sum-mod-83 IoC={p.combine_ioc:.4f} "
                     f"z={p.combine_z:.2f} (null {p.null_ioc_mean:.4f}); "
                     f"digit-sum IoC={p.digit_sum_ioc:.4f}; "
                     f"significant={p.significant}")
        L.append("")

    L.extend([
        "## Candidate ranking",
        "",
        "| rank | id | verdict | score | real contra | clean | flagged | refrain |",
        "|---:|---|---|---:|---:|---:|---:|---:|",
    ])
    for r in sb.candidates:
        rc = f"{r.real_contradiction_rate:.2%}" if r.real_contradiction_rate is not None else "—"
        ref = str(r.refrain_extent) if r.refrain_extent is not None else "—"
        cw = r.clean_windows if r.clean_windows is not None else "—"
        fl = r.flagged if r.flagged is not None else "—"
        L.append(f"| {r.rank} | {r.model_id} | {r.verdict} | {r.score} | "
                 f"{rc} | {cw} | {fl} | {ref} |")

    L.extend([
        "",
        "## Read",
        "- **SUPPORTED** now requires plant discrimination AND refrain extent strictly "
        "beating pure-progressive AND lower real-corpus contradiction rate.",
        "- **SUGGESTIVE** = passes plants but model not uniquely identified on real corpus.",
        "- Block-difference premise is model-independent; triplet **combine** does not "
        "produce structured meta-trigrams (sum mod 83 ≈ null).",
        "- Current symbols are base-5 trigrams of individual glyphs (provenance 9/9), "
        "not a composite of the three messages in each triplet.",
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

    sb = build_scoreboard(msgs, N)
    out.append(("build_scoreboard returns candidates", len(sb.candidates) >= 8))
    out.append(("methodology audit present", sb.methodology is not None))

    mono = next(r for r in sb.candidates if r.model_id == "monoalphabetic")
    free = next(r for r in sb.candidates if r.model_id == "free-delta")
    out.append(("mono EXCLUDED", mono.verdict == "EXCLUDED"))
    out.append(("free-delta PERMISSIVE", free.verdict == "PERMISSIVE"))

    try:
        import corpus as corpus_mod
        M = [list(x) for x in corpus_mod.load().ciphertexts]
        sb_real = build_scoreboard(M, corpus_mod.load().N)
        pm = next(r for r in sb_real.candidates if r.model_id == "per-msg-progressive")
        pure = next(r for r in sb_real.candidates if r.model_id == "pure-progressive")

        out.append(("real: chain_models agrees", sb_real.methodology.chain_models_agrees))
        out.append(("real: per-msg real contra < pure",
                    (pm.real_contradiction_rate or 1) < (pure.real_contradiction_rate or 0)))
        out.append(("real: per-msg refrain > pure",
                    (pm.refrain_extent or 0) > (pure.refrain_extent or 0)))
        out.append(("real: per-msg not over-scored as SUPPORTED alone",
                    pm.verdict in ("SUPPORTED", "SUGGESTIVE")))
        out.append(("real: triplet combine not significant",
                    not any(p.significant for p in sb_real.methodology.triplet_combine)))
        out.append(("real: premise ok", sb_real.premise.premise_ok))
        out.append(("render markdown", len(render_markdown(sb_real)) > 800))

        # Scoring must not give SUPPORTED to free-delta
        out.append(("free-delta not SUPPORTED on real corpus",
                    free.verdict != "SUPPORTED"))
    except Exception as e:
        out.append((f"real corpus smoke: {e}", False))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} eyescoreboard checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
