#!/usr/bin/env python3
"""EyeCrack crib-globality test — is the keystream GLOBAL or LOCAL?

A crib in ONE message filters candidate generator seeds (repeat-pattern, additive,
mapping-free); each surviving seed yields the keystream EVERYWHERE, so we decrypt
ALL nine messages and ask whether they JOINTLY become structured:

  * whole corpus lights up  -> GLOBAL keystream (depth opens to nine)
  * only the crib's triplet  -> LOCAL (per-triplet keystream)
  * nothing                  -> no seed in range for these generators (exclusion)

Calibrated against a random-seed per-message null, so a verdict is trustworthy.
Honest scope: this assumes a generator family; a generator-free crib has no
globality power on a flat corpus (proved in the core selftest).

    # one generator, one position
    python3 globality.py --crib-word sisaltaa --crib-msg "East 1" --crib-pos 3 \
                         --generators nolla --count 2000000 --html ../globality.html
    # sweep ALL generators and an early-middle position window in one run
    python3 globality.py --crib-word messages --crib-msg "East 1" \
                         --crib-pos 3 --crib-pos-end 40 --generators all \
                         --count 100000000 --html ../globality.html
"""
from __future__ import annotations

import argparse
import html
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import globality as gl        # noqa: E402
import keyscan as ks          # noqa: E402


