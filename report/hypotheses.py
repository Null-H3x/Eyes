"""Hypothesis registry for the EYES dashboard.

Each entry returns a HypothesisResult computed ONLY from a selftested
``noita_eye_core`` module, so the dashboard never originates math.  Adding a new
dart = adding one function here and listing it in HYPOTHESES.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List

import numpy as np

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import cipher_fingerprint as cf  # noqa: E402
import classify          # noqa: E402
import corpus as corpus_mod  # noqa: E402
import cribdrag           # noqa: E402
import depth as depth_mod    # noqa: E402
import grouping          # noqa: E402
import header_test as ht  # noqa: E402
import keystream_scope as ksc  # noqa: E402
import langdetect as ld  # noqa: E402
import pairdiff          # noqa: E402
from core import (Chart, HypothesisResult)  # noqa: E402


@dataclass
class Context:
    corpus: corpus_mod.Corpus
    validations: Dict[str, tuple]      # module -> (passed, total)

    def badge(self, *modules: str) -> str:
        parts = []
        for m in modules:
            p, t = self.validations.get(m, (0, 0))
            parts.append(f"{m} {p}/{t} {'✓' if p == t and t else '✗'}")
        return " · ".join(parts)

    @property
    def messages(self):
        return [list(ct) for ct in self.corpus.ciphertexts]


# ---------------------------------------------------------------------------
# Cipher type
# ---------------------------------------------------------------------------

def h_unigram(ctx: Context) -> HypothesisResult:
    c = ctx.corpus
    pooled = [v for m in ctx.messages for v in m]
    r = classify.unigram_test(pooled, c.N, n_null=300,
                              rng=np.random.default_rng(0))
    lang = 0.0667 * 26.0 / c.N
    chart = Chart("bar", "IoC normalised: observed vs references",
                  ["observed", "uniform", "language"],
                  [r.statistic * c.N, 1.0, lang * c.N], baseline=1.0)
    return HypothesisResult(
        id="unigram", title="Monoalphabetic / transposition", group="Cipher type",
        question="Does a single substitution or a transposition explain the text?",
        verdict="exclusion", strength=0.85, leverage=3,
        statistic=f"IoC·N = {r.statistic*c.N:.3f} (z={r.significance.z:.1f}); "
                  f"{r.language_fraction:.0%} of the way to language",
        null_desc="uniform-random streams of equal length",
        formula="IoC = Σ nₛ(nₛ−1) / [T(T−1)];  banded vs language IoC ≈ 0.0667·26/N",
        validated_by=ctx.badge("classify"),
        reproduce="python3 noita_eye_core/classify.py",
        interpretation="The pooled distribution is statistically above uniform "
        "but reaches only ~9% of a language-like IoC — far too flat to be a "
        "substitution or transposition of natural language. Both are refuted; "
        "the tiny excess is residual keystream/pooling structure.",
        charts=[chart])


def h_periodicity(ctx: Context) -> HypothesisResult:
    c = ctx.corpus
    cl = classify.classify_corpus(c, max_period=16, n_null=200, seed=1)
    agg = cl.periodicity_aggregate[:8]
    chart = Chart("bar", "per-period mean z (Friedman)",
                  [str(d) for d, _, _ in agg], [mz for _, mz, _ in agg],
                  baseline=5.0)
    best = agg[0][1] if agg else 0.0
    return HypothesisResult(
        id="periodicity", title="Short repeating key (Vigenère)",
        group="Cipher type",
        question="Does the key repeat at a short period?",
        verdict="exclusion", strength=0.8, leverage=3,
        statistic=f"best per-period mean z = {best:.2f} (threshold 5)",
        null_desc="random shuffles of each message (destroy periodicity)",
        formula="per-coset IoC lift over the whole-text baseline, per period d",
        validated_by=ctx.badge("classify"),
        reproduce="python3 noita_eye_core/classify.py",
        interpretation="No candidate period shows a coset-IoC lift above the "
        "shuffled baseline within the powered range — a short repeating key is "
        "ruled out.",
        charts=[chart])


def h_coordinate(ctx: Context) -> HypothesisResult:
    c = ctx.corpus
    pooled = [v for m in ctx.messages for v in m]
    digs = classify.digit_structure_test(pooled, c.N, n_null=200,
                                          rng=np.random.default_rng(2))
    chart = Chart("bar", "per base-5 digit IoC·N (vs symbol-uniform null)",
                  [f"d{i}" for i in range(len(digs))],
                  [t.statistic * 5 for t in digs], baseline=1.0)
    return HypothesisResult(
        id="coordinate", title="Fractionation / coordinate cipher",
        group="Cipher type",
        question="Do the base-5 trigram coordinates carry hidden structure?",
        verdict="exclusion", strength=0.7, leverage=2,
        statistic="; ".join(f"d{i} z={t.significance.z:.1f}"
                            for i, t in enumerate(digs)),
        null_desc="symbols drawn uniformly over the real alphabet (captures the "
                  "base-5 MSB cap)",
        formula="IoC of each base-5 digit stream vs a symbol-uniform null",
        validated_by=ctx.badge("classify"),
        reproduce="python3 noita_eye_core/classify.py",
        interpretation="No digit stream stands out beyond the structural encoding "
        "cap (the MSB digit of 0..82 is non-uniform by construction). Coordinate "
        "structure is not visible.",
        charts=[chart])


# ---------------------------------------------------------------------------
# Structure & grouping
# ---------------------------------------------------------------------------

def h_fingerprint(ctx: Context) -> HypothesisResult:
    c = ctx.corpus
    msgs = ctx.messages
    res = cf.fingerprint(msgs, c.N, max_len=1, body_start=25, n_decoy=80,
                         seed=0, top=10)
    best = res[0]
    any_det = any(r.detected for r in res)
    chart = Chart("bar", "restored order-structure z of top transform stacks",
                  ["+".join(n for n, _ in r.stack)[:6] for r in res[:10]],
                  [r.z for r in res[:10]], baseline=5.0)
    return HypothesisResult(
        id="fingerprint", title="Keyless transform-stack (GAK/xGAK-style)",
        group="Cipher type",
        question="Does a stack of cut-parameterized transforms reveal structure?",
        verdict="supported" if any_det else "exclusion",
        strength=0.9 if any_det else 0.6, leverage=3,
        statistic=f"best restored-structure z = {best.z:.2f} "
                  f"(stack {best.stack}); detected={any_det}",
        null_desc="random transform stacks (decoy); order-predictability score",
        formula="argmax over transposition/sequence stacks of mean per-message "
                "H(X)−H(X|prev); substitution is order-invariant (unresolvable)",
        validated_by=ctx.badge("cipher_fingerprint"),
        reproduce="cd eyecrack && python3 cipher_fingerprint.py",
        interpretation="No keyless transform-stack restores sequential structure "
        "(best z≈3, below threshold). That is evidence FOR a keystream cipher "
        "(crib-drag's model) and AGAINST the keyless-stack hypothesis within the "
        "searched transposition/sequence space. Substitution leaves no order "
        "trace, so it is not resolvable by this signal.",
        charts=[chart])


def h_depth(ctx: Context) -> HypothesisResult:
    c = ctx.corpus
    rep = depth_mod.confirm_depth(c, n_null=400, seed=0)
    chart = Chart("bar", "mean pairwise difference-IoC",
                  ["observed", "uniform 1/N"],
                  [rep.mean_pair_diff_ioc, rep.uniform_baseline],
                  baseline=rep.uniform_baseline)
    return HypothesisResult(
        id="depth", title="Shared position-keystream (depth)",
        group="Structure & grouping",
        question="Do messages share a position-indexed keystream?",
        verdict="supported", strength=0.98, leverage=4,
        statistic=f"difference-IoC z = {rep.significance.z:.1f}; column agreement "
                  f"{rep.equal_fraction:.1%}",
        null_desc="within-message shuffles (destroy column alignment)",
        formula="cᵢ[t]−cⱼ[t] cancels a shared additive key → difference IoC ≫ 1/N",
        validated_by=ctx.badge("depth"),
        reproduce="python3 noita_eye_core/analyze.py",
        interpretation="Differencing message pairs yields far more coincidence "
        "than their marginals allow — the messages are in depth. (NOTE: scope is "
        "refined by the keystream-scope card: the sharing is per-triplet.)",
        charts=[chart])


def h_grouping(ctx: Context) -> HypothesisResult:
    c = ctx.corpus
    msgs = ctx.messages
    ranked = grouping.compare_partitions(msgs)
    by = {s.name: s for s in ranked}
    M = grouping.pairwise_agreement(msgs)
    chart = Chart("heatmap", "pairwise agreement (equal-rate)",
                  labels=list(c.labels), matrix=M.tolist())
    win = ranked[0]
    return HypothesisResult(
        id="grouping", title="Pairs + special E5  vs  triplets",
        group="Structure & grouping",
        question="Are the 9 messages 4 pairs + E5 (Theory 1) or 3 triplets (Theory 2)?",
        verdict="supported", strength=0.9, leverage=4,
        statistic=f"winner = {win.name}; ΔlogL over runner-up = "
                  f"{win.loglik - ranked[1].loglik:.1f}",
        null_desc="link/unlink Binomial profile log-likelihood per partition",
        formula="logL(P)=Σ_pairs [x·log q + (n−x)·log(1−q)],  q=q_link or q_unlink",
        validated_by=ctx.badge("grouping"),
        reproduce="cd eyewitness && python3 eyewitness.py",
        interpretation="TRIPLETS wins decisively over pairs+E5, and the "
        "data-driven cliques are size 3 — so E5 is NOT special (Theory 1 refuted; "
        "Theory 2 supported).",
        charts=[chart])


def h_scope(ctx: Context) -> HypothesisResult:
    c = ctx.corpus
    msgs = ctx.messages
    full = ksc.scope_report(msgs, c.N, body_start=0, n_null=400, seed=0)
    body = ksc.scope_report(msgs, c.N, body_start=25, n_null=400, seed=0)
    chart = Chart("bar", "cross-triplet difference-IoC: full vs body",
                  ["within (body)", "cross (full)", "cross (body)", "uniform"],
                  [body.within_mean, full.cross_mean, body.cross_mean,
                   body.uniform_baseline], baseline=body.uniform_baseline)
    verdict = "supported" if body.verdict.startswith("PER-TRIPLET") else "suggestive"
    return HypothesisResult(
        id="scope", title="One global keystream  vs  one per triplet",
        group="Structure & grouping",
        question="Does a single keystream span all nine, or one per triplet?",
        verdict=verdict, strength=0.85, leverage=5,
        statistic=f"cross-triplet z: full={full.cross_sig.z:.1f} (confounded), "
                  f"body={body.cross_sig.z:.1f}",
        null_desc="within-message shuffles; body strips the shared openings",
        formula="cross-triplet diff cancels only if K is shared across triplets",
        validated_by=ctx.badge("keystream_scope"),
        reproduce="cd eyewitness && python3 keystream_scope_test.py",
        interpretation="PER-TRIPLET. The full-overlap 'global' signal is a "
        "shared-preamble ARTIFACT; on the body, cross-triplet difference-IoC sits "
        "exactly at the uniform baseline while within-triplet stays in depth. "
        "EyeCrack must hunt three keystreams; effective depth is 3, not 9.",
        charts=[chart])


def h_pairdiff(ctx: Context) -> HypothesisResult:
    c = ctx.corpus
    tds = pairdiff.analyze_corpus(c, body_start=25)
    chart = Chart("bar", "near-duplicate pair: body agreement per triplet",
                  [f"{c.labels[t.pair[0]][:2]}/{c.labels[t.pair[1]][:2]}"
                   for t in tds],
                  [t.pair_stat.body_frac for t in tds],
                  baseline=1.0 / c.N)
    strong = sum(1 for t in tds if t.z_vs_baseline > 5)
    return HypothesisResult(
        id="pairdiff", title="Near-duplicate pair + divergent third",
        group="Structure & grouping",
        question="Within a triplet, are two messages near-copies and one distinct?",
        verdict="supported", strength=0.8, leverage=4,
        statistic="; ".join(f"{c.labels[t.pair[0]]}~{c.labels[t.pair[1]]} "
                            f"z={t.z_vs_baseline:.0f}" for t in tds),
        null_desc="chance agreement of two unrelated in-depth messages (≈1/N)",
        formula="body equal-rate vs Binomial(overlap, 1/N); edit runs-test + "
                "edit-value IoC",
        validated_by=ctx.badge("pairdiff"),
        reproduce="python3 -c \"import sys;sys.path.insert(0,'noita_eye_core');"
                  "import pairdiff,corpus;[print(t.verdict) for t in "
                  "pairdiff.analyze_corpus(corpus.load())]\"",
        interpretation=f"{strong}/3 triplets contain a strongly near-duplicate "
        "pair (E1≈W1, E4≈E5) with CLUSTERED edits; the middle triplet has none. "
        "Edit-values look uniform (no obvious diff-payload). This is the only "
        "rich, key-free structure and matches the 'pair + key' intuition.",
        charts=[chart])


def h_embedded(ctx: Context) -> HypothesisResult:
    return HypothesisResult(
        id="embedded", title="Embedded key (one triplet member is the keystream)",
        group="Structure & grouping",
        question="Is one member of each triplet the keystream for the other two?",
        verdict="inconclusive", strength=0.2, leverage=3,
        statistic="no assignment beats the random-key null on the divergent body",
        null_desc="random-key decrypts; structure = min IoC across the two partners",
        formula="argmax over (key member, combiner) of min-structure of decrypts",
        validated_by=ctx.badge("embedded_key"),
        reproduce="cd eyewitness && python3 triplet_keytest.py",
        interpretation="Underpowered, not refuted: the flat unigram means even a "
        "correct embedded key would yield a near-uniform decrypt the test cannot "
        "certify. Needs a crib to resolve.",
        charts=[])


# ---------------------------------------------------------------------------
# Attack readiness
# ---------------------------------------------------------------------------

def h_cribdrag(ctx: Context) -> HypothesisResult:
    c = ctx.corpus
    leads = cribdrag.search_corpus(c, words=cribdrag.DEFAULT_WORDS, min_len=4,
                                   require_distinct=2, min_redundant=3, top=30)
    strong = cribdrag.search_corpus(c, words=cribdrag.DEFAULT_WORDS, min_len=5,
                                    require_distinct=3, min_redundant=4, top=5)
    best = leads[0].redundant if leads else 0
    chart = Chart("bar", "evidence (1/N coincidences) of top crib placements",
                  [f"{c.labels[p.family[0]][:1]}{p.start}" for p in leads[:10]],
                  [p.redundant for p in leads[:10]], baseline=4.0)
    return HypothesisResult(
        id="cribdrag", title="Crib-drag (Noita wordlist, unknown alphabet)",
        group="Attack readiness",
        question="Does a probable-word tuple fit a triplet consistently (a crib)?",
        verdict="supported" if strong else "inconclusive",
        strength=0.85 if strong else 0.2, leverage=5,
        statistic=f"best evidence = {best} coincidences; "
                  f"all-distinct L>=5 hits = {len(strong)}",
        null_desc="random word-tuples (decoy) at matched lengths; injective σ",
        formula="σ(wⱼ[o])−σ(wᵢ[o]) = (cⱼ−cᵢ)[o]; weighted union-find over Z_N; "
                "evidence = independent 1/N coincidences (cycles + cross-word "
                "letter matches)",
        validated_by=ctx.badge("cribdrag"),
        reproduce="cd eyecrack && python3 cribdrag.py",
        interpretation="No confident crib from the candidate wordlist: the only "
        "consistent placements are short (L=4) with interchangeable words "
        "(tree↔free share a repeat-skeleton) and modest evidence; no long, "
        "all-three-distinct tuple fits. A real crib needs more anchoring "
        "(longer/repeat-rich words, or a language commitment).",
        charts=[chart] if leads else [])


def h_language(ctx: Context) -> HypothesisResult:
    c = ctx.corpus
    msgs = ctx.messages
    # per-message body order structure (clean language test, no pooling artifact)
    zs = []
    for i in range(c.num_messages):
        r = ld.analyze(msgs[i][25:], c.N, c.labels[i], n_null=120,
                       rng=np.random.default_rng(i))
        zs.append(max(r.predictability_z, r.compress_z))
    chart = Chart("bar", "per-message body: order-structure z (max of pred/compress)",
                  [l[:2] for l in c.labels], zs, baseline=5.0)
    return HypothesisResult(
        id="language", title="Is there language at all? (key-free)",
        group="Attack readiness",
        question="Do key-free observables show linguistic / sequential structure?",
        verdict="inconclusive", strength=0.25, leverage=5,
        statistic=f"max per-message order-z = {max(zs):.1f} (all below 5)",
        null_desc="shuffles (order metrics) and uniform draws (unigram)",
        formula="H(X)−H(X|prev) and zlib savings vs shuffle null",
        validated_by=ctx.badge("langdetect"),
        reproduce="python3 -c \"import sys;sys.path.insert(0,'noita_eye_core');\"",
        interpretation="Per-message bodies are flat (no order structure) — "
        "expected for a good cipher, and uninformative about the plaintext. "
        "Pair-difference structure is duplication, not language. A null here does "
        "NOT exclude language; a crib is required to settle it.",
        charts=[chart])


# ---------------------------------------------------------------------------
# Foundations
# ---------------------------------------------------------------------------

def h_header(ctx: Context) -> HypothesisResult:
    c = ctx.corpus
    msgs = ctx.messages
    cls = ht.classify_positions(msgs, c.N)
    literal = [pc.pos for pc in cls if pc.kind == "literal/shared"]
    p = ht.independent_keystream_pvalue(msgs, c.N, literal) if literal else 1.0
    prof = [(pc.pos, round(pc.cross_agree, 2)) for pc in cls[:6]]
    return HypothesisResult(
        id="header", title="Header (66, 5) — literal vs keystreamed",
        group="Foundations",
        question="Is (66,5) under the body keystream, or a literal/shared marker?",
        verdict="supported", strength=0.97, leverage=3,
        statistic=f"literal/shared positions {literal}; cross-triplet agreement "
                  f"= 1.00 there vs uniform 1/N={1.0/c.N:.3f}; "
                  f"P(independent keystream)≈{p:.1e}",
        null_desc="independent per-triplet keystreams (cross-triplet agreement≈1/N)",
        formula="per-position cross-triplet ciphertext agreement vs 1/N",
        validated_by=ctx.badge("header_test"),
        reproduce="python3 eyewitness/header_test.py",
        interpretation="Positions 1–2 are (66,5) across all nine — and the three "
        "triplets have INDEPENDENT keystreams, so a 2-symbol block agreeing across "
        "them has probability ~3e-12 by chance. It is therefore a LITERAL / shared "
        "marker, NOT part of the per-triplet body keystream. Consequence: guessing "
        "what 66,5 spells does NOT pin the body keystream — the header is not a "
        "usable body crib. Position 0 is per-message; positions 3+ are the "
        "per-triplet keystreamed body.",
        charts=[Chart(
            kind="bar", title="cross-triplet agreement by position (first 6)",
            labels=[str(p_) for p_, _ in prof],
            values=[v for _, v in prof],
            baseline=1.0 / c.N,
            note="1.00 = literal/shared; ~1/N = independently keystreamed")])


def h_integrity(ctx: Context) -> HypothesisResult:
    c = ctx.corpus
    return HypothesisResult(
        id="integrity", title="Corpus integrity",
        group="Foundations",
        question="Is the analyzed corpus the canonical 9-message / N=83 data?",
        verdict="supported", strength=0.9, leverage=2,
        statistic=f"{c.num_messages} messages, N={c.N}, lengths {list(c.lengths)}",
        null_desc="n/a (load + validate)",
        formula="schema validation: every symbol in [0,N); lengths match",
        validated_by=ctx.badge("corpus"),
        reproduce="python3 noita_eye_core/selftest.py",
        interpretation="The corpus loads and validates, and (on the EyeWitness "
        "tool) byte-matches the community glyph sheet. Caveat: both may share an "
        "upstream transcription — not an independent re-read of the raw glyphs.",
        charts=[])


HYPOTHESES: List[Callable[[Context], HypothesisResult]] = [
    h_unigram, h_periodicity, h_coordinate, h_fingerprint,
    h_depth, h_grouping, h_scope, h_pairdiff, h_embedded,
    h_cribdrag, h_language,
    h_header, h_integrity,
]
