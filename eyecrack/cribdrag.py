#!/usr/bin/env python3
"""EyeCrack crib-drag — two-time-pad crib search over the unknown alphabet.

Drags candidate word-tuples across each per-triplet family and keeps the
mutually-consistent ones, ranked by *evidence* (independent 1/N coincidences
survived).  Mapping-free and keystream-free: it uses only ciphertext differences.

    python3 cribdrag.py                       # default Noita wordlist
    python3 cribdrag.py --words tree,free,blood,three,devoted --min-redundant 4
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import cribdrag               # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="two-time-pad crib-drag")
    ap.add_argument("--words", default="",
                    help="comma list (default: the Noita candidate wordlist)")
    ap.add_argument("--min-len", type=int, default=4)
    ap.add_argument("--require-distinct", type=int, default=2,
                    help="distinct words required in a tuple (3 = all members)")
    ap.add_argument("--min-redundant", type=int, default=3,
                    help="minimum evidence (1/N coincidences) to report")
    ap.add_argument("--top", type=int, default=25)
    args = ap.parse_args()

    c = corpus_mod.load()
    words = ([w.strip() for w in args.words.split(",") if w.strip()]
             if args.words else cribdrag.DEFAULT_WORDS)
    msgs = [list(ct) for ct in c.ciphertexts]

    print("=" * 70)
    print("EYECRACK — crib-drag (two-time-pad over an unknown alphabet)")
    print("=" * 70)
    print(f"words: {sorted(set(w for w in words if len(w) >= args.min_len))}")
    print(f"per-triplet families: {cribdrag.TRIPLETS}\n")

    res = cribdrag.search_corpus(c, words=words, min_len=args.min_len,
                                 require_distinct=args.require_distinct,
                                 min_redundant=args.min_redundant, top=args.top)

    # Decoy false-positive rate per family (random words, same lengths) gives a
    # multiple-testing-aware sense of whether a hit is surprising.
    lengths = sorted({len(w) for w in words if len(w) >= args.min_len})
    fp = {fam: cribdrag.decoy_rate(msgs, fam, c.N, lengths, n_decoys=800, seed=9)
          for fam in cribdrag.TRIPLETS}

    if not res:
        print("No placements clear the evidence threshold. That is a result: the "
              "candidate wordlist yields no consistent crib at any position.")
        return 0

    print(f"{len(res)} placement(s), ranked by evidence (each unit ~ 1/{c.N} "
          f"coincidence ~ {math.log10(c.N):.1f} decimal orders):\n")
    print("  family            pos  L  evidence  words")
    for p in res:
        fam = "+".join(c.labels[i][:2] for i in p.family)
        print(f"  {fam:16} {p.start:>4} {p.length:>2}  {p.redundant:>8}  "
              f"{p.words}")

    print("\nfalse-positive (decoy) rate per family at these lengths:")
    for fam, r in fp.items():
        print(f"  {fam}: {r:.2%}")

    best = res[0]
    # Honest verdict.
    distinct_top = best.distinct_words
    print()
    if best.redundant >= 6 and distinct_top == 3:
        print("=> STRONG candidate: long, all-three-distinct, high evidence. "
              "Resolve the per-component offsets (try the third member / seed) "
              "and feed the keystream to `structscan --crib`.")
    else:
        print("=> No confident crib. The surviving placements are short and/or "
              "carry interchangeable words (e.g. tree<->free share a repeat-"
              "skeleton), so this is a lead at best, not a confirmation. "
              "Stronger cribs (longer, all-three-distinct, repeat-rich) or a "
              "language/mapping anchor are needed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
