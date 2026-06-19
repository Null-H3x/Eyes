#!/usr/bin/env python3
"""EyeCrack — template-guided refrain candidate sweep.

Filters wordlist / enumerated candidates through template constraints, GF fits,
pin_structure, and order_solve scoring — the productive replacement for blind
phrase guessing.

Usage:
    python3 refrain_sweep.py --show-template
    python3 refrain_sweep.py --wordlist ../eyestat/noita_wordlist.txt
    python3 refrain_sweep.py --wordlist eyestat/noita_wordlist.txt   # from repo root
    python3 refrain_sweep.py --wordlist cands.txt --also-enum
    python3 refrain_sweep.py --phrase "..."   # must be exactly 22 chars
    python3 refrain_sweep.py --wordlist ../eyestat/noita_wordlist.txt --html
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CORE = ROOT / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import refrain as rf          # noqa: E402
import ngram_solve as ng      # noqa: E402
import refrain_sweep as rs    # noqa: E402
import template as tp         # noqa: E402

_PATH_ANCHORS = (HERE, ROOT, Path.cwd())


def _show_template(messages, N) -> int:
    c = corpus_mod.load()
    region = rf.DEFAULT_INSTANCES
    L = rf.DEFAULT_LEN
    tmpl = rs.load_template(messages, region, L, N)
    print("=" * 70)
    print("EYECRACK — refrain repeat-template (for sweep filtering)")
    print("=" * 70)
    print(f"Region {[(c.labels[m], p) for m, p in region]}, L={L}")
    if not tmpl.consistent:
        print(f"  INCONSISTENT at {tmpl.contradiction}")
        return 1
    print(f"\nFree plaintext dof: {tmpl.dof} of {L}")
    print(f"Forced-SAME groups: {tmpl.same_groups}")
    print(f"Free positions: {tmpl.free_positions}")
    print(f"Forced-DIFFERENT pairs: {len(tmpl.diff_pairs)}")
    print(f"\nSkeleton:")
    print(f"  pos: " + " ".join(f"{i % 10}" for i in range(L)))
    print(f"  pat: " + "  ".join(tp.skeleton_string(tmpl)))
    return 0


def _write_html(rows: list, out_path: Path, meta: dict) -> None:
    esc = html.escape
    trs = []
    for r in rows:
        stage = r.stage_failed or "scored"
        words = ", ".join(r.words[:8]) if r.words else ""
        trs.append(
            f"<tr><td>{esc(r.phrase)}</td><td>{r.offset}</td>"
            f"<td>{esc(stage)}</td><td>{r.symbols_pinned}</td>"
            f"<td>{r.coverage:.1%}</td><td>{r.z:.2f}</td>"
            f"<td>{r.word_coverage:.1%}</td><td>{esc(words)}</td></tr>"
        )
    body = "\n".join(trs) if trs else "<tr><td colspan='8'>No survivors</td></tr>"
    ts = esc(meta.get("ts", ""))
    nc = meta.get("candidates", 0)
    ns = meta.get("survivors", 0)
    doc = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Refrain template sweep</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #1a1a2e; color: #eee; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #444; padding: 0.4rem 0.6rem; text-align: left; }}
th {{ background: #16213e; }}
tr:nth-child(even) {{ background: #0f3460; }}
.meta {{ color: #aaa; margin-bottom: 1rem; }}
</style></head><body>
<h1>Refrain template sweep</h1>
<p class="meta">Generated {ts} — {nc} candidates, {ns} scored</p>
<table>
<thead><tr><th>phrase</th><th>off</th><th>stage</th><th>pinned</th>
<th>cov</th><th>z</th><th>wcov</th><th>words</th></tr></thead>
<tbody>{body}</tbody></table>
<script>const META = {json.dumps(meta)};</script>
</body></html>"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(doc, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phrase", action="append", dest="phrases")
    ap.add_argument("--wordlist")
    ap.add_argument("--also-enum", action="store_true")
    ap.add_argument("--show-template", action="store_true")
    ap.add_argument("--alphabet", default=rf.DEFAULT_ALPHABET)
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--restarts", type=int, default=1)
    ap.add_argument("--iters", type=int, default=400)
    ap.add_argument("--null", type=int, default=12)
    ap.add_argument("--html", action="store_true")
    ap.add_argument("--html-out", default=str(ROOT / "report" / "refrain_sweep_report.html"))
    ap.add_argument("--no-expand-wordlist", action="store_true",
                    help="do not join short wordlist tokens into length-22 windows")
    ap.add_argument("--score-limit", type=int, default=20,
                    help="max candidates for full order_solve after cheap filter")
    ap.add_argument("--full-score", action="store_true",
                    help="use thorough scoring (restarts=4, iters=3000) on --phrase inputs")
    args = ap.parse_args()

    c = corpus_mod.load()
    N = c.N
    M = [list(x) for x in c.ciphertexts]

    if args.show_template:
        return _show_template(M, N)

    phrases = list(args.phrases or [])
    if args.wordlist:
        try:
            wl = rs.resolve_path(args.wordlist, anchors=_PATH_ANCHORS)
        except FileNotFoundError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2
        phrases.extend(rs.load_wordlist(wl))

    if not phrases and not args.also_enum:
        print("Pass --phrase (22 chars), --wordlist, --also-enum, or --show-template.")
        return 0

    print("=" * 70)
    print("EYECRACK — template-guided refrain sweep")
    print("=" * 70)
    print(f"Region L={rf.DEFAULT_LEN}; stages: length -> pattern -> fits -> pin -> order_solve")

    model = ng.TrigramModel(args.alphabet, ng._ENGLISH)
    restarts = 4 if args.full_score else args.restarts
    iters = 3000 if args.full_score else args.iters
    n_null = 30 if args.full_score else args.null
    explicit = list(args.phrases or [])
    try:
        all_results = rs.sweep_candidates(
            M, phrases, N,
            alphabet=args.alphabet, model=model,
            restarts=restarts, iters=iters, n_null=n_null,
            also_enum=args.also_enum,
            expand_wordlist=not args.no_expand_wordlist,
            score_limit=args.score_limit,
            always_score=[p for p in explicit if len(p.strip()) == rf.DEFAULT_LEN],
        )
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130

    scored = [r for r in all_results if r.consistent]
    scored.sort(key=lambda r: (r.z, r.word_coverage), reverse=True)
    pattern_ok = [r for r in all_results if r.stage_failed not in ("length", "pattern")]
    fits_ok = [r for r in all_results if r.stage_failed not in ("length", "pattern", "fits")]

    fits_ok = [r for r in all_results if r.stage_failed not in
               ("length", "pattern", "fits")]
    cheap_ok = [r for r in all_results if r.stage_failed in ("cheap_ok", None) or r.consistent]

    print(f"\nCandidates tried: {len(all_results)}")
    print(f"  passed pattern: {len(pattern_ok)}")
    print(f"  passed fits:    {len(fits_ok)}")
    print(f"  cheap_ok (fits+offset): {len(cheap_ok)}")
    print(f"  fully scored:   {len(scored)}")

    display = sorted(all_results,
                     key=lambda r: (r.consistent, r.z, r.word_coverage),
                     reverse=True)[: args.top]

    print(f"\n{'phrase':22s} {'off':>3} {'stage':>8} {'pin':>4} {'cov':>4} "
          f"{'z':>6} {'wcov':>5}  words")
    print("-" * 78)
    for r in display:
        stage = r.stage_failed or "scored"
        words = ", ".join(r.words[:5]) if r.words else ""
        print(f"{r.phrase[:22]:22s} {r.offset:>3} {stage:>8} "
              f"{r.symbols_pinned:>4} {r.coverage:>3.0%} {r.z:>6.1f} "
              f"{r.word_coverage:>4.0%}  {words}")

    if args.html:
        meta = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "candidates": len(all_results),
            "survivors": len(scored),
        }
        _write_html(display, Path(args.html_out), meta)
        print(f"\nWrote {args.html_out}")

    print("\nREAD: Most wordlist windows fail at pattern/fits (expected). Survivors")
    print("with high z AND word-coverage warrant manual review.")
    print(f"Note: --phrase must be exactly {rf.DEFAULT_LEN} characters.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
