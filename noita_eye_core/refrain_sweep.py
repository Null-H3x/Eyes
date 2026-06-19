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

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

import ngram_solve as ng
import order_solve as os_
import refrain as rf
import template as tp

_ALNUM = re.compile(r"[^a-zA-Z0-9]+")


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


def resolve_path(path: str | Path, *, anchors: Sequence[Path]) -> Path:
    """Resolve a user path against several anchor directories."""
    p = Path(path)
    if p.is_file():
        return p.resolve()
    for base in anchors:
        cand = (base / p).resolve()
        if cand.is_file():
            return cand
    tried = ", ".join(str((base / p).resolve()) for base in anchors)
    raise FileNotFoundError(f"wordlist not found: {path} (tried: {tried})")


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


def _partial_pattern_ok(phrase: List[Optional[str]], tmpl: tp.Template) -> bool:
    """Backtracking helper: check constraints on assigned positions only."""
    for group in tmpl.same_groups:
        seen = {phrase[p] for p in group if phrase[p] is not None}
        if len(seen) > 1:
            return False
    for i, j, _ in tmpl.diff_pairs:
        a, b = phrase[i], phrase[j]
        if a is not None and b is not None and a == b:
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
    score: bool = True,
) -> SweepResult:
    """Run the pipeline for one phrase. Set score=False to stop after cheap stages."""
    if region is None:
        region = rf.DEFAULT_INSTANCES
    L = rf.DEFAULT_LEN
    tmpl = load_template(messages, region, L, N)

    if len(phrase) != L:
        return SweepResult(phrase, offset or 0, stage_failed="length")

    if not letter_pattern_ok(phrase, tmpl):
        return SweepResult(phrase, offset or 0, stage_failed="pattern")

    if not tp.fits(messages, region, L, phrase, N):
        return SweepResult(phrase, offset or 0, stage_failed="fits")

    offs = [offset] if offset is not None else rf.viable_offsets(
        messages, phrase, region, L, N)
    if not offs:
        return SweepResult(phrase, 0, stage_failed="offset")

    if not score:
        return SweepResult(phrase, offs[0], stage_failed="cheap_ok")

    if alphabet is None:
        alphabet = rf.DEFAULT_ALPHABET
    if model is None:
        model = ng.TrigramModel(alphabet, ng._ENGLISH)

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


def enumerate_patterns(
    tmpl: tp.Template,
    charset: str = "abcdefghijklmnopqrstuvwxyz",
    max_out: int = 5000,
) -> Iterator[str]:
    """Enumerate L-char patterns obeying template same/diff constraints."""
    if not tmpl.consistent:
        return
    L = tmpl.L
    slots: List[Optional[str]] = [None] * L
    seen: set[str] = set()
    found = 0

    # Pre-fill forced-same groups to cut the search tree dramatically.
    group_positions: List[List[int]] = [sorted(g) for g in tmpl.same_groups]
    grouped = {p for g in tmpl.same_groups for p in g}

    def dfs(pos: int) -> Iterator[str]:
        nonlocal found
        if found >= max_out:
            return
        while pos < L and slots[pos] is not None:
            pos += 1
        if pos == L:
            s = "".join(slots)  # type: ignore[arg-type]
            if s not in seen and letter_pattern_ok(s, tmpl):
                seen.add(s)
                found += 1
                yield s
            return
        for ch in charset:
            slots[pos] = ch
            if _partial_pattern_ok(slots, tmpl):
                yield from dfs(pos + 1)
            if found >= max_out:
                return
            slots[pos] = None

    if not group_positions:
        yield from dfs(0)
        return

    n_g = len(group_positions)
    if n_g > len(charset):
        return

    import itertools
    for letters in itertools.permutations(charset, n_g):
        slots = [None] * L
        for positions, ch in zip(group_positions, letters):
            for p in positions:
                slots[p] = ch
        if not _partial_pattern_ok(slots, tmpl):
            continue
        start = 0
        while start < L and slots[start] is not None:
            start += 1
        yield from dfs(start)
        if found >= max_out:
            return


def _clean_token(raw: str) -> str:
    return _ALNUM.sub("", raw.lower())


