#!/usr/bin/env python3
"""EyeCrack — crib-seeded English n-gram solver.

Give it a refrain guess (placed in the 25-glyph repeat region). It pins the cipher
alphabet from the crib under the per-message-progressive model, hill-climbs the
residual symbols to maximise English character-trigram likelihood (searching each
message's base), and prints the resulting decryption + an order-sensitive z-score.

This is the productive successor to IoC hill-climbing (which is degenerate). It
needs the plaintext-alphabet ORDERING (--alphabet, default = noita-alphabet2 order)
as well as the crib; a wrong ordering fails even with the right crib, so try a few.

Usage:
    python3 ngram_solve.py "trueknowledge"                  # try at every offset
    python3 ngram_solve.py "trueknowledge" --off 0          # fix the offset
    python3 ngram_solve.py --wordlist cands.txt             # rank candidates by z
    python3 ngram_solve.py "seekeroftruth" --restarts 12 --iters 4000   # deeper
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
import alphabet_env as alph_env  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("phrases", nargs="*")
    ap.add_argument("--wordlist")
    ap.add_argument("--alphabet", default=None)
    ap.add_argument("--off", type=int, default=None, help="fix the offset (else sweep)")
    ap.add_argument("--restarts", type=int, default=6)
    ap.add_argument("--iters", type=int, default=1500)
    ap.add_argument("--null", type=int, default=60)
    ap.add_argument("--show", type=int, default=3)
    args = ap.parse_args()
    alphabet = args.alphabet or alph_env.resolve_alphabet(rf.DEFAULT_ALPHABET)

    c = corpus_mod.load()
    N = c.N
    M = [list(x) for x in c.ciphertexts]
    region = rf.DEFAULT_INSTANCES
    REGION = rf.DEFAULT_LEN
    model = ng.TrigramModel(alphabet, ng._ENGLISH)

    print("=" * 70)
    print("EYECRACK — crib-seeded English n-gram solver")
    print("=" * 70)
    print(f"Region: {[(c.labels[m], p) for m, p in region]} ({REGION} glyphs). "
          f"Model: English char-trigram. Ordering: '{alphabet[:36]}...'")

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
            continue
        offs = [args.off] if args.off is not None else \
            rf.viable_offsets(M, s, region, REGION, N)
        for off in offs:
            res = ng.solve(M, s, off, N, alphabet=alphabet, model=model,
                           region=region, restarts=args.restarts, iters=args.iters,
                           n_null=args.null)
            if res.consistent:
                rows.append((s, off, res))

    rows.sort(key=lambda x: x[2].z, reverse=True)
    print(f"\n{'phrase':16s} {'off':>3} {'pinned':>6} {'score':>8} {'z':>7}  verdict")
    print("-" * 64)
    for s, off, r in rows[:max(args.show, 15)]:
        verdict = ("STRONG — see decryption" if r.z >= 6 else
                   "promising" if r.z >= 4 else "weak" if r.z >= 2 else "noise")
        print(f"{s:16s} {off:>3} {r.pinned:>6} {r.score:>8.3f} {r.z:>7.2f}  {verdict}")
    for s, off, r in rows[:args.show]:
        if r.z >= 4:
            print(f"\n--- best decryption under '{s}' @off {off} (z={r.z:.2f}) ---")
            for mi in range(len(M)):
                print(f"  {c.labels[mi]}: {r.plaintext.get(mi, '')}")
    if not rows:
        print("  (no candidate was consistent at any viable offset under this ordering)")
    print("\nREAD: z = trigram order-structure vs shuffled decryption. z>>6 means the")
    print("WHOLE corpus reads as English under this (crib, ordering) — a real break.")
    print("Low z under this ordering may mean wrong ordering, not wrong phrase.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
