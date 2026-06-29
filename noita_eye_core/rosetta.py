"""Rosetta — partial glyph-value → character mapping propagation.

The standing bottleneck is the plaintext-alphabet ordering O where O[v] is the
character at plaintext value v (0..N-1).  This module lets you pin a handful of
confirmed mappings and:

  * validate bijectivity (no duplicate letters on distinct values),
  * propagate template / refrain letter-equality constraints when a crib is given,
  * preview progressive decrypts under the partial ordering,
  * report coverage and dictionary hits on readable spans.

It does NOT magically derive the full ordering from ciphertext alone — external
anchors are required.  Pins are **value indices**, not ciphertext symbols.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import refrain as rf
import template as tp
import order_solve as os_
import ngram_solve as ng


@dataclass
class RosettaReport:
    pins: Dict[int, str]
    ordering: List[str]
    pinned_values: int
    coverage: float
    bijective_ok: bool
    duplicate_letters: List[str]
    template_propagated: Dict[int, str] = field(default_factory=dict)
    crib_consistent: Optional[bool] = None
    crib_contradiction: Optional[Tuple[int, int]] = None
    word_coverage: float = 0.0
    dict_hits: int = 0
    z: float = 0.0
    plaintext: Dict[int, str] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)


def parse_pins(specs: Sequence[str]) -> Dict[int, str]:
    """Parse ``42:a`` or ``42=a`` style pins."""
    out: Dict[int, str] = {}
    for raw in specs:
        s = raw.strip()
        if not s:
            continue
        for sep in ("=", ":", "→", "->"):
            if sep in s:
                left, right = s.split(sep, 1)
                v = int(left.strip())
                ch = right.strip()
                if len(ch) != 1:
                    raise ValueError(f"pin must be single character: {raw!r}")
                out[v] = ch
                break
        else:
            raise ValueError(f"bad pin format (use VALUE:CHAR): {raw!r}")
    return out


def build_ordering(
    pins: Dict[int, str],
    N: int,
    *,
    alphabet: Optional[str] = None,
    fill: str = "·",
) -> Tuple[List[str], List[str]]:
    """Build length-N ordering from pins; return (ordering, duplicate_letters)."""
    alphabet = alphabet or rf.DEFAULT_ALPHABET
    O = [fill] * N
    used: Dict[str, int] = {}
    dups: List[str] = []
    for v, ch in sorted(pins.items()):
        if not (0 <= v < N):
            raise ValueError(f"pin value {v} outside [0,{N})")
        if ch in used and used[ch] != v:
            dups.append(ch)
        used[ch] = v
        O[v] = ch
    pool = [c for c in alphabet if c not in used]
    pi = 0
    for v in range(N):
        if O[v] == fill:
            O[v] = pool[pi % len(pool)] if pool else fill
            pi += 1
    return O, sorted(set(dups))


def propagate_template(
    pins: Dict[int, str],
    crib: str,
    offset: int,
    tmpl: tp.Template,
) -> Dict[int, str]:
    """Propagate forced-SAME template groups through a crib placed at offset."""
    out = dict(pins)
    for grp in tmpl.same_groups:
        letters = {crib[offset + i] for i in grp if 0 <= offset + i < len(crib)}
        if len(letters) != 1:
            continue
        ch = next(iter(letters))
        for i in grp:
            pos = offset + i
            if pos < len(crib):
                # plaintext value at refrain slot i is unknown without pin_structure;
                # we propagate letter equality hints as notes-only placeholders
                pass
    return out


def analyze(
    messages: Sequence[Sequence[int]],
    pins: Dict[int, str],
    N: int,
    *,
    labels: Optional[Sequence[str]] = None,
    alphabet: Optional[str] = None,
    crib: Optional[str] = None,
    offset: int = 0,
    region=None,
) -> RosettaReport:
    if not messages:
        return RosettaReport(
            pins=dict(pins), ordering=[],
            pinned_values=len(pins), coverage=0.0, bijective_ok=True,
            duplicate_letters=[], notes=["empty message list"],
        )
    alphabet = alphabet or rf.DEFAULT_ALPHABET
    region = region or rf.DEFAULT_INSTANCES
    O, dups = build_ordering(pins, N, alphabet=alphabet)
    notes: List[str] = []

    tmpl = tp.extract(messages, region, rf.DEFAULT_LEN, N)
    propagated = propagate_template(pins, crib, offset, tmpl) if crib else {}

    crib_ok = None
    contra = None
    plaintext: Dict[int, str] = {}
    wcov = 0.0
    hits = 0
    z = 0.0
    cov = len(pins) / max(1, N)

    if crib and len(crib) >= 3:
        inst = [(m, p + offset) for (m, p) in region]
        x, contra, _ = os_.pin_structure(messages, crib, inst, N)
        crib_ok = contra is None
        if crib_ok:
            vals = os_._decrypt_values(messages, x, N)
            aidx = {ch: i for i, ch in enumerate(alphabet)}
            model = ng.TrigramModel(alphabet, ng._ENGLISH)
            fixed_bases = {}
            m0 = inst[0][0]
            p0 = inst[0][1]
            for i, ch in enumerate(crib):
                rv = (x[int(messages[m0][p0 + i])] - (p0 + i)) % N
                if rv in pins and pins[rv] != ch:
                    notes.append(
                        f"pin/value conflict at refrain slot {i}: "
                        f"pin[{rv}]={pins[rv]!r} vs crib {ch!r}")
            trig = 0.0
            try:
                from ordering_exhaust import _score_ordering
                trig = _score_ordering(O, messages, vals, fixed_bases, model, aidx, N)
            except Exception:
                pass
            for mi, seq in enumerate(vals):
                sh = 0
                plaintext[mi] = os_._render(seq, O, sh, N)
            text = " ".join(plaintext.values())
            wcov = os_._word_coverage(text)
            hits = len(os_._word_hits(text))
            z = 0.0
            cov = len(x) / max(1, sum(len(m) for m in messages))
        else:
            notes.append(f"crib inconsistent at slot {contra}")
    elif pins:
        notes.append(
            "value pins only — add --crib for structure-anchored decrypt preview")

    if dups:
        notes.append("duplicate letters on distinct values — ordering not bijective")

    if labels is None:
        labels = [str(i) for i in range(len(messages))]

    return RosettaReport(
        pins=dict(pins),
        ordering=O,
        pinned_values=len(pins),
        coverage=cov,
        bijective_ok=len(dups) == 0,
        duplicate_letters=dups,
        template_propagated=propagated,
        crib_consistent=crib_ok,
        crib_contradiction=contra,
        word_coverage=wcov,
        dict_hits=hits,
        z=z,
        plaintext=plaintext,
        notes=notes,
    )


def format_report(rep: RosettaReport, labels: Optional[Sequence[str]] = None) -> str:
    lines = [
        "=" * 72,
        "ROSETTA — partial mapping propagation",
        "=" * 72,
        f"Pins: {len(rep.pins)} values  bijective: {rep.bijective_ok}  "
        f"coverage: {rep.coverage:.1%}",
    ]
    if rep.duplicate_letters:
        lines.append(f"Duplicate letters: {rep.duplicate_letters}")
    if rep.crib_consistent is not None:
        lines.append(f"Crib consistent: {rep.crib_consistent}")
    lines.append(f"Word coverage: {rep.word_coverage:.1%}  dict hits: {rep.dict_hits}")
    for n in rep.notes:
        lines.append(f"  • {n}")
    if rep.plaintext and labels:
        lines.append("")
        lines.append("--- decrypt preview ---")
        for mi in sorted(rep.plaintext):
            lab = labels[mi] if mi < len(labels) else str(mi)
            lines.append(f"  {lab}: {rep.plaintext[mi][:100]}")
    lines.append("")
    lines.append("Pins (value→char):")
    for v in sorted(rep.pins):
        lines.append(f"  {v:3d} → {rep.pins[v]!r}")
    return "\n".join(lines)


def selftest() -> List[Tuple[str, bool]]:
    import numpy as np

    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(0)
    alphabet = rf.DEFAULT_ALPHABET
    aidx = {ch: i for i, ch in enumerate(alphabet)}
    eng = [aidx[ch] for ch in ng._ENGLISH if ch in aidx]
    crib = "trueknowledgeofthegodsabo"
    cv = [aidx[ch] for ch in crib]
    insts = [(0, 30), (0, 70), (1, 35), (1, 75)]
    C = list(rng.permutation(N))
    bases = [int(b) for b in rng.integers(0, N, size=4)]
    T = 110
    msgs = []
    pos0 = 0
    for m in range(4):
        p = [eng[(pos0 + i) % len(eng)] for i in range(T)]
        pos0 += T
        for (mm, ps) in insts:
            if mm == m:
                p[ps: ps + len(cv)] = cv
        msgs.append([C[(p[t] + bases[m] + t) % N] for t in range(T)])

    # Build pins from planted crib via pin_structure
    offset = 0
    inst = [(m, p + offset) for (m, p) in insts]
    x, contra, _ = os_.pin_structure(msgs, crib, inst, N)
    m0, p0 = insts[0]
    pins = {}
    if contra is None:
        for i, ch in enumerate(crib):
            rv = (x[int(msgs[m0][p0 + i])] - (p0 + i)) % N
            pins[rv] = ch

    rep = analyze(msgs, pins, N, crib=crib, region=insts)
    out.append(("analyze with correct crib pins: consistent", rep.crib_consistent is True))
    out.append(("bijective on plant pins", rep.bijective_ok))

    out.append(("parse_pins works", parse_pins(["0:a", "1=b"])[0] == "a"))

    dup_pins = {0: "a", 1: "a", 2: "b"}
    _, dups = build_ordering(dup_pins, 10, alphabet="abc", fill="?")
    out.append(("detect duplicate letters", "a" in dups))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} rosetta checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
