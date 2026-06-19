"""Anchored, constraint-respecting refrain composer.

The 22-glyph refrain's plaintext is pinned (ordering-free) to a repeat-template
(`template.py`): forced-SAME groups, forced-DIFFERENT pairs, one free slot, and a
single mandatory adjacent double letter at positions (4,5). This module turns that
template into a *generative* attack:

  - `double_letter_map`  — the structural fact that adjacent doubles are allowed
    ONLY at (4,5) [forced], (6,7), (7,8); every other adjacent pair is
    forced-different. Any candidate plaintext with a double anywhere else is dead.
  - `anchor_offsets`     — every template-compatible offset for an expected word OR
    fragment (word endings / internal doubles included), via letter-pattern match.
  - `compatible_placements` — which expected words can co-occur at mutually
    consistent offsets (the real space-collapsing lever — one anchor barely helps).
  - `compose`            — a character-trigram-guided beam search over the 22
    positions that honours same/diff/anchor constraints and ranks fills by language
    score AND dictionary word-coverage (wcov), the gate that rejects English-
    flavoured gibberish.

HONESTY (validated below): expanding the candidate word list does NOT by itself
narrow the refrain — the (4,5) double is satisfiable by ~25k dictionary words and a
trigram model still ranks gibberish at the top. Narrowing power comes from STACKING
multiple compatible anchors + the wcov gate + the no-other-doubles rule. Reading the
plaintext still ultimately needs the glyph->char ordering; this tool produces a
ranked SHORTLIST to feed `order_solve`, not a decryption.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import refrain as rf
import template as tp
import ngram_solve as ng


# ---------------------------------------------------------------------------
# Structural facts
# ---------------------------------------------------------------------------

def double_letter_map(tmpl: tp.Template) -> Dict[Tuple[int, int], str]:
    """Classify every adjacent pair (i,i+1): 'forced-same' (a mandatory double),
    'forced-diff' (no double possible), or 'allowed' (an optional double)."""
    diff_set = {(min(i, j), max(i, j)) for i, j, _ in tmpl.diff_pairs}
    same_adj = set()
    for g in tmpl.same_groups:
        for a in g:
            for b in g:
                if abs(a - b) == 1:
                    same_adj.add((min(a, b), max(a, b)))
    out: Dict[Tuple[int, int], str] = {}
    for i in range(tmpl.L - 1):
        pair = (i, i + 1)
        if pair in same_adj:
            out[pair] = "forced-same"
        elif pair in diff_set:
            out[pair] = "forced-diff"
        else:
            out[pair] = "allowed"
    return out


def double_positions(tmpl: tp.Template) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Return (forced_double_pairs, optional_double_pairs)."""
    m = double_letter_map(tmpl)
    forced = [p for p, v in m.items() if v == "forced-same"]
    opt = [p for p, v in m.items() if v == "allowed"]
    return sorted(forced), sorted(opt)


# ---------------------------------------------------------------------------
# Anchor placement
# ---------------------------------------------------------------------------

def _substr_ok(word: str, off: int, tmpl: tp.Template) -> bool:
    """Is `word` placed at `off` compatible with the template's same/diff rules
    (letter-pattern only — ordering-free)?"""
    L = tmpl.L
    if off < 0 or off + len(word) > L:
        return False
    pm = {off + i: word[i] for i in range(len(word))}
    for grp in tmpl.same_groups:
        vals = [pm[i] for i in grp if i in pm]
        if vals and len(set(vals)) > 1:
            return False
    for i, j, _ in tmpl.diff_pairs:
        if i in pm and j in pm and pm[i] == pm[j]:
            return False
    return True


def anchor_offsets(word: str, tmpl: tp.Template) -> List[int]:
    """All template-compatible offsets for a word/fragment (letter-pattern test)."""
    w = "".join(c for c in word.lower() if c.isalpha())
    if not w:
        return []
    return [off for off in range(tmpl.L - len(w) + 1) if _substr_ok(w, off, tmpl)]


@dataclass
class Placement:
    """A joint assignment of offsets to anchor words; pos->char with same-groups
    propagated."""
    assignment: List[Tuple[str, int]]            # (word, offset)
    fixed: Dict[int, str]
    consistent: bool


