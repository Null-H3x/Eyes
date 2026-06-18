#!/usr/bin/env python3
"""EyeCrack — crib-placement tester for the repeated maximal-aligned isomorphs.

Throw candidate plaintext phrases at the extractor's certified same-plaintext
targets (default: the 4x repeated 15-glyph segment in West 1 / East 2) and see
whether they can fit, under the per-message-progressive model
    x[c_m[pos+i]] = p[i] + base_m + pos + i.

TWO modes (the tool always shows the calibrated NULL so you can't be fooled):

  PATTERN (value-free): uses only your phrase's letter-equality pattern. This is
    PERMISSIVE for a sliding cipher (the ciphertext repeat pattern reflects p[i]+i,
    not p[i]) — most phrases "pass", so it is NOT decisive on its own.

  VALUE (sharp): also commits to a plaintext-alphabet ORDERING (letter -> value),
    given by --alphabet. Placement at all 4 instances + consistency with the
    already-extracted corpus alphabet is razor-sharp — a random phrase passes ~0%.
    A phrase+ordering that passes AND extends the corpus is strong joint evidence.

Examples:
    python3 crib_fit.py "doyoubelieve" "threeeyeswatch"
    python3 crib_fit.py --wordlist mywords.txt
    python3 crib_fit.py --alphabet "abcdefghijklmnopqrstuvwxyz" "seekertruth..."
    python3 crib_fit.py --list-targets
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import cribfit                # noqa: E402

DEFAULT_ALPHABET = "abcdefghijklmnopqrstuvwxyz"


def norm(text: str) -> str:
    return re.sub(r"[^a-z]", "", text.lower())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("phrases", nargs="*", help="candidate plaintext phrases")
    ap.add_argument("--wordlist", help="file of candidate phrases (one per line)")
    ap.add_argument("--alphabet", default=DEFAULT_ALPHABET,
                    help="plaintext ordering letter->value (position = value); "
                         "default a-z (a HYPOTHESIS — change it to test others)")
    ap.add_argument("--target", type=int, default=0,
                    help="target index from --list-targets (default 0 = largest)")
    ap.add_argument("--list-targets", action="store_true")
    ap.add_argument("--null", type=int, default=500, help="random cribs for calibration")
    args = ap.parse_args()

    c = corpus_mod.load()
    N = c.N
    M = [list(x) for x in c.ciphertexts]
    targets = cribfit.find_targets(M, N=N)

    print("=" * 70)
    print("EYECRACK — crib-placement tester (repeated aligned-isomorph targets)")
    print("=" * 70)
    if not targets:
        print("No clean repeated-isomorph targets found.")
        return 1
    if args.list_targets:
        for i, t in enumerate(targets):
            locs = ", ".join(f"{c.labels[m]}@{p}" for m, p in t.instances)
            print(f"  [{i}] L={t.length}  {len(t.instances)} instances: {locs}")
        return 0

    tgt = targets[args.target]
    locs = ", ".join(f"{c.labels[m]}@{p}" for m, p in tgt.instances)
    print(f"Target [{args.target}]: L={tgt.length}, {len(tgt.instances)} instances "
          f"({locs})")
    print(f"Ciphertext skeleton: {tgt.skeleton}")
    print(f"Plaintext-alphabet hypothesis (--alphabet): '{args.alphabet}'")
    print()

    corpus_gf = cribfit._corpus_gf(M, N)

    phrases = list(args.phrases)
    if args.wordlist:
        phrases += [ln.strip() for ln in Path(args.wordlist).read_text().splitlines()
                    if ln.strip()]
    if not phrases:
        print("No phrases given. Pass phrases as arguments or use --wordlist.")
        print("Tip: --list-targets to see all targets.")
        return 0

    L = tgt.length
    print(f"{'candidate':24s} {'off':>3} {'PATTERN':>8} {'VALUE':>7} "
          f"{'+corpus':>8} {'null':>6}  verdict")
    print("-" * 78)
    for raw in phrases:
        s = norm(raw)
        if len(s) < L:
            print(f"{raw[:24]:24s}  --  too short ({len(s)}<{L})")
            continue
        # slide a window of length L; report the strongest placement
        best = None
        for off in range(len(s) - L + 1):
            sub = s[off:off + L]
            patt = cribfit.letter_pattern(sub)
            rp = cribfit.test_pattern(tgt, patt, M, N, n_null=args.null)
            vals = cribfit.letters_to_values(sub, args.alphabet)
            rv = (cribfit.test_value(tgt, vals, M, N, corpus_gf=corpus_gf,
                                     n_null=args.null) if vals is not None else None)
            score = (rv.consistent and rv.extends_corpus) if rv else False
            cand = (off, sub, rp, rv, score)
            if best is None or (score and not best[4]):
                best = cand
        off, sub, rp, rv, score = best
        pat = "fits" if rp.consistent else "no"
        if rv is None:
            valc, ext, nul = "n/a", "n/a", rp.null_rate
            verdict = "needs letters in --alphabet"
        else:
            valc = "fits" if rv.consistent else "no"
            ext = ("yes" if rv.extends_corpus else "no") if rv.consistent else "-"
            nul = rv.null_rate
            if rv.consistent and rv.extends_corpus:
                verdict = "CANDIDATE (sharp: extends corpus, null~%.0f%%)" % (nul * 100)
            elif rv.consistent:
                verdict = "fits 4x but NOT corpus -> likely coincidence"
            else:
                verdict = "rejected"
        print(f"{sub:24s} {off:>3} {pat:>8} {valc:>7} {ext:>8} {nul:>6.2f}  {verdict}")

    print("\nREAD:")
    print("  PATTERN 'fits' is near-automatic (permissive) — ignore it alone.")
    print("  VALUE 'fits' + '+corpus yes' with null~0 is the real signal: the")
    print("  phrase AND the --alphabet ordering jointly explain all instances and")
    print("  stay consistent with the extracted alphabet. Try alternate --alphabet")
    print("  orderings (Finnish, custom) — the ordering is itself a hypothesis.")
    print("  A 'fits 4x but NOT corpus' is almost certainly a local coincidence.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
