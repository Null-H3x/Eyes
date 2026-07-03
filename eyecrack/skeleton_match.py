#!/usr/bin/env python3
"""skeleton_match.py -- constrain crib phrases by the refrain's own structure.

THE IDEA
========
The two shared refrains (Triplet 1: E1/W1/E2, and Triplet 3: E4/W4/E5)
are model-free anchors: because "same glyph = same plaintext character"
holds under ANY substitution model (including homophonic), the repeated
glyphs inside a refrain FORCE letter-equalities on whatever the plaintext
is.  A candidate crib that violates even one forced equality is impossible,
no matter how in-voice it sounds.  This module turns those forced
equalities into a fast filter so you sweep a phrase bank instead of
hand-testing phrases one at a time.

WHAT THE CORPUS FORCES (extracted live in build_skeletons(), not hardcoded)
===========================================================================
Position 0 of each refrain is message-specific (it differs across the three
members -- a label/index), so the shared crib begins at position 1.

  Triplet 1 -- refrain length 24 (positions 1..24), forced equalities:
      pos1  == pos12   (glyph 66)
      pos4  == pos13   (glyph 62)
      pos5  == pos22   (glyph 13)
      pos7  == pos21   (glyph 29)

  Triplet 3 -- refrain length 20 (positions 1..20), forced equalities:
      pos2  == pos19   (glyph 5)
      pos6  == pos10   (glyph 2)

CROSS-REFRAIN ANCHOR (the strong, non-obvious constraint)
=========================================================
Both refrains OPEN WITH THE SAME TWO GLYPHS: 66 then 5.  So under one
consistent alphabet the two cribs share their first two characters, and
glyph 5 (T1 pos2, T3 pos2 & pos19) and glyph 66 (T1 pos1 & pos12, T3 pos1)
tie the two phrases together.  A joint hypothesis therefore fits BOTH
openers with the same leading bigram -- a much sharper test than either
refrain alone.  cross_consistent() enforces it.

WHAT THIS DOES NOT ASSUME
=========================
* It forces only EQUALITIES (same glyph -> same letter).  It does NOT force
  inequalities: two DIFFERENT glyphs may still be the same letter if the
  cipher is homophonic (which the N=83 >> 26 alphabet strongly suggests).
  So a phrase with repeated letters at non-repeated-glyph positions is NOT
  rejected -- correctly, because homophones allow it.  --strict-injective
  adds the (риск) inequality assumption for users who want a monoalphabetic
  filter; off by default.
* Spaces: the refrain shows NO space-like glyph (no value repeats 4+ times
  at word-boundary gaps), so the default target treats the plaintext as
  letters-only, no encoded spaces -- phrases are matched with spaces
  stripped.  --with-spaces flips this if you later find a space glyph.

USAGE
=====
    # score hand phrases against T1
    python3 skeleton_match.py --triplet T1 --phrases "..." "..."
    # sweep a phrase bank file (one phrase per line)
    python3 skeleton_match.py --triplet T1 --bank phrases.txt
    # compose phrases from a wordlist and sweep (2-6 words, len-filtered)
    python3 skeleton_match.py --triplet T1 --compose eyestat/noita_wordlist.txt
    # joint T1+T3 with the shared 66,5 opener enforced
    python3 skeleton_match.py --joint --compose eyestat/noita_wordlist.txt

Survivors are the ONLY phrases worth the expensive cross-message
consistency check (eyecrack/crib_fit.py); this module is the cheap
pre-filter in front of it.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
_CORE = HERE.parent / "noita_eye_core" if (HERE.parent / "noita_eye_core").exists() \
    else HERE / "noita_eye_core"
for p in (_CORE,):
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))


@dataclass
class Skeleton:
    """A refrain's forced structure."""
    name: str
    members: Tuple[str, str, str]
    pos0: Tuple[int, int, int]          # the message-specific leading glyphs
    length: int                          # refrain length (chars, pos1..length)
    glyphs: Tuple[int, ...]              # the shared glyph values, pos1..length
    equalities: List[Tuple[int, int]]    # 1-indexed (a,b): letter[a]==letter[b]

    def check(self, phrase: str, strict_injective: bool = False
              ) -> Tuple[bool, str]:
        """Return (passes, normalized) for a phrase against this skeleton.
        Phrase is normalized to lowercase, spaces stripped, must equal length.
        """
        s = _norm(phrase)
        if len(s) != self.length:
            return False, s
        for a, b in self.equalities:
            if s[a - 1] != s[b - 1]:
                return False, s
        if strict_injective:
            # different glyph -> different letter (monoalphabetic assumption)
            g2l: Dict[int, str] = {}
            l2g: Dict[str, int] = {}
            for i, g in enumerate(self.glyphs):
                ch = s[i]
                if g in g2l and g2l[g] != ch:
                    return False, s
                if ch in l2g and l2g[ch] != g:
                    return False, s
                g2l[g] = ch
                l2g[ch] = g
        return True, s


