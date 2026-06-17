#!/usr/bin/env python3
"""GPU port of the crib-globality test (additive scalar-keystream branch).

Mirrors ``noita_eye_core.globality`` but vectorised over a ``cupy``-or-``numpy``
backend (``xp``), so it validates on CPU here (numpy) and runs unchanged on the
GPU (cupy) — no separate CUDA source to keep in sync.

Pipeline, per seed batch:
  1. generate the scalar keystream prefix (nolla / minstd / xorshift32 / lfsr32)
  2. repeat-pattern crib filter (mapping-free): keep seeds whose keystream
     reproduces the crib word's equal-letter ciphertext differences
  3. for survivors, generate the full keystream, decrypt ALL nine messages, and
     score each with order-predictability (H(X)-H(X|prev), the exact CPU metric)
  4. z each message vs a random-seed decoy null; verdict global / local / none

Every vectorised primitive is cross-validated byte/score-exact against the CPU
references (keyscan generators, langdetect.order_predictability) in selftest, so
the GPU path is trustworthy even though this box has no GPU.

    python3 globality_gpu.py                      # validate on CPU (numpy)
    python3 globality_gpu.py --crib-word messages --crib-pos 3 --crib-pos-end 40 \
        --generators all --seed-end 100000000 --html ../globality_gpu.html
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

try:
    import cupy as _cp
    xp = _cp
    GPU = True
except Exception:                       # pragma: no cover - depends on host
    xp = np
    GPU = False

CORE = Path(__file__).resolve().parent.parent / "noita_eye_core"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

import keyscan as ks            # noqa: E402  (CPU helpers: repeat_constraints, _markov)

N_DEFAULT = 83
TRIPLETS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
GENERATORS = ("nolla", "minstd", "xorshift32", "lfsr32")


# ---------------------------------------------------------------------------
# Vectorised scalar generators -> keystream (n_seeds, L), values in [0, N)
# (each validated byte-exact against keyscan.gen_* in selftest)
# ---------------------------------------------------------------------------

def _i32(x):
    return ((x + 0x80000000) & 0xFFFFFFFF).astype(xp.int64) - 0x80000000


def _ks_nolla(seeds, N: int, L: int):
    INT_MAX = 2147483647
    s = _i32(seeds.astype(xp.int64).copy())
    out = xp.empty((seeds.shape[0], L), dtype=xp.int64)
    for t in range(L):
        t1 = _i32(s * 0x41A7)
        q = xp.trunc(s / 0x1F31D).astype(xp.int64)      # C trunc-toward-zero div
        t2 = _i32(q * (-INT_MAX))
        v4 = _i32(t1 + t2)
        v4 = xp.where(v4 < 0, v4 + INT_MAX, v4)
        s = v4
        out[:, t] = (N * s * 4.656612875e-10).astype(xp.int64)
    return out


def _ks_minstd(seeds, N: int, L: int):
    x = (seeds.astype(xp.int64) % 2147483646) + 1
    out = xp.empty((seeds.shape[0], L), dtype=xp.int64)
    for t in range(L):
        x = (16807 * x) % 2147483647
        out[:, t] = x % N
    return out


def _ks_xorshift32(seeds, N: int, L: int):
    x = seeds.astype(xp.uint64) & xp.uint64(0xFFFFFFFF)
    x = xp.where(x == 0, xp.uint64(0x1234), x).astype(xp.uint64)
    M = xp.uint64(0xFFFFFFFF)
    out = xp.empty((seeds.shape[0], L), dtype=xp.int64)
    for t in range(L):
        x ^= (x << xp.uint64(13)) & M
        x ^= x >> xp.uint64(17)
        x ^= (x << xp.uint64(5)) & M
        out[:, t] = (x % xp.uint64(N)).astype(xp.int64)
    return out


def _ks_lfsr32(seeds, N: int, L: int):
    x = seeds.astype(xp.uint64) & xp.uint64(0xFFFFFFFF)
    x = xp.where(x == 0, xp.uint64(0xACE1), x).astype(xp.uint64)
    out = xp.empty((seeds.shape[0], L), dtype=xp.int64)
    for t in range(L):
        lsb = x & xp.uint64(1)
        x = x >> xp.uint64(1)
        x = xp.where(lsb == xp.uint64(1), x ^ xp.uint64(0xA3000000), x)
        out[:, t] = (x % xp.uint64(N)).astype(xp.int64)
    return out


_GEN = {"nolla": _ks_nolla, "minstd": _ks_minstd,
        "xorshift32": _ks_xorshift32, "lfsr32": _ks_lfsr32}


def keystream_batch(generator: str, seeds, N: int, L: int):
    return _GEN[generator](seeds, N, L)


# ---------------------------------------------------------------------------
# Repeat-pattern crib filter (mapping-free, additive)
# ---------------------------------------------------------------------------

def repeat_filter(member_ct: Sequence[int], word: str, position: int,
                  generator: str, seeds, N: int):
    """Boolean mask over ``seeds``: keystream reproduces the crib's equal-letter
    ciphertext differences at ``position`` in ``member_ct``."""
    cons = ks.repeat_constraints(word)
    P = position + len(word)
    K = keystream_batch(generator, seeds, N, P)         # (nseed, P)
    if not cons:
        return xp.ones(seeds.shape[0], dtype=bool)      # no constraint -> all pass
    mask = xp.ones(seeds.shape[0], dtype=bool)
    for (i, j) in cons:
        d = (int(member_ct[position + i]) - int(member_ct[position + j])) % N
        mask &= ((K[:, position + i] - K[:, position + j]) % N == d)
    return mask


# ---------------------------------------------------------------------------
# Vectorised order-predictability  H(X) - H(X|prev)  (exact CPU match)
# ---------------------------------------------------------------------------

def order_pred_batch(D, N: int, body_start: int = 0, add_k: float = 0.5,
                     sub: int = 4096):
    """``D`` is (nseed, L) int; returns (nseed,) order-predictability.  Processed
    in sub-batches to bound the (sub, N, N) bigram tensor."""
    D = D[:, body_start:]
    nseed, L = D.shape
    if L < 3:
        return xp.zeros(nseed)
    out = xp.empty(nseed)
    rows = xp.arange(min(sub, nseed))
    for lo in range(0, nseed, sub):
        hi = min(lo + sub, nseed)
        b = hi - lo
        Db = D[lo:hi]
        r = rows[:b]
        uni = xp.zeros((b, N))
        for t in range(L):
            uni[r, Db[:, t]] += 1
        pu = uni / L
        Hu = -xp.where(pu > 0, pu * xp.log2(xp.where(pu > 0, pu, 1.0)), 0.0).sum(1)
        bi = xp.zeros((b, N, N))
        for t in range(L - 1):
            bi[r, Db[:, t], Db[:, t + 1]] += 1
        ca = bi.sum(2)
        k = (bi > 0).sum(2)
        denom = ca + add_k * k
        denom = xp.where(denom > 0, denom, 1.0)
        p = (bi + add_k) / denom[:, :, None]
        term = xp.where(bi > 0, p * xp.log2(xp.where(p > 0, p, 1.0)), 0.0)
        h = -term.sum(2)
        Hc = (ca / (L - 1) * h).sum(1)
        out[lo:hi] = xp.maximum(0.0, Hu - Hc)
    return out


def _decrypt_all_scores(messages: List, seeds, generator: str, combiner: str,
                        N: int, body_start: int, Lmax: int):
    """(n_seeds, n_msg) order-predictability of each message's decrypt."""
    K = keystream_batch(generator, seeds, N, Lmax)       # (nseed, Lmax)
    scores = xp.empty((seeds.shape[0], len(messages)))
    for mi, m in enumerate(messages):
        Lm = len(m)
        cm = xp.asarray(m, dtype=xp.int64)[None, :]
        if combiner == "add":
            D = (cm - K[:, :Lm]) % N
        elif combiner == "sub":
            D = (cm + K[:, :Lm]) % N
        else:  # beaufort
            D = (K[:, :Lm] - cm) % N
        scores[:, mi] = order_pred_batch(D, N, body_start)
    return scores


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def decoy_null(messages: List, generator: str, combiner: str, N: int,
               body_start: int, Lmax: int, decoy_seeds: int = 200):
    seeds = xp.arange(1_000_000_000, 1_000_000_000 + decoy_seeds, dtype=xp.int64)
    sc = _decrypt_all_scores(messages, seeds, generator, combiner, N,
                             body_start, Lmax)
    mu = sc.mean(0)
    sd = sc.std(0, ddof=1)
    sd = xp.where(sd > 0, sd, 1e-9)
    return mu, sd


