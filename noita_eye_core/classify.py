"""Cipher-type classifier — narrow the search before spending GPU/seed budget.

The other modules in this package *assume* the answer (a shared, position-indexed
keystream — EyeStat's PRNG model) and go straight to recovery.  This module asks
the prior question rigorously: **what family of cipher is this even, and what can
we formally rule out?**  The goal is to turn "everyone assumes polyalphabetic"
into a set of falsifiable statements, each with an explicit null distribution, an
effect size, a multiple-testing-corrected p-value, and an honest statement of how
much signal we could even detect at this length and alphabet size.

Design — one decision per distinguishing statistic
--------------------------------------------------
Every classical cipher family leaves a different fingerprint on a handful of
order-statistics.  We test each fingerprint as a hypothesis:

1. **Unigram uniformity** (IoC / chi-squared vs uniform).
   * Monoalphabetic substitution **and** transposition *preserve* the plaintext's
     non-uniform letter distribution -> IoC stays high (>> 1/N).
   * Polyalphabetic / stream / random *flatten* it -> IoC ~ 1/N.
   This is the top split.  (Substitution vs transposition cannot be separated by
   the unigram alone — both keep the same multiset — so when the unigram is
   *structured* we report both and defer to a language-profile match.)

2. **Periodicity** (Friedman per-coset IoC + Kasiski), only informative once the
   unigram is flat.
   * A periodic key (Vigenere/Beaufort, length d) makes every d-th symbol
     monoalphabetic -> coset-IoC rises above the whole-text baseline at the true
     period.  Cheap to break.
   * An aperiodic keystream (running key / PRNG / long key / OTP) shows no period.

3. **Depth** (the decisive multi-message test, delegated to :mod:`depth`).
   * If the messages share a position-indexed keystream, differencing cancels the
     key and the difference IoC sits above uniform.  Crucially this also *rules
     out* per-message autokey/running-key (whose key depends on each message's own
     content and so would NOT cancel across messages) — leaving a message-
     independent keystream (a fixed long key or a position PRNG): exactly the
     EyeStat model.

4. **Coordinate / fractionation structure** (per base-5-digit IoC, via
   :mod:`trigram`).  A digit stream that is non-uniform while the combined symbol
   is flat points at Bifid/Trifid/columnar-on-coordinates.

Honesty about power
-------------------
With N=83 and ~115 symbols/message, single-message statistics are noisy.  Every
test reports the 3-sigma minimum detectable effect from its own null, and marks a
"flat"/"no period" result as *underpowered* rather than *negative* when the data
could not have revealed the effect anyway.  The pooled (1036-symbol) and the
9-way depth tests are where the real power is.

Validation
----------
``selftest`` runs the classifier on **synthetic ciphertext of known type**
(plaintext-like, monoalphabetic, periodic Vigenere, aperiodic keystream, uniform,
and an in-depth corpus) and asserts the verdict matches the ground truth.  That is
the soundness gate: the tool is only as trustworthy as its ability to label cases
whose answer we already know.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

import corpus as corpus_mod
import depth as depth_mod
import trigram
from null_model import Significance, bonferroni, significance
from stats import ioc, uniform_ioc

# Significance threshold used for the qualitative verdicts.  z > Z_STRONG is
# treated as a confident detection (p ~ 1e-6 one-sided normal); this is also the
# threshold the existing depth analysis uses.
Z_STRONG = 5.0
Z_WEAK = 3.0


# ---------------------------------------------------------------------------
# Result containers
# ---------------------------------------------------------------------------

@dataclass
class TestResult:
    """One statistic, its calibrated significance, and a readable verdict."""
    name: str
    statistic: float
    significance: Significance
    powered: bool                 # could this test have detected the effect?
    min_detectable: float         # 3-sigma effect size from the null
    note: str = ""
    band: str = ""                # unigram only: flat | residual | language_like
    language_fraction: float = 0.0  # (obs-uniform)/(language-uniform)

    @property
    def detected(self) -> bool:
        return self.significance.z >= Z_STRONG

    def __str__(self) -> str:
        flag = "DETECTED" if self.detected else (
            "flat" if self.powered else "flat (UNDERPOWERED)")
        return (f"{self.name}: stat={self.statistic:.5g}  z={self.significance.z:.2f}"
                f"  p={self.significance.p_value:.3g}  [{flag}]")


@dataclass
class PeriodScan:
    """Friedman-style per-period coset-IoC scan + Kasiski corroboration."""
    per_period: List[Tuple[int, float, float, float, bool]]  # d, coset_ioc, z, p, powered
    baseline_ioc: float           # whole-text IoC (d=1)
    best_period: Optional[int]
    best_z: float
    best_p_corrected: float
    kasiski_top: List[Tuple[int, int]]  # (period, #repeat-distances divisible)

    @property
    def detected(self) -> bool:
        return self.best_period is not None and self.best_z >= Z_STRONG


@dataclass
class FamilyVerdict:
    family: str
    status: str          # SUPPORTED | CONSISTENT | UNDETERMINED | REFUTED
    reason: str
    next_attack: str
    cost: str            # cheap | moderate | expensive


@dataclass
class MessageReport:
    label: str
    length: int
    unigram: TestResult
    periodicity: PeriodScan


@dataclass
class Classification:
    N: int
    pooled_length: int
    unigram: TestResult
    periodicity_aggregate: List[Tuple[int, float, int]]  # d, mean_z, #msgs argmax
    depth: depth_mod.DepthReport
    digit: List[TestResult]
    per_message: List[MessageReport]
    families: List[FamilyVerdict] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Monte-Carlo nulls (distribution-free; no Gaussian assumption on the stat)
# ---------------------------------------------------------------------------

def _uniform_ioc_null(T: int, N: int, n: int, rng: np.random.Generator
                      ) -> List[float]:
    """IoC of ``n`` independent uniform-random streams of length ``T``."""
    out: List[float] = []
    for _ in range(n):
        s = rng.integers(0, N, size=T)
        out.append(ioc(s.tolist()))
    return out


def _min_detectable(sig: Significance) -> float:
    """3-sigma minimum detectable statistic above the null mean."""
    return sig.null_mean + 3.0 * sig.null_std


# ---------------------------------------------------------------------------
# Test 1 — unigram uniformity
# ---------------------------------------------------------------------------

def unigram_test(seq: Sequence[int], N: int, n_null: int = 400,
                 rng: Optional[np.random.Generator] = None,
                 lang_ioc_hint: Optional[float] = None) -> TestResult:
    """Is the symbol distribution flatter-than-language (poly/stream) or
    language-like (mono-substitution / transposition)?

    Statistic: raw IoC.  Null: uniform-random streams of the same length.  A
    significant *excess* over the uniform null means the cipher preserved a
    non-uniform distribution.
    """
    rng = rng or np.random.default_rng(0)
    T = len(seq)
    obs = ioc(seq)
    null = _uniform_ioc_null(T, N, n_null, rng)
    sig = significance(obs, null, tail="greater")
    mde = _min_detectable(sig)
    # "powered" = a language-like IoC (default ~ 0.0667 scaled by 26/N if no
    # hint) would clear the 3-sigma bar at this length.
    unif = uniform_ioc(N)
    lang_ioc = lang_ioc_hint if lang_ioc_hint is not None else (0.0667 * 26.0 / N)
    powered = lang_ioc >= mde
    # How far toward a language-like IoC does the observed value reach?  This is
    # what separates a *substitution/transposition* (preserves the full
    # non-uniform distribution -> fraction near 1) from a near-flat keystream
    # cipher with a hair of residual structure (significant but fraction ~ 0).
    frac = (obs - unif) / (lang_ioc - unif) if lang_ioc > unif else 0.0
    if sig.z < Z_STRONG:
        band = "flat" if powered else "flat_underpowered"
    elif frac >= 0.5:
        band = "language_like"
    else:
        band = "residual"
    note = (f"uniform 1/N={unif:.4f}; language-like IoC~{lang_ioc:.4f}; "
            f"3-sigma MDE={mde:.4f}; reached {frac:.0%} of the way to "
            f"language-like")
    return TestResult("unigram IoC vs uniform", obs, sig, powered, mde, note,
                      band=band, language_fraction=frac)


# ---------------------------------------------------------------------------
# Test 2 — periodicity (Friedman + Kasiski)
# ---------------------------------------------------------------------------

def _mean_coset_ioc(seq: Sequence[int], d: int) -> float:
    """Mean IoC over the ``d`` cosets ``seq[r::d]`` (cosets of length < 2 are
    skipped)."""
    iocs: List[float] = []
    for r in range(d):
        coset = seq[r::d]
        if len(coset) >= 2:
            iocs.append(ioc(coset))
    return float(np.mean(iocs)) if iocs else 0.0


def _kasiski_tally(seq: Sequence[int], min_len: int = 3,
                   max_period: int = 20) -> List[Tuple[int, int]]:
    """For each candidate period, count how many repeated-n-gram distances it
    divides (the standard factor-analysis form, robust to chance repeats)."""
    positions: Dict[Tuple[int, ...], List[int]] = {}
    seq = list(seq)
    for i in range(len(seq) - min_len + 1):
        gram = tuple(seq[i:i + min_len])
        positions.setdefault(gram, []).append(i)
    distances: List[int] = []
    for occ in positions.values():
        if len(occ) > 1:
            for a in range(len(occ)):
                for b in range(a + 1, len(occ)):
                    distances.append(occ[b] - occ[a])
    tally = Counter()
    for d in range(2, max_period + 1):
        tally[d] = sum(1 for dist in distances if dist % d == 0)
    return tally.most_common(5)


def periodicity_test(seq: Sequence[int], N: int, max_period: int = 16,
                     n_null: int = 300, min_coset: int = 30,
                     rng: Optional[np.random.Generator] = None) -> PeriodScan:
    """Detect a repeating-key period via per-coset IoC lift over the whole-text
    baseline.

    Null model: random shuffles of the sequence (preserves the marginal
    histogram, destroys all positional structure), evaluated at every candidate
    period in one pass.  At the true period of a Vigenere-style cipher each coset
    is monoalphabetic, so its IoC exceeds the shuffled baseline.
    """
    rng = rng or np.random.default_rng(0)
    seq = list(seq)
    T = len(seq)
    baseline = ioc(seq)

    periods = list(range(2, max_period + 1))
    observed = {d: _mean_coset_ioc(seq, d) for d in periods}

    null_by_d: Dict[int, List[float]] = {d: [] for d in periods}
    arr = np.array(seq)
    for _ in range(n_null):
        rng.shuffle(arr)
        sh = arr.tolist()
        for d in periods:
            null_by_d[d].append(_mean_coset_ioc(sh, d))

    per_period: List[Tuple[int, float, float, float, bool]] = []
    raw_p: List[float] = []
    for d in periods:
        sig = significance(observed[d], null_by_d[d], tail="greater")
        powered = (T // d) >= min_coset
        per_period.append((d, observed[d], sig.z, sig.p_value, powered))
        raw_p.append(sig.p_value)

    # Multiple-testing correction over the periods tried; only powered periods
    # are eligible to be "the period".
    best_period: Optional[int] = None
    best_z = -np.inf
    best_p_corr = 1.0
    for (d, _ioc, z, p, powered) in per_period:
        if powered and z > best_z:
            best_z = z
            best_period = d
            best_p_corr = bonferroni(p, len(periods))
    if best_period is None:
        best_z = 0.0

    kas = _kasiski_tally(seq, 3, max_period)
    return PeriodScan(per_period=per_period, baseline_ioc=baseline,
                      best_period=best_period, best_z=float(best_z),
                      best_p_corrected=best_p_corr, kasiski_top=kas)


# ---------------------------------------------------------------------------
# Test 3 — coordinate / fractionation structure (base-5 trigram digits)
# ---------------------------------------------------------------------------

def digit_structure_test(seq: Sequence[int], N: int, base: int = 5,
                         ndigits: int = 3, n_null: int = 400,
                         symbol_range: Optional[int] = None,
                         rng: Optional[np.random.Generator] = None
                         ) -> List[TestResult]:
    """Per-digit IoC against a **symbol-uniform** null.

    A digit stream that is significantly non-uniform *beyond what a uniform draw
    over the alphabet already forces* is a fingerprint of fractionation/coordinate
    ciphers.  (N=83 is prime, so this is a *source-encoding* view, not an
    algebraic alphabet split — see :mod:`trigram`.)

    Critical subtlety: with ``N=83`` the most-significant base-5 digit can only be
    ``0..3`` (``82 // 25 == 3``), so it is non-uniform *by construction*.  The null
    therefore samples symbols uniformly over ``[0, symbol_range)`` (default ``N``)
    and decomposes THOSE — capturing the structural cap — rather than assuming
    each digit is uniform over ``base``.  Otherwise the cap masquerades as cipher
    structure (it is the single biggest false-positive trap here).
    """
    rng = rng or np.random.default_rng(0)
    if not trigram.alphabet_fits(seq, base, ndigits):
        return []
    rng_max = symbol_range if symbol_range is not None else N
    streams = trigram.decompose_sequence(seq, base, ndigits)
    T = len(seq)

    # Build the symbol-uniform null once, reading off every digit per draw.
    null_by_digit: List[List[float]] = [[] for _ in range(ndigits)]
    for _ in range(n_null):
        draw = rng.integers(0, rng_max, size=T).tolist()
        d_streams = trigram.decompose_sequence(draw, base, ndigits)
        for i in range(ndigits):
            null_by_digit[i].append(ioc(d_streams[i]))

    out: List[TestResult] = []
    for i, s in enumerate(streams):
        obs = ioc(s)
        sig = significance(obs, null_by_digit[i], tail="greater")
        mde = _min_detectable(sig)
        out.append(TestResult(f"digit[{i}] IoC (base {base})", obs, sig,
                              powered=True, min_detectable=mde,
                              note=f"symbol-uniform null mean={sig.null_mean:.4f}"))
    return out


# ---------------------------------------------------------------------------
# Per-message and corpus-level classification
# ---------------------------------------------------------------------------

def classify_message(seq: Sequence[int], label: str, N: int,
                     max_period: int = 16, n_null: int = 300,
                     rng: Optional[np.random.Generator] = None) -> MessageReport:
    rng = rng or np.random.default_rng(0)
    uni = unigram_test(seq, N, n_null=n_null, rng=rng)
    per = periodicity_test(seq, N, max_period=max_period, n_null=n_null, rng=rng)
    return MessageReport(label=label, length=len(seq), unigram=uni,
                         periodicity=per)


def _build_families(uni: TestResult, period_agg: List[Tuple[int, float, int]],
                    dep: depth_mod.DepthReport, digit: List[TestResult]
                    ) -> List[FamilyVerdict]:
    """Walk the decision tree and emit a per-family verdict + recommended attack.

    The ordering is by attack cost so the shortlist literally narrows effort:
    cheap structural attacks first, expensive brute-force last.
    """
    fams: List[FamilyVerdict] = []
    any_period = (period_agg and period_agg[0][1] >= Z_STRONG)
    in_depth = dep.significance.z >= Z_STRONG

    # --- Substitution / transposition (need a language-like unigram) ---
    if uni.band == "language_like":
        fams.append(FamilyVerdict(
            "monoalphabetic_substitution", "CONSISTENT",
            f"unigram reaches {uni.language_fraction:.0%} of the way to a "
            "language-like IoC: the cipher preserves a non-uniform distribution.",
            "frequency analysis + hill-climb on a fixed substitution table.",
            "cheap"))
        fams.append(FamilyVerdict(
            "simple_transposition", "CONSISTENT",
            "a language-like unigram is also consistent with transposition, "
            "which keeps the exact symbol multiset; the unigram alone cannot "
            "separate this from substitution.",
            "match the symbol multiset to a language profile, then anagram / "
            "columnar search.",
            "cheap"))
    elif uni.band == "residual":
        reason = (f"unigram is significantly above uniform (z={uni.significance.z:.1f})"
                  f" but reaches only {uni.language_fraction:.0%} of a language-like"
                  " IoC — far too flat to be a substitution/transposition of "
                  "natural language. The small excess is residual structure (a "
                  "slightly non-flat keystream and/or shared-keystream pooling), "
                  "not a preserved language distribution.")
        fams.append(FamilyVerdict(
            "monoalphabetic_substitution", "REFUTED", reason,
            "n/a (distribution is near-uniform, not language-shaped).", "cheap"))
        fams.append(FamilyVerdict(
            "simple_transposition", "REFUTED", reason,
            "n/a (a transposition would preserve the full language distribution)."
            , "cheap"))
    else:  # flat or flat_underpowered
        powered_flat = (uni.band == "flat")
        reason = ("unigram is statistically flat (IoC ~ 1/N)"
                  if powered_flat else
                  "unigram looks flat but the test is UNDERPOWERED at this "
                  "length (a language-like IoC would not clear 3-sigma)")
        status = "REFUTED" if powered_flat else "UNDETERMINED"
        fams.append(FamilyVerdict(
            "monoalphabetic_substitution", status,
            reason + " — a single substitution table would leave the "
            "distribution non-uniform.",
            "n/a" if status == "REFUTED" else "lengthen text / pool messages "
            "to gain power before trusting this.",
            "cheap"))
        fams.append(FamilyVerdict(
            "simple_transposition", status,
            reason + " — pure transposition would preserve the (non-uniform) "
            "plaintext distribution.",
            "n/a" if status == "REFUTED" else "pool messages for a powered "
            "unigram test.",
            "cheap"))

    # --- Periodic polyalphabetic ---
    if any_period:
        d = period_agg[0][0]
        fams.append(FamilyVerdict(
            "polyalphabetic_periodic_vigenere", "SUPPORTED",
            f"a repeating-key period d={d} shows significant per-coset IoC lift "
            f"(Friedman) consistent across messages.",
            f"split into d={d} cosets and solve each as a monoalphabetic shift.",
            "cheap"))
    else:
        fams.append(FamilyVerdict(
            "polyalphabetic_periodic_vigenere", "REFUTED",
            "no candidate period shows a coset-IoC lift above the shuffled "
            "baseline within the powered range — the key does not repeat at a "
            "short period.",
            "n/a (rules out a short repeating key).",
            "cheap"))

    # --- Depth: shared position-keystream vs per-message keys ---
    if in_depth:
        fams.append(FamilyVerdict(
            "polyalphabetic_shared_keystream", "SUPPORTED",
            f"messages are IN DEPTH (difference-IoC z={dep.significance.z:.1f}): "
            "they share a position-indexed keystream, so differencing cancels "
            "the key.  This is a message-independent keystream — a fixed long key "
            "or a position-seeded PRNG.",
            "depth/crib-drag (exact) to read all messages at once; in parallel, "
            "hunt the PRNG seed (EyeStat).",
            "moderate"))
        fams.append(FamilyVerdict(
            "autokey_or_running_key_per_message", "REFUTED",
            "confirmed cross-message depth is INCOMPATIBLE with a per-message "
            "autokey/running-key: such a key depends on each message's own "
            "plaintext and would not cancel across messages.",
            "n/a (ruled out by depth).",
            "moderate"))
        fams.append(FamilyVerdict(
            "random_or_one_time_pad", "REFUTED",
            "a true OTP / per-message random key would not align across "
            "messages; the observed column coincidence rules it out.",
            "n/a (ruled out by depth).",
            "expensive"))
    else:
        fams.append(FamilyVerdict(
            "polyalphabetic_shared_keystream", "UNDETERMINED",
            "no significant cross-message depth detected (or single message): "
            "cannot assert a shared keystream.",
            "align messages by a different offset / direction and re-test depth.",
            "moderate"))
        fams.append(FamilyVerdict(
            "random_or_one_time_pad", "CONSISTENT",
            "flat unigram, no period, no depth is also what a one-time-pad / "
            "irrecoverable keystream looks like.",
            "n/a (no statistical purchase; needs external info).",
            "expensive"))

    # --- Coordinate / fractionation ---
    digit_hit = any(t.detected for t in digit)
    if digit_hit:
        which = ", ".join(t.name for t in digit if t.detected)
        fams.append(FamilyVerdict(
            "fractionation_coordinate", "SUPPORTED",
            f"a base-5 digit stream is significantly non-uniform ({which}) while "
            "the combined symbol is flat — coordinate-level structure.",
            "Bifid/Trifid and columnar attacks on the base-5 coordinates "
            "(trigram module).",
            "moderate"))
    elif digit:
        fams.append(FamilyVerdict(
            "fractionation_coordinate", "UNDETERMINED",
            "no single base-5 digit stream stands out from uniform; coordinate "
            "structure is not visible (depends on the source-encoding hypothesis "
            "being correct).",
            "test alternative radices / digit orders before committing.",
            "moderate"))

    # Order by status priority then cost.
    status_rank = {"SUPPORTED": 0, "CONSISTENT": 1, "UNDETERMINED": 2,
                   "REFUTED": 3}
    cost_rank = {"cheap": 0, "moderate": 1, "expensive": 2}
    fams.sort(key=lambda f: (status_rank[f.status], cost_rank[f.cost]))
    return fams


def classify_corpus(c: corpus_mod.Corpus, max_period: int = 16,
                    n_null: int = 300, seed: int = 0) -> Classification:
    """Full corpus classification: pooled unigram, per-message periodicity
    aggregate, depth, and coordinate structure -> ranked family shortlist."""
    rng = np.random.default_rng(seed)
    N = c.N
    pooled: List[int] = [v for ct in c.ciphertexts for v in ct]

    uni = unigram_test(pooled, N, n_null=n_null, rng=rng)

    per_message: List[MessageReport] = []
    for i, ct in enumerate(c.ciphertexts):
        per_message.append(
            classify_message(ct, c.labels[i], N, max_period=max_period,
                             n_null=n_null, rng=rng))

    # Aggregate periodicity across messages: mean z per period and how often
    # each period is a message's powered argmax.
    period_z: Dict[int, List[float]] = {}
    argmax_count: Counter = Counter()
    for mr in per_message:
        best_d, best_z = None, -np.inf
        for (d, _ioc, z, _p, powered) in mr.periodicity.per_period:
            period_z.setdefault(d, []).append(z)
            if powered and z > best_z:
                best_z, best_d = z, d
        if best_d is not None and best_z >= Z_WEAK:
            argmax_count[best_d] += 1
    period_agg = sorted(
        ((d, float(np.mean(zs)), argmax_count.get(d, 0))
         for d, zs in period_z.items()),
        key=lambda x: -x[1])

    dep = depth_mod.confirm_depth(c, n_null=max(n_null, 300), seed=seed)
    digit = digit_structure_test(pooled, N, n_null=n_null, rng=rng)

    fams = _build_families(uni, period_agg, dep, digit)
    return Classification(N=N, pooled_length=len(pooled), unigram=uni,
                          periodicity_aggregate=period_agg, depth=dep,
                          digit=digit, per_message=per_message, families=fams)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def format_classification(cl: Classification) -> str:
    L: List[str] = []
    L.append("=" * 70)
    L.append("CIPHER-TYPE CLASSIFICATION")
    L.append("=" * 70)
    L.append(f"alphabet N={cl.N}   pooled length={cl.pooled_length}   "
             f"messages={len(cl.per_message)}")
    L.append("")
    L.append("[1] Unigram uniformity (pooled)")
    L.append(f"    {cl.unigram}")
    L.append(f"    {cl.unigram.note}")
    L.append("")
    L.append("[2] Periodicity (per-message Friedman, aggregated)")
    L.append("    period   mean-z   #msgs-argmax")
    for d, mz, cnt in cl.periodicity_aggregate[:6]:
        L.append(f"      {d:>3}   {mz:>6.2f}   {cnt}")
    L.append("")
    L.append("[3] Depth (shared position-keystream)")
    L.append(f"    mean pairwise difference IoC : {cl.depth.mean_pair_diff_ioc:.4f}")
    L.append(f"    uniform baseline (1/N)       : {cl.depth.uniform_baseline:.4f}")
    L.append(f"    column agreement             : {cl.depth.equal_fraction:.1%}")
    L.append(f"    significance                 : {cl.depth.significance}")
    L.append("")
    if cl.digit:
        L.append("[4] Coordinate structure (base-5 trigram digits, pooled)")
        for t in cl.digit:
            L.append(f"    {t}")
        L.append("")
    L.append("-" * 70)
    L.append("VERDICT — families ranked (cheap, supported attacks first)")
    L.append("-" * 70)
    for f in cl.families:
        L.append(f"  [{f.status:12}] {f.family}  ({f.cost})")
        L.append(f"      why : {f.reason}")
        L.append(f"      next: {f.next_attack}")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Selftest — synthetic ciphertext of KNOWN type
# ---------------------------------------------------------------------------

def _zipf_pmf(k: int, N: int) -> np.ndarray:
    """A clearly non-uniform 'language-like' pmf over the first ``k`` of ``N``
    symbols (Zipf weights), padded with zeros."""
    w = np.zeros(N)
    w[:k] = 1.0 / (np.arange(1, k + 1))
    return w / w.sum()


def _sample(pmf: np.ndarray, T: int, rng: np.random.Generator) -> List[int]:
    return rng.choice(len(pmf), size=T, p=pmf).tolist()


def selftest() -> List[tuple[str, bool]]:
    out: List[tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(7)
    pmf = _zipf_pmf(30, N)          # IoC ~ 0.10, normalised ~ 8.5 >> uniform

    # --- (a) plaintext-like / monoalphabetic: structured unigram ---
    plain = _sample(pmf, 1400, rng)
    perm = rng.permutation(N)
    mono = [int(perm[p]) for p in plain]
    r_mono = classify_message(mono, "mono", N, n_null=200,
                              rng=np.random.default_rng(1))
    out.append(("monoalphabetic -> unigram DETECTED",
                r_mono.unigram.detected))
    out.append(("monoalphabetic -> no spurious short period",
                not r_mono.periodicity.detected))

    # --- (b) periodic Vigenere (period 5): flat-ish unigram, period detected ---
    key5 = rng.integers(0, N, size=5)
    plain_v = _sample(pmf, 1400, rng)
    vig = [(plain_v[t] + int(key5[t % 5])) % N for t in range(len(plain_v))]
    r_vig = periodicity_test(vig, N, max_period=16, n_null=200,
                             rng=np.random.default_rng(2))
    out.append(("vigenere period-5 detected",
                r_vig.detected and r_vig.best_period in (5, 10, 15)))

    # --- (c) aperiodic full-length keystream: flat, NO period ---
    ks = rng.integers(0, N, size=1400)
    plain_s = _sample(pmf, 1400, rng)
    stream = [(plain_s[t] + int(ks[t])) % N for t in range(len(plain_s))]
    r_str = classify_message(stream, "stream", N, n_null=200,
                             rng=np.random.default_rng(3))
    out.append(("aperiodic keystream -> unigram flat",
                not r_str.unigram.detected))
    out.append(("aperiodic keystream -> no period detected",
                not r_str.periodicity.detected))

    # --- (d) uniform random: flat, no period ---
    uni_seq = rng.integers(0, N, size=1400).tolist()
    r_uni = classify_message(uni_seq, "uniform", N, n_null=200,
                             rng=np.random.default_rng(4))
    out.append(("uniform -> unigram flat",
                not r_uni.unigram.detected))
    out.append(("uniform -> no period",
                not r_uni.periodicity.detected))

    # --- (e) in-depth corpus: shared keystream cancels under differencing ---
    M, T = 6, 200
    shared_ks = rng.integers(0, N, size=T)
    cts = []
    for _ in range(M):
        p = _sample(pmf, T, rng)
        cts.append(tuple((p[t] + int(shared_ks[t])) % N for t in range(T)))
    depth_corpus = corpus_mod.Corpus(
        deck_size=N, labels=tuple(f"m{i}" for i in range(M)),
        ciphertexts=tuple(cts), lengths=tuple(T for _ in range(M)),
        sigma0_targets=None)
    cl_depth = classify_corpus(depth_corpus, max_period=12, n_null=200, seed=5)
    out.append(("in-depth corpus -> depth SUPPORTED",
                cl_depth.depth.significance.z >= Z_STRONG))
    out.append(("in-depth corpus -> shared_keystream is top family",
                cl_depth.families[0].family == "polyalphabetic_shared_keystream"
                and cl_depth.families[0].status == "SUPPORTED"))
    out.append(("in-depth corpus -> autokey/running-key REFUTED",
                any(f.family == "autokey_or_running_key_per_message"
                    and f.status == "REFUTED" for f in cl_depth.families)))

    # --- (f) independent-key corpus: NO depth ---
    cts_ind = []
    for _ in range(M):
        p = _sample(pmf, T, rng)
        k = rng.integers(0, N, size=T)
        cts_ind.append(tuple((p[t] + int(k[t])) % N for t in range(T)))
    indep_corpus = corpus_mod.Corpus(
        deck_size=N, labels=tuple(f"m{i}" for i in range(M)),
        ciphertexts=tuple(cts_ind), lengths=tuple(T for _ in range(M)),
        sigma0_targets=None)
    cl_indep = classify_corpus(indep_corpus, max_period=12, n_null=200, seed=6)
    out.append(("independent-key corpus -> no depth",
                cl_indep.depth.significance.z < Z_STRONG))

    # --- (g) digit-structure test flags a planted constant coordinate ---
    planted = []
    for _ in range(1400):
        d0 = rng.integers(0, 5); d1 = rng.integers(0, 5); d2 = 4
        planted.append(trigram.from_digits([int(d0), int(d1), d2], 5))
    # Null spans the full 0..124 range so each digit is genuinely uniform over
    # base-5; the planted constant LSB must then stand out (and only it).
    dig = digit_structure_test(planted, N, n_null=200, symbol_range=125,
                               rng=np.random.default_rng(8))
    out.append(("digit test flags planted constant coordinate",
                len(dig) == 3 and dig[2].detected))
    out.append(("digit test does NOT false-positive uniform coordinates",
                len(dig) == 3 and not dig[0].detected and not dig[1].detected))

    # The encoding-cap trap: a plain uniform-over-N stream must NOT trip the
    # digit test, even though its MSB digit is non-uniform by construction.
    flat_syms = np.random.default_rng(9).integers(0, N, size=1400).tolist()
    dig_flat = digit_structure_test(flat_syms, N, n_null=200,
                                    rng=np.random.default_rng(10))
    out.append(("digit test ignores the base-5 MSB encoding cap (no FP)",
                len(dig_flat) == 3 and not any(t.detected for t in dig_flat)))

    return out


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        results = selftest()
        for label, ok in results:
            print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
        n_ok = sum(1 for _, ok in results if ok)
        print(f"\n{n_ok}/{len(results)} classify checks passed")
        sys.exit(0 if n_ok == len(results) else 1)

    c = corpus_mod.load()
    cl = classify_corpus(c, max_period=16, n_null=400, seed=1)
    print(format_classification(cl))
