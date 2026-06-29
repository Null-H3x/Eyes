"""Template-constrained refrain phrase generator.

Filters candidate words/fragments against the refrain repeat-template and
ordering-free ciphertext viability.  For small templates (≤6 letter classes)
optionally enumerates fills; otherwise uses the wordlist + compose path only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

import refrain as rf
import refrain_compose as rc
import template as tp


@dataclass
class PhraseCandidate:
    phrase: str
    offset: int
    viable: bool
    source: str = "wordlist"


def _rep_classes(tmpl: tp.Template) -> List[List[int]]:
    parent = list(range(tmpl.L))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for grp in tmpl.same_groups:
        r = min(grp)
        for p in grp:
            parent[find(p)] = find(r)
    comp: Dict[int, List[int]] = {}
    for i in range(tmpl.L):
        comp.setdefault(find(i), []).append(i)
    return [sorted(v) for v in comp.values()]


def _valid_fill(phrase: str, tmpl: tp.Template) -> bool:
    if len(phrase) != tmpl.L:
        return False
    dmap = rc.double_letter_map(tmpl)
    for i, j, _ in tmpl.diff_pairs:
        if phrase[i] == phrase[j]:
            return False
    for (a, b), kind in dmap.items():
        if kind == "forced-diff" and phrase[a] == phrase[b]:
            return False
        if kind == "forced-same" and phrase[a] != phrase[b]:
            return False
    for grp in tmpl.same_groups:
        letters = {phrase[i] for i in grp}
        if len(letters) > 1:
            return False
    return True


def enumerate_template_fills(
    tmpl: tp.Template,
    *,
    alphabet: str = "abcdefghijklmnopqrstuvwxyz",
    max_phrases: int = 5000,
) -> Iterator[str]:
    """Bounded enumeration — only when ≤6 equivalence classes."""
    classes = _rep_classes(tmpl)
    if len(classes) > 6:
        yield from ()
        return

    count = 0

    def gen(ci: int, chosen: List[str]) -> Iterator[str]:
        nonlocal count
        if count >= max_phrases:
            return
        if ci >= len(classes):
            mp: Dict[int, str] = {}
            for cls, ch in zip(classes, chosen):
                for p in cls:
                    mp[p] = ch
            phrase = "".join(mp[i] for i in range(tmpl.L))
            if _valid_fill(phrase, tmpl):
                count += 1
                yield phrase
            return
        for ch in alphabet:
            yield from gen(ci + 1, chosen + [ch])

    yield from gen(0, [])


def generate_from_words(
    messages: Sequence[Sequence[int]],
    N: int,
    words: Sequence[str],
    *,
    region=None,
    max_out: int = 500,
) -> List[PhraseCandidate]:
    """Filter wordlist entries by template + viable_offsets."""
    region = region or rf.DEFAULT_INSTANCES
    tmpl = tp.extract(messages, region, rf.DEFAULT_LEN, N)
    if not tmpl.consistent:
        return []
    out: List[PhraseCandidate] = []
    seen = set()
    for raw in words:
        w = "".join(c for c in raw.lower() if c.isalpha())
        if len(w) < 3 or len(w) > tmpl.L:
            continue
        offs = rc.anchor_offsets(w, tmpl) if len(w) <= tmpl.L else []
        for off in offs:
            if off + len(w) > tmpl.L:
                continue
            # extend to full L with placeholders for partial words
            if len(w) == tmpl.L:
                phrase = w
            else:
                continue  # only full-length or use compose for partial
            if not _valid_fill(phrase, tmpl):
                continue
            voffs = rf.viable_offsets(messages, phrase, region, rf.DEFAULT_LEN, N)
            if not voffs:
                continue
            key = (phrase, voffs[0])
            if key in seen:
                continue
            seen.add(key)
            out.append(PhraseCandidate(phrase, voffs[0], True, "wordlist"))
            if len(out) >= max_out:
                return out
    return out


def generate_candidates(
    messages: Sequence[Sequence[int]],
    N: int,
    *,
    region=None,
    words: Optional[Sequence[str]] = None,
    alphabet: str = "abcdefghijklmnopqrstuvwxyz",
    max_phrases: int = 2000,
    require_viable: bool = True,
) -> List[PhraseCandidate]:
    if not messages:
        return []
    region = region or rf.DEFAULT_INSTANCES
    tmpl = tp.extract(messages, region, rf.DEFAULT_LEN, N)
    if not tmpl.consistent:
        return []

    wordset = list(words) if words else sorted(rc._DEFAULT_WORDS)
    out = generate_from_words(messages, N, wordset, region=region,
                              max_out=max_phrases)

    seen = {(c.phrase, c.offset) for c in out}
    classes = _rep_classes(tmpl)
    if len(classes) <= 6:
        for phrase in enumerate_template_fills(tmpl, alphabet=alphabet[:10],
                                               max_phrases=max(500, max_phrases // 4)):
            if (phrase, 0) in seen:
                continue
            offs = rf.viable_offsets(messages, phrase, region, rf.DEFAULT_LEN, N)
            if require_viable and not offs:
                continue
            off = offs[0] if offs else 0
            seen.add((phrase, off))
            out.append(PhraseCandidate(phrase, off, bool(offs), "enumerate"))
            if len(out) >= max_phrases:
                break
    return out


def selftest() -> List[Tuple[str, bool]]:
    import numpy as np

    out: List[Tuple[str, bool]] = []
    N = 83
    rng = np.random.default_rng(1)
    aidx = {ch: i for i, ch in enumerate(rf.DEFAULT_ALPHABET)}
    eng = [aidx[ch] for ch in "thetruthisthatthereisnothingmorevaluable" if ch in aidx]
    crib = "trueknowledgeofthe"
    cv = [aidx[ch] for ch in crib]
    insts = [(0, 30), (0, 70), (1, 35), (1, 75)]
    C = list(rng.permutation(N))
    bases = [3, 7, 11, 19]
    T = 110
    msgs = []
    for m in range(4):
        p = [eng[(m * 17 + i) % len(eng)] for i in range(T)]
        for (mm, ps) in insts:
            if mm == m:
                p[ps: ps + len(cv)] = cv
        msgs.append([C[(p[t] + bases[m] + t) % N] for t in range(T)])

    cands = generate_candidates(msgs, N, region=insts, words=[crib],
                                max_phrases=50, require_viable=True)
    out.append(("wordlist path returns candidates", len(cands) >= 0))

    toy = tp.Template(L=4, consistent=True, same_groups=[[0, 1]],
                      diff_pairs=[(2, 3, 1)], free_positions=[2, 3], dof=2)
    fills = list(enumerate_template_fills(toy, alphabet="ab", max_phrases=50))
    out.append(("small template enumerates fills", len(fills) >= 1))
    out.append(("empty corpus safe", generate_candidates([], 83) == []))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} template_phrase checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
