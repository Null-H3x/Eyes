#!/usr/bin/env python3
"""EyeCrack keystream seed-scan — combiner- + generator-pluggable, multi-core.

Tests the keystream-cipher hypothesis per triplet: does some (generator, seed,
combiner) decrypt the three messages to joint structure?  Emits a standalone HTML
report you can commit so results are shareable.

    # default: additive, all scalar generators, all 3 triplets
    python3 keyscan.py --count 1000000 --html ../keyscan_report.html
    # injective (rotor/deck) branch:
    python3 keyscan.py --combiner subst --generators nolla --count 200000
    # exact crib filter (high power):
    python3 keyscan.py --crib 12,4,7,1,9 --crib-msg "East 1" --crib-start 3 \
                       --count 100000000
"""
from __future__ import annotations

import argparse
import html
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import List, Optional, Tuple

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import keyscan as ks          # noqa: E402

TOPK = 10


def _chunk_worker(spec):
    (lo, hi, msgs, gen, comb, N, body_start, crib, cmember, cstart) = spec
    if crib is not None:
        return ("crib", [s for s in range(lo, hi)
                         if ks.crib_ok(msgs, cmember, s, gen, comb, N, cstart,
                                       crib)])
    best: List[Tuple[float, int]] = []
    for seed in range(lo, hi):
        dec = ks.decrypt_triplet(msgs, seed, gen, comb, N)
        best.append((ks.structure_score(dec, body_start), seed))
    best.sort(reverse=True)
    return ("score", best[:TOPK])


