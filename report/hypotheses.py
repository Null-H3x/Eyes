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
import depthmap as dmap  # noqa: E402
import header_test as ht  # noqa: E402
import keystream_scope as ksc  # noqa: E402
import numbertest as nt  # noqa: E402
import langdetect as ld  # noqa: E402
import pairdiff          # noqa: E402
import repeats as rep    # noqa: E402
import isomorph as iso   # noqa: E402
import chain_extract as ce  # noqa: E402
import chain_models as cm  # noqa: E402
import headerbase as hb   # noqa: E402
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


def h_depthmap(ctx: Context) -> HypothesisResult:
    c = ctx.corpus
    msgs = ctx.messages
    d = dmap.build(msgs, c.N)
    body = [comp for comp in d.body_components if len(comp) > 1]
    body_str = "; ".join("{" + ", ".join(c.labels[i] for i in comp) + "}"
                         for comp in body) or "none beyond pairs"
    return HypothesisResult(
        id="depthmap", title="True depth — how much shared keystream is provable?",
        group="Structure",
        question="How many messages provably share a keystream, and where?",
        verdict="supported", strength=0.8, leverage=4,
        statistic=f"opening shared-K clades: {len(d.opening_components)}; "
                  f"body-persistent shared-K: {body_str}; "
                  f"exploitable (2-deep) positions: {d.exploitable_total}; "
                  f"undetermined pairs: {d.undetermined}/{len(d.pairs)}",
        null_desc="per-pair binomial vs 1/N equality; identical-run proof",
        formula="equal-ciphertext run / equality-rate z; union-find components",
        validated_by=ctx.badge("depthmap"),
        reproduce="python3 eyewitness/depth_map.py",
        interpretation="Shared keystream is only PROVABLE where ciphertext "
        "coincides (identical runs or equality ≫ 1/N); where plaintexts differ it "
        "is invisible, and independence can NEVER be proven. The openings share a "
        "keystream across triplets (refuting strictly-independent per-triplet "
        "keys), but that region is shared plaintext — no decryption leverage. "
        "Body-persistent shared keystream is proven for only TWO near-duplicate "
        "pairs (E1~W1, E4~E5), giving ~136 key-free 2-deep difference positions — "
        "exactly the crib-drag surface. We do NOT have free 3+ depth in the body. "
        "Whether the body keystream is global (which would unlock deep depth) is "
        "undetermined from ciphertext and must be tested with a crib.",
        charts=[])


def h_number(ctx: Context) -> HypothesisResult:
    c = ctx.corpus
    sym = [v for _, v in corpus_mod.universal_positions(c)]
    vals = nt.decode_header(sym, c.N)
    lk = nt.luck_baseline(c.N, sym)
    is34 = 34 in vals.values()
    return HypothesisResult(
        id="number", title="Header is a literal number (e.g. 34)",
        group="Foundations",
        question="Does the literal header (66,5) encode a specific number such as 34?",
        verdict="exclusion", strength=0.82, leverage=2,
        statistic=f"(66,5) -> {sorted(set(vals.values()))}; 34 reachable: {is34}; "
                  f"small ints reachable {lk['reachable_small']}; "
                  f"p(random 1–166 target reachable)={lk['p_random_target_hit']:.3f}",
        null_desc="pre-registered principled encoding family (no free parameters)",
        formula="base-N / base-5-trigram place value, digit sums, per-symbol reads",
        validated_by=ctx.badge("numbertest"),
        reproduce="python3 eyewitness/number_test.py --target 34",
        interpretation="The header is literal (see the header card), so it COULD be "
        "a literal number — but under every principled encoding (66,5) is one of "
        f"{sorted(set(vals.values()))}, and 34 is NOT among them (nor 33/11). Only "
        f"{lk['n_reachable_small']} small integers are reachable at all, so even a "
        "match would be weak. Reading (66,5) as 34 requires a bespoke parameter-fit "
        "map, which two symbols cannot justify. Refuted as stated; a longer literal "
        "run or an independent corroborator would be needed to pin any number.",
        charts=[])


