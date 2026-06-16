#!/usr/bin/env python3
"""EyeCrack — decryption attacks on the Noita eye corpus, fed by EyeWitness.

EyeCrack is Effort B: the *bet*.  It tries to actually recover plaintext, using
the depth structure EyeWitness confirms.  Everything routes through the calibrated
joint oracle (:mod:`noita_eye_core.oracle`) so a candidate is only ever called a
"hit" if it survives a Bonferroni correction for the whole search — the trust
gate the unconstrained seed scans lack.

Three subcommands, cheap-to-expensive:

* ``crib``  — *exact, no LM, works on the real corpus today.*  A guessed plaintext
  fragment over a span pins the shared keystream and (because the key is shared)
  reveals that span in **every** in-depth message at once.  Feed it the equal-span
  cribs from ``fingerprint.json``.
* ``viterbi`` — globally optimal keystream under a 1st-order model (needs a
  symbol-space LM; exact MAP given the model).
* ``seedscan`` — the GPU-ready brute force: ``(PRNG x seed x combiner)`` ->
  keystream -> joint score, with a null-calibrated, Bonferroni-corrected verdict.
  This CPU reference mirrors the kernel structure EyeStat runs on the GPU
  (keystream-gen + decrypt + cheap score is the kernel; the calibrated survivor
  test is the CPU stage).
* ``demo`` — plants a NollaPRNG keystream with a known seed and recovers it
  uniquely, proving the pipeline end-to-end.

Honesty: on the *real* corpus the LM-based prongs need a symbol-space language
model, which is unknown without a rune->letter mapping (EyeStat's Hungarian
mapping + dictionary is the production answer).  The ``crib`` prong needs no LM
and is exact today.  See README.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional, Sequence

import numpy as np

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import cipher_ops          # noqa: E402
import corpus as corpus_mod  # noqa: E402
import depth as depth_mod   # noqa: E402
from lm import MarkovModel  # noqa: E402
from oracle import JointOracle, markov_scorer  # noqa: E402
from prng import NollaPRNG  # noqa: E402


# ---------------------------------------------------------------------------
# Fingerprint contract (from EyeWitness) — optional
# ---------------------------------------------------------------------------

def load_fingerprint(path: Optional[str]) -> Optional[dict]:
    if not path:
        return None
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def resolve_in_depth(c: corpus_mod.Corpus, fp: Optional[dict]) -> List[int]:
    if fp and fp.get("for_eyecrack", {}).get("in_depth_set"):
        return list(fp["for_eyecrack"]["in_depth_set"])
    rep = depth_mod.confirm_depth(c, n_null=300, seed=0)
    return list(range(c.num_messages)) if rep.significance.z > 5 else [0]


# ---------------------------------------------------------------------------
# Fast vectorised symbol-space scorer (for the scan); matches MarkovModel.logprob
# ---------------------------------------------------------------------------

def _score_plain(plain: np.ndarray, uni: np.ndarray, bi: np.ndarray) -> float:
    if plain.size == 0:
        return 0.0
    total = float(uni[plain[0]])
    if plain.size > 1:
        total += float(bi[plain[:-1], plain[1:]].sum())
    return total


def _pooled_per_symbol(keystream: np.ndarray, msgs: Sequence[np.ndarray],
                       N: int, mode: str, uni: np.ndarray, bi: np.ndarray
                       ) -> float:
    if mode == "add":
        dec = lambda m: (m - keystream[:len(m)]) % N
    elif mode == "sub":
        dec = lambda m: (m + keystream[:len(m)]) % N
    elif mode == "beaufort":
        dec = lambda m: (keystream[:len(m)] - m) % N
    else:
        raise KeyError(mode)
    tot = 0.0
    nsym = 0
    for m in msgs:
        p = dec(m)
        tot += _score_plain(p, uni, bi)
        nsym += len(p)
    return tot / nsym if nsym else 0.0


# ---------------------------------------------------------------------------
# Subcommand: crib-drag (exact, no LM)
# ---------------------------------------------------------------------------

def cmd_crib(args) -> int:
    c = corpus_mod.load(args.corpus) if args.corpus else corpus_mod.load()
    fp = load_fingerprint(args.fingerprint)

    if args.plain:
        plain = [int(x) for x in args.plain.split(",")]
    else:
        print("crib-drag needs a guessed plaintext fragment (--plain a,b,c,...).")
        if fp and fp.get("cribs"):
            print("\nEqual-span cribs from the fingerprint (shared plaintext, "
                  "value unknown — guess one member to reveal all):")
            for cr in fp["cribs"][:10]:
                print(f"  {'+'.join(cr['members'])}  @pos {cr['start']} "
                      f"len {cr['length']}  p={cr['p_value']:.3g}")
        return 2

    ref = c.labels.index(args.ref) if args.ref in c.labels else int(args.ref)
    res = depth_mod.crib_drag(c, ref_index=ref, start=args.start, plain=plain,
                              mode=args.mode)
    print(f"crib on {c.labels[ref]} @pos {args.start} (mode={args.mode})")
    print(f"implied shared keystream k[{args.start}:{args.start+len(plain)}] "
          f"= {res.keystream}\n")
    print("revealed plaintext span in every message (shared key):")
    for i in range(c.num_messages):
        print(f"  {c.labels[i]:8} -> {res.revealed[i]}")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: Viterbi MAP keystream (needs a symbol-space LM)
# ---------------------------------------------------------------------------

def cmd_viterbi(args) -> int:
    c = corpus_mod.load(args.corpus) if args.corpus else corpus_mod.load()
    model = _load_or_planted_model(args.lm, c.N)
    res = depth_mod.solve_keystream_viterbi(c, model, mode=args.mode)
    print(f"Viterbi MAP keystream (mode={args.mode}, total logprob "
          f"{res.total_logprob:.1f})")
    print(f"k[0:20] = {res.keystream[:20]}")
    print("\nNOTE: on the real corpus the unigram is flat, so unsupervised "
          "Viterbi is under-determined (see noita_eye_core/README). Trust the "
          "crib prong; use this with a real LM/mapping.")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: seed scan (GPU-ready brute force, calibrated)
# ---------------------------------------------------------------------------

def _keystream_for_seed(prng_name: str, seed: int, N: int, length: int
                        ) -> np.ndarray:
    if prng_name == "nolla":
        return np.asarray(NollaPRNG(seed).keystream_mod(N, length))
    if prng_name == "uniform":   # deterministic generic stream (demo/control)
        rng = np.random.default_rng(seed)
        return rng.integers(0, N, size=length)
    raise KeyError(f"unknown prng {prng_name!r}")


def seedscan(c: corpus_mod.Corpus, model: MarkovModel, prng_name: str,
             seed_start: int, count: int, mode: str, in_depth: List[int],
             topk: int = 16, n_null: int = 2000,
             seed_null: int = 0) -> List[dict]:
    """Scan ``count`` seeds; score every seed cheaply, then run the calibrated
    joint oracle on the top-``topk`` survivors with Bonferroni over ``count``."""
    N = c.N
    msgs = [np.asarray(c.ciphertexts[i]) for i in in_depth]
    Lmax = max(len(m) for m in msgs)
    uni = model.uni_logp
    bi = model.bi_logp

    scores = np.empty(count, dtype=np.float64)
    for s in range(count):
        ks = _keystream_for_seed(prng_name, seed_start + s, N, Lmax)
        scores[s] = _pooled_per_symbol(ks, msgs, N, mode, uni, bi)

    order = np.argsort(scores)[::-1][:topk]

    scorer = markov_scorer(model)
    oracle = JointOracle([c.ciphertexts[i] for i in in_depth], N, scorer,
                         mode=mode, in_depth_set=list(range(len(in_depth))))
    oracle.build_null(n_null=n_null, rng=np.random.default_rng(seed_null))

    hits: List[dict] = []
    for s in order:
        seed = seed_start + int(s)
        ks = _keystream_for_seed(prng_name, seed, N, Lmax).tolist()
        v = oracle.evaluate(ks, n_trials=count)
        hits.append({"seed": seed, "per_symbol": float(scores[s]),
                     "z": v.significance.z, "p": v.p_analytic,
                     "q_bonferroni": v.q_bonferroni,
                     "trustworthy": bool(v.trustworthy)})
    hits.sort(key=lambda h: -h["z"])
    return hits


def cmd_seedscan(args) -> int:
    c = corpus_mod.load(args.corpus) if args.corpus else corpus_mod.load()
    fp = load_fingerprint(args.fingerprint)
    in_depth = resolve_in_depth(c, fp)
    model = _load_or_planted_model(args.lm, c.N)

    print(f"seed scan: prng={args.prng} seeds=[{args.seed_start}, "
          f"{args.seed_start+args.count})  mode={args.mode}  "
          f"in_depth={len(in_depth)} msgs")
    hits = seedscan(c, model, args.prng, args.seed_start, args.count, args.mode,
                    in_depth, topk=args.topk)
    print("\ntop candidates (by joint z):")
    print("  seed         per_symbol     z       q(Bonf)   trustworthy")
    for h in hits[:10]:
        print(f"  {h['seed']:<11} {h['per_symbol']:>9.4f}  {h['z']:>7.2f}  "
              f"{h['q_bonferroni']:>9.2g}   {h['trustworthy']}")
    tw = [h for h in hits if h["trustworthy"]]
    print(f"\n{len(tw)} trustworthy hit(s) after Bonferroni over "
          f"{args.count} seeds.")
    if not tw:
        print("=> no seed in this window survives correction. Widen the range "
              "or change PRNG/combiner. (A null result here is still a result.)")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: demo — plant a seed, recover it uniquely
# ---------------------------------------------------------------------------

def _planted_language_model(N: int, seed: int) -> MarkovModel:
    rng = np.random.default_rng(seed)
    bi = np.zeros((N, N))
    for a in range(N):
        row = rng.random(N) ** 8
        row[(a + 1) % N] += 5.0
        row[(a * 7 + 3) % N] += 3.0
        bi[a] = row / row.sum()
    return MarkovModel(N, np.log(np.full(N, 1.0 / N)), np.log(bi))


def _emit(model: MarkovModel, T: int, rng: np.random.Generator) -> List[int]:
    N = model.N
    bi = np.exp(model.bi_logp)
    s = int(rng.integers(0, N))
    out = [s]
    for _ in range(T - 1):
        s = int(rng.choice(N, p=bi[s]))
        out.append(s)
    return out


def cmd_demo(args) -> int:
    N = 83
    rng = np.random.default_rng(args.seed)
    model = _planted_language_model(N, seed=1)
    true_seed = args.true_seed
    lengths = [99, 103, 118, 102, 137, 124, 119, 120, 114]
    Lmax = max(lengths)

    true_key = NollaPRNG(true_seed).keystream_mod(N, Lmax)
    plains = [_emit(model, L, rng) for L in lengths]
    cipher = tuple(tuple((plains[i][t] + true_key[t]) % N
                         for t in range(lengths[i])) for i in range(9))
    synth = corpus_mod.Corpus(deck_size=N,
                              labels=tuple(f"M{i}" for i in range(9)),
                              ciphertexts=cipher, lengths=tuple(lengths),
                              sigma0_targets=None)

    window = args.count
    start = true_seed - window // 2
    print(f"DEMO: planted NollaPRNG seed={true_seed}; scanning "
          f"[{start}, {start+window}) with the joint oracle...")
    hits = seedscan(synth, model, "nolla", start, window, "add",
                    list(range(9)), topk=8)
    tw = [h for h in hits if h["trustworthy"]]
    print("\ntop candidates:")
    for h in hits[:5]:
        marker = "  <== planted" if h["seed"] == true_seed else ""
        print(f"  seed {h['seed']:<10} z={h['z']:>7.2f}  "
              f"q={h['q_bonferroni']:.2g}  trustworthy={h['trustworthy']}{marker}")
    ok = (len(tw) == 1 and tw[0]["seed"] == true_seed)
    print(f"\nrecovered the planted seed uniquely: {ok}")
    return 0 if ok else 1


# ---------------------------------------------------------------------------

def _load_or_planted_model(spec: Optional[str], N: int) -> MarkovModel:
    if spec in (None, "planted"):
        return _planted_language_model(N, seed=1)
    # A JSON file of symbol sequences (lists of ints in [0,N)) to train on.
    data = json.loads(Path(spec).read_text(encoding="utf-8"))
    seqs = data["sequences"] if isinstance(data, dict) else data
    return MarkovModel.from_int_sequences(seqs, N, add_k=0.5)


def main() -> int:
    ap = argparse.ArgumentParser(description="EyeCrack decryption attacks")
    ap.add_argument("--corpus", default=None)
    ap.add_argument("--fingerprint", default=str(HERE.parent / "eyewitness"
                                                 / "fingerprint.json"))
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("crib", help="exact crib-drag (no LM)")
    p.add_argument("--ref", default="East 3")
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--plain", default="")
    p.add_argument("--mode", default="add", choices=["add", "sub", "beaufort"])
    p.set_defaults(func=cmd_crib)

    p = sub.add_parser("viterbi", help="MAP keystream under a 1st-order LM")
    p.add_argument("--lm", default="planted")
    p.add_argument("--mode", default="add", choices=["add", "sub", "beaufort"])
    p.set_defaults(func=cmd_viterbi)

    p = sub.add_parser("seedscan", help="calibrated PRNG seed brute force")
    p.add_argument("--prng", default="nolla", choices=["nolla", "uniform"])
    p.add_argument("--seed-start", type=int, default=0)
    p.add_argument("--count", type=int, default=5000)
    p.add_argument("--mode", default="add", choices=["add", "sub", "beaufort"])
    p.add_argument("--lm", default="planted")
    p.add_argument("--topk", type=int, default=16)
    p.set_defaults(func=cmd_seedscan)

    p = sub.add_parser("demo", help="plant a seed and recover it end-to-end")
    p.add_argument("--true-seed", type=int, default=1234567)
    p.add_argument("--count", type=int, default=400)
    p.add_argument("--seed", type=int, default=7)
    p.set_defaults(func=cmd_demo)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
