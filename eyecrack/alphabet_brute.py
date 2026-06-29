#!/usr/bin/env python3
"""EyeCrack — brute-force plaintext-alphabet ordering with scoring.

Tractable search over the value→character ordering O, ranked by trigram z-score,
dictionary word-coverage, and hit count.

Modes
-----
rotate   All N cyclic rotations of the default alphabet (83 trials, no crib).
swap     All pair swaps from a seed ordering (O(N²) trials, no crib).
random   Monte Carlo permutations (--samples, optional --crib anchors free slots).
exhaust  Full enumeration of free slots when crib leaves few degrees of freedom.

Examples
--------
    # Quick sanity: try every rotation of the default alphabet
    python3 alphabet_brute.py --mode rotate

    # Monte Carlo without crib (exploratory — weak on real corpus)
    python3 alphabet_brute.py --mode random --samples 10000 --top 15

    # Productive path: crib-anchored random search
    python3 alphabet_brute.py --mode random --crib trueknowledgeofthegods \\
        --samples 50000 --top 10

    # Exhaust residual permutations after crib pins structure
    python3 alphabet_brute.py --mode exhaust --crib trueknowledgeofthegods

    # Write HTML leaderboard
    python3 alphabet_brute.py --mode random --crib trueknowledge --samples 20000 \\
        --html ../alphabet_brute_report.html
"""
from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import alphabet_brute as ab  # noqa: E402
import corpus as corpus_mod  # noqa: E402
import refrain as rf         # noqa: E402


def _write_html(path: Path, mode: str, scores, labels, crib, offset) -> None:
    rows = []
    for i, sc in enumerate(scores, 1):
        rows.append(
            f"<tr><td>{i}</td><td>{sc.trigram:.4f}</td><td>{sc.z:.2f}</td>"
            f"<td>{sc.word_coverage:.1%}</td><td>{sc.dict_hits}</td>"
            f"<td>{sc.composite:.2f}</td><td>{html.escape(sc.method)}</td></tr>"
        )
    best_block = ""
    if scores:
        b = scores[0]
        if b.plaintext:
            best_block = "<h2>Best decryption</h2><pre>" + html.escape(
                "\n".join(f"{labels[mi]}: {b.plaintext[mi]}"
                          for mi in sorted(b.plaintext))
            ) + "</pre>"
    crib_line = f"<p>crib: <code>{html.escape(crib)}</code> offset {offset}</p>" if crib else ""
    doc = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Alphabet brute — {html.escape(mode)}</title>
<style>
body{{font-family:system-ui;background:#0d0d12;color:#c8d6e0;margin:2rem}}
h1{{color:#ff8c00}} table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #333;padding:.4rem .6rem;text-align:left}}
th{{color:#0ff0fc}} pre{{background:#13131a;padding:1rem;overflow:auto}}
</style></head><body>
<h1>Alphabet brute-force report</h1>
<p>mode: <strong>{html.escape(mode)}</strong></p>
{crib_line}
<table><thead><tr>
<th>#</th><th>trigram</th><th>z</th><th>word cov</th><th>hits</th>
<th>composite</th><th>method</th>
</tr></thead><tbody>
{"".join(rows)}
</tbody></table>
{best_block}
</body></html>"""
    path.write_text(doc, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--mode",
        choices=("rotate", "swap", "random", "exhaust"),
        default="random",
        help="search strategy (default: random)",
    )
    ap.add_argument("--samples", type=int, default=5000,
                    help="Monte Carlo trials for random mode")
    ap.add_argument("--crib", help="refrain phrase — anchors ordering slots")
    ap.add_argument("--offset", type=int, default=0,
                    help="refrain offset within the repeat region")
    ap.add_argument("--exhaust-if-free", type=int, default=10,
                    help="exhaust when free slots <= this (exhaust mode)")
    ap.add_argument("--max-perms", type=int, default=500_000,
                    help="cap exhaustive permutations")
    ap.add_argument("--top", type=int, default=15, help="show top N scores")
    ap.add_argument("--null", type=int, default=25, dest="n_null",
                    help="null samples for z-score")
    ap.add_argument("--seed", type=int, default=0, help="RNG seed")
    ap.add_argument("--html", metavar="PATH", help="write HTML report")
    args = ap.parse_args()

    c = corpus_mod.load()
    M = [list(x) for x in c.ciphertexts]

    if args.mode == "exhaust" and not args.crib:
        print("error: exhaust mode requires --crib")
        return 2

    try:
        mode, scores = ab.run_brute(
            M, c.N,
            mode=args.mode,
            samples=args.samples,
            crib=args.crib,
            offset=args.offset,
            region=rf.DEFAULT_INSTANCES,
            exhaust_if_free=args.exhaust_if_free,
            max_perms=args.max_perms,
            top=args.top,
            n_null=args.n_null,
            seed=args.seed,
        )
    except ValueError as exc:
        print(f"error: {exc}")
        return 2

    if not scores and args.crib:
        print("No scores — crib may be inconsistent with ciphertext at this offset.")
        return 1

    print(ab.format_report(
        mode, scores,
        labels=c.labels,
        crib=args.crib,
        offset=args.offset if args.crib else None,
    ))

    if args.html:
        out = Path(args.html)
        if not out.is_absolute():
            out = HERE / out
        _write_html(out, mode, scores, c.labels, args.crib, args.offset)
        print(f"Wrote {out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