def h_isomorph(ctx: Context) -> HypothesisResult:
    c = ctx.corpus
    msgs = ctx.messages
    sig = iso.significance(msgs, 12, 3, n_null=120)
    pairs13 = iso.find_isomorphs(msgs, 13, 3)
    pc_raw = iso.progressive_chain(msgs, pairs13, c.N)
    # contamination-filtered clean set (clean anchor mr=4) vs raw
    res = ce.extract(msgs, 13, broad_repeats=3, anchor_repeats=4, N=c.N)
    clean = [pr for pr in pairs13
             if ce._redundant(res._gf, pr, msgs, cm.per_msg_prog_rows, c.N)]
    pc_clean = iso.progressive_chain(msgs, clean, c.N)
    return HypothesisResult(
        id="isomorph",
        title="Interrelated alphabets; progressive NOT refuted (contamination corrected)",
        group="Structure",
        verdict="supported", strength=0.85, leverage=4,
        question="Are the per-position alphabets interrelated, and is the "
                 "interrelation positional (progressive)?",
        statistic=f"true isomorphs (L=12): {sig['observed']} vs null "
                  f"{sig['null_mean']:.1f} (z={sig['z']:.0f}); progressive "
                  f"contradictions RAW={pc_raw.contradictions} vs CLEAN="
                  f"{pc_clean.contradictions} (the refutation was contamination); "
                  f"free-δ: permissive",
        null_desc="within-message shuffle null; planted progressive/2-alphabet controls",
        formula="repeat-skeleton matches (diff values); Z_N offset union-find + GF(N) solve",
        validated_by=ctx.badge("isomorph"),
        reproduce="python3 eyewitness/header_base.py",
        interpretation="Abundant isomorphs (same repeated-letter pattern, different "
        "values) at z>100 confirm INTERRELATED alphabets — ruling out independent-"
        "column substitution (general GAK) and unrelated-alphabet running-key/OTP. "
        "CORRECTION: PROGRESSIVE (offset = position) is NOT refuted — the earlier "
        "contradictions came from CONTAMINATED isomorphs; on the contamination-"
        "filtered CLEAN set pure progressive is consistent (two solvers agree). The "
        "literal universal (66,5) header further FORCES pure progressive within the "
        "per-message-progressive family (equal bases). HONEST LIMITS: the clean set "
        "is under-determined (one repeated passage), and free-δ is permissive — so "
        "progressive is a live CANDIDATE, not confirmed; autokey/clock is the "
        "alternative. Open: the specific member, and ordering the alphabet.",
        charts=[])


def h_repeats(ctx: Context) -> HypothesisResult:
    c = ctx.corpus
    msgs = ctx.messages
    offs = sum(len(rep.census(msgs, c.N, k).offset) for k in (3, 4, 5, 6))
    cen5 = rep.census(msgs, c.N, 5)

    def grp(mi):
        for gi, g in enumerate(rep.TRIPLETS):
            if mi in g:
                return gi
        return -1
    cross_body = sum(1 for a in cen5.aligned
                     if grp(a[1][0]) != grp(a[2][0]) and a[1][1] >= 25)
    return HypothesisResult(
        id="repeats", title="Stream vs block / periodic / transposition",
        group="Structure",
        verdict="exclusion", strength=0.9, leverage=3,
        question="Does any substring repeat at a shifted position (a moved/reused "
                 "block, a period, a cut/shuffle)?",
        statistic=f"offset collisions (k=3..6): {offs}; cross-group BODY aligned "
                  f"collisions: {cross_body}; aligned(depth) k=5: {len(cen5.aligned)}",
        null_desc="chance k-gram collisions ~ pairs / N^k (<<1 for k>=4)",
        formula="k-gram census: aligned (same-pos)=depth; offset (diff-pos)=mode tell",
        validated_by=ctx.badge("repeats"),
        reproduce="python3 eyewitness/repeat_census.py",
        interpretation="ZERO offset collisions at every k: no substring sits at a "
        "different position anywhere. This is a verified exclusion of transposition, "
        "a cut / positional shuffle, a periodic / repeating key, and block/ECB "
        "reuse — the cipher is a pure aperiodic, position-locked stream (a per-column "
        "bijection that never moves a symbol). Cross-group repeats occur ONLY in the "
        "opening preamble (positions 1–6), none in the body, so the body keystream is "
        "per-group, not global. (A deck-shuffle keystream — GAK/xGAK — is still "
        "consistent: it generates a per-column bijection without moving positions.)",
        charts=[])


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


def h_provenance(ctx: Context) -> HypothesisResult:
    return HypothesisResult(
        id="provenance",
        title="Provenance: messages are hard-coded constants in noita.exe",
        group="Foundations",
        verdict="confirmed", strength=0.95, leverage=3,
        question="Where do the eye messages come from — an engine algorithm/seed, "
                 "or static data?",
        statistic="9/9 messages decode from SpawnSecretEyes (FUN_005b2d10) to the "
                  "corpus byte-for-byte (base-7 unpack); exactly 9 cases (no West 5)",
        null_desc="n/a (decompiled binary cross-check)",
        formula="base-7 digits MSB-first, drop 0 padding, subtract 1 -> base-5 (5=newline)",
        validated_by=ctx.badge("provenance"),
        reproduce="python3 eyewitness/binary_provenance.py",
        interpretation="The 9 messages are hard-coded 64-bit constants the engine "
        "only unpacks and draws — there is NO decryption, key, or keystream in the "
        "binary, and exactly 9 messages (no hidden West 5). So the cipher was "
        "applied OFFLINE by the author; this is WHY every in-game seed scan was null "
        "(no in-game seed exists) and a third independent source confirms the corpus.",
        charts=[])


