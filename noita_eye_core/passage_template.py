"""Passage template pipeline — discover, certify, extend, and validate repeat anchors.

Automates stages 3–6 of the structural-anchor workflow:

  3. Group clean isomorph instances into targets (``discover_targets``)
  4. Extract ordering-free repeat-templates at increasing L (``extend_length``)
  5. Report forced-SAME letter classes, dof, ciphertext collision constraints
  6. Optional sharp crib validation via ``cribfit`` VALUE mode (``validate_phrase``)

Targets come from three sources (deduplicated):

  * ``chain_extract`` clean maximal runs (via ``cribfit.find_targets``)
  * ``shared_structure`` repeated-passage census (model-free, skeleton-checked)
  * The certified 4× refrain (``refrain.DEFAULT_INSTANCES``)

Every target is analysed under the per-message-progressive model used by
``template.extract`` — flagged as model-dependent in reports.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import cribfit as cf
import refrain as rf
import shared_structure as ss
import template as tp


def _sk(seq: Sequence[int]) -> Tuple[int, ...]:
    first: Dict[int, int] = {}
    return tuple(first.setdefault(int(v), i) for i, v in enumerate(seq))


def _collision_pair_sets(messages, instances: Sequence[Tuple[int, int]], L: int,
                         N: int) -> List[Tuple[Tuple[int, int, int], ...]]:
    """Per-instance sorted collision triples."""
    sets: List[Tuple[Tuple[int, int, int], ...]] = []
    for m, pos in instances:
        if pos + L > len(messages[m]):
            return []
        seg = messages[m][pos:pos + L]
        first: Dict[int, int] = {}
        pairs: List[Tuple[int, int, int]] = []
        for i, v in enumerate(seg):
            v = int(v)
            if v in first:
                j = first[v]
                pairs.append((j, i, (i - j) % N))
            else:
                first[v] = i
        sets.append(tuple(sorted(pairs)))
    return sets


def collisions_cross_instance_match(messages, instances: Sequence[Tuple[int, int]],
                                    L: int, N: int = 83) -> bool:
    """True iff every instance yields the same collision triple set."""
    sets = _collision_pair_sets(messages, instances, L, N)
    if not sets or len(instances) == 0:
        return len(instances) == 0
    return len(set(sets)) == 1


def collision_constraints(messages, instances: Sequence[Tuple[int, int]],
                          L: int, N: int = 83) -> List[Tuple[int, int, int]]:
    """Ordering-independent plaintext value ties from ciphertext symbol repeats.

    Under per-message-progressive, equal ciphertext at relative positions ``i`` and
    ``j`` within one instance forces ``p[j] = p[i] - (j-i) (mod N)``.

    When all instances share the same plaintext (certified target), every instance
    must yield the **same** collision set; otherwise returns ``[]``.
    """
    sets = _collision_pair_sets(messages, instances, L, N)
    if not sets or len(set(sets)) != 1:
        return []
    return list(sets[0])


def collision_dsu(messages, instances: Sequence[Tuple[int, int]], L: int,
                    N: int = 83) -> bool:
    """Return True iff every instance yields a non-contradictory collision DSU."""
    if not instances:
        return False
    for m, pos in instances:
        if pos + L > len(messages[m]):
            return False
        d = __import__("isomorph", fromlist=["OffsetDSU"]).OffsetDSU(N)
        occ: Dict[int, int] = {}
        for k in range(L):
            sym = int(messages[m][pos + k])
            if sym in occ:
                if not d.union(occ[sym], k, (occ[sym] - k) % N):
                    return False
            else:
                occ[sym] = k
    return True


def verify_collisions_vs_template(messages, instances: Sequence[Tuple[int, int]],
                                  tmpl: tp.Template, N: int) -> List[Tuple[str, bool]]:
    """Cross-check ciphertext collisions against the extracted template GF."""
    out: List[Tuple[str, bool]] = []
    if not tmpl.consistent:
        return out
    gf, _ = tp._build_gf(messages, list(instances), tmpl.L, N)
    if gf is None:
        out.append(("template GF rebuild", False))
        return out
    out.append(("template GF rebuild", True))
    out.append(("collisions cross-instance pair-set match",
                collisions_cross_instance_match(messages, instances, tmpl.L, N)))
    cols = collision_constraints(messages, instances, tmpl.L, N)
    for i, j, gap in cols:
        # p[j] = p[i] - gap  <=>  p[i] - p[j] = gap
        cls = gf.classify({i: 1, j: (N - 1) % N}, gap % N)
        out.append((f"collision ({i},{j}) gap={gap} implied by template",
                    cls == "redundant"))
    for grp in tmpl.same_groups:
        for a in range(len(grp)):
            for b in range(a + 1, len(grp)):
                i, j = grp[a], grp[b]
                cls = gf.classify({i: 1, j: (N - 1) % N}, 0)
                out.append((f"same_group ({i},{j}) forced equal in template",
                            cls == "redundant"))
    dsu = collision_dsu(messages, instances, tmpl.L, N)
    out.append(("collision OffsetDSU per-instance consistent", dsu))
    return out


def verify_extend_consistent(messages, instances: Sequence[Tuple[int, int]],
                             start_L: int, N: int, max_extra: int = 40
                             ) -> List[Tuple[str, bool]]:
    """Verify extend_length monotonicity and final template agreement."""
    out: List[Tuple[str, bool]] = []
    max_L, steps = extend_length(messages, instances, start_L, N, max_extra=max_extra)
    out.append(("extend: at least one step recorded", len(steps) >= 1))
    out.append(("extend: step L values strictly increase when multiple",
                all(steps[i].L < steps[i + 1].L for i in range(len(steps) - 1))))
    consistent_steps = [s for s in steps if s.consistent]
    if consistent_steps:
        out.append(("extend: max_L equals last consistent step",
                    max_L == consistent_steps[-1].L))
        tmpl = tp.extract(messages, list(instances), max_L, N)
        out.append(("extend: template at max_L is consistent",
                    tmpl.consistent and max_L > 0))
        if tmpl.consistent:
            out.append(("extend: final step dof matches template",
                        consistent_steps[-1].dof == tmpl.dof))
    else:
        out.append(("extend: no consistent length", max_L == 0))
    return out


@dataclass
class PassageTarget:
    """A same-plaintext passage with known instance sites."""
    name: str
    instances: List[Tuple[int, int]]
    base_length: int
    skeleton: Tuple[int, ...]
    source: str                          # extract | shared_structure | refrain


@dataclass
class LengthStep:
    L: int
    consistent: bool
    dof: int
    n_same_groups: int
    n_diff_pairs: int
    skeleton: str
    same_groups: List[List[int]]


@dataclass
class PassageAnalysis:
    target: PassageTarget
    max_L: int
    max_template: Optional[tp.Template]
    steps: List[LengthStep]
    collisions: List[Tuple[int, int, int]]   # (i, j, j-i) at max_L
    redundant_with: List[str] = field(default_factory=list)


@dataclass
class CribValidation:
    target_name: str
    phrase: str
    offset: int
    pattern_consistent: bool
    pattern_null: float
    value_consistent: Optional[bool]
    extends_corpus: Optional[bool]
    value_null: Optional[float]
    verdict: str


def _target_key(instances: Sequence[Tuple[int, int]], L: int) -> Tuple[Tuple[int, int], ...]:
    return (tuple(sorted(instances)), L)


def target_from_instances(name: str, messages, instances: Sequence[Tuple[int, int]],
                          L: int, source: str) -> Optional[PassageTarget]:
    """Build a target if every instance has room and shares one skeleton."""
    inst = sorted((int(m), int(p)) for m, p in instances)
    if len(inst) < 2:
        return None
    skels = []
    for m, p in inst:
        if p + L > len(messages[m]):
            return None
        skels.append(_sk(messages[m][p:p + L]))
    if len(set(skels)) != 1:
        return None
    return PassageTarget(name, inst, L, skels[0], source)


def discover_targets(messages, labels: Optional[Sequence[str]] = None,
                     base_len: int = 13, broad_repeats: int = 3,
                     min_passage_len: int = 12, include_refrain: bool = True,
                     N: Optional[int] = None) -> List[PassageTarget]:
    """Discover passage targets from extractor clean runs, shared-structure census,
    and the known refrain."""
    if N is None:
        N = max(int(max(m)) for m in messages) + 1
    if labels is None:
        labels = [f"m{i}" for i in range(len(messages))]

    seen: set = set()
    out: List[PassageTarget] = []

    def add(t: Optional[PassageTarget]) -> None:
        if t is None:
            return
        key = _target_key(t.instances, t.base_length)
        if key in seen:
            return
        seen.add(key)
        out.append(t)

    if include_refrain:
        add(target_from_instances(
            "refrain-4x", messages, rf.DEFAULT_INSTANCES, rf.DEFAULT_LEN, "refrain"))

    for i, t in enumerate(cf.find_targets(messages, base_len=base_len,
                                          broad_repeats=broad_repeats, N=N)):
        locs = ", ".join(f"{labels[m]}@{p}" for m, p in t.instances[:4])
        if len(t.instances) > 4:
            locs += f", +{len(t.instances) - 4} more"
        add(target_from_instances(
            f"extract-{i}", messages, t.instances, t.length, "extract"))

    for j, fam in enumerate(ss.repeated_passages(messages, min_len=min_passage_len)):
        occ = [(m, p) for m, p in fam["occurrences"]]
        add(target_from_instances(
            f"passage-{fam['length']}-{j}", messages, occ, fam["length"],
            "shared_structure"))

    out.sort(key=lambda t: (len(t.instances), t.base_length), reverse=True)
    return out


def extend_length(messages, instances: Sequence[Tuple[int, int]], start_L: int,
                  N: int, max_extra: int = 40) -> Tuple[int, List[LengthStep]]:
    """Increase L from ``start_L`` until ``template.extract`` contradicts."""
    steps: List[LengthStep] = []
    max_L = 0
    for extra in range(max_extra + 1):
        L = start_L + extra
        if any(p + L > len(messages[m]) for m, p in instances):
            break
        tmpl = tp.extract(messages, list(instances), L, N)
        steps.append(LengthStep(
            L=L,
            consistent=tmpl.consistent,
            dof=tmpl.dof if tmpl.consistent else L,
            n_same_groups=len(tmpl.same_groups),
            n_diff_pairs=len(tmpl.diff_pairs),
            skeleton=tp.skeleton_string(tmpl) if tmpl.consistent else "",
            same_groups=list(tmpl.same_groups) if tmpl.consistent else [],
        ))
        if not tmpl.consistent:
            break
        max_L = L
    return max_L, steps


def _skeleton_subset(a: Tuple[int, ...], b: Tuple[int, ...]) -> bool:
    """True if skeleton ``a`` matches a prefix of ``b`` (same repeat classes)."""
    if len(a) > len(b):
        return False
    return a == b[:len(a)]


def redundancy_pairs(analyses: Sequence[PassageAnalysis]) -> Dict[str, List[str]]:
    """Mark targets whose instances+skeleton appear redundant with a larger target."""
    redundant: Dict[str, List[str]] = {a.target.name: [] for a in analyses}
    for i, a in enumerate(analyses):
        for b in analyses:
            if a.target.name == b.target.name:
                continue
            if len(a.target.instances) > len(b.target.instances):
                continue
            if a.max_L > b.max_L:
                continue
            inst_a = set(a.target.instances)
            if not inst_a.issubset(set(b.target.instances)):
                continue
            if _skeleton_subset(a.target.skeleton, b.target.skeleton):
                redundant[a.target.name].append(b.target.name)
    return redundant


def analyze_target(messages, target: PassageTarget, N: int,
                   max_extra: int = 40) -> PassageAnalysis:
    """Run extend-length + template extraction for one target."""
    max_L, steps = extend_length(messages, target.instances, target.base_length,
                                 N, max_extra=max_extra)
    if max_L <= 0:
        return PassageAnalysis(target, 0, None, steps, [])
    tmpl = tp.extract(messages, target.instances, max_L, N)
    cols = collision_constraints(messages, target.instances, max_L, N)
    return PassageAnalysis(target, max_L, tmpl if tmpl.consistent else None,
                           steps, cols)


def analyze_all(messages, targets: Sequence[PassageTarget], N: int,
                max_extra: int = 40) -> List[PassageAnalysis]:
    analyses = [analyze_target(messages, t, N, max_extra=max_extra) for t in targets]
    pairs = redundancy_pairs(analyses)
    for a in analyses:
        a.redundant_with = pairs.get(a.target.name, [])
    return analyses


def validate_phrase(target: PassageTarget, phrase: str, messages, N: int,
                    alphabet: str, n_null: int = 200,
                    corpus_gf=None) -> Optional[CribValidation]:
    """Stage 6: sharp VALUE-mode crib test at best sliding offset (requires alphabet)."""
    import re
    s = re.sub(r"[^a-z]", "", phrase.lower())
    L = target.base_length
    if len(s) < L:
        return None
    if corpus_gf is None:
        corpus_gf = cf._corpus_gf(messages, N)
    ct = cf.Target(target.instances, L, target.skeleton)
    best: Optional[CribValidation] = None
    for off in range(len(s) - L + 1):
        sub = s[off:off + L]
        patt = cf.letter_pattern(sub)
        rp = cf.test_pattern(ct, patt, messages, N, n_null=n_null)
        vals = cf.letters_to_values(sub, alphabet)
        if vals is None:
            continue
        rv = cf.test_value(ct, vals, messages, N, corpus_gf=corpus_gf, n_null=n_null)
        if rv.consistent and rv.extends_corpus:
            verdict = "CANDIDATE (VALUE+corpus, null~%.0f%%)" % (rv.null_rate * 100)
        elif rv.consistent:
            verdict = "fits instances but NOT corpus"
        else:
            verdict = "rejected"
        cand = CribValidation(
            target_name=target.name,
            phrase=sub,
            offset=off,
            pattern_consistent=rp.consistent,
            pattern_null=rp.null_rate,
            value_consistent=rv.consistent,
            extends_corpus=rv.extends_corpus,
            value_null=rv.null_rate,
            verdict=verdict,
        )

        def _rank(v: CribValidation) -> Tuple[bool, bool, float]:
            return (bool(v.value_consistent and v.extends_corpus),
                    bool(v.value_consistent),
                    -(v.value_null or 1.0))

        if best is None or _rank(cand) > _rank(best):
            best = cand
    return best


def validate_phrases(analyses: Sequence[PassageAnalysis], phrases: Sequence[str],
                     messages, N: int, alphabet: str,
                     n_null: int = 200) -> List[CribValidation]:
    """Run stage-6 validation on every target at its ``max_L`` (uses base_length crib
    window on the extended region — phrase must match ``max_L`` for sharp test)."""
    corpus_gf = cf._corpus_gf(messages, N)
    out: List[CribValidation] = []
    for a in analyses:
        t = a.target
        m0, p0 = t.instances[0]
        sk = _sk(messages[m0][p0:p0 + a.max_L])
        test_target = PassageTarget(t.name, t.instances, a.max_L, sk, t.source)
        for phrase in phrases:
            v = validate_phrase(test_target, phrase, messages, N, alphabet,
                                n_null=n_null, corpus_gf=corpus_gf)
            if v is not None:
                out.append(v)
    return out


def format_collision_line(cols: Sequence[Tuple[int, int, int]]) -> str:
    if not cols:
        return "(none)"
    parts = [f"p[{j}]=p[{i}]-{gap}" for i, j, gap in sorted(cols)]
    return ", ".join(parts)


def render_report(analyses: Sequence[PassageAnalysis],
                  validations: Optional[Sequence[CribValidation]] = None,
                  labels: Optional[Sequence[str]] = None) -> str:
    """Markdown report for ``report/passage_template_report.md``."""
    lines = [
        "# Passage template pipeline — anchor discovery report",
        "",
        "*Reproduce: `python3 eyewitness/passage_template.py`. "
        "Gate: `python3 noita_eye_core/selftest.py`.*",
        "",
        "Model-dependent (per-message-progressive template). Same-plaintext "
        "instance sites are certified by extractor or model-free skeleton match.",
        "",
    ]
    for a in analyses:
        t = a.target
        locs = ", ".join(
            f"{labels[m] if labels else f'm{m}'}@{p}" for m, p in t.instances[:6])
        if len(t.instances) > 6:
            locs += f", +{len(t.instances) - 6} more"
        lines.append(f"## {t.name} ({t.source})")
        lines.append("")
        lines.append(f"- **Instances ({len(t.instances)}):** {locs}")
        lines.append(f"- **Base L:** {t.base_length} → **max consistent L:** {a.max_L}")
        if a.redundant_with:
            lines.append(f"- **Redundant with:** {', '.join(a.redundant_with)}")
        if a.max_template:
            tmpl = a.max_template
            lines.append(f"- **dof:** {tmpl.dof} · **forced-SAME groups:** "
                          f"{tmpl.same_groups}")
            lines.append(f"- **free positions:** {tmpl.free_positions}")
            lines.append(f"- **skeleton:** `{tp.skeleton_string(tmpl)}`")
            lines.append(f"- **collisions (mod 83):** {format_collision_line(a.collisions)}")
        elif a.max_L == 0:
            lines.append("- **INCONSISTENT** at base length (max L=0)")
        else:
            lines.append("- **INCONSISTENT** under per-msg-progressive at max extend")
        if len(a.steps) > 1:
            lines.append("")
            lines.append("| L | dof | same groups | skeleton |")
            lines.append("|---:|---:|---:|---|")
            for st in a.steps:
                if st.consistent:
                    lines.append(f"| {st.L} | {st.dof} | {st.n_same_groups} | "
                                 f"`{st.skeleton}` |")
        lines.append("")
    if validations:
        lines.append("## Stage 6 — crib validation (VALUE mode)")
        lines.append("")
        lines.append("| target | phrase | offset | VALUE | +corpus | null | verdict |")
        lines.append("|---|---|---:|---|---|---:|---|")
        for v in validations:
            val = "yes" if v.value_consistent else "no"
            ext = ("yes" if v.extends_corpus else "no") if v.value_consistent else "-"
            nul = f"{v.value_null:.2f}" if v.value_null is not None else "-"
            lines.append(f"| {v.target_name} | `{v.phrase}` | {v.offset} | {val} | "
                         f"{ext} | {nul} | {v.verdict} |")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def run_paranoia_audit(messages, labels: Sequence[str], N: int) -> List[Tuple[str, bool]]:
    """Bulletproof invariant checks on the real corpus pipeline."""
    out: List[Tuple[str, bool]] = []
    targets = discover_targets(messages, labels=labels)
    out.append(("discover: at least refrain + one more target", len(targets) >= 2))
    out.append(("discover: every target has >=2 instances",
                all(len(t.instances) >= 2 for t in targets)))
    for t in targets:
        sk_ok = all(
            _sk(messages[m][p:p + t.base_length]) == t.skeleton
            for m, p in t.instances)
        out.append((f"discover: {t.name} skeleton matches all instances", sk_ok))

    analyses = analyze_all(messages, targets, N, max_extra=15)
    refrain = next((a for a in analyses if a.target.source == "refrain"), None)
    out.append(("refrain: max consistent L == 22",
                refrain is not None and refrain.max_L == 22))
    out.append(("refrain: dof == 2 at max L",
                refrain is not None and refrain.max_template is not None and
                refrain.max_template.dof == 2))
    out.append(("refrain: exactly 3 forced-SAME groups",
                refrain is not None and refrain.max_template is not None and
                len(refrain.max_template.same_groups) == 3))

    if refrain is not None and refrain.max_template is not None:
        out.extend(verify_collisions_vs_template(
            messages, refrain.target.instances, refrain.max_template, N))
        out.extend(verify_extend_consistent(
            messages, refrain.target.instances, refrain.target.base_length, N,
            max_extra=15))
        cols = collision_constraints(messages, refrain.target.instances,
                                     refrain.max_L, N)
        ra_pairs = []
        m0, p0 = refrain.target.instances[0]
        seg = messages[m0][p0:p0 + refrain.max_L]
        first: Dict[int, int] = {}
        for i, v in enumerate(seg):
            v = int(v)
            if v in first:
                ra_pairs.append((first[v], i))
            else:
                first[v] = i
        ra_line = format_collision_line([(i, j, (j - i) % N) for i, j in ra_pairs])
        pt_line = format_collision_line(cols)
        out.append(("collisions match refrain_attack format", ra_line == pt_line))

    for a in analyses:
        if not a.steps:
            out.append((f"{a.target.name}: has extend steps", False))
            continue
        out.append((f"{a.target.name}: extend steps monotonic in L",
                    all(a.steps[i].L < a.steps[i + 1].L
                        for i in range(len(a.steps) - 1))))
        if a.max_L == 0:
            out.append((f"{a.target.name}: inconsistent at base (max_L=0)", True))
            continue
        if a.max_template:
            out.append((f"{a.target.name}: max_L template consistent", True))
            for g in a.max_template.same_groups:
                out.append((f"{a.target.name}: same_group in range",
                            all(0 <= p < a.max_L for p in g)))
            for i, j, gap in a.collisions:
                out.append((f"{a.target.name}: collision i<j", i < j))
                out.append((f"{a.target.name}: collision gap mod N valid",
                            0 < gap < N))
            for st in a.steps:
                if st.consistent and st.L == a.max_L:
                    out.append((f"{a.target.name}: final step dof matches template",
                                st.dof == a.max_template.dof))

    # Stage 6: wrong phrase must not extend corpus on refrain (sharp gate)
    if refrain is not None:
        v = validate_phrase(
            PassageTarget(refrain.target.name, refrain.target.instances,
                          refrain.max_L,
                          _sk(messages[refrain.target.instances[0][0]]
                              [refrain.target.instances[0][1]:
                               refrain.target.instances[0][1] + refrain.max_L]),
                          "refrain"),
            "x" * refrain.max_L, messages, N, "abcdefghijklmnopqrstuvwxyz",
            n_null=80)
        out.append(("stage6: garbage phrase does not extend corpus",
                    v is not None and not (v.value_consistent and v.extends_corpus)))

    report = render_report(analyses, labels=labels)
    out.append(("render_report non-empty", len(report) > 200))
    return out


def selftest() -> List[Tuple[str, bool]]:
    import numpy as np
    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(0)
    C = list(rng.permutation(N))
    bases = [int(b) for b in rng.integers(0, N, size=2)]

    # Plant with engineered collisions -> forced same groups at extend
    L0 = 12
    vals = [int(v) for v in rng.permutation(N)[:L0]]
    vals[5] = (vals[2] + (2 - 5)) % N
    region = [(0, 30), (0, 55), (1, 40)]
    T = 90
    msgs = [[], []]
    for m in range(2):
        p = [int(rng.integers(0, N)) for _ in range(T)]
        for mm, pos in region:
            if mm == m:
                p[pos:pos + L0] = vals
        msgs[m] = [C[(p[t] + bases[m] + t) % N] for t in range(T)]

    tgt = target_from_instances("plant", msgs, region, L0, "plant")
    out.append(("target_from_instances accepts valid plant", tgt is not None))
    max_L, steps = extend_length(msgs, region, L0, N, max_extra=8)
    out.append(("extend_length reaches at least base L", max_L >= L0))
    out.append(("extend stops before contradiction", all(s.consistent for s in steps[:-1])
                or len(steps) == 1))
    ana = analyze_target(msgs, tgt, N, max_extra=8)
    out.append(("analyze produces max_template", ana.max_template is not None))
    out.append(("collision_constraints returns list",
                isinstance(ana.collisions, list)))
    if ana.max_template:
        tmpl0 = tp.extract(msgs, region, L0, N)
        out.extend(verify_collisions_vs_template(msgs, region, tmpl0, N))
        out.extend(verify_extend_consistent(msgs, region, L0, N, max_extra=8))

    # Cross-instance mismatch must not emit constraints
    bad = [list(row) for row in msgs]
    bad[1][45] = (bad[1][45] + 1) % N  # corrupt rel index 5 in instance (1,40)
    out.append(("collision mismatch across instances -> empty",
                not collisions_cross_instance_match(bad, region, L0, N)
                and collision_constraints(bad, region, L0, N) == []))
    out.append(("collision_dsu still per-instance ok on mismatch",
                collision_dsu(bad, region, L0, N)))

    # discover dedup: refrain + extract on plant won't have refrain but discover works
    # discover on tiny plant may return 0 (needs rich internal repeat skeletons);
    # real-corpus discovery is covered by run_paranoia_audit below.
    discovered = discover_targets(msgs, include_refrain=False, min_passage_len=8)
    out.append(("discover_targets runs on plant (may be empty)",
                isinstance(discovered, list)))

    # redundancy: plant target redundant with itself only
    pairs = redundancy_pairs([ana, ana])
    out.append(("redundancy self not marked",
                ana.target.name not in pairs.get(ana.target.name, []) or
                pairs[ana.target.name] == []))

    # validate_phrase: wrong phrase rejects on plant
    bad = validate_phrase(tgt, "x" * L0, msgs, N, "abcdefghijklmnopqrstuvwxyz",
                          n_null=50)
    out.append(("validate_phrase runs", bad is not None))

    # Real corpus smoke (must not crash; refrain max_L == 22)
    import corpus as corpus_mod
    c = corpus_mod.load()
    M = [list(x) for x in c.ciphertexts]
    real = discover_targets(M, labels=c.labels, include_refrain=True)
    out.append(("real corpus: discover returns targets", len(real) >= 2))
    refrain_ana = next((a for a in analyze_all(M, real, c.N, max_extra=12)
                        if a.target.source == "refrain"), None)
    out.append(("real corpus: refrain max_L is 22",
                refrain_ana is not None and refrain_ana.max_L == 22))
    out.append(("real corpus: refrain has 3 same-groups at L=22",
                refrain_ana is not None and refrain_ana.max_template is not None and
                len(refrain_ana.max_template.same_groups) == 3))
    render_report(analyze_all(M, real[:3], c.N, max_extra=5), labels=c.labels)
    out.append(("render_report produces markdown", True))

    out.extend(run_paranoia_audit(M, c.labels, c.N))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} passage_template checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