def render_html(results, meta) -> str:
    css = """body{background:#0f0d0a;color:#e8dcc0;font-family:Georgia,serif;
    max-width:1000px;margin:0 auto;padding:24px}h1{color:#c9a227;letter-spacing:.1em}
    table{border-collapse:collapse;width:100%;margin:8px 0 22px}th,td{border:1px solid
    #2d2615;padding:5px 9px;font-size:.82rem}th{color:#4ec9b0}.g{color:#3fb950;font-weight:bold}
    .l{color:#d29922}.n{color:#8b949e}.meta{color:#a99c80;font-family:monospace;font-size:.8rem}"""
    rows = []
    for r in results[:40]:
        cls = {"global": "g", "local": "l", "partial": "l"}.get(r.verdict, "n")
        cells = "".join(f"<td class='{'g' if s else 'n'}'>{z:.1f}</td>"
                        for s, z in zip(r.structured, r.z))
        rows.append(f"<tr><td>{r.generator}</td><td>{r.position}</td>"
                    f"<td>{r.seed}</td><td class='{cls}'>{r.verdict}</td>"
                    f"<td>{r.n_structured}/9</td>{cells}</tr>")
    any_g = any(r.verdict == "global" for r in results)
    verdict = ("A GLOBAL-keystream seed was found — one seed decrypts (almost) all "
               "nine to structure. Depth opens to nine; decode and read." if any_g else
               "No global seed in range. Either the keystream is local/per-triplet, "
               "the crib/position is wrong, or the generator is not in this set.")
    head = "<tr><th>gen</th><th>pos</th><th>seed</th><th>verdict</th><th>n</th>" + \
           "".join(f"<th>m{i}</th>" for i in range(9)) + "</tr>"
    return f"""<!doctype html><html><head><meta charset='utf-8'>
<title>EYES crib-globality</title><style>{css}</style></head><body>
<h1>E Y E S — crib-globality test</h1>
<p class='meta'>{html.escape(' · '.join(f'{k}: {v}' for k,v in meta.items()))}</p>
<p class='{'g' if any_g else 'n'}'><b>{html.escape(verdict)}</b></p>
<table>{head}{''.join(rows)}</table>
<p class='meta'>Each cell is the per-message structure z vs a random-seed null;
green = clears the null. One seed (from a crib in a single message) lighting up
the whole row = global keystream.</p></body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser(description="crib-globality test")
    ap.add_argument("--crib-word", required=True)
    ap.add_argument("--crib-msg", default="East 1")
    ap.add_argument("--crib-pos", type=int, default=3,
                    help="start of the position sweep (inclusive)")
    ap.add_argument("--crib-pos-end", type=int, default=None,
                    help="end of the position sweep (inclusive); default = crib-pos")
    ap.add_argument("--generators", default="nolla",
                    help="'all', or a comma-separated subset of "
                         + ",".join(ks.SCALAR_GENERATORS.keys()))
    ap.add_argument("--combiner", default="add", choices=["add", "sub", "beaufort"])
    ap.add_argument("--seed-start", type=int, default=0)
    ap.add_argument("--count", type=int, default=1_000_000)
    ap.add_argument("--body-start", type=int, default=0)
    ap.add_argument("--decoy-seeds", type=int, default=200)
    ap.add_argument("--z-thr", type=float, default=3.0)
    ap.add_argument("--html", default="")
    args = ap.parse_args()

    c = corpus_mod.load()
    N = c.N
    msgs = [list(x) for x in c.ciphertexts]
    member = c.labels.index(args.crib_msg) if args.crib_msg in c.labels else 0

    gens = (list(ks.SCALAR_GENERATORS.keys()) if args.generators == "all"
            else [g.strip() for g in args.generators.split(",")])
    bad = [g for g in gens if g not in ks.SCALAR_GENERATORS]
    if bad:
        print(f"unknown generator(s): {bad}; choices: "
              f"{list(ks.SCALAR_GENERATORS.keys())}")
        return 2
    pos_end = args.crib_pos if args.crib_pos_end is None else args.crib_pos_end
    positions = list(range(args.crib_pos, pos_end + 1))
    msg_len = len(msgs[member])
    positions = [p for p in positions if p + len(args.crib_word) <= msg_len]

    k, frac = ks.crib_power(args.crib_word, N)
    print(f"crib '{args.crib_word}' in {c.labels[member]}: {k} repeat "
          f"constraint(s) -> ~{frac:.2e} of seeds survive per (gen,pos)")
    if k == 0:
        print("  WARNING: no repeated letters -> no mapping-free filter; every seed "
              "survives and this becomes a full calibrated scan per cell.")
    print(f"sweep: {len(gens)} generator(s) x {len(positions)} position(s) "
          f"[{positions[0]}..{positions[-1]}] x {args.count:,} seeds")

    all_results = []
    t0 = time.time()
    for gen in gens:
        # decoy null depends only on the generator, so compute it ONCE per gen.
        mu, sd = gl.decoy_null(msgs, gen, args.combiner, N, args.body_start,
                               args.decoy_seeds)
        for pos in positions:
            res = gl.scan_global(msgs, args.crib_word, pos, member, gen,
                                 args.combiner, args.seed_start, args.count, N,
                                 args.body_start, mu, sd, args.z_thr)
            for r in res:
                r.generator, r.position = gen, pos
            all_results.extend(res)
            hot = [r for r in res if r.verdict in ("global", "local", "partial")]
            if hot:
                print(f"  [{gen} @ {pos}] {len(res)} survivors; "
                      f"{sum(1 for r in res if r.verdict=='global')} global, "
                      f"{sum(1 for r in res if r.verdict=='local')} local")
    dt = time.time() - t0

    all_results.sort(key=lambda r: (-r.n_structured, -max(r.z, default=0)))
    glob = [r for r in all_results if r.verdict == "global"]
    loc = [r for r in all_results if r.verdict == "local"]
    print(f"\nscored seeds across the whole sweep in {dt:.1f}s; "
          f"{len(all_results)} total crib survivors")
    for r in all_results[:10]:
        print(f"  {r.generator:10} pos {r.position:>3}  seed {r.seed:>12}  "
              f"{r.verdict:8}  {r.n_structured}/9")
    print("\nVERDICT:", "GLOBAL keystream candidate found!" if glob else
          (f"{len(loc)} local (crib-triplet only) candidate(s); no global hit"
           if loc else "no structured seed in range"))

    if args.html:
        meta = {"crib": args.crib_word, "msg": c.labels[member],
                "positions": f"{positions[0]}..{positions[-1]}",
                "generators": ",".join(gens),
                "seeds": f"{args.seed_start:,}..{args.seed_start+args.count:,}"}
        Path(args.html).write_text(render_html(all_results, meta), encoding="utf-8")
        print(f"wrote {args.html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