def _norm(text: str) -> str:
    return "".join(c for c in text.lower() if c.isalpha())


def build_skeletons() -> Dict[str, Skeleton]:
    """Extract skeletons live from the corpus (never hardcoded)."""
    import corpus as cm
    from collections import defaultdict
    c = cm.load()
    cts = [list(x) for x in c.ciphertexts]
    labels = ["E1", "W1", "E2", "W2", "E3", "W3", "E4", "W4", "E5"]

    def one(name: str, idxs: Tuple[int, int, int]) -> Skeleton:
        a, b, d = (cts[i] for i in idxs)
        L = min(len(a), len(b), len(d))
        k = 1
        while k < L and a[k] == b[k] == d[k]:
            k += 1
        refrain = tuple(a[1:k])                       # pos1..k-1
        pos = defaultdict(list)
        for i, v in enumerate(refrain):
            pos[v].append(i + 1)                      # 1-indexed
        eqs: List[Tuple[int, int]] = []
        for v, ps in sorted(pos.items()):
            for j in range(len(ps) - 1):
                eqs.append((ps[0], ps[j + 1]))
        return Skeleton(name, tuple(labels[i] for i in idxs),
                        (a[0], b[0], d[0]), len(refrain), refrain, eqs)

    return {"T1": one("T1", (0, 1, 2)), "T3": one("T3", (6, 7, 8))}


def cross_consistent(s1: str, s3: str, sk1: Skeleton, sk3: Skeleton
                     ) -> bool:
    """Both refrains share leading glyphs (66,5,...) and glyph 5/66 recur
    across them.  A joint crib pair must assign the SAME letter everywhere
    the SAME glyph appears in either refrain.  Build the glyph->letter map
    from both and require consistency."""
    g2l: Dict[int, str] = {}
    for sk, s in ((sk1, s1), (sk3, s3)):
        if len(s) != sk.length:
            return False
        for i, g in enumerate(sk.glyphs):
            ch = s[i]
            if g in g2l and g2l[g] != ch:
                return False
            g2l[g] = ch
    return True


# ---------------------------------------------------------------------------
# phrase sources
# ---------------------------------------------------------------------------
def load_bank(path: str) -> List[str]:
    out = []
    for line in Path(path).read_text(encoding="utf-8",
                                     errors="ignore").splitlines():
        t = line.strip()
        if t and not t.startswith("#"):
            out.append(t)
    return out


def load_words(path: str, min_len: int = 2, max_len: int = 14) -> List[str]:
    ws = []
    for line in Path(path).read_text(encoding="utf-8",
                                     errors="ignore").splitlines():
        t = line.strip().lower()
        if t and not t.startswith("#") and t.isalpha():
            if min_len <= len(t) <= max_len:
                ws.append(t)
    # dedupe, keep order
    seen = set()
    return [w for w in ws if not (w in seen or seen.add(w))]