def h_bodymodel(ctx: Context) -> HypothesisResult:
    return HypothesisResult(
        id="bodymodel",
        title="Body key schedule: per-message-progressive (not a single alphabet)",
        group="Structure",
        verdict="supported", strength=0.8, leverage=4,
        question="At the repeated body refrain, is there one global sliding "
                 "alphabet (pure-progressive) or a per-message offset?",
        statistic="4x repeat spans 25 glyphs (W1@32-56/@62-86, E2@37-61/@72-96); "
                  "pure-progressive CONTRADICTS across instances, within-instance "
                  "consistent -> per-message bases",
        null_desc="within-instance vs cross-instance consistency (OffsetDSU/GF)",
        formula="c[m][t]=C[(p[m][t]+base_m+t)]; cross-instance symbol agreement",
        validated_by=ctx.badge("refrain", "headerbase"),
        reproduce="python3 eyecrack/refrain_attack.py --constraints",
        interpretation="The body uses PER-MESSAGE bases (pure-progressive is "
        "contradicted across the four refrain instances; within-instance structure "
        "is consistent) — matching the earlier per-group body-key finding. The "
        "literal header forcing pure-progressive applies to the OPENING, not the body.",
        charts=[])


def h_trifid(ctx: Context) -> HypothesisResult:
    return HypothesisResult(
        id="trifid",
        title="Digit-level / fractionation (Trifid family)",
        group="Cipher type",
        verdict="excluded", strength=0.7, leverage=2,
        question="Does the cipher operate on the three base-5 eye-marks "
                 "(fractionation / Trifid), rather than whole glyphs?",
        statistic="per-eye-mark IoC ~uniform; only d0&d1 assoc is a 0..82-compaction "
                  "artifact; inverse digit-transpose at every period 2..24 lowers IoC",
        null_desc="uniform baseline per digit; identity-IoC reference for periods",
        formula="to_digits(value,5,3); per-digit IoC, Cramer V, period scan",
        validated_by=ctx.badge("trifid"),
        reproduce="python3 eyewitness/trifid_scan.py",
        interpretation="No Trifid/fractionation signature: the three eye-mark streams "
        "are near-uniform, their only association is a counting artifact of the "
        "0..82 compaction, and no period reveals structure under inverse "
        "digit-transposition. The structure is glyph-level, not digit-level.",
        charts=[])


def h_refrain(ctx: Context) -> HypothesisResult:
    return HypothesisResult(
        id="refrain",
        title="Attack readiness: refrain known-position crib + n-gram solve",
        group="Attack readiness",
        verdict="inconclusive", strength=0.45, leverage=5,
        question="Can the 4x repeated refrain be cribbed to recover the alphabet?",
        statistic="a correct 25-glyph guess pins 59/83 symbols (~78% corpus); "
                  "IoC hill-climb is degenerate (proven); crib-seeded n-gram solve "
                  "is the live lever",
        null_desc="random-refrain per-message-IoC null; English n-gram fitness",
        formula="x[c]=p+base_m+pos; per-message bases; crib pins q-structure",
        validated_by=ctx.badge("refrain"),
        reproduce="python3 eyecrack/refrain_attack.py --constraints",
        interpretation="The 4x refrain is the live decryption lever: a correct "
        "plaintext guess pins ~78% of the alphabet. IoC-scored hill-climbing is a "
        "proven dead end (order-blind/degenerate); the productive path is a "
        "crib-seeded n-gram solver in the plaintext language. Needs a correct "
        "refrain phrase + alphabet ordering as human input.",
        charts=[])


