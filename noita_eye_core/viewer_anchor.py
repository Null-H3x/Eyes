"""Isomorph Viewer pattern → anchor candidacy pipeline (steps 1–2).

Replicates the tomster12/isomorph-viewer discovery filters on the Eyes corpus,
then classifies each pattern's instance pairs against the contamination-resistant
``chain_extract`` consensus alphabet (per-message-progressive model).

Outputs a ranked anchor-candidacy report: which viewer patterns are trustworthy
same-plaintext sites vs skeleton-only / contaminated hits.

Viewer defaults (matches https://tomster12.github.io/isomorph-viewer/):
  max_length=30, min_values=2, shared_sections=False, remove_overlaps=False
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import chain_extract as ce
import chain_models as cm
import refrain as rf
from isomorph import IsoPair


@dataclass
class ViewerPattern:
    pattern: str
    length: int
    instances: List[Tuple[int, int]]
    score: float
    n_instances: int
    n_letter_classes: int
    n_distinct_sequences: int
    clean_pairs: int
    total_pairs: int
    clean_ratio: float
    redundant_pairs: int
    redundant_ratio: float
    tier: str
    refrain_overlap: int
    on_clean_maximal: bool
    nested_in: Optional[str] = None
    anchor_score: float = 0.0


def pattern_from_sequence(sequence: Sequence[int]) -> str:
    """Viewer/Javascript repeat-pattern (A/B/C for repeats, '.' for singletons)."""
    letter_counts: Dict[int, int] = {}
    for v in sequence:
        letter_counts[int(v)] = letter_counts.get(int(v), 0) + 1
    letter_mapping: Dict[int, str] = {}
    out: List[str] = []
    for v in sequence:
        v = int(v)
        if letter_counts[v] > 1 and v not in letter_mapping:
            letter_mapping[v] = chr(65 + len(letter_mapping))
        out.append(letter_mapping.get(v, "."))
    return "".join(out)


def _viewer_sequence_ok(sequence: Sequence[int]) -> bool:
    if len(sequence) < 2:
        return False
    if sequence[0] == sequence[-1]:
        return True
    inner = sequence[1:-1]
    found_start = any(v == sequence[0] for v in inner)
    found_end = any(v == sequence[-1] for v in inner)
    return found_start and found_end


def _viewer_group_score(pattern: str, n_instances: int, total_message_length: int,
                        n_messages: int, alphabet_size: int) -> float:
    used: set = set()
    internal = 0
    for ch in pattern:
        if ch == ".":
            continue
        if ch not in used:
            used.add(ch)
        else:
            internal += 1
    if internal <= 1:
        return 0.0
    iso_prob = 1 / (alphabet_size ** internal)
    trial_count = total_message_length - n_messages * len(pattern)
    total_prob = 0.0
    last = 0.0
    for occ in range(n_instances, n_instances + 30):
        # n choose k (JS choose())
        k = occ
        n = trial_count
        if k > n // 2:
            k = n - k
        comb = 1.0
        for i in range(1, k + 1):
            comb *= (n - i + 1) / i
        total_prob += comb * ((1 - iso_prob) ** (trial_count - occ)) * (iso_prob ** occ)
        if total_prob == last:
            break
        last = total_prob
    return -math.log10(max(total_prob, 1e-300))


def discover_viewer_patterns(
    messages: Sequence[Sequence[int]],
    *,
    max_length: int = 30,
    min_values: int = 2,
    allow_shared_sections: bool = False,
    remove_overlaps: bool = False,
    alphabet_size: int = 83,
) -> Dict[str, List[Tuple[int, int]]]:
    """Return pattern -> [(message, pos), ...] under viewer default filters."""
    raw: Dict[str, List[Tuple[int, int]]] = {}
    for pl in range(2, max_length + 1):
        for mi, msg in enumerate(messages):
            for pos in range(len(msg) - pl + 1):
                seq = msg[pos:pos + pl]
                if not _viewer_sequence_ok(seq):
                    continue
                pat = pattern_from_sequence(seq)
                raw.setdefault(pat, []).append((mi, pos))

    out: Dict[str, List[Tuple[int, int]]] = {}
    for pat, inst in raw.items():
        letters = {ch for ch in pat if ch != "."}
        if len(letters) < min_values:
            continue
        if len(inst) < 2:
            continue
        if not allow_shared_sections:
            seqs = {tuple(messages[m][p:p + len(pat)]) for m, p in inst}
            if len(seqs) < 2:
                continue
        if remove_overlaps:
            inst = _remove_overlaps(inst, len(pat))
            if len(inst) < 2:
                continue
        out[pat] = inst
    return out


def _remove_overlaps(instances: List[Tuple[int, int]], length: int
                     ) -> List[Tuple[int, int]]:
    by_msg: Dict[int, List[Tuple[int, int]]] = {}
    for mi, pos in instances:
        by_msg.setdefault(mi, []).append((mi, pos))
    filtered: List[Tuple[int, int]] = []
    for insts in by_msg.values():
        insts.sort(key=lambda x: x[1])
        last_end = -1
        for mi, pos in insts:
            end = pos + length
            if pos >= last_end:
                filtered.append((mi, pos))
                last_end = end
    return filtered


def _instance_pairs(instances: Sequence[Tuple[int, int]], length: int
                    ) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
    pairs: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []
    for i in range(len(instances)):
        for j in range(i + 1, len(instances)):
            pairs.append((instances[i], instances[j]))
    return pairs


def _iso_pair(messages, a: Tuple[int, int], b: Tuple[int, int], length: int) -> IsoPair:
    m1, p1 = a
    m2, p2 = b
    seg_a = tuple(messages[m1][p1:p1 + length])
    seg_b = tuple(messages[m2][p2:p2 + length])
    return IsoPair(m1, p1, m2, p2, length, exact=(seg_a == seg_b))


def classify_pattern_pairs(
    messages: Sequence[Sequence[int]],
    instances: Sequence[Tuple[int, int]],
    length: int,
    gf,
    *,
    N: int = 83,
) -> Tuple[int, int, int]:
    """Return (consistent_pairs, redundant_pairs, total_pairs).

    * consistent — no ``contradiction`` under per-msg-progressive GF
    * redundant — every constraint row already implied (strongest; chain_extract clean)
    """
    rows_fn = cm.per_msg_prog_rows
    total = 0
    consistent = 0
    redundant = 0
    for a, b in _instance_pairs(instances, length):
        pr = _iso_pair(messages, a, b, length)
        total += 1
        rows = list(rows_fn(pr, messages, N))
        if not rows:
            continue
        status = "redundant"
        for row, rhs in rows:
            cls = gf.classify(row, rhs)
            if cls == "contradiction":
                status = "contradiction"
                break
            if cls != "redundant":
                status = "consistent"
        if status == "contradiction":
            continue
        consistent += 1
        if status == "redundant":
            redundant += 1
    return consistent, redundant, total


def _clean_maximal_windows(messages, clean_pairs: Sequence[IsoPair]
                           ) -> List[Tuple[int, int, int]]:
    """List (message, start, length) spans covered by extractor clean pairs."""
    spans: List[Tuple[int, int, int]] = []
    for pr in clean_pairs:
        spans.append((pr.m1, pr.p1, pr.length))
        spans.append((pr.m2, pr.p2, pr.length))
    return spans


def _on_clean_span(m: int, pos: int, length: int,
                   spans: Sequence[Tuple[int, int, int]]) -> bool:
    end = pos + length
    for sm, sp, sl in spans:
        if sm == m and sp <= pos and end <= sp + sl:
            return True
    return False


def _refrain_overlap(instances: Sequence[Tuple[int, int]], length: int,
                     margin: int = 2) -> int:
    ref = rf.DEFAULT_INSTANCES
    ref_end = {m: p + rf.DEFAULT_LEN for m, p in ref}
    count = 0
    for m, pos in instances:
        for rm, rp in ref:
            if m != rm:
                continue
            if abs(pos - rp) <= margin or (pos + length >= rp - margin and
                                           pos <= ref_end[rm] + margin):
                count += 1
                break
    return count


def _assign_tier(n_inst: int, consistent_ratio: float, redundant_ratio: float,
                 on_clean: bool, refrain_ov: int) -> str:
    if consistent_ratio < 1.0:
        return "CONTAMINATED" if consistent_ratio == 0 else "PARTIAL"
    if on_clean and redundant_ratio >= 1.0 and n_inst >= 4:
        return "CERTIFIED"
    if redundant_ratio >= 1.0 and n_inst >= 3:
        return "PROMISING"
    if consistent_ratio >= 1.0 and n_inst >= 4 and refrain_ov >= 2:
        return "LIKELY"
    if consistent_ratio >= 1.0 and n_inst >= 3:
        return "LIKELY"
    if refrain_ov >= 2:
        return "REFRAIN-ADJ"
    return "PARTIAL"


def _anchor_score(p: ViewerPattern) -> float:
    tier_w = {"CERTIFIED": 1000, "PROMISING": 500, "LIKELY": 200,
              "REFRAIN-ADJ": 150, "PARTIAL": 50, "CONTAMINATED": 0,
              "NESTED": -100}
    return (tier_w.get(p.tier, 0)
            + p.score * 10
            + p.length * 2
            + p.n_instances * 5
            + p.clean_ratio * 100
            + p.redundant_ratio * 50
            + p.refrain_overlap * 20
            + (50 if p.on_clean_maximal else 0))


def rank_viewer_patterns(
    messages: Sequence[Sequence[int]],
    patterns: Optional[Dict[str, List[Tuple[int, int]]]] = None,
    *,
    extract_result: Optional[ce.ExtractResult] = None,
    max_length: int = 30,
    min_values: int = 2,
    allow_shared_sections: bool = False,
    remove_overlaps: bool = False,
    N: int = 83,
) -> List[ViewerPattern]:
    if patterns is None:
        patterns = discover_viewer_patterns(
            messages, max_length=max_length, min_values=min_values,
            allow_shared_sections=allow_shared_sections,
            remove_overlaps=remove_overlaps, alphabet_size=N)
    if extract_result is None:
        extract_result = ce.extract(messages, base_len=13, broad_repeats=3, N=N)
    gf = extract_result._gf
    assert gf is not None

    total_len = sum(len(m) for m in messages)
    clean_spans = _clean_maximal_windows(messages, extract_result.clean_pairs)
    ranked: List[ViewerPattern] = []

    for pat, inst in patterns.items():
        L = len(pat)
        # Verify every instance reproduces the pattern string
        for m, p in inst:
            assert pattern_from_sequence(messages[m][p:p + L]) == pat

        seqs = {tuple(messages[m][p:p + L]) for m, p in inst}
        consistent, redundant, total = classify_pattern_pairs(messages, inst, L, gf, N=N)
        cr = consistent / total if total else 0.0
        rr = redundant / total if total else 0.0
        on_clean = all(_on_clean_span(m, p, L, clean_spans) for m, p in inst)
        ref_ov = _refrain_overlap(inst, L)
        tier = _assign_tier(len(inst), cr, rr, on_clean, ref_ov)
        vp = ViewerPattern(
            pattern=pat,
            length=L,
            instances=list(inst),
            score=_viewer_group_score(pat, len(inst), total_len, len(messages), N),
            n_instances=len(inst),
            n_letter_classes=len({ch for ch in pat if ch != "."}),
            n_distinct_sequences=len(seqs),
            clean_pairs=consistent,
            total_pairs=total,
            clean_ratio=cr,
            redundant_pairs=redundant,
            redundant_ratio=rr,
            tier=tier,
            refrain_overlap=ref_ov,
            on_clean_maximal=on_clean,
        )
        vp.anchor_score = _anchor_score(vp)
        ranked.append(vp)

    ranked.sort(key=lambda p: (-p.anchor_score, -p.score, -p.length))

    # Mark nested patterns (strict substring of a higher-ranked pattern's string)
    for i, parent in enumerate(ranked):
        for child in ranked[i + 1:]:
            if child.pattern in parent.pattern and child.pattern != parent.pattern:
                if child.nested_in is None:
                    child.nested_in = parent.pattern
                    if child.tier not in ("CERTIFIED", "PROMISING"):
                        child.tier = "NESTED"
                        child.anchor_score = _anchor_score(child)

    ranked.sort(key=lambda p: (-p.anchor_score, -p.score, -p.length))
    return ranked


def render_report(
    ranked: Sequence[ViewerPattern],
    labels: Sequence[str],
    *,
    max_rows: int = 0,
) -> str:
    lines = [
        "# Isomorph Viewer → anchor candidacy report",
        "",
        "*Reproduce: `python3 eyewitness/viewer_anchor.py`. "
        "Classifies viewer patterns via `chain_extract` consensus GF.*",
        "",
        "| rank | tier | pattern | L | inst | clean | score | refrain | notes |",
        "|---:|---|---|---:|---:|---:|---:|---:|---|",
    ]
    rows = list(ranked) if max_rows <= 0 else list(ranked)[:max_rows]
    for i, p in enumerate(rows, 1):
        clean = f"{p.clean_pairs}/{p.total_pairs}"
        notes = []
        if p.on_clean_maximal:
            notes.append("on clean maximal")
        if p.nested_in:
            notes.append(f"nested in `{p.nested_in[:12]}…`" if len(p.nested_in) > 12
                         else f"nested in `{p.nested_in}`")
        locs = ", ".join(f"{labels[m]}@{pos}" for m, pos in p.instances[:4])
        if len(p.instances) > 4:
            locs += f", +{len(p.instances) - 4}"
        lines.append(
            f"| {i} | {p.tier} | `{p.pattern}` | {p.length} | {len(p.instances)} | "
            f"{clean} | {p.score:.1f} | {p.refrain_overlap} | {locs} |")
    lines.append("")
    tier_counts: Dict[str, int] = {}
    for p in ranked:
        tier_counts[p.tier] = tier_counts.get(p.tier, 0) + 1
    lines.append("## Tier summary")
    lines.append("")
    for tier in ("CERTIFIED", "PROMISING", "LIKELY", "REFRAIN-ADJ",
                 "PARTIAL", "CONTAMINATED", "NESTED"):
        if tier in tier_counts:
            lines.append(f"- **{tier}**: {tier_counts[tier]}")
    lines.append("")
    return "\n".join(lines)


def run_paranoia_audit(messages, labels: Sequence[str], N: int = 83
                       ) -> List[Tuple[str, bool]]:
    out: List[Tuple[str, bool]] = []
    patterns = discover_viewer_patterns(messages, alphabet_size=N)
    out.append(("viewer defaults yield 61 patterns on real corpus",
                len(patterns) == 61))

    ranked = rank_viewer_patterns(messages, patterns, N=N)
    out.append(("ranked count matches discovered", len(ranked) == len(patterns)))
    out.append(("ranking monotonic by anchor_score",
                all(ranked[i].anchor_score >= ranked[i + 1].anchor_score
                    for i in range(len(ranked) - 1))))

    for p in ranked:
        for m, pos in p.instances:
            ok = 0 <= m < len(messages) and 0 <= pos and pos + p.length <= len(messages[m])
            out.append((f"bounds: {p.pattern[:10]}… @{labels[m]}@{pos}", ok))
            sk_ok = pattern_from_sequence(messages[m][pos:pos + p.length]) == p.pattern
            out.append((f"pattern string matches instance {p.pattern[:8]}…", sk_ok))

    out.append(("at least one CERTIFIED or PROMISING pattern",
                any(p.tier in ("CERTIFIED", "PROMISING") for p in ranked)))
    out.append(("top pattern has 4 instances",
                len(ranked[0].instances) == 4 if ranked else False))
    out.append(("top pattern overlaps refrain region",
                ranked[0].refrain_overlap >= 2 if ranked else False))

    extract = ce.extract(messages, N=N)
    gf = extract._gf
    out.append(("extract GF available", gf is not None))

    # Pair math: sum of n*(n-1)/2 matches classify totals
    pair_sum = sum(p.total_pairs for p in ranked)
    expected = sum(len(p.instances) * (len(p.instances) - 1) // 2 for p in ranked)
    out.append(("total pair counts consistent", pair_sum == expected))

    # Symmetry: classify(a,b) == classify(b,a) — IsoPair is ordered but GF symmetric
    if ranked:
        top = ranked[0]
        a, b = top.instances[0], top.instances[1]
        pr1 = _iso_pair(messages, a, b, top.length)
        pr2 = _iso_pair(messages, b, a, top.length)
        c1 = ce._redundant(gf, pr1, messages, cm.per_msg_prog_rows, N)
        c2 = ce._redundant(gf, pr2, messages, cm.per_msg_prog_rows, N)
        out.append(("classification symmetric on top pattern pair", c1 == c2))

    # refrain certified target: all pairs clean at DEFAULT_LEN windows
    ref_inst = rf.DEFAULT_INSTANCES
    ref_pat = pattern_from_sequence(
        messages[ref_inst[0][0]][ref_inst[0][1]:ref_inst[0][1] + rf.DEFAULT_LEN])
    ref_cons, ref_red, ref_total = classify_pattern_pairs(
        messages, ref_inst, rf.DEFAULT_LEN, gf, N=N)
    out.append(("refrain 4x all pairs consistent under extract GF",
                ref_cons == ref_total and ref_total == 6))
    out.append(("refrain 4x has no redundant-only classification at L=22",
                ref_red < ref_total))

    report = render_report(ranked, labels)
    out.append(("render_report non-empty", len(report) > 200))

    return out


def selftest() -> List[Tuple[str, bool]]:
    import numpy as np

    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(7)
    C = list(rng.permutation(N))
    bases = [int(b) for b in rng.integers(0, N, size=2)]

    # Plant: 3 aligned instances, same plaintext (direct classification test)
    L0 = 14
    vals = [int(v) for v in rng.permutation(N)[:L0]]
    vals[4] = (vals[1] + (1 - 4)) % N
    vals[9] = (vals[3] + (3 - 9)) % N
    region = [(0, 20), (0, 45), (1, 30)]
    T = 80
    msgs = [[], []]
    for m in range(2):
        p = [int(rng.integers(0, N)) for _ in range(T)]
        for mm, pos in region:
            if mm == m:
                p[pos:pos + L0] = vals
        msgs[m] = [C[(p[t] + bases[m] + t) % N] for t in range(T)]

    extract = ce.extract(msgs, base_len=min(13, L0 - 1), broad_repeats=2, N=N)
    gf = extract._gf
    assert gf is not None
    cons, red, tot = classify_pattern_pairs(msgs, region, L0, gf, N=N)
    out.append(("plant: all instance pairs consistent",
                tot == 3 and cons == 3))
    out.append(("plant: at least one pair fully redundant",
                red >= 1))

    out.append(("tier: CONTAMINATED when no consistent pairs",
                _assign_tier(4, 0.0, 0.0, False, 0) == "CONTAMINATED"))
    out.append(("tier: LIKELY when all consistent, 4 instances",
                _assign_tier(4, 1.0, 0.0, False, 0) == "LIKELY"))

    # GF classify sanity (isomorph KAT edge)
    from isomorph import GFSystem
    gfk = GFSystem(N)
    gfk.add({0: 1, 1: N - 1}, 5)
    out.append(("classify: identical row is redundant",
                gfk.classify({0: 1, 1: N - 1}, 5) == "redundant"))
    out.append(("classify: same LHS different RHS contradicts",
                gfk.classify({0: 1, 1: N - 1}, 6) == "contradiction"))

    # Viewer sequence gate rejects random short windows mostly
    random_hits = 0
    for _ in range(50):
        seq = [int(rng.integers(0, N)) for _ in range(8)]
        if _viewer_sequence_ok(seq):
            random_hits += 1
    out.append(("sequence gate rejects most random 8-grams", random_hits < 10))

    # Real corpus
    import corpus as corpus_mod
    c = corpus_mod.load()
    M = [list(x) for x in c.ciphertexts]
    out.extend(run_paranoia_audit(M, c.labels, c.N))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} viewer_anchor checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
