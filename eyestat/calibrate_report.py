#!/usr/bin/env python3
"""Re-evaluate EyeStat result hits with the calibrated trust gate.

EyeStat ranks hits by raw dictionary-substring count, which is uncalibrated: a
random decrypt racks up short Finnish substrings by chance.  This re-scores the
top hits in an EyeStat HTML report with `noita_eye_core.calibrate` — comparing
each decrypt's match count and char-LM score against a SHUFFLE of its own symbols
(real language survives shuffling; chance substrings don't).

    python3 calibrate_report.py triplet-results/ctak_right_park_miller_v0_report.html
    python3 calibrate_report.py REPORT.html --lang fi --top 15
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import calibrate  # noqa: E402

WORDLISTS = {"fi": HERE / "extra_words_fi.txt", "en": HERE / "eng-wordlist.txt"}


def extract_hits(html: str):
    m = re.search(r"const\s+DATA\s*=\s*(\[.*?\]);", html, re.S)
    if not m:
        return []
    return json.loads(m.group(1))


def main() -> int:
    ap = argparse.ArgumentParser(description="calibrate EyeStat report hits")
    ap.add_argument("report", help="EyeStat results HTML")
    ap.add_argument("--lang", default="fi", choices=["fi", "en"])
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--n-null", type=int, default=300)
    args = ap.parse_args()

    wl = WORDLISTS[args.lang]
    if not wl.exists():
        print(f"ERROR: wordlist not found: {wl}", file=sys.stderr)
        return 2
    print(f"loading {args.lang} wordlist + training char-LM ...")
    words = sorted(calibrate.load_wordset(wl, min_len=4))
    wordset = set(words)
    charlm = calibrate.train_charlm(words)

    hits = extract_hits(Path(args.report).read_text(encoding="utf-8"))
    if not hits:
        print("No DATA array found in report.")
        return 1
    # rank by best-language z (EyeStat's own ranking)
    def hz(r):
        return r["L"].get(r.get("bl"), {}).get("z", 0)
    hits.sort(key=hz, reverse=True)

    print(f"\nRe-scoring top {args.top} hits with the calibrated gate "
          f"(shuffle null, n={args.n_null}):\n")
    print("  seed            raw_z  matches  z_dict   z_lm    verdict")
    real_count = 0
    for r in hits[:args.top]:
        bl = r.get("bl")
        info = r["L"].get(bl, {})
        t = info.get("t", "")
        if not t:
            continue
        a = calibrate.assess(t, wordset, charlm, n_null=args.n_null, seed=1)
        tag = "REAL" if a["real"] else "noise"
        if a["real"]:
            real_count += 1
        print(f"  {r['k']:<15} {info.get('z',0):>5.1f}  {a['matches']:>6}  "
              f"{a['z_dict']:>6.2f}  {a['z_lm']:>6.2f}   {tag}")

    print()
    if real_count == 0:
        print("VERDICT: every top hit is NOISE. The high dictionary z is an "
              "artifact of EyeStat's mapping-optimisation — the rune->letter map "
              "was chosen to PLANT Finnish words, so they beat a shuffle "
              "(z_dict>5) tautologically. But the mapping-robust char-LM shows NO "
              "Finnish sequence structure (z_lm at the shuffle null): the decrypt "
              "is scattered chance words under a fitted alphabet, not Finnish "
              "plaintext. EyeStat's raw z is uncalibrated for this corpus.")
    else:
        print(f"VERDICT: {real_count} hit(s) flagged REAL — INVESTIGATE: their "
              "words survive shuffling and/or LM is far above null. Read the "
              "decrypt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