def compose_phrases(words: Sequence[str], target_len: int,
                    max_words: int = 6, cap: int = 5_000_000
                    ) -> Iterator[str]:
    """Yield space-joined word sequences whose stripped length == target_len.

    Length-bucketed DFS: at each step only extend with words that can still
    reach the target, so the search stays near the length shell instead of
    exploding.  cap bounds total yields."""
    by_len: Dict[int, List[str]] = {}
    for w in words:
        by_len.setdefault(len(w), []).append(w)
    lengths = sorted(by_len)
    yielded = 0

    def rec(remaining: int, depth: int, acc: List[str]) -> Iterator[str]:
        nonlocal yielded
        if yielded >= cap:
            return
        if remaining == 0:
            if acc:
                yield " ".join(acc)
                yielded += 1
            return
        if depth >= max_words or remaining < 0:
            return
        for L in lengths:
            if L > remaining:
                break
            for w in by_len[L]:
                yield from rec(remaining - L, depth + 1, acc + [w])
                if yielded >= cap:
                    return

    yield from rec(target_len, 0, [])


def slide_windows(text: str, length: int) -> Iterator[str]:
    """Slide a length-char window over DESPACED text, yielding each window.

    This is the high-value phrase source: real running text (game strings,
    the hidden messages, alchemical sources, Finnish/Karelian corpora) is
    far more likely to contain the true refrain than composed word-salad.
    We despace so the window is `length` LETTERS (the default no-space
    plaintext convention); punctuation/digits are dropped too."""
    letters = _norm(text)
    for i in range(0, len(letters) - length + 1):
        yield letters[i:i + length]


def slide_bank(paths: Sequence[str], length: int) -> Iterator[Tuple[str, str]]:
    """Yield (source_line, window) over every line of every file."""
    for path in paths:
        for ln in Path(path).read_text(encoding="utf-8",
                                       errors="ignore").splitlines():
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            for w in slide_windows(ln, length):
                yield ln, w


# ---------------------------------------------------------------------------
# sweep drivers
# ---------------------------------------------------------------------------
def sweep_single(sk: Skeleton, phrases: Iterable[str],
                 strict_injective: bool = False) -> List[str]:
    out = []
    for ph in phrases:
        ok, s = sk.check(ph, strict_injective=strict_injective)
        if ok:
            out.append(ph)
    return out


def sweep_joint(sk1: Skeleton, sk3: Skeleton, words: Sequence[str],
                max_words: int = 6, cap: int = 2_000_000,
                strict_injective: bool = False) -> List[Tuple[str, str]]:
    """Phrases fitting T1 whose leading letters are compatible with a T3 fit.

    We first collect T1 survivors and T3 survivors independently (cheap),
    then keep the cross-consistent pairs (shared glyphs 66,5 -> same
    letters).  Because both refrains start 66,5, the pair must agree on at
    least the first two characters; cross_consistent() enforces the full
    shared-glyph map."""
    t1 = sweep_single(sk1, compose_phrases(words, sk1.length, max_words, cap),
                      strict_injective)
    t3 = sweep_single(sk3, compose_phrases(words, sk3.length, max_words, cap),
                      strict_injective)
    # index T3 survivors by leading bigram for a fast join
    from collections import defaultdict
    t3_by_prefix = defaultdict(list)
    for p in t3:
        t3_by_prefix[_norm(p)[:2]].append(p)
    pairs = []
    for p1 in t1:
        pref = _norm(p1)[:2]
        for p3 in t3_by_prefix.get(pref, ()):
            if cross_consistent(_norm(p1), _norm(p3), sk1, sk3):
                pairs.append((p1, p3))
    return pairs