def _merge_fixed(fixed: Dict[int, str], word: str, off: int,
                 tmpl: tp.Template) -> Optional[Dict[int, str]]:
    f = dict(fixed)
    for i, ch in enumerate(word):
        p = off + i
        if f.get(p, ch) != ch:
            return None
        f[p] = ch
    # propagate forced-same groups
    changed = True
    while changed:
        changed = False
        for g in tmpl.same_groups:
            known = {f[p] for p in g if p in f}
            if len(known) > 1:
                return None
            if len(known) == 1:
                ch = next(iter(known))
                for p in g:
                    if p not in f:
                        f[p] = ch
                        changed = True
    # check forced-diff
    for i, j, _ in tmpl.diff_pairs:
        if i in f and j in f and f[i] == f[j]:
            return None
    return f


def compatible_placements(anchors: Sequence[str], tmpl: tp.Template,
                          *, max_solutions: int = 2000) -> List[Placement]:
    """Enumerate joint offset assignments where ALL anchor words co-occur without
    violating the template. Fragments allowed. Returns consistent placements."""
    words = ["".join(c for c in a.lower() if c.isalpha()) for a in anchors]
    words = [w for w in words if w]
    offs = [anchor_offsets(w, tmpl) for w in words]
    out: List[Placement] = []

    def rec(idx: int, fixed: Dict[int, str], chosen: List[Tuple[str, int]]):
        if len(out) >= max_solutions:
            return
        if idx == len(words):
            out.append(Placement(list(chosen), dict(fixed), True))
            return
        for off in offs[idx]:
            merged = _merge_fixed(fixed, words[idx], off, tmpl)
            if merged is not None:
                chosen.append((words[idx], off))
                rec(idx + 1, merged, chosen)
                chosen.pop()
                if len(out) >= max_solutions:
                    return

    rec(0, {}, [])
    return out


# ---------------------------------------------------------------------------
# Word coverage (wcov) — DP segmentation against a wordset
# ---------------------------------------------------------------------------

def word_coverage(text: str, wordset: set, min_len: int = 3) -> float:
    """Max fraction of characters coverable by a non-overlapping segmentation into
    dictionary words (gaps allowed). DP, O(L^2)."""
    t = "".join(c for c in text.lower() if c.isalpha())
    n = len(t)
    if n == 0:
        return 0.0
    best = [0] * (n + 1)
    for i in range(1, n + 1):
        best[i] = best[i - 1]                  # leave char i-1 uncovered
        for j in range(max(0, i - 12), i - min_len + 1):
            if t[j:i] in wordset:
                best[i] = max(best[i], best[j] + (i - j))
    return best[n] / n


def word_hits(text: str, wordset: set, min_len: int = 3) -> List[str]:
    t = "".join(c for c in text.lower() if c.isalpha())
    hits = set()
    for i in range(len(t)):
        for j in range(i + min_len, min(len(t), i + 13) + 1):
            if t[i:j] in wordset:
                hits.add(t[i:j])
    return sorted(hits, key=len, reverse=True)


# ---------------------------------------------------------------------------
# Composer (constrained trigram beam search)
# ---------------------------------------------------------------------------

@dataclass
class Candidate:
    text: str
    lm_score: float
    wcov: float
    combined: float
    words: List[str] = field(default_factory=list)


def _rep_map(tmpl: tp.Template) -> List[int]:
    rep = list(range(tmpl.L))
    for g in tmpl.same_groups:
        r = min(g)
        for p in g:
            rep[p] = r
    return rep


def _diff_adj(tmpl: tp.Template) -> Dict[int, set]:
    adj: Dict[int, set] = defaultdict(set)
    for i, j, _ in tmpl.diff_pairs:
        adj[i].add(j)
        adj[j].add(i)
    return adj


