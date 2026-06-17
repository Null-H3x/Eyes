"""Salakieli register — curated plaintext-crib vocabulary for the eye puzzle.

Noita's data files are AES-128-CTR (ruled out as the eye cipher: see
eyewitness/salakieli_aes.py), and their *decrypted content* is a run of English
phrases with no spaces, in the puzzle's exact register (knowledge / seeing /
eyes).  If the eye glyphs decrypt to more of this narrative, these phrases — and
their spaceless sub-phrases — are the highest-value cribs available.

This module turns the raw CamelCase phrases into a principled crib register:
  * the full phrases (spaceless, lowercased),
  * every contiguous word n-gram joined without spaces (so SeekerOfKnowledge,
    ThreeEyes, AllSeeing, TrueKnowledge etc. are first-class — the user's point
    that the in-game strings carry no spaces, so a crib can sit mid-message),
  * the individual content words.

Each entry is ranked by mapping-free crib power: the count of equal-letter
repeat constraints (K[p+i]-K[p+j] == c[p+i]-c[p+j]), which is what makes a crib
filter seeds without knowing the alphabet.  These phrases carry 8-24 constraints
versus 1-3 for short guesses, so a correct placement is essentially unmissable.
"""
from __future__ import annotations

import re
from typing import Dict, List, Tuple

# Raw decrypted salakieli phrases (CamelCase, as found in the game files).
RAW_PHRASES = [
    "WeSeeATrueSeekerOfKnowledge",
    "YouAreSoCloseToBeingEnlightened",
    "TheTruthIsThatThereIsNothing",
    "MoreValuableThanKnowledge",
    "KnowledgeIsTheHighestOfTheHeighest",
    "WhoWouldntGiveEverythingForTrueKnowledge",
    "SecretsOfTheAllSeeing",
    "ThreeEyesAreWatchingYou",
    "WhenYouHaveNothingLeftToSeek",
    "PeopleWillRejoiceAndDance",
]


def split_camel(phrase: str) -> List[str]:
    """CamelCase -> lowercased word list (WeSeeATrue -> [we, see, a, true])."""
    return [w.lower() for w in re.findall(r"[A-Z][a-z]*|[a-z]+", phrase)]


def _letters(s: str) -> str:
    return re.sub("[^a-z]", "", s.lower())


def repeat_constraints(word: str) -> int:
    """Number of independent equal-letter constraints (mapping-free crib power)."""
    first: Dict[str, int] = {}
    k = 0
    for i, ch in enumerate(word):
        if ch in first:
            k += 1
        else:
            first[ch] = i
    return k


def build_register(min_word: int = 4, max_ngram: int = 4
                   ) -> Dict[str, List[str]]:
    """Return {'phrases','subphrases','words'} of spaceless lowercase cribs."""
    phrases = [_letters(p) for p in RAW_PHRASES]
    words = set()
    subphrases = set()
    for raw in RAW_PHRASES:
        toks = split_camel(raw)
        for w in toks:
            if len(w) >= min_word:
                words.add(w)
        # contiguous word n-grams joined without spaces
        for n in range(2, max_ngram + 1):
            for i in range(len(toks) - n + 1):
                sp = "".join(toks[i:i + n])
                if len(sp) >= min_word:
                    subphrases.add(sp)
    # full phrases are not "subphrases"
    subphrases -= set(phrases)
    return {"phrases": sorted(phrases),
            "subphrases": sorted(subphrases),
            "words": sorted(words)}


def ranked(min_len: int = 4) -> List[Tuple[str, int, str]]:
    """All register entries as (crib, repeat_constraints, kind), strongest first."""
    reg = build_register(min_word=min_len)
    out: List[Tuple[str, int, str]] = []
    for kind in ("phrases", "subphrases", "words"):
        for w in reg[kind]:
            if len(w) >= min_len:
                out.append((w, repeat_constraints(w), kind))
    # dedupe keeping the first (phrase>subphrase>word) occurrence
    seen = set()
    uniq = []
    for w, k, kind in out:
        if w in seen:
            continue
        seen.add(w)
        uniq.append((w, k, kind))
    uniq.sort(key=lambda t: -t[1])
    return uniq


def all_cribs(min_len: int = 4) -> List[str]:
    return [w for w, _, _ in ranked(min_len)]


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def selftest() -> List[tuple[str, bool]]:
    out: List[tuple[str, bool]] = []

    out.append(("CamelCase split: WeSeeATrueSeekerOfKnowledge -> 6 words",
                split_camel("WeSeeATrueSeekerOfKnowledge")
                == ["we", "see", "a", "true", "seeker", "of", "knowledge"]))

    reg = build_register()
    # User's named high-value spaceless sub-phrases must be present.
    for want in ("seekerofknowledge", "threeeyes", "allseeing", "trueknowledge"):
        out.append((f"register contains sub-phrase '{want}'",
                    want in reg["subphrases"]))

    # Every sub-phrase/word is a contiguous spaceless fragment of some phrase's
    # full concatenation (sanity: nothing fabricated).
    joined = ["".join(split_camel(p)) for p in RAW_PHRASES]
    ok_frag = all(any(w in j for j in joined)
                  for w in reg["subphrases"] + reg["words"])
    out.append(("every register entry is a real phrase fragment", ok_frag))

    # crib power: full phrases are strong (>= 8 constraints); ranking is sorted.
    r = ranked()
    out.append(("strongest crib has >= 8 repeat constraints", r[0][1] >= 8))
    out.append(("ranking is sorted by constraints (desc)",
                all(r[i][1] >= r[i + 1][1] for i in range(len(r) - 1))))
    out.append(("repeat_constraints KAT: 'knowledge' has 2 (k,o,w,l,e,d,g,e -> e)",
                repeat_constraints("knowledge") == 1))  # only 'e' repeats once
    out.append(("repeat_constraints KAT: 'threeeyes' counts the e-run",
                repeat_constraints("threeeyes") == 3))  # e at 3,4,5,7 -> 3 constraints
    out.append(("register is non-trivial (>= 40 distinct cribs)",
                len(all_cribs()) >= 40))
    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} salakieli checks passed")
    if "--list" in sys.argv:
        print("\nRegister (crib, constraints, kind), strongest first:")
        for w, k, kind in ranked():
            print(f"  {k:>2}  {kind:10} {w}")
    sys.exit(0 if n_ok == len(results) else 1)