# ---------------------------------------------------------------------------
# selftest
# ---------------------------------------------------------------------------
def selftest() -> List[Tuple[str, bool]]:
    checks: List[Tuple[str, bool]] = []
    sks = build_skeletons()
    t1, t3 = sks["T1"], sks["T3"]

    # (1) skeleton lengths and leading-glyph facts match the corpus finding.
    checks.append((f"T1 length 24, T3 length 20 "
                   f"({t1.length},{t3.length})",
                   t1.length == 24 and t3.length == 20))
    checks.append(("both refrains open with glyphs 66,5",
                   t1.glyphs[:2] == (66, 5) and t3.glyphs[:2] == (66, 5)))
    checks.append(("pos0 differs per member (message-specific)",
                   len(set(t1.pos0)) > 1 and len(set(t3.pos0)) > 1))

    # (2) forced equalities match the hand-derived set for T1.
    checks.append((f"T1 equalities = {t1.equalities}",
                   set(t1.equalities) ==
                   {(1, 12), (4, 13), (5, 22), (7, 21)}))
    checks.append((f"T3 equalities = {t3.equalities}",
                   set(t3.equalities) == {(2, 19), (6, 10)}))

    # (3) a CONSTRUCTED plaintext that literally IS the glyph pattern passes;
    #     one that breaks a single equality fails.
    # Build a passing string: assign each distinct glyph a distinct letter.
    def synth(sk):
        alpha = "abcdefghijklmnopqrstuvwxyz"
        m = {}
        nxt = 0
        s = []
        for g in sk.glyphs:
            if g not in m:
                m[g] = alpha[nxt % 26]
                nxt += 1
            s.append(m[g])
        return "".join(s)
    good = synth(t1)
    ok_good, _ = t1.check(good, strict_injective=True)
    checks.append(("synthesized true-pattern passes (strict)", ok_good))
    # break equality (1,12): change char at pos12 only
    bad = list(good)
    bad[11] = "z" if bad[11] != "z" else "q"
    ok_bad, _ = t1.check("".join(bad))
    checks.append(("breaking one equality fails", not ok_bad))

    # (4) homophonic tolerance: a phrase with a repeated LETTER at positions
    #     whose GLYPHS differ must still PASS in default (non-strict) mode
    #     and FAIL under --strict-injective.
    base = list(synth(t1))
    # positions 2 and 3 have different glyphs (5 vs 48); force same letter
    base[1] = base[2]
    phrase = "".join(base)
    ok_default, _ = t1.check(phrase, strict_injective=False)
    ok_strict, _ = t1.check(phrase, strict_injective=True)
    checks.append(("homophonic repeat: passes default, fails strict",
                   ok_default and not ok_strict))

    # (5) length filter: wrong-length phrase rejected.
    ok_len, _ = t1.check("too short", strict_injective=False)
    checks.append(("wrong length rejected", not ok_len))

    # (6) compose_phrases hits the exact target length and respects max_words.
    words = ["the", "work", "begins", "seeker", "of", "wisdom", "aa", "bb"]
    comp = list(compose_phrases(words, 10, max_words=3, cap=1000))
    ok = all(len(_norm(p)) == 10 for p in comp) and len(comp) > 0
    checks.append((f"compose hits target length ({len(comp)} phrases)", ok))

    # (7) cross_consistent: identical shared-glyph letters pass; a clash on
    #     glyph 66 (T1 pos1 / T3 pos1) fails.  Build s3 so that EVERY shared
    #     glyph (66, 5) carries the same letter as in s1, at all occurrences.
    s1 = synth(t1)
    s1_map: Dict[int, str] = {}
    for i, g in enumerate(t1.glyphs):
        s1_map.setdefault(g, s1[i])
    # synth T3 but seed its glyph->letter map with T1's shared assignments
    def synth_seeded(sk, seed_map):
        # test helper: preserve seeded shared-glyph letters; give every other
        # distinct glyph a distinct symbol.  Uses a wide symbol pool so it
        # cannot exhaust (T1 has up to 24 distinct glyphs).
        pool = ("abcdefghijklmnopqrstuvwxyz"
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        m = dict(seed_map)
        used = set(m.values())
        it = (ch for ch in pool if ch not in used)
        out = []
        for g in sk.glyphs:
            if g not in m:
                ch = next(it)
                m[g] = ch
                used.add(ch)
            out.append(m[g])
        return "".join(out)
    # ALL shared glyphs must agree (T1 & T3 share seven: 2,5,15,29,49,66,75),
    # not just the 66,5 opener -- that is the real strength of the joint test.
    s3_ok = synth_seeded(t3, {g: s1_map[g] for g in set(t1.glyphs)
                              if g in s1_map})
    ok_pair = cross_consistent(s1, s3_ok, t1, t3)
    # clash: force glyph 66 in T3 to a different letter at BOTH... only pos1
    s3bad = list(s3_ok)
    s3bad[0] = "z" if s1[0] != "z" else "q"   # clash glyph66 (T3 pos1 only)
    ok_clash = cross_consistent(s1, "".join(s3bad), t1, t3)
    checks.append(("cross-consistent agrees on 66,5; clash rejected",
                   ok_pair and not ok_clash))

    # (8) determinism.
    checks.append(("skeletons deterministic",
                   build_skeletons()["T1"].equalities == t1.equalities))
    return checks


def _run_selftest() -> int:
    ok = True
    for name, passed in selftest():
        print(f"[{'OK  ' if passed else 'FAIL'}] {name}")
        ok &= passed
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--triplet", choices=["T1", "T3"], default="T1")
    ap.add_argument("--joint", action="store_true",
                    help="fit T1 and T3 jointly via the shared 66,5 opener")
    ap.add_argument("--phrases", nargs="*", default=None)
    ap.add_argument("--bank", default=None, help="file: one phrase per line")
    ap.add_argument("--compose", default=None,
                    help="wordlist file: compose phrases to target length")
    ap.add_argument("--slide", nargs="*", default=None,
                    help="text file(s): slide a length-window over real prose "
                         "(despaced) -- the high-value source")
    ap.add_argument("--max-words", type=int, default=6)
    ap.add_argument("--cap", type=int, default=2_000_000)
    ap.add_argument("--strict-injective", action="store_true",
                    help="assume monoalphabetic (different glyph->different "
                         "letter); off by default since N=83>>26 suggests "
                         "homophonic")
    ap.add_argument("--limit-out", type=int, default=60)
    args = ap.parse_args()
    if args.selftest:
        return _run_selftest()

    sks = build_skeletons()

    if args.joint:
        if not args.compose:
            print("--joint requires --compose WORDLIST", file=sys.stderr)
            return 2
        words = load_words(args.compose)
        print(f"[joint] words={len(words)}  T1 len={sks['T1'].length}  "
              f"T3 len={sks['T3'].length}  (shared opener 66,5)")
        pairs = sweep_joint(sks["T1"], sks["T3"], words,
                            max_words=args.max_words, cap=args.cap,
                            strict_injective=args.strict_injective)
        print(f"[joint] {len(pairs)} cross-consistent (T1,T3) pairs")
        for p1, p3 in pairs[:args.limit_out]:
            print(f"   T1: {p1!r}")
            print(f"   T3: {p3!r}")
            print()
        return 0

    sk = sks[args.triplet]
    print(f"[{sk.name}] members={sk.members} refrain_len={sk.length} "
          f"equalities={sk.equalities}")
    print(f"[{sk.name}] leading glyphs: {sk.glyphs[:6]}...")

    if args.phrases:
        survivors = sweep_single(sk, args.phrases, args.strict_injective)
        for ph in args.phrases:
            ok, s = sk.check(ph, args.strict_injective)
            print(f"   [{'PASS' if ok else 'fail'}] len={len(s):2} {ph!r}")
        return 0

    if args.bank:
        phrases = load_bank(args.bank)
        survivors = sweep_single(sk, phrases, args.strict_injective)
        print(f"[{sk.name}] bank={len(phrases)} -> {len(survivors)} survivors")
        for ph in survivors[:args.limit_out]:
            print(f"   {ph!r}")
        return 0

    if args.slide:
        seen = {}
        n_win = 0
        for src, w in slide_bank(args.slide, sk.length):
            n_win += 1
            ok, s2 = sk.check(w, args.strict_injective)
            if ok:
                seen.setdefault(w, src)
        print(f"[{sk.name}] slid {n_win} windows over {len(args.slide)} "
              f"file(s) -> {len(seen)} distinct survivors")
        for w, src in list(seen.items())[:args.limit_out]:
            print(f"   {w!r}   <= {src[:60]!r}")
        return 0

    if args.compose:
        words = load_words(args.compose)
        phrases = compose_phrases(words, sk.length, args.max_words, args.cap)
        survivors = sweep_single(sk, phrases, args.strict_injective)
        print(f"[{sk.name}] composed from {len(words)} words -> "
              f"{len(survivors)} survivors (cap {args.cap})")
        for ph in survivors[:args.limit_out]:
            print(f"   {ph!r}")
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