def _verdict(structured_row, n_msg: int, crib_member: int) -> str:
    n = int(structured_row.sum())
    crib_trip = next((t for t in TRIPLETS if crib_member in t), ())
    in_trip = int(sum(int(structured_row[i]) for i in crib_trip))
    if n >= n_msg - 1:
        return "global"
    if in_trip == len(crib_trip) and n <= len(crib_trip) + 1:
        return "local"
    if n >= 2:
        return "partial"
    return "none"


def scan(messages: List, word: str, position: int, member: int, generator: str,
         combiner: str, seed_start: int, seed_end: int, N: int = N_DEFAULT,
         body_start: int = 0, mu=None, sd=None, z_thr: float = 3.0,
         chunk: int = 1 << 20, decoy_seeds: int = 200) -> List[dict]:
    Lmax = max(len(m) for m in messages)
    member_ct = list(messages[member])
    if mu is None:
        mu, sd = decoy_null(messages, generator, combiner, N, body_start, Lmax,
                            decoy_seeds)
    survivors = []
    for lo in range(seed_start, seed_end, chunk):
        hi = min(lo + chunk, seed_end)
        seeds = xp.arange(lo, hi, dtype=xp.int64)
        mask = repeat_filter(member_ct, word, position, generator, seeds, N)
        if bool(mask.any()):
            survivors.append(seeds[mask])
    if not survivors:
        return []
    surv = xp.concatenate(survivors)
    sc = _decrypt_all_scores(messages, surv, generator, combiner, N, body_start,
                             Lmax)
    z = (sc - mu[None, :]) / sd[None, :]
    structured = z > z_thr
    surv_h = np.asarray(surv.get() if GPU else surv)
    z_h = np.asarray(z.get() if GPU else z)
    st_h = np.asarray(structured.get() if GPU else structured)
    results = []
    for r in range(surv_h.shape[0]):
        results.append({
            "seed": int(surv_h[r]), "generator": generator, "position": position,
            "z": [round(float(v), 2) for v in z_h[r]],
            "n_structured": int(st_h[r].sum()),
            "verdict": _verdict(st_h[r], len(messages), member),
        })
    results.sort(key=lambda d: (-d["n_structured"], -max(d["z"])))
    return results