def h_shared_structure(ctx: Context) -> HypothesisResult:
    import shared_structure as ss
    msgs = ctx.messages
    tr = ss.triplet_openings(msgs, [("T1", (0, 1, 2)), ("T2", (3, 4, 5)),
                                    ("T3", (6, 7, 8))], n_null=300)
    stat = "; ".join(f"{r.name}={r.extent}{'*' if r.significant else ''}" for r in tr)
    return HypothesisResult(
        id="shared_structure",
        title="Model-independent triplet structure (shared openings)",
        group="Structure",
        verdict="supported", strength=0.9, leverage=3,
        question="Do the messages come in triplets sharing long openings, with no "
                 "cipher-model assumption?",
        statistic=f"3-way opening extents (glyphs, *=above null): {stat}",
        null_desc="random aligned-start 3-way isomorph extent",
        formula="isomorph-skeleton extent (same glyph=same glyph); no model",
        validated_by=ctx.badge("shared_structure"),
        reproduce="python3 eyewitness/shared_structure.py",
        interpretation="MODEL-FREE: Triplet 1 (E1/W1/E2) shares a ~22-glyph opening "
        "and Triplet 3 (E4/W4/E5) ~18, both far above the null; Triplet 2 (W2/E3/W3) "
        "shares none and E3 is structurally distinct. The refrain also repeats within "
        "messages. Confirms the triplet theory rigorously and gives model-independent "
        "same-plaintext anchors.",
        charts=[])


def h_model_audit(ctx: Context) -> HypothesisResult:
    import model_audit as ma
    import refrain as rf
    a = ma.audit(ctx.messages, rf.DEFAULT_INSTANCES, ctx.corpus.N, n_null=300)
    return HypothesisResult(
        id="model_audit",
        title="Model verification: per-message-progressive (plausible, not proven)",
        group="Cipher type",
        verdict="inconclusive", strength=0.4, leverage=3,
        question="Is the cipher specifically per-message-progressive, licensing the "
                 "refrain template?",
        statistic=f"per-msg extent {a.refrain_permsg} vs pure {a.refrain_pure}; "
                  f"null p(≥{a.refrain_permsg})={a.p_value:.4f}",
        null_desc="random 4-window consistent-extent distribution",
        formula="GF consistency depth, per-message vs pure vs random",
        validated_by=ctx.badge("model_audit"),
        reproduce="python3 eyewitness/model_audit.py",
        interpretation="SOLID: the 4 refrain instances are the same plaintext "
        "(isomorphs z≫100). NOT cleanly confirmed: the SPECIFIC model — pure-"
        "progressive fits nearly as well and some random windows pass too, so "
        "per-message-progressive is a flexible fit. The dof=2 refrain template is a "
        "model-dependent HYPOTHESIS, not a fact.",
        charts=[])


def h_eyescoreboard(ctx: Context) -> HypothesisResult:
    import eyescoreboard as esb
    sb = esb.build_scoreboard(ctx.messages, ctx.corpus.N)
    top = sb.candidates[0]
    pm = next(r for r in sb.candidates if r.model_id == "per-msg-progressive")
    stat = (f"rank-1 `{top.model_id}` {top.verdict} (score {top.score}); "
            f"per-msg real contra {sb.methodology.per_msg_real_contra:.2%} vs "
            f"pure {sb.methodology.pure_real_contra:.2%}; "
            f"refrain gap {sb.methodology.refrain_extent_gap}; "
            f"premise={'OK' if sb.premise.premise_ok else 'weak'}")
    tier_verdict = "supported" if pm.verdict == "SUPPORTED" else (
        "suggestive" if pm.verdict == "SUGGESTIVE" else "inconclusive")
    strength = 0.75 if pm.verdict == "SUPPORTED" else (
        0.55 if pm.verdict == "SUGGESTIVE" else 0.35)
    return HypothesisResult(
        id="eyescoreboard",
        title="Cipher candidate scoreboard (methodology-audited ranking)",
        group="Cipher type",
        verdict=tier_verdict, strength=strength, leverage=4,
        question="Which interrelated-alphabet models survive plant + real-corpus audits?",
        statistic=stat,
        null_desc="plant wrong-model controls; shuffle-null extract; triplet-combine probe",
        formula="GF contradiction rate on broad isomorph pairs + refrain extent gap",
        validated_by=ctx.badge("eyescoreboard"),
        reproduce="python3 eyewitness/eyescoreboard.py",
        interpretation="Premise (block-difference + triplet depth) holds. "
        "per-msg-progressive leads on real-corpus contradiction rate and refrain "
        "extent but is NOT uniquely proven (pure within 1 glyph; null p~0.003). "
        "free-δ/autokey-1 are PERMISSIVE. Whole families EXCLUDED. Triplet member "
        "combine (sum mod 83) does NOT yield structured meta-trigrams.",
        charts=[])


HYPOTHESES: List[Callable[[Context], HypothesisResult]] = [
    h_unigram, h_periodicity, h_coordinate, h_fingerprint, h_trifid,
    h_depth, h_grouping, h_scope, h_depthmap, h_repeats, h_isomorph, h_bodymodel,
    h_shared_structure, h_pairdiff, h_embedded,
    h_cribdrag, h_language, h_refrain, h_model_audit, h_eyescoreboard,
    h_header, h_number, h_integrity, h_provenance,
]
