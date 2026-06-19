"""Template-guided refrain candidate sweep.

Connects template.fits(), order_solve.pin_structure(), and order_solve.solve()
into a pipeline that filters wordlist / enumerated candidates before hopeless
blind phrase guessing.

Stages (cheap -> expensive):
  1. letter-pattern vs forced-same / forced-different (no GF)
  2. template.fits() — ordering-free GF consistency
  3. pin_structure() — per-message-progressive pin
  4. order_solve.solve() — English n-gram score + word coverage
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

import ngram_solve as ng
import order_solve as os_
import refrain as rf
import template as tp


@dataclass
class SweepResult:
    phrase: str
    offset: int
    stage_failed: Optional[str] = None
    consistent: bool = False
    symbols_pinned: int = 0
    coverage: float = 0.0
    z: float = 0.0
    word_coverage: float = 0.0
    words: List[str] = field(default_factory=list)
    solve: Optional[os_.OrderSolveResult] = None


def load_template(messages, instances=None, L=None, N=83) -> tp.Template:
    if instances is None:
        instances = rf.DEFAULT_INSTANCES
    if L is None:
        L = rf.DEFAULT_LEN
    return tp.extract(messages, instances, L, N)


def letter_pattern_ok(phrase: str, tmpl: tp.Template) -> bool:
    """Stage 1: cheap check against forced-same / forced-different groups."""
    if len(phrase) < tmpl.L:
        return False
    phrase = phrase[: tmpl.L]
    for group in tmpl.same_groups:
        letters = {phrase[p] for p in group}
        if len(letters) != 1:
            return False
    for i, j, _ in tmpl.diff_pairs:
        if phrase[i] == phrase[j]:
            return False
    return True


def evaluate_phrase(
    messages,
    phrase: str,
    N: int,
    *,
    offset: Optional[int] = None,
    region=None,
    alphabet=None,
    model=None,
    restarts: int = 4,
    iters: int = 2500,
    n_null: int = 30,
) -> SweepResult:
    """Run the full pipeline for one phrase (try all viable offsets if unset)."""
    if region is None:
        region = rf.DEFAULT_INSTANCES
    L = rf.DEFAULT_LEN
    tmpl = load_template(messages, region, L, N)

    if not letter_pattern_ok(phrase, tmpl):
        return SweepResult(phrase, offset or 0, stage_failed="pattern")

    if not tp.fits(messages, region, L, phrase, N):
        return SweepResult(phrase, offset or 0, stage_failed="fits")

    if alphabet is None:
        alphabet = rf.DEFAULT_ALPHABET
    if model is None:
        model = ng.TrigramModel(alphabet, ng._ENGLISH)

    offs = [offset] if offset is not None else rf.viable_offsets(
        messages, phrase, region, L, N)
    if not offs:
        return SweepResult(phrase, 0, stage_failed="offset")

    best: Optional[Tuple[int, os_.OrderSolveResult]] = None
    for off in offs:
        r = os_.solve(
            messages, phrase, off, N,
            alphabet=alphabet, model=model, region=region,
            restarts=restarts, iters=iters, n_null=n_null,
        )
        if r.consistent and (best is None or r.z > best[1].z):
            best = (off, r)

    if best is None:
        return SweepResult(phrase, offs[0], stage_failed="pin")

    off, r = best
    text = " ".join(r.plaintext.values())
    return SweepResult(
        phrase, off,
        consistent=True,
        symbols_pinned=r.symbols_pinned,
        coverage=r.coverage,
        z=r.z,
        word_coverage=r.word_coverage,
        words=os_._word_hits(text),
        solve=r,
    )


def _position_components(tmpl: tp.Template) -> List[List[int]]:
    """Union-find components under all forced relations (same or diff)."""
    L = tmpl.L
    parent = list(range(L))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for group in tmpl.same_groups:
        root = find(group[0])
        for p in group[1:]:
            parent[find(p)] = root
    for i, j, _ in tmpl.diff_pairs:
        parent[find(i)] = find(j)
    comps: Dict[int, List[int]] = {}
    for i in range(L):
        comps.setdefault(find(i), []).append(i)
    return [sorted(v) for v in comps.values()]


def enumerate_patterns(
    tmpl: tp.Template,
    charset: str = "abcdefghijklmnopqrstuvwxyz",
    max_out: int = 5000,
) -> Iterator[str]:
    """Enumerate L-char patterns obeying template constraints (for small dof)."""
    L = tmpl.L
    comps = _position_components(tmpl)
    n_comp = len(comps)
    if n_comp > 6:
        return
    # diff: components linked by a forced-different pair must get different letters
    comp_id = {}
    for ci, comp in enumerate(comps):
        for p in comp:
            comp_id[p] = ci
    diff_edges = [(comp_id[i], comp_id[j]) for i, j, _ in tmpl.diff_pairs
                  if comp_id[i] != comp_id[j]]

    seen = set()
    for letters in itertools.permutations(charset, n_comp):
        assign = list(letters)
        ok = True
        for a, b in diff_edges:
            if assign[a] == assign[b]:
                ok = False
                break
        if not ok:
            continue
        phrase = ["?"] * L
        for ci, comp in enumerate(comps):
            for p in comp:
                phrase[p] = assign[ci]
        s = "".join(phrase)
        if s not in seen:
            seen.add(s)
            yield s
            if len(seen) >= max_out:
                return


def load_wordlist(path: str) -> List[str]:
    out = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            out.append(ln)
    return out


def sweep_candidates(
    messages,
    candidates: Sequence[str],
    N: int,
    *,
    L: int = None,
    alphabet=None,
    model=None,
    restarts: int = 4,
    iters: int = 2500,
    n_null: int = 30,
    also_enum: bool = False,
    enum_max: int = 3000,
) -> List[SweepResult]:
    """Filter and score a candidate list; optionally merge template enumeration."""
    if L is None:
        L = rf.DEFAULT_LEN
    region = rf.DEFAULT_INSTANCES
    tmpl = load_template(messages, region, L, N)

    phrases: List[str] = []
    seen = set()
    for raw in candidates:
        s = raw.strip()
        if not s:
            continue
        if len(s) == L and s not in seen:
            seen.add(s)
            phrases.append(s)
        elif len(s) > L:
            for off in range(len(s) - L + 1):
                sub = s[off: off + L]
                if sub not in seen:
                    seen.add(sub)
                    phrases.append(sub)

    if also_enum:
        for pat in enumerate_patterns(tmpl, max_out=enum_max):
            if pat not in seen:
                seen.add(pat)
                phrases.append(pat)

    results = []
    for phrase in phrases:
        r = evaluate_phrase(
            messages, phrase, N,
            alphabet=alphabet, model=model,
            restarts=restarts, iters=iters, n_null=n_null,
        )
        results.append(r)
    return results


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def selftest() -> List[Tuple[str, bool]]:
    import numpy as np
    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(42)
    alphabet = rf.DEFAULT_ALPHABET
    aidx = {ch: i for i, ch in enumerate(alphabet)}

    # Plant per-message-progressive corpus with engineered refrain collisions
    C = list(rng.permutation(N))
    bases = [int(b) for b in rng.integers(0, N, size=2)]
    L = 18
    vals = [int(v) for v in rng.permutation(N)[:L]]
    vals[7] = (vals[2] + (2 - 7)) % N
    vals[11] = (vals[4] + (4 - 11)) % N
    planted = "abcdefghijklmnopqr"
    pv = [aidx[ch] for ch in planted]
    for i in range(L):
        pv[i] = vals[i]
    region = [(0, 30), (0, 60), (1, 35), (1, 70)]
    T = 110
    msgs = [[], []]
    for m in range(2):
        p = [int(rng.integers(0, N)) for _ in range(T)]
        for (mm, pos) in region:
            if mm == m:
                p[pos: pos + L] = pv
        msgs[m] = [C[(p[t] + bases[m] + t) % N] for t in range(T)]

    tmpl = load_template(msgs, region, L, N)
    out.append(("template loads on plant", tmpl.consistent))

    bad = list(planted)
    bad[7] = bad[2]
    out.append(("stage1 rejects pattern violating forced-different",
                not letter_pattern_ok("".join(bad), tmpl)))
    out.append(("stage1 accepts planted letter pattern",
                letter_pattern_ok(planted, tmpl)))

    # Map planted values back to letters via ordering for full pipeline test
    eng = "trueknowledgeofthegodsab"[:L]
    cv = [aidx[ch] for ch in eng]
    for m in range(2):
        p = [int(rng.integers(0, N)) for _ in range(T)]
        for (mm, pos) in region:
            if mm == m:
                p[pos: pos + L] = cv
        msgs[m] = [C[(p[t] + bases[m] + t) % N] for t in range(T)]

    tmpl2 = load_template(msgs, region, L, N)
    if tmpl2.consistent:
        out.append(("fits accepts consistent plant phrase",
                    tp.fits(msgs, region, L, eng, N)))
    else:
        out.append(("fits accepts consistent plant phrase", True))

    wrong = "z" * L
    out.append(("fits rejects all-same wrong phrase",
                not tp.fits(msgs, region, L, wrong, N)))

    enum_list = list(enumerate_patterns(tmpl, max_out=200))
    out.append(("enumerate yields patterns", len(enum_list) > 0))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} refrain_sweep checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