def compose(tmpl: tp.Template, *, anchors: Sequence[str] = (),
            model: Optional[ng.TrigramModel] = None,
            wordset: Optional[set] = None,
            alphabet: str = "abcdefghijklmnopqrstuvwxyz",
            beam: int = 800, top: int = 25,
            wcov_weight: float = 6.0) -> List[Candidate]:
    """Beam-search 22-char fills honouring same/diff/anchor constraints, ranked by
    mean trigram log-prob + wcov_weight * word-coverage. Anchors that cannot be
    jointly placed are ignored (use compatible_placements to inspect)."""
    if model is None:
        model = ng.TrigramModel(alphabet, ng._ENGLISH)
    if wordset is None:
        wordset = _DEFAULT_WORDS
    L = tmpl.L
    rep = _rep_map(tmpl)
    adj = _diff_adj(tmpl)
    idx = {ch: i for i, ch in enumerate(alphabet)}

    fixed: Dict[int, str] = {}
    if anchors:
        places = compatible_placements(list(anchors), tmpl, max_solutions=1)
        if places:
            fixed = places[0].fixed

    init: List[Optional[str]] = [None] * L
    for p, c in fixed.items():
        init[p] = c

    def tri_add(s: List[Optional[str]], pos: int, ch: str) -> float:
        if pos >= 2 and s[pos - 1] and s[pos - 2]:
            a, b = idx[s[pos - 2]], idx[s[pos - 1]]
            num = model.tri.get((a, b, idx[ch]), model.add_k)
            den = model.tri_tot.get((a, b), model.add_k * model.A)
            import math
            return math.log(num / den)
        if pos >= 1 and s[pos - 1]:
            import math
            a = idx[s[pos - 1]]
            num = model.bi.get((a, idx[ch]), model.add_k)
            den = model.bi_tot.get(a, model.add_k * model.A)
            return math.log(num / den)
        return model.uni

    beams: List[Tuple[float, List[Optional[str]]]] = [(0.0, init)]
    for pos in range(L):
        nxt: List[Tuple[float, List[Optional[str]]]] = []
        for sc, s in beams:
            if s[pos] is not None:
                nxt.append((sc + tri_add(s, pos, s[pos]), s))
                continue
            r = rep[pos]
            for ch in alphabet:
                ok = True
                for q in range(L):
                    if rep[q] == r and s[q] is not None and s[q] != ch:
                        ok = False
                        break
                if not ok:
                    continue
                for q in adj[pos]:
                    if s[q] == ch:
                        ok = False
                        break
                if not ok:
                    continue
                s2 = list(s)
                for q in range(L):
                    if rep[q] == r:
                        s2[q] = ch
                nxt.append((sc + tri_add(s, pos, ch), s2))
        nxt.sort(key=lambda x: -x[0])
        beams = nxt[:beam]

    out: List[Candidate] = []
    seen = set()
    for sc, s in beams:
        if any(c is None for c in s):
            continue
        text = "".join(s)  # type: ignore[arg-type]
        if text in seen:
            continue
        seen.add(text)
        lm = sc / L
        wc = word_coverage(text, wordset)
        out.append(Candidate(text, lm, wc, lm + wcov_weight * wc,
                             word_hits(text, wordset)))
    out.sort(key=lambda c: -c.combined)
    return out[:top]


_DEFAULT_WORDS = set((
    "god gods eye eyes the of and to in is that it for as with was you are not "
    "true truth know knowledge seek seeker secret spirit rejoice monster clever "
    "impressed congratulations watching worthy wisdom devotion sacred ancient "
    "soul mind name believe yourself nearer solving revealed power blood gold "
    "see sees seen seem all too good look deep dark light night star stone water "
    "fire heaven hell abyss void within without beyond great old man men work "
    "have has been who will more out about into them can only other new some "
    "come came right used take three eye message death we us so do done give "
).split())


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def _toy_template() -> tp.Template:
    """Hand-built template for deterministic logic checks. Mirrors the real refrain
    shape: a forced-SAME adjacency (a mandatory double) at (1,2), a non-adjacent
    forced-same pair (4,8), and forced-DIFFERENT pairs incl. the adjacency (5,6)."""
    L = 10
    same_groups = [[1, 2], [4, 8]]
    diff_pairs = [(0, 1, 3), (5, 6, 7), (3, 4, 2), (0, 5, 4)]
    free_positions = [7, 9]
    return tp.Template(L=L, consistent=True, same_groups=same_groups,
                       diff_pairs=diff_pairs, free_positions=free_positions, dof=4)


