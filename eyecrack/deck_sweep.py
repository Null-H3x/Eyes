#!/usr/bin/env python3
"""EyeCrack — 26 / 52 deck sweep with wiki header crib and range-cut permutations.

Builds plaintext-alphabet candidates from:
  - sequential range cuts (``A-F H-N P-C E-R`` → GOD preset)
  - arbitrary cut specs via ``--cuts``
  - named presets (``god``, ``az``)

Each candidate is embedded in an **N=83** deck (26- or 52-letter block + tail),
optionally pins the wiki header (``deck[66]='.'``, ``deck[5]=' '``), and scores
refrain anchors + pos-0 digit mapping.

Usage:
    python3 deck_sweep.py --presets                    # GOD + A-Z + raw cuts
    python3 deck_sweep.py --variant 26 --preset god
    python3 deck_sweep.py --variant 52 --preset god --lower mirror
    python3 deck_sweep.py --cuts A-F H-N P-C E-R --promote-god
    python3 deck_sweep.py --show-cuts A-F H-N P-C E-R
    python3 deck_sweep.py --cuts A-F B-C --anchors god see eye
    python3 deck_sweep.py --phrase godseeye --compat god see eye
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import alphabet_cut as ac          # noqa: E402
import corpus as corpus_mod        # noqa: E402
import deck_sweep as ds            # noqa: E402
import refrain as rf               # noqa: E402
import refrain_compose as rc       # noqa: E402
import template as tp              # noqa: E402


def _print_score(row: ds.DeckScore, *, verbose: bool = False) -> None:
    flags = []
    flags.append("wiki" if row.wiki_symbol_ok else "no-wiki")
    flags.append("digits" if row.header_digits_ok else f"digits={row.header_digits!r}")
    flags.append("tmpl" if row.template_ok else "no-tmpl")
    anchor_bits = []
    for ph, ok in row.anchors.items():
        if not ok:
            anchor_bits.append(f"{ph}:unmap")
        elif row.refrain_ok.get(ph):
            anchor_bits.append(f"{ph}:tmpl+")
        else:
            anchor_bits.append(f"{ph}:map")
    print(
        f"  {row.name:16s}  score={row.total_score:5.1f}  "
        f"{' '.join(flags)}  anchors=[{', '.join(anchor_bits)}]"
    )
    if verbose:
        print(f"    26-block: {row.letters_26}")
        print(f"    deck[0:32]: {row.deck[:32]}")
        if row.notes:
            print(f"    notes: {'; '.join(row.notes)}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--presets", action="store_true", help="run GOD + A-Z + raw-cut presets")
    ap.add_argument("--preset", choices=("god", "az", "god-raw"), help="single preset")
    ap.add_argument("--variant", choices=("26", "52", "both"), default="both")
    ap.add_argument("--cuts", nargs="*", metavar="RANGE", help="range-cut specs (e.g. A-F H-N)")
    ap.add_argument("--promote-god", action="store_true", help="apply GOD prefix promotion after cuts")
    ap.add_argument("--promote", metavar="PREFIX", help="promote arbitrary prefix after cuts")
    ap.add_argument("--show-cuts", nargs="*", metavar="RANGE",
                    help="print intermediate cut steps and exit")
    ap.add_argument("--lower", choices=("mirror", "shift", "none"), default="mirror",
                    help="52-variant lowercase layout")
    ap.add_argument("--anchors", nargs="*", default=list(ds.DEFAULT_ANCHORS))
    ap.add_argument("--wiki-mode", choices=("symbol", "value", "off"), default="symbol")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--phrase", action="append", default=[], help="extra anchor phrase")
    ap.add_argument("--compat", nargs="*", metavar="WORD",
                    help="show refrain_compose joint placements")
    args = ap.parse_args()

    if args.show_cuts is not None:
        specs = args.show_cuts or list(ac.GOD_CUT_SPECS)
        print("Range-cut steps (standard A-Z base):")
        for line in ac.describe_cuts(specs):
            print(f"  {line}")
        final = ac.apply_range_cuts(ac.STANDARD_26, specs)
        if args.promote_god:
            final = ac.promote_god_prefix(final)
        elif args.promote:
            final = ac.promote_prefix(final, args.promote)
        print(f"\nFinal 26: {final}")
        return 0

    c = corpus_mod.load()
    M = [list(x) for x in c.ciphertexts]
    N = c.N
    anchors = list(dict.fromkeys(args.anchors + args.phrase))

    print("=" * 72)
    print("EYECRACK — 26 / 52 deck sweep (wiki header crib + refrain anchors)")
    print("=" * 72)
    print(f"Corpus N={N}, wiki_mode={args.wiki_mode}, anchors={anchors}")

    if args.compat:
        tmpl = tp.extract(M, rf.DEFAULT_INSTANCES, rf.DEFAULT_LEN, N)
        print(f"\nRefrain template: {tp.skeleton_string(tmpl)}")
        pls = rc.compatible_placements(args.compat, tmpl, max_solutions=12)
        print(f"Joint placements for {args.compat}: {len(pls)}")
        for p in pls:
            fixed = "".join(p.fixed.get(i, ".") for i in range(tmpl.L))
            assign = ", ".join(f"{w}@{o}" for w, o in p.assignment)
            print(f"  {assign}  ->  {fixed}")
        print()

    rows: list[ds.DeckScore] = []

    if args.presets:
        rows.extend(ds.sweep_presets(M, anchors=anchors, wiki_mode=args.wiki_mode))

    if args.preset == "god":
        u = ac.god_alphabet_26()
        rows.extend(
            ds.sweep_variants(
                M, upper26=u, name="god", anchors=anchors,
                wiki_mode=args.wiki_mode,
                lower_modes=(args.lower,) if args.variant != "26" else ("mirror",),
            )
        )
    elif args.preset == "az":
        rows.extend(
            ds.sweep_variants(
                M, upper26=ac.STANDARD_26, name="az", anchors=anchors,
                wiki_mode=args.wiki_mode,
                lower_modes=(args.lower,) if args.variant != "26" else ("mirror",),
            )
        )
    elif args.preset == "god-raw":
        u = ac.apply_range_cuts(ac.STANDARD_26, ac.GOD_CUT_SPECS)
        rows.extend(
            ds.sweep_variants(
                M, upper26=u, name="god-raw", anchors=anchors,
                wiki_mode=args.wiki_mode,
                lower_modes=(args.lower,) if args.variant != "26" else ("mirror",),
            )
        )

    if args.cuts:
        u = ac.apply_range_cuts(ac.STANDARD_26, args.cuts)
        if args.promote_god:
            u = ac.promote_god_prefix(u)
        elif args.promote:
            u = ac.promote_prefix(u, args.promote)
        name = "-".join(args.cuts) + ("+GOD" if args.promote_god else "")
        modes = ("mirror",) if args.variant == "26" else (args.lower,)
        if args.variant in ("26", "both"):
            d26 = ac.build_deck_83(u, variant="26", wiki_crib=True, wiki_mode=args.wiki_mode)
            rows.append(
                ds.score_deck(name + "/26", d26, M, variant="26", letters_26=u,
                              anchors=anchors, wiki_mode=args.wiki_mode)
            )
        if args.variant in ("52", "both"):
            for lm in modes:
                g52 = ac.expand_to_52(u, lower_mode=lm)
                d52 = ac.build_deck_83(g52, variant="52", wiki_crib=True, wiki_mode=args.wiki_mode)
                rows.append(
                    ds.score_deck(f"{name}/52-{lm}", d52, M, variant="52", letters_26=u,
                                  anchors=anchors, wiki_mode=args.wiki_mode)
                )

    if not rows:
        print("\nNothing to run. Try --presets, --preset god, or --cuts A-F H-N P-C E-R --promote-god")
        return 0

    if args.variant == "26":
        rows = [r for r in rows if "/26" in r.name or r.variant == "26"]
    elif args.variant == "52":
        rows = [r for r in rows if "/52" in r.name or r.variant == "52"]

    # dedupe by deck string
    seen = set()
    uniq: list[ds.DeckScore] = []
    for r in sorted(rows, key=lambda x: -x.total_score):
        if r.deck in seen:
            continue
        seen.add(r.deck)
        uniq.append(r)

    print(f"\n{'name':16s}  {'score':>5}  flags / anchors")
    print("-" * 72)
    for row in uniq[: args.top]:
        _print_score(row, verbose=args.verbose)

    best = uniq[0] if uniq else None
    if best:
        print("\nBest deck (first 52 chars):")
        print(f"  {best.deck[:52]}")
        print(f"  wiki: deck[5]={best.deck[5]!r} deck[66]={best.deck[66]!r}")
    print("\nREAD: high score = wiki crib + pos0 digits + template-matching anchors.")
    print("None validate decryption alone — feed survivors to order_solve with a long crib.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