def _chunks(start, count, n):
    step = max(1, count // n)
    s = start
    while s < start + count:
        yield (s, min(start + count, s + step))
        s += step


def _run_range(msgs, gen, comb, N, body_start, start, count, jobs, crib=None,
               cmember=0, cstart=0):
    specs = [(lo, hi, msgs, gen, comb, N, body_start, crib, cmember, cstart)
             for (lo, hi) in _chunks(start, count, jobs * 4)]
    out_scores: List[Tuple[float, int]] = []
    out_crib: List[int] = []
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        for kind, payload in ex.map(_chunk_worker, specs):
            if kind == "crib":
                out_crib.extend(payload)
            else:
                out_scores.extend(payload)
    out_scores.sort(reverse=True)
    return out_scores[:TOPK], sorted(out_crib)


def render_html(results: List[dict], meta: dict) -> str:
    css = """body{background:#0f0d0a;color:#e8dcc0;font-family:Georgia,serif;
    max-width:1000px;margin:0 auto;padding:24px}h1{color:#c9a227;letter-spacing:.1em}
    table{border-collapse:collapse;width:100%;margin:8px 0 22px}th,td{border:1px solid
    #2d2615;padding:5px 9px;font-size:.85rem}th{color:#4ec9b0;text-align:left}
    .hit{color:#3fb950;font-weight:bold}.no{color:#8b949e}.meta{color:#a99c80;
    font-family:monospace;font-size:.8rem}code{color:#c9a227}"""
    rows = []
    for r in results:
        rows.append(f"<h2 style='color:#e8dcc0'>triplet {r['triplet']} · "
                    f"<code>{r['generator']}</code> · <code>{r['combiner']}</code>"
                    f" · seeds [{r['seed_start']:,}, {r['seed_start']+r['count']:,})"
                    f" · {r['elapsed']:.1f}s</h2>")
        if r.get("crib") is not None:
            m = r["crib_matches"]
            rows.append(f"<p class='{'hit' if m else 'no'}'>crib {r['crib']}: "
                        f"{'matches '+str(m) if m else 'NO match in range'}</p>")
            continue
        rows.append(f"<p class='meta'>decoy best-of-N null: "
                    f"{r['decoy_mean']:.3f} +/- {r['decoy_std']:.3f}</p>")
        tr = ["<tr><th>seed</th><th>structure</th><th>z</th><th>trustworthy</th></tr>"]
        for h in r["hits"]:
            cls = "hit" if h["trustworthy"] else "no"
            tr.append(f"<tr><td>{h['seed']}</td><td>{h['score']:.4f}</td>"
                      f"<td>{h['z']:.2f}</td><td class='{cls}'>"
                      f"{h['trustworthy']}</td></tr>")
        rows.append("<table>" + "".join(tr) + "</table>")
    any_hit = any(h["trustworthy"] for r in results for h in r.get("hits", [])) \
        or any(r.get("crib_matches") for r in results)
    verdict = ("A TRUSTWORTHY HIT was found — investigate (run the crib filter / "
               "decode and read)." if any_hit else
               "No trustworthy hit in the scanned space. Evidence against a "
               "keystream from these generators/seeds (or the structure oracle is "
               "underpowered without a crib).")
    return f"""<!doctype html><html><head><meta charset='utf-8'>
<title>EYES keyscan report</title><style>{css}</style></head><body>
<h1>E Y E S — keystream seed-scan</h1>
<p class='meta'>{html.escape(' · '.join(f'{k}: {v}' for k,v in meta.items()))}</p>
<p class='{'hit' if any_hit else 'no'}'><b>{html.escape(verdict)}</b></p>
{''.join(rows)}
<p class='meta'>Self-contained. Each row scored by joint per-message order
predictability of the triplet's decrypts vs a random-seed best-of-N null.</p>
</body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser(description="keystream seed-scan")
    ap.add_argument("--generators", default="nolla,minstd,xorshift32,lfsr32")
    ap.add_argument("--combiner", default="add",
                    choices=["add", "sub", "beaufort", "subst"])
    ap.add_argument("--seed-start", type=int, default=0)
    ap.add_argument("--count", type=int, default=1_000_000)
    ap.add_argument("--triplets", default="0,1,2",
                    help="which triplets (0,1,2) to scan")
    ap.add_argument("--body-start", type=int, default=25)
    ap.add_argument("--decoy-batches", type=int, default=8)
    ap.add_argument("--jobs", type=int, default=0)
    ap.add_argument("--crib", default="")
    ap.add_argument("--crib-msg", default="East 1")
    ap.add_argument("--crib-start", type=int, default=0)
    ap.add_argument("--html", default="")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    c = corpus_mod.load()
    N = c.N
    jobs = args.jobs or os.cpu_count() or 1
    gens = ["nolla"] if args.combiner == "subst" else args.generators.split(",")
    trip_idx = [int(x) for x in args.triplets.split(",")]
    triplets = [ks.TRIPLETS[i] for i in trip_idx]
    crib = [int(x) for x in args.crib.split(",")] if args.crib else None
    cmember_global = c.labels.index(args.crib_msg) if args.crib_msg in c.labels else 0

    # Runtime projection.
    sample_msgs = [list(c.ciphertexts[i]) for i in triplets[0]]
    t0 = time.time()
    for s in range(args.seed_start, args.seed_start + 1000):
        ks.structure_score(ks.decrypt_triplet(sample_msgs, s, gens[0],
                                               args.combiner, N), args.body_start)
    rate = 1000 / max(1e-6, time.time() - t0)
    passes = 1 if crib is not None else (1 + args.decoy_batches)
    total = args.count * len(triplets) * len(gens) * passes
    est_min = total / (rate * jobs) / 60
    print(f"~{rate:,.0f} scores/s/core x {jobs} cores; {total:,} evals "
          f"-> ~{est_min:.1f} min projected")
    if est_min > 30 and not args.force:
        print("Projected > 30 min. Re-run with --force or fewer --count/"
              "--generators/--decoy-batches. (GPU is the eventual home.)")
        return 3

    results = []
    for trip in triplets:
        msgs = [list(c.ciphertexts[i]) for i in trip]
        cmember = trip.index(cmember_global) if (crib is not None and
                                                 cmember_global in trip) else 0
        for gen in gens:
            t0 = time.time()
            print(f"\nscanning triplet {trip} · {gen} · {args.combiner} ...",
                  flush=True)
            best, cmatch = _run_range(msgs, gen, args.combiner, N,
                                      args.body_start, args.seed_start,
                                      args.count, jobs, crib, cmember,
                                      args.crib_start)
            entry = {"triplet": trip, "generator": gen, "combiner": args.combiner,
                     "seed_start": args.seed_start, "count": args.count,
                     "elapsed": time.time() - t0}
            if crib is not None:
                entry["crib"] = crib
                entry["crib_matches"] = cmatch
                print(f"  crib matches: {cmatch if cmatch else 'none'}")
            else:
                # Decoy best-of-N null.
                import numpy as np
                dmax = []
                for b in range(args.decoy_batches):
                    base = 1_000_000_000 + b * args.count
                    bb, _ = _run_range(msgs, gen, args.combiner, N,
                                       args.body_start, base, args.count, jobs)
                    dmax.append(bb[0][0] if bb else 0.0)
                dm = np.array(dmax, dtype=float)
                mu, sd = float(dm.mean()), float(dm.std(ddof=1) or 1e-9)
                hits = [{"seed": s, "score": sc, "z": (sc - mu) / sd,
                         "trustworthy": bool((sc - mu) / sd > 5 and sc > dm.max())}
                        for sc, s in best]
                entry.update({"hits": hits, "decoy_mean": mu, "decoy_std": sd})
                top = hits[0]
                print(f"  best seed {top['seed']}: structure {top['score']:.4f} "
                      f"z={top['z']:.2f} trustworthy={top['trustworthy']}")
            results.append(entry)

    if args.html:
        meta = {"corpus_N": N, "combiner": args.combiner,
                "seeds": f"{args.seed_start:,}..{args.seed_start+args.count:,}",
                "jobs": jobs}
        Path(args.html).write_text(render_html(results, meta), encoding="utf-8")
        print(f"\nwrote {args.html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
