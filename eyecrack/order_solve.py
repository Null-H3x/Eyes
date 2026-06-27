#!/usr/bin/env python3
"""EyeCrack — ordering-search solver (recovers the alphabet ordering from a crib).

Unlike ngram_solve, this does NOT need the value->character ordering: it pins the
alphabet structure ordering-free from the crib's letter-pattern + ciphertext, then
hill-climbs the ordering O + per-message bases by English character-trigram
likelihood, with a dictionary word-coverage acceptance gate.

It is a DIAGNOSTIC, not a yes/no oracle. For each (crib, offset) it reports:
  - consistency / contradiction slot (ordering-free — narrows the real refrain),
  - z = n-gram order-structure vs shuffled decryption (warmer/colder gradient),
  - word-coverage + the actual dictionary words recovered (the acceptance gate),
  - the decryption itself (partial readouts reveal which symbols are right).

IMPORTANT (validated): a crib must be long enough to pin DISTINCT plaintext values
— roughly the full ~25-glyph region. A 13-letter crib UNDER-DETERMINES the alphabet
(distinct letters collapse onto the same value), so it gives diagnostics but cannot
fully read out. Extend promising 13-letter guesses toward the full refrain.

Usage:
    python3 order_solve.py "trueknowledgeofthegods"      # ~full-region crib
    python3 order_solve.py --wordlist cands.txt
    python3 order_solve.py "trueknowledge" --off 6        # fix offset
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import refrain as rf          # noqa: E402
import ngram_solve as ng      # noqa: E402
import order_solve as os_     # noqa: E402
import alphabet_env as alph_env  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("phrases", nargs="*")
    ap.add_argument("--wordlist")
    ap.add_argument("--alphabet", default=None,
                    help="83-char plaintext alphabet (or set EYES_ALPHABET)")
    ap.add_argument("--off", type=int, default=None)
    ap.add_argument("--restarts", type=int, default=4)
    ap.add_argument("--iters", type=int, default=3000)
    ap.add_argument("--null", type=int, default=30)
    ap.add_argument("--show", type=int, default=3)
    args = ap.parse_args()

    c = corpus_mod.load()
    N = c.N
    M = [list(x) for x in c.ciphertexts]
    region = rf.DEFAULT_INSTANCES
    REGION = rf.DEFAULT_LEN
    alphabet = args.alphabet or alph_env.resolve_alphabet(rf.DEFAULT_ALPHABET)
    model = ng.TrigramModel(alphabet, ng._ENGLISH)

    print("=" * 70)
    print("EYECRACK — ordering-search solver (crib -> alphabet ordering, English)")
    print("=" * 70)
    print(f"Region {[(c.labels[m], p) for m, p in region]} ({REGION} glyphs). "
          f"Crib should approach the full region to pin distinct values.")

    phrases = list(args.phrases)
    if args.wordlist:
        phrases += [ln.strip() for ln in Path(args.wordlist).read_text().splitlines()
                    if ln.strip()]
    if not phrases:
        print("\nNo phrases. Pass guesses or --wordlist.")
        return 0

    rows = []
    for raw in phrases:
        s = raw
        if len(s) < 3 or len(s) > REGION:
            print(f"  {s[:24]:24s} (skip: length must be 3..{REGION})")
            continue
        offs = [args.off] if args.off is not None else \
            rf.viable_offsets(M, s, region, REGION, N)
        if not offs:
            print(f"  {s:22s} no viable offset (letter-pattern incompatible)")
            continue
        best = None
        for off in offs:
            r = os_.solve(M, s, off, N, alphabet=alphabet, model=model,
                          region=region, restarts=args.restarts, iters=args.iters,
                          n_null=args.null)
            if r.consistent and (best is None or r.z > best[1].z):
                best = (off, r)
        if best is None:
            print(f"  {s:22s} contradiction at all viable offsets")
            continue
        rows.append((s, best[0], best[1]))

    rows.sort(key=lambda x: x[2].z, reverse=True)
    print(f"\n{'phrase':22s} {'off':>3} {'pin':>4} {'cov':>4} {'z':>6} {'wcov':>5}  words")
    print("-" * 74)
    for s, off, r in rows:
        hits = os_._word_hits(" ".join(r.plaintext.values()))
        verdict = ", ".join(hits[:6]) if hits else "(none)"
        print(f"{s:22s} {off:>3} {r.symbols_pinned:>4} {r.coverage:>3.0%} "
              f"{r.z:>6.1f} {r.word_coverage:>4.0%}  {verdict}")
    for s, off, r in rows[:args.show]:
        if r.z >= 8 or r.word_coverage >= 0.2:
            print(f"\n--- decryption under '{s}' @off {off} (z={r.z:.1f}, "
                  f"word-cov={r.word_coverage:.0%}) ---")
            for mi in range(len(M)):
                print(f"  {c.labels[mi]}: {r.plaintext.get(mi, '')}")
    if not rows:
        print("  (no candidate consistent at any viable offset)")
    print("\nREAD: z = English order-structure; words = dictionary hits (the real")
    print("gate). A genuine refrain reads coherently AND yields many words. A short")
    print("(13-letter) crib under-determines the alphabet — extend it toward the full")
    print("~25-glyph region for a real read-out.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
