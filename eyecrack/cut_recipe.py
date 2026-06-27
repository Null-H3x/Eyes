#!/usr/bin/env python3
"""EyeCrack — cut recipe CLI (range cuts + phrase viability).

Usage:
    python3 cut_recipe.py --phrase Eyes --cuts A-F H-N P-C E-R --promote-god
    python3 cut_recipe.py --preset god --phrase godseeye
    python3 cut_recipe.py --show-cuts A-F H-N P-C E-R --promote-god
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import alphabet_cut as ac  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phrase", default="Eyes")
    ap.add_argument("--cuts", nargs="*", default=list(ac.GOD_CUT_SPECS))
    ap.add_argument("--preset", choices=("god", "az", "god-raw"))
    ap.add_argument("--promote-god", action="store_true")
    ap.add_argument("--promote")
    ap.add_argument("--variant", choices=("26", "52", "both"), default="both")
    ap.add_argument("--lower", default="mirror")
    ap.add_argument("--show-cuts", nargs="*", metavar="RANGE")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.show_cuts is not None:
        specs = args.show_cuts or list(ac.GOD_CUT_SPECS)
        for line in ac.describe_cuts(specs):
            print(line)
        final = ac.apply_range_cuts(ac.STANDARD_26, specs)
        if args.promote_god:
            final = ac.promote_god_prefix(final)
        elif args.promote:
            final = ac.promote_prefix(final, args.promote)
        print(f"\nFinal 26: {final}")
        return 0

    if args.preset == "god":
        specs = list(ac.GOD_CUT_SPECS)
        promote_god = True
    elif args.preset == "god-raw":
        specs = list(ac.GOD_CUT_SPECS)
        promote_god = False
    elif args.preset == "az":
        specs = []
        promote_god = False
    else:
        specs = args.cuts
        promote_god = args.promote_god

    rec = ac.build_recipe(
        specs,
        promote_god=promote_god,
        promote=args.promote,
        variant=args.variant,
        lower_mode=args.lower,
        phrase=args.phrase,
    )
    if args.json:
        # omit full deck strings in json if huge - keep previews
        slim = dict(rec)
        for vk, vv in slim.get("variants", {}).items():
            if "deck" in vv:
                vv["deck_len"] = len(vv["deck"])
                vv.pop("deck", None)
        slim.pop("selected_deck", None)
        print(json.dumps(slim, indent=2))
        return 0 if rec.get("ok") else 1

    if not rec.get("ok"):
        print("ERROR:", rec.get("error"))
        return 1
    print("upper26:", rec["upper26"])
    for row in rec.get("steps", []):
        print(f"  {row['label']}: {row['alphabet_26']}")
    ph = rec.get("phrase", {})
    if ph:
        print(f"\nphrase {ph['phrase']!r}: recommended {ph['recommended_variant']}")
        print(f"  26 viable: {ph['v26']['viable']}  missing: {ph['v26'].get('missing')}")
        print(f"  52 viable: {ph['v52']['viable']}  missing: {ph['v52'].get('missing')}")
    deck = rec.get("selected_deck") or rec.get("variants", {}).get("52", {}).get("deck", "")
    print(f"\nselected deck preview: {deck[:60]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
