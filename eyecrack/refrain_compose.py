#!/usr/bin/env python3
"""EyeCrack — anchored refrain composer.

Turns the refrain repeat-template into a GENERATIVE attack: place expected words
and fragments (word endings / internal doubles included) at template-compatible
offsets, then fill the rest with a character-trigram model ranked by dictionary
word-coverage (wcov). The honest payoff is a ranked SHORTLIST to feed order_solve,
not a decryption — reading still needs the glyph->char ordering.

Usage:
    python3 refrain_compose.py --doubles          # show where doubles are allowed
    python3 refrain_compose.py --offsets god eye see spirit   # compatible offsets
    python3 refrain_compose.py --compat god see   # joint placements (stacking)
    python3 refrain_compose.py --anchor see        # compose seeded by an anchor
    python3 refrain_compose.py --anchor god --anchor see --top 30
    python3 refrain_compose.py --wordlist ../eyestat/eng-wordlist.txt --anchor god
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CORE = ROOT / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod      # noqa: E402
import refrain as rf             # noqa: E402
import template as tp            # noqa: E402
import ngram_solve as ng         # noqa: E402
import refrain_compose as rc     # noqa: E402


def _load_wordset(path: str | None) -> set:
    if not path:
        return rc._DEFAULT_WORDS
    p = Path(path)
    if not p.is_file():
        for base in (HERE, ROOT, Path.cwd()):
            cand = base / path
            if cand.is_file():
                p = cand
                break
    ws = set()
    with open(p, encoding="utf-8", errors="replace") as f:
        for ln in f:
            w = "".join(c for c in ln.strip().lower() if c.isalpha())
            if 3 <= len(w) <= 22:
                ws.add(w)
    return ws or rc._DEFAULT_WORDS


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--doubles", action="store_true",
                    help="show which adjacent positions can hold a doubled letter")
    ap.add_argument("--offsets", nargs="*", metavar="WORD",
                    help="report template-compatible offsets for each word/fragment")
    ap.add_argument("--compat", nargs="*", metavar="WORD",
                    help="enumerate joint (stacked) placements for these anchors")
    ap.add_argument("--anchor", action="append", default=[], metavar="WORD",
                    help="anchor word/fragment to seed composition (repeatable)")
    ap.add_argument("--wordlist", help="wordlist for the wcov gate")
    ap.add_argument("--beam", type=int, default=1200)
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--wcov-weight", type=float, default=6.0)
    args = ap.parse_args()

    c = corpus_mod.load()
    M = [list(x) for x in c.ciphertexts]
    tmpl = tp.extract(M, rf.DEFAULT_INSTANCES, rf.DEFAULT_LEN, c.N)
    skel = tp.skeleton_string(tmpl)

    print("=" * 70)
    print("EYECRACK — anchored refrain composer")
    print("=" * 70)
    print(f"Template L={tmpl.L} dof={tmpl.dof}  skeleton: {skel}")
    print(f"Forced-same groups: {tmpl.same_groups}   free: {tmpl.free_positions}")
    print()

    did = False

    if args.doubles:
        did = True
        dmap = rc.double_letter_map(tmpl)
        forced, opt = rc.double_positions(tmpl)
        print("Adjacent-pair double-letter map:")
        for i in range(tmpl.L - 1):
            print(f"  ({i:2d},{i+1:2d}): {dmap[(i, i+1)]}")
        print(f"\nForced double (mandatory): {forced}")
        print(f"Optional doubles allowed:  {opt}")
        print("Every other adjacent pair is forced-different — NO double possible.")
        print()

    if args.offsets:
        did = True
        print("Template-compatible offsets (fragments/endings included):")
        for w in args.offsets:
            offs = rc.anchor_offsets(w, tmpl)
            print(f"  {w!r:18s} -> {offs}")
        print()

    if args.compat:
        did = True
        places = rc.compatible_placements(args.compat, tmpl, max_solutions=50)
        print(f"Joint placements for {args.compat}: {len(places)} found "
              f"(showing up to 20)")
        for pl in places[:20]:
            asg = ", ".join(f"{w}@{o}" for w, o in pl.assignment)
            filled = "".join(pl.fixed.get(i, ".") for i in range(tmpl.L))
            print(f"  {asg:32s} -> {filled}")
        if not places:
            print("  NONE — these anchors cannot co-occur in the refrain.")
        print()

    if args.anchor or not did:
        wordset = _load_wordset(args.wordlist)
        model = ng.TrigramModel("abcdefghijklmnopqrstuvwxyz", ng._ENGLISH)
        if args.anchor:
            places = rc.compatible_placements(args.anchor, tmpl, max_solutions=1)
            if not places:
                print(f"Anchors {args.anchor} cannot be jointly placed — aborting.")
                return 1
            asg = ", ".join(f"{w}@{o}" for w, o in places[0].assignment)
            print(f"Seeding with: {asg}")
        cands = rc.compose(tmpl, anchors=args.anchor, model=model, wordset=wordset,
                           beam=args.beam, top=args.top,
                           wcov_weight=args.wcov_weight)
        print(f"\n{'candidate':24s} {'lm':>7} {'wcov':>6}  words")
        print("-" * 70)
        for cd in cands:
            print(f"{cd.text:24s} {cd.lm_score:7.2f} {cd.wcov:6.0%}  "
                  f"{' '.join(cd.words[:6])}")
        print()
        print("READ: high wcov + readable words = worth feeding to order_solve. The "
              "trigram top-rank is English-FLAVOURED, not necessarily meaningful — "
              "stack more compatible anchors to collapse the space.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