# ---------------------------------------------------------------------------
# Selftest — validate vectorised primitives + end-to-end vs the CPU reference.
# ---------------------------------------------------------------------------

def selftest() -> List[tuple[str, bool]]:
    out: List[tuple[str, bool]] = []
    import langdetect
    N = 83
    seeds = xp.asarray([1, 2, 42, 12345, 1_000_000, 99_999_999], dtype=xp.int64)
    sh = np.asarray(seeds.get() if GPU else seeds)

    for name in GENERATORS:
        M = keystream_batch(name, seeds, N, 14)
        Mh = np.asarray(M.get() if GPU else M)
        ref = {"nolla": ks.gen_nolla, "minstd": ks.gen_minstd,
               "xorshift32": ks.gen_xorshift32, "lfsr32": ks.gen_lfsr32}[name]
        ok = all(list(Mh[i]) == ref(int(s), N, 14) for i, s in enumerate(sh))
        out.append((f"{name} keystream byte-exact vs CPU", ok))

    rng = np.random.default_rng(0)
    Dnp = np.array([ks._markov(N, 90, rng, conc=50) for _ in range(5)]
                   + [list(rng.integers(0, N, size=90)) for _ in range(3)])
    mine = np.asarray((order_pred_batch(xp.asarray(Dnp), N).get() if GPU
                       else order_pred_batch(xp.asarray(Dnp), N)))
    ref = np.array([langdetect.order_predictability(list(Dnp[i]))
                    for i in range(len(Dnp))])
    out.append(("order-predictability batch matches CPU (<1e-9)",
                bool(np.allclose(mine, ref, atol=1e-9))))

    # End-to-end: GLOBAL plant -> verdict global; LOCAL plant -> verdict local.
    T = 160
    word = "sisaltaa"
    letters = sorted(set(word))
    sigma = {ch: (i * 11 + 4) % N for i, ch in enumerate(letters)}
    pos = 30
    rng2 = np.random.default_rng(11)

    def plant(keys):
        pl = [ks._markov(N, T, rng2, conc=80) for _ in range(9)]
        for o, ch in enumerate(word):
            pl[0][pos + o] = sigma[ch]
        return [[(pl[k][t] + keys[k][t]) % N for t in range(T)] for k in range(9)]

    S = 5151515
    Kg = ks.gen_nolla(S, N, T)
    mg = plant([Kg] * 9)
    rg = scan(mg, word, pos, 0, "nolla", "add", S - 3000, S + 3000, N=N,
              body_start=0, decoy_seeds=80, chunk=1 << 16)
    topg = next((r for r in rg if r["seed"] == S), None)
    out.append(("GPU-path global plant: true seed found", topg is not None))
    out.append(("GPU-path global plant: verdict global",
                topg is not None and topg["verdict"] == "global"))

    seeds3 = [4242424, 7373737, 9191919]
    Ks = [ks.gen_nolla(s, N, T) for s in seeds3]
    per = [Ks[0]] * 3 + [Ks[1]] * 3 + [Ks[2]] * 3
    ml = plant(per)
    rl = scan(ml, word, pos, 0, "nolla", "add", seeds3[0] - 3000, seeds3[0] + 3000,
              N=N, body_start=0, decoy_seeds=80, chunk=1 << 16)
    topl = next((r for r in rl if r["seed"] == seeds3[0]), None)
    out.append(("GPU-path local plant: crib seed found", topl is not None))
    out.append(("GPU-path local plant: verdict local",
                topl is not None and topl["verdict"] == "local"))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="GPU crib-globality scan")
    ap.add_argument("--crib-word", default="")
    ap.add_argument("--crib-msg", default="East 1")
    ap.add_argument("--crib-pos", type=int, default=3)
    ap.add_argument("--crib-pos-end", type=int, default=None)
    ap.add_argument("--generators", default="all")
    ap.add_argument("--combiner", default="add", choices=["add", "sub", "beaufort"])
    ap.add_argument("--seed-start", type=int, default=0)
    ap.add_argument("--seed-end", type=int, default=100_000_000)
    ap.add_argument("--body-start", type=int, default=0)
    ap.add_argument("--decoy-seeds", type=int, default=200)
    ap.add_argument("--z-thr", type=float, default=3.0)
    ap.add_argument("--chunk", type=int, default=1 << 21,
                    help="seeds per GPU batch (lower if you hit OOM)")
    ap.add_argument("--html", default="")
    args = ap.parse_args()

    print(f"backend: {'CuPy (GPU)' if GPU else 'NumPy (CPU)'}")
    if not args.crib_word:
        results = selftest()
        for label, ok in results:
            print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
        n_ok = sum(1 for _, ok in results if ok)
        print(f"\n{n_ok}/{len(results)} globality_gpu checks passed")
        sys.exit(0 if n_ok == len(results) else 1)

    import corpus as corpus_mod
    c = corpus_mod.load()
    N = c.N
    messages = [list(x) for x in c.ciphertexts]
    member = c.labels.index(args.crib_msg) if args.crib_msg in c.labels else 0
    gens = list(GENERATORS) if args.generators == "all" else \
        [g.strip() for g in args.generators.split(",")]
    pos_end = args.crib_pos if args.crib_pos_end is None else args.crib_pos_end
    Lmax = max(len(m) for m in messages)
    positions = [p for p in range(args.crib_pos, pos_end + 1)
                 if p + len(args.crib_word) <= len(messages[member])]

    k, frac = ks.crib_power(args.crib_word, N)
    print(f"crib '{args.crib_word}' in {c.labels[member]}: {k} constraint(s) "
          f"~{frac:.2e} survive | {len(gens)} gen x {len(positions)} pos x "
          f"{args.seed_end-args.seed_start:,} seeds")
    all_res = []
    t0 = time.time()
    for gen in gens:
        mu, sd = decoy_null(messages, gen, args.combiner, N, args.body_start,
                            Lmax, args.decoy_seeds)
        for p in positions:
            res = scan(messages, args.crib_word, p, member, gen, args.combiner,
                       args.seed_start, args.seed_end, N=N,
                       body_start=args.body_start, mu=mu, sd=sd, z_thr=args.z_thr,
                       chunk=args.chunk)
            all_res.extend(res)
    all_res.sort(key=lambda d: (-d["n_structured"], -max(d["z"])))
    dt = time.time() - t0
    glob = [r for r in all_res if r["verdict"] == "global"]
    print(f"\nscanned in {dt:.1f}s; {len(all_res)} crib survivors")
    for r in all_res[:10]:
        print(f"  {r['generator']:10} pos {r['position']:>3} seed {r['seed']:>12} "
              f"{r['verdict']:8} {r['n_structured']}/9")
    print("\nVERDICT:", "GLOBAL keystream candidate!" if glob else
          "no global hit (local/none in range)")
    if args.html:
        rows = "".join(
            "<tr><td>{generator}</td><td>{position}</td><td>{seed}</td>"
            "<td>{verdict}</td><td>{n_structured}/9</td><td>{z}</td></tr>".format(**r)
            for r in all_res[:60])
        Path(args.html).write_text(
            f"<!doctype html><meta charset='utf-8'><title>globality GPU</title>"
            f"<h1>crib-globality (GPU)</h1><p>crib={args.crib_word} "
            f"backend={'GPU' if GPU else 'CPU'}</p><table border=1>"
            f"<tr><th>gen<th>pos<th>seed<th>verdict<th>n<th>z</tr>{rows}</table>",
            encoding="utf-8")
        print(f"wrote {args.html}")