def phrases_from_wordlist(
    words: Sequence[str],
    L: int = rf.DEFAULT_LEN,
    *,
    max_words: int = 4,
    max_phrases: int = 50_000,
) -> List[str]:
    """Build length-L candidate phrases from short dictionary tokens.

    The Noita lore wordlist has no length-22 entries; we join 1–max_words
    cleaned tokens and take every length-L window from the concatenation.
    """
    tokens = []
    seen_tok = set()
    for raw in words:
        t = _clean_token(raw)
        if len(t) < 2 or t in seen_tok:
            continue
        seen_tok.add(t)
        tokens.append(t)
    if not tokens:
        return []

    out: List[str] = []
    seen: set[str] = set()

    def add_from(s: str) -> None:
        if len(s) < L:
            return
        for off in range(len(s) - L + 1):
            sub = s[off: off + L]
            if sub not in seen:
                seen.add(sub)
                out.append(sub)
                if len(out) >= max_phrases:
                    return

    for t in tokens:
        add_from(t)
        if len(out) >= max_phrases:
            return out

    n = len(tokens)
    for k in range(2, max_words + 1):
        for i in range(n - k + 1):
            add_from("".join(tokens[i: i + k]))
            if len(out) >= max_phrases:
                return out
    return out


def load_wordlist(path: str | Path, *, anchors: Optional[Sequence[Path]] = None) -> List[str]:
    p = Path(path)
    if anchors is not None and not p.is_file():
        p = resolve_path(p, anchors=anchors)
    elif not p.is_file():
        raise FileNotFoundError(f"wordlist not found: {path}")
    out = []
    with open(p, encoding="utf-8", errors="replace") as f:
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
    enum_max: int = 500,
    expand_wordlist: bool = True,
    score_limit: int = 40,
    always_score: Optional[Sequence[str]] = None,
) -> List[SweepResult]:
    """Filter and score a candidate list; optionally merge template enumeration."""
    if L is None:
        L = rf.DEFAULT_LEN
    region = rf.DEFAULT_INSTANCES
    tmpl = load_template(messages, region, L, N)

    phrases: List[str] = []
    seen = set()

    def add_phrase(s: str) -> None:
        s = s.strip()
        if len(s) != L or s in seen:
            return
        seen.add(s)
        phrases.append(s)

    if expand_wordlist and candidates and all(len(x.strip()) != L for x in candidates if x.strip()):
        for s in phrases_from_wordlist(candidates, L):
            add_phrase(s)
    else:
        for raw in candidates:
            s = raw.strip()
            if not s:
                continue
            if len(s) == L:
                add_phrase(s)
            elif len(s) > L:
                for off in range(len(s) - L + 1):
                    add_phrase(s[off: off + L])

    if also_enum:
        for pat in enumerate_patterns(tmpl, max_out=enum_max):
            add_phrase(pat)

    results = []
    scored = 0
    must_score = set(always_score or ())
    for phrase in phrases:
        cheap = evaluate_phrase(messages, phrase, N, score=False)
        if cheap.stage_failed != "cheap_ok":
            results.append(cheap)
            continue
        if phrase not in must_score and scored >= score_limit:
            cheap.stage_failed = "cheap_ok"
            results.append(cheap)
            continue
        r = evaluate_phrase(
            messages, phrase, N,
            alphabet=alphabet, model=model,
            restarts=restarts, iters=iters, n_null=n_null,
            score=True,
        )
        results.append(r)
        if phrase not in must_score:
            scored += 1
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

    # --- path resolution ---
    root = Path(__file__).resolve().parent.parent
    try:
        p = resolve_path("eyestat/noita_wordlist.txt",
                         anchors=[root, root / "eyecrack"])
        out.append(("resolve_path finds repo wordlist from relative path",
                    p.is_file()))
    except FileNotFoundError:
        out.append(("resolve_path finds repo wordlist from relative path", False))

    # --- wordlist phrase expansion ---
    wl = load_wordlist(root / "eyestat" / "noita_wordlist.txt")
    built = phrases_from_wordlist(wl, L=22)
    out.append(("phrases_from_wordlist yields length-22 candidates",
                len(built) > 0))
    out.append(("phrases_from_wordlist candidates are length 22",
                all(len(s) == 22 for s in built[:20])))

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

    wrong = "z" * L
    out.append(("fits rejects all-same wrong phrase",
                not tp.fits(msgs, region, L, wrong, N)))

    enum_list = [p for p in enumerate_patterns(tmpl, max_out=200)
                 if letter_pattern_ok(p, tmpl)]
    out.append(("enumerate yields template-valid patterns", len(enum_list) > 0))

    # Real corpus: enumeration should pass stage-1 pattern filter
    real = [list(x) for x in __import__("corpus").load().ciphertexts]
    real_tmpl = load_template(real)
    if real_tmpl.consistent:
        real_enum = [p for p in enumerate_patterns(real_tmpl, max_out=50)
                     if letter_pattern_ok(p, real_tmpl)]
        out.append(("real corpus enum passes letter_pattern_ok",
                    len(real_enum) > 0))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} refrain_sweep checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
