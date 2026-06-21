#!/usr/bin/env python3
"""Independent verifier for an EyeWitness fingerprint.json.

This script deliberately depends on **nothing but the Python standard library +
numpy**.  It does not import noita_eye_core, EyeWitness, or any of the rest of the
stack.  Point it at a ``fingerprint.json`` and the raw ``corpus.json`` and it
re-derives the three load-bearing claims from scratch:

  1. the corpus hash matches (the claims are about THIS data),
  2. the messages are in depth (difference-IoC far above a shuffle null),
  3. the winning grouping (TRIPLETS vs PAIRS_PLUS_E5 vs ...) is really the
     maximum-likelihood partition under the link/unlink Binomial model,
  4. each reported crib is an actual identical run in the raw runes.

The point is anti-fragility against "I don't trust your code": a skeptic can read
these ~150 lines, run them, and confirm the headline without taking anything else
on faith.

Usage::

    python3 verify_fingerprint.py [fingerprint.json] [--corpus corpus.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from itertools import combinations
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DEFAULT_CORPUS = HERE.parent / "noita_eye_core" / "corpus.json"


def _default_corpus() -> Path:
    env = os.environ.get("EYES_CORPUS_PATH")
    return Path(env) if env else DEFAULT_CORPUS

PAIRS_PLUS_E5 = ((0, 1), (2, 3), (4, 5), (6, 7), (8,))
TRIPLETS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
ALL_NINE = (tuple(range(9)),)
ALL_SINGLETON = tuple((i,) for i in range(9))
NAMED = {"PAIRS_PLUS_E5": PAIRS_PLUS_E5, "TRIPLETS": TRIPLETS,
         "ALL_NINE": ALL_NINE, "ALL_SINGLETON": ALL_SINGLETON}


def load_corpus(path):
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    cts = [[int(x) for x in ct] for ct in raw["ciphertexts"]]
    return int(raw["deck_size"]), cts


def corpus_hash(deck_size, cts):
    blob = json.dumps({"deck_size": deck_size, "ciphertexts": cts},
                      sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def ioc(seq):
    T = len(seq)
    if T < 2:
        return 0.0
    _, counts = np.unique(np.asarray(seq), return_counts=True)
    return float(np.sum(counts * (counts - 1)) / (T * (T - 1)))


def diff_ioc(a, b, N):
    L = min(len(a), len(b))
    d = [(a[t] - b[t]) % N for t in range(L)]
    return ioc(d)


def mean_pair_diff_ioc(cts, N):
    vals = [diff_ioc(cts[i], cts[j], N)
            for i, j in combinations(range(len(cts)), 2)]
    return float(np.mean(vals))


def depth_z(cts, N, n_null=500, seed=0):
    rng = np.random.default_rng(seed)
    obs = mean_pair_diff_ioc(cts, N)
    null = []
    for _ in range(n_null):
        sh = [rng.permutation(np.asarray(m)).tolist() for m in cts]
        null.append(mean_pair_diff_ioc(sh, N))
    null = np.asarray(null)
    z = (obs - null.mean()) / null.std(ddof=1)
    return obs, float(z)


def pair_counts(cts):
    out = {}
    for i, j in combinations(range(len(cts)), 2):
        L = min(len(cts[i]), len(cts[j]))
        eq = sum(1 for t in range(L) if cts[i][t] == cts[j][t])
        out[(i, j)] = (eq, L)
    return out


def within_pairs(partition):
    s = set()
    for g in partition:
        for a, b in combinations(sorted(g), 2):
            s.add((a, b))
    return s


def binom_term(x, n, q):
    if n == 0:
        return 0.0
    q = min(max(q, 1e-9), 1 - 1e-9)
    return x * math.log(q) + (n - x) * math.log(1 - q)


def score_partition(partition, pc):
    within = within_pairs(partition)
    sx_in = sn_in = sx_out = sn_out = 0
    for (i, j), (x, n) in pc.items():
        if (i, j) in within:
            sx_in += x; sn_in += n
        else:
            sx_out += x; sn_out += n
    q_link = sx_in / sn_in if sn_in else 0.0
    q_unlink = sx_out / sn_out if sn_out else 0.0
    return sum(binom_term(x, n, q_link if (i, j) in within else q_unlink)
               for (i, j), (x, n) in pc.items())


def main():
    ap = argparse.ArgumentParser(description="verify an EyeWitness fingerprint")
    ap.add_argument("fingerprint", nargs="?",
                    default=str(HERE / "fingerprint.json"))
    ap.add_argument("--corpus", default=None,
                    help="corpus JSON (default: EYES_CORPUS_PATH or noita_eye_core/corpus.json)")
    args = ap.parse_args()

    fp = json.loads(Path(args.fingerprint).read_text(encoding="utf-8"))
    N, cts = load_corpus(args.corpus or str(_default_corpus()))
    checks = []

    # 1. corpus identity
    h = corpus_hash(N, cts)
    checks.append(("corpus sha256 matches the fingerprint",
                   h == fp["corpus_sha256"]))

    # 2. depth
    obs, z = depth_z(cts, N, n_null=500, seed=0)
    checks.append((f"messages are in depth (diff-IoC z={z:.1f} > 5)", z > 5))

    # 3. grouping winner is the max-likelihood partition
    pc = pair_counts(cts)
    scores = {name: score_partition(p, pc) for name, p in NAMED.items()}
    winner = max(scores, key=scores.get)
    claimed = fp["grouping"]["winner"]
    checks.append((f"max-likelihood partition is {winner} "
                   f"(fingerprint claims {claimed})", winner == claimed))
    runner = sorted(scores, key=scores.get, reverse=True)[1]
    checks.append((f"{winner} beats runner-up {runner} by "
                   f"{scores[winner]-scores[runner]:.1f} logL",
                   scores[winner] - scores[runner] > 0))

    # 4. cribs are real identical runs
    crib_ok = True
    for cr in fp.get("cribs", []):
        mi = cr["member_indices"]; s = cr["start"]; ln = cr["length"]
        cols = [cts[m][s:s + ln] for m in mi]
        if not all(col == cols[0] for col in cols):
            crib_ok = False
    checks.append((f"all {len(fp.get('cribs', []))} cribs are real identical runs",
                   crib_ok))

    print("EyeWitness fingerprint verification")
    print("-" * 60)
    for label, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in checks if ok)
    print("-" * 60)
    print(f"{n_ok}/{len(checks)} independent checks passed")
    print("\nrecomputed partition log-likelihoods (higher = better):")
    for name in sorted(scores, key=scores.get, reverse=True):
        print(f"  {name:16} {scores[name]:10.1f}")
    return 0 if n_ok == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