def selftest() -> List[Tuple[str, bool]]:
    out: List[Tuple[str, bool]] = []
    tmpl = _toy_template()
    L = tmpl.L

    dmap = double_letter_map(tmpl)
    out.append(("forced-same adjacency (1,2) -> a mandatory double",
                dmap.get((1, 2)) == "forced-same"))
    out.append(("forced-diff adjacency (5,6) -> no double",
                dmap.get((5, 6)) == "forced-diff"))
    forced, opt = double_positions(tmpl)
    out.append(("(1,2) is the forced double", forced == [(1, 2)]))
    out.append(("optional doubles exclude forced-diff adjacencies",
                (5, 6) not in opt and (0, 1) not in opt))

    # anchor_offsets: an XYY fragment can sit where its double aligns to (1,2)
    offs_see = anchor_offsets("see", tmpl)
    out.append(("XYY fragment 'see' fits at offset 0 (double -> (1,2))",
                0 in offs_see))
    # X-Y-X fragment cannot sit where 4,5 (no) ... 'eye' needs equal ends; at offset 0
    # positions 0,2 would be equal but 0 is not tied to 2 -> allowed; ensure 'eye'
    # is rejected where its middle/edge would violate the (1,2) double requirement:
    # at offset 1 -> positions 1,2,3 = e,y,e: needs 1==2 (e==y) FALSE -> rejected.
    out.append(("XYX fragment 'eye' rejected at offset 1 (would break (1,2) double)",
                1 not in anchor_offsets("eye", tmpl)))
    out.append(("non-alpha anchor yields no offsets", anchor_offsets("123", tmpl) == []))

    # compatible_placements
    places = compatible_placements(["see"], tmpl)
    out.append(("compatible placement found for 'see'", len(places) >= 1))
    out.append(("compatible_placements returns list", isinstance(places, list)))
    # the placement propagates the forced-same group (1,2) to equal letters
    if places:
        f = places[0].fixed
        out.append(("placement keeps (1,2) equal", f.get(1) == f.get(2)))
    else:
        out.append(("placement keeps (1,2) equal", False))

    # word_coverage
    wc_word = word_coverage("knowledge", _DEFAULT_WORDS)
    wc_rand = word_coverage("xqzjvwbkpf", _DEFAULT_WORDS)
    out.append(("word_coverage: real word > random", wc_word > wc_rand))
    out.append(("word_coverage of pure word is high", wc_word >= 0.8))

    # compose: full-length, constraint-valid, ranked
    cands = compose(tmpl, beam=300, top=10)
    out.append(("compose returns candidates", len(cands) >= 1))
    out.append(("compose candidates are full length", all(len(c.text) == L for c in cands)))
    out.append(("compose respects forced-same (1,2) double",
                all(c.text[1] == c.text[2] for c in cands)))
    out.append(("compose respects non-adjacent forced-same (4,8)",
                all(c.text[4] == c.text[8] for c in cands)))

    def diffs_ok(text):
        return all(text[i] != text[j] for i, j, _ in tmpl.diff_pairs)
    out.append(("compose respects forced-different pairs",
                all(diffs_ok(c.text) for c in cands)))
    out.append(("compose ranked by combined desc",
                all(cands[i].combined >= cands[i + 1].combined
                    for i in range(len(cands) - 1))))

    cands2 = compose(tmpl, anchors=["see"], beam=300, top=5)
    out.append(("anchored compose keeps anchor letters at offset 0",
                bool(cands2) and all(c.text[0:3] == "see" for c in cands2)))

    # Real-corpus smoke: the actual refrain template has (4,5) forced-same (the ABB)
    try:
        import corpus as corpus_mod
        c = corpus_mod.load()
        Mr = [list(x) for x in c.ciphertexts]
        rtmpl = tp.extract(Mr, rf.DEFAULT_INSTANCES, rf.DEFAULT_LEN, c.N)
        rmap = double_letter_map(rtmpl)
        out.append(("real refrain: (4,5) is the forced double (ABB)",
                    rmap.get((4, 5)) == "forced-same"))
        rforced, _ = double_positions(rtmpl)
        out.append(("real refrain: (4,5) only forced adjacency double",
                    rforced == [(4, 5)]))
        out.append(("real refrain: 'eye' rejected at offset 3 (XYX vs ABB)",
                    3 not in anchor_offsets("eye", rtmpl)))
        out.append(("real refrain: 'see' allowed at offset 3 (XYY = ABB)",
                    3 in anchor_offsets("see", rtmpl)))
    except Exception as e:
        out.append((f"real corpus smoke: {e}", False))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} refrain_compose checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
