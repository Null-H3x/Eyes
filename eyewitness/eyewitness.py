#!/usr/bin/env python3
"""EyeWitness — verifiable structural fingerprint of the Noita eye corpus.

EyeWitness answers ONE falsifiable question and signs the answer so anyone can
re-check it: **are the 9 messages organised as pairs + a special E5 (Theory 1),
or as triplets (Theory 2)?**  It does not try to decrypt anything — that is
EyeCrack's job.  EyeWitness produces a deterministic, null-calibrated artifact
(``fingerprint.json``) plus a human report, and ships a standalone
``verify_fingerprint.py`` (numpy only, no dependency on this stack) so a skeptic
can reproduce the headline numbers straight from the raw runes.

The logic rests on the already-established depth finding (the messages share a
position keystream, z~60): under a linear combiner with a shared key,
``c_i[t] == c_j[t]  <=>  p_i[t] == p_j[t]``, so identical ciphertext spans are
identical plaintext spans, and "which messages group together" becomes a matter
of arithmetic with p-values, not opinion.

Run::

    python3 eyewitness.py                 # report + write fingerprint.json
    python3 eyewitness.py --out fp.json   # choose the artifact path
    python3 verify_fingerprint.py fp.json # independent re-check (numpy only)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import depth as depth_mod     # noqa: E402
import grouping               # noqa: E402


SCHEMA_VERSION = 1


def corpus_hash(c: corpus_mod.Corpus) -> str:
    """Stable SHA-256 over the ciphertexts + deck size — the data identity that
    the verifier re-checks so claims are pinned to *this* corpus."""
    blob = json.dumps({"deck_size": c.deck_size,
                       "ciphertexts": [list(ct) for ct in c.ciphertexts]},
                      sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def build_fingerprint(c: corpus_mod.Corpus, n_null: int = 1000,
                      seed: int = 0, span_min_len: int = 5) -> dict:
    N = c.N
    messages = [list(ct) for ct in c.ciphertexts]

    dep = depth_mod.confirm_depth(c, n_null=n_null, seed=seed)
    q_depth = grouping.depth_baseline_rate(messages)

    pair_stats = grouping.agreement_significance(messages, N, baseline=q_depth)
    adj = grouping.significant_pair_graph(pair_stats, alpha=0.01)
    cliques = grouping.maximal_cliques(adj)

    ranked = grouping.compare_partitions(messages)

    # Robustness: does the winner survive stripping the shared opening? (defeats
    # the "it's just shared headers" objection). Re-run on increasingly deep
    # tails of every message.
    robustness = []
    for drop in (0, 5, 12, 25, 40):
        tail = [m[drop:] for m in messages]
        if min(len(t) for t in tail) < 10:
            break
        rr = grouping.compare_partitions(tail)
        robustness.append({
            "drop_prefix": drop, "winner": rr[0].name,
            "margin_over_runner_up": rr[0].loglik - rr[1].loglik,
            "mean_within": rr[0].mean_within, "mean_across": rr[0].mean_across})

    spans = grouping.top_spans(messages, N, subset_sizes=(2, 3),
                               min_len=span_min_len, n_null=n_null, seed=seed,
                               max_report=15)

    # Power: shortest run we could even call significant for a representative
    # pair and triple.
    mdr_pair = grouping.min_detectable_run(messages, (0, 1), N, n_null=n_null,
                                           seed=seed)
    mdr_triple = grouping.min_detectable_run(messages, (0, 1, 2), N,
                                             n_null=n_null, seed=seed)

    # Verdicts.
    winner = ranked[0]
    runner = ranked[1]
    clique_sizes = sorted({len(cl) for cl in cliques}) if cliques else []
    e5 = c.num_messages - 1
    e5_in_clique = any(e5 in cl for cl in cliques)

    if winner.name == "PAIRS_PLUS_E5":
        theory = "Theory 1 (pairs + special E5)"
    elif winner.name == "TRIPLETS":
        theory = "Theory 2 (triplets)"
    else:
        theory = winner.name

    # in-depth set = the messages EyeCrack must satisfy jointly (here: all, since
    # depth is global). cribs = significant equal spans for crib-drag.
    in_depth_set = list(range(c.num_messages)) if dep.significance.z > 5 else []
    cribs = [{"members": [c.labels[m] for m in sp.members],
              "member_indices": list(sp.members),
              "start": sp.start, "length": sp.length,
              "symbols": list(sp.symbols), "p_value": sp.p_value}
             for sp in spans if sp.p_value < 0.01]

    return {
        "schema_version": SCHEMA_VERSION,
        "tool": "EyeWitness",
        "corpus_sha256": corpus_hash(c),
        "deck_size": N,
        "labels": list(c.labels),
        "lengths": list(c.lengths),
        "depth": {
            "mean_pair_diff_ioc": dep.mean_pair_diff_ioc,
            "uniform_baseline": dep.uniform_baseline,
            "equal_fraction": dep.equal_fraction,
            "z": dep.significance.z,
            "p_value": dep.significance.p_value,
            "n_null": dep.significance.n_null,
            "shared_keystream": bool(dep.significance.z > 5),
            "baseline_collision_rate": q_depth,
        },
        "grouping": {
            "winner": winner.name,
            "theory": theory,
            "winner_loglik": winner.loglik,
            "winner_lr_vs_baseline": winner.lr_vs_baseline,
            "winner_q_link": winner.q_link,
            "winner_q_unlink": winner.q_unlink,
            "winner_mean_within": winner.mean_within,
            "winner_mean_across": winner.mean_across,
            "margin_over_runner_up": winner.loglik - runner.loglik,
            "runner_up": runner.name,
            "ranking": [{"name": s.name, "loglik": s.loglik,
                         "lr_vs_baseline": s.lr_vs_baseline,
                         "q_link": s.q_link, "q_unlink": s.q_unlink,
                         "partition": [list(g) for g in s.partition]}
                        for s in ranked],
            "data_driven_cliques": [list(cl) for cl in cliques],
            "data_driven_clique_sizes": clique_sizes,
            "e5_index": e5,
            "e5_in_significant_clique": e5_in_clique,
            "robustness_prefix_drop": robustness,
            "winner_survives_prefix_strip": bool(
                robustness and all(r["winner"] == winner.name
                                   for r in robustness)),
        },
        "power": {
            "min_detectable_run_pair": mdr_pair,
            "min_detectable_run_triple": mdr_triple,
            "note": "shortest identical run that clears alpha=0.01 under the "
                    "within-message shuffle null at these message lengths",
        },
        "pair_agreement": [{"i": ps.i, "j": ps.j,
                            "labels": [c.labels[ps.i], c.labels[ps.j]],
                            "overlap": ps.overlap, "equal_rate": ps.equal_rate,
                            "baseline": ps.chance_rate, "z": ps.z,
                            "q_value": ps.q_value}
                           for ps in pair_stats],
        "cribs": cribs,
        "for_eyecrack": {
            "in_depth_set": in_depth_set,
            "combiner_candidates": ["add", "sub", "beaufort"],
            "note": "EyeCrack must make every in_depth_set message decrypt "
                    "jointly; cribs pin the shared keystream over their spans.",
        },
    }


def format_report(fp: dict) -> str:
    L = []
    g = fp["grouping"]
    d = fp["depth"]
    L.append("=" * 70)
    L.append("EYEWITNESS — structural fingerprint")
    L.append("=" * 70)
    L.append(f"corpus sha256 : {fp['corpus_sha256']}")
    L.append(f"messages      : {len(fp['labels'])}  alphabet N={fp['deck_size']}")
    L.append("")
    L.append("[depth] shared position-keystream (the premise)")
    L.append(f"  difference-IoC z = {d['z']:.1f}  (p={d['p_value']:.3g})  "
             f"shared_keystream={d['shared_keystream']}")
    L.append(f"  baseline collision rate (depth-only) = {d['baseline_collision_rate']:.4f}")
    L.append("")
    L.append("[grouping] model selection over named partitions")
    L.append("  partition         logL        LR-vs-baseline   q_link  q_unlink")
    for s in g["ranking"]:
        L.append(f"  {s['name']:16} {s['loglik']:10.1f}   {s['lr_vs_baseline']:12.1f}"
                 f"   {s['q_link']:.3f}   {s['q_unlink']:.3f}")
    L.append("")
    L.append(f"  WINNER : {g['winner']}  -> {g['theory']}")
    L.append(f"  margin over runner-up ({g['runner_up']}): "
             f"{g['margin_over_runner_up']:.1f} log-likelihood")
    L.append(f"  within-group agreement {g['winner_mean_within']:.1%} vs "
             f"across-group {g['winner_mean_across']:.1%}")
    L.append("")
    L.append("[robustness] does the winner survive stripping the shared opening?")
    for r in g.get("robustness_prefix_drop", []):
        L.append(f"  drop first {r['drop_prefix']:>2}: winner={r['winner']:14} "
                 f"margin={r['margin_over_runner_up']:6.1f}  "
                 f"within={r['mean_within']:.1%} across={r['mean_across']:.1%}")
    L.append(f"  winner survives prefix strip: {g['winner_survives_prefix_strip']}")
    L.append("")
    L.append("[data-driven] significant-agreement cliques (no theory imposed)")
    L.append(f"  cliques      : {g['data_driven_cliques']}")
    L.append(f"  clique sizes : {g['data_driven_clique_sizes']}  "
             f"(2 => pairs, 3 => triplets)")
    L.append(f"  E5 (idx {g['e5_index']}) in a significant clique: "
             f"{g['e5_in_significant_clique']}")
    L.append("")
    L.append("[power] shortest identical run we could call significant")
    L.append(f"  pair >= {fp['power']['min_detectable_run_pair']}   "
             f"triple >= {fp['power']['min_detectable_run_triple']}")
    L.append("")
    L.append(f"[cribs] {len(fp['cribs'])} significant equal-spans (for EyeCrack)")
    for cr in fp["cribs"][:8]:
        L.append(f"  {'+'.join(cr['members']):20} @pos {cr['start']:>3} "
                 f"len {cr['length']:>3}  p={cr['p_value']:.3g}")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description="EyeWitness structural fingerprint")
    ap.add_argument("--corpus", type=str, default=None,
                    help="path to corpus.json (default: noita_eye_core)")
    ap.add_argument("--out", type=str, default=str(HERE / "fingerprint.json"))
    ap.add_argument("--n-null", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    c = corpus_mod.load(args.corpus) if args.corpus else corpus_mod.load()
    fp = build_fingerprint(c, n_null=args.n_null, seed=args.seed)

    out = Path(args.out)
    out.write_text(json.dumps(fp, indent=2), encoding="utf-8")
    if not args.quiet:
        print(format_report(fp))
        print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
